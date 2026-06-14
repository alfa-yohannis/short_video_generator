#!/usr/bin/env python3
"""Back-compat shim — the enterprise-architecture video queue (ArchiMate + TOGAF).

The real logic now lives in :mod:`auto_generate` (one driver for every subject).
This forwards to it with the EA queue CSV; each row is routed to the ``archimate``
or ``togaf`` subject pack by its category (replacing the old ``_is_togaf_topic``
keyword check). See auto_generate.py and subjects/{archimate,togaf}/.
"""
import sys

from auto_generate import main

if __name__ == "__main__":
    main(["--csv", "enterprise_architecture_todo.csv", *sys.argv[1:]])
