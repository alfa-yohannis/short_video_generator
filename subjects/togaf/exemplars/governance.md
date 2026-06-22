---
title: architecture_governance
subject: togaf
language: both
length: 2-3 minutes
preparation_profile: togaf
---

# Architecture Governance

A short tutorial on Architecture Governance in the TOGAF framework. This is the
governance teaching method: its main visuals are a small governance CYCLE and a
board with its controls around it. TOGAF is full of technical terms, so every term
is explained in plain words the first time it appears — assume the viewer has
never heard them. TOGAF is a methodology, not program code, so every scene is
built from labelled boxes, cycles, and arrows, never source code, and never with
an invented "official TOGAF icon" (TOGAF has no standard icon set). The running
example is from everyday life: a small neighbourhood coffee shop that wants to start taking orders online. Use PRIMARY for titles, ACCENT for
labels and relationships, HIGHLIGHT for the item in focus, OK for a passing or
coherent result, and DANGER for a rule broken or an exception. The English version
should be entirely in English, including the examples.

# Preparation
Before drawing any scene, verify how TOGAF actually defines Architecture Governance
against an authoritative source (The Open Group's TOGAF Standard) rather than
recalling it from memory: the role of the Architecture Board, the governance process
steps, and the official meaning of compliance levels. So the board, its controls, and
any scale or ladder reflect the real framework, not an invented one.

## What It Is (~18s)
Show "Architecture Governance" as a LARGE CENTERED title with a short subtitle
beneath it, such as "Making sure the plan is actually followed". Explain the words
plainly: here "architecture" just means the agreed design of how a business and its
computer systems fit together, and "governance" means keeping the work on track
and to the agreed rules — like a building inspector checking a house is built to
the approved drawings. Name the example: a small coffee shop adding
online ordering.

## The Governance Cycle (~30s)
Draw a small cycle of labelled boxes — Agree the rules, Do the work, Keep watch,
Adjust — joined by curved ACCENT arrows that turn continuously. Put it in plain
words: decide how things should be done, build it, check it as it runs, fix what
drifts, then go round again. Stress it never really finishes; it keeps repeating
for every change.

## The Board and Its Controls (~31s)
Place an Architecture Board in the centre — explain it plainly as the small group
of decision-makers who approve and oversee the work, like a panel that signs off
plans. Around it, draw labelled boxes for its main controls, each with a plain
gloss joined to the board by an ACCENT arrow: Architecture Principles (agreed rules
of thumb, such as "reuse before buying something new"), an Architecture Contract
(a written promise of what will be delivered and to what standard), a Compliance
Review (a check that the work follows the rules), and the Governance Log (the
logbook of decisions and exceptions).

## How Well Does It Follow the Rules? (~27s)
Show a simple scale of labelled steps from least to most aligned — Non-Conformant,
Consistent, Compliant, Conformant, Fully Conformant. Gloss the two that matter:
"compliant" means it follows the rules that apply to it, and "conformant" means it
does everything the agreed design asks for. Put a passing project in OK and a
rule-breaking one in DANGER, and explain that a Compliance Review simply decides
where a project lands on this scale.

## A Worked Review (~37s)
Walk the coffee shop's online-ordering project through governance, the step in focus in
HIGHLIGHT. The Board checks it against two principles — "reuse before buying new"
and "keep customer data safe". It issues an Architecture Contract that sets what the
ordering app must deliver. A Compliance Review finds it mostly follows the rules, so
it is marked Compliant in OK — with one exception: it uses an outside payment
service. That exception is written down as a waiver (a recorded, approved
exception) in the Governance Log, shown in DANGER then accepted and logged in OK.

## Conclusion (~22s)
Recap in plain words: a board, agreed rules, a written contract, a check, and a
logbook — repeated for every change — keep the design honest. Mention a Maturity
Model, a simple ladder for rating how good your governance is so you can improve it
over time. End with the line of sight on screen:
Principles -> Contract -> Compliance Review -> Governance Log.
