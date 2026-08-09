#!/usr/bin/env python3
"""Stable V3 launcher for compact Pauli-state local/IBM buffers."""

from __future__ import annotations

import sys

from qac_ibm_wavetable_bridge import main


def has_option(name: str) -> bool:
    return any(arg == name or arg.startswith(name + "=") for arg in sys.argv[1:])


if __name__ == "__main__":
    if not has_option("--transform"):
        sys.argv.extend(["--transform", "none"])
    if not has_option("--mapping"):
        sys.argv.extend(["--mapping", "pauli15"])
    if "--compact-state" not in sys.argv:
        sys.argv.append("--compact-state")
    main()
