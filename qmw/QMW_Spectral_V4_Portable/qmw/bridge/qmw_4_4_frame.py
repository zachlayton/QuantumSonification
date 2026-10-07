"""Canonical bounded quantum-observer frame for the integrated instrument."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from qmw.flow.current_events import CurrentEvent
from qmw.quantum.diagnostics import HilbertDiagnostics
from qmw.quantum.hilbert_current import CurrentEdge
from qmw.quantum.pauli_flow import PauliActivity


@dataclass(frozen=True)
class QMW44QuantumFrame:
    """One read-only four-qubit observation transaction.

    The authoritative density matrix and Hamiltonian are intentionally absent.
    This is the stable interface consumed by visual and sonic observers.
    """

    revision: int
    time: float
    populations: np.ndarray
    current: np.ndarray
    current_edges: tuple[CurrentEdge, ...]
    pauli_activity: tuple[PauliActivity, ...]
    current_events: tuple[CurrentEvent, ...]
    diagnostics: HilbertDiagnostics
    provenance: str = "read_only_four_qubit_hilbert_transport_observer_v4_4"

    def __post_init__(self) -> None:
        if int(self.revision) != self.revision or self.revision < 0:
            raise ValueError("revision must be a nonnegative integer.")
        if not math.isfinite(float(self.time)):
            raise ValueError("time must be finite.")
        populations = np.asarray(self.populations, dtype=float)
        current = np.asarray(self.current, dtype=float)
        if populations.shape != (16,) or not np.all(np.isfinite(populations)):
            raise ValueError("V4.4 quantum populations must be a finite 16-vector.")
        if np.min(populations) < -1.0e-9 or not np.isclose(np.sum(populations), 1.0, atol=1.0e-8, rtol=0.0):
            raise ValueError("V4.4 quantum populations must be normalized and nonnegative.")
        if current.shape != (16, 16) or not np.all(np.isfinite(current)):
            raise ValueError("V4.4 Hilbert current must be a finite 16x16 matrix.")
        if not np.allclose(current, -current.T, atol=1.0e-9, rtol=0.0):
            raise ValueError("V4.4 Hilbert current must be antisymmetric.")
        object.__setattr__(self, "populations", np.array(populations, copy=True))
        object.__setattr__(self, "current", np.array(current, copy=True))


__all__ = ["QMW44QuantumFrame"]
