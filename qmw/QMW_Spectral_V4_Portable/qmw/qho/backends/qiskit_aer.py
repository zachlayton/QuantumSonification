"""Exact Aer realization of the finite boson-to-qubit encoding."""

from __future__ import annotations

import math

import numpy as np

from ..model import OscillatorModel, OscillatorSpec
from ..observables import frame_from_density
from ..schema import OscillatorFrame
from ..states import density_matrix


def required_qubits(dimension: int) -> int:
    qubits = int(round(math.log2(dimension)))
    if 2**qubits != dimension:
        raise ValueError("binary QHO backends require a power-of-two dimension")
    return qubits


class QiskitAerEncodedBackend:
    """Aer density-matrix simulator using |n> <-> |b...b0>, q0 least-significant."""

    def __init__(self, spec: OscillatorSpec | None = None, *, seed: int = 1729) -> None:
        try:
            from qiskit_aer import AerSimulator
        except ImportError as exc:
            raise ImportError("QiskitAerEncodedBackend requires qiskit-aer") from exc
        self.model = OscillatorModel.from_spec(spec)
        self.num_qubits = required_qubits(self.model.spec.dimension)
        self.seed = int(seed)
        self.simulator = AerSimulator(method="density_matrix")

    def run(
        self,
        state: np.ndarray,
        *,
        time: float = 0.0,
        include_rho: bool = False,
        include_wigner: bool = False,
    ) -> OscillatorFrame:
        from qiskit import QuantumCircuit, transpile

        rho = density_matrix(state)
        expected_shape = (self.model.spec.dimension, self.model.spec.dimension)
        if rho.shape != expected_shape:
            raise ValueError("state dimension does not match oscillator model")
        circuit = QuantumCircuit(self.num_qubits)
        circuit.set_density_matrix(rho)
        # Rz(theta) gives relative |1>/<0> phase exp(i theta).  Choosing
        # theta=-omega*2**j*t implements exp(-i omega n t), up to global phase.
        for qubit in range(self.num_qubits):
            circuit.rz(-self.model.spec.omega * (2**qubit) * float(time), qubit)
        circuit.save_density_matrix()
        compiled = transpile(circuit, self.simulator, optimization_level=0)
        result = self.simulator.run(compiled, seed_simulator=self.seed).result()
        evolved = np.asarray(result.data(0)["density_matrix"], dtype=np.complex128)
        return frame_from_density(
            evolved,
            self.model,
            time=time,
            backend="qiskit_aer_binary_encoded",
            backend_metadata={
                "authoritative": False,
                "simulator": "AerSimulator(method=density_matrix)",
                "encoding": "finite_boson_to_qubit_binary",
                "basis_order": f"|q{self.num_qubits - 1}...q0>",
                "integer_basis_index": "+".join(
                    f"{2**q}*q{q}" for q in range(self.num_qubits)
                ),
                "q0_is_lsb": True,
                "physical_qubit_oscillator_claim": False,
            },
            include_rho=include_rho,
            include_wigner=include_wigner,
        )


__all__ = ["QiskitAerEncodedBackend", "required_qubits"]
