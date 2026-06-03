"""Shared pytest fixtures/helpers for the ``vgen`` package test suite.

The implementation now lives in the ``vgen`` package (under ``video_generator/``)
rather than one big module, so tests import the specific classes/functions they
exercise. This file puts the package on the import path, provides a couple of
builders (a storyboard markdown writer, an in-memory ``Storyboard``, a fake AI
client) and the media fixtures the integration tests need.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR_ROOT = REPO_ROOT / "video_generator"
TEMPLATES = GENERATOR_ROOT / "templates"

# Make ``import vgen.<module>`` work. The marker env var stops the package's
# bootstrap from ever trying to create/enter a venv (we never import bootstrap
# here, but set it defensively).
os.environ.setdefault("VIDEO_GENERATOR_VENV", "1")
if str(GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(GENERATOR_ROOT))


# --- builders --------------------------------------------------------------


def make_storyboard(**overrides):
    """A small in-memory :class:`vgen.models.Storyboard` for resolver/logic tests."""
    from vgen import config
    from vgen.models import Storyboard

    defaults = dict(
        title="t", languages=["id", "en"], orientations=["landscape", "portrait"],
        voices={}, tts_provider="edge", gemini_model=config.DEFAULT_GEMINI_MODEL,
        gemini_api_key=None, ai_cli="claude", fps=30,
        resolution_landscape=(1920, 1080), scenes_landscape_dir=None,
        scenes_portrait_dir=None, scenes=[], project_brief="",
    )
    defaults.update(overrides)
    return Storyboard(**defaults)


class FakeAiClient:
    """A stand-in :class:`~vgen.ai_client.AiClient` that returns a canned reply.

    ``reply`` may be a string or a ``callable(prompt) -> str``. Every prompt it
    receives is recorded on ``.prompts`` so tests can assert on what was asked.
    """

    name = "fake"

    def __init__(self, reply="") -> None:
        self.reply = reply
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.reply(prompt) if callable(self.reply) else self.reply


@pytest.fixture()
def fake_ai():
    return FakeAiClient()


# --- storyboard markdown writer --------------------------------------------


def storyboard_text(
    *,
    title: str = "demo_video",
    languages=("id", "en"),
    orientations=("landscape", "portrait"),
    voices: dict | None = None,
    tts_provider: str = "edge",
    ai_cli: str = "claude",
    gemini_model: str | None = None,
    gemini_api_key: str | None = None,
    scenes_landscape_dir: str | None = None,
    scenes_portrait_dir: str | None = None,
    brief: str = "A short tutorial used by the test suite.",
    scenes=None,
) -> str:
    """Build a storyboard markdown document for parser tests."""
    if scenes is None:
        scenes = [{
            "basename": "01_intro", "classname": "Intro",
            "description": "Title card introducing the topic.",
            "narration": {"id": "Halo dunia.", "en": "Hello world."},
        }]

    fm_lines = [
        f"title: {title}",
        f"languages: [{', '.join(languages)}]",
        f"orientations: [{', '.join(orientations)}]",
    ]
    if voices:
        fm_lines.append("voices:")
        for lang, v in voices.items():
            fm_lines.append(f"  {lang}: {v}")
    fm_lines.append(f"tts_provider: {tts_provider}")
    fm_lines.append(f"ai_cli: {ai_cli}")
    if gemini_model:
        fm_lines.append(f"gemini_model: {gemini_model}")
    if gemini_api_key:
        fm_lines.append(f"gemini_api_key: {gemini_api_key}")
    if scenes_landscape_dir:
        fm_lines.append(f"scenes_landscape_dir: {scenes_landscape_dir}")
    if scenes_portrait_dir:
        fm_lines.append(f"scenes_portrait_dir: {scenes_portrait_dir}")
    fm_lines.append("fps: 30")
    fm_lines.append("resolution_landscape: [1920, 1080]")

    parts = ["---", "\n".join(fm_lines), "---", "", f"# {title}", "", brief, ""]
    for sc in scenes:
        basename = sc["basename"]
        classname = sc.get("classname", "")
        heading = f"## Scene: {basename}" + (f" / {classname}" if classname else "")
        parts.append(heading)
        parts.append("")
        parts.append(f"**file:** {sc.get('file', f'scene_{basename}.py')}")
        parts.append(f"**fallback_duration:** {sc.get('duration', 12)}")
        parts.append("")
        if "description" in sc:
            parts.append("### description")
            parts.append(sc["description"])
            parts.append("")
        for lang, text in (sc.get("narration") or {}).items():
            parts.append(f"### narration.{lang}")
            parts.append(text)
            parts.append("")
    return "\n".join(parts)


def write_storyboard(path: Path, **kwargs) -> Path:
    path.write_text(storyboard_text(**kwargs), encoding="utf-8")
    return path


# --- scene _common loaders (need manim) ------------------------------------


def _load_scene_common(subdir: str, modname: str):
    """Import a scene ``_common.py`` under a unique module name (skips if manim
    isn't importable)."""
    path = TEMPLATES / subdir / "_common.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(modname, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # pragma: no cover - depends on env
        pytest.skip(f"cannot import {subdir}/_common.py ({exc})")
    module.config.media_dir = str(Path(tempfile.gettempdir()) / "vg_test_media")
    return module


@pytest.fixture(scope="session")
def landscape_common():
    return _load_scene_common("scenes_landscape", "_common_landscape")


@pytest.fixture(scope="session")
def portrait_common():
    return _load_scene_common("scenes_portrait", "_common_portrait")


# --- skip markers ----------------------------------------------------------


def requires(*binaries: str):
    """Skip an integration test when a required external tool is missing."""
    missing = [x for x in binaries if not shutil.which(x)]
    return pytest.mark.skipif(bool(missing), reason=f"missing tools: {', '.join(missing)}")


# --- media fixtures (ffmpeg) -----------------------------------------------


def silent_mp3(path: Path, seconds: float = 1.0) -> Path:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
         "-i", "anullsrc=r=24000:cl=mono", "-t", str(seconds),
         "-c:a", "libmp3lame", "-q:a", "9", str(path)],
        check=True,
    )
    return path


def color_video(path: Path, seconds: float = 1.0, w: int = 320, h: int = 180,
                fps: int = 30) -> Path:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
         "-i", f"color=c=navy:s={w}x{h}:r={fps}", "-t", str(seconds),
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
         str(path)],
        check=True,
    )
    return path


def pcm_silence(seconds: float = 1.0, rate: int = 24000) -> bytes:
    n = int(rate * seconds)
    return struct.pack("<%dh" % n, *([0] * n))
