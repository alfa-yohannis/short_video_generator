#!/usr/bin/env python3
"""Back-compat shim — the TOGAF video queue.

The real logic now lives in :mod:`auto_generate` (one driver for every subject).
This forwards to it with ``--subject togaf`` so every row uses the TOGAF pack
(and its ``togaf_todo.csv`` queue), bypassing the mixed-CSV category routing.
This is the TOGAF-only counterpart to ``auto_generate_ea.py`` (the combined
ArchiMate + TOGAF enterprise-architecture queue). See auto_generate.py and
subjects/togaf/.
"""
import sys

from auto_generate import main

if __name__ == "__main__":
    main(["--subject", "togaf", *sys.argv[1:]])
