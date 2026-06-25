"""Rendering scene ``.py`` files into silent video clips with Manim.

`ManimRenderer` runs the ``manim`` command for each (language, orientation,
scene). When a render fails — either a strict layout-check violation or a plain
crash (a ``NameError``, a wrong helper argument …) — it feeds the error back to
the :class:`~vgen.scenes.SceneSynthesizer` to regenerate the scene and tries
again, up to ``repair_attempts`` times. That self-healing loop is what makes
AI-generated scenes practical.

The two ``extract_*`` functions are pure parsers of Manim's console output and
live at module level so they're trivial to unit-test.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

from typing import Optional

from . import config
from .media import is_up_to_date
from .models import Storyboard
from .parallel import resolve_workers, run_parallel
from .progress import progress
from .scenes import SceneSynthesizer


# --- pure parsers of Manim's output ----------------------------------------

def extract_layout_issues(text: str) -> str:
    """Pull the layout-violation summary out of a failed render's output.

    The scene ``_common.py`` raises ``LayoutError: [layout] N issue(s) ...`` in
    strict mode and also prints ``  - <issue>`` bullet lines. Prefer the single
    ``LayoutError:`` line; fall back to the bullets. Returns ``""`` when the
    failure was not a layout violation.
    """
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("LayoutError:"):
            return stripped[len("LayoutError:"):].strip()
    bullets = [ln.strip()[2:].strip() for ln in lines if ln.strip().startswith("- ")]
    if bullets and any("[layout]" in ln for ln in lines):
        return "; ".join(bullets)
    return ""


_RENDER_ERROR_RE = re.compile(r"\b([A-Za-z_][\w.]*(?:Error|Exception))\b\s*:\s*(.+)")
_SCENE_LOC_RE = re.compile(r"(scene_[\w./-]+\.py)[:\s]+(\d+)\s+in\s+(\w+)")


def extract_render_error(text: str) -> str:
    """Pull the failing exception (e.g. ``NameError: name 'X' is not defined``)
    out of Manim's output, with the scene ``file:line`` for context. Returns
    ``""`` if no exception is found."""
    error = ""
    for line in text.splitlines():
        match = _RENDER_ERROR_RE.search(line.strip())
        if match and "Traceback" not in line:
            error = f"{match.group(1)}: {match.group(2).strip()}"  # keep the LAST match
    if not error:
        return ""
    locations = _SCENE_LOC_RE.findall(text)
    if locations:
        fname, lineno, func = locations[-1]
        return f"{error}  (at {Path(fname).name}:{lineno} in {func})"
    return error


class SceneValidator:
    """Renders one freshly generated scene in low-quality, *strict* layout-check
    mode purely to surface violations — the output video is thrown away.

    The layout self-check lives in the scene ``_common.py`` and only runs during
    a render, so the only way to know whether a generated scene is clean is to
    render it. ``-ql`` (low quality) keeps this cheap; the checks work in scene
    units, so resolution doesn't change what they find. :class:`SceneSynthesizer`
    uses this to validate a scene the moment it is generated.
    """

    def check_scene(self, storyboard: Storyboard, output: Path, scenes_dir: Path,
                    scene, orient: str, lang: str,
                    check_layout: str = "strict") -> Tuple[bool, str, bool]:
        """Render one scene for one language and report ``(ok, problem, is_layout)``."""
        if not config.MANIM_BIN.exists():
            raise SystemExit(f"manim binary not found at {config.MANIM_BIN}")
        scene_path = scenes_dir / scene.file
        media_dir = output / "manim_check" / lang / orient
        media_dir.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["MANIM_LANG"] = lang
        env["LANG_CODE"] = lang
        env["MANIM_AUDIO_DIR"] = str((output / "audio").resolve())
        env["MANIM_CHECK_LAYOUT"] = check_layout
        command = [str(config.MANIM_BIN), "-ql", "--media_dir", str(media_dir),
                   str(scene_path), scene.classname]
        proc = subprocess.run(command, env=env, cwd=str(scenes_dir),
                              capture_output=True, text=True)
        combined = (proc.stdout or "") + (proc.stderr or "")
        layout = extract_layout_issues(combined)
        problem = layout or extract_render_error(combined)
        # In strict mode a violation makes manim exit non-zero, so a clean exit
        # means no layout problem and no crash.
        ok = proc.returncode == 0 and not problem
        return ok, problem, bool(layout)


class ManimRenderer:
    """Renders a storyboard's scenes to per-scene silent MP4s."""

    #: `--jobs` ceiling, injected by build_pipeline (None = use the render cap).
    jobs: Optional[int] = None

    def __init__(self, scene_synth: SceneSynthesizer) -> None:
        self.synth = scene_synth          # used to repair a failing scene

    def render_all(self, storyboard: Storyboard, output: Path, langs, orients,
                   force: bool, check_layout: str = "off",
                   repair_attempts: int = 0) -> None:
        """Render every stale (lang, orient, scene) clip, in parallel.

        Each clip is independent (distinct ``video/<lang>/<orient>/<scene>.mp4``),
        so they run on a thread pool capped at ``MAX_PARALLEL_RENDER``. Per-(lang,
        orient) setup (dirs, env) is done once and captured per work item; the
        repair loop inside ``_render_one`` is per-scene, so it parallelises too.
        """
        if not config.MANIM_BIN.exists():
            raise SystemExit(f"manim binary not found at {config.MANIM_BIN}")
        work = []
        for lang in langs:
            for orient in orients:
                scenes_dir = storyboard.scenes_dir(orient)
                if scenes_dir is None or not scenes_dir.exists():
                    raise SystemExit(f"scenes_{orient}_dir does not exist: {scenes_dir}")
                video_dir = output / "video" / lang / orient
                media_dir = output / "manim_media" / lang / orient
                video_dir.mkdir(parents=True, exist_ok=True)
                media_dir.mkdir(parents=True, exist_ok=True)
                env = self._render_env(output, lang, check_layout)
                common_path = scenes_dir / "_common.py"
                for scene in storyboard.scenes:
                    dest = video_dir / f"{scene.basename}.mp4"
                    scene_path = scenes_dir / scene.file
                    if not scene_path.exists():
                        raise SystemExit(f"Scene file missing: {scene_path}")
                    if not force and is_up_to_date(dest, scene_path, common_path):
                        continue
                    work.append((scene, lang, orient, scenes_dir, media_dir, dest, env))

        def _one(item) -> None:
            scene, lang, orient, scenes_dir, media_dir, dest, env = item
            self._render_one(storyboard, scene, lang, orient, scenes_dir, media_dir,
                             dest, env, repair_attempts)

        run_parallel(work, _one, resolve_workers(config.MAX_PARALLEL_RENDER, self.jobs))

    def render(self, storyboard: Storyboard, output: Path, lang: str, orient: str,
               force: bool, check_layout: str = "off", repair_attempts: int = 0) -> None:
        scenes_dir = storyboard.scenes_dir(orient)
        if scenes_dir is None or not scenes_dir.exists():
            raise SystemExit(f"scenes_{orient}_dir does not exist: {scenes_dir}")
        if not config.MANIM_BIN.exists():
            raise SystemExit(f"manim binary not found at {config.MANIM_BIN}")

        video_dir = output / "video" / lang / orient
        media_dir = output / "manim_media" / lang / orient
        video_dir.mkdir(parents=True, exist_ok=True)
        media_dir.mkdir(parents=True, exist_ok=True)
        env = self._render_env(output, lang, check_layout)
        common_path = scenes_dir / "_common.py"

        for scene in storyboard.scenes:
            dest = video_dir / f"{scene.basename}.mp4"
            scene_path = scenes_dir / scene.file
            if not scene_path.exists():
                raise SystemExit(f"Scene file missing: {scene_path}")
            # Skip only if the clip is up to date with its sources (a regenerated
            # scene .py or refreshed _common.py makes it stale).
            if not force and is_up_to_date(dest, scene_path, common_path):
                continue
            self._render_one(storyboard, scene, lang, orient, scenes_dir, media_dir,
                             dest, env, repair_attempts)

    # --- internals ---------------------------------------------------------

    def _render_env(self, output: Path, lang: str, check_layout: str) -> dict:
        env = os.environ.copy()
        env["MANIM_LANG"] = lang
        env["LANG_CODE"] = lang
        env["MANIM_AUDIO_DIR"] = str((output / "audio").resolve())
        # The scene _common.py reads this to run its layout self-check.
        env["MANIM_CHECK_LAYOUT"] = check_layout
        return env

    def _manim_command(self, storyboard: Storyboard, orient: str, media_dir: Path,
                       scene_path: Path, classname: str) -> List[str]:
        command = [str(config.MANIM_BIN)]
        if orient == "landscape":
            w, h = storyboard.resolution_landscape
            command += ["--resolution", f"{w},{h}"]
        command += ["--fps", str(storyboard.fps), "--media_dir", str(media_dir),
                    str(scene_path), classname]
        return command

    def _render_one(self, storyboard, scene, lang, orient, scenes_dir, media_dir,
                    dest, env, repair_attempts) -> None:
        scene_path = scenes_dir / scene.file
        command = self._manim_command(storyboard, orient, media_dir, scene_path, scene.classname)
        progress.log(f"  render {lang}/{orient}/{scene.basename}::{scene.classname}…")
        started = time.monotonic()

        # AI repair is enabled only when an AI CLI is configured.
        max_repairs = repair_attempts if storyboard.ai_cli not in ("", "none", None) else 0
        for attempt in range(max_repairs + 1):
            proc = subprocess.run(command, env=env, cwd=str(scenes_dir),
                                  capture_output=True, text=True)
            if proc.stdout:
                sys.stdout.write(proc.stdout)
            if proc.stderr:
                sys.stderr.write(proc.stderr)
            if proc.returncode == 0:
                break
            combined = (proc.stdout or "") + (proc.stderr or "")
            layout = extract_layout_issues(combined)
            problem = layout or extract_render_error(combined)
            if not problem or attempt >= max_repairs:
                if problem and max_repairs > 0:
                    kind = "Layout check" if layout else "Render"
                    raise SystemExit(
                        f"{kind} still failing for {orient}/{scene.basename} after "
                        f"{max_repairs} AI repair attempt(s): {problem}"
                    )
                raise subprocess.CalledProcessError(proc.returncode, command)
            kind = "layout violation" if layout else "render error"
            progress.log(f"    {kind}, repairing {orient}/{scene.file} via "
                         f"{storyboard.ai_cli} (attempt {attempt + 1}/{max_repairs})… {problem}")
            self.synth.repair(storyboard, scene, orient, scene_path, problem, bool(layout))

        progress.log(f"    ↳ {lang}/{orient}/{scene.basename}.mp4 in "
                     f"{time.monotonic() - started:.1f}s")
        self._collect_output(media_dir, scene_path, scene.classname, dest)

    def _collect_output(self, media_dir: Path, scene_path: Path, classname: str,
                        dest: Path) -> None:
        """Copy Manim's rendered file out of its media tree to the canonical dest."""
        stem = scene_path.stem
        candidates = list((media_dir / "videos" / stem).rglob(f"{classname}.mp4"))
        if not candidates:
            raise SystemExit(
                f"Could not find Manim render output for {scene_path}::{classname}"
            )
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)  # newest quality
        shutil.copy2(candidates[0], dest)
