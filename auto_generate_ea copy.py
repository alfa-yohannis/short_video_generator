#!/usr/bin/env python3
"""Cron-driven enterprise-architecture video factory.

The ArchiMate / enterprise-architecture sibling of ``auto_generate_patterns.py``.
It drives the same short-video generator, but its to-do list, storyboard naming,
and the prompt it feeds the AI are all tuned for enterprise-architecture topics
(ArchiMate layers, viewpoints, frameworks) rather than software design patterns.

Each run (default mode):

1. Reads ``enterprise_architecture_todo.csv`` (no, name, category, status).
2. If ``MAX_PARALLEL_BUILDS`` generator processes are already running, exits;
   otherwise it starts one more (builds run in parallel). NOTE: the running count
   is taken over ``generate_video.py`` as a whole, so it is SHARED with the
   patterns factory — together they will not exceed this cap.
3. Picks the first pending (blank-status) topic, marks it "in progress", saves.
4. Generates a storyboard for it under ``storyboards/`` using the Claude CLI at
   ``xhigh`` effort (skipped if a valid one already exists), validating it parses.
   EA storyboards are named ``<slug>_storyboard.md`` (NO ``_pattern_`` infix). The
   prompt is chosen by topic: TOGAF / ADM rows get a process-flow arc (the ADM
   cycle, then inputs -> activities -> deliverables), while ArchiMate rows get the
   modeling-notation arc (locate the layer, its elements, their relationships).
5. Launches the short-video generator in a SEPARATE console window so you can
   watch it, building into ``tmp/<slug>/`` with:
   ``--tts edge --ai-cli claude --effort xhigh --refine-storyboard
   --validate-scenes --force``.
6. When that console finishes it calls this script back in ``--finalize`` mode,
   which marks the row "done" on success (or reverts it to pending on failure so
   the next cron run retries it).

Helper modes:
    --finalize NO --exit-code N   (called by the spawned console)
    --start NO                    (manually start a specific row now)
    --reset-stuck                 (clear any "in progress" rows back to pending)
    --status                      (print the to-do summary and exit)

Run it by hand in a terminal to test, or wire it to cron (every 2 hours).
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import fcntl
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# --- Layout (everything is derived from where this file lives) --------------
REPO = Path(__file__).resolve().parent
CSV_PATH = REPO / "enterprise_architecture_todo.csv"
STORYBOARDS = REPO / "storyboards"
TMP = REPO / "tmp"
VENV_PY = REPO / ".venv" / "bin" / "python"
GENERATOR = REPO / "video_generator" / "generate_video.py"
LOCK_PATH = TMP / ".auto_ea.lock"

STATUS_DONE = "done"
STATUS_IN_PROGRESS = "in progress"
FIELDNAMES = ["no", "name", "category", "status", "start_time", "end_time"]

# How many builds may run at once. Each cron run starts one more topic as long
# as fewer than this many generator processes are actually running. The count is
# shared with auto_generate_patterns.py (both run generate_video.py).
MAX_PARALLEL_BUILDS = 2

# Make the Claude / ffmpeg binaries findable even under cron's minimal PATH.
os.environ["PATH"] = os.pathsep.join([
    str(Path.home() / ".local" / "bin"),
    "/usr/local/bin", "/usr/bin", "/bin",
    os.environ.get("PATH", ""),
])

# Import the project's own (tested) Claude client + storyboard parser.
sys.path.insert(0, str(REPO / "video_generator"))
from vgen.ai_client import create_ai_client          # noqa: E402
from vgen.storyboard import StoryboardParser          # noqa: E402


# --- Small utilities --------------------------------------------------------
def log(msg: str) -> None:
    stamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{stamp}] {msg}", flush=True)


def slugify(name: str) -> str:
    """'ArchiMate Strategy Layer' -> 'archimate_strategy_layer'; drops '(...)'."""
    name = re.sub(r"\(.*?\)", " ", name)          # drop "(MVC)" etc.
    name = name.lower().replace("&", " and ")
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def storyboard_path(name: str) -> Path:
    # EA storyboards have no "_pattern_" infix, e.g. archimate_strategy_layer_storyboard.md
    return STORYBOARDS / f"{slugify(name)}_storyboard.md"


def output_dir(name: str) -> Path:
    return TMP / slugify(name)


class _Lock:
    """Best-effort single-instance lock for the short CSV-mutating section."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._fh = None

    def __enter__(self) -> "_Lock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path, "w")
        try:
            fcntl.flock(self._fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            log("another instance holds the lock — exiting.")
            sys.exit(0)
        return self

    def __exit__(self, *exc) -> None:
        if self._fh:
            fcntl.flock(self._fh, fcntl.LOCK_UN)
            self._fh.close()


# --- CSV read / write -------------------------------------------------------
def read_rows() -> List[Dict[str, str]]:
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for col in ("status", "start_time", "end_time"):
            r[col] = (r.get(col) or "").strip()
    return rows


def write_rows(rows: List[Dict[str, str]]) -> None:
    tmp = CSV_PATH.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in FIELDNAMES})
    tmp.replace(CSV_PATH)        # atomic-ish swap so a reader never sees a half file


def _now() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def update_row(no: str, **fields: str) -> None:
    """Set one or more columns on the row with the given `no`, then save."""
    rows = read_rows()
    for r in rows:
        if r["no"] == str(no):
            r.update(fields)
            break
    write_rows(rows)


# --- Storyboard generation --------------------------------------------------
# A compact reference in the SIMPLIFIED format (optional front-matter, plain `##`
# scene headings with an inline `(~Ns)` duration, the description right under the
# heading). This exemplar shows the ENTERPRISE-ARCHITECTURE house style: ArchiMate
# notation rather than code, official layer colors, a teaching arc that locates the
# topic, names its elements, joins them with relationships, ties them to the
# Motivation goals, and demonstrates them on a small, familiar example in English.
_EXEMPLAR = """\
---
title: archimate_strategy_layer
language: both
length: 2-3 minutes
---

# ArchiMate Strategy Layer

A short tutorial on the Strategy Layer of the ArchiMate enterprise-architecture
language. This is a modeling notation, not program code, so every scene is built
from labelled ArchiMate elements and relationships. Use ArchiMate's official layer
colors: Strategy orange, Motivation purple, Business yellow, Application cyan,
Technology green. The running example is small and familiar: a neighbourhood
restaurant that wants to grow by selling online. Keep the ArchiMate element-type
words in English (Resource, Capability, Course of Action, Value Stream, Goal,
Outcome) and name the example's own elements in English so the model reads
consistently. Use PRIMARY for titles, ACCENT for element-type and relationship
labels, HIGHLIGHT for the current element, OK for a finished, coherent model.
The English version should all be in English, including the examples.
Every scene must use the real, original ArchiMate element icons/symbols, never an
invented shape.

## Where It Sits (~18s)
Show "ArchiMate Strategy Layer" as a LARGE CENTERED title with a short subtitle
beneath it. Draw ArchiMate's layered framework as colored bands: Strategy on top in
orange, then Business in yellow, Application in cyan, Technology in green, with a
purple Motivation column alongside. HIGHLIGHT the Strategy band and note it
captures where the enterprise is headed.

## The Four Elements (~34s)
Introduce the vocabulary, grouped by ArchiMate aspect, each ACCENT-labelled.
Resource is the one active structure element, an asset drawn as a plain rectangle,
such as "Delivery App Account". The other three are behavior elements drawn as
rounded boxes: Capability, an ability such as "Online Sales"; Course of Action,
a chosen plan such as "Start Selling Online"; and Value Stream, a chevron of
value-adding stages such as "From Order to Delivery". Show a Resource assigned to a
Capability in OK.

## A Worked Example (~40s)
Assemble one model top to bottom. A purple Motivation Goal "Grow Revenue" is
realized by a Course of Action "Start Selling Online", which draws on Capabilities
"Online Sales" and "Delivery Service", each backed by an assigned Resource. A Value
Stream "From Order to Delivery" is served by those capabilities, and "Online Sales"
is realized by a "Delivery App" application in the layer below. Build it up in OK
with the active element in HIGHLIGHT.

## Conclusion (~28s)
Recap: the Strategy layer answers what the enterprise wants to achieve and with
what high-level means, using Resource, Capability, Course of Action, and Value
Stream, tied upward to the Motivation layer's goals. End with the line of sight on
screen: Resource -> Capability -> Course of Action -> Goal.
"""


# The TOGAF / ADM counterpart of _EXEMPLAR. TOGAF is a METHOD, not a notation, so
# this exemplar teaches a single ADM phase as a process flow — its place in the ADM
# cycle, then inputs -> activities -> deliverables — rather than from ArchiMate
# elements and relationships. Used for rows whose topic/category is TOGAF/ADM.
_EXEMPLAR_TOGAF = """\
---
title: adm_phase_b_business_architecture
language: both
length: 2-3 minutes
---

# TOGAF ADM Phase B: Business Architecture

A short tutorial on Phase B of the TOGAF Architecture Development Method (ADM).
TOGAF is a method, not a drawing notation, so every scene is built from the ADM
cycle and a process flow of inputs, activities, and deliverables - not from
ArchiMate boxes and relationships. The running example is small and familiar: a
growing restaurant business that wants to open new branches. Keep the TOGAF terms
in English (Architecture Vision, Business Architecture, Gap Analysis, Architecture
Definition Document, Stakeholder) and name the example's own details in English.
Use PRIMARY for titles, ACCENT for phase and deliverable labels, HIGHLIGHT for the
current step, OK for a finished, agreed result.
The English version should all be in English, including the examples.
Depict the ADM cycle accurately - the correct phase names in their correct order -
and use clear process/flow diagrams (inputs to activities to deliverables), never
an invented notation.

## Where It Sits in the ADM (~20s)
Show "TOGAF ADM Phase B: Business Architecture" as a LARGE CENTERED title with a
short subtitle beneath it. Draw the ADM as a cycle of phases - Preliminary, then A
through H, with Requirements Management at the hub - and HIGHLIGHT Phase B. Note it
is the first of the three core architecture-domain phases, following the approved
Architecture Vision.

## What Phase B Is For (~24s)
State the purpose: Phase B describes the baseline and target Business Architecture -
the organisation's structure, processes, functions, and roles - and the gap
between them. Ground it in the restaurant business: today one branch run by hand,
with a target of several branches sharing one way of working. The phase makes the
business side concrete before any application or technology is chosen.

## Inputs (~22s)
Lay out what flows into Phase B as ACCENT-labelled deliverables from earlier work:
the Architecture Vision and the Statement of Architecture Work from Phase A, the
Organisational Model, the applicable Architecture Principles, and existing
Architecture Repository content. HIGHLIGHT that Phase B refines what Phase A
approved rather than starting from a blank page.

## Key Steps (~34s)
Walk the activities as a process flow, one HIGHLIGHTed at a time: select reference
models and viewpoints; develop the Baseline Business Architecture (how the single
branch works today); develop the Target Business Architecture (how the branch
network should work); perform a Gap Analysis between baseline and target; define
candidate roadmap components; and resolve impacts across the architecture
landscape. Each step feeds the next in OK.

## Deliverables and a Worked Example (~42s)
Assemble the outputs the phase produces, building them up in OK. For the restaurant
business: a Baseline showing one owner doing ordering, cooking, and cashier work; a
Target showing a Branch Manager role, a standard Order-to-Serve process repeated per
branch, and a central Menu and Pricing function; a Gap Analysis naming what is
missing (a manager role, a standard process, shared menu data); and these gaps
captured in the Architecture Definition Document and as draft roadmap components.
HIGHLIGHT each deliverable as it lands.

## How It Connects, and Recap (~28s)
Close by placing Phase B back in the cycle: its agreed Target Business Architecture
and gaps feed Phase C (Information Systems) and Phase D (Technology), and every
change is checked against Requirements Management at the hub. Recap the flow of the
phase on screen: Inputs -> Baseline -> Target -> Gap Analysis -> Deliverables.
"""


def _build_prompt_archimate(name: str, category: str) -> str:
    title = slugify(name)
    return (
        "You are authoring a storyboard markdown file for an automated tutorial-"
        "video generator. Below is a COMPLETE example in the required format. "
        "Study its structure: a small YAML front-matter block, a `# Title` "
        "heading, a free-form brief, then one plain `## Scene Title (~Ns)` heading "
        "per scene with the scene's visual description written directly under it.\n\n"
        f"Produce a NEW storyboard explaining **{name}** (category: {category}) from "
        "the field of enterprise architecture, modelled with the ArchiMate language, "
        "in the SAME format and the same level of detail.\n\n"
        "Hard requirements:\n"
        f"- front-matter has exactly: `title: {title}`, `language: both`, "
        "`length: 2-3 minutes`.\n"
        f"- the `# ` title heading reads exactly `# {name}`.\n"
        "- do NOT include a `# Preparation` section. Instead, the brief (the prose "
        "right after the `# ` title, before the first `## ` scene) must state that "
        "every scene uses the real, original ArchiMate element icons/symbols, never "
        "an invented shape.\n"
        "- 6 to 8 scenes; each is a plain `## Human Title (~Ns)` heading (the "
        "`(~Ns)` is that scene's length in seconds) with the description right "
        "underneath. Do NOT write `## Scene:`, `**file:**`, `**fallback_duration:**`, "
        "`**class:**`, or `### description` — those are derived automatically.\n"
        "- the per-scene seconds must sum to between 120 and 180.\n"
        f"- the FIRST (intro) scene must present the topic name as the LARGE "
        f"CENTERED title (not only in the small top bar) — it reads exactly "
        f"`{name}`. A short subtitle may sit directly beneath it.\n"
        "- this is an ENTERPRISE-ARCHITECTURE MODELING tutorial, NOT program code: "
        "build every scene from labelled ArchiMate boxes and relationships, never "
        "source code. Use ArchiMate's official layer colors so the model reads as "
        "authentic — Strategy orange, Business yellow, Application cyan, Technology "
        "green, Motivation purple, Implementation and Migration pink.\n"
        "- follow the teaching arc for a modeling topic: locate it in the ArchiMate "
        "framework -> its purpose -> its vocabulary/elements, each with a short "
        "example -> the relationships that join them -> how it connects to the "
        "neighbouring layers (especially the Motivation layer's goals where "
        "relevant) -> ONE worked model that demonstrates the elements in a concrete "
        "case -> a conclusion.\n"
        "- use ONE concrete running example that is simple and familiar (for "
        "example a neighbourhood restaurant, a small shop, or a food-delivery "
        "service). Name the example's own elements in English, and keep the "
        "ArchiMate element-type words in English too (Resource, Capability, Goal, "
        "Business Process, Application Component, and so on). The English version "
        "should be entirely in English, including the examples.\n"
        "- descriptions ONLY (no narration text, no Manim/Python code blocks). "
        "Use semantic colors DANGER/OK/HIGHLIGHT/PRIMARY/ACCENT as the example does.\n"
        "- avoid orientation words (left/right/above/below) in any text meant to "
        "be shown or spoken.\n\n"
        "Output ONLY the raw markdown file content. No code fences, no commentary "
        "before or after.\n\n"
        "===== EXAMPLE STORYBOARD (format reference) =====\n"
        f"{_EXEMPLAR}\n"
        "===== END EXAMPLE =====\n"
    )


def _build_prompt_togaf(name: str, category: str) -> str:
    title = slugify(name)
    return (
        "You are authoring a storyboard markdown file for an automated tutorial-"
        "video generator. Below is a COMPLETE example in the required format. "
        "Study its structure: a small YAML front-matter block, a `# Title` "
        "heading, a free-form brief, then one plain `## Scene Title (~Ns)` heading "
        "per scene with the scene's visual description written directly under it.\n\n"
        f"Produce a NEW storyboard explaining **{name}** (category: {category}) from "
        "the TOGAF framework's Architecture Development Method (ADM), in the SAME "
        "format and the same level of detail.\n\n"
        "Hard requirements:\n"
        f"- front-matter has exactly: `title: {title}`, `language: both`, "
        "`length: 2-3 minutes`.\n"
        f"- the `# ` title heading reads exactly `# {name}`.\n"
        "- do NOT include a `# Preparation` section. Instead, the brief (the prose "
        "right after the `# ` title, before the first `## ` scene) must say to "
        "depict the ADM cycle accurately (the correct phase names in their correct "
        "order) and to use clear process/flow diagrams (inputs to activities to "
        "deliverables), never an invented notation.\n"
        "- 6 to 8 scenes; each is a plain `## Human Title (~Ns)` heading (the "
        "`(~Ns)` is that scene's length in seconds) with the description right "
        "underneath. Do NOT write `## Scene:`, `**file:**`, `**fallback_duration:**`, "
        "`**class:**`, or `### description` — those are derived automatically.\n"
        "- the per-scene seconds must sum to between 120 and 180.\n"
        f"- the FIRST (intro) scene must present the topic name as the LARGE "
        f"CENTERED title (not only in the small top bar) — it reads exactly "
        f"`{name}`. A short subtitle may sit directly beneath it.\n"
        "- this is a TOGAF METHOD tutorial, NOT a modeling notation and NOT program "
        "code: build every scene from the ADM cycle and process flows (a phase's "
        "position in the cycle, and its inputs -> activities -> outputs/deliverables), "
        "never from ArchiMate elements/relationships and never source code. Do NOT "
        "use ArchiMate's official layer colors; rely on the semantic colors below.\n"
        "- follow the teaching arc for a single ADM phase: show where the phase sits "
        "in the ADM cycle (the wheel) -> its purpose/objectives -> its inputs (the "
        "deliverables it receives from earlier phases) -> its key steps/activities -> "
        "its outputs/deliverables -> how it connects to the adjacent phases and to "
        "Requirements Management at the hub -> ONE worked example that walks the "
        "phase on a concrete case -> a conclusion/recap.\n"
        "- use ONE concrete running example that is simple and familiar (for "
        "example a neighbourhood restaurant, a small shop, or a food-delivery "
        "service) and describe it through the phase's activities and deliverables. "
        "Keep the TOGAF terms in English (Architecture Vision, Business "
        "Architecture, Gap Analysis, Architecture Definition Document, Stakeholder, "
        "and so on) and name the example's own details in English. The English "
        "version should be entirely in English, including the examples.\n"
        "- descriptions ONLY (no narration text, no Manim/Python code blocks). "
        "Use semantic colors DANGER/OK/HIGHLIGHT/PRIMARY/ACCENT as the example does.\n"
        "- avoid orientation words (left/right/above/below) in any text meant to "
        "be shown or spoken.\n\n"
        "Output ONLY the raw markdown file content. No code fences, no commentary "
        "before or after.\n\n"
        "===== EXAMPLE STORYBOARD (format reference) =====\n"
        f"{_EXEMPLAR_TOGAF}\n"
        "===== END EXAMPLE =====\n"
    )


def _is_togaf_topic(category: str, name: str) -> bool:
    """Route TOGAF / ADM topics to the process-flow track; everything else (e.g.
    ArchiMate layers) uses the modeling-notation track."""
    text = f"{category} {name}".lower()
    return "togaf" in text or "adm" in text


def _build_prompt(name: str, category: str) -> str:
    """Pick the storyboard prompt for the topic: a process/method arc for TOGAF
    ADM phases, or the ArchiMate notation arc for modeling topics."""
    if _is_togaf_topic(category, name):
        return _build_prompt_togaf(name, category)
    return _build_prompt_archimate(name, category)


_SB_FENCE_RE = re.compile(r"```(?:markdown|md)?\s*\n(.*?)```", re.DOTALL)


def _clean_storyboard(raw: str) -> str:
    """Turn a raw AI reply into storyboard markdown.

    NOTE: do NOT use vgen's strip_code_fences here — that one is a *Python*
    extractor that drops everything before the first `from `/`import ` line, and
    a storyboard description sentence can start with the word "from", which would
    delete the whole front-matter. Instead: unwrap a ``` fence if present, then
    trim any preamble before the storyboard actually starts (front-matter `---`,
    the `# ` title, or the first `## ` scene).
    """
    text = raw.strip()
    m = _SB_FENCE_RE.search(text)
    if m:
        text = m.group(1).strip()
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s == "---" or s.startswith("# ") or s.startswith("## "):
            text = "\n".join(lines[i:])
            break
    return text.strip() + "\n"


def ensure_storyboard(name: str, category: str) -> Path:
    """Return a valid storyboard path for `name`, generating it if needed."""
    path = storyboard_path(name)
    parser = StoryboardParser()
    if path.exists():
        try:
            parser.parse(path)
            log(f"reusing existing storyboard {path.name}")
            return path
        except (Exception, SystemExit) as exc:   # parser raises SystemExit on bad input
            log(f"existing {path.name} did not parse ({exc}); regenerating")

    client = create_ai_client("claude", "xhigh")
    prompt = _build_prompt(name, category)
    last_err: Optional[BaseException] = None
    for attempt in range(1, 4):
        log(f"generating storyboard for '{name}' (attempt {attempt}/3) via claude xhigh…")
        content = _clean_storyboard(client.generate(prompt))
        path.write_text(content, encoding="utf-8")
        try:
            parser.parse(path)
            log(f"storyboard written + validated: {path}")
            return path
        except (Exception, SystemExit) as exc:   # parser raises SystemExit on bad input
            last_err = exc
            log(f"  attempt {attempt} produced an invalid storyboard: {exc}")
    raise SystemExit(f"Could not produce a valid storyboard for '{name}': {last_err}")


# --- Spawning the generator in its own console ------------------------------
def _write_runner(no: str, name: str, sb: Path, out: Path) -> Path:
    runner = TMP / f"_runner_{slugify(name)}.sh"
    logfile = TMP / f"{slugify(name)}.log"
    title = f"▶ {name}"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        'export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"\n'
        # Set the window/tab title (cross-emulator OSC escape) so parallel builds
        # are tellable apart at a glance.
        f'printf "\\033]0;{title}\\007"\n'
        f'echo "[auto] building video for {name} ..."\n'
        # tee so the run is always logged, even in a GUI console; PIPESTATUS[0]
        # keeps the generator's real exit code (not tee's).
        f'{{ "{VENV_PY}" "{GENERATOR}" \\\n'
        f'  --storyboard "{sb}" \\\n'
        f'  --output "{out}" \\\n'
        '  --tts edge \\\n'
        '  --ai-cli claude --effort xhigh \\\n'
        '  --refine-storyboard \\\n'
        '  --validate-scenes \\\n'
        f'  --force; }} 2>&1 | tee "{logfile}"\n'
        'code=${PIPESTATUS[0]}\n'
        f'if [ "$code" = "0" ]; then printf "\\033]0;✓ {name}\\007"; '
        f'else printf "\\033]0;✗ {name}\\007"; fi\n'
        f'"{VENV_PY}" "{Path(__file__).resolve()}" --finalize "{no}" --exit-code "$code"\n'
        "echo\n"
        f'echo "[auto] {name} finished with exit code $code (log: {logfile})"\n'
        'if [ -t 0 ]; then echo "Press Enter to close this window..."; read _; fi\n',
        encoding="utf-8",
    )
    runner.chmod(0o755)
    return runner


def _terminal_argv(runner: Path, title: str) -> Optional[List[str]]:
    r = str(runner)
    # Each emulator gets its own title flag where supported; the OSC escape in the
    # runner is the cross-emulator fallback that also covers tab titles.
    candidates = [
        ("gnome-terminal", ["gnome-terminal", "--title", title, "--", "bash", r]),
        ("konsole", ["konsole", "-p", f"tabtitle={title}", "-e", "bash", r]),
        ("xfce4-terminal", ["xfce4-terminal", "--disable-server", "--title", title,
                            "-x", "bash", r]),
        ("mate-terminal", ["mate-terminal", "--title", title, "-x", "bash", r]),
        ("x-terminal-emulator", ["x-terminal-emulator", "-T", title, "-e", "bash", r]),
        ("xterm", ["xterm", "-T", title, "-e", "bash", r]),
    ]
    if not os.environ.get("DISPLAY"):
        return None
    for binary, argv in candidates:
        if shutil.which(binary):
            return argv
    return None


def launch_generator(no: str, name: str, sb: Path, out: Path) -> None:
    runner = _write_runner(no, name, sb, out)
    argv = _terminal_argv(runner, f"▶ {name}")
    if argv:
        log(f"launching generator in a new console: {argv[0]}")
        subprocess.Popen(argv, cwd=str(REPO), start_new_session=True)
        return
    # No GUI terminal available (e.g. headless cron) — run detached, log to file.
    logfile = TMP / f"{slugify(name)}.log"
    log(f"no GUI terminal/DISPLAY; running detached, log -> {logfile}")
    with open(logfile, "w", encoding="utf-8") as f:
        subprocess.Popen(["bash", str(runner)], cwd=str(REPO),
                         stdout=f, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, start_new_session=True)


# --- Modes ------------------------------------------------------------------
def _running_build_count() -> int:
    """Number of generator processes currently running (one per active build)."""
    try:
        out = subprocess.run(["pgrep", "-fc", f"{GENERATOR}"],
                             capture_output=True, text=True)
        return int((out.stdout or "0").strip() or 0)
    except Exception:        # noqa: BLE001 - pgrep missing/odd output -> assume none
        return 0


def mode_pick() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV not found: {CSV_PATH}")
    with _Lock(LOCK_PATH):
        # Parallel: don't gate on "in progress" status — gate on how many builds
        # are ACTUALLY running, so a crashed/stuck row can't block the queue.
        running = _running_build_count()
        if running >= MAX_PARALLEL_BUILDS:
            log(f"{running} build(s) already running (cap {MAX_PARALLEL_BUILDS}); "
                "skipping this run.")
            return
        rows = read_rows()
        pending = [r for r in rows if r["status"].lower() not in (STATUS_DONE, STATUS_IN_PROGRESS)]
        if not pending:
            log("nothing pending — all topics are done or in progress.")
            return
        row = pending[0]
        log(f"picked #{row['no']} {row['name']} ({row['category']}); "
            f"{running} build(s) already running.")
        update_row(row["no"], status=STATUS_IN_PROGRESS, start_time=_now(), end_time="")

    _build_and_launch(row)


def _build_and_launch(row: Dict[str, str]) -> None:
    """Generate the storyboard and launch the build console (outside any lock)."""
    try:
        sb = ensure_storyboard(row["name"], row["category"])
    except SystemExit as exc:
        log(f"storyboard step failed: {exc}; reverting #{row['no']} to pending.")
        update_row(row["no"], status="", start_time="", end_time="")
        raise
    out = output_dir(row["name"])
    out.mkdir(parents=True, exist_ok=True)
    launch_generator(row["no"], row["name"], sb, out)
    log(f"#{row['no']} {row['name']} is building in its own console; "
        "it will be marked done on success.")


def mode_start(no: str) -> None:
    """Manually start a specific row NOW, regardless of the first-pending order
    and the one-at-a-time guard (use to jump ahead or re-run a topic)."""
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV not found: {CSV_PATH}")
    with _Lock(LOCK_PATH):
        rows = read_rows()
        row = next((r for r in rows if r["no"] == str(no)), None)
        if row is None:
            raise SystemExit(f"No row with no={no} in {CSV_PATH.name}.")
        if row["status"].lower() == STATUS_IN_PROGRESS:
            log(f"#{no} {row['name']} is already in progress; not starting again.")
            return
        if row["status"].lower() == STATUS_DONE:
            log(f"#{no} {row['name']} is already done; re-starting it anyway.")
        log(f"manually starting #{row['no']} {row['name']} ({row['category']}).")
        update_row(row["no"], status=STATUS_IN_PROGRESS, start_time=_now(), end_time="")

    _build_and_launch(row)


def mode_finalize(no: str, exit_code: int) -> None:
    with _Lock(LOCK_PATH):
        if exit_code == 0:
            update_row(no, status=STATUS_DONE, end_time=_now())
            log(f"#{no} completed successfully — marked done.")
        else:
            update_row(no, status="", start_time="", end_time="")
            log(f"#{no} failed (exit {exit_code}) — reverted to pending for retry.")


def mode_reset_stuck() -> None:
    with _Lock(LOCK_PATH):
        rows = read_rows()
        n = 0
        for r in rows:
            if r["status"].lower() == STATUS_IN_PROGRESS:
                r["status"] = ""
                r["start_time"] = ""
                r["end_time"] = ""
                n += 1
        write_rows(rows)
    log(f"reset {n} stuck 'in progress' row(s) to pending.")


def mode_status() -> None:
    rows = read_rows()
    done = sum(1 for r in rows if r["status"].lower() == STATUS_DONE)
    prog = sum(1 for r in rows if r["status"].lower() == STATUS_IN_PROGRESS)
    pend = len(rows) - done - prog
    for r in rows:
        mark = {"done": "✓", "in progress": "…"}.get(r["status"].lower(), " ")
        times = ""
        if r["start_time"] or r["end_time"]:
            times = f"  {r['start_time'] or '—':<19} -> {r['end_time'] or '—':<19}"
        print(f"  [{mark}] {r['no']:>3}  {r['name']:<44} {r['category']:<22} {r['status']:<12}{times}")
    print(f"\n  {done} done · {prog} in progress · {pend} pending · {len(rows)} total")


def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--finalize", metavar="NO",
                   help="(internal) mark row NO done/pending based on --exit-code")
    p.add_argument("--exit-code", type=int, default=0,
                   help="exit code of the generator run (used with --finalize)")
    p.add_argument("--start", metavar="NO",
                   help="manually start a specific row NO now (jump ahead / re-run)")
    p.add_argument("--reset-stuck", action="store_true",
                   help="clear any 'in progress' rows back to pending")
    p.add_argument("--status", action="store_true",
                   help="print the to-do summary and exit")
    args = p.parse_args(argv)

    TMP.mkdir(parents=True, exist_ok=True)
    if args.status:
        mode_status()
    elif args.reset_stuck:
        mode_reset_stuck()
    elif args.finalize:
        mode_finalize(args.finalize, args.exit_code)
    elif args.start:
        mode_start(args.start)
    else:
        mode_pick()


if __name__ == "__main__":
    main()
