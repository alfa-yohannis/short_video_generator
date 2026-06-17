---
title: python_variables
subject: python_101
language: en
orientation: portrait
length: 2-3 minutes
---

# Python Variables

A short beginner tutorial on variables in Python 3, using one small running
example: a quiz score tracker for a player named Gatotkaca. This is a code-only
tutorial on the dark editor theme, so every scene types its code in (typewriter)
and shows the printed output in a terminal panel. Use a FIXED layout that stays
consistent across all scenes: a code panel that the code is typed into, and a
separate output panel for what it prints — anchored in the same place and size in
every scene via `place_code` and `place_output`. Scenes that explain no code (the
title card and the call-to-action) use neither panel. Use DANGER for a buggy
result, OK for the correct output, HIGHLIGHT for the line in focus, PRIMARY for
titles, ACCENT for labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Open with a hook that types itself in to grab attention — a short question reading
"How does a program remember your name and your score?" in HIGHLIGHT. Let it land
for a beat, then clear it and reveal "Python Variables" as a LARGE CENTERED title,
with a short subtitle directly beneath it reading that a variable is a name that
holds a value you can use and change. End with a small hint that the next scenes
will type real Python and run it. Keep the hook and the title as separate beats so
they never sit on screen at the same time.

## What Is a Variable (~25s)
Type two simple assignments onto one card: a name bound to a number, and a name
bound to some text — a score starting at zero and a player name. Type-reveal each
piece; as the narration names the variable name, the `=` that does the
assignment, and the value it stores, briefly HIGHLIGHT that token in the code
itself rather than adding separate floating labels. Then type a `print` of both
names and show the matching terminal output panel with the player name and score
printed in OK. Emphasize that the name now refers to its value.

Type exactly this code:

```python
score = 0
player = "Gatotkaca"
print(player, score)
```

Terminal output (in OK):

```text
Gatotkaca 0
```

## Variables Have Types (~22s)
Explain that every value has a type and Python infers it from the value — you
never declare it. On a code card, type quick `type(...)` checks on the example's
own variables plus two more everyday literals: the whole-number score is an int,
the name is a str, a decimal like a price is a float, and a true or false flag is
a bool. Reveal the matching terminal output panel where each line reports its
type. As the narration names each one, briefly HIGHLIGHT that line in the code
itself rather than adding floating labels. Close with a single spoken note that
because the type follows the value, the same name can later hold a value of a
different type — that is dynamic typing — and that a dedicated video covers
converting between types in depth.

Type exactly this code:

```python
print(type(score))
print(type(player))
```

Terminal output (in OK):

```text
<class 'int'>
<class 'str'>
```

## Updating a Variable (~25s)
Show that a variable can be reassigned. Type `score = score + 10`, then type the
same line again, and show the stored value moving from zero to ten to twenty.
Pair it with the terminal output panel printing the latest score in OK, and mark
the line currently running in HIGHLIGHT. Emphasize that the value on the right is
computed first, then the name is rebound to the new result.

Type exactly this code:

```python
score = score + 10
score = score + 10
print(score)
```

Terminal output (in OK):

```text
20
```

## A Common Mistake (~30s)
Show a classic beginner pitfall: trying to build a message by joining text and a
number directly. Type `message = "Score: " + score` and run it. Mark the joining
expression and the resulting TypeError in DANGER, and explain that Python will not
add a piece of text and a number together because they are different types.

Type exactly this code:

```python
message = "Score: " + score
print(message)
```

Terminal output (the error, in DANGER):

```text
TypeError: can only concatenate str (not "int") to str
```

## The Fix (~25s)
Type the one-line fix: use an f-string to drop the score straight into the text,
then print the message. Show the corrected terminal output reading the score
message in OK. Note that the f-string turns the number into text automatically,
and mention wrapping the number in `str(...)` as an alternative, labeled in
ACCENT.

Type exactly this code:

```python
message = f"Score: {score}"
print(message)
```

Terminal output (in OK):

```text
Score: 20
```

Type the alternative as a labeled aside (in ACCENT):

```python
message = "Score: " + str(score)
```

## Like, Subscribe and Share (~6s)
A short call to action: reveal the single line "If you find this video helpful, please
like, subscribe, and share" with the words Like, Subscribe, and Share in
HIGHLIGHT. Keep it as its own clean beat — no code or output panel.

## Recap (~20s)
Recap as a clean bullet list: a variable is a name bound to a value with `=`; its
type is inferred from the value; reassign the name to update it; use an f-string
to mix text and numbers. Then show the final state of the example (in OK).

```python
player = "Gatotkaca"
score = 20
```

Close by turning to the audience as a separate final beat: clear the recap, then
type a short question in HIGHLIGHT asking what they would store in their very
first variable, and invite them to drop their answer or any questions in the
comments. Keep this engagement prompt on its own so it stays clear of the recap
list and above the caption-safe zone.
