"""Rewriting the storyboard with the AI: density review and scene splitting.

`StoryboardRefiner` has two jobs, both keeping the whole video within the
duration cap:

* :meth:`refine` — an optional up-front pass (``--refine-storyboard``) that
  rewrites scenes judged too dense *from their descriptions*.
* :meth:`split_scene` — called mid-build when a scene proves too dense *when
  rendered* (it kept overflowing): split that one scene into smaller ones,
  dividing its duration.

Both write the result to ``<output>/storyboard.refined.md`` (the user's original
file is never touched) and re-parse it. Re-parsing plus an explicit budget check
is the strict guard: the result must fit the cap, and the AI is retried until it
does. They build the prompt from ``Storyboard.to_markdown()`` so they always act
on the current plan, even after an earlier edit.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Optional

from . import config
from .ai_client import AiClient
from .models import Scene, Storyboard
from .progress import progress
from .storyboard import StoryboardParser


class StoryboardRefiner:
    """Rewrites a too-dense storyboard via the AI, keeping it within the cap."""

    def __init__(self, ai_client: AiClient, parser: Optional[StoryboardParser] = None) -> None:
        self.ai = ai_client
        self.parser = parser or StoryboardParser()

    # --- public passes -----------------------------------------------------

    def refine(self, storyboard: Storyboard, output: Path, cap_seconds: float,
               attempts: int = 3) -> Storyboard:
        """Review every scene's density and rewrite the over-dense ones."""
        current = storyboard.to_markdown()
        floor_seconds = storyboard.min_duration or config.DEFAULT_DURATION_FLOOR_SECONDS
        progress.log(f"  reviewing storyboard density "
                     f"({floor_seconds:.0f}-{cap_seconds:.0f}s) via {self.ai.name}…")
        return self._generate_valid(
            lambda last: self._density_prompt(current, floor_seconds, cap_seconds, last),
            output, floor_seconds, cap_seconds, attempts,
            describe=lambda sb: f"refined storyboard: {len(sb.scenes)} scenes, "
                                f"{sb.duration_budget():.0f}s total")

    def split_scene(self, storyboard: Storyboard, scene: Scene, evidence: str,
                    output: Path, cap_seconds: float, attempts: int = 3) -> Storyboard:
        """Split one too-dense scene into smaller ones, dividing its duration."""
        current = storyboard.to_markdown()
        floor_seconds = storyboard.min_duration or config.DEFAULT_DURATION_FLOOR_SECONDS
        progress.log(f"  splitting too-dense scene '{scene.basename}' "
                     f"({scene.fallback_duration:g}s) via {self.ai.name}…")
        return self._generate_valid(
            lambda last: self._split_prompt(
                current, scene, evidence, floor_seconds, cap_seconds, last),
            output, floor_seconds, cap_seconds, attempts,
            describe=lambda sb: f"split into {len(sb.scenes)} scenes, "
                                f"{sb.duration_budget():.0f}s total")

    # --- shared generate -> parse -> validate -> retry loop ----------------

    def _generate_valid(self, build_prompt: Callable[[str], str], output: Path,
                        floor_seconds: float, cap_seconds: float, attempts: int,
                        describe: Callable[[Storyboard], str]) -> Storyboard:
        refined_path = output / "storyboard.refined.md"
        last_problem = ""
        for _ in range(attempts):
            markdown = self._extract_markdown(self.ai.generate(build_prompt(last_problem)))
            refined_path.write_text(markdown, encoding="utf-8")
            try:
                refined = self.parser.parse(refined_path)          # raises if over the cap
            except SystemExit as exc:
                last_problem = str(exc)
                continue
            budget = refined.duration_budget()
            if budget < floor_seconds - 1e-6:
                last_problem = (f"the scene fallback_duration values sum to {budget:.0f}s, "
                                f"below the {floor_seconds:.0f}s minimum")
                continue
            if budget > cap_seconds + 1e-6:
                last_problem = (f"the scene fallback_duration values sum to {budget:.0f}s, "
                                f"over the {cap_seconds:.0f}s cap")
                continue
            progress.log(f"    ↳ {describe(refined)} -> {refined_path}")
            return refined
        raise SystemExit(
            f"Storyboard rewrite could not stay within the {floor_seconds:.0f}-"
            f"{cap_seconds:.0f}s range after "
            f"{attempts} attempt(s). Last problem: {last_problem}"
        )

    # --- prompts -----------------------------------------------------------

    def _density_prompt(self, markdown: str, floor_seconds: float,
                        cap_seconds: float, last_problem: str) -> str:
        floor_minutes = floor_seconds / 60.0
        minutes = cap_seconds / 60.0
        return f"""You are reviewing a tutorial-video STORYBOARD (markdown) for scene density.

A scene is "too dense" when its `### description` asks for more concepts or
visuals than can be taught clearly in its `**fallback_duration:**` seconds.

Return a revised storyboard in the SAME markdown format. If a scene is too dense
you MAY: trim/simplify its `### description`; split one dense scene into two
(each with its own `## Scene: NN_basename / ClassName`, `**file:**`,
`**fallback_duration:**`, `### description`); or rebalance the
`**fallback_duration:**` values.

HARD RULES:
- The whole video MUST stay between {floor_seconds:.0f} seconds
  ({floor_minutes:.0f} minutes) and {cap_seconds:.0f} seconds
  ({minutes:.0f} minutes): the SUM of every `**fallback_duration:**` MUST be
  >= {floor_seconds:.0f} and <= {cap_seconds:.0f}.
- Keep the YAML front-matter intact. Do NOT add narration text or scene code.
- If NO scene is too dense, return the storyboard UNCHANGED.
- Output ONLY the storyboard markdown — no commentary, no code fences.
{self._retry_note(last_problem)}
Here is the current storyboard:

{markdown}
"""

    def _split_prompt(self, markdown: str, scene: Scene, evidence: str,
                      floor_seconds: float, cap_seconds: float, last_problem: str) -> str:
        floor = config.MIN_CHILD_DURATION_SECONDS
        return f"""You are fixing a TOO-DENSE scene in a tutorial-video storyboard.

When rendered, scene `{scene.basename}` repeatedly overflowed the frame even
after its layout was adjusted — it tries to show too much for its
{scene.fallback_duration:g} seconds. Rendering evidence:
{evidence}

Rewrite the storyboard so that ONLY scene `{scene.basename}` is SPLIT into two
(or at most three) smaller scenes, each teaching one part of it.

HARD RULES:
- DIVIDE `{scene.basename}`'s {scene.fallback_duration:g}s among the new scenes
  (they should sum to about {scene.fallback_duration:g}s — do NOT add total time).
  Each new scene's `**fallback_duration:**` MUST be >= {floor:g} seconds.
- Give each new scene a UNIQUE basename derived from the original (e.g.
  `{scene.basename}a`, `{scene.basename}b`) with its own
  `## Scene: <basename> / <ClassName>`, `**file:** scene_<basename>.py`,
  `**fallback_duration:**`, and a focused `### description`.
- Do NOT change any other scene. Keep the YAML front-matter intact. The SUM of
  ALL `**fallback_duration:**` values MUST stay >= {floor_seconds:.0f} and
  <= {cap_seconds:.0f}.
- Do NOT add narration text or scene code.
- Output ONLY the storyboard markdown — no commentary, no code fences.
{self._retry_note(last_problem)}
Here is the current storyboard:

{markdown}
"""

    @staticmethod
    def _retry_note(last_problem: str) -> str:
        if not last_problem:
            return ""
        return f"\nYour previous attempt was rejected: {last_problem}. Fix that and try again.\n"

    @staticmethod
    def _extract_markdown(reply: str) -> str:
        """Pull the storyboard markdown out of the AI reply (strip fences/prose)."""
        text = reply.strip()
        fenced = re.search(r"```(?:markdown|md)?[ \t]*\n(.*?)```", text, re.S | re.I)
        if fenced:
            text = fenced.group(1).strip()
        idx = text.find("---")                     # drop any prose before the front-matter
        if idx > 0 and text[:idx].strip():
            text = text[idx:]
        return text.strip()
