"""Five-route benchmark for QMW's four-qubit Floquet Ising Hamiltonian.

The QMW NumPy model remains authoritative. Qiskit supplies independent exact,
product-formula, and noisy execution routes over the same Hamiltonian terms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import HamiltonianGate, PauliEvolutionGate
from qiskit.quantum_info import DensityMatrix, SparsePauliOp, Statevector
from qiskit.synthesis import LieTrotter, SuzukiTrotter

from ..models import QuantumMaterialFrame


@dataclass(frozen=True)
class RouteTrajectory:
    route: str
    frames: tuple[QuantumMaterialFrame, ...]
    density_matrices: np.ndarray = field(repr=False)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def magnetization_z(self) -> np.ndarray:
        return np.asarray(
            [frame.expectations["magnetization_z"] for frame in self.frames],
            dtype=float,
        )

    @property
    def return_probability(self) -> np.ndarray:
        return np.asarray(
            [frame.expectations["return_probability"] for frame in self.frames],
            dtype=float,
        )


@dataclass(frozen=True)
class FloquetComparison:
    routes: Mapping[str, RouteTrajectory]
    summary: Mapping[str, Mapping[str, float]]
    deferred_routes: tuple[str, ...] = ("ibm_runtime_v2",)

    def as_dict(self) -> dict[str, Any]:
        return {
            "routes": {
                name: {
                    "metadata": dict(route.metadata),
                    "frames": [frame.as_dict() for frame in route.frames],
                }
                for name, route in self.routes.items()
            },
            "summary": {name: dict(values) for name, values in self.summary.items()},
            "deferred_routes": list(self.deferred_routes),
        }


def noncommuting_benchmark_model():
    """Return the existing QMW model with its transverse-field knobs engaged."""
    try:
        from qmw_temporal_crystal16_v1.qmw_floquet_time_crystal16_v1 import (
            FloquetIsingConfig,
            FloquetTimeCrystal16,
        )
    except ModuleNotFoundError as exc:
        # In the durable checkout this bridge and the temporal model are sibling
        # directories. Make that source-tree relationship explicit while still
        # allowing ordinary installed-package imports to win.
        repository_root = Path(__file__).resolve().parents[3]
        temporal_package = repository_root / "qmw_temporal_crystal16_v1"
        if not temporal_package.is_dir():
            raise ModuleNotFoundError(
                "qmw_temporal_crystal16_v1 must be installed or be a sibling "
                "of qmw_qiskit_bridge_v1"
            ) from exc
        sys.path.insert(0, str(repository_root))
        from qmw_temporal_crystal16_v1.qmw_floquet_time_crystal16_v1 import (
            FloquetIsingConfig,
            FloquetTimeCrystal16,
        )

    return FloquetTimeCrystal16(
        FloquetIsingConfig(
            pulse_error=0.035,
            transverse_fields=(0.17, -0.11, 0.09, -0.05),
        )
    )


def _single_pauli(symbol: str, qubit: int, n_qubits: int = 4) -> str:
    letters = ["I"] * n_qubits
    letters[n_qubits - 1 - qubit] = symbol
    return "".join(letters)


def _two_pauli(symbol: str, left: int, right: int, n_qubits: int = 4) -> str:
    letters = ["I"] * n_qubits
    letters[n_qubits - 1 - left] = symbol
    letters[n_qubits - 1 - right] = symbol
    return "".join(letters)


def _model_operators(model) -> tuple[SparsePauliOp, SparsePauliOp, SparsePauliOp]:
    config = model.config
    bonds = [(q, q + 1) for q in range(3)]
    if config.periodic_boundary:
        bonds.append((3, 0))
    interaction_terms = [
        (_two_pauli("Z", left, right), float(strength))
        for strength, (left, right) in zip(config.interaction_strengths, bonds)
    ]
    interaction_terms.extend(
        (_single_pauli("Z", qubit), float(value))
        for qubit, value in enumerate(config.longitudinal_fields)
        if value
    )
    interaction_terms.extend(
        (_single_pauli("X", qubit), float(value))
        for qubit, value in enumerate(config.transverse_fields)
        if value
    )
    kick = SparsePauliOp.from_list(
        [(_single_pauli("X", qubit), 0.5) for qubit in range(4)]
    )
    interaction = SparsePauliOp.from_list(interaction_terms).simplify()
    magnetization = SparsePauliOp.from_list(
        [(_single_pauli("Z", qubit), 0.25) for qubit in range(4)]
    )
    if not np.allclose(interaction.to_matrix(), model.interaction_hamiltonian):
        raise RuntimeError("Qiskit interaction operator disagrees with QMW model")
    if not np.allclose(kick.to_matrix(), model.kick_hamiltonian):
        raise RuntimeError("Qiskit kick operator disagrees with QMW model")
    return interaction, kick, magnetization


def _frame(tick: int, rho: np.ndarray, magnetization: np.ndarray, route: str, **metadata) -> QuantumMaterialFrame:
    initial_probability = float(np.real(rho[0, 0]))
    mz = float(np.real(np.trace(rho @ magnetization)))
    purity = float(np.real(np.trace(rho @ rho)))
    return QuantumMaterialFrame(
        time=float(tick),
        expectations={
            "magnetization_z": mz,
            "return_probability": initial_probability,
            "purity": purity,
        },
        backend={"route": route, **metadata},
    )


def _qmw_dense(model, periods: int, magnetization: np.ndarray) -> RouteTrajectory:
    trajectory = model.run(periods)
    matrices = np.asarray(trajectory.density_matrices)
    frames = tuple(_frame(tick, rho, magnetization, "qmw_dense_exact") for tick, rho in enumerate(matrices))
    return RouteTrajectory(
        "qmw_dense_exact", frames, matrices,
        {"authority": True, "evolution": "Hermitian eigendecomposition"},
    )


def _qiskit_statevector(
    model, periods: int, interaction: SparsePauliOp, kick: SparsePauliOp, magnetization: np.ndarray
) -> RouteTrajectory:
    period = QuantumCircuit(4)
    period.append(HamiltonianGate(kick.to_matrix(), model.config.actual_kick_angle), range(4))
    period.append(HamiltonianGate(interaction.to_matrix(), model.config.interaction_time), range(4))
    state = Statevector.from_int(0, 2**4)
    matrices = []
    frames = []
    for tick in range(periods + 1):
        rho = np.asarray(DensityMatrix(state).data)
        matrices.append(rho)
        frames.append(_frame(tick, rho, magnetization, "qiskit_statevector_exact"))
        if tick < periods:
            state = state.evolve(period)
    return RouteTrajectory(
        "qiskit_statevector_exact", tuple(frames), np.asarray(matrices),
        {"authority": False, "evolution": "Qiskit HamiltonianGate"},
    )


def _trotter(
    model, periods: int, interaction: SparsePauliOp, kick: SparsePauliOp,
    magnetization: np.ndarray, *, order: int, reps: int,
) -> RouteTrajectory:
    period = _trotter_period_circuit(
        model, interaction, kick, order=order, reps=reps
    )
    state = Statevector.from_int(0, 2**4)
    matrices = []
    frames = []
    route = f"qiskit_trotter_order_{order}"
    for tick in range(periods + 1):
        rho = np.asarray(DensityMatrix(state).data)
        matrices.append(rho)
        frames.append(_frame(tick, rho, magnetization, route, order=order, reps=reps))
        if tick < periods:
            state = state.evolve(period)
    return RouteTrajectory(route, tuple(frames), np.asarray(matrices), {"order": order, "reps": reps})


def _trotter_period_circuit(
    model,
    interaction: SparsePauliOp,
    kick: SparsePauliOp,
    *,
    order: int,
    reps: int,
) -> QuantumCircuit:
    synthesis = LieTrotter(reps=reps, preserve_order=True) if order == 1 else SuzukiTrotter(order=order, reps=reps, preserve_order=True)
    period = QuantumCircuit(4)
    period.append(PauliEvolutionGate(kick, model.config.actual_kick_angle, synthesis=synthesis), range(4))
    period.append(PauliEvolutionGate(interaction, model.config.interaction_time, synthesis=synthesis), range(4))
    # Statevector can evaluate an undecomposed PauliEvolutionGate as the exact
    # exponential. Decompose explicitly so this route measures the requested
    # product formula rather than silently reproducing the exact route.
    period = period.decompose()
    return period


def _noise_model(single_qubit_error: float, two_qubit_error: float):
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    model = NoiseModel()
    model.add_all_qubit_quantum_error(depolarizing_error(single_qubit_error, 1), ["sx", "x"])
    model.add_all_qubit_quantum_error(depolarizing_error(two_qubit_error, 2), ["cx"])
    return model


def _aer_noisy(
    model, periods: int, interaction: SparsePauliOp, kick: SparsePauliOp,
    magnetization: np.ndarray, *, single_qubit_error: float, two_qubit_error: float, seed: int,
) -> RouteTrajectory:
    from qiskit_aer import AerSimulator

    period = _trotter_period_circuit(
        model, interaction, kick, order=2, reps=1
    )
    noise = _noise_model(single_qubit_error, two_qubit_error)
    simulator = AerSimulator(method="density_matrix", noise_model=noise)
    matrices = []
    frames = []
    for tick in range(periods + 1):
        circuit = QuantumCircuit(4)
        for _ in range(tick):
            circuit.compose(period, inplace=True)
        # Fix the compiled gate alphabet independently of the noise model so
        # zero-noise and noisy Aer routes execute the same circuit topology.
        compiled = transpile(
            circuit,
            basis_gates=["rz", "sx", "x", "cx"],
            optimization_level=0,
            seed_transpiler=seed,
        )
        compiled.save_density_matrix()
        rho = np.asarray(
            simulator.run(compiled, seed_simulator=seed).result().data(0)["density_matrix"],
            dtype=np.complex128,
        )
        matrices.append(rho)
        frames.append(
            _frame(
                tick, rho, magnetization, "aer_noisy",
                single_qubit_depolarizing_error=single_qubit_error,
                two_qubit_depolarizing_error=two_qubit_error,
            )
        )
    return RouteTrajectory(
        "aer_noisy", tuple(frames), np.asarray(matrices),
        {
            "noise": "controlled_depolarizing",
            "single_qubit_error": single_qubit_error,
            "two_qubit_error": two_qubit_error,
            "seed": seed,
        },
    )


def _trace_distance(left: np.ndarray, right: np.ndarray) -> float:
    delta = (left - right + (left - right).conj().T) * 0.5
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(delta))))


def compare_floquet_routes(
    *, model=None, periods: int = 16, trotter_reps: int = 1,
    single_qubit_error: float = 0.0015, two_qubit_error: float = 0.012, seed: int = 2718,
) -> FloquetComparison:
    if periods < 1:
        raise ValueError("periods must be positive")
    model = model or noncommuting_benchmark_model()
    interaction, kick, magnetization_op = _model_operators(model)
    magnetization = np.asarray(magnetization_op.to_matrix())
    route_list = [
        _qmw_dense(model, periods, magnetization),
        _qiskit_statevector(model, periods, interaction, kick, magnetization),
        _trotter(model, periods, interaction, kick, magnetization, order=1, reps=trotter_reps),
        _trotter(model, periods, interaction, kick, magnetization, order=2, reps=trotter_reps),
        _aer_noisy(
            model, periods, interaction, kick, magnetization,
            single_qubit_error=single_qubit_error, two_qubit_error=two_qubit_error, seed=seed,
        ),
    ]
    routes = {route.route: route for route in route_list}
    reference = routes["qmw_dense_exact"]
    summary = {}
    for name, route in routes.items():
        mz_delta = route.magnetization_z - reference.magnetization_z
        distances = np.asarray([
            _trace_distance(rho, exact)
            for rho, exact in zip(route.density_matrices, reference.density_matrices)
        ])
        summary[name] = {
            "magnetization_rmse": float(np.sqrt(np.mean(mz_delta**2))),
            "maximum_magnetization_error": float(np.max(np.abs(mz_delta))),
            "final_trace_distance": float(distances[-1]),
            "maximum_trace_distance": float(np.max(distances)),
        }
    return FloquetComparison(routes, summary)
