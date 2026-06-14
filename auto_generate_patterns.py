#!/usr/bin/env python3
"""Back-compat shim — the design-pattern video queue.

The real logic now lives in :mod:`auto_generate` (one driver for every subject).
This forwards to it with ``--subject design_patterns`` so existing cron entries
and muscle memory keep working. See auto_generate.py and subjects/design_patterns/.
"""
import sys

from auto_generate import main

if __name__ == "__main__":
    main(["--subject", "design_patterns", *sys.argv[1:]])
