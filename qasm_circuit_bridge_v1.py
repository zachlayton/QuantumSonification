#!/usr/bin/env python3
"""
qasm_circuit_bridge_v1.py

Bridge layer between the canonical qasm_gate_registry_v1.py and a
Composer-style circuit representation.

Purpose:
    - Store circuit operations in a neutral Python form.
    - Validate operations through qasm_gate_registry_v1.py.
    - Export OpenQASM 3 text.
    - Compile measurement/listener-basis macros:
        MZ, MX, MY, MN(theta, phi)
    - Prepare clean integration with Qiskit and the Max circuit programmer.

This file has no qiskit dependency yet.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, field
from typing import Any, List, Optional, Sequence, Union

from qasm_gate_registry_v1 import (
    GateSpec,
    MeasurementBasis,
    ParamValue,
    compile_measurement_macro,
    gate_menu_items,
    get_gate,
    measurement_basis_for_operation,
    parse_pi_param,
    qasm_gate_call,
    qasm_program_header,
    validate_gate_call,
)


QubitRef = Union[int, str]
ClassicalRef = Union[int, str]
QMW_REGISTER_BUSES = (
    "pitch",
    "energy",
    "spin",
    "parity",
    "ancilla",
    "hamiltonian",
    "notation",
)
DEFAULT_REGISTER_PROCESSES = {
    "pitch": "note_generation",
    "energy": "resonator_frequency_mapping",
    "spin": "spatial_trajectory_mapping",
    "parity": "rhythm_generation",
    "ancilla": "circuit_branching_control",
    "hamiltonian": "circuit_mutation_hamiltonian_evolution",
    "notation": "score_notation",
}
QMW_REGISTER_ALIASES = {
    "measurement_pitch": "pitch",
    "measurement_rhythm": "parity",
    "measurement_space": "spin",
    "measurement_spatial": "spin",
    "measurement_texture": "energy",
    "measurement_spectral": "energy",
    "measurement_timbre": "energy",
    "measurement_lighting": "spin",
    "measurement_control": "ancilla",
    "measurement_ancilla": "ancilla",
    "measurement_energy": "energy",
    "measurement_spin": "spin",
    "measurement_parity": "parity",
    "measurement_hamiltonian": "hamiltonian",
    "measurement_notation": "notation",
    "rhythm": "parity",
    "space": "spin",
    "spatial": "spin",
    "texture": "energy",
    "spectral": "energy",
    "timbre": "energy",
    "lighting": "spin",
    "visual": "spin",
    "control": "ancilla",
    "branch": "ancilla",
    "branching": "ancilla",
}


def normalize_register_bus_name(target_register: str) -> str:
    name = str(target_register).strip().lower()
    if name.startswith("/qmw/register/"):
        name = name.removeprefix("/qmw/register/")
    name = QMW_REGISTER_ALIASES.get(name, name)
    return name or "pitch"


def default_measurement_osc_route(target_register: str) -> str:
    route_name = normalize_register_bus_name(target_register)
    return f"/qmw/register/{route_name}"


@dataclass
class ClassicalRegisterSpec:
    """Named classical register partition for sampler/event routing."""

    name: str
    width: int
    role: str = "measurement"


@dataclass
class MeasurementRoute:
    """
    Musical routing metadata for a first-class measurement object.

    target_register:
        Named classical register/bus such as pitch, energy, spin,
        parity, ancilla, hamiltonian, or notation. Performance names
        like timbre, rhythm, spatial, and control are accepted at bridge
        boundaries and normalized for OSC routing.

    osc_route:
        Optional OSC subsystem route that should receive the event.

    persistence:
        single_shot, repeated, or averaged.

    shots:
        Suggested shot count for averaged/statistical measurement modes.

    register_bit:
        Bit index inside the named classical register, e.g. pitch[0].

    process:
        Musical/material process associated with this register.
    """

    target_register: str = "pitch"
    osc_route: str = "/qmw/register/pitch"
    persistence: str = "single_shot"
    shots: int = 1
    register_bit: Optional[int] = None
    process: str = "note_generation"

    def __post_init__(self) -> None:
        self.target_register = normalize_register_bus_name(self.target_register)
        if not self.osc_route:
            self.osc_route = default_measurement_osc_route(self.target_register)
        if self.register_bit is not None:
            self.register_bit = int(self.register_bit)
        self.shots = int(self.shots)
        if self.process == "note_generation":
            self.process = DEFAULT_REGISTER_PROCESSES.get(
                self.target_register,
                self.process,
            )


@dataclass
class CircuitOperation:
    """
    One neutral circuit/composer operation.

    name:
        Registry operation name or alias, e.g. h, cx, toffoli, MX.

    qubits:
        Qubit indices or references.

    params:
        Numeric or symbolic parameters.

    classical_target:
        Classical bit target for measurement operations.

    step:
        Optional composer step index.

    label:
        Optional UI label.

    measurement_route:
        Optional musical routing metadata for measurement operations.
    """

    name: str
    qubits: List[QubitRef]
    params: List[ParamValue] = field(default_factory=list)
    classical_target: Optional[ClassicalRef] = None
    step: Optional[int] = None
    label: Optional[str] = None
    measurement_route: Optional[MeasurementRoute] = None

    def gate_spec(self) -> GateSpec:
        return get_gate(self.name)

    def measurement_basis(self) -> Optional[MeasurementBasis]:
        return measurement_basis_for_operation(self.name, self.params)


@dataclass
class ComposerCircuit:
    """
    Registry-backed circuit container.

    This is intentionally simple:
        - no Qiskit dependency
        - no Max dependency
        - no state-vector simulation

    It gives us one canonical operation list that now drives:
        - QASM export
        - Qiskit circuit building
        - local simulation
        - Max UI gate menus
        - measurement-basis OSC/JSUI geometry
    """

    n_qubits: int = 4
    n_bits: int = 4
    qubit_register: str = "q"
    classical_register: str = "c"
    classical_registers: dict[str, ClassicalRegisterSpec] = field(default_factory=dict)
    operations: List[CircuitOperation] = field(default_factory=list)

    def declare_classical_register(
        self,
        name: str,
        width: int,
        *,
        role: str = "measurement",
    ) -> ClassicalRegisterSpec:
        register = normalize_register_bus_name(name)
        width = max(1, int(width))
        existing = self.classical_registers.get(register)
        if existing is not None:
            existing.width = max(existing.width, width)
            if role:
                existing.role = role
            return existing

        spec = ClassicalRegisterSpec(register, width, role=role)
        self.classical_registers[register] = spec
        return spec

    def add(
        self,
        name: str,
        qubits: Sequence[QubitRef],
        params: Optional[Sequence[ParamValue]] = None,
        classical_target: Optional[ClassicalRef] = None,
        step: Optional[int] = None,
        label: Optional[str] = None,
        measurement_route: Optional[MeasurementRoute] = None,
        target_register: Optional[str] = None,
        register_bit: Optional[int] = None,
        osc_route: Optional[str] = None,
        persistence: str = "single_shot",
        shots: int = 1,
        process: Optional[str] = None,
    ) -> CircuitOperation:
        params_list = list(params or [])
        qubits_list = list(qubits)

        spec = validate_gate_call(name, qubits_list, params_list)

        # Native measure and measurement macros need a classical bit target.
        if spec.name == "measure" or spec.category == "measurement_macro":
            if measurement_route is None:
                register = normalize_register_bus_name(target_register or "pitch")
                partition_requested = target_register is not None or register_bit is not None
                bit_index = None
                if partition_requested:
                    bit_index = (
                        int(register_bit)
                        if register_bit is not None
                        else (
                            int(qubits_list[0])
                            if len(qubits_list) == 1 and isinstance(qubits_list[0], int)
                            else 0
                        )
                    )
                    self.declare_classical_register(register, bit_index + 1)
                measurement_route = MeasurementRoute(
                    target_register=register,
                    osc_route=osc_route or default_measurement_osc_route(register),
                    persistence=persistence,
                    shots=int(shots),
                    register_bit=bit_index,
                    process=process or DEFAULT_REGISTER_PROCESSES.get(register, register),
                )
            elif measurement_route.register_bit is not None:
                self.declare_classical_register(
                    measurement_route.target_register,
                    int(measurement_route.register_bit) + 1,
                )

            if classical_target is None:
                if target_register is not None or measurement_route.register_bit is not None:
                    classical_target = (
                        f"{measurement_route.target_register}"
                        f"[{measurement_route.register_bit or 0}]"
                    )
                elif len(qubits_list) == 1 and isinstance(qubits_list[0], int):
                    classical_target = qubits_list[0]
                else:
                    raise ValueError(
                        f"{name} requires classical_target when qubit is not an int."
                    )

        op = CircuitOperation(
            name=spec.name,
            qubits=qubits_list,
            params=params_list,
            classical_target=classical_target,
            step=step,
            label=label,
            measurement_route=measurement_route,
        )

        self.operations.append(op)
        return op

    def clear(self) -> None:
        self.operations.clear()
        self.classical_registers.clear()

    def to_qasm_lines(self) -> List[str]:
        lines: List[str] = [
            qasm_program_header(
                self.n_qubits,
                self.n_bits,
                qubit_register=self.qubit_register,
                classical_register=self.classical_register,
            )
        ]
        for register in self.classical_registers.values():
            if register.name != self.classical_register:
                lines.append(f"bit[{register.width}] {register.name};")

        for op in self.operations:
            spec = op.gate_spec()

            if spec.category == "measurement_macro":
                if len(op.qubits) != 1:
                    raise ValueError(
                        f"{op.name} currently supports one qubit in QASM export."
                    )

                lines.extend(
                    compile_measurement_macro(
                        op.name,
                        op.qubits[0],
                        op.classical_target,
                        op.params,
                        qubit_register=self.qubit_register,
                        classical_register=self.classical_register,
                    )
                )
                continue

            lines.append(
                qasm_gate_call(
                    op.name,
                    op.qubits,
                    op.params,
                    classical_target=op.classical_target,
                    qubit_register=self.qubit_register,
                    classical_register=self.classical_register,
                )
            )

        return lines

    def to_qasm(self) -> str:
        return "\n".join(self.to_qasm_lines())

    def to_qiskit_circuit(self) -> Any:
        """
        Build a Qiskit QuantumCircuit from the canonical operation list.

        Qiskit is imported lazily so this bridge keeps its no-Qiskit default.
        Measurement macros are compiled as the same basis rotations used by
        QASM export, followed by a native measure.
        """
        try:
            from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
            from qiskit.circuit import Parameter
        except ImportError as exc:
            raise ImportError(
                "to_qiskit_circuit() requires qiskit. Install qiskit or use "
                "to_qasm()/simulate_statevector() for dependency-light paths."
            ) from exc

        qreg = QuantumRegister(self.n_qubits, self.qubit_register)
        creg = ClassicalRegister(self.n_bits, self.classical_register)
        extra_registers = [
            ClassicalRegister(register.width, register.name)
            for register in self.classical_registers.values()
            if register.name != self.classical_register
        ]
        circuit = QuantumCircuit(qreg, creg, *extra_registers)
        classical_registers = {self.classical_register: creg}
        classical_registers.update(
            {
                register.name: qiskit_register
                for register, qiskit_register in zip(
                    [
                        register
                        for register in self.classical_registers.values()
                        if register.name != self.classical_register
                    ],
                    extra_registers,
                )
            }
        )

        def qarg(q: QubitRef) -> Any:
            if not isinstance(q, int):
                raise ValueError(
                    f"Qiskit build requires integer qubit indices, got {q!r}."
                )
            return qreg[q]

        def carg(c: ClassicalRef | None) -> Any:
            if c is None:
                raise ValueError("Measurement requires a classical target.")
            if isinstance(c, int):
                return creg[c]
            text = str(c).strip()
            if "[" in text and text.endswith("]"):
                name, index_text = text[:-1].split("[", 1)
                register = classical_registers.get(name)
                if register is None:
                    raise ValueError(f"Unknown classical register {name!r}.")
                return register[int(index_text)]
            if text.isdigit():
                return creg[int(text)]
            raise ValueError(f"Unsupported classical target for Qiskit: {c!r}.")

        def param(value: ParamValue) -> Any:
            parsed = parse_pi_param(value)
            if parsed is not None:
                return parsed
            return Parameter(str(value))

        for op in self.operations:
            spec = op.gate_spec()
            qubits = [qarg(q) for q in op.qubits]
            params = [param(value) for value in op.params]

            if spec.category == "measurement_macro":
                if spec.name == "mx":
                    circuit.h(qubits[0])
                elif spec.name == "my":
                    circuit.sdg(qubits[0])
                    circuit.h(qubits[0])
                elif spec.name == "mn":
                    if len(params) != 2:
                        raise ValueError("MN requires params: theta, phi.")
                    theta, phi = params
                    circuit.rz(-phi, qubits[0])
                    circuit.ry(-theta, qubits[0])
                elif spec.name != "mz":
                    raise NotImplementedError(
                        f"Qiskit build does not support macro {spec.name!r}."
                    )
                circuit.measure(qubits[0], carg(op.classical_target))
                continue

            if spec.name == "measure":
                circuit.measure(qubits[0], carg(op.classical_target))
                continue

            if spec.name == "nop":
                continue

            qiskit_name = spec.qiskit_name
            if qiskit_name is None or not hasattr(circuit, qiskit_name):
                raise NotImplementedError(
                    f"Qiskit build has no method for operation {spec.name!r}."
                )

            method = getattr(circuit, qiskit_name)
            method(*params, *qubits)

        return circuit

    def to_simulation_plan(self, *, include_measurement_rotations: bool = True) -> List[dict[str, object]]:
        """
        Return low-level operation dictionaries for local engines.

        Measurement macros are represented as basis rotations plus a measurement
        marker. Local statevector simulation can use the rotations and ignore
        the non-unitary marker, while a sampler can consume the marker later.
        """
        plan: List[dict[str, object]] = []

        for op in self.operations:
            spec = op.gate_spec()
            basis = op.measurement_basis()

            if spec.category == "measurement_macro":
                q = op.qubits[0]
                if include_measurement_rotations:
                    if spec.name == "mx":
                        plan.append({"name": "h", "qubits": [q], "params": []})
                    elif spec.name == "my":
                        plan.append({"name": "sdg", "qubits": [q], "params": []})
                        plan.append({"name": "h", "qubits": [q], "params": []})
                    elif spec.name == "mn":
                        theta, phi = op.params
                        plan.append({"name": "rz", "qubits": [q], "params": [-self._numeric_param(phi)]})
                        plan.append({"name": "ry", "qubits": [q], "params": [-self._numeric_param(theta)]})
                plan.append(
                    {
                        "name": "measure",
                        "qubits": list(op.qubits),
                        "params": [],
                        "classical_target": op.classical_target,
                        "basis": None if basis is None else basis.label,
                        "route": self._measurement_route_dict(op.measurement_route),
                        "step": op.step,
                    }
                )
                continue

            plan.append(
                {
                    "name": spec.name,
                    "qubits": list(op.qubits),
                    "params": [self._numeric_param(value) for value in op.params],
                    "classical_target": op.classical_target,
                    "step": op.step,
                }
            )

        return plan

    def simulate_statevector(
        self,
        *,
        initial_state: Any = None,
        include_measurement_rotations: bool = False,
    ) -> Any:
        """
        Run a small dependency-light statevector simulation.

        This is unitary-only: measure/reset markers are ignored. By default,
        listener-basis measurement macros update metadata but do not rotate or
        collapse the simulated state. Set include_measurement_rotations=True to
        mirror the pre-measurement rotations used by QASM/Qiskit export.
        """
        import numpy as np

        if initial_state is None:
            state = np.zeros(2**self.n_qubits, dtype=np.complex128)
            state[0] = 1.0 + 0.0j
        else:
            state = np.asarray(initial_state, dtype=np.complex128).reshape(-1)
            if state.size != 2**self.n_qubits:
                raise ValueError(
                    f"initial_state must have {2**self.n_qubits} amplitudes."
                )

        for item in self.to_simulation_plan(
            include_measurement_rotations=include_measurement_rotations
        ):
            name = str(item["name"])
            if name in {"measure", "reset", "nop"}:
                continue
            qubits = item["qubits"]
            if any(not isinstance(q, int) for q in qubits):
                raise ValueError(f"Simulation requires integer qubits: {qubits!r}.")
            state = self._apply_simulation_gate(
                state,
                name,
                qubits,  # type: ignore[arg-type]
                item.get("params", []),  # type: ignore[arg-type]
                self.n_qubits,
            )

        norm = np.linalg.norm(state)
        return state / norm if norm > 0.0 else state

    def basis_probabilities(self, **simulate_kwargs: Any) -> Any:
        """Return computational-basis probabilities from simulate_statevector()."""
        import numpy as np

        state = self.simulate_statevector(**simulate_kwargs)
        return np.abs(state) ** 2

    def max_gate_menu_items(self, *, only_qasm_exportable: bool = True) -> List[dict[str, object]]:
        """
        Return Max/menu-friendly gate metadata from the registry.

        The payload is ready for JS/Max menus and includes arity, parameters,
        aliases, QASM support, Qiskit method names, and basis geometry.
        """
        return gate_menu_items(only_qasm_exportable=only_qasm_exportable)

    def measurement_basis_geometry(self) -> List[dict[str, object]]:
        """Return current JSUI/OSC-friendly measurement basis geometry."""
        geometry: List[dict[str, object]] = []
        routes = self.active_measurement_routes()

        for qubit, basis in self.active_measurement_bases():
            route = routes.get(qubit)
            geometry.append(
                {
                    "qubit": qubit,
                    "theta": basis.theta,
                    "phi": basis.phi,
                    "label": basis.label,
                    "pauli_axis": basis.pauli_axis,
                    "axis_vector": [
                        math.sin(basis.theta) * math.cos(basis.phi),
                        math.sin(basis.theta) * math.sin(basis.phi),
                        math.cos(basis.theta),
                    ],
                    "route": self._measurement_route_dict(route),
                }
            )

        return geometry

    def measurement_basis_osc_messages(self) -> List[tuple[str, object]]:
        """Return OSC address/value pairs for the active JSUI basis layer."""
        messages: List[tuple[str, object]] = []

        for item in self.measurement_basis_geometry():
            qubit = int(item["qubit"])
            axis = item["pauli_axis"] or ""
            theta = float(item["theta"])
            phi = float(item["phi"])
            label = str(item["label"])
            messages.extend(
                [
                    (f"/qmw/circuit/basis/q{qubit}", [theta, phi, label, axis]),
                    (f"/basis/{qubit}/theta", theta),
                    (f"/basis/{qubit}/phi", phi),
                    (f"/basis/{qubit}/label", label),
                    (f"/basis/{qubit}/axis", axis),
                    (f"/qubit/{qubit}/basis/theta", theta),
                    (f"/qubit/{qubit}/basis/phi", phi),
                    (f"/qubit/{qubit}/measure/basis/theta", theta),
                    (f"/qubit/{qubit}/measure/basis/phi", phi),
                    (f"/qubit/{qubit}/measure/basis/label", label),
                ]
            )

            route = item.get("route")
            if isinstance(route, dict):
                messages.extend(
                    [
                        (f"/qubit/{qubit}/measure/register", route["target_register"]),
                        (f"/qubit/{qubit}/measure/route", route["osc_route"]),
                        (f"/qubit/{qubit}/measure/persistence", route["persistence"]),
                        (f"/qubit/{qubit}/measure/shots", int(route["shots"])),
                        (
                            f"/qubit/{qubit}/measure/register_bit",
                            -1 if route["register_bit"] is None else int(route["register_bit"]),
                        ),
                        (f"/qubit/{qubit}/measure/process", route["process"]),
                    ]
                )

        return messages

    @staticmethod
    def _measurement_route_dict(route: Optional[MeasurementRoute]) -> Optional[dict[str, object]]:
        if route is None:
            return None
        return {
            "target_register": route.target_register,
            "osc_route": route.osc_route,
            "persistence": route.persistence,
            "shots": route.shots,
            "register_bit": route.register_bit,
            "process": route.process,
        }

    @staticmethod
    def _numeric_param(value: ParamValue) -> float:
        parsed = parse_pi_param(value)
        if parsed is None:
            raise ValueError(
                f"Local simulation requires numeric parameters, got {value!r}."
            )
        return parsed

    @classmethod
    def _apply_simulation_gate(
        cls,
        state: Any,
        name: str,
        qubits: Sequence[int],
        params: Sequence[float],
        n_qubits: int,
    ) -> Any:
        import numpy as np

        i = 1j
        x = np.array([[0, 1], [1, 0]], dtype=np.complex128)
        y = np.array([[0, -i], [i, 0]], dtype=np.complex128)
        z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
        h = (1.0 / math.sqrt(2.0)) * np.array(
            [[1, 1], [1, -1]], dtype=np.complex128
        )

        def phase(lam: float) -> Any:
            return np.array([[1, 0], [0, np.exp(i * lam)]], dtype=np.complex128)

        def rx(theta: float) -> Any:
            c = math.cos(theta / 2.0)
            s = math.sin(theta / 2.0)
            return np.array([[c, -i * s], [-i * s, c]], dtype=np.complex128)

        def ry(theta: float) -> Any:
            c = math.cos(theta / 2.0)
            s = math.sin(theta / 2.0)
            return np.array([[c, -s], [s, c]], dtype=np.complex128)

        def rz(theta: float) -> Any:
            return np.array(
                [
                    [np.exp(-i * theta / 2.0), 0],
                    [0, np.exp(i * theta / 2.0)],
                ],
                dtype=np.complex128,
            )

        def u3(theta: float, phi: float, lam: float) -> Any:
            c = math.cos(theta / 2.0)
            s = math.sin(theta / 2.0)
            return np.array(
                [
                    [c, -np.exp(i * lam) * s],
                    [np.exp(i * phi) * s, np.exp(i * (phi + lam)) * c],
                ],
                dtype=np.complex128,
            )

        single = {
            "id": np.eye(2, dtype=np.complex128),
            "x": x,
            "y": y,
            "z": z,
            "h": h,
            "s": phase(math.pi / 2.0),
            "sdg": phase(-math.pi / 2.0),
            "t": phase(math.pi / 4.0),
            "tdg": phase(-math.pi / 4.0),
            "sx": 0.5 * np.array(
                [[1 + i, 1 - i], [1 - i, 1 + i]], dtype=np.complex128
            ),
        }

        if name in {"p", "phase", "u1"}:
            return cls._apply_matrix(state, phase(params[0]), qubits, n_qubits)
        if name == "rx":
            return cls._apply_matrix(state, rx(params[0]), qubits, n_qubits)
        if name == "ry":
            return cls._apply_matrix(state, ry(params[0]), qubits, n_qubits)
        if name == "rz":
            return cls._apply_matrix(state, rz(params[0]), qubits, n_qubits)
        if name == "u2":
            return cls._apply_matrix(
                state,
                u3(math.pi / 2.0, params[0], params[1]),
                qubits,
                n_qubits,
            )
        if name == "u3":
            return cls._apply_matrix(
                state,
                u3(params[0], params[1], params[2]),
                qubits,
                n_qubits,
            )
        if name in single:
            return cls._apply_matrix(state, single[name], qubits, n_qubits)
        if name == "swap":
            return cls._apply_matrix(
                state,
                np.array(
                    [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]],
                    dtype=np.complex128,
                ),
                qubits,
                n_qubits,
            )

        controlled_unitaries = {
            "cx": x,
            "cy": y,
            "cz": z,
            "ch": h,
            "cp": phase(params[0]) if name == "cp" else None,
            "cphase": phase(params[0]) if name == "cphase" else None,
            "crx": rx(params[0]) if name == "crx" else None,
            "cry": ry(params[0]) if name == "cry" else None,
            "crz": rz(params[0]) if name == "crz" else None,
            "cu": np.exp(1j * params[3])
            * u3(params[0], params[1], params[2])
            if name == "cu"
            else None,
        }
        if name in controlled_unitaries:
            unitary = controlled_unitaries[name]
            if unitary is None:
                raise ValueError(f"Missing parameters for controlled gate {name}.")
            matrix = np.eye(4, dtype=np.complex128)
            matrix[2:4, 2:4] = unitary
            return cls._apply_matrix(state, matrix, qubits, n_qubits)

        if name == "ccx":
            matrix = np.eye(8, dtype=np.complex128)
            matrix[6, 6] = 0
            matrix[7, 7] = 0
            matrix[6, 7] = 1
            matrix[7, 6] = 1
            return cls._apply_matrix(state, matrix, qubits, n_qubits)

        if name == "cswap":
            matrix = np.eye(8, dtype=np.complex128)
            matrix[5, 5] = 0
            matrix[6, 6] = 0
            matrix[5, 6] = 1
            matrix[6, 5] = 1
            return cls._apply_matrix(state, matrix, qubits, n_qubits)

        raise NotImplementedError(f"Local simulation does not support {name!r}.")

    @staticmethod
    def _apply_matrix(
        state: Any,
        matrix: Any,
        qubits: Sequence[int],
        n_qubits: int,
    ) -> Any:
        import numpy as np

        if len(set(qubits)) != len(qubits):
            raise ValueError(f"Gate qubits must be distinct: {qubits!r}.")
        if any(q < 0 or q >= n_qubits for q in qubits):
            raise ValueError(f"Qubit index out of range: {qubits!r}.")

        k = len(qubits)
        expected = 2**k
        matrix = np.asarray(matrix, dtype=np.complex128)
        if matrix.shape != (expected, expected):
            raise ValueError(
                f"Gate matrix shape {matrix.shape} does not match {k} qubit(s)."
            )

        tensor = state.reshape((2,) * n_qubits)
        moved = np.moveaxis(tensor, qubits, range(k))
        front = moved.reshape(expected, -1)
        transformed = matrix @ front
        restored = transformed.reshape((2,) * n_qubits)
        restored = np.moveaxis(restored, range(k), qubits)
        return restored.reshape(-1)

    def active_measurement_bases(self) -> List[tuple[int, MeasurementBasis]]:
        """
        Return latest known measurement/listener basis per qubit.

        This is the bridge to the JSUI gold vector and OSC basis layer.
        """
        bases: dict[int, MeasurementBasis] = {}

        for op in self.operations:
            basis = op.measurement_basis()
            if basis is None:
                continue

            if len(op.qubits) != 1:
                continue

            q = op.qubits[0]
            if isinstance(q, int):
                bases[q] = basis

        return sorted(bases.items(), key=lambda item: item[0])

    def active_measurement_routes(self) -> dict[int, MeasurementRoute]:
        """
        Return latest known measurement routing metadata per qubit.

        Measurement routes make M gates first-class musical operators:
        they identify which classical register/bus receives the BitArray,
        which OSC subsystem should hear it, and how persistent/statistical
        the measurement should be.
        """
        routes: dict[int, MeasurementRoute] = {}

        for op in self.operations:
            if op.measurement_route is None:
                continue

            if op.measurement_basis() is None:
                continue

            if len(op.qubits) != 1:
                continue

            q = op.qubits[0]
            if isinstance(q, int):
                routes[q] = op.measurement_route

        return routes

    def measurement_register_partitions(self) -> dict[str, dict[str, object]]:
        partitions: dict[str, dict[str, object]] = {}

        for name, register in self.classical_registers.items():
            partitions[name] = {
                "name": name,
                "width": register.width,
                "role": register.role,
                "process": DEFAULT_REGISTER_PROCESSES.get(name, name),
                "osc_route": default_measurement_osc_route(name),
                "qubits": [],
            }

        for op in self.operations:
            if op.measurement_route is None:
                continue
            if len(op.qubits) != 1 or not isinstance(op.qubits[0], int):
                continue

            route = op.measurement_route
            partition = partitions.setdefault(
                route.target_register,
                {
                    "name": route.target_register,
                    "width": 0,
                    "role": "measurement",
                    "process": route.process,
                    "osc_route": route.osc_route,
                    "qubits": [],
                },
            )
            partition["process"] = route.process
            partition["osc_route"] = route.osc_route
            if route.register_bit is not None:
                partition["width"] = max(
                    int(partition["width"]),
                    int(route.register_bit) + 1,
                )
            partition["qubits"].append(
                {
                    "qubit": op.qubits[0],
                    "bit": route.register_bit,
                    "basis": op.measurement_basis().label if op.measurement_basis() else "",
                    "step": op.step,
                }
            )

        return partitions

    def describe(self) -> str:
        lines = [
            "ComposerCircuit",
            "---------------",
            f"qubits: {self.n_qubits}",
            f"bits:   {self.n_bits}",
            f"ops:    {len(self.operations)}",
            "",
        ]
        if self.classical_registers:
            lines.append("classical registers:")
            for register in self.classical_registers.values():
                process = DEFAULT_REGISTER_PROCESSES.get(register.name, register.role)
                lines.append(
                    f"  {register.name}[{register.width}] "
                    f"role={register.role} process={process}"
                )
            lines.append("")

        for i, op in enumerate(self.operations):
            spec = op.gate_spec()
            params = ""
            if op.params:
                params = "(" + ", ".join(str(p) for p in op.params) + ")"

            ctarget = ""
            if op.classical_target is not None:
                if isinstance(op.classical_target, int) or str(op.classical_target).isdigit():
                    ctarget = f" -> {self.classical_register}[{op.classical_target}]"
                else:
                    ctarget = f" -> {op.classical_target}"

            route = ""
            if op.measurement_route is not None:
                bit = ""
                if op.measurement_route.register_bit is not None:
                    bit = f"[{op.measurement_route.register_bit}]"
                route = (
                    f" route={op.measurement_route.target_register}{bit}"
                    f" osc={op.measurement_route.osc_route}"
                    f" mode={op.measurement_route.persistence}"
                    f" shots={op.measurement_route.shots}"
                    f" process={op.measurement_route.process}"
                )

            step = "" if op.step is None else f" step={op.step}"

            lines.append(
                f"{i:02d}: {op.name}{params} "
                f"q={op.qubits}{ctarget}"
                f" [{spec.category}/{spec.kind}]{step}{route}"
            )

            basis = op.measurement_basis()
            if basis is not None:
                lines.append(
                    f"    basis: {basis.label} "
                    f"theta={basis.theta:.6g} phi={basis.phi:.6g}"
                )

        return "\n".join(lines)


def demo_circuit() -> ComposerCircuit:
    circuit = ComposerCircuit(n_qubits=4, n_bits=4)

    # Basic superposition / entanglement.
    circuit.add("h", [0], step=0)
    circuit.add("cx", [0, 1], step=1)

    # Newly supported Composer/QASM operations.
    circuit.add("swap", [2, 3], step=2)
    circuit.add("toffoli", [0, 1, 2], step=3)

    # Phase/quadrature gates.
    circuit.add("s", [0], step=4)
    circuit.add("tdg", [1], step=5)
    circuit.add("rz", [2], params=["pi/4"], step=6)

    # Measurement/listener-basis macros.
    circuit.add("MX", [0], step=7)
    circuit.add("MY", [1], step=8)
    circuit.add("MZ", [2], step=9)
    circuit.add("MN", [3], params=["pi/3", "pi/4"], step=10)

    return circuit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Registry-backed Composer circuit bridge."
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Print demo circuit description.",
    )

    parser.add_argument(
        "--qasm",
        action="store_true",
        help="Print demo circuit as OpenQASM.",
    )

    parser.add_argument(
        "--bases",
        action="store_true",
        help="Print active measurement/listener bases from demo circuit.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    circuit = demo_circuit()

    if args.qasm:
        print(circuit.to_qasm())
        return

    if args.bases:
        for q, basis in circuit.active_measurement_bases():
            print(
                f"q{q}: {basis.label} "
                f"theta={basis.theta:.6g} phi={basis.phi:.6g} "
                f"axis={basis.pauli_axis}"
            )
        return

    print(circuit.describe())

    if args.demo:
        return

    print()
    print("Try:")
    print("  python qasm_circuit_bridge_v1.py --qasm")
    print("  python qasm_circuit_bridge_v1.py --bases")


if __name__ == "__main__":
    main()
