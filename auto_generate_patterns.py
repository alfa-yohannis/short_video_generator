#!/usr/bin/env python3
"""Cron-driven design-pattern video factory.

Each run (default mode):

1. Reads ``design_patterns_todo.csv`` (no, name, category, status).
2. If ``MAX_PARALLEL_BUILDS`` generator processes are already running, exits;
   otherwise it starts one more (builds run in parallel).
3. Picks the first pending (blank-status) pattern, marks it "in progress", and
   saves the CSV.
4. Generates a storyboard for it under ``storyboards/`` using the Claude CLI at
   ``xhigh`` effort (skipped if a valid one already exists), validating it parses.
5. Launches the short-video generator in a SEPARATE console window so you can
   watch it, building into ``tmp/<slug>/`` with:
   ``--tts edge --ai-cli claude --effort xhigh --refine-storyboard
   --validate-scenes --force``.
6. When that console finishes it calls this script back in ``--finalize`` mode,
   which marks the row "done" on success (or reverts it to pending on failure so
   the next cron run retries it).

Helper modes:
    --finalize NO --exit-code N   (called by the spawned console)
    --reset-stuck                 (clear any "in progress" rows back to pending)
    --status                      (print the to-do summary and exit)

Run it by hand in a terminal to test, or wire it to cron (every 2 hours) — see the
README banner printed by ``--help``.
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
CSV_PATH = REPO / "design_patterns_todo.csv"
STORYBOARDS = REPO / "storyboards"
TMP = REPO / "tmp"
VENV_PY = REPO / ".venv" / "bin" / "python"
GENERATOR = REPO / "video_generator" / "generate_video.py"
LOCK_PATH = TMP / ".auto_patterns.lock"

STATUS_DONE = "done"
STATUS_IN_PROGRESS = "in progress"
FIELDNAMES = ["no", "name", "category", "status", "start_time", "end_time"]

# How many builds may run at once. Each cron run starts one more pattern as long
# as fewer than this many generator processes are actually running.
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
    """'Abstract Factory' -> 'abstract_factory'; drops any '(...)' qualifier."""
    name = re.sub(r"\(.*?\)", " ", name)          # drop "(MVC)" etc.
    name = name.lower().replace("&", " and ")
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def storyboard_path(name: str) -> Path:
    return STORYBOARDS / f"{slugify(name)}_pattern_storyboard.md"


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
# heading — no file names, class names, or `### description` blocks).
_EXEMPLAR = """\
---
title: strategy_pattern
language: both
length: 2-3 minutes
---

# Strategy Pattern

A short tutorial on the Strategy pattern using a shipping-cost example: a Checkout
that calculates shipping with interchangeable algorithms. Code in Java. Use
DANGER for rigid conditionals, OK for the Strategy design, HIGHLIGHT for the
current object, PRIMARY for titles, ACCENT for labels.

## Introduction (~15s)
Show "Strategy Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it. Explain it defines a family of algorithms, puts each in its own class,
and makes them interchangeable. Three shipping icons labeled Standard, Express,
Same-Day.

## The Problem (~25s)
A Java Checkout class calculates shipping with hardcoded if/else branches for
each shipping type. Show the class growing as rules are added; mark the rigid
branches in DANGER. The pain: every new algorithm forces editing this class.

## The Strategy Solution (~30s)
Define a ShippingStrategy interface with cost(Order). Show StandardShipping,
ExpressShipping, SameDayShipping implementing it, and a Checkout that holds a
ShippingStrategy and delegates with shippingStrategy.cost(order). Swap the
strategy at runtime in OK color.

## Conclusion (~15s)
Recap: encapsulate interchangeable algorithms behind one interface. Benefits:
fewer conditionals, easier testing, runtime flexibility. End with
Context -> Strategy -> ConcreteStrategy.
"""


def _build_prompt(name: str, category: str) -> str:
    title = f"{slugify(name)}_pattern"
    return (
        "You are authoring a storyboard markdown file for an automated tutorial-"
        "video generator. Below is a COMPLETE example in the required format. "
        "Study its structure: a small YAML front-matter block, a `# Title` "
        "heading, a free-form brief, then one plain `## Scene Title (~Ns)` heading "
        "per scene with the scene's visual description written directly under it.\n\n"
        f"Produce a NEW storyboard for the **{name}** ({category}) software design "
        "pattern, in the SAME format and the same level of detail.\n\n"
        "Hard requirements:\n"
        f"- front-matter has exactly: `title: {title}`, `language: both`, "
        "`length: 2-3 minutes`.\n"
        f"- the `# ` title heading reads exactly `# {name} Pattern`.\n"
        "- 6 to 8 scenes; each is a plain `## Human Title (~Ns)` heading (the "
        "`(~Ns)` is that scene's length in seconds) with the description right "
        "underneath. Do NOT write `## Scene:`, `**file:**`, `**fallback_duration:**`, "
        "`**class:**`, or `### description` — those are derived automatically.\n"
        "- the per-scene seconds must sum to between 120 and 180.\n"
        f"- the FIRST (intro) scene must present the pattern name as the LARGE "
        f"CENTERED title (not only in the small top bar) — it reads exactly "
        f"`{name} Pattern` (for a SOLID principle, drop the word Pattern). A short "
        "subtitle may sit directly beneath it.\n"
        "- write ONE concrete running example in **Java**; flow problem -> naive "
        "approach -> the pattern -> a class/structure diagram -> before/after code "
        "-> conclusion, adapted to this pattern.\n"
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
        ("xfce4-terminal", ["xfce4-terminal", "--title", title, "-x", "bash", r]),
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
            log("nothing pending — all patterns are done or in progress.")
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
    and the one-at-a-time guard (use to jump ahead or re-run a pattern)."""
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
        print(f"  [{mark}] {r['no']:>3}  {r['name']:<32} {r['category']:<22} {r['status']:<12}{times}")
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
