---
title: proxy_pattern
language: both
length: 2-3 minutes
---

# Proxy Pattern

A short tutorial on the Proxy pattern using an image-gallery example: a viewer that
shows high-resolution photos that are expensive to load from disk. A stand-in object
controls access to the real one and defers the costly work until it is actually
needed. Code in Java. Use DANGER for eager loading and tangled lazy checks, OK for
the Proxy design, HIGHLIGHT for the current object, PRIMARY for titles, ACCENT for
labels.

# Preparation
No preparation is needed: this is a code-only tutorial, so every scene is written
directly from the source examples and there are no external tools or reference
assets to set up.

## Introduction (~15s)
Show "Proxy Pattern" as a LARGE CENTERED title, with a short subtitle directly
beneath it. Explain it provides a surrogate, or stand-in, for another object to
control access to it. Three icons labeled Client, Proxy, and Real Object, with the
Proxy sitting between the other two as a gatekeeper in ACCENT.

## The Problem (~25s)
A Java ImageGallery builds a list of RealImage objects, and each RealImage reads its
full-size file from disk inside its constructor. Show the gallery opening and every
photo loading at once, with a stack of "loading 8 MB..." labels piling up in DANGER.
The pain: the gallery freezes on startup even though most photos are never viewed.

## A Naive Fix (~20s)
Show the client code trying to defer loading by hand: a RealImage field that starts
null, plus repeated `if (image == null) image = new RealImage(file)` guards scattered
before every display call. Mark these duplicated null checks in DANGER and note the
loading logic now leaks into every caller.

## The Proxy Solution (~30s)
Define an Image interface with display(). RealImage implements it and loads the file
in its constructor. ProxyImage also implements Image, stores only the filename, and
creates its RealImage the first time display() is called, then forwards the call.
Show the client holding an Image reference and never knowing which one it has, with
the deferred-load step highlighted in OK.

## Structure Diagram (~25s)
Draw the class diagram: an Image interface at the center with display(); RealImage
and ProxyImage both realizing it. ProxyImage holds a reference to a RealImage,
labeled "creates on demand" in ACCENT. A Client box depends only on Image. Highlight
the ProxyImage box in HIGHLIGHT to show it shares the interface with the real subject.

## Before and After (~30s)
Two code panels. The first panel shows the gallery eagerly constructing eight
RealImage objects, marked in DANGER. The second panel shows it constructing eight
ProxyImage objects instead, with construction now instant and the heavy load
happening only inside display(); mark this panel in OK. Emphasize that the gallery
code is otherwise identical because both share the Image interface.

## Conclusion (~15s)
Recap: a Proxy stands in for a real object behind the same interface and controls
when and how that object is used. Benefits: lazy creation, access control, and a
client that stays unaware. Note the common variants in ACCENT: virtual, protection,
and remote. End with Client -> Proxy -> RealSubject.
