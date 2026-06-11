---
title: archimate_motivation_layer
language: both
length: 2-3 minutes
preparation_profile: archi
---

# ArchiMate Motivation Layer

A short tutorial on the Motivation Layer of the ArchiMate enterprise-architecture
language - the layer that captures the why behind everything else. This is a
modeling notation, not program code, so every scene is built from labelled
ArchiMate elements and relationships rather than source code. The goal is to teach
the layer the way a modeling language is learned: locate it in the framework,
explain its purpose, introduce its full vocabulary in small groups, join them with
relationships, show how it drives the layers below, assemble one real model, and
conclude.

One running example carries the lesson, deliberately small and familiar in the
Indonesian context: "Warung Makan Bu Sari", a neighbourhood food stall deciding
how to grow. Keep the ArchiMate element-type words in English - Stakeholder,
Driver, Assessment, Goal, Outcome, Principle, Requirement, Constraint, Value,
Meaning - because those are the notation's standard vocabulary, but name the
example's own elements in Indonesian so the model feels local.

Visual conventions. Tint every Motivation element in the purple ArchiMate assigns
this layer, and use ArchiMate's own layer colors when other layers appear:
Strategy in orange, Business in yellow, Application in cyan, Technology in green.
Use PRIMARY for titles, ACCENT for element-type and relationship labels, HIGHLIGHT
for the element currently being introduced, and OK for a finished, coherent model.
Keep every scene clean, visual, and minimal.

# Preparation
Every scene must use the real, original ArchiMate element icons/symbols, never an
invented shape. Obtain ONLY the symbols this video uses, not every layer: the ten
Motivation elements (Stakeholder, Driver, Assessment, Goal, Outcome, Principle,
Requirement, Constraint, Value, Meaning), the relationships shown between them, and
the two neighbouring elements the worked example connects down to (a Strategy
Course of Action and an Application Component). Get each in this order of
preference: first export it from the Archi modelling tool (the "archi" MCP server);
if Archi does not provide it, find the official symbol online; only if neither is
available, draw it yourself, preferring SVG and falling back to JPG when SVG is not
possible. Keep each element's official shape, icon and color as the reference for
the purple
Motivation elements drawn in the scenes below.

## Where It Sits (~16s)
Open on "ArchiMate Motivation Layer" as a LARGE CENTERED title, with a short
subtitle directly beneath it reading "the why behind the architecture". Draw
ArchiMate's framework as colored bands - Strategy orange, Business yellow,
Application cyan, Technology green - and show the Motivation layer as a tall purple
column standing alongside all of them, since it gives reasons for elements in every
other layer. HIGHLIGHT the purple column.

## What the Layer Is For (~22s)
State the purpose plainly: the Motivation layer records who cares, what pushes
them, and what they want - the intentions that justify every other element in the
model. Ground it in the warung: a core model can show that Bu Sari cooks and
serves, but only the Motivation layer says why she is about to change how she
works. Show a purple band quietly sitting behind a plain Business process in OK,
and note that without it a model has what and how but never why.

## Sources of Motivation: Stakeholder, Driver, Assessment (~26s)
Introduce the first trio, each purple and ACCENT-labelled with its type, appearing
in HIGHLIGHT. Stakeholder: someone whose interests shape the architecture, such as
"Pemilik Warung" (the owner) and "Pelanggan" (customers). Driver: a condition that
motivates change, such as "Persaingan" (competition) and "Pendapatan" (revenue).
Assessment: the finding when a driver is analysed, a SWOT-style judgement, such as
"Penjualan Menurun" (sales are falling). Show a Stakeholder associated with a
Driver, and the Driver carrying an Assessment, so concern flows into insight.

## Intentions: Goal, Outcome, Requirement, Constraint, Principle (~30s)
Introduce the intention set, still purple and ACCENT-labelled. Goal: a high-level
statement of intent, such as "Naikkan Omzet" (grow revenue). Outcome: a concrete,
measurable result, such as "Penjualan Naik 30%". Requirement: a specific need the
solution must meet, such as "Bisa Terima Pesanan Online". Constraint: a restricting
requirement that limits how a goal may be met, such as "Anggaran Terbatas" (limited
budget). Principle: a qualitative guideline that always applies, such as "Utamakan
Layanan Cepat" (always prioritise fast service).

## Worth and Interpretation: Value and Meaning (~16s)
Complete the vocabulary with the two elements that tie motivation to what
stakeholders actually perceive, both purple and ACCENT-labelled. Value: the
relative worth or importance something holds for a stakeholder, such as
"Kepraktisan" (convenience) - the value a customer gains by ordering without
leaving home. Meaning: the interpretation an element carries in context, such as a
"Pesanan Siap" notice understood as "makanan siap diambil" (the food is ready).
Note these two attach to the core elements they describe, rounding the layer out
to ten elements in all.

## How They Relate: the Motivation Chain (~26s)
Connect the vocabulary with ArchiMate's own relationships, labelling each arrow
with its ACCENT name. An Assessment influences a Goal - "Penjualan Menurun" pushes
"Naikkan Omzet". A Goal is realized by an Outcome - "Penjualan Naik 30%" makes the
goal concrete. A Goal is refined into a Requirement - "Naikkan Omzet" leads to
"Bisa Terima Pesanan Online". A Principle influences that Requirement, and a
Constraint limits it. HIGHLIGHT that influence and realization arrows turn a vague
wish into a testable need.

## A Worked Example and Connecting Down (~28s)
Assemble the warung's whole motivation model in OK, then show it driving the rest.
Stakeholder "Pemilik Warung" holds Driver "Pendapatan", whose Assessment "Penjualan
Menurun" influences the Goal "Naikkan Omzet"; the goal is realized by the Outcome
"Penjualan Naik 30%" and refined into the Requirement "Bisa Terima Pesanan Online",
limited by the Constraint "Anggaran Terbatas". Now cross the boundary downward: the
Outcome is realized by a Strategy-layer Course of Action "Mulai Jualan Online" in
orange, and the Requirement is realized by an Application "Aplikasi Pesan-Antar" in
cyan. The purple why now provably drives the orange plan and the cyan system.

## Conclusion (~14s)
Recap: the Motivation layer captures the why with ten elements - Stakeholder,
Driver, Assessment, Goal, Outcome, Principle, Requirement, Constraint, Value, and
Meaning. Benefits: every element can be traced to a reason, choices are justified,
and the whole model stays aligned. End with the chain on screen: Stakeholder ->
Driver -> Assessment -> Goal -> Requirement.
