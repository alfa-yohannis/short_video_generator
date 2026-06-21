---
title: dependency_inversion_principle_pattern
language: both
length: 2-3 minutes
---

# Dependency Inversion Principle Pattern

A short tutorial on the Dependency Inversion Principle (SOLID) using an order-saving
example: an OrderService that must persist orders without being welded to one storage
technology. Code in Java. Use DANGER for the rigid dependency on a concrete class, OK
for the inverted abstraction-based design, HIGHLIGHT for the current focus, PRIMARY for
titles, ACCENT for labels.

## Introduction (~15s)
Show "Dependency Inversion Principle" as a LARGE CENTERED title, with a short subtitle
directly beneath it. State the idea: high-level modules and low-level modules should both
depend on abstractions, not on each other; abstractions must not depend on details.
Two blocks labeled Policy and Detail meeting at a shared interface icon in PRIMARY.

## The Problem (~25s)
Introduce a Java OrderService — the high-level business policy that must save an order.
Show it reaching straight into a concrete MySQLDatabase, the low-level detail. Draw a
thick dependency arrow from OrderService directly onto MySQLDatabase marked in DANGER.
The pain: the business policy is now chained to one specific storage technology.

## The Naive Approach (~25s)
Inside OrderService a method runs new MySQLDatabase() and calls its save method; mark
that construction in DANGER. List the consequences: the store cannot be swapped, the
policy cannot be tested without a real database, and any storage change forces edits to
the business class. Add a new wish "switch to MongoDB" and show OrderService cracking
under the strain.

## Inverting the Dependency (~30s)
Define a Database interface declaring save(Order) — the abstraction, drawn in OK. Show
MySQLDatabase and MongoDatabase both implementing it. OrderService now holds a Database
field and receives it through its constructor (injection) rather than building one
itself. Redraw the arrows so both the OrderService policy and the concrete stores now
point toward the Database abstraction, highlighted in HIGHLIGHT.

## The Structure (~25s)
Class diagram with the Database interface at the center in PRIMARY exposing save(Order).
OrderService depends on Database, tagged with an ACCENT label "depends on abstraction".
MySQLDatabase and MongoDatabase realize the Database interface. Emphasize that arrows
from the high-level policy and the low-level details converge on the same abstraction —
the dependency has been inverted.

## Before and After (~30s)
Two panels. Before: OrderService internally calls new MySQLDatabase() and is hardwired
to it, the coupling marked in DANGER. After: the constructor accepts a Database, stores
it as a field, and save delegates with db.save(order) in OK. Then pass a fake
InMemoryDatabase into the same OrderService for a unit test, shown in HIGHLIGHT, proving
the policy works against any implementation.

## Conclusion (~15s)
Recap: depend on abstractions, never on concretions, and supply the details from
outside. Benefits: interchangeable implementations, easy testing, and a stable business
policy that no longer changes when storage does. End with OrderService -> Database
interface <- MySQLDatabase / MongoDatabase.
