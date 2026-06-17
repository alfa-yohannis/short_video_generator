# --- Orientation delta: landscape (16:9) ----------------------------------
# Spliced into _core.py at the ORIENTATION_DELTA marker by
# scenes.SceneSynthesizer.materialize_dir. Defines the size constants the core
# helpers read. Landscape uses Manim's default 16:9 frame, so no frame override.
# Not importable on its own (relies on _core's imports above the marker).

TITLE_SIZE = 40
BODY_SIZE = 28
SECTION_SIZE = 24
LOGO_W_CAP, LOGO_W_FLOOR, LOGO_W_FACTOR = 2.0, 1.5, 0.135
TOP_RULE_H = 0.04
SOFT_RADIUS = 0.16
NODE_W, NODE_H, NODE_FS, NODE_RADIUS, NODE_MARGIN = 2.6, 0.72, 20, 0.12, 0.35
BAR_H, BAR_STRIP_H, BAR_TITLE_FS, BAR_TAG_FS, BAR_TAG_BUFF, BAR_SHIFT, BAR_PAD = \
    0.88, 0.06, 31, 13, 0.03, 0.55, 1.1
BULLET_SIZE, BULLET_BUFF_V, BULLET_DOT_RAD, BULLET_DOT_SIZE = 28, 0.35, 0.03, 0.18
UML_W, UML_STEREO_FS, UML_NAME_FS, UML_INNER_PAD, UML_PAD, UML_BODY_FS, UML_SHIFT = \
    4.2, 18, 22, 0.36, 0.28, 18, 0.18
HEAD_SIZE, REAL_DASH, ASSOC_FS, ASSOC_PERP = 0.28, 0.18, 18, 0.3

# Caret (typing-cursor) height for type_text(..., cursor=caret()).
CARET_H = 0.42

# Landscape has no Reels/Shorts caption-safe reserve; tech_background() draws the
# corner bracket when this is None (the portrait delta sets it to a real value).
SHORTS_SAFE_BOTTOM = None


# --- Fixed code / output stage (landscape) --------------------------------
# Two anchored slots a code-walkthrough scene fills consistently: the code card
# on the left, its program output on the right — same place, same bounded size
# in every scene (see place_code / place_output in _core). The wide 16:9 frame
# favours side-by-side over stacking. CX = horizontal centre, TOP = top edge
# (content is top-anchored so it grows downward predictably).
_STAGE_TOP = config.frame_height / 2 - BAR_H - 0.35
_STAGE_H = config.frame_height - BAR_H - 1.1

CODE_SLOT_CX = -config.frame_width / 4
CODE_SLOT_TOP = _STAGE_TOP
CODE_SLOT_W = config.frame_width / 2 - 0.9
CODE_SLOT_H = _STAGE_H

OUTPUT_SLOT_CX = config.frame_width / 4
OUTPUT_SLOT_TOP = _STAGE_TOP
OUTPUT_SLOT_W = config.frame_width / 2 - 1.2
OUTPUT_SLOT_H = _STAGE_H
