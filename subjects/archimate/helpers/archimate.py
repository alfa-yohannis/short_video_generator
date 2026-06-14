# --- ArchiMate notation helpers -------------------------------------------
# Subject-pack scene helpers for `subject: archimate`. This file is a FRAGMENT:
# the build pipeline (scenes.SceneSynthesizer.materialize_dir) APPENDS it into
# the build's `_common.py`, so it relies on names already defined there —
# `from manim import *` (RoundedRectangle, MarkupText, SVGMobject, Polygon,
# Line, DashedLine, Dot, VGroup, UR, LEFT, DOWN, ITALIC), `np`, and the theme
# constants (PRIMARY, PANEL_DARK, W_SEMIBOLD). It is not meant to be imported on
# its own. Generated ArchiMate scenes then do `from _common import (archi_element,
# influence_arrow, ...)` exactly as before.
#
# Elements LOAD their real type logo (`<layer>_<type>_logo.svg`); relationships
# are DRAWN (a connector can't be a static SVG). Use these so the notation is
# identical at every --effort level.

ARCHI_LAYER_FILL = {
    "strategy": "#F4B860", "business": "#FFF3B0", "application": "#B6E3EB",
    "technology": "#BCE3BC", "physical": "#BCE3BC", "motivation": "#CBC8E6",
    "implementation": "#F4C9D4", "other": "#E6E6E6",
}


def archi_logo(path, height: float = 0.34, color: str = PANEL_DARK):
    """Load an ArchiMate `*_logo.svg` glyph so it is ALWAYS visible.

    These logos are thin stroke-only outlines; a naive ``SVGMobject`` renders
    them nearly invisible when scaled small. We force a bold stroke (keeping any
    fill) so the type icon reads at any size. Returns the glyph, or ``None`` if
    the file is missing/empty so the caller can simply skip it."""
    try:
        logo = SVGMobject(str(path))
    except Exception:
        return None
    if len(logo.family_members_with_points()) == 0:
        return None
    logo.scale_to_fit_height(height)
    logo.set_stroke(color=color, width=2.6, opacity=1)
    return logo


def archi_element(name, logo_path, fill, *, width: float = 2.7,
                  height: float = 1.2, text_color: str = PANEL_DARK,
                  font_size: int = 24, logo_height=None):
    """Standard ArchiMate element box. ALWAYS use this for an element so the
    notation never varies: a layer-colored ``RoundedRectangle`` with the name
    centered inside and the REAL type logo pinned to the TOP-RIGHT corner (never
    overlapping the label). ``fill`` may be a hex color or a layer key
    (e.g. ``"strategy"``)."""
    fill_color = ARCHI_LAYER_FILL.get(fill, fill)
    box = RoundedRectangle(corner_radius=0.14, width=width, height=height,
                           stroke_color=PRIMARY, stroke_width=2.5,
                           fill_color=fill_color, fill_opacity=1.0)
    label = MarkupText(name, font_size=font_size, color=text_color,
                       weight=W_SEMIBOLD)
    max_w = width - 0.7
    if label.width > max_w:
        label.scale(max_w / label.width)
    label.move_to(box.get_center())
    group = VGroup(box, label)
    logo = archi_logo(logo_path, height=logo_height or min(0.34, height * 0.30))
    if logo is not None:
        logo.move_to(box.get_corner(UR) + LEFT * 0.26 + DOWN * 0.24)
        group.add(logo)
    return group


def _filled_head(tip, base_center, color=PRIMARY, size: float = 0.26):
    tip = np.array(tip, float); base_center = np.array(base_center, float)
    d = tip - base_center; n = np.linalg.norm(d)
    if n == 0:
        return VGroup()
    d = d / n; perp = np.array([-d[1], d[0], 0]) * size * 0.55
    base = tip - d * size
    return Polygon(tip, base + perp, base - perp, color=color,
                   stroke_width=0, fill_color=color, fill_opacity=1.0)


def _open_head(tip, base_center, color=PRIMARY, size: float = 0.26):
    tip = np.array(tip, float); base_center = np.array(base_center, float)
    d = tip - base_center; n = np.linalg.norm(d)
    if n == 0:
        return VGroup()
    d = d / n; perp = np.array([-d[1], d[0], 0]) * size * 0.55
    base = tip - d * size
    return VGroup(Line(base + perp, tip, color=color, stroke_width=2.6),
                  Line(base - perp, tip, color=color, stroke_width=2.6))


def _rel_label(group, start, end, label, color):
    if not label:
        return group
    lbl = MarkupText(label, font_size=18, color=color, slant=ITALIC)
    start = np.array(start, float); end = np.array(end, float)
    mid = (start + end) / 2.0
    d = end - start
    if np.linalg.norm(d) > 0:
        u = d / np.linalg.norm(d)
        lbl.move_to(mid + np.array([-u[1], u[0], 0]) * 0.28)
    else:
        lbl.next_to(group, UP, buff=0.1)
    group.add(lbl)
    return group


def assignment_arrow(start, end, color=PRIMARY, label=None):
    """Assignment: solid line, filled ball at source, filled arrowhead at target."""
    start = np.array(start, float); end = np.array(end, float)
    d = end - start; n = np.linalg.norm(d)
    if n == 0:
        return VGroup()
    u = d / n; hs = 0.26
    line = Line(start, end - u * hs, color=color, stroke_width=2.6)
    ball = Dot(start, radius=0.075, color=color)
    head = _filled_head(end, end - u * hs, color=color, size=hs)
    return _rel_label(VGroup(line, ball, head), start, end, label, color)


def serving_arrow(start, end, color=PRIMARY, label=None):
    """Serving: solid line, OPEN (line) arrowhead at target."""
    start = np.array(start, float); end = np.array(end, float)
    d = end - start; n = np.linalg.norm(d)
    if n == 0:
        return VGroup()
    u = d / n; hs = 0.26
    line = Line(start, end - u * hs, color=color, stroke_width=2.6)
    head = _open_head(end, end - u * hs, color=color, size=hs)
    return _rel_label(VGroup(line, head), start, end, label, color)


def influence_arrow(start, end, color=PRIMARY, label=None, dash_length: float = 0.14):
    """Influence: DASHED line, OPEN arrowhead at target."""
    start = np.array(start, float); end = np.array(end, float)
    d = end - start; n = np.linalg.norm(d)
    if n == 0:
        return VGroup()
    u = d / n; hs = 0.26
    line = DashedLine(start, end - u * hs, color=color, stroke_width=2.4,
                      dash_length=dash_length)
    head = _open_head(end, end - u * hs, color=color, size=hs)
    return _rel_label(VGroup(line, head), start, end, label, color)


def composition_arrow(start, end, color=PRIMARY, label=None):
    """Composition: solid line, FILLED diamond at the SOURCE end."""
    start = np.array(start, float); end = np.array(end, float)
    d = end - start; n = np.linalg.norm(d)
    if n == 0:
        return VGroup()
    u = d / n; ds = 0.16
    perp = np.array([-u[1], u[0], 0]) * ds * 0.6
    diamond = Polygon(start, start + u * ds + perp, start + u * ds * 2,
                      start + u * ds - perp, color=color, stroke_width=0,
                      fill_color=color, fill_opacity=1.0)
    line = Line(start + u * ds * 2, end, color=color, stroke_width=2.6)
    return _rel_label(VGroup(diamond, line), start, end, label, color)
