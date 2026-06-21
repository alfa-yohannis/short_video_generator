---
title: archimate_implementation_migration_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Implementation & Migration Layer

A short animated tutorial video about the Implementation & Migration Layer in the ArchiMate enterprise-architecture language — the layer that plans the transition: the roadmap, work packages, and milestones that carry the architecture from the current state to the desired state. Audience: beginners. Style: clean, one idea per screen, smooth transitions.

The English version is entirely in English (including ALL displayed and spoken restaurant examples/labels). The Indonesian version is entirely in Indonesian. The ONLY exception: STANDARD ArchiMate VOCABULARY — terms that the ArchiMate notation itself uses in English — stays the same (in English) in BOTH versions. This covers:
- Product names: "ArchiMate", "The Open Group".
- Layer names: Strategy, Business, Application, Technology, Motivation, Implementation & Migration.
- Aspect names: Active Structure, Behavior, Passive Structure, Motivation.
- Element type names: e.g. Capability, Business Process, Application Component, Node, Goal, Work Package.
- Relationship names: e.g. Realization, Serving, Assignment, Influence, Composition, Association.
ALL other words (ordinary titles, subtitles, narration, explanatory phrases, and restaurant example labels) MUST follow the video's language.

MANDATORY LANGUAGE RULE (to avoid mixing): every displayed example label is written as an `ID "…" | EN "…"` pair. The English version may use ONLY the EN text; the Indonesian version may use ONLY the ID text. NEVER show an Indonesian word in the English video, and vice versa — including text inside boxes, line/relationship labels, titles, subtitles, and the spoken narration.

Consistent example across ALL scenes: a RESTAURANT that rolls out an online ordering / delivery service GRADUALLY (from offline-only toward online + delivery).

# Preparation
No MCP/Archi needed. Element-type icons are available as `_logo` SVG files in the folder at `assets_dir` (front-matter) together with `manifest.json`; the generator automatically injects the file list + their absolute paths into every scene.

HOW TO DRAW (strict — consistent across all scenes and all effort levels):

ELEMENT = a box (RoundedRectangle) drawn with Manim:
- Box fill color = its native layer color: Implementation & Migration = PINK; Strategy = ORANGE; Motivation = PURPLE; Business = YELLOW; Application = LIGHT BLUE; Technology = GREEN. (Panel/text accents may use variations of the Implementation/pink color.)
- Element name as text INSIDE the box (must not be cut off).
- The type icon is loaded from its original `_logo.svg` file via `SVGMobject("<path>")`, scaled SMALL, placed in the TOP-RIGHT CORNER of the box with a small margin — NOT covering the name/label. DO NOT draw/invent your own icon and DO NOT recolor the logo (show it as is).
- Implementation & Migration logo files: `implementation_work_package_logo.svg`, `implementation_deliverable_logo.svg`, `implementation_implementation_event_logo.svg`, `implementation_plateau_logo.svg`, `implementation_gap_logo.svg`.
- Cross-layer logo files (ONLY cross-layer scene 05): `strategy_course_of_action_logo.svg`, `motivation_goal_logo.svg`.

RELATIONSHIP = DO NOT load SVG. Draw with Manim's internal methods (`Line` / `DashedLine` + head shapes from `Polygon`/`Triangle`/`Dot`) using the available build-helpers (`archi_element`, `assignment_arrow`, `serving_arrow`, `realization_arrow`, `influence_arrow`, `composition_arrow`, `association_arrow`) so they can adapt position, length, and direction between boxes. Line pattern + head shape per ArchiMate notation (the patterns USED in this layer):
- Realization (`realization_arrow`): DOTTED line; HOLLOW TRIANGLE (outline) head at the target. Used: Work Package —realization→ Deliverable; Deliverable —realization→ Plateau (deliverables collectively realize a plateau); Plateau —realization→ Motivation Goal; Work Package —realization→ Strategy Course of Action.
- Composition (`composition_arrow`): SOLID line; FILLED DIAMOND at the source end. Used: a Plateau is composed of (or aggregates) the CORE architecture elements valid at that state — NOT the deliverables (deliverables REALIZE the plateau, they are not parts of it).
- Association (`association_arrow`): plain SOLID line (no head, or a small open arrow). Used: a Gap is associated with TWO Plateaus (Baseline and Target).
- Triggering (sequence between Work Packages over time): SOLID line with a FILLED arrow head at the target — expressing "then continue to" (sequence/temporal).
Label the relationship name near the line where it helps.

## 01_layer_position (~18s)
Big title "ArchiMate — Implementation & Migration Layer" centered + subtitle "the roadmap that delivers the change". Draw the ArchiMate framework as colored bands — Strategy ORANGE, Business YELLOW, Application LIGHT BLUE, Technology GREEN, Motivation PURPLE — then show Implementation & Migration as a PINK band that spans the BOTTOM and WRAPS all the other layers (because it plans how all those changes are REALIZED gradually over time). Highlight the pink band with HIGHLIGHT color. Emphasize: this layer answers "when & in what steps" the change happens.

## 02_element_vocabulary (~30s)
Introduce the layer's vocabulary; each box = Implementation/PINK color + name inside + logo in the top-right corner + restaurant example below the box, revealed gradually:
- Work Package (`implementation_work_package_logo.svg`): ID "Bangun Aplikasi Delivery" | EN "Build Delivery App", ID "Pelatihan Staf" | EN "Staff Training" — a set of work to achieve a result.
- Deliverable (`implementation_deliverable_logo.svg`): ID "Aplikasi Delivery v1" | EN "Delivery App v1", ID "Dokumen SOP" | EN "SOP Document" — a tangible, measurable result of a Work Package.
- Plateau (`implementation_plateau_logo.svg`): ID "Baseline: Hanya Offline" | EN "Baseline: Offline Only", ID "Target: Online + Delivery" | EN "Target: Online + Delivery" — a stable architecture state at a point in time.
- Gap (`implementation_gap_logo.svg`): ID "Belum ada sistem pemesanan online" | EN "No online ordering system yet" — the difference between two Plateaus.
- Implementation Event (`implementation_implementation_event_logo.svg`): ID "Go-Live" | EN "Go-Live" — an event/milestone that marks a change of state.
Reveal gradually so the screen does not get crowded; use ACCENT color for the example labels.

## 03_plateau_and_gap (~26s)
Focus on the change of state; each box = Implementation/PINK color + name inside + logo in the top-right corner; relationships DRAWN by Manim:
- Plateau (`implementation_plateau_logo.svg`) ID "Baseline: Hanya Offline" | EN "Baseline: Offline Only" on the left (neutral/DANGER color to mark the old state we want to leave behind).
- Plateau (`implementation_plateau_logo.svg`) ID "Target: Online + Delivery" | EN "Target: Online + Delivery" on the right (OK color for the desired state).
- Between them, Gap (`implementation_gap_logo.svg`) ID "Belum ada sistem pemesanan online" | EN "No online ordering system yet" —association→ BOTH Plateaus (plain SOLID line to Baseline and to Target), highlighted with HIGHLIGHT. Emphasize: Gap = what is MISSING/MUST BE CLOSED when moving from Baseline to Target.

## 04_element_relationships (~26s)
Connect the elements with ArchiMate relationships DRAWN by Manim; each box = Implementation/PINK color + name inside + logo in the top-right corner; label each line:
- Work Package (`implementation_work_package_logo.svg`) ID "Bangun Aplikasi Delivery" | EN "Build Delivery App" —realization→ Deliverable (`implementation_deliverable_logo.svg`) ID "Aplikasi Delivery v1" | EN "Delivery App v1" (DOTTED line; HOLLOW TRIANGLE head at the Deliverable): the work package produces the deliverable.
- Work Package ID "Pelatihan Staf" | EN "Staff Training" —realization→ Deliverable ID "Dokumen SOP" | EN "SOP Document".
- Sequence between Work Packages (triggering over time): Work Package ID "Bangun Aplikasi Delivery" | EN "Build Delivery App" —triggering→ Work Package ID "Pelatihan Staf" | EN "Staff Training" (SOLID line; FILLED arrow head), then toward Implementation Event (`implementation_implementation_event_logo.svg`) ID "Go-Live" | EN "Go-Live". Emphasize: work packages run IN SEQUENCE toward the Go-Live milestone.

## 05_cross_layer_relationships (~28s)
Tie the roadmap back to the "why" (Motivation) and the "high-level approach" (Strategy). Each box = its native layer color + name inside + logo in the top-right corner; all relationships DRAWN by Manim (see the patterns in Preparation):
- Work Package (PINK box, `implementation_work_package_logo.svg`) ID "Bangun Aplikasi Delivery" | EN "Build Delivery App" —realization→ Strategy Course of Action (ORANGE box, `strategy_course_of_action_logo.svg`) ID "Mulai jualan online" | EN "Start selling online" (DOTTED line; HOLLOW TRIANGLE head): the work package realizes the strategic plan.
- Plateau (PINK box, `implementation_plateau_logo.svg`) ID "Target: Online + Delivery" | EN "Target: Online + Delivery" —realization→ Motivation Goal (PURPLE box, `motivation_goal_logo.svg`) ID "Tingkatkan pendapatan" | EN "Increase revenue" (DOTTED line; HOLLOW TRIANGLE head): the target state realizes the goal.
Emphasize with PRIMARY color: Implementation & Migration = the "when & in what steps" that REALIZES Strategy ("the high-level approach") and Motivation ("the why").

## 06_roadmap_example (~32s)
Assemble the restaurant roadmap gradually; all element boxes + relationships DRAWN by Manim, from left (now) to right (the goal):
Plateau (`implementation_plateau_logo.svg`) ID "Baseline: Hanya Offline" | EN "Baseline: Offline Only" — Gap (`implementation_gap_logo.svg`) ID "Belum ada sistem pemesanan online" | EN "No online ordering system yet" —association→ both Plateaus. Deliverable (`implementation_deliverable_logo.svg`) ID "Aplikasi Delivery v1" | EN "Delivery App v1" + ID "Dokumen SOP" | EN "SOP Document" —realization→ Plateau ID "Target: Online + Delivery" | EN "Target: Online + Delivery" (DOTTED line; HOLLOW TRIANGLE head at the Plateau): the deliverables collectively realize the target plateau. Work Package (`implementation_work_package_logo.svg`) ID "Bangun Aplikasi Delivery" | EN "Build Delivery App" —triggering→ Work Package ID "Pelatihan Staf" | EN "Staff Training" (SOLID line; FILLED arrow head), each one —realization→ its Deliverable, then —triggering→ Implementation Event (`implementation_implementation_event_logo.svg`) ID "Go-Live" | EN "Go-Live" that marks reaching the Target Plateau. Highlight the timeline path with HIGHLIGHT color.

## 07_conclusion (~16s)
Recap: the Implementation & Migration Layer plans the transition through five elements — show the five original icons again (PINK box + logo in the top-right corner): Work Package (`implementation_work_package_logo.svg`), Deliverable (`implementation_deliverable_logo.svg`), Plateau (`implementation_plateau_logo.svg`), Gap (`implementation_gap_logo.svg`), Implementation Event (`implementation_implementation_event_logo.svg`). One sentence on the role of each element. Benefits: change is split into clear steps, every Plateau can be traced to a goal, and the team knows what to deliver and when. Close with the chain on screen: Baseline → (Work Package → Deliverable) → Go-Live → Target.
