"""Small-system exact truncated normal-mode backend for QMW V3 validation."""

from __future__ import annotations

from dataclasses import replace
import math

import numpy as np

from qmw.qho.operators import annihilation_operator
from qmw.qho.states import coherent_state, density_matrix, vacuum_state

from ..gaussian import GaussianFieldState
from ..model import ScalarFieldModel, ScalarFieldSpec
from ..observables import frame_from_gaussian
from ..schema import ScalarFieldFrame


def _tensor_product(values: list[np.ndarray]) -> np.ndarray:
    result = np.asarray([1.0], dtype=np.complex128)
    for value in values:
        result = np.kron(result, value)
    return result


def exact_product_vacuum(sites: int, cutoff: int) -> np.ndarray:
    return _tensor_product([vacuum_state(cutoff) for _ in range(sites)])


def exact_product_coherent(amplitudes: np.ndarray, cutoff: int) -> np.ndarray:
    alpha = np.asarray(amplitudes, dtype=np.complex128)
    if alpha.ndim != 1:
        raise ValueError("coherent amplitudes must be a one-dimensional array")
    return _tensor_product([coherent_state(value, cutoff) for value in alpha])


def exact_single_particle_wavepacket(
    amplitudes: np.ndarray, cutoff: int
) -> np.ndarray:
    """One normalized particle distributed across normal modes."""

    values = np.asarray(amplitudes, dtype=np.complex128)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("wavepacket amplitudes must be a finite vector")
    norm = float(np.linalg.norm(values))
    if norm <= 1e-15:
        raise ValueError("wavepacket amplitudes must have nonzero norm")
    values = values / norm
    vacuum = vacuum_state(cutoff)
    one = np.zeros(cutoff, dtype=np.complex128)
    one[1] = 1.0
    terms = []
    for occupied_mode, amplitude in enumerate(values):
        factors = [
            one if mode == occupied_mode else vacuum
            for mode in range(len(values))
        ]
        terms.append(amplitude * _tensor_product(factors))
    return np.sum(terms, axis=0)


class ExactTruncatedScalarFieldBackend:
    """Dense reference backend in a product of truncated normal-mode bases.

    This backend is intentionally limited to small validation systems. Its
    tensor factors are field normal modes, not physical qubits and not lattice
    sites. The scalable Gaussian backend remains authoritative for larger free
    fields.
    """

    def __init__(
        self,
        spec: ScalarFieldSpec | None = None,
        *,
        cutoff: int = 6,
        maximum_dimension: int = 2048,
    ) -> None:
        self.model = ScalarFieldModel.from_spec(spec)
        self.cutoff = int(cutoff)
        if self.cutoff < 2:
            raise ValueError("exact mode cutoff must be at least two")
        self.dimension = self.cutoff ** self.model.spec.sites
        if self.dimension > int(maximum_dimension):
            raise ValueError(
                "exact truncated field exceeds maximum_dimension; use Gaussian backend"
            )
        self._build_operators()

    def _embed(self, local: np.ndarray, mode: int) -> np.ndarray:
        identity = np.eye(self.cutoff, dtype=np.complex128)
        return _tensor_product(
            [local if index == mode else identity for index in range(self.model.spec.sites)]
        )

    def _build_operators(self) -> None:
        sites = self.model.spec.sites
        hbar = self.model.spec.hbar
        local_a = annihilation_operator(self.cutoff)
        identity = np.eye(self.dimension, dtype=np.complex128)
        self.annihilation = tuple(self._embed(local_a, mode) for mode in range(sites))
        self.number = tuple(operator.conj().T @ operator for operator in self.annihilation)
        mode_phi = []
        mode_pi = []
        hamiltonian = np.zeros((self.dimension, self.dimension), dtype=np.complex128)
        for frequency, operator, number in zip(
            self.model.frequencies, self.annihilation, self.number
        ):
            creation = operator.conj().T
            mode_phi.append(math.sqrt(hbar / (2.0 * frequency)) * (operator + creation))
            mode_pi.append(
                -1j * math.sqrt(hbar * frequency / 2.0) * (operator - creation)
            )
            hamiltonian += hbar * frequency * (number + 0.5 * identity)
        self.field = tuple(
            sum(
                self.model.mode_vectors[site, mode] * mode_phi[mode]
                for mode in range(sites)
            )
            for site in range(sites)
        )
        self.momentum = tuple(
            sum(
                self.model.mode_vectors[site, mode] * mode_pi[mode]
                for mode in range(sites)
            )
            for site in range(sites)
        )
        self.hamiltonian = hamiltonian

    @staticmethod
    def _expectation(rho: np.ndarray, operator: np.ndarray) -> complex:
        return complex(np.trace(rho @ operator))

    def run(
        self,
        state: np.ndarray,
        *,
        time: float = 0.0,
        include_rho: bool = False,
    ) -> ScalarFieldFrame:
        rho = density_matrix(state)
        if rho.shape != (self.dimension, self.dimension):
            raise ValueError("state dimension does not match exact field backend")
        energies = np.real(np.diag(self.hamiltonian))
        phases = np.exp(-1j * energies * float(time) / self.model.spec.hbar)
        evolved = phases[:, None] * rho * phases.conj()[None, :]
        canonical = self.field + self.momentum
        means = np.asarray(
            [self._expectation(evolved, operator).real for operator in canonical]
        )
        covariance = np.empty((len(canonical), len(canonical)), dtype=float)
        for row, left in enumerate(canonical):
            for column, right in enumerate(canonical):
                symmetrized = 0.5 * (left @ right + right @ left)
                covariance[row, column] = (
                    self._expectation(evolved, symmetrized).real
                    - means[row] * means[column]
                )
        gaussian_moments = GaussianFieldState(means, covariance)
        frame = frame_from_gaussian(
            gaussian_moments,
            self.model,
            time=time,
            backend="exact_truncated_normal_modes",
            backend_metadata={
                "authoritative": True,
                "representation": "product_truncated_normal_mode_fock_basis",
                "cutoff_per_mode": self.cutoff,
                "hilbert_dimension": self.dimension,
                "tensor_factors_are_physical_qubits": False,
                "validation_scale_only": True,
            },
        )
        occupations = np.asarray(
            [self._expectation(evolved, number).real for number in self.number]
        )
        return replace(
            frame,
            mode_occupations=occupations,
            mean_energy=self._expectation(evolved, self.hamiltonian).real,
            purity=float(np.trace(evolved @ evolved).real),
            rho=evolved.copy() if include_rho else None,
        )


__all__ = [
    "ExactTruncatedScalarFieldBackend",
    "exact_product_coherent",
    "exact_product_vacuum",
    "exact_single_particle_wavepacket",
]
