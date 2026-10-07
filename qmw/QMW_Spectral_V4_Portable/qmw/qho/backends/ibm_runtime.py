"""IBM Runtime V2 primitive adapter for the finite binary encoding.

IBM-specific imports are deliberately isolated in this module.  Hardware is a
measurement backend, not the authority for the canonical bosonic state.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from ..model import OscillatorModel, OscillatorSpec
from ..schema import OscillatorFrame
from ..states import density_matrix
from .qiskit_aer import required_qubits


class IBMRuntimeEncodedBackend:
    """Run pure encoded states with Runtime SamplerV2 and EstimatorV2.

    V1 intentionally rejects mixed density matrices because preparing a mixed
    state on hardware requires an explicit ensemble or purification protocol.
    """

    def __init__(
        self,
        spec: OscillatorSpec | None = None,
        *,
        backend: Any | None = None,
        service: Any | None = None,
        backend_name: str | None = None,
        shots: int = 4096,
        optimization_level: int = 1,
        require_cross_backend_validation: bool = True,
        validation_atol: float = 1e-9,
        sampler_options: Mapping[str, Any] | None = None,
        estimator_options: Mapping[str, Any] | None = None,
    ) -> None:
        if shots < 1:
            raise ValueError("shots must be positive")
        self.model = OscillatorModel.from_spec(spec)
        self.num_qubits = required_qubits(self.model.spec.dimension)
        self.shots = int(shots)
        self.optimization_level = int(optimization_level)
        self.require_cross_backend_validation = bool(require_cross_backend_validation)
        if not np.isfinite(validation_atol) or validation_atol <= 0.0:
            raise ValueError("validation_atol must be finite and positive")
        self.validation_atol = float(validation_atol)
        self.sampler_options = dict(sampler_options or {})
        self.estimator_options = dict(estimator_options or {})
        if backend is None:
            try:
                from qiskit_ibm_runtime import QiskitRuntimeService
            except ImportError as exc:
                raise ImportError(
                    "IBMRuntimeEncodedBackend requires qiskit-ibm-runtime"
                ) from exc
            runtime_service = service or QiskitRuntimeService()
            backend = (
                runtime_service.backend(backend_name)
                if backend_name
                else runtime_service.least_busy(operational=True, simulator=False)
            )
        self.backend = backend

    @staticmethod
    def _pure_statevector(state: np.ndarray, *, atol: float = 1e-9) -> np.ndarray:
        rho = density_matrix(state)
        eigenvalues, eigenvectors = np.linalg.eigh(rho)
        index = int(np.argmax(eigenvalues))
        if not np.isclose(eigenvalues[index], 1.0, atol=atol, rtol=0.0):
            raise ValueError(
                "IBM Runtime v1 accepts only pure states; use an explicit ensemble "
                "or purification protocol for mixed states"
            )
        ket = eigenvectors[:, index]
        pivot = int(np.argmax(np.abs(ket)))
        if abs(ket[pivot]) > 0.0:
            ket *= np.exp(-1j * np.angle(ket[pivot]))
        return ket

    def _circuit(self, state: np.ndarray, time: float):
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import StatePreparation

        ket = self._pure_statevector(state)
        if ket.size != self.model.spec.dimension:
            raise ValueError("state dimension does not match oscillator model")
        circuit = QuantumCircuit(self.num_qubits)
        circuit.append(StatePreparation(ket), range(self.num_qubits))
        for qubit in range(self.num_qubits):
            circuit.rz(-self.model.spec.omega * (2**qubit) * float(time), qubit)
        return circuit

    def run(
        self,
        state: np.ndarray,
        *,
        time: float = 0.0,
        include_rho: bool = False,
        include_wigner: bool = False,
    ) -> OscillatorFrame:
        if include_rho or include_wigner:
            raise ValueError("IBM hardware does not return rho or a Wigner grid")
        from qiskit.quantum_info import Operator, SparsePauliOp
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import EstimatorV2, SamplerV2

        circuit = self._circuit(state, time)
        validation_summary: dict[str, float | bool] | None = None
        if self.require_cross_backend_validation:
            from ..validation import validate_reference_against_aer

            validation = validate_reference_against_aer(
                state,
                spec=self.model.spec,
                time=time,
                atol=self.validation_atol,
            )
            validation_summary = validation.summary()
            if not validation.passed:
                raise RuntimeError(
                    "reference/Aer cross-backend validation failed; hardware jobs "
                    "were not submitted"
                )
        measured = circuit.copy()
        measured.measure_all()
        pass_manager = generate_preset_pass_manager(
            backend=self.backend,
            optimization_level=self.optimization_level,
        )
        isa_circuit = pass_manager.run(circuit)
        isa_measured = pass_manager.run(measured)
        ops = self.model.operators
        dense_observables = [
            ops.number,
            ops.hamiltonian,
            ops.x,
            ops.p,
            ops.x @ ops.x,
            ops.p @ ops.p,
        ]
        observables = [
            SparsePauliOp.from_operator(Operator(operator)).apply_layout(
                isa_circuit.layout
            )
            for operator in dense_observables
        ]
        sampler = SamplerV2(mode=self.backend, options=self.sampler_options)
        estimator = EstimatorV2(mode=self.backend, options=self.estimator_options)
        sampler_job = sampler.run([isa_measured], shots=self.shots)
        estimator_job = estimator.run([(isa_circuit, observables)])
        counts = sampler_job.result()[0].data.meas.get_counts()
        populations = np.zeros(self.model.spec.dimension, dtype=float)
        for bitstring, count in counts.items():
            index = int(str(bitstring).replace(" ", ""), 2)
            if index < populations.size:
                populations[index] += int(count) / self.shots
        values = np.asarray(estimator_job.result()[0].data.evs, dtype=float)
        mean_n, energy, mean_x, mean_p, x2, p2 = values.tolist()
        backend_name = getattr(self.backend, "name", None)
        if callable(backend_name):
            backend_name = backend_name()
        return OscillatorFrame(
            time=float(time),
            dimension=self.model.spec.dimension,
            populations=populations,
            mean_n=float(mean_n),
            mean_energy=float(energy),
            x=float(mean_x),
            p=float(mean_p),
            var_x=max(0.0, float(x2 - mean_x * mean_x)),
            var_p=max(0.0, float(p2 - mean_p * mean_p)),
            backend="ibm_runtime_binary_encoded",
            backend_metadata={
                "authoritative": False,
                "backend_name": str(backend_name),
                "encoding": "finite_boson_to_qubit_binary",
                "basis_order": f"|q{self.num_qubits - 1}...q0>",
                "q0_is_lsb": True,
                "shots": self.shots,
                "sampler_job_id": sampler_job.job_id(),
                "estimator_job_id": estimator_job.job_id(),
                "preflight_validation": validation_summary,
                "physical_qubit_oscillator_claim": False,
            },
        )


__all__ = ["IBMRuntimeEncodedBackend"]
