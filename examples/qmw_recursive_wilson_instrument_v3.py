#!/usr/bin/env python3
"""Playable recursive Wilson Hexany circuit instrument for Max."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import signal
import sys
import threading
from urllib.parse import unquote

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from qmw.recursive_wilson import HEXANY_MASKS, RecursiveWilsonEngine, hexany_voices
from qmw.synthesis import SynthesisOSCPublisher
from qmw_circuit_bridge import QMWCircuitBridge


class RecursiveWilsonMaxHost:
    def __init__(
        self,
        *,
        control_host: str = "127.0.0.1",
        control_port: int = 7403,
        max_host: str = "127.0.0.1",
        max_port: int = 7410,
        seed: int = 23,
        temperature: float = 0.65,
        max_depth: int = 32,
        interval_ms: int = 240,
        full_circuit_generation_limit: int = 24,
    ) -> None:
        self.control_host = control_host
        self.control_port = int(control_port)
        self.interval_ms = max(30, int(interval_ms))
        # Full accumulated QASM eventually exceeds one UDP datagram.  The
        # musical state stream remains small, so snapshot the growing circuit
        # only while it is safely inspectable and continue notes/status after.
        self.full_circuit_generation_limit = max(
            0, int(full_circuit_generation_limit)
        )
        self.engine = RecursiveWilsonEngine(
            seed=seed,
            temperature=temperature,
            max_depth=max_depth,
        )
        self.bridge = QMWCircuitBridge(
            n_qubits=4,
            n_steps=256,
            active_length=16,
            osc_host=max_host,
            osc_out_port=int(max_port),
            osc_control_port=self.control_port,
        )
        self.publisher = SynthesisOSCPublisher(control_host, self.control_port)
        self._lock = threading.RLock()
        self._stop_recursion = threading.Event()
        self._recursion_thread: threading.Thread | None = None
        self._qasm_transfer: dict[str, object] | None = None

        handlers = {
            "/qmw/recursive/next": self._osc_next,
            "/qmw/recursive/start": self._osc_start,
            "/qmw/recursive/stop": self._osc_stop,
            "/qmw/recursive/reset": self._osc_reset,
            "/qmw/recursive/temperature": self._osc_temperature,
            "/qmw/recursive/seed": self._osc_seed,
            "/qmw/recursive/max_depth": self._osc_max_depth,
            "/qmw/recursive/interval_ms": self._osc_interval,
            "/qmw/recursive/intervene": self._osc_intervene,
            "/qmw/qac/gate": self._osc_qac_gate,
            "/qmw/qac/begin": self._osc_qasm_begin,
            "/qmw/qac/chunk": self._osc_qasm_chunk,
            "/qmw/qac/end": self._osc_qasm_end,
        }
        for address, callback in handlers.items():
            self.bridge.add_control_handler(address, callback)

    def _send(self, address: str, values: object) -> None:
        self.bridge.client.send_message(address, values)

    def _error(self, message: object) -> None:
        print(f"recursive Wilson error: {message}")
        self._send("/qmw/recursive/error", str(message))

    def _publish_state(self, *, publish_circuit: bool) -> None:
        shell_probability, voices = hexany_voices(self.engine.state)
        generation = self.engine.generation
        if publish_circuit:
            result = self.engine.synthesis_result()
            revision = self.publisher.publish(result)
        else:
            revision = -1
        probabilities = [voice.conditional_probability for voice in voices]
        entropy = -sum(p * math.log2(p) for p in probabilities if p > 1e-15)
        duration_ms = int(round(80 + 45 * entropy))
        for voice_index, voice in enumerate(voices):
            if voice.conditional_probability < 1e-6:
                continue
            fractional_pitch = 60.0 + 12.0 * math.log2(voice.ratio)
            note_pitch = int(round(fractional_pitch))
            deviation = fractional_pitch - note_pitch
            bend_14bit = int(round(8192 + (deviation / 2.0) * 8191))
            phase_cc74 = int(
                round((voice.relative_phase + math.pi) * 127 / (2 * math.pi))
            )
            self._send(
                "/qmw/recursive/wilson_note",
                [
                    generation,
                    voice.basis_index,
                    voice.complement_basis_index,
                    note_pitch,
                    max(1, min(127, int(round(127 * math.sqrt(voice.conditional_probability))))),
                    duration_ms,
                    voice.absolute_probability,
                    voice.conditional_probability,
                    voice.relative_phase,
                    voice.ratio_numerator,
                    voice.ratio_denominator,
                    max(0, min(16383, bend_14bit)),
                    max(0, min(127, phase_cc74)),
                    2 + voice_index,
                ],
            )
        self._send(
            "/qmw/recursive/status",
            [
                generation,
                shell_probability,
                entropy,
                self.engine.temperature,
                self.engine.max_depth,
                self.engine.seed,
                revision,
                len(self.engine.logical_circuit.data),
            ],
        )

    def advance(self) -> None:
        with self._lock:
            step = self.engine.next()
            self._publish_state(
                publish_circuit=(
                    step.generation <= self.full_circuit_generation_limit
                )
            )
        print(
            f"recursive generation={step.generation} exchange={step.qubits} "
            f"theta={step.theta:.4f} beta={step.beta:.4f} "
            f"shell={step.shell_probability:.6f}"
        )

    def _run_recursion(self) -> None:
        while not self._stop_recursion.wait(self.interval_ms / 1000.0):
            try:
                self.advance()
            except Exception as exc:
                self._error(exc)
                self._stop_recursion.set()

    def start_recursion(self) -> None:
        if self._recursion_thread and self._recursion_thread.is_alive():
            return
        self._stop_recursion.clear()
        self._recursion_thread = threading.Thread(target=self._run_recursion, daemon=True)
        self._recursion_thread.start()
        self._send("/qmw/recursive/running", 1)

    def stop_recursion(self) -> None:
        self._stop_recursion.set()
        self._send("/qmw/recursive/running", 0)

    def _osc_next(self, _address: str, *_args: object) -> None:
        try:
            self.advance()
        except Exception as exc:
            self._error(exc)

    def _osc_start(self, _address: str, *_args: object) -> None:
        self.start_recursion()

    def _osc_stop(self, _address: str, *_args: object) -> None:
        self.stop_recursion()

    def _osc_reset(self, _address: str, *_args: object) -> None:
        try:
            self.stop_recursion()
            with self._lock:
                self.engine.reset()
                self._publish_state(publish_circuit=True)
        except Exception as exc:
            self._error(exc)

    def _osc_temperature(self, _address: str, value: float) -> None:
        try:
            self.engine.configure(temperature=float(value))
            self._publish_state(publish_circuit=False)
        except Exception as exc:
            self._error(exc)

    def _osc_seed(self, _address: str, value: int) -> None:
        try:
            self.engine.configure(seed=int(value))
            self.engine.reset()
            self._publish_state(publish_circuit=True)
        except Exception as exc:
            self._error(exc)

    def _osc_max_depth(self, _address: str, value: int) -> None:
        try:
            self.engine.configure(max_depth=int(value))
            self._publish_state(publish_circuit=False)
        except Exception as exc:
            self._error(exc)

    def _osc_interval(self, _address: str, value: int) -> None:
        self.interval_ms = max(30, int(value))
        self._send("/qmw/recursive/interval_ms", self.interval_ms)

    def _apply_intervention(self, gate: str, qubits: tuple[int, ...]) -> None:
        with self._lock:
            self.engine.apply_gate(gate, qubits)
            self._publish_state(publish_circuit=True)

    def _osc_intervene(self, _address: str, gate: str, *qubits: int) -> None:
        try:
            self._apply_intervention(str(gate), tuple(int(q) for q in qubits))
        except Exception as exc:
            self._error(exc)

    def _osc_qac_gate(self, _address: str, _event: int, gate: str, *qubits: int) -> None:
        self._osc_intervene(_address, gate, *qubits)

    def _osc_qasm_begin(self, _address: str, revision: int, total: int) -> None:
        self._qasm_transfer = {
            "revision": int(revision),
            "total": int(total),
            "chunks": {},
        }

    def _osc_qasm_chunk(
        self,
        _address: str,
        revision: int,
        index: int,
        total: int,
        encoded_text: str,
    ) -> None:
        transfer = self._qasm_transfer
        if (
            transfer is None
            or int(revision) != transfer["revision"]
            or int(total) != transfer["total"]
        ):
            self._error("QASM chunk does not match an active transfer")
            return
        transfer["chunks"][int(index)] = str(encoded_text)

    def _osc_qasm_end(self, _address: str, revision: int) -> None:
        try:
            transfer = self._qasm_transfer
            if transfer is None or int(revision) != transfer["revision"]:
                raise ValueError("QASM end does not match an active transfer")
            total = int(transfer["total"])
            chunks = transfer["chunks"]
            if set(chunks) != set(range(total)):
                raise ValueError(f"incomplete QASM transfer: {len(chunks)}/{total}")
            qasm_text = unquote("".join(chunks[index] for index in range(total)))
            self.stop_recursion()
            with self._lock:
                self.engine.load_qasm2(qasm_text)
                self._publish_state(publish_circuit=True)
            self._qasm_transfer = None
            self._send("/qmw/recursive/seed_accepted", [revision, len(qasm_text)])
        except Exception as exc:
            self._error(exc)

    def start(self) -> None:
        self.bridge.start_control_server(self.control_host)
        self._publish_state(publish_circuit=True)

    def stop(self) -> None:
        self.stop_recursion()
        self.bridge.stop_control_server()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-port", type=int, default=7403)
    parser.add_argument("--max-port", type=int, default=7410)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--temperature", type=float, default=0.65)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--interval-ms", type=int, default=240)
    args = parser.parse_args()
    host = RecursiveWilsonMaxHost(
        control_port=args.control_port,
        max_port=args.max_port,
        seed=args.seed,
        temperature=args.temperature,
        max_depth=args.max_depth,
        interval_ms=args.interval_ms,
    )
    stop_event = threading.Event()

    def request_stop(_signum=None, _frame=None):
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    host.start()
    print("QMW recursive Wilson instrument v3 ready")
    stop_event.wait()
    host.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
