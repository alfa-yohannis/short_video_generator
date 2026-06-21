---
title: template_method_pattern
language: both
length: 2-3 minutes
---

# Template Method Pattern

A short tutorial on the Template Method pattern using a beverage-preparation
example: a CaffeineBeverage base class that fixes the recipe skeleton while Tea
and Coffee fill in the steps that differ. Code in Java. Use DANGER for
duplicated and rigid steps, OK for the Template Method design, HIGHLIGHT for the
current object, PRIMARY for titles, ACCENT for labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Template Method Pattern" as a LARGE CENTERED title, with a short subtitle
directly beneath it. Explain it defines the skeleton of an algorithm in a base
method and defers selected steps to subclasses, so the overall flow stays fixed
while individual steps vary. Two beverage icons labeled Tea and Coffee share one
recipe outline drawn in PRIMARY.

## The Problem (~25s)
Two Java classes, Tea and Coffee, each implement a full prepareRecipe() method.
Both repeat the identical boilWater() and pourInCup() steps word for word; mark
these duplicated steps in DANGER. Highlight that the recipe order lives in two
places, so fixing the sequence means editing every beverage class.

## The Naive Approach (~20s)
Attempt a single Beverage class with a flag and if/else branches choosing tea or
coffee behavior inside prepareRecipe(). Show the conditionals in DANGER and note
that adding a third drink reopens this method and risks breaking the shared
sequence. Label this "still rigid" in ACCENT.

## The Template Method Solution (~30s)
Introduce an abstract CaffeineBeverage class. Its prepareRecipe() is a final
template method that calls boilWater(), brew(), pourInCup(), then addCondiments()
in fixed order, shown in OK. boilWater() and pourInCup() are concrete and shared;
brew() and addCondiments() are abstract steps. The fixed skeleton is locked while
the varying steps stay open for subclasses, marked in ACCENT.

## Structure Diagram (~25s)
Draw the class structure: an abstract CaffeineBeverage box holding the
prepareRecipe() template method plus abstract brew() and addCondiments(). Two
subclasses, Tea and Coffee, connect with inheritance arrows and each supply their
own brew() and addCondiments(). HIGHLIGHT the template method as the single owner
of the algorithm's order; ACCENT the abstract steps as the extension points.

## Before and After (~30s)
Place the two versions together. The before side shows Tea and Coffee each
repeating the whole recipe with the duplicated steps in DANGER. The after side
shows Tea overriding brew() to steep a tea bag and addCondiments() to add lemon,
and Coffee overriding brew() to drip through a filter and addCondiments() to add
sugar and milk, both inheriting prepareRecipe() unchanged in OK. HIGHLIGHT the
active subclass as prepareRecipe() runs.

## Conclusion (~15s)
Recap: keep the algorithm's skeleton in one final method and let subclasses
redefine only the varying steps. Benefits: no duplicated sequence, a single place
that controls order, and easy new beverages. End with AbstractClass ->
templateMethod() -> ConcreteSteps.
