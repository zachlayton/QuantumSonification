#!/usr/bin/env python3
"""
Run from the qmw_process_graph folder:

    PYTHONPATH="$(pwd)" python examples/process_graph_to_max.py --port 7400
"""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import math
import time

from qmw.quantum_engine import QuantumProcessEngine
from qmw.osc_sender import QMWOSCSender


def build_demo_engine(t: float = 0.0) -> QuantumProcessEngine:
    engine = QuantumProcessEngine(
        num_qubits=4,
        name="process_state_demo",
        
    
    )

    engine.prepare_zero()

    # Qubit 0: H creates |+>, then RY changes population,
    # and RZ adds evolving phase structure.
    engine.h(0)

    engine.ry(
        1.45 * math.sin(t * 1.9 + 0.4),
        0,
    )

    engine.rz(
        (math.pi / 3) + 0.85 * math.sin(t * 0.31),
        0,
    )

    # Qubit 1 begins in |0>, so RX now has a real effect
    # on probabilities rather than only adding global phase.
    engine.rx(
        1.10 * math.sin(t * 0.17 + 1.2),
        1,
    )

    engine.ry(
        0.95 * math.sin(t * 0.29 + 2.1),
        1,
    )

    # Entangling structure.
    engine.cx(0, 2)
    engine.cx(1, 3)

    engine.rz(
        (math.pi / 7) + 1.10 * math.sin(t * 0.23 + 2.4),
        2,
    )

    engine.cx(2, 3)
    
    # Local Bloch-sphere readout rotations.
    # These rotate each reduced-state vector after entanglement,
    # making X, Y, and Z visually legible in Max.

    engine.ry(1.35 * math.sin(t * 0.43 + 0.2), 0)
    engine.rx(1.10 * math.sin(t * 0.37 + 1.1), 0)

    engine.ry(1.20 * math.sin(t * 0.31 + 1.8), 1)
    engine.rx(0.95 * math.sin(t * 0.47 + 2.4), 1)

    engine.ry(1.10 * math.sin(t * 0.39 + 2.9), 2)
    engine.rx(1.05 * math.sin(t * 0.29 + 0.7), 2)

    engine.ry(1.25 * math.sin(t * 0.35 + 1.5), 3)
    engine.rx(0.90 * math.sin(t * 0.41 + 3.0), 3)

    # Sonic-only graph relation: does not alter the Qiskit circuit.
    engine.add_sonic_feedback_node(
        source="cx_008",
        target="rz_007",
        label="entanglement_driven_resonant_feedback",
    )

    return engine


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7400)
    parser.add_argument("--interval", type=float, default=0.50)
    parser.add_argument("--frames", type=int, default=0)
    args = parser.parse_args()

    engine = build_demo_engine(t=0.0)
    sender = QMWOSCSender(args.host, args.port)

    engine.graph.validate()

    print("\nPROCESS GRAPH:\n")
    print(engine.graph.to_json())
    print(f"\nSending OSC to {args.host}:{args.port}\n")

    # Send static process topology once.
    sender.send_graph(engine.graph)

    frame = 0

    try:
        while args.frames == 0 or frame < args.frames:
            current_time = frame * args.interval

            # Same topology; changing Bloch-sphere trajectory.
            engine = build_demo_engine(t=current_time)
            snapshot = engine.snapshot()
            
            for qubit, (x, y, z) in enumerate(snapshot.bloch_vectors):
                radius = (x * x + y * y + z * z) ** 0.5
                print(
                    f"  q{qubit}: "
                    f"x={x:+.3f}  y={y:+.3f}  z={z:+.3f}  r={radius:.3f}"
    )
            
            sender.send_snapshot(frame, snapshot)

            material = snapshot.material

            print(
                f"frame={frame:03d} | "
                f"H={snapshot.shannon_entropy:.3f} | "
                f"phase={snapshot.phase_dispersion:.3f} | "
                f"entangle={snapshot.entangling_power:.3f} | "
                f"modes={material['mode_family']} | "
                f"density={material['density']:.3f} | "
                f"brightness={material['brightness']:.3f}"
            )

            frame += 1
            time.sleep(max(0.01, args.interval))

    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()