"""Read-only mapping from authoritative four-qubit state to a V4.4 frame."""

from __future__ import annotations

import math

import numpy as np

from qmw.flow.current_events import events_from_hilbert_edges
from qmw.quantum.diagnostics import diagnose_hilbert_transport
from qmw.quantum.hilbert_current import (
    current_matrix,
    hermitian_matrix,
    pauli_resolved_current,
    sparse_current_edges,
)
from qmw.quantum.pauli_decompose import pauli_decomposition
from qmw.quantum.pauli_flow import pauli_activities, rank_pauli_activity

from .qmw_4_4_frame import QMW44QuantumFrame


def observe_qmw_4_4_quantum_frame(
    revision: int,
    time: float,
    rho: object,
    hamiltonian: object,
    *,
    top_k: int = 8,
    current_threshold: float = 1.0e-9,
    hbar: float = 1.0,
) -> QMW44QuantumFrame:
    """Observe one bounded frame without evolving or modifying its sources."""

    density = hermitian_matrix("rho", rho)
    generator = hermitian_matrix("hamiltonian", hamiltonian)
    if density.shape != (16, 16) or generator.shape != density.shape:
        raise ValueError("QMW V4.4 requires matching 16x16 rho and Hamiltonian matrices.")
    trace = complex(np.trace(density))
    eigenvalues = np.linalg.eigvalsh(density)
    if abs(trace.imag) > 1.0e-9 or not np.isclose(trace.real, 1.0, atol=1.0e-8, rtol=0.0):
        raise ValueError("rho must have unit trace.")
    if float(np.min(eigenvalues)) < -1.0e-9:
        raise ValueError("rho must be positive semidefinite.")

    current = current_matrix(density, generator, hbar=hbar)
    contributions = {
        term.label: pauli_resolved_current(
            density, term.matrix, term.coefficient, hbar=hbar
        )
        for term in pauli_decomposition(generator)
        if set(term.label) != {"I"}
    }
    edges = sparse_current_edges(
        current, threshold=current_threshold,
        pauli_contributions=contributions,
    )
    activities = rank_pauli_activity(
        pauli_activities(density, generator, hbar=hbar), top_k=top_k
    )
    populations = np.real(np.diag(density))
    return QMW44QuantumFrame(
        revision=int(revision),
        time=float(time),
        populations=populations,
        current=current,
        current_edges=edges,
        pauli_activity=activities,
        current_events=events_from_hilbert_edges(edges),
        diagnostics=diagnose_hilbert_transport(density, generator, hbar=hbar),
    )


def hilbert_event_strength(
    frame: QMW44QuantumFrame,
    dt: float,
    *,
    current_scale: float = 1.0,
) -> float:
    """Convert current rate to a bounded per-step event probability.

    Current magnitudes have inverse-time units. Integrating the rate over
    ``dt`` before applying the exponential makes this cue stable when the
    same trajectory is observed at a different frame rate.
    """

    if not isinstance(frame, QMW44QuantumFrame):
        raise ValueError("frame must be a QMW44QuantumFrame.")
    if not math.isfinite(float(dt)) or dt <= 0.0:
        raise ValueError("dt must be finite and positive.")
    if not math.isfinite(float(current_scale)) or current_scale <= 0.0:
        raise ValueError("current_scale must be finite and positive.")
    total_rate = sum(edge.magnitude for edge in frame.current_edges)
    return float(1.0 - math.exp(-(total_rate / current_scale) * float(dt)))


def hilbert_pair_modal_drive(rho: object) -> np.ndarray:
    """Project sixteen computational lanes into eight complex observer modes.

    Adjacent basis lanes ``(2m, 2m+1)`` define one declared modal bin.  Pair
    occupation owns magnitude and the within-pair density-matrix coherence
    owns phase.  The result has unit norm for a normalized density matrix.
    It is a read-only downstream descriptor, not an alternate evolution of
    ``rho`` and not an amplitude-producing sonic event.
    """

    density = hermitian_matrix("rho", rho)
    if density.shape != (16, 16):
        raise ValueError("Hilbert pair-modal projection requires a 16x16 rho.")
    trace = complex(np.trace(density))
    if abs(trace.imag) > 1.0e-9 or not np.isclose(
        trace.real, 1.0, atol=1.0e-8, rtol=0.0
    ):
        raise ValueError("rho must have unit trace.")
    eigenvalues = np.linalg.eigvalsh(density)
    if float(np.min(eigenvalues)) < -1.0e-9:
        raise ValueError("rho must be positive semidefinite.")

    populations = np.maximum(np.real(np.diag(density)), 0.0)
    result = np.zeros(8, dtype=np.complex128)
    for mode in range(8):
        left, right = 2 * mode, (2 * mode) + 1
        occupation = float(populations[left] + populations[right])
        coherence = complex(density[left, right])
        phase = float(np.angle(coherence)) if abs(coherence) > 1.0e-12 else 0.0
        result[mode] = math.sqrt(max(occupation, 0.0)) * np.exp(1j * phase)
    norm = float(np.linalg.norm(result))
    if norm <= 1.0e-12:
        raise ValueError("rho produced no finite pair-modal occupation.")
    return result / norm


def rotating_hilbert_pair_modal_drive(
    rho: object, frequencies: object, time: float,
) -> np.ndarray:
    """Express the normalized Hilbert descriptor in a modal rotating frame."""

    omega = np.asarray(frequencies, dtype=float)
    if omega.shape != (8,) or not np.all(np.isfinite(omega)):
        raise ValueError("frequencies must be a finite eight-vector.")
    if not math.isfinite(float(time)):
        raise ValueError("time must be finite.")
    return hilbert_pair_modal_drive(rho) * np.exp(1j * omega * float(time))


__all__ = [
    "hilbert_event_strength", "hilbert_pair_modal_drive",
    "rotating_hilbert_pair_modal_drive",
    "observe_qmw_4_4_quantum_frame",
]
