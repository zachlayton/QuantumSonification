"""Classical, source-free SU(2) Hamiltonian lattice dynamics in 2+1 dimensions.

Temporal gauge, periodic square lattice, dimensionless lattice/model time.
Links transport from the neighbor to their source; electric fields live at
the source. T_a = sigma_a/2, H = sum(E_a**2)/2 + beta*sum(1-Re tr(U_p)/2).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

PAULI = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]],
                  [[1, 0], [0, -1]]], dtype=np.complex128)
GENERATORS = PAULI / 2
IDENTITY = np.eye(2, dtype=np.complex128)


def dagger(value: np.ndarray) -> np.ndarray:
    return np.swapaxes(value.conj(), -1, -2)


def su2_exp(vector: np.ndarray) -> np.ndarray:
    """exp(i vector_a T_a), evaluated analytically including the zero limit."""
    vector = np.asarray(vector, dtype=float)
    length = np.linalg.norm(vector, axis=-1)
    algebra = np.einsum("...a,aij->...ij", vector, GENERATORS)
    return (np.cos(length / 2)[..., None, None] * IDENTITY
            + 1j * np.sinc(length / (2 * np.pi))[..., None, None] * algebra)


def algebra_vector(matrix: np.ndarray) -> np.ndarray:
    return 2 * np.einsum("aij,...ji->...a", GENERATORS, matrix).real


@dataclass(frozen=True)
class FieldSnapshot:
    time: float
    electric_energy: np.ndarray
    magnetic_energy: np.ndarray
    wilson_trace: np.ndarray
    total_energy: float
    relative_energy_drift: float
    gauss_error: float
    unitarity_error: float
    determinant_error: float

    @property
    def site_energy(self) -> np.ndarray:
        # A fixed source-site convention; its sum is the full Hamiltonian.
        return self.electric_energy + self.magnetic_energy


class SU2Lattice:
    def __init__(self, size: int = 4, *, beta: float = 1.0,
                 amplitude: float = 0.6, seed: int = 7) -> None:
        if isinstance(size, bool) or not isinstance(size, (int, np.integer)) or size < 2:
            raise ValueError("size must be an integer >= 2")
        if not math.isfinite(beta) or beta <= 0:
            raise ValueError("beta must be finite and positive")
        if not math.isfinite(amplitude) or amplitude < 0:
            raise ValueError("amplitude must be finite and nonnegative")
        self.size = int(size)
        self.beta = float(beta)
        rng = np.random.default_rng(seed)
        self.links = su2_exp(amplitude * rng.normal(size=(size, size, 2, 3)))
        # E=0 obeys source-free Gauss's law for any initial link configuration.
        self.electric = np.zeros((size, size, 2, 3), dtype=float)
        self.time = 0.0
        self.initial_energy = self.snapshot().total_energy

    def _plaquette_factors(self) -> tuple[np.ndarray, ...]:
        ux, uy = self.links[:, :, 0], self.links[:, :, 1]
        return (ux, np.roll(uy, -1, axis=0),
                dagger(np.roll(ux, -1, axis=1)), dagger(uy))

    def plaquettes(self) -> np.ndarray:
        a, b, c, d = self._plaquette_factors()
        return a @ b @ c @ d

    def magnetic_force(self) -> np.ndarray:
        """Exact negative left derivative of the Wilson plaquette potential."""
        factors = self._plaquette_factors()
        force = np.zeros_like(self.electric)
        # Each plaquette touches (direction, source offset, orientation).
        edges = ((0, (0, 0), 1), (1, (1, 0), 1),
                 (0, (0, 1), -1), (1, (0, 0), -1))
        for k, (direction, shift, sign) in enumerate(edges):
            before = np.broadcast_to(IDENTITY, factors[0].shape)
            after = before
            for item in factors[:k]:
                before = before @ item
            for item in factors[k + 1:]:
                after = after @ item
            loop = (factors[k] @ after @ before if sign > 0
                    else after @ before @ factors[k])
            derivative = np.einsum("aij,...ji->...a", GENERATORS, loop).imag
            contribution = -sign * self.beta * derivative / 2
            force[:, :, direction] += np.roll(contribution, shift, axis=(0, 1))
        return force

    def step(self, dt: float = 0.01, *, substeps: int = 1) -> FieldSnapshot:
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be finite and positive")
        if isinstance(substeps, bool) or not isinstance(substeps, (int, np.integer)) or substeps < 1:
            raise ValueError("substeps must be a positive integer")
        h = dt / substeps
        # Symmetric kick / group-exponential drift / kick. No projection or
        # damping is applied; each exact subflow preserves Gauss's law.
        for _ in range(substeps):
            self.electric += (h / 2) * self.magnetic_force()
            self.links = su2_exp(h * self.electric) @ self.links
            self.electric += (h / 2) * self.magnetic_force()
        self.time += dt
        return self.snapshot()

    def gauss_residual(self) -> np.ndarray:
        electric_matrix = np.einsum("...a,aij->...ij", self.electric, GENERATORS)
        residual = np.sum(electric_matrix, axis=2)
        for direction in range(2):
            incoming_u = np.roll(self.links[:, :, direction], 1, axis=direction)
            incoming_e = np.roll(electric_matrix[:, :, direction], 1, axis=direction)
            residual -= dagger(incoming_u) @ incoming_e @ incoming_u
        return algebra_vector(residual)

    def gauge_transform(self, gauges: np.ndarray) -> None:
        """Apply independent site rotations, leaving all observables invariant."""
        gauges = np.asarray(gauges, dtype=np.complex128)
        if gauges.shape != (self.size, self.size, 2, 2) or not np.all(np.isfinite(gauges)):
            raise ValueError("gauges must be finite site SU(2) matrices")
        if (not np.allclose(dagger(gauges) @ gauges, IDENTITY, atol=1e-10, rtol=0)
                or not np.allclose(np.linalg.det(gauges), 1, atol=1e-10, rtol=0)):
            raise ValueError("gauges must be unitary with determinant one")
        electric_matrix = np.einsum("...a,aij->...ij", self.electric, GENERATORS)
        for direction in range(2):
            neighbor = np.roll(gauges, -1, axis=direction)
            self.links[:, :, direction] = gauges @ self.links[:, :, direction] @ dagger(neighbor)
            self.electric[:, :, direction] = algebra_vector(
                gauges @ electric_matrix[:, :, direction] @ dagger(gauges))

    def covariant_laplacian(self) -> np.ndarray:
        """Hermitian PSD operator on two-component fundamental test fields.

        This is an analysis probe, not a dynamical matter field. Its 2*N*N
        eigenvalues are gauge invariant; eigenvector components are covariant.
        """
        n = self.size
        result = np.zeros((2 * n * n, 2 * n * n), dtype=np.complex128)
        for x in range(n):
            for y in range(n):
                source = 2 * (x * n + y)
                a = slice(source, source + 2)
                for direction, (dx, dy) in enumerate(((1, 0), (0, 1))):
                    target = 2 * (((x + dx) % n) * n + (y + dy) % n)
                    b = slice(target, target + 2)
                    u = self.links[x, y, direction]
                    result[a, a] += IDENTITY
                    result[b, b] += IDENTITY
                    result[a, b] -= u
                    result[b, a] -= dagger(u)
        return result

    def snapshot(self) -> FieldSnapshot:
        electric_energy = 0.5 * np.sum(self.electric ** 2, axis=(2, 3))
        wilson_trace = np.trace(self.plaquettes(), axis1=-2, axis2=-1).real / 2
        magnetic_energy = self.beta * np.maximum(1 - wilson_trace, 0)
        total = float(np.sum(electric_energy + magnetic_energy))
        initial = getattr(self, "initial_energy", total)
        return FieldSnapshot(
            time=self.time, electric_energy=electric_energy.copy(),
            magnetic_energy=magnetic_energy.copy(), wilson_trace=wilson_trace.copy(),
            total_energy=total,
            relative_energy_drift=(total - initial) / max(abs(initial), 1e-12),
            gauss_error=float(np.max(np.linalg.norm(self.gauss_residual(), axis=-1))),
            unitarity_error=float(np.max(np.abs(dagger(self.links) @ self.links - IDENTITY))),
            determinant_error=float(np.max(np.abs(np.linalg.det(self.links) - 1))),
        )
