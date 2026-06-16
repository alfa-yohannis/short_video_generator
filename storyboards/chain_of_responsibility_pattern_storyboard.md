---
title: chain_of_responsibility_pattern
language: both
length: 2-3 minutes
---

# Chain of Responsibility Pattern

A short tutorial on the Chain of Responsibility pattern using an expense-approval
example: a PurchaseRequest that travels through a series of approvers until one of
them is authorized to handle it. Code in Java. Use DANGER for the rigid nested
conditional, OK for the chain design, HIGHLIGHT for the handler currently
inspecting the request, PRIMARY for titles, ACCENT for labels and links.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Chain of Responsibility Pattern" as a LARGE CENTERED title in PRIMARY, with
a short subtitle directly beneath it reading that it passes a request along a chain
of handlers until one handles it. A small PurchaseRequest token glides past three
linked handler boxes labeled in ACCENT: Manager, Director, CEO.

## The Problem (~25s)
Introduce a company expense system in Java. A single ExpenseService.approve method
must decide who can sign off a PurchaseRequest based on its amount: small amounts
go to a manager, larger ones to a director, the biggest to the CEO. Show one
PurchaseRequest with an amount field entering this one method, with the hint that
the approval rules and the approvers are tangled into a single place.

## The Naive Approach (~25s)
Reveal the body of ExpenseService.approve as a deep nested if / else if ladder
that compares the amount against hardcoded limits and prints which role approved.
Paint the whole conditional ladder in DANGER. Call out the pain: every new
approver tier forces editing this method, the limits are scattered, and the
sender is hard-wired to know every possible receiver.

## The Chain Solution (~30s)
Define an abstract Approver in OK color holding a successor reference and a method
setNext(Approver) that returns the successor for fluent linking. Its approve method
checks whether the request fits this approver's limit; when it fits, it signs off,
otherwise it forwards to the successor with next.approve(request). Show concrete
ManagerApprover, DirectorApprover, and CeoApprover, each owning only its own limit.
Animate a PurchaseRequest hopping handler to handler, the active one glowing in
HIGHLIGHT, until one approves.

## Class Structure (~25s)
Draw the diagram. An abstract Approver box lists a next:Approver field and the
methods setNext(Approver) and approve(PurchaseRequest), tagged in ACCENT. Three
concrete approver boxes inherit from it. A Client box builds the chain with
manager.setNext(director).setNext(ceo). Connect each handler to its successor with
ACCENT arrows so the linear chain is visible, and link the client to the chain's
head.

## Before and After (~25s)
Two panels. The first holds the old ExpenseService.approve with its nested if / else
ladder in DANGER. The second holds the chain version in OK: a slim approve in each
small Approver subclass, plus a few setNext lines wiring the chain. Highlight that
adding a new VicePresidentApprover means writing one new class and inserting one
link, with no edits to existing handlers or to the caller.

## Conclusion (~15s)
Recap in PRIMARY: decouple the sender of a request from its receivers by passing it
down a chain of handlers. Benefits listed in ACCENT: no giant conditional, each
handler has one responsibility, and the chain can be reordered or extended at
runtime. End with Client -> Approver -> ConcreteApprover -> next.
