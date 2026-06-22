---
title: gap_analysis
subject: togaf
language: both
length: 2-3 minutes
preparation_profile: togaf
---

# Gap Analysis

A short tutorial on Gap Analysis, a technique used in several phases of the TOGAF
framework. This is the technique teaching method: it leads with the technique's
signature TOOL — the Gap Analysis MATRIX, a clean labelled grid — and shows how to
read it. TOGAF is full of technical terms, so every term is explained in plain
words the first time it appears — assume the viewer has never heard them. TOGAF is
a methodology, not program code, so every scene is built from labelled grids,
boxes, and arrows, never source code, and never with an invented "official TOGAF
icon" (TOGAF has no standard icon set). The running example is from everyday life:
a small neighbourhood coffee shop that wants to start taking orders
online. Use PRIMARY for titles, ACCENT for headers and labels, HIGHLIGHT for the
cell in focus, OK for something you already have, and DANGER for a gap you must
fill. The English version should be entirely in English, including the examples.

# Preparation
Before drawing any scene, verify how TOGAF actually describes Gap Analysis against an
authoritative source (The Open Group's TOGAF Standard) rather than recalling it from
memory: how the matrix is laid out (baseline along one axis, target along the other,
with an "eliminated/missing" row and column) and which ADM phases use it. If any scene
shows the ADM ring, confirm the canonical layout too — the ring is Phases A through H
only, with the Preliminary phase outside it feeding into Phase A and Phase H looping
back to Phase A — so the tool and its context reflect the real framework.

## What It Is (~18s)
Show "Gap Analysis" as a LARGE CENTERED title with a short subtitle beneath it,
such as "What is missing between today and the goal". Explain the words plainly:
the "baseline" is what you have today, the "target" is what you want, and a "gap"
is anything the target needs that you do not have yet. Gap Analysis simply compares
the two and lists those gaps. Name the example: a small coffee shop
adding online ordering.

## The Gap Matrix (~33s)
Draw the signature tool: a labelled grid. Across the headers, list what you want
(the target); down the side, list what you have today (the baseline); add a final
"Removed" row and a "New" column, each ACCENT-labelled. Explain in plain words how
to read a cell — a filled cell means something you have already covers what you
want, a "New" cell means the goal needs something that does not exist yet, and a
"Removed" cell means you are deliberately dropping something.

## Reading the Gaps (~27s)
Walk the cells. A covered cell sits in OK — you keep it. A "New" cell is the real
gap, marked in DANGER and HIGHLIGHTed — it becomes a job to do. A "Removed" cell is
a choice you made, not a mistake. Say it plainly: every empty box in the target
that should be filled is a gap, and the gaps are your to-do list.

## A Worked Matrix (~40s)
Fill the grid for the coffee shop. What they have today: a till at the counter, phone
orders, and card payments. What they want: online ordering, delivery tracking,
customer accounts, and card payments. Card payments are already covered, shown in
OK. Phone orders are Removed. Online ordering, delivery tracking, and customer
accounts are New — three gaps in DANGER. Collect the three gaps into a short to-do
list in OK, each becoming a piece of work to deliver.

## Where It Is Used (~24s)
Show a small ADM ring (TOGAF's step-by-step cycle) with three phases in HIGHLIGHT —
Business, Information Systems, and Technology — and explain in one line that Gap
Analysis is run in each to compare today with the goal for how the shop works, its
software, and its technology. Draw an ACCENT arrow from the to-do list into an
Architecture Roadmap — simply the schedule of which gap is closed when.

## Conclusion (~22s)
Recap in plain words: list what you have and what you want, lay them on a grid, and
read off what is new, kept, or dropped. The gaps become the plan of work. End with
the line of sight on screen: Today -> Goal -> Gaps -> Work to Do.
