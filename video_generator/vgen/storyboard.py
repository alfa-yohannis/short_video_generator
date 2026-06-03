"""Reading a storyboard markdown file into a :class:`Storyboard` object.

`StoryboardParser` is a small *service* class: give it a path, get back a fully
populated domain object. The markdown format is:

    ---
    title: ...            # YAML front-matter block (project config)
    languages: [id, en]
    ---
    A project brief paragraph...

    ## Scene: 01_pengantar / Pengantar
    **fallback_duration:** 12
    ### description
    ...
    ### narration.id
    ...
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from . import config
from .models import Scene, Storyboard
from .text_utils import camel_from_snake, strip_leading_digits


# --- duration parsing (a pure helper used by the parser) -------------------

_DURATION_SPEC_RE = re.compile(
    r"^\s*([0-9]*\.?[0-9]+)\s*"
    r"(h(?:ours?|rs?)?|m(?:in(?:ute)?s?)?|s(?:ec(?:ond)?s?)?)?\s*$",
    re.I,
)


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
    _SCENE_HEADING_RE = re.compile(r"^##\s+Scene\s*:\s*(.+?)\s*$", re.M)
    _SUBSECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.M)
    _FILE_META_RE = re.compile(r"\*\*file:\*\*\s*([^\s]+)", re.I)
    _DURATION_META_RE = re.compile(r"\*\*fallback[_ ]duration:\*\*\s*([0-9.]+)", re.I)
    _CLASS_META_RE = re.compile(r"\*\*class:\*\*\s*([^\s]+)", re.I)

    # --- scenes ------------------------------------------------------------

    def parse_scene(self, header: str, body: str) -> Scene:
        """Build one :class:`Scene` from its ``## Scene:`` header and body text."""
        classname = ""
        basename = header.strip()
        if "/" in header:
            left, right = (s.strip() for s in header.split("/", 1))
            basename, classname = left, right
        class_meta = self._CLASS_META_RE.search(body)
        if class_meta:
            classname = class_meta.group(1).strip()
        if not classname:
            classname = camel_from_snake(strip_leading_digits(basename))

        file_match = self._FILE_META_RE.search(body)
        file_path = file_match.group(1).strip() if file_match else f"scene_{basename}.py"
        dur_match = self._DURATION_META_RE.search(body)
        fallback_duration = float(dur_match.group(1)) if dur_match else 15.0

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

    def _parse_subsections(self, body: str):
        """Split a scene body's ``### ...`` subsections into description /
        narration / everything-else."""
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
        return description, narration, extras

    # --- whole storyboard --------------------------------------------------

    def parse(self, path: Path) -> Storyboard:
        """Parse the whole storyboard file into a :class:`Storyboard`."""
        import yaml  # imported lazily so a missing dependency can be installed first

        text = path.read_text(encoding="utf-8")
        front = self._FRONT_MATTER_RE.match(text)
        if not front:
            raise SystemExit(
                f"Storyboard {path} must begin with a YAML front-matter block "
                "delimited by '---' lines."
            )
        cfg = yaml.safe_load(front.group(1)) or {}
        body = text[front.end():]

        scene_starts = list(self._SCENE_HEADING_RE.finditer(body))
        if not scene_starts:
            raise SystemExit("Storyboard must contain at least one '## Scene:' heading.")
        project_brief = body[: scene_starts[0].start()].strip()
        scenes: List[Scene] = []
        for i, match in enumerate(scene_starts):
            start = match.end()
            end = scene_starts[i + 1].start() if i + 1 < len(scene_starts) else len(body)
            scenes.append(self.parse_scene(match.group(1), body[start:end]))

        base = path.parent
        raw_landscape = cfg.get("scenes_landscape_dir")
        raw_portrait = cfg.get("scenes_portrait_dir")
        max_duration = self._read_max_duration(cfg, scenes)

        return Storyboard(
            title=str(cfg.get("title") or path.stem),
            languages=list(cfg.get("languages") or ["id", "en"]),
            orientations=list(cfg.get("orientations") or ["landscape", "portrait"]),
            voices=dict(cfg.get("voices") or {}),
            tts_provider=str(cfg.get("tts_provider") or "edge"),
            gemini_model=str(cfg.get("gemini_model") or config.DEFAULT_GEMINI_MODEL),
            gemini_api_key=(str(cfg["gemini_api_key"]) if cfg.get("gemini_api_key") else None),
            ai_cli=str(cfg.get("ai_cli") or "claude"),
            fps=int(cfg.get("fps") or 30),
            resolution_landscape=tuple(cfg.get("resolution_landscape") or (1920, 1080)),
            scenes_landscape_dir=(base / raw_landscape).resolve() if raw_landscape else None,
            scenes_portrait_dir=(base / raw_portrait).resolve() if raw_portrait else None,
            scenes=scenes,
            project_brief=project_brief,
            max_duration=max_duration,
        )

    def _read_max_duration(self, cfg: dict, scenes: List[Scene]) -> Optional[float]:
        """Read the optional whole-video cap and sanity-check it against the budget."""
        max_duration = parse_duration_spec(
            cfg.get("max_duration", cfg.get("max_scene_duration"))
        )
        if max_duration is not None:
            budget = sum(s.fallback_duration for s in scenes)
            if budget > max_duration + 1e-6:
                raise SystemExit(
                    f"Storyboard duration budget is {budget:.0f}s but max_duration is "
                    f"{max_duration:.0f}s. The video length tracks the sum of each "
                    f"scene's fallback_duration, so trim those until they sum to "
                    f"<= {max_duration:.0f}s (currently over by {budget - max_duration:.0f}s)."
                )
        return max_duration

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
