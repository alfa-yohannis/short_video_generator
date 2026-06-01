"""Shared helpers + theme for landscape (16:9) scenes."""

import os
import subprocess
from pathlib import Path

import numpy as np
import manimpango
from manim import *

# --- Engineering studio palette ------------------------------------------
# Editorial, software-engineering oriented: calm light canvas, dark code
# surfaces, and semantic accents for architecture/status.
PRIMARY = "#173B8F"
ACCENT = "#06A6D8"
HIGHLIGHT = "#F4B740"
BG = "#F6F8FB"
TEXT = "#172033"
DANGER = "#C2413A"
OK = "#1F9D69"
CARD_BG = "#FFFFFF"
CARD_SHADOW = "#D7DEE8"
CODE_BG = "#111827"
CODE_BORDER = "#38BDF8"
PANEL_DARK = "#0F172A"
MUTED = "#64748B"
GRID = "#D9E3EE"

config.background_color = BG

ROOT_DIR = Path(__file__).resolve().parent.parent
LANG_CODE = os.environ.get("MANIM_LANG", os.environ.get("LANG_CODE", "id")).lower()
if LANG_CODE not in {"id", "en"}:
    LANG_CODE = "id"


def L(id_text: str, en_text: str) -> str:
    return en_text if LANG_CODE == "en" else id_text


def audio_duration(scene_name: str, fallback: float) -> float:
    audio_root = os.environ.get("MANIM_AUDIO_DIR")
    base = Path(audio_root) if audio_root else ROOT_DIR / "audio"
    audio_path = base / LANG_CODE / f"{scene_name}.mp3"
    if not audio_path.exists():
        return fallback
    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1",
            str(audio_path),
        ], text=True)
        return float(out.strip())
    except (subprocess.CalledProcessError, ValueError):
        return fallback

# --- Font registration ----------------------------------------------------
_FONT_DIR = ROOT_DIR / "assets" / "fonts"
for _ttf in [
    "NotoSansMono-Regular.ttf",
    "NotoSansMono-Medium.ttf",
    "NotoSansMono-SemiBold.ttf",
    "NotoSansMono-Bold.ttf",
    "NotoSans-Regular.ttf",
    "NotoSans-Medium.ttf",
    "NotoSans-SemiBold.ttf",
    "NotoSans-Bold.ttf",
    "JetBrainsMonoNL-Regular.ttf",
    "JetBrainsMonoNL-Medium.ttf",
]:
    manimpango.register_font(str(_FONT_DIR / _ttf))

# Non-code text (titles, body, subtitles) uses the proportional Noto Sans for
# even, kerned spacing. Code samples use JetBrains Mono NL. Noto Sans Mono stays
# registered so scenes can opt into a monospace look via font="Noto Sans Mono".
BODY_FONT = "Noto Sans"
CODE_FONT = "JetBrains Mono NL"

# Pango / Manim weight constants for explicit control
W_REGULAR = "NORMAL"        # 400
W_MEDIUM = "MEDIUM"         # 500
W_SEMIBOLD = "SEMIBOLD"     # 600
W_BOLD = "BOLD"             # 700

# --- Patch Text + MarkupText defaults so kerning is consistent ------------
_orig_text_init = Text.__init__
_orig_markup_init = MarkupText.__init__


def _patched_text_init(self, *args, font=None, **kwargs):
    if font is None:
        font = BODY_FONT
    _orig_text_init(self, *args, font=font, **kwargs)


def _patched_markup_init(self, *args, font=None, **kwargs):
    if font is None:
        font = BODY_FONT
    _orig_markup_init(self, *args, font=font, **kwargs)


Text.__init__ = _patched_text_init
MarkupText.__init__ = _patched_markup_init


# --- Typography helpers ---------------------------------------------------
# Title / heading: Noto Sans SemiBold (with Bold reserved for very large
# display type). Body: Noto Sans Regular. Subtitles: Noto Sans Medium.

def title_text(text: str, size: int = 40, color=PRIMARY,
               weight=W_BOLD) -> MarkupText:
    return MarkupText(text, font_size=size, weight=weight, color=color)


def body_text(text: str, size: int = 28, color=TEXT,
              weight=W_REGULAR) -> MarkupText:
    return MarkupText(text, font_size=size, color=color, weight=weight)


def section_label(text: str, color=ACCENT, size: int = 24,
                  weight=W_SEMIBOLD) -> MarkupText:
    return MarkupText(text, font_size=size, weight=weight, color=color)


# --- Scene surface --------------------------------------------------------

def tech_background() -> VGroup:
    """Subtle blueprint grid used behind every scene."""
    fw, fh = config.frame_width, config.frame_height
    base = Rectangle(width=fw, height=fh, fill_color=BG, fill_opacity=1.0,
                     stroke_opacity=0)

    lines = VGroup()
    step = 0.8
    x_start = np.ceil((-fw / 2) / step) * step
    y_start = np.ceil((-fh / 2) / step) * step
    for x in np.arange(x_start, fw / 2 + step, step):
        lines.add(Line([x, -fh / 2, 0], [x, fh / 2, 0]))
    for y in np.arange(y_start, fh / 2 + step, step):
        lines.add(Line([-fw / 2, y, 0], [fw / 2, y, 0]))
    lines.set_stroke(GRID, width=1, opacity=0.42)

    top_rule = Rectangle(width=fw, height=0.04, fill_color=ACCENT,
                         fill_opacity=0.95, stroke_opacity=0)
    top_rule.to_edge(UP, buff=0)
    corner = VGroup(
        Line([-fw / 2 + 0.55, fh / 2 - 0.55, 0],
             [-fw / 2 + 1.45, fh / 2 - 0.55, 0]),
        Line([-fw / 2 + 0.55, fh / 2 - 0.55, 0],
             [-fw / 2 + 0.55, fh / 2 - 1.2, 0]),
    )
    corner.set_stroke(HIGHLIGHT, width=3, opacity=0.75)

    bg = VGroup(base, lines, top_rule, corner)
    bg.set_z_index(-20)
    return bg


def soft_panel(width: float, height: float, stroke=PRIMARY, fill=CARD_BG,
               radius: float = 0.16, stroke_width: float = 2,
               shadow: bool = True) -> VGroup:
    panel = RoundedRectangle(corner_radius=radius, width=width, height=height,
                             stroke_color=stroke, stroke_width=stroke_width,
                             fill_color=fill, fill_opacity=1.0)
    if not shadow:
        return VGroup(panel)
    shade = RoundedRectangle(corner_radius=radius, width=width, height=height,
                             stroke_opacity=0, fill_color=CARD_SHADOW,
                             fill_opacity=0.55)
    shade.shift(RIGHT * 0.06 + DOWN * 0.06)
    return VGroup(shade, panel)


def node_label(text: str, color=PRIMARY, width: float = 2.6,
               height: float = 0.72, font_size: int = 20,
               fill: str = CARD_BG) -> VGroup:
    box = RoundedRectangle(corner_radius=0.12, width=width, height=height,
                           stroke_color=color, stroke_width=2,
                           fill_color=fill, fill_opacity=1.0)
    label = MarkupText(text, font_size=font_size, color=color,
                       weight=W_SEMIBOLD).move_to(box.get_center())
    if label.width > width - 0.35:
        label.scale((width - 0.35) / label.width)
    return VGroup(box, label)


# --- Top banner ----------------------------------------------------------

def title_bar(text: str) -> VGroup:
    bar = Rectangle(
        width=config.frame_width,
        height=0.88,
        fill_color=PANEL_DARK,
        fill_opacity=1.0,
        stroke_opacity=0,
    ).to_edge(UP, buff=0)
    accent_strip = Rectangle(
        width=config.frame_width,
        height=0.06,
        fill_color=HIGHLIGHT,
        fill_opacity=1.0,
        stroke_opacity=0,
    ).next_to(bar, DOWN, buff=0)
    left_accent = Rectangle(width=0.08, height=bar.height,
                            fill_color=ACCENT, fill_opacity=1.0,
                            stroke_opacity=0).align_to(bar, LEFT)
    left_accent.move_to([left_accent.get_center()[0], bar.get_center()[1], 0])
    tag = MarkupText("DESIGN PATTERN", font_size=13, weight=W_SEMIBOLD,
                     color=HIGHLIGHT)
    title = MarkupText(text, font_size=31, weight=W_SEMIBOLD,
                       color=WHITE)
    label = VGroup(tag, title).arrange(DOWN, aligned_edge=LEFT, buff=0.03)
    label.move_to(bar.get_center()).align_to(bar, LEFT).shift(RIGHT * 0.55)
    if label.width > config.frame_width - 1.1:
        label.scale((config.frame_width - 1.1) / label.width)
        label.align_to(bar, LEFT).shift(RIGHT * 0.55)
    return VGroup(bar, left_accent, accent_strip, label)


# --- Bullet list ---------------------------------------------------------

def bullet_list(items, size: int = 28, dot_color=HIGHLIGHT,
                text_color=TEXT, buff_v: float = 0.35,
                buff_h: float = 0.3) -> VGroup:
    rows = VGroup()
    for s in items:
        dot = RoundedRectangle(corner_radius=0.03, width=0.18, height=0.18,
                               stroke_opacity=0, fill_color=dot_color,
                               fill_opacity=1.0)
        t = MarkupText(s, font_size=size, color=text_color)
        row = VGroup(dot, t).arrange(RIGHT, buff=buff_h)
        rows.add(row)
    rows.arrange(DOWN, aligned_edge=LEFT, buff=buff_v)
    return rows


# --- Syntax-highlighted code card ----------------------------------------

def code_card(code_str: str, language: str = "java",
              font_size: int = 22, max_width: float | None = None,
              max_height: float | None = None,
              line_spacing: float = 0.65) -> Code:
    """Manim Code block themed like a polished engineering editor."""
    card = Code(
        code_string=code_str.rstrip("\n"),
        language=language,
        formatter_style="monokai",
        add_line_numbers=False,
        background="rectangle",
        background_config={
            "fill_color": CODE_BG,
            "fill_opacity": 1.0,
            "stroke_color": CODE_BORDER,
            "stroke_width": 2,
            "corner_radius": 0.18,
            "buff": 0.25,
        },
        paragraph_config={
            "font": CODE_FONT,
            "font_size": font_size,
            "line_spacing": line_spacing,
        },
    )
    if max_width is not None and card.width > max_width:
        card.scale(max_width / card.width)
    if max_height is not None and card.height > max_height:
        card.scale(max_height / card.height)

    shadow = RoundedRectangle(corner_radius=0.18,
                              width=card.background.width,
                              height=card.background.height,
                              stroke_opacity=0,
                              fill_color=CARD_SHADOW,
                              fill_opacity=0.5)
    shadow.move_to(card.background).shift(RIGHT * 0.06 + DOWN * 0.06)
    card.add_to_back(shadow)
    return card


def highlight_lines(card: Code, indices, color=HIGHLIGHT,
                    buff: float = 0.08, stroke_width: float = 3):
    line_objs = VGroup(*[card.code_lines[i] for i in indices])
    return SurroundingRectangle(line_objs, color=color, buff=buff,
                                stroke_width=stroke_width, corner_radius=0.05,
                                fill_color=color, fill_opacity=0.12)


# --- UML helpers ---------------------------------------------------------

def uml_class_box(name: str, stereotype: str | None = None,
                  attrs: list[str] | None = None,
                  methods: list[str] | None = None,
                  stroke=PRIMARY, fill=CARD_BG,
                  width: float = 4.2, header_color=None) -> VGroup:
    """3-compartment UML class (header, attrs, methods)."""
    header_color = header_color or stroke
    parts = VGroup()

    header_inner = VGroup()
    if stereotype:
        header_inner.add(MarkupText(f"«{stereotype}»",
                                    font_size=18, color=ACCENT,
                                    slant=ITALIC))
    header_inner.add(MarkupText(name, font_size=22, weight=BOLD,
                                color=header_color))
    header_inner.arrange(DOWN, buff=0.06)
    max_inner_width = width - 0.36
    if header_inner.width > max_inner_width:
        header_inner.scale(max_inner_width / header_inner.width)
    header_h = header_inner.height + 0.28
    header_rect = Rectangle(width=width, height=header_h,
                            stroke_color=stroke, stroke_width=2,
                            fill_color=PANEL_DARK, fill_opacity=1.0)
    header_inner.move_to(header_rect.get_center())
    for mob in header_inner:
        mob.set_color(WHITE if mob is header_inner[-1] else HIGHLIGHT)
    parts.add(VGroup(header_rect, header_inner))

    if attrs:
        attr_lines = VGroup(*[
            MarkupText(s, font_size=18, color=TEXT) for s in attrs
        ]).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        max_inner_width = width - 0.36
        if attr_lines.width > max_inner_width:
            attr_lines.scale(max_inner_width / attr_lines.width)
        attr_h = attr_lines.height + 0.28
        attr_rect = Rectangle(width=width, height=attr_h,
                              stroke_color=stroke, stroke_width=2,
                              fill_color=fill, fill_opacity=1.0)
        attr_lines.move_to(attr_rect.get_center()).align_to(
            attr_rect.get_left(), LEFT).shift(RIGHT * 0.18)
        parts.add(VGroup(attr_rect, attr_lines))

    if methods:
        meth_lines = VGroup(*[
            MarkupText(s, font_size=18, color=TEXT) for s in methods
        ]).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        max_inner_width = width - 0.36
        if meth_lines.width > max_inner_width:
            meth_lines.scale(max_inner_width / meth_lines.width)
        meth_h = meth_lines.height + 0.28
        meth_rect = Rectangle(width=width, height=meth_h,
                              stroke_color=stroke, stroke_width=2,
                              fill_color=fill, fill_opacity=1.0)
        meth_lines.move_to(meth_rect.get_center()).align_to(
            meth_rect.get_left(), LEFT).shift(RIGHT * 0.18)
        parts.add(VGroup(meth_rect, meth_lines))

    parts.arrange(DOWN, buff=0)
    return parts


def _hollow_triangle(tip, base_center, color=PRIMARY, size: float = 0.28):
    tip = np.array(tip, dtype=float)
    base_center = np.array(base_center, dtype=float)
    direction = tip - base_center
    norm = np.linalg.norm(direction)
    if norm == 0:
        return VGroup()
    direction = direction / norm
    perp = np.array([-direction[1], direction[0], 0]) * size * 0.6
    base = tip - direction * size
    p1 = base + perp
    p2 = base - perp
    return Polygon(tip, p1, p2,
                   stroke_color=color, stroke_width=2.5,
                   fill_color=BG, fill_opacity=1.0)


def realization_arrow(start, end, color=PRIMARY,
                      dash_length: float = 0.18) -> VGroup:
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    direction = end - start
    norm = np.linalg.norm(direction)
    if norm == 0:
        return VGroup()
    unit = direction / norm
    head_size = 0.28
    line_end = end - unit * head_size
    line = DashedLine(start, line_end, color=color,
                      dash_length=dash_length, stroke_width=2.5)
    head = _hollow_triangle(end, line_end, color=color, size=head_size)
    return VGroup(line, head)


def association_arrow(start, end, color=PRIMARY,
                      label: str | None = None) -> VGroup:
    arrow = Arrow(start=start, end=end, color=color,
                  buff=0.0, stroke_width=2.5,
                  max_tip_length_to_length_ratio=0.05,
                  max_stroke_width_to_length_ratio=5.0)
    group = VGroup(arrow)
    if label:
        lbl = MarkupText(label, font_size=18, color=color, slant=ITALIC)
        mid = (np.array(start) + np.array(end)) / 2
        direction = np.array(end) - np.array(start)
        if np.linalg.norm(direction) > 0:
            unit = direction / np.linalg.norm(direction)
            perp = np.array([-unit[1], unit[0], 0]) * 0.3
            lbl.move_to(mid + perp)
        else:
            lbl.next_to(arrow, UP, buff=0.1)
        group.add(lbl)
    return group
