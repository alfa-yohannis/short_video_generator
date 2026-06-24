"""Keeping the finished video under its ``max_duration`` cap.

`DurationFitter` runs in two passes, both only when the storyboard sets a cap:

* :meth:`fit_before_tts` — *estimate* each language's spoken time from the word
  count and shorten over-long scenes, so we never waste a text-to-speech pass on
  audio that is doomed to be too long.
* :meth:`enforce_after_tts` — *measure* the real audio, and if a language is
  still over, shorten by the measured overshoot and re-synthesise the affected
  scenes.

It needs an :class:`~vgen.ai_client.AiClient` (to rewrite narration shorter) and
a :class:`~vgen.tts.TtsEngine` (to regenerate the dropped audio); both are
injected.
"""

from __future__ import annotations

from pathlib import Path

from . import config
from .ai_client import AiClient
from .media import ffprobe_duration, valid_audio
from .models import Scene, Storyboard
from .progress import progress
from .tts import TtsEngine


def count_words(text: str) -> int:
    return len(text.split())


def estimate_seconds(text: str) -> float:
    """Estimated spoken length of some narration text, in seconds."""
    return count_words(text) / config.ESTIMATE_WORDS_PER_SECOND


class DurationFitter:
    """Shrinks narration so the whole video fits under ``storyboard.max_duration``."""

    def __init__(self, ai_client: AiClient, tts_engine: TtsEngine) -> None:
        self.ai = ai_client
        self.tts = tts_engine

    # --- the two public passes --------------------------------------------

    def fit_before_tts(self, storyboard: Storyboard, output: Path,
                       margin: float = 0.92, passes: int = 2) -> None:
        """Estimate-and-shorten over-long narration *before* any audio is made."""
        if storyboard.max_duration is None or storyboard.ai_cli in ("", "none", None):
            return
        for lang in storyboard.languages:
            for _ in range(passes):
                total = sum(self._scene_seconds(storyboard, output, lang, sc, measured=False)
                            for sc in storyboard.scenes)
                if total <= storyboard.max_duration:
                    break
                progress.log(f"  [{lang}] estimated narration {total:.0f}s > cap "
                             f"{storyboard.max_duration:.0f}s — compressing to "
                             f"~{storyboard.max_duration * margin:.0f}s")
                if not self._shrink_language(storyboard, output, lang, total,
                                             measured=False, margin=margin):
                    break

    def enforce_after_tts(self, storyboard: Storyboard, output: Path,
                          margin: float = 0.92, passes: int = 2) -> None:
        """Measure real audio and, if still over, shorten + re-synthesise."""
        if storyboard.max_duration is None or storyboard.ai_cli in ("", "none", None):
            return
        for _ in range(passes):
            regenerated = False
            for lang in storyboard.languages:
                total = sum(self._scene_seconds(storyboard, output, lang, sc, measured=True)
                            for sc in storyboard.scenes)
                if total <= storyboard.max_duration:
                    continue
                progress.log(f"  [{lang}] rendered audio {total:.0f}s > cap "
                             f"{storyboard.max_duration:.0f}s — compressing and re-synthesizing")
                if self._shrink_language(storyboard, output, lang, total,
                                         measured=True, margin=margin):
                    regenerated = True
            if not regenerated:
                break
            self.tts.synthesize_storyboard(storyboard, output, force=False)

    def enforce_floor_after_tts(self, storyboard: Storyboard, output: Path,
                                margin: float = 1.06, passes: int = 2) -> None:
        """Measure real audio and, if a language is UNDER ``min_duration``, EXPAND
        its narration and re-synthesise so the finished video clears the floor.

        The mirror of :meth:`enforce_after_tts`. A language whose spoken audio sums
        to less than the floor (e.g. terse Indonesian) otherwise renders a video
        well under the requested 2–3 minutes, since each scene only pads out to its
        own audio. Expanding lifts every spoken scene proportionally toward
        ``margin × floor`` (kept under any ``max_duration`` cap), preserving meaning.
        """
        if storyboard.min_duration is None or storyboard.ai_cli in ("", "none", None):
            return
        floor = storyboard.min_duration
        for _ in range(passes):
            regenerated = False
            for lang in storyboard.languages:
                total = sum(self._scene_seconds(storyboard, output, lang, sc, measured=True)
                            for sc in storyboard.scenes)
                if total >= floor:
                    continue
                progress.log(f"  [{lang}] rendered audio {total:.0f}s < floor "
                             f"{floor:.0f}s — expanding and re-synthesizing")
                if self._grow_language(storyboard, output, lang, total, floor, margin):
                    regenerated = True
            if not regenerated:
                break
            self.tts.synthesize_storyboard(storyboard, output, force=False)

    def fill_short_scenes_after_tts(self, storyboard: Storyboard, output: Path,
                                    margin: float = 0.82, passes: int = 2) -> None:
        """Fill any single scene whose narration renders much SHORTER than that
        scene's intended length (its ``fallback_duration``), so the narration covers
        the scene instead of leaving a long silent tail.

        A scene's video length is ``max(animation_time, narration)``: if the
        narration is shorter than the animation, the video can't shrink to match and
        the clip ends with seconds of silence (e.g. the English "five questions" ran
        ~6s silent while the naturally-longer Indonesian matched the video exactly).
        This expands such a scene's narration toward its ``fallback_duration`` and
        re-synthesises ONLY that scene — no re-render needed; the mux holds the last
        frame for any small residual. Cap-safe: the sum of ``fallback_duration``
        values is already constrained to <= ``max_duration`` at parse time, so
        filling each scene to its own length can't blow the whole-video cap.
        """
        if storyboard.ai_cli in ("", "none", None):
            return
        for _ in range(passes):
            regenerated = False
            for lang in storyboard.languages:
                for scene in storyboard.scenes:
                    text = scene.narration.get(lang, "")
                    target = scene.fallback_duration
                    if not text.strip() or target <= 0:
                        continue
                    measured = self._scene_seconds(storyboard, output, lang, scene,
                                                   measured=True)
                    if measured >= target * margin:
                        continue
                    target_words = int(target * config.ESTIMATE_WORDS_PER_SECOND)
                    if target_words <= count_words(text):
                        continue
                    progress.log(f"  [{lang}] scene {scene.basename}: narration "
                                 f"{measured:.0f}s << scene {target:.0f}s — filling")
                    new_text = self._expand_narration(storyboard, lang, text,
                                                      target_words, scene)
                    if count_words(new_text) <= count_words(text):
                        continue
                    scene.narration[lang] = new_text
                    (output / "scripts" / lang / f"{scene.basename}.txt").write_text(
                        new_text.strip() + "\n", encoding="utf-8")
                    (output / "audio" / lang / f"{scene.basename}.mp3").unlink(missing_ok=True)
                    (output / "audio" / lang / f"{scene.basename}.srt").unlink(missing_ok=True)
                    progress.log(f"    ↳ {lang}/{scene.basename}: "
                                 f"{count_words(text)}→{count_words(new_text)} words")
                    regenerated = True
            if not regenerated:
                break
            self.tts.synthesize_storyboard(storyboard, output, force=False)

    # --- helpers -----------------------------------------------------------

    def _scene_seconds(self, storyboard: Storyboard, output: Path, lang: str,
                       scene: Scene, measured: bool) -> float:
        """A scene's length: measured from audio, or estimated from word count."""
        if measured:
            mp3 = output / "audio" / lang / f"{scene.basename}.mp3"
            return ffprobe_duration(mp3) if valid_audio(mp3) else scene.fallback_duration
        return estimate_seconds(scene.narration.get(lang, ""))

    def _shrink_language(self, storyboard: Storyboard, output: Path, lang: str,
                         total: float, measured: bool, margin: float) -> bool:
        """Compress every over-budget scene in a language toward ``margin × cap``.

        Rewrites the script file and (when measuring real audio) drops the stale
        mp3/srt so they regenerate. Returns True if anything changed.
        """
        scale = (storyboard.max_duration * margin) / total
        changed = False
        for scene in storyboard.scenes:
            current = scene.narration.get(lang, "")
            if not current.strip():
                continue
            target_words = max(15, int(count_words(current) * scale))
            if count_words(current) <= target_words:
                continue
            new_text = self._compress_narration(storyboard, lang, current, target_words)
            scene.narration[lang] = new_text
            (output / "scripts" / lang / f"{scene.basename}.txt").write_text(
                new_text.strip() + "\n", encoding="utf-8")
            # Invalidate stale audio/srt so it regenerates from the shorter text.
            # (Both live under audio/<lang>/ now.)
            (output / "audio" / lang / f"{scene.basename}.mp3").unlink(missing_ok=True)
            (output / "audio" / lang / f"{scene.basename}.srt").unlink(missing_ok=True)
            progress.log(f"    ↳ {lang}/{scene.basename}: "
                         f"{count_words(current)}→{count_words(new_text)} words")
            changed = True
        return changed

    def _compress_narration(self, storyboard: Storyboard, lang: str,
                            current: str, target_words: int) -> str:
        """Ask the AI to rewrite narration shorter, preserving meaning."""
        lang_name = {"id": "Indonesian", "en": "English"}.get(lang, lang)
        prompt = (
            f"Rewrite the following {lang_name} tutorial narration to be SHORTER: at "
            f"most {target_words} words, preserving the key meaning and a natural "
            "spoken tone. Output ONLY the rewritten narration text — no preamble, no "
            "quotation marks, no commentary.\n\n" + current
        )
        out = self.ai.generate(prompt).strip()
        return out or current

    def _grow_language(self, storyboard: Storyboard, output: Path, lang: str,
                       total: float, floor: float, margin: float) -> bool:
        """Expand every spoken scene in a language toward ``margin × floor``.

        Rewrites the script file and drops the stale mp3/srt so they regenerate
        from the longer text. Returns True if anything changed.
        """
        target_total = floor * margin
        if storyboard.max_duration is not None:                 # never blow the cap
            target_total = max(floor, min(target_total, storyboard.max_duration * 0.95))
        if total <= 0:
            return False
        scale = target_total / total
        if scale <= 1.02:
            return False
        changed = False
        for scene in storyboard.scenes:
            current = scene.narration.get(lang, "")
            if not current.strip():
                continue
            target_words = max(count_words(current) + 4, int(count_words(current) * scale))
            new_text = self._expand_narration(storyboard, lang, current,
                                              target_words, scene)
            if count_words(new_text) <= count_words(current):
                continue
            scene.narration[lang] = new_text
            (output / "scripts" / lang / f"{scene.basename}.txt").write_text(
                new_text.strip() + "\n", encoding="utf-8")
            # Invalidate stale audio/srt so it regenerates from the longer text.
            (output / "audio" / lang / f"{scene.basename}.mp3").unlink(missing_ok=True)
            (output / "audio" / lang / f"{scene.basename}.srt").unlink(missing_ok=True)
            progress.log(f"    ↳ {lang}/{scene.basename}: "
                         f"{count_words(current)}→{count_words(new_text)} words")
            changed = True
        return changed

    def _expand_narration(self, storyboard: Storyboard, lang: str, current: str,
                          target_words: int, scene: Scene) -> str:
        """Ask the AI to rewrite narration LONGER, adding plain-language detail
        without inventing facts. Uses the companion-language script (if present) as
        a depth reference so the expanded text matches the other language's level."""
        lang_name = {"id": "Indonesian", "en": "English"}.get(lang, lang)
        other = "en" if lang == "id" else "id"
        other_name = {"id": "Indonesian", "en": "English"}.get(other, other)
        companion = scene.narration.get(other, "").strip()
        ref = ""
        if companion:
            ref = (f"\n\nFor reference, the {other_name} narration of the SAME scene "
                   f"covers this depth of detail (match its level — but write natural "
                   f"{lang_name}, do NOT translate it word-for-word):\n{companion}")
        prompt = (
            f"Expand the following {lang_name} tutorial narration to about "
            f"{target_words} words (it is currently {count_words(current)}). Add "
            "helpful plain-language explanation, examples already implied by the "
            "scene, and natural spoken flow — WITHOUT inventing new facts or changing "
            f"the meaning. Keep it in {lang_name}. Output ONLY the narration text — no "
            f"preamble, no quotation marks, no commentary.\n\nCurrent narration:\n"
            f"{current}{ref}"
        )
        out = self.ai.generate(prompt).strip()
        return out or current
