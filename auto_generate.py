#!/usr/bin/env python3
"""Cron-driven tutorial-video factory — one driver for every subject.

This is the unified replacement for the old per-subject ``auto_generate_patterns.py``
and ``auto_generate_ea.py``. The shared machinery (CSV queue, single-instance lock,
storyboard generation, launching builds in their own console, the finalize/reset/
status modes, the parallelism cap) lives here once; everything that differs per
*subject* (the storyboard-generation prompt + exemplar, the storyboard filename
convention, the generator CLI flags, the to-do CSV) comes from a **subject pack**
under ``subjects/<name>/`` (see ``vgen/subjects.py``).

Pick the subject either explicitly or by routing each CSV row:

    # single-subject queue: every row uses the design_patterns pack
    auto_generate.py --subject design_patterns

    # mixed queue: route each row to archimate/togaf by its CSV category
    auto_generate.py --csv enterprise_architecture_todo.csv

Each run (default mode):
1. Reads the queue CSV (no, name, category, status, start_time, end_time).
2. If ``MAX_PARALLEL_BUILDS`` generator processes are already running, exits;
   otherwise it starts one more (builds run in parallel).
3. Picks the first pending pattern, marks it "in progress", saves the CSV.
4. Resolves the row's subject pack, generates a storyboard with that pack's prompt
   (skipped if a valid one already exists), validating it parses.
5. Launches the short-video generator in a SEPARATE console window with the pack's
   CLI flags, building into ``tmp/<slug>/``.
6. When that console finishes it calls this script back in ``--finalize`` mode.

Helper modes (subject-agnostic):
    --finalize NO --exit-code N   (called by the spawned console)
    --reset-stuck                 (clear any "in progress" rows back to pending)
    --status                      (print the to-do summary and exit)
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
STORYBOARDS = REPO / "storyboards"
TMP = REPO / "tmp"
VENV_PY = REPO / ".venv" / "bin" / "python"
GENERATOR = REPO / "video_generator" / "generate_video.py"

STATUS_DONE = "done"
STATUS_IN_PROGRESS = "in progress"
FIELDNAMES = ["no", "name", "category", "status", "start_time", "end_time"]

# How many builds may run at once (across ALL subjects — the cap counts every
# generate_video.py process). Each cron run starts one more while under the cap.
MAX_PARALLEL_BUILDS = 2

# Make the Claude / ffmpeg binaries findable even under cron's minimal PATH.
os.environ["PATH"] = os.pathsep.join([
    str(Path.home() / ".local" / "bin"),
    "/usr/local/bin", "/usr/bin", "/bin",
    os.environ.get("PATH", ""),
])

# Import the project's own (tested) Claude client, storyboard parser, subjects.
sys.path.insert(0, str(REPO / "video_generator"))
from vgen.ai_client import create_ai_client          # noqa: E402
from vgen.storyboard import StoryboardParser          # noqa: E402
from vgen.subjects import SubjectPack, get_subject, resolve_for_category  # noqa: E402

# --- Run configuration (set by main() from CLI args) ------------------------
CSV_PATH: Path = REPO / "design_patterns_todo.csv"
LOCK_PATH: Path = TMP / ".auto.lock"
FORCE_SUBJECT: Optional[str] = None      # when set, every row uses this pack


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


def pack_for(name: str, category: str) -> SubjectPack:
    """Resolve the subject pack for a row: forced subject, else route by category."""
    if FORCE_SUBJECT:
        return get_subject(FORCE_SUBJECT)
    pack = resolve_for_category(category, name)
    if pack is None:
        raise SystemExit(
            f"No subject pack matches row '{name}' (category '{category}'). "
            "Add the topic's keyword to a subjects/<name>/subject.yaml `aliases:` "
            "list, or pass --subject explicitly."
        )
    return pack


def storyboard_path(name: str, pack: SubjectPack) -> Path:
    suffix = pack.naming.get("storyboard_suffix", "_storyboard.md")
    return STORYBOARDS / f"{slugify(name)}{suffix}"


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
def _build_prompt(name: str, category: str, pack: SubjectPack) -> str:
    """Render the pack's storyboard prompt template for one topic.

    The template uses ``{{NAME}}``, ``{{CATEGORY}}``, ``{{TITLE}}`` and
    ``{{EXEMPLAR}}`` tokens (plain replacement, so literal braces in the prompt
    are safe). ``title`` = slug + the pack's ``title_suffix``."""
    slug = slugify(name)
    title = slug + pack.naming.get("title_suffix", "")
    spec = pack.storyboard_spec
    template = pack.read_text(spec.get("prompt_file", "storyboard_prompt.md"))
    exemplar = pack.read_text(spec.get("exemplar_file", "exemplars/default.md")).strip()
    if not template:
        raise SystemExit(f"subject '{pack.name}' has no storyboard prompt template.")
    return (template.replace("{{NAME}}", name)
                    .replace("{{CATEGORY}}", category)
                    .replace("{{TITLE}}", title)
                    .replace("{{EXEMPLAR}}", exemplar))


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


def ensure_storyboard(name: str, category: str, pack: SubjectPack) -> Path:
    """Return a valid storyboard path for `name`, generating it if needed."""
    path = storyboard_path(name, pack)
    parser = StoryboardParser()
    if path.exists():
        try:
            parser.parse(path)
            log(f"reusing existing storyboard {path.name}")
            return path
        except (Exception, SystemExit) as exc:   # parser raises SystemExit on bad input
            log(f"existing {path.name} did not parse ({exc}); regenerating")

    client = create_ai_client("claude", "xhigh")
    prompt = _build_prompt(name, category, pack)
    last_err: Optional[BaseException] = None
    for attempt in range(1, 4):
        log(f"generating storyboard for '{name}' [{pack.name}] "
            f"(attempt {attempt}/3) via claude xhigh…")
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
def _write_runner(no: str, name: str, sb: Path, out: Path, pack: SubjectPack) -> Path:
    runner = TMP / f"_runner_{slugify(name)}.sh"
    logfile = TMP / f"{slugify(name)}.log"
    title = f"▶ {name}"
    flags = " ".join(pack.cli_flags) or "--tts edge --ai-cli claude --force"
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
        f'  {flags}; }} 2>&1 | tee "{logfile}"\n'
        'code=${PIPESTATUS[0]}\n'
        f'if [ "$code" = "0" ]; then printf "\\033]0;✓ {name}\\007"; '
        f'else printf "\\033]0;✗ {name}\\007"; fi\n'
        f'"{VENV_PY}" "{Path(__file__).resolve()}" --finalize "{no}" --exit-code "$code" --csv "{CSV_PATH}"\n'
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


def launch_generator(no: str, name: str, sb: Path, out: Path, pack: SubjectPack) -> None:
    runner = _write_runner(no, name, sb, out, pack)
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
    pack = pack_for(row["name"], row["category"])
    try:
        sb = ensure_storyboard(row["name"], row["category"], pack)
    except SystemExit as exc:
        log(f"storyboard step failed: {exc}; reverting #{row['no']} to pending.")
        update_row(row["no"], status="", start_time="", end_time="")
        raise
    out = output_dir(row["name"])
    out.mkdir(parents=True, exist_ok=True)
    launch_generator(row["no"], row["name"], sb, out, pack)
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
        print(f"  [{mark}] {r['no']:>3}  {r['name']:<32} {r['category']:<22} {r['status']:<12}{times}")
    print(f"\n  {done} done · {prog} in progress · {pend} pending · {len(rows)} total")


def _resolve_csv_and_lock(args) -> None:
    """Set the module-level CSV_PATH / LOCK_PATH / FORCE_SUBJECT from CLI args."""
    global CSV_PATH, LOCK_PATH, FORCE_SUBJECT
    FORCE_SUBJECT = args.subject
    if args.csv:
        csv_path = Path(args.csv)
        CSV_PATH = csv_path if csv_path.is_absolute() else (REPO / csv_path)
    elif args.subject:
        pack = get_subject(args.subject)
        if not pack.csv:
            raise SystemExit(f"subject '{args.subject}' declares no `csv:`; pass --csv.")
        CSV_PATH = REPO / pack.csv
    else:
        raise SystemExit("Pass --subject NAME and/or --csv PATH.")
    LOCK_PATH = TMP / f".auto_{CSV_PATH.stem}.lock"


def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--subject", metavar="NAME",
                   help="force every row to this subjects/<NAME>/ pack (else route "
                        "each row by its CSV category)")
    p.add_argument("--csv", metavar="PATH",
                   help="the to-do queue CSV (defaults to the --subject pack's csv:)")
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

    _resolve_csv_and_lock(args)
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
