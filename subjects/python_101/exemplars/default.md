---
title: python_functions
subject: python_101
language: both
length: 2-3 minutes
---

# Python Functions

A short beginner tutorial on defining and calling functions in Python 3, using a
small running example: a function that turns a price into a discounted price.
This is a code-only tutorial on the dark editor theme, so every scene types its
code in (typewriter) and shows the printed output beside it. Use DANGER for a
buggy result, OK for the correct output, HIGHLIGHT for the line in focus, PRIMARY
for titles, ACCENT for labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Python Functions" as a LARGE CENTERED title, with a short subtitle directly
beneath it reading that functions are reusable, named blocks of code. A small
hint that the next scenes will type real Python and run it.

## What Is a Function (~25s)
Type in a tiny function definition with the `def` keyword, a name, a parameter,
and a `return`. Type-reveal each part and label the pieces in ACCENT: the `def`
keyword, the function name, the parameter, and the returned value. Keep the code
on one card.

## Calling the Function (~30s)
Below the definition, type a call that passes an argument and prints the result.
Show the matching terminal output panel with the printed value in OK. Emphasize
in HIGHLIGHT how the argument flows into the parameter and the returned value
flows back out.

## A Common Mistake (~30s)
Show a beginner pitfall: a function that computes a value but forgets to `return`
it, so the caller prints `None`. Mark the missing return and the `None` output in
DANGER. Then type the one-line fix — add the `return` — and show the corrected
output in OK.

## Default Arguments (~25s)
Extend the example with a default parameter value, type it in, and show two calls
(one passing the argument, one relying on the default) with both results in the
output panel. Label the default value in HIGHLIGHT.

## Recap (~15s)
Recap the parts of a function: `def`, name, parameters, body, `return`. End with a
short reminder that functions let you name and reuse logic, shown as a clean
bullet list with the example function name in OK.
