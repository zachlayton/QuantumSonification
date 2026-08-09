#!/usr/bin/env python3
"""Workshop launcher for the Full4Q tomography OSC service."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from full4q_tomography_v1.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
