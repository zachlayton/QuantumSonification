from __future__ import annotations

from typing import Any

import numpy as np

from qmw.core import QuantumStateFrame


def frame_from_engine_snapshot(
    *,
    t: float,
    dt: float,
    rho: np.ndarray,
    hamiltonian: Any | None = None,
    density_metrics: dict[str, Any] | None = None,
    density_engine: Any | None = None,
    extra_observables: dict[str, Any] | None = None,
    memory: dict[str, Any] | None = None,
    bohm: dict[str, Any] | None = None,
    visual: dict[str, Any] | None = None,
) -> QuantumStateFrame:
    """Build a QuantumStateFrame from the current monolithic engine objects."""
    observables = dict(density_metrics or {})
    if extra_observables:
        observables.update(extra_observables)

    arrays: dict[str, np.ndarray] = {}
    source = getattr(density_engine, "excitation_source", None)
    source_name = type(source).__name__ if source is not None else None

    if source is not None and hasattr(source, "probability_distribution"):
        arrays["wavepacket_probability"] = np.asarray(
            source.probability_distribution,
            dtype=float,
        )
    if source is not None and hasattr(source, "wavefunction"):
        arrays["wavefunction"] = np.asarray(source.wavefunction, dtype=np.complex128)

    return QuantumStateFrame(
        t=float(t),
        dt=float(dt),
        rho=np.asarray(rho, dtype=np.complex128),
        hamiltonian=hamiltonian,
        source_name=source_name,
        source_descriptor=getattr(density_engine, "source_descriptor", None),
        observables=observables,
        arrays=arrays,
        metadata={
            "circuit_state": getattr(density_engine, "circuit_state", {}),
            "memory": dict(memory or {}),
            "bohm": dict(bohm or {}),
            "visual": dict(visual or {}),
        },
    )
