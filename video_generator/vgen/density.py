"""Deciding when a failing scene is *too dense* (split it) vs merely needing a
layout tweak (repair it in place).

The layout checker's ``OVERFLOW`` messages already carry the offending bounding
box and the frame size, e.g.::

    OVERFLOW: 'Long title' extends past the frame (x[-8.20,8.20] y[-3.00,3.00], frame 14.2x8.0)

so we can read how badly a scene overflows without any extra instrumentation:

* if fitting the content would need shrinking it below ~60% of its size, the
  text would be unreadable -> too dense;
* if two or more items overflow/spill at once, it's the content volume, not one
  stray label -> too dense.

These are pure functions plus one exception type, so they're trivial to test.
"""

from __future__ import annotations

import re
from typing import Optional

from .models import Scene

# Pull "x[a,b] y[c,d], frame WxH" out of an OVERFLOW message.
_OVERFLOW_BBOX_RE = re.compile(
    r"x\[(-?[\d.]+),(-?[\d.]+)\] y\[(-?[\d.]+),(-?[\d.]+)\], frame ([\d.]+)x([\d.]+)"
)


def overflow_count(problem: str) -> int:
    """How many overflow/containment violations the failure mentions."""
    return problem.count("OVERFLOW") + problem.count("CONTAINMENT")


def min_fit_scale(problem: str) -> Optional[float]:
    """Smallest shrink factor that would make the overflowing items fit.

    Derived from each OVERFLOW message's bounding box vs the frame. Returns
    ``None`` when the failure carries no size information (so the caller falls
    back to the count signal).
    """
    scales = []
    for match in _OVERFLOW_BBOX_RE.finditer(problem):
        x0, x1, y0, y1, frame_w, frame_h = (float(g) for g in match.groups())
        width, height = x1 - x0, y1 - y0
        if width > 0 and height > 0:
            scales.append(min(frame_w / width, frame_h / height, 1.0))
    return min(scales) if scales else None


def is_too_dense(problem: str, min_scale: float) -> bool:
    """True if this layout failure means the scene carries too much content.

    Too dense = fitting it would need shrinking below ``min_scale`` (unreadable),
    OR two-plus items overflow at once. A single, fixable overflow is not dense.
    """
    if not problem:
        return False
    if overflow_count(problem) >= 2:
        return True
    scale = min_fit_scale(problem)
    return scale is not None and scale < min_scale


class SceneTooDenseError(Exception):
    """Raised when in-place repair can't make a scene fit — it has too much
    content and should be split into smaller scenes in the storyboard.

    Carries the offending scene and the rendering evidence, so the build can ask
    the storyboard refiner to split exactly that scene.
    """

    def __init__(self, scene: Scene, orientation: str, evidence: str) -> None:
        super().__init__(f"scene '{scene.basename}' is too dense ({orientation}): {evidence}")
        self.scene = scene
        self.orientation = orientation
        self.evidence = evidence
