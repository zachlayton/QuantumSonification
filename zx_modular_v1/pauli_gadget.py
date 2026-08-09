"""Four-qubit Pauli-gadget semantics shared by Processing, PyZX, and OSC."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


PAULI_MATRICES = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


@dataclass(frozen=True)
class PauliGadgetVerification:
    label: str
    theta: float
    weight: int
    verified: bool
    absolute_error: float
    message: str


@dataclass(frozen=True)
class PauliGadgetSpec:
    gadget_id: int
    label: str
    theta: float


@dataclass(frozen=True)
class PauliScoreVerification:
    gadget_count: int
    verified: bool
    absolute_error: float
    message: str


def normalize_pauli_label(label: str, *, allow_identity: bool = False) -> str:
    """Validate a q0,q1,q2,q3 Pauli label such as ``XYZI``."""
    normalized = str(label).strip().upper()
    if len(normalized) != 4 or any(axis not in "IXYZ" for axis in normalized):
        raise ValueError("Pauli label must contain exactly four I/X/Y/Z symbols")
    if not allow_identity and normalized == "IIII":
        raise ValueError("IIII is the identity, not a phase gadget")
    return normalized


def pauli_weight(label: str) -> int:
    return sum(axis != "I" for axis in normalize_pauli_label(label, allow_identity=True))


def pauli_operator(label: str) -> np.ndarray:
    """Return the operator in the project's q3⊗q2⊗q1⊗q0 basis order."""
    normalized = normalize_pauli_label(label, allow_identity=True)
    operator = PAULI_MATRICES[normalized[3]]
    for logical_qubit in (2, 1, 0):
        operator = np.kron(operator, PAULI_MATRICES[normalized[logical_qubit]])
    return operator


def pauli_rotation_matrix(label: str, theta: float) -> np.ndarray:
    """Return exp(-i theta P / 2) without requiring SciPy."""
    operator = pauli_operator(label)
    half_angle = 0.5 * float(theta)
    return (
        math.cos(half_angle) * np.eye(16, dtype=complex)
        - 1j * math.sin(half_angle) * operator
    )


def pauli_strings_commute(left: str, right: str) -> bool:
    """Return whether two Pauli strings commute."""
    a = normalize_pauli_label(left, allow_identity=True)
    b = normalize_pauli_label(right, allow_identity=True)
    anticommuting_sites = sum(
        x != "I" and y != "I" and x != y
        for x, y in zip(a, b)
    )
    return anticommuting_sites % 2 == 0


def pauli_score_matrix(gadgets: list[PauliGadgetSpec]) -> np.ndarray:
    """Compose an ordered left-to-right score of Pauli rotations."""
    matrix = np.eye(16, dtype=complex)
    for gadget in gadgets:
        matrix = pauli_rotation_matrix(gadget.label, gadget.theta) @ matrix
    return matrix


def can_fuse_score_gadgets(
    gadgets: list[PauliGadgetSpec],
    first_index: int,
    second_index: int,
) -> bool:
    """Check whether equal gadgets can commute together and fuse."""
    low, high = sorted((int(first_index), int(second_index)))
    if low < 0 or high >= len(gadgets) or low == high:
        return False
    left = gadgets[low]
    right = gadgets[high]
    if normalize_pauli_label(left.label) != normalize_pauli_label(right.label):
        return False
    return all(
        pauli_strings_commute(left.label, gadgets[index].label)
        for index in range(low + 1, high)
    )


def fuse_score_gadgets(
    gadgets: list[PauliGadgetSpec],
    first_index: int,
    second_index: int,
) -> list[PauliGadgetSpec]:
    """Fuse equal gadgets after proving every intervening move commutes."""
    if not can_fuse_score_gadgets(gadgets, first_index, second_index):
        raise ValueError(
            "gadgets must have equal labels and commute through every intervening gadget"
        )
    low, high = sorted((int(first_index), int(second_index)))
    result = list(gadgets)
    result[low] = PauliGadgetSpec(
        result[low].gadget_id,
        normalize_pauli_label(result[low].label),
        float(result[low].theta + result[high].theta),
    )
    del result[high]
    return result


def pauli_expectation(rho: np.ndarray, label: str) -> float:
    """Calculate the real tomography coefficient Tr(rho P)."""
    matrix = np.asarray(rho, dtype=complex)
    if matrix.shape != (16, 16):
        raise ValueError("four-qubit density matrix must have shape (16, 16)")
    value = np.trace(matrix @ pauli_operator(label))
    if abs(float(value.imag)) > 1e-8:
        raise ValueError("Pauli expectation acquired an unexpected imaginary part")
    return float(value.real)


def verify_visual_pauli_gadget(
    visual_graph,
    label: str,
    theta: float,
    *,
    atol: float = 1e-8,
) -> PauliGadgetVerification:
    """Use PyZX's tensor evaluator to check a complete visual gadget."""
    normalized = normalize_pauli_label(label)
    expected = pauli_rotation_matrix(normalized, theta)
    try:
        actual = visual_graph._to_pyzx().to_matrix(preserve_scalar=True)
        if actual.shape != expected.shape:
            raise ValueError(
                f"gadget has matrix shape {actual.shape}, expected {expected.shape}"
            )
        absolute_error = float(np.linalg.norm(actual - expected))
        scale = max(1.0, float(np.linalg.norm(expected)))
        verified = absolute_error <= atol * scale
        message = (
            f"{normalized} verified exactly against exp(-i theta P/2)"
            if verified
            else f"{normalized} differs from its Pauli rotation"
        )
        return PauliGadgetVerification(
            normalized,
            float(theta),
            pauli_weight(normalized),
            verified,
            absolute_error,
            message,
        )
    except (ImportError, KeyError, TypeError, ValueError) as exc:
        return PauliGadgetVerification(
            normalized,
            float(theta),
            pauli_weight(normalized),
            False,
            math.inf,
            str(exc),
        )


def verify_visual_pauli_score(
    visual_graph,
    gadgets: list[PauliGadgetSpec],
    *,
    atol: float = 1e-8,
) -> PauliScoreVerification:
    """Verify the complete ordered product represented by a visual graph."""
    if not gadgets:
        return PauliScoreVerification(
            0,
            False,
            math.inf,
            "Pauli score must contain at least one gadget",
        )
    normalized = [
        PauliGadgetSpec(
            int(gadget.gadget_id),
            normalize_pauli_label(gadget.label),
            float(gadget.theta),
        )
        for gadget in gadgets
    ]
    try:
        actual = visual_graph._to_pyzx().to_matrix(preserve_scalar=True)
        expected = pauli_score_matrix(normalized)
        if actual.shape != expected.shape:
            raise ValueError(
                f"score has matrix shape {actual.shape}, expected {expected.shape}"
            )
        absolute_error = float(np.linalg.norm(actual - expected))
        scale = max(1.0, float(np.linalg.norm(expected)))
        verified = absolute_error <= atol * scale
        labels = " · ".join(gadget.label for gadget in normalized)
        return PauliScoreVerification(
            len(normalized),
            verified,
            absolute_error,
            (
                f"ordered Pauli score verified exactly: {labels}"
                if verified
                else f"ordered Pauli score differs from its rotation product: {labels}"
            ),
        )
    except (ImportError, KeyError, TypeError, ValueError) as exc:
        return PauliScoreVerification(
            len(normalized),
            False,
            math.inf,
            str(exc),
        )
