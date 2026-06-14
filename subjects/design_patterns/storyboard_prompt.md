You are authoring a storyboard markdown file for an automated tutorial-video generator. Below is a COMPLETE example in the required format. Study its structure: a small YAML front-matter block, a `# Title` heading, a free-form brief, then one plain `## Scene Title (~Ns)` heading per scene with the scene's visual description written directly under it.

Produce a NEW storyboard for the **{{NAME}}** ({{CATEGORY}}) software design pattern, in the SAME format and the same level of detail.

Hard requirements:
- front-matter has exactly: `title: {{TITLE}}`, `language: both`, `length: 2-3 minutes`.
- the `# ` title heading reads exactly `# {{NAME}} Pattern`.
- after the brief, include exactly one `# Preparation` section (a level-1 heading, NOT a `## ` scene) stating that no preparation is needed because this is a code-only tutorial with no external tools or reference assets to set up. It has NO `(~Ns)` duration and is not counted as a scene.
- 6 to 8 scenes; each is a plain `## Human Title (~Ns)` heading (the `(~Ns)` is that scene's length in seconds) with the description right underneath. Do NOT write `## Scene:`, `**file:**`, `**fallback_duration:**`, `**class:**`, or `### description` — those are derived automatically.
- the per-scene seconds must sum to between 120 and 180.
- the FIRST (intro) scene must present the pattern name as the LARGE CENTERED title (not only in the small top bar) — it reads exactly `{{NAME}} Pattern` (for a SOLID principle, drop the word Pattern). A short subtitle may sit directly beneath it.
- write ONE concrete running example in **Java**; flow problem -> naive approach -> the pattern -> a class/structure diagram -> before/after code -> conclusion, adapted to this pattern.
- descriptions ONLY (no narration text, no Manim/Python code blocks). Use semantic colors DANGER/OK/HIGHLIGHT/PRIMARY/ACCENT as the example does.
- avoid orientation words (left/right/above/below) in any text meant to be shown or spoken.

Output ONLY the raw markdown file content. No code fences, no commentary before or after.

===== EXAMPLE STORYBOARD (format reference) =====
{{EXEMPLAR}}
===== END EXAMPLE =====
