"""Canonical finite-lattice free scalar field for QMW V3."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class ScalarFieldSpec:
    """One-dimensional periodic Klein-Gordon lattice conventions.

    The Hamiltonian is ``H = 1/2 pi.T pi + 1/2 phi.T K phi`` with
    ``[phi_j, pi_l] = i hbar delta_jl`` and

    ``K = mass^2 I + (c/a)^2 (2I - shift_left - shift_right)``.
    """

    sites: int = 8
    mass: float = 0.6
    lattice_spacing: float = 1.0
    propagation_speed: float = 1.0
    hbar: float = 1.0
    boundary: str = "periodic"

    def __post_init__(self) -> None:
        if int(self.sites) != self.sites or self.sites < 2:
            raise ValueError("sites must be an integer of at least two")
        values = (
            self.mass,
            self.lattice_spacing,
            self.propagation_speed,
            self.hbar,
        )
        if not np.isfinite(values).all() or min(values) <= 0.0:
            raise ValueError("mass, spacing, speed, and hbar must be positive")
        if self.boundary != "periodic":
            raise ValueError("the scalar-field backend supports periodic boundaries only")


@dataclass(frozen=True)
class ScalarFieldModel:
    spec: ScalarFieldSpec
    stiffness: np.ndarray
    frequencies: np.ndarray
    mode_vectors: np.ndarray

    @classmethod
    def from_spec(cls, spec: ScalarFieldSpec | None = None) -> "ScalarFieldModel":
        spec = spec or ScalarFieldSpec()
        sites = spec.sites
        gradient_scale = (spec.propagation_speed / spec.lattice_spacing) ** 2
        stiffness = np.eye(sites, dtype=float) * (spec.mass**2 + 2 * gradient_scale)
        indices = np.arange(sites)
        stiffness[indices, (indices + 1) % sites] -= gradient_scale
        stiffness[indices, (indices - 1) % sites] -= gradient_scale

        # A generic eigensolver leaves every real eigenvector free to change
        # sign and can rotate the sine/cosine pairs inside degenerate periodic
        # subspaces. Those mathematically irrelevant gauge changes become
        # audible discontinuities when a coherent amplitude is attached to a
        # live mode index. Use the canonical real Fourier basis instead.
        positions = np.arange(sites, dtype=float)
        vectors_in_order: list[np.ndarray] = [
            np.ones(sites, dtype=float) / math.sqrt(sites)
        ]
        wave_numbers: list[int] = [0]
        for wave_number in range(1, (sites + 1) // 2):
            angle = 2.0 * math.pi * wave_number * positions / sites
            normalization = math.sqrt(2.0 / sites)
            vectors_in_order.extend(
                [normalization * np.cos(angle), normalization * np.sin(angle)]
            )
            wave_numbers.extend([wave_number, wave_number])
        if sites % 2 == 0:
            vectors_in_order.append(((-1.0) ** positions) / math.sqrt(sites))
            wave_numbers.append(sites // 2)
        vectors = np.column_stack(vectors_in_order)
        eigenvalues = np.asarray(
            [
                spec.mass**2
                + 4.0
                * gradient_scale
                * math.sin(math.pi * wave_number / sites) ** 2
                for wave_number in wave_numbers
            ],
            dtype=float,
        )
        if float(np.min(eigenvalues)) <= 0.0:
            raise ValueError("field stiffness must be positive definite")
        return cls(
            spec=spec,
            stiffness=stiffness,
            frequencies=np.sqrt(eigenvalues),
            mode_vectors=vectors,
        )

    @property
    def phase_space_dimension(self) -> int:
        return 2 * self.spec.sites

    @property
    def symplectic_form(self) -> np.ndarray:
        identity = np.eye(self.spec.sites)
        zero = np.zeros_like(identity)
        return np.block([[zero, identity], [-identity, zero]])

    def analytic_periodic_frequencies(self) -> np.ndarray:
        """Sorted lattice dispersion values, independent of eigenvector gauge."""

        momenta = 2.0 * math.pi * np.arange(self.spec.sites) / self.spec.sites
        values = np.sqrt(
            self.spec.mass**2
            + 4.0
            * (self.spec.propagation_speed / self.spec.lattice_spacing) ** 2
            * np.sin(0.5 * momenta) ** 2
        )
        return np.sort(values)


__all__ = ["ScalarFieldModel", "ScalarFieldSpec"]
