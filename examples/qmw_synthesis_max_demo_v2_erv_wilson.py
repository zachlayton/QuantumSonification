#!/usr/bin/env python3
"""Wilson CPS lattice + MPE host for QMW's Qiskit synthesis commands."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import signal
import sys
import threading
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from qmw.synthesis import (
    SynthesisOSCPublisher,
    analyze_synthesis_state,
    project_frame_to_wilson_cps,
    synthesize_clifford,
    synthesize_evolution,
    synthesize_permutation,
    synthesize_qft,
)
from qmw_circuit_bridge import QMWCircuitBridge


# Channel 10 is the General MIDI percussion channel. Strict MPE receivers can
# use it, but excluding it keeps the patch safe with QuickTime/DLS and other
# GM-compatible destinations while preserving per-note channel expression.
MPE_MEMBER_CHANNELS = (2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16)


class SynthesisMaxDemoHost:
    def __init__(
        self,
        *,
        control_host: str = "127.0.0.1",
        control_port: int = 7403,
        max_host: str = "127.0.0.1",
        max_port: int = 7410,
        probe_basis: int = 5,
    ) -> None:
        self.control_host = control_host
        self.control_port = int(control_port)
        self.probe_basis = int(probe_basis)
        self.bridge = QMWCircuitBridge(
            n_qubits=4,
            n_steps=256,
            active_length=16,
            osc_host=max_host,
            osc_out_port=int(max_port),
            osc_control_port=self.control_port,
        )
        self.publisher = SynthesisOSCPublisher(control_host, self.control_port)
        self._performance_lock = threading.Lock()
        self._performance_generation = 0
        self.bridge.add_control_handler("/qmw/synthesis/demo", self._osc_demo)

    def _start_performance(self, result, revision: int) -> None:
        with self._performance_lock:
            self._performance_generation += 1
            generation = self._performance_generation
        threading.Thread(
            target=self._perform,
            args=(result, revision, generation),
            daemon=True,
        ).start()

    def _perform(self, result, revision: int, generation: int) -> None:
        operations = result.composer_circuit.operations
        frames = analyze_synthesis_state(
            result,
            initial_basis_index=self.probe_basis,
        )
        self.bridge.client.send_message(
            "/qmw/synthesis/demo/performance",
            ["begin", revision, len(operations), self.probe_basis],
        )
        dimension = 1 << result.qiskit_circuit.num_qubits
        for operation, frame in zip(operations, frames):
            with self._performance_lock:
                if generation != self._performance_generation:
                    return
            hilbert_position = frame.expected_basis_index / max(1, dimension - 1)
            phase_displacement = 6.0 * frame.relative_phase / math.pi
            pitch = int(round(48 + 24 * hilbert_position + phase_displacement))
            pitch = max(0, min(127, pitch))
            velocity = int(
                round(
                    42
                    + 48 * frame.normalized_coherence
                    + 30 * frame.mean_qubit_entropy
                )
            )
            velocity = max(1, min(127, velocity))
            duration_ms = int(
                round(
                    70
                    + 90 * frame.population_entropy
                    + 120 * frame.mean_qubit_entropy
                )
            )
            self.bridge.client.send_message(
                "/qmw/synthesis/demo/gate",
                [
                    revision,
                    frame.index,
                    operation.name,
                    ",".join(str(q) for q in operation.qubits),
                    pitch,
                    velocity,
                    duration_ms,
                    frame.expected_basis_index,
                    frame.dominant_basis_index,
                    frame.normalized_coherence,
                    frame.population_entropy,
                    frame.mean_qubit_entropy,
                    frame.relative_phase,
                ],
            )
            wilson_nodes = project_frame_to_wilson_cps(frame)[:4]
            for component_rank, node in enumerate(wilson_nodes):
                # CPS ratios set exact JI pitch. Quantum phase remains a
                # separate circular dimension on MPE timbre (CC74).
                fractional_pitch = 60.0 + 12.0 * math.log2(node.ratio)
                note_pitch = int(round(fractional_pitch))
                tuning_deviation = fractional_pitch - note_pitch
                note_velocity = int(round(127 * math.sqrt(node.probability)))
                bend_14bit = int(
                    round(8192 + (tuning_deviation / 2.0) * 8191)
                )
                phase_cc74 = int(
                    round((node.relative_phase + math.pi) * 127 / (2 * math.pi))
                )
                mpe_channel = MPE_MEMBER_CHANNELS[
                    (frame.index * 4 + component_rank) % len(MPE_MEMBER_CHANNELS)
                ]
                self.bridge.client.send_message(
                    "/qmw/synthesis/demo/wilson_note",
                    [
                        revision,
                        frame.index,
                        node.basis_index,
                        node.cps_grade,
                        node.complement_basis_index,
                        max(0, min(127, note_pitch)),
                        max(1, min(127, note_velocity)),
                        duration_ms,
                        node.probability,
                        node.relative_phase,
                        node.ratio_numerator,
                        node.ratio_denominator,
                        max(0, min(16383, bend_14bit)),
                        max(0, min(127, phase_cc74)),
                        mpe_channel,
                    ],
                )
            time.sleep(max(0.06, 0.15 - 0.06 * frame.population_entropy))
        self.bridge.client.send_message(
            "/qmw/synthesis/demo/performance",
            ["end", revision, len(operations)],
        )

    @staticmethod
    def synthesize(name: str):
        selected = str(name).strip().lower()
        if selected == "qft":
            return synthesize_qft(4)
        if selected == "evolution":
            return synthesize_evolution(
                [("XXII", 0.70), ("IIZZ", 0.35), ("ZIII", 0.20)],
                1.5,
                method="suzuki_trotter",
                order=2,
                reps=2,
            )
        if selected == "clifford":
            from qiskit.quantum_info import random_clifford

            return synthesize_clifford(
                random_clifford(4, seed=23),
                method="greedy",
            )
        if selected == "permutation":
            return synthesize_permutation([2, 0, 3, 1], topology="line")
        raise ValueError(
            "demo must be qft, evolution, clifford, or permutation"
        )

    def _osc_demo(self, _address: str, *args: object) -> None:
        selected = str(args[0]) if args else "evolution"
        try:
            result = self.synthesize(selected)
            revision = self.publisher.publish(result)
            self.bridge.client.send_message(
                "/qmw/synthesis/demo/summary",
                [revision, result.kind, json.dumps(result.summary(), sort_keys=True)],
            )
            self._start_performance(result, revision)
            print(
                f"published {result.kind}: revision={revision} "
                f"operations={len(result.composer_circuit.operations)}"
            )
        except Exception as exc:
            message = str(exc)
            print(f"synthesis demo rejected: {message}")
            self.bridge.client.send_message(
                "/qmw/synthesis/demo/error",
                [selected, message],
            )

    def start(self) -> None:
        self.bridge.start_control_server(self.control_host)

    def stop(self) -> None:
        self.bridge.stop_control_server()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-port", type=int, default=7403)
    parser.add_argument("--max-port", type=int, default=7410)
    parser.add_argument(
        "--probe-basis",
        type=int,
        default=5,
        help="initial computational-basis state used to hear the unitary (default: 5)",
    )
    args = parser.parse_args()

    host = SynthesisMaxDemoHost(
        control_port=args.control_port,
        max_port=args.max_port,
        probe_basis=args.probe_basis,
    )
    stopped = threading.Event()

    def request_stop(_signum=None, _frame=None) -> None:
        stopped.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    host.start()
    print("QMW synthesis Max demo ready")
    print(f"Max commands: udp://127.0.0.1:{args.control_port}/qmw/synthesis/demo")
    print(f"Max status:   udp://127.0.0.1:{args.max_port}")
    try:
        stopped.wait()
    finally:
        host.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
