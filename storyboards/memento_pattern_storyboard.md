---
title: memento_pattern
language: both
length: 2-3 minutes
---

# Memento Pattern

A short tutorial on the Memento pattern using a text-editor undo example: a
TextEditor whose typing history can be captured and rolled back. Code in Java.
Use DANGER for code that exposes or pokes at internal state, OK for the Memento
design, HIGHLIGHT for the snapshot currently being restored, PRIMARY for titles,
ACCENT for labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Memento Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it reading "Capture and restore an object's state". Explain the pattern
saves a snapshot of an object's internal state and lets it be restored later
without exposing how that state is stored. A small editor icon with an undo arrow
curling back into it.

## The Problem (~25s)
A Java TextEditor class holds a private String content that grows as the user
types. The goal is an undo feature that returns the editor to an earlier moment.
Show content changing through several edits, then highlight the question: how do
we remember each past version and roll back to one of them? Mark the lost earlier
versions fading away in DANGER.

## The Naive Approach (~25s)
To enable undo, the editor's content field is made public so a separate History
class can read it, copy it, and write it back directly. Show History reaching
into editor.content and editor.content = saved in DANGER. The pain: encapsulation
is broken, anyone can corrupt the state, and the rollback logic is scattered
outside the editor that owns the data.

## The Memento Solution (~30s)
Introduce three roles in OK color. The Originator (TextEditor) keeps content
private and offers save() returning an EditorMemento and restore(EditorMemento)
that reads it back. The Memento (EditorMemento) holds the captured state as an
opaque snapshot, readable only by the editor. The Caretaker (History) collects
mementos in a stack without ever inspecting them. Show history.push(editor.save())
and editor.restore(history.pop()).

## Structure at a Glance (~25s)
Draw the class structure. TextEditor (Originator) with private content, save() and
restore(); EditorMemento with the stored state and a narrow getState(); History
(Caretaker) holding a stack of EditorMemento. Arrows: Originator creates Memento,
Caretaker stores Memento, Originator reads Memento back. Label each role with
ACCENT tags Originator, Memento, Caretaker.

## Before and After (~30s)
Side-by-side comparison. The before version mutates editor.content from the
outside and is marked DANGER. The after version types text, calls
history.push(editor.save()) after each change, then on undo calls
editor.restore(history.pop()) and the content snaps back to the prior version in
OK. HIGHLIGHT the single snapshot being restored as content rewinds to it.

## Conclusion (~15s)
Recap: externalize a snapshot of internal state behind an opaque memento so it can
be restored later, with encapsulation intact. Benefits: clean undo, no leaking of
internal fields, and the owner stays in charge of its own state. End with
Originator -> Memento -> Caretaker.
