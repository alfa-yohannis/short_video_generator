---
title: bridge_pattern
language: both
length: 2-3 minutes
---

# Bridge Pattern

A short tutorial on the Bridge pattern using a notification example: notifications
of different urgency that can be delivered through different channels. Code in
Java. Use DANGER for the combinatorial class explosion, OK for the Bridge design,
HIGHLIGHT for the current object, PRIMARY for titles, ACCENT for labels.

## Introduction (~15s)
Show "Bridge Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it reading that it splits an abstraction from its implementation so both
can vary independently. A simple visual hints at two separate ladders joined by a
single connecting span, tinted PRIMARY.

## The Problem (~25s)
Introduce a notification system with two independent dimensions: urgency
(Normal, Urgent) and delivery channel (Email, SMS). Show each dimension as its own
ACCENT-labeled axis. The point: these two ideas change for different reasons, yet
a single inheritance tree forces them to be tangled together.

## The Class Explosion (~25s)
A Java hierarchy tries to cover every pairing by subclassing:
NormalEmailNotification, UrgentEmailNotification, NormalSmsNotification,
UrgentSmsNotification. Mark every combined class in DANGER. Add a third channel,
Slack, and watch the count jump as new classes sprout for each urgency. The pain:
the class total is urgencies multiplied by channels.

## The Bridge Idea (~20s)
Reveal the key move: stop merging the two axes into one tree. Keep an abstraction
hierarchy for urgency and a separate implementation hierarchy for channels. Draw a
single connecting span, the bridge, joining them and highlight it in OK. Each side
now grows on its own.

## The Bridge Solution (~30s)
Define a MessageSender implementor interface with send(String text). Show
EmailSender, SmsSender, and SlackSender implementing it. Define a Notification
abstraction that holds a MessageSender and exposes notify(String). Show
UrgentNotification refining notify to repeat or flag the message, delegating the
actual delivery with messageSender.send(...). Color the held sender in HIGHLIGHT to
show it is swappable while the program runs.

## Structure Diagram (~25s)
Show the two hierarchies as parallel ladders. One ladder: Notification refined by
UrgentNotification. The other ladder: MessageSender implemented by EmailSender,
SmsSender, SlackSender. Draw a has-a bridge arrow from Notification to
MessageSender in OK, labeled with the ACCENT word delegates. Note that adding a
channel touches only one ladder and adding an urgency touches only the other.

## Before and After (~20s)
Split the view. The before half stacks the tangled combined subclasses in DANGER,
counting urgencies times channels. The after half shows a slim Notification wired
to a chosen MessageSender in OK, where each new feature adds one class to a single
ladder, turning multiplication into simple addition.

## Conclusion (~15s)
Recap: separate an abstraction from its implementation and connect them with
composition so each can vary on its own. Benefits: no combinatorial explosion,
mix-and-match flexibility, channels swapped while running. End with
Abstraction -> bridge -> Implementor.
