You are authoring a storyboard markdown file for an automated tutorial-video generator. Below is a COMPLETE example in the required format. Study its structure: a small YAML front-matter block, a `# Title` heading, a free-form brief, then one plain `## Scene Title (~Ns)` heading per scene with the scene's visual description written directly under it.

Produce a NEW storyboard for the **{{NAME}}** ({{CATEGORY}}) beginner Python topic, in the SAME format and the same level of detail.

Hard requirements:
- front-matter has exactly: `title: {{TITLE}}`, `subject: python_101`, `language: both`, `length: 2-3 minutes`. (The dark `python_dark` template with typing animations is selected automatically by the subject; do NOT add a `template:` line.)
- the `# ` title heading reads exactly `# {{NAME}}`.
- after the brief, include exactly one `# Preparation` section (a level-1 heading, NOT a `## ` scene) stating that no preparation is needed because this is a code-only tutorial with no external tools or reference assets to set up. It has NO `(~Ns)` duration and is not counted as a scene.
- 6 to 8 scenes; each is a plain `## Human Title (~Ns)` heading (the `(~Ns)` is that scene's length in seconds) with the description right underneath. Do NOT write `## Scene:`, `**file:**`, `**fallback_duration:**`, `**class:**`, or `### description` — those are derived automatically.
- the per-scene seconds must sum to between 120 and 180.
- the FIRST (intro) scene must present the topic name as the LARGE CENTERED title (not only in the small top bar) — it reads exactly `{{NAME}}`. A short subtitle may sit directly beneath it.
- write ONE concrete running example in **Python 3**; flow concept -> a minimal code example that is TYPED IN -> run it and show the printed OUTPUT -> a common beginner pitfall -> the fix -> recap. Keep code short enough to fit one card.
- lean on the template's signature TYPING animation: say the code is "typed in" (typewriter) and pair each runnable snippet with its console/terminal output. Use semantic colors DANGER (bugs / wrong output), OK (correct result), HIGHLIGHT (current focus), PRIMARY (titles), ACCENT (labels) as the example does.
- descriptions ONLY (no narration text, no Manim/Python code blocks). Avoid orientation words (left/right/above/below) in any text meant to be shown or spoken.

Output ONLY the raw markdown file content. No code fences, no commentary before or after.

===== EXAMPLE STORYBOARD (format reference) =====
{{EXEMPLAR}}
===== END EXAMPLE =====
