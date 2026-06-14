---
title: flyweight_pattern
language: both
length: 2-3 minutes
---

# Flyweight Pattern

A short tutorial on the Flyweight pattern using a forest-rendering example: a
game that draws millions of trees by sharing the heavy, repeated data instead of
duplicating it per object. Code in Java. Use DANGER for duplicated heavyweight
state and memory bloat, OK for the Flyweight design, HIGHLIGHT for the single
shared object, PRIMARY for titles, ACCENT for labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Flyweight Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it. Explain it shares many fine-grained objects efficiently by separating
the data they can share from the data unique to each. A dense grid of identical
tree icons fades in to hint at scale.

## The Problem (~25s)
A Java Tree class stores name, color, a texture image, and a mesh, plus its x and
y coordinates. Show a forest creating 1,000,000 Tree objects, each carrying its
own copy of the same texture and mesh. Animate a memory meter climbing into the
red and mark the duplicated texture and mesh fields in DANGER. The pain: identical
heavy data is stored a million times.

## Intrinsic vs Extrinsic State (~25s)
Split the fields of Tree into two groups with ACCENT labels. Intrinsic state —
name, color, texture, mesh — is shared and identical across many trees, shown
once in HIGHLIGHT. Extrinsic state — x and y — is unique per tree and stays with
the caller. The insight: only the intrinsic part is worth sharing.

## The Flyweight Solution (~30s)
Introduce a TreeType flyweight holding only the intrinsic fields, created once and
reused. A TreeFactory keeps a cache keyed by name and color, returning the same
TreeType instance for repeat requests in OK color. A Tree now keeps just x, y, and
a reference to its TreeType. Show many trees pointing to one shared TreeType in
HIGHLIGHT while the memory meter drops back into the green.

## Structure Diagram (~25s)
Draw a class structure in OK: TreeFactory holds a cache map and exposes
getTreeType(name, color); it produces TreeType flyweights with a draw(canvas, x, y)
method. Tree holds x, y, and a TreeType reference and delegates drawing to it.
Forest holds many Tree objects and one TreeFactory. Arrows show many Tree
references converging on a single shared TreeType.

## Before and After Code (~30s)
Place two snippets together. The before snippet builds Tree objects that each
allocate texture and mesh, with those allocations marked in DANGER. The after
snippet calls factory.getTreeType(name, color) so repeated types resolve to one
cached instance, marked in OK; draw(canvas, x, y) passes the extrinsic coordinates
in at render time. Highlight that a thousand "oak" trees now share one TreeType.

## Conclusion (~15s)
Recap: separate intrinsic shared state into a flyweight, hand extrinsic state in
per call, and reuse instances through a factory cache. Benefits: dramatic memory
savings and cheap fine-grained objects. End with Factory -> Flyweight (intrinsic)
+ Context (extrinsic).
