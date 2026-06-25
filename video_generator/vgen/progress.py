"""Progress logging with elapsed time.

`ProgressLogger` prints lines prefixed with ``[MM:SS]`` counted from when the
build started, so the time each step takes is visible as the gap between
lines. A single shared instance, `progress`, is imported across the package —
that keeps the call sites short (``progress.log("...")``) while still being a
real object you could create a second of (e.g. in a test).
"""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from typing import Iterator


class ProgressLogger:
    """Stopwatch-style console logger."""

    def __init__(self) -> None:
        self._start = time.monotonic()
        # Stages run their per-scene work on a thread pool; the lock keeps
        # concurrent log lines from interleaving mid-string.
        self._lock = threading.Lock()

    def reset(self) -> None:
        """Restart the stopwatch (called once at the beginning of a build)."""
        self._start = time.monotonic()

    def elapsed(self) -> float:
        """Seconds since the last :meth:`reset`."""
        return time.monotonic() - self._start

    def clock(self) -> str:
        """The elapsed time formatted as ``MM:SS``."""
        seconds = int(self.elapsed())
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def log(self, message: str) -> None:
        """Print one progress line prefixed with the elapsed clock (thread-safe)."""
        with self._lock:
            print(f"[{self.clock()}] {message}", flush=True)

    @contextmanager
    def stage(self, label: str) -> Iterator[None]:
        """Wrap a pipeline stage so its header and duration are logged.

        Usage::

            with progress.stage("[2/8] generate audio"):
                ...do the work...
        """
        self.log(label)
        start = time.monotonic()
        yield
        # Strip the "[n/8] " numbering from the closing line for a tidy summary.
        name = label.split("] ", 1)[-1]
        self.log(f"  ✓ {name} in {time.monotonic() - start:.1f}s")


# The shared logger used throughout the package.
progress = ProgressLogger()
