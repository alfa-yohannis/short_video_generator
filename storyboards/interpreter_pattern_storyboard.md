---
title: interpreter_pattern
language: both
length: 2-3 minutes
---

# Interpreter Pattern

A short tutorial on the Interpreter pattern using an arithmetic-expression
evaluator: turn a sentence like "5 + 3 - 2" into a tree of small expression
objects that each know how to interpret themselves. Code in Java. Use DANGER for
the tangled string-parsing evaluator, OK for the Interpreter design, HIGHLIGHT
for the expression node currently being evaluated, PRIMARY for titles, ACCENT for
labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Interpreter Pattern" as a LARGE CENTERED title, with a short subtitle
directly beneath it. Explain it defines a grammar for a small language and gives
each grammar rule its own class that knows how to interpret itself. Display a
sample sentence "5 + 3 - 2" in ACCENT as the language we want to understand.

## The Problem (~25s)
A Java Calculator class evaluates expression strings inside one giant evaluate
method: it splits the text, scans token by token, and branches with nested
if/else for every operator. Show the method swelling as "+", "-", and parentheses
get bolted on; mark the tangled parsing branches in DANGER. The pain: the grammar
and the evaluation logic are fused into one block that everyone must edit.

## Grammar Becomes Objects (~25s)
Reframe the idea: every rule of the grammar turns into its own class. A bare
number is a terminal rule; an addition or a subtraction is a composite rule built
from smaller expressions. Show the sentence "5 + 3 - 2" reshaping into a tidy tree
of nodes in OK, each node a self-contained piece of grammar with one job.

## The Interpreter Solution (~30s)
Define an Expression interface with interpret(Context). Show NumberExpression as
the terminal holding a literal value, and AddExpression and SubtractExpression as
composites that each hold two operand Expressions and combine their interpreted
results. A Parser assembles these objects into a tree; calling interpret on the
root walks the whole structure. HIGHLIGHT each node as its interpret call fires,
in OK color.

## Class Structure (~25s)
Draw the class diagram: the Expression interface at the crown, with
NumberExpression, AddExpression, and SubtractExpression branching from it as
implementations. Label NumberExpression as TerminalExpression and the operator
classes as NonterminalExpression in ACCENT. Show the composition link where each
nonterminal references two child Expressions, forming the recursive tree.

## Before and After (~30s)
Place the two designs together. The before: the monolithic evaluate method
parsing and switching on raw strings, every branch in DANGER. The after: a parsed
tree of NumberExpression, AddExpression, and SubtractExpression objects, root
.interpret(context) returning 6, all in OK. Show a brand-new MultiplyExpression
class dropping in cleanly without touching any existing class.

## Conclusion (~15s)
Recap: model each grammar rule as a class, then interpret a sentence by walking
the tree those classes form. Benefits: an extensible grammar, recursive
evaluation for free, and new rules added in isolation. End with
Context -> Expression -> Terminal and Nonterminal expressions.
