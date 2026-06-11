"""Reading a storyboard markdown file into a :class:`Storyboard` object.

`StoryboardParser` is a small *service* class: give it a path, get back a fully
populated domain object. Two markdown shapes are accepted.

Simplified (recommended for humans) — front-matter is optional, scenes are plain
``##`` headings with the description right underneath, durations are inline:

    ---
    language: both        # optional; id | en | both
    length: 2-3 minutes   # optional
    ---
    # Strategy Pattern    # the title (else the filename)

    A project brief paragraph...

    ## Introduction (~15s)
    Show the title and explain the idea...

Legacy (still fully supported) — explicit metadata and ``###`` subsections:

    ---
    title: ...
    languages: [id, en]
    ---
    ## Scene: 01_pengantar / Pengantar
    **file:** scene_01_pengantar.py
    **fallback_duration:** 12
    ### description
    ...
    ### narration.id
    ...

Technical fields (file name, class name, fps, resolution) are derived when
omitted; provider settings (tts, ai) accept friendly aliases; secrets are never
read from the storyboard (use --gemini-api-key / $GEMINI_API_KEY / .env).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import config
from .progress import progress
from .models import Scene, Storyboard
from .text_utils import camel_from_snake, slugify, strip_leading_digits


# --- duration parsing (a pure helper used by the parser) -------------------

_DURATION_SPEC_RE = re.compile(
    r"^\s*([0-9]*\.?[0-9]+)\s*"
    r"(h(?:ours?|rs?)?|m(?:in(?:ute)?s?)?|s(?:ec(?:ond)?s?)?)?\s*$",
    re.I,
)


def safe_duration_spec(value) -> Optional[float]:
    """Like :func:`parse_duration_spec` but returns ``None`` instead of raising
    when the value isn't a valid duration (used to *probe* heading text)."""
    try:
        return parse_duration_spec(value)
    except SystemExit:
        return None


def parse_duration_spec(value) -> Optional[float]:
    """Parse a duration into seconds.

    Accepts a number (seconds), a unit string like ``"3 minutes"`` / ``"90s"`` /
    ``"1.5 min"``, or a clock form ``"M:SS"`` / ``"H:MM:SS"``. ``None``/empty -> None.
    """
    if value is None:
        return None
    if isinstance(value, bool):           # bool is a subclass of int — guard it
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    if ":" in text:
        try:
            numbers = [float(p) for p in text.split(":")]
        except ValueError:
            raise SystemExit(f"Invalid duration '{value}'. Use seconds, '3 minutes', or 'M:SS'.")
        total = 0.0
        for number in numbers:            # base-60 accumulation: H:MM:SS
            total = total * 60 + number
        return total
    match = _DURATION_SPEC_RE.match(text)
    if not match:
        raise SystemExit(f"Invalid duration '{value}'. Use seconds, '3 minutes', or 'M:SS'.")
    amount = float(match.group(1))
    unit = (match.group(2) or "s").lower()
    if unit.startswith("h"):
        return amount * 3600
    if unit.startswith("m"):
        return amount * 60
    return amount


class StoryboardParser:
    """Turns a storyboard markdown file into a :class:`Storyboard`."""

    _FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
    # Any level-2 heading is a scene. Legacy `## Scene: <name>` still matches
    # (the "Scene:" label is stripped in parse_scene); the simplified format uses
    # a plain `## Human Title`. `###` subsections never match (no space after ##).
    _SCENE_HEADING_RE = re.compile(r"^##[ \t]+(.+?)\s*$", re.M)
    _H1_RE = re.compile(r"^#[ \t]+(.+?)\s*$", re.M)
    # A dedicated `# Preparation` block (setup/reference notes) that sits between
    # the project brief and the first `## ` scene. It is NOT a scene; the parser
    # lifts it out into Storyboard.preparation and feeds it to scene generation.
    _PREPARATION_HEADING_RE = re.compile(
        r"^#[ \t]+preparation[ \t]*(?::|\(.*\))?[ \t]*$", re.I | re.M
    )
    _HEADING_DURATION_RE = re.compile(r"\(([^()]*)\)\s*$")
    _SUBSECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.M)
    _FILE_META_RE = re.compile(r"\*\*file:\*\*\s*([^\s]+)", re.I)
    _DURATION_META_RE = re.compile(r"\*\*fallback[_ ]duration:\*\*\s*([0-9.]+)", re.I)
    _CLASS_META_RE = re.compile(r"\*\*class:\*\*\s*([^\s]+)", re.I)

    # --- scenes ------------------------------------------------------------

    def parse_scene(self, header: str, body: str) -> Scene:
        """Build one :class:`Scene` from its ``##`` heading and body text.

        Supports both the legacy ``## Scene: 01_x / ClassName`` form and the
        simplified ``## Human Title (~15s)`` form.
        """
        header, heading_duration = self._extract_heading_duration(header.strip())
        header = re.sub(r"^scene\s*:\s*", "", header, flags=re.I).strip()

        classname = ""
        if "/" in header:                       # legacy: "01_x / ClassName"
            left, right = (s.strip() for s in header.split("/", 1))
            basename, classname = left, right    # keep the legacy slug verbatim
        else:
            basename = slugify(header)           # plain heading or bare slug -> slug

        class_meta = self._CLASS_META_RE.search(body)
        if class_meta:
            classname = class_meta.group(1).strip()
        if not classname:
            classname = camel_from_snake(strip_leading_digits(basename))

        file_match = self._FILE_META_RE.search(body)
        file_path = file_match.group(1).strip() if file_match else f"scene_{basename}.py"
        dur_match = self._DURATION_META_RE.search(body)
        if dur_match is not None:                # explicit legacy meta wins
            fallback_duration = float(dur_match.group(1))
        elif heading_duration is not None:       # simplified "(~15s)" form
            fallback_duration = heading_duration
        else:
            fallback_duration = 15.0

        # Strip metadata lines so they don't leak into description/extras.
        clean = self._FILE_META_RE.sub("", body)
        clean = self._DURATION_META_RE.sub("", clean)
        clean = self._CLASS_META_RE.sub("", clean)

        description, narration, extras = self._parse_subsections(clean)
        return Scene(
            basename=basename, classname=classname, file=file_path,
            fallback_duration=fallback_duration, description=description,
            narration=narration, extras=extras,
        )

    @classmethod
    def _extract_heading_duration(cls, header: str) -> Tuple[str, Optional[float]]:
        """Pull a trailing ``(~15s)`` / ``(20 sec)`` / ``(0:20)`` off a heading.

        Returns ``(heading_without_duration, seconds_or_None)``. A trailing
        parenthetical that isn't a duration (e.g. ``(MVC)``) is left in place.
        """
        m = cls._HEADING_DURATION_RE.search(header)
        if not m:
            return header, None
        inner = m.group(1).strip()
        had_tilde = inner.startswith("~")
        core = inner.lstrip("~").strip()
        # Only treat as a duration if it starts with a digit and is clearly a
        # time (has ~, a unit letter, or a clock colon) — so "(MVC)"/"(2)" stay.
        looks_like_time = bool(core) and core[0].isdigit() and (
            had_tilde or ":" in core or re.search(r"[A-Za-z]", core)
        )
        if not looks_like_time:
            return header, None
        seconds = safe_duration_spec(core)
        if seconds is None:
            return header, None
        return header[: m.start()].strip(), seconds

    def _parse_subsections(self, body: str):
        """Split a scene body's ``### ...`` subsections into description /
        narration / everything-else.

        In the simplified format there are no ``###`` subsections, so the scene's
        body text *is* the description (parts[0]); an explicit ``### description``
        still wins when present (legacy format)."""
        parts = self._SUBSECTION_RE.split(body)
        description = ""
        narration: Dict[str, str] = {}
        extras: Dict[str, str] = {}
        # parts[0] is the text before any ###; then alternating key / content.
        for i in range(1, len(parts), 2):
            key = parts[i].strip().lower()
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            if key == "description":
                description = content
            elif key.startswith("narration."):
                lang = key.split(".", 1)[1].strip()
                narration[lang] = content
            else:
                extras[key] = content
        if not description:                  # simplified format: body is the description
            description = parts[0].strip()
        return description, narration, extras

    # --- whole storyboard --------------------------------------------------

    def parse(self, path: Path) -> Storyboard:
        """Parse the whole storyboard file into a :class:`Storyboard`."""
        import yaml  # imported lazily so a missing dependency can be installed first

        text = path.read_text(encoding="utf-8")
        front = self._FRONT_MATTER_RE.match(text)
        if front:                               # front-matter is OPTIONAL
            cfg = yaml.safe_load(front.group(1)) or {}
            body = text[front.end():]
        else:
            cfg, body = {}, text
        if not isinstance(cfg, dict):
            cfg = {}

        scene_starts = list(self._SCENE_HEADING_RE.finditer(body))
        if not scene_starts:
            raise SystemExit(
                "Storyboard must contain at least one '## ' scene heading."
            )
        brief_region = body[: scene_starts[0].start()]
        # Pull the preparation block out FIRST so its `# Preparation` heading can
        # never be mistaken for the document's title H1.
        pre_prep, preparation = self._split_off_preparation(brief_region)
        project_brief, h1_title = self._split_off_title(pre_prep)
        scenes: List[Scene] = []
        for i, match in enumerate(scene_starts):
            start = match.end()
            end = scene_starts[i + 1].start() if i + 1 < len(scene_starts) else len(body)
            scenes.append(self.parse_scene(match.group(1), body[start:end]))

        base = path.parent
        raw_landscape = cfg.get("scenes_landscape_dir")
        raw_portrait = cfg.get("scenes_portrait_dir")
        min_duration, max_duration = self._read_duration_limits(cfg, scenes)
        languages = self._read_languages(cfg)
        tts_provider = str(cfg.get("tts_provider") or cfg.get("tts") or "edge")

        return Storyboard(
            title=str(cfg.get("title") or h1_title or path.stem),
            languages=languages,
            orientations=self._read_orientations(cfg),
            voices=self._read_voices(cfg, languages, tts_provider),
            tts_provider=tts_provider,
            gemini_model=str(cfg.get("gemini_model") or config.DEFAULT_GEMINI_MODEL),
            gemini_api_key=self._read_gemini_key(cfg),
            ai_cli=str(cfg.get("ai_cli") or cfg.get("ai") or "claude"),
            fps=int(cfg.get("fps") or 30),
            resolution_landscape=self._read_resolution(cfg),
            scenes_landscape_dir=(base / raw_landscape).resolve() if raw_landscape else None,
            scenes_portrait_dir=(base / raw_portrait).resolve() if raw_portrait else None,
            scenes=scenes,
            project_brief=project_brief,
            preparation=preparation,
            preparation_profile=str(cfg.get("preparation_profile") or "generic"),
            min_duration=min_duration,
            max_duration=max_duration,
        )

    # --- front-matter readers (each accepts a friendly alias) --------------

    @classmethod
    def _split_off_preparation(cls, brief_region: str) -> Tuple[str, str]:
        """Split the brief region at a ``# Preparation`` heading.

        Returns ``(text_before_preparation, preparation_body)``. Everything from
        the heading to the start of the first scene becomes the preparation body
        (the heading line itself is dropped); the text before it is handed on for
        normal title/brief extraction. No heading -> ``(brief_region, "")``."""
        m = cls._PREPARATION_HEADING_RE.search(brief_region)
        if not m:
            return brief_region, ""
        before = brief_region[: m.start()]
        preparation = brief_region[m.end():].strip()
        return before, preparation

    @classmethod
    def _split_off_title(cls, brief_region: str) -> Tuple[str, Optional[str]]:
        """Return the brief with a leading ``# H1`` removed, and that H1 text.

        In the simplified format the document title is the first ``# Heading``;
        we lift it out so it doesn't duplicate inside the project brief."""
        lines = brief_region.strip().splitlines()
        title: Optional[str] = None
        kept: List[str] = []
        for line in lines:
            m = cls._H1_RE.match(line)
            if m and title is None:
                title = m.group(1).strip()
                continue                         # drop the H1 line from the brief
            kept.append(line)
        return "\n".join(kept).strip(), title

    @staticmethod
    def _read_languages(cfg: dict) -> List[str]:
        if cfg.get("languages"):
            return list(cfg["languages"])
        lang = cfg.get("language")
        if lang:
            s = str(lang).strip().lower()
            return ["id", "en"] if s == "both" else [s]
        return ["id", "en"]

    @staticmethod
    def _read_orientations(cfg: dict) -> List[str]:
        if cfg.get("orientations"):
            return list(cfg["orientations"])
        orient = cfg.get("orientation")
        if orient:
            s = str(orient).strip().lower()
            return ["landscape", "portrait"] if s == "both" else [s]
        return ["landscape", "portrait"]

    @staticmethod
    def _read_resolution(cfg: dict) -> Tuple[int, int]:
        raw = cfg.get("resolution_landscape") or cfg.get("resolution")
        if not raw:
            return (1920, 1080)
        if isinstance(raw, str):
            m = re.match(r"\s*(\d+)\s*[xX×]\s*(\d+)\s*$", raw)
            if not m:
                raise SystemExit(
                    f"Invalid resolution '{raw}'. Use WIDTHxHEIGHT, e.g. 1920x1080."
                )
            return (int(m.group(1)), int(m.group(2)))
        return tuple(raw)

    @staticmethod
    def _read_voices(cfg: dict, languages: List[str], tts_provider: str) -> Dict[str, str]:
        if cfg.get("voices"):
            return dict(cfg["voices"])
        voice = cfg.get("voice")
        if not voice:
            return {}
        s = str(voice).strip()
        if s.lower() in ("", "default", "auto"):
            return {}                            # let the provider default apply
        if s.lower() in ("male", "female"):
            if tts_provider == "edge":
                table = config.EDGE_VOICES_BY_GENDER.get(s.lower(), {})
                return {lang: table[lang] for lang in languages if lang in table}
            return {}                            # gemini voices aren't gendered here
        return {lang: s for lang in languages}   # a specific voice id for every language

    @staticmethod
    def _read_gemini_key(cfg: dict) -> Optional[str]:
        if cfg.get("gemini_api_key"):
            progress.log(
                "  note: ignoring 'gemini_api_key' in the storyboard for security — "
                "set it via --gemini-api-key, $GEMINI_API_KEY, or a .env file."
            )
        return None

    @staticmethod
    def _parse_length(value) -> Tuple[Optional[float], Optional[float]]:
        """Parse a friendly ``length:`` value into ``(min, max)`` seconds.

        A single value (``3 minutes`` / ``180`` / ``2:30``) -> ``(None, that)``.
        A range (``2-3 minutes``, ``120-180``) -> ``(low, high)``.
        """
        if value is None:
            return (None, None)
        text = str(value).strip()
        m = re.match(r"^\s*([0-9.]+)\s*-\s*([0-9.]+)\s*(.*)$", text)
        if m:
            unit = m.group(3).strip()
            lo = parse_duration_spec(f"{m.group(1)} {unit}".strip())
            hi = parse_duration_spec(f"{m.group(2)} {unit}".strip())
            return (lo, hi)
        return (None, parse_duration_spec(text))

    def _read_duration_limits(
        self, cfg: dict, scenes: List[Scene]
    ) -> Tuple[Optional[float], Optional[float]]:
        """Read whole-video duration limits and sanity-check them against the budget."""
        length_min, length_max = self._parse_length(cfg.get("length"))

        if cfg.get("min_duration") is not None:
            min_duration = parse_duration_spec(cfg["min_duration"])
        elif length_min is not None:
            min_duration = length_min
        else:
            min_duration = config.DEFAULT_DURATION_FLOOR_SECONDS
        if min_duration is None:
            min_duration = config.DEFAULT_DURATION_FLOOR_SECONDS

        max_raw = cfg.get("max_duration", cfg.get("max_scene_duration"))
        if max_raw is not None:
            max_duration = parse_duration_spec(max_raw)
        else:
            max_duration = length_max
        if (
            max_duration is not None
            and min_duration is not None
            and max_duration < min_duration - 1e-6
        ):
            raise SystemExit(
                f"max_duration is {max_duration:.0f}s but minimum duration is "
                f"{min_duration:.0f}s. Increase max_duration or lower min_duration."
            )
        budget = sum(s.fallback_duration for s in scenes)
        if min_duration is not None and budget < min_duration - 1e-6:
            raise SystemExit(
                f"Storyboard duration budget is {budget:.0f}s but minimum duration is "
                f"{min_duration:.0f}s. The video length tracks the sum of each "
                f"scene's fallback_duration, so extend those until they sum to "
                f">= {min_duration:.0f}s (currently short by {min_duration - budget:.0f}s)."
            )
        if max_duration is not None:
            if budget > max_duration + 1e-6:
                raise SystemExit(
                    f"Storyboard duration budget is {budget:.0f}s but max_duration is "
                    f"{max_duration:.0f}s. The video length tracks the sum of each "
                    f"scene's fallback_duration, so trim those until they sum to "
                    f"<= {max_duration:.0f}s (currently over by {budget - max_duration:.0f}s)."
                )
        return min_duration, max_duration

    # --- a cheap front-matter peek (no yaml) -------------------------------

    @staticmethod
    def peek_ai_cli(path: Path) -> Optional[str]:
        """Read just ``ai_cli:`` from the front-matter, without importing yaml.

        Used before the dependency check so it can decide whether the AI CLI is
        needed at all. Returns ``None`` on any problem.
        """
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return None
        front = StoryboardParser._FRONT_MATTER_RE.match(text)
        if not front:
            return None
        for line in front.group(1).splitlines():
            if line.strip().startswith("ai_cli:"):
                value = line.split(":", 1)[1].strip().strip('"').strip("'")
                return value or None
        return None
