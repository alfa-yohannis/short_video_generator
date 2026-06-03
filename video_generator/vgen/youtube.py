"""Writing YouTube publishing metadata (``youtube/<lang>/youtube.txt``).

`YouTubeMetadataWriter` asks the AI for a title / description / keywords block
from a language's narration transcript, then *sanitises and clamps* each field
to YouTube's limits with the small pure helpers in this module. It is a trailing
nice-to-have: a failure here never aborts the build.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from . import config
from .ai_client import AiClient
from .models import Storyboard
from .progress import progress


# Emoji / pictograph ranges to strip (kept narrow so ordinary punctuation —
# em dash, ellipsis, curly quotes — survives).
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U0001F1E6-\U0001F1FF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U00002B00-\U00002BFF"
    "\U0000FE00-\U0000FE0F"
    "\U00002190-\U000021FF"
    "]+",
    flags=re.UNICODE,
)


def tidy_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" *\n", "\n", text)
    return text.strip()


def strip_emoji(text: str) -> str:
    """Remove emoji/pictographs but keep hashtags and ordinary punctuation."""
    return tidy_whitespace(_EMOJI_RE.sub("", text))


def strip_emoji_and_hashtags(text: str) -> str:
    """For the title: strip emoji AND ``#hashtags`` (but keep things like ``C#``)."""
    text = _EMOJI_RE.sub("", text)
    text = re.sub(r"(?<!\S)#\w+", "", text)
    return tidy_whitespace(text)


def cap_hashtags(text: str, max_tags: int = 15) -> str:
    """YouTube ignores ALL hashtags once a description has more than 15, so drop
    any beyond the 15th rather than risk losing them all."""
    count = 0

    def repl(match: re.Match) -> str:
        nonlocal count
        count += 1
        return match.group(0) if count <= max_tags else ""

    return tidy_whitespace(re.sub(r"(?<!\S)#\w+", repl, text))


def clamp(text: str, limit: int) -> str:
    """Trim text to ``limit`` characters, snapping to a word boundary if one is near."""
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    space = cut.rfind(" ")
    if space >= limit - 20:
        cut = cut[:space]
    return cut.rstrip()


def clamp_keywords(keywords: str, limit: int = config.YT_KEYWORDS_MAX) -> str:
    """Keep whole comma-separated tags until the total length would exceed ``limit``."""
    tags = [t.strip() for t in keywords.replace("\n", ",").split(",") if t.strip()]
    out = []
    total = 0
    for tag in tags:
        addition = len(tag) + (2 if out else 0)  # account for the ", " joiner
        if total + addition > limit:
            break
        out.append(tag)
        total += addition
    return ", ".join(out)


def extract_json(text: str) -> dict:
    """Parse a JSON object out of an AI reply, tolerating ``` fences / surrounding prose."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def youtube_text(title: str, description: str, keywords: str) -> str:
    """Render the final ``youtube.txt`` body."""
    return (
        f"TITLE\n{title.strip()}\n\n"
        f"DESCRIPTION\n{description.strip()}\n\n"
        f"KEYWORDS\n{keywords.strip()}\n"
    )


def youtube_prompt(transcript: str, lang: str) -> str:
    """The prompt asking the AI for title/description/keywords as one JSON object."""
    lang_name = {"id": "Indonesian", "en": "English"}.get(lang, lang)
    return (
        "You are writing YouTube publishing metadata for a narrated tutorial "
        f"video. Base it ONLY on the narration transcript below. Write the "
        f'"title" and "description" in {lang_name}.\n\n'
        'Return ONE JSON object with exactly these keys: "title", "description", '
        '"keywords".\n'
        "- title: at most 100 characters; put the most important, searchable "
        "terms in the first ~70 characters; no emoji; NO hashtags.\n"
        "- description: at most 5000 characters; no emoji. Start with a strong "
        "hook in the first ~157 characters, then a short overview and a bulleted "
        'list (plain "- " lines) of what the video covers. END with one final '
        "line of 5 to 10 relevant hashtags as single words with no spaces "
        "(e.g. #Pythagoras #Mathematics). Use at most 15 hashtags, and put "
        "hashtags ONLY here in the description, never in the title.\n"
        "- keywords: a comma-separated list of plain tags (NO '#'); total length "
        "at most 500 characters; each tag at most 30 characters; mix "
        f"{lang_name} and English technical terms.\n\n"
        "Output ONLY the JSON object. No code fence, no commentary.\n\n"
        "Transcript:\n" + transcript
    )


class YouTubeMetadataWriter:
    """Generates ``youtube/<lang>/youtube.txt`` for each language."""

    def __init__(self, ai_client: AiClient) -> None:
        self.ai = ai_client

    def generate(self, storyboard: Storyboard, output: Path, force: bool) -> None:
        """Write metadata per language. Never raises on AI/parse failure — the
        video itself is unaffected."""
        for lang in storyboard.languages:
            out_path = output / "youtube" / lang / "youtube.txt"
            if out_path.exists() and not force:
                print(f"  youtube/{lang}/youtube.txt exists — skipping (use --force)")
                continue
            transcript = self._read_transcript(storyboard, output, lang)
            if not transcript:
                print(f"  no narration for {lang} — skipping youtube.txt")
                continue
            try:
                meta = extract_json(self.ai.generate(youtube_prompt(transcript, lang)))
            except (SystemExit, RuntimeError, json.JSONDecodeError, OSError) as exc:
                print(f"  youtube metadata for {lang} failed ({type(exc).__name__}: {exc}); "
                      "skipping. The video itself is unaffected.")
                continue
            title = clamp(strip_emoji_and_hashtags(str(meta.get("title", ""))), config.YT_TITLE_MAX)
            desc = clamp(cap_hashtags(strip_emoji(str(meta.get("description", "")))), config.YT_DESC_MAX)
            keywords = clamp_keywords(str(meta.get("keywords", "")), config.YT_KEYWORDS_MAX)
            if not title or not desc:
                print(f"  AI returned empty title/description for {lang}; skipping youtube.txt")
                continue
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(youtube_text(title, desc, keywords), encoding="utf-8")
            progress.log(f"  -> {out_path} (title {len(title)}/{config.YT_TITLE_MAX}, "
                         f"desc {len(desc)}/{config.YT_DESC_MAX}, "
                         f"keywords {len(keywords)}/{config.YT_KEYWORDS_MAX})")

    def _read_transcript(self, storyboard: Storyboard, output: Path, lang: str) -> str:
        """Concatenate a language's per-scene narration scripts in scene order."""
        parts = []
        for scene in storyboard.scenes:
            path = output / "scripts" / lang / f"{scene.basename}.txt"
            if path.exists():
                text = path.read_text(encoding="utf-8").strip()
                if text:
                    parts.append(text)
            elif scene.narration.get(lang, "").strip():
                parts.append(scene.narration[lang].strip())
        return "\n\n".join(parts)
