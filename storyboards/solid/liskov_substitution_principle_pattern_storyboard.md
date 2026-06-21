---
title: liskov_substitution_principle_pattern
language: both
length: 2-3 minutes
---

# Liskov Substitution Principle Pattern

A short tutorial on the Liskov Substitution Principle using a shapes example: a
Rectangle and a Square that must stand in for a base type without breaking the
code that uses them. Code in Java. Use DANGER for substitution that breaks
expectations, OK for the LSP-correct design, HIGHLIGHT for the current object,
PRIMARY for titles, ACCENT for labels.

## Introduction (~15s)
The main title, shown large and centered, must read exactly "Liskov Substitution
Principle". Directly beneath it a short subtitle "Subtypes that keep their
promises", then two shape icons labeled Rectangle and Square in ACCENT. Explain
that any subtype must be usable anywhere its base type is expected, without
surprising the caller.

## The Problem (~25s)
A Java Rectangle class with setWidth, setHeight, and getArea returning
width * height. Show a client method resize(Rectangle r) that sets width to 5,
height to 4, then asserts getArea() equals 20. Run it against a plain Rectangle
and mark the passing assertion in OK. Frame the question: will every subtype keep
this promise?

## The Naive Approach (~25s)
Introduce a Square that extends Rectangle and overrides setWidth and setHeight so
both sides always stay equal. Pass this HIGHLIGHTed Square into the same
resize(Rectangle r) method. Show getArea() returning 16 instead of 20, and flash
the broken assertion in DANGER. The pain: a Square cannot honor what callers of
Rectangle assume, so inheritance here lies.

## Why It Breaks (~20s)
Zoom on the overridden setters in DANGER and the caller's expectation in ACCENT,
showing the conflict: the base type promises width and height move
independently, the subtype secretly couples them. State the rule plainly:
strengthening preconditions or weakening guarantees of the base type violates
substitutability.

## The LSP Solution (~30s)
Stop forcing Square to be a Rectangle. Define a Shape interface with a single
area() method. Make Rectangle and Square separate implementations of Shape, each
with its own fields and constructor, no shared mutable setters. Show a client
loop totaling area() over a list of Shape, accepting either type interchangeably,
all marked in OK. Substitution now never surprises the caller.

## Structure Diagram (~25s)
Draw a class diagram: a Shape interface in PRIMARY at the center with area(),
and two boxes Rectangle and Square in OK each connected by an implements arrow.
Label that every Shape reference can hold either box safely in ACCENT. Contrast
with a faded DANGER ghost of the old Square-extends-Rectangle arrow being
removed.

## Before and After Code (~25s)
Pair the two versions. The before snippet shows class Square extends Rectangle
with coupled setters and the failing resize assertion, the whole block tinted
DANGER. The after snippet shows immutable Rectangle and Square implementing
Shape with area(), and the client summing areas, the whole block tinted OK.
HIGHLIGHT the moment the assertion turns from failing to holding.

## Conclusion (~15s)
Recap: a subtype must be substitutable for its base type without breaking callers'
expectations. Benefits: reliable polymorphism, no hidden special cases, safer
extension. End with Base Type -> honest Subtype -> trusting Client.
