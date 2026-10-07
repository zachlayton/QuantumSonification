from __future__ import annotations

import numpy as np

from qmw.core.quantum_frame import QuantumFrame


def from_legacy_physics_frame(legacy_frame) -> QuantumFrame:
    """
    Adapter for the standalone QMW four-qubit XY validation model created earlier.
    """
    return QuantumFrame(
        t=np.asarray(legacy_frame.t),
        psi=np.asarray(legacy_frame.psi) if legacy_frame.psi is not None else None,
        rho=np.asarray(legacy_frame.rho),
        observables=dict(legacy_frame.observables),
        diagnostics=dict(legacy_frame.diagnostics),
        metadata=dict(legacy_frame.metadata),
    )
