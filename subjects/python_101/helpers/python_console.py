# --- Python console / output helpers --------------------------------------
# Subject-pack scene helpers for `subject: python_101`. This file is a FRAGMENT:
# the build pipeline (scenes.SceneSynthesizer.materialize_dir) APPENDS it into
# the build's `_common.py`, so it relies on names already defined there —
# `from manim import *` (Rectangle, RoundedRectangle, Text, VGroup, LEFT, RIGHT,
# UP, DOWN, ORIGIN), and the theme constants (CODE_BG, CODE_BORDER, CARD_SHADOW,
# TEXT, MUTED, OK, DANGER, CODE_FONT). It is not meant to be imported on its own.
# Generated Python scenes then do `from _common import (console_panel, repl)`.
#
# These show the RESULT of running code — a terminal window for program output
# and a REPL transcript — so a tutorial can pair a typed `code_card` with what it
# prints. They pair naturally with the python_dark template's typing animations
# (reveal each output line with `type_text`, or the whole panel with `FadeIn`).


def _console_dots():
    """The three macOS-style traffic-light dots for a window title bar."""
    from manim import Circle  # local import keeps the fragment self-contained
    colors = ["#FF5F56", "#FFBD2E", "#27C93F"]
    dots = VGroup(*[
        Circle(radius=0.07, fill_color=c, fill_opacity=1.0, stroke_opacity=0)
        for c in colors
    ]).arrange(RIGHT, buff=0.12)
    return dots


def console_panel(lines, width: float = 6.6, title: str = "Output",
                  font_size: int = 24, line_buff: float = 0.16,
                  ok_color=OK) -> VGroup:
    """A dark terminal window showing program output.

    ``lines`` is a list of strings, or of ``(text, color)`` pairs to color a
    line (e.g. errors in DANGER, results in OK). Returns a VGroup laid out as a
    titled window; drop it next to a ``code_card`` to show what the code prints.
    """
    from manim import Line

    header_h = 0.5
    title_t = Text(title, font=CODE_FONT, font_size=font_size - 4, color=MUTED)
    dots = _console_dots()

    body = VGroup()
    for item in lines:
        text, color = item if isinstance(item, (tuple, list)) else (item, TEXT)
        body.add(Text(str(text), font=CODE_FONT, font_size=font_size, color=color))
    if len(body) > 0:
        body.arrange(DOWN, aligned_edge=LEFT, buff=line_buff)

    inner_w = width - 0.5
    if len(body) > 0 and body.width > inner_w:
        body.scale(inner_w / body.width)

    body_h = (body.height if len(body) > 0 else 0.0) + 0.5
    height = header_h + body_h
    win = RoundedRectangle(corner_radius=0.14, width=width, height=height,
                           stroke_color=CODE_BORDER, stroke_width=1.5,
                           fill_color=CODE_BG, fill_opacity=1.0)
    shadow = RoundedRectangle(corner_radius=0.14, width=width, height=height,
                              stroke_opacity=0, fill_color=CARD_SHADOW,
                              fill_opacity=0.55)
    shadow.move_to(win).shift(RIGHT * 0.07 + DOWN * 0.07)

    rule = Line(win.get_left() + UP * (height / 2 - header_h) + RIGHT * 0.02,
                win.get_right() + UP * (height / 2 - header_h) + LEFT * 0.02,
                color=CODE_BORDER, stroke_width=1.0)

    dots.next_to(win.get_corner(UP + LEFT), DOWN + RIGHT, buff=0.18)
    title_t.move_to([win.get_center()[0], dots.get_center()[1], 0])

    if len(body) > 0:
        body.move_to([win.get_center()[0],
                      win.get_bottom()[1] + body_h / 2, 0])
        body.align_to(win.get_left() + RIGHT * 0.32, LEFT)

    return VGroup(shadow, win, rule, dots, title_t, body)


def repl(pairs, font_size: int = 24, prompt: str = ">>>",
         prompt_color=OK, line_buff: float = 0.18) -> VGroup:
    """A Python REPL transcript: ``pairs`` is a list of ``(input, output)``.

    Each input is shown after a ``>>>`` prompt; a non-empty output is shown on
    the next line. Returns a left-aligned VGroup of monospace lines."""
    rows = VGroup()
    for item in pairs:
        src, out = item if isinstance(item, (tuple, list)) else (item, "")
        line = VGroup(
            Text(prompt, font=CODE_FONT, font_size=font_size, color=prompt_color),
            Text(str(src), font=CODE_FONT, font_size=font_size, color=TEXT),
        ).arrange(RIGHT, buff=0.22)
        rows.add(line)
        if str(out) != "":
            rows.add(Text(str(out), font=CODE_FONT, font_size=font_size,
                          color=MUTED))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=line_buff)
    return rows
