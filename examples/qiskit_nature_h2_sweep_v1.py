"""Runnable entry point for the Qiskit Nature H2 sweep."""

from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from qiskit_nature_molecular_v1.cli import main


if __name__ == "__main__":
    main()

