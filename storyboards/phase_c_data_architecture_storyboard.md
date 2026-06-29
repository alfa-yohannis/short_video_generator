---
title: phase_c_data_architecture
subject: togaf
language: both
language: both
length: 2-3 minutes
preparation_profile: togaf
---

# Phase C Data Architecture

A short tutorial on Phase C Data Architecture, the step of the Architecture
Development Method (ADM) that maps out the DATA an organization runs on. This is the
adm_cycle teaching method: a phase topic, so its main visual is the ADM CYCLE — a
clockwise ring of phases around a central hub — with Phase C lit up so you can see
where it sits and what it does. TOGAF is a methodology and framework, taught with
clean labelled diagrams — rounded boxes, the ADM cycle, matrices, layered bands,
generic-to-specific spectrums, and relationship maps — never as source code, and
never with an invented "official TOGAF icon" (TOGAF has no standard icon set). TOGAF
is full of technical terms ordinary people have never heard, so every term is
explained in plain words the first time it appears, usually with an everyday
comparison — assume the viewer has never heard them. The ADM is always drawn the
canonical way: Phases A through H arranged clockwise on a ring with Requirements
Management as the central hub joined to every phase, the Preliminary phase drawn
outside the ring feeding one arrow into Phase A (Architecture Vision), and Phase H
looping back to Phase A to close the ring. The running example is from everyday life:
a small neighbourhood bakery that wants to start taking orders online. Use PRIMARY for
titles, ACCENT for phase and relationship labels, HIGHLIGHT for the part in focus, OK
for a finished result, and DANGER for a gap to be closed. The English version should
be entirely in English, including the examples.

# Preparation
Before drawing any scene, verify the canonical structure and terminology of Phase C
Data Architecture against an authoritative TOGAF source (The Open Group's TOGAF
Standard) instead of recalling it from memory, so the diagram matches the official
method and not an invented one. Confirm: that Phase C is "Information Systems
Architectures" and is made of two parts — a Data Architecture and an Application
Architecture — and that this tutorial covers the Data part; the objective of the Data
Architecture (describe the Target Data Architecture and find the gaps from the
Baseline); the standard steps in order (select reference models, viewpoints and tools;
develop the Baseline Data Architecture description; develop the Target Data
Architecture description; perform gap analysis; define candidate roadmap components;
resolve impacts; conduct a stakeholder review; finalize; create the Architecture
Definition Document); and the recognized outputs and artifacts (the Data Architecture
components of the Architecture Definition Document, the Architecture Requirements
Specification, Architecture Roadmap components, and the Data Entity/Data Component
catalog, Data Entity/Business Function and System/Data matrices, and Conceptual/Logical
Data diagrams). Because the ADM cycle is involved, also confirm: the phase names and
their clockwise order; that the ring is Phases A through H only; that the Preliminary
phase sits outside the ring with a single arrow into Phase A (Architecture Vision) and
is not a box on the ring; that Requirements Management is the central hub joined to
every phase; and that Phase H (Architecture Change Management) loops back to Phase A to
close the cycle.

## What It Is (~18s)
Show "Phase C Data Architecture" as a LARGE CENTERED title in PRIMARY, with a short
subtitle beneath it such as "Mapping the data the business runs on". Explain the words
plainly: Enterprise Architecture is just the big-picture plan of how a whole
organization's work and computer systems fit together — like a city plan, not a single
building. The Architecture Development Method (ADM) is TOGAF's step-by-step recipe for
building that plan, and Phase C is the step about DATA — the facts and records the
business keeps, such as its list of customers and its list of orders. Name the example:
a small neighbourhood bakery that wants to start taking orders online.

## Where Phase C Sits (~30s)
Draw the cycle: a ring of labelled rounded boxes running clockwise — Phase A
Architecture Vision, Phase B Business Architecture, Phase C Information Systems
Architectures, Phase D Technology Architecture, Phase E Opportunities and Solutions,
Phase F Migration Planning, Phase G Implementation Governance, and Phase H Architecture
Change Management — joined by curved ACCENT arrows that show the clockwise flow. Draw
the Preliminary phase as a separate box outside the ring with one arrow feeding into
Phase A — it is the one-time setup before the cycle begins, not a step on the ring.
Close the ring with an arrow from Phase H back to Phase A. Place Requirements Management
as a hub in the centre, joined to every phase. HIGHLIGHT Phase C and explain it plainly:
Phase C is called "Information Systems Architectures" and has two halves — Data (the
records the business keeps) and Application (the software that uses those records) — and
this tutorial zooms into the Data half. Gloss the neighbours: Architecture Vision is a
short agreed picture of what you want; Business Architecture, decided just before in
Phase B, is how the business itself will work.

## What Phase C Is For (~20s)
Pull Phase C out of the ring as a single card kept in HIGHLIGHT. State its purpose in
plain words: describe the data the bakery will need — the Target Data Architecture, the
picture of the data you want — and compare it with the data the bakery keeps today — the
Baseline Data Architecture, the picture of what you have now — then list every
difference as a Gap (a Gap is simply something missing that you must add, marked in
DANGER). Explain Data Architecture itself: a tidy map of the kinds of information a
business keeps and how they connect — like labelling every drawer in a filing cabinet
and drawing lines between the drawers that belong together.

## Inputs, Steps, Outputs (~28s)
Show three ACCENT-labelled bands as a flow: INPUTS feeding STEPS feeding OUTPUTS.
Inputs: the Architecture Vision and the Business Architecture handed over from Phase B,
plus any reusable data definitions kept in the Architecture Repository — a shared
library of past architecture work, like a household recipe folder. Steps, in order:
choose the reference models and Viewpoints (a Viewpoint is the chosen angle you look
from, like a floor plan versus a wiring plan); describe the Baseline data; describe the
Target data; do a gap analysis; and list the candidate roadmap pieces. Outputs in OK:
the data part of the Architecture Definition Document — the written record of the agreed
design — the data Building Blocks (a Building Block is a reusable part, like a LEGO
brick — here a reusable chunk of data such as "Customer"), and roadmap items that feed
the later phases.

## What Phase C Hands On (~22s)
Show the Data Architecture's everyday artifacts as small labelled cards and read each
plainly: a Catalog is a simple list (every kind of data the business keeps), a Matrix is
a grid that crosses two lists to show what touches what (which business job uses which
data), and a Diagram draws the data records as boxes joined by lines. Then draw the
relationship arrows in ACCENT: Business Architecture from Phase B feeds in, the finished
Data Architecture feeds the Application side and Phase D Technology Architecture — the
computers, networks, and storage underneath — and two-way arrows connect to the
Requirements Management hub, because every needed change is logged there.

## One Pass for a Bakery (~34s)
Walk the bakery through Phase C, the current step in HIGHLIGHT. Baseline — what is kept
today: a paper notebook of orders and a till, drawn in DANGER, with no shared customer
list, so the same name is written out again and again. Target: four neat data records
drawn as boxes joined by relationship lines — Customer, Product (the loaves and cakes),
Order, and Payment — where one Customer places many Orders and each Order lists
Products. Gap analysis in DANGER: "no digital customer list" and "no link from an order
to its products". Building Blocks in OK: a reusable Customer record and a reusable Order
record that other steps can pick up. End with the result in OK: a one-page data map plus
a short gap list, ready to hand to the roadmap.

## Conclusion (~20s)
Recap in plain words: Phase C Data Architecture is the ADM step that maps the data a
business needs — you describe the Target, compare it with the Baseline, mark the Gaps in
DANGER, and hand on reusable data Building Blocks and roadmap items. Show the small ADM
ring once more with Phase C in HIGHLIGHT and Requirements Management at the hub, to fix
where it lives. End with the line of sight on screen in OK:
Business needs -> Target Data Map -> Gaps -> Data Building Blocks -> Roadmap.
