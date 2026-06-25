"""Command-line interface: parse arguments into :class:`BuildOptions` and build.

This module is intentionally thin. Its only job is to translate the command
line into a :class:`~vgen.pipeline.BuildOptions` value object and hand it to
:func:`~vgen.pipeline.run_build`. All the real work lives in the service classes.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

from . import config
from .pipeline import BuildOptions, run_build


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a bilingual Manim tutorial video from a storyboard markdown file."
    )
    parser.add_argument("--storyboard", required=True, help="Path to storyboard markdown file")
    parser.add_argument("--output", required=True, help="Output directory (all intermediates go here)")
    parser.add_argument(
        "--stage",
        choices=["all", "scripts", "audio", "scenes", "render", "mux", "concat",
                 "thumbnails", "srt", "youtube"],
        default="all", help="Run only one stage of the pipeline (default: all)",
    )
    parser.add_argument(
        "--only", nargs="*", default=None,
        help="Restrict pipeline to these scene basenames (for testing one scene)",
    )
    parser.add_argument("--force", action="store_true", help="Rebuild artifacts even if they exist")
    parser.add_argument(
        "--ai-cli", choices=["claude", "codex"], default="claude",
        help="AI CLI used to fill in missing narration / scene .py files "
             "(default: claude). Overrides 'ai_cli' in the storyboard front-matter.",
    )
    parser.add_argument(
        "--effort", choices=["low", "medium", "high", "xhigh", "max"],
        default=config.DEFAULT_CLAUDE_EFFORT,
        help="Reasoning effort for the Claude AI CLI (default: "
             f"{config.DEFAULT_CLAUDE_EFFORT}; pass 'max' for the top tier). "
             "Ignored when --ai-cli is codex.",
    )
    parser.add_argument(
        "--tts", choices=["edge", "gemini", "gemini_id"], default=None,
        help="Text-to-speech provider. edge is free/no-key with exact subtitle "
             "timing (default voice Ardi); gemini needs an API key and gives nicer "
             "voices with estimated subtitle timing (default voice Iapetus); "
             "gemini_id voices Indonesian with Gemini (Iapetus) but reproduces a "
             "clip on the free Edge Indonesian voice if Gemini fails, while every "
             "other language stays on Edge. "
             "Overrides 'tts_provider' in the storyboard front-matter when set.",
    )
    parser.add_argument(
        "--voice", default=None,
        help="Override the TTS voice for every language this run "
             "(e.g. id-ID-GadisNeural for edge, or Charon for gemini).",
    )
    parser.add_argument(
        "--orientation", choices=["landscape", "portrait", "both"], default="both",
        help="Which orientation(s) to generate (default: both). 'landscape' or "
             "'portrait' restricts the whole run to that one; 'both' uses the "
             "storyboard's 'orientations:' (which itself defaults to both).",
    )
    parser.add_argument(
        "--gemini-api-key", default=None,
        help="Gemini API key. Defaults to $GEMINI_API_KEY, then a .env at the "
             "repo root. (For security it is never read from the storyboard.)",
    )
    parser.add_argument(
        "--check-layout", choices=["off", "warn", "strict", "fit"], default="off",
        help="At render time, check each scene's text for off-frame overflow / "
             "clipping / overlap. 'warn' logs; 'strict' fails; 'fit' auto-scales "
             "overflowing text back inside the frame (default: off).",
    )
    parser.add_argument(
        "--repair-attempts", "--layout-repair-attempts", type=int, default=2,
        dest="repair_attempts",
        help="How many times to ask the AI to fix a scene that FAILS to render "
             "before giving up (default: 2; 0 disables AI repair).",
    )
    parser.add_argument(
        "--validate-scenes", action="store_true",
        help="Right after generating each scene, render-check it against the "
             "layout rules (strict) and automatically refine it until it passes "
             "(see --validate-attempts), before the real render.",
    )
    parser.add_argument(
        "--validate-attempts", type=int, default=10,
        help="With --validate-scenes, how many times to refine a scene that "
             "fails the check before giving up (default: 10).",
    )
    parser.add_argument(
        "--refine-storyboard", action="store_true",
        help="Before building, let the AI rewrite the storyboard if any scene is "
             "too dense (trim/split/rebalance scenes), keeping the whole video "
             "within the duration cap. If it changes the plan, everything is "
             "regenerated from scratch. The revision is saved to "
             "<output>/storyboard.refined.md (your original file is untouched). "
             "Without this flag, an existing <output>/storyboard.refined.md from a "
             "previous run is always reused; if none exists, the original is used. "
             "--force removes the refined file and rebuilds from the original.",
    )
    parser.add_argument(
        "--run-preparation", action="store_true",
        help="Before generating scenes, run the storyboard's `# Preparation` block "
             "AGENTICALLY (tools on, with the MCP servers in --mcp-config) so the AI "
             "actually fetches the reference assets it describes. The behavior is set "
             "by the storyboard's `preparation_profile:` (a profiles/<name>.yaml; "
             "default 'generic'); the 'archi' profile launches Archi and exports "
             "ArchiMate symbols into <output>/assets/archi/. Best-effort: falls back "
             "to Manim primitives if it can't. Without this flag the block is "
             "context-only (no execution).",
    )
    parser.add_argument(
        "--mcp-config", default=None,
        help="Path to the .mcp.json the preparation agent loads (default: the repo "
             "root .mcp.json). Only used with --run-preparation.",
    )
    parser.add_argument("--skip-youtube", action="store_true",
                        help="Don't generate the final/<title>_<orient>_<lang>.txt metadata")
    parser.add_argument("--skip-dep-check", action="store_true",
                        help="Don't validate / auto-install dependencies before building")
    parser.add_argument("--no-ai-cli-check", action="store_true",
                        help="Skip the AI CLI presence check even if the storyboard declares one")
    parser.add_argument(
        "--no-fit-narration", action="store_true",
        help="Keep narration verbatim — skip the duration-fitter passes that "
             "compress/expand/fill narration to hit the length window. Use when you "
             "provide exact narration scripts and don't want them rewritten.",
    )
    parser.add_argument(
        "--jobs", type=int, default=None, metavar="N",
        help="Parallelism ceiling for the per-scene stages (narration, TTS, scene "
             "generation, render). Default: per-stage caps (AI 2, Edge-TTS 4, "
             "Gemini-TTS 2, render ~cores-2). A number lowers every stage to "
             "min(cap, N); --jobs 1 forces fully serial.",
    )
    return parser


def options_from_args(args: argparse.Namespace) -> BuildOptions:
    """Convert parsed argparse output into a :class:`BuildOptions`."""
    return BuildOptions(
        storyboard=Path(args.storyboard),
        output=Path(args.output),
        stage=args.stage,
        only=args.only,
        force=args.force,
        ai_cli=args.ai_cli,
        effort=args.effort,
        tts=args.tts,
        voice=args.voice,
        orientation=args.orientation,
        gemini_api_key=args.gemini_api_key,
        check_layout=args.check_layout,
        repair_attempts=args.repair_attempts,
        validate_scenes=args.validate_scenes,
        validate_attempts=args.validate_attempts,
        refine_storyboard=args.refine_storyboard,
        run_preparation=args.run_preparation,
        mcp_config=Path(args.mcp_config) if args.mcp_config else None,
        skip_youtube=args.skip_youtube,
        skip_dep_check=args.skip_dep_check,
        no_ai_cli_check=args.no_ai_cli_check,
        jobs=args.jobs,
        no_fit_narration=args.no_fit_narration,
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    run_build(options_from_args(args))
