"""Bounded parallelism for the per-scene pipeline stages.

Every per-scene unit of work (narration, TTS, scene-gen, render) is a blocking
``subprocess`` call that writes its own files and shares no mutable state. Those
calls release the GIL while they wait, so a plain ``ThreadPoolExecutor`` gives
real parallelism without the cost/complexity of multiprocessing.

:func:`run_parallel` is the one helper the stages use. It deliberately mirrors the
behaviour of the serial ``[fn(x) for x in items]`` it replaces:

* results come back in **input order**;
* the **first** exception raised by any worker is re-raised after the pool drains
  (so one failure surfaces, exactly like a serial loop would stop on it);
* ``workers <= 1`` runs a plain serial loop — no executor, no threads — which is
  the safe escape hatch (``--jobs 1``) and keeps tests deterministic.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Optional, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def resolve_workers(cap: int, jobs: Optional[int]) -> int:
    """The effective worker count: the stage ``cap`` lowered by a ``--jobs`` ceiling.

    ``jobs is None`` → use the stage cap as-is. Otherwise take ``min(cap, jobs)``.
    Never below 1.
    """
    n = cap if jobs is None else min(cap, jobs)
    return max(1, int(n))


def run_parallel(items: Sequence[T], fn: Callable[[T], R],
                 workers: int) -> List[R]:
    """Apply ``fn`` to every item, up to ``workers`` at a time, preserving order.

    With ``workers <= 1`` (or 0/1 items) this is just a serial loop. Otherwise the
    work runs on a thread pool; the first exception is propagated once all
    submitted work has settled.
    """
    items = list(items)
    if workers <= 1 or len(items) <= 1:
        return [fn(x) for x in items]

    results: List[Optional[R]] = [None] * len(items)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fn, item): i for i, item in enumerate(items)}
        first_exc: Optional[BaseException] = None
        for fut in futures:                       # iterate in submission order
            i = futures[fut]
            try:
                results[i] = fut.result()
            except BaseException as exc:           # noqa: BLE001 - re-raised below
                if first_exc is None:
                    first_exc = exc
    if first_exc is not None:
        raise first_exc
    return results  # type: ignore[return-value]
