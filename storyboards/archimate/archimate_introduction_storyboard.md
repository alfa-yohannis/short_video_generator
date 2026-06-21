---
title: archimate_introduction
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Introduction

A short animated tutorial video that introduces / gives an overview of ArchiMate — the open enterprise-architecture modeling language from The Open Group — before the per-layer videos. Audience: beginners. Style: clean, one idea per screen, smooth transitions.

The English version is entirely in English (including ALL displayed and spoken restaurant examples/labels). The Indonesian version is entirely in Indonesian. The ONLY exception: STANDARD ArchiMate VOCABULARY — terms that the ArchiMate notation itself uses in English — stays the same (in English) in BOTH versions. This covers:
- Product names: "ArchiMate", "The Open Group".
- Layer names: Strategy, Business, Application, Technology, Motivation, Implementation & Migration.
- Aspect names: Active Structure, Behavior, Passive Structure, Motivation.
- Element type names: e.g. Capability, Business Process, Application Component, Node, Goal, Work Package.
- Relationship names: e.g. Realization, Serving, Assignment, Influence, Composition, Association.
ALL other words (ordinary titles, subtitles, narration, explanatory phrases, and restaurant example labels) MUST follow the video's language.

MANDATORY LANGUAGE RULE (to avoid mixing): every displayed example label is written as an `ID "…" | EN "…"` pair. The English version may use ONLY the EN text; the Indonesian version may use ONLY the ID text. NEVER show an Indonesian word in the English video, and vice versa — including text inside boxes, line/relationship labels, titles, subtitles, and the spoken narration.

Consistent example across ALL scenes: a RESTAURANT that wants to grow (from strategic direction, business process, application, down to technology infrastructure) — one complete model from strategy to technology.

# Preparation
No MCP/Archi needed. Element-type icons are available as `_logo` SVG files in the folder at `assets_dir` (front-matter) together with `manifest.json`; the generator automatically injects the file list + their absolute paths into every scene.

HOW TO DRAW (strict — consistent across all scenes and all effort levels):

ELEMENT = a box (RoundedRectangle) drawn with Manim:
- Box fill color = its native layer color: Strategy = ORANGE; Business = YELLOW; Application = LIGHT BLUE; Technology = GREEN; Motivation = PURPLE; Implementation & Migration = PINK. (Panel/text accents may use variations of the related layer color.)
- Element name as text INSIDE the box (must not be cut off).
- The type icon is loaded from its original `_logo.svg` file via `SVGMobject("<path>")`, scaled SMALL, placed in the TOP-RIGHT CORNER of the box with a small margin — NOT covering the name/label. DO NOT draw/invent your own icon and DO NOT recolor the logo (show it as is).
- For this overview, ONE representative element per layer is enough. Logo file per layer:
  - Strategy: `strategy_capability_logo.svg` (Capability).
  - Business: `business_business_process_logo.svg` (Business Process).
  - Application: `application_application_component_logo.svg` (Application Component).
  - Technology: `technology_node_logo.svg` (Node).
  - Motivation: `motivation_goal_logo.svg` (Goal).
  - Implementation & Migration: `implementation_work_package_logo.svg` (Work Package).

RELATIONSHIP = DO NOT load SVG. Draw with Manim's internal methods (`Line` / `DashedLine` + head shapes from `Polygon`/`Triangle`/`Dot`) using the available build-helpers (`realization_arrow`, `serving_arrow`, `assignment_arrow`, `influence_arrow`, `composition_arrow`, `association_arrow`) so they can adapt position, length, and direction between boxes. Line pattern + head shape per ArchiMate notation:
- Realization (`realization_arrow`): DOTTED line; HOLLOW TRIANGLE (outline) head at the target. For the overview, used going UP the stack — a lower/more concrete element realizes the more abstract element above it (Business Process realizes Capability; Capability realizes the Motivation Goal). The triangle always points UP toward the realized element.
- Serving (`serving_arrow`): SOLID line; OPEN arrow head (V) at the target. For the overview, used going DOWN serving the stack (Technology serves Application serves Business).
- Assignment (`assignment_arrow`): SOLID line; FILLED dot (`Dot`) at the source end; FILLED arrow head at the target.
- Influence (`influence_arrow`): DASHED line; OPEN arrow head (V) at the target. (Available for motivation-style influence between elements. NOTE: in this overview the core/strategy elements REALIZE the Goal — do NOT draw an arrow from the Goal pointing down into the stack.)
- Composition (`composition_arrow`): SOLID line; FILLED DIAMOND at the source end.
- Association (`association_arrow`): plain SOLID line (no head, or a small open arrow).
Label the relationship name near the line where it helps.

Semantic colors for emphasis (separate from the layer colors): DANGER, OK, HIGHLIGHT, PRIMARY, ACCENT. Avoid any word that names the orientation/aspect-ratio in displayed or spoken text.

## 01_what_is_archimate (~22s)
Big title "ArchiMate" centered on screen + subtitle "one language for enterprise architecture" (Indonesian version: "satu bahasa untuk enterprise architecture"). Explain what it is: an open modeling language from The Open Group to describe, analyze, and communicate enterprise architecture. Emphasize why it is needed: it unifies strategy down to technology in ONE shared model understood by all stakeholders. Highlight keywords with HIGHLIGHT/PRIMARY color. No element boxes yet — focus on the title and the big idea.

## 02_layered_framework (~30s)
Introduce the LAYERED FRAMEWORK: draw colored bands stacked top to bottom and label each band —
- Strategy (ORANGE band).
- Business (YELLOW band).
- Application (LIGHT BLUE band).
- Technology (GREEN band).
Then draw Motivation as a tall PURPLE COLUMN standing crosswise beside the whole stack of bands (providing the reason for all layers), and Implementation & Migration as a PINK BAND at the very bottom (realizing the change from plan to reality). Label each band/column. Reveal them gradually so each layer gets attention. Emphasize: the four core layers stack up, Motivation runs crosswise, Implementation & Migration closes at the bottom.

## 03_framework_aspects (~26s)
Show the framework as a GRID: three ASPECTS columns + Motivation beside it. Explain each aspect with one short phrase:
- Active Structure = "who/what acts" (Indonesian: "siapa/apa yang bertindak").
- Behavior = "what happens" (Indonesian: "apa yang terjadi").
- Passive Structure = "what is acted on" (Indonesian: "apa yang dikenai tindakan").
- Motivation = "the why" (Indonesian: "mengapa"), crosswise on the side.
Draw the grid: rows = colored layers (Strategy/Business/Application/Technology), columns = the three aspects, with a PURPLE Motivation column on the side. Highlight the aspect column headers with ACCENT color. Emphasize: every ArchiMate element occupies one layer × aspect cell, so the model is tidy and comparable.

## 04_one_element_per_layer (~30s)
Show ONE representative element per layer as a box (per the drawing rules: layer color + name inside + logo in the top-right corner), revealed gradually top to bottom, each with its restaurant example below the box:
- Strategy — Capability (ORANGE box, `strategy_capability_logo.svg`) ID "Layanan delivery" | EN "Delivery service".
- Business — Business Process (YELLOW box, `business_business_process_logo.svg`) ID "Proses pesan-antar" | EN "Order & delivery process".
- Application — Application Component (LIGHT BLUE box, `application_application_component_logo.svg`) ID "Aplikasi Pemesanan" | EN "Ordering App".
- Technology — Node (GREEN box, `technology_node_logo.svg`) ID "Server aplikasi" | EN "Application server".
Also show the context: Motivation — Goal (PURPLE box, `motivation_goal_logo.svg`) ID "Tingkatkan pendapatan" | EN "Increase revenue" on the side, and Implementation & Migration — Work Package (PINK box, `implementation_work_package_logo.svg`) ID "Proyek go-online" | EN "Go-online project" at the bottom. Emphasize: the same single vocabulary is used for the whole restaurant, from direction to machine.

## 05_relationships_between_layers (~34s)
Arrange the six boxes from the previous scene into a stack, then connect them with RELATIONSHIPS DRAWN by Manim (see the patterns + helpers in Preparation); each box = layer color + name inside + logo in the top-right corner; label each line:
- Node (`technology_node_logo.svg`) ID "Server aplikasi" | EN "Application server" —serving (`serving_arrow`)→ Application Component (`application_application_component_logo.svg`) ID "Aplikasi Pemesanan" | EN "Ordering App" (SOLID line; OPEN arrow head): technology SERVES the application.
- Application Component ID "Aplikasi Pemesanan" | EN "Ordering App" —serving (`serving_arrow`)→ Business Process (`business_business_process_logo.svg`) ID "Proses pesan-antar" | EN "Order & delivery process" (SOLID line; OPEN arrow head): the application SERVES the business.
- Business Process ID "Proses pesan-antar" | EN "Order & delivery process" —realization (`realization_arrow`)→ Capability (`strategy_capability_logo.svg`) ID "Layanan delivery" | EN "Delivery service" (DOTTED line; HOLLOW TRIANGLE head pointing up): the business REALIZES the strategic capability.
- Capability (`strategy_capability_logo.svg`) ID "Layanan delivery" | EN "Delivery service" —realization (`realization_arrow`)→ Goal (`motivation_goal_logo.svg`) ID "Tingkatkan pendapatan" | EN "Increase revenue" (PURPLE box on the side) (DOTTED line; HOLLOW TRIANGLE head pointing UP to the Goal): the strategic capability REALIZES the motivation goal — the stack points UP to the "why" that justifies it.
Emphasize: serving flows DOWN serving the stack, realization flows UP toward what it realizes (the layer above it, and finally the Goal), so Motivation gives the "why" for everything — the model becomes coherent and traceable. (ArchiMate rule: the core/strategy elements point UP to realize the Goal; never draw the Goal arrowing down into the stack.)

## 06_why_archimate (~30s)
Recap the benefits: ArchiMate gives ONE coherent model, TRACEABILITY from strategy to technology, and a SHARED COMMUNICATION for all stakeholders. Show the concise chain again on screen with colored boxes + logo in the top-right corner, drawn so the ArchiMate arrows flow UP the stack (providers/concrete elements point to what they serve or realize): Node (GREEN, `technology_node_logo.svg`) —serving→ Application Component (LIGHT BLUE, `application_application_component_logo.svg`) —serving→ Business Process (YELLOW, `business_business_process_logo.svg`) —realization→ Capability (ORANGE, `strategy_capability_logo.svg`) —realization→ Goal (PURPLE, `motivation_goal_logo.svg`), with Work Package (PINK, `implementation_work_package_logo.svg`) realizing the change. You MAY narrate it top-down ("the Goal needs this Capability, run by this Process, supported by this App, on this Node"), but the DRAWN arrows must point upward. Highlight the benefits with OK/HIGHLIGHT color. Close with a call to action: continue to the per-layer videos — Strategy, Business, Application, Technology, Motivation, and Implementation & Migration — to dive deeper into each layer.
