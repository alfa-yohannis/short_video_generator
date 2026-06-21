---
title: decorator_pattern
language: both
length: 2-3 minutes
---

# Decorator Pattern

A short tutorial on the Decorator pattern using a coffee-shop example: a Beverage
whose cost and description grow as optional add-ons are wrapped around it. Code in
Java. Use DANGER for the subclass explosion and rigid flags, OK for the Decorator
design, HIGHLIGHT for the object currently being wrapped, PRIMARY for titles,
ACCENT for labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Decorator Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it. Explain it attaches new responsibilities to an object dynamically by
wrapping it in another object that shares the same interface. A plain coffee cup
icon gains thin labeled layers Milk, Sugar, Whip wrapped around it one by one.

## The Problem (~25s)
A coffee shop sells an Espresso with optional add-ons. Show a Java class hierarchy
that tries to cover every combination with its own subclass: Espresso,
EspressoWithMilk, EspressoWithMilkAndSugar, EspressoWithMilkSugarAndWhip, and on
and on. Mark the exploding pile of subclasses in DANGER. The pain: each new add-on
roughly doubles the number of classes.

## The Naive Approach (~25s)
Replace the subclasses with a single Beverage class carrying boolean flags
hasMilk, hasSugar, hasWhip, and a cost() method packed with conditionals that add
a little for each flag that is set. Show the method swelling as flags are added;
mark the flags and the branching in DANGER. The pain: every new add-on edits this
one shared class, and customers cannot stack the same add-on twice.

## The Decorator Solution (~30s)
Define a Beverage interface with cost() and description(). Espresso implements it
as the plain ConcreteComponent. Introduce an abstract CondimentDecorator that also
implements Beverage and holds a wrapped Beverage. Milk, Sugar, and Whip extend it;
each adds its own charge to cost() and its own word to description(), then
delegates to the wrapped Beverage. Show the wrapping happen in OK, with the
inner Espresso kept in HIGHLIGHT as each layer is added.

## Class Structure (~25s)
Show the class diagram. The Beverage interface sits at the heart as PRIMARY, with
Espresso implementing it. CondimentDecorator implements Beverage and also holds a
Beverage reference, drawn as the wrapping link. Milk, Sugar, and Whip extend
CondimentDecorator. Use ACCENT labels Component, ConcreteComponent, Decorator, and
ConcreteDecorator to name each role.

## Before and After (~30s)
Compare the two styles. The before snippet sets boolean flags on one Beverage and
relies on conditionals inside cost(), shown in DANGER. The after snippet composes
the order by nesting wrappers: Beverage drink = new Whip(new Sugar(new
Milk(new Espresso()))), then calls drink.cost() and drink.description(), shown in
OK. Keep the innermost Espresso in HIGHLIGHT so the layering reads clearly.

## Conclusion (~15s)
Recap: wrap an object to add behavior without touching its class, and stack
wrappers to mix and match responsibilities at runtime. Benefits: open for
extension, no subclass explosion, and add-ons that combine freely. End with
Component -> Decorator -> ConcreteDecorator.
