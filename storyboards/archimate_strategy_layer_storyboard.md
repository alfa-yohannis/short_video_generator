---
title: archimate_strategy_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Strategy Layer

A short animated tutorial video about the Strategy Layer in the ArchiMate enterprise-architecture language. Audience: beginners. Style: clean, one idea per screen, smooth transitions.

The English version is entirely in English (including ALL displayed and spoken restaurant examples/labels). The Indonesian version is entirely in Indonesian. The ONLY exception: STANDARD ArchiMate VOCABULARY — terms that the ArchiMate notation itself uses in English — stays the same (in English) in BOTH versions. This covers:
- Product names: "ArchiMate", "The Open Group".
- Layer names: Strategy, Business, Application, Technology, Motivation, Implementation & Migration.
- Aspect names: Active Structure, Behavior, Passive Structure, Motivation.
- Element type names: e.g. Capability, Business Process, Application Component, Node, Goal, Work Package.
- Relationship names: e.g. Realization, Serving, Assignment, Influence, Composition, Association.
ALL other words (ordinary titles, subtitles, narration, explanatory phrases, and restaurant example labels) MUST follow the video's language.

MANDATORY LANGUAGE RULE (to avoid mixing): every displayed example label is written as an `ID "…" | EN "…"` pair. The English version may use ONLY the EN text; the Indonesian version may use ONLY the ID text. NEVER show an Indonesian word in the English video, and vice versa — including text inside boxes, line/relationship labels, titles, subtitles, and the spoken narration.

Consistent example across ALL scenes: a RESTAURANT context (online sales, delivery service, online booking).

# Preparation
No MCP/Archi needed. Element-type icons are available as `_logo` SVG files in the folder at `assets_dir` (front-matter) together with `manifest.json`; the generator automatically injects the file list + their absolute paths into every scene.

HOW TO DRAW (strict — consistent across all scenes and all effort levels):

ELEMENT = a box (RoundedRectangle) drawn with Manim:
- Box fill color = its native layer color: Strategy = ORANGE/golden yellow; Motivation = PURPLE; Business = YELLOW; Application = LIGHT BLUE. (Panel/text accents may use variations of the Strategy color.)
- Element name as text INSIDE the box (must not be cut off).
- The type icon is loaded from its original `_logo.svg` file via `SVGMobject("<path>")`, scaled SMALL, placed in the TOP-RIGHT CORNER of the box with a small margin, with a slightly larger right margin — NOT covering the name/label. DO NOT draw/invent your own icon and DO NOT recolor the logo (show it as is).
- Logo files: `strategy_resource_logo.svg`, `strategy_capability_logo.svg`, `strategy_course_of_action_logo.svg`, `strategy_value_stream_logo.svg`, `business_business_process_logo.svg`, `application_application_component_logo.svg`.
- Cross-layer logo files (connection to the Motivation Layer, scene 05): `motivation_driver_logo.svg`, `motivation_goal_logo.svg`.

RELATIONSHIP = DO NOT load SVG. Draw with Manim's internal methods (`Line` / `DashedLine` + head shapes from `Polygon`/`Triangle`/`Dot`) so they can adapt position, length, and direction between boxes. Line pattern + head shape per ArchiMate notation:
- Assignment: SOLID line; FILLED dot (`Dot`) at the source end; FILLED arrow head at the target.
- Serving: SOLID line; OPEN arrow head (two "V" lines, no fill) at the target.
- Realization: DOTTED line; HOLLOW TRIANGLE (outline) head at the target.
- Influence: DASHED line; OPEN arrow head (V) at the target.
- Composition: SOLID line; FILLED DIAMOND at the source end.
Label the relationship name near the line where it helps.

## 01_introduction (~22s)
Big title "ArchiMate — Strategy Layer" centered on screen + a short subtitle. Below it, line up the four Strategy elements as boxes (per the drawing rules): Resource, Capability, Course of Action, Value Stream — each box in the Strategy color, name inside, logo in the top-right corner. Narration: what the Strategy Layer is, its purpose (high-level direction & strategy), and its position above the Business/Application/Technology layers.

## 02_strategy_elements (~34s)
The four element boxes appear gradually; each box = Strategy color + name inside + logo in the top-right corner + 2 restaurant examples below the box:
- Resource (`strategy_resource_logo.svg`): ID "Armada kurir" | EN "Courier fleet", ID "Aplikasi POS" | EN "POS application".
- Capability (`strategy_capability_logo.svg`): ID "Penjualan online" | EN "Online sales", ID "Layanan delivery" | EN "Delivery service".
- Course of Action (`strategy_course_of_action_logo.svg`): ID "Buka cabang baru" | EN "Open a new branch", ID "Gandeng kurir mitra" | EN "Partner with courier services".
- Value Stream (`strategy_value_stream_logo.svg`): ID "Pesan lalu antar" | EN "Order then deliver", ID "Reservasi meja" | EN "Table reservation".

## 03_relationships_between_elements (~26s)
Connect the Strategy element boxes with RELATIONSHIPS DRAWN by Manim (see the patterns in Preparation); each box = Strategy color + name inside + logo in the top-right corner:
- Resource (`strategy_resource_logo.svg`) ID "Armada kurir" | EN "Courier fleet" —assignment→ Capability (`strategy_capability_logo.svg`) ID "Layanan delivery" | EN "Delivery service" (solid line; dot at the source; filled arrow head at the target).
- Capability (`strategy_capability_logo.svg`) ID "Layanan delivery" | EN "Delivery service" —serving→ Value Stream (`strategy_value_stream_logo.svg`) ID "Pesan lalu antar" | EN "Order then deliver" (solid line; open arrow head).
- Capability (`strategy_capability_logo.svg`) ID "Layanan delivery" | EN "Delivery service" —realization→ Course of Action (`strategy_course_of_action_logo.svg`) ID "Gandeng kurir mitra" | EN "Partner with courier services" (DOTTED line; HOLLOW TRIANGLE head at the Course of Action): the capability realizes (carries out) the course of action. (ArchiMate rule: courses of action are realized BY capabilities; you may NOT point an Influence at a Capability — an Influence's target must be a Motivation element.)

## 04_relationships_between_layers (~24s)
Capability (`strategy_capability_logo.svg`) (Strategy box) is REALIZED by lower-layer elements: Business Process (yellow Business box, `business_business_process_logo.svg`) and Application Component (blue Application box, `application_application_component_logo.svg`). The realization relationship is DRAWN by Manim: DOTTED line with a HOLLOW TRIANGLE head pointing to the Capability. Emphasize: Strategy = "why/direction", the other layers = "how/execution".

## 05_motivation_relationships (~22s)
Connect the Strategy Layer UPWARD to the Motivation Layer — the "why" behind the strategy (complementing the previous scene that went down to Business/Application). Each box = its native layer color + name inside + logo in the top-right corner; all relationships are DRAWN by Manim (see the patterns in Preparation):
- Motivation Driver (PURPLE box, `motivation_driver_logo.svg`) ID "Pendapatan turun" | EN "Declining revenue" —influence→ Motivation Goal (PURPLE box, `motivation_goal_logo.svg`) ID "Tingkatkan pendapatan" | EN "Increase revenue" (DASHED line; OPEN arrow head): the driver motivates the goal.
- Strategy Course of Action (orange box, `strategy_course_of_action_logo.svg`) ID "Buka cabang baru" | EN "Open a new branch" —realization→ Goal (DOTTED line; HOLLOW TRIANGLE head pointing to the Goal): the plan realizes the goal.
- Strategy Capability (orange box, `strategy_capability_logo.svg`) ID "Penjualan online" | EN "Online sales" —realization→ Goal (DOTTED line; HOLLOW TRIANGLE head): the capability realizes the goal.
Emphasize: Strategy elements REALIZE the goal in the Motivation Layer — Motivation = the reason/direction ("why"), Strategy = the high-level way to achieve it.

## 06_case_example (~32s)
A mini restaurant diagram is built gradually; all element boxes + relationships are DRAWN by Manim:
Resource (`strategy_resource_logo.svg`) ID "Armada kurir" | EN "Courier fleet" + ID "Aplikasi POS" | EN "POS application" —assignment→ Capability (`strategy_capability_logo.svg`) ID "Layanan delivery" | EN "Delivery service" —serving→ Value Stream (`strategy_value_stream_logo.svg`) ID "Pesan lalu antar" | EN "Order then deliver"; Capability (`strategy_capability_logo.svg`) ID "Layanan delivery" | EN "Delivery service" —realization→ Course of Action (`strategy_course_of_action_logo.svg`) ID "Gandeng kurir mitra" | EN "Partner with courier services" (DOTTED line; HOLLOW TRIANGLE head at the Course of Action). Use the line patterns + heads per the rules.

## 07_conclusion (~16s)
Show the four Strategy element boxes again (logo in the top-right corner),
- Resource (`strategy_resource_logo.svg`) "Resource"
- Capability (`strategy_capability_logo.svg`) "Capability"
- Course of Action (`strategy_course_of_action_logo.svg`) "Course of Action"
- Value Stream (`strategy_value_stream_logo.svg`) "Value Stream"
- one sentence on the role of each element, then a short closing sentence.
