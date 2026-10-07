"""Sign-invariant Laplacian controls for the Unified Instrument V3 resonator.

The graph itself is a declared read-only relational model. This module does
not alter a quantum frame, graph geometry, or the geometry-derived tuning. It
derives bounded control vectors for an audio adapter from invariant eigenvalue
gaps and graph-Fourier *band energies*, never raw eigenvector signs.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .frames import (
    MODE_COUNT,
    QUBIT_COUNT,
    RelationalGeometryFrame,
    RelationalSpectralControlFrame,
)
from .modal_resonance import modal_shape_membership


_EPS = 1.0e-12


@dataclass(frozen=True)
class RelationalSpectralConfig:
    """Bounded downstream response policy; none of these values alters tuning.

    ``excitation_depth`` controls the modal gain contrast, ``decay_depth`` the
    amplitude e-folding-time contrast, and ``brightness_depth`` the high-band
    emphasis supplied to a renderer. Each is an adapter choice in ``[0, 1]``.
    """

    excitation_depth: float = 0.55
    decay_depth: float = 0.35
    brightness_depth: float = 0.60

    def __post_init__(self) -> None:
        for name in ("excitation_depth", "decay_depth", "brightness_depth"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1].")


def _graph_band_energy(geometry: RelationalGeometryFrame) -> tuple[np.ndarray, float]:
    """Return sign-invariant nonconstant band energy of centred node degree."""

    degree = np.sum(geometry.adjacency, axis=1)
    field = degree - float(np.mean(degree))
    field_energy = float(field @ field)
    if field_energy <= _EPS:
        return np.zeros(QUBIT_COUNT - 1, dtype=float), 0.0
    coefficients = geometry.eigenvectors.T @ field
    bands = np.square(np.abs(coefficients[1:])) / field_energy
    laplacian_energy = float(field @ geometry.laplacian @ field)
    maximum = float(geometry.eigenvalues[-1])
    tension = 0.0 if maximum <= _EPS else np.clip(
        laplacian_energy / (maximum * field_energy), 0.0, 1.0
    )
    return bands, float(tension)


def observe_relational_spectral_control(
    geometry: RelationalGeometryFrame,
    *,
    config: RelationalSpectralConfig | None = None,
    revision: int | None = None,
) -> RelationalSpectralControlFrame:
    """Derive a compact 20-mode resonator control frame from one graph frame.

    The scalar bridge is ``lambda_2 / lambda_max``. Segmentation is the
    normalized high-mode gap ``(lambda_3 - lambda_2) / lambda_max``. The three
    band energies are squared graph-Fourier coefficients of centred degree;
    squaring makes the result independent of eigenvector sign.
    """

    if not isinstance(geometry, RelationalGeometryFrame):
        raise TypeError("geometry must be a RelationalGeometryFrame.")
    cfg = config or RelationalSpectralConfig()
    eigenvalues = np.asarray(geometry.eigenvalues, dtype=float)
    maximum = float(eigenvalues[-1])
    bridge = 0.0 if maximum <= _EPS else float(np.clip(eigenvalues[1] / maximum, 0.0, 1.0))
    segmentation = 0.0 if maximum <= _EPS else float(np.clip((eigenvalues[3] - eigenvalues[2]) / maximum, 0.0, 1.0))
    global_connectivity = float(np.clip(
        np.mean(geometry.adjacency[np.triu_indices(QUBIT_COUNT, 1)]), 0.0, 1.0
    ))
    bands, tension = _graph_band_energy(geometry)

    # The pre-existing 4 x 5 membership declares the lifting seam. The DC
    # group receives global connectivity; each other group receives one
    # nonconstant graph-Fourier band, without assigning significance to sign.
    group_activity = np.r_[global_connectivity, np.sqrt(np.clip(bands, 0.0, 1.0))]
    membership = modal_shape_membership()
    modal_activity = membership @ group_activity
    mode_position = np.linspace(0.0, 1.0, MODE_COUNT)
    excitation = np.clip(
        1.0 + float(cfg.excitation_depth) * ((2.0 * modal_activity) - 1.0),
        0.20,
        1.80,
    )
    persistence = (2.0 * bridge) - 1.0
    decay = np.clip(
        1.0 + float(cfg.decay_depth) * (persistence - (tension * mode_position)),
        0.25,
        1.75,
    )
    brightness = np.clip(
        0.25 + (0.45 * modal_activity)
        + (float(cfg.brightness_depth) * tension * mode_position),
        0.0,
        1.0,
    )
    return RelationalSpectralControlFrame(
        revision=geometry.revision if revision is None else revision,
        time=geometry.time,
        geometry_revision=geometry.revision,
        mode_ids=tuple(f"mode_{index:02d}" for index in range(MODE_COUNT)),
        bridge_strength=bridge,
        segmentation=segmentation,
        global_connectivity=global_connectivity,
        relational_tension=tension,
        graph_band_energy=bands,
        excitation_gain=excitation,
        decay_scale=decay,
        brightness=brightness,
        graph_field_label="centred_relational_degree_graph_fourier_energy",
        diagnostics=(
            "read-only relational Laplacian controls; no state evolution or tuning change",
            "graph Fourier bands use squared coefficients and are invariant to eigenvector sign",
            "decay_scale multiplies amplitude e-folding time; brightness is renderer-facing only",
        ),
    )


__all__ = ["RelationalSpectralConfig", "observe_relational_spectral_control"]
