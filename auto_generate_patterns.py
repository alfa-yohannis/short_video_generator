#!/usr/bin/env python3
"""Cron-driven design-pattern video factory.

Each run (default mode):

1. Reads ``design_patterns_todo.csv`` (no, name, category, status).
2. If some pattern is already "in progress", exits (one video at a time).
3. Otherwise picks the first pending (blank-status) pattern, marks it
   "in progress", and saves the CSV.
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

Run it by hand in a terminal to test, or wire it to cron (hourly) — see the
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
FIELDNAMES = ["no", "name", "category", "status"]

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
from vgen.text_utils import strip_code_fences          # noqa: E402


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
        r["status"] = (r.get("status") or "").strip()
    return rows


def write_rows(rows: List[Dict[str, str]]) -> None:
    tmp = CSV_PATH.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in FIELDNAMES})
    tmp.replace(CSV_PATH)        # atomic-ish swap so a reader never sees a half file


def set_status(no: str, status: str) -> None:
    rows = read_rows()
    for r in rows:
        if r["no"] == str(no):
            r["status"] = status
            break
    write_rows(rows)


# --- Storyboard generation --------------------------------------------------
def _exemplar_storyboard() -> str:
    """An existing, known-good storyboard used as the format/style reference."""
    for cand in ("strategy", "singleton", "observer", "factory_method"):
        p = STORYBOARDS / f"{cand}_pattern_storyboard.md"
        if p.exists():
            return p.read_text(encoding="utf-8")
    raise SystemExit("No exemplar storyboard found under storyboards/.")


def _build_prompt(name: str, category: str, example: str) -> str:
    title = f"{slugify(name)}_pattern"
    return (
        "You are authoring a storyboard markdown file for an automated tutorial-"
        "video generator. Below is a COMPLETE working example for another "
        "pattern. Study its exact structure: YAML front-matter between '---' "
        "lines, a free-form project description, then one '## Scene:' heading per "
        "scene with '**file:**', '**fallback_duration:**', and a '### "
        "description' block.\n\n"
        "Produce a NEW storyboard for the "
        f"**{name}** ({category}) software design pattern, in the SAME format and "
        "the same level of detail.\n\n"
        "Hard requirements:\n"
        f"- front-matter `title:` must be exactly `{title}`.\n"
        "- keep `languages: [id, en]`, `orientations: [landscape, portrait]`, "
        "`tts_provider: edge`, `ai_cli: claude`, `fps: 30`, "
        "`resolution_landscape: [1920, 1080]`, and the same duration caps.\n"
        "- 6 to 8 scenes; Indonesian scene slugs like the example "
        "(e.g. 01_pengantar, 02_masalah, ... kesimpulan).\n"
        "- the FIRST scene's description must require the main title to read "
        f"exactly `{name} Pattern`.\n"
        "- write ONE concrete running example in **Java**; introduce problem -> "
        "naive approach -> the pattern -> UML class diagram (it doesn't have to be this) or other more apropriate diagrams -> before/after code "
        "-> conclusion, adapted to this pattern.\n"
        "- descriptions ONLY (no narration text, no Manim/Python code blocks). "
        "Mention semantic colors DANGER/OK/HIGHLIGHT/PRIMARY/ACCENT as the "
        "example does.\n"
        "- avoid orientation words (left/right/above/below) in any text meant to "
        "be shown or spoken.\n\n"
        "Output ONLY the raw markdown file content. No code fences, no commentary "
        "before or after.\n\n"
        "===== EXAMPLE STORYBOARD (format reference) =====\n"
        f"{example}\n"
        "===== END EXAMPLE =====\n"
    )


def ensure_storyboard(name: str, category: str) -> Path:
    """Return a valid storyboard path for `name`, generating it if needed."""
    path = storyboard_path(name)
    parser = StoryboardParser()
    if path.exists():
        try:
            parser.parse(path)
            log(f"reusing existing storyboard {path.name}")
            return path
        except Exception as exc:        # noqa: BLE001 - regenerate on any parse issue
            log(f"existing {path.name} did not parse ({exc}); regenerating")

    client = create_ai_client("claude", "xhigh")
    prompt = _build_prompt(name, category, _exemplar_storyboard())
    last_err: Optional[Exception] = None
    for attempt in range(1, 4):
        log(f"generating storyboard for '{name}' (attempt {attempt}/3) via claude xhigh…")
        content = strip_code_fences(client.generate(prompt)).strip() + "\n"
        path.write_text(content, encoding="utf-8")
        try:
            parser.parse(path)
            log(f"storyboard written + validated: {path}")
            return path
        except Exception as exc:        # noqa: BLE001
            last_err = exc
            log(f"  generated storyboard failed to parse: {exc}")
    raise SystemExit(f"Could not produce a valid storyboard for '{name}': {last_err}")


# --- Spawning the generator in its own console ------------------------------
def _write_runner(no: str, name: str, sb: Path, out: Path) -> Path:
    runner = TMP / f"_runner_{slugify(name)}.sh"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        'export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"\n'
        f'echo "[auto] building video for {name} ..."\n'
        f'"{VENV_PY}" "{GENERATOR}" \\\n'
        f'  --storyboard "{sb}" \\\n'
        f'  --output "{out}" \\\n'
        '  --tts edge \\\n'
        '  --ai-cli claude --effort xhigh \\\n'
        '  --refine-storyboard \\\n'
        '  --validate-scenes \\\n'
        '  --force\n'
        'code=$?\n'
        f'"{VENV_PY}" "{Path(__file__).resolve()}" --finalize "{no}" --exit-code "$code"\n'
        "echo\n"
        f'echo "[auto] {name} finished with exit code $code"\n'
        'if [ -t 0 ]; then echo "Press Enter to close this window..."; read _; fi\n',
        encoding="utf-8",
    )
    runner.chmod(0o755)
    return runner


def _terminal_argv(runner: Path) -> Optional[List[str]]:
    candidates = [
        ("gnome-terminal", ["gnome-terminal", "--", "bash", str(runner)]),
        ("konsole", ["konsole", "-e", "bash", str(runner)]),
        ("xfce4-terminal", ["xfce4-terminal", "-x", "bash", str(runner)]),
        ("mate-terminal", ["mate-terminal", "-x", "bash", str(runner)]),
        ("x-terminal-emulator", ["x-terminal-emulator", "-e", "bash", str(runner)]),
        ("xterm", ["xterm", "-e", "bash", str(runner)]),
    ]
    if not os.environ.get("DISPLAY"):
        return None
    for binary, argv in candidates:
        if shutil.which(binary):
            return argv
    return None


def launch_generator(no: str, name: str, sb: Path, out: Path) -> None:
    runner = _write_runner(no, name, sb, out)
    argv = _terminal_argv(runner)
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
def mode_pick() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV not found: {CSV_PATH}")
    with _Lock(LOCK_PATH):
        rows = read_rows()
        in_progress = [r for r in rows if r["status"].lower() == STATUS_IN_PROGRESS]
        if in_progress:
            names = ", ".join(r["name"] for r in in_progress)
            log(f"already in progress ({names}); skipping this run.")
            return
        pending = [r for r in rows if r["status"].lower() not in (STATUS_DONE, STATUS_IN_PROGRESS)]
        if not pending:
            log("all patterns are done — nothing to do.")
            return
        row = pending[0]
        log(f"picked #{row['no']} {row['name']} ({row['category']}).")
        set_status(row["no"], STATUS_IN_PROGRESS)

    # Heavy work happens OUTSIDE the lock.
    try:
        sb = ensure_storyboard(row["name"], row["category"])
    except SystemExit as exc:
        log(f"storyboard step failed: {exc}; reverting #{row['no']} to pending.")
        set_status(row["no"], "")
        raise
    out = output_dir(row["name"])
    out.mkdir(parents=True, exist_ok=True)
    launch_generator(row["no"], row["name"], sb, out)
    log(f"#{row['no']} {row['name']} is building in its own console; "
        "it will be marked done on success.")


def mode_finalize(no: str, exit_code: int) -> None:
    with _Lock(LOCK_PATH):
        if exit_code == 0:
            set_status(no, STATUS_DONE)
            log(f"#{no} completed successfully — marked done.")
        else:
            set_status(no, "")
            log(f"#{no} failed (exit {exit_code}) — reverted to pending for retry.")


def mode_reset_stuck() -> None:
    with _Lock(LOCK_PATH):
        rows = read_rows()
        n = 0
        for r in rows:
            if r["status"].lower() == STATUS_IN_PROGRESS:
                r["status"] = ""
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
        print(f"  [{mark}] {r['no']:>2}  {r['name']:<32} {r['category']:<16} {r['status']}")
    print(f"\n  {done} done · {prog} in progress · {pend} pending · {len(rows)} total")


def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--finalize", metavar="NO",
                   help="(internal) mark row NO done/pending based on --exit-code")
    p.add_argument("--exit-code", type=int, default=0,
                   help="exit code of the generator run (used with --finalize)")
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
    else:
        mode_pick()


if __name__ == "__main__":
    main()
