"""Text-to-speech engines — a second Strategy hierarchy.

A scene's narration can be voiced by either **Edge TTS** (free, no key, exact
word timings) or **Gemini TTS** (an API key, nicer voices, *estimated*
subtitles). They produce the same outputs — an ``.mp3`` and a ``.srt`` per
scene per language — but get there very differently, so each is a strategy:

    TtsEngine (abstract)
      ├── EdgeTtsEngine     <- shells out to the `edge-tts` CLI, retries on
      │                        flaky network errors
      └── GeminiTtsEngine   <- calls a REST API, decodes PCM -> MP3 with ffmpeg,
                               and estimates the subtitle timing

The pipeline only knows about :meth:`TtsEngine.synthesize_storyboard`; the
``create_tts_engine`` factory picks the concrete class from the storyboard.
The base class provides the shared loop (the *template method*); subclasses
fill in the one-clip behaviour and an optional ``prepare`` step.
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple

from . import config
from .media import valid_audio, ffprobe_duration
from .progress import progress
from .subtitles import write_estimated_srt


# =====================================================================
# Shared: resolving the Gemini API key (used by the engine + the CLI check)
# =====================================================================

def resolve_gemini_key(storyboard) -> Optional[str]:
    """Find the Gemini API key, or ``None``.

    Order of precedence: the storyboard / CLI override, then the
    ``GEMINI_API_KEY`` environment variable, then a ``.env`` file at the repo
    root. Reads ``config.REPO_ROOT`` by attribute (not a local copy) so tests
    can point it at a temporary directory.
    """
    import os
    if storyboard.gemini_api_key:
        return storyboard.gemini_api_key
    env_value = os.environ.get("GEMINI_API_KEY")
    if env_value:
        return env_value
    env_file = config.REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            if key.strip() == "GEMINI_API_KEY":
                return val.strip().strip('"').strip("'")
    return None


# =====================================================================
# The Strategy interface
# =====================================================================

class TtsEngine(ABC):
    """The interface the pipeline uses to turn narration into audio + subtitles."""

    #: storyboard ``tts_provider`` value / log label.
    name: str = ""
    #: voice used when neither the storyboard nor the per-language map has one.
    default_voice: str = ""
    #: per-language default voices (overrides ``default_voice`` for that language).
    default_voices: dict = {}

    def voice_for(self, storyboard, lang: str) -> str:
        """The voice for a language: the storyboard's, else this engine's
        per-language default, else the generic fallback."""
        return (storyboard.voices.get(lang)
                or self.default_voices.get(lang)
                or self.default_voice)

    def prepare(self, storyboard) -> None:
        """Hook run once before synthesising (e.g. check a tool / key). No-op by default."""

    def synthesize_storyboard(self, storyboard, output: Path, force: bool) -> None:
        """Template method: produce an mp3 + srt for every (language, scene).

        The loop, the "skip what's already done" check and the logging are the
        same for every engine; only :meth:`synthesize_one` differs.
        """
        self.prepare(storyboard)
        for lang in storyboard.languages:
            voice = self.voice_for(storyboard, lang)
            audio_dir = output / "audio" / lang
            srt_dir = output / "subtitles" / lang
            audio_dir.mkdir(parents=True, exist_ok=True)
            srt_dir.mkdir(parents=True, exist_ok=True)
            for scene in storyboard.scenes:
                mp3 = audio_dir / f"{scene.basename}.mp3"
                srt = srt_dir / f"{scene.basename}.srt"
                if valid_audio(mp3) and srt.exists() and not force:
                    continue
                progress.log(f"  {self.name} {voice} -> {lang}/{scene.basename}…")
                started = time.monotonic()
                self.synthesize_one(scene.narration[lang], voice, mp3, srt)
                progress.log(f"    ↳ {lang}/{scene.basename}.mp3 in "
                             f"{time.monotonic() - started:.1f}s")

    @abstractmethod
    def synthesize_one(self, text: str, voice: str, mp3: Path, srt: Path) -> None:
        """Produce one scene's mp3 + srt from its narration text."""


# =====================================================================
# Edge TTS
# =====================================================================

# Substrings that mark a *transient* edge-tts failure worth retrying (DNS /
# connection drops to speech.platform.bing.com), as opposed to a real error
# like a bad voice name.
_EDGE_TRANSIENT = (
    "name resolution", "getaddrinfo", "Cannot connect to host", "ClientConnector",
    "TimeoutError", "Connection reset", "ServerDisconnected", "Temporary failure",
)


class EdgeTtsEngine(TtsEngine):
    """Microsoft Edge online voices, via the ``edge-tts`` command-line tool."""

    name = "edge-tts"
    default_voice = config.DEFAULT_EDGE_VOICE
    default_voices = config.DEFAULT_EDGE_VOICES

    def prepare(self, storyboard) -> None:
        if not config.EDGE_TTS_BIN.exists():
            raise SystemExit(f"edge-tts not found at {config.EDGE_TTS_BIN}")

    def synthesize_one(self, text: str, voice: str, mp3: Path, srt: Path) -> None:
        self.synthesize_clip(voice, text, mp3, srt)

    def synthesize_clip(self, voice: str, text: str, mp3: Path, srt: Path,
                        retries: int = 3, wait: float = 3.0) -> None:
        """Run edge-tts for one clip, retrying transient network failures with
        exponential backoff. A non-network failure (e.g. a bad voice) fails fast.
        """
        attempts = retries + 1
        for attempt in range(1, attempts + 1):
            proc = subprocess.run(
                [str(config.EDGE_TTS_BIN), "--voice", voice, "--text", text,
                 "--write-media", str(mp3), "--write-subtitles", str(srt)],
                capture_output=True, text=True,
            )
            if proc.returncode == 0:
                return
            mp3.unlink(missing_ok=True)   # drop any partial output before retry
            srt.unlink(missing_ok=True)
            err = (proc.stderr or proc.stdout or "").strip()
            transient = any(s in err for s in _EDGE_TRANSIENT)
            if attempt >= attempts or not transient:
                hint = ("\nThis looks like a network problem reaching Edge TTS "
                        "(speech.platform.bing.com). Check connectivity and re-run "
                        "— already-generated audio is cached, so it resumes."
                        if transient else "")
                raise SystemExit(
                    f"edge-tts failed for {mp3.name} after {attempt} attempt(s): "
                    f"{err[-200:]}{hint}"
                )
            delay = wait * (2 ** (attempt - 1))
            progress.log(f"    edge-tts network error, retry {attempt}/{attempts} "
                         f"(waiting {delay:.0f}s)…")
            time.sleep(delay)


# =====================================================================
# Gemini TTS
# =====================================================================

class GeminiQuotaError(RuntimeError):
    """Raised on a 429 *daily* quota exhaustion — not retryable within a run
    (the per-day limit only resets on a daily boundary)."""


def gemini_error_message(detail: str) -> str:
    """Pull a concise message out of a Gemini error body, or truncate the blob."""
    try:
        return str(json.loads(detail)["error"]["message"]).strip()[:240]
    except (ValueError, KeyError, TypeError):
        return " ".join(detail.split())[:240]


def is_daily_quota(detail: str) -> bool:
    """True when a 429 body names a *per-day* quota (which can't recover soon)."""
    normalised = re.sub(r"[\s_]+", "", detail.lower())
    return "perday" in normalised


def request_gemini_audio(text: str, api_key: str, model: str, voice: str,
                         timeout: float) -> Tuple[bytes, int]:
    """Call the Gemini TTS endpoint; return ``(pcm_s16le_bytes, sample_rate)``.

    Uses only the standard library (``urllib``) — no extra dependency. Raises
    :class:`GeminiQuotaError` on a daily-quota 429, ``RuntimeError`` otherwise.
    """
    body = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}
            },
        },
    }
    request = urllib.request.Request(
        config.GEMINI_TTS_ENDPOINT.format(model=model),
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        message = gemini_error_message(detail)
        if exc.code == 429 and is_daily_quota(detail):
            raise GeminiQuotaError(message) from exc
        raise RuntimeError(f"gemini HTTP {exc.code}: {message}") from exc
    try:
        inline = data["candidates"][0]["content"]["parts"][0]["inlineData"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"gemini: no audio in response: {str(data)[:400]}") from exc
    pcm = base64.b64decode(inline["data"])
    rate = 24000
    for token in inline.get("mimeType", "").split(";"):
        if "rate=" in token:
            try:
                rate = int(token.split("rate=")[1])
            except ValueError:
                pass
    return pcm, rate


def write_gemini_clip(text: str, mp3: Path, srt: Path, api_key: str, model: str,
                      voice: str, timeout: float) -> None:
    """Request audio, pipe the PCM through ffmpeg to MP3, and write an SRT."""
    pcm, rate = request_gemini_audio(text, api_key, model, voice, timeout)
    if not pcm:
        raise RuntimeError("gemini produced 0-byte audio")
    tmp_mp3 = mp3.with_suffix(mp3.suffix + ".part")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", "pipe:0",
             "-c:a", "libmp3lame", "-q:a", "2", "-f", "mp3", str(tmp_mp3)],
            input=pcm, check=True,
        )
        if tmp_mp3.stat().st_size == 0:
            raise RuntimeError("ffmpeg produced 0-byte mp3")
        tmp_mp3.replace(mp3)            # atomic rename only once it's complete
    except BaseException:
        tmp_mp3.unlink(missing_ok=True)
        raise
    write_estimated_srt(text, ffprobe_duration(mp3), srt)


class GeminiTtsEngine(TtsEngine):
    """Google Gemini voices over the REST API (PCM audio + estimated subtitles)."""

    name = "gemini"
    default_voice = config.DEFAULT_GEMINI_VOICE

    def __init__(self, model: str = config.DEFAULT_GEMINI_MODEL,
                 retries: int = 2, wait: float = 5.0, timeout: float = 180.0) -> None:
        self.model = model
        self.retries = retries
        self.wait = wait
        self.timeout = timeout
        self._api_key: Optional[str] = None

    def prepare(self, storyboard) -> None:
        self._api_key = resolve_gemini_key(storyboard)
        if not self._api_key:
            raise SystemExit(
                "gemini TTS requires an API key. Set GEMINI_API_KEY in the "
                "environment or in a .env at the repo root, set `gemini_api_key:` "
                "in the storyboard front-matter, or pass --gemini-api-key."
            )

    def synthesize_one(self, text: str, voice: str, mp3: Path, srt: Path) -> None:
        attempts = self.retries + 1
        for attempt in range(1, attempts + 1):
            try:
                write_gemini_clip(text, mp3, srt, self._api_key, self.model,
                                  voice, self.timeout)
                return
            except GeminiQuotaError as exc:
                # A per-day quota won't recover in seconds — stop now with
                # actionable advice instead of burning retries.
                raise SystemExit(
                    f"Gemini daily quota exhausted: {exc}\n"
                    f"The free tier caps the preview TTS model ({self.model}) at a "
                    "low number of requests/day. Options:\n"
                    "  • finish now for free with  --tts edge\n"
                    "  • re-run after the daily quota resets — cached audio resumes\n"
                    "  • if you enabled billing, confirm the GEMINI_API_KEY in .env "
                    "belongs to the billed project."
                )
            except BaseException as exc:  # noqa: BLE001
                if attempt >= attempts:
                    raise SystemExit(
                        f"gemini TTS failed after {attempts} attempts: {str(exc)[:160]}"
                    )
                delay = self.wait * (2 ** (attempt - 1))   # exponential backoff
                progress.log(f"    retry {attempt}/{attempts} ({type(exc).__name__}: "
                             f"{str(exc)[:120]}); waiting {delay:.0f}s…")
                time.sleep(delay)


# =====================================================================
# Factory
# =====================================================================

# Legacy aliases kept for back-compat with older storyboards.
GEMINI_ALIASES = {"gemini", "google", "google_chirp", "chirp"}


def create_tts_engine(storyboard) -> TtsEngine:
    """Factory: build the :class:`TtsEngine` for a storyboard's ``tts_provider``."""
    provider = storyboard.tts_provider
    if provider == "edge":
        return EdgeTtsEngine()
    if provider in GEMINI_ALIASES:
        return GeminiTtsEngine(model=storyboard.gemini_model)
    raise SystemExit(f"Unknown tts_provider '{provider}'.")
