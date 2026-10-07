"""Energy-valued Pauli terms; qubit 0 is the leftmost tensor factor."""
from __future__ import annotations
from collections.abc import Mapping
import numpy as np
from ...core.spec import ParameterSpec

PAULI = {
    "i": np.eye(2, dtype=complex),
    "x": np.array([[0, 1], [1, 0]], dtype=complex),
    "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def tensor_operator(n_qubits: int, factors: Mapping[int, np.ndarray]) -> np.ndarray:
    result = np.ones((1, 1), dtype=complex)
    for index in range(n_qubits):
        result = np.kron(result, factors.get(index, PAULI["i"]))
    return result


class HamiltonianBuilder:
    """H = sum h_ai sigma_ai + sum J_aij sigma_ai sigma_aj.

    h and J are energies in the declared scaled units. H/hbar is computed only
    when constructing the evolution generator. No Hz-to-energy conversion occurs.
    For four qubits the 30 coefficients cover 12 local and 18 pair terms.
    """

    def __init__(self, n_qubits: int = 4, defaults: Mapping[str, float] | None = None):
        if isinstance(n_qubits, bool) or not isinstance(n_qubits, int) or n_qubits < 1:
            raise ValueError("n_qubits must be a positive integer")
        self.n_qubits = n_qubits
        self.dimension = 2**n_qubits
        self.terms: dict[str, np.ndarray] = {}
        self.labels: dict[str, str] = {}
        for index in range(n_qubits):
            for axis in ("x", "y", "z"):
                name = f"h_{axis}{index}"
                self.terms[name] = tensor_operator(n_qubits, {index: PAULI[axis]})
                self.labels[name] = f"{axis.upper()}_{index}"
        for left in range(n_qubits):
            for right in range(left + 1, n_qubits):
                for axis in ("x", "y", "z"):
                    name = f"j_{axis}{axis}{left}{right}"
                    self.terms[name] = tensor_operator(
                        n_qubits, {left: PAULI[axis], right: PAULI[axis]}
                    )
                    self.labels[name] = f"{axis.upper()}_{left} {axis.upper()}_{right}"
        self.defaults = {name: 0.0 for name in self.terms}
        if defaults:
            if set(defaults) - set(self.terms):
                raise ValueError("Unknown Hamiltonian coefficient in defaults")
            self.defaults.update({name: float(value) for name, value in defaults.items()})
        if not np.isfinite(list(self.defaults.values())).all():
            raise ValueError("Hamiltonian coefficients must be finite")

    def coefficients(self, controls=None) -> dict[str, float]:
        controls = controls or {}
        coefficients = {
            name: float(controls.get(name, self.defaults[name])) for name in self.terms
        }
        if not np.isfinite(list(coefficients.values())).all():
            raise ValueError("Hamiltonian coefficients must be finite")
        return coefficients

    def build(self, controls=None) -> np.ndarray:
        coefficients = self.coefficients(controls)
        result = np.zeros((self.dimension, self.dimension), dtype=complex)
        for name, coefficient in coefficients.items():
            if coefficient:
                result += coefficient * self.terms[name]
        return result

    def term_contributions(self, controls=None) -> dict[str, dict]:
        return {
            name: {"operator": self.labels[name], "coefficient": value,
                   "unit": "scaled energy"}
            for name, value in self.coefficients(controls).items()
        }

    def parameter_specs(self) -> tuple[ParameterSpec, ...]:
        return tuple(
            ParameterSpec(name, self.labels[name], self.defaults[name], -4.0, 4.0,
                          "scaled energy", f"Energy coefficient of {self.labels[name]} in H")
            for name in self.terms
        )
