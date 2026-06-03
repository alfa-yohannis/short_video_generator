"""Small pure text helpers used when turning AI replies into source files.

These are free functions on purpose: they take text in and return text out,
with no state and no I/O, so they are trivial to read and to unit-test. Naming
is descriptive (``strip_code_fences`` rather than a method buried in a class)
because that is genuinely the clearest design for stateless string work.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path


def camel_from_snake(name: str) -> str:
    """``strategy_pattern`` -> ``StrategyPattern`` (also splits on ``-`` and space)."""
    return "".join(part.capitalize() for part in re.split(r"[_\-\s]+", name) if part)


def strip_leading_digits(name: str) -> str:
    """``01_pengantar`` -> ``pengantar`` (drop a leading number + separators)."""
    return re.sub(r"^[0-9]+[_\-\s]*", "", name)


# A ``` fenced block, optionally tagged ```python / ```py. Group 1 is the code.
_FENCE_BLOCK_RE = re.compile(r"```(?:python|py)?[ \t]*\n(.*?)```", re.S | re.I)


def strip_code_fences(text: str) -> str:
    """Pull a clean Python source out of an AI reply.

    Language models stray from "output only the file" in two ways:

    1. They wrap the file in a ``` fence (sometimes with prose around it) — so
       we take the first fenced block.
    2. They prepend a sentence before the code (e.g. "Here is scene 6, ~30s:").
       That leading line makes :func:`ast.parse` choke (a bare "30s" is an
       invalid number), so we drop everything before the first ``import`` line —
       the scene prompt mandates ``from manim import *`` as the first line.
    """
    text = text.strip()
    match = _FENCE_BLOCK_RE.search(text)
    if match:
        text = match.group(1).strip()
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines)
                  if line.lstrip().startswith("from manim import")), None)
    if start is None:
        start = next((i for i, line in enumerate(lines)
                      if line.lstrip().startswith(("from ", "import ", "#!"))), None)
    if start:  # only trim when real preamble precedes the code (start > 0)
        text = "\n".join(lines[start:]).strip()
    return text


# A short Python string literal (single/double quote, no triple, no escapes).
# Group "body" is the inner text — good enough for the L(...) / MarkupText(...)
# call arguments the AI tends to put a bare ``&`` in.
_STRING_LITERAL_RE = re.compile(r"(?P<q>['\"])(?P<body>[^'\"\\\n]*?)(?P=q)")
_KNOWN_ENTITIES = ("&amp;", "&lt;", "&gt;", "&quot;", "&apos;", "&#")


def escape_unsafe_ampersands(src: str) -> str:
    """Rewrite a bare ``&`` to ``&amp;`` inside every short string literal.

    The Manim helpers (``title_bar``, ``body_text``, ``bullet_list`` ...) feed
    their text into Pango ``MarkupText``, which parses XML-ish markup and
    rejects a raw ``&``. We only touch text *inside string literals*, and we
    leave already-escaped entities (``&amp;``, ``&lt;`` ...) alone — so the pass
    is safe to run more than once.
    """

    def fix(match: re.Match) -> str:
        body = match.group("body")
        if "&" not in body:
            return match.group(0)
        out = []
        i = 0
        while i < len(body):
            starts_entity = any(body[i:].startswith(ent) for ent in _KNOWN_ENTITIES)
            if body[i] == "&" and not starts_entity:
                out.append("&amp;")
            else:
                out.append(body[i])
            i += 1
        return f"{match.group('q')}{''.join(out)}{match.group('q')}"

    return _STRING_LITERAL_RE.sub(fix, src)


def validate_python_source(path: Path, src: str) -> None:
    """Raise ``SystemExit`` with a clear message if ``src`` isn't valid Python.

    Catching a syntax error here (at generation time) is far friendlier than
    letting it blow up later, mid-render.
    """
    try:
        ast.parse(src, filename=str(path))
    except SyntaxError as exc:
        raise SystemExit(
            f"AI-generated scene at {path} is not valid Python: "
            f"line {exc.lineno} col {exc.offset}: {exc.msg}\n"
            "Re-run with --force after editing the file, or delete it and "
            "re-run --stage scenes to regenerate."
        ) from exc
