"""Bumper clips spliced into every main video.

Two short pre-rendered clips live bundled under :data:`config.BUMPERS_DIR`:

* **engagement** — a "Like / Follow / Share" call-to-action, inserted right AFTER
  the first scene of the main video;
* **end** — a "comments / questions" closer, appended at the very END.

Each kind has one clip per ``(orientation, language)``, named
``<kind>_<orient>_<lang>.mp4`` (with a matching ``.srt``). They are produced from
``storyboards/engagement_scene_storyboard.md`` / ``end_scene_storyboard.md`` and
copied into the bumpers dir; rebuild + re-copy to refresh them.

The pipeline reserves the bumpers' running time out of the duration cap (see
:func:`reservation`) so ``main scenes + bumpers`` still fits the 3-minute ceiling.
A storyboard can opt out with ``bumpers: false`` in its front-matter (the bumper
storyboards themselves do, so they don't recursively wrap themselves).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from . import config
from .media import ffprobe_duration

#: Order matters only for the end clip; the engagement clip is inserted after the
#: first scene by the assembler, so it is not listed here.
KINDS = ("engagement", "end")


def bumper_clip(kind: str, orient: str, lang: str) -> Optional[Path]:
    """The bumper mp4 for ``(kind, orient, lang)``, or ``None`` if not bundled."""
    path = config.BUMPERS_DIR / f"{kind}_{orient}_{lang}.mp4"
    return path if path.exists() else None


def bumper_srt(kind: str, orient: str, lang: str) -> Optional[Path]:
    """The bumper subtitle file for ``(kind, orient, lang)``, or ``None``."""
    path = config.BUMPERS_DIR / f"{kind}_{orient}_{lang}.srt"
    return path if path.exists() else None


def bumper_duration(kind: str, orient: str, lang: str) -> float:
    """Running time of one bumper, or 0.0 if it isn't bundled."""
    clip = bumper_clip(kind, orient, lang)
    return ffprobe_duration(clip) if clip else 0.0


def reservation(orientations: Iterable[str], languages: Iterable[str]) -> float:
    """Seconds to hold back from the duration cap so the main video + bumpers fit.

    The cap is a single value but bumper lengths vary by language/orientation, so
    reserve the WORST case — the largest ``engagement + end`` total over every
    (orientation, language) this build produces. Conservative by design: it
    guarantees ``main + bumpers <= cap`` for every output.
    """
    worst = 0.0
    for orient in orientations:
        for lang in languages:
            total = sum(bumper_duration(k, orient, lang) for k in KINDS)
            worst = max(worst, total)
    return worst
