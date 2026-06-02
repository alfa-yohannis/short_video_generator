# Video Generator — HTML backend (Mermaid + anime.js + Playwright)

The web sibling of the Manim app. Same storyboard format and same Python
pipeline, but scenes are **HTML/CSS**, **diagrams are drawn with
[Mermaid](https://mermaid.js.org)** (clean SVG UML/flow/sequence), animated with
a seekable **[anime.js](https://animejs.com)** timeline, and captured
frame-by-frame with **Playwright** (Python). Layout is CSS flexbox, so text wraps
and flows on its own — the overflow/overlap problems of the coordinate-based
Manim backend largely disappear — and there is **no Node toolchain** (Playwright
drives Chromium directly from Python).

```
storyboard.md ─▶ narration (Claude | Codex) ─▶ MP3 + SRT (Edge | Gemini)
   ─▶ HTML scene module .js (Claude | Codex) ─▶ Playwright screenshots ─▶ silent MP4
   ─▶ mux audio ─▶ concat ─▶ merged SRT + youtube.txt
```

Bilingual (id/en), landscape **and** portrait, swappable narrator/TTS, resumable
per-stage, `max_duration` cap, YouTube metadata — all identical to the Manim app.

## Why Mermaid + anime.js

- **Mermaid for diagrams.** You describe a diagram in text (`classDiagram
  class AppConfig { -instance\n +getInstance() }`) and Mermaid renders polished
  SVG. LLMs are *extremely* fluent in Mermaid (it's everywhere in markdown/docs),
  so AI-generated UML/flow diagrams come out correct and clean — far better than
  hand-built `<div>` boxes.
- **anime.js for animation.** Its timeline can be paused and *seeked*
  (`tl.seek(ms)`), rendering an exact frame synchronously — that's what makes
  deterministic, frame-accurate capture possible (Playwright seeks to `i/fps`,
  screenshots, repeats). MIT-licensed and well-known to LLMs.
- **No Node build.** Both are vendored as single browser files; Playwright
  (Python) drives Chromium. Fonts are preloaded before render so Mermaid measures
  box sizes with the real Noto Sans metrics.

## Layout

```
video_generator_html/
├── generate_video.py        ← Python orchestrator (the 8-stage pipeline)
├── requirements.txt         ← PyYAML, srt, edge-tts, playwright (auto-installed)
└── template/                ← copied into <output>/render_html/ at render time
    ├── index.html           ← harness: loads anime + mermaid + theme + components,
    │                            exposes window.__render(t) for per-frame seeking
    ├── theme.css            ← palette + fonts + flexbox layout (mirrors _common.py)
    ├── components.js         ← L(id,en) + builders: titleBar, bodyText, bulletList,
    │                            codeCard, and c.diagram (Mermaid → SVG)
    ├── scene_skeleton.js     ← reference module the AI mimics
    ├── vendor/anime.min.js   ← vendored anime.js (seekable timeline, no npm)
    ├── vendor/mermaid.min.js ← vendored Mermaid (diagrams, no npm)
    └── assets/fonts/         ← Noto Sans + JetBrains Mono NL
```

Generated scenes are written to `<output>/render_html/scenes/<basename>.js`.

## Requirements

| Tool | For | Install |
|------|-----|---------|
| Python 3.10+ | orchestrator (self-bootstraps a repo-local `.venv`) | system |
| ffmpeg / ffprobe | frames → MP4, audio probing/mux | `sudo apt install ffmpeg` |
| Chromium/Chrome | Playwright rendering | a system Chrome is used if present, else `.venv/bin/python -m playwright install chromium` |
| `claude` / `codex` | AI narration + scene modules | [Claude Code](https://claude.com/claude-code) / `npm i -g @openai/codex` |
| `GEMINI_API_KEY` | only for `--tts gemini` | a `.env` at the repo root |

`playwright` is a Python package (auto-installed into `.venv`). It needs a
browser — this app prefers a **system Chrome** (no download); otherwise run
`playwright install chromium` once.

## Usage

```bash
python3 video_generator_html/generate_video.py \
    --storyboard storyboards/singleton_pattern_storyboard.md \
    --output     tmp/singleton_html \
    --tts edge
```

| Stage (`--stage`) | What it does |
| --- | --- |
| `scripts` | AI-fill missing narration → `scripts/<lang>/*.txt` |
| `audio`   | Edge/Gemini TTS → `audio/<lang>/*.mp3` + per-scene SRT |
| `scenes`  | AI-generate `render_html/scenes/<basename>.js` (+ copy the template) |
| `render`  | Playwright seeks each scene's anime.js timeline per frame, screenshots, encodes a **silent** MP4 per (lang, orient) scene |
| `mux`     | Add the narration audio to each scene clip |
| `concat`  | Concatenate clips → `final/<lang>/<title>_<orient>.mp4` |
| `srt`     | Merge per-scene SRTs → `subtitles/<lang>/<title>.srt` |
| `youtube` | YouTube title/description/keywords per language |
| `all`     | (default) all of the above |

Flags: `--ai-cli {claude,codex}`, `--tts {edge,gemini}`, `--voice`,
`--gemini-api-key`, `--only`, `--force`, `--repair-attempts N` (feed a scene's
browser error back to the AI to regenerate it), `--skip-youtube`,
`--skip-dep-check`, `--no-ai-cli-check`.

## How a scene works

Each AI-generated scene is an ES module exporting an **async** `build(ctx)`
(async because Mermaid renders asynchronously):

```js
export default async function build(ctx) {
  const {stage, c, L, tl} = ctx;
  stage.appendChild(c.titleBar(L('Judul', 'Title')));
  const content = c.content();
  const body = c.bodyText(L('Teks.', 'Text.'));
  const uml = await c.diagram(`classDiagram
    class AppConfig { -instance: AppConfig\n +getInstance() AppConfig }`);
  content.append(body, uml); stage.appendChild(content);
  tl.add({targets: body, opacity: [0, 1], translateY: [30, 0], duration: 600}, 0);
  tl.add({targets: uml,  opacity: [0, 1], scale: [0.9, 1], duration: 700}, 350);
}
```

The harness builds the scene once, then the renderer calls `window.__render(t)`
(= `tl.seek(t·1000)`) for each frame `t = i/fps` and screenshots. After the
timeline ends the final frame holds, so a scene can be shorter than its narration.

## Status

End-to-end verified here: parse, template materialization, system-Chrome launch,
**Mermaid UML diagram render**, anime.js timeline seek, per-frame screenshot, and
ffmpeg encode all work — a hand-written scene with a UML class diagram renders to
a clean MP4 (fonts are preloaded so Mermaid sizes boxes correctly). The remaining
variable is **AI scene quality**: LLMs are very fluent in HTML/CSS, Mermaid, and
anime.js, and `--repair-attempts` feeds any browser-side error back to the model
to self-heal. Performance note: rendering is one screenshot per frame, so a long
scene at 30fps is many screenshots — lower `fps` or test with `--only` for quick
iteration.

## Testing

```bash
.venv/bin/python -m pytest tests_html        # this app's suite
```

Separate from the Manim app's `tests/` (each has its own `conftest.py`); run them
in separate sessions.
