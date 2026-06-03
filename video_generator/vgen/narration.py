"""Writing each scene's narration text.

`NarrationWriter` fills in any missing ``narration.<lang>`` by asking an
:class:`~vgen.ai_client.AiClient` to write it from the scene description, then
saves every script to ``<output>/scripts/<lang>/<basename>.txt``. It is given
its AI client in the constructor (*dependency injection*) so the same writer
works with Claude, Codex, or a fake client in tests.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from .ai_client import AiClient
from .models import Scene, Storyboard
from .progress import progress


class NarrationWriter:
    """Generates and persists narration scripts for every scene + language."""

    def __init__(self, ai_client: AiClient) -> None:
        self.ai = ai_client

    def build_prompt(self, storyboard: Storyboard, scene: Scene, lang: str) -> str:
        """The prompt that asks the AI for one scene's narration in one language."""
        lang_name = {"id": "Indonesian", "en": "English"}.get(lang, lang)
        other = next(
            (scene.narration[k] for k in scene.narration
             if k != lang and scene.narration[k].strip()),
            "",
        )
        # ~1.9 words/sec — the real speaking rate is slower than a naive 2.5, so
        # this leaves margin to stay under the scene's duration (and any cap).
        target_words = max(20, int(scene.fallback_duration * 1.9))
        parts = [
            "You are writing the narration for one scene of a software-engineering tutorial video.",
            f"Project title: {storyboard.title}",
            f"Project brief:\n{storyboard.project_brief[:800]}",
            f"Scene: {scene.basename}  (class {scene.classname})",
            f"Scene description:\n{scene.description or '(none)'}",
        ]
        if other:
            parts.append(
                "Equivalent narration that already exists in another language "
                f"(use it for *meaning* only, do not translate word-for-word):\n{other}"
            )
        parts.append(
            f"Write ONLY the {lang_name} narration text. No headings, no bullet points, "
            "no quotation marks, no preamble or trailing commentary. "
            f"HARD LIMIT: at most {target_words} words (aim for ~{int(target_words * 0.9)}) "
            f"so the spoken narration stays within ~{scene.fallback_duration:.0f} seconds. "
            "Be tight and concise — use short sentences and cut detail rather than "
            "exceed the limit. Avoid orientation words (left/right/above/below) since "
            "the same script feeds both landscape and portrait renders."
        )
        return "\n\n".join(parts)

    def ensure(self, storyboard: Storyboard, scene: Scene, lang: str,
               output: Optional[Path] = None) -> str:
        """Return the narration for a scene+language, generating it if missing.

        Priority: text already in the storyboard, then a previously-written
        script file (so resuming a build doesn't re-spend AI tokens), then the AI.
        The result is cached back onto ``scene.narration[lang]``.
        """
        if scene.narration.get(lang, "").strip():
            return scene.narration[lang].strip()
        if output is not None:
            cached = output / "scripts" / lang / f"{scene.basename}.txt"
            if cached.exists():
                text = cached.read_text(encoding="utf-8").strip()
                if text:
                    scene.narration[lang] = text
                    return text
        progress.log(f"  ai-fill narration.{lang} for {scene.basename} via {self.ai.name}…")
        started = time.monotonic()
        text = self.ai.generate(self.build_prompt(storyboard, scene, lang))
        progress.log(f"    ↳ narration.{lang}/{scene.basename} in {time.monotonic() - started:.1f}s")
        if not text:
            raise SystemExit(
                f"AI CLI returned empty narration for {scene.basename}/{lang}. "
                "Fill in the storyboard manually."
            )
        scene.narration[lang] = text
        return text

    def write_scripts(self, storyboard: Storyboard, output: Path) -> None:
        """Ensure every scene's narration exists and save it under scripts/."""
        for lang in storyboard.languages:
            (output / "scripts" / lang).mkdir(parents=True, exist_ok=True)
        for scene in storyboard.scenes:
            for lang in storyboard.languages:
                text = self.ensure(storyboard, scene, lang, output=output)
                (output / "scripts" / lang / f"{scene.basename}.txt").write_text(
                    text.strip() + "\n", encoding="utf-8"
                )
