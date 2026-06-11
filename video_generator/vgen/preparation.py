"""The preparation step: fetch real reference assets before the scenes are built.

A storyboard's ``# Preparation`` block is, by default, just *context* fed to the
scene generator (see :mod:`vgen.scenes`). When ``--run-preparation`` is set, this
module turns that block into *action*: it runs the AI CLI **agentically** (tools
enabled, with the project's MCP servers attached from ``.mcp.json``) so the model
can actually carry the block out.

What "carrying it out" means is topic-specific, so it is delegated to a
**preparation profile** chosen by the storyboard's ``preparation_profile:``
front-matter key (default ``generic``). Profiles are plain **YAML files in the
repo-root ``profiles/`` directory** — drop ``profiles/<name>.yaml`` in to add one;
no code change needed. A profile may declare:

* ``assets_subdir`` — where under ``<output>/`` to save the fetched files;
* ``mcp_server`` + ``launch`` — an MCP server to make sure is up before the agent
  runs, and how to launch the app that serves it (with an optional preference to
  set first), so e.g. the ``archi`` profile starts Archi and its MCP server;
* ``prompt_specialization`` — extra, topic-specific instructions for the agent;
* ``extra_tools`` — tool allowances beyond the base file/web set.

Either way the agent saves files + a ``manifest.json`` into ``<output>/assets/…``;
:func:`load_manifest` reads it back and the scene generator lists those paths so
scenes load the real assets instead of inventing shapes. The whole step is
best-effort: if the AI CLI isn't agentic, the MCP config is missing, or nothing
usable is produced, it logs a warning and returns ``None`` so the build falls back
to Manim primitives.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

from . import config
from .models import Storyboard
from .progress import progress

MANIFEST_NAME = "manifest.json"

# Tools every profile allows without prompting: the file + web tools the agent
# needs to save assets or fall back to an online source. Each profile may add
# more, and the runner additionally allows ``mcp__<server>__*`` for every MCP
# server present in the project's .mcp.json.
_BASE_TOOLS = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch"]

# Phrases that mark a "nothing to do" preparation block (the patterns generator
# emits one of these). Matched case-insensitively as a substring.
_NOOP_MARKERS = ("no preparation is needed", "no preparation needed")

# Launch defaults used when a profile's `launch:` block omits them.
_DEFAULT_LAUNCH_TIMEOUT = 60.0
_DEFAULT_LAUNCH_POLL = 2.0


# --- manifest + small introspection helpers --------------------------------

def load_manifest(assets_dir: Path) -> List[Dict[str, str]]:
    """Return the list of asset records from ``<assets_dir>/manifest.json``.

    Each record is a dict with at least ``type`` and ``file`` (a path relative to
    ``assets_dir``); extra keys (e.g. ``layer``) are kept. Returns ``[]`` if the
    manifest is absent or malformed — callers treat that as "no assets"."""
    manifest = assets_dir / MANIFEST_NAME
    if not manifest.exists():
        return []
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []
    symbols = data.get("symbols") if isinstance(data, dict) else data
    if not isinstance(symbols, list):
        return []
    out: List[Dict[str, str]] = []
    for item in symbols:
        if isinstance(item, dict) and item.get("type") and item.get("file"):
            out.append({k: str(v) for k, v in item.items()})
    return out


def is_noop_preparation(preparation: str) -> bool:
    """True if the block explicitly says no preparation is needed (or is empty)."""
    text = preparation.strip().lower()
    return not text or any(marker in text for marker in _NOOP_MARKERS)


def _load_mcp(mcp_config: Optional[Path]) -> dict:
    try:
        data = json.loads(Path(mcp_config).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def mcp_server_names(mcp_config: Optional[Path]) -> List[str]:
    """Every server name declared under ``mcpServers`` in an ``.mcp.json``."""
    servers = _load_mcp(mcp_config).get("mcpServers", {})
    return list(servers.keys()) if isinstance(servers, dict) else []


def mcp_tool_patterns(mcp_config: Optional[Path]) -> List[str]:
    """``mcp__<server>__*`` allow-patterns for every server in the MCP config."""
    return [f"mcp__{name}__*" for name in mcp_server_names(mcp_config)]


def mcp_host_port(mcp_config: Optional[Path], server: str) -> Optional[Tuple[str, int]]:
    """Read ``(host, port)`` for one server out of an ``.mcp.json``.

    Returns ``None`` if the file/server/URL can't be read or has no explicit
    port — callers then skip the launch-and-poll and just let the agent try."""
    try:
        url = _load_mcp(mcp_config)["mcpServers"][server]["url"]
    except (KeyError, TypeError):
        return None
    parsed = urlparse(str(url))
    if not parsed.hostname or not parsed.port:
        return None
    return parsed.hostname, parsed.port


def port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """True if a TCP connection to ``host:port`` succeeds within ``timeout``."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _expand(text: str) -> str:
    """Expand ``$VARS`` and a leading ``~`` in a path string from a profile."""
    return os.path.expanduser(os.path.expandvars(text))


# --- bringing an MCP server up (generic, driven by a profile's launch spec) -

def set_preference(spec: dict) -> None:
    """Set ``key=value`` in a Java/Eclipse-style ``.properties`` file (used to
    enable an app's 'auto-start the server on launch' preference).

    ``spec`` = ``{file, key, value, ensure_eclipse_version?}``. Preserves existing
    keys/comments; a no-op if the key already holds the wanted value."""
    try:
        prefs = Path(_expand(str(spec["file"])))
        key = str(spec["key"])
        value = str(spec.get("value", "true"))
    except (KeyError, TypeError):
        return
    try:
        existing = prefs.read_text(encoding="utf-8").splitlines() if prefs.exists() else []
    except OSError:
        existing = []
    if any(ln.strip() == f"{key}={value}" for ln in existing):
        return                                   # already set — leave the file alone
    kept = [ln for ln in existing if not ln.startswith(f"{key}=")]
    if spec.get("ensure_eclipse_version", True) and not any(
        ln.startswith("eclipse.preferences.version=") for ln in kept
    ):
        kept.insert(0, "eclipse.preferences.version=1")
    kept.append(f"{key}={value}")
    try:
        prefs.parent.mkdir(parents=True, exist_ok=True)
        prefs.write_text("\n".join(kept) + "\n", encoding="utf-8")
        progress.log(f"  [prep] set preference {key}={value} in {prefs.name}.")
    except OSError as exc:
        progress.log(f"  [prep] could not write preference {key} ({exc}).")


def _scratch_model(open_file) -> Optional[Path]:
    """Copy a profile's model template to a scratch file so the app opens a FRESH
    model without mutating the repo template. Relative paths resolve against the
    profiles dir. Returns the scratch path (the source if copying fails, or None if
    the source is missing)."""
    src = Path(_expand(str(open_file)))
    if not src.is_absolute():
        src = config.PROFILES_DIR / src
    if not src.exists():
        progress.log(f"  [prep] model template {src} not found; launching without a "
                     "preloaded model.")
        return None
    try:
        dst = Path(tempfile.gettempdir()) / f"vgen_scratch_{src.name}"
        shutil.copyfile(src, dst)
        return dst
    except OSError as exc:
        progress.log(f"  [prep] could not copy model template ({exc}); opening it directly.")
        return src


def launch_app(launch: dict) -> bool:
    """Launch a profile's app detached so its MCP server can start. Returns
    whether the launch was attempted; needs a display (unless opted out) and the
    command to exist. A ``open_file`` is passed as an argument (so e.g. Archi opens
    a model on launch via its openFile launcher action)."""
    command = _expand(str(launch.get("command", "")))
    if not command:
        return False
    if launch.get("requires_display", True) and not os.environ.get("DISPLAY"):
        progress.log("  [prep] no DISPLAY (headless) — cannot launch "
                     f"{Path(command).name}; start it manually.")
        return False
    if not Path(command).exists():
        progress.log(f"  [prep] launcher not found at {command} — start it manually.")
        return False
    argv = [command]
    if launch.get("open_file"):
        scratch = _scratch_model(launch["open_file"])
        if scratch is not None:
            argv.append(str(scratch))
    try:
        subprocess.Popen(
            argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
    except OSError as exc:
        progress.log(f"  [prep] failed to launch {Path(command).name} ({exc}).")
        return False
    extra = " with a fresh model" if len(argv) > 1 else ""
    progress.log(f"  [prep] launched {Path(command).name}{extra}; waiting for the MCP server…")
    return True


def _wait_for_window(name: str, timeout: float) -> Optional[str]:
    """Poll ``xdotool`` for an X window whose name matches ``name``; return its id."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            out = subprocess.run(["xdotool", "search", "--name", name],
                                 capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            return None
        ids = (out.stdout or "").strip().splitlines()
        if ids:
            return ids[0]
        time.sleep(1.0)
    return None


def run_post_launch_keys(launch: dict) -> bool:
    """Best-effort: wait for the launched app's window and send key chords to it
    (e.g. ``ctrl+n`` to create a new model) via ``xdotool``.

    Returns whether the keys were sent. No-op (logged) without a display, without
    ``xdotool``, or if the window never appears — the agent then does it itself."""
    keys = list(launch.get("after_launch_keys") or [])
    if not keys:
        return False
    if not os.environ.get("DISPLAY"):
        return False
    if shutil.which("xdotool") is None:
        progress.log("  [prep] xdotool not installed; the agent will create the "
                     "model itself.")
        return False
    window = str(launch.get("window_name", "Archi"))
    wait = float(launch.get("window_wait_seconds", 30.0))
    wid = _wait_for_window(window, wait)
    if not wid:
        progress.log(f"  [prep] {window} window not found within {wait:.0f}s; the "
                     "agent will create the model itself.")
        return False
    try:
        subprocess.run(["xdotool", "windowactivate", "--sync", wid],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        for chord in keys:
            subprocess.run(["xdotool", "key", "--window", wid, chord],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            time.sleep(0.5)
    except (OSError, subprocess.SubprocessError) as exc:
        progress.log(f"  [prep] could not send keys to {window} ({exc}).")
        return False
    progress.log(f"  [prep] sent {', '.join(keys)} to {window} (created a new model).")
    return True


def ensure_server(mcp_config: Optional[Path], server: str, launch: dict) -> bool:
    """Ensure ``server``'s MCP port is reachable, launching its app if not.

    Returns True if the port is open (already, or after launching). Best-effort:
    a False result is logged but never aborts the build."""
    hostport = mcp_host_port(mcp_config, server)
    if hostport is None:
        return True                              # no explicit port -> let the agent try
    host, port = hostport
    if port_open(host, port):
        progress.log(f"  [prep] MCP server already reachable at {host}:{port}.")
        return True

    progress.log(f"  [prep] MCP server not reachable at {host}:{port}; "
                 "launching its app to bring it up…")
    if launch.get("enable_preference"):
        set_preference(launch["enable_preference"])
    if not launch_app(launch):
        return port_open(host, port)
    run_post_launch_keys(launch)                 # e.g. Ctrl+N: create a model first
    timeout = float(launch.get("timeout_seconds", _DEFAULT_LAUNCH_TIMEOUT))
    poll = float(launch.get("poll_seconds", _DEFAULT_LAUNCH_POLL))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if port_open(host, port):
            progress.log(f"  [prep] ✓ MCP server is up at {host}:{port}.")
            return True
        time.sleep(poll)
    progress.log(
        f"  [prep] app launched but the MCP server did not come up at {host}:{port} "
        f"within {timeout:.0f}s. Enable its 'auto-start on launch' option, or start "
        "the server manually. Continuing without it."
    )
    return False


# --- preparation profiles --------------------------------------------------

class PreparationProfile:
    """Default, topic-agnostic preparation behavior.

    Runs the ``# Preparation`` block agentically and saves whatever reference
    assets it produces; launches no external application. The ``archi`` profile
    (and any other) is a :class:`DeclarativeProfile` loaded from a YAML file."""

    name = "generic"
    assets_subdir = Path("assets") / "prep"
    extra_tools: Sequence[str] = ()

    def ensure_ready(self, mcp_config: Optional[Path]) -> None:
        """Bring up anything the profile needs before the agent runs (no-op here)."""

    def prompt_specialization(self) -> str:
        """Extra instructions inserted into the agent prompt (none by default)."""
        return ""


class DeclarativeProfile(PreparationProfile):
    """A profile built from a ``profiles/<name>.yaml`` spec (see module docs)."""

    def __init__(self, spec: dict) -> None:
        self.name = str(spec.get("name") or "generic")
        self.assets_subdir = Path(str(spec.get("assets_subdir") or "assets/prep"))
        self.extra_tools = list(spec.get("extra_tools") or [])
        self._special = str(spec.get("prompt_specialization") or "")
        self._server = spec.get("mcp_server")
        self._launch = spec.get("launch") or {}

    def ensure_ready(self, mcp_config: Optional[Path]) -> None:
        if self._server and self._launch and mcp_config is not None:
            ensure_server(mcp_config, str(self._server), dict(self._launch))

    def prompt_specialization(self) -> str:
        return self._special


def _load_profile_spec(name: str) -> Optional[dict]:
    """Read ``profiles/<name>.yaml`` (or ``.yml``) from the profiles dir."""
    for ext in (".yaml", ".yml"):
        path = config.PROFILES_DIR / f"{name}{ext}"
        if path.exists():
            import yaml  # lazy: only needed when a profile is actually used
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError):
                return None
            return data if isinstance(data, dict) else None
    return None


def get_profile(name: Optional[str]) -> PreparationProfile:
    """Resolve a preparation profile by name.

    A ``profiles/<name>.yaml`` file wins; otherwise the built-in ``generic``
    default is used (with a note when an unknown name was requested)."""
    key = (name or "generic").strip().lower()
    spec = _load_profile_spec(key)
    if spec is not None:
        return DeclarativeProfile(spec)
    if key != "generic":
        progress.log(f"  [prep] no profiles/{key}.yaml found; using 'generic'.")
    return PreparationProfile()


# --- the runner ------------------------------------------------------------

class PreparationRunner:
    """Executes a storyboard's ``# Preparation`` block as an agentic AI run,
    delegating the topic-specific parts to a :class:`PreparationProfile`."""

    def __init__(self, client, mcp_config: Optional[Path],
                 *, timeout: float = config.PREPARATION_TIMEOUT_SECONDS) -> None:
        self.client = client
        self.mcp_config = mcp_config
        self.timeout = timeout

    def is_actionable(self, storyboard: Storyboard) -> bool:
        """Whether running the agent for this storyboard makes sense at all."""
        if is_noop_preparation(storyboard.preparation):
            return False
        if not hasattr(self.client, "run_agent"):   # only claude is agentic here
            return False
        return True

    def run(self, storyboard: Storyboard, output: Path, force: bool) -> Optional[Path]:
        """Run the preparation agent; return the assets dir if usable, else None."""
        profile = get_profile(storyboard.preparation_profile)
        assets_dir = (output / profile.assets_subdir).resolve()

        if is_noop_preparation(storyboard.preparation):
            progress.log("  [prep] no preparation needed for this storyboard — skipping.")
            return None
        if not hasattr(self.client, "run_agent"):
            progress.log(f"  [prep] ai_cli '{getattr(self.client, 'name', '?')}' has no "
                         "agentic mode — skipping preparation (scenes use primitives).")
            return None
        if self.mcp_config is None or not Path(self.mcp_config).exists():
            progress.log(f"  [prep] no MCP config at {self.mcp_config} — skipping "
                         "preparation (scenes use primitives).")
            return None

        existing = load_manifest(assets_dir)
        if existing and not force:
            progress.log(f"  [prep] reusing {len(existing)} cached asset(s) in "
                         f"{assets_dir} (pass --force to refetch).")
            return assets_dir

        assets_dir.mkdir(parents=True, exist_ok=True)
        # Best-effort: let the profile bring up whatever it needs (e.g. Archi).
        # We proceed regardless — the agent can still source assets online/by
        # producing them when the service is unreachable.
        profile.ensure_ready(self.mcp_config)
        allowed = self._allowed_tools(profile)
        progress.log(f"  [prep] running the # Preparation block agentically via "
                     f"{self.client.name} (profile: {profile.name}, mcp: {self.mcp_config})…")
        prompt = self._build_prompt(storyboard, assets_dir, profile)
        try:
            self.client.run_agent(
                prompt, mcp_config=self.mcp_config, allowed_tools=allowed,
                add_dirs=[assets_dir], cwd=config.REPO_ROOT, timeout=self.timeout,
            )
        except SystemExit as exc:                # never fail the whole build on prep
            progress.log(f"  [prep] preparation agent failed ({exc}); continuing with "
                         "Manim primitives.")
            return None

        assets = load_manifest(assets_dir)
        if not assets:
            progress.log("  [prep] preparation produced no usable assets "
                         "(no manifest.json) — continuing with Manim primitives.")
            return None
        progress.log(f"  [prep] ✓ {len(assets)} asset(s) ready in {assets_dir}: "
                     f"{', '.join(s['type'] for s in assets[:8])}"
                     f"{'…' if len(assets) > 8 else ''}")
        return assets_dir

    def _allowed_tools(self, profile: PreparationProfile) -> List[str]:
        """Base file/web tools + the profile's extras + every configured MCP server."""
        out: List[str] = []
        for tool in [*_BASE_TOOLS, *profile.extra_tools, *mcp_tool_patterns(self.mcp_config)]:
            if tool not in out:
                out.append(tool)
        return out

    def _build_prompt(self, storyboard: Storyboard, assets_dir: Path,
                      profile: PreparationProfile) -> str:
        """The instruction the agent carries out to gather the reference assets."""
        special = profile.prompt_specialization().strip()
        special_block = f"\n{special}\n" if special else ""
        scene_lines = [f"- {s.basename}: {s.description.strip()}"
                       for s in storyboard.scenes if s.description.strip()]
        scenes_block = "\n".join(scene_lines) if scene_lines else "(see the brief above)"
        return f"""You are the PREPARATION step for an automated tutorial-video build.
Your job is to gather the real, authoritative reference ASSETS this video needs,
save them as files, and write a manifest — then stop. You are NOT writing any
video/scene code.

PROJECT TITLE: {storyboard.title}

PROJECT BRIEF:
{storyboard.project_brief}

THE STORYBOARD'S OWN PREPARATION INSTRUCTIONS (carry these out):
{storyboard.preparation.strip()}
{special_block}
SCENES IN THIS VIDEO — fetch ONLY the symbols these scenes actually use; do NOT
exhaustively gather every possible symbol. Read the descriptions and collect just
the element/relationship types they name (including any from neighbouring layers):
{scenes_block}

OUTPUT CONTRACT (follow EXACTLY):
- Save every asset into this directory: {assets_dir}
- Prefer SVG. Name each file by a lowercase, hyphen-free slug of the thing it
  depicts, e.g. "stakeholder.svg". If you truly cannot get or make an SVG, save a
  PNG/JPG with the same stem instead (e.g. "stakeholder.jpg").
- Crop every asset TIGHTLY: trim any empty/transparent margin on all four sides so
  the subject fills the image with no surrounding whitespace (it gets sized and
  placed in scenes, so padding throws the layout off).
- Source each asset in this order of preference: (1) the MCP tools/servers
  available to you (per the instructions above; if you cannot reach a server, say
  so and move on); (2) the official source found online; (3) only if neither
  works, produce it yourself as a clean SVG (fallback raster).
- After saving the files, write {assets_dir / MANIFEST_NAME} as JSON of the form:
  {{"symbols": [{{"type": "Stakeholder", "file": "stakeholder.svg"}}, ...]}}
  where each "file" is the file name relative to that directory (extra fields are
  fine). Include one entry per asset you actually saved (omit ones you failed to
  obtain).

Work until the files and manifest.json exist, then stop with a one-line summary of
what you saved and where each came from.
"""
