"""Exact frozen-generator Lindblad evolution, without state correction."""
from __future__ import annotations
from collections import OrderedDict
from collections.abc import Sequence
import numpy as np
from scipy.linalg import expm
from ...core.domain import Domain
from ...core.frame import StateData, ObservableData, Diagnostics
from ...core.spec import ModuleSpec, PortSpec, ParameterSpec
from .hamiltonian import HamiltonianBuilder, PAULI, tensor_operator


class LindbladModel:
    model_id = "finite-dimensional-lindblad"

    def __init__(self, hamiltonian: np.ndarray | None = None,
                 collapse_operators: Sequence[np.ndarray] | None = None,
                 hbar: float = 1.0, builder: HamiltonianBuilder | None = None):
        if not np.isfinite(hbar) or hbar <= 0:
            raise ValueError("hbar must be finite and positive")
        if hamiltonian is not None and builder is not None:
            raise ValueError("Supply a frozen Hamiltonian or a builder, not both")
        self.hbar = float(hbar)
        if hamiltonian is None:
            self.builder = builder or HamiltonianBuilder(4, {
                "h_x0": .35, "h_z0": -.5, "h_z1": -.5,
                "h_z2": -.5, "h_z3": -.5,
            })
            self.dimension = self.builder.dimension
            self._fixed_hamiltonian = None
        else:
            self.builder = None
            self._fixed_hamiltonian = np.asarray(hamiltonian, dtype=complex).copy()
            self.dimension = self._fixed_hamiltonian.shape[0] if self._fixed_hamiltonian.ndim == 2 else 0
            self._check_matrix(self._fixed_hamiltonian, "Hamiltonian", hermitian=True)
        self.domain = Domain.basis(self.dimension)
        self.n_qubits = int(np.log2(self.dimension)) if self.dimension > 0 else 0
        if 2**self.n_qubits != self.dimension:
            self.n_qubits = None
        self._fixed_collapses = None if collapse_operators is None else tuple(
            np.asarray(operator, dtype=complex).copy() for operator in collapse_operators
        )
        if self._fixed_collapses is not None:
            for collapse in self._fixed_collapses:
                self._check_matrix(collapse, "Collapse operator")
        lower = np.array([[0, 1], [0, 0]], dtype=complex)
        self._local_lowering = tuple(
            tensor_operator(self.n_qubits, {index: lower})
            for index in range(self.n_qubits or 0)
        )
        self._local_z = tuple(
            tensor_operator(self.n_qubits, {index: PAULI["z"]})
            for index in range(self.n_qubits or 0)
        )
        self._channel_key = None
        self._channel_values: tuple[np.ndarray, ...] = ()
        # Dense exponentials are expensive at d=16; reuse the exact frozen map.
        # Cache bounded to eight maps; controls/dt/matrices are all in the key.
        self._propagators: OrderedDict[tuple, np.ndarray] = OrderedDict()

    def _check_matrix(self, matrix: np.ndarray, label: str, hermitian=False):
        if self.dimension < 1 or matrix.shape != (self.dimension, self.dimension):
            raise ValueError(f"{label} must be a nonempty square dimension-matched matrix")
        if not np.isfinite(matrix).all():
            raise ValueError(f"{label} must be finite")
        if hermitian and not np.allclose(matrix, matrix.conj().T, atol=1e-12, rtol=1e-12):
            raise ValueError(f"{label} must be Hermitian")

    def hamiltonian(self, controls=None) -> np.ndarray:
        return self.builder.build(controls) if self.builder is not None else self._fixed_hamiltonian.copy()

    def collapse_operators(self, controls=None) -> tuple[np.ndarray, ...]:
        if self._fixed_collapses is not None:
            return self._fixed_collapses
        controls = controls or {}
        damping = float(controls.get("damping_rate", .05 if self.builder is not None else 0.0))
        dephasing = float(controls.get("dephasing_rate", .02 if self.builder is not None else 0.0))
        if not np.isfinite([damping, dephasing]).all() or min(damping, dephasing) < 0:
            raise ValueError("Lindblad rates must be finite and nonnegative")
        if self.n_qubits is None:
            if damping or dephasing:
                raise ValueError("Built-in damping/dephasing requires a power-of-two dimension")
            return ()
        channel_key = (damping, dephasing)
        if channel_key == self._channel_key:
            return self._channel_values
        collapses = []
        for index in range(self.n_qubits):
            if damping:
                collapses.append(np.sqrt(damping) * self._local_lowering[index])
            if dephasing:
                # This convention makes an isolated off-diagonal element decay at gamma_phi.
                collapses.append(np.sqrt(dephasing/2) * self._local_z[index])
        self._channel_key, self._channel_values = channel_key, tuple(collapses)
        return self._channel_values

    def initialize(self, controls=None) -> StateData:
        controls = controls or {}
        initial = str(controls.get("init", "zero"))
        vector = np.zeros(self.dimension, dtype=complex)
        if initial == "zero":
            vector[0] = 1.0
        elif initial == "plus":
            vector[:] = 1/np.sqrt(self.dimension)
        elif initial == "yplus" and self.n_qubits is not None:
            vector = np.ones(1, dtype=complex)
            for _ in range(self.n_qubits):
                vector = np.kron(vector, np.array([1, 1j])/np.sqrt(2))
        elif initial == "ghz":
            if self.dimension < 2:
                raise ValueError("GHZ initialization needs at least two basis states")
            vector[0] = vector[-1] = 1/np.sqrt(2)
        elif initial == "bell_pairs" and self.n_qubits is not None and self.n_qubits % 2 == 0:
            vector = np.ones(1, dtype=complex)
            for _ in range(self.n_qubits//2):
                vector = np.kron(vector, np.array([1, 0, 0, 1])/np.sqrt(2))
        elif initial == "random":
            rng = np.random.default_rng(int(controls.get("seed", 0)))
            vector = rng.normal(size=self.dimension) + 1j*rng.normal(size=self.dimension)
            vector /= np.linalg.norm(vector)
        else:
            raise ValueError(f"Unsupported density-matrix initialization: {initial}")
        return StateData(rho=np.outer(vector, vector.conj()))

    def dissipator(self, rho: np.ndarray, controls=None) -> np.ndarray:
        result = np.zeros_like(rho, dtype=complex)
        for collapse in self.collapse_operators(controls):
            cc = collapse.conj().T @ collapse
            result += collapse @ rho @ collapse.conj().T - .5*(cc @ rho + rho @ cc)
        return result

    def derivative(self, rho: np.ndarray, controls=None) -> np.ndarray:
        hamiltonian = self.hamiltonian(controls)
        return -1j/self.hbar*(hamiltonian @ rho - rho @ hamiltonian) + self.dissipator(rho, controls)

    def liouvillian(self, controls=None) -> np.ndarray:
        """Column-major vec convention: vec(A rho B) = (B.T tensor A) vec(rho)."""
        hamiltonian = self.hamiltonian(controls)
        identity = np.eye(self.dimension, dtype=complex)
        generator = -1j/self.hbar*(np.kron(identity, hamiltonian) - np.kron(hamiltonian.T, identity))
        for collapse in self.collapse_operators(controls):
            cc = collapse.conj().T @ collapse
            generator += np.kron(collapse.conj(), collapse)
            generator -= .5*(np.kron(identity, cc) + np.kron(cc.T, identity))
        return generator

    def step(self, state: StateData, controls=None, dt: float = .001) -> StateData:
        state.validate(self.domain)
        if state.rho is None:
            raise ValueError("Lindblad requires a density matrix")
        if isinstance(dt, (bool, np.bool_)) or not np.isfinite(dt) or dt < 0:
            raise ValueError("dt must be finite and nonnegative")
        if dt == 0:
            return StateData(rho=state.rho.copy())
        hamiltonian = self.hamiltonian(controls)
        collapses = self.collapse_operators(controls)
        if not collapses:
            unitary = expm(-1j*hamiltonian*dt/self.hbar)
            return StateData(rho=unitary @ state.rho @ unitary.conj().T)
        key = (float(dt), hamiltonian.tobytes(), tuple(c.tobytes() for c in collapses))
        if key not in self._propagators:
            self._propagators[key] = expm(dt*self.liouvillian(controls))
            if len(self._propagators) > 8:
                self._propagators.popitem(last=False)
        propagator = self._propagators[key]
        self._propagators.move_to_end(key)
        rho = (propagator @ state.rho.reshape(-1, order="F")).reshape(
            (self.dimension, self.dimension), order="F"
        )
        # No symmetrization, trace normalization, or eigenvalue clipping.
        return StateData(rho=rho)

    def compute_observables(self, state: StateData, controls=None) -> ObservableData:
        state.validate(self.domain)
        rho = state.rho
        if rho is None:
            raise ValueError("Lindblad requires a density matrix")
        hamiltonian = self.hamiltonian(controls)
        dissipative_rate = self.dissipator(rho, controls)
        rho_rate = -1j/self.hbar*(hamiltonian @ rho - rho @ hamiltonian) + dissipative_rate
        power = float(np.trace(hamiltonian @ dissipative_rate).real)
        expectations = {}
        if self.builder is not None:
            expectations = {
                name: float(np.trace(rho @ operator).real)
                for name, operator in self.builder.terms.items()
            }
        return ObservableData(
            probability_density=np.diag(rho).real.copy(),
            probability_rate=np.diag(rho_rate).real.copy(),
            total_energy=float(np.trace(rho @ hamiltonian).real),
            norm=float(np.trace(rho).real), purity=float(np.trace(rho @ rho).real),
            source_power=power, expectations=expectations,
        )

    def environment_energy_step(self, previous: StateData, current: StateData, controls=None) -> float:
        """Energy received by the system from its environment, frozen H only.

        Tr[H(rho_next-rho_old)] is exact for this frozen step because the unitary
        term does no work. A control quench must be accounted separately.
        """
        hamiltonian = self.hamiltonian(controls)
        return float(np.trace(hamiltonian @ (current.rho - previous.rho)).real)

    def diagnostics(self, state: StateData) -> Diagnostics:
        state.validate(self.domain)
        rho = state.rho
        if rho is None:
            raise ValueError("Lindblad requires a density matrix")
        hermiticity = float(np.linalg.norm(rho-rho.conj().T, ord="fro"))
        # Hermitian part is used only to diagnose; the stored state is not altered.
        minimum = float(np.linalg.eigvalsh(.5*(rho+rho.conj().T)).min())
        return Diagnostics(
            trace_error=float(abs(np.trace(rho)-1)),
            hermiticity_error=hermiticity,
            positivity_error=max(0.0, -minimum),
            notes=["Exact frozen Liouvillian; initial density matrix validity remains observable."],
        )

    def module_specs(self) -> tuple[ModuleSpec, ...]:
        parameters = list(self.builder.parameter_specs() if self.builder is not None else ())
        parameters += [
            ParameterSpec("damping_rate", "Basis-state amplitude damping", .05, 0, 2,
                          "1 / scaled time", "C_i=sqrt(gamma) |0><1| on qubit i"),
            ParameterSpec("dephasing_rate", "Coherence decay", .02, 0, 2,
                          "1 / scaled time", "C_i=sqrt(gamma_phi/2) Z_i"),
        ]
        return (ModuleSpec(
            "lindblad", "Density-matrix evolution",
            r"\dot\rho=-\frac{i}{\hbar}[H,\rho]+\sum_k(C_k\rho C_k^\dagger-\frac12\{C_k^\dagger C_k,\rho\})",
            "rho_dot = -i[H,rho]/hbar + sum(C rho C† - {C†C,rho}/2)",
            inputs=(PortSpec("rho", "density matrix", "dimensionless", "basis_index"),),
            outputs=(PortSpec("rho", "evolved density matrix", "dimensionless", "basis_index"),
                     PortSpec("source_power", "environment-to-system power", "scaled energy/time", "scalar")),
            parameters=tuple(parameters),
            description="Exact exponential for constant controls within each step; H has energy units.",
            destinations=("basis populations", "modal projection", "conservation diagnostics"),
            assumptions=("Finite-dimensional Markovian GKSL model.",
                         "Control variation is piecewise constant; no continuous driving interpolation.",
                         "Basis damping need not thermalize the selected Hamiltonian.",
                         "First d=16 exponential is dense and may miss real-time deadlines; cached maps thereafter."),
        ),)
