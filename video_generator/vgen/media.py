"""Helpers for inspecting media files and deciding what needs rebuilding.

These shell out to ``ffprobe`` (part of ffmpeg) or just compare file
timestamps. They are free functions for the same reason as the text helpers:
no state, easy to test.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def ffprobe_duration(path: Path) -> float:
    """Return the duration of an audio/video file in seconds (via ffprobe)."""
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1",
        str(path),
    ])
    return float(out.strip())


def valid_audio(mp3: Path) -> bool:
    """True only if ``mp3`` exists, is non-empty, and decodes to a real length.

    This guards the "skip if already done" checks against the 0-byte or
    truncated file an interrupted text-to-speech run can leave behind (which
    ffprobe would later choke on).
    """
    try:
        if not mp3.exists() or mp3.stat().st_size == 0:
            return False
        return ffprobe_duration(mp3) > 0
    except (subprocess.CalledProcessError, ValueError, OSError):
        return False


def is_up_to_date(dest: Path, *sources: Path) -> bool:
    """True if ``dest`` exists and is at least as new as every source that exists.

    This drives incremental rebuilds: a regenerated scene file (or refreshed
    template, or re-narrated audio) is *newer* than the clip derived from it, so
    the stale clip is no longer skipped. Sources that don't exist are ignored.
    """
    if not dest.exists():
        return False
    dest_mtime = dest.stat().st_mtime
    return all(
        (not src.exists()) or src.stat().st_mtime <= dest_mtime
        for src in sources
    )
