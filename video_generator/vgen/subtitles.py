"""Building estimated subtitle (.srt) files.

Edge TTS returns exact word timings, but Gemini returns only raw audio. For
Gemini we therefore *estimate* a subtitle track: split the narration into
sentences and hand each one a slice of the measured audio length in proportion
to its character count. Good enough for on-screen captions.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List


def format_timestamp(seconds: float) -> str:
    """Format seconds as an SRT timestamp ``HH:MM:SS,mmm`` (negatives clamp to 0)."""
    if seconds < 0:
        seconds = 0.0
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def split_sentences(text: str) -> List[str]:
    """Split text into sentences on ``.``/``!``/``?`` boundaries (empties dropped)."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def write_estimated_srt(text: str, duration: float, srt_path: Path) -> None:
    """Write an SRT whose cues share ``duration`` proportionally to sentence length."""
    sentences = split_sentences(text)
    if not sentences:
        srt_path.write_text("", encoding="utf-8")
        return
    weights = [max(1, len(s)) for s in sentences]
    total = sum(weights) or 1
    elapsed = 0
    cues: List[str] = []
    for index, (sentence, weight) in enumerate(zip(sentences, weights), start=1):
        start = duration * elapsed / total
        elapsed += weight
        end = duration * elapsed / total
        if index == len(sentences):
            end = duration  # make the last cue land exactly on the end
        cues.append(
            f"{index}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{sentence}\n"
        )
    srt_path.write_text("\n".join(cues), encoding="utf-8")
