"""Project-wide configuration: filesystem paths and default values.

Everything here is a plain constant — no behaviour. Keeping the "magic values"
(where files live, which voice/model to use by default) in one place means the
rest of the code never hard-codes a path or a default, and a change is a
one-line edit here.

Layout on disk::

    short_video_generator/        <- REPO_ROOT
    ├── .venv/                     <- VENV_DIR (auto-created on first run)
    └── video_generator/           <- GENERATOR_ROOT
        ├── generate_video.py       <- thin entry point
        ├── templates/              <- TEMPLATES_DIR (_common.py, fonts, skeleton)
        └── vgen/                   <- this package
"""

from __future__ import annotations

from pathlib import Path

# --- Filesystem paths ------------------------------------------------------
# `__file__` is .../video_generator/vgen/config.py, so two parents up is the
# generator root and three parents up is the repository root.
GENERATOR_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = GENERATOR_ROOT / "templates"
REPO_ROOT = GENERATOR_ROOT.parent
REQUIREMENTS = GENERATOR_ROOT / "requirements.txt"

# A project-local virtual environment at the repo root. The bootstrap step
# creates it on first run and re-execs the program inside it (see bootstrap.py),
# so the program never depends on a system or ~/venv interpreter.
VENV_DIR = REPO_ROOT / ".venv"
VENV_BIN = VENV_DIR / "bin"
PYTHON_BIN = VENV_BIN / "python"
MANIM_BIN = VENV_BIN / "manim"
EDGE_TTS_BIN = VENV_BIN / "edge-tts"

# Environment variable used as a "already inside the venv" marker so the
# bootstrap re-exec does not loop forever.
VENV_MARK = "VIDEO_GENERATOR_VENV"

# --- Default voices / models -----------------------------------------------
# Used when the storyboard's `voices:` map omits a language, or when a
# provider/voice/model isn't pinned on the command line.
DEFAULT_EDGE_VOICE = "id-ID-ArdiNeural"
DEFAULT_GEMINI_VOICE = "Iapetus"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-preview-tts"

# Default Claude model + effort tier for narration / scene generation. Opus at
# the top ("max") effort gives the best layout-aware scene code.
DEFAULT_CLAUDE_MODEL = "claude-opus-4-8"
DEFAULT_CLAUDE_EFFORT = "max"

# Codex CLI: maximum reasoning effort ("high") = max capacity. The model is left
# to codex's own default for the signed-in account, because ChatGPT-account
# logins reject an explicit 'gpt-5-codex' (that id needs API access). Set
# DEFAULT_CODEX_MODEL to pin a specific model only if your account supports it.
DEFAULT_CODEX_MODEL = None
DEFAULT_CODEX_REASONING = "high"

# Google Generative Language endpoint for Gemini text-to-speech.
GEMINI_TTS_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

# Whole-video duration cap used when the storyboard doesn't set its own
# (max_duration / max_scene_duration). "Strictly 3 minutes."
DEFAULT_DURATION_CAP_SECONDS = 180.0

# --- Narration timing ------------------------------------------------------
# Words-per-second used to *estimate* spoken time from a script before any
# audio is produced. The real Edge/Gemini rate is ~2.0-2.2, so 2.0 errs
# slightly long (safer for staying under a max-duration cap).
ESTIMATE_WORDS_PER_SECOND = 2.0

# --- Too-dense-scene escalation (split a scene into smaller ones) ----------
# Used when --validate-scenes is on. A scene is "too dense" when fitting it
# would require shrinking content below DENSITY_MIN_SCALE (i.e. unreadable) OR
# it shows >= 2 overflow/containment items at once. Such a scene is split in
# the storyboard after REPAIRS_BEFORE_SPLIT in-place repairs fail — but never
# into pieces shorter than MIN_CHILD_DURATION_SECONDS, and never more than
# MAX_SPLIT_ROUNDS times.
REPAIRS_BEFORE_SPLIT = 3
DENSITY_MIN_SCALE = 0.60
MAX_SPLIT_ROUNDS = 2
MIN_CHILD_DURATION_SECONDS = 7.0

# --- YouTube field limits --------------------------------------------------
YT_TITLE_MAX = 100
YT_DESC_MAX = 5000
YT_KEYWORDS_MAX = 500

# --- Output subdirectories that `--force` wipes ----------------------------
# Everything the generator itself creates under <output>. User-placed files
# (a README, .gitignore, ...) are left untouched.
WIPE_SUBDIRS = (
    "scripts", "audio", "subtitles", "video", "clips", "final",
    "scenes_landscape", "scenes_portrait", "manim_media", "manim_check",
    "assets", "youtube",
)
