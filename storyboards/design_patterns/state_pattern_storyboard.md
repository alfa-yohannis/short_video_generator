---
title: state_pattern
language: both
length: 2-3 minutes
---

# State Pattern

A short tutorial on the State pattern using a music-player example: a MusicPlayer
whose play, pause, and stop buttons behave differently depending on its current
state. Code in Java. Use DANGER for tangled state conditionals, OK for the State
design, HIGHLIGHT for the current state object, PRIMARY for titles, ACCENT for
labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "State Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it reading that an object changes its behavior when its internal state
changes. Three player icons labeled Stopped, Playing, Paused in PRIMARY, hinting
that the same buttons act differently in each mode.

## The Problem (~25s)
A Java MusicPlayer class keeps the current mode in a single String field and each
button method — pressPlay, pressPause, pressStop — opens with the same chain of
if/else checks against that field. Show the three methods stacked, with the
repeated mode checks marked in DANGER. The pain: the same conditions are copied
into every method.

## State Explosion (~20s)
Add a new mode, Buffering, and watch each button method grow another branch in
DANGER. Transition logic is scattered across every method, so the valid moves
between modes are impossible to read at a glance and easy to break.

## The State Solution (~30s)
Define a PlayerState interface with pressPlay(MusicPlayer), pressPause(MusicPlayer),
and pressStop(MusicPlayer). Show StoppedState, PlayingState, and PausedState each
implementing it in OK color, every method holding only the behavior for that one
mode. MusicPlayer keeps a PlayerState field and each button simply forwards the
call to it. A state hands control onward with player.setState(new PlayingState()).

## Class Structure (~25s)
Draw the structure: MusicPlayer as the Context, holding a reference to a
PlayerState. PlayerState shown as the interface in ACCENT, with StoppedState,
PlayingState, and PausedState connected to it as implementations. An arrow from
MusicPlayer to PlayerState labeled "delegates to current state"; a return arrow
labeled setState shows a state choosing the next one.

## Before and After (~30s)
Pair the two versions. The earlier MusicPlayer.pressPlay is one long switch over
the mode String, highlighted in DANGER. The reworked pressPlay is a single line,
state.pressPlay(this), in OK. HIGHLIGHT the active state object as the field swaps
from StoppedState to PlayingState, showing behavior change with no conditionals.

## Conclusion (~15s)
Recap: put each state's behavior in its own class and let the context delegate to
the current one, making transitions explicit. Benefits: no repeated conditionals,
self-contained states, and clear valid moves. End with
Context -> State -> ConcreteState.
