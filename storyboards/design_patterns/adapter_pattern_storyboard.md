---
title: adapter_pattern
language: both
length: 2-3 minutes
---

# Adapter Pattern

A short tutorial on the Adapter pattern using a payments example: a Checkout that
expects a clean PaymentProcessor interface, while a third-party bank gateway speaks
a different, incompatible API. Code in Java. Use DANGER for the mismatched calls and
conversion code leaking into the client, OK for the Adapter design, HIGHLIGHT for the
wrapped object, PRIMARY for titles, ACCENT for labels.

## Introduction (~15s)
Show "Adapter Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it reading "make incompatible interfaces work together". Explain it wraps an
existing class in a new interface the client expects, so two parties that were never
designed to fit can collaborate. Two puzzle pieces with mismatched shapes snap
together through a small connector piece in OK.

## The Problem (~25s)
A Java Checkout depends on a PaymentProcessor interface with pay(double amount). The
business buys a third-party BankGateway whose only method is sendPayment(long cents,
String currency). Show Checkout trying to call gateway.pay(...) and the call failing
to compile, marked in DANGER. The shapes do not line up: dollars versus cents, one
argument versus two.

## The Naive Approach (~25s)
Show the tempting fix: change Checkout to call gateway.sendPayment(amount * 100,
"USD") directly, scattering dollars-to-cents math and currency strings through the
client. Highlight in DANGER that Checkout now hard-depends on the vendor type, the
conversion logic is duplicated at every call site, and swapping vendors means
rewriting Checkout.

## The Adapter Solution (~30s)
Introduce BankGatewayAdapter that implements PaymentProcessor and holds a BankGateway
as the wrapped object in HIGHLIGHT. Its pay(double amount) converts dollars to cents,
supplies the currency, and delegates to sendPayment. Show Checkout depending only on
PaymentProcessor, unaware of the vendor, in OK. The conversion lives in exactly one
place.

## Structure Diagram (~25s)
Draw the roles as a class diagram. Target labeled PaymentProcessor in PRIMARY with
pay(amount). Adaptee labeled BankGateway in ACCENT with sendPayment(cents, currency).
Adapter labeled BankGatewayAdapter implementing the Target and composing the Adaptee,
drawn in OK with a HIGHLIGHT arrow showing delegation. Client labeled Checkout
pointing only at the Target.

## Before and After (~30s)
Split the screen. The before side shows Checkout littered with amount * 100, "USD",
and the concrete BankGateway type, all in DANGER. The after side shows a slim Checkout
holding a PaymentProcessor field and a single pay(total) call, with
BankGatewayAdapter quietly doing the translation in OK. Emphasize that adding a second
vendor now means writing one more adapter, never touching Checkout.

## Conclusion (~15s)
Recap: wrap an existing, incompatible class behind the interface the client expects.
Benefits: the client stays clean and vendor-agnostic, conversion logic is isolated,
and new providers plug in without edits. End with Client -> Target -> Adapter ->
Adaptee.
