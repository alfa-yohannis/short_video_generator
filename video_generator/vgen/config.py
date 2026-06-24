"""Project-wide configuration: filesystem paths and default values.

Everything here is a plain constant — no behaviour. Keeping the "magic values"
(where files live, which voice/model to use by default) in one place means the
rest of the code never hard-codes a path or a default, and a change is a
one-line edit here.

Layout on disk::

    short_video_generator/        <- REPO_ROOT
    ├── .venv/                     <- VENV_DIR (auto-created on first run)
    ├── templates/                 <- USER_TEMPLATES_DIR (project-local templates)
    ├── subjects/                  <- SUBJECTS_DIR (subject packs)
    ├── profiles/                  <- PROFILES_DIR (preparation profiles)
    └── video_generator/           <- GENERATOR_ROOT
        ├── generate_video.py       <- thin entry point
        ├── templates/              <- TEMPLATES_DIR (bundled templates, fonts, skeleton)
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

# Project-local presentation templates live at the repo root (``templates/<name>/``),
# the same drop-in-a-folder model as ``subjects/`` and ``profiles/``. A template
# here wins over a bundled one of the same name, so you can override ``default``
# or add a brand-new look (e.g. a dark code theme) with no code change. See
# vgen/scenes.py:resolve_template_dir.
USER_TEMPLATES_DIR = REPO_ROOT / "templates"

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
DEFAULT_EDGE_VOICE = "id-ID-ArdiNeural"          # generic fallback for unknown langs
# Per-language Edge defaults, so English narration isn't voiced by the Indonesian
# default when the storyboard omits a `voices:` map.
DEFAULT_EDGE_VOICES = {
    "id": "id-ID-ArdiNeural",
    "en": "en-US-AndrewNeural",
}
DEFAULT_GEMINI_VOICE = "Iapetus"                 # multilingual — one voice covers both
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-preview-tts"

# Gemini TTS voice-consistency knobs. Each scene is voiced by a SEPARATE Gemini
# call, so by default the model freshly samples every clip and the voice can
# drift between scenes — most visibly the male Iapetus voice occasionally coming
# out higher/feminine. A style preamble pins ONE narrator persona: it is prepended
# to the narration as a natural-language delivery instruction (applied to the
# performance, not read aloud). Set it to "" to disable, or edit the persona/pace.
#
# Temperature: the format/placement (generationConfig.temperature, a number) is
# fine, but gemini-2.5-flash-preview-tts only tolerates the UPPER part of the
# 0.0–2.0 range. Empirically (id narration, Iapetus) the cliff is sharp and sits
# between 0.55 and 0.60: values ≤ 0.55 hang / return `finishReason: OTHER` with NO
# audio — so every clip exhausts its retries and falls back to Edge (the old 0.1
# caused exactly that "Gemini doesn't work"). 0.60 works (tested 3/3) and up.
# 0.60 is the lowest usable value but sits right at the edge; 1.0 keeps a safe
# margin above the cliff (the conventional default) at a small cost to voice
# consistency, which the style preamble below largely covers. Do NOT go ≤ 0.55.
GEMINI_TTS_TEMPERATURE = 1.5
GEMINI_TTS_STYLE = (
    "Narrate in a calm, clear, professional male voice with a warm, even tone "
    "and a brisk, lively pace — a little faster than average but never rushed — "
    "keeping exactly the same voice from start to finish"
)

# Friendly `voice: male|female` aliases for the simplified storyboard format,
# resolved per language for the Edge engine. Gemini voices aren't gendered here,
# so `voice: male|female` with gemini falls back to the Gemini default.
EDGE_VOICES_BY_GENDER = {
    "male":   {"id": "id-ID-ArdiNeural",  "en": "en-US-GuyNeural"},
    "female": {"id": "id-ID-GadisNeural", "en": "en-US-JennyNeural"},
}

# Default Claude model + effort tier for narration / scene generation. Opus at
# "high" effort gives strong layout-aware scene code; bump to "max" if you want
# the top reasoning tier at extra latency/cost.
DEFAULT_CLAUDE_MODEL = "claude-opus-4-8"
DEFAULT_CLAUDE_EFFORT = "high"

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

# Whole-video duration floor/cap. The floor is enforced for every parsed
# storyboard; the cap is used when the storyboard doesn't set its own
# (max_duration / max_scene_duration). "Strictly 2-3 minutes."
DEFAULT_DURATION_FLOOR_SECONDS = 120.0
DEFAULT_DURATION_CAP_SECONDS = 180.0

# A short hold at the END of every scene's muxed clip — the last frame is frozen
# for this many seconds (with matching silence) so viewers get a beat to digest the
# scene before the next one starts. Applied in ClipAssembler.mux (no Manim re-render
# needed). Set to 0 to disable. The merged SRT offsets follow the clip length, so
# subtitles stay aligned and no cue runs over the silent tail.
SCENE_TAIL_PAD_SECONDS = 1.0

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

# --- Preparation step ------------------------------------------------------
# How long the agentic ``--run-preparation`` pass (fetch reference symbols via a
# profile's MCP server) may run before it is killed and the build falls back to
# Manim primitives.
PREPARATION_TIMEOUT_SECONDS = 900.0

# Preparation profiles live as YAML files here (repo-root ``profiles/``); the
# storyboard's ``preparation_profile:`` key selects one. See vgen/preparation.py.
PROFILES_DIR = REPO_ROOT / "profiles"

# Subject packs live as folders here (repo-root ``subjects/<name>/``); the
# storyboard's ``subject:`` key selects one. A pack bundles the scene-render
# helpers, the scene-prompt guidance, and the bulk-driver storyboard prompt /
# exemplar / naming / flags for one teaching subject. See vgen/subjects.py.
SUBJECTS_DIR = REPO_ROOT / "subjects"

# The presentation TEMPLATE — the _core scaffold (palette, top bar, background,
# typography, helpers) plus its orientation deltas — is a folder
# ``templates/<name>/`` holding _core.py + _landscape.py + _portrait.py. A
# storyboard's ``template:`` key (or a subject pack's ``template:``) selects one,
# defaulting to ``default``. It is resolved by searching the repo-root
# ``templates/`` (USER_TEMPLATES_DIR) first, then the bundled TEMPLATES_DIR, so a
# project-local template overrides a bundled one. See
# vgen/scenes.py:resolve_template_dir / materialize_dir.
DEFAULT_TEMPLATE = "default"

# --- YouTube field limits --------------------------------------------------
YT_TITLE_MAX = 100
YT_DESC_MAX = 5000
YT_KEYWORDS_MAX = 500

# --- Output subdirectories that `--force` wipes ----------------------------
# Everything the generator itself creates under <output>. User-placed files
# (a README, .gitignore, ...) are left untouched.
WIPE_SUBDIRS = (
    "scripts", "audio", "video", "clips", "final",
    "scenes_landscape", "scenes_portrait", "manim_media", "manim_check",
    "assets",
)
