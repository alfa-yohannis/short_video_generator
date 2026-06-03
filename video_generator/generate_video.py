#!/usr/bin/env python3
"""Generate a bilingual Manim tutorial video from a storyboard markdown file.

This file is just the entry point. The implementation lives in the ``vgen``
package next to it (see ``vgen/__init__.py`` for a map). On first run it
bootstraps a project-local ``.venv`` and re-execs itself inside it, then hands
off to the command-line interface.

    python3 video_generator/generate_video.py \
        --storyboard storyboards/singleton_pattern_storyboard.md \
        --output build/singleton
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the sibling ``vgen`` package importable when this file is run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from vgen.bootstrap import bootstrap_venv

# Create/enter the project-local virtual environment. This may re-exec the
# program and therefore not return; everything below runs inside ``.venv``.
bootstrap_venv()

from vgen.cli import main

if __name__ == "__main__":
    main()
