---
title: archimate_strategy_layer
language: both
length: 2-3 minutes
---

# ArchiMate Strategy Layer

A short tutorial on the Strategy Layer of the ArchiMate enterprise-architecture
language. This is a modeling notation, not program code, so every scene is built
from labelled ArchiMate elements and relationships rather than source code. The
goal is to teach the layer the way a modeling language is actually learned: first
locate it in the framework, then explain its purpose, introduce its vocabulary
and the relationships that join it, connect it upward to the Motivation layer's
goals, then assemble one real model, and finally show why it pays off.

One running example carries the second half, deliberately small and familiar in
the Indonesian context: "Warung Makan Bu Sari", a neighbourhood food stall that
wants to grow by selling online and offering delivery through a food-delivery app
(seperti GoFood atau GrabFood). Keep the ArchiMate element-type words in English -
Resource, Capability, Course of Action, Value Stream, Goal, Outcome - because
those are the notation's standard vocabulary, but name the example's own elements
in Indonesian so the model feels local.

Visual conventions. Tint Strategy-layer elements in the warm orange ArchiMate
assigns this layer, and use ArchiMate's own layer colors elsewhere so the model
reads as authentic: Motivation in purple, Business in yellow, Application in cyan,
and Technology in green. Use PRIMARY for titles, ACCENT for element-type and
relationship labels, HIGHLIGHT for the element currently being introduced, and OK
for a finished, coherent model. Keep every scene clean, visual, and minimal.

## Where It Sits (~18s)
Open on "ArchiMate Strategy Layer" as a LARGE CENTERED title, with a short
subtitle directly beneath it reading "modeling where the enterprise is headed".
Draw ArchiMate's layered framework as a stack of horizontal bands in their
official colors: Strategy on top in orange, then Business in yellow, Application
in cyan, and Technology in green, with a Motivation column in purple alongside.
HIGHLIGHT the top Strategy band and note it was added in ArchiMate 3.0 to sit
above the layers that actually run the business, just below the Motivation layer
that holds the goals.

## What the Layer Is For (~26s)
State the purpose plainly: the Strategy layer expresses how an organisation
intends to create value, the abilities it needs to do so, the assets behind those
abilities, and the plan for putting them to work. Ground it in the warung: show a
purple Motivation Goal at the top - "Naikkan Omzet" (grow revenue) - and a line
of sight being drawn down to the everyday cooking and serving at the bottom, with
the Strategy layer slotting into the middle as the connecting band in OK. The
takeaway: without this layer a model jumps straight into operations and loses the
link back to the goal; with it, even Bu Sari's choices trace to a clear aim.

## The Four Elements (~32s)
Introduce the whole vocabulary - just four elements - grouped by ArchiMate aspect
so the shapes make sense, giving each one short, familiar instance shown as a
small labelled chip beside it. Resource is the layer's one active structure
element: an asset that has abilities, drawn as a plain rectangle - for instance
"Akun Aplikasi Pesan-Antar" (delivery-app account). The other three are behavior
elements, drawn as rounded boxes because they describe doing, not being.
Capability, an ability the warung possesses such as "Penjualan Online". Course of
Action, a plan the owner has chosen such as "Mulai Jualan Online", marked with a
directional icon. Value Stream, an end-to-end sequence of value-adding stages for
the customer such as "Dari Pesan ke Antar", drawn as a chevron (added in ArchiMate
3.1). Make the structure-versus-behavior split explicit, each ACCENT-labelled with
its aspect: it is exactly why a Resource (structure) is assigned to a Capability
(behavior), the same way an actor is assigned to a process in the Business layer.

## How the Elements Relate (~26s)
Connect the vocabulary with ArchiMate's own relationships, labelling each arrow
with its ACCENT name, using the warung's elements. A Resource is assigned to a
Capability - the "Akun Aplikasi Pesan-Antar" is the means behind "Pesan-Antar", a
structure element assigned to a behavior element. A Capability serves a Value
Stream - "Penjualan Online" enables the "Dari Pesan ke Antar" stages. Then turn
the arrows downward: a Capability is realized by the core layers below, where a
business process or application actually performs it. HIGHLIGHT that these few
relationships wire the strategy together horizontally and downward; the next scene
wires it upward to the goals.

## Connecting to the Goals (Motivation Layer) (~20s)
Reveal the purple Motivation layer sitting directly above Strategy - the layer
that captures the why. Place Bu Sari as a Stakeholder, a Driver "Persaingan"
(competition) that raises the concern, a Goal "Naikkan Omzet", and an Outcome
"Penjualan Naik 30%". Now draw the realization arrows upward across the
orange-to-purple boundary: the Course of Action "Mulai Jualan Online" realizes the
Outcome, which in turn realizes the Goal, so the chosen plan is provably tied to
the owner's aim. Note in ACCENT that capabilities, value streams, and resources
may also realize or influence goals and requirements - the whole Strategy layer
exists to answer Motivation's why.

## A Worked Example: Warung Goes Online (~33s)
Assemble one complete model in OK, top to bottom across three colored bands. In
the purple Motivation band, a Goal "Naikkan Omzet" with an Outcome "Penjualan
Naik 30%". In the orange Strategy band, a Course of Action "Mulai Jualan Online"
realizing that outcome and drawing on three Capabilities - "Penjualan Online",
"Pemasaran Media Sosial", and "Pesan-Antar" - each backed by an assigned Resource:
an "Akun Aplikasi Pesan-Antar", a "Smartphone & Akun Instagram", and the "Tim
Dapur" (kitchen team). A Value Stream "Dari Pesan ke Antar", with stages Pesan,
Masak, Antar, runs along the bottom of the strategy band, served by those
capabilities. Finally drop one realization arrow into the layers below, where a
cyan "Aplikasi Pesan-Antar" application and a yellow "Proses Pesanan" business
process bring "Penjualan Online" to life. Animate the pieces snapping into one
coherent picture that spans Motivation, Strategy, and the operational layers.

## Why It Pays Off, and Recap (~20s)
Close on the practical value. Because capabilities describe what the warung can do
rather than how, they change far more slowly than the apps and people that realize
them, giving a stable bridge from goals to operations that survives a change of
delivery app or a new cook. Mention that the same elements feed capability maps
and investment heat maps, and a shared language between owner and architect. Then
recap the four elements and end with the line of sight on screen: Resource ->
Capability -> Course of Action -> Goal.
