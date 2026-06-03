"""Checking that every external tool the build needs is available.

`DependencyChecker` verifies the Python packages we import and the command-line
tools we shell out to, auto-installing the pip ones into the project ``.venv``
when it can, and printing a clear "install this" message (then exiting) for the
system tools it can't.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from . import config
from .ai_client import create_ai_client


class DependencyChecker:
    """Validates Python packages, CLI tools, and (optionally) the AI CLI."""

    # (import name, pip name) for packages we import directly.
    PYTHON_PACKAGES = [
        ("yaml", "PyYAML"),
        ("srt", "srt"),
    ]

    def __init__(self) -> None:
        # Executables we shell out to. ``install_pip`` is a pip package name to
        # install into .venv, or None for a tool the user must install.
        self.binaries = [
            {"path": config.MANIM_BIN, "name": "manim", "install_pip": "manim"},
            {"path": config.EDGE_TTS_BIN, "name": "edge-tts", "install_pip": "edge-tts"},
            {"path": shutil.which("ffmpeg"), "name": "ffmpeg", "install_pip": None,
             "hint": "Install via the system package manager, e.g. `sudo apt install ffmpeg`."},
            {"path": shutil.which("ffprobe"), "name": "ffprobe", "install_pip": None,
             "hint": "Ships with ffmpeg; installing ffmpeg also provides ffprobe."},
        ]

    def check(self, need_ai_cli: Optional[str] = None) -> None:
        """Run every check; install what we can; exit with a list of what we can't."""
        print("Checking dependencies…")
        missing: List[str] = []
        self._check_python_packages(missing)
        self._check_binaries(missing)
        if need_ai_cli:
            self._check_ai_cli(need_ai_cli, missing)
        if missing:
            print("\nMissing dependencies — please install before re-running:")
            for item in missing:
                print(f"  - {item}")
            raise SystemExit(1)
        print("  all dependencies present.\n")

    # --- individual checks -------------------------------------------------

    def _check_python_packages(self, missing: List[str]) -> None:
        for import_name, pip_name in self.PYTHON_PACKAGES:
            try:
                __import__(import_name)
                continue
            except ImportError:
                print(f"  missing python package: {import_name} (pip: {pip_name})")
            if not self._pip_install(pip_name):
                missing.append(f"python package '{pip_name}' — install with "
                               f"`{config.VENV_BIN / 'pip'} install {pip_name}`")
                continue
            try:
                __import__(import_name)
            except ImportError:
                missing.append(f"python package '{pip_name}' — pip reported success "
                               "but import still fails")

    def _check_binaries(self, missing: List[str]) -> None:
        for binary in self.binaries:
            path = binary["path"]
            if path and Path(path).exists():
                continue
            if binary["install_pip"]:
                print(f"  missing binary: {binary['name']} "
                      f"(trying pip install {binary['install_pip']})")
                if self._pip_install(binary["install_pip"]):
                    continue
                missing.append(f"{binary['name']} — pip install failed; try "
                               f"`{config.VENV_BIN / 'pip'} install {binary['install_pip']}`")
            else:
                missing.append(f"{binary['name']} not found on PATH. "
                               f"{binary.get('hint', '')}".strip())

    def _check_ai_cli(self, name: str, missing: List[str]) -> None:
        # Reuse the AiClient's own "where do I live?" logic.
        client = create_ai_client(name)
        if client.locate_binary() is None:
            missing.append(client._not_found_message())

    def _pip_install(self, pip_name: str) -> bool:
        pip = config.VENV_BIN / "pip"
        if not pip.exists():
            return False
        print(f"  installing {pip_name} into {config.VENV_BIN.parent}…")
        proc = subprocess.run([str(pip), "install", "--quiet", pip_name],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"  pip install {pip_name} failed: "
                  f"{proc.stderr.strip() or proc.stdout.strip()}")
            return False
        return True
