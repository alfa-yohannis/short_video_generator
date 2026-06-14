# --- Orientation delta: portrait (9:16) -----------------------------------
# Spliced into _core.py at the ORIENTATION_DELTA marker by
# scenes.SceneSynthesizer.materialize_dir. Sets the portrait frame, the
# (slightly larger) size constants the core helpers read, the Reels/Shorts
# caption-safe reserve, and fit_to_shorts_area. Not importable on its own
# (relies on _core's `from manim import *` / theme constants above the marker).

# Portrait frame: 9:16. Use 16 units tall, 9 wide.
config.frame_height = 16.0
config.frame_width = 9.0
config.pixel_height = 1920
config.pixel_width = 1080

TITLE_SIZE = 48
BODY_SIZE = 34
SECTION_SIZE = 30
LOGO_W_CAP, LOGO_W_FLOOR, LOGO_W_FACTOR = 3.2, 2.0, 0.2
TOP_RULE_H = 0.05
SOFT_RADIUS = 0.18
NODE_W, NODE_H, NODE_FS, NODE_RADIUS, NODE_MARGIN = 4.8, 0.82, 25, 0.14, 0.45
BAR_H, BAR_STRIP_H, BAR_TITLE_FS, BAR_TAG_FS, BAR_TAG_BUFF, BAR_SHIFT, BAR_PAD = \
    1.18, 0.08, 39, 18, 0.04, 0.45, 0.9
BULLET_SIZE, BULLET_BUFF_V, BULLET_DOT_RAD, BULLET_DOT_SIZE = 32, 0.45, 0.04, 0.22
UML_W, UML_STEREO_FS, UML_NAME_FS, UML_INNER_PAD, UML_PAD, UML_BODY_FS, UML_SHIFT = \
    6.5, 22, 26, 0.4, 0.32, 22, 0.2
HEAD_SIZE, REAL_DASH, ASSOC_FS, ASSOC_PERP = 0.32, 0.2, 22, 0.35

# Reels/Shorts/TikTok reserve: keep the bottom 2/10 of portrait frames empty
# for platform captions and UI overlays. Content should stay above y = -4.8.
SHORTS_SAFE_BOTTOM = -config.frame_height / 2 + config.frame_height * 0.2
SHORTS_SAFE_TOP = config.frame_height / 2 - 1.85
SHORTS_SAFE_WIDTH = config.frame_width - 0.6


def fit_to_shorts_area(mob: Mobject, top: float = SHORTS_SAFE_TOP,
                       bottom: float = SHORTS_SAFE_BOTTOM,
                       max_width: float = SHORTS_SAFE_WIDTH,
                       buff: float = 0.08) -> Mobject:
    """Fit a group above the lower 2/10 caption-safe zone."""
    max_height = top - bottom - 2 * buff
    if max_width is not None and mob.width > max_width:
        mob.scale(max_width / mob.width)
    if mob.height > max_height:
        mob.scale(max_height / mob.height)
    mob.move_to([mob.get_center()[0], (top + bottom) / 2, 0])
    return mob
