#!/usr/bin/env python3
"""Workshop launcher for the v4 Hamiltonian OSC service."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qmw_representation_laboratory_v4.osc_cli import main


if __name__ == "__main__":
    raise SystemExit(main())
