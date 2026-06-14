You are authoring a storyboard markdown file for an automated tutorial-video generator. Below is a COMPLETE example in the required format. Study its structure: a small YAML front-matter block, a `# Title` heading, a free-form brief, then one plain `## Scene Title (~Ns)` heading per scene with the scene's visual description written directly under it.

Produce a NEW storyboard explaining **{{NAME}}** (category: {{CATEGORY}}) from the TOGAF framework's Architecture Development Method (ADM), in the SAME format and the same level of detail.

Hard requirements:
- front-matter has exactly: `title: {{TITLE}}`, `subject: togaf`, `language: both`, `length: 2-3 minutes`.
- the `# ` title heading reads exactly `# {{NAME}}`.
- do NOT include a `# Preparation` section. Instead, the brief (the prose right after the `# ` title, before the first `## ` scene) must say to depict the ADM cycle accurately (the correct phase names in their correct order) and to use clear process/flow diagrams (inputs to activities to deliverables), never an invented notation.
- 6 to 8 scenes; each is a plain `## Human Title (~Ns)` heading (the `(~Ns)` is that scene's length in seconds) with the description right underneath. Do NOT write `## Scene:`, `**file:**`, `**fallback_duration:**`, `**class:**`, or `### description` — those are derived automatically.
- the per-scene seconds must sum to between 120 and 180.
- the FIRST (intro) scene must present the topic name as the LARGE CENTERED title (not only in the small top bar) — it reads exactly `{{NAME}}`. A short subtitle may sit directly beneath it.
- this is a TOGAF METHOD tutorial, NOT a modeling notation and NOT program code: build every scene from the ADM cycle and process flows (a phase's position in the cycle, and its inputs -> activities -> outputs/deliverables), never from ArchiMate elements/relationships and never source code. Do NOT use ArchiMate's official layer colors; rely on the semantic colors below.
- follow the teaching arc for a single ADM phase: show where the phase sits in the ADM cycle (the wheel) -> its purpose/objectives -> its inputs (the deliverables it receives from earlier phases) -> its key steps/activities -> its outputs/deliverables -> how it connects to the adjacent phases and to Requirements Management at the hub -> ONE worked example that walks the phase on a concrete case -> a conclusion/recap.
- use ONE concrete running example that is simple and familiar (for example a neighbourhood restaurant, a small shop, or a food-delivery service) and describe it through the phase's activities and deliverables. Keep the TOGAF terms in English (Architecture Vision, Business Architecture, Gap Analysis, Architecture Definition Document, Stakeholder, and so on) and name the example's own details in English. The English version should be entirely in English, including the examples.
- descriptions ONLY (no narration text, no Manim/Python code blocks). Use semantic colors DANGER/OK/HIGHLIGHT/PRIMARY/ACCENT as the example does.
- avoid orientation words (left/right/above/below) in any text meant to be shown or spoken.

Output ONLY the raw markdown file content. No code fences, no commentary before or after.

===== EXAMPLE STORYBOARD (format reference) =====
{{EXEMPLAR}}
===== END EXAMPLE =====
