#!/usr/bin/env python3
"""
qasm_gate_registry_v1.py

Canonical OpenQASM / Qiskit / Max circuit-composer gate registry.

Purpose:
    - Define a single source of truth for Composer operations.
    - Normalize aliases such as CNOT -> cx, TOFFOLI -> ccx.
    - Track arity, parameters, QASM spelling, Qiskit method name, and geometry.
    - Add measurement-basis macros:
        MZ, MX, MY, MN(theta, phi)
      which compile to normal basis-rotation + Z-basis measurement.

This file is intentionally metadata-first and has no qiskit dependency.
Later files can import this registry to build:
    - Qiskit circuits
    - OpenQASM export
    - local state-vector / density-matrix simulation
    - Max circuit-programmer UI
    - OSC listener-basis geometry
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Union


ParamValue = Union[float, int, str]

# ------------------------------------------------------------
# Data classes
# ------------------------------------------------------------

@dataclass(frozen=True)
class MeasurementBasis:
    """
    Bloch-sphere measurement/listening basis.

    theta:
        polar angle away from +Z

    phi:
        azimuthal angle in X/Y plane

    label:
        human-readable basis label, e.g. MZ, MX, MY, MN

    pauli_axis:
        optional Pauli-axis label when the basis is one of X/Y/Z
    """

    theta: float
    phi: float
    label: str
    pauli_axis: Optional[str] = None


@dataclass(frozen=True)
class GateSpec:
    """
    Registry entry for one Composer operation.
    """

    name: str
    qasm_name: str
    qiskit_name: Optional[str]
    kind: str
    category: str
    arity: int
    params: Tuple[str, ...] = ()
    aliases: Tuple[str, ...] = ()
    qasm_version: str = "3.0"
    geometry: str = ""
    description: str = ""
    is_macro: bool = False
    measurement_basis: Optional[MeasurementBasis] = None


# ------------------------------------------------------------
# Internal registry containers
# ------------------------------------------------------------

GATES: Dict[str, GateSpec] = {}
ALIASES: Dict[str, str] = {}


def _norm(name: str) -> str:
    return str(name).strip().lower().replace("-", "_")


def _register(spec: GateSpec) -> None:
    canonical = _norm(spec.name)
    if canonical in GATES:
        raise ValueError(f"Duplicate gate registry entry: {canonical}")

    GATES[canonical] = spec
    ALIASES[canonical] = canonical

    for alias in spec.aliases:
        ALIASES[_norm(alias)] = canonical


def normalize_gate_name(name: str) -> str:
    """
    Normalize a Composer/QASM/Qiskit-facing name to our canonical registry name.
    """
    key = _norm(name)
    if key not in ALIASES:
        raise KeyError(f"Unknown gate or operation: {name}")
    return ALIASES[key]


def get_gate(name: str) -> GateSpec:
    return GATES[normalize_gate_name(name)]


def is_supported(name: str) -> bool:
    try:
        get_gate(name)
        return True
    except KeyError:
        return False


def gate_names(
    *,
    category: Optional[str] = None,
    kind: Optional[str] = None,
    include_macros: bool = True,
) -> List[str]:
    names: List[str] = []

    for name, spec in sorted(GATES.items()):
        if category is not None and spec.category != category:
            continue
        if kind is not None and spec.kind != kind:
            continue
        if not include_macros and spec.is_macro:
            continue
        names.append(name)

    return names


def measurement_basis_dict(
    basis: Optional[MeasurementBasis],
) -> Optional[Dict[str, Union[float, str, None]]]:
    if basis is None:
        return None

    return {
        "theta": basis.theta,
        "phi": basis.phi,
        "label": basis.label,
        "pauli_axis": basis.pauli_axis,
    }


def qasm_export_supported(name: str) -> bool:
    """
    Return whether the current bridge can export this operation to QASM text.

    Most registered gates are ordinary QASM calls. Measurement/listener macros
    need explicit compilers; mstring is intentionally metadata-only for now.
    """
    spec = get_gate(name)

    if spec.category != "measurement_macro":
        return True

    return spec.name in {"mz", "mx", "my", "mn"}


def gate_menu_items(
    *,
    include_builtin: bool = True,
    include_compatibility: bool = True,
    include_measurement_macros: bool = True,
    only_qasm_exportable: bool = False,
) -> List[Dict[str, object]]:
    """
    Return registry entries in a Max/menu-friendly JSON-serializable form.

    Max can use this to build the gate menu and know:
        - how many qubits to request
        - which params to expose
        - whether the operation updates listener basis geometry
        - whether the bridge can export it to OpenQASM now
    """
    items: List[Dict[str, object]] = []

    for name, spec in sorted(GATES.items()):
        if spec.category == "builtin" and not include_builtin:
            continue
        if spec.category == "compatibility" and not include_compatibility:
            continue
        if spec.category == "measurement_macro" and not include_measurement_macros:
            continue
        if only_qasm_exportable and not qasm_export_supported(name):
            continue

        basis = measurement_basis_dict(spec.measurement_basis)

        items.append(
            {
                "name": spec.name,
                "label": spec.name.upper() if spec.is_macro else spec.name,
                "qasm_name": spec.qasm_name,
                "qiskit_name": spec.qiskit_name,
                "category": spec.category,
                "kind": spec.kind,
                "arity": spec.arity,
                "params": list(spec.params),
                "aliases": list(spec.aliases),
                "qasm_version": spec.qasm_version,
                "qasm_export_supported": qasm_export_supported(name),
                "is_macro": spec.is_macro,
                "measurement_basis": basis,
                "geometry": spec.geometry,
                "description": spec.description,
            }
        )

    return items


# ------------------------------------------------------------
# OpenQASM stdgates.inc registry
# ------------------------------------------------------------

# Single-qubit standard gates.
_register(
    GateSpec(
        name="p",
        qasm_name="p",
        qiskit_name="p",
        kind="phase",
        category="stdgate",
        arity=1,
        params=("lambda",),
        aliases=("phase_gate",),
        geometry="phase_on_z",
        description="OpenQASM phase gate P(lambda).",
    )
)

_register(
    GateSpec(
        name="x",
        qasm_name="x",
        qiskit_name="x",
        kind="pauli",
        category="stdgate",
        arity=1,
        aliases=("pauli_x",),
        geometry="x_flip",
        description="Pauli X gate.",
    )
)

_register(
    GateSpec(
        name="y",
        qasm_name="y",
        qiskit_name="y",
        kind="pauli",
        category="stdgate",
        arity=1,
        aliases=("pauli_y",),
        geometry="y_flip_quadrature",
        description="Pauli Y gate.",
    )
)

_register(
    GateSpec(
        name="z",
        qasm_name="z",
        qiskit_name="z",
        kind="pauli",
        category="stdgate",
        arity=1,
        aliases=("pauli_z",),
        geometry="z_phase_flip",
        description="Pauli Z gate.",
    )
)

_register(
    GateSpec(
        name="h",
        qasm_name="h",
        qiskit_name="h",
        kind="basis_mixer",
        category="stdgate",
        arity=1,
        aliases=("hadamard",),
        geometry="z_to_x_basis",
        description="Hadamard gate.",
    )
)

_register(
    GateSpec(
        name="s",
        qasm_name="s",
        qiskit_name="s",
        kind="phase",
        category="stdgate",
        arity=1,
        aliases=("sqrt_z",),
        geometry="quarter_turn_phase",
        description="S gate, equivalent to P(pi/2).",
    )
)

_register(
    GateSpec(
        name="sdg",
        qasm_name="sdg",
        qiskit_name="sdg",
        kind="phase",
        category="stdgate",
        arity=1,
        aliases=("sdag", "s_dagger", "s†"),
        geometry="negative_quarter_turn_phase",
        description="Adjoint S gate, equivalent to P(-pi/2).",
    )
)

_register(
    GateSpec(
        name="t",
        qasm_name="t",
        qiskit_name="t",
        kind="phase",
        category="stdgate",
        arity=1,
        aliases=("sqrt_s",),
        geometry="eighth_turn_phase",
        description="T gate, equivalent to P(pi/4).",
    )
)

_register(
    GateSpec(
        name="tdg",
        qasm_name="tdg",
        qiskit_name="tdg",
        kind="phase",
        category="stdgate",
        arity=1,
        aliases=("tdag", "t_dagger", "t†"),
        geometry="negative_eighth_turn_phase",
        description="Adjoint T gate, equivalent to P(-pi/4).",
    )
)

_register(
    GateSpec(
        name="sx",
        qasm_name="sx",
        qiskit_name="sx",
        kind="sqrt_pauli",
        category="stdgate",
        arity=1,
        aliases=("sqrt_x",),
        geometry="sqrt_x_rotation",
        description="Square-root X gate.",
    )
)

_register(
    GateSpec(
        name="rx",
        qasm_name="rx",
        qiskit_name="rx",
        kind="rotation",
        category="stdgate",
        arity=1,
        params=("theta",),
        geometry="x_axis_rotation",
        description="Rotation about X axis.",
    )
)

_register(
    GateSpec(
        name="ry",
        qasm_name="ry",
        qiskit_name="ry",
        kind="rotation",
        category="stdgate",
        arity=1,
        params=("theta",),
        geometry="y_axis_rotation",
        description="Rotation about Y axis.",
    )
)

_register(
    GateSpec(
        name="rz",
        qasm_name="rz",
        qiskit_name="rz",
        kind="rotation",
        category="stdgate",
        arity=1,
        params=("theta",),
        geometry="z_axis_rotation",
        description="Rotation about Z axis.",
    )
)


# Two-qubit standard gates.
_register(
    GateSpec(
        name="cx",
        qasm_name="cx",
        qiskit_name="cx",
        kind="controlled",
        category="stdgate",
        arity=2,
        aliases=("cnot", "controlled_x", "CX"),
        geometry="controlled_bit_flip_entangler",
        description="Controlled X / CNOT gate. First qubit is control.",
    )
)

_register(
    GateSpec(
        name="cy",
        qasm_name="cy",
        qiskit_name="cy",
        kind="controlled",
        category="stdgate",
        arity=2,
        aliases=("controlled_y",),
        geometry="controlled_quadrature_flip",
        description="Controlled Y gate. First qubit is control.",
    )
)

_register(
    GateSpec(
        name="cz",
        qasm_name="cz",
        qiskit_name="cz",
        kind="controlled",
        category="stdgate",
        arity=2,
        aliases=("controlled_z",),
        geometry="controlled_phase_flip",
        description="Controlled Z gate.",
    )
)

_register(
    GateSpec(
        name="cp",
        qasm_name="cp",
        qiskit_name="cp",
        kind="controlled_phase",
        category="stdgate",
        arity=2,
        params=("lambda",),
        aliases=("cphase", "controlled_phase"),
        geometry="controlled_phase_angle",
        description="Controlled phase gate CP(lambda).",
    )
)

_register(
    GateSpec(
        name="crx",
        qasm_name="crx",
        qiskit_name="crx",
        kind="controlled_rotation",
        category="stdgate",
        arity=2,
        params=("theta",),
        geometry="controlled_x_rotation",
        description="Controlled RX(theta).",
    )
)

_register(
    GateSpec(
        name="cry",
        qasm_name="cry",
        qiskit_name="cry",
        kind="controlled_rotation",
        category="stdgate",
        arity=2,
        params=("theta",),
        geometry="controlled_y_rotation",
        description="Controlled RY(theta).",
    )
)

_register(
    GateSpec(
        name="crz",
        qasm_name="crz",
        qiskit_name="crz",
        kind="controlled_rotation",
        category="stdgate",
        arity=2,
        params=("theta",),
        geometry="controlled_z_rotation",
        description="Controlled RZ(theta).",
    )
)

_register(
    GateSpec(
        name="ch",
        qasm_name="ch",
        qiskit_name="ch",
        kind="controlled",
        category="stdgate",
        arity=2,
        aliases=("controlled_h",),
        geometry="controlled_basis_mixer",
        description="Controlled Hadamard.",
    )
)

_register(
    GateSpec(
        name="cu",
        qasm_name="cu",
        qiskit_name="cu",
        kind="controlled_u",
        category="stdgate",
        arity=2,
        params=("theta", "phi", "lambda", "gamma"),
        geometry="controlled_general_unitary",
        description="Controlled U with four OpenQASM parameters.",
    )
)

_register(
    GateSpec(
        name="swap",
        qasm_name="swap",
        qiskit_name="swap",
        kind="permutation",
        category="stdgate",
        arity=2,
        aliases=("state_exchange",),
        geometry="state_exchange",
        description="Swap the states of two qubits.",
    )
)


# Three-qubit standard gates.
_register(
    GateSpec(
        name="ccx",
        qasm_name="ccx",
        qiskit_name="ccx",
        kind="multi_control",
        category="stdgate",
        arity=3,
        aliases=("toffoli", "controlled_controlled_x"),
        geometry="reversible_logic_threshold",
        description="Toffoli gate. First two qubits are controls, last is target.",
    )
)

_register(
    GateSpec(
        name="cswap",
        qasm_name="cswap",
        qiskit_name="cswap",
        kind="controlled_permutation",
        category="stdgate",
        arity=3,
        aliases=("fredkin", "controlled_swap"),
        geometry="conditional_state_exchange",
        description="Fredkin / controlled-SWAP gate. First qubit is control.",
    )
)


# OpenQASM compatibility / explicit aliases.
_register(
    GateSpec(
        name="id",
        qasm_name="id",
        qiskit_name="id",
        kind="identity",
        category="compatibility",
        arity=1,
        aliases=("i", "identity"),
        geometry="identity_noop_gate",
        description="Identity gate.",
    )
)

_register(
    GateSpec(
        name="phase",
        qasm_name="phase",
        qiskit_name="p",
        kind="phase",
        category="compatibility",
        arity=1,
        params=("lambda",),
        aliases=("phase_alias",),
        geometry="alias_for_p",
        description="OpenQASM compatibility alias for p(lambda).",
    )
)

_register(
    GateSpec(
        name="cphase",
        qasm_name="cphase",
        qiskit_name="cp",
        kind="controlled_phase",
        category="compatibility",
        arity=2,
        params=("lambda",),
        aliases=("cphase_alias",),
        geometry="alias_for_cp",
        description="OpenQASM compatibility alias for cp(lambda).",
    )
)

_register(
    GateSpec(
        name="u1",
        qasm_name="u1",
        qiskit_name="p",
        kind="u_compat",
        category="compatibility",
        arity=1,
        params=("lambda",),
        geometry="qasm2_phase_compat",
        description="OpenQASM 2 compatibility U1(lambda).",
    )
)

_register(
    GateSpec(
        name="u2",
        qasm_name="u2",
        qiskit_name="u",
        kind="u_compat",
        category="compatibility",
        arity=1,
        params=("phi", "lambda"),
        geometry="qasm2_u2_compat",
        description="OpenQASM 2 compatibility U2(phi, lambda).",
    )
)

_register(
    GateSpec(
        name="u3",
        qasm_name="u3",
        qiskit_name="u",
        kind="u_compat",
        category="compatibility",
        arity=1,
        params=("theta", "phi", "lambda"),
        geometry="qasm2_u3_compat",
        description="OpenQASM 2 compatibility U3(theta, phi, lambda).",
    )
)


# Built-in quantum instructions.
_register(
    GateSpec(
        name="reset",
        qasm_name="reset",
        qiskit_name="reset",
        kind="builtin_instruction",
        category="builtin",
        arity=1,
        geometry="state_reinitialization",
        description="Reset qubit to |0>.",
    )
)

_register(
    GateSpec(
        name="measure",
        qasm_name="measure",
        qiskit_name="measure",
        kind="builtin_instruction",
        category="builtin",
        arity=1,
        aliases=("mz_raw", "measure_z_raw"),
        measurement_basis=MeasurementBasis(
            theta=0.0,
            phi=0.0,
            label="Z",
            pauli_axis="Z",
        ),
        geometry="z_basis_projective_measurement",
        description="Native OpenQASM Z-basis measurement.",
    )
)

_register(
    GateSpec(
        name="nop",
        qasm_name="nop",
        qiskit_name=None,
        kind="builtin_instruction",
        category="builtin",
        arity=-1,
        geometry="explicit_no_operation",
        description="Explicit no-operation.",
    )
)


# ------------------------------------------------------------
# Composer-level measurement/listener-basis macros
# ------------------------------------------------------------

_register(
    GateSpec(
        name="mz",
        qasm_name="measure",
        qiskit_name="measure",
        kind="measurement_macro",
        category="measurement_macro",
        arity=1,
        aliases=("MZ", "measure_z", "listen_z"),
        is_macro=True,
        measurement_basis=MeasurementBasis(
            theta=0.0,
            phi=0.0,
            label="MZ",
            pauli_axis="Z",
        ),
        geometry="listener_basis_z",
        description="Composer macro: measure/listen in Z basis.",
    )
)

_register(
    GateSpec(
        name="mx",
        qasm_name="measure",
        qiskit_name="measure",
        kind="measurement_macro",
        category="measurement_macro",
        arity=1,
        aliases=("MX", "measure_x", "listen_x"),
        is_macro=True,
        measurement_basis=MeasurementBasis(
            theta=math.pi / 2.0,
            phi=0.0,
            label="MX",
            pauli_axis="X",
        ),
        geometry="listener_basis_x",
        description="Composer macro: H then Z measurement.",
    )
)

_register(
    GateSpec(
        name="my",
        qasm_name="measure",
        qiskit_name="measure",
        kind="measurement_macro",
        category="measurement_macro",
        arity=1,
        aliases=("MY", "measure_y", "listen_y"),
        is_macro=True,
        measurement_basis=MeasurementBasis(
            theta=math.pi / 2.0,
            phi=math.pi / 2.0,
            label="MY",
            pauli_axis="Y",
        ),
        geometry="listener_basis_y",
        description="Composer macro: Sdg, H, then Z measurement.",
    )
)

_register(
    GateSpec(
        name="mn",
        qasm_name="measure",
        qiskit_name="measure",
        kind="measurement_macro",
        category="measurement_macro",
        arity=1,
        params=("theta", "phi"),
        aliases=("MN", "measure_n", "listen_n", "observe_n"),
        is_macro=True,
        geometry="listener_basis_arbitrary_bloch_axis",
        description="Composer macro: arbitrary Bloch-axis measurement/listening basis.",
    )
)

_register(
    GateSpec(
        name="mstring",
        qasm_name="measure",
        qiskit_name="measure",
        kind="measurement_macro",
        category="measurement_macro",
        arity=-1,
        params=("pauli_string",),
        aliases=("MSTRING", "measure_pauli_string", "listen_pauli_string"),
        is_macro=True,
        geometry="multi_qubit_pauli_observable",
        description="Composer macro: Pauli-string measurement/listener observable.",
    )
)


# ------------------------------------------------------------
# Formatting helpers
# ------------------------------------------------------------

def qref(q: Union[int, str], register_name: str = "q") -> str:
    """
    Convert int or raw string to OpenQASM qubit reference.

    Examples:
        qref(0)      -> q[0]
        qref("q[2]") -> q[2]
        qref("$0")   -> $0
    """
    if isinstance(q, int):
        return f"{register_name}[{q}]"

    text = str(q).strip()
    if text.startswith(register_name + "[") or text.startswith("$"):
        return text

    if text.isdigit():
        return f"{register_name}[{text}]"

    return text


def cref(c: Union[int, str], register_name: str = "c") -> str:
    if isinstance(c, int):
        return f"{register_name}[{c}]"

    text = str(c).strip()
    if text.startswith(register_name + "["):
        return text

    if text.isdigit():
        return f"{register_name}[{text}]"

    return text


def format_param(value: ParamValue) -> str:
    """
    Format a parameter for QASM.

    Strings are passed through so the caller can use expressions:
        "pi/2"
        "theta"
        "2*pi*t"
    """
    if isinstance(value, bool):
        raise TypeError("Boolean is not a valid gate parameter.")

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if math.isclose(value, math.pi):
            return "pi"
        if math.isclose(value, 2.0 * math.pi):
            return "2*pi"
        if math.isclose(value, math.pi / 2.0):
            return "pi/2"
        if math.isclose(value, math.pi / 3.0):
            return "pi/3"
        if math.isclose(value, -math.pi / 2.0):
            return "-pi/2"
        if math.isclose(value, -math.pi / 3.0):
            return "-pi/3"
        if math.isclose(value, math.pi / 4.0):
            return "pi/4"
        if math.isclose(value, -math.pi / 4.0):
            return "-pi/4"
        return f"{value:.12g}"

    return str(value)


def parse_pi_param(value: ParamValue) -> Optional[float]:
    """
    Parse small Composer/Max-friendly pi expressions.

    Supported strings:
        pi, pi/2, pi/8, -pi/16, 2*pi, 3*pi/8

    Numeric values pass through. Other symbolic strings return None.
    """
    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(" ", "").lower()
    table = {
        "pi": math.pi,
        "+pi": math.pi,
        "2*pi": 2.0 * math.pi,
        "2pi": 2.0 * math.pi,
        "pi/2": math.pi / 2.0,
        "+pi/2": math.pi / 2.0,
        "-pi/2": -math.pi / 2.0,
        "pi/3": math.pi / 3.0,
        "+pi/3": math.pi / 3.0,
        "-pi/3": -math.pi / 3.0,
        "pi/4": math.pi / 4.0,
        "+pi/4": math.pi / 4.0,
        "-pi/4": -math.pi / 4.0,
    }

    if text in table:
        return table[text]

    if "pi" in text:
        try:
            if text == "pi":
                return math.pi
            if text == "-pi":
                return -math.pi

            if "*pi" in text:
                coefficient_text, remainder = text.split("*pi", 1)
                coefficient = float(coefficient_text)
            elif text.startswith("pi"):
                coefficient = 1.0
                remainder = text[2:]
            elif text.startswith("-pi"):
                coefficient = -1.0
                remainder = text[3:]
            else:
                return None

            if not remainder:
                divisor = 1.0
            elif remainder.startswith("/"):
                divisor = float(remainder[1:])
            else:
                return None

            if divisor == 0.0:
                return None
            return coefficient * math.pi / divisor
        except ValueError:
            return None

    try:
        return float(text)
    except ValueError:
        return None


def neg_param_expr(value: ParamValue) -> str:
    if isinstance(value, (int, float)):
        return format_param(-float(value))

    text = str(value).strip()
    if text.startswith("-"):
        return text[1:]
    return f"-({text})"


# ------------------------------------------------------------
# Validation and QASM generation
# ------------------------------------------------------------

def validate_gate_call(
    name: str,
    qubits: Sequence[Union[int, str]],
    params: Optional[Sequence[ParamValue]] = None,
) -> GateSpec:
    spec = get_gate(name)
    params = params or ()

    if spec.arity >= 0 and len(qubits) != spec.arity:
        raise ValueError(
            f"{spec.name} expects {spec.arity} qubit(s), got {len(qubits)}."
        )

    if len(params) != len(spec.params):
        raise ValueError(
            f"{spec.name} expects {len(spec.params)} parameter(s) "
            f"{spec.params}, got {len(params)}."
        )

    return spec


def qasm_gate_call(
    name: str,
    qubits: Sequence[Union[int, str]],
    params: Optional[Sequence[ParamValue]] = None,
    *,
    classical_target: Optional[Union[int, str]] = None,
    qubit_register: str = "q",
    classical_register: str = "c",
) -> str:
    """
    Build one OpenQASM statement for a standard gate or built-in operation.

    Measurement-basis macros should use compile_measurement_macro(...).
    """
    spec = validate_gate_call(name, qubits, params)
    params = params or ()

    qargs = ", ".join(qref(q, qubit_register) for q in qubits)

    if spec.name == "measure":
        if classical_target is None:
            raise ValueError("measure requires classical_target.")
        return f"{cref(classical_target, classical_register)} = measure {qargs};"

    if spec.name == "reset":
        return f"reset {qargs};"

    if spec.name == "nop":
        return f"nop {qargs};" if qargs else "nop;"

    if spec.is_macro:
        raise ValueError(
            f"{spec.name} is a Composer macro. "
            "Use compile_measurement_macro(...) instead."
        )

    if params:
        pargs = ", ".join(format_param(p) for p in params)
        return f"{spec.qasm_name}({pargs}) {qargs};"

    return f"{spec.qasm_name} {qargs};"


def compile_measurement_macro(
    name: str,
    qubit: Union[int, str],
    classical_target: Union[int, str],
    params: Optional[Sequence[ParamValue]] = None,
    *,
    qubit_register: str = "q",
    classical_register: str = "c",
) -> List[str]:
    """
    Compile Composer measurement/listener-basis macros to ordinary QASM lines.

    MZ:
        c[i] = measure q[i];

    MX:
        h q[i];
        c[i] = measure q[i];

    MY:
        sdg q[i];
        h q[i];
        c[i] = measure q[i];

    MN(theta, phi):
        rz(-phi) q[i];
        ry(-theta) q[i];
        c[i] = measure q[i];

    The final physical readout remains a native Z-basis measurement.
    """
    spec = get_gate(name)
    params = params or ()

    if spec.category != "measurement_macro":
        raise ValueError(f"{name} is not a measurement macro.")

    canonical = spec.name
    q = qref(qubit, qubit_register)
    c = cref(classical_target, classical_register)

    if canonical == "mz":
        return [f"{c} = measure {q};"]

    if canonical == "mx":
        return [
            f"h {q};",
            f"{c} = measure {q};",
        ]

    if canonical == "my":
        return [
            f"sdg {q};",
            f"h {q};",
            f"{c} = measure {q};",
        ]

    if canonical == "mn":
        if len(params) != 2:
            raise ValueError("MN requires params: theta, phi.")

        theta, phi = params
        return [
            f"rz({neg_param_expr(phi)}) {q};",
            f"ry({neg_param_expr(theta)}) {q};",
            f"{c} = measure {q};",
        ]

    raise NotImplementedError(
        f"Measurement macro {canonical!r} requires a custom compiler."
    )


def measurement_basis_for_operation(
    name: str,
    params: Optional[Sequence[ParamValue]] = None,
) -> Optional[MeasurementBasis]:
    """
    Return the Bloch listener basis implied by a measurement macro.

    For MN(theta, phi), numeric theta/phi are returned when possible.
    Symbolic params return None because the runtime value is unknown here.
    """
    spec = get_gate(name)
    params = params or ()

    if spec.measurement_basis is not None:
        return spec.measurement_basis

    if spec.name == "mn":
        if len(params) != 2:
            raise ValueError("MN requires params: theta, phi.")

        theta, phi = params

        theta_value = parse_pi_param(theta)
        phi_value = parse_pi_param(phi)

        if theta_value is not None and phi_value is not None:
            return MeasurementBasis(
                theta=theta_value,
                phi=phi_value,
                label="MN",
                pauli_axis=None,
            )

        return None

    return None


def qiskit_method_name(name: str) -> Optional[str]:
    """
    Return likely QuantumCircuit method name.

    This does not import Qiskit. It is metadata only.
    """
    return get_gate(name).qiskit_name


def qasm_program_header(
    n_qubits: int,
    n_bits: Optional[int] = None,
    *,
    version: str = "3.0",
    qubit_register: str = "q",
    classical_register: str = "c",
    include_stdlib: bool = True,
) -> str:
    n_bits = n_qubits if n_bits is None else n_bits

    lines = [f"OPENQASM {version};"]
    if include_stdlib:
        lines.append('include "stdgates.inc";')

    lines.append(f"qubit[{n_qubits}] {qubit_register};")
    lines.append(f"bit[{n_bits}] {classical_register};")

    return "\n".join(lines)


# ------------------------------------------------------------
# Reporting
# ------------------------------------------------------------

def registry_summary() -> str:
    categories = sorted({spec.category for spec in GATES.values()})
    lines = ["QASM Gate Registry v1", "---------------------"]

    for category in categories:
        names = gate_names(category=category)
        lines.append(f"{category}: {len(names)}")
        lines.append("  " + ", ".join(names))

    return "\n".join(lines)


def describe_gate(name: str) -> str:
    spec = get_gate(name)

    lines = [
        f"name:        {spec.name}",
        f"qasm:        {spec.qasm_name}",
        f"qiskit:      {spec.qiskit_name}",
        f"category:    {spec.category}",
        f"kind:        {spec.kind}",
        f"arity:       {spec.arity}",
        f"params:      {spec.params}",
        f"aliases:     {spec.aliases}",
        f"geometry:    {spec.geometry}",
        f"description: {spec.description}",
    ]

    if spec.measurement_basis is not None:
        basis = spec.measurement_basis
        lines.extend(
            [
                "measurement basis:",
                f"  theta: {basis.theta}",
                f"  phi:   {basis.phi}",
                f"  label: {basis.label}",
                f"  axis:  {basis.pauli_axis}",
            ]
        )

    return "\n".join(lines)


def example_program() -> str:
    lines = [
        qasm_program_header(4),
        "",
        qasm_gate_call("h", [0]),
        qasm_gate_call("cx", [0, 1]),
        qasm_gate_call("swap", [2, 3]),
        qasm_gate_call("ccx", [0, 1, 2]),
        "",
        "// Measurement/listener-basis macro MX on q[0]",
        *compile_measurement_macro("mx", 0, 0),
        "",
        "// Measurement/listener-basis macro MY on q[1]",
        *compile_measurement_macro("my", 1, 1),
        "",
        "// Arbitrary listener basis MN(theta=pi/3, phi=pi/4) on q[2]",
        *compile_measurement_macro("mn", 2, 2, params=("pi/3", "pi/4")),
    ]

    return "\n".join(lines)


# ------------------------------------------------------------
# CLI self-test
# ------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OpenQASM / Qiskit / Composer gate registry."
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Print registry summary.",
    )

    parser.add_argument(
        "--gate",
        type=str,
        default=None,
        help="Describe one gate or operation.",
    )

    parser.add_argument(
        "--example",
        action="store_true",
        help="Print an example QASM program.",
    )

    parser.add_argument(
        "--menu-json",
        action="store_true",
        help="Print Max/menu-friendly gate metadata as JSON.",
    )

    parser.add_argument(
        "--exportable-only",
        action="store_true",
        help="With --menu-json, omit entries that cannot export to QASM yet.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list:
        print(registry_summary())
        return

    if args.gate:
        print(describe_gate(args.gate))
        return

    if args.example:
        print(example_program())
        return

    if args.menu_json:
        print(
            json.dumps(
                gate_menu_items(only_qasm_exportable=args.exportable_only),
                indent=2,
            )
        )
        return

    print(registry_summary())
    print()
    print("Try:")
    print("  python qasm_gate_registry_v1.py --gate swap")
    print("  python qasm_gate_registry_v1.py --gate toffoli")
    print("  python qasm_gate_registry_v1.py --gate mx")
    print("  python qasm_gate_registry_v1.py --example")
    print("  python qasm_gate_registry_v1.py --menu-json --exportable-only")


if __name__ == "__main__":
    main()
