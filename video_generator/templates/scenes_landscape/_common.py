"""Shared helpers + theme for landscape (16:9) scenes."""

import os
import subprocess
import sys
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
    "NotoSans-Regular.ttf",
    "NotoSans-Medium.ttf",
    "NotoSans-SemiBold.ttf",
    "NotoSans-Bold.ttf",
    "JetBrainsMonoNL-Regular.ttf",
    "JetBrainsMonoNL-Medium.ttf",
]:
    manimpango.register_font(str(_FONT_DIR / _ttf))

# Non-code text (titles, body, subtitles) uses the proportional Noto Sans for
# even, kerned spacing. Code samples use JetBrains Mono NL.
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


# --- Layout self-check & auto-fix -----------------------------------------
# Opt-in via the MANIM_CHECK_LAYOUT env var, which the generator sets from its
# --check-layout flag:
#   unset / "off" (default) → no check, render behaves exactly as before
#   "warn"                  → print any violations to stderr, keep rendering
#   "strict"                → raise LayoutError (fails the render → AI re-repair)
#   "fit"                   → auto-correct the geometric ones in-render (below)
#
# THINGS CHECKED AND FIXED (single source of truth; keep README in sync):
#   1. OVERFLOW    text/blocks past the frame edge (clipping)
#                    detect: yes   auto-fix(fit): yes  (scale + nudge inside;
#                    applied to entering elements too, so a clipped item is
#                    corrected before its first frame — never a visible "pop")
#   2. SAFE-AREA   content below SHORTS_SAFE_BOTTOM (portrait caption zone)
#                    detect: yes   auto-fix(fit): yes  (lift above the line)
#   3. CONTAINMENT text/code spilling outside its own panel/box
#                    detect: —     auto-fix(fit): yes  (shrink content to panel)
#   4. OVERLAP     text-vs-text and block-vs-block collisions
#                    detect: yes   auto-fix(fit): no   (fix via strict + AI repair)
#   5. INTRUDE     text resting over a filled panel it isn't part of (e.g. a
#                  note line on a card's bottom padding)
#                    detect: yes   auto-fix(fit): no   (fix via strict + AI repair)
# Semantic problems (e.g. an arrow pointing the wrong way) are intentionally NOT
# auto-checked here — geometry can't know intent; those are fixed at authoring /
# AI-generation time. Detection runs after every play AND at end of render, so
# transient mid-scene violations are caught, not just the final frame.

class LayoutError(Exception):
    """Raised in strict mode when a scene's text leaves the frame or overlaps."""


def _layout_mode(explicit=None):
    return (explicit or os.environ.get("MANIM_CHECK_LAYOUT", "off")).strip().lower()


def _bbox(m):
    """(x_min, x_max, y_min, y_max) of a mobject in Manim units."""
    return (m.get_left()[0], m.get_right()[0], m.get_bottom()[1], m.get_top()[1])


def _overlap_area(a, b):
    ix = max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[2], b[2]))
    return ix * iy


def _text_mobjects(scene):
    out, ids = [], set()
    for top in scene.mobjects:
        for m in top.get_family():
            if isinstance(m, (Text, MarkupText)) and id(m) not in ids:
                if m.width > 1e-3 and m.height > 1e-3:
                    ids.add(id(m))
                    out.append(m)
    return out


def _text_label(m):
    try:
        t = m.text
    except Exception:
        t = m.__class__.__name__
    return (t or m.__class__.__name__).strip().replace("\n", " ")[:48]


def _content_units(scene):
    """Top-level mobjects that carry visible text and aren't full-bleed bars /
    backgrounds — i.e. the cards, panels, callouts and labels a viewer reads as
    distinct blocks. Used for block-vs-block overlap (a box drawn over code, a
    stray label over a card) that text-vs-text comparison alone misses."""
    fw, fh = config.frame_width, config.frame_height
    cand = []
    for top in scene.mobjects:
        if not _has_text(top):
            continue
        w, h = top.width, top.height
        if w <= 1e-3 or h <= 1e-3:
            continue
        if w >= 0.97 * fw or h >= 0.97 * fh:   # full-bleed bar / background
            continue
        cand.append(top)
    # Drop nested / promoted items: a unit whose centre sits inside a LARGER
    # unit's box is that block's own content, not a peer block. Manim promotes a
    # sub-mobject to the top level when you animate it (e.g. Indicate(child)),
    # which would otherwise read as the child "overlapping" its own parent card.
    boxes = []
    for c in cand:
        bb = _bbox(c)
        boxes.append((bb, (bb[1] - bb[0]) * (bb[3] - bb[2]), c))
    out = []
    for bi, ai, ci in boxes:
        cx, cy = (bi[0] + bi[1]) / 2.0, (bi[2] + bi[3]) / 2.0
        nested = any(
            cj is not ci and aj > ai
            and bj[0] <= cx <= bj[1] and bj[2] <= cy <= bj[3]
            for bj, aj, cj in boxes
        )
        if not nested:
            out.append(ci)
    return out


def _filled_panels(scene):
    """Opaque rectangle panels (a card / box background a viewer can't see
    through), excluding full-bleed bars/backgrounds. Foreign text drawn over one
    of these visually collides even if it only touches the panel's padding."""
    fw, fh = config.frame_width, config.frame_height
    out, ids = [], set()
    for top in scene.mobjects:
        for m in top.get_family():
            if isinstance(m, (Rectangle, RoundedRectangle)) and id(m) not in ids:
                try:
                    op = float(m.get_fill_opacity())
                except Exception:
                    op = 0.0
                w, h = m.width, m.height
                if op >= 0.5 and w > 0.4 and h > 0.4 and not (
                    w >= 0.97 * fw or h >= 0.97 * fh
                ):
                    ids.add(id(m))
                    out.append(m)
    return out


def _detect_layout_issues(scene, overlap_frac=0.5, eps=0.05):
    """Pure detector: return the list of violation strings (no logging,
    no raising). Shared by the end-of-render check and the during-render pass."""
    fw, fh = config.frame_width, config.frame_height
    texts = _text_mobjects(scene)
    issues = []

    # 1. Off-frame overflow / clipping.
    for m in texts:
        x0, x1, y0, y1 = _bbox(m)
        if x0 < -fw / 2 - eps or x1 > fw / 2 + eps or y0 < -fh / 2 - eps or y1 > fh / 2 + eps:
            issues.append(
                f"OVERFLOW: {_text_label(m)!r} extends past the frame "
                f"(x[{x0:.2f},{x1:.2f}] y[{y0:.2f},{y1:.2f}], frame {fw:.1f}x{fh:.1f})"
            )

    # 2. Portrait caption-reserved zone (only where SHORTS_SAFE_BOTTOM exists).
    safe_bottom = globals().get("SHORTS_SAFE_BOTTOM")
    if safe_bottom is not None:
        for m in texts:
            y0 = _bbox(m)[2]
            if y0 < safe_bottom - eps:
                issues.append(
                    f"SAFE-AREA: {_text_label(m)!r} dips below SHORTS_SAFE_BOTTOM "
                    f"({y0:.2f} < {safe_bottom:.2f}; the bottom 2/10 is reserved "
                    "for Reels/Shorts/TikTok captions)"
                )

    # 3. Significant text-text overlap (ignores ancestor/descendant pairs).
    boxes = [(_bbox(m), m) for m in texts]
    for i in range(len(boxes)):
        bi, mi = boxes[i]
        area_i = (bi[1] - bi[0]) * (bi[3] - bi[2])
        for j in range(i + 1, len(boxes)):
            bj, mj = boxes[j]
            if mi in mj.get_family() or mj in mi.get_family():
                continue
            area_j = (bj[1] - bj[0]) * (bj[3] - bj[2])
            smaller = min(area_i, area_j)
            ov = _overlap_area(bi, bj)
            if smaller > 1e-6 and ov > overlap_frac * smaller:
                issues.append(
                    f"OVERLAP: {_text_label(mi)!r} and {_text_label(mj)!r} overlap "
                    f"({ov / smaller * 100:.0f}% of the smaller box)"
                )

    # 4. Block-vs-block overlap: two distinct content groups (a card, a panel,
    #    a callout) whose bounding boxes collide — e.g. a summary box drawn over
    #    a code card, or a stray label over a panel.
    units = [(_bbox(u), u) for u in _content_units(scene)]
    for i in range(len(units)):
        bi, ui = units[i]
        area_i = (bi[1] - bi[0]) * (bi[3] - bi[2])
        for j in range(i + 1, len(units)):
            bj, uj = units[j]
            if ui in uj.get_family() or uj in ui.get_family():
                continue
            area_j = (bj[1] - bj[0]) * (bj[3] - bj[2])
            smaller = min(area_i, area_j)
            ov = _overlap_area(bi, bj)
            if smaller > 1e-6 and ov > overlap_frac * smaller:
                issues.append(
                    f"OVERLAP: block {_text_label(ui)!r} and block {_text_label(uj)!r} "
                    f"overlap ({ov / smaller * 100:.0f}% of the smaller block)"
                )

    # 5. Text intruding into a filled panel it doesn't belong to — e.g. a note
    #    line resting on a card's bottom padding. Caught even when no glyphs
    #    collide (text-text) and the overlap is well under half a block.
    panels = [(_bbox(p), p) for p in _filled_panels(scene)]
    for m in texts:
        tb = _bbox(m)
        ta = (tb[1] - tb[0]) * (tb[3] - tb[2])
        if ta <= 1e-6:
            continue
        tcx, tcy = (tb[0] + tb[1]) / 2.0, (tb[2] + tb[3]) / 2.0
        for pb, p in panels:
            if m in p.get_family() or p in m.get_family():
                continue
            # Skip the panel's own content / an intentional overlay: a text
            # whose centre sits inside the panel isn't "intruding" from outside.
            if pb[0] <= tcx <= pb[1] and pb[2] <= tcy <= pb[3]:
                continue
            ov = _overlap_area(tb, pb)
            if ov > 0.30 * ta:
                issues.append(
                    f"INTRUDE: {_text_label(m)!r} overlaps a panel it isn't part "
                    f"of ({ov / ta * 100:.0f}% of the text is inside the box)"
                )
                break

    return issues


def _report_layout(scene, issues, mode, seen=None):
    """Log new issues to stderr; raise LayoutError in strict mode. When `seen`
    is given, only issues not already in it are reported (used to de-dupe the
    repeated during-render passes)."""
    new = []
    for s in issues:
        if seen is not None:
            if s in seen:
                continue
            seen.add(s)
        new.append(s)
    if not new:
        return new
    header = f"[layout] {len(new)} issue(s) in {type(scene).__name__}:"
    print(header, file=sys.stderr)
    for s in new:
        print(f"  - {s}", file=sys.stderr)
    if mode == "strict":
        raise LayoutError(header + " " + "; ".join(new))
    return new


def check_layout(scene, mode=None, overlap_frac=0.5, eps=0.05):
    """Inspect a scene's text/blocks for off-frame overflow, portrait safe-area
    violations, and significant overlap. Returns the issue strings; logs them in
    warn/strict mode and raises in strict mode."""
    mode = _layout_mode(mode)
    if mode in ("", "0", "off", "false", "no", "none"):
        return []
    issues = _detect_layout_issues(scene, overlap_frac, eps)
    _report_layout(scene, issues, mode)
    return issues


def _check_during_render(scene):
    """Run the detector after each play in warn/strict mode so mid-scene
    violations (a callout that later fades out, a transient overlap) are caught
    too — not just whatever survives to the final frame. De-duped per scene."""
    mode = _layout_mode()
    if mode not in ("warn", "strict"):
        return
    seen = getattr(scene, "_layout_seen", None)
    if seen is None:
        seen = set()
        scene._layout_seen = seen
    _report_layout(scene, _detect_layout_issues(scene), mode, seen=seen)


# --- Auto-fit (opt-in via MANIM_CHECK_LAYOUT=fit) -------------------------
# In "fit" mode we don't just report overflow — we readjust the offending text
# so its bounding box lands back inside the frame (and, in portrait, above the
# caption safe zone) *before* the frames that show it are rendered. The fit is
# geometry only: shrink a too-big label, then translate a clipped one inward.
# It runs right before every self.play / self.wait (the calls that emit frames)
# so the correction is baked into the output — unlike the end-of-render check,
# which fires too late to change what was already drawn.

def _box_dims_ok(m):
    """True for a rectangle-ish panel we may shrink content into — not a
    full-bleed background/title bar and not a hairline accent strip."""
    fw, fh = config.frame_width, config.frame_height
    fam = m.get_family()
    has_rect = any(isinstance(x, (Rectangle, RoundedRectangle)) for x in fam)
    has_text = any(isinstance(x, (Text, MarkupText)) for x in fam)
    if not has_rect or has_text:
        return False
    w, h = m.width, m.height
    if w < 0.4 or h < 0.4:
        return False
    if w >= 0.97 * fw or h >= 0.97 * fh:   # full-bleed bar / background
        return False
    return True


def _has_text(m):
    return any(isinstance(x, (Text, MarkupText)) and x.width > 1e-3 and x.height > 1e-3
               for x in m.get_family())


def _fit_content_in_box(content, box, pad=0.14):
    """Scale a content group down as a whole (so internal alignment survives)
    and recenter it on `box` — but only when it actually overflows the box and
    the shrink is modest. A drastic shrink means `box` isn't really this
    content's container (e.g. a thin highlight rectangle laid over it), so we
    leave it for the AI-repair path rather than squashing it to nothing."""
    bx0, bx1, by0, by1 = _bbox(box)
    avail_w = (bx1 - bx0) - 2 * pad
    avail_h = (by1 - by0) - 2 * pad
    if avail_w <= 0.1 or avail_h <= 0.1:
        return False
    cw, ch = content.width, content.height
    if cw <= 1e-6 or ch <= 1e-6 or (cw <= avail_w and ch <= avail_h):
        return False
    factor = min(avail_w / cw, avail_h / ch, 1.0)
    if factor < 0.5:          # too aggressive — `box` isn't a real container
        return False
    content.scale(factor)
    content.move_to(box.get_center())
    return True


def _autofit_boxes(roots):
    """Keep panel contents inside their panel: for each parent, match a content
    child to its smallest *plausible* enclosing sibling box and shrink it to
    fit. Matches the `VGroup(panel, content)` idiom AI-generated scenes use. A
    box only counts as a container when it's comparable to / bigger than the
    content — so a thin highlight / SurroundingRectangle laid over a card never
    causes the whole card to be squashed into it."""
    def process(children):
        boxes = [k for k in children if _box_dims_ok(k)]
        if boxes:
            for c in children:
                if c in boxes or not _has_text(c):
                    continue
                bc = _bbox(c)
                c_area = (bc[1] - bc[0]) * (bc[3] - bc[2])
                cx, cy = c.get_center()[0], c.get_center()[1]
                best, best_area = None, None
                for b in boxes:
                    if b is c or b in c.get_family() or c in b.get_family():
                        continue
                    x0, x1, y0, y1 = _bbox(b)
                    if not (x0 <= cx <= x1 and y0 <= cy <= y1):
                        continue
                    area = (x1 - x0) * (y1 - y0)
                    if area < 0.6 * c_area:   # too small to be the container
                        continue
                    if best_area is None or area < best_area:
                        best, best_area = b, area
                if best is not None:
                    _fit_content_in_box(c, best)
        for k in children:
            subs = list(getattr(k, "submobjects", []))
            if subs:
                process(subs)
    process(list(roots))


def _fit_into_frame(m, eps=0.08):
    """Scale + translate one mobject so its bounding box sits inside the frame
    and above SHORTS_SAFE_BOTTOM (when defined). Skips full-bleed bars /
    backgrounds. Returns True if changed."""
    fw, fh = config.frame_width, config.frame_height
    if m.width <= 1e-6 or m.height <= 1e-6:
        return False
    if m.width >= 0.97 * fw or m.height >= 0.97 * fh:  # full-bleed: leave alone
        return False
    safe_bottom = globals().get("SHORTS_SAFE_BOTTOM")
    left_lim, right_lim = -fw / 2 + eps, fw / 2 - eps
    top_lim = fh / 2 - eps
    bot_lim = (safe_bottom if safe_bottom is not None else -fh / 2) + eps
    changed = False

    # 1. Shrink to fit the usable width/height band.
    factor = min(1.0, (right_lim - left_lim) / m.width, (top_lim - bot_lim) / m.height)
    if factor < 1.0 - 1e-3:
        m.scale(factor)
        changed = True

    # 2. Translate the (possibly shrunk) box inside the limits.
    x0, x1, y0, y1 = _bbox(m)
    dx = (right_lim - x1) if x1 > right_lim else 0.0
    if x0 + dx < left_lim:
        dx += left_lim - (x0 + dx)
    dy = (top_lim - y1) if y1 > top_lim else 0.0
    if y0 + dy < bot_lim:
        dy += bot_lim - (y0 + dy)
    if abs(dx) > 1e-6 or abs(dy) > 1e-6:
        m.shift(RIGHT * dx + UP * dy)
        changed = True
    return changed


def _animation_mobjects(animations):
    """Mobjects an about-to-play animation touches (handles nested groups)."""
    out, stack = [], list(animations)
    while stack:
        a = stack.pop()
        mob = getattr(a, "mobject", None)
        if mob is not None:
            out.append(mob)
        subs = getattr(a, "animations", None)
        if subs:
            stack.extend(subs)
    return out


def _autofit_scene(scene, extra=()):
    """In fit mode: (1) keep each panel's contents inside the panel, then
    (2) clamp every top-level content group inside the frame / above the
    portrait safe area. Runs before each play / wait so the fix is rendered."""
    if _layout_mode() != "fit":
        return
    roots = [m for m in (list(scene.mobjects) + [m for m in extra if m is not None])
             if not getattr(m, "_vgen_overlay", False)]   # never move the brand logo
    _autofit_boxes(roots)
    # Frame-clamp top-level items AND entering animation targets, so a clipped
    # element is corrected before its intro frame renders (no visible "pop"
    # where it appears off-frame then jumps in). Skip any item nested inside
    # another in the set so a group and its child aren't clamped twice.
    for m in roots:
        if any(other is not m and m in other.get_family() for other in roots):
            continue
        _fit_into_frame(m)


# --- Brand logo watermark (bottom-right, per-language) --------------------
# A small, semi-transparent horizontal logo sits at the BOTTOM-RIGHT of every
# scene: "Belajar" (ayo-belajar-horizontal) for Indonesian, "Learn"
# (ayo-learn-horizontal) for English. It's tagged ``_vgen_overlay`` so the
# layout self-check / auto-fit never move or flag it, and drawn BEHIND scene
# content (low z-index) so objects render over it; the play/wait hooks just
# re-add it if a scene clears the canvas.

def _make_brand_logo():
    """Build the language-specific horizontal logo, placed bottom-right."""
    name = "ayo-learn-horizontal" if LANG_CODE == "en" else "ayo-belajar-horizontal"
    logo_dir = ROOT_DIR / "assets" / "logo"
    logo = None
    svg = logo_dir / f"{name}.svg"
    if svg.exists():
        try:
            logo = SVGMobject(str(svg))
        except Exception:
            logo = None
    if logo is None or len(logo.submobjects) == 0:   # fall back to the PNG
        png = logo_dir / f"{name}.png"
        if png.exists():
            try:
                logo = ImageMobject(str(png))
            except Exception:
                logo = None
    if logo is None:
        return None

    fw, fh = config.frame_width, config.frame_height
    target_w = min(2.0, max(1.5, fw * 0.135))   # small (landscape)
    logo.scale_to_fit_width(target_w)
    margin = 0.3
    x = fw / 2 - margin - logo.width / 2
    y = -fh / 2 + margin + logo.height / 2       # bottom-right corner
    logo.move_to([x, y, 0])
    logo.set_z_index(-10)        # above the background (z=-20), below all content
    try:
        logo.set_opacity(0.5)    # semi-transparent
    except Exception:
        pass
    logo._vgen_overlay = True
    return logo


def _add_brand_logo(scene):
    if getattr(scene, "_vgen_logo", None) is not None:
        return
    logo = _make_brand_logo()
    if logo is None:
        return
    scene._vgen_logo = logo
    scene.add(logo)              # normal mobject; z_index keeps it behind content


def _ensure_logo_present(scene):
    """Re-add the logo if a scene cleared the canvas; z_index keeps it behind
    content, so no need to reorder."""
    logo = getattr(scene, "_vgen_logo", None)
    if logo is None:
        return
    try:
        if logo not in scene.mobjects:
            scene.add(logo)
    except Exception:
        pass


_orig_scene_render = Scene.render
_orig_scene_play = Scene.play
_orig_scene_wait = Scene.wait


def _patched_scene_render(self, *args, **kwargs):
    _add_brand_logo(self)
    result = _orig_scene_render(self, *args, **kwargs)
    check_layout(self)
    return result


def _patched_scene_play(self, *animations, **kwargs):
    _autofit_scene(self, extra=_animation_mobjects(animations))
    _ensure_logo_present(self)
    result = _orig_scene_play(self, *animations, **kwargs)
    _check_during_render(self)
    return result


def _patched_scene_wait(self, *args, **kwargs):
    _autofit_scene(self)
    _ensure_logo_present(self)
    result = _orig_scene_wait(self, *args, **kwargs)
    _check_during_render(self)
    return result


Scene.render = _patched_scene_render
Scene.play = _patched_scene_play
Scene.wait = _patched_scene_wait


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


def fit_inside(content: Mobject, box: Mobject, pad: float = 0.25) -> Mobject:
    """Shrink `content` (never enlarge) so its bounding box fits inside `box`
    with `pad` units of clearance on every side, then center it on `box`.

    Use this whenever text or a code block is dropped onto a fixed-size
    `soft_panel(...)` / rectangle: it guarantees the content can't spill past
    the border (the recurring "text overflows its box" bug)."""
    avail_w = max(0.1, box.width - 2 * pad)
    avail_h = max(0.1, box.height - 2 * pad)
    if content.width > avail_w or content.height > avail_h:
        factor = min(avail_w / content.width, avail_h / content.height)
        if 0 < factor < 1:
            content.scale(factor)
    content.move_to(box.get_center())
    return content


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

def title_bar(text: str, eyebrow: str = "") -> VGroup:
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
    title = MarkupText(text, font_size=31, weight=W_SEMIBOLD,
                       color=WHITE)
    if eyebrow:
        tag = MarkupText(eyebrow, font_size=13, weight=W_SEMIBOLD,
                         color=HIGHLIGHT)
        label = VGroup(tag, title).arrange(DOWN, aligned_edge=LEFT, buff=0.03)
    else:
        label = VGroup(title)
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
