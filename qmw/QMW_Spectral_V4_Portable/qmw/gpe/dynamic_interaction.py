"""Experimental density-coherence mappings for dynamic GPE interaction control."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from .density_matrix_coupling import _rho


Array = np.ndarray


@dataclass(frozen=True)
class CoherenceInteractionConfig:
    """An explicitly experimental law ``g = g0 + alpha f(C)``."""

    base_interaction: float = 0.0
    coherence_scale: float = 0.0
    inverse_coherence: bool = False

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.base_interaction)) or not math.isfinite(float(self.coherence_scale)):
            raise ValueError("interaction mapping parameters must be finite.")


@dataclass(frozen=True)
class CoherenceInteractionControl:
    """A scalar or spatial ``g`` field derived read-only from a density matrix."""

    coherence: float
    scalar_interaction: float
    interaction_field: Array | None
    mapping: str
    provenance: str = "experimental_density_coherence_to_gpe_interaction_mapping"


def global_coherence_metric(rho: Any) -> float:
    """Return bounded average off-diagonal coherence magnitude in ``[0, 1]``."""

    matrix = _rho(rho)
    count = matrix.shape[0]
    if count == 1:
        return 0.0
    magnitude = np.abs(matrix).copy()
    np.fill_diagonal(magnitude, 0.0)
    return float(np.clip(np.sum(magnitude) / (count - 1), 0.0, 1.0))


def density_coherence_to_interaction(
    rho: Any,
    *,
    config: CoherenceInteractionConfig | None = None,
    spatial_profile: Any | None = None,
) -> CoherenceInteractionControl:
    """Map a density coherence metric to scalar or spatial experimental ``g``.

    A supplied profile is a finite multiplicative field.  Pass the returned
    ``interaction_field`` (when present), otherwise ``scalar_interaction``,
    to ``GPEEngine.set_interaction`` before the desired integration step.
    """

    mapping = config or CoherenceInteractionConfig()
    coherence = global_coherence_metric(rho)
    driver = 1.0 - coherence if mapping.inverse_coherence else coherence
    scalar = float(mapping.base_interaction + mapping.coherence_scale * driver)
    field: Array | None = None
    if spatial_profile is not None:
        profile = np.asarray(spatial_profile, dtype=float)
        if profile.ndim not in (1, 2) or not np.all(np.isfinite(profile)):
            raise ValueError("spatial_profile must be a finite one- or two-dimensional field.")
        field = scalar * np.array(profile, copy=True)
    return CoherenceInteractionControl(
        coherence=coherence, scalar_interaction=scalar, interaction_field=field,
        mapping="inverse_coherence" if mapping.inverse_coherence else "direct_coherence",
    )


__all__ = [
    "CoherenceInteractionConfig", "CoherenceInteractionControl",
    "density_coherence_to_interaction", "global_coherence_metric",
]
