from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from qmw.core import QuantumStateFrame


X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
PAULI_AXES = (X, Y, Z)


@dataclass(frozen=True)
class DescriptorVector:
    identifier: str
    names: tuple[str, ...]
    values: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, float]:
        return {
            name: float(value)
            for name, value in zip(self.names, self.values, strict=True)
        }


class QuantumDescriptorExtractor:
    """Convert a quantum state frame into a stable numeric descriptor vector."""

    names: tuple[str, ...] = (
        "global_purity",
        "global_entropy",
        "coherence_l1",
        "population_max",
        "population_spread",
        "participation",
        "mean_spin_x",
        "mean_spin_y",
        "mean_spin_z",
        "mean_spin_length",
        "spin_length_std",
        "mean_local_purity",
        "mean_local_entropy",
        "pair_xx_mean",
        "pair_yy_mean",
        "pair_zz_mean",
        "pair_abs_mean",
        "trajectory_speed",
        "trajectory_acceleration",
        "bohm_speed",
        "bohm_curvature",
        "measurement_entropy",
    )

    def extract(self, frame: QuantumStateFrame, identifier: str | None = None) -> DescriptorVector:
        rho = np.asarray(frame.rho, dtype=np.complex128)
        n_qubits = self._infer_n_qubits(rho)
        if n_qubits <= 0:
            return DescriptorVector(
                identifier=identifier or f"state_{frame.t:.6f}",
                names=self.names,
                values=np.zeros(len(self.names), dtype=float),
                metadata={"valid": False},
            )

        populations = np.clip(np.real(np.diag(rho)), 0.0, 1.0)
        pop_sum = float(np.sum(populations))
        if pop_sum > 1e-12:
            populations = populations / pop_sum

        local_bloch: list[tuple[float, float, float]] = []
        local_lengths: list[float] = []
        local_purities: list[float] = []
        local_entropies: list[float] = []

        for qubit in range(n_qubits):
            reduced = self._partial_trace(rho, (qubit,), n_qubits)
            bloch = self._bloch(reduced)
            length = math.sqrt(sum(axis * axis for axis in bloch))
            local_bloch.append(bloch)
            local_lengths.append(float(np.clip(length, 0.0, 1.0)))
            local_purities.append(float(np.trace(reduced @ reduced).real))
            local_entropies.append(self._entropy(reduced))

        pair_xx: list[float] = []
        pair_yy: list[float] = []
        pair_zz: list[float] = []
        pair_abs: list[float] = []
        for qubit_a in range(n_qubits):
            for qubit_b in range(qubit_a + 1, n_qubits):
                rho_pair = self._partial_trace(rho, (qubit_a, qubit_b), n_qubits)
                tensor = self._pair_spin_correlation_tensor(rho_pair)
                pair_xx.append(tensor[0])
                pair_yy.append(tensor[4])
                pair_zz.append(tensor[8])
                pair_abs.extend(abs(value) for value in tensor)

        bloch_array = np.asarray(local_bloch, dtype=float)
        descriptor = np.asarray(
            [
                float(np.trace(rho @ rho).real),
                self._entropy(rho),
                self._coherence_l1(rho),
                float(np.max(populations)) if populations.size else 0.0,
                float(np.std(populations)) if populations.size else 0.0,
                self._participation(populations),
                float(np.mean(bloch_array[:, 0])),
                float(np.mean(bloch_array[:, 1])),
                float(np.mean(bloch_array[:, 2])),
                float(np.mean(local_lengths)),
                float(np.std(local_lengths)),
                float(np.mean(local_purities)),
                float(np.mean(local_entropies)),
                float(np.mean(pair_xx)) if pair_xx else 0.0,
                float(np.mean(pair_yy)) if pair_yy else 0.0,
                float(np.mean(pair_zz)) if pair_zz else 0.0,
                float(np.mean(pair_abs)) if pair_abs else 0.0,
                self._observable(frame, "trajectory_speed"),
                self._observable(frame, "trajectory_acceleration"),
                self._observable(frame, "bohm_speed"),
                self._observable(frame, "bohm_curvature"),
                self._measurement_entropy(populations),
            ],
            dtype=float,
        )

        return DescriptorVector(
            identifier=identifier or f"state_{frame.t:.6f}",
            names=self.names,
            values=np.nan_to_num(descriptor, nan=0.0, posinf=1.0, neginf=-1.0),
            metadata={
                "valid": True,
                "time": float(frame.t),
                "n_qubits": n_qubits,
                "source_name": frame.source_name,
            },
        )

    @staticmethod
    def _observable(frame: QuantumStateFrame, name: str) -> float:
        value = frame.observable(name, 0.0)
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _infer_n_qubits(rho: np.ndarray) -> int:
        if rho.ndim != 2 or rho.shape[0] != rho.shape[1] or rho.shape[0] < 2:
            return 0
        n_qubits = int(round(math.log2(rho.shape[0])))
        return n_qubits if 2**n_qubits == rho.shape[0] else 0

    @staticmethod
    def _partial_trace(rho: np.ndarray, keep: tuple[int, ...], n_qubits: int) -> np.ndarray:
        keep = tuple(sorted(keep))
        tensor = rho.reshape((2,) * (2 * n_qubits))
        input_labels = list(range(n_qubits))
        for qubit in range(n_qubits):
            input_labels.append(qubit + n_qubits if qubit in keep else qubit)
        output_labels = list(keep) + [qubit + n_qubits for qubit in keep]
        reduced = np.einsum(tensor, input_labels, output_labels)
        dim = 2 ** len(keep)
        return reduced.reshape(dim, dim)

    @staticmethod
    def _bloch(rho_single: np.ndarray) -> tuple[float, float, float]:
        return (
            float(np.trace(rho_single @ X).real),
            float(np.trace(rho_single @ Y).real),
            float(np.trace(rho_single @ Z).real),
        )

    @staticmethod
    def _pair_spin_correlation_tensor(rho_pair: np.ndarray) -> list[float]:
        return [
            float(np.trace(rho_pair @ np.kron(axis_a, axis_b)).real)
            for axis_a in PAULI_AXES
            for axis_b in PAULI_AXES
        ]

    @staticmethod
    def _entropy(rho: np.ndarray) -> float:
        values = np.clip(np.linalg.eigvalsh(rho).real, 0.0, 1.0)
        values = values[values > 1e-12]
        if not values.size:
            return 0.0
        n_qubits = max(math.log2(rho.shape[0]), 1.0)
        return float(-np.sum(values * np.log2(values)) / n_qubits)

    @staticmethod
    def _measurement_entropy(populations: np.ndarray) -> float:
        values = populations[populations > 1e-12]
        if not values.size:
            return 0.0
        max_entropy = max(math.log2(len(populations)), 1.0)
        return float(-np.sum(values * np.log2(values)) / max_entropy)

    @staticmethod
    def _coherence_l1(rho: np.ndarray) -> float:
        off_diagonal = rho - np.diag(np.diag(rho))
        dim = max(rho.shape[0], 1)
        return float(np.sum(np.abs(off_diagonal)) / max(dim - 1, 1))

    @staticmethod
    def _participation(populations: np.ndarray) -> float:
        denom = float(np.sum(populations * populations))
        if denom <= 1e-12:
            return 0.0
        return float(np.clip((1.0 / denom) / len(populations), 0.0, 1.0))
