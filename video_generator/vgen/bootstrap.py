"""Self-bootstrapping into a project-local virtual environment.

On first run there is no ``.venv`` yet, so :func:`bootstrap_venv` creates one at
the repository root, installs the Python dependencies into it, and then
re-launches the program using that interpreter. A marker environment variable
stops the re-launch from looping. After this returns, the program is always
running inside ``.venv`` — so the lazy ``import yaml`` / ``srt`` and the
``manim`` / ``edge-tts`` console scripts all resolve locally.

This is kept deliberately separate and dependency-free so it can run *before*
any third-party package is importable.
"""

from __future__ import annotations

import os
import subprocess
import sys

from . import config


def bootstrap_venv() -> None:
    """Create ``.venv`` if needed, install deps, and re-exec inside it."""
    if os.environ.get(config.VENV_MARK) == "1":
        return  # already inside the venv — nothing to do

    is_fresh = not config.VENV_DIR.exists()
    if is_fresh:
        print(f"[setup] creating virtual environment at {config.VENV_DIR}")
        subprocess.check_call([sys.executable, "-m", "venv", str(config.VENV_DIR)])

    pip = config.VENV_BIN / "pip"
    python = config.VENV_BIN / "python"
    if not pip.exists():
        sys.exit(f"[setup] venv looks broken; missing {pip}. "
                 f"Delete {config.VENV_DIR} and re-run.")

    if is_fresh:
        print("[setup] installing dependencies (PyYAML, srt, manim, edge-tts)…")
        subprocess.check_call([str(pip), "install", "-q", "--upgrade", "pip"])
        if config.REQUIREMENTS.exists():
            subprocess.check_call([str(pip), "install", "-q", "-r", str(config.REQUIREMENTS)])
        else:
            subprocess.check_call([str(pip), "install", "-q",
                                   "PyYAML", "srt", "manim", "edge-tts"])

    # Re-exec this program with the venv's interpreter; the marker stops a loop.
    env = os.environ.copy()
    env[config.VENV_MARK] = "1"
    entry = config.GENERATOR_ROOT / "generate_video.py"
    os.execvpe(str(python), [str(python), str(entry), *sys.argv[1:]], env)
