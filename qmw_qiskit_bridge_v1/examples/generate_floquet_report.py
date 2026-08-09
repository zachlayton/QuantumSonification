from __future__ import annotations

from pathlib import Path

from qmw_qiskit_bridge_v1.experiments import generate_floquet_comparison_report


output = Path(__file__).resolve().parents[1] / "reports"
for path in generate_floquet_comparison_report(output):
    print(path)
