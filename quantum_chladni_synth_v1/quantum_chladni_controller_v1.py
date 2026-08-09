#!/usr/bin/env python3
"""Stream quantum-conditioned Laplace--Beltrami modes to Max over OSC."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import math
import signal
import threading
import time
from typing import Any

import numpy as np

from quantum_eigenfield_engine_v1 import (
    QuantumEigenfieldConfig,
    QuantumEigenfieldEngine,
)
from qpe_synthesizer_v1.qpe_model import (
    Eigenstate,
    conditional_eigenstate_probabilities,
    run_qpe,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODAL_PACKET = (
    ROOT
    / "algebraic_surfaces"
    / "tanglecube_v1"
    / "living"
    / "state_000001"
    / "surface_material.npz"
)


@dataclass(frozen=True)
class ModalProfile:
    name: str
    eigenvalues: np.ndarray
    frequencies_hz: np.ndarray
    decay_seconds: np.ndarray
    mode_weights: np.ndarray
    vertices: np.ndarray
    eigenvectors: np.ndarray

    def __post_init__(self) -> None:
        arrays = (
            self.eigenvalues,
            self.frequencies_hz,
            self.decay_seconds,
            self.mode_weights,
        )
        if not arrays or len({len(np.asarray(value)) for value in arrays}) != 1:
            raise ValueError("modal profile arrays must have equal lengths")
        if len(self.eigenvalues) < 1:
            raise ValueError("modal profile must contain at least one mode")
        if np.any(np.asarray(self.frequencies_hz) <= 0.0):
            raise ValueError("modal frequencies must be positive")
        if np.any(np.asarray(self.decay_seconds) <= 0.0):
            raise ValueError("modal decays must be positive")
        if self.vertices.ndim != 2 or self.vertices.shape[1] != 3:
            raise ValueError("vertices must have shape (samples, 3)")
        if self.eigenvectors.shape != (len(self.vertices), len(self.eigenvalues)):
            raise ValueError("eigenvectors must have shape (samples, modes)")


@dataclass(frozen=True)
class QuantumChladniFrame:
    revision: int
    purity: float
    entropy_normalized: float
    coherence_normalized: float
    frequencies_hz: np.ndarray
    decay_seconds: np.ndarray
    mode_weights: np.ndarray
    probabilities: np.ndarray
    phases: np.ndarray
    pans: np.ndarray
    basis_populations: np.ndarray
    basis_phases: np.ndarray
    qpe_bits: int
    qpe_integer: int
    qpe_phase: float
    qpe_dominant_mode: int
    qpe_confidence: float

    @property
    def mode_count(self) -> int:
        return len(self.frequencies_hz)

    @property
    def qpe_bitstring(self) -> str:
        return format(self.qpe_integer, f"0{self.qpe_bits}b")


@dataclass(frozen=True)
class QPEConditioning:
    bits: int
    measured_integer: int
    measured_phase: float
    latent_mode: int
    posterior: np.ndarray

    @property
    def dominant_mode(self) -> int:
        return int(np.argmax(self.posterior))

    @property
    def confidence(self) -> float:
        return float(self.posterior[self.dominant_mode])


def modal_eigenphases(eigenvalues: np.ndarray, *, maximum_phase: float = 0.875) -> np.ndarray:
    """Map H eigenvalues to phases of U=exp(2*pi*i*maximum_phase*H/lambda_max)."""

    values = np.asarray(eigenvalues, dtype=np.float64)
    if values.ndim != 1 or len(values) < 1 or np.any(~np.isfinite(values)):
        raise ValueError("eigenvalues must be a finite nonempty vector")
    shifted = values - min(0.0, float(np.min(values)))
    scale = float(np.max(shifted))
    if scale <= 0.0:
        return np.zeros_like(shifted)
    return np.clip(float(maximum_phase), 0.01, 0.99) * shifted / scale


def qpe_condition_modal_distribution(
    probabilities: np.ndarray,
    eigenvalues: np.ndarray,
    bits: int,
    rng: object,
) -> QPEConditioning:
    """Measure a finite QPE register and condition the spatial mode state."""

    priors = np.asarray(probabilities, dtype=np.float64)
    if priors.ndim != 1 or len(priors) != len(eigenvalues) or np.any(priors < 0.0):
        raise ValueError("probabilities must match the eigenvalue vector")
    total = float(np.sum(priors))
    if total <= 0.0:
        raise ValueError("modal probabilities must have positive mass")
    priors = priors / total
    eigenphases = modal_eigenphases(eigenvalues)
    states = [
        Eigenstate(float(phase), math.sqrt(float(weight)), f"mode-{index + 1}")
        for index, (phase, weight) in enumerate(zip(eigenphases, priors))
    ]
    shot = run_qpe(states, int(bits), rng)
    posterior = conditional_eigenstate_probabilities(
        states, int(bits), shot.measured_integer
    )
    return QPEConditioning(
        int(bits),
        shot.measured_integer,
        shot.measured_phase,
        shot.eigenstate_index,
        posterior,
    )


def _plate_profile(mode_count: int = 24) -> ModalProfile:
    """Portable fallback: rectangular-membrane Laplacian spectrum."""
    pairs = sorted(
        ((m * m + n * n, m, n) for m in range(1, 9) for n in range(1, 9)),
        key=lambda item: (item[0], item[1], item[2]),
    )[: max(1, mode_count)]
    eigenvalues = np.asarray([item[0] for item in pairs], dtype=np.float64)
    frequencies = 62.0 * np.sqrt(eigenvalues)
    index = np.arange(len(pairs), dtype=np.float64)
    decays = 2.2 / (1.0 + 0.045 * index)
    weights = 1.0 / np.sqrt(1.0 + index)
    side = 28
    x, y = np.meshgrid(
        np.linspace(-1.0, 1.0, side),
        np.linspace(-1.0, 1.0, side),
        indexing="xy",
    )
    vertices = np.column_stack((x.reshape(-1), y.reshape(-1), np.zeros(side * side)))
    eigenvectors = np.column_stack(
        [
            np.sin(item[1] * math.pi * (vertices[:, 0] + 1.0) * 0.5)
            * np.sin(item[2] * math.pi * (vertices[:, 1] + 1.0) * 0.5)
            for item in pairs
        ]
    )
    return ModalProfile(
        "rectangular_membrane",
        eigenvalues,
        frequencies,
        decays,
        weights,
        vertices,
        eigenvectors,
    )


def load_modal_profile(
    path: str | Path | None = None,
    mode_count: int = 24,
    visual_samples: int = 768,
) -> ModalProfile:
    selected = Path(path) if path is not None else DEFAULT_MODAL_PACKET
    if not selected.exists():
        return _plate_profile(mode_count)
    with np.load(selected, allow_pickle=False) as packet:
        required = ("eigenvalues", "frequencies_hz", "decay_times_seconds", "mode_weights")
        missing = [name for name in required if name not in packet]
        if missing:
            raise ValueError(f"modal packet missing {missing}")
        count = min(mode_count, *(len(packet[name]) for name in required))
        eigenvalues = np.asarray(packet["eigenvalues"][:count], dtype=np.float64)
        frequencies = np.asarray(packet["frequencies_hz"][:count], dtype=np.float64)
        decays = np.asarray(packet["decay_times_seconds"][:count], dtype=np.float64)
        weights = np.asarray(packet["mode_weights"][:count], dtype=np.float64)
    geometry_path = selected.with_name("spectral_geometry.npz")
    if not geometry_path.exists():
        return _plate_profile(count)
    with np.load(geometry_path, allow_pickle=False) as geometry:
        vertices = np.asarray(geometry["vertices"], dtype=np.float64)
        eigenvectors = np.asarray(geometry["eigenvectors"][:, :count], dtype=np.float64)
    sample_count = min(max(64, int(visual_samples)), len(vertices))
    selection = np.linspace(0, len(vertices) - 1, sample_count, dtype=np.int64)
    vertices = vertices[selection]
    vertices -= np.mean(vertices, axis=0, keepdims=True)
    vertices /= max(float(np.max(np.linalg.norm(vertices, axis=1))), 1e-12)
    return ModalProfile(
        selected.stem,
        eigenvalues,
        frequencies,
        decays,
        weights,
        vertices,
        eigenvectors[selection],
    )


def _single_qubit_gate(gate: np.ndarray, qubit: int, qubits: int = 4) -> np.ndarray:
    # Qubit zero is the least-significant tensor factor, matching Qiskit.
    factors = [gate if index == qubit else np.eye(2) for index in reversed(range(qubits))]
    result = np.asarray([[1.0 + 0.0j]])
    for factor in factors:
        result = np.kron(result, factor)
    return result


def _cnot(control: int, target: int, qubits: int = 4) -> np.ndarray:
    dimension = 2**qubits
    result = np.zeros((dimension, dimension), dtype=np.complex128)
    for basis in range(dimension):
        destination = basis ^ (1 << target) if basis & (1 << control) else basis
        result[destination, basis] = 1.0
    return result


def _rotation(axis: str, angle: float) -> np.ndarray:
    identity = np.eye(2, dtype=np.complex128)
    pauli = {
        "x": np.asarray([[0, 1], [1, 0]], dtype=np.complex128),
        "y": np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128),
        "z": np.asarray([[1, 0], [0, -1]], dtype=np.complex128),
    }[axis]
    return math.cos(0.5 * angle) * identity - 1j * math.sin(0.5 * angle) * pauli


def exact_density_frame(phase: float, entanglement: float = 0.82) -> np.ndarray:
    """Exact four-qubit statevector evolution followed by declared dephasing."""
    state = np.zeros(16, dtype=np.complex128)
    state[0] = 1.0
    hadamard = np.asarray([[1, 1], [1, -1]], dtype=np.complex128) / math.sqrt(2.0)
    state = _single_qubit_gate(hadamard, 0) @ state
    for target in (1, 2, 3):
        state = _cnot(0, target) @ state
    for qubit in range(4):
        ry = _single_qubit_gate(_rotation("y", phase * (0.31 + 0.09 * qubit)), qubit)
        rz = _single_qubit_gate(_rotation("z", phase * (0.23 + 0.07 * qubit)), qubit)
        state = rz @ ry @ state
    pure = np.outer(state, state.conj())
    mix = np.eye(16, dtype=np.complex128) / 16.0
    coherence = float(np.clip(entanglement, 0.0, 1.0))
    return coherence * pure + (1.0 - coherence) * mix


class QuantumChladniController:
    def __init__(
        self,
        profile: ModalProfile,
        client: Any,
        *,
        rate_hz: float = 8.0,
        entanglement: float = 0.82,
        temporal_client: Any | None = None,
        qpe_bits: int = 5,
        random_seed: int = 20260719,
    ) -> None:
        self.profile = profile
        self.client = client
        self.rate_hz = max(0.2, float(rate_hz))
        self.entanglement = float(np.clip(entanglement, 0.0, 1.0))
        self.temporal_client = temporal_client
        self.qpe_bits = int(np.clip(int(qpe_bits), 2, 10))
        self._rng = np.random.default_rng(random_seed)
        self.running = True
        self.revision = 0
        self.phase = 0.0
        self._lock = threading.RLock()
        self._stop = threading.Event()

    def frame(self) -> QuantumChladniFrame:
        with self._lock:
            rho = exact_density_frame(self.phase, self.entanglement)
            # Make population transfer, rather than only phase rotation,
            # perceptible between the 8 Hz published frames.
            self.phase += 0.18
            self.revision += 1
            revision = self.revision
        if self.temporal_client is not None:
            flattened = rho.reshape(-1)
            density_payload: list[float | int] = [revision, rho.shape[0]]
            for value in flattened:
                density_payload.extend((float(value.real), float(value.imag)))
            self.temporal_client.send_message(
                "/qmw/temporal/source/density", density_payload
            )
        count = len(self.profile.eigenvalues)
        modal_packet = {
            "model": self.profile.name,
            "eigenvalues": self.profile.eigenvalues,
            # Projection needs the geometric mode count, not vertex positions.
            "eigenvectors": self.profile.eigenvectors,
            "frequencies_hz": self.profile.frequencies_hz,
            "decay_times_seconds": self.profile.decay_seconds,
            "mode_weights": self.profile.mode_weights,
        }
        engine = QuantumEigenfieldEngine(
            rho,
            modal_packet=modal_packet,
            config=QuantumEigenfieldConfig(n_geometric_modes=count),
        )
        probabilities, amplitudes = engine.project()
        with self._lock:
            qpe = qpe_condition_modal_distribution(
                probabilities,
                self.profile.eigenvalues,
                self.qpe_bits,
                self._rng,
            )
        # Measuring the phase register leaves the system in the conditional
        # superposition of eigenmodes compatible with that finite-bit result.
        # Retain the projected complex phases while replacing magnitudes with
        # the exact QPE posterior that drives both V*a and resonator gains.
        probabilities = qpe.posterior
        amplitudes = np.sqrt(probabilities) * np.exp(1j * np.angle(amplitudes))
        descriptors = engine.quantum_descriptors
        entropy_norm = descriptors.entropy_bits / max(descriptors.max_mixed_entropy_bits, 1e-12)
        coherence_norm = min(1.0, descriptors.coherence_l1 / max(descriptors.dimension - 1, 1))
        index = np.arange(count, dtype=np.float64)
        pans = np.sin(index * 2.399963229728653 + np.angle(amplitudes))
        diagonal = np.real(np.diag(rho))
        basis_populations = np.asarray(diagonal, dtype=np.float64)
        density_values, density_vectors = np.linalg.eigh(rho)
        principal = density_vectors[:, int(np.argmax(density_values))]
        reference_index = int(np.argmax(np.abs(principal)))
        reference_phase = float(np.angle(principal[reference_index]))
        basis_phases = np.angle(principal * np.exp(-1j * reference_phase))
        return QuantumChladniFrame(
            revision,
            descriptors.purity,
            entropy_norm,
            coherence_norm,
            self.profile.frequencies_hz.copy(),
            self.profile.decay_seconds.copy(),
            self.profile.mode_weights.copy(),
            probabilities,
            np.angle(amplitudes),
            pans,
            basis_populations,
            basis_phases,
            qpe.bits,
            qpe.measured_integer,
            qpe.measured_phase,
            qpe.dominant_mode,
            qpe.confidence,
        )

    def publish(self, frame: QuantumChladniFrame) -> None:
        self.client.send_message(
            "/qmw/chladni/begin",
            [
                frame.revision,
                frame.mode_count,
                frame.purity,
                frame.entropy_normalized,
                frame.coherence_normalized,
            ],
        )
        self.client.send_message(
            "/qmw/chladni/populations",
            [
                frame.revision,
                *[
                    component
                    for probability, phase in zip(
                        frame.basis_populations, frame.basis_phases
                    )
                    for component in (float(probability), float(phase))
                ],
            ],
        )
        for index in range(frame.mode_count):
            self.client.send_message(
                "/qmw/chladni/mode",
                [
                    frame.revision,
                    index,
                    float(frame.frequencies_hz[index]),
                    float(frame.decay_seconds[index]),
                    float(frame.mode_weights[index]),
                    float(frame.probabilities[index]),
                    float(frame.phases[index]),
                    float(frame.pans[index]),
                ],
            )
        self.client.send_message("/qmw/chladni/end", frame.revision)
        self.client.send_message(
            "/qmw/chladni/status",
            (
                f"QPE m={frame.qpe_bits} |{frame.qpe_bitstring}> "
                f"phi={frame.qpe_phase:.6f} | mode {frame.qpe_dominant_mode + 1} "
                f"posterior={100.0 * frame.qpe_confidence:.1f}% | "
                f"{frame.frequencies_hz[frame.qpe_dominant_mode]:.2f} Hz"
            ),
        )

    def publish_geometry(self) -> None:
        """Send a downsampled mesh/eigenbasis once; Max stores it as Jitter matrices."""
        sample_count, mode_count = self.profile.eigenvectors.shape
        self.client.send_message(
            "/qmw/chladni/geometry/begin", [sample_count, mode_count]
        )
        for index, (vertex, modes) in enumerate(
            zip(self.profile.vertices, self.profile.eigenvectors)
        ):
            self.client.send_message(
                "/qmw/chladni/geometry/vertex",
                [index, *vertex.astype(float).tolist(), *modes.astype(float).tolist()],
            )
            # Avoid overflowing Max's UDP receive queue with one large burst.
            # Missing even one vertex prevents the atomic Jitter commit.
            if index % 16 == 15:
                time.sleep(0.002)
        self.client.send_message("/qmw/chladni/geometry/end", sample_count)

    def set_running(self, value: Any) -> None:
        with self._lock:
            self.running = bool(int(value))

    def set_entanglement(self, value: Any) -> None:
        with self._lock:
            self.entanglement = float(np.clip(float(value), 0.0, 1.0))

    def set_qpe_bits(self, value: Any) -> None:
        with self._lock:
            self.qpe_bits = int(np.clip(int(float(value)), 2, 10))

    def measure(self) -> None:
        # The continuous frame stream already performs QPE. This gesture moves
        # the trial state into a new phase sector and audibly strikes the latest
        # QPE-conditioned modal bank.
        with self._lock:
            outcome = int(np.argmax(np.real(np.diag(exact_density_frame(self.phase, self.entanglement)))))
            self.phase = (outcome + 1) * math.pi / 8.0
        self.client.send_message("/qmw/chladni/strike", 0.72)

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        self.client.send_message("/qmw/chladni/status", f"online {self.profile.name}")
        self.publish_geometry()
        period = 1.0 / self.rate_hz
        while not self._stop.is_set():
            started = time.monotonic()
            with self._lock:
                active = self.running
            if active:
                self.publish(self.frame())
            self._stop.wait(max(0.0, period - (time.monotonic() - started)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modal-packet", type=Path)
    parser.add_argument("--modes", type=int, default=24)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7400)
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=7473)
    parser.add_argument("--rate", type=float, default=8.0)
    parser.add_argument("--entanglement", type=float, default=0.82)
    parser.add_argument("--qpe-bits", type=int, default=5)
    parser.add_argument("--visual-samples", type=int, default=768)
    parser.add_argument("--temporal-host", default="127.0.0.1")
    parser.add_argument("--temporal-port", type=int, default=7444)
    args = parser.parse_args()

    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
    from pythonosc.udp_client import SimpleUDPClient

    profile = load_modal_profile(
        args.modal_packet,
        max(1, args.modes),
        max(64, args.visual_samples),
    )
    controller = QuantumChladniController(
        profile,
        SimpleUDPClient(args.host, args.out_port),
        rate_hz=args.rate,
        entanglement=args.entanglement,
        temporal_client=SimpleUDPClient(args.temporal_host, args.temporal_port),
        qpe_bits=args.qpe_bits,
    )
    dispatcher = Dispatcher()
    dispatcher.map("/qmw/chladni/control/run", lambda _address, value: controller.set_running(value))
    dispatcher.map(
        "/qmw/chladni/control/entanglement",
        lambda _address, value: controller.set_entanglement(value),
    )
    dispatcher.map("/qmw/chladni/control/measure", lambda _address, *_args: controller.measure())
    dispatcher.map(
        "/qmw/chladni/control/qpe-bits",
        lambda _address, value: controller.set_qpe_bits(value),
    )
    dispatcher.map(
        "/qmw/chladni/control/geometry",
        lambda _address, *_args: controller.publish_geometry(),
    )
    server = ThreadingOSCUDPServer((args.control_host, args.control_port), dispatcher)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def halt(_signum: int, _frame: Any) -> None:
        controller.stop()

    signal.signal(signal.SIGINT, halt)
    signal.signal(signal.SIGTERM, halt)
    print(f"Quantum Chladni → {args.host}:{args.out_port}; controls {args.control_host}:{args.control_port}")
    print(
        f"Profile: {profile.name}, modes: {len(profile.eigenvalues)}, "
        f"QPE register: {controller.qpe_bits} qubits"
    )
    try:
        controller.run()
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
