#!/usr/bin/env python3
"""Portable entry point; equivalent to ``python -m ...engine``."""

from quantum_resonant_membrane.engine import main


if __name__ == "__main__":
    raise SystemExit(main())
