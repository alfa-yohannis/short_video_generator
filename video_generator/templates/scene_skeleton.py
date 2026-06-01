# Skeleton reference scene. Copy this structure when generating new Manim
# scenes from a storyboard. The same file shape works for both landscape and
# portrait — only layout positions need to change (portrait gets 16-unit tall,
# 9-unit wide frame; keep all content above SHORTS_SAFE_BOTTOM = -4.8).
#
# Required ingredients in every scene:
#   1. `from manim import *` then `from _common import ...`
#   2. Module-level `TARGET_DURATION = audio_duration("<basename>", fallback)`
#   3. A single `class <ClassName>(Scene)` with a `construct` method
#   4. `self.add(tech_background())` before any visible content
#   5. `title_bar(...)` at the top, OR a hero layout (only for opener scenes)
#   6. Every user-visible string wrapped with `L(id_text, en_text)`
#   7. A final `self.wait(max(0.5, TARGET_DURATION - elapsed))` to absorb
#      any difference between animated runtime and audio length
#
# Helpers available from `_common`:
#   Colors:     PRIMARY, ACCENT, HIGHLIGHT, TEXT, OK, DANGER, BG, CODE_BG,
#               PANEL_DARK, MUTED, GRID
#   Weights:    W_REGULAR, W_MEDIUM, W_SEMIBOLD, W_BOLD
#   Text:       title_text, body_text, section_label, bullet_list
#   Structural: tech_background, title_bar, soft_panel, node_label
#   Code:       code_card, highlight_lines
#   UML:        uml_class_box, realization_arrow, association_arrow
#   Locale:     L(id_text, en_text)            # picks per MANIM_LANG
#   Timing:     audio_duration(basename, fallback)
#   Portrait:   SHORTS_SAFE_BOTTOM, fit_to_shorts_area  (portrait _common only)

from manim import *
from _common import (
    PRIMARY, ACCENT, HIGHLIGHT, TEXT,
    title_text, body_text, section_label,
    tech_background, title_bar,
    L, audio_duration,
)

TARGET_DURATION = audio_duration("00_skeleton", 12.0)


class Skeleton(Scene):
    def construct(self):
        self.add(tech_background())

        bar = title_bar(L("Judul Bahasa Indonesia", "English Title"))
        self.play(FadeIn(bar, shift=UP * 0.2), run_time=0.6)

        headline = title_text(
            L("Kalimat utama", "Main statement"),
            size=56, color=PRIMARY,
        )
        sub = body_text(
            L("Penjelasan singkat satu baris.",
              "A short one-line elaboration."),
            size=28, color=TEXT,
        )
        group = VGroup(headline, sub).arrange(DOWN, buff=0.4)
        group.next_to(bar, DOWN, buff=0.8)

        self.play(Write(headline), run_time=1.4)
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.7)

        elapsed = 0.6 + 1.4 + 0.7
        self.wait(max(0.5, TARGET_DURATION - elapsed))
