#!/usr/bin/env python3
"""Phase 3 Wilson Hexany host for the Max instrument and Processing geometry."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import signal
import sys
import threading

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from examples.qmw_recursive_wilson_instrument_v3 import RecursiveWilsonMaxHost
from pythonosc.udp_client import SimpleUDPClient
from wilson_quantum_geometry_v1 import (
    WilsonAdapterConfig,
    WilsonOSCPublisher,
    WilsonStateAdapter,
)


class WilsonHexanyPhase3Host(RecursiveWilsonMaxHost):
    """Send one authoritative CPS frame to sound and geometry renderers."""

    def __init__(
        self,
        *,
        visual_host: str = "127.0.0.1",
        visual_port: int = 7411,
        fundamental_hz: float = 220.0,
        **kwargs,
    ) -> None:
        super().__init__(full_circuit_generation_limit=0, **kwargs)
        # Circuit-listening mode begins at |0000>. The old recursive host
        # prepares a weight-two probe automatically, which made an empty
        # programmer sound and obscured the difference between presets.
        self.engine.clear_circuit()
        self.visual_client = SimpleUDPClient(visual_host, int(visual_port))
        self.wilson_adapter = WilsonStateAdapter(
            WilsonAdapterConfig(
                fundamental_hz=float(fundamental_hz),
                attack_ms=70.0,
                persistence_ms=1100.0,
            )
        )
        self.wilson_publisher = WilsonOSCPublisher(
            self.wilson_adapter,
            [self.bridge.client, self.visual_client],
        )
        self._latest_frame = None
        self.bridge.add_control_handler(
            "/qmw/wilson/cps/complement", self._osc_complement
        )
        self.bridge.add_control_handler(
            "/qmw/wilson/cps/probe", self._osc_probe
        )

    def _publish_state(self, *, publish_circuit: bool) -> None:
        dt = self.interval_ms / 1000.0
        frame = self.wilson_adapter.adapt_statevector(
            self.engine.state.data,
            time=self.engine.generation * dt,
            dt=dt,
        )
        self.wilson_publisher.publish(frame)
        self._latest_frame = frame
        probabilities = [
            vertex.conditional_probability
            for vertex in frame.vertices
            if vertex.conditional_probability > 1e-15
        ]
        entropy = -sum(value * math.log2(value) for value in probabilities)
        self._send(
            "/qmw/wilson/cps/status",
            [
                frame.revision,
                self.engine.generation,
                frame.shell_probability,
                frame.leakage_probability,
                frame.conditional_shell_purity,
                entropy,
                self.engine.temperature,
                self.interval_ms,
            ],
        )

    def advance(self) -> None:
        with self._lock:
            step = self.engine.next()
            self._publish_state(publish_circuit=False)
            revision = self._latest_frame.revision
            for flow in step.flows[:2]:
                self.wilson_publisher.publish_flow(
                    revision=revision,
                    generation=step.generation,
                    source_basis_index=flow.source_basis_index,
                    destination_basis_index=flow.destination_basis_index,
                    absolute_flow=flow.absolute_probability_flow,
                    conditional_flow=flow.conditional_probability_flow,
                    theta=step.theta,
                    beta=step.beta,
                    relative_phase=flow.relative_phase,
                )
        strongest = step.flows[0].conditional_probability_flow if step.flows else 0.0
        print(
            f"phase3 generation={step.generation} exchange={step.qubits} "
            f"flow={strongest:.6f} shell={step.shell_probability:.6f}"
        )

    def _reset_adapter(self) -> None:
        self.wilson_adapter.reset()
        self.wilson_publisher.reset_topology()
        self._latest_frame = None

    def _osc_reset(self, _address: str, *_args: object) -> None:
        try:
            self.stop_recursion()
            with self._lock:
                self.engine.clear_circuit()
                self._reset_adapter()
                self._publish_state(publish_circuit=False)
        except Exception as exc:
            self._error(exc)

    def _osc_seed(self, _address: str, value: int) -> None:
        try:
            self.stop_recursion()
            with self._lock:
                self.engine.configure(seed=int(value))
                self.engine.clear_circuit()
                self._reset_adapter()
                self._publish_state(publish_circuit=False)
        except Exception as exc:
            self._error(exc)

    def _osc_complement(self, _address: str, *_args: object) -> None:
        """Apply X to every qubit: Wilson complement/particle-hole involution."""
        try:
            with self._lock:
                for qubit in range(4):
                    self.engine.apply_gate("x", (qubit,))
                self._publish_state(publish_circuit=False)
        except Exception as exc:
            self._error(exc)

    def _osc_probe(self, _address: str, *_args: object) -> None:
        """Explicitly enter autonomous Hexany mode from circuit-listening mode."""
        try:
            self.stop_recursion()
            with self._lock:
                self.engine.seed_circuit = None
                self.engine.reset(prepare_probe=True)
                self._reset_adapter()
                self._publish_state(publish_circuit=False)
        except Exception as exc:
            self._error(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-port", type=int, default=7433)
    parser.add_argument("--max-port", type=int, default=7420)
    parser.add_argument("--visual-port", type=int, default=7411)
    parser.add_argument("--fundamental", type=float, default=220.0)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--temperature", type=float, default=0.65)
    parser.add_argument("--max-depth", type=int, default=256)
    parser.add_argument("--interval-ms", type=int, default=240)
    parser.add_argument(
        "--autostart",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    args = parser.parse_args()
    host = WilsonHexanyPhase3Host(
        control_port=args.control_port,
        max_port=args.max_port,
        visual_port=args.visual_port,
        fundamental_hz=args.fundamental,
        seed=args.seed,
        temperature=args.temperature,
        max_depth=args.max_depth,
        interval_ms=args.interval_ms,
    )
    stop_event = threading.Event()

    def request_stop(_signum=None, _frame=None) -> None:
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    host.start()
    if args.autostart:
        host.start_recursion()
    print("QMW Wilson Hexany Phase 3 ready")
    print(f"sound renderer: udp://127.0.0.1:{args.max_port}/qmw/wilson/cps")
    print(f"geometry view: udp://127.0.0.1:{args.visual_port}/qmw/wilson/cps")
    try:
        stop_event.wait()
    finally:
        host.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
