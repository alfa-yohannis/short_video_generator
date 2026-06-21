---
title: archimate_viewpoints
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Views & Viewpoints

A short animated tutorial video about Views & Viewpoints in the ArchiMate enterprise-architecture language — the difference between the whole MODEL and a single VIEW, and how a Stakeholder's Concern determines which Viewpoint is used. Audience: beginners. Style: clean, one idea per screen, smooth transitions.

The English version is entirely in English (including ALL displayed and spoken restaurant examples/labels). The Indonesian version is entirely in Indonesian. The ONLY exception: STANDARD ArchiMate VOCABULARY — terms that the ArchiMate notation itself uses in English — stays the same (in English) in BOTH versions. This covers:
- Product names: "ArchiMate", "The Open Group".
- Layer names: Strategy, Business, Application, Technology, Motivation, Implementation & Migration.
- Aspect names: Active Structure, Behavior, Passive Structure, Motivation.
- Element type names: e.g. Capability, Business Process, Application Component, Node, Goal, Work Package.
- Relationship names: e.g. Realization, Serving, Assignment, Influence, Composition, Association.
- View/Viewpoint vocabulary: Model, View, Viewpoint, Stakeholder, Concern, and standard viewpoint names.
ALL other words (ordinary titles, subtitles, narration, explanatory phrases, and restaurant example labels) MUST follow the video's language.

MANDATORY LANGUAGE RULE (to avoid mixing): every displayed example label is written as an `ID "…" | EN "…"` pair. The English version may use ONLY the EN text; the Indonesian version may use ONLY the ID text. NEVER show an Indonesian word in the English video, and vice versa — including text inside boxes, line/relationship labels, titles, subtitles, and the spoken narration.

Consistent example across ALL scenes: a RESTAURANT with one whole model, shown through different views for different stakeholders (the Owner looks at Motivation/Strategy; the IT staff look at Application/Technology).

# Preparation
No MCP/Archi needed. Element-type icons are available as `_logo` SVG files in the folder at `assets_dir` (front-matter) together with `manifest.json`; the generator automatically injects the file list + their absolute paths into every scene.

HOW TO DRAW (strict — consistent across all scenes and all effort levels):

ELEMENT = a box (RoundedRectangle) drawn with Manim:
- Box fill color = its native layer color: Motivation = PURPLE; Strategy = ORANGE; Business = YELLOW; Application = LIGHT BLUE; Technology = GREEN. (Panel/text accents may use variations of the related layer color.)
- Element name as text INSIDE the box (must not be cut off).
- The type icon is loaded from its original `_logo.svg` file via `SVGMobject("<path>")`, scaled SMALL, placed in the TOP-RIGHT CORNER of the box with a small margin — NOT covering the name/label. DO NOT draw/invent your own icon and DO NOT recolor the logo (show it as is).
- Logo files used (ONLY these six): `motivation_stakeholder_logo.svg`, `motivation_goal_logo.svg`, `strategy_capability_logo.svg`, `business_business_process_logo.svg`, `application_application_component_logo.svg`, `technology_node_logo.svg`.

VIEW = a labeled panel/frame (a large/semi-transparent RoundedRectangle + panel title) that GROUPS selected boxes. A view shows only a subset of the elements from the whole model; draw the panel frame around the chosen boxes and label it with the view's name. The whole model = all boxes + relationships shown densely without a selecting frame.

RELATIONSHIP = DO NOT load SVG. Draw with Manim's internal methods (`Line` / `DashedLine` + head shapes from `Polygon`/`Triangle`/`Dot`) so they can adapt position, length, and direction between boxes. Provide helpers and use them consistently — line pattern + head shape per ArchiMate notation:
- serving_arrow: SOLID line; OPEN arrow head (two "V" lines, no fill) at the target.
- realization_arrow: DOTTED line; HOLLOW TRIANGLE (outline) head at the target.
- association_arrow: plain SOLID line (no head, or a small open arrow).
- influence_arrow: DASHED line; OPEN arrow head (V) at the target — valid ONLY with a Motivation element as the TARGET.
The ArchiMate relationship glyphs above are used ONLY between real model ELEMENTS (the boxes), keeping their real meaning and direction. IMPORTANT: Model, View, Viewpoint, and Concern are FRAMEWORK concepts (the ArchiMate / ISO 42010 architecture-description mechanism), NOT model elements — so the Stakeholder → Concern → Viewpoint → View chain is drawn with PLAIN labeled arrows (a simple line/arrowhead), NEVER an ArchiMate relationship glyph (no influence/realization/serving/association head). Only the Stakeholder is a real ArchiMate element (Motivation). You may label the relationship name near the line where it helps.

Semantic colors for emphasis (separate from the layer colors): DANGER for overload/visual clutter, OK for a clean/selected result, HIGHLIGHT to spotlight focus, PRIMARY for the main view panel/title, ACCENT for the connecting chain Stakeholder → Concern → Viewpoint → View. Avoid any word that names the orientation/aspect-ratio in displayed or spoken text.

## 01_the_big_model (~16s)
Big title "ArchiMate — Views & Viewpoints" centered on screen + short subtitle "the right slice for the right audience". Briefly show the entire restaurant model: many boxes from several layers (Motivation purple, Strategy orange, Business yellow, Application blue, Technology green) crammed together with many relationships (drawn with Manim) so it feels DENSE. Highlight the density with DANGER color. Emphasize: the complete model is big — we rarely show all of it at once.

## 02_model_vs_view (~24s)
Show the difference between MODEL and VIEW. Left: the dense whole model (all boxes + relationships, drawn with Manim) — mark it DANGER because it is too busy for a single audience. Right: a clean VIEW — a labeled panel (PRIMARY) that only SELECTS a subset of boxes from that model. For this view pick a few elements, e.g. Business Process (`business_business_process_logo.svg`) ID "Layani pesanan" | EN "Serve orders" and Application Component (`application_application_component_logo.svg`) ID "Aplikasi Delivery" | EN "Delivery App", framed inside a labeled panel, with the rest dimmed. Mark the resulting panel with OK. Emphasize: a View = a chosen slice of the model, not a new model — the same elements, shown in part.

## 03_mechanism (~26s)
Explain the mechanism chain with ACCENT, built up gradually, with all relationships DRAWN by Manim:
- A Stakeholder (PURPLE box, `motivation_stakeholder_logo.svg`) ID "Pemilik Restoran" | EN "Restaurant Owner" has a Concern (label/text ID "Bagaimana bisnis tumbuh?" | EN "How does the business grow?").
- That Concern selects a VIEWPOINT — draw a PLAIN labeled arrow (NOT an influence glyph) to the Viewpoint, shown as a "lens": a HIGHLIGHT panel/frame that states WHICH element types & relationships are allowed to appear.
- The Viewpoint produces a VIEW — draw a PLAIN labeled arrow (NOT a realization glyph) to the View: a PRIMARY panel holding the boxes that pass the lens. Inside the View, the boxes keep their REAL ArchiMate relationships.
Show the chain on screen with PLAIN arrows: Stakeholder → Concern → Viewpoint (lens) → View (diagram). Emphasize: the Viewpoint defines the RULES (the allowed types), the View is its actual DIAGRAM. (Concern/Viewpoint/View are framework concepts, not model elements — that is why the chain uses plain arrows, not ArchiMate relationship notation.)

## 04_two_lenses (~32s)
One restaurant model, TWO lenses — draw two view panels side by side, each box = native layer color + name inside + logo in the top-right corner. Inside each panel the boxes keep their REAL ArchiMate relationships (a View shows the model's existing links, it does not invent new ones):
- Panel "Owner View" (PRIMARY) for the Stakeholder ID "Pemilik" | EN "Owner": Business Process (YELLOW box, `business_business_process_logo.svg`) ID "Layani pesanan" | EN "Serve orders" —realization→ Strategy Capability (ORANGE box, `strategy_capability_logo.svg`) ID "Penjualan online" | EN "Online sales" —realization→ Motivation Goal (PURPLE box, `motivation_goal_logo.svg`) ID "Tingkatkan pendapatan" | EN "Increase revenue" (DOTTED realization lines; HOLLOW TRIANGLE heads pointing up). Concern: business direction & value.
- Panel "IT View" (PRIMARY) for the IT staff: Technology Node (GREEN box, `technology_node_logo.svg`) ID "Server Cloud" | EN "Cloud Server" —serving→ Application Component (LIGHT BLUE box, `application_application_component_logo.svg`) ID "Aplikasi Delivery" | EN "Delivery App" (SOLID serving line; OPEN arrow head). Concern: systems & infrastructure.
Emphasize with HIGHLIGHT: the SAME MODEL, TWO different views for different audiences — each stakeholder sees only the slice relevant to their concern.

## 05_standard_viewpoints (~30s)
A short walk through several standard ArchiMate Viewpoints; each viewpoint as a labeled HIGHLIGHT panel/frame + 1 sentence of its use + an example box content (layer color + logo in the top-right corner):
- Layered viewpoint: see many layers at once and how they stack on each other — show boxes across layers, e.g. Business Process (`business_business_process_logo.svg`) above Application Component (`application_application_component_logo.svg`) above Technology Node (`technology_node_logo.svg`), linked with serving_arrow going up.
- Business Process viewpoint: focus on the business workflow — show Business Process (YELLOW box, `business_business_process_logo.svg`) ID "Layani pesanan" | EN "Serve orders" as the center.
- Application Cooperation viewpoint: focus on how applications work together — show two Application Components (LIGHT BLUE boxes, `application_application_component_logo.svg`) ID "Aplikasi Delivery" | EN "Delivery App" and ID "Aplikasi POS" | EN "POS App" linked with serving_arrow.
Briefly mention two more as examples: the Motivation viewpoint (focus on Goal/Stakeholder) and the Implementation & Migration viewpoint (focus on the transition plan). Emphasize: each viewpoint = a different lens for a different concern.

## 06_conclusion (~16s)
Recap the chain once more with ACCENT (PLAIN labeled arrows — Concern/Viewpoint/View are framework concepts, not ArchiMate model relationships): Stakeholder (`motivation_stakeholder_logo.svg`) → Concern → Viewpoint (lens) → View (diagram). Show again the two view panels from scene 04 side by side (Owner View vs IT View) from one and the same model, mark them both OK. Benefit: views deliver the right slice to the right audience — the model stays single and whole, while each person sees the part they care about. Close with a short closing sentence.
