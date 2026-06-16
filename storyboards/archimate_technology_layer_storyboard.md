---
title: archimate_technology_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Technology Layer

A short animated tutorial video about the Technology Layer in the ArchiMate enterprise-architecture language — the foundation layer that provides the infrastructure (hardware, system software, and networks) for the layers above it, including Physical elements for the real-world side. Audience: beginners. Style: clean, one idea per screen, smooth transitions.

The English version is entirely in English (including ALL displayed and spoken restaurant examples/labels). The Indonesian version is entirely in Indonesian. The ONLY exception: STANDARD ArchiMate VOCABULARY — terms that the ArchiMate notation itself uses in English — stays the same (in English) in BOTH versions. This covers:
- Product names: "ArchiMate", "The Open Group".
- Layer names: Strategy, Business, Application, Technology, Motivation, Implementation & Migration.
- Aspect names: Active Structure, Behavior, Passive Structure, Motivation.
- Element type names: e.g. Capability, Business Process, Application Component, Node, Goal, Work Package.
- Relationship names: e.g. Realization, Serving, Assignment, Influence, Composition, Association.
ALL other words (ordinary titles, subtitles, narration, explanatory phrases, and restaurant example labels) MUST follow the video's language.

MANDATORY LANGUAGE RULE (to avoid mixing): every displayed example label is written as an `ID "…" | EN "…"` pair. The English version may use ONLY the EN text; the Indonesian version may use ONLY the ID text. NEVER show an Indonesian word in the English video, and vice versa — including text inside boxes, line/relationship labels, titles, subtitles, and the spoken narration.

Consistent example across ALL scenes: a RESTAURANT that runs an online service (server, database, POS tablet, delivery app, internet network) together with its physical side (kitchen, oven, food ingredients, delivery routes).

# Preparation
No MCP/Archi needed. Element-type icons are available as `_logo` SVG files in the folder at `assets_dir` (front-matter) together with `manifest.json`; the generator automatically injects the file list + their absolute paths into every scene.

HOW TO DRAW (strict — consistent across all scenes and all effort levels):

ELEMENT = a box (RoundedRectangle) drawn with Manim:
- Box fill color = its native layer color: Technology = GREEN; Physical elements are ALSO green (part of the Technology Layer); Application = LIGHT BLUE; Business = YELLOW; Strategy = ORANGE/YELLOW; Motivation = PURPLE. (Panel/text accents may use variations of the Technology/green color.)
- Element name as text INSIDE the box (must not be cut off).
- The type icon is loaded from its original `_logo.svg` file via `SVGMobject("<path>")`, scaled SMALL, placed in the TOP-RIGHT CORNER of the box with a small margin — NOT covering the name/label. DO NOT draw/invent your own icon and DO NOT recolor the logo (show it as is).
- Technology logo files: `technology_node_logo.svg`, `technology_device_logo.svg`, `technology_system_software_logo.svg`, `technology_technology_collaboration_logo.svg`, `technology_technology_interface_logo.svg`, `technology_path_logo.svg`, `technology_communication_network_logo.svg`, `technology_technology_function_logo.svg`, `technology_technology_process_logo.svg`, `technology_technology_interaction_logo.svg`, `technology_technology_event_logo.svg`, `technology_technology_service_logo.svg`, `technology_artifact_logo.svg`.
- Physical logo files (green color, part of this layer): `physical_equipment_logo.svg`, `physical_facility_logo.svg`, `physical_distribution_network_logo.svg`, `physical_material_logo.svg`.
- Cross-layer logo file (connection to the Application Layer, scene 05): `application_application_component_logo.svg`.

RELATIONSHIP = DO NOT load SVG. Draw with Manim's internal methods (`Line` / `DashedLine` + head shapes from `Polygon`/`Triangle`/`Dot`) using the available build-helpers (`archi_element`, `assignment_arrow`, `serving_arrow`, `realization_arrow`, `influence_arrow`, `composition_arrow`, `association_arrow`) so they can adapt position, length, and direction between boxes. Line pattern + head shape per ArchiMate notation:
- Assignment: SOLID line; FILLED dot (`Dot`) at the source end; FILLED arrow head at the target. Used for DEPLOYMENT: Node —assignment→ Artifact — the NODE (active structure) is the SOURCE (filled dot at the Node) and the Artifact (passive structure) is the TARGET (arrow head). (ArchiMate rule: assignment runs active→passive, so the arrow points FROM the Node TO the Artifact — NOT Artifact→Node.)
- Composition: SOLID line; FILLED DIAMOND at the source end. Used for: a Facility composed of its Equipment; a Node composed of its constituent Devices/System Software. (Do NOT compose two separate machines that are merely network-connected — use Association for that.)
- Serving: SOLID line; OPEN arrow head (two "V" lines, no fill) at the target. Used for: Node / Technology Service —serving→ Application Component (technology SERVES the application).
- Realization: DOTTED line; HOLLOW TRIANGLE (outline) head at the target. Used for: Artifact —realization→ Application Component (the deployed artifact realizes the component); Artifact / Node —realization→ Technology Service. (A Node or System Software does NOT *realize* an Application Component — it serves it.)
- Association: plain SOLID line (no head, or a small open arrow). Used for a neutral link between elements (e.g. Path & Communication Network, Equipment & Material).
- Influence: DASHED line; OPEN arrow head (V) at the target. (Spare, if you need to mark an influence.)
Label the relationship name near the line where it helps.

## 01_layer_position (~18s)
Big title "ArchiMate — Technology Layer" centered + subtitle "the foundation that runs everything". Draw the ArchiMate framework as a stack of colored bands — Motivation purple, Strategy orange, Business yellow, Application light blue — then reveal Technology as the GREEN band at the very BOTTOM that supports everything. Highlight the green band and emphasize it with HIGHLIGHT color: the Technology Layer is the foundation (hardware, system software, and network infrastructure) that sits below the Application Layer and runs everything above it. Mention that Physical elements also live here for the real world (kitchen, oven, ingredients).

## 02_technology_vocabulary (~30s)
Introduce the core Technology vocabulary; each GREEN box + name inside + logo in the top-right corner + restaurant example, revealed gradually (arrange so it doesn't get crowded):
- Node (`technology_node_logo.svg`) ID "Server Cloud" | EN "Cloud Server": a compute unit where software runs.
- Device (`technology_device_logo.svg`) ID "Tablet Kasir" | EN "POS Tablet": physical hardware.
- System Software (`technology_system_software_logo.svg`) ID "Database" | EN "Database" and ID "Sistem Operasi" | EN "Operating System": system software.
- Technology Service (`technology_technology_service_logo.svg`) ID "Layanan Hosting" | EN "Hosting Service": a technology capability offered to the layers above. Mark it with ACCENT color.
- Artifact (`technology_artifact_logo.svg`) ID "delivery-app.jar" | EN "delivery-app.jar": a deployed file that represents an application component.
- Communication Network (`technology_communication_network_logo.svg`) ID "Internet" | EN "Internet": the network that connects the nodes.
- Technology Function (`technology_technology_function_logo.svg`) ID "Pemrosesan Pesanan" | EN "Order Processing": internal behavior performed by a node.

## 03_physical_elements (~28s)
Introduce the PHYSICAL elements — part of the Technology Layer but for the physical world; each GREEN box + name inside + logo in the top-right corner + restaurant example:
- Facility (`physical_facility_logo.svg`) ID "Dapur Pusat" | EN "Central Kitchen": a physical facility (the Node analog for the physical world). Mark it with PRIMARY color.
- Equipment (`physical_equipment_logo.svg`) ID "Oven" | EN "Oven" and ID "Kompor" | EN "Stove": physical equipment (the Device analog).
- Material (`physical_material_logo.svg`) ID "Bahan Makanan" | EN "Food Ingredients": tangible material that is processed/moved.
- Distribution Network (`physical_distribution_network_logo.svg`) ID "Rute Pengantaran" | EN "Delivery Route": a physical distribution network (the Communication Network analog).
Show the links DRAWN by Manim: Facility ID "Dapur Pusat" | EN "Central Kitchen" —composition→ Equipment ID "Oven" | EN "Oven" (solid line; filled diamond at the Facility source); Equipment ID "Oven" | EN "Oven" —association→ Material ID "Bahan Makanan" | EN "Food Ingredients"; Material —association→ Distribution Network ID "Rute Pengantaran" | EN "Delivery Route". Emphasize: Physical is the physical mirror of the digital Technology concepts.

## 04_relationships_between_elements (~26s)
Connect the Technology boxes with RELATIONSHIPS DRAWN by Manim (see the patterns in Preparation); each box = GREEN color + name inside + logo in the top-right corner:
- Node (`technology_node_logo.svg`) ID "Server Cloud" | EN "Cloud Server" —composition→ System Software (`technology_system_software_logo.svg`) ID "Database" | EN "Database" (solid line; filled diamond at the Node source): the node is composed of (hosts) its system software. (A Node consists of its System Software — this is composition; assignment between two active-structure elements is not valid.)
- Node ID "Server Cloud" | EN "Cloud Server" —assignment→ Artifact (`technology_artifact_logo.svg`) ID "delivery-app.jar" | EN "delivery-app.jar" (solid line; filled dot at the Node source; filled arrow head at the Artifact): the artifact is DEPLOYED on the node. (Direction: the Node — active structure — is the source; the Artifact — passive structure — is the target.)
- Node ID "Server Cloud" | EN "Cloud Server" —association→ Device (`technology_device_logo.svg`) ID "Tablet Kasir" | EN "POS Tablet" (plain solid line): the tablet is a SEPARATE device connected to the server over the network — not a part of it (so it is an Association, not a Composition).
- Node ID "Server Cloud" | EN "Cloud Server" —realization→ Technology Service (`technology_technology_service_logo.svg`) ID "Layanan Hosting" | EN "Hosting Service" (dotted line; hollow triangle at the target): the node realizes the technology service used by the layers above.

## 05_application_relationships (~24s)
Connect the Technology Layer UP to the Application Layer — how the foundation runs the system. Each box = its native layer color + name inside + logo in the top-right corner; all relationships DRAWN by Manim (see the patterns in Preparation):
- Technology Service (`technology_technology_service_logo.svg`) (GREEN box) ID "Layanan Hosting" | EN "Hosting Service" —serving→ Application Component (`application_application_component_logo.svg`) (LIGHT BLUE box) ID "Aplikasi Delivery" | EN "Delivery App" (solid line; open arrow head): the technology service serves the application component.
- Node (`technology_node_logo.svg`) (GREEN box) ID "Server Cloud" | EN "Cloud Server" —serving→ Application Component ID "Aplikasi Delivery" | EN "Delivery App" (solid line; open arrow head): the infrastructure SERVES (runs/supports) the application component. (NOT realization — a Node serves a component, it does not realize it.)
- Artifact (`technology_artifact_logo.svg`) (GREEN box) ID "delivery-app.jar" | EN "delivery-app.jar" —realization→ Application Component ID "Aplikasi Delivery" | EN "Delivery App" (dotted line; hollow triangle at the target): the deployed ARTIFACT realizes the application component — this is the one correct realization across the Technology→Application boundary.
Emphasize with HIGHLIGHT color: Technology = the foundation / "what it runs on" (it SERVES the application); only the deployed Artifact REALIZES the application component.

## 06_case_example (~30s)
A mini restaurant diagram built up gradually; all element boxes + relationships DRAWN by Manim (use the line patterns + heads per the rules):
Node (`technology_node_logo.svg`) ID "Server Cloud" | EN "Cloud Server" —composition→ System Software (`technology_system_software_logo.svg`) ID "Database" | EN "Database" (the node is composed of its system software), and Node ID "Server Cloud" | EN "Cloud Server" —assignment→ Artifact (`technology_artifact_logo.svg`) ID "delivery-app.jar" | EN "delivery-app.jar" (deployed; filled dot at the Node source, arrow head at the Artifact). ID "Server Cloud" | EN "Cloud Server" is connected to Device (`technology_device_logo.svg`) ID "Tablet Kasir" | EN "POS Tablet" via Communication Network (`technology_communication_network_logo.svg`) ID "Internet" | EN "Internet" (association — the tablet is a separate device on the network, not a part of the server). ID "Server Cloud" | EN "Cloud Server" —realization→ Technology Service (`technology_technology_service_logo.svg`) ID "Layanan Hosting" | EN "Hosting Service" —serving→ Application Component (`application_application_component_logo.svg`) (LIGHT BLUE box) ID "Aplikasi Delivery" | EN "Delivery App". On the physical side, Facility (`physical_facility_logo.svg`) ID "Dapur Pusat" | EN "Central Kitchen" —composition→ Equipment (`physical_equipment_logo.svg`) ID "Oven" | EN "Oven", which processes Material (`physical_material_logo.svg`) ID "Bahan Makanan" | EN "Food Ingredients" (association). Emphasize: one picture shows both the digital AND physical foundation of the restaurant supporting the application above it.

## 07_conclusion (~16s)
Show the core boxes again (logo in the top-right corner) as a recap:
- Node (`technology_node_logo.svg`) "Node"
- Device (`technology_device_logo.svg`) "Device"
- System Software (`technology_system_software_logo.svg`) "System Software"
- Technology Service (`technology_technology_service_logo.svg`) "Technology Service"
- Artifact (`technology_artifact_logo.svg`) "Artifact"
- Communication Network (`technology_communication_network_logo.svg`) "Communication Network"
- Facility (`physical_facility_logo.svg`) "Facility" + Equipment (`physical_equipment_logo.svg`) "Equipment" + Material (`physical_material_logo.svg`) "Material" + Distribution Network (`physical_distribution_network_logo.svg`) "Distribution Network" (the Physical side).
One sentence on the role of each group, then a short closing sentence: the Technology Layer (including Physical) is the foundation that runs and supports the whole architecture. Close with the chain on screen: Node → Technology Service → Application Component.
