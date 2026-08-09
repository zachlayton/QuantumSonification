from __future__ import annotations

from pathlib import Path

from qmw_qiskit_bridge_v1.sonification import render_dual_stream_sonification


output = Path(__file__).resolve().parents[1] / "renders"
for route in ("qiskit_trotter_order_2", "aer_noisy"):
    render = render_dual_stream_sonification(
        output / route,
        transformed_route=route,
        periods=16,
    )
    print(render.mix_path)
