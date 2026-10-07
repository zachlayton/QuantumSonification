"""Explicit, renderer-neutral sonification adapter for atomic frames."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .schema import AtomicOrbitalFrame


@dataclass(frozen=True)
class AtomicSonificationFrame:
    """Perceptual controls derived from, but not confused with, atomic physics."""

    m_values: tuple[int, ...]
    orbital_populations: np.ndarray
    orbital_amplitudes: np.ndarray
    adjacent_coherence_magnitudes: np.ndarray
    adjacent_coherence_phases: np.ndarray
    spin_bloch: np.ndarray
    spin_purity: float
    orbital_direction: np.ndarray
    total_direction: np.ndarray
    spin_orbit_correlation: float
    radial_nodes: int
    angular_nodes: int


def atomic_sonification_frame(frame: AtomicOrbitalFrame) -> AtomicSonificationFrame:
    """Map a scientific frame to bounded controls without assigning pitches."""

    ell = frame.ell
    coherences = np.diag(frame.orbital_rho, k=1)
    hbar = float(frame.metadata.get("hbar", 1.0))
    orbital_scale = max(float(ell), 1.0) * hbar
    total_scale = max(float(ell) + 0.5, 0.5) * hbar
    correlation_scale = max(0.5 * (ell + 1), 0.5) * hbar**2
    return AtomicSonificationFrame(
        m_values=tuple(range(-ell, ell + 1)),
        orbital_populations=np.asarray(frame.orbital_populations, dtype=float).copy(),
        orbital_amplitudes=np.sqrt(
            np.clip(np.asarray(frame.orbital_populations, dtype=float), 0.0, 1.0)
        ),
        adjacent_coherence_magnitudes=np.abs(coherences),
        adjacent_coherence_phases=np.angle(coherences),
        spin_bloch=np.clip(np.asarray(frame.pauli_vector, dtype=float), -1.0, 1.0),
        spin_purity=float(frame.spin_purity),
        orbital_direction=np.clip(np.asarray(frame.mean_l) / orbital_scale, -1.0, 1.0),
        total_direction=np.clip(np.asarray(frame.mean_j) / total_scale, -1.0, 1.0),
        spin_orbit_correlation=float(
            np.clip(frame.mean_l_dot_s / correlation_scale, -1.0, 1.0)
        ),
        radial_nodes=frame.n - frame.ell - 1,
        angular_nodes=frame.ell,
    )


__all__ = ["AtomicSonificationFrame", "atomic_sonification_frame"]
