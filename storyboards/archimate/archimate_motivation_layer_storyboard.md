---
title: archimate_motivation_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Motivation Layer

A short animated tutorial video about the Motivation Layer in the ArchiMate enterprise-architecture language — the layer that captures the "why" behind all other elements. Audience: beginners. Style: clean, one idea per screen, smooth transitions.

The English version is entirely in English (including ALL displayed and spoken restaurant examples/labels). The Indonesian version is entirely in Indonesian. The ONLY exception: STANDARD ArchiMate VOCABULARY — terms that the ArchiMate notation itself uses in English — stays the same (in English) in BOTH versions. This covers:
- Product names: "ArchiMate", "The Open Group".
- Layer names: Strategy, Business, Application, Technology, Motivation, Implementation & Migration.
- Aspect names: Active Structure, Behavior, Passive Structure, Motivation.
- Element type names: e.g. Capability, Business Process, Application Component, Node, Goal, Work Package.
- Relationship names: e.g. Realization, Serving, Assignment, Influence, Composition, Association.
ALL other words (ordinary titles, subtitles, narration, explanatory phrases, and restaurant example labels) MUST follow the video's language.

MANDATORY LANGUAGE RULE (to avoid mixing): every displayed example label is written as an `ID "…" | EN "…"` pair. The English version may use ONLY the EN text; the Indonesian version may use ONLY the ID text. NEVER show an Indonesian word in the English video, and vice versa — including text inside boxes, line/relationship labels, titles, subtitles, and the spoken narration.

Consistent example across ALL scenes: a RESTAURANT that wants to grow (revenue is falling → it wants to grow → it accepts online orders).

# Preparation
No MCP/Archi needed. Element-type icons are available as `_logo` SVG files in the folder at `assets_dir` (front-matter) together with `manifest.json`; the generator automatically injects the file list + their absolute paths into every scene.

HOW TO DRAW (strict — consistent across all scenes and all effort levels):

ELEMENT = a box (RoundedRectangle) drawn with Manim:
- Box fill color = its native layer color: Motivation = PURPLE; Strategy = ORANGE/YELLOW; Application = LIGHT BLUE; Business = YELLOW; Technology = GREEN. (Panel/text accents may use variations of the Motivation/purple color.)
- Element name as text INSIDE the box (must not be cut off).
- The type icon is loaded from its original `_logo.svg` file via `SVGMobject("<path>")`, scaled SMALL, placed in the TOP-RIGHT CORNER of the box with a small margin — NOT covering the name/label. DO NOT draw/invent your own icon and DO NOT recolor the logo (show it as is).
- Motivation logo files: `motivation_stakeholder_logo.svg`, `motivation_driver_logo.svg`, `motivation_assessment_logo.svg`, `motivation_goal_logo.svg`, `motivation_outcome_logo.svg`, `motivation_principle_logo.svg`, `motivation_requirement_logo.svg`, `motivation_constraint_logo.svg`, `motivation_value_logo.svg`, `motivation_meaning_logo.svg`.
- Cross-layer logo files (scene 7): `strategy_course_of_action_logo.svg`, `application_application_component_logo.svg`.

RELATIONSHIP = DO NOT load SVG. Draw with Manim's internal methods (`Line` / `DashedLine` + head shapes from `Polygon`/`Triangle`/`Dot`) so they can adapt position, length, and direction between boxes. Line pattern + head shape per ArchiMate notation:
- Influence: DASHED line; OPEN arrow head (V) at the target.
- Realization: DOTTED line; HOLLOW TRIANGLE (outline) head at the target.
- Association: plain SOLID line (no head, or a small open arrow).
- Serving: SOLID line; OPEN arrow head at the target.
Label the relationship name near the line where it helps.

## 01_layer_position (~16s)
Big title "ArchiMate — Motivation Layer" centered + subtitle "the why behind the architecture". Draw the ArchiMate framework as colored bands — Strategy ORANGE, Business YELLOW, Application LIGHT BLUE, Technology GREEN — then show Motivation as a tall PURPLE COLUMN standing crosswise beside all of them (because it provides the reason for the elements in every other layer). Highlight the purple column.

## 02_layer_purpose (~22s)
Explain its purpose: the Motivation Layer records who cares, what drives, and what is wanted — the intentions that justify every other element. Restaurant example: the core model shows it cooks and serves, but only the Motivation Layer states WHY it is going to change. Show a single purple band behind a plain Business process; emphasize that without this layer the model has the "what" and the "how" but not the "why".

## 03_motivation_sources (~26s)
Introduce the trio of motivation sources, each a purple box + name inside + logo in the top-right corner, revealed gradually:
- Stakeholder (`motivation_stakeholder_logo.svg`) ID "Pemilik Restoran" | EN "Restaurant Owner", ID "Pelanggan" | EN "Customer".
- Driver (`motivation_driver_logo.svg`) ID "Persaingan" | EN "Competition", ID "Pendapatan" | EN "Revenue".
- Assessment (`motivation_assessment_logo.svg`) ID "Penjualan menurun" | EN "Sales declining".
Connect them with relationships DRAWN by Manim: Stakeholder —association→ Driver; Driver —association→ Assessment (concern flows into a finding).

## 04_intentions (~30s)
Introduce the group of intentions, each a purple box + logo in the top-right corner:
- Goal (`motivation_goal_logo.svg`) ID "Tingkatkan pendapatan" | EN "Increase revenue".
- Outcome (`motivation_outcome_logo.svg`) ID "Penjualan naik 30%" | EN "Sales up 30%".
- Requirement (`motivation_requirement_logo.svg`) ID "Terima pesanan online" | EN "Accept online orders".
- Constraint (`motivation_constraint_logo.svg`) ID "Anggaran terbatas" | EN "Limited budget".
- Principle (`motivation_principle_logo.svg`) ID "Utamakan layanan cepat" | EN "Prioritize fast service".
Reveal them gradually so the screen does not get crowded.

## 05_value_meaning (~16s)
Complete the vocabulary with two elements that connect motivation to the stakeholder's perception, each a purple box + logo in the top-right corner:
- Value (`motivation_value_logo.svg`) ID "Kenyamanan" | EN "Convenience" — the value the customer gets when ordering without leaving home.
- Meaning (`motivation_meaning_logo.svg`) ID "Pesanan siap" | EN "Order ready" — interpreted as "the food is ready for pickup".
Note that both attach to the core element they describe, completing the layer to ten elements.

## 06_relationships (~26s)
Wire the vocabulary together with ArchiMate relationships DRAWN by Manim, each a purple box + logo in the top-right corner, each line labeled:
- Assessment (`motivation_assessment_logo.svg`) ID "Penjualan menurun" | EN "Sales declining" —influence→ Goal (`motivation_goal_logo.svg`) ID "Tingkatkan pendapatan" | EN "Increase revenue".
- Outcome (`motivation_outcome_logo.svg`) ID "Penjualan naik 30%" | EN "Sales up 30%" —realization→ Goal.
- Requirement (`motivation_requirement_logo.svg`) ID "Terima pesanan online" | EN "Accept online orders" —realization→ Goal.
- Principle (`motivation_principle_logo.svg`) ID "Utamakan layanan cepat" | EN "Prioritize fast service" —influence→ Requirement; Constraint (`motivation_constraint_logo.svg`) ID "Anggaran terbatas" | EN "Limited budget" —influence→ Requirement.
Highlight that influence + realization turn a vague wish into a tested need.

## 07_case_example (~28s)
Assemble the restaurant's motivation model gradually, all boxes + relationships DRAWN by Manim, then show it driving the lower layers:
Stakeholder ID "Pemilik Restoran" | EN "Restaurant Owner" —association→ Driver ID "Pendapatan" | EN "Revenue"; Assessment ID "Penjualan menurun" | EN "Sales declining" —influence→ Goal ID "Tingkatkan pendapatan" | EN "Increase revenue"; Goal is realized by Outcome ID "Penjualan naik 30%" | EN "Sales up 30%" and refined into Requirement ID "Terima pesanan online" | EN "Accept online orders", bounded by Constraint ID "Anggaran terbatas" | EN "Limited budget". Then connect the lower layers, which point UP to realize the motivation: Course of Action ID "Mulai jualan online" | EN "Start selling online" (ORANGE Strategy box, `strategy_course_of_action_logo.svg`) —realization→ Outcome ID "Penjualan naik 30%" | EN "Sales up 30%"; Application Component ID "Aplikasi Delivery" | EN "Delivery App" (LIGHT BLUE Application box, `application_application_component_logo.svg`) —realization→ Requirement ID "Terima pesanan online" | EN "Accept online orders". (ArchiMate rule: the concrete strategy/core elements REALIZE the abstract motivation — the triangle head points UP toward the Outcome/Requirement, NOT down from them.) The orange plan and the blue system are now proven to realize the purple "why".

## 08_conclusion (~14s)
Recap: the Motivation Layer captures the "why" through ten elements — show the ten original icons again (purple box + logo in the top-right corner): Stakeholder (`motivation_stakeholder_logo.svg`), Driver (`motivation_driver_logo.svg`), Assessment (`motivation_assessment_logo.svg`), Goal (`motivation_goal_logo.svg`), Outcome (`motivation_outcome_logo.svg`), Principle (`motivation_principle_logo.svg`), Requirement (`motivation_requirement_logo.svg`), Constraint (`motivation_constraint_logo.svg`), Value (`motivation_value_logo.svg`), Meaning (`motivation_meaning_logo.svg`). Benefits: every element can be traced back to its reason, choices are justified, and the model stays aligned. Close with the chain on screen: Stakeholder → Driver → Assessment → Goal → Requirement.
