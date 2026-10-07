"""Declared closed-boundary observer for valid V3 relational geometry.

The output contour is a bounded spectral parameter domain derived from the
ordered relational links.  It is intentionally *not* asserted to be a
physical surface of the tetrahedron.  This gives the acoustic field a stable
closed boundary without reifying the finite geometry model as spacetime.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .frames import DEFAULT_MODE_IDS, GeometryBoundaryFrame, MODE_COUNT, RelationalGeometryFrame


@dataclass(frozen=True)
class GeometryBoundaryConfig:
    """Declared bounded spectral-boundary policy.

    Ordered link-adjacency contrasts drive harmonics one through six.  Removing
    the mean ensures a uniform relational graph yields a circle.  The radial
    depth is bounded below one, so the closed contour cannot cross its origin.
    """

    sample_count: int = 256
    base_radius: float = 1.0
    radial_depth: float = 0.3
    orientation: str = "counterclockwise"
    mode_ids: tuple[str, ...] = DEFAULT_MODE_IDS

    def __post_init__(self) -> None:
        if int(self.sample_count) != self.sample_count or self.sample_count < 20:
            raise ValueError("sample_count must be an integer of at least 20.")
        if not math.isfinite(float(self.base_radius)) or self.base_radius <= 0.0:
            raise ValueError("base_radius must be finite and positive.")
        if not math.isfinite(float(self.radial_depth)) or not 0.0 <= self.radial_depth < 1.0:
            raise ValueError("radial_depth must lie in [0, 1).")
        if str(self.orientation) not in {"clockwise", "counterclockwise"}:
            raise ValueError("orientation must be clockwise or counterclockwise.")
        if len(self.mode_ids) != MODE_COUNT or len(set(self.mode_ids)) != MODE_COUNT or any(not str(item) for item in self.mode_ids):
            raise ValueError("mode_ids must contain the 20 unique stable mode identifiers.")


def real_fourier_boundary_basis(parameter: object) -> np.ndarray:
    """Return the named twenty-mode real Fourier lift on a periodic boundary."""

    samples = np.asarray(parameter, dtype=float)
    if samples.ndim != 1 or samples.size < MODE_COUNT or not np.all(np.isfinite(samples)):
        raise ValueError("parameter must be a finite one-dimensional vector with at least 20 samples.")
    theta = 2.0 * np.pi * samples
    columns = [np.ones(samples.size)]
    for harmonic in range(1, 10):
        columns.extend((np.cos(harmonic * theta), np.sin(harmonic * theta)))
    columns.append(np.cos(10.0 * theta))
    basis = np.column_stack(columns)
    if basis.shape != (samples.size, MODE_COUNT):
        raise RuntimeError("real Fourier lift did not produce twenty modes.")
    basis.flags.writeable = False
    return basis


def observe_geometry_boundary(
    geometry: RelationalGeometryFrame,
    *,
    config: GeometryBoundaryConfig | None = None,
    revision: int | None = None,
) -> GeometryBoundaryFrame:
    """Observe a bounded closed contour and its real 20-mode boundary basis.

    Invalid tetrahedral metrics are intentionally rejected: a best-fit display
    embedding is useful for diagnosis but cannot silently become the source of
    acoustic field evaluation.
    """

    if not isinstance(geometry, RelationalGeometryFrame):
        raise TypeError("geometry must be a RelationalGeometryFrame.")
    if not geometry.embedding_valid:
        raise ValueError("GeometryBoundaryFrame requires a valid relational tetrahedral embedding.")
    cfg = config or GeometryBoundaryConfig()
    parameter = np.arange(int(cfg.sample_count), dtype=float) / int(cfg.sample_count)
    theta = 2.0 * np.pi * parameter
    links = geometry.adjacency[np.triu_indices(geometry.adjacency.shape[0], 1)]
    contrast = links - float(np.mean(links))
    normalizer = float(np.sum(np.abs(contrast)))
    profile = np.zeros_like(theta)
    if normalizer > 1.0e-12:
        for harmonic, weight in enumerate(contrast, start=1):
            profile += (weight / normalizer) * np.cos(harmonic * theta)
    radius = float(cfg.base_radius) * (1.0 + (float(cfg.radial_depth) * profile))
    if np.min(radius) <= 0.0:
        raise RuntimeError("bounded radial policy produced a nonpositive contour radius.")
    direction = -1.0 if cfg.orientation == "clockwise" else 1.0
    contour = np.column_stack((radius * np.cos(theta), direction * radius * np.sin(theta), np.zeros_like(theta)))
    diagnostics = (
        "spectral parameter-domain contour derived from adjacency contrast; not a physical tetrahedral surface",
        "boundary basis is a declared real Fourier lift, not a graph-Laplacian eigenbasis",
    )
    return GeometryBoundaryFrame(
        revision=geometry.revision if revision is None else revision,
        time=geometry.time,
        geometry_revision=geometry.revision,
        mode_ids=tuple(cfg.mode_ids),
        sample_parameter=parameter,
        contour_xyz=contour,
        boundary_basis=real_fourier_boundary_basis(parameter),
        basis_label="v3_real_fourier_boundary_lift_on_relational_spectral_contour",
        orientation=cfg.orientation,
        diagnostics=diagnostics,
    )


__all__ = [
    "GeometryBoundaryConfig", "observe_geometry_boundary",
    "real_fourier_boundary_basis",
]
