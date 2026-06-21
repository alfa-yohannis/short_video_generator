---
title: archimate_application_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Application Layer

A short animated tutorial video about the Application Layer in the ArchiMate enterprise-architecture language — the layer that captures the applications and data supporting business processes. Audience: beginners. Style: clean, one idea per screen, smooth transitions.

The English version is entirely in English (including ALL displayed and spoken restaurant examples/labels). The Indonesian version is entirely in Indonesian. The ONLY exception: STANDARD ArchiMate VOCABULARY — terms that the ArchiMate notation itself uses in English — stays the same (in English) in BOTH versions. This covers:
- Product names: "ArchiMate", "The Open Group".
- Layer names: Strategy, Business, Application, Technology, Motivation, Implementation & Migration.
- Aspect names: Active Structure, Behavior, Passive Structure, Motivation.
- Element type names: e.g. Capability, Business Process, Application Component, Node, Goal, Work Package.
- Relationship names: e.g. Realization, Serving, Assignment, Influence, Composition, Association.
ALL other words (ordinary titles, subtitles, narration, explanatory phrases, and restaurant example labels) MUST follow the video's language.

MANDATORY LANGUAGE RULE (to avoid mixing): every displayed example label is written as an `ID "…" | EN "…"` pair. The English version may use ONLY the EN text; the Indonesian version may use ONLY the ID text. NEVER show an Indonesian word in the English video, and vice versa — including text inside boxes, line/relationship labels, titles, subtitles, and the spoken narration.

Consistent example across ALL scenes: a RESTAURANT context (POS app, delivery app, online ordering, payment).

# Preparation
No MCP/Archi needed. Element-type icons are available as `_logo` SVG files in the folder at `assets_dir` (front-matter) together with `manifest.json`; the generator automatically injects the file list + their absolute paths into every scene.

HOW TO DRAW (strict — consistent across all scenes and all effort levels):

ELEMENT = a box (RoundedRectangle) drawn with Manim:
- Box fill color = its native layer color: Application = LIGHT BLUE (light blue / cyan); Business = YELLOW; Technology = GREEN; Motivation = PURPLE; Strategy = ORANGE/YELLOW. (Panel/text accents may use variations of the Application / light blue color.)
- Element name as text INSIDE the box (must not be cut off).
- The type icon is loaded from its original `_logo.svg` file via `SVGMobject("<path>")`, scaled SMALL, placed in the TOP-RIGHT CORNER of the box with a small margin — NOT covering the name/label. DO NOT draw/invent your own icon and DO NOT recolor the logo (show it as is).
- Application logo files: `application_application_component_logo.svg`, `application_application_collaboration_logo.svg`, `application_application_interface_logo.svg`, `application_application_function_logo.svg`, `application_application_interaction_logo.svg`, `application_application_process_logo.svg`, `application_application_event_logo.svg`, `application_application_service_logo.svg`, `application_data_object_logo.svg`.
- Cross-layer logo files (scene 04): `business_business_process_logo.svg`, `business_business_service_logo.svg`, `technology_node_logo.svg`, `technology_system_software_logo.svg`.

RELATIONSHIP = DO NOT load SVG. Draw with Manim's internal methods (`Line` / `DashedLine` + head shapes from `Polygon`/`Triangle`/`Dot`) using the available build-helpers (`archi_element`, `assignment_arrow`, `serving_arrow`, `realization_arrow`, `influence_arrow`, `composition_arrow`, `association_arrow`) so they can adapt position, length, and direction between boxes. Line pattern + head shape per ArchiMate notation:
- Assignment (`assignment_arrow`): SOLID line; FILLED dot (`Dot`) at the source end; FILLED arrow head at the target. Used Application Component —assignment→ Application Function.
- Realization (`realization_arrow`): DOTTED line; HOLLOW TRIANGLE (outline) head at the target. Used Application Function —realization→ Application Service, and Application Component —realization→ Application Service.
- Serving (`serving_arrow`): SOLID line; OPEN arrow head (two "V" lines, no fill) at the target. Used Application Service —serving→ Business Process.
- Composition (`composition_arrow`): SOLID line; FILLED DIAMOND at the source end (whole). Used to group functions/components, and for a Component composed of its Interface (the access point) — Component —composition→ Interface.
- Association (`association_arrow`): plain SOLID line (no head, or a small open arrow).
- Influence (`influence_arrow`): DASHED line; OPEN arrow head (V) at the target.
- Access (for reading/writing a Data Object): DOTTED line with a SMALL OPEN arrow head at the Data Object. Used Application Function —access→ Data Object.
Label the relationship name near the line where it helps.

## 01_layer_position (~18s)
Big title "ArchiMate — Application Layer" centered + a short subtitle "the apps & data that run the business". Draw the ArchiMate framework as stacked colored bands — Business yellow on the top band, Application light blue on the middle band, Technology green on the bottom band. HIGHLIGHT the light blue Application band in the middle and emphasize its position: Application sits BELOW Business and ABOVE Technology — applications support business processes while being supported by technology. Brief narration: what the Application Layer is and its role as the connector.

## 02_element_vocabulary (~34s)
Element boxes appear gradually; each box = Application color (light blue) + name inside + logo in the top-right corner + restaurant example below the box:
- Application Component (`application_application_component_logo.svg`): ID "Aplikasi POS" | EN "POS App", ID "Aplikasi Delivery" | EN "Delivery App".
- Application Service (`application_application_service_logo.svg`): ID "Layanan Pemesanan Online" | EN "Online Ordering Service".
- Application Function (`application_application_function_logo.svg`): ID "Proses Pembayaran" | EN "Payment Processing".
- Application Interface (`application_application_interface_logo.svg`): ID "API Pembayaran" | EN "Payment API".
- Application Collaboration (`application_application_collaboration_logo.svg`): two application components working together.
- Application Process (`application_application_process_logo.svg`): a sequence of steps inside the application.
- Application Event (`application_application_event_logo.svg`): an occurrence that triggers the application.
- Data Object (`application_data_object_logo.svg`): ID "Data Pesanan" | EN "Order Data", ID "Data Menu" | EN "Menu Data".
Reveal them gradually so the screen does not get crowded; use ACCENT emphasis on the difference between Component (structure) vs Function/Service (behavior) vs Data Object (information).

## 03_relationships_between_elements (~30s)
Connect the Application element boxes with RELATIONSHIPS DRAWN by Manim (see the patterns in Preparation); each box = Application light blue color + name inside + logo in the top-right corner; label each line:
- Application Component (`application_application_component_logo.svg`) ID "Aplikasi POS" | EN "POS App" —assignment→ Application Function (`application_application_function_logo.svg`) ID "Proses Pembayaran" | EN "Payment Processing" (solid line; dot at the source; filled arrow at the target): the component performs the function.
- Application Function (`application_application_function_logo.svg`) ID "Proses Pembayaran" | EN "Payment Processing" —realization→ Application Service (`application_application_service_logo.svg`) ID "Layanan Pemesanan Online" | EN "Online Ordering Service" (dotted line; hollow triangle at the target): the function realizes the service.
- Application Function (`application_application_function_logo.svg`) ID "Proses Pembayaran" | EN "Payment Processing" —access→ Data Object (`application_data_object_logo.svg`) ID "Data Pesanan" | EN "Order Data" (dotted line; SMALL open arrow at the Data Object): the function reads/writes data.
HIGHLIGHT the chain Component → Function → Service as the core pattern, and emphasize access as the way the application touches data.

## 04_relationships_between_layers (~32s)
A cross-layer scene — Application as the connector between Business (above) and Technology (below). Each box = its native layer color + name inside + logo in the top-right corner; all relationships are DRAWN by Manim (see the patterns in Preparation):
- UPWARD: Application Service (Application light blue box, `application_application_service_logo.svg`) ID "Layanan Pemesanan Online" | EN "Online Ordering Service" —serving→ Business Process (Business yellow box, `business_business_process_logo.svg`) ID "Menerima Pesanan" | EN "Receive Order" (solid line; OPEN arrow head pointing to the Business Process): the application service serves the business process. (Add Business Service `business_business_service_logo.svg` as upper context if it helps.)
- DOWNWARD: Technology Node (Technology green box, `technology_node_logo.svg`) ID "Server Restoran" | EN "Restaurant Server" —serving→ Application Component (Application light blue box, `application_application_component_logo.svg`) ID "Aplikasi POS" | EN "POS App" (SOLID line; OPEN arrow head pointing to the Application Component); and Technology System Software (Technology green box, `technology_system_software_logo.svg`) ID "Database Engine" | EN "Database Engine" —serving→ Application Component ID "Aplikasi POS" | EN "POS App" (SOLID line; OPEN arrow head). Technology SERVES (supports) the application. (ArchiMate rule: a Node/System Software does NOT *realize* an Application Component — it serves it; only a deployed Artifact realizes a component.)
Emphasize (PRIMARY): Application = "apps & data", serving Business above and supported by Technology below.

## 05_case_example (~26s)
A mini restaurant application diagram built up gradually; all element boxes + relationships are DRAWN by Manim, each box = Application light blue color + name inside + logo in the top-right corner:
Application Component (`application_application_component_logo.svg`) ID "Aplikasi Delivery" | EN "Delivery App" —assignment→ Application Function (`application_application_function_logo.svg`) ID "Proses Pembayaran" | EN "Payment Processing"; Application Function —realization→ Application Service (`application_application_service_logo.svg`) ID "Layanan Pemesanan Online" | EN "Online Ordering Service"; Application Function —access→ Data Object (`application_data_object_logo.svg`) ID "Data Pesanan" | EN "Order Data" (dotted, small open arrow) and Data Object (`application_data_object_logo.svg`) ID "Data Menu" | EN "Menu Data"; then Application Component (`application_application_component_logo.svg`) ID "Aplikasi Delivery" | EN "Delivery App" —composition→ Application Interface (`application_application_interface_logo.svg`) ID "API Pembayaran" | EN "Payment API" (SOLID line; FILLED DIAMOND at the Component): the component is composed of (exposes) its interface — the access point. (An interface belongs to its component via composition; it is NOT assigned to it.) Use the line patterns + heads per the rules, arranged gradually so the flow Component → Function → Service + data reads clearly.

## 06_conclusion (~16s)
Recap: Application Layer = the applications & data that support the business. Show the key element boxes again (Application light blue color + logo in the top-right corner):
- Application Component (`application_application_component_logo.svg`) "Component"
- Application Service (`application_application_service_logo.svg`) "Service"
- Application Function (`application_application_function_logo.svg`) "Function"
- Application Interface (`application_application_interface_logo.svg`) "Interface"
- Data Object (`application_data_object_logo.svg`) "Data Object"
One sentence on the role of each element, then close with the chain on screen: Component → Function → Service —serving→ Business; supported by Technology below.
