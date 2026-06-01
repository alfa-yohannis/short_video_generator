"""Tests for the render-time layout self-check in the scene `_common.py`.

`check_layout` inspects a scene's text mobjects for off-frame overflow, portrait
caption-zone violations, and significant text overlap. We exercise it directly
on fabricated text mobjects (no full render) by wrapping them in a tiny
scene-like object exposing `.mobjects`. These need manim + manimpango, so they
skip cleanly when those aren't importable.
"""

from __future__ import annotations

import types

import pytest

pytestmark = pytest.mark.integration


def _scene(*mobs):
    return types.SimpleNamespace(mobjects=list(mobs))


def _text(c, s, **kw):
    # Use the module's manim namespace so fonts are already registered.
    return c.MarkupText(s, font_size=kw.get("font_size", 30))


# --- landscape: overflow / overlap / off-switch ----------------------------


def test_clean_scene_has_no_issues(landscape_common):
    c = landscape_common
    c.config.frame_width, c.config.frame_height = 14.222, 8.0
    t = _text(c, "Pythagorean Theorem").move_to(c.ORIGIN)
    assert c.check_layout(_scene(t), mode="warn") == []


def test_overflow_detected(landscape_common):
    c = landscape_common
    c.config.frame_width, c.config.frame_height = 14.222, 8.0
    t = _text(c, "Edge").move_to(c.RIGHT * 100)  # shoved far off-frame
    issues = c.check_layout(_scene(t), mode="warn")
    assert any("OVERFLOW" in i for i in issues)


def test_overlap_detected(landscape_common):
    c = landscape_common
    c.config.frame_width, c.config.frame_height = 14.222, 8.0
    a = _text(c, "SAME SPOT").move_to(c.ORIGIN)
    b = _text(c, "SAME SPOT").move_to(c.ORIGIN)
    issues = c.check_layout(_scene(a, b), mode="warn")
    assert any("OVERLAP" in i for i in issues)


def test_off_mode_skips_everything(landscape_common):
    c = landscape_common
    c.config.frame_width, c.config.frame_height = 14.222, 8.0
    t = _text(c, "Edge").move_to(c.RIGHT * 100)
    assert c.check_layout(_scene(t), mode="off") == []
    # default (env unset in tests) is also off
    assert c.check_layout(_scene(t)) == []


def test_strict_mode_raises(landscape_common):
    c = landscape_common
    c.config.frame_width, c.config.frame_height = 14.222, 8.0
    t = _text(c, "Edge").move_to(c.RIGHT * 100)
    with pytest.raises(c.LayoutError):
        c.check_layout(_scene(t), mode="strict")


def test_non_overlapping_texts_ok(landscape_common):
    c = landscape_common
    c.config.frame_width, c.config.frame_height = 14.222, 8.0
    a = _text(c, "Top").move_to(c.UP * 2)
    b = _text(c, "Bottom").move_to(c.DOWN * 2)
    assert c.check_layout(_scene(a, b), mode="warn") == []


# --- portrait: caption safe-area -------------------------------------------


def test_portrait_safe_area_violation(portrait_common):
    c = portrait_common
    # portrait _common sets a 9x16 frame; SHORTS_SAFE_BOTTOM ~= -4.8
    t = _text(c, "Caption-zone intruder").move_to(c.DOWN * 6)
    issues = c.check_layout(_scene(t), mode="warn")
    assert any("SAFE-AREA" in i for i in issues)


def test_portrait_above_safe_area_ok(portrait_common):
    c = portrait_common
    t = _text(c, "Well inside").move_to(c.UP * 2)
    issues = c.check_layout(_scene(t), mode="warn")
    assert not any("SAFE-AREA" in i for i in issues)
