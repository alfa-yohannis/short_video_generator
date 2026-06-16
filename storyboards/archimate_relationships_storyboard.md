---
title: archimate_relationships
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Relationships

A short animated tutorial video about Relationships (Connectors) in the ArchiMate enterprise-architecture language — the lines that connect elements and give the model meaning. Audience: beginners. Style: clean, one idea per screen, smooth transitions.

The English version is entirely in English (including ALL displayed and spoken restaurant examples/labels). The Indonesian version is entirely in Indonesian. The ONLY exception: STANDARD ArchiMate VOCABULARY — terms that the ArchiMate notation itself uses in English — stays the same (in English) in BOTH versions. This covers:
- Product names: "ArchiMate", "The Open Group".
- Layer names: Strategy, Business, Application, Technology, Motivation, Implementation & Migration.
- Aspect names: Active Structure, Behavior, Passive Structure, Motivation.
- Element type names: e.g. Capability, Business Process, Application Component, Node, Goal, Work Package.
- Relationship names: e.g. Realization, Serving, Assignment, Influence, Composition, Association.
ALL other words (ordinary titles, subtitles, narration, explanatory phrases, and restaurant example labels) MUST follow the video's language.

MANDATORY LANGUAGE RULE (to avoid mixing): every displayed example label is written as an `ID "…" | EN "…"` pair. The English version may use ONLY the EN text; the Indonesian version may use ONLY the ID text. NEVER show an Indonesian word in the English video, and vice versa — including text inside boxes, line/relationship labels, titles, subtitles, and the spoken narration.

Consistent example across ALL scenes: a RESTAURANT context (kitchen process, waiter, online ordering system, delivery service).

# Preparation
No MCP/Archi needed. Element-type icons are available as `_logo` SVG files in the folder at `assets_dir` (front-matter) together with `manifest.json`; the generator automatically injects the file list + their absolute paths into every scene.

IMPORTANT — the focus of this video is RELATIONSHIPS (connectors), i.e. the LINES between elements, NOT the elements themselves. A relationship has NO `_logo.svg` file and is NEVER loaded from SVG. Every relationship is ALWAYS DRAWN with Manim (`Line` / `DashedLine` / `DottedLine` + head/end shapes from `Polygon` / `Triangle` / `Dot`). DO NOT reference any relationship logo. SVG logos are only used for the small demo boxes that the lines connect.

HOW TO DRAW (strict — consistent across all scenes and all effort levels):

DEMO BOX = a box (RoundedRectangle) drawn with Manim, just two endpoints to show off one relationship:
- Box fill color = its native layer color: Business = YELLOW; Application = LIGHT BLUE; Technology = GREEN; Motivation = PURPLE; Strategy = ORANGE/golden yellow. (Panel/text accents may use variations of the HIGHLIGHT/ACCENT color.)
- Element name as text INSIDE the box (must not be cut off).
- The type icon is loaded from its original `_logo.svg` file via `SVGMobject("<path>")`, scaled SMALL, placed in the TOP-RIGHT CORNER of the box with a small margin — NOT covering the name/label. DO NOT draw/invent your own icon and DO NOT recolor the logo (show it as is).
- Element logo files used for the demo boxes (ONLY these): `business_business_process_logo.svg`, `business_business_actor_logo.svg`, `business_business_object_logo.svg`, `business_business_service_logo.svg`, `application_application_component_logo.svg`, `application_application_service_logo.svg`, `application_data_object_logo.svg`, `technology_node_logo.svg`, `motivation_driver_logo.svg`, `motivation_goal_logo.svg` (the last two — PURPLE motivation boxes — are used only for the Influence example, whose target must be a Motivation element).

RELATIONSHIP = DO NOT load SVG. ALWAYS draw with Manim's internal methods so they can adapt position, length, and direction between boxes. Direction convention: SOURCE = the origin box (often where the diamond/dot attaches), TARGET = the destination box (often where the arrow head/triangle attaches). Line pattern + end shape per ArchiMate notation — document EVERY relationship here:

STRUCTURAL (how elements are composed / assigned):
- Composition: SOLID line (`Line`); FILLED DIAMOND (`Polygon` with 4 points, fully filled, PRIMARY color) attached at the SOURCE end. (helper: `composition_arrow`) Meaning: a part belongs to a whole; the part cannot exist apart from its owner.
- Aggregation: SOLID line (`Line`); HOLLOW DIAMOND (`Polygon` with 4 points, outline only, no fill) attached at the SOURCE end. Meaning: a grouping; the part can stand on its own.
- Assignment: SOLID line (`Line`); FILLED dot (`Dot`) attached at the SOURCE end + FILLED arrow head (`Triangle`/`Polygon` triangle, fully filled) at the TARGET end. (helper: `assignment_arrow`) Meaning: active assignment (who performs what).
- Realization: DOTTED line (`DottedLine`); HOLLOW TRIANGLE head (`Triangle`, outline only, no fill) at the TARGET end. (helper: `realization_arrow`) Meaning: something realizes/makes concrete a more abstract thing.

DEPENDENCY (how elements depend on / are served by each other):
- Serving: SOLID line (`Line`); OPEN arrow head (two "V" lines, no fill) at the TARGET end. (helper: `serving_arrow`) Meaning: one element serves/provides a function to another.
- Access: DOTTED line (`DottedLine`); SMALL OPEN arrow head (small V) at the TARGET end (the arrow direction indicates read/write). Meaning: behavior accessing data/objects.
- Influence: DASHED line (`DashedLine`); OPEN arrow head (V) at the TARGET end; optional small "+" or "−" label near the line. (helper: `influence_arrow`) Meaning: something influences (positively/negatively) another.

DYNAMIC (how sequence/flow runs):
- Triggering: SOLID line (`Line`); FILLED arrow head (fully filled triangle) at the TARGET end. Meaning: causal/temporal sequence — one triggers the next. (Distinguish from Assignment: Triggering has NO dot at the SOURCE.)
- Flow: DASHED line (`DashedLine`); FILLED arrow head (fully filled triangle) at the TARGET end. Meaning: a flow of information/value/goods from one to another.

OTHER:
- Specialization: SOLID line (`Line`); HOLLOW TRIANGLE head (`Triangle`, outline only, no fill) at the TARGET end (the parent). Meaning: "is a kind of" (is-a). (Distinguish from Realization, whose line is DOTTED.)
- Association: plain SOLID line (`Line`) with no head, or an optional SMALL OPEN arrow at one end. (helper: `association_arrow`) Meaning: a general relationship not covered by the other types.
- Junction: NOT a full line, but a small NODE — a SMALL FILLED circle (`Dot`, AND) or a SMALL HOLLOW circle (small `Circle` outline, OR) — where several relationships of the same kind meet/branch. Draw it as a connecting point at the junction of several lines.

Label the relationship name near the line where it helps. Use semantic colors (DANGER/OK/HIGHLIGHT/PRIMARY/ACCENT) only for emphasis, not to replace the meaning of the notation.

## 01_why_notation_matters (~18s)
Big title "ArchiMate — Relationships" centered + subtitle "the lines that give the model meaning". Show two plain demo boxes (Business YELLOW) with a single line between them, then emphasize: the line itself carries meaning — the line style (solid / dashed / dotted) and the end shape (diamond / dot / triangle / arrow) determine the MEANING of the relationship. Quick preview: cycle through the three line styles (solid, dashed, dotted) then the three end shapes. Emphasize that a relationship is a CONNECTOR, not an element — always drawn, never has a logo. Highlight the message with HIGHLIGHT color.

## 02_structural_relationships (~32s)
Introduce the STRUCTURAL family one by one; each pair = two demo boxes (layer color + name inside + logo in the top-right corner) connected by a relationship DRAWN by Manim per the patterns in Preparation; label the relationship name near the line:
- Composition: Business Process (`business_business_process_logo.svg`) ID "Layani Pelanggan" | EN "Serve Customer" —composition→ Business Process (`business_business_process_logo.svg`) ID "Memasak" | EN "Cooking" (SOLID line; FILLED DIAMOND attached at the SOURCE ID "Layani Pelanggan" | EN "Serve Customer"). Meaning: cooking is an integral part of the overall serve-customer process — the part cannot stand on its own. (Note: a Service is REALIZED by a Process, so don't compose a Service out of a Process.)
- Aggregation: Business Object (`business_business_object_logo.svg`) ID "Paket Menu" | EN "Menu Package" —aggregation→ Business Object (`business_business_object_logo.svg`) ID "Menu Item" | EN "Menu Item" (SOLID line; HOLLOW DIAMOND at the SOURCE). Meaning: a loose grouping; the item can stand on its own.
- Assignment: Business Actor (`business_business_actor_logo.svg`) ID "Pelayan" | EN "Waiter" —assignment→ Business Process (`business_business_process_logo.svg`) ID "Menyajikan" | EN "Serving" (SOLID line; FILLED dot at the SOURCE ID "Pelayan" | EN "Waiter" + FILLED arrow head at the TARGET). Mention the helper `assignment_arrow`.
- Realization: Application Component (`application_application_component_logo.svg`) ID "Aplikasi Pemesanan" | EN "Ordering App" —realization→ Application Service (`application_application_service_logo.svg`) ID "Layanan Pemesanan Online" | EN "Online Ordering Service" (DOTTED line; HOLLOW TRIANGLE at the TARGET). Mention the helper `realization_arrow`. Emphasize that the diamond fill (filled vs hollow) is what tells Composition from Aggregation.

## 03_dependency_relationships (~26s)
Introduce the DEPENDENCY family; each pair = two demo boxes + a relationship DRAWN by Manim; label near the line:
- Serving: Application Service (`application_application_service_logo.svg`) ID "Layanan Pemesanan Online" | EN "Online Ordering Service" —serving→ Business Process (`business_business_process_logo.svg`) ID "Menerima Pesanan" | EN "Receive Order" (SOLID line; OPEN "V" arrow head at the TARGET). Mention the helper `serving_arrow`. Meaning: the service serves the process.
- Access: Business Process (`business_business_process_logo.svg`) ID "Menerima Pesanan" | EN "Receive Order" —access→ Data Object (`application_data_object_logo.svg`) ID "Data Pesanan" | EN "Order Data" (DOTTED line; SMALL OPEN arrow head at the TARGET). Meaning: the process reads/writes the data.
- Influence: Driver (`motivation_driver_logo.svg`) ID "Persaingan" | EN "Competition" —influence→ Goal (`motivation_goal_logo.svg`) ID "Tingkatkan pendapatan" | EN "Increase revenue" (DASHED line; OPEN "V" arrow head at the TARGET Goal; show a small "+/−" label). Mention the helper `influence_arrow`. IMPORTANT: an Influence relationship's TARGET must always be a Motivation element (Goal, Requirement, Outcome, Principle, …) — that is why it points at a Goal, NOT at a Business Service or a Capability. Emphasize: dependency = "who needs/influences whom".

## 04_dynamic_relationships (~24s)
Introduce the DYNAMIC family (sequence & flow); each pair = two demo boxes + a relationship DRAWN by Manim; label near the line:
- Triggering: Business Process (`business_business_process_logo.svg`) ID "Menerima Pesanan" | EN "Receive Order" —triggering→ Business Process (`business_business_process_logo.svg`) ID "Memasak" | EN "Cooking" (SOLID line; FILLED arrow head at the TARGET; NO dot at the SOURCE). Meaning: a step triggers the next step in sequence.
- Flow: Business Process (`business_business_process_logo.svg`) ID "Memasak" | EN "Cooking" —flow→ Business Process (`business_business_process_logo.svg`) ID "Mengantar" | EN "Delivering" (DASHED line; FILLED arrow head at the TARGET). Meaning: something (food/information) flows between steps. Place Triggering vs Flow side by side and highlight the difference in line style (SOLID vs DASHED) with ACCENT color.

## 05_other_relationships (~24s)
Introduce the OTHER family; each pair = two demo boxes + a relationship DRAWN by Manim; label near the line:
- Specialization: Business Process (`business_business_process_logo.svg`) ID "Pesan Antar" | EN "Delivery Order" —specialization→ Business Process (`business_business_process_logo.svg`) ID "Layani Pesanan" | EN "Serve Order" (SOLID line; HOLLOW TRIANGLE at the TARGET/parent). Meaning: "is a kind of". Emphasize the difference from Realization: here the line is SOLID, while Realization is DOTTED.
- Association: Business Actor (`business_business_actor_logo.svg`) ID "Pelanggan" | EN "Customer" —association→ Business Service (`business_business_service_logo.svg`) ID "Layanan Restoran" | EN "Restaurant Service" (plain SOLID line; optional SMALL OPEN arrow). Mention the helper `association_arrow`. Meaning: a general relationship.
- Junction: show two Triggering lines from Business Process (`business_business_process_logo.svg`) ID "Bayar" | EN "Pay" and Business Process ID "Konfirmasi" | EN "Confirm" meeting at a JUNCTION (a SMALL FILLED circle = AND), then one Triggering line continuing to Business Process ID "Cetak Struk" | EN "Print Receipt". Emphasize that a Junction joins/branches several relationships of the same kind (draw it as a small `Dot` at the junction).

## 06_restaurant_mini_diagram (~30s)
A restaurant mini-diagram built up step by step using several relationships at once; all demo boxes + relationships DRAWN by Manim per the patterns in Preparation:
- Business Actor (`business_business_actor_logo.svg`) ID "Pelanggan" | EN "Customer" —serving← Application Service (`application_application_service_logo.svg`) ID "Layanan Pemesanan Online" | EN "Online Ordering Service" (the service serves the customer; OPEN arrow head at the TARGET, the customer).
- Application Component (`application_application_component_logo.svg`) ID "Aplikasi Pemesanan" | EN "Ordering App" —realization→ Application Service (`application_application_service_logo.svg`) ID "Layanan Pemesanan Online" | EN "Online Ordering Service" (DOTTED line; HOLLOW TRIANGLE at the TARGET): the component realizes the service it exposes.
- Application Service ID "Layanan Pemesanan Online" | EN "Online Ordering Service" —serving→ Business Process (`business_business_process_logo.svg`) ID "Menerima Pesanan" | EN "Receive Order".
- Business Process ID "Menerima Pesanan" | EN "Receive Order" —triggering→ Business Process (`business_business_process_logo.svg`) ID "Memasak" | EN "Cooking" —flow→ Business Process (`business_business_process_logo.svg`) ID "Mengantar" | EN "Delivering" (triggering SOLID with FILLED arrow; flow DASHED with FILLED arrow).
- Business Process ID "Menerima Pesanan" | EN "Receive Order" —access→ Data Object (`application_data_object_logo.svg`) ID "Data Pesanan" | EN "Order Data" (DOTTED line, small open arrow).
- Technology Node (`technology_node_logo.svg`) ID "Server" | EN "Server" —serving→ Application Component ID "Aplikasi Pemesanan" | EN "Ordering App" (SOLID line; OPEN arrow head at the component): the node serves/runs the component — Technology SERVES Application (not assignment). Emphasize: it is this combination of relationships that lets the model tell a complete story.

## 07_recap_cheat_sheet (~22s)
Close with a cheat-sheet of all the relationships — each row = a short line segment DRAWN by Manim with its end shape + name:
- Composition: SOLID line + FILLED diamond.
- Aggregation: SOLID line + HOLLOW diamond.
- Assignment: SOLID line + FILLED dot at the source + FILLED arrow.
- Realization: DOTTED line + HOLLOW triangle.
- Serving: SOLID line + OPEN arrow.
- Access: DOTTED line + SMALL open arrow.
- Influence: DASHED line + OPEN arrow (+/−).
- Triggering: SOLID line + FILLED arrow.
- Flow: DASHED line + FILLED arrow.
- Specialization: SOLID line + HOLLOW triangle.
- Association: plain SOLID line.
- Junction: small circle (FILLED = AND, HOLLOW = OR).
Closing message: remember two things — LINE STYLE (solid/dashed/dotted) and END SHAPE (diamond/ball/triangle/arrow); that is what distinguishes each relationship. Highlight the summary with HIGHLIGHT color.
