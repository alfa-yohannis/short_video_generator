"""Fixtures for the HTML/Playwright orchestrator test suite.

Loads `video_generator_html/generate_video.py` under a DISTINCT module name
(`generate_video_html`) so it never collides with the Manim app's module in the
sibling `tests/` suite. Run the two suites separately (each has its own conftest).
The venv bootstrap is skipped via the marker env var.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GV_PATH = REPO_ROOT / "video_generator_html" / "generate_video.py"


def _load_module():
    os.environ.setdefault("VIDEO_GENERATOR_VENV", "1")  # skip venv bootstrap/re-exec
    spec = importlib.util.spec_from_file_location("generate_video_html", GV_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["generate_video_html"] = module
    spec.loader.exec_module(module)
    return module


gv = _load_module()


@pytest.fixture()
def g():
    """The loaded HTML generate_video module under test."""
    return gv


def requires(*binaries: str):
    missing = [x for x in binaries if not shutil.which(x)]
    return pytest.mark.skipif(bool(missing), reason=f"missing tools: {', '.join(missing)}")


def silent_mp3(path: Path, seconds: float = 1.0) -> Path:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
         "-i", "anullsrc=r=24000:cl=mono", "-t", str(seconds),
         "-c:a", "libmp3lame", "-q:a", "9", str(path)],
        check=True,
    )
    return path


def storyboard_text(*, title="demo_video", languages=("id", "en"),
                    orientations=("landscape", "portrait"), voices=None,
                    tts_provider="edge", ai_cli="claude", scenes=None) -> str:
    if scenes is None:
        scenes = [{"basename": "01_intro", "classname": "Intro",
                   "description": "Title card.",
                   "narration": {"id": "Halo dunia.", "en": "Hello world."}}]
    fm = [f"title: {title}",
          f"languages: [{', '.join(languages)}]",
          f"orientations: [{', '.join(orientations)}]"]
    if voices:
        fm.append("voices:")
        fm += [f"  {k}: {v}" for k, v in voices.items()]
    fm += [f"tts_provider: {tts_provider}", f"ai_cli: {ai_cli}",
           "fps: 30", "resolution_landscape: [1920, 1080]"]
    parts = ["---", "\n".join(fm), "---", "", f"# {title}", "", "A brief.", ""]
    for sc in scenes:
        b = sc["basename"]
        head = f"## Scene: {b}" + (f" / {sc['classname']}" if sc.get("classname") else "")
        parts += [head, "", f"**file:** scene_{b}.py",
                  f"**fallback_duration:** {sc.get('duration', 12)}", ""]
        if "description" in sc:
            parts += ["### description", sc["description"], ""]
        for lang, text in (sc.get("narration") or {}).items():
            parts += [f"### narration.{lang}", text, ""]
    return "\n".join(parts)


def write_storyboard(path: Path, **kwargs) -> Path:
    path.write_text(storyboard_text(**kwargs), encoding="utf-8")
    return path
