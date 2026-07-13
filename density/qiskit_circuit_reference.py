"""
qiskit_circuit_reference.py
===========================

Reference implementation for the Quantum Material Workstation circuit layer.

Purpose
-------
This module is deliberately *not* the real-time MLX density-matrix engine.
It provides an authoritative Qiskit interpretation of the gate grid so that
you can:

    1. Compile Max/QMW gate events into a QuantumCircuit.
    2. Produce a Qiskit reference DensityMatrix for purely unitary circuits.
    3. Execute explicit measurement and reset events with density-matrix
       semantics, including post-measurement collapse.
    4. Compare a live MLX/NumPy rho against the Qiskit reference rho.
    5. Keep one explicit qubit-ordering convention across Max, MLX, and Qiskit.

Qubit-ordering convention
--------------------------
QMW uses Qiskit's native subsystem convention:

    Max q0 -> Qiskit q0 -> least-significant computational-basis bit.

For four qubits, a basis index is interpreted as:

    |q3 q2 q1 q0>

Do not reverse matrices on import or export unless your existing MLX engine
currently uses the opposite convention. If it does, call
``reverse_qargs=True`` in ``compare_density_matrices`` while migrating.

Example gate event
------------------
{
    "step": 0,
    "gate": "H",
    "targets": [0],
}

Two-qubit gate:
{
    "step": 1,
    "gate": "CX",
    "controls": [0],
    "targets": [1],
}

Parameterized rotation:
{
    "step": 2,
    "gate": "RZ",
    "targets": [2],
    "theta": 0.6,
}

Measurement is *not* put into a QuantumCircuit for density-matrix reference
simulation. It is processed directly through DensityMatrix.measure(), because
it produces an outcome and a collapsed post-measurement density matrix:
{
    "step": 3,
    "gate": "MEASURE",
    "targets": [1],
}

Dependencies
------------
    pip install qiskit numpy

The module has no MLX dependency. Any array-like rho with shape
(2**n_qubits, 2**n_qubits) can be compared.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import DensityMatrix
except ImportError as exc:  # pragma: no cover - only exercised without Qiskit
    raise ImportError(
        "qiskit_circuit_reference.py requires Qiskit. "
        "Install it in the music environment with: pip install qiskit"
    ) from exc


GateEvent = Mapping[str, Any]


@dataclass(frozen=True)
class CircuitReferenceResult:
    """Complete result from one QMW circuit-grid evaluation."""

    circuit: QuantumCircuit
    density_matrix: DensityMatrix
    measurement_outcomes: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    @property
    def rho(self) -> np.ndarray:
        """Return the reference density matrix as a complex NumPy array."""
        return np.asarray(self.density_matrix.data, dtype=np.complex128)

    @property
    def probabilities(self) -> np.ndarray:
        """Return computational-basis probabilities in Qiskit's q3...q0 order."""
        return np.asarray(self.density_matrix.probabilities(), dtype=np.float64)

    @property
    def purity(self) -> float:
        """Return Tr(rho^2)."""
        return float(np.real_if_close(self.density_matrix.purity()))

    @property
    def is_valid(self) -> bool:
        """True when rho is trace-one and positive semidefinite."""
        return bool(self.density_matrix.is_valid())


class QiskitCircuitReference:
    """
    Qiskit reference compiler/evaluator for the QMW gate grid.

    The class recognizes discrete gate events. Continuous Hamiltonian
    evolution, feedback fields, Lindblad terms, and real-time OSC extraction
    remain in the MLX engine.

    Supported gates
    ---------------
    I, X, Y, Z, H, S, SDG, T, TDG, SX, SXDG,
    RX, RY, RZ, P,
    CX/CNOT, CY, CZ, CH, SWAP,
    CRX, CRY, CRZ, CP,
    CCX/TOFFOLI, CSWAP/FREDKIN,
    BARRIER, RESET, MEASURE.

    Event grammar
    -------------
    - ``gate``: gate name, case-insensitive.
    - ``targets``: a list of target qubits.
    - ``controls``: a list of control qubits, for controlled gates.
    - ``theta`` or ``angle``: radians for parameterized gates.
    - ``step``: optional ordering index. Input order resolves ties.
    - ``enabled``: optional boolean; False skips the event.
    """

    _ONE_QUBIT_NO_PARAM = {
        "I": "id",
        "ID": "id",
        "X": "x",
        "Y": "y",
        "Z": "z",
        "H": "h",
        "S": "s",
        "SDG": "sdg",
        "T": "t",
        "TDG": "tdg",
        "SX": "sx",
        "SXDG": "sxdg",
    }

    def __init__(self, n_qubits: int = 4, seed: int | None = None) -> None:
        if n_qubits < 1:
            raise ValueError("n_qubits must be at least 1.")
        self.n_qubits = int(n_qubits)
        self.seed = seed

    def compile(self, events: Sequence[GateEvent]) -> QuantumCircuit:
        """
        Compile only unitary/reset/barrier-compatible events to QuantumCircuit.

        MEASURE events are intentionally excluded because a Qiskit
        DensityMatrix measurement is stochastic and returns a collapsed state.
        Use ``evaluate`` to obtain that state.
        """
        circuit = QuantumCircuit(self.n_qubits, name="QMW_reference")
        for event in self._ordered_events(events):
            gate = self._gate_name(event)
            if gate in {"MEASURE", "M"}:
                continue
            self._append_event_to_circuit(circuit, event)
        return circuit

    def evaluate(
        self,
        events: Sequence[GateEvent],
        initial_rho: np.ndarray | DensityMatrix | None = None,
    ) -> CircuitReferenceResult:
        """
        Evaluate gate events from an optional initial density matrix.

        Unitary events are accumulated into short QuantumCircuit segments.
        Before a MEASURE or RESET event, the pending segment evolves the state.
        Measurement events return a sampled outcome and collapsed rho.

        A deterministic seed can be supplied when constructing this class.
        """
        state = self._coerce_initial_state(initial_rho)
        if self.seed is not None:
            state.seed(self.seed)

        circuit = QuantumCircuit(self.n_qubits, name="QMW_reference")
        pending = QuantumCircuit(self.n_qubits, name="QMW_pending")
        outcomes: list[dict[str, Any]] = []

        def flush_pending() -> None:
            nonlocal state, pending
            if len(pending.data):
                state = state.evolve(pending)
                pending = QuantumCircuit(self.n_qubits, name="QMW_pending")

        for event in self._ordered_events(events):
            gate = self._gate_name(event)

            if gate in {"MEASURE", "M"}:
                flush_pending()
                qargs = self._targets(event, expected_min=1)
                outcome, state = state.measure(qargs=qargs)
                outcomes.append(
                    {
                        "step": event.get("step"),
                        "qargs": tuple(qargs),
                        "outcome": outcome,
                    }
                )
                # A classical bit is added solely for readable circuit drawing.
                # The density-matrix state itself is already collapsed above.
                continue

            if gate == "RESET":
                flush_pending()
                qargs = self._targets(event, expected_min=1)
                state = state.reset(qargs=qargs)
                for qubit in qargs:
                    circuit.reset(qubit)
                continue

            self._append_event_to_circuit(pending, event)
            self._append_event_to_circuit(circuit, event)

        flush_pending()
        return CircuitReferenceResult(
            circuit=circuit,
            density_matrix=state,
            measurement_outcomes=tuple(outcomes),
        )

    def reference_density_matrix(
        self,
        events: Sequence[GateEvent],
        initial_rho: np.ndarray | DensityMatrix | None = None,
    ) -> DensityMatrix:
        """Convenience method returning only the final Qiskit DensityMatrix."""
        return self.evaluate(events, initial_rho=initial_rho).density_matrix

    def _coerce_initial_state(
        self,
        initial_rho: np.ndarray | DensityMatrix | None,
    ) -> DensityMatrix:
        if initial_rho is None:
            return DensityMatrix.from_int(0, dims=(2,) * self.n_qubits)

        if isinstance(initial_rho, DensityMatrix):
            state = initial_rho.copy()
        else:
            array = np.asarray(initial_rho, dtype=np.complex128)
            dimension = 2**self.n_qubits
            if array.shape != (dimension, dimension):
                raise ValueError(
                    f"initial_rho must have shape {(dimension, dimension)}, "
                    f"received {array.shape}."
                )
            state = DensityMatrix(array, dims=(2,) * self.n_qubits)

        if state.num_qubits != self.n_qubits:
            raise ValueError(
                f"initial_rho has {state.num_qubits} qubits, but this reference "
                f"uses {self.n_qubits}."
            )
        return state

    def _ordered_events(self, events: Sequence[GateEvent]) -> Iterable[GateEvent]:
        indexed = [
            (index, event)
            for index, event in enumerate(events)
            if bool(event.get("enabled", True))
        ]
        indexed.sort(key=lambda pair: (int(pair[1].get("step", pair[0])), pair[0]))
        return (event for _, event in indexed)

    def _append_event_to_circuit(
        self,
        circuit: QuantumCircuit,
        event: GateEvent,
    ) -> None:
        gate = self._gate_name(event)
        targets = self._targets(event, expected_min=1)

        if gate in self._ONE_QUBIT_NO_PARAM:
            self._require_count(gate, targets, 1)
            getattr(circuit, self._ONE_QUBIT_NO_PARAM[gate])(targets[0])
            return

        if gate in {"RX", "RY", "RZ", "P", "PHASE"}:
            self._require_count(gate, targets, 1)
            angle = self._angle(event)
            method = "p" if gate in {"P", "PHASE"} else gate.lower()
            getattr(circuit, method)(angle, targets[0])
            return

        if gate in {"CX", "CNOT", "CY", "CZ", "CH"}:
            controls = self._controls(event, expected_count=1)
            self._require_count(gate, targets, 1)
            method = "cx" if gate in {"CX", "CNOT"} else gate.lower()
            getattr(circuit, method)(controls[0], targets[0])
            return

        if gate == "SWAP":
            self._require_count(gate, targets, 2)
            circuit.swap(targets[0], targets[1])
            return

        if gate in {"CRX", "CRY", "CRZ", "CP"}:
            controls = self._controls(event, expected_count=1)
            self._require_count(gate, targets, 1)
            angle = self._angle(event)
            getattr(circuit, gate.lower())(angle, controls[0], targets[0])
            return

        if gate in {"CCX", "TOFFOLI"}:
            controls = self._controls(event, expected_count=2)
            self._require_count(gate, targets, 1)
            circuit.ccx(controls[0], controls[1], targets[0])
            return

        if gate in {"CSWAP", "FREDKIN"}:
            controls = self._controls(event, expected_count=1)
            self._require_count(gate, targets, 2)
            circuit.cswap(controls[0], targets[0], targets[1])
            return

        if gate == "BARRIER":
            circuit.barrier(*targets)
            return

        if gate == "RESET":
            for qubit in targets:
                circuit.reset(qubit)
            return

        raise ValueError(
            f"Unsupported QMW gate {gate!r}. "
            "Add it explicitly to QiskitCircuitReference before exposing it in Max."
        )

    def _gate_name(self, event: GateEvent) -> str:
        raw = event.get("gate", event.get("operation", ""))
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError(f"Gate event has no valid 'gate': {event!r}")
        return raw.strip().upper()

    def _targets(self, event: GateEvent, expected_min: int) -> list[int]:
        raw = event.get("targets", event.get("target"))
        if raw is None:
            raise ValueError(f"Gate {self._gate_name(event)} requires 'targets'.")
        targets = self._as_qubit_list(raw, "targets")
        if len(targets) < expected_min:
            raise ValueError(
                f"Gate {self._gate_name(event)} requires at least {expected_min} target(s)."
            )
        return targets

    def _controls(self, event: GateEvent, expected_count: int) -> list[int]:
        raw = event.get("controls", event.get("control"))
        if raw is None:
            raise ValueError(f"Gate {self._gate_name(event)} requires 'controls'.")
        controls = self._as_qubit_list(raw, "controls")
        if len(controls) != expected_count:
            raise ValueError(
                f"Gate {self._gate_name(event)} requires exactly {expected_count} "
                f"control(s), received {controls}."
            )
        return controls

    def _as_qubit_list(self, raw: Any, label: str) -> list[int]:
        values = [raw] if isinstance(raw, (int, np.integer)) else list(raw)
        qubits = [int(value) for value in values]
        if len(set(qubits)) != len(qubits):
            raise ValueError(f"{label} contains duplicate qubits: {qubits}")
        invalid = [q for q in qubits if q < 0 or q >= self.n_qubits]
        if invalid:
            raise ValueError(
                f"{label} contains invalid qubits {invalid}; valid range is "
                f"0..{self.n_qubits - 1}."
            )
        return qubits

    @staticmethod
    def _require_count(gate: str, qubits: Sequence[int], count: int) -> None:
        if len(qubits) != count:
            raise ValueError(
                f"Gate {gate} requires exactly {count} target(s), received {list(qubits)}."
            )

    @staticmethod
    def _angle(event: GateEvent) -> float:
        raw = event.get("theta", event.get("angle", event.get("parameter")))
        if raw is None:
            raise ValueError(
                f"Parameterized gate {event.get('gate')} requires theta/angle in radians."
            )
        return float(raw)


def compare_density_matrices(
    rho_live: Any,
    rho_reference: np.ndarray | DensityMatrix,
    *,
    reverse_qargs: bool = False,
    atol: float = 1e-8,
    rtol: float = 1e-5,
) -> dict[str, float | bool]:
    """
    Compare an MLX/NumPy density matrix against a Qiskit reference.

    Parameters
    ----------
    rho_live:
        Array-like live state. ``np.asarray`` is used, so MLX arrays work.
    rho_reference:
        A Qiskit DensityMatrix or a compatible complex array.
    reverse_qargs:
        Set True only when the live engine stores the opposite tensor-factor
        ordering from Qiskit. This reverses the Qiskit reference before
        comparison; it does not mutate either input.
    atol, rtol:
        Numerical tolerances for the allclose result.

    Returns
    -------
    Diagnostics suitable for console logs or OSC:
    max_abs_error, frobenius_error, trace_error, hermitian_error,
    live_is_valid, reference_is_valid, matrices_close.
    """
    live = np.asarray(rho_live, dtype=np.complex128)
    reference_state = (
        rho_reference.copy()
        if isinstance(rho_reference, DensityMatrix)
        else DensityMatrix(np.asarray(rho_reference, dtype=np.complex128))
    )
    if reverse_qargs:
        reference_state = reference_state.reverse_qargs()
    reference = np.asarray(reference_state.data, dtype=np.complex128)

    if live.shape != reference.shape:
        raise ValueError(
            f"Density-matrix shape mismatch: live={live.shape}, "
            f"reference={reference.shape}."
        )

    dimension = live.shape[0]
    live_state = DensityMatrix(live)
    delta = live - reference

    return {
        "max_abs_error": float(np.max(np.abs(delta))),
        "frobenius_error": float(np.linalg.norm(delta, ord="fro")),
        "trace_error": float(abs(np.trace(live) - np.trace(reference))),
        "hermitian_error": float(np.max(np.abs(live - live.conj().T))),
        "live_is_valid": bool(live_state.is_valid()),
        "reference_is_valid": bool(reference_state.is_valid()),
        "matrices_close": bool(np.allclose(live, reference, atol=atol, rtol=rtol)),
        "dimension": float(dimension),
    }


if __name__ == "__main__":
    # Bell-pair smoke test: H(q0) followed by CX(q0 -> q1).
    bridge = QiskitCircuitReference(n_qubits=4, seed=7)

    demo_events = [
        {"step": 0, "gate": "H", "targets": [0]},
        {"step": 1, "gate": "CX", "controls": [0], "targets": [1]},
        {"step": 2, "gate": "RZ", "targets": [2], "theta": 0.6},
    ]

    result = bridge.evaluate(demo_events)

    print(result.circuit.draw(output="text"))
    print("valid:", result.is_valid)
    print("purity:", result.purity)
    print("probabilities:", result.probabilities)
    print("comparison:", compare_density_matrices(result.rho, result.density_matrix))
