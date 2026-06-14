You are authoring a storyboard markdown file for an automated tutorial-video generator. Below is a COMPLETE example in the required format. Study its structure: a small YAML front-matter block, a `# Title` heading, a free-form brief, then one plain `## Scene Title (~Ns)` heading per scene with the scene's visual description written directly under it.

Produce a NEW storyboard explaining **{{NAME}}** (category: {{CATEGORY}}) from the field of enterprise architecture, modelled with the ArchiMate language, in the SAME format and the same level of detail.

Hard requirements:
- front-matter has exactly: `title: {{TITLE}}`, `subject: archimate`, `language: both`, `length: 2-3 minutes`.
- the `# ` title heading reads exactly `# {{NAME}}`.
- do NOT include a `# Preparation` section. Instead, the brief (the prose right after the `# ` title, before the first `## ` scene) must state that every scene uses the real, original ArchiMate element icons/symbols, never an invented shape.
- 6 to 8 scenes; each is a plain `## Human Title (~Ns)` heading (the `(~Ns)` is that scene's length in seconds) with the description right underneath. Do NOT write `## Scene:`, `**file:**`, `**fallback_duration:**`, `**class:**`, or `### description` — those are derived automatically.
- the per-scene seconds must sum to between 120 and 180.
- the FIRST (intro) scene must present the topic name as the LARGE CENTERED title (not only in the small top bar) — it reads exactly `{{NAME}}`. A short subtitle may sit directly beneath it.
- this is an ENTERPRISE-ARCHITECTURE MODELING tutorial, NOT program code: build every scene from labelled ArchiMate boxes and relationships, never source code. Use ArchiMate's official layer colors so the model reads as authentic — Strategy orange, Business yellow, Application cyan, Technology green, Motivation purple, Implementation and Migration pink.
- follow the teaching arc for a modeling topic: locate it in the ArchiMate framework -> its purpose -> its vocabulary/elements, each with a short example -> the relationships that join them -> how it connects to the neighbouring layers (especially the Motivation layer's goals where relevant) -> ONE worked model that demonstrates the elements in a concrete case -> a conclusion.
- use ONE concrete running example that is simple and familiar (for example a neighbourhood restaurant, a small shop, or a food-delivery service). Name the example's own elements in English, and keep the ArchiMate element-type words in English too (Resource, Capability, Goal, Business Process, Application Component, and so on). The English version should be entirely in English, including the examples.
- descriptions ONLY (no narration text, no Manim/Python code blocks). Use semantic colors DANGER/OK/HIGHLIGHT/PRIMARY/ACCENT as the example does.
- avoid orientation words (left/right/above/below) in any text meant to be shown or spoken.

Output ONLY the raw markdown file content. No code fences, no commentary before or after.

===== EXAMPLE STORYBOARD (format reference) =====
{{EXEMPLAR}}
===== END EXAMPLE =====
