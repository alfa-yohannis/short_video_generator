"""The domain model: the data the whole pipeline is built around.

A `Storyboard` is parsed once from a markdown file and then read by every
stage. It is a plain *value object* (a `@dataclass`) — it holds data and a
couple of tiny derived helpers, but no pipeline behaviour. Keeping data and
behaviour separated here keeps the model easy to read and to test.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Scene:
    """One scene of the video.

    Attributes:
        basename:   file-stem identifier, e.g. ``01_pengantar``.
        classname:  the Manim ``Scene`` subclass to render, e.g. ``Pengantar``.
        file:       the scene's Python filename, e.g. ``scene_01_pengantar.py``.
        fallback_duration: seconds the scene lasts when there is no audio yet;
                    also sets the narration word budget.
        description: a short brief the AI uses to write narration + visuals.
        narration:  language code -> narration text (filled in as we go).
        extras:     any other ``### subsection`` from the storyboard (e.g. notes).
    """

    basename: str
    classname: str
    file: str
    fallback_duration: float
    description: str
    narration: Dict[str, str] = field(default_factory=dict)
    extras: Dict[str, str] = field(default_factory=dict)


@dataclass
class Storyboard:
    """The whole project: global settings plus the ordered list of scenes.

    This is the single source of truth shared by every pipeline stage. CLI
    flags may override a few fields (``ai_cli``, ``tts_provider``, ``voices``,
    ``gemini_api_key``) before the build starts.
    """

    title: str
    languages: List[str]
    orientations: List[str]
    voices: Dict[str, str]
    tts_provider: str
    gemini_model: str
    gemini_api_key: Optional[str]
    ai_cli: str
    fps: int
    resolution_landscape: Tuple[int, int]
    scenes_landscape_dir: Optional[Path]
    scenes_portrait_dir: Optional[Path]
    scenes: List[Scene]
    project_brief: str
    min_duration: Optional[float] = None  # whole-video floor in seconds, or None
    max_duration: Optional[float] = None  # whole-video cap in seconds, or None

    # --- tiny derived helpers (no side effects) ---------------------------

    def duration_budget(self) -> float:
        """Sum of every scene's fallback duration — the video's planned length."""
        return sum(scene.fallback_duration for scene in self.scenes)

    def scenes_dir(self, orientation: str) -> Optional[Path]:
        """The user-declared scenes directory for an orientation, if any."""
        if orientation == "landscape":
            return self.scenes_landscape_dir
        return self.scenes_portrait_dir

    def to_markdown(self) -> str:
        """Serialize back to the storyboard markdown format.

        Round-trips through :class:`~vgen.storyboard.StoryboardParser` — used by
        the refiner so it can show the AI the *current* storyboard (after any
        earlier edit) without depending on the original file on disk.
        """
        lines = [
            "---",
            f"title: {self.title}",
            f"languages: [{', '.join(self.languages)}]",
            f"orientations: [{', '.join(self.orientations)}]",
        ]
        if self.voices:
            lines.append("voices:")
            lines += [f"  {lang}: {voice}" for lang, voice in self.voices.items()]
        lines.append(f"tts_provider: {self.tts_provider}")
        lines.append(f"gemini_model: {self.gemini_model}")
        if self.gemini_api_key:
            lines.append(f"gemini_api_key: {self.gemini_api_key}")
        lines.append(f"ai_cli: {self.ai_cli}")
        lines.append(f"fps: {self.fps}")
        w, h = self.resolution_landscape
        lines.append(f"resolution_landscape: [{w}, {h}]")
        if self.min_duration is not None:
            lines.append(f"min_duration: {self.min_duration:g}")
        if self.max_duration is not None:
            lines.append(f"max_duration: {self.max_duration:g}")
        lines.append("---")
        lines.append("")
        if self.project_brief:
            lines += [self.project_brief, ""]
        for scene in self.scenes:
            lines.append(f"## Scene: {scene.basename} / {scene.classname}")
            lines.append("")
            lines.append(f"**file:** {scene.file}")
            lines.append(f"**fallback_duration:** {scene.fallback_duration:g}")
            lines.append("")
            if scene.description:
                lines += ["### description", scene.description, ""]
            for lang, text in scene.narration.items():
                if text.strip():
                    lines += [f"### narration.{lang}", text, ""]
        return "\n".join(lines).rstrip() + "\n"
