from __future__ import annotations

import math
from collections import deque
from typing import Any, Deque

import numpy as np

from qmw.core import QuantumStateFrame


X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
PAULI_AXES = (X, Y, Z)
PAULI_BY_NAME = {
    "I": np.eye(2, dtype=np.complex128),
    "X": X,
    "Y": Y,
    "Z": Z,
}


class SpinView:
    """Publish live density-derived local spin and pair spin correlations."""

    def __init__(self, trail_length: int = 48) -> None:
        self.trail_length = trail_length
        self._trails: dict[int, Deque[tuple[float, float, float]]] = {}
        self._previous: dict[int, tuple[float, float, float]] = {}
        self._step_count = 0

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        rho = np.asarray(frame.rho, dtype=np.complex128)
        n_qubits = self._infer_n_qubits(rho)
        if n_qubits <= 0:
            return

        dt = max(float(frame.dt), 1e-9)
        qubit_data: list[dict[str, float]] = []

        for qubit in range(n_qubits):
            reduced = self._partial_trace(rho, (qubit,), n_qubits)
            bx, by, bz = self._bloch(reduced)
            vector = (bx, by, bz)
            length = float(np.clip(math.sqrt(bx * bx + by * by + bz * bz), 0.0, 1.0))
            phase = float(math.atan2(by, bx))
            theta = float(math.acos(np.clip(bz / max(length, 1e-9), -1.0, 1.0)))
            phi = phase
            basis_theta, basis_phi = self._legacy_basis_angles(frame.t)
            basis_projection = self._basis_projection(
                bx,
                by,
                bz,
                basis_theta,
                basis_phi,
            )
            purity = float(np.trace(reduced @ reduced).real)
            entropy = self._entropy(reduced)
            previous = self._previous.get(qubit)
            speed = 0.0 if previous is None else math.dist(vector, previous) / dt
            self._previous[qubit] = vector

            trail = self._trails.setdefault(qubit, deque(maxlen=self.trail_length))
            trail.append(vector)
            trail_payload: list[float] = []
            for x, y, z in trail:
                trail_payload.extend([x, y, z])

            s1 = bz
            s2 = bx
            s3 = by
            degree = length
            azimuth = 0.5 * math.atan2(s2, s1)
            ellipticity = 0.5 * math.asin(float(np.clip(s3 / max(degree, 1e-9), -1.0, 1.0)))
            circularity = abs(s3)
            linearity = float(np.clip(math.sqrt(s1 * s1 + s2 * s2), 0.0, 1.0))
            audio_phase = phi / math.pi
            audio_swirl = by
            audio_interference = bx
            audio_brightness = 0.5 * (bz + 1.0)
            qubit_data.append(
                {
                    "x": bx,
                    "y": by,
                    "z": bz,
                    "degree": degree,
                    "circularity": circularity,
                    "linearity": linearity,
                    "basis_projection": basis_projection,
                    "audio_phase": audio_phase,
                    "audio_swirl": audio_swirl,
                    "audio_interference": audio_interference,
                    "audio_brightness": audio_brightness,
                }
            )

            payloads = {
                f"/qmw/spin/q{qubit}/bloch": [bx, by, bz],
                f"/qmw/spin/q{qubit}/length": length,
                f"/qmw/spin/q{qubit}/phase": phase,
                f"/qmw/spin/q{qubit}/purity": purity,
                f"/qmw/spin/q{qubit}/entropy": entropy,
                f"/qmw/spin/q{qubit}/speed": speed,
                f"/qmw/spin/q{qubit}/trail": trail_payload,
                f"/spin/{qubit}/x": bx,
                f"/spin/{qubit}/y": by,
                f"/spin/{qubit}/z": bz,
                f"/spin/{qubit}/phase": phase,
                f"/spin/{qubit}/speed": speed,
                f"/qubit/{qubit}/x": bx,
                f"/qubit/{qubit}/y": by,
                f"/qubit/{qubit}/z": bz,
                f"/qubit/{qubit}/stokes/s1": s1,
                f"/qubit/{qubit}/stokes/s2": s2,
                f"/qubit/{qubit}/stokes/s3": s3,
                f"/qubit/{qubit}/polarization/degree": degree,
                f"/qubit/{qubit}/polarization/azimuth": azimuth,
                f"/qubit/{qubit}/polarization/ellipticity": ellipticity,
                f"/qubit/{qubit}/polarization/circularity": circularity,
                f"/qubit/{qubit}/polarization/linearity": linearity,
                f"/qubit/{qubit}/bloch/r": length,
                f"/qubit/{qubit}/bloch/theta": theta,
                f"/qubit/{qubit}/bloch/phi": phi,
                f"/qubit/{qubit}/basis/theta": basis_theta,
                f"/qubit/{qubit}/basis/phi": basis_phi,
                f"/qubit/{qubit}/basis/projection": basis_projection,
                f"/qubit/{qubit}/audio/phase": audio_phase,
                f"/qubit/{qubit}/audio/swirl": audio_swirl,
                f"/qubit/{qubit}/audio/interference": audio_interference,
                f"/qubit/{qubit}/audio/brightness": audio_brightness,
            }
            for address, value in payloads.items():
                osc.send_message(address, value)
                visual_osc.send_message(address, value)

        basis_theta, basis_phi = self._legacy_basis_angles(frame.t)
        global_payloads = {
            "/global/spin/x": self._mean(qubit_data, "x"),
            "/global/spin/y": self._mean(qubit_data, "y"),
            "/global/spin/z": self._mean(qubit_data, "z"),
            "/global/polarization/degree": self._mean(qubit_data, "degree"),
            "/global/polarization/circularity": self._mean(qubit_data, "circularity"),
            "/global/polarization/linearity": self._mean(qubit_data, "linearity"),
            "/global/basis/theta": basis_theta,
            "/global/basis/phi": basis_phi,
            "/global/basis/projection": self._mean(qubit_data, "basis_projection"),
            "/global/audio/phase": self._mean(qubit_data, "audio_phase"),
            "/global/audio/swirl": self._mean(qubit_data, "audio_swirl"),
            "/global/audio/interference": self._mean(qubit_data, "audio_interference"),
            "/global/audio/brightness": self._mean(qubit_data, "audio_brightness"),
        }
        for address, value in global_payloads.items():
            osc.send_message(address, value)
            visual_osc.send_message(address, value)

        for name, value in self._selected_pauli_strings(rho, n_qubits).items():
            osc.send_message(f"/pauli/{name}", value)
            visual_osc.send_message(f"/pauli/{name}", value)

        osc.send_message("/engine/time", float(frame.t))
        osc.send_message("/engine/step", self._step_count)
        visual_osc.send_message("/engine/time", float(frame.t))
        visual_osc.send_message("/engine/step", self._step_count)
        self._step_count += 1

        for qubit_a in range(n_qubits):
            for qubit_b in range(qubit_a + 1, n_qubits):
                rho_pair = self._partial_trace(rho, (qubit_a, qubit_b), n_qubits)
                tensor = self._pair_spin_correlation_tensor(rho_pair)
                payloads = {
                    f"/qmw/spin/pair/{qubit_a}_{qubit_b}/correlation": tensor,
                    f"/qmw/spin/pair/{qubit_a}_{qubit_b}/xx_yy_zz": [
                        tensor[0],
                        tensor[4],
                        tensor[8],
                    ],
                }
                for address, value in payloads.items():
                    osc.send_message(address, value)
                    visual_osc.send_message(address, value)

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
    def _entropy(rho: np.ndarray) -> float:
        values = np.clip(np.linalg.eigvalsh(rho).real, 0.0, 1.0)
        values = values[values > 1e-12]
        return float(-np.sum(values * np.log2(values))) if values.size else 0.0

    @staticmethod
    def _pair_spin_correlation_tensor(rho_pair: np.ndarray) -> list[float]:
        return [
            float(np.trace(rho_pair @ np.kron(axis_a, axis_b)).real)
            for axis_a in PAULI_AXES
            for axis_b in PAULI_AXES
        ]

    @staticmethod
    def _legacy_basis_angles(t: float) -> tuple[float, float]:
        theta = 0.65 * math.sin(2.0 * math.pi * 0.031 * float(t))
        phi = 1.0 * math.sin(2.0 * math.pi * 0.047 * float(t))
        return theta, phi

    @staticmethod
    def _basis_projection(
        x: float,
        y: float,
        z: float,
        theta: float,
        phi: float,
    ) -> float:
        nx = math.sin(theta) * math.cos(phi)
        ny = math.sin(theta) * math.sin(phi)
        nz = math.cos(theta)
        return float(np.clip(x * nx + y * ny + z * nz, -1.0, 1.0))

    @staticmethod
    def _mean(items: list[dict[str, float]], key: str) -> float:
        return float(np.mean([item[key] for item in items])) if items else 0.0

    @classmethod
    def _selected_pauli_strings(
        cls,
        rho: np.ndarray,
        n_qubits: int,
    ) -> dict[str, float]:
        names = ["ZZII", "XXII", "YYII", "ZIZI", "IZIZ", "ZZZZ", "XXXX", "YYYY"]
        values: dict[str, float] = {}
        for name in names:
            if len(name) != n_qubits:
                continue
            operator = cls._pauli_string_operator(name)
            values[name] = float(np.clip(np.trace(rho @ operator).real, -1.0, 1.0))
        return values

    @staticmethod
    def _pauli_string_operator(name: str) -> np.ndarray:
        result = PAULI_BY_NAME[name[0]]
        for symbol in name[1:]:
            result = np.kron(result, PAULI_BY_NAME[symbol])
        return result
