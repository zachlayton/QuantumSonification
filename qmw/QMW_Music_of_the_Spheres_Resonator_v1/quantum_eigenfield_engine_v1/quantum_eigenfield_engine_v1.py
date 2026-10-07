#!/usr/bin/env python3
"""Quantum Eigenfield Engine v1.

Projects a finite-dimensional quantum state into the intrinsic eigenmodes of
an emergent geometry.

The engine does not identify Hilbert-space eigenvectors with geometric
eigenfunctions. Those spaces generally have different dimensions and meanings.
Instead it constructs an explicit coupling matrix C between them:

    quantum state rho
        -> quantum modal coordinates
        -> coupling matrix C
        -> geometric mode amplitudes
        -> spatial eigenfield
        -> optional developmental drive

Inputs
------
1. A density matrix rho with shape (d, d), typically d=16 for four qubits.
2. A spectral-geometry NPZ produced by spectral_geometry_v1.py containing:
       eigenvalues
       eigenvectors
       frequencies_hz
       vertices
       faces

Outputs
-------
- quantum eigenvalues/eigenvectors
- Pauli expectation features when d is a power of two
- geometric mode weights
- complex geometric mode amplitudes
- real spatial eigenfield
- normalized developmental drive
- JSON descriptor report
- compressed NPZ state

Dependencies
------------
numpy
scipy
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import json
from typing import Any, Mapping

import numpy as np
from scipy.linalg import expm


PAULI = {
    "I": np.array([[1, 0], [0, 1]], dtype=np.complex128),
    "X": np.array([[0, 1], [1, 0]], dtype=np.complex128),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
    "Z": np.array([[1, 0], [0, -1]], dtype=np.complex128),
}


@dataclass(frozen=True)
class QuantumEigenfieldConfig:
    n_geometric_modes: int = 32
    coupling_mode: str = "hybrid"
    coupling_seed: int = 23
    temperature: float = 1.0
    purity_sharpness: float = 1.0
    entropy_spread: float = 1.0
    coherence_gain: float = 1.0
    pauli_gain: float = 0.35
    spectral_decay: float = 0.35
    phase_gain: float = 1.0
    developmental_gain: float = 1.0
    developmental_bias: float = 0.0


@dataclass
class QuantumStateDescriptors:
    dimension: int
    n_qubits: int | None
    purity: float
    entropy_bits: float
    max_mixed_entropy_bits: float
    coherence_l1: float
    dominant_population: float
    eigenvalues: np.ndarray

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "n_qubits": self.n_qubits,
            "purity": self.purity,
            "entropy_bits": self.entropy_bits,
            "max_mixed_entropy_bits": self.max_mixed_entropy_bits,
            "coherence_l1": self.coherence_l1,
            "dominant_population": self.dominant_population,
            "eigenvalues": self.eigenvalues.tolist(),
        }


def validate_density_matrix(rho: np.ndarray, atol: float = 1e-8) -> np.ndarray:
    rho = np.asarray(rho, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("density matrix must be square")

    hermitian_error = np.max(np.abs(rho - rho.conj().T))
    if hermitian_error > 1e-6:
        raise ValueError(
            f"density matrix is not Hermitian; max error={hermitian_error:.3e}"
        )

    trace = np.trace(rho)
    if abs(trace) < atol:
        raise ValueError("density matrix trace is zero")
    rho = rho / trace

    eigenvalues = np.linalg.eigvalsh(rho)
    if np.min(eigenvalues) < -1e-6:
        raise ValueError(
            f"density matrix is not positive semidefinite; "
            f"minimum eigenvalue={np.min(eigenvalues):.3e}"
        )

    # Remove tiny numerical negativity and reconstruct.
    values, vectors = np.linalg.eigh(rho)
    values = np.clip(np.real(values), 0.0, None)
    values /= max(float(np.sum(values)), atol)
    rho = (vectors * values[None, :]) @ vectors.conj().T
    return rho


def infer_qubits(dimension: int) -> int | None:
    n = int(round(np.log2(dimension)))
    return n if 2**n == dimension else None


def von_neumann_entropy(rho: np.ndarray) -> float:
    values = np.clip(np.linalg.eigvalsh(rho).real, 1e-15, 1.0)
    return float(-np.sum(values * np.log2(values)))


def density_descriptors(rho: np.ndarray) -> QuantumStateDescriptors:
    values = np.sort(np.linalg.eigvalsh(rho).real)[::-1]
    d = rho.shape[0]
    off_diagonal = rho - np.diag(np.diag(rho))
    return QuantumStateDescriptors(
        dimension=d,
        n_qubits=infer_qubits(d),
        purity=float(np.real(np.trace(rho @ rho))),
        entropy_bits=von_neumann_entropy(rho),
        max_mixed_entropy_bits=float(np.log2(d)),
        coherence_l1=float(np.sum(np.abs(off_diagonal))),
        dominant_population=float(np.max(np.real(np.diag(rho)))),
        eigenvalues=values,
    )


def pauli_operator(label: str) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for symbol in label:
        if symbol not in PAULI:
            raise ValueError(f"unknown Pauli symbol {symbol!r}")
        result = np.kron(result, PAULI[symbol])
    return result


def selected_pauli_labels(n_qubits: int) -> list[str]:
    labels: list[str] = []

    # Local axes.
    for q in range(n_qubits):
        for axis in "XYZ":
            chars = ["I"] * n_qubits
            chars[q] = axis
            labels.append("".join(chars))

    # Pairwise same-axis correlations.
    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            for axis in "XYZ":
                chars = ["I"] * n_qubits
                chars[i] = axis
                chars[j] = axis
                labels.append("".join(chars))

    # Global strings.
    labels.extend([axis * n_qubits for axis in "XYZ"])
    return list(dict.fromkeys(labels))


def pauli_expectations(
    rho: np.ndarray,
    labels: list[str] | None = None,
) -> dict[str, float]:
    n_qubits = infer_qubits(rho.shape[0])
    if n_qubits is None:
        return {}
    labels = selected_pauli_labels(n_qubits) if labels is None else labels
    result: dict[str, float] = {}
    for label in labels:
        operator = pauli_operator(label)
        result[label] = float(np.real(np.trace(rho @ operator)))
    return result


def load_density_matrix(path: str | Path, key: str = "rho") -> np.ndarray:
    path = Path(path)
    if path.suffix.lower() == ".npy":
        return validate_density_matrix(np.load(path))
    if path.suffix.lower() == ".npz":
        payload = np.load(path)
        if key in payload:
            return validate_density_matrix(payload[key])
        candidates = [name for name in payload.files if payload[name].ndim == 2]
        if not candidates:
            raise ValueError(f"NPZ contains no matrix: {path}")
        return validate_density_matrix(payload[candidates[0]])
    raise ValueError("density matrix must be .npy or .npz")


def load_modal_packet(path: str | Path) -> dict[str, Any]:
    """Load either a spectral-geometry or surface-material modal packet."""
    with np.load(path, allow_pickle=False) as payload:
        result: dict[str, Any] = {
            name: payload[name] for name in payload.files
        }
    metadata_key = (
        "material_metadata_json"
        if "material_metadata_json" in result
        else "metadata_json" if "metadata_json" in result else None
    )
    if metadata_key is not None:
        result["metadata"] = json.loads(
            str(np.asarray(result[metadata_key]).item())
        )
    if "model" not in result and "material_model" not in result:
        if "geometry_kind" in result:
            result["model"] = result["geometry_kind"]
    if "damping_rates" not in result and "damping" in result:
        result["damping_rates"] = result["damping"]
    eigenvalue_key = (
        "eigenvalues"
        if "eigenvalues" in result
        else "geometric_eigenvalues"
    )
    eigenvector_key = (
        "eigenvectors"
        if "eigenvectors" in result
        else "geometric_eigenvectors"
    )
    if eigenvalue_key not in result or eigenvector_key not in result:
        raise ValueError(
            "modal NPZ requires eigenvalues/eigenvectors or "
            "geometric_eigenvalues/geometric_eigenvectors"
        )
    result["eigenvalues"] = result[eigenvalue_key]
    result["eigenvectors"] = result[eigenvector_key]
    eigenvectors = result["eigenvectors"]
    eigenvalues = result["eigenvalues"]
    if eigenvectors.ndim != 2:
        raise ValueError("eigenvectors must have shape (vertices, modes)")
    if eigenvalues.ndim != 1:
        raise ValueError("eigenvalues must be one-dimensional")
    return result


def load_spectral_geometry(path: str | Path) -> dict[str, Any]:
    """Backward-compatible alias for older callers."""
    return load_modal_packet(path)


def _modal_packet_mapping(packet: Any) -> dict[str, Any]:
    if isinstance(packet, Mapping):
        return dict(packet)
    names = (
        "model",
        "material_model",
        "geometry_kind",
        "eigenvalues",
        "eigenvectors",
        "geometric_eigenvalues",
        "geometric_eigenvectors",
        "frequencies_hz",
        "angular_frequencies",
        "decay_times_seconds",
        "t60_seconds",
        "damping_rates",
        "damping",
        "mode_weights",
        "metadata",
    )
    return {
        name: getattr(packet, name)
        for name in names
        if hasattr(packet, name)
    }


def _text_scalar(value: Any, default: str) -> str:
    if value is None:
        return default
    array = np.asarray(value)
    return str(array.item() if array.ndim == 0 else value)


class QuantumEigenfieldEngine:
    """Map quantum organization into geometric eigenmode organization."""

    def __init__(
        self,
        rho: np.ndarray,
        geometric_eigenvalues: np.ndarray | None = None,
        geometric_eigenvectors: np.ndarray | None = None,
        config: QuantumEigenfieldConfig = QuantumEigenfieldConfig(),
        modal_packet: Mapping[str, Any] | Any | None = None,
    ) -> None:
        self.rho = validate_density_matrix(rho)
        self.config = config

        modal: dict[str, Any] = {}
        if modal_packet is not None:
            modal = _modal_packet_mapping(modal_packet)
        elif geometric_eigenvectors is None and geometric_eigenvalues is not None:
            candidate = _modal_packet_mapping(geometric_eigenvalues)
            if "eigenvectors" in candidate or "geometric_eigenvectors" in candidate:
                modal = candidate
                geometric_eigenvalues = None

        if modal:
            geometric_eigenvalues = modal.get(
                "eigenvalues", modal.get("geometric_eigenvalues")
            )
            geometric_eigenvectors = modal.get(
                "eigenvectors", modal.get("geometric_eigenvectors")
            )
        if geometric_eigenvalues is None or geometric_eigenvectors is None:
            raise ValueError(
                "geometric eigenvalues and eigenvectors, or a modal packet, are required"
            )

        eigenvalues = np.asarray(geometric_eigenvalues, dtype=np.float64)
        eigenvectors = np.asarray(geometric_eigenvectors, dtype=np.float64)
        if eigenvectors.shape[1] != len(eigenvalues):
            raise ValueError("geometric eigenvalue/eigenvector count mismatch")

        mode_count = min(
            config.n_geometric_modes,
            len(eigenvalues),
            eigenvectors.shape[1],
        )
        if mode_count < 1:
            raise ValueError("at least one geometric mode is required")

        self.geometric_eigenvalues = eigenvalues[:mode_count]
        self.geometric_eigenvectors = eigenvectors[:, :mode_count]
        self.material_model = _text_scalar(
            modal.get(
                "model",
                modal.get("material_model", modal.get("geometry_kind")),
            ),
            "spectral_geometry",
        )
        metadata = modal.get("metadata", {})
        if not metadata and modal.get("metadata_json") is not None:
            metadata = json.loads(
                str(np.asarray(modal["metadata_json"]).item())
            )
        self.material_metadata = dict(metadata)

        def optional_modes(name: str) -> np.ndarray | None:
            value = modal.get(name)
            if value is None:
                return None
            values = np.asarray(value, dtype=np.float64).reshape(-1)
            if len(values) == 0:
                return None
            if len(values) < mode_count:
                raise ValueError(
                    f"modal field {name!r} has {len(values)} values; "
                    f"expected at least {mode_count}"
                )
            return values[:mode_count]

        self.material_frequencies_hz = optional_modes("frequencies_hz")
        self.material_angular_frequencies = optional_modes(
            "angular_frequencies"
        )
        self.material_decay_times_seconds = optional_modes(
            "decay_times_seconds"
        )
        self.material_t60_seconds = optional_modes("t60_seconds")
        self.material_damping_rates = optional_modes("damping_rates")
        if self.material_damping_rates is None:
            self.material_damping_rates = optional_modes("damping")
        if (
            self.material_angular_frequencies is None
            and self.material_frequencies_hz is not None
        ):
            self.material_angular_frequencies = (
                2.0 * np.pi * self.material_frequencies_hz
            )
        if (
            self.material_decay_times_seconds is None
            and self.material_damping_rates is not None
        ):
            self.material_decay_times_seconds = 1.0 / np.maximum(
                self.material_damping_rates, 1e-12
            )
        if self.material_t60_seconds is None:
            if self.material_damping_rates is not None:
                self.material_t60_seconds = np.log(1000.0) / np.maximum(
                    self.material_damping_rates, 1e-12
                )
            elif self.material_decay_times_seconds is not None:
                self.material_t60_seconds = (
                    np.log(1000.0) * self.material_decay_times_seconds
                )
        self.material_mode_weights = optional_modes("mode_weights")
        self.quantum_descriptors = density_descriptors(self.rho)
        self.pauli_features = pauli_expectations(self.rho)

        self.quantum_eigenvalues: np.ndarray | None = None
        self.quantum_eigenvectors: np.ndarray | None = None
        self.coupling_matrix: np.ndarray | None = None
        self.mode_probabilities: np.ndarray | None = None
        self.mode_amplitudes: np.ndarray | None = None
        self.spatial_eigenfield: np.ndarray | None = None
        self.developmental_drive: np.ndarray | None = None

    def quantum_eigendecomposition(self) -> tuple[np.ndarray, np.ndarray]:
        values, vectors = np.linalg.eigh(self.rho)
        order = np.argsort(values)[::-1]
        self.quantum_eigenvalues = np.clip(values[order].real, 0.0, 1.0)
        self.quantum_eigenvectors = vectors[:, order]
        return self.quantum_eigenvalues, self.quantum_eigenvectors

    def _quantum_feature_vector(self) -> np.ndarray:
        if self.quantum_eigenvalues is None:
            self.quantum_eigendecomposition()
        assert self.quantum_eigenvalues is not None

        descriptors = self.quantum_descriptors
        entropy_normalized = descriptors.entropy_bits / max(
            descriptors.max_mixed_entropy_bits, 1e-12
        )
        coherence_normalized = descriptors.coherence_l1 / max(
            descriptors.dimension - 1, 1
        )

        features = list(self.quantum_eigenvalues)
        features.extend(
            [
                descriptors.purity,
                entropy_normalized,
                coherence_normalized,
                descriptors.dominant_population,
            ]
        )
        features.extend(self.pauli_features.values())
        vector = np.asarray(features, dtype=np.float64)
        if np.linalg.norm(vector) < 1e-12:
            vector = np.ones_like(vector)
        return vector / np.linalg.norm(vector)

    def build_coupling_matrix(self) -> np.ndarray:
        """Construct an explicit map from quantum features to geometric modes.

        hybrid:
            deterministic orthogonal random projection, then spectrally shaped
            by geometric eigenvalues.

        spectral:
            cosine feature bank ordered by quantum and geometric mode index.

        pauli:
            emphasizes Pauli features and local/correlation structure.
        """
        features = self._quantum_feature_vector()
        n_features = len(features)
        n_modes = len(self.geometric_eigenvalues)
        rng = np.random.default_rng(self.config.coupling_seed)

        if self.config.coupling_mode == "spectral":
            i = np.arange(n_modes, dtype=np.float64)[:, None] + 1.0
            j = np.arange(n_features, dtype=np.float64)[None, :] + 1.0
            matrix = np.cos(np.pi * i * j / (n_modes + n_features + 1.0))
        elif self.config.coupling_mode == "pauli":
            matrix = rng.normal(0.0, 1.0, (n_modes, n_features))
            pauli_start = (0 if self.quantum_eigenvalues is None else len(self.quantum_eigenvalues)) + 4
            if pauli_start < n_features:
                matrix[:, pauli_start:] *= 1.0 + self.config.pauli_gain
        elif self.config.coupling_mode == "hybrid":
            raw = rng.normal(0.0, 1.0, (max(n_modes, n_features), n_features))
            q, _ = np.linalg.qr(raw)
            matrix = q[:n_modes, :n_features]
        else:
            raise ValueError(
                "coupling_mode must be one of: hybrid, spectral, pauli"
            )

        lambdas = self.geometric_eigenvalues
        lambda_norm = lambdas / max(float(np.max(lambdas)), 1e-12)
        spectral_shape = np.exp(-self.config.spectral_decay * lambda_norm)
        matrix = matrix * spectral_shape[:, None]

        row_norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        matrix /= np.maximum(row_norms, 1e-12)
        self.coupling_matrix = matrix
        return matrix

    def project(self) -> tuple[np.ndarray, np.ndarray]:
        """Return geometric mode probabilities and complex amplitudes."""
        if self.coupling_matrix is None:
            self.build_coupling_matrix()

        assert self.coupling_matrix is not None
        features = self._quantum_feature_vector()
        logits = self.coupling_matrix @ features

        descriptors = self.quantum_descriptors
        entropy_norm = descriptors.entropy_bits / max(
            descriptors.max_mixed_entropy_bits, 1e-12
        )
        purity = descriptors.purity

        temperature = max(
            1e-4,
            self.config.temperature
            * (1.0 + self.config.entropy_spread * entropy_norm)
            / (1.0 + self.config.purity_sharpness * purity),
        )
        shifted = logits / temperature
        shifted -= np.max(shifted)
        probabilities = np.exp(shifted)
        probabilities /= max(float(np.sum(probabilities)), 1e-12)

        # Coherence controls complex phase spread. The phase seed comes from
        # off-diagonal density-matrix phases rather than arbitrary LFO motion.
        upper = self.rho[np.triu_indices(self.rho.shape[0], k=1)]
        coherence_phase = (
            float(np.angle(np.sum(upper))) if np.any(np.abs(upper) > 1e-12) else 0.0
        )
        mode_index = np.arange(len(probabilities), dtype=np.float64)
        phases = self.config.phase_gain * (
            coherence_phase
            + 2.0 * np.pi * mode_index / max(len(probabilities), 1)
        )

        amplitude_magnitude = np.sqrt(probabilities)
        coherence_norm = min(
            1.0,
            descriptors.coherence_l1 / max(descriptors.dimension - 1, 1),
        )
        complex_amplitudes = amplitude_magnitude * np.exp(
            1j * self.config.coherence_gain * coherence_norm * phases
        )

        self.mode_probabilities = probabilities
        self.mode_amplitudes = complex_amplitudes
        return probabilities, complex_amplitudes

    def synthesize_spatial_eigenfield(self) -> np.ndarray:
        if self.mode_amplitudes is None:
            self.project()
        assert self.mode_amplitudes is not None

        complex_field = self.geometric_eigenvectors @ self.mode_amplitudes
        field = np.real(complex_field)
        field -= float(np.mean(field))
        std = float(np.std(field))
        if std > 1e-12:
            field /= std
        self.spatial_eigenfield = field
        return field

    def create_developmental_drive(self) -> np.ndarray:
        if self.spatial_eigenfield is None:
            self.synthesize_spatial_eigenfield()
        assert self.spatial_eigenfield is not None

        drive = np.tanh(
            self.config.developmental_gain * self.spatial_eigenfield
            + self.config.developmental_bias
        )
        self.developmental_drive = drive.astype(np.float32)
        return self.developmental_drive

    def mode_descriptors(self) -> dict[str, Any]:
        if self.mode_probabilities is None or self.mode_amplitudes is None:
            self.project()
        assert self.mode_probabilities is not None
        assert self.mode_amplitudes is not None

        probabilities = self.mode_probabilities
        entropy = float(
            -np.sum(probabilities * np.log2(np.maximum(probabilities, 1e-15)))
        )
        participation = float(
            1.0 / max(np.sum(probabilities**2), 1e-15)
        )
        dominant = int(np.argmax(probabilities))

        return {
            "geometric_mode_count": int(len(probabilities)),
            "dominant_geometric_mode": dominant,
            "dominant_mode_probability": float(probabilities[dominant]),
            "geometric_mode_entropy_bits": entropy,
            "effective_mode_participation": participation,
            "amplitude_real_mean": float(np.mean(np.real(self.mode_amplitudes))),
            "amplitude_imag_mean": float(np.mean(np.imag(self.mode_amplitudes))),
            "field_mean": (
                None if self.spatial_eigenfield is None
                else float(np.mean(self.spatial_eigenfield))
            ),
            "field_variance": (
                None if self.spatial_eigenfield is None
                else float(np.var(self.spatial_eigenfield))
            ),
        }

    def export(self, prefix: str | Path) -> dict[str, Path]:
        if self.quantum_eigenvalues is None:
            self.quantum_eigendecomposition()
        if self.coupling_matrix is None:
            self.build_coupling_matrix()
        if self.mode_probabilities is None:
            self.project()
        if self.spatial_eigenfield is None:
            self.synthesize_spatial_eigenfield()
        if self.developmental_drive is None:
            self.create_developmental_drive()

        assert self.quantum_eigenvalues is not None
        assert self.quantum_eigenvectors is not None
        assert self.coupling_matrix is not None
        assert self.mode_probabilities is not None
        assert self.mode_amplitudes is not None
        assert self.spatial_eigenfield is not None
        assert self.developmental_drive is not None

        prefix = Path(prefix)
        prefix.parent.mkdir(parents=True, exist_ok=True)
        npz_path = prefix.with_suffix(".npz")
        json_path = prefix.with_suffix(".json")

        state: dict[str, Any] = {
            "rho": self.rho,
            "quantum_eigenvalues": self.quantum_eigenvalues,
            "quantum_eigenvectors": self.quantum_eigenvectors,
            "model": np.array(self.material_model),
            "material_model": np.array(self.material_model),
            "eigenvalues": self.geometric_eigenvalues,
            "eigenvectors": self.geometric_eigenvectors,
            "geometric_eigenvalues": self.geometric_eigenvalues,
            "geometric_eigenvectors": self.geometric_eigenvectors,
            "coupling_matrix": self.coupling_matrix,
            "mode_probabilities": self.mode_probabilities,
            "mode_amplitudes": self.mode_amplitudes,
            "spatial_eigenfield": self.spatial_eigenfield,
            "developmental_drive": self.developmental_drive,
            "material_metadata_json": np.asarray(
                json.dumps(self.material_metadata, sort_keys=True)
            ),
        }
        optional_state = {
            "frequencies_hz": self.material_frequencies_hz,
            "angular_frequencies": self.material_angular_frequencies,
            "decay_times_seconds": self.material_decay_times_seconds,
            "t60_seconds": self.material_t60_seconds,
            "damping_rates": self.material_damping_rates,
            "mode_weights": self.material_mode_weights,
        }
        state.update(
            {name: value for name, value in optional_state.items() if value is not None}
        )
        np.savez_compressed(npz_path, **state)

        payload = {
            "config": asdict(self.config),
            "quantum": self.quantum_descriptors.to_dict(),
            "pauli_expectations": self.pauli_features,
            "projection": self.mode_descriptors(),
            "material": {
                "model": self.material_model,
                "metadata": self.material_metadata,
                "frequencies_hz": (
                    None
                    if self.material_frequencies_hz is None
                    else self.material_frequencies_hz.tolist()
                ),
                "decay_times_seconds": (
                    None
                    if self.material_decay_times_seconds is None
                    else self.material_decay_times_seconds.tolist()
                ),
                "t60_seconds": (
                    None
                    if self.material_t60_seconds is None
                    else self.material_t60_seconds.tolist()
                ),
                "mode_weights": (
                    None
                    if self.material_mode_weights is None
                    else self.material_mode_weights.tolist()
                ),
            },
            "geometric_eigenvalues": self.geometric_eigenvalues.tolist(),
            "mode_probabilities": self.mode_probabilities.tolist(),
            "mode_amplitudes_real": np.real(self.mode_amplitudes).tolist(),
            "mode_amplitudes_imag": np.imag(self.mode_amplitudes).tolist(),
        }
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return {"npz": npz_path, "json": json_path}


def demo_density_matrix(n_qubits: int = 4) -> np.ndarray:
    """Create a coherent GHZ-like mixed state for a standalone test."""
    dimension = 2**n_qubits
    psi = np.zeros(dimension, dtype=np.complex128)
    psi[0] = 1.0 / np.sqrt(2.0)
    psi[-1] = 1j / np.sqrt(2.0)
    pure = np.outer(psi, psi.conj())
    mixed = np.eye(dimension, dtype=np.complex128) / dimension
    return validate_density_matrix(0.88 * pure + 0.12 * mixed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "spectrum",
        type=Path,
        help=(
            "spectral geometry NPZ or material modal NPZ from "
            "surface_material_models_v1.py"
        ),
    )
    parser.add_argument(
        "--rho",
        type=Path,
        help="density matrix .npy or .npz; omitted uses a 4-qubit demo state",
    )
    parser.add_argument("--rho-key", default="rho")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--modes", type=int, default=32)
    parser.add_argument(
        "--coupling-mode",
        choices=["hybrid", "spectral", "pauli"],
        default="hybrid",
    )
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--spectral-decay", type=float, default=0.35)
    parser.add_argument("--developmental-gain", type=float, default=1.0)
    args = parser.parse_args()

    spectral = load_modal_packet(args.spectrum)
    rho = (
        load_density_matrix(args.rho, args.rho_key)
        if args.rho is not None
        else demo_density_matrix(4)
    )

    engine = QuantumEigenfieldEngine(
        rho=rho,
        modal_packet=spectral,
        config=QuantumEigenfieldConfig(
            n_geometric_modes=args.modes,
            coupling_mode=args.coupling_mode,
            coupling_seed=args.seed,
            temperature=args.temperature,
            spectral_decay=args.spectral_decay,
            developmental_gain=args.developmental_gain,
        ),
    )

    engine.quantum_eigendecomposition()
    engine.build_coupling_matrix()
    engine.project()
    engine.synthesize_spatial_eigenfield()
    engine.create_developmental_drive()
    paths = engine.export(args.output)

    q = engine.quantum_descriptors
    m = engine.mode_descriptors()
    print("Quantum Eigenfield Engine v1 complete")
    print(f"  quantum dimension:       {q.dimension}")
    print(f"  qubits:                  {q.n_qubits}")
    print(f"  purity:                  {q.purity:.6f}")
    print(f"  entropy:                 {q.entropy_bits:.6f} bits")
    print(f"  coherence L1:            {q.coherence_l1:.6f}")
    print(f"  geometric modes:         {m['geometric_mode_count']}")
    print(f"  dominant geometric mode: {m['dominant_geometric_mode']}")
    print(f"  effective participation: {m['effective_mode_participation']:.4f}")
    print(f"  state:                   {paths['npz']}")
    print(f"  descriptors:             {paths['json']}")


if __name__ == "__main__":
    main()
