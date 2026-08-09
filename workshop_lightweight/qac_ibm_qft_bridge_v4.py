#!/usr/bin/env python3
"""V4 QFT launcher for the QAC/IBM wavetable bridge.

V3 remains the stable no-transform workflow. V4 selects QFT by default while
retaining explicit ``--transform iqft`` and ``--transform none`` overrides.
"""

from __future__ import annotations

import sys

from qac_ibm_wavetable_bridge import main


def has_option(name: str) -> bool:
    return any(arg == name or arg.startswith(name + "=") for arg in sys.argv[1:])


if __name__ == "__main__":
    if not has_option("--transform"):
        sys.argv.extend(["--transform", "qft"])
    if not has_option("--mapping"):
        sys.argv.extend(["--mapping", "pauli15"])
    if "--compact-state" not in sys.argv:
        sys.argv.append("--compact-state")
    main()
