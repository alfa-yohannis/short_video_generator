---
title: phase_c_application_architecture
subject: togaf
language: both
length: 2-3 minutes
preparation_profile: togaf
---

# Phase C Application Architecture

A short tutorial on Phase C Application Architecture, the step in TOGAF's
Architecture Development Method (ADM) where you design the software side of the
plan. This is the adm_cycle teaching method: a process topic, so its main visual is
the ADM CYCLE — a clockwise ring of phases around a central hub — with Phase C lit
up as the phase in focus. TOGAF is a methodology, not program code, so every scene
is built from clean labelled diagrams — rounded boxes, the ADM cycle, matrices,
layered bands, spectrums, and relationship maps — never source code, and never with
an invented "official TOGAF icon", because TOGAF has no standard icon set. TOGAF is
full of technical terms, so every term is explained in plain words the first time it
appears — assume the viewer has never heard them. The ADM is always drawn the
canonical way: Phases A through H arranged clockwise on a ring with Requirements
Management as the central hub joined to every phase, the Preliminary phase drawn
outside the ring feeding one arrow into Phase A (Architecture Vision), and Phase H
looping back to Phase A to close the ring. The running example is from everyday
life: a small neighbourhood coffee shop that wants to start taking orders online.
Use PRIMARY for titles, ACCENT for phase and relationship labels, HIGHLIGHT for the
phase in focus, OK for a finished result, and DANGER for a gap to be closed. The
English version should be entirely in English, including the examples.

# Preparation
Before drawing any scene, verify the canonical structure and terminology of Phase C
against an authoritative TOGAF source (The Open Group's TOGAF Standard) instead of
recalling it from memory, so the diagram matches the official method and not an
invented one. Confirm: that Phase C is named "Information Systems Architectures" and
is made of two parts — Data Architecture and Application Architecture — and that
Application Architecture is one of those two parts, not the whole phase; that the
objective of Application Architecture is to develop the Target Application
Architecture and identify candidate Architecture Roadmap components; that its
application building blocks are described in logical terms independent of specific
products; the canonical steps (describe the baseline applications, develop the
target applications, perform gap analysis, define candidate roadmap components,
review with stakeholders, finalise, and update the Architecture Definition
Document); its inputs (Architecture Vision, Business Architecture, Architecture
Requirements) and its outputs (Target Application Architecture, gap analysis,
candidate Roadmap components, updated Architecture Definition Document and
Architecture Requirements Specification); and the standard Phase C work products such
as the Application Portfolio Catalog, the Interface Catalog, the Application/Function
matrix, and the Application Communication diagram. Because the ADM cycle appears,
also confirm: the phase names and their clockwise order; that the ring is Phases A
through H only; that the Preliminary phase sits outside the ring with a single arrow
into Phase A (Architecture Vision) and is not a box on the ring; that Requirements
Management is the central hub joined to every phase; and that Phase H (Architecture
Change Management) loops back to Phase A to close the cycle. Also confirm in plain
words what each item delivers.

## What It Is (~18s)
Show "Phase C Application Architecture" as a LARGE CENTERED title in PRIMARY with a
short subtitle beneath it, such as "Designing the software side of the plan".
Explain the words plainly: Enterprise Architecture is just the big-picture plan of
how a whole organization's business and computer systems fit together — like a city
plan, not a single building — and the ADM (Architecture Development Method) is the
step-by-step recipe TOGAF gives you to build that plan, drawn as a ring of phases.
Phase C is the step where you design the Information Systems Architectures — the
software and the data — and Application Architecture is the half of Phase C that
decides which application systems (the actual programs and apps) the business needs
and how they fit together. Name the example: a small neighbourhood coffee shop that
wants to start taking orders online.

## Phase C on the ADM Ring (~30s)
Draw the cycle: a ring of labelled rounded boxes running clockwise — Phase A
Architecture Vision, Phase B Business Architecture, Phase C Information Systems
Architectures, Phase D Technology Architecture, Phase E Opportunities and Solutions,
Phase F Migration Planning, Phase G Implementation Governance, and Phase H
Architecture Change Management — joined by curved ACCENT arrows that show the
clockwise flow. Draw the Preliminary phase as a separate box outside the ring with
one arrow feeding into Phase A — it is the one-time setup before the cycle begins,
not a step on the ring. Close the ring with an arrow from Phase H back to Phase A.
Place Requirements Management as a hub in the centre, joined to every phase.
HIGHLIGHT Phase C. Say it plainly: Phase C comes right after Phase B Business
Architecture (how the business runs day to day) and right before Phase D Technology
Architecture (the computers and cloud underneath). Then split the focused phase into
two ACCENT-labelled halves — Data Architecture (the information the business keeps,
such as the menu and the orders) and Application Architecture (the programs that use
that information) — and keep the Application Architecture half in HIGHLIGHT as our
subject.

## What Application Architecture Is For (~22s)
State the purpose in plain words: Application Architecture names the major kinds of
application systems the business needs and shows how they talk to each other —
described in everyday logical terms, not as one particular product or brand, so the
design stays stable even if the real software is swapped out later. Introduce the
jargon gently: an Application Building Block is a reusable software part, like a LEGO
brick — one named chunk such as "the ordering app" or "the customer list". Contrast
the two pictures it produces: the Baseline Application Architecture in PRIMARY — the
software the business runs today — and the Target Application Architecture in OK —
the software it wants. Mark the difference between them as the Gap in DANGER — in
plain words, the apps that are missing or must change to get from today to the goal.

## Inputs and Outputs (~24s)
Show Phase C Application Architecture as a single rounded box in HIGHLIGHT with
inputs flowing in and outputs flowing out, each ACCENT-labelled and glossed. Inputs:
the Architecture Vision from Phase A — the short agreed picture of the goal, like a
sketch of a finished room before a renovation — and the Business Architecture from
Phase B — how the business will work — together with the running list of needs from
the Requirements Management hub. Outputs in OK: the Target Application Architecture
(the chosen set of apps and how they connect), a Gap list in DANGER (what is missing
today), candidate Architecture Roadmap components (rough pieces of work for the
schedule of steps from today to the goal), and an updated Architecture Definition
Document — the written design — alongside the Architecture Requirements
Specification, the plain list of what each app must do.

## Mapping the Applications (~26s)
Show the two signature tools of Phase C as clean labelled diagrams. First an
Application Communication diagram: each Application Building Block as a rounded ACCENT
box — "ordering app", "customer list", "payment handler", "kitchen order screen" —
joined by labelled arrows for the information that flows between them, such as "order
details" and "customer name". Then an Application/Function matrix: a simple grid with
the business jobs (take an order, take a payment, tell the kitchen) along one set of
headers and the apps along the other, a tick where an app does that job. Explain how
to read it plainly: scan a job's line for a tick, and a job with no tick anywhere is
one no app covers yet — show that empty cell in DANGER as a Gap to close.

## One Pass for a Coffee Shop (~36s)
Walk the coffee shop through Phase C Application Architecture, the running example in
HIGHLIGHT. Start from the Baseline in PRIMARY — today the shop runs on a paper
notebook and a shared phone. Bring in the inputs: the Vision ("take orders online and
deliver within one year") and the Business Architecture (a new way to take online
orders and get them delivered). Build the Target Application Architecture in OK as
four Application Building Blocks — an online ordering app, a customer list, a payment
handler, and a kitchen order screen — joined by labelled arrows showing the order
details and the customer name flowing between them. Run the gap analysis: the shop
has none of these yet, so each block is a Gap in DANGER. Turn the gaps into candidate
Roadmap components — build the ordering app first, add the payment handler next.
Build it step by step, ending with the finished Target Application Architecture in OK
as the clear line of sight.

## Conclusion (~18s)
Recap in plain words: Phase C Application Architecture is the step on the ADM ring
where you decide which application systems the business needs and how they connect —
turning the agreed Vision and the Business Architecture into a checked Target design,
a list of Gaps, and pieces for the Roadmap. Remind the viewer that it hands its
results on to Phase D Technology Architecture — the computers and cloud that will
actually run the apps — and feeds the central Requirements Management hub the whole
way round. End with the line of sight on screen:
Vision -> Business -> Applications -> Gaps -> Roadmap.
