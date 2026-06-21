---
title: archimate_business_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Business Layer

A short animated tutorial video about the Business Layer in the ArchiMate enterprise-architecture language — the layer that captures "what" the organization does: the actors, roles, processes, and services delivered to customers. Audience: beginners. Style: clean, one idea per screen, smooth transitions.

The English version is entirely in English (including ALL displayed and spoken restaurant examples/labels). The Indonesian version is entirely in Indonesian. The ONLY exception: STANDARD ArchiMate VOCABULARY — terms that the ArchiMate notation itself uses in English — stays the same (in English) in BOTH versions. This covers:
- Product names: "ArchiMate", "The Open Group".
- Layer names: Strategy, Business, Application, Technology, Motivation, Implementation & Migration.
- Aspect names: Active Structure, Behavior, Passive Structure, Motivation.
- Element type names: e.g. Capability, Business Process, Application Component, Node, Goal, Work Package.
- Relationship names: e.g. Realization, Serving, Assignment, Influence, Composition, Association.
ALL other words (ordinary titles, subtitles, narration, explanatory phrases, and restaurant example labels) MUST follow the video's language.

MANDATORY LANGUAGE RULE (to avoid mixing): every displayed example label is written as an `ID "…" | EN "…"` pair. The English version may use ONLY the EN text; the Indonesian version may use ONLY the ID text. NEVER show an Indonesian word in the English video, and vice versa — including text inside boxes, line/relationship labels, titles, subtitles, and the spoken narration.

Consistent example across ALL scenes: a RESTAURANT that serves its customers (dine-in and delivery) — the owner, cashier, chef, order process, all the way to a value meal.

# Preparation
No MCP/Archi needed. Element-type icons are available as `_logo` SVG files in the folder at `assets_dir` (front-matter) together with `manifest.json`; the generator automatically injects the file list + their absolute paths into every scene.

HOW TO DRAW (strict — consistent across all scenes and all effort levels):

ELEMENT = a box (RoundedRectangle) drawn with Manim:
- Box fill color = its native layer color: Business = YELLOW; Application = LIGHT BLUE; Strategy = ORANGE; Motivation = PURPLE; Technology = GREEN. (Panel/text accents may use variations of the Business/yellow color.)
- Element name as text INSIDE the box (must not be cut off).
- The type icon is loaded from its original `_logo.svg` file via `SVGMobject("<path>")`, scaled SMALL, placed in the TOP-RIGHT CORNER of the box with a small margin — NOT covering the name/label. DO NOT draw/invent your own icon and DO NOT recolor the logo (show it as is).
- Business logo files: `business_business_actor_logo.svg`, `business_business_role_logo.svg`, `business_business_collaboration_logo.svg`, `business_business_interface_logo.svg`, `business_business_process_logo.svg`, `business_business_function_logo.svg`, `business_business_interaction_logo.svg`, `business_business_event_logo.svg`, `business_business_service_logo.svg`, `business_business_object_logo.svg`, `business_contract_logo.svg`, `business_product_logo.svg`, `business_representation_logo.svg`.
- Cross-layer logo files (cross-layer scenes only): `application_application_service_logo.svg`, `application_application_component_logo.svg`, `strategy_capability_logo.svg`.

RELATIONSHIP = DO NOT load SVG. Draw with Manim's internal methods (`Line` / `DashedLine` + head shapes from `Polygon`/`Triangle`/`Dot`) so they can adapt position, length, and direction between boxes. Build-helpers available: `archi_element`, `assignment_arrow`, `serving_arrow`, `realization_arrow`, `influence_arrow`, `composition_arrow`, `association_arrow`. Line pattern + head shape per ArchiMate notation:
- Assignment: SOLID line; FILLED dot (`Dot`) at the source end; FILLED arrow head at the target. Used for Actor→Role and Role→Process.
- Serving: SOLID line; OPEN arrow head (two-line "V", no fill) at the target. Used for a Service that serves a customer/process.
- Realization: DOTTED line; HOLLOW TRIANGLE (outline) head at the target. Used for a Business Process realizing a Business Service, and a Business Process realizing a Strategy Capability.
- Aggregation: SOLID line; HOLLOW DIAMOND at the source end (whole→part; the part can also exist on its own). Used for a Product that AGGREGATES its Service(s) and Contract. (ArchiMate models a Product with aggregation — hollow diamond — not composition, because the services/contract can exist independently and be shared.)
- Access: DOTTED line; SMALL OPEN arrow head at the target (the object). Used for a Business Process that reads/writes a Business Object.
- Association: plain SOLID line (no head, or a small open arrow). Used for a neutral link not covered by the other types.
- Triggering (Process→Process): SOLID line; FILLED arrow head at the target (flow between processes).
Label the relationship name near the line where it helps.

## 01_layer_position (~20s)
Big title "ArchiMate — Business Layer" centered + a short subtitle "what the organization does for its customers". Draw the ArchiMate framework as stacked colored bands — Strategy ORANGE, Business YELLOW, Application BLUE, Technology GREEN — then highlight the YELLOW Business band that sits below Strategy and above Application. Use the HIGHLIGHT color for the Business band. Narration: the Business Layer describes the services, processes, and actors that run the organization day to day; it receives direction from Strategy and is supported by Application.

## 02_element_vocabulary (~34s)
Introduce the core Business vocabulary; each box = Business YELLOW color + name inside + logo in the top-right corner + restaurant example. Reveal gradually so it does not get crowded:
- Business Actor (`business_business_actor_logo.svg`) ID "Pemilik Restoran" | EN "Restaurant Owner".
- Business Role (`business_business_role_logo.svg`) ID "Kasir" | EN "Cashier", ID "Koki" | EN "Chef".
- Business Process (`business_business_process_logo.svg`) ID "Proses Pesanan" | EN "Order Process", ID "Penyajian" | EN "Serving".
- Business Function (`business_business_function_logo.svg`) ID "Manajemen Dapur" | EN "Kitchen Management".
- Business Service (`business_business_service_logo.svg`) ID "Layanan Makan di Tempat" | EN "Dine-in Service", ID "Layanan Pesan Antar" | EN "Delivery Service".
- Business Object (`business_business_object_logo.svg`) ID "Pesanan" | EN "Order".
- Product (`business_product_logo.svg`) ID "Paket Hemat" | EN "Value Meal".
- Business Event (`business_business_event_logo.svg`) ID "Pesanan Masuk" | EN "Order Received".
Emphasize with the ACCENT color that an Actor is a real performer, while a Role is the part that a performer plays.

## 03_relationships_between_elements (~28s)
Connect the Business element boxes with RELATIONSHIPS DRAWN by Manim (see the patterns in Preparation); each box = Business YELLOW color + name inside + logo in the top-right corner; label each line:
- Business Actor (`business_business_actor_logo.svg`) ID "Pemilik Restoran" | EN "Restaurant Owner" —assignment→ Business Role (`business_business_role_logo.svg`) ID "Kasir" | EN "Cashier" (SOLID line; FILLED dot at the source; FILLED arrow head at the target): the performer is given a role.
- Business Role (`business_business_role_logo.svg`) ID "Kasir" | EN "Cashier" —assignment→ Business Process (`business_business_process_logo.svg`) ID "Proses Pesanan" | EN "Order Process" (SOLID line; FILLED dot at the source; FILLED arrow head at the target): the role performs the process.
- Business Process (`business_business_process_logo.svg`) ID "Proses Pesanan" | EN "Order Process" —realization→ Business Service (`business_business_service_logo.svg`) ID "Layanan Makan di Tempat" | EN "Dine-in Service" (DOTTED line; HOLLOW TRIANGLE head at the target): the process realizes the service.
- Business Service (`business_business_service_logo.svg`) ID "Layanan Makan di Tempat" | EN "Dine-in Service" —serving→ Business Role (`business_business_role_logo.svg`) ID "Pelanggan" | EN "Customer" (SOLID line; OPEN arrow head): the service serves the party being served.
Highlight with the PRIMARY color the flow "performer → role → process → service".

## 04_relationships_between_layers (~26s)
A two-directional cross-layer scene; each box = its native layer color + name inside + logo in the top-right corner; all relationships DRAWN by Manim:
- DOWNWARD (supported by Application): Application Service (Application LIGHT BLUE box, `application_application_service_logo.svg`) ID "Layanan POS" | EN "POS Service" —serving→ Business Process (Business YELLOW box, `business_business_process_logo.svg`) ID "Proses Pesanan" | EN "Order Process" (SOLID line; OPEN arrow head): the system serves the business process.
- UPWARD (realizing Strategy): Business Process (Business YELLOW box, `business_business_process_logo.svg`) ID "Proses Pesanan" | EN "Order Process" —realization→ Strategy Capability (Strategy ORANGE box, `strategy_capability_logo.svg`) ID "Penjualan online" | EN "Online sales" (DOTTED line; HOLLOW TRIANGLE head pointing toward the Capability): the business process realizes the strategic capability.
Emphasize with the OK color: Business = "what is done", Application = "the system that supports it", Strategy = "the direction being realized".

## 05_case_example (~32s)
Assemble the restaurant model step by step; all element boxes + relationships DRAWN by Manim, each box = Business YELLOW color + name inside + logo in the top-right corner:
- Business Event (`business_business_event_logo.svg`) ID "Pesanan Masuk" | EN "Order Received" triggers Business Process (`business_business_process_logo.svg`) ID "Proses Pesanan" | EN "Order Process" (SOLID line; FILLED arrow head): the event triggers the process.
- Business Actor (`business_business_actor_logo.svg`) ID "Pemilik Restoran" | EN "Restaurant Owner" —assignment→ Business Role (`business_business_role_logo.svg`) ID "Koki" | EN "Chef"; Role ID "Koki" | EN "Chef" —assignment→ Business Process (`business_business_process_logo.svg`) ID "Penyajian" | EN "Serving".
- Business Process (`business_business_process_logo.svg`) ID "Proses Pesanan" | EN "Order Process" —triggering→ Business Process (`business_business_process_logo.svg`) ID "Penyajian" | EN "Serving" (SOLID line; FILLED arrow head): one process flows into the next.
- Business Process (`business_business_process_logo.svg`) ID "Proses Pesanan" | EN "Order Process" —access→ Business Object (`business_business_object_logo.svg`) ID "Pesanan" | EN "Order" (DOTTED line; SMALL OPEN arrow head at the Business Object): the process reads/writes the data object (a behavior element touching a passive object is Access, not Association).
- Business Process (`business_business_process_logo.svg`) ID "Penyajian" | EN "Serving" —realization→ Business Service (`business_business_service_logo.svg`) ID "Layanan Makan di Tempat" | EN "Dine-in Service".
- Product (`business_product_logo.svg`) ID "Paket Hemat" | EN "Value Meal" —aggregation→ Business Service (`business_business_service_logo.svg`) ID "Layanan Pesan Antar" | EN "Delivery Service" and —aggregation→ Contract (`business_contract_logo.svg`) ID "Syarat Promo" | EN "Promo Terms" (SOLID line; HOLLOW DIAMOND at the Product end): the product AGGREGATES a service and a contract (hollow diamond — the service/contract can exist on their own).
Highlight with the HIGHLIGHT color the main chain: Event → Process → Service → Product.

## 06_conclusion (~16s)
Recap: the Business Layer captures "what is done" through actors, roles, processes, functions, services, objects, and products — show the original icons again (Business YELLOW box + logo in the top-right corner):
- Business Actor (`business_business_actor_logo.svg`) "Actor"
- Business Role (`business_business_role_logo.svg`) "Role"
- Business Process (`business_business_process_logo.svg`) "Process"
- Business Function (`business_business_function_logo.svg`) "Function"
- Business Service (`business_business_service_logo.svg`) "Service"
- Business Object (`business_business_object_logo.svg`) "Object"
- Product (`business_product_logo.svg`) "Product"
- Business Event (`business_business_event_logo.svg`) "Event"
One sentence on the role of each element, emphasize with the OK color that this layer connects the direction from Strategy to the support from Application, then close with the chain on screen: Actor → Role → Process → Service → Product.
