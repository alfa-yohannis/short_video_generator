---
title: mediator_pattern
language: both
length: 2-3 minutes
---

# Mediator Pattern

A short tutorial on the Mediator pattern using a chat-room example: many User
objects that must talk to each other. Code in Java. Use DANGER for the tangled
direct references between users, OK for the clean Mediator design, HIGHLIGHT for
the object currently sending a message, PRIMARY for titles, ACCENT for labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Mediator Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it reading "coordinate without coupling". Explain it defines one object
that encapsulates how a set of objects interact, so the objects stop referring to
each other directly. Show four user icons labeled Alice, Bob, Carol, Dave with a
small hub icon at the center in PRIMARY.

## The Problem (~25s)
A Java chat app where each User holds a list of every other User and calls
their receive() method directly. Show the User class with a sendToAll loop that
walks a List<User> of peers. As a new participant joins, draw fresh connection
lines between every pair of users; mark this growing web of direct references in
DANGER. The pain: N participants means roughly N times N links, and adding one
user means touching all the others.

## Why It Hurts (~20s)
Highlight the tangle: lines crossing between Alice, Bob, Carol, and Dave forming a
dense mesh in DANGER. Point out each User now knows the concrete details of every
peer, so muting one person, logging messages, or adding a moderator means editing
every User. Label the mesh "tight coupling" in ACCENT.

## The Mediator Solution (~30s)
Introduce a ChatMediator interface with sendMessage(text, sender) and
addUser(user). Show ChatRoom implementing it, holding the single List<User>.
Refactor User so it keeps only one reference, the ChatMediator, and calls
mediator.sendMessage(text, this) instead of looping over peers. Redraw the
picture: every User connects only to the central ChatRoom hub in OK, and the hub
fans the message out. Color the sending User in HIGHLIGHT as its message flows
through the hub to the others.

## Structure Diagram (~25s)
Show the class structure. ChatMediator interface in PRIMARY at the center; ChatRoom
as the concrete mediator pointing to it in OK; an abstract User (the colleague)
holding a ChatMediator reference; ConcreteUser extending User. Draw arrows: User
talks to ChatMediator, ChatRoom holds many User objects. Label the roles Mediator,
ConcreteMediator, and Colleague in ACCENT.

## Before and After Code (~30s)
Split into two stacked snippets. The first shows the old User with List<User>
peers and a sendToAll loop, the direct calls marked DANGER. The second shows the
new User sending through mediator.sendMessage(text, this) and ChatRoom.sendMessage
iterating its users and skipping the sender, all marked OK. Emphasize that the
coordination logic now lives in one place and individual users stay simple.

## Conclusion (~15s)
Recap: route all interaction through one mediator so participants depend on the
mediator, not on each other. Benefits: looser coupling, communication rules in a
single class, and easy addition of new participants or behaviors. End with the
chain Colleague -> Mediator -> ConcreteMediator in PRIMARY.
