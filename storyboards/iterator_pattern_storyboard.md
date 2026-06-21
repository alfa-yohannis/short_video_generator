---
title: iterator_pattern
language: both
length: 2-3 minutes
---

# Iterator Pattern

A short tutorial on the Iterator pattern using a book-collection example: a
BookShelf that lets clients walk through its elements one at a time without ever
seeing how they are stored. Code in Java. Use DANGER for traversal logic welded
to a collection's internals, OK for the Iterator design, HIGHLIGHT for the
current cursor position, PRIMARY for titles, ACCENT for role labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Iterator Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it. Explain it provides a way to access the elements of a collection
sequentially without exposing how the collection stores them. Show a row of book
icons with a single moving marker stepping from one book to the next, the active
book tinted HIGHLIGHT.

## The Problem (~25s)
A Java BookShelf class stores Book objects in a fixed array with a count field.
Client code walks it with a manual index loop, reading shelf.getBookAt(i) for i
from zero up to shelf.getCount(). Mark the index arithmetic and the array-shaped
access in DANGER. The pain: the loop knows the shelf is an array, so the storage
choice has leaked into every place that reads the collection.

## A Naive Fix (~20s)
Try to "decouple" by exposing the internals through getBooks() returning a raw
Book[]. The client now iterates that array directly. Then introduce a Magazine
collection backed by a LinkedList: every existing loop breaks, because linked
traversal looks nothing like array indexing. Keep the leaked structure and the
duplicated, structure-specific loops in DANGER.

## The Iterator Solution (~30s)
Define an Iterator interface with hasNext() and next(). Define an Aggregate
interface with createIterator(). BookShelf implements Aggregate and returns a
BookShelfIterator that holds its own cursor field. The client loops with
while (it.hasNext()) processing it.next(), never touching the array. Draw the
design in OK and tint the cursor's current element in HIGHLIGHT as it advances.

## Structure Diagram (~25s)
A class diagram. Show the Iterator interface and the Aggregate interface as the
two roles, their names tagged with ACCENT labels and boxed in PRIMARY. Show
ConcreteIterator (BookShelfIterator) realizing Iterator, and ConcreteAggregate
(BookShelf) realizing Aggregate. Connect BookShelf to the iterator it produces,
and connect the iterator to the BookShelf it walks. Mark hasNext, next, and
createIterator on the interfaces.

## Before and After (~30s)
Two side-by-side code panels sharing the same client task: print every title.
The "before" panel ties an index loop to BookShelf's array and is repeated for
the LinkedList collection, all in DANGER. The "after" panel is one loop over an
Iterator in OK; the exact same client code drives both BookShelf and the
LinkedList-backed collection, since each just hands back its own iterator.

## Conclusion (~15s)
Recap: hand out a small Iterator object so collections can be traversed
uniformly while their storage stays hidden. Benefits: one traversal style for
many structures, encapsulated internals, several independent walks at once, and
each class keeping a single responsibility. End with Aggregate -> Iterator ->
ConcreteIterator.
