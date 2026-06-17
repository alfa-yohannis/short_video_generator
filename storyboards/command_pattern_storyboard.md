---
title: command_pattern
language: both
length: 2-3 minutes
---

# Command Pattern

A short tutorial on the Command pattern using a home-automation remote: a
RemoteControl that triggers actions on devices like a Light without knowing how
those actions are carried out. Code in Java. Use DANGER for tight coupling and
sprawling conditionals, OK for the Command design, HIGHLIGHT for the active
command, PRIMARY for titles, ACCENT for role labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Command Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it reading "Wrap a request as an object". Explain that it turns an action
plus its receiver into a standalone object, so the part that triggers work is
decoupled from the part that does it. Three button icons labeled On, Off, Undo.

## The Problem (~25s)
A Java RemoteControl class handles every button inside one press(buttonId) method
packed with if/else branches that reach straight into devices: light.on(),
light.off(), stereo.setVolume(). Show the method swelling as more gadgets are
wired in; mark the rigid branches in DANGER. The pain: the invoker is glued to
every device, new buttons force edits here, and there is no way to record, queue,
or undo an action.

## The Command Solution (~30s)
Define a Command interface with a single execute() method. Show LightOnCommand and
LightOffCommand implementing it, each holding a reference to its Light receiver
and forwarding the call inside execute(). A RemoteControl now simply stores a
Command and runs command.execute() when a button is pressed, shown in OK color.
The invoker no longer names any device; it only speaks to the Command abstraction.

## Class Structure (~25s)
Draw the roles and connect them. A Command interface (ACCENT label "Command") with
LightOnCommand and LightOffCommand pointing to it (ACCENT label "ConcreteCommand").
Each concrete command links to Light (ACCENT label "Receiver"). RemoteControl
holds a Command (ACCENT label "Invoker"). A Client builds the commands, hands each
its receiver, and loads them onto the invoker (ACCENT label "Client"). Keep the
Command box in PRIMARY as the hinge everything turns on.

## Before and After (~30s)
Contrast two versions of pressing a button. The earlier version shows
RemoteControl with a switch on buttonId calling device methods directly, framed in
DANGER. The reworked version shows one slot-based call, button.execute(), framed
in OK, with the matching LightOnCommand whose execute() body is just light.on().
HIGHLIGHT how the same press now works for any device without touching the
RemoteControl.

## Adding Undo (~20s)
Extend the Command interface with an undo() method. LightOnCommand.undo() calls
light.off(), reversing its own effect. RemoteControl keeps a history stack and
pushes each executed command; pressing Undo pops the most recent one and calls its
undo(). HIGHLIGHT the active command as it is replayed in reverse, and note the
same stack enables queueing, logging, and macro commands.

## Conclusion (~15s)
Recap: encapsulate a request as an object so the trigger and the work stay
independent. Benefits: a decoupled invoker, interchangeable actions, and built-in
support for undo, queueing, and logging. End with
Client -> Invoker -> Command -> Receiver.
