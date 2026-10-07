"""Run and report NumPy-exact versus QuTiP XY parity."""
from __future__ import annotations
import argparse
import json
from .parity import run_xy_qutip_parity

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--samples", type=int, default=2048)
parser.add_argument("--duration", type=float, default=24.0)
parser.add_argument("--tolerance", type=float, default=1.0e-8)
args = parser.parse_args()
report = run_xy_qutip_parity(samples=args.samples, duration=args.duration, tolerance=args.tolerance)
print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
raise SystemExit(0 if report.accepted else 1)
