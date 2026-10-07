"""Typed access to the Hilbert-basis flow sealed in a ``QuantumFrame``.

The observation keeps the authoritative frame by identity.  It does not copy
or reinterpret its current as a configuration-space or spatial current.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qmw.quantum.dynamics import QuantumFrame


@dataclass(frozen=True)
class HilbertBasisFlowObservation:
    """Read-only computational-basis flow view of one quantum revision."""

    source: QuantumFrame
    basis_label: str = "displayed_computational_basis"
    provenance: str = "authoritative_quantum_frame_hilbert_basis_flow_v1"

    def __post_init__(self) -> None:
        if not isinstance(self.source, QuantumFrame):
            raise TypeError("source must be a sealed QuantumFrame")
        if not self.basis_label:
            raise ValueError("basis_label must be nonempty")
        if not self.provenance:
            raise ValueError("provenance must be nonempty")
        if self.source.basis_current_inflow.flags.writeable:
            raise ValueError("the authoritative basis current must be read-only")
        if not np.allclose(
            np.sum(self.source.basis_current_inflow, axis=1),
            self.source.population_rate_unitary,
            atol=1.0e-10,
            rtol=1.0e-10,
        ):
            raise ValueError("basis current does not satisfy unitary population continuity")

    @property
    def time(self) -> float:
        return self.source.time

    @property
    def revision(self) -> int:
        return self.source.frame_index

    @property
    def current_inflow(self) -> np.ndarray:
        return self.source.basis_current_inflow

    @property
    def population_rate_unitary(self) -> np.ndarray:
        return self.source.population_rate_unitary

    @property
    def is_spatial(self) -> bool:
        return False


__all__ = ["HilbertBasisFlowObservation"]
