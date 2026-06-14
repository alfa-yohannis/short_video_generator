"""Subject packs — per-topic generation knowledge, resolved from ``subjects/<name>/``.

This generalizes the ``profiles/<name>.yaml`` precedent (see
:func:`vgen.preparation.get_profile`) from "asset preparation only" to
*everything specific to one teaching subject*:

* **scene render helpers** (``scene_helpers``) — Manim helper modules composed
  into each build's ``_common.py`` (e.g. the ArchiMate ``archi_element`` /
  relationship-arrow helpers), so a build carries only its subject's helpers.
* **scene-prompt guidance** (``scene_guidance``) — the notation/rendering rules
  injected into the scene-generation prompt (replaces what used to be hardcoded
  in ``scenes.py``). May contain an ``{asset_listing}`` placeholder.
* **bulk-driver fields** (``storyboard`` prompt + exemplar, ``naming``, ``csv``,
  ``cli_flags``, ``aliases``) — used by the unified ``auto_generate.py``.

A storyboard selects its pack with the ``subject:`` front-matter key. The default
is ``generic`` (no helpers, no guidance) which reproduces the pre-subject
behavior exactly. Mirrors ``preparation.get_profile``: a folder wins, else the
built-in generic pack is used.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from . import config
from .progress import progress


class SubjectPack:
    """Default, topic-agnostic subject: no scene helpers, no extra guidance.

    Concrete subjects are :class:`DeclarativeSubjectPack` loaded from
    ``subjects/<name>/subject.yaml``. This base class doubles as the ``generic``
    pack and as the escape hatch for a future subject that needs imperative
    behavior (subclass and override), the same dual shape as
    :class:`vgen.preparation.PreparationProfile`."""

    name = "generic"
    root: Optional[Path] = None
    scene_helpers: Sequence[str] = ()
    scene_guidance: str = ""
    template: str = ""       # default presentation template (storyboard `template:` overrides)
    aliases: Sequence[str] = ()
    asset_source: dict = {}
    naming: dict = {}
    csv: str = ""
    cli_flags: Sequence[str] = ()
    storyboard_spec: dict = {}

    # --- scene generation -------------------------------------------------

    def helper_sources(self) -> List[Tuple[str, str]]:
        """Return ``[(filename, source_text), ...]`` for the pack's scene helpers.

        These are appended into a build's ``_common.py`` so generated scenes can
        import them and the scene prompt shows only this subject's helpers."""
        out: List[Tuple[str, str]] = []
        for rel in self.scene_helpers:
            path = (self.root / rel) if self.root else None
            if path and path.exists():
                out.append((Path(rel).name, path.read_text(encoding="utf-8")))
            else:
                progress.log(f"  subject '{self.name}': helper not found: {rel}")
        return out

    def guidance(self, asset_listing: str = "") -> str:
        """The scene-prompt guidance, with ``{asset_listing}`` filled in if present."""
        if not self.scene_guidance:
            return ""
        if "{asset_listing}" in self.scene_guidance:
            return self.scene_guidance.replace("{asset_listing}", asset_listing)
        return self.scene_guidance

    # --- bulk driver ------------------------------------------------------

    def read_text(self, rel: str) -> str:
        """Read a pack-relative file (e.g. the storyboard prompt / an exemplar)."""
        path = (self.root / rel) if self.root else None
        return path.read_text(encoding="utf-8") if path and path.exists() else ""


class DeclarativeSubjectPack(SubjectPack):
    """A subject pack built from a ``subjects/<name>/subject.yaml`` spec."""

    def __init__(self, spec: dict, root: Path) -> None:
        self.name = str(spec.get("name") or root.name).strip().lower()
        self.root = root
        self.scene_helpers = list(spec.get("scene_helpers") or [])
        self.scene_guidance = str(spec.get("scene_guidance") or "")
        self.template = str(spec.get("template") or "")
        self.aliases = [str(a).strip().lower() for a in (spec.get("aliases") or [])]
        self.asset_source = dict(spec.get("asset_source") or {})
        self.naming = dict(spec.get("naming") or {})
        self.csv = str(spec.get("csv") or "")
        self.cli_flags = list(spec.get("cli_flags") or [])
        self.storyboard_spec = dict(spec.get("storyboard") or {})


def _load_pack_spec(name: str) -> Optional[Tuple[dict, Path]]:
    """Read ``subjects/<name>/subject.yaml`` (or ``.yml``); return ``(spec, root)``."""
    root = config.SUBJECTS_DIR / name
    for fn in ("subject.yaml", "subject.yml"):
        path = root / fn
        if path.exists():
            import yaml  # lazy: only needed when a pack is actually used
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError):
                return None
            if isinstance(data, dict):
                return data, root
    return None


def get_subject(name: Optional[str]) -> SubjectPack:
    """Resolve a subject pack by name.

    A ``subjects/<name>/subject.yaml`` file wins; otherwise the built-in
    ``generic`` default is used (with a note when an unknown name was requested)."""
    key = (name or "generic").strip().lower()
    loaded = _load_pack_spec(key)
    if loaded is not None:
        return DeclarativeSubjectPack(*loaded)
    if key != "generic":
        progress.log(f"  no subjects/{key}/ pack found; using 'generic'.")
    return SubjectPack()


def all_subjects() -> List[DeclarativeSubjectPack]:
    """Every ``subjects/<name>/`` pack on disk (for the bulk driver / routing)."""
    out: List[DeclarativeSubjectPack] = []
    if config.SUBJECTS_DIR.is_dir():
        for d in sorted(config.SUBJECTS_DIR.iterdir()):
            if d.is_dir():
                loaded = _load_pack_spec(d.name)
                if loaded is not None:
                    out.append(DeclarativeSubjectPack(*loaded))
    return out


def resolve_for_category(category: str, name: str = "") -> Optional[DeclarativeSubjectPack]:
    """Pick the pack whose name/aliases appear in a CSV ``category``/topic.

    Replaces the bulk driver's hardcoded keyword routing (``_is_togaf_topic``):
    a new subject becomes a data addition (its ``aliases``), not an ``if`` branch."""
    text = f"{category} {name}".lower()
    for pack in all_subjects():
        for key in (pack.name, *pack.aliases):
            if key and key in text:
                return pack
    return None
