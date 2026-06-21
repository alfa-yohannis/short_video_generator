---
title: builder_pattern
language: both
length: 2-3 minutes

---

# Builder Pattern

A short tutorial on the Builder pattern using a Computer assembly example: a
Computer object with many required and optional parts, constructed step by step
through a fluent Builder. Code in Java. Use DANGER for telescoping constructors
and half-built objects, OK for the Builder design, HIGHLIGHT for the builder
instance being filled in, PRIMARY for titles, ACCENT for labels.

## Introduction (~15s)
Show "Builder Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it reading that it separates how a complex object is constructed from how
it is represented. Surround the title with small part icons labeled CPU, RAM,
Storage, GPU, WiFi to hint at an object assembled from many pieces.

## The Problem (~25s)
A Java Computer class has many fields: some required like cpu, ram, storage and
some optional like gpu, wifi, bluetooth. Show a stack of overloaded
"telescoping" constructors, each adding one more parameter. Mark the longest
constructor in DANGER and highlight a confusing call with several bare values in
a row where two int arguments are easy to swap with no compiler complaint.

## The Naive Fix and Why It Fails (~25s)
Replace the constructors with a no-arg Computer plus a setter for every field.
Show a call sequence that creates the object, sets cpu, then uses it before ram
or storage are set. Mark the mutable, half-built object in DANGER and label the
window where it exists in an invalid, inconsistent state with an ACCENT tag
reading "incomplete".

## The Builder Solution (~30s)
Introduce a static nested Computer.Builder with required parts passed once at the
start and a fluent method per optional part, each returning the builder so calls
chain. End the chain with build(), which validates the parts and returns a fully
formed, immutable Computer in OK color. Track the builder instance in HIGHLIGHT as
each method fills one more field, and show the finished Computer popping out only
after build().

## Structure Diagram (~25s)
Draw a class diagram in OK: a Product box (Computer) with final fields, a Builder
box (Computer.Builder) holding the same fields plus chaining methods and build(),
and a dashed "constructs" arrow from Builder to Computer. Add an optional Director
box that knows a recipe and drives the builder through a standard sequence. Label
each role with ACCENT tags: Product, Builder, Director.

## Before and After (~30s)
Present two code panels with ACCENT headers "before" and "after". The "before"
panel shows a long positional constructor call in DANGER, hard to read and easy to
misorder. The "after" panel shows the same Computer produced by a readable fluent
chain in OK: new Builder with the required parts, then withGpu, then withWifi,
then build(). Emphasize that every step is named and the result is immutable.

## Conclusion (~15s)
Recap: build complex objects step by step through a dedicated Builder, keeping the
product immutable and construction readable. Benefits: no telescoping
constructors, no half-built objects, named optional parts, and validation in
build(). End with the flow Director -> Builder -> Product.
