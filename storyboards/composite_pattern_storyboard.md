---
title: composite_pattern
language: both
length: 2-3 minutes
---

# Composite Pattern

A short tutorial on the Composite pattern using a file-system example: a file
explorer that computes the total size of files and folders, where a folder may
contain files and more folders. Code in Java. Use DANGER for type-checking and
manual recursion, OK for the Composite design, HIGHLIGHT for the current node,
PRIMARY for titles, ACCENT for labels.

## Introduction (~15s)
Show "Composite Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it. Explain it composes objects into tree structures so that single
objects and whole groups are treated through one uniform interface. Two icons
labeled File and Folder, with the Folder fanning out into smaller files in ACCENT.

## The Problem (~25s)
A file explorer must report the total size of a folder. Files and folders are
different Java types, yet a folder can hold files and other folders nested to any
depth. Show a tree of mixed File and Folder nodes growing, and mark the awkward
mismatch between a flat method call and a deeply nested structure in DANGER.

## The Naive Approach (~25s)
A single SizeCalculator inspects each node with instanceof, casts Folder to reach
its children, and recurses by hand for every level. Show the chained type checks
and casts in DANGER. The pain: client code carries the recursion, and every new
node kind forces editing this calculator.

## The Composite Solution (~30s)
Define a FileSystemNode interface with size(). TextFile and ImageFile are leaves
returning their own bytes. Folder is the composite: it keeps a list of
FileSystemNode children, exposes add(child), and computes size() by summing each
child's size(). Show the client calling node.size() on any node uniformly in OK,
with the active node in HIGHLIGHT as the recursion flows through the tree.

## Structure Diagram (~25s)
Draw the structure: FileSystemNode as the central component in PRIMARY, labeled
Component in ACCENT. TextFile and ImageFile branch off as Leaf in OK. Folder
branches off as Composite in OK and aggregates many FileSystemNode, shown by an
arrow looping back to the component to express self-similar nesting.

## Before and After (~30s)
Contrast two Java snippets. The earlier one in DANGER: a calculator switching on
instanceof, casting, and recursing manually. The reworked one in OK: leaves
implement size() directly, Folder sums children with a simple loop, and the
client just writes root.size() with no type checks. HIGHLIGHT the single uniform
call that replaces the branching.

## Conclusion (~15s)
Recap: compose objects into trees and treat leaves and composites through one
interface, letting the structure own its own recursion. Benefits: simpler client
code, no type checks, easy to extend with new node kinds. End with
Component -> Leaf and Component -> Composite.
