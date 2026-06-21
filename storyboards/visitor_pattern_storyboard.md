---
title: visitor_pattern
language: both
length: 2-3 minutes
---

# Visitor Pattern

A short tutorial on the Visitor pattern using a vector-graphics example: a set of
Shape types (Circle, Rectangle, Triangle) that must support a growing list of
operations such as area calculation and XML export. Code in Java. Use DANGER for
operation logic crammed into the shape classes, OK for the Visitor design,
HIGHLIGHT for the current object during double dispatch, PRIMARY for titles,
ACCENT for labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Visitor Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it. Explain it lets you add new operations to an object structure without
changing the classes of the elements it operates on. Three shape icons labeled
Circle, Rectangle, Triangle, with a small ACCENT tag reading "operations" hovering
over the trio.

## The Problem (~25s)
A Java Shape hierarchy with Circle, Rectangle, and Triangle. The team keeps
inventing new operations: area, perimeter, XML export, JSON export, bounding box.
Show a matrix of shapes against operations and watch the cells multiply. The pain:
operations are unrelated to a shape's core data, yet they all want to live somewhere.

## The Naive Approach (~25s)
Each Shape class grows a method per operation: area(), toXml(), toJson(). Show
Circle, Rectangle, and Triangle each bloating with the same set of methods, marked
in DANGER. Highlight the real cost: adding one new operation forces editing every
shape class, and unrelated concerns like XML pile up inside geometry code.

## The Visitor Solution (~30s)
Introduce a ShapeVisitor interface with visit(Circle), visit(Rectangle), and
visit(Triangle). Each Shape keeps just one method, accept(ShapeVisitor), which
calls visitor.visit(this). Operations move into ConcreteVisitors like AreaVisitor
and XmlExportVisitor, drawn in OK. Show a shape calling accept and the visitor
calling back into the matching visit — the double-dispatch handshake glows in
HIGHLIGHT.

## Structure Diagram (~25s)
Draw the class diagram: a Shape interface declaring accept(ShapeVisitor), with
Circle, Rectangle, Triangle as ConcreteElements. A ShapeVisitor interface
declaring one visit method per shape type, realized by AreaVisitor and
XmlExportVisitor as ConcreteVisitors in OK. Animate the two dispatch arrows:
element to accept, then visitor to the matching visit. Label this pair "double
dispatch" in ACCENT.

## Before and After (~30s)
Replay the contrast. Before: a Circle stuffed with area(), toXml(), toJson() in
DANGER, and a note that new operations reopen every shape. After: a lean Circle
with only accept(visitor) in OK, and a fresh PerimeterVisitor appearing as a single
new class that needs zero edits to the shapes. The current shape being visited stays
in HIGHLIGHT as the visitor sweeps the structure.

## Conclusion (~15s)
Recap: separate algorithms from the objects they run on, and add operations as new
visitors instead of editing elements. Benefits: cleaner element classes, easy new
operations, related logic gathered in one place. End with
Element -> accept(Visitor) -> visit(Element).
