"""Refining an over-dense storyboard before the build.

`StoryboardRefiner` is an optional pre-pass (enabled with ``--refine-storyboard``):
it shows the storyboard to the AI and asks it to rewrite *only* the scenes that
are too dense to teach clearly in their time — by trimming a description,
splitting one scene into two, or rebalancing the per-scene durations — under one
hard rule: the whole video must stay within the duration cap (3 minutes).

The revised storyboard is written to ``<output>/storyboard.refined.md`` (the
user's original file is never touched) and re-parsed. Re-parsing is itself the
strict guard: :class:`~vgen.storyboard.StoryboardParser` refuses a storyboard
whose scene durations sum past the cap, and this class re-checks the budget too,
retrying the AI until the result fits.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from . import config
from .ai_client import AiClient
from .models import Storyboard
from .progress import progress
from .storyboard import StoryboardParser


class StoryboardRefiner:
    """Rewrites a too-dense storyboard via the AI, keeping it within the cap."""

    def __init__(self, ai_client: AiClient, parser: Optional[StoryboardParser] = None) -> None:
        self.ai = ai_client
        self.parser = parser or StoryboardParser()

    def refine(self, storyboard_path: Path, output: Path, cap_seconds: float,
               attempts: int = 3) -> Storyboard:
        """Ask the AI to refine the storyboard; return the re-parsed result.

        Loops up to ``attempts`` times: if the AI returns something that won't
        parse or that overruns ``cap_seconds``, it is asked again with the
        problem explained. The accepted result is written to
        ``<output>/storyboard.refined.md``.
        """
        original = storyboard_path.read_text(encoding="utf-8")
        refined_path = output / "storyboard.refined.md"
        progress.log(f"  reviewing storyboard density (cap {cap_seconds:.0f}s) via {self.ai.name}…")
        last_problem = ""
        for attempt in range(1, attempts + 1):
            markdown = self._extract_markdown(
                self.ai.generate(self._build_prompt(original, cap_seconds, last_problem)))
            refined_path.write_text(markdown, encoding="utf-8")
            try:
                refined = self.parser.parse(refined_path)
            except SystemExit as exc:               # malformed, or over the cap
                last_problem = str(exc)
                continue
            budget = refined.duration_budget()
            if budget > cap_seconds + 1e-6:
                last_problem = (f"the scene fallback_duration values sum to {budget:.0f}s, "
                                f"which exceeds the {cap_seconds:.0f}s cap")
                continue
            progress.log(f"    ↳ refined storyboard: {len(refined.scenes)} scenes, "
                         f"{budget:.0f}s total -> {refined_path}")
            return refined
        raise SystemExit(
            f"Storyboard refinement could not produce a valid storyboard within the "
            f"{cap_seconds:.0f}s cap after {attempts} attempt(s). Last problem: {last_problem}"
        )

    # --- prompt + reply parsing -------------------------------------------

    def _build_prompt(self, original_markdown: str, cap_seconds: float, last_problem: str) -> str:
        minutes = cap_seconds / 60.0
        retry_note = ""
        if last_problem:
            retry_note = (f"\nYour previous attempt was rejected: {last_problem}. "
                          "Fix that and try again.\n")
        return f"""You are reviewing a tutorial-video STORYBOARD (markdown) for scene density.

A scene is "too dense" when its `### description` asks for more concepts or
visuals than can be taught clearly in its `**fallback_duration:**` seconds.

Your job: return a revised storyboard in the SAME markdown format. If a scene is
too dense, you MAY:
  - trim or simplify its `### description` to focus on the core idea,
  - split one dense scene into two scenes (give the new scene its own
    `## Scene: NN_basename / ClassName` heading, `**file:**`, `**fallback_duration:**`
    and `### description`), or
  - rebalance the `**fallback_duration:**` values across scenes.

HARD RULES:
- The whole video MUST fit within {cap_seconds:.0f} seconds ({minutes:.0f} minutes):
  the SUM of every scene's `**fallback_duration:**` MUST be <= {cap_seconds:.0f}.
- Keep the YAML front-matter fields intact (title, languages, orientations,
  voices, tts_provider, ai_cli, fps, resolution_landscape, and the max-duration
  cap). Do NOT add narration text or scene code — only descriptions/structure.
- If NO scene is too dense, return the storyboard UNCHANGED.
- Output ONLY the storyboard markdown — no commentary, no code fences.
{retry_note}
Here is the current storyboard:

{original_markdown}
"""

    @staticmethod
    def _extract_markdown(reply: str) -> str:
        """Pull the storyboard markdown out of the AI reply (strip fences/prose)."""
        text = reply.strip()
        fenced = re.search(r"```(?:markdown|md)?[ \t]*\n(.*?)```", text, re.S | re.I)
        if fenced:
            text = fenced.group(1).strip()
        # Drop any leading prose before the YAML front-matter's opening '---'.
        idx = text.find("---")
        if idx > 0 and text[:idx].strip():
            text = text[idx:]
        return text.strip()
