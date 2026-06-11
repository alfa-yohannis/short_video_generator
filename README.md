# Short Video Generator

Turn a single storyboard markdown file into a finished, **bilingual** (Indonesian
+ English) Manim tutorial video — in both **landscape** and **portrait** — with
narration, spoken audio, and synchronized subtitles, end to end.

Two CLI arguments drive the whole thing: the storyboard file and an output
directory. Every intermediate artifact (narration scripts, audio, raw renders,
muxed clips, final videos, subtitles) lands under the output directory.

```
storyboard.md ─▶ narration scripts (Claude | Codex) ─▶ MP3 + SRT (Edge | Gemini TTS)
   ─▶ Manim scene .py (Claude | Codex when missing) ─▶ rendered MP4 (landscape + portrait)
   ─▶ per-scene clips (ffmpeg mux) ─▶ concatenated MP4 + merged SRT
```

The storyboard intentionally contains **no narration text and no Manim scene
code** — just a description per scene. When narration or a scene `.py` file is
missing, the configured AI CLI writes it from the description. Both the narrator
and the TTS engine are swappable.

---

## Features

- **One storyboard in, narrated videos out** — landscape *and* portrait from the
  same scene sources, so the result doubles as long-form and Reels/Shorts/TikTok.
  Generate both (default) or just one with `--orientation {landscape,portrait}`.
- **Bilingual** — Indonesian + English narration, audio, and subtitles in one run.
- **Swappable narrator** — Claude Code (default, reuses your `claude` session, no
  API key) or the Codex CLI (`--ai-cli codex`). Used to write missing narration
  *and* missing Manim scene files from each scene's description. Claude runs Opus
  at `high` reasoning effort by default — raise it with `--effort max`.
- **Swappable TTS** — free Microsoft **Edge TTS** (default, no key, exact subtitle
  timing, default voice `id-ID-ArdiNeural`) or Google **Gemini TTS**
  (`--tts gemini`, nicer voices, needs an API key, estimated subtitle timing,
  default voice `Iapetus`).
- **Per-run voice selection** — `--voice` overrides the voice for every language,
  or set per-language voices in the storyboard's `voices:` map.
- **Robust AI scene generation** — generated Manim sources are Pango-escaped
  (bare `&` → `&amp;`) and `ast.parse()`-checked before they hit disk, so a
  malformed scene fails at generation time, not six scenes into a render.
- **Self-bootstrapping** — first run creates a project-local `.venv` at the repo
  root, installs its Python deps (PyYAML, srt, manim, edge-tts), and re-execs
  inside it. Launch it with any Python 3.
- **Resumable** — every stage skips artifacts that already exist; re-run anytime,
  or run a single stage with `--stage` and a single scene with `--only`.
- **Bring your own Manim sources** — point `scenes_*_dir` at hand-authored scenes
  to skip AI scene generation entirely.

---

## Requirements

### System tools (must be on your `PATH`)

| Tool | Provides | Needed for | Install (Debian/Ubuntu) |
|------|----------|------------|--------------------------|
| `ffmpeg`, `ffprobe` | video/audio encoding & probing | **always** | `sudo apt install ffmpeg` |
| `claude` | narration / scene generation | default AI CLI | [Claude Code](https://claude.com/claude-code) |
| `codex` | narration / scene generation | `--ai-cli codex` | `npm install -g @openai/codex` |

`manim` and `edge-tts` are **not** system tools here — they are Python packages
installed automatically into the project-local `.venv` (see below).

### Python

- **Python 3.10+** to launch the script (it self-bootstraps the rest).
- **Runtime deps** — `PyYAML`, `srt`, `manim`, `edge-tts`, listed in
  [`video_generator/requirements.txt`](video_generator/requirements.txt) and
  installed **automatically** into `.venv` on first run. You don't install them
  yourself.
- **Gemini TTS** (`--tts gemini`) needs **no extra Python package** — it calls
  the REST API over the standard library and pipes audio through `ffmpeg`.

### Credentials / accounts

| For | What you need | How to set it |
|-----|---------------|---------------|
| Claude narrator (default) | A logged-in Claude Code session (no API key) | `claude` then `/login`, or `ANTHROPIC_API_KEY` |
| Codex narrator | A logged-in Codex CLI | `codex login` |
| Gemini TTS | A Gemini API key | `GEMINI_API_KEY` env var, a `.env` at the repo root, or `--gemini-api-key` |

> Edge TTS (the default voice engine) needs **no key and no account**. A minimal
> run needs only `ffmpeg` + a logged-in `claude` (or pre-filled narration).

---

## Installation & setup

### 1. System tools

```bash
sudo apt update && sudo apt install -y ffmpeg
ffmpeg -version | head -1
```

### 2. Python dependencies (automatic)

There is **no manual install step**. The first time you run `generate_video.py`
it self-bootstraps:

1. Creates `.venv` at the repo root.
2. Installs `PyYAML`, `srt`, `manim`, `edge-tts` (from
   [`video_generator/requirements.txt`](video_generator/requirements.txt)).
3. Re-launches itself inside that `.venv`.

```bash
# Any Python 3 triggers the one-time bootstrap, then prints help:
python3 video_generator/generate_video.py --help
```

> If `.venv` ever breaks, just delete it — it's rebuilt on the next run:
> `rm -rf .venv`.

### 3. AI CLI — pick one

**Claude (default):** install [Claude Code](https://claude.com/claude-code) and
log in once:

```bash
claude            # then run /login, or export ANTHROPIC_API_KEY=sk-ant-...
echo "Reply OK" | claude -p     # verify it answers
```

**Codex (optional, for `--ai-cli codex`):**

```bash
npm install -g @openai/codex
codex login
```

> The CLI binary is located via `$CLAUDE_BIN` / `$CODEX_BIN`, then `PATH`, then
> `~/.local/bin/<cli>`. Pre-fill every narration + scene `.py` and pass
> `--no-ai-cli-check` to skip needing an AI CLI at all.

### 4. Gemini TTS key (optional, for `--tts gemini`)

Get a key from **[Google AI Studio](https://aistudio.google.com/apikey)**, then
provide it in any **one** of these ways:

```bash
# a) a .env at the repo root (auto-read; keep it gitignored)
echo 'GEMINI_API_KEY=YOUR_KEY_HERE' >> .env

# b) an environment variable
export GEMINI_API_KEY=YOUR_KEY_HERE

# c) pass it inline
python3 video_generator/generate_video.py ... --tts gemini --gemini-api-key YOUR_KEY_HERE
```

Resolution order: `--gemini-api-key` → `$GEMINI_API_KEY` → a `.env` at the repo
root. For security the key is **never** read from the storyboard. The preview TTS
model is rate-limited on the free tier; smoke-test a single scene with `--only`
first.

---

## Quick start

```bash
python3 video_generator/generate_video.py \
    --storyboard storyboards/pythagorean_theorem_storyboard.md \
    --output     /tmp/pythagorean_build
```

After it finishes:

```
/tmp/pythagorean_build/
├── scripts/{id,en}/<scene>.txt          ← narration text per language
├── audio/{id,en}/<scene>.mp3            ← TTS output
├── subtitles/{id,en}/<scene>.srt
├── scenes_landscape/                     ← _common.py + per-scene .py
├── scenes_portrait/
├── assets/fonts/                         ← copied from templates
├── manim_media/{id,en}/{landscape,portrait}/
├── video/{id,en}/{landscape,portrait}/<scene>.mp4
├── clips/{id,en}/{landscape,portrait}/<scene>.mp4
├── final/{id,en}/<title>_landscape.mp4
├── final/{id,en}/<title>_portrait.mp4
├── thumbnails/{id,en}_{landscape,portrait}.png  ← poster: first scene, last second
├── subtitles/{id,en}/<title>.srt         ← merged with proper timestamps
└── youtube/{id,en}/youtube.txt           ← title / description / keywords per language
```

---

## How it works (the stages)

Run everything (default) or just one stage with `--stage`:

| Stage | What it does |
| --- | --- |
| `scripts` | Fill in any missing narration via the AI CLI; write `scripts/<lang>/*.txt` |
| `audio`   | Run the TTS engine on each script; write `audio/<lang>/*.mp3` + per-scene `subtitles/<lang>/*.srt` |
| `scenes`  | Materialize `scenes_<orient>/_common.py` from templates and AI-generate any missing per-scene `.py` files |
| `render`  | Run Manim with `MANIM_LANG=<lang>` and `MANIM_AUDIO_DIR=<output>/audio` for each (lang, orientation) pair |
| `mux`     | Combine raw video + MP3 into per-scene clips at 48 kHz stereo AAC |
| `concat`  | Concat clips into `final/<lang>/<title>_<orient>.mp4` |
| `thumbnails` | Save a poster frame per (lang, orientation) — the first scene's last second — to `thumbnails/<lang>_<orient>.png` |
| `srt`     | Merge per-scene SRTs into `subtitles/<lang>/<title>.srt` with proper offsets |
| `youtube` | Ask the AI CLI for YouTube title/description/keywords per language; write `youtube/<lang>/youtube.txt` |
| `all`     | (default) all of the above, in order |

---

## Storyboard format

A storyboard is a plain **Markdown** file. The recommended (simplified) form is
just a title and one **`##` heading per scene** with the scene's description
written underneath. Narration text and the Manim scene `.py` files are
intentionally NOT in the storyboard — the AI CLI generates them from each
scene's description.

```markdown
---
# Everything in this front-matter is OPTIONAL (sensible defaults apply).
language: both           # id | en | both                        (default: both)
length: 2-3 minutes      # 3 minutes | 180 | 2:30 | 90s          (total length)
voice: default           # default | male | female | a voice id  (default: default)
# More options you can add:
#   orientation: both    # landscape | portrait | both
#   tts: edge            # edge | gemini      (gemini needs an API key)
#   ai: claude           # claude | codex
#   fps: 30
#   resolution: 1920x1080
---

# Strategy Pattern

A free-form project brief (everything before the first `##`). Code in Java.

## Introduction (~15s)
Show the title "Strategy Pattern". Explain swapping algorithms at runtime.

## The Problem (~25s)
A Checkout class with hardcoded if/else per shipping type...
```

Everything technical is **derived**: the scene's file name, its Manim class
name, fps, and resolution. The per-scene `(~Ns)` hint sets that scene's length
(optional; defaults to 15s). The document title comes from the `#` heading (or
the file name, or `title:`). Secrets are **never** read from the storyboard —
the Gemini key comes from `--gemini-api-key`, `$GEMINI_API_KEY`, or `.env`.

### Preparation block (optional)

A single `# Preparation` section may sit between the project brief and the first
`##` scene. It is a level-1 heading (`#`), **not** a scene: it has no `(~Ns)`
duration, is never rendered, and never counts toward the duration budget. Use it
to record one-time setup or reference-gathering the author should do *before*
drawing the scenes.

It works in two modes:

- **Context only (default).** The block's text is passed to the scene generator
  as authoritative context (so the visuals match the real notation), but no step
  in it is executed.
- **Executed (`--run-preparation`).** Before generating scenes, the block is run
  **agentically** — the AI CLI is launched with tools on and the MCP servers from
  `--mcp-config` (default: the repo-root `.mcp.json`) attached, so it actually
  carries the block out. What "carrying it out" means is set by a **preparation
  profile** (see below). Either way the agent saves files + a `manifest.json` under
  `<output>/assets/…`, and each generated scene is told their paths so it loads the
  **real artwork** via `SVGMobject(...)` / `ImageMobject(...)` instead of inventing
  shapes. Best-effort: if nothing usable is produced it logs a warning and the
  build falls back to Manim primitives. You'll see `[prep] …` lines while it runs
  and a `(+ N reference assets)` suffix on each `ai-generate …` line afterward.

#### Preparation profiles (`profiles/<name>.yaml`)

The executed behavior is a **profile**, chosen by the storyboard's
`preparation_profile:` front-matter key (default `generic`). Profiles are plain
YAML files in the repo-root [`profiles/`](profiles/) directory — **drop a
`profiles/<name>.yaml` in to add one, no code change.** A profile may declare:

| Field | Purpose |
|---|---|
| `assets_subdir` | Where under `<output>/` to save fetched files (e.g. `assets/archi`) |
| `mcp_server` + `launch` | An MCP server to ensure is up, and how to launch the app that serves it (with an optional preference to set first) |
| `prompt_specialization` | Extra, topic-specific instructions for the agent |
| `extra_tools` | Tool allowances beyond the base file/web set |

- **`generic`** (built-in default) — just runs the block agentically with the
  general file/web tools (plus every MCP server in `.mcp.json`) and saves whatever
  it produces under `assets/prep/`. Launches no app.
- **`archi`** ([`profiles/archi.yaml`](profiles/archi.yaml)) — connects to the
  **Archi MCP server**, working in an empty scratch model (the elements panel and
  render/export tools only work with a model open), then creates one element of
  each type and exports its symbol. **Archi is started for you**: if the MCP port
  is down, the profile sets the van Heerden plugin's *Auto-start on launch*
  preference and launches `Archi.sh` **with a fresh model file**
  ([`profiles/model.archimate`](profiles/model.archimate), copied to a scratch path
  so the repo copy stays pristine) via Archi's `openFile` launcher action — so a
  model is active the moment the server comes up, no GUI automation needed. Then it
  waits up to 60s for the port. Needs a graphical display — under headless/cron (no
  `DISPLAY`) start Archi yourself.

```markdown
# My Topic

A free-form project brief.

# Preparation
Before drawing any scene, gather the authentic notation instead of inventing it:
start the modelling tool, then collect each element's official symbol to use as
the visual reference.

## Introduction (~15s)
...
```

The enterprise-architecture generator (`auto_generate_ea.py`) emits a Preparation
block requiring the **real, original ArchiMate element icons/symbols** (never
invented shapes), sourced in order of preference: export them from
[Archi](https://www.archimatetool.com/)'s MCP server (the `archi` endpoint in
`.mcp.json`); else find the official symbol online; else draw it by hand,
preferring SVG and falling back to JPG. The software-pattern generator
(`auto_generate_patterns.py`) emits one that simply states no preparation is
needed (those tutorials are code-only).

### Legacy format (still fully supported)

The earlier, more explicit form keeps working unchanged — required front-matter,
`## Scene: <basename> / <ClassName>` headings, and `**file:**`,
`**fallback_duration:**`, `**class:**`, `### description`, `### narration.<lang>`,
`### notes` blocks:

```markdown
---
title: pythagorean_theorem
languages: [id, en]
orientations: [landscape, portrait]
tts_provider: edge
ai_cli: claude
---

## Scene: 01_pengantar / Pengantar

**file:** scene_01_pengantar.py
**fallback_duration:** 14

### description
Title card. Introduce the theorem by name...
```

You can mix styles, and any field a scene doesn't specify is derived. If
`narration.<lang>` is absent the AI CLI writes it; if a scene's `.py` file is
absent the AI CLI generates it from the description + narration + the embedded
`_common.py` helpers.

### Constraining total duration

The generator enforces a **2-minute minimum** by default. Set `min_duration` in
the front-matter to make that floor explicit or choose a different floor. Set
`max_duration` (e.g. `3 minutes`, `180`, `2:30`, `90s`) to cap the whole video
(`max_scene_duration` is an accepted alias and still means the whole-video
total). The duration range is enforced at three points:

1. **Parse time** — the sum of per-scene `fallback_duration` values must be ≥ the
   minimum and, when `max_duration` is set, ≤ the cap. Otherwise the build refuses
   before any AI/TTS/render cost.
2. **Before TTS (estimate)** — once narration text exists, the generator
   estimates each language's spoken time from the word count (~2 words/sec) and,
   if it's over the cap, asks the AI to **compress the over-long scenes** so the
   estimate fits — *before* spending a TTS pass.
3. **After TTS (measured)** — it then ffprobes the real per-scene audio and, if a
   language is still over, compresses the narration by the measured overshoot,
   drops the stale audio, and **re-synthesizes**. This is the accurate guarantee.

Narration is generated tightly (~1.9 words/sec, as a hard word limit) so it
usually fits on the first pass; steps 2–3 are the safety net. To leave more
headroom, trim the per-scene `fallback_duration` values. To satisfy the
2-minute floor, extend or add scenes until their `fallback_duration` values sum
to at least 120 seconds.

### Bringing your own Manim sources

Point at existing hand-authored scenes from the front-matter:

```yaml
scenes_landscape_dir: ../../manim_claude/scenes_landscape
scenes_portrait_dir:  ../../manim_claude/scenes_portrait
```

Paths resolve relative to the storyboard file. When `scenes_<orient>_dir` is
provided and exists, those files are used as-is and AI scene generation is
skipped entirely.

---

## Usage examples

```bash
# Default: Claude narrator + Edge TTS (free, no key)
python3 video_generator/generate_video.py --storyboard SB.md --output OUT

# Claude narrator + Gemini TTS, voice Iapetus
python3 video_generator/generate_video.py --storyboard SB.md --output OUT \
    --tts gemini --voice Iapetus

# Codex narrator instead of Claude
python3 video_generator/generate_video.py --storyboard SB.md --output OUT \
    --ai-cli codex

# Edge female voice override for every language
python3 video_generator/generate_video.py --storyboard SB.md --output OUT \
    --voice id-ID-GadisNeural

# Portrait only (Reels/Shorts/TikTok) — skips all landscape work
python3 video_generator/generate_video.py --storyboard SB.md --output OUT \
    --orientation portrait

# Smoke-test one scene's narration + audio only
python3 video_generator/generate_video.py --storyboard SB.md --output OUT \
    --stage audio --only 01_pengantar

# Force a clean rebuild from scratch
python3 video_generator/generate_video.py --storyboard SB.md --output OUT --force
```

---

## Command-line options

| Flag | Default | Description |
| --- | --- | --- |
| `--storyboard PATH` | *(required)* | Storyboard markdown file |
| `--output DIR` | *(required)* | Output directory (all intermediates go here) |
| `--stage STAGE` | `all` | One of `scripts`, `audio`, `scenes`, `render`, `mux`, `concat`, `srt`, `youtube`, or `all` |
| `--only SCENE…` | *(all)* | Restrict to a subset of scene basenames |
| `--force` | off | Wipe generator-owned subdirs and rebuild from a clean slate |
| `--ai-cli {claude,codex}` | `claude` | AI CLI for missing narration / scene `.py`. Overrides `ai_cli:` |
| `--effort {low,medium,high,xhigh,max}` | `high` | Reasoning effort for the **Claude** AI CLI (pass `max` for the top tier). Ignored when `--ai-cli codex` |
| `--tts {edge,gemini}` | *(front-matter)* | TTS provider. Overrides `tts_provider:` when set |
| `--voice NAME` | *(front-matter)* | Override the voice for every language this run |
| `--orientation {landscape,portrait,both}` | `both` | Which orientation(s) to generate. `landscape`/`portrait` restrict the whole run to one; `both` uses the storyboard's `orientations:` (itself defaulting to both) |
| `--gemini-api-key KEY` | *(env / .env)* | Gemini API key |
| `--check-layout {off,warn,strict,fit}` | `off` | At render time, check each scene's text for overflow/clipping, portrait caption-zone violations, and overlap. `warn` logs; `strict` fails the render; `fit` auto-scales/nudges overflowing text back inside the frame as it renders |
| `--repair-attempts N` (alias `--layout-repair-attempts`) | `2` | How many times to ask the AI CLI to fix a scene that fails to render — or fails `--check-layout strict` — then re-render, before giving up (`0` disables AI repair) |
| `--validate-scenes` | off | After generating each scene, render-check it (strict) and auto-refine it until it passes, *before* the real render |
| `--validate-attempts N` | `10` | With `--validate-scenes`, max refine attempts per failing scene before giving up |
| `--refine-storyboard` | off | Before building, let the AI rewrite an over-dense storyboard (trim/split/rebalance within the duration cap). Written to `<output>/storyboard.refined.md` — your original is untouched; if the plan changes, everything regenerates |
| `--run-preparation` | off | Execute the storyboard's `# Preparation` block agentically before generating scenes (tools on + MCP), per its `preparation_profile:` (a `profiles/<name>.yaml`; default `generic`). The `archi` profile fetches ArchiMate symbols into `<output>/assets/archi/`, auto-launching Archi if its port is down. Best-effort; falls back to primitives. See [Preparation block](#preparation-block-optional) |
| `--mcp-config PATH` | *(repo `.mcp.json`)* | `.mcp.json` the `--run-preparation` agent loads its MCP servers from |
| `--skip-youtube` | off | Don't generate `youtube/<lang>/youtube.txt` |
| `--skip-dep-check` | off | Skip the startup dependency validation |
| `--no-ai-cli-check` | off | Don't enforce AI CLI presence (every narration / scene `.py` pre-filled) |

> `--force` removes only generator-owned subdirectories under `--output`
> (`scripts/`, `audio/`, `subtitles/`, `video/`, `clips/`, `final/`,
> `scenes_landscape/`, `scenes_portrait/`, `manim_media/`, `assets/`). Files you
> placed there yourself (a `.gitignore`, a README, etc.) are left alone.

---

## How AI generation works

When a piece is missing, the generator shells out to the chosen CLI in
non-interactive `-p / --print` mode and pipes the prompt on stdin:

- **Narration prompt** — receives the project brief, scene description, fallback
  duration, and (if available) the narration in the other language. Returns plain
  narration text in the requested language.
- **Scene prompt** — receives the project brief, the `# Preparation` block (when
  present), any preparation-fetched reference symbols (with `--run-preparation`),
  the scene description, narration in both languages, the verbatim `_common.py`,
  and the `scene_skeleton.py` reference. Returns a complete Manim scene file.

These two run with **tools disabled** (`--tools ""`) so the CLI returns the file
text on stdout instead of acting like an agent. The one exception is the
**preparation pass** (`--run-preparation`): it runs the CLI *agentically* (tools
on, `--mcp-config` attached, `--allowedTools` pre-approving Bash/Read/Write/web +
`mcp__archi__*`) so the model can drive the Archi MCP server and write the fetched
symbol files itself. Its return text is just a summary — the real product is the
files it writes under `<output>/assets/archi/`.

Each AI-generated scene file is post-processed before it's written:

- **Pango-escape pass** — bare `&` in short string literals is rewritten to
  `&amp;` (unless it already starts a recognised entity like `&amp;`, `&lt;`,
  `&#…;`). The `_common.py` text helpers feed Pango `MarkupText`, which otherwise
  crashes on a raw ampersand. (Caveat: literals inside `code_card(...)` are
  escaped too, so pre-escape or base64 code samples that legitimately contain `&`.)
- **Syntax check** — the rewritten source is `ast.parse()`d before being written;
  a `SyntaxError` aborts the build with a file + line + column pointer.

### Claude authentication

The generator invokes `claude` with `-p --model <model> --effort <effort>
--tools '' --permission-mode bypassPermissions
--allow-dangerously-skip-permissions --disable-slash-commands` (model defaults
to `claude-opus-4-8`, effort to `high` — raise it with `--effort max`; `--tools
''` disables tools so Claude returns the file text instead of writing it
itself). It deliberately **does not** pass `--bare`, so the OAuth session from
`claude /login` is honored.

Authenticate either way:

1. **Interactive OAuth (desktop):** `claude /login`, then verify with
   `echo "Reply with just OK" | claude -p`.
2. **API key (headless / CI):** `export ANTHROPIC_API_KEY=sk-ant-...`.

> Common pitfall: if `claude /login` succeeded but the generator still says "Not
> logged in", you previously added `--bare`. Remove it; the current version omits
> it intentionally.

---

## Layout self-check

AI-generated scenes occasionally place text past the frame edge, stack two
labels on the same spot, spill text outside its panel, or (in portrait) drop
content into the caption zone. `--check-layout` turns on a render-time guard,
implemented in the scene `_common.py`. Detection runs **after every animation
step and at the end of every `Scene.render`**, so a violation that only exists
mid-scene (a callout that later fades out) is caught too — not just the final
frame.

**Things checked and fixed** (the code is the source of truth — see the
"Layout self-check & auto-fix" block in each `_common.py`; keep this table in
sync with it):

| # | Check | What it flags | Detected | Auto-fixed in `fit` |
|---|-------|---------------|----------|---------------------|
| 1 | **OVERFLOW** | a text/block bounding box extends past the frame edge (clipping) | ✅ | ✅ scale down + nudge inside — applied to *entering* elements too, so a clipped item is corrected before its first frame (never a visible "pop") |
| 2 | **SAFE-AREA** (portrait) | content dips below `SHORTS_SAFE_BOTTOM` (bottom 2/10 reserved for captions) | ✅ | ✅ lift above the line |
| 3 | **CONTAINMENT** | text/code spills outside its own panel/box | — | ✅ shrink content to its panel |
| 4 | **OVERLAP** | two text mobjects **or** two content blocks (card/panel/callout) overlap by more than half the smaller one's area (ancestor/descendant pairs ignored) | ✅ | ❌ fixed via `strict` + AI repair |
| 5 | **INTRUDE** | text resting over a *filled panel it isn't part of* (e.g. a note line on a card's bottom padding) — caught even when no glyphs collide and the overlap is well under half a block | ✅ | ❌ fixed via `strict` + AI repair |

Not auto-checked: **semantic** problems such as an arrow pointing the wrong
direction. Geometry can't know the intended direction, so those are fixed at
authoring / AI-generation time (the scene prompt steers toward auto-orienting
arrows), or via the `strict` + AI re-repair loop, which regenerates the scene.

```bash
# Log issues but keep rendering:
python3 video_generator/generate_video.py --storyboard SB.md --output OUT --check-layout warn

# Fail the render on the first scene with a violation (good for CI):
python3 video_generator/generate_video.py --storyboard SB.md --output OUT --check-layout strict

# Auto-fix: scale/nudge overflowing text back inside the frame as it renders:
python3 video_generator/generate_video.py --storyboard SB.md --output OUT --check-layout fit
```

The generator passes the mode to Manim via the `MANIM_CHECK_LAYOUT` env var, so
a direct `manim` invocation honors it too. Overflow/safe-area target **text**
(`Text` / `MarkupText`) — the usual culprit — while overlap and the `fit`
clamps also consider **content blocks** (cards, panels, callouts); full-bleed
bars and backgrounds are excluded to keep false positives low. Default is
`off`, so it never changes a normal render.

### Automated fixing

Two complementary repair paths turn a detected violation into a fixed video
instead of just a report:

- **`fit` (deterministic, in-render).** Because the end-of-render check fires
  *after* a scene's frames are already drawn, `fit` instead hooks every
  `self.play` / `self.wait` and, just before those frames render: shrinks panel
  contents that overflow their box (CONTAINMENT), then scales/nudges any
  too-large or clipped text **or content block** back inside the frame and,
  in portrait, above `SHORTS_SAFE_BOTTOM`. Geometry only — no AI, no extra
  render passes — so it's fast, but it can change a label's size or position
  from what the scene intended. It does **not** resolve OVERLAP (moving
  overlapping blocks apart safely needs to understand intent — that's the AI
  repair path's job).
- **AI re-repair loop (with `strict`).** When `--check-layout strict` aborts a
  scene, the generator feeds that scene's source **and the exact violations**
  back to the AI CLI, writes the corrected `.py`, and re-renders — up to
  `--repair-attempts` times (default 2) before giving up. This preserves
  the intended design better than `fit` but costs an AI call and a re-render per
  attempt. Set `--repair-attempts 0` to disable it and fail fast.

Use `fit` for a quick, hands-off pass; use `strict` (with repair) when you want
the AI to redesign an offending scene rather than mechanically squeeze it.

> The materialised `_common.py` under each build's `scenes_<orient>/` is
> refreshed from the bundled template whenever it changes, so an existing
> output directory picks up the auto-fit logic on the next run without `--force`.

---

## YouTube metadata

The final `youtube` stage asks the configured AI CLI to write publishing
metadata from each language's narration transcript, and writes one file per
language at `youtube/<lang>/youtube.txt`:

```
TITLE
<= 100 chars, searchable terms first, no hashtags

DESCRIPTION
hook + overview + bulleted coverage, ending with <=15 #hashtags

KEYWORDS
comma-separated tags, <= 500 chars, no '#'
```

Each field is sanitised and clamped to YouTube's limits (title 100, description
5000, keywords 500), emoji are stripped, and description hashtags are capped at
15 (YouTube ignores them all past 15). It's a trailing nice-to-have: an AI/parse
failure logs a warning and is skipped — the video itself is unaffected. Disable
with `--skip-youtube`, or run it alone with `--stage youtube` once narration
scripts exist.

---

## Fonts

Fonts live in [`video_generator/templates/assets/fonts/`](video_generator/templates/assets/fonts/)
and are copied into each build's `assets/fonts/`, then registered with
`manimpango` by the scene `_common.py`:

- **Non-code text** (titles, body, subtitles) uses the proportional **Noto Sans**
  (`BODY_FONT`) for even, kerned spacing. Weights Regular / Medium / SemiBold /
  Bold are bundled.
- **Code** uses **JetBrains Mono NL** (`CODE_FONT`).

---

## Common pitfalls

- Use only standard two-letter language codes (`id`, `en`). The bundled
  `_common.py` reads `MANIM_LANG` / `LANG_CODE` and only recognises those.
- Edge TTS's `en-US-GuyNeural` is male; `en-US-JennyNeural` is female. Gemini
  voices (e.g. `Iapetus`, `Charon`) are multilingual — one voice covers both
  languages.
- Gemini subtitle timing is **estimated** (narration split into sentences,
  allocated proportionally over the measured audio duration), whereas Edge timing
  is exact (word-level). Expect coarser cues with `--tts gemini`.
- For portrait, do not pass a custom resolution — the frame dims are baked into
  `templates/scenes_portrait/_common.py`.
- The bottom 2/10 of the portrait frame is reserved for Reels/Shorts/TikTok
  caption overlays; keep content above `SHORTS_SAFE_BOTTOM = -4.8`.
- AI-generated scene files aren't guaranteed to compile first try. After a
  `--stage scenes` run, review the generated `.py` files before `--stage render`.

---

## Testing

The suite lives in [`tests/`](tests/) and runs against the project-local `.venv`.
Install the dev dependency once, then run pytest:

```bash
.venv/bin/pip install -r video_generator/requirements-dev.txt
.venv/bin/python -m pytest
```

- **Unit tests** ([tests/test_unit.py](tests/test_unit.py)) — storyboard parsing,
  voice/key resolution, timestamp + estimated-SRT math, the Pango ampersand
  escape, the AST syntax guard, prompt construction, TTS dispatch, CLI overrides,
  and Gemini HTTP parsing (with `urlopen` mocked). No tools or network needed.
- **Integration tests** ([tests/test_integration.py](tests/test_integration.py),
  marked `integration`) — mux/concat/SRT-merge and the Gemini PCM→MP3 path driven
  through real `ffmpeg`/`ffprobe` on fabricated silent media. Auto-skipped if a
  tool is missing.
- **Live TTS** (marked `network`) — opt in with `VIDEO_GENERATOR_NETWORK_TESTS=1`
  to exercise the real Edge TTS service.

```bash
.venv/bin/python -m pytest -m "not integration"        # fast unit-only run
VIDEO_GENERATOR_NETWORK_TESTS=1 .venv/bin/python -m pytest -m network
```

---

## Notes on `_common.py`

The bundled `_common.py` honors `MANIM_AUDIO_DIR` when computing per-scene target
durations:

```python
audio_root = os.environ.get("MANIM_AUDIO_DIR")
base = Path(audio_root) if audio_root else ROOT_DIR / "audio"
audio_path = base / LANG_CODE / f"{scene_name}.mp3"
```

The generator always sets this to `<output>/audio`, so Manim picks up the
freshly-generated narration timings without any path manipulation in the scene
files themselves.
