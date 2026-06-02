#!/usr/bin/env python3
"""Generate a bilingual Manim tutorial video from a storyboard markdown file.

Usage:
    python3 video_generator/generate_video.py \
        --storyboard storyboard/storyboard_v2.md \
        --output build/strategy_pattern

On first run the script bootstraps a project-local `.venv` at the repo root,
installs its Python deps into it, and re-execs itself there, so any Python 3
interpreter can launch it.

Required CLI arguments are only the storyboard markdown path and the target
output directory; every intermediate artifact (scripts, audio, subtitles, raw
renders, muxed clips, final videos) is written under <output>.

The storyboard is a markdown file. The first block must be YAML front-matter
between '---' fences declaring the project config. The body contains one '##
Scene: <basename> / <ClassName>' heading per scene, each with optional '###'
subsections such as 'description', 'narration.id', 'narration.en', 'notes'.

If a scene's narration.<lang> section is missing, the generator can call out
to a Claude / Codex CLI (configured via 'ai_cli' in front-matter) to fill it
in. The Manim scene .py files themselves are NOT auto-generated; they must
exist under the configured scenes_landscape_dir / scenes_portrait_dir.

The patch to scenes_*/_common.py honours MANIM_AUDIO_DIR so the same scene
files can be rendered against an arbitrary output directory.
"""

from __future__ import annotations

import argparse
import base64
import dataclasses
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Tuple

GENERATOR_ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = GENERATOR_ROOT / "templates"
REPO_ROOT = GENERATOR_ROOT.parent
REQUIREMENTS = GENERATOR_ROOT / "requirements.txt"

# A project-local virtual environment at the repo root. The script bootstraps
# this on first run (see _bootstrap_venv) and re-execs itself inside it, so it
# never touches a system or ~/venv interpreter.
VENV_DIR = REPO_ROOT / ".venv"
VENV_BIN = VENV_DIR / "bin"
PYTHON_BIN = VENV_BIN / "python"
MANIM_BIN = VENV_BIN / "manim"
EDGE_TTS_BIN = VENV_BIN / "edge-tts"


# --- Progress logging with elapsed time -----------------------------------
# Every progress line is prefixed with [MM:SS] elapsed since the build started,
# so the duration of each step is visible as the delta between lines. Slow steps
# (AI calls, TTS, renders) also print their own "done in Xs".

_T0 = time.monotonic()


def _reset_clock() -> None:
    global _T0
    _T0 = time.monotonic()


def _elapsed() -> float:
    return time.monotonic() - _T0


def _clock() -> str:
    e = int(_elapsed())
    return f"{e // 60:02d}:{e % 60:02d}"


def log(msg: str) -> None:
    """Print a progress line prefixed with elapsed [MM:SS]."""
    print(f"[{_clock()}] {msg}", flush=True)


# Voice / TTS defaults. Used when the storyboard's `voices:` map omits a
# language, or when a provider/voice isn't pinned on the command line.
DEFAULT_EDGE_VOICE = "id-ID-ArdiNeural"
DEFAULT_GEMINI_VOICE = "Iapetus"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-preview-tts"
# Default Claude model + effort for narration / scene generation. Opus 4.8 at
# the top ("max") effort tier gives the best layout-aware scene code. Override
# per run with --claude-model / --claude-effort.
DEFAULT_CLAUDE_MODEL = "claude-opus-4-8"
DEFAULT_CLAUDE_EFFORT = "max"
GEMINI_TTS_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


# --- Bootstrap: relaunch inside a project-local .venv ---------------------
#
# Mirrors the sibling `slides_narrator` project: on first run we create
# `<repo>/.venv`, install the Python deps into it, and re-exec this script with
# that interpreter. A marker env var stops the re-exec from looping. After this
# returns we are always running inside `.venv`, so the lazy `import yaml` / srt
# and the `manim` / `edge-tts` console scripts all resolve locally.

VENV_MARK = "VIDEO_GENERATOR_VENV"


def _bootstrap_venv() -> None:
    if os.environ.get(VENV_MARK) == "1":
        return
    fresh = not VENV_DIR.exists()
    if fresh:
        print(f"[setup] creating virtual environment at {VENV_DIR}")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    pip = VENV_BIN / "pip"
    python = VENV_BIN / "python"
    if not pip.exists():
        sys.exit(f"[setup] venv looks broken; missing {pip}. Delete {VENV_DIR} and re-run.")
    if fresh:
        print("[setup] installing dependencies (PyYAML, srt, manim, edge-tts)…")
        subprocess.check_call([str(pip), "install", "-q", "--upgrade", "pip"])
        if REQUIREMENTS.exists():
            subprocess.check_call([str(pip), "install", "-q", "-r", str(REQUIREMENTS)])
        else:
            subprocess.check_call([str(pip), "install", "-q",
                                   "PyYAML", "srt", "manim", "edge-tts"])
    env = os.environ.copy()
    env[VENV_MARK] = "1"
    os.execvpe(str(python), [str(python), str(Path(__file__).resolve()), *sys.argv[1:]], env)


_bootstrap_venv()


# --- Dependency check -----------------------------------------------------


# Python packages we directly import; if missing, try to pip install into .venv.
_PYTHON_PACKAGES = [
    # (import_name, pip_name)
    ("yaml", "PyYAML"),
    ("srt", "srt"),
]

# Executables we shell out to. `install` is either a pip package name (to be
# installed into .venv) or None if the tool must be installed by the user.
_BINARIES = [
    {"path": MANIM_BIN, "name": "manim", "install_pip": "manim", "required": True},
    {"path": EDGE_TTS_BIN, "name": "edge-tts", "install_pip": "edge-tts", "required": True},
    {"path": shutil.which("ffmpeg"), "name": "ffmpeg", "install_pip": None, "required": True,
     "hint": "Install via the system package manager, e.g. `sudo apt install ffmpeg`."},
    {"path": shutil.which("ffprobe"), "name": "ffprobe", "install_pip": None, "required": True,
     "hint": "Ships with ffmpeg; installing ffmpeg also provides ffprobe."},
]


def _pip_install(pip_name: str) -> bool:
    pip = VENV_BIN / "pip"
    if not pip.exists():
        return False
    print(f"  installing {pip_name} into {VENV_BIN.parent}…")
    proc = subprocess.run(
        [str(pip), "install", "--quiet", pip_name],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print(f"  pip install {pip_name} failed: {proc.stderr.strip() or proc.stdout.strip()}")
        return False
    return True


def check_dependencies(need_ai_cli: str | None = None) -> None:
    """Validate every tool the generator depends on. Install Python deps that
    are missing if `.venv/bin/pip` is available; for system tools that can't
    be auto-installed, print the install command and exit."""
    print("Checking dependencies…")
    missing: List[str] = []

    # Python packages
    for import_name, pip_name in _PYTHON_PACKAGES:
        try:
            __import__(import_name)
        except ImportError:
            print(f"  missing python package: {import_name} (pip: {pip_name})")
            if not _pip_install(pip_name):
                missing.append(
                    f"python package '{pip_name}' — install with `{VENV_BIN/'pip'} install {pip_name}`"
                )
            else:
                try:
                    __import__(import_name)
                except ImportError:
                    missing.append(
                        f"python package '{pip_name}' — pip install reported success but import still fails"
                    )

    # Binaries
    for b in _BINARIES:
        path = b["path"]
        if path and Path(path).exists():
            continue
        # Try pip install if the tool installs into the venv.
        if b["install_pip"]:
            print(f"  missing binary: {b['name']} (trying pip install {b['install_pip']})")
            if _pip_install(b["install_pip"]):
                # Re-resolve the expected location.
                continue
            missing.append(
                f"{b['name']} — pip install failed; try manually: "
                f"`{VENV_BIN/'pip'} install {b['install_pip']}`"
            )
        else:
            hint = b.get("hint", "")
            missing.append(f"{b['name']} not found on PATH. {hint}".strip())

    # AI CLI (only enforced if the storyboard's ai_cli is needed).
    if need_ai_cli:
        env_key = {"claude": "CLAUDE_BIN", "codex": "CODEX_BIN"}.get(need_ai_cli)
        candidate = (
            os.environ.get(env_key) if env_key else None
        ) or shutil.which(need_ai_cli) or str(Path.home() / ".local" / "bin" / need_ai_cli)
        if not candidate or not Path(candidate).exists():
            if need_ai_cli == "claude":
                missing.append(
                    "claude CLI not found. Install Claude Code "
                    "(https://docs.claude.com/en/docs/claude-code/installation), "
                    f"or set $CLAUDE_BIN to its path, or pre-fill narration / scene .py "
                    "files in the storyboard."
                )
            else:
                missing.append(
                    f"{need_ai_cli} CLI not found. Install it or set "
                    f"${env_key} to its path."
                )

    if missing:
        print()
        print("Missing dependencies — please install before re-running:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    print("  all dependencies present.")
    print()


# --- Storyboard data model ------------------------------------------------


@dataclass
class Scene:
    basename: str
    classname: str
    file: str
    fallback_duration: float
    description: str
    narration: Dict[str, str] = field(default_factory=dict)
    extras: Dict[str, str] = field(default_factory=dict)


@dataclass
class Storyboard:
    title: str
    languages: List[str]
    orientations: List[str]
    voices: Dict[str, str]
    tts_provider: str
    gemini_model: str
    gemini_api_key: "str | None"
    ai_cli: str
    fps: int
    resolution_landscape: Tuple[int, int]
    scenes_landscape_dir: "Path | None"
    scenes_portrait_dir: "Path | None"
    scenes: List[Scene]
    project_brief: str
    max_duration: "float | None" = None  # total video cap in seconds, or None


# --- Markdown parser ------------------------------------------------------


_DURATION_SPEC_RE = re.compile(
    r"^\s*([0-9]*\.?[0-9]+)\s*"
    r"(h(?:ours?|rs?)?|m(?:in(?:ute)?s?)?|s(?:ec(?:ond)?s?)?)?\s*$",
    re.I,
)


def _parse_duration_spec(value) -> "float | None":
    """Parse a duration into seconds. Accepts a number (seconds), a unit string
    like '3 minutes' / '90s' / '1.5 min', or a clock form 'M:SS' / 'H:MM:SS'."""
    if value is None:
        return None
    if isinstance(value, bool):  # guard: bool is an int subclass
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    if ":" in s:
        try:
            nums = [float(p) for p in s.split(":")]
        except ValueError:
            raise SystemExit(f"Invalid duration '{value}'. Use seconds, '3 minutes', or 'M:SS'.")
        total = 0.0
        for n in nums:
            total = total * 60 + n
        return total
    m = _DURATION_SPEC_RE.match(s)
    if not m:
        raise SystemExit(f"Invalid duration '{value}'. Use seconds, '3 minutes', or 'M:SS'.")
    num = float(m.group(1))
    unit = (m.group(2) or "s").lower()
    if unit.startswith("h"):
        return num * 3600
    if unit.startswith("m"):
        return num * 60
    return num


_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
_SCENE_HEADING_RE = re.compile(r"^##\s+Scene\s*:\s*(.+?)\s*$", re.M)
_SUBSECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.M)
_FILE_META_RE = re.compile(r"\*\*file:\*\*\s*([^\s]+)", re.I)
_DURATION_META_RE = re.compile(r"\*\*fallback[_ ]duration:\*\*\s*([0-9.]+)", re.I)
_CLASS_META_RE = re.compile(r"\*\*class:\*\*\s*([^\s]+)", re.I)


def _camel_from_snake(name: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[_\-\s]+", name) if part)


def _strip_leading_digits(name: str) -> str:
    return re.sub(r"^[0-9]+[_\-\s]*", "", name)


def parse_scene(header: str, body: str) -> Scene:
    classname = ""
    basename = header.strip()
    if "/" in header:
        left, right = (s.strip() for s in header.split("/", 1))
        basename, classname = left, right
    m = _CLASS_META_RE.search(body)
    if m:
        classname = m.group(1).strip()
    if not classname:
        classname = _camel_from_snake(_strip_leading_digits(basename))

    file_match = _FILE_META_RE.search(body)
    file_path = file_match.group(1).strip() if file_match else f"scene_{basename}.py"
    dur_match = _DURATION_META_RE.search(body)
    fallback_duration = float(dur_match.group(1)) if dur_match else 15.0

    # Strip metadata lines so they don't leak into description/extras.
    body_clean = _FILE_META_RE.sub("", body)
    body_clean = _DURATION_META_RE.sub("", body_clean)
    body_clean = _CLASS_META_RE.sub("", body_clean)

    parts = _SUBSECTION_RE.split(body_clean)
    description = ""
    narration: Dict[str, str] = {}
    extras: Dict[str, str] = {}
    # parts[0] is the preamble before any ###; everything after is alternating key/content.
    for i in range(1, len(parts), 2):
        key = parts[i].strip().lower()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if key == "description":
            description = content
        elif key.startswith("narration."):
            lang = key.split(".", 1)[1].strip()
            narration[lang] = content
        else:
            extras[key] = content

    return Scene(
        basename=basename,
        classname=classname,
        file=file_path,
        fallback_duration=fallback_duration,
        description=description,
        narration=narration,
        extras=extras,
    )


def parse_storyboard(path: Path) -> Storyboard:
    import yaml  # imported lazily so check_dependencies can install it first

    text = path.read_text(encoding="utf-8")
    fm = _FRONT_MATTER_RE.match(text)
    if not fm:
        raise SystemExit(
            f"Storyboard {path} must begin with a YAML front-matter block "
            "delimited by '---' lines."
        )
    config = yaml.safe_load(fm.group(1)) or {}
    body = text[fm.end():]

    scene_starts = list(_SCENE_HEADING_RE.finditer(body))
    if not scene_starts:
        raise SystemExit("Storyboard must contain at least one '## Scene:' heading.")
    project_brief = body[: scene_starts[0].start()].strip()
    scenes: List[Scene] = []
    for i, m in enumerate(scene_starts):
        start = m.end()
        end = scene_starts[i + 1].start() if i + 1 < len(scene_starts) else len(body)
        scenes.append(parse_scene(m.group(1), body[start:end]))

    languages = list(config.get("languages") or ["id", "en"])
    orientations = list(config.get("orientations") or ["landscape", "portrait"])
    base = path.parent
    # If the storyboard specifies explicit dirs, resolve them relative to the
    # storyboard. Otherwise, fall back to None so the build step can default
    # them under <output>/scenes_*.
    raw_landscape = config.get("scenes_landscape_dir")
    raw_portrait = config.get("scenes_portrait_dir")
    scenes_landscape_dir = (base / raw_landscape).resolve() if raw_landscape else None
    scenes_portrait_dir = (base / raw_portrait).resolve() if raw_portrait else None

    # Total video duration cap. `max_duration` is the canonical key; we also
    # accept `max_scene_duration` as an alias (it's still the whole-video cap).
    max_duration = _parse_duration_spec(
        config.get("max_duration", config.get("max_scene_duration"))
    )
    if max_duration is not None:
        budget = sum(sc.fallback_duration for sc in scenes)
        if budget > max_duration + 1e-6:
            raise SystemExit(
                f"Storyboard duration budget is {budget:.0f}s but max_duration is "
                f"{max_duration:.0f}s. The video length tracks the sum of each "
                f"scene's fallback_duration (it sets the narration word budget), so "
                f"trim those values until they sum to <= {max_duration:.0f}s "
                f"(currently over by {budget - max_duration:.0f}s)."
            )

    return Storyboard(
        title=str(config.get("title") or path.stem),
        languages=languages,
        orientations=orientations,
        voices=dict(config.get("voices") or {}),
        tts_provider=str(config.get("tts_provider") or "edge"),
        gemini_model=str(config.get("gemini_model") or DEFAULT_GEMINI_MODEL),
        gemini_api_key=(str(config["gemini_api_key"]) if config.get("gemini_api_key") else None),
        ai_cli=str(config.get("ai_cli") or "claude"),
        fps=int(config.get("fps") or 30),
        resolution_landscape=tuple(config.get("resolution_landscape") or (1920, 1080)),
        scenes_landscape_dir=scenes_landscape_dir,
        scenes_portrait_dir=scenes_portrait_dir,
        scenes=scenes,
        project_brief=project_brief,
        max_duration=max_duration,
    )


# --- AI CLI integration ---------------------------------------------------


def _resolve_ai_cli(cli: str) -> str:
    """Locate the CLI binary. Honors $CLAUDE_BIN / $CODEX_BIN; falls back to
    PATH and to ~/.local/bin/ which is where the official installers land."""
    env_key = {"claude": "CLAUDE_BIN", "codex": "CODEX_BIN"}.get(cli)
    if env_key and os.environ.get(env_key):
        return os.environ[env_key]
    found = shutil.which(cli)
    if found:
        return found
    local = Path.home() / ".local" / "bin" / cli
    if local.exists():
        return str(local)
    raise SystemExit(
        f"AI CLI '{cli}' not found. Install it, set ${env_key} to its path, "
        "or pre-fill narration / scene .py files in the storyboard."
    )


def run_ai_cli(cli: str, prompt: str) -> str:
    """Run claude / codex CLI in non-interactive print mode and return stdout."""
    binary = _resolve_ai_cli(cli)
    if cli == "claude":
        # Don't pass --bare here: with --bare, Claude Code ignores OAuth/keychain
        # auth entirely and demands ANTHROPIC_API_KEY. We want the subprocess
        # to inherit the user's interactive `/login` session.
        #
        # `--tools ""` disables ALL tools. Without it, Claude Code runs as an
        # agent: instead of printing the requested file to stdout it uses its
        # Write tool to create the file and prints a prose summary ("Created
        # `scene.py` — ..."), which then fails ast.parse. Disabling tools forces
        # a plain text response that IS the file content.
        cmd = [
            binary, "-p",
            "--model", DEFAULT_CLAUDE_MODEL,
            "--effort", DEFAULT_CLAUDE_EFFORT,
            "--tools", "",
            "--permission-mode", "bypassPermissions",
            "--allow-dangerously-skip-permissions",
            "--disable-slash-commands",
        ]
    elif cli == "codex":
        # --sandbox read-only stops codex from writing the file itself (same
        # agentic pitfall as claude above); we want the content on stdout.
        cmd = [binary, "exec", "--sandbox", "read-only"]
    else:
        raise SystemExit(f"Unknown ai_cli '{cli}'. Use 'claude' or 'codex'.")
    proc = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True
    )
    if proc.returncode != 0:
        detail = (proc.stdout or "").strip() or (proc.stderr or "").strip() or "(no output)"
        raise SystemExit(
            f"{cli} CLI failed (exit {proc.returncode}). "
            f"Output: {detail}\n"
            f"If this says 'Not logged in', run `{binary} /login` once "
            "to authenticate before retrying."
        )
    return proc.stdout.strip()


def build_narration_prompt(sb: Storyboard, sc: Scene, lang: str) -> str:
    lang_name = {"id": "Indonesian", "en": "English"}.get(lang, lang)
    other = next(
        (sc.narration[k] for k in sc.narration if k != lang and sc.narration[k].strip()),
        "",
    )
    target_words = max(20, int(sc.fallback_duration * 2.5))
    parts = [
        f"You are writing the narration for one scene of a software-engineering tutorial video.",
        f"Project title: {sb.title}",
        f"Project brief:\n{sb.project_brief[:800]}",
        f"Scene: {sc.basename}  (class {sc.classname})",
        f"Scene description:\n{sc.description or '(none)'}",
    ]
    if other:
        parts.append(
            "Equivalent narration that already exists in another language "
            f"(use it for *meaning* only, do not translate word-for-word):\n{other}"
        )
    parts.append(
        f"Write ONLY the {lang_name} narration text. No headings, no bullet points, "
        "no quotation marks, no preamble or trailing commentary. Approximately "
        f"{target_words} words to fit ~{sc.fallback_duration:.0f} seconds of speech. "
        "Avoid orientation words (left/right/above/below) since the same script "
        "feeds both landscape and portrait renders."
    )
    return "\n\n".join(parts)


def ensure_narration(sb: Storyboard, sc: Scene, lang: str, output: "Path | None" = None) -> str:
    if sc.narration.get(lang, "").strip():
        return sc.narration[lang].strip()
    # Reuse an already-written narration file when available, so that resuming
    # a half-finished build doesn't re-spend AI tokens on text we already have.
    # `--force` short-circuits this by wiping `scripts/` before this runs.
    if output is not None:
        cached = output / "scripts" / lang / f"{sc.basename}.txt"
        if cached.exists():
            text = cached.read_text(encoding="utf-8").strip()
            if text:
                sc.narration[lang] = text
                return text
    log(f"  ai-fill narration.{lang} for {sc.basename} via {sb.ai_cli}…")
    _t = time.monotonic()
    text = run_ai_cli(sb.ai_cli, build_narration_prompt(sb, sc, lang))
    log(f"    ↳ narration.{lang}/{sc.basename} in {time.monotonic() - _t:.1f}s")
    if not text:
        raise SystemExit(
            f"AI CLI returned empty narration for {sc.basename}/{lang}. "
            "Fill in the storyboard manually."
        )
    sc.narration[lang] = text
    return text


# --- Scene file materialization (templates + AI generation) ---------------


def _materialize_scenes_dir(sb: Storyboard, output: Path, orient: str) -> Path:
    """Decide the scenes dir for an orientation and copy templates if needed.

    If the storyboard specified a scenes_<orient>_dir AND the dir exists, use
    it as-is (the user is bringing their own Manim sources). Otherwise the
    canonical location becomes <output>/scenes_<orient>/, and templates
    (_common.py, fonts) are copied in once.
    """
    declared = sb.scenes_landscape_dir if orient == "landscape" else sb.scenes_portrait_dir
    if declared is not None and declared.exists():
        return declared
    target = (output / f"scenes_{orient}").resolve()
    target.mkdir(parents=True, exist_ok=True)
    template_common = TEMPLATES_DIR / f"scenes_{orient}" / "_common.py"
    target_common = target / "_common.py"
    # _common.py is generator-owned (only materialised here, never hand-edited
    # in the default flow), so refresh it whenever the bundled template differs
    # — otherwise older builds silently miss fixes like the layout auto-fit.
    if template_common.exists() and (
        not target_common.exists()
        or target_common.read_bytes() != template_common.read_bytes()
    ):
        shutil.copy2(template_common, target_common)
    # _common.py also expects assets/fonts/ next to the scenes dir (ROOT_DIR/assets/fonts).
    assets_target = output / "assets"
    if not assets_target.exists() and (TEMPLATES_DIR / "assets").exists():
        shutil.copytree(TEMPLATES_DIR / "assets", assets_target)
    return target


def _build_scene_prompt(sb: Storyboard, sc: Scene, orient: str, skeleton: str, common_src: str) -> str:
    other_orient = "portrait" if orient == "landscape" else "landscape"
    portrait_note = ""
    if orient == "portrait":
        portrait_note = (
            "\nPortrait constraint: frame is 9 wide x 16 tall in Manim units, "
            "rendered at 1080x1920. Keep ALL visible content above "
            "SHORTS_SAFE_BOTTOM = -4.8 (the bottom 2/10 of the frame is "
            "reserved for Reels/Shorts/TikTok caption overlays). Use "
            "fit_to_shorts_area() to compress wide groups when needed.\n"
        )
    return f"""You are generating one Manim scene file for a tutorial video.

PROJECT TITLE: {sb.title}
PROJECT BRIEF:
{sb.project_brief}

SCENE BASENAME: {sc.basename}
SCENE CLASS:    {sc.classname}
ORIENTATION:    {orient} (a parallel file will exist for {other_orient})
FALLBACK DURATION: {sc.fallback_duration:.1f} seconds
SCENE DESCRIPTION:
{sc.description or "(no description provided)"}

LOCALIZED NARRATION (timed to fit the scene; visuals should illustrate this):

[id] {sc.narration.get("id", "(missing)").strip()}

[en] {sc.narration.get("en", "(missing)").strip()}
{portrait_note}
HELPERS AVAILABLE FROM `_common` (reproduced verbatim below for reference):
```python
{common_src}
```

REFERENCE SKELETON (the structure your output MUST follow — same imports,
same TARGET_DURATION assignment, same Scene subclass, same final wait):
```python
{skeleton}
```

REQUIREMENTS:
- Output ONLY a complete valid Python file, no markdown fences, no commentary.
- First line: `from manim import *`
- Second line group: `from _common import (...)` importing every helper you use.
- Module-level: `TARGET_DURATION = audio_duration("{sc.basename}", {sc.fallback_duration:.1f})`
- Exactly one class: `class {sc.classname}(Scene):` with a single `construct` method.
- `self.add(tech_background())` at the very start of `construct`.
- Wrap every user-visible string with `L("teks Indonesia", "english text")`.
- Avoid orientation words ("left", "right", "above", "below") in any visible string.
- End `construct` with `self.wait(max(0.5, TARGET_DURATION - elapsed))` where
  `elapsed` is the sum of the `run_time` values you used.
- Use only helpers documented in the `_common` source above; do not import
  anything else.
- Keep visuals clean and instructional. Use semantic colors: DANGER for
  problems/naive code, OK for improved/refactored states, HIGHLIGHT for the
  currently-discussed element, PRIMARY for headline statements, ACCENT for
  section labels and emphasis.
- `title_bar`, `title_text`, `body_text`, `section_label`, and `bullet_list`
  all feed their text into Pango `MarkupText`, which parses Pango XML markup.
  Every `&` in those strings MUST be written as `&amp;`, every `<` as `&lt;`,
  every `>` as `&gt;`. Do not put raw ampersands or angle brackets inside
  any string that ends up in `L(...)`, `title_bar(...)`, `title_text(...)`,
  `body_text(...)`, `section_label(...)`, or `bullet_list([...])` items.
- Code shown via `code_card(...)` is NOT Pango markup; raw `&`, `<`, `>`
  are fine there.

Return ONLY the Python file contents.
"""


_FENCE_BLOCK_RE = re.compile(r"```(?:python|py)?[ \t]*\n(.*?)```", re.S | re.I)


def _strip_code_fences(text: str) -> str:
    """Pull a clean Python source out of an AI reply.

    Handles the two ways the model strays from "output only the file":
      1. It wraps the file in a ``` fence (optionally with prose around it) —
         take the first fenced block.
      2. It prepends a prose sentence before the code (e.g. "Here is scene 6,
         ~30s:") — the leading non-code line then makes `ast.parse` choke (a
         bare "30s" is an invalid decimal literal). The scene prompt mandates
         `from manim import *` as the first line, so we drop everything before
         the first import line.
    """
    text = text.strip()
    m = _FENCE_BLOCK_RE.search(text)
    if m:
        text = m.group(1).strip()
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines)
                  if ln.lstrip().startswith("from manim import")), None)
    if start is None:
        start = next((i for i, ln in enumerate(lines)
                      if ln.lstrip().startswith(("from ", "import ", "#!"))), None)
    if start:  # only trim when real preamble precedes the code (start > 0)
        text = "\n".join(lines[start:]).strip()
    return text


# Match a Python string literal — single or double quote, no triple, no backslash
# escapes — captured group is the inner content. Good enough for L(...) /
# MarkupText(...) call args, which is what the AI tends to put `&` in.
_STRING_LITERAL_RE = re.compile(r"(?P<q>['\"])(?P<body>[^'\"\\\n]*?)(?P=q)")
_KNOWN_ENTITIES = ("&amp;", "&lt;", "&gt;", "&quot;", "&apos;", "&#")


def _escape_unsafe_ampersands(src: str) -> str:
    """Walk through every short Python string literal in `src` and rewrite a
    bare `&` to `&amp;` unless it already starts a recognised XML entity.

    This is a guard against a recurring Pango/MarkupText failure mode: every
    helper in `_common.py` (title_bar, title_text, body_text, section_label,
    bullet_list, ...) feeds its argument straight into `MarkupText`, which
    parses Pango markup and rejects raw `&`.
    """

    def fix(match: re.Match) -> str:
        body = match.group("body")
        if "&" not in body:
            return match.group(0)
        out = []
        i = 0
        while i < len(body):
            ch = body[i]
            if ch == "&" and not any(
                body[i:].startswith(ent) for ent in _KNOWN_ENTITIES
            ):
                out.append("&amp;")
            else:
                out.append(ch)
            i += 1
        return f"{match.group('q')}{''.join(out)}{match.group('q')}"

    return _STRING_LITERAL_RE.sub(fix, src)


def _validate_scene_source(path: Path, src: str) -> None:
    """Parse `src` with the stdlib `ast`. Raise with a clear message if it
    isn't valid Python — better to fail at generation time than mid-render."""
    import ast

    try:
        ast.parse(src, filename=str(path))
    except SyntaxError as exc:
        raise SystemExit(
            f"AI-generated scene at {path} is not valid Python: "
            f"line {exc.lineno} col {exc.offset}: {exc.msg}\n"
            "Re-run with --force after editing the file, or delete it and "
            "re-run --stage scenes to regenerate."
        ) from exc


def ensure_scene_files(sb: Storyboard, output: Path, force: bool) -> Tuple[Path, Path]:
    """Make sure every scene .py exists under the materialised scenes dirs.

    Returns the resolved (landscape_dir, portrait_dir). After this step,
    `sb.scenes_landscape_dir` and `sb.scenes_portrait_dir` are updated to
    point at the locations actually used downstream.
    """
    landscape_dir = _materialize_scenes_dir(sb, output, "landscape")
    portrait_dir = _materialize_scenes_dir(sb, output, "portrait")
    sb.scenes_landscape_dir = landscape_dir
    sb.scenes_portrait_dir = portrait_dir

    skeleton_path = TEMPLATES_DIR / "scene_skeleton.py"
    skeleton = skeleton_path.read_text(encoding="utf-8") if skeleton_path.exists() else ""

    for orient, scenes_dir in (("landscape", landscape_dir), ("portrait", portrait_dir)):
        common_path = scenes_dir / "_common.py"
        common_src = common_path.read_text(encoding="utf-8") if common_path.exists() else ""
        for sc in sb.scenes:
            scene_path = scenes_dir / sc.file
            if scene_path.exists() and not force:
                continue
            if sb.ai_cli in ("", "none", None):
                raise SystemExit(
                    f"Scene file {scene_path} is missing and no ai_cli is "
                    "configured to generate it. Either drop the .py in place "
                    "or set `ai_cli: claude` in the storyboard front-matter."
                )
            log(f"  ai-generate {orient}/{sc.file} via {sb.ai_cli}…")
            _t = time.monotonic()
            prompt = _build_scene_prompt(sb, sc, orient, skeleton, common_src)
            scene_src = run_ai_cli(sb.ai_cli, prompt)
            scene_src = _strip_code_fences(scene_src)
            if not scene_src.strip():
                raise SystemExit(f"AI returned empty source for {scene_path}")
            scene_src = _escape_unsafe_ampersands(scene_src)
            _validate_scene_source(scene_path, scene_src)
            scene_path.write_text(scene_src.rstrip() + "\n", encoding="utf-8")
            log(f"    ↳ {orient}/{sc.file} in {time.monotonic() - _t:.1f}s")
    return landscape_dir, portrait_dir


# --- Pipeline steps -------------------------------------------------------


def write_narration_scripts(sb: Storyboard, output: Path) -> None:
    for lang in sb.languages:
        d = output / "scripts" / lang
        d.mkdir(parents=True, exist_ok=True)
    for sc in sb.scenes:
        for lang in sb.languages:
            text = ensure_narration(sb, sc, lang, output=output)
            (output / "scripts" / lang / f"{sc.basename}.txt").write_text(
                text.strip() + "\n", encoding="utf-8"
            )


def _ffprobe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1",
        str(path),
    ])
    return float(out.strip())


def _resolve_voice(sb: Storyboard, lang: str) -> str:
    """The voice for a language: the storyboard's `voices[lang]` if set,
    otherwise the provider's default (Ardi for edge, Iapetus for Gemini)."""
    voice = sb.voices.get(lang)
    if voice:
        return voice
    if sb.tts_provider == "edge":
        return DEFAULT_EDGE_VOICE
    return DEFAULT_GEMINI_VOICE


def _resolve_gemini_key(sb: Storyboard) -> "str | None":
    """Resolve the Gemini API key from the storyboard / CLI override
    (`sb.gemini_api_key`), then `$GEMINI_API_KEY`, then a `.env` at the repo
    root. Returns None if none is found."""
    if sb.gemini_api_key:
        return sb.gemini_api_key
    env_value = os.environ.get("GEMINI_API_KEY")
    if env_value:
        return env_value
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            if key.strip() == "GEMINI_API_KEY":
                return val.strip().strip('"').strip("'")
    return None


def generate_audio(sb: Storyboard, output: Path, force: bool) -> None:
    if sb.tts_provider == "edge":
        _generate_audio_edge(sb, output, force)
    elif sb.tts_provider in {"gemini", "google", "google_chirp", "chirp"}:
        # `google`/`google_chirp`/`chirp` are legacy aliases for the Gemini path.
        _generate_audio_gemini(sb, output, force)
    else:
        raise SystemExit(f"Unknown tts_provider '{sb.tts_provider}'.")


def _generate_audio_edge(sb: Storyboard, output: Path, force: bool) -> None:
    if not EDGE_TTS_BIN.exists():
        raise SystemExit(f"edge-tts not found at {EDGE_TTS_BIN}")
    for lang in sb.languages:
        voice = _resolve_voice(sb, lang)
        audio_dir = output / "audio" / lang
        srt_dir = output / "subtitles" / lang
        audio_dir.mkdir(parents=True, exist_ok=True)
        srt_dir.mkdir(parents=True, exist_ok=True)
        for sc in sb.scenes:
            mp3 = audio_dir / f"{sc.basename}.mp3"
            srt = srt_dir / f"{sc.basename}.srt"
            if mp3.exists() and srt.exists() and not force:
                continue
            log(f"  edge-tts {voice} -> {lang}/{sc.basename}…")
            _t = time.monotonic()
            subprocess.run(
                [
                    str(EDGE_TTS_BIN),
                    "--voice", voice,
                    "--text", sc.narration[lang],
                    "--write-media", str(mp3),
                    "--write-subtitles", str(srt),
                ],
                check=True,
            )
            log(f"    ↳ {lang}/{sc.basename}.mp3 in {time.monotonic() - _t:.1f}s")


# --- Gemini TTS -----------------------------------------------------------
#
# The Gemini API returns raw PCM audio only (no timing events), so we pipe the
# PCM through ffmpeg into MP3 and estimate the SRT by splitting the script into
# sentences and allocating time proportionally to sentence length. This mirrors
# the implementation in the sibling `slides_narrator` project.


def _fmt_ts(seconds: float) -> str:
    """Format seconds as an SRT timestamp: HH:MM:SS,mmm."""
    if seconds < 0:
        seconds = 0.0
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class GeminiQuotaError(RuntimeError):
    """Raised when Gemini returns a 429 daily-quota exhaustion (not retryable
    within the run — the per-day limit only resets on a daily boundary)."""


def _gemini_error_message(detail: str) -> str:
    """Pull a concise message out of a Gemini error body (the JSON's
    error.message), falling back to a truncated blob."""
    try:
        return str(json.loads(detail)["error"]["message"]).strip()[:240]
    except (ValueError, KeyError, TypeError):
        return " ".join(detail.split())[:240]


def _is_daily_quota(detail: str) -> bool:
    """True when a 429 body is a per-day quota (e.g. the metric
    generate_requests_per_model_per_day), which cannot recover in seconds."""
    norm = re.sub(r"[\s_]+", "", detail.lower())
    return "perday" in norm


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _write_estimated_srt(text: str, duration: float, srt: Path) -> None:
    """Build a per-scene SRT by splitting narration into sentences and
    allocating the measured audio duration in proportion to sentence length."""
    sentences = _split_sentences(text)
    if not sentences:
        srt.write_text("", encoding="utf-8")
        return
    weights = [max(1, len(s)) for s in sentences]
    total = sum(weights) or 1
    elapsed = 0
    pieces: List[str] = []
    for idx, (sentence, weight) in enumerate(zip(sentences, weights), start=1):
        start = duration * elapsed / total
        elapsed += weight
        end = duration * elapsed / total
        if idx == len(sentences):
            end = duration
        pieces.append(f"{idx}\n{_fmt_ts(start)} --> {_fmt_ts(end)}\n{sentence}\n")
    srt.write_text("\n".join(pieces), encoding="utf-8")


def _gemini_synth(text: str, api_key: str, model: str, voice: str,
                  timeout: float) -> "Tuple[bytes, int]":
    """Return (pcm_s16le_bytes, sample_rate). Raises RuntimeError on failure."""
    body = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}
            },
        },
    }
    req = urllib.request.Request(
        GEMINI_TTS_ENDPOINT.format(model=model),
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        msg = _gemini_error_message(detail)
        if e.code == 429 and _is_daily_quota(detail):
            raise GeminiQuotaError(msg) from e
        raise RuntimeError(f"gemini HTTP {e.code}: {msg}") from e
    try:
        inline = data["candidates"][0]["content"]["parts"][0]["inlineData"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"gemini: no audio in response: {str(data)[:400]}") from e
    pcm = base64.b64decode(inline["data"])
    rate = 24000
    for tok in inline.get("mimeType", "").split(";"):
        if "rate=" in tok:
            try:
                rate = int(tok.split("rate=")[1])
            except ValueError:
                pass
    return pcm, rate


def _gemini_tts_one(text: str, mp3: Path, srt: Path, api_key: str, model: str,
                    voice: str, timeout: float) -> None:
    pcm, rate = _gemini_synth(text, api_key, model, voice, timeout)
    if not pcm:
        raise RuntimeError("gemini produced 0-byte audio")
    tmp_mp3 = mp3.with_suffix(mp3.suffix + ".part")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", "pipe:0",
             "-c:a", "libmp3lame", "-q:a", "2", "-f", "mp3", str(tmp_mp3)],
            input=pcm, check=True,
        )
        if tmp_mp3.stat().st_size == 0:
            raise RuntimeError("ffmpeg produced 0-byte mp3")
        tmp_mp3.replace(mp3)
    except BaseException:
        try:
            tmp_mp3.unlink()
        except FileNotFoundError:
            pass
        raise
    _write_estimated_srt(text, _ffprobe_duration(mp3), srt)


def _generate_audio_gemini(sb: Storyboard, output: Path, force: bool,
                           retries: int = 2, wait: float = 5.0,
                           timeout: float = 180.0) -> None:
    api_key = _resolve_gemini_key(sb)
    if not api_key:
        raise SystemExit(
            "gemini TTS requires an API key. Set GEMINI_API_KEY in the "
            "environment or in a .env at the repo root, set `gemini_api_key:` "
            "in the storyboard front-matter, or pass --gemini-api-key."
        )
    for lang in sb.languages:
        voice = _resolve_voice(sb, lang)
        audio_dir = output / "audio" / lang
        srt_dir = output / "subtitles" / lang
        audio_dir.mkdir(parents=True, exist_ok=True)
        srt_dir.mkdir(parents=True, exist_ok=True)
        for sc in sb.scenes:
            mp3 = audio_dir / f"{sc.basename}.mp3"
            srt = srt_dir / f"{sc.basename}.srt"
            if mp3.exists() and srt.exists() and not force:
                continue
            log(f"  gemini {sb.gemini_model}/{voice} -> {lang}/{sc.basename}…")
            _t = time.monotonic()
            attempts = retries + 1
            for attempt in range(1, attempts + 1):
                try:
                    _gemini_tts_one(sc.narration[lang], mp3, srt, api_key,
                                    sb.gemini_model, voice, timeout)
                    break
                except GeminiQuotaError as e:
                    # A per-day quota won't recover in seconds — fail fast with
                    # actionable guidance instead of burning retries.
                    raise SystemExit(
                        f"Gemini daily quota exhausted at {lang}/{sc.basename}: {e}\n"
                        f"The free tier caps the preview TTS model "
                        f"({sb.gemini_model}) at a low number of requests/day. Options:\n"
                        "  • finish now for free with  --tts edge  "
                        "(no quota; voice id-ID-ArdiNeural)\n"
                        "  • re-run after the daily quota resets — already-generated "
                        "audio is cached, so it resumes where it stopped\n"
                        "  • if you enabled billing, make sure the GEMINI_API_KEY in "
                        ".env belongs to the billed project (preview TTS models can "
                        "still keep low daily caps)."
                    )
                except BaseException as e:  # noqa: BLE001
                    if attempt >= attempts:
                        raise SystemExit(
                            f"gemini TTS failed for {lang}/{sc.basename} after "
                            f"{attempts} attempts: {str(e)[:160]}"
                        )
                    delay = wait * (2 ** (attempt - 1))  # exponential backoff
                    log(f"    retry {attempt}/{attempts} ({type(e).__name__}: "
                        f"{str(e)[:120]}); waiting {delay:.0f}s…")
                    time.sleep(delay)
            log(f"    ↳ {lang}/{sc.basename}.mp3 in {time.monotonic() - _t:.1f}s")


def _extract_layout_issues(text: str) -> str:
    """Pull the layout-violation summary out of a failed render's output.

    The scene `_common.py` raises `LayoutError: [layout] N issue(s) in Cls:
    OVERFLOW: …; OVERLAP: …` in strict mode and also prints `  - <issue>`
    bullet lines. Prefer the single-line LayoutError message; fall back to the
    bullets. Returns "" when the failure wasn't a layout violation."""
    lines = text.splitlines()
    for line in lines:
        s = line.strip()
        if s.startswith("LayoutError:"):
            return s[len("LayoutError:"):].strip()
    bullets = [ln.strip()[2:].strip() for ln in lines if ln.strip().startswith("- ")]
    if bullets and any("[layout]" in ln for ln in lines):
        return "; ".join(bullets)
    return ""


def _build_layout_repair_prompt(sb: Storyboard, sc: Scene, orient: str,
                                skeleton: str, common_src: str,
                                current_src: str, issues: str) -> str:
    safe_note = ""
    if orient == "portrait":
        safe_note = (" and entirely above SHORTS_SAFE_BOTTOM = -4.8 (the bottom "
                     "2/10 reserved for caption overlays)")
    base = _build_scene_prompt(sb, sc, orient, skeleton, common_src)
    return base + f"""

LAYOUT REPAIR — IMPORTANT:
A previous version of this exact scene FAILED an automated layout check with:
{issues}

Here is that failing scene source:
```python
{current_src}
```

Produce a corrected COMPLETE scene file that preserves the same content, timing
(`TARGET_DURATION`, `run_time` values, final wait) and instructional intent, but
guarantees every visible text mobject stays fully inside the frame{safe_note},
with no two text labels overlapping by more than half the smaller one. Fix it by
repositioning, reducing font `size=`, wrapping long strings onto multiple lines,
arranging with VGroup(...).arrange(...), or (portrait) fit_to_shorts_area(...).
Return ONLY the corrected Python file, no fences, no commentary.
"""


def _repair_scene_layout(sb: Storyboard, sc: Scene, orient: str,
                         scene_path: Path, issues: str) -> None:
    """Ask the AI CLI to fix a scene that failed the layout check, validate the
    reply, and overwrite the scene file in place."""
    scenes_dir = scene_path.parent
    common_path = scenes_dir / "_common.py"
    common_src = common_path.read_text(encoding="utf-8") if common_path.exists() else ""
    skeleton_path = TEMPLATES_DIR / "scene_skeleton.py"
    skeleton = skeleton_path.read_text(encoding="utf-8") if skeleton_path.exists() else ""
    current_src = scene_path.read_text(encoding="utf-8")
    prompt = _build_layout_repair_prompt(
        sb, sc, orient, skeleton, common_src, current_src, issues
    )
    new_src = _strip_code_fences(run_ai_cli(sb.ai_cli, prompt))
    if not new_src.strip():
        raise SystemExit(f"AI returned empty source repairing {scene_path}")
    new_src = _escape_unsafe_ampersands(new_src)
    _validate_scene_source(scene_path, new_src)
    scene_path.write_text(new_src.rstrip() + "\n", encoding="utf-8")


def render_manim(sb: Storyboard, output: Path, lang: str, orient: str, force: bool,
                 check_layout: str = "off", repair_attempts: int = 0) -> None:
    scenes_dir = sb.scenes_landscape_dir if orient == "landscape" else sb.scenes_portrait_dir
    if not scenes_dir.exists():
        raise SystemExit(f"scenes_{orient}_dir does not exist: {scenes_dir}")
    video_dir = output / "video" / lang / orient
    video_dir.mkdir(parents=True, exist_ok=True)
    media_dir = output / "manim_media" / lang / orient
    media_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["MANIM_LANG"] = lang
    env["LANG_CODE"] = lang
    env["MANIM_AUDIO_DIR"] = str((output / "audio").resolve())
    # The scene _common.py reads this to run its layout self-check (overflow /
    # clipping / overlap). "strict" makes a violation fail the render.
    env["MANIM_CHECK_LAYOUT"] = check_layout
    if not MANIM_BIN.exists():
        raise SystemExit(f"manim binary not found at {MANIM_BIN}")
    for sc in sb.scenes:
        dest = video_dir / f"{sc.basename}.mp4"
        if dest.exists() and not force:
            continue
        scene_path = scenes_dir / sc.file
        if not scene_path.exists():
            raise SystemExit(f"Scene file missing: {scene_path}")
        cmd: List[str] = [str(MANIM_BIN)]
        if orient == "landscape":
            w, h = sb.resolution_landscape
            cmd += ["--resolution", f"{w},{h}"]
        cmd += [
            "--fps", str(sb.fps),
            "--media_dir", str(media_dir),
            str(scene_path), sc.classname,
        ]
        log(f"  render {lang}/{orient}/{sc.basename}::{sc.classname}…")
        _t = time.monotonic()
        # In strict mode a layout violation aborts the render. When AI repair is
        # enabled, feed the violation back to the CLI, regenerate the scene, and
        # re-render — up to repair_attempts times before giving up.
        max_repairs = repair_attempts if check_layout == "strict" else 0
        for attempt in range(max_repairs + 1):
            proc = subprocess.run(cmd, env=env, cwd=str(scenes_dir),
                                  capture_output=True, text=True)
            if proc.stdout:
                sys.stdout.write(proc.stdout)
            if proc.stderr:
                sys.stderr.write(proc.stderr)
            if proc.returncode == 0:
                break
            issues = _extract_layout_issues((proc.stdout or "") + (proc.stderr or ""))
            can_repair = (issues and attempt < max_repairs
                          and sb.ai_cli not in ("", "none", None))
            if not can_repair:
                if issues and attempt >= max_repairs > 0:
                    raise SystemExit(
                        f"Layout check still failing for {orient}/{sc.basename} "
                        f"after {max_repairs} AI repair attempt(s): {issues}"
                    )
                raise subprocess.CalledProcessError(proc.returncode, cmd)
            log(f"    layout violation, repairing {orient}/{sc.file} via "
                f"{sb.ai_cli} (attempt {attempt + 1}/{max_repairs})… {issues}")
            _repair_scene_layout(sb, sc, orient, scene_path, issues)
        log(f"    ↳ {lang}/{orient}/{sc.basename}.mp4 in {time.monotonic() - _t:.1f}s")

        stem = scene_path.stem
        candidates = list((media_dir / "videos" / stem).rglob(f"{sc.classname}.mp4"))
        if not candidates:
            raise SystemExit(
                f"Could not find Manim render output for {scene_path}::{sc.classname}"
            )
        # Pick the newest if multiple qualities ended up there.
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        shutil.copy2(candidates[0], dest)


def mux_clips(sb: Storyboard, output: Path, lang: str, orient: str, force: bool) -> None:
    clip_dir = output / "clips" / lang / orient
    clip_dir.mkdir(parents=True, exist_ok=True)
    for sc in sb.scenes:
        video = output / "video" / lang / orient / f"{sc.basename}.mp4"
        audio = output / "audio" / lang / f"{sc.basename}.mp3"
        clip = clip_dir / f"{sc.basename}.mp4"
        if clip.exists() and not force:
            continue
        if not video.exists() or not audio.exists():
            raise SystemExit(f"Missing inputs for muxing {clip}: {video}, {audio}")
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", str(video), "-i", str(audio),
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                "-af", "aresample=48000,pan=stereo|c0=c0|c1=c0",
                "-shortest", "-movflags", "+faststart",
                str(clip),
            ],
            check=True,
        )


def concat_final(sb: Storyboard, output: Path, lang: str, orient: str) -> Path:
    clip_dir = output / "clips" / lang / orient
    list_path = clip_dir / "concat_list.txt"
    list_path.write_text(
        "\n".join(f"file '{sc.basename}.mp4'" for sc in sb.scenes) + "\n",
        encoding="utf-8",
    )
    final_dir = output / "final" / lang
    final_dir.mkdir(parents=True, exist_ok=True)
    final_path = final_dir / f"{sb.title}_{orient}.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-r", str(sb.fps),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart",
            str(final_path),
        ],
        check=True,
    )
    return final_path


def merge_srts(sb: Storyboard, output: Path, lang: str) -> Path:
    import srt as _srt  # imported lazily so check_dependencies can install it first

    srt_dir = output / "subtitles" / lang
    merged: List = []
    offset = timedelta(0)
    idx = 1
    pick_orient = "landscape" if "landscape" in sb.orientations else sb.orientations[0]
    for sc in sb.scenes:
        clip = output / "clips" / lang / pick_orient / f"{sc.basename}.mp4"
        dur = timedelta(seconds=_ffprobe_duration(clip))
        srt_path = srt_dir / f"{sc.basename}.srt"
        if srt_path.exists():
            subs = list(_srt.parse(srt_path.read_text(encoding="utf-8")))
            for sub in subs:
                merged.append(
                    _srt.Subtitle(
                        index=idx,
                        start=sub.start + offset,
                        end=sub.end + offset,
                        content=sub.content,
                    )
                )
                idx += 1
        offset += dur
    out_path = srt_dir / f"{sb.title}.srt"
    out_path.write_text(_srt.compose(merged), encoding="utf-8")
    return out_path


# --- YouTube publishing metadata (youtube.txt per language) ---------------
#
# Asks the configured AI CLI to write a title/description/keywords block from a
# language's narration transcript, then sanitises and clamps each field to
# YouTube's limits. Mirrors the sibling `slides_narrator` project, adapted to
# this project's bilingual layout: one file per language at
# <output>/youtube/<lang>/youtube.txt. It's a trailing nice-to-have — a failure
# here never aborts the build.

YT_TITLE_MAX = 100
YT_DESC_MAX = 5000
YT_KEYWORDS_MAX = 500

# Emoji / pictograph ranges to strip (kept narrow so ordinary punctuation like
# em dash, ellipsis or curly quotes survives).
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U0001F1E6-\U0001F1FF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U00002B00-\U00002BFF"
    "\U0000FE00-\U0000FE0F"
    "\U00002190-\U000021FF"
    "]+",
    flags=re.UNICODE,
)


def _tidy_ws(text: str) -> str:
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" *\n", "\n", text)
    return text.strip()


def _strip_emoji(text: str) -> str:
    """Remove emoji/pictographs but keep hashtags and ordinary punctuation."""
    return _tidy_ws(_EMOJI_RE.sub("", text))


def _strip_emoji_hashtags(text: str) -> str:
    """For the title: strip emoji AND #hashtags (but keep things like 'C#')."""
    text = _EMOJI_RE.sub("", text)
    text = re.sub(r"(?<!\S)#\w+", "", text)
    return _tidy_ws(text)


def _cap_hashtags(text: str, max_tags: int = 15) -> str:
    """YouTube ignores ALL hashtags once a description has more than 15, so drop
    any beyond the 15th rather than risk losing them all."""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        return m.group(0) if count <= max_tags else ""

    return _tidy_ws(re.sub(r"(?<!\S)#\w+", repl, text))


def _clamp(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    sp = cut.rfind(" ")
    if sp >= limit - 20:  # snap to a word boundary if one is close to the end
        cut = cut[:sp]
    return cut.rstrip()


def _clamp_keywords(keywords: str, limit: int = YT_KEYWORDS_MAX) -> str:
    tags = [t.strip() for t in keywords.replace("\n", ",").split(",") if t.strip()]
    out: List[str] = []
    total = 0
    for tag in tags:
        add = len(tag) + (2 if out else 0)  # account for the ", " joiner
        if total + add > limit:
            break
        out.append(tag)
        total += add
    return ", ".join(out)


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            raise
        return json.loads(m.group(0))


def _youtube_prompt(transcript: str, lang: str) -> str:
    lang_name = {"id": "Indonesian", "en": "English"}.get(lang, lang)
    return (
        "You are writing YouTube publishing metadata for a narrated tutorial "
        f"video. Base it ONLY on the narration transcript below. Write the "
        f'"title" and "description" in {lang_name}.\n\n'
        'Return ONE JSON object with exactly these keys: "title", "description", '
        '"keywords".\n'
        "- title: at most 100 characters; put the most important, searchable "
        "terms in the first ~70 characters; no emoji; NO hashtags.\n"
        "- description: at most 5000 characters; no emoji. Start with a strong "
        "hook in the first ~157 characters, then a short overview and a bulleted "
        'list (plain "- " lines) of what the video covers. END with one final '
        "line of 5 to 10 relevant hashtags as single words with no spaces "
        "(e.g. #Pythagoras #Mathematics). Use at most 15 hashtags, and put "
        "hashtags ONLY here in the description, never in the title.\n"
        "- keywords: a comma-separated list of plain tags (NO '#'); total length "
        "at most 500 characters; each tag at most 30 characters; mix "
        f"{lang_name} and English technical terms.\n\n"
        "Output ONLY the JSON object. No code fence, no commentary.\n\n"
        "Transcript:\n" + transcript
    )


def _youtube_text(title: str, description: str, keywords: str) -> str:
    return (
        f"TITLE\n{title.strip()}\n\n"
        f"DESCRIPTION\n{description.strip()}\n\n"
        f"KEYWORDS\n{keywords.strip()}\n"
    )


def _read_transcript(sb: Storyboard, output: Path, lang: str) -> str:
    """Concatenate a language's per-scene narration scripts in scene order."""
    parts = []
    for sc in sb.scenes:
        p = output / "scripts" / lang / f"{sc.basename}.txt"
        if p.exists():
            t = p.read_text(encoding="utf-8").strip()
            if t:
                parts.append(t)
        elif sc.narration.get(lang, "").strip():
            parts.append(sc.narration[lang].strip())
    return "\n\n".join(parts)


def generate_youtube(sb: Storyboard, output: Path, force: bool) -> None:
    """Write <output>/youtube/<lang>/youtube.txt for each language. Never raises
    on AI/parse failure — the video itself is unaffected."""
    for lang in sb.languages:
        out_path = output / "youtube" / lang / "youtube.txt"
        if out_path.exists() and not force:
            print(f"  youtube/{lang}/youtube.txt exists — skipping (use --force)")
            continue
        transcript = _read_transcript(sb, output, lang)
        if not transcript:
            print(f"  no narration for {lang} — skipping youtube.txt")
            continue
        try:
            raw = run_ai_cli(sb.ai_cli, _youtube_prompt(transcript, lang))
            meta = _extract_json(raw)
        except (SystemExit, RuntimeError, json.JSONDecodeError, OSError) as e:
            print(f"  youtube metadata for {lang} failed ({type(e).__name__}: {e}); "
                  "skipping. The video itself is unaffected.")
            continue
        title = _clamp(_strip_emoji_hashtags(str(meta.get("title", ""))), YT_TITLE_MAX)
        # Description keeps hashtags (emoji stripped, capped at 15 so YouTube honours them).
        desc = _clamp(_cap_hashtags(_strip_emoji(str(meta.get("description", "")))), YT_DESC_MAX)
        keywords = _clamp_keywords(str(meta.get("keywords", "")), YT_KEYWORDS_MAX)
        if not title or not desc:
            print(f"  AI returned empty title/description for {lang}; skipping youtube.txt")
            continue
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(_youtube_text(title, desc, keywords), encoding="utf-8")
        log(f"  -> {out_path} (title {len(title)}/{YT_TITLE_MAX}, "
            f"desc {len(desc)}/{YT_DESC_MAX}, keywords {len(keywords)}/{YT_KEYWORDS_MAX})")


# --- CLI ------------------------------------------------------------------


def _peek_ai_cli(storyboard_path: Path) -> str | None:
    """Read just the YAML front-matter to find ai_cli without importing yaml.

    We do this before check_dependencies() runs so the dep check can decide
    whether the AI CLI is required at all. Falls back to None on any parse
    error; check_dependencies() then won't enforce the AI CLI requirement.
    """
    try:
        text = storyboard_path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        return None
    for line in m.group(1).splitlines():
        if line.strip().startswith("ai_cli:"):
            value = line.split(":", 1)[1].strip().strip('"').strip("'")
            return value or None
    return None


_WIPE_SUBDIRS = (
    "scripts",
    "audio",
    "subtitles",
    "video",
    "clips",
    "final",
    "scenes_landscape",
    "scenes_portrait",
    "manim_media",
    "assets",
    "youtube",
)


def _wipe_outputs(output: Path) -> None:
    """Delete every generator-owned subdirectory under `output`. Other files
    (a user-placed .gitignore, README, etc.) are left untouched."""
    removed = []
    for name in _WIPE_SUBDIRS:
        target = output / name
        if target.exists():
            shutil.rmtree(target)
            removed.append(name)
    if removed:
        print(f"  --force: wiped {', '.join(removed)} under {output}")
    else:
        print(f"  --force: nothing to wipe (output dir was already clean)")


def cmd_build(args: argparse.Namespace) -> None:
    _reset_clock()
    storyboard_path = Path(args.storyboard).resolve()
    need_ai_cli: str | None = None
    if not args.skip_dep_check:
        if args.no_ai_cli_check:
            need_ai_cli = None
        else:
            # CLI flag wins; otherwise fall back to whatever the storyboard declares.
            need_ai_cli = args.ai_cli or _peek_ai_cli(storyboard_path)
        check_dependencies(need_ai_cli=need_ai_cli)
    sb = parse_storyboard(storyboard_path)
    if args.ai_cli:
        sb.ai_cli = args.ai_cli
    # CLI overrides for TTS so the storyboard stays portable while the
    # invocation picks provider / voice / key.
    if args.tts:
        sb.tts_provider = args.tts
    if args.voice:
        # A single --voice applies to every language for this run; per-language
        # control still lives in the storyboard's `voices:` map.
        sb.voices = {lang: args.voice for lang in sb.languages}
    if args.gemini_api_key:
        sb.gemini_api_key = args.gemini_api_key
    if not args.skip_dep_check and sb.tts_provider in {
        "gemini", "google", "google_chirp", "chirp"
    } and not _resolve_gemini_key(sb):
        raise SystemExit(
            "gemini TTS selected but no API key found. Set GEMINI_API_KEY in the "
            "environment or in a .env at the repo root, set `gemini_api_key:` in "
            "the storyboard front-matter, or pass --gemini-api-key. "
            "Get a key at https://aistudio.google.com/apikey."
        )
    output_for_wipe = Path(args.output).resolve()
    if args.force and output_for_wipe.exists():
        _wipe_outputs(output_for_wipe)
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)

    print(f"Storyboard:   {args.storyboard}")
    print(f"Output dir:   {output}")
    print(f"Title:        {sb.title}")
    print(f"Languages:    {sb.languages}")
    print(f"Orientations: {sb.orientations}")
    print(f"Scenes:       {len(sb.scenes)} -> "
          f"{', '.join(s.basename for s in sb.scenes)}")
    print(f"TTS:          {sb.tts_provider} (voices: {sb.voices})")
    print(f"AI CLI:       {sb.ai_cli}")
    print(f"Scenes dirs:  landscape={sb.scenes_landscape_dir}, portrait={sb.scenes_portrait_dir}")
    if sb.max_duration is not None:
        budget = sum(s.fallback_duration for s in sb.scenes)
        print(f"Duration:     budget {budget:.0f}s / cap {sb.max_duration:.0f}s")
    print()

    if args.only:
        wanted = set(args.only)
        sb.scenes = [s for s in sb.scenes if s.basename in wanted]
        if not sb.scenes:
            raise SystemExit(f"No scenes matched --only filter: {args.only}")

    def _stage(label: str):
        """Print a stage header and return a closer that logs its duration."""
        log(label)
        start = time.monotonic()
        return lambda: log(f"  ✓ {label.split('] ', 1)[-1]} in {time.monotonic() - start:.1f}s")

    if args.stage in ("all", "scripts"):
        done = _stage("[1/8] write narration scripts (AI-generated when missing)")
        write_narration_scripts(sb, output)
        done()
    if args.stage in ("all", "audio"):
        done = _stage("[2/8] generate audio + per-scene SRTs")
        # Make sure narration is populated even if --stage audio is run alone.
        for sc in sb.scenes:
            for lang in sb.languages:
                ensure_narration(sb, sc, lang, output=output)
        generate_audio(sb, output, args.force)
        done()
    if args.stage in ("all", "scenes"):
        done = _stage("[3/8] materialize scene .py files (AI-generated when missing)")
        ensure_scene_files(sb, output, args.force)
        done()
    if args.stage in ("all", "render"):
        done = _stage("[4/8] render Manim scenes")
        # Render assumes scene .py files exist; populate dirs from defaults.
        ensure_scene_files(sb, output, force=False)
        for lang in sb.languages:
            for orient in sb.orientations:
                render_manim(sb, output, lang, orient, args.force,
                             check_layout=args.check_layout,
                             repair_attempts=args.layout_repair_attempts)
        done()
    if args.stage in ("all", "mux"):
        done = _stage("[5/8] mux clips (video + audio)")
        for lang in sb.languages:
            for orient in sb.orientations:
                mux_clips(sb, output, lang, orient, args.force)
        done()
    if args.stage in ("all", "concat"):
        done = _stage("[6/8] concat per-scene clips into final videos")
        for lang in sb.languages:
            for orient in sb.orientations:
                final = concat_final(sb, output, lang, orient)
                log(f"  -> {final}")
        done()
    if args.stage in ("all", "srt"):
        done = _stage("[7/8] merge per-scene SRTs into final SRTs")
        for lang in sb.languages:
            merged = merge_srts(sb, output, lang)
            log(f"  -> {merged}")
        done()
    if args.stage in ("all", "youtube") and not args.skip_youtube:
        done = _stage("[8/8] generate YouTube metadata (per language)")
        generate_youtube(sb, output, args.force)
        done()
    log(f"Done in {_clock()}.")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate a bilingual Manim tutorial video from a storyboard markdown file."
    )
    ap.add_argument("--storyboard", required=True, help="Path to storyboard markdown file")
    ap.add_argument("--output", required=True, help="Output directory (all intermediates go here)")
    ap.add_argument(
        "--stage",
        choices=["all", "scripts", "audio", "scenes", "render", "mux", "concat", "srt", "youtube"],
        default="all",
        help="Run only one stage of the pipeline (default: all)",
    )
    ap.add_argument(
        "--only", nargs="*", default=None,
        help="Restrict pipeline to these scene basenames (for testing one scene)",
    )
    ap.add_argument("--force", action="store_true", help="Rebuild artifacts even if they exist")
    ap.add_argument(
        "--ai-cli", choices=["claude", "codex"], default="claude",
        help="AI CLI used to fill in missing narration / scene .py files "
             "(default: claude). Overrides 'ai_cli' in the storyboard front-matter.",
    )
    ap.add_argument(
        "--tts", choices=["edge", "gemini"], default=None,
        help="Text-to-speech provider. edge is free/no-key with exact subtitle "
             "timing (default voice Ardi); gemini needs an API key and gives "
             "nicer voices with estimated subtitle timing (default voice Iapetus). "
             "Overrides 'tts_provider' in the storyboard front-matter when set.",
    )
    ap.add_argument(
        "--voice", default=None,
        help="Override the TTS voice for every language this run "
             "(e.g. id-ID-GadisNeural for edge, or Charon for gemini). "
             "Per-language control still lives in the storyboard's 'voices:' map.",
    )
    ap.add_argument(
        "--gemini-api-key", default=None,
        help="Gemini API key. Defaults to $GEMINI_API_KEY, then a .env at the "
             "repo root, then 'gemini_api_key:' in the storyboard front-matter.",
    )
    ap.add_argument(
        "--check-layout", choices=["off", "warn", "strict", "fit"], default="off",
        help="At render time, check each scene's text for off-frame overflow / "
             "clipping, portrait caption-zone violations, and text overlap. "
             "'warn' logs issues; 'strict' fails the render; 'fit' auto-scales / "
             "nudges overflowing text back inside the frame as it renders "
             "(default: off).",
    )
    ap.add_argument(
        "--layout-repair-attempts", type=int, default=2,
        help="With --check-layout strict, how many times to ask the AI CLI to "
             "fix a scene that fails the layout check and re-render it before "
             "giving up (default: 2; 0 disables AI repair).",
    )
    ap.add_argument(
        "--skip-youtube", action="store_true",
        help="Don't generate youtube/<lang>/youtube.txt (title/description/keywords)",
    )
    ap.add_argument(
        "--skip-dep-check", action="store_true",
        help="Don't validate / auto-install dependencies before building",
    )
    ap.add_argument(
        "--no-ai-cli-check", action="store_true",
        help="Skip the AI CLI presence check even if the storyboard declares one "
             "(use when you've already pre-filled every narration / scene .py)",
    )
    args = ap.parse_args()
    cmd_build(args)


if __name__ == "__main__":
    main()
