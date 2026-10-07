#!/usr/bin/env python3
"""Phase-aware bridge from the eight-qubit I Ching oracle to QMW networks.

One consultation is frozen into one immutable, revisioned control frame.  The
frame contains a validated four-qubit density state, a magnetic Laplacian on
the 64-node hexagram hypercube, line coherences/phases, and gauge-invariant
square-cycle fluxes.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
import time
from typing import Iterable

import numpy as np

import qmw_iching_oracle8_v2 as oracle

HEXAGRAM_QUBITS = tuple(range(6))
DENSITY_QUBITS = oracle.PAULI_QUBITS
NETWORK_ROOT = "/qmw/iching/network"


def bit_reversal_permutation(n_qubits: int) -> np.ndarray:
    """Convert oracle tensor-axis order to q0-as-least-significant order."""
    return np.asarray(
        [int(f"{index:0{n_qubits}b}"[::-1], 2) for index in range(1 << n_qubits)],
        dtype=np.int64,
    )


def density_in_lsb_order(psi: np.ndarray, qubits: Iterable[int]) -> np.ndarray:
    qubits = tuple(qubits)
    rho = oracle.reduced_density_matrix(psi, qubits)
    permutation = bit_reversal_permutation(len(qubits))
    return rho[np.ix_(permutation, permutation)]


def validate_density_matrix(rho: np.ndarray, tolerance: float = 1e-9) -> np.ndarray:
    """Validate and remove only harmless floating-point negativity."""
    matrix = np.asarray(rho, dtype=np.complex128)
    if matrix.shape != (16, 16):
        raise ValueError(f"Expected a 16x16 density matrix; got {matrix.shape}")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("Density matrix contains non-finite values")
    if np.max(np.abs(matrix - matrix.conj().T)) > tolerance:
        raise ValueError("Density matrix is not Hermitian")
    if abs(np.trace(matrix) - 1.0) > tolerance:
        raise ValueError("Density matrix trace is not one")
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2)
    if values.min() < -tolerance:
        raise ValueError("Density matrix is not positive semidefinite")
    values = np.clip(values.real, 0.0, None)
    repaired = (vectors * values) @ vectors.conj().T
    return repaired / np.trace(repaired).real


@dataclass(frozen=True)
class LinePhase:
    line: int
    moving_probability: float
    coherence: float
    phase_radians: float


@dataclass(frozen=True)
class GraphEdge:
    source: int
    target: int
    line: int
    weight: float
    phase_radians: float


@dataclass(frozen=True)
class CycleFlux:
    line_a: int
    line_b: int
    flux_radians: float
    strength: float


@dataclass(frozen=True)
class NetworkControlFrame:
    revision: int
    seed: int
    primary: int
    moving_mask: int
    transformed: int
    change_register: int
    pauli_operator: str
    pauli_expectation: float
    mutual_information_bits: float
    change_entropy_bits: float
    density_purity: float
    primary_path_phase_radians: float
    primary_path_strength: float
    line_phases: tuple[LinePhase, ...]
    edges: tuple[GraphEdge, ...]
    cycle_fluxes: tuple[CycleFlux, ...]


def line_phase_field(psi: np.ndarray, moving_probabilities: Iterable[float]) -> tuple[LinePhase, ...]:
    result = []
    for q, probability in enumerate(moving_probabilities):
        # <X> + i<Y> is a phase-sensitive local coherence quadrature.
        quadrature = complex(oracle.expect(psi, {q: "X"}), oracle.expect(psi, {q: "Y"}))
        result.append(LinePhase(q + 1, float(probability), float(abs(quadrature)),
                                float(np.angle(quadrature)) if abs(quadrature) > 1e-12 else 0.0))
    return tuple(result)


def build_magnetic_laplacian(
    rho_lu: np.ndarray,
    moving_probabilities: Iterable[float],
    *,
    phase_threshold: float = 1e-12,
) -> tuple[np.ndarray, np.ndarray, tuple[GraphEdge, ...]]:
    """Build L=D-A with conjugate phase edges on the hexagram hypercube."""
    probabilities = tuple(float(np.clip(p, 0.0, 1.0)) for p in moving_probabilities)
    adjacency = np.zeros((64, 64), dtype=np.complex128)
    edges = []
    for source in range(64):
        for q in range(6):
            target = source ^ (1 << q)
            if source >= target:
                continue
            coherence = complex(rho_lu[source, target])
            magnitude = abs(coherence)
            weight = probabilities[q] * magnitude
            phase = float(np.angle(coherence)) if magnitude > phase_threshold else 0.0
            value = weight * np.exp(1j * phase)
            adjacency[source, target] = value
            adjacency[target, source] = value.conjugate()
            edges.append(GraphEdge(source, target, q + 1, float(weight), phase))
    degree = np.sum(np.abs(adjacency), axis=1)
    laplacian = np.diag(degree) - adjacency
    return adjacency, laplacian, tuple(edges)


def canonical_path(primary: int, moving_mask: int) -> tuple[int, ...]:
    path = [int(primary)]; node = int(primary)
    for q in range(6):
        if moving_mask & (1 << q):
            node ^= 1 << q
            path.append(node)
    return tuple(path)


def path_phase(adjacency: np.ndarray, path: Iterable[int]) -> tuple[float, float]:
    nodes = tuple(path)
    if len(nodes) < 2:
        return 0.0, 1.0
    phase, strength = 0.0, 1.0
    for source, target in zip(nodes, nodes[1:]):
        value = complex(adjacency[source, target])
        phase += float(np.angle(value)) if abs(value) > 1e-15 else 0.0
        strength *= abs(value)
    return float(np.angle(np.exp(1j * phase))), float(strength)


def square_cycle_fluxes(adjacency: np.ndarray, primary: int) -> tuple[CycleFlux, ...]:
    fluxes = []
    for qa in range(6):
        for qb in range(qa + 1, 6):
            a = primary
            b = a ^ (1 << qa)
            c = b ^ (1 << qb)
            d = a ^ (1 << qb)
            product = adjacency[a, b] * adjacency[b, c] * adjacency[c, d] * adjacency[d, a]
            fluxes.append(CycleFlux(qa + 1, qb + 1,
                                    float(np.angle(product)) if abs(product) > 1e-15 else 0.0,
                                    float(abs(product) ** 0.25)))
    return tuple(fluxes)


def build_control_frame(seed: int | None = None, depth: int = 3, revision: int | None = None):
    reading, psi, _rho, _reduced, field = oracle.consult(seed, depth)
    rho_density = validate_density_matrix(density_in_lsb_order(psi, DENSITY_QUBITS))
    rho_lu = density_in_lsb_order(psi, HEXAGRAM_QUBITS)
    adjacency, laplacian, edges = build_magnetic_laplacian(
        rho_lu, reading.moving_probabilities
    )
    path = canonical_path(reading.primary_binary, reading.moving_mask)
    primary_phase, primary_strength = path_phase(adjacency, path)
    if revision is None:
        revision = time.monotonic_ns() & 0x7fffffff
    frame = NetworkControlFrame(
        revision=int(revision), seed=reading.seed, primary=reading.primary_binary,
        moving_mask=reading.moving_mask, transformed=reading.transformed_binary,
        change_register=reading.change_register,
        pauli_operator=reading.pauli81_operator,
        pauli_expectation=reading.pauli81_expectation,
        mutual_information_bits=reading.mutual_information_L_U_bits,
        change_entropy_bits=reading.entropy_C_bits,
        density_purity=float(np.trace(rho_density @ rho_density).real),
        primary_path_phase_radians=primary_phase,
        primary_path_strength=primary_strength,
        line_phases=line_phase_field(psi, reading.moving_probabilities), edges=edges,
        cycle_fluxes=square_cycle_fluxes(adjacency, reading.primary_binary),
    )
    return frame, rho_density, rho_lu, adjacency, laplacian, field


def _matrix_json(matrix: np.ndarray) -> dict:
    return {"real": matrix.real.tolist(), "imag": matrix.imag.tolist()}


def export_json(path: str, frame: NetworkControlFrame, rho_density: np.ndarray,
                rho_lu: np.ndarray, adjacency: np.ndarray, laplacian: np.ndarray,
                pauli_field: dict[str, float]) -> None:
    payload = {"frame": asdict(frame), "density_4q": _matrix_json(rho_density),
               "rho_LU": _matrix_json(rho_lu), "adjacency": _matrix_json(adjacency),
               "magnetic_laplacian": _matrix_json(laplacian), "pauli81": pauli_field}
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def osc_messages(frame: NetworkControlFrame, rho_density: np.ndarray):
    """Yield a bounded, atomic OSC transaction; rows avoid oversized datagrams."""
    root, revision = NETWORK_ROOT, frame.revision
    yield root + "/begin", [revision, frame.seed, 64, 4]
    yield root + "/reading", [revision, frame.primary, frame.moving_mask,
                               frame.transformed, frame.change_register]
    yield root + "/metrics", [revision, frame.mutual_information_bits,
                               frame.change_entropy_bits, frame.density_purity]
    yield root + "/primary_phase", [revision, frame.primary_path_phase_radians,
                                     frame.primary_path_strength]
    yield root + "/pauli", [revision, frame.pauli_operator, frame.pauli_expectation]
    for item in frame.line_phases:
        yield root + "/line_phase", [revision, item.line, item.moving_probability,
                                      item.coherence, item.phase_radians]
    for edge in frame.edges:
        yield root + "/edge", [revision, edge.source, edge.target, edge.line,
                                edge.weight, edge.phase_radians]
    for flux in frame.cycle_fluxes:
        yield root + "/flux", [revision, flux.line_a, flux.line_b,
                                flux.flux_radians, flux.strength]
    for row in range(16):
        yield root + "/density/real_row", [revision, row, *rho_density[row].real.tolist()]
        yield root + "/density/imag_row", [revision, row, *rho_density[row].imag.tolist()]
    yield root + "/end", [revision]


def send_osc(frame: NetworkControlFrame, rho_density: np.ndarray, host: str, port: int):
    try:
        from pythonosc.udp_client import SimpleUDPClient
    except ImportError as exc:
        raise SystemExit("OSC requested: pip install python-osc") from exc
    client = SimpleUDPClient(host, port)
    for address, arguments in osc_messages(frame, rho_density):
        client.send_message(address, arguments)


def main():
    parser = argparse.ArgumentParser(description="Phase-aware I Ching density/Laplacian bridge")
    parser.add_argument("--seed", type=int); parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--revision", type=int); parser.add_argument("--json")
    parser.add_argument("--osc", action="store_true"); parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7403)
    args = parser.parse_args()
    result = build_control_frame(args.seed, args.depth, args.revision)
    frame, rho_density, rho_lu, adjacency, laplacian, field = result
    print("QMW I CHING PHASE-AWARE NETWORK BRIDGE V1")
    print(f"revision={frame.revision} seed={frame.seed}")
    print(f"H0={frame.primary} M={frame.moving_mask} H1={frame.transformed}")
    print(f"path phase={frame.primary_path_phase_radians:+.6f} rad "
          f"strength={frame.primary_path_strength:.6g}")
    print(f"density purity={frame.density_purity:.6f} "
          f"I(L:U)={frame.mutual_information_bits:.6f} bits")
    print(f"Pauli={frame.pauli_operator} expectation={frame.pauli_expectation:+.6f}")
    print(f"graph edges={len(frame.edges)} cycle fluxes={len(frame.cycle_fluxes)} "
          f"laplacian trace={np.trace(laplacian).real:.6f}")
    if args.json:
        export_json(args.json, frame, rho_density, rho_lu, adjacency, laplacian, field)
    if args.osc:
        send_osc(frame, rho_density, args.host, args.port)


if __name__ == "__main__":
    main()
