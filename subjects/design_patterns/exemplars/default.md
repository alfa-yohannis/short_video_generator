---
title: strategy_pattern
language: both
length: 2-3 minutes
---

# Strategy Pattern

A short tutorial on the Strategy pattern using a shipping-cost example: a Checkout
that calculates shipping with interchangeable algorithms. Code in Java. Use
DANGER for rigid conditionals, OK for the Strategy design, HIGHLIGHT for the
current object, PRIMARY for titles, ACCENT for labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Strategy Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it. Explain it defines a family of algorithms, puts each in its own class,
and makes them interchangeable. Three shipping icons labeled Standard, Express,
Same-Day.

## The Problem (~25s)
A Java Checkout class calculates shipping with hardcoded if/else branches for
each shipping type. Show the class growing as rules are added; mark the rigid
branches in DANGER. The pain: every new algorithm forces editing this class.

## The Strategy Solution (~30s)
Define a ShippingStrategy interface with cost(Order). Show StandardShipping,
ExpressShipping, SameDayShipping implementing it, and a Checkout that holds a
ShippingStrategy and delegates with shippingStrategy.cost(order). Swap the
strategy at runtime in OK color.

## Conclusion (~15s)
Recap: encapsulate interchangeable algorithms behind one interface. Benefits:
fewer conditionals, easier testing, runtime flexibility. End with
Context -> Strategy -> ConcreteStrategy.
