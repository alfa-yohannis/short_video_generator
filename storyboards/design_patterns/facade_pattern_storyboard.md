---
title: facade_pattern
language: both
length: 2-3 minutes
---

# Facade Pattern

A short tutorial on the Facade pattern using a home-theater example: a client that
wants to watch a movie must drive many subsystem parts in the right order. Code in
Java. Use DANGER for the tangled subsystem calls, OK for the Facade design,
HIGHLIGHT for the current object, PRIMARY for titles, ACCENT for labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Facade Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it reading "one simple door into a complex system". Explain it provides a
single unified entry point that hides a complicated set of subsystems. A simple
button icon labeled watchMovie sits in front of a cluster of small gears in PRIMARY.

## The Problem (~25s)
Introduce a home theater built from many Java classes: Amplifier, Tuner,
StreamingPlayer, Projector, Screen, TheaterLights, PopcornPopper. To start a
movie the client must call many methods in a precise order — dim the lights, drop
the screen, power the amplifier, set its volume, switch the projector to wide mode,
then start the player. Render that long ordered call list in DANGER and label it
"client must know everything" in ACCENT.

## The Naive Approach (~25s)
Show the client class holding references to all seven subsystems and orchestrating
every step itself, with endMovie() repeating the same chore in reverse. Highlight
the coupling in DANGER: the client breaks whenever a subsystem changes its API or
its required ordering, and the same fragile sequence gets copy-pasted everywhere it
is needed.

## The Facade Solution (~30s)
Define a HomeTheaterFacade that wraps all subsystems and exposes two friendly
methods: watchMovie(movie) and endMovie(). Mark the facade in HIGHLIGHT and show
it delegating internally to each subsystem in the correct order, draw the wrapped
subsystems in OK. The client now calls only homeTheater.watchMovie("Interstellar"),
and the messy choreography stays sealed inside the facade.

## Structure Diagram (~25s)
Present a class/structure diagram in PRIMARY. A Client box points to a single
HomeTheaterFacade box in HIGHLIGHT. The facade fans out with simple arrows to the
subsystem boxes — Amplifier, Projector, Screen, TheaterLights, StreamingPlayer —
each in OK and labeled in ACCENT. Stress that the subsystems stay usable on their
own; the facade only adds a convenient front, it does not hide or seal them off.

## Before and After (~35s)
Split into two stacked panels. The first, in DANGER, shows the original client:
eight separate subsystem calls just to begin one movie. The second, in OK, shows
the same goal as a single line, homeTheater.watchMovie("Interstellar"), with a
matching homeTheater.endMovie(). Animate the long sequence collapsing into the one
clean call to make the simplification obvious.

## Conclusion (~20s)
Recap: a Facade offers one simple interface over a tangled subsystem, reducing
coupling and removing repeated orchestration while leaving the subsystems
available for advanced use. Benefits: easier onboarding, looser dependencies,
a single place to fix ordering. End with Client -> Facade -> Subsystems.
