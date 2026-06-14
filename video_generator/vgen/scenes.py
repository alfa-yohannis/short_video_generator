"""Generating (and repairing) the Manim scene ``.py`` files with an AI client.

`SceneSynthesizer` owns everything about turning a scene's description +
narration into a runnable Manim source file:

* copying the shared template (`_common.py`, fonts) into the output,
* building the prompt and asking the AI to write the scene,
* cleaning + syntax-checking the reply, and
* re-asking the AI to *fix* a scene that later fails to render (the renderer
  calls :meth:`repair` for that).

It depends on an :class:`~vgen.ai_client.AiClient`, injected in the constructor.
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

from . import config
from .ai_client import AiClient
from .density import SceneTooDenseError, is_too_dense
from .models import Scene, Storyboard
from .preparation import is_noop_preparation, load_manifest
from .progress import progress
from .subjects import get_subject
from .text_utils import (
    escape_unsafe_ampersands,
    python_syntax_error,
    strip_code_fences,
    validate_python_source,
)

if TYPE_CHECKING:  # only for type hints — avoids a runtime import cycle
    from .renderer import SceneValidator


class SceneSynthesizer:
    """Creates and repairs Manim scene files for a storyboard.

    When given a ``validator`` and ``validate_attempts > 0``, each scene is
    *checked the moment it is generated*: it's render-validated against the
    layout rules and, if it fails, refined and re-checked in a loop until it
    passes or the attempts run out — so the real render only ever sees scenes
    that already pass.
    """

    def __init__(self, ai_client: AiClient,
                 validator: "Optional[SceneValidator]" = None,
                 validate_attempts: int = 0,
                 generate_attempts: int = 3) -> None:
        self.ai = ai_client
        self.validator = validator
        self.validate_attempts = validate_attempts
        # How many times to re-ask the AI when its reply is empty or not valid
        # Python (a syntax error is fed back so the next try can fix it).
        self.generate_attempts = max(1, generate_attempts)

    # --- template materialization -----------------------------------------

    def materialize_dir(self, storyboard: Storyboard, output: Path, orient: str) -> Path:
        """Decide the scenes directory for an orientation, copying templates in.

        If the storyboard names an existing directory, use it as-is (the user
        brought their own sources). Otherwise the canonical location is
        ``<output>/scenes_<orient>/`` and the bundled ``_common.py`` + fonts are
        copied in (and refreshed whenever the template changes).
        """
        declared = storyboard.scenes_dir(orient)
        if declared is not None and declared.exists():
            return declared
        target = (output / f"scenes_{orient}").resolve()
        target.mkdir(parents=True, exist_ok=True)

        # Compose the build's _common.py from the selected presentation TEMPLATE
        # plus the active subject's helpers, so a build carries only what it needs
        # and there is a single source of truth:
        #   1. the chosen template (templates/<template>/): its orientation-agnostic
        #      CORE (_core.py) with the orientation delta (_<orient>.py) spliced in
        #      at the ORIENTATION_DELTA marker. The template is the storyboard's
        #      `template:` (else the subject's, else DEFAULT_TEMPLATE); an unknown
        #      name falls back to the default so a build never loses its scaffold.
        #   2. the ACTIVE subject pack's scene helpers (e.g. ArchiMate's
        #      archi_element / arrows) — so design-pattern builds carry no ArchiMate
        #      code and the scene prompt (which injects _common verbatim) shows only
        #      the relevant helpers.
        # Rewritten only when it would change, so a template OR subject change is
        # picked up on the next build.
        pack = get_subject(getattr(storyboard, "subject", "generic"))
        tmpl = (getattr(storyboard, "template", "") or pack.template
                or config.DEFAULT_TEMPLATE)
        tdir = config.TEMPLATES_DIR / tmpl
        core_file, delta_file = tdir / "_core.py", tdir / f"_{orient}.py"
        if not (core_file.exists() and delta_file.exists()):
            if tmpl != config.DEFAULT_TEMPLATE:
                progress.log(f"  template '{tmpl}' not found; using "
                             f"'{config.DEFAULT_TEMPLATE}'.")
            tdir = config.TEMPLATES_DIR / config.DEFAULT_TEMPLATE
            core_file, delta_file = tdir / "_core.py", tdir / f"_{orient}.py"
        if not (core_file.exists() and delta_file.exists()):
            return target
        composed = core_file.read_text(encoding="utf-8").replace(
            "# <<ORIENTATION_DELTA>>", delta_file.read_text(encoding="utf-8"))
        target_common = target / "_common.py"
        for fname, src in pack.helper_sources():
            composed += (f"\n\n# === subject '{pack.name}' helper: {fname} "
                         "(composed into _common by materialize_dir) ===\n" + src)
        if (not target_common.exists()
                or target_common.read_text(encoding="utf-8") != composed):
            target_common.write_text(composed, encoding="utf-8")

        assets_src = config.TEMPLATES_DIR / "assets"
        if assets_src.exists():
            # Merge-copy so new template assets (e.g. logo/) land in existing
            # build dirs too, not only freshly-created ones.
            shutil.copytree(assets_src, output / "assets", dirs_exist_ok=True)

        # Stage the storyboard's declared reference assets (assets_dir:) into the
        # build's assets/ too. The scene prompt injects each asset's ABSOLUTE
        # path, but generated scenes often rebuild the path from ROOT_DIR/assets
        # instead; without this copy those *_logo.svg lookups miss and the type
        # icon silently renders as nothing. Copying here makes the icon resolve
        # whether the scene uses the absolute path or a ROOT_DIR/assets lookup.
        declared_assets = getattr(storyboard, "prep_assets_dir", None)
        if declared_assets and Path(declared_assets).is_dir():
            shutil.copytree(declared_assets, output / "assets", dirs_exist_ok=True)
        return target

    def ensure_all(self, storyboard: Storyboard, output: Path, force: bool) -> Tuple[Optional[Path], Optional[Path]]:
        """Make sure every scene ``.py`` exists for each requested orientation.

        Only the orientations in ``storyboard.orientations`` are materialized and
        generated (so ``--orientation landscape`` never spends AI calls on
        portrait). Updates ``storyboard.scenes_landscape_dir`` /
        ``scenes_portrait_dir`` to the directories actually used, and returns them
        (``None`` for an orientation that wasn't requested).
        """
        dirs = {orient: self.materialize_dir(storyboard, output, orient)
                for orient in storyboard.orientations}
        landscape_dir = dirs.get("landscape")
        portrait_dir = dirs.get("portrait")
        storyboard.scenes_landscape_dir = landscape_dir
        storyboard.scenes_portrait_dir = portrait_dir

        skeleton = self._read_skeleton()
        for orient, scenes_dir in dirs.items():
            common_src = self._read_common(scenes_dir)
            for scene in storyboard.scenes:
                scene_path = scenes_dir / scene.file
                if scene_path.exists() and not force:
                    continue
                if storyboard.ai_cli in ("", "none", None):
                    raise SystemExit(
                        f"Scene file {scene_path} is missing and no ai_cli is "
                        "configured to generate it. Either drop the .py in place "
                        "or set `ai_cli: claude` in the storyboard front-matter."
                    )
                self._generate_one(storyboard, output, scene, orient, scene_path,
                                   skeleton, common_src)
        return landscape_dir, portrait_dir

    # --- generation + repair ----------------------------------------------

    def _generate_one(self, storyboard: Storyboard, output: Path, scene: Scene,
                      orient: str, scene_path: Path, skeleton: str, common_src: str) -> None:
        symbols = load_manifest(Path(storyboard.prep_assets_dir)) if storyboard.prep_assets_dir else []
        if symbols:
            prep_note = f" (+ {len(symbols)} reference assets)"
        elif not is_noop_preparation(storyboard.preparation):
            prep_note = " (+ # Preparation context)"
        else:
            prep_note = ""
        progress.log(f"  ai-generate {orient}/{scene.file} via {self.ai.name}{prep_note}…")
        started = time.monotonic()
        prompt = self.build_prompt(storyboard, scene, orient, skeleton, common_src)
        source = self._generate_valid_source(prompt, scene_path, orient)
        scene_path.write_text(source.rstrip() + "\n", encoding="utf-8")
        progress.log(f"    ↳ {orient}/{scene.file} in {time.monotonic() - started:.1f}s")
        self._validate_and_fix(storyboard, output, scene, orient, scene_path)

    def _generate_valid_source(self, base_prompt: str, scene_path: Path, orient: str) -> str:
        """Ask the AI for a scene file, retrying when the reply is empty or not
        valid Python. The syntax error is fed back so the next attempt can fix it,
        mirroring the render/layout repair loop (which only runs after this)."""
        prompt, problem = base_prompt, ""
        for attempt in range(1, self.generate_attempts + 1):
            source = escape_unsafe_ampersands(strip_code_fences(self.ai.generate(prompt)))
            if not source.strip():
                problem = "the reply was empty"
            else:
                err = python_syntax_error(source, scene_path)
                if err is None:
                    return source
                problem = f"not valid Python ({err})"
            if attempt < self.generate_attempts:
                progress.log(f"    {orient}/{scene_path.name}: {problem}; regenerating "
                             f"(attempt {attempt}/{self.generate_attempts})…")
                prompt = (
                    f"{base_prompt}\n\nYOUR PREVIOUS OUTPUT WAS REJECTED — {problem}. "
                    "Return ONLY a corrected, COMPLETE, valid Python file: no markdown "
                    "fences, no commentary, no stray characters."
                )
        raise SystemExit(
            f"AI could not produce valid Python for {scene_path} after "
            f"{self.generate_attempts} attempt(s): {problem}.\n"
            "Re-run with --force, or delete the file and re-run --stage scenes."
        )

    def _validate_and_fix(self, storyboard: Storyboard, output: Path, scene: Scene,
                          orient: str, scene_path: Path) -> None:
        """Render-check a just-generated scene and refine it until it passes.

        Renders the scene (low quality, strict layout check) for each language;
        on the first failure it asks the AI to fix the scene and checks again,
        up to ``validate_attempts`` times. If a *density* failure (the content
        won't fit, not a stray label) survives ``REPAIRS_BEFORE_SPLIT`` repairs,
        it raises :class:`SceneTooDenseError` so the build can split the scene in
        the storyboard. No-op unless a validator is wired in.
        """
        if self.validator is None or self.validate_attempts <= 0:
            return
        scenes_dir = scene_path.parent
        density_fails = 0
        for attempt in range(1, self.validate_attempts + 1):
            failure = None
            for lang in storyboard.languages:
                ok, problem, is_layout = self.validator.check_scene(
                    storyboard, output, scenes_dir, scene, orient, lang)
                if not ok:
                    failure = (lang, problem, is_layout)
                    break
            if failure is None:
                progress.log(f"    ✓ {orient}/{scene.basename} passes the layout check")
                return
            lang, problem, is_layout = failure
            # Too-dense escalation: when content genuinely won't fit, repairing in
            # place is futile — after a few tries, hand it off to be split.
            if is_layout and is_too_dense(problem, config.DENSITY_MIN_SCALE):
                if density_fails >= config.REPAIRS_BEFORE_SPLIT:
                    raise SceneTooDenseError(scene, orient, problem)
                density_fails += 1
            if attempt >= self.validate_attempts:
                raise SystemExit(
                    f"{orient}/{scene.basename} still violates the checks after "
                    f"{self.validate_attempts} refine attempt(s) [{lang}]: {problem}"
                )
            kind = "layout violation" if is_layout else "render error"
            progress.log(f"    {kind} in {orient}/{scene.basename} [{lang}], refining "
                         f"(attempt {attempt}/{self.validate_attempts})… {problem}")
            self.repair(storyboard, scene, orient, scene_path, problem, is_layout)

    def repair(self, storyboard: Storyboard, scene: Scene, orient: str,
               scene_path: Path, problem: str, is_layout: bool) -> None:
        """Ask the AI to fix a scene that failed (a render crash or a layout
        violation), then overwrite the file in place. Called by the renderer."""
        scenes_dir = scene_path.parent
        common_src = self._read_common(scenes_dir)
        skeleton = self._read_skeleton()
        current_src = scene_path.read_text(encoding="utf-8")
        prompt = self._build_repair_prompt(
            storyboard, scene, orient, skeleton, common_src, current_src, problem, is_layout
        )
        new_src = strip_code_fences(self.ai.generate(prompt))
        if not new_src.strip():
            raise SystemExit(f"AI returned empty source repairing {scene_path}")
        new_src = escape_unsafe_ampersands(new_src)
        validate_python_source(scene_path, new_src)
        scene_path.write_text(new_src.rstrip() + "\n", encoding="utf-8")

    # --- prompts -----------------------------------------------------------

    @staticmethod
    def _assets_note(storyboard: Storyboard) -> str:
        """List any preparation-fetched reference assets for the scene prompt.

        Empty unless ``--run-preparation`` saved assets and wrote a manifest. Each
        line gives the asset's type and the absolute file path so the generated
        scene can load the real artwork via ``SVGMobject(path)`` /
        ``ImageMobject(path)`` instead of inventing a shape."""
        assets_dir = storyboard.prep_assets_dir
        if not assets_dir:
            return ""
        symbols = load_manifest(Path(assets_dir))
        if not symbols:
            return ""
        lines = []
        for s in symbols:
            path = (Path(assets_dir) / s["file"]).resolve()
            layer = f" [{s['layer']}]" if s.get("layer") else ""
            lines.append(f"  - {s['type']}{layer}: {path}")
        listing = "\n".join(lines)
        return (
            "\nREFERENCE ASSETS (real artwork for this build — these are MANDATORY). "
            "For every element/relationship/symbol a scene shows, you MUST load the "
            "matching real file below — `SVGMobject(\"<path>\")` for .svg or "
            "`ImageMobject(\"<path>\")` for .jpg/.png — then size and label it. Do NOT "
            "draw, redraw, recolor, or invent a shape for anything that has an asset "
            "below; a hand-built primitive is allowed ONLY when no asset matches its "
            "type. Reference these exact paths verbatim in the scene file — they "
            "are already absolute, so pass each one directly as a string literal; "
            "do NOT rebuild a path from ROOT_DIR, __file__, or an assets/ subfolder "
            "(those lookups miss and the asset silently renders as nothing):\n"
            f"{listing}\n"
        )
        # Subject-specific rendering rules (e.g. ArchiMate's archi_element +
        # relationship arrows) used to be hardcoded here; they now live in the
        # active subject pack's `scene_guidance` and are injected by build_prompt.

    def build_prompt(self, storyboard: Storyboard, scene: Scene, orient: str,
                     skeleton: str, common_src: str) -> str:
        """The prompt that asks the AI to write one Manim scene file."""
        other_orient = "portrait" if orient == "landscape" else "landscape"
        prep_note = ""
        if not is_noop_preparation(storyboard.preparation):
            prep_note = (
                "\nPREPARATION (project-level reference material gathered before "
                "authoring; treat as authoritative context for how things should "
                "look — do NOT re-run any setup steps it mentions):\n"
                f"{storyboard.preparation.strip()}\n"
            )
        assets_note = self._assets_note(storyboard)
        # Subject-specific rendering guidance (notation rules + which helpers to
        # use), from the active subject pack. Injected whether or not the build
        # has reference assets, so asset-less subjects (e.g. a process-flow TOGAF
        # pack) get their guidance too. Empty for the 'generic' subject.
        subject_guidance = get_subject(storyboard.subject).guidance()
        subject_note = f"\n{subject_guidance.strip()}\n" if subject_guidance.strip() else ""
        portrait_note = ""
        if orient == "portrait":
            portrait_note = (
                "\nPortrait constraint: frame is 9 wide x 16 tall in Manim units, "
                "rendered at 1080x1920. Keep ALL visible content above "
                "SHORTS_SAFE_BOTTOM = -4.8 (the bottom 2/10 of the frame is "
                "reserved for Reels/Shorts/TikTok caption overlays). Use "
                "fit_to_shorts_area() to compress wide groups when needed.\n"
            )
        return f"""You are generating one Manim scene file for a tutorial video.

PROJECT TITLE: {storyboard.title}
PROJECT BRIEF:
{storyboard.project_brief}
{prep_note}{assets_note}{subject_note}
SCENE BASENAME: {scene.basename}
SCENE CLASS:    {scene.classname}
ORIENTATION:    {orient} (a parallel file will exist for {other_orient})
FALLBACK DURATION: {scene.fallback_duration:.1f} seconds
SCENE DESCRIPTION:
{scene.description or "(no description provided)"}

LOCALIZED NARRATION (timed to fit the scene; visuals should illustrate this):

[id] {scene.narration.get("id", "(missing)").strip()}

[en] {scene.narration.get("en", "(missing)").strip()}
{portrait_note}
HELPERS AVAILABLE FROM `_common` (reproduced verbatim below for reference):
```python
{common_src}
```

REFERENCE SKELETON (the structure your output MUST follow — same imports,
same TARGET_DURATION assignment, same Scene subclass, same final wait):
```python
{skeleton}
```

REQUIREMENTS:
- Output ONLY a complete valid Python file, no markdown fences, no commentary.
- First line: `from manim import *`
- Second line group: `from _common import (...)` importing every helper you use.
- Module-level: `TARGET_DURATION = audio_duration("{scene.basename}", {scene.fallback_duration:.1f})`
- Exactly one class: `class {scene.classname}(Scene):` with a single `construct` method.
- `self.add(tech_background())` at the very start of `construct`.
- Wrap every user-visible string with `L("teks Indonesia", "english text")`.
- Avoid orientation words ("left", "right", "above", "below") in any visible string.
- End `construct` with `self.wait(max(0.5, TARGET_DURATION - elapsed))` where
  `elapsed` is the sum of the `run_time` values you used.
- Use only helpers documented in the `_common` source above; do not import
  anything else.
- Keep visuals clean and instructional. Use semantic colors: DANGER for
  problems/naive code, OK for improved/refactored states, HIGHLIGHT for the
  currently-discussed element, PRIMARY for headline statements, ACCENT for
  section labels and emphasis.
- `title_bar`, `title_text`, `body_text`, `section_label`, and `bullet_list`
  all feed their text into Pango `MarkupText`, which parses Pango XML markup.
  Every `&` in those strings MUST be written as `&amp;`, every `<` as `&lt;`,
  every `>` as `&gt;`. Do not put raw ampersands or angle brackets inside
  any string that ends up in `L(...)`, `title_bar(...)`, `title_text(...)`,
  `body_text(...)`, `section_label(...)`, or `bullet_list([...])` items.
- Code shown via `code_card(...)` is NOT Pango markup; raw `&`, `<`, `>`
  are fine there.

Return ONLY the Python file contents.
"""

    def _build_repair_prompt(self, storyboard: Storyboard, scene: Scene, orient: str,
                             skeleton: str, common_src: str, current_src: str,
                             problem: str, is_layout: bool) -> str:
        base = self.build_prompt(storyboard, scene, orient, skeleton, common_src)
        if is_layout:
            safe_note = ""
            if orient == "portrait":
                safe_note = (" and entirely above SHORTS_SAFE_BOTTOM = -4.8 (the bottom "
                             "2/10 reserved for caption overlays)")
            fix = f"""

LAYOUT REPAIR — IMPORTANT:
A previous version of this exact scene FAILED an automated layout check with:
{problem}

Here is that failing scene source:
```python
{current_src}
```

Produce a corrected COMPLETE scene file that preserves the same content, timing
(`TARGET_DURATION`, `run_time` values, final wait) and instructional intent, but
guarantees every visible text mobject stays fully inside the frame{safe_note},
with no two text labels overlapping by more than half the smaller one. Fix it by
repositioning, reducing font `size=`, wrapping long strings onto multiple lines,
arranging with VGroup(...).arrange(...), or (portrait) fit_to_shorts_area(...).
Return ONLY the corrected Python file, no fences, no commentary.
"""
        else:
            fix = f"""

RENDER REPAIR — IMPORTANT:
A previous version of this exact scene FAILED to render with this error:
{problem}

Here is that failing scene source:
```python
{current_src}
```

Produce a corrected COMPLETE scene file that fixes the error while preserving the
same content, timing (`TARGET_DURATION`, `run_time` values, final wait) and
instructional intent. Common causes: a NameError from a colour/constant or helper
that is NOT defined in the `_common` source above; a wrong/typo'd argument to a
helper; calling a constant like a function. Use ONLY names, colours and helpers
that actually appear in the `_common` source above — do not invent constants.
Return ONLY the corrected Python file, no fences, no commentary.
"""
        return base + fix

    # --- small file readers ------------------------------------------------

    @staticmethod
    def _read_skeleton() -> str:
        path = config.TEMPLATES_DIR / "scene_skeleton.py"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    @staticmethod
    def _read_common(scenes_dir: Path) -> str:
        path = scenes_dir / "_common.py"
        return path.read_text(encoding="utf-8") if path.exists() else ""
