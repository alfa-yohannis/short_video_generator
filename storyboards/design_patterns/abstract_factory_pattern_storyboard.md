---
title: abstract_factory_pattern
language: both
length: 2-3 minutes
---

# Abstract Factory Pattern

A short tutorial on the Abstract Factory pattern using a cross-platform UI toolkit
example: an Application that builds a family of matching widgets (Button and
Checkbox) for either a Windows or a Mac look-and-feel. Code in Java. Use DANGER
for scattered direct instantiation and mismatched families, OK for the Abstract
Factory design, HIGHLIGHT for the active factory, PRIMARY for titles, ACCENT for
labels.

## Introduction (~15s)
Show "Abstract Factory Pattern" as a LARGE CENTERED title, with a short subtitle
directly beneath it. Explain it provides one interface for creating whole families
of related objects without naming their concrete classes. Show two grouped icon
sets in ACCENT labeled Windows and Mac, each holding a matching Button and Checkbox.

## The Problem (~25s)
A Java Application builds a UI screen that needs a Button and a Checkbox that share
the same look-and-feel. Show code calling new WindowsButton() and new MacCheckbox()
directly, scattered across the class, in DANGER. Reveal the pain: the concrete
classes are hardcoded everywhere, and nothing stops a Windows button from sitting
beside a Mac checkbox.

## The Naive Approach (~25s)
Replace direct construction with a platform flag and if/else branches deciding which
concrete widget to create, repeated at every place a widget is needed. Mark the
duplicated conditionals in DANGER. Show how one forgotten branch quietly mixes a
WindowsButton with a MacCheckbox, breaking the consistent look-and-feel.

## The Abstract Factory Solution (~30s)
Define a GUIFactory interface with createButton() and createCheckbox(). Show
WindowsFactory and MacFactory implementing it in OK color, each returning only its
own matching widgets. The Application holds a single GUIFactory field and builds the
screen through factory.createButton() and factory.createCheckbox(), never naming a
concrete class. HIGHLIGHT the chosen factory to show one family is locked in.

## Structure Diagram (~25s)
Show the class structure. A GUIFactory interface in PRIMARY with createButton and
createCheckbox, implemented by ConcreteFactories WindowsFactory and MacFactory.
Two product interfaces, Button and Checkbox, each implemented by a Windows variant
and a Mac variant, labeled in ACCENT. Draw a Client depending only on GUIFactory,
Button, and Checkbox, with arrows showing each ConcreteFactory produces its own
matching ConcreteProducts.

## Before and After Code (~25s)
Compare two snippets. The before snippet shows the platform flag and repeated
if/else new-statements in DANGER. The after snippet shows the Application receiving
a GUIFactory once and calling factory.createButton() and factory.createCheckbox()
in OK, with the active WindowsFactory in HIGHLIGHT. Note that swapping to MacFactory
changes the whole family in a single place.

## Conclusion (~15s)
Recap: group the creation of related objects behind one factory interface so a whole
family stays consistent. Benefits: no hardcoded concrete classes, guaranteed
matching products, and easy switching between families. End with
Client -> AbstractFactory -> ConcreteFactory -> Products.
