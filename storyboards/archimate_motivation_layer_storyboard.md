---
title: archimate_motivation_layer
language: both
length: 2-3 minutes
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

One running example carries the lesson, deliberately small and familiar: a
neighbourhood restaurant deciding how to grow. Keep the ArchiMate element-type
words in English - Stakeholder, Driver, Assessment, Goal, Outcome, Principle,
Requirement, Constraint, Value, Meaning - because those are the notation's standard
vocabulary, and name the example's own elements in English so the model reads
consistently.

Visual conventions. Tint every Motivation element in the purple ArchiMate assigns
this layer, and use ArchiMate's own layer colors when other layers appear:
Strategy in orange, Business in yellow, Application in cyan, Technology in green.
Use PRIMARY for titles, ACCENT for element-type and relationship labels, HIGHLIGHT
for the element currently being introduced, and OK for a finished, coherent model.
Keep every scene clean, visual, and minimal.
The English version should all be in English, including the examples.
Every scene must use the real, original ArchiMate element icons/symbols, never an
invented shape.

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
model. Ground it in the restaurant: a core model can show that it cooks and
serves, but only the Motivation layer says why it is about to change how it
works. Show a purple band quietly sitting behind a plain Business process in OK,
and note that without it a model has what and how but never why.

## Sources of Motivation: Stakeholder, Driver, Assessment (~26s)
Introduce the first trio, each purple and ACCENT-labelled with its type, appearing
in HIGHLIGHT. Stakeholder: someone whose interests shape the architecture, such as
"Restaurant Owner" and "Customers". Driver: a condition that
motivates change, such as "Competition" and "Revenue". Assessment: the
finding when a driver is analysed, a SWOT-style judgement, such as
"Sales Declining". Show a Stakeholder associated with a
Driver, and the Driver carrying an Assessment, so concern flows into insight.

## Intentions: Goal, Outcome, Requirement, Constraint, Principle (~30s)
Introduce the intention set, still purple and ACCENT-labelled. Goal: a high-level
statement of intent, such as "Grow Revenue". Outcome: a concrete,
measurable result, such as "Sales Up 30%". Requirement: a specific need the
solution must meet, such as "Accept Online Orders". Constraint: a restricting
requirement that limits how a goal may be met, such as "Limited
Budget". Principle: a qualitative guideline that always applies, such as "Always
Prioritise Fast Service".

## Worth and Interpretation: Value and Meaning (~16s)
Complete the vocabulary with the two elements that tie motivation to what
stakeholders actually perceive, both purple and ACCENT-labelled. Value: the
relative worth or importance something holds for a stakeholder, such as
"Convenience" - the value a customer gains by ordering without
leaving home. Meaning: the interpretation an element carries in context, such as a
"Order Ready" notice understood as "the food is ready to collect".
Note these two attach to the core elements they describe, rounding the layer out
to ten elements in all.

## How They Relate: the Motivation Chain (~26s)
Connect the vocabulary with ArchiMate's own relationships, labelling each arrow
with its ACCENT name. An Assessment influences a Goal - "Sales Declining" pushes
"Grow Revenue". A Goal is realized by an Outcome - "Sales Up 30%" makes the
goal concrete. A Goal is refined into a Requirement - "Grow Revenue" leads to
"Accept Online Orders". A Principle influences that Requirement, and a
Constraint limits it. HIGHLIGHT that influence and realization arrows turn a vague
wish into a testable need.

## A Worked Example and Connecting Down (~28s)
Assemble the restaurant's whole motivation model in OK, then show it driving the rest.
Stakeholder "Restaurant Owner" holds Driver "Revenue", whose Assessment "Sales
Declining" influences the Goal "Grow Revenue"; the goal is realized by the Outcome
"Sales Up 30%" and refined into the Requirement "Accept Online Orders",
limited by the Constraint "Limited Budget". Now cross the boundary downward: the
Outcome is realized by a Strategy-layer Course of Action "Start Selling Online" in
orange, and the Requirement is realized by an Application "Delivery App" in
cyan. The purple why now provably drives the orange plan and the cyan system.

## Conclusion (~14s)
Recap: the Motivation layer captures the why with ten elements - Stakeholder,
Driver, Assessment, Goal, Outcome, Principle, Requirement, Constraint, Value, and
Meaning. Benefits: every element can be traced to a reason, choices are justified,
and the whole model stays aligned. End with the chain on screen: Stakeholder ->
Driver -> Assessment -> Goal -> Requirement.