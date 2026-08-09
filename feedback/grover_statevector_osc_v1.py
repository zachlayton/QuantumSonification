#!/usr/bin/env python3
"""Stream an exact MLX Grover statevector to Max, one operator at a time.

The stream is deliberately not generated from Grover's closed-form success
curve.  Every frame is measured from the currently evolving complex64 vector
after either the phase oracle or the diffusion reflection.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from pathlib import Path
import sys
import time
from typing import Any, Protocol

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class OSCClient(Protocol):
    def send_message(self, address: str, value: Any) -> None: ...


@dataclass(frozen=True)
class GroverStatevectorFrame:
    iteration: int
    operator: str
    success_probability: float
    grover_plane_angle: float
    relative_phase: float
    norm: float
    marked_amplitude: complex
    unmarked_amplitude: complex
    walsh_coefficients: np.ndarray
    represented_energy: float
    residual_energy: float


class ExactGroverStatevectorEngine:
    """Incremental matrix-free Grover evolution with literal state readout."""

    def __init__(
        self,
        n_qubits: int = 16,
        target: int | str = 57_893,
        modes: int = 64,
        backend: str = "numpy",
    ):
        if n_qubits < 1:
            raise ValueError("n_qubits must be positive")
        dimension = 1 << n_qubits
        if modes < 1 or modes > dimension or modes & (modes - 1):
            raise ValueError("modes must be a power of two no larger than the statevector")
        if dimension % modes:
            raise ValueError("modes must divide the statevector dimension")

        self.n_qubits = n_qubits
        self.dimension = dimension
        self.target = self._basis_index(target, n_qubits)
        self.modes = modes
        self.iteration = 0
        if backend not in {"numpy", "mlx"}:
            raise ValueError("backend must be 'numpy' or 'mlx'")
        self.backend = backend
        self._mx: Any | None = None

        phases = np.ones(dimension, dtype=np.float32)
        phases[self.target] = -1.0
        if backend == "mlx":
            import mlx.core as mx

            self._mx = mx
            self.oracle_phases = mx.array(phases, dtype=mx.complex64)
            self.state = mx.ones((dimension,), dtype=mx.complex64) / math.sqrt(dimension)
            mx.eval(self.oracle_phases, self.state)
        else:
            self.oracle_phases = phases.astype(np.complex64)
            self.state = np.full(
                dimension, 1.0 / math.sqrt(dimension), dtype=np.complex64
            )
        self._walsh = self._make_walsh_projection(modes)

    @staticmethod
    def _basis_index(state: int | str, n_qubits: int) -> int:
        if isinstance(state, bool):
            raise TypeError("target must be an integer or binary string")
        if isinstance(state, int):
            index = state
        elif isinstance(state, str) and len(state) == n_qubits and set(state) <= {"0", "1"}:
            index = int(state, 2)
        else:
            raise ValueError(f"target must identify exactly {n_qubits} bits")
        if not 0 <= index < (1 << n_qubits):
            raise ValueError("target lies outside the statevector")
        return index

    @staticmethod
    def _make_walsh_projection(size: int) -> np.ndarray:
        indices = np.arange(size, dtype=np.uint64)
        projection = np.empty((size, size), dtype=np.float32)
        for mask in range(size):
            values = np.bitwise_and(indices, np.uint64(mask))
            parity = np.zeros(size, dtype=np.uint8)
            while np.any(values):
                parity ^= np.asarray(values & np.uint64(1), dtype=np.uint8)
                values >>= np.uint64(1)
            projection[mask] = 1.0 - 2.0 * parity
        return projection

    def frame(self, operator: str) -> GroverStatevectorFrame:
        state = np.asarray(self.state, dtype=np.complex64)
        marked = complex(state[self.target])
        unmarked = complex((np.sum(state, dtype=np.complex128) - marked) / math.sqrt(self.dimension - 1))
        probability = float(abs(marked) ** 2)
        norm = float(np.sum(np.abs(state) ** 2, dtype=np.float64))
        angle = math.atan2(abs(marked), abs(unmarked))
        relative_phase = float(np.angle(marked) - np.angle(unmarked))
        relative_phase = (relative_phase + math.pi) % (2.0 * math.pi) - math.pi

        # These are exact projections onto the first `modes` Walsh-Hadamard
        # characters, not fabricated spectral weights.  At |s> only DC is
        # present; as the marked basis vector emerges its bit signature spreads
        # coherently through this orthogonal basis.
        collapsed = state.reshape(-1, self.modes).sum(axis=0, dtype=np.complex128)
        coefficients = (self._walsh @ collapsed) / math.sqrt(self.dimension)
        coefficients = np.asarray(coefficients, dtype=np.complex64)
        represented = float(np.sum(np.abs(coefficients) ** 2, dtype=np.float64))
        return GroverStatevectorFrame(
            iteration=self.iteration,
            operator=operator,
            success_probability=probability,
            grover_plane_angle=angle,
            relative_phase=relative_phase,
            norm=norm,
            marked_amplitude=marked,
            unmarked_amplitude=unmarked,
            walsh_coefficients=coefficients,
            represented_energy=represented,
            residual_energy=max(0.0, norm - represented),
        )

    def apply_oracle(self) -> GroverStatevectorFrame:
        self.iteration += 1
        self.state = self.oracle_phases * self.state
        if self.backend == "mlx":
            self._mx.eval(self.state)
        return self.frame("oracle")

    def apply_diffusion(self) -> GroverStatevectorFrame:
        oracle_state = self.state
        if self.backend == "mlx":
            self.state = 2.0 * self._mx.mean(oracle_state) - oracle_state
            self._mx.eval(self.state)
        else:
            self.state = np.asarray(
                2.0 * np.mean(oracle_state, dtype=np.complex128) - oracle_state,
                dtype=np.complex64,
            )
        return self.frame("diffusion")


class GroverOSCAdapter:
    PREFIX = "/qmw/grover/statevector"

    def __init__(self, client: OSCClient):
        self.client = client

    def publish_frame(self, frame: GroverStatevectorFrame) -> None:
        operator_code = {"prepared": 0, "oracle": 1, "diffusion": 2}[frame.operator]
        self.client.send_message(
            f"{self.PREFIX}/frame",
            [
                frame.iteration,
                operator_code,
                frame.success_probability,
                frame.grover_plane_angle,
                frame.relative_phase,
                frame.norm,
                frame.represented_energy,
                frame.residual_energy,
                frame.marked_amplitude.real,
                frame.marked_amplitude.imag,
                frame.unmarked_amplitude.real,
                frame.unmarked_amplitude.imag,
            ],
        )
        values: list[float | int] = [frame.iteration, operator_code]
        for coefficient in frame.walsh_coefficients:
            values.extend((float(coefficient.real), float(coefficient.imag)))
        self.client.send_message(f"{self.PREFIX}/modes", values)

    def state(self, name: str) -> None:
        self.client.send_message(f"{self.PREFIX}/state", name)

    def found(self, frame: GroverStatevectorFrame) -> None:
        self.client.send_message(
            f"{self.PREFIX}/found",
            [frame.iteration, frame.success_probability, frame.grover_plane_angle],
        )


def run_stream(
    adapter: GroverOSCAdapter,
    engine: ExactGroverStatevectorEngine,
    operator_interval_seconds: float,
    threshold: float,
    stabilization_seconds: float = 0.0,
) -> GroverStatevectorFrame:
    if operator_interval_seconds < 0.0:
        raise ValueError("operator_interval_seconds must be non-negative")
    if not 0.0 < threshold < 1.0:
        raise ValueError("threshold must be in (0, 1)")
    if stabilization_seconds < 0.0:
        raise ValueError("stabilization_seconds must be non-negative")

    adapter.state("SEARCHING")
    prepared = engine.frame("prepared")
    adapter.publish_frame(prepared)
    best = prepared
    approaching_announced = False
    theta = math.asin(1.0 / math.sqrt(engine.dimension))
    limit = int(math.floor(math.pi / (4.0 * theta)))
    for _ in range(limit):
        if operator_interval_seconds:
            time.sleep(operator_interval_seconds)
        oracle = engine.apply_oracle()
        adapter.publish_frame(oracle)
        if operator_interval_seconds:
            time.sleep(operator_interval_seconds)
        diffusion = engine.apply_diffusion()
        adapter.publish_frame(diffusion)
        if diffusion.success_probability > best.success_probability:
            best = diffusion
        if diffusion.success_probability >= 0.90 and not approaching_announced:
            adapter.state("APPROACHING")
            approaching_announced = True
        if diffusion.success_probability >= threshold:
            best = diffusion
            break

    adapter.state("FOUND")
    adapter.found(best)
    adapter.state("STABILIZING")
    if stabilization_seconds:
        time.sleep(stabilization_seconds)
    adapter.state("HELD")
    return best


def main() -> None:
    from pythonosc.udp_client import SimpleUDPClient

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qubits", type=int, default=16)
    parser.add_argument("--target", type=int, default=57_893)
    parser.add_argument("--modes", type=int, default=64)
    parser.add_argument(
        "--backend",
        choices=("numpy", "mlx"),
        default="numpy",
        help="NumPy is exact and avoids per-frame Metal readback latency; MLX remains available for parity runs.",
    )
    parser.add_argument("--operator-ms", type=float, default=45.0)
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.999985,
        help="Stop/hold threshold. 16-qubit one-target Grover peaks just below 0.99999.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7493)
    parser.add_argument("--stabilize-ms", type=float, default=700.0)
    args = parser.parse_args()

    engine = ExactGroverStatevectorEngine(
        args.qubits, args.target, args.modes, backend=args.backend
    )
    adapter = GroverOSCAdapter(SimpleUDPClient(args.host, args.port))
    print(
        f"Exact {args.backend.upper()} Grover |{args.target:0{args.qubits}b}>: {engine.dimension:,} amplitudes, "
        f"oracle/diffusion every {args.operator_ms:g} ms -> OSC {args.host}:{args.port}",
        flush=True,
    )
    result = run_stream(
        adapter,
        engine,
        args.operator_ms / 1000.0,
        args.threshold,
        stabilization_seconds=max(0.0, args.stabilize_ms / 1000.0),
    )
    print(
        f"HELD at iteration {result.iteration}: p={result.success_probability:.9f}, "
        f"norm={result.norm:.9f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
