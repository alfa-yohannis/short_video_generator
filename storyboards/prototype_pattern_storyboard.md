---
title: prototype_pattern
language: both
length: 2-3 minutes
---

# Prototype Pattern

A short tutorial on the Prototype pattern using a game monster-spawner example: a
Spawner that produces many fully configured Monster objects by cloning a
ready-made prototype instead of rebuilding each one from scratch. Code in Java.
Use DANGER for expensive repeated construction and brittle manual copies, OK for
the Prototype design, HIGHLIGHT for the active prototype object, PRIMARY for
titles, ACCENT for labels.

## Introduction (~15s)
Show "Prototype Pattern" as a LARGE CENTERED title in PRIMARY, with a short
subtitle directly beneath it reading "Create new objects by cloning a ready-made
one". Explain it lets you copy an existing, fully configured object instead of
building a new one field by field. Three identical monster icons fan out from a
single glowing original, each tagged with an ACCENT label "clone".

## The Problem (~25s)
A Java Spawner builds each Monster with a heavy constructor: load a sprite sheet,
assemble a behavior tree, roll base stats, attach loot tables. Show the same
costly setup steps repeating every time a Monster appears on a wave. Mark the
repeated expensive construction calls in DANGER and show a rising cost meter as
dozens of monsters spawn. The pain: identical, slow setup runs over and over.

## The Naive Copy (~25s)
Attempt a shortcut: a second constructor that copies an existing Monster by
reading every field one at a time into a brand-new instance. Show new fields
(armor, faction, statusEffects) being added to Monster, and highlight in DANGER
how each addition silently breaks the hand-written copy because someone forgets a
field. The pain: copy logic lives apart from the class and drifts out of sync.

## The Prototype Solution (~30s)
Define a Prototype interface with a single method clone() returning Prototype.
Show Monster implementing clone() so it knows how to duplicate itself, fields and
all, in one place. A PrototypeRegistry holds pre-built, fully configured monsters
keyed by name. The Spawner asks the registry for a key and calls clone() to mint a
fresh, ready monster. Render the registry lookup and clone() call in OK, and pulse
the stored original in HIGHLIGHT as copies stream out cheaply.

## Structure Diagram (~25s)
Draw the class structure: a Prototype interface at the center declaring clone() in
ACCENT. A concrete Monster box implements Prototype with an arrow tagged
"implements". A PrototypeRegistry box holds a map of Prototype instances with an
arrow tagged "stores". A Client/Spawner box points to the registry with an arrow
tagged "requests clone". Keep the Prototype interface and the clone() return path
in OK to stress that everyone depends only on the interface.

## Before and After (~30s)
Split into two panels. The first panel, framed in DANGER, shows the old line
new Monster(spriteSheet, behaviorTree, baseStats, lootTable) called inside the
spawn loop, with the cost meter climbing. The second panel, framed in OK, shows
registry.get("orc").clone() returning an instant, fully configured Monster with a
flat cost meter. Animate one new field being added to Monster and show only
clone() needing care, while the call sites stay untouched.

## Conclusion (~15s)
Recap: register a configured original once, then clone it to produce new objects.
Benefits in OK: skip expensive setup, keep copy logic inside the class, and add
variations by storing more prototypes. End with the flow
Client -> Registry -> Prototype.clone() centered in PRIMARY.
