"""The pipeline that ties every stage together.

`VideoPipeline` is the *orchestrator*: it owns the storyboard, the output
directory, the build options, and one instance of each collaborator service
(narration writer, scene synthesizer, renderer, TTS engine, ...). Those
collaborators are passed in (*dependency injection*), so the pipeline doesn't
build them itself — that keeps it easy to test with fakes and easy to read,
because each method does one stage and delegates the work.

``run_build(options)`` is the top-level entry: it checks dependencies, parses
the storyboard, applies CLI overrides, wires up a pipeline and runs it.
"""

from __future__ import annotations

import dataclasses
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from . import config
from .ai_client import create_ai_client
from .assembly import ClipAssembler
from .density import SceneTooDenseError
from .dependencies import DependencyChecker
from .duration import DurationFitter
from .models import Storyboard
from .narration import NarrationWriter
from .preparation import PreparationRunner, is_noop_preparation
from .progress import progress
from .refine import StoryboardRefiner
from .renderer import ManimRenderer, SceneValidator
from .scenes import SceneSynthesizer
from .storyboard import StoryboardParser
from .tts import GEMINI_ALIASES, TtsEngine, create_tts_engine, resolve_gemini_key
from .youtube import YouTubeMetadataWriter


@dataclass
class BuildOptions:
    """Everything the command line can choose about a build."""

    storyboard: Path
    output: Path
    stage: str = "all"
    only: Optional[List[str]] = None
    force: bool = False
    ai_cli: Optional[str] = "claude"
    effort: str = config.DEFAULT_CLAUDE_EFFORT   # Claude reasoning tier; codex ignores it
    tts: Optional[str] = None
    voice: Optional[str] = None
    orientation: str = "both"   # landscape | portrait | both (both = use storyboard's)
    gemini_api_key: Optional[str] = None
    check_layout: str = "off"
    repair_attempts: int = 2
    validate_scenes: bool = False     # render-check each scene right after generating it
    validate_attempts: int = 10       # how many times to refine a failing scene
    refine_storyboard: bool = False   # let the AI rewrite an over-dense storyboard first
    run_preparation: bool = False     # execute the # Preparation block agentically (fetch assets)
    mcp_config: Optional[Path] = None # .mcp.json for the preparation agent (default: repo root)
    skip_youtube: bool = False
    skip_dep_check: bool = False
    no_ai_cli_check: bool = False


class VideoPipeline:
    """Runs the eight build stages, delegating each to an injected collaborator."""

    def __init__(self, storyboard: Storyboard, output: Path, options: BuildOptions,
                 *, narration: NarrationWriter, scene_synth: SceneSynthesizer,
                 renderer: ManimRenderer, tts: TtsEngine, assembler: ClipAssembler,
                 youtube: YouTubeMetadataWriter, duration: DurationFitter) -> None:
        self.storyboard = storyboard
        self.output = output
        self.options = options
        self.narration = narration
        self.scene_synth = scene_synth
        self.renderer = renderer
        self.tts = tts
        self.assembler = assembler
        self.youtube = youtube
        self.duration = duration

    # --- the eight stages --------------------------------------------------

    def stage_scripts(self) -> None:
        self.narration.write_scripts(self.storyboard, self.output)

    def stage_audio(self) -> None:
        # Make sure narration exists even if --stage audio is run on its own.
        for scene in self.storyboard.scenes:
            for lang in self.storyboard.languages:
                self.narration.ensure(self.storyboard, scene, lang, output=self.output)
        self.duration.fit_before_tts(self.storyboard, self.output)        # estimate + compress
        self.tts.synthesize_storyboard(self.storyboard, self.output, self.options.force)
        self.duration.enforce_after_tts(self.storyboard, self.output)     # measure + re-narrate

    def stage_scenes(self) -> None:
        self.scene_synth.ensure_all(self.storyboard, self.output, self.options.force)

    def stage_render(self) -> None:
        # Render assumes scene .py files exist; generate any that are missing.
        self.scene_synth.ensure_all(self.storyboard, self.output, force=False)
        for lang in self.storyboard.languages:
            for orient in self.storyboard.orientations:
                self.renderer.render(self.storyboard, self.output, lang, orient,
                                     self.options.force, check_layout=self.options.check_layout,
                                     repair_attempts=self.options.repair_attempts)

    def stage_mux(self) -> None:
        for lang in self.storyboard.languages:
            for orient in self.storyboard.orientations:
                self.assembler.mux(self.storyboard, self.output, lang, orient, self.options.force)

    def stage_concat(self) -> None:
        for lang in self.storyboard.languages:
            for orient in self.storyboard.orientations:
                final = self.assembler.concat(self.storyboard, self.output, lang, orient,
                                              self.options.force)
                progress.log(f"  -> {final}")

    def stage_srt(self) -> None:
        for lang in self.storyboard.languages:
            merged = self.assembler.merge_subtitles(self.storyboard, self.output, lang)
            progress.log(f"  -> {merged}")

    def stage_thumbnails(self) -> None:
        # A poster frame per (language, orientation): the first scene's last second.
        for lang in self.storyboard.languages:
            for orient in self.storyboard.orientations:
                thumb = self.assembler.thumbnail(self.storyboard, self.output, lang,
                                                 orient, self.options.force)
                if thumb:
                    progress.log(f"  -> {thumb}")

    def stage_youtube(self) -> None:
        self.youtube.generate(self.storyboard, self.output, self.options.force)

    # --- driver ------------------------------------------------------------

    def run(self) -> None:
        """Run the requested stage(s), each wrapped with a header + timing line."""
        stage = self.options.stage
        plan = [
            ("scripts", "[1/9] write narration scripts (AI-generated when missing)", self.stage_scripts),
            ("audio",   "[2/9] generate audio + per-scene SRTs", self.stage_audio),
            ("scenes",  "[3/9] materialize scene .py files (AI-generated when missing)", self.stage_scenes),
            ("render",  "[4/9] render Manim scenes", self.stage_render),
            ("mux",     "[5/9] mux clips (video + audio)", self.stage_mux),
            ("concat",  "[6/9] concat per-scene clips into final videos", self.stage_concat),
            ("thumbnails", "[7/9] thumbnails (first scene, last second)", self.stage_thumbnails),
            ("srt",     "[8/9] merge per-scene SRTs into final SRTs", self.stage_srt),
            ("youtube", "[9/9] generate YouTube metadata (per language)", self.stage_youtube),
        ]
        for name, label, runner in plan:
            if stage not in ("all", name):
                continue
            if name == "youtube" and self.options.skip_youtube:
                continue
            with progress.stage(label):
                runner()
        progress.log(f"Done in {progress.clock()}.")


# =====================================================================
# Top-level build entry point
# =====================================================================

def build_pipeline(storyboard: Storyboard, output: Path, options: BuildOptions) -> VideoPipeline:
    """Wire a :class:`VideoPipeline` from a storyboard (the composition root).

    This is the one place that knows which concrete classes implement each role,
    so the rest of the program depends only on the interfaces.
    """
    ai_client = create_ai_client(storyboard.ai_cli, options.effort)
    tts_engine = create_tts_engine(storyboard)
    # When --validate-scenes is on, give the synthesizer a validator so it
    # render-checks (and refines) each scene the moment it is generated.
    validator = SceneValidator() if options.validate_scenes else None
    scene_synth = SceneSynthesizer(ai_client, validator=validator,
                                   validate_attempts=options.validate_attempts)
    return VideoPipeline(
        storyboard, output, options,
        narration=NarrationWriter(ai_client),
        scene_synth=scene_synth,
        renderer=ManimRenderer(scene_synth),
        tts=tts_engine,
        assembler=ClipAssembler(),
        youtube=YouTubeMetadataWriter(ai_client),
        duration=DurationFitter(ai_client, tts_engine),
    )


def apply_cli_overrides(storyboard: Storyboard, options: BuildOptions) -> None:
    """Let command-line flags override storyboard settings, in place.

    The storyboard stays portable while a single invocation picks the narrator,
    TTS provider, voice, or API key. A single ``--voice`` applies to every
    language (per-language control still lives in the storyboard).
    """
    if options.ai_cli:
        storyboard.ai_cli = options.ai_cli
    if options.tts:
        storyboard.tts_provider = options.tts
    if options.voice:
        storyboard.voices = {lang: options.voice for lang in storyboard.languages}
    if options.orientation and options.orientation != "both":
        storyboard.orientations = [options.orientation]
    if options.gemini_api_key:
        storyboard.gemini_api_key = options.gemini_api_key


def run_build(options: BuildOptions) -> None:
    """Check dependencies, parse + configure the storyboard, and run the pipeline."""
    progress.reset()
    storyboard_path = Path(options.storyboard).resolve()
    output = Path(options.output).resolve()
    refined_path = output / "storyboard.refined.md"

    # --force is a clean rebuild: wipe generated outputs (and any previously
    # refined storyboard) up front, before we choose which storyboard to use.
    if options.force:
        _wipe_outputs(output)
        refined_path.unlink(missing_ok=True)

    # Without --refine-storyboard, always prefer a refined storyboard from a
    # previous run if one exists. Only when there's no refined file (or --force
    # removed it) is the original used.
    if not options.refine_storyboard and refined_path.exists():
        storyboard_path = refined_path
        progress.log(f"  using previously refined storyboard: {refined_path}")

    if not options.skip_dep_check:
        if options.no_ai_cli_check:
            need_ai_cli = None
        else:  # the CLI flag wins; otherwise use what the storyboard declares
            need_ai_cli = options.ai_cli or StoryboardParser.peek_ai_cli(storyboard_path)
        DependencyChecker().check(need_ai_cli=need_ai_cli)

    storyboard = StoryboardParser().parse(storyboard_path)
    apply_cli_overrides(storyboard, options)

    if (not options.skip_dep_check and storyboard.tts_provider in GEMINI_ALIASES
            and not resolve_gemini_key(storyboard)):
        raise SystemExit(
            "gemini TTS selected but no API key found. Set GEMINI_API_KEY in the "
            "environment or in a .env at the repo root, set `gemini_api_key:` in the "
            "storyboard front-matter, or pass --gemini-api-key. "
            "Get a key at https://aistudio.google.com/apikey."
        )

    output.mkdir(parents=True, exist_ok=True)

    # Optional pre-pass: let the AI rewrite an over-dense storyboard (within the
    # duration cap). If it actually changes the plan, the cached scripts/audio/
    # scenes from the OLD plan are stale, so we must regenerate from scratch.
    # (--force already wiped above, before the storyboard was chosen.)
    regenerate = False
    if options.refine_storyboard:
        cap = storyboard.max_duration or config.DEFAULT_DURATION_CAP_SECONDS
        refined = StoryboardRefiner(create_ai_client(storyboard.ai_cli, options.effort)).refine(
            storyboard, output, cap)
        if _scenes_changed(storyboard, refined):
            progress.log("  storyboard changed by refinement — regenerating everything "
                         "from the start")
            regenerate = True
        storyboard = refined
        apply_cli_overrides(storyboard, options)   # re-apply flags to the new storyboard

    if regenerate:
        _wipe_outputs(output)
    output.mkdir(parents=True, exist_ok=True)

    _print_header(storyboard, output)
    # Optional agentic pre-pass: actually carry out the # Preparation block (fetch
    # reference assets). Runs AFTER the wipe so --force doesn't delete what it
    # fetched, and BEFORE scene generation so the scenes can use the assets.
    if options.run_preparation:
        _run_preparation(storyboard, output, options)
    _run_with_splits(storyboard, output, options)


def _run_preparation(storyboard: Storyboard, output: Path, options: BuildOptions) -> None:
    """Execute the storyboard's # Preparation block agentically, recording any
    fetched reference assets on the storyboard for scene generation to use."""
    mcp_config = options.mcp_config or (config.REPO_ROOT / ".mcp.json")
    client = create_ai_client(storyboard.ai_cli, options.effort)
    runner = PreparationRunner(client, mcp_config)
    fetched = runner.run(storyboard, output, options.force)
    if fetched is not None:                       # keep any front-matter assets_dir
        storyboard.prep_assets_dir = fetched      # as a fallback when prep yields nothing


def _run_with_splits(storyboard: Storyboard, output: Path, options: BuildOptions) -> None:
    """Run the pipeline; if a scene proves too dense to fit, split it in the
    storyboard and run again, up to a bounded number of rounds.

    A split only renames/adds the split scene's children, so the next run reuses
    every unchanged scene's cached artifacts (no full wipe needed) and generates
    just the new scenes.
    """
    rounds = 0
    while True:
        active = _filtered(storyboard, options.only)
        try:
            build_pipeline(active, output, options).run()
            return
        except SceneTooDenseError as exc:
            _guard_split(exc, rounds)
            rounds += 1
            progress.log(f"  '{exc.scene.basename}' is too dense — splitting it in the "
                         f"storyboard (round {rounds}/{config.MAX_SPLIT_ROUNDS}) and "
                         "regenerating the new scenes")
            cap = storyboard.max_duration or config.DEFAULT_DURATION_CAP_SECONDS
            before = {s.basename for s in storyboard.scenes}
            storyboard = StoryboardRefiner(
                create_ai_client(storyboard.ai_cli, options.effort)).split_scene(
                storyboard, exc.scene, exc.evidence, output, cap)
            apply_cli_overrides(storyboard, options)
            if options.only and exc.scene.basename in options.only:
                children = [s.basename for s in storyboard.scenes if s.basename not in before]
                options.only = [b for b in options.only if b != exc.scene.basename] + children


def _guard_split(exc: SceneTooDenseError, rounds: int) -> None:
    """Refuse to split when it can't help — fail with actionable advice instead."""
    if rounds >= config.MAX_SPLIT_ROUNDS:
        raise SystemExit(
            f"'{exc.scene.basename}' is still too dense after {config.MAX_SPLIT_ROUNDS} "
            f"split(s). Simplify it in the storyboard. Evidence: {exc.evidence}"
        )
    if exc.scene.fallback_duration / 2.0 < config.MIN_CHILD_DURATION_SECONDS:
        raise SystemExit(
            f"'{exc.scene.basename}' ({exc.scene.fallback_duration:g}s) is too dense, but "
            f"splitting it would create scenes under {config.MIN_CHILD_DURATION_SECONDS:g}s. "
            f"Simplify it in the storyboard instead. Evidence: {exc.evidence}"
        )


def _filtered(storyboard: Storyboard, only: Optional[List[str]]) -> Storyboard:
    """A view of the storyboard restricted to the ``--only`` scene basenames."""
    if not only:
        return storyboard
    scenes = [s for s in storyboard.scenes if s.basename in set(only)]
    if not scenes:
        raise SystemExit(f"No scenes matched --only filter: {only}")
    return dataclasses.replace(storyboard, scenes=scenes)


def _scenes_changed(before: Storyboard, after: Storyboard) -> bool:
    """True if refinement altered the scene plan (basename / description / duration).

    Compared on content, not whitespace, so a cosmetically-reformatted but
    identical storyboard does NOT trigger a needless full rebuild.
    """
    def signature(sb: Storyboard):
        return [(s.basename, s.description.strip(), s.fallback_duration) for s in sb.scenes]
    return signature(before) != signature(after)


def _wipe_outputs(output: Path) -> None:
    """Delete every generator-owned subdirectory under ``output`` (for --force /
    a storyboard that refinement changed). The refined storyboard .md is a file
    in the output root, so it is left in place."""
    removed = [name for name in config.WIPE_SUBDIRS if (output / name).exists()]
    for name in removed:
        shutil.rmtree(output / name)
    if removed:
        print(f"  wiped {', '.join(removed)} under {output} (regenerating from scratch)")
    else:
        print("  nothing to wipe (output dir was already clean)")


def _print_header(storyboard: Storyboard, output: Path) -> None:
    print(f"Output dir:   {output}")
    print(f"Title:        {storyboard.title}")
    print(f"Languages:    {storyboard.languages}")
    print(f"Orientations: {storyboard.orientations}")
    print(f"Scenes:       {len(storyboard.scenes)} -> "
          f"{', '.join(s.basename for s in storyboard.scenes)}")
    if not is_noop_preparation(storyboard.preparation):
        print(f"Preparation:  {len(storyboard.preparation)} chars "
              "— applied as scene-generation context")
    print(f"TTS:          {storyboard.tts_provider} (voices: {storyboard.voices})")
    print(f"AI CLI:       {storyboard.ai_cli}")
    print(f"Scenes dirs:  landscape={storyboard.scenes_landscape_dir}, "
          f"portrait={storyboard.scenes_portrait_dir}")
    if storyboard.min_duration is not None or storyboard.max_duration is not None:
        parts = [f"budget {storyboard.duration_budget():.0f}s"]
        if storyboard.min_duration is not None:
            parts.append(f"min {storyboard.min_duration:.0f}s")
        if storyboard.max_duration is not None:
            parts.append(f"cap {storyboard.max_duration:.0f}s")
        print(f"Duration:     {' / '.join(parts)}")
    print()
