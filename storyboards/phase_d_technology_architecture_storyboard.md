---
title: phase_d_technology_architecture
subject: togaf
language: both
length: 2-3 minutes
preparation_profile: togaf
---

# Phase D Technology Architecture

A short tutorial on Phase D, Technology Architecture — the step of the Architecture
Development Method (ADM) that designs the technology foundation an organization's
systems run on. The ADM is TOGAF's step-by-step recipe for planning a whole
organization's systems. TOGAF is a methodology and framework, not program code, so
every scene is built from clean labelled diagrams — rounded boxes, the ADM cycle,
matrices, layered bands, generic-to-specific spectrums, and relationship maps with
labelled arrows — never source code, and never with an invented "official TOGAF
icon", because TOGAF has no standard icon set. Because this is a process / phase
topic, the main visual is the ADM CYCLE — a clockwise ring of phases around a
central hub, with Phase D held in focus. The ADM is always drawn the canonical way:
Phases A through H clockwise on a ring with Requirements Management as the central
hub joined to every phase, the Preliminary phase outside the ring feeding one arrow
into Phase A (Architecture Vision), and Phase H looping back to Phase A to close the
ring. TOGAF is full of technical terms, so every TOGAF term is explained in plain
words the first time it appears — assume the viewer has never heard them. The
running example is from everyday life: a small neighbourhood bakery that wants to
start taking orders online. Use PRIMARY for titles, ACCENT for phase and
relationship labels, HIGHLIGHT for Phase D in focus, OK for a finished result, and
DANGER for a gap to be closed. The English version should be entirely in English,
including the example.

# Preparation
Before drawing any scene, verify the canonical structure and terminology of Phase D
Technology Architecture against an authoritative TOGAF source (The Open Group's
TOGAF Standard) rather than recalling it from memory, so every diagram matches the
official method and not an invented one. Confirm for this topic: that Phase D
produces the Technology Architecture — the platforms, computing, networks, and
infrastructure that carry the applications and data from Phase C; that its steps run
in the canonical order (select reference models, viewpoints and tools; describe the
Baseline Technology Architecture; describe the Target Technology Architecture;
perform gap analysis; define candidate roadmap components; resolve impacts across the
architecture landscape; conduct the formal stakeholder review; finalize the
Technology Architecture; and create the Architecture Definition Document); that its
inputs include the outputs of Phases A, B and C plus the Architecture Repository;
and that its outputs include the Baseline and Target Technology Architecture,
Technology Building Blocks, gap results, and contributions to the Architecture
Roadmap. Whenever the ADM cycle is shown, confirm that the ring is Phases A through H
only; that the Preliminary phase sits outside the ring with a single arrow into
Phase A (Architecture Vision) and is not a box on the ring; that Requirements
Management is the central hub joined to every phase; and that Phase H (Architecture
Change Management) loops back to Phase A to close the cycle. Also confirm in plain
words what Phase D delivers.

## What It Is (~18s)
Show "Phase D Technology Architecture" as a LARGE CENTERED title in PRIMARY, with a
short subtitle beneath it such as "TOGAF's blueprint for the technology underneath".
Explain the words plainly: Enterprise Architecture is the big-picture plan of how a
whole organization's business and computer systems fit together — like a city plan,
not a single building. The ADM (Architecture Development Method) is TOGAF's
step-by-step recipe for building that plan. Technology Architecture is the layer that
describes the technology foundation — the computers, networks, storage, and platforms
that everything runs on, like the wiring and plumbing of a building. Phase D is the
ADM step that designs that foundation. Name the example: a small bakery that wants to
take orders online.

## Where Phase D Sits on the ADM Cycle (~30s)
Draw the cycle: a ring of labelled rounded boxes running clockwise — Phase A
Architecture Vision (a short agreed picture of what you want and why), Phase B
Business Architecture (how the organization works day to day), Phase C Information
Systems Architectures (the software and the data it handles), Phase D Technology
Architecture, Phase E Opportunities and Solutions, Phase F Migration Planning, Phase G
Implementation Governance, and Phase H Architecture Change Management — joined by
curved ACCENT arrows showing the clockwise flow. Draw the Preliminary phase as a
separate box outside the ring with one arrow into Phase A — the one-time setup before
the cycle begins, not a step on the ring. Place Requirements Management as a hub in
the centre joined to every phase — in plain words, keeping track of everything the
architecture must do. Close the ring with an arrow from Phase H back to Phase A. Hold
Phase D Technology Architecture in HIGHLIGHT, and point out plainly that it comes
right after Phase C and feeds into Phase E.

## The Job of Phase D (~22s)
State the purpose with a few clean boxes. Phase D answers one question: what
technology foundation do we need so the software and data designed in Phase C, and the
way of working from Phase B, can actually run? Introduce two pictures in plain words:
the Baseline Technology Architecture is the "before" picture — the technology you have
today; the Target Technology Architecture is the "after" picture — the technology you
want. Show Baseline in a plain box and Target in OK. For the bakery, the foundation is
humble: today just a shop computer and home internet; tomorrow, technology that can
host an ordering page and take card payments.

## Inputs, Steps, and Outputs (~30s)
Walk the phase as inputs -> steps -> outputs, each ACCENT-labelled. Inputs flow in
from earlier phases: the Architecture Vision from Phase A, the Business Architecture
from Phase B, the Information Systems Architectures from Phase C, and the Architecture
Repository — in plain words, the shared library shelf of reusable parts and past
designs. Steps, in order: choose viewpoints (a viewpoint is simply a chosen way of
looking at the design for one audience, like a floor plan made for the builder);
describe the Baseline (today's technology); describe the Target (the wanted
technology); do a gap analysis; list candidate roadmap components; review with the
people who care; and finalize. Outputs flow out in OK: the Baseline and Target
Technology Architecture, Technology Building Blocks (a Building Block is a reusable
part, like a LEGO brick — here a piece of technology such as web hosting or a payment
service), the list of Gaps (a Gap is simply what is missing between today and the
goal, shown in DANGER), and the Architecture Definition Document — the written design
write-up.

## What Phase D Hands On (~24s)
Show the handoff as a small relationship map. Phase D's finished Target and its
Technology Building Blocks, together with the Gaps it found, become inputs to Phase E
Opportunities and Solutions, where the work gets grouped into deliverable pieces, and
they feed the Architecture Roadmap — in plain words, the schedule of steps from today
to the goal. Draw ACCENT arrows from Phase D to Phase E and to the Roadmap box. Keep a
two-way ACCENT arrow to the Requirements Management hub to show Phase D both reads
needs and adds new ones. Show the gap list in DANGER and the agreed Target in OK,
making the point that every gap Phase D names becomes a planned step later.

## One Pass for the Bakery (~34s)
Walk the bakery through Phase D step by step, the current step in HIGHLIGHT. Baseline
(today): one shop computer, a paper order book, a card reader, and home broadband.
Target (the goal): rented computing online (the cloud — simply using someone else's
computers over the internet) to run the ordering page, a card-payment service, a
faster and reliable internet line, and automatic backups. Gap analysis in DANGER: no
online hosting, no automatic backup, broadband too slow. Technology Building Blocks
chosen: web hosting, a payment service, storage for the orders, and the network.
Candidate roadmap components: get faster internet, sign up for cloud hosting, add the
payment service, switch on backups. End with the agreed Target Technology Architecture
in OK — a clear technology foundation ready to hand to the next phase.

## Conclusion (~20s)
Recap in plain words: Phase D Technology Architecture is the ADM step that designs the
technology foundation — it takes the software and data from Phase C, pictures the
Baseline and the Target, names the Gaps, and hands Technology Building Blocks and
roadmap steps to Phase E, all while the Requirements Management hub keeps needs in
view. Show the line of sight on screen: Baseline -> Target -> Gaps -> Roadmap. Stress
that it is one phase of a repeating cycle — go round again as the technology changes.
