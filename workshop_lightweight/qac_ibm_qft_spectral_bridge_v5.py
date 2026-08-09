#!/usr/bin/env python3
"""V5 launcher: compact Pauli state plus full QFT spectral descriptors."""

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
    if "--publish-qft-spectrum" not in sys.argv:
        sys.argv.append("--publish-qft-spectrum")
    main()
