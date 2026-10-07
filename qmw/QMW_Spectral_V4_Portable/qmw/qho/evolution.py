"""Backend-independent closed- and open-system evolution."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm
from scipy.sparse import csr_matrix, eye as sparse_eye, kron
from scipy.sparse.linalg import expm_multiply

from .states import density_matrix


@dataclass(frozen=True)
class LindbladEnvironment:
    """Markovian environment rates in inverse model-time units.

    ``dephasing_rate`` multiplies ``D[N]``. ``damping_rate`` is the oscillator
    energy-relaxation rate, and ``bath_mean_n`` is the thermal bath occupation.
    Zero rates recover the exact closed-system evolution path.
    """

    dephasing_rate: float = 0.0
    damping_rate: float = 0.0
    bath_mean_n: float = 0.0

    def __post_init__(self) -> None:
        values = (self.dephasing_rate, self.damping_rate, self.bath_mean_n)
        if not np.isfinite(values).all() or any(value < 0.0 for value in values):
            raise ValueError(
                "Lindblad environment values must be finite and nonnegative"
            )

    @property
    def is_closed(self) -> bool:
        return self.dephasing_rate == 0.0 and self.damping_rate == 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "dephasing_rate": float(self.dephasing_rate),
            "damping_rate": float(self.damping_rate),
            "bath_mean_n": float(self.bath_mean_n),
        }


def unitary(hamiltonian: np.ndarray, time: float, *, hbar: float = 1.0) -> np.ndarray:
    operator = np.asarray(hamiltonian, dtype=np.complex128)
    if operator.ndim != 2 or operator.shape[0] != operator.shape[1]:
        raise ValueError("hamiltonian must be square")
    if not np.allclose(operator, operator.conj().T, atol=1e-10, rtol=0.0):
        raise ValueError("hamiltonian must be Hermitian")
    if not np.isfinite(time):
        raise ValueError("time must be finite")
    if not np.isfinite(hbar) or hbar <= 0.0:
        raise ValueError("hbar must be finite and positive")
    return expm((-1j * float(time) / float(hbar)) * operator)


def evolve_density(
    rho: np.ndarray,
    hamiltonian: np.ndarray,
    time: float,
    *,
    hbar: float = 1.0,
) -> np.ndarray:
    state = density_matrix(rho)
    if state.shape != np.asarray(hamiltonian).shape:
        raise ValueError("rho and hamiltonian dimensions must match")
    propagator = unitary(hamiltonian, time, hbar=hbar)
    evolved = propagator @ state @ propagator.conj().T
    return density_matrix(evolved)


def oscillator_collapse_operators(
    annihilation: np.ndarray,
    number: np.ndarray,
    environment: LindbladEnvironment,
) -> tuple[np.ndarray, ...]:
    """Construct finite-basis collapse operators for one bosonic mode."""

    a = np.asarray(annihilation, dtype=np.complex128)
    n = np.asarray(number, dtype=np.complex128)
    if a.shape != n.shape or a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError(
            "oscillator operators must be equally sized square matrices"
        )
    collapse: list[np.ndarray] = []
    if environment.dephasing_rate > 0.0:
        collapse.append(np.sqrt(environment.dephasing_rate) * n)
    if environment.damping_rate > 0.0:
        kappa = environment.damping_rate
        bath = environment.bath_mean_n
        collapse.append(np.sqrt(kappa * (bath + 1.0)) * a)
        if bath > 0.0:
            collapse.append(np.sqrt(kappa * bath) * a.conj().T)
    return tuple(collapse)


def evolve_lindblad(
    rho: np.ndarray,
    hamiltonian: np.ndarray,
    time: float,
    collapse_operators: tuple[np.ndarray, ...] | list[np.ndarray],
    *,
    hbar: float = 1.0,
) -> np.ndarray:
    """Evolve ``rho`` under a time-independent GKSL/Lindblad generator."""

    state = density_matrix(rho)
    operator = np.asarray(hamiltonian, dtype=np.complex128)
    if state.shape != operator.shape:
        raise ValueError("rho and hamiltonian dimensions must match")
    if not np.isfinite(time) or time < 0.0:
        raise ValueError("open-system time must be finite and nonnegative")
    if not np.isfinite(hbar) or hbar <= 0.0:
        raise ValueError("hbar must be finite and positive")
    if time == 0.0:
        return state

    dimension = state.shape[0]
    identity = sparse_eye(dimension, dtype=np.complex128, format="csr")
    h_sparse = csr_matrix(operator)
    # Column-major vectorization: vec(A rho B) = (B^T x A) vec(rho).
    generator = (-1j / float(hbar)) * (
        kron(identity, h_sparse, format="csr")
        - kron(h_sparse.T, identity, format="csr")
    )
    for collapse in collapse_operators:
        value = np.asarray(collapse, dtype=np.complex128)
        if value.shape != state.shape or not np.isfinite(value).all():
            raise ValueError("collapse operators must be finite and match rho")
        c_sparse = csr_matrix(value)
        cdag_c = c_sparse.getH() @ c_sparse
        generator = generator + kron(c_sparse.conjugate(), c_sparse, format="csr")
        generator = generator - 0.5 * kron(identity, cdag_c, format="csr")
        generator = generator - 0.5 * kron(cdag_c.T, identity, format="csr")

    vector = state.reshape(dimension * dimension, order="F")
    evolved = expm_multiply(generator * float(time), vector).reshape(
        state.shape, order="F"
    )
    evolved = 0.5 * (evolved + evolved.conj().T)
    return density_matrix(evolved, atol=1e-9)


__all__ = [
    "LindbladEnvironment",
    "evolve_density",
    "evolve_lindblad",
    "oscillator_collapse_operators",
    "unitary",
]
