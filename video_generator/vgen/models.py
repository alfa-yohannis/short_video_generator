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
