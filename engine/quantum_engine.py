from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any
import numpy as np

from .process_graph import ProcessNode, QuantumProcessGraph

EPS = 1e-12


@dataclass
class ProcessSnapshot:
    state_dimension: int
    bloch_vectors: list[tuple[float, float, float]]
    joint_pairs: list[dict[str, float]]
    shannon_entropy: float
    phase_dispersion: float
    phase_centroid: float
    process_complexity: float
    purity_proxy: float
    schmidt_proxy: float
    entangling_power: float
    material: dict[str, float]


class QuantumProcessEngine:
    """
    Qiskit-backed process engine.

    The quantum graph describes a feed-forward circuit.
    Sonic feedback belongs in the Max/MSP realization layer.
    """

    def __init__(self, num_qubits: int = 4, name: str = "qmw_process") -> None:
        if not 1 <= num_qubits <= 8:
            raise ValueError("Use 1–8 qubits for statevector process snapshots.")

        self.num_qubits = num_qubits
        self.graph = QuantumProcessGraph(name)
        self._circuit = None
        self._depth = 0
        self._last_by_qubit: dict[int, str] = {}
        self._gate_count = 0
        self._entangler_count = 0

    @property
    def circuit(self):
        if self._circuit is None:
            from qiskit import QuantumCircuit
            self._circuit = QuantumCircuit(self.num_qubits)
        return self._circuit

    def prepare_zero(self) -> None:
        node = ProcessNode(
            node_id="prepare_zero",
            kind="state",
            label="|0...0>",
            qubits=tuple(range(self.num_qubits)),
            depth=0,
        )

        self.graph.add_node(node)

        for q in range(self.num_qubits):
            self._last_by_qubit[q] = node.node_id

    def _add_gate_node(
        self,
        gate_name: str,
        qubits: tuple[int, ...],
        kind: str = "unitary",
        params: dict[str, Any] | None = None,
    ) -> str:
        node_id = f"{gate_name.lower()}_{self._gate_count:03d}"

        node = ProcessNode(
            node_id=node_id,
            kind=kind,
            label=gate_name,
            qubits=qubits,
            params=params or {},
            depth=self._depth,
        )

        self.graph.add_node(node)

        incoming = {
            self._last_by_qubit[q]
            for q in qubits
            if q in self._last_by_qubit
        }

        for previous in incoming:
            self.graph.connect(
                previous,
                node_id,
                relation="sequential",
                system="quantum",
            )

        for q in qubits:
            self._last_by_qubit[q] = node_id

        self._depth += 1
        self._gate_count += 1

        return node_id

    def h(self, qubit: int) -> None:
        self.circuit.h(qubit)
        self._add_gate_node("H", (qubit,), "unitary")

    def rz(self, theta: float, qubit: int) -> None:
        self.circuit.rz(theta, qubit)
        self._add_gate_node("RZ", (qubit,), "unitary", {"theta": theta})

    def rx(self, theta: float, qubit: int) -> None:
        self.circuit.rx(theta, qubit)
        self._add_gate_node("RX", (qubit,), "unitary", {"theta": theta})

    def ry(self, theta: float, qubit: int) -> None:
        self.circuit.ry(theta, qubit)
        self._add_gate_node("RY", (qubit,), "unitary", {"theta": theta})

    def cx(self, control: int, target: int) -> None:
        self.circuit.cx(control, target)
        self._add_gate_node("CX", (control, target), "entangler")
        self._entangler_count += 1

    def barrier(self) -> None:
        self.circuit.barrier()

    def add_sonic_feedback_node(
        self,
        source: str,
        target: str,
        label: str = "resonant_feedback",
    ) -> str:
        sonic_count = len(
            [node_id for node_id in self.graph.nodes if node_id.startswith("sonic_")]
        )

        node_id = f"sonic_{sonic_count:03d}"

        self.graph.add_node(
            ProcessNode(
                node_id=node_id,
                kind="sonic",
                label=label,
                depth=self._depth,
            )
        )

        self.graph.connect(source, node_id, relation="sonic", system="audio")
        self.graph.connect(node_id, target, relation="sonic", system="audio")

        return node_id

    def snapshot(self) -> ProcessSnapshot:
        from qiskit.quantum_info import Statevector

        psi = np.asarray(
            Statevector.from_instruction(self.circuit).data,
            dtype=np.complex128,
        )

        n = self.num_qubits
        probabilities = np.abs(psi) ** 2

        shannon_entropy = float(
            -np.sum(probabilities * np.log2(probabilities + EPS)) / max(1, n)
        )

        phases = np.angle(psi)
        weights = probabilities / max(float(np.sum(probabilities)), EPS)

        phase_centroid = float(
            np.angle(np.sum(weights * np.exp(1j * phases)))
        )

        phase_dispersion = float(
            1.0 - np.abs(np.sum(weights * np.exp(1j * phases)))
        )

        bloch_vectors = [self._bloch_vector(psi, q) for q in range(n)]

        joint_pairs = []

        for q0, q1 in combinations(range(n), 2):
            rho2 = self._reduced_density_matrix(psi, [q0, q1])
            rho0 = self._reduced_density_matrix(psi, [q0])
            rho1 = self._reduced_density_matrix(psi, [q1])

            entropy0 = self._von_neumann_entropy(rho0)
            entropy1 = self._von_neumann_entropy(rho1)
            entropy2 = self._von_neumann_entropy(rho2)

            mutual_information = max(0.0, entropy0 + entropy1 - entropy2)

            zz_correlation = self._expectation_pauli(
                psi,
                {q0: "Z", q1: "Z"},
            )

            shared_resonance = float(
                np.clip(
                    0.5 * mutual_information + 0.5 * abs(zz_correlation),
                    0.0,
                    1.0,
                )
            )

            joint_pairs.append(
                {
                    "q0": q0,
                    "q1": q1,
                    "mutual_information": float(mutual_information),
                    "zz_correlation": float(zz_correlation),
                    "shared_resonance": shared_resonance,
                }
            )

        local_purities = []

        for q in range(n):
            rho = self._reduced_density_matrix(psi, [q])
            local_purities.append(float(np.real(np.trace(rho @ rho))))

        purity_proxy = float(np.mean(local_purities))
        entangling_power = float(1.0 - purity_proxy)

        max_pair_mi = max(
            (pair["mutual_information"] for pair in joint_pairs),
            default=0.0,
        )

        schmidt_proxy = float(np.clip(max_pair_mi, 0.0, 1.0))

        process_complexity = float(
            np.clip(
                0.35 * (self._depth / max(1, self._depth + 4))
                + 0.35 * (
                    self._entangler_count / max(1, self.num_qubits - 1)
                )
                + 0.30 * phase_dispersion,
                0.0,
                1.0,
            )
        )

        material = self._material_map(
            shannon=shannon_entropy,
            phase_dispersion=phase_dispersion,
            process_complexity=process_complexity,
            entangling_power=entangling_power,
            pairs=joint_pairs,
        )

        return ProcessSnapshot(
            state_dimension=2**n,
            bloch_vectors=bloch_vectors,
            joint_pairs=joint_pairs,
            shannon_entropy=shannon_entropy,
            phase_dispersion=phase_dispersion,
            phase_centroid=phase_centroid,
            process_complexity=process_complexity,
            purity_proxy=purity_proxy,
            schmidt_proxy=schmidt_proxy,
            entangling_power=entangling_power,
            material=material,
        )

    def _material_map(
        self,
        shannon: float,
        phase_dispersion: float,
        process_complexity: float,
        entangling_power: float,
        pairs: list[dict[str, float]],
    ) -> dict[str, float]:
        shared = (
            float(np.mean([pair["shared_resonance"] for pair in pairs]))
            if pairs
            else 0.0
        )

        return {
            "mode_family": int(
                np.clip(round(1 + 6 * process_complexity), 1, 7)
            ),
            "decay": float(np.clip(0.20 + 0.75 * shared, 0.0, 0.98)),
            "brightness": float(
                np.clip(0.15 + 0.85 * phase_dispersion, 0.0, 1.0)
            ),
            "damping": float(np.clip(0.92 - 0.75 * shannon, 0.05, 0.98)),
            "density": float(np.clip(0.10 + 0.90 * shannon, 0.0, 1.0)),
            "space": float(
                np.clip(0.10 + 0.90 * entangling_power, 0.0, 1.0)
            ),
        }

    def _bloch_vector(
        self,
        psi: np.ndarray,
        qubit: int,
    ) -> tuple[float, float, float]:
        x = self._expectation_pauli(psi, {qubit: "X"})
        y = self._expectation_pauli(psi, {qubit: "Y"})
        z = self._expectation_pauli(psi, {qubit: "Z"})

        return float(x), float(y), float(z)

    def _expectation_pauli(
        self,
        psi: np.ndarray,
        ops: dict[int, str],
    ) -> float:
        out = np.zeros_like(psi)

        for index, amplitude in enumerate(psi):
            target = index
            phase = 1.0 + 0.0j

            for qubit, operator in ops.items():
                bit = (index >> qubit) & 1

                if operator == "Z":
                    phase *= 1 if bit == 0 else -1

                elif operator == "X":
                    target ^= 1 << qubit

                elif operator == "Y":
                    target ^= 1 << qubit
                    phase *= 1j if bit == 0 else -1j

                else:
                    raise ValueError(
                        f"Unsupported Pauli operator: {operator}"
                    )

            out[target] += phase * amplitude

        return float(np.real(np.vdot(psi, out)))

    def _reduced_density_matrix(
        self,
        psi: np.ndarray,
        keep_qubits: list[int],
    ) -> np.ndarray:
        n = self.num_qubits
        keep = list(keep_qubits)
        trace_out = [q for q in range(n) if q not in keep]

        psi_tensor = psi.reshape([2] * n)

        # Qiskit qubit 0 is the least-significant basis bit.
        keep_axes = [n - 1 - q for q in keep]
        trace_axes = [n - 1 - q for q in trace_out]

        permutation = keep_axes + trace_axes
        arranged = np.transpose(psi_tensor, permutation)

        dim_keep = 2 ** len(keep)
        dim_trace = 2 ** len(trace_out)

        matrix = arranged.reshape(dim_keep, dim_trace)

        return matrix @ matrix.conj().T

    @staticmethod
    def _von_neumann_entropy(rho: np.ndarray) -> float:
        eigenvalues = np.linalg.eigvalsh(rho)
        eigenvalues = np.clip(np.real(eigenvalues), 0.0, 1.0)

        return float(
            -np.sum(eigenvalues * np.log2(eigenvalues + EPS))
        )