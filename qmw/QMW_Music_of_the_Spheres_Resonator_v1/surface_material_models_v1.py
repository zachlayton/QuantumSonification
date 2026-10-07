#!/usr/bin/env python3
"""Surface Material Models v1.

Canonical resonant-surface model registry for QuantumSonification.

Models
------
1. surface_laplacian
2. tensioned_membrane
3. elastic_shell
4. bioelectric_surface
5. graph_diffusion

The first three operate on a previously solved cotangent Laplace–Beltrami
spectrum. The final two may build modified operators from mesh topology and
vertex fields.

Dependencies
------------
numpy
scipy

Compatible input
----------------
A spectral NPZ produced by spectral_geometry_v1.py containing:
    vertices
    faces
    eigenvalues
    eigenvectors
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
import argparse
import json
from typing import Any

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as spla


MODEL_ORDER = (
    "surface_laplacian",
    "tensioned_membrane",
    "elastic_shell",
    "bioelectric_surface",
    "graph_diffusion",
)

LOG_1000 = float(np.log(1000.0))
DEFAULT_T60_SECONDS = 4.0
DEFAULT_DAMPING_RATE = LOG_1000 / DEFAULT_T60_SECONDS


def damping_rate_from_t60(t60_seconds: Any) -> Any:
    values = np.asarray(t60_seconds, dtype=np.float64)
    if np.any(~np.isfinite(values)) or np.any(values <= 0.0):
        raise ValueError("T60 values must be finite and positive")
    rates = LOG_1000 / values
    return float(rates) if rates.ndim == 0 else rates


def t60_from_damping_rate(damping_rates: Any) -> Any:
    values = np.asarray(damping_rates, dtype=np.float64)
    if np.any(~np.isfinite(values)) or np.any(values <= 0.0):
        raise ValueError("damping rates must be finite and positive")
    times = LOG_1000 / values
    return float(times) if times.ndim == 0 else times


@dataclass(frozen=True)
class SurfaceMaterialConfig:
    model: str = "surface_laplacian"
    n_modes: int = 32

    # Generic Laplacian scale.
    effective_wave_speed: float = 120.0

    # Membrane / shell.
    surface_tension: float = 1.0
    surface_density: float = 1.0
    bending_stiffness: float = 0.0

    # Amplitude damping rate in s^-1. The default corresponds to T60 = 4 s.
    # Values remain unclamped so material/quantum data can create sub-second
    # responses or exceptionally long tails.
    damping_base: float = DEFAULT_DAMPING_RATE
    damping_frequency_tilt: float = 0.35
    damping_curvature_gain: float = 0.0

    # Bioelectric weighted operator.
    conductivity_base: float = 1.0
    conductivity_gain: float = 0.75
    leakage_base: float = 0.01
    voltage_gain: float = 1.0

    # Graph diffusion.
    graph_edge_scale: float = 1.0
    graph_normalized: bool = True

    regularization: float = 1e-9


@dataclass
class SurfaceModalPacket:
    model: str
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    frequencies_hz: np.ndarray
    angular_frequencies: np.ndarray
    decay_times_seconds: np.ndarray
    damping_rates: np.ndarray
    mode_weights: np.ndarray
    metadata: dict[str, Any]

    @property
    def t60_seconds(self) -> np.ndarray:
        return np.asarray(
            t60_from_damping_rate(self.damping_rates), dtype=np.float64
        )

    def json_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "eigenvalues": self.eigenvalues.tolist(),
            "frequencies_hz": self.frequencies_hz.tolist(),
            "angular_frequencies": self.angular_frequencies.tolist(),
            "decay_times_seconds": self.decay_times_seconds.tolist(),
            "t60_seconds": self.t60_seconds.tolist(),
            "damping_rates": self.damping_rates.tolist(),
            "mode_weights": self.mode_weights.tolist(),
            "metadata": self.metadata,
        }


def load_spectral_npz(path: str | Path) -> dict[str, Any]:
    with np.load(path, allow_pickle=False) as payload:
        required = {"vertices", "faces", "eigenvalues", "eigenvectors"}
        missing = required.difference(payload.files)
        if missing:
            raise ValueError(f"spectral NPZ missing keys: {sorted(missing)}")
        result: dict[str, Any] = {
            name: payload[name] for name in payload.files
        }
    if "metadata_json" in result:
        result["metadata"] = json.loads(
            str(np.asarray(result["metadata_json"]).item())
        )
    return result


def normalize01(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    lo = float(np.min(values))
    hi = float(np.max(values))
    if hi - lo < 1e-15:
        return np.zeros_like(values)
    return (values - lo) / (hi - lo)


def mesh_vertex_areas(
    vertices: np.ndarray,
    faces: np.ndarray,
) -> np.ndarray:
    areas = np.zeros(len(vertices), dtype=np.float64)
    for i, j, k in np.asarray(faces, dtype=np.int64):
        vi, vj, vk = vertices[i], vertices[j], vertices[k]
        area = 0.5 * np.linalg.norm(np.cross(vj - vi, vk - vi))
        if area > 0:
            areas[[i, j, k]] += area / 3.0
    return np.maximum(areas, 1e-12)


def mesh_adjacency(
    vertices: np.ndarray,
    faces: np.ndarray,
    edge_scale: float = 1.0,
) -> sparse.csr_matrix:
    edge_weights: dict[tuple[int, int], float] = {}
    for i, j, k in np.asarray(faces, dtype=np.int64):
        for a, b in ((i, j), (j, k), (k, i)):
            key = (min(int(a), int(b)), max(int(a), int(b)))
            distance = np.linalg.norm(vertices[key[0]] - vertices[key[1]])
            weight = edge_scale / max(distance, 1e-12)
            edge_weights[key] = max(edge_weights.get(key, 0.0), weight)

    rows, cols, data = [], [], []
    for (i, j), weight in edge_weights.items():
        rows.extend([i, j])
        cols.extend([j, i])
        data.extend([weight, weight])

    return sparse.coo_matrix(
        (data, (rows, cols)),
        shape=(len(vertices), len(vertices)),
    ).tocsr()


def solve_smallest_modes(
    operator: sparse.spmatrix,
    mass: sparse.spmatrix | None,
    n_modes: int,
    regularization: float,
) -> tuple[np.ndarray, np.ndarray]:
    n = operator.shape[0]
    k = max(2, min(n_modes + 1, n - 1))
    op = operator.tocsr() + regularization * sparse.eye(n, format="csr")
    values, vectors = spla.eigsh(
        op,
        k=k,
        M=mass,
        sigma=0.0,
        which="LM",
    )
    order = np.argsort(values)
    values = np.maximum(np.real(values[order]), 0.0)
    vectors = np.real(vectors[:, order])

    keep = values > 1e-8
    values = values[keep][:n_modes]
    vectors = vectors[:, keep][:, :n_modes]
    return values, vectors


class SurfaceResonanceModel(ABC):
    model_name = "surface"

    def __init__(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        base_eigenvalues: np.ndarray,
        base_eigenvectors: np.ndarray,
        config: SurfaceMaterialConfig,
    ) -> None:
        self.vertices = np.asarray(vertices, dtype=np.float64)
        self.faces = np.asarray(faces, dtype=np.int64)
        base_eigenvalues = np.asarray(base_eigenvalues, dtype=np.float64).reshape(-1)
        base_eigenvectors = np.asarray(base_eigenvectors, dtype=np.float64)
        if self.vertices.ndim != 2 or self.vertices.shape[1] != 3:
            raise ValueError("vertices must have shape (vertex_count, 3)")
        if self.faces.ndim != 2 or self.faces.shape[1] != 3:
            raise ValueError("faces must have shape (face_count, 3)")
        if base_eigenvectors.ndim != 2:
            raise ValueError("eigenvectors must have shape (vertices, modes)")
        if base_eigenvectors.shape[0] != len(self.vertices):
            raise ValueError("eigenvector vertex count does not match vertices")
        if base_eigenvectors.shape[1] != len(base_eigenvalues):
            raise ValueError("eigenvalue/eigenvector mode count mismatch")
        if config.n_modes < 1:
            raise ValueError("n_modes must be positive")
        count = min(
            config.n_modes,
            len(base_eigenvalues),
            base_eigenvectors.shape[1],
        )
        self.base_eigenvalues = base_eigenvalues[:count]
        self.base_eigenvectors = base_eigenvectors[:, :count]
        self.config = config

    @abstractmethod
    def solve(self, **fields: np.ndarray) -> SurfaceModalPacket:
        raise NotImplementedError

    def _generic_damping(
        self,
        frequencies: np.ndarray,
        mode_shape_factor: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        f = np.asarray(frequencies, dtype=np.float64)
        if len(f) == 0:
            return f.copy(), f.copy()

        median = max(float(np.median(f)), 1e-12)
        rates = self.config.damping_base * (
            np.maximum(f / median, 1e-8)
            ** self.config.damping_frequency_tilt
        )
        if mode_shape_factor is not None:
            rates *= 1.0 + self.config.damping_curvature_gain * normalize01(
                mode_shape_factor
            )
        rates = np.maximum(rates, 1e-6)
        return rates, 1.0 / rates

    @staticmethod
    def _default_weights(eigenvalues: np.ndarray) -> np.ndarray:
        weights = 1.0 / np.sqrt(1.0 + np.arange(len(eigenvalues)))
        return weights / max(float(np.max(weights)), 1e-12)


class SurfaceLaplacianModel(SurfaceResonanceModel):
    model_name = "surface_laplacian"

    def solve(self, **fields: np.ndarray) -> SurfaceModalPacket:
        lambdas = self.base_eigenvalues
        omega = self.config.effective_wave_speed * np.sqrt(lambdas)
        frequencies = omega / (2.0 * np.pi)
        damping, decays = self._generic_damping(frequencies)
        return SurfaceModalPacket(
            model=self.model_name,
            eigenvalues=lambdas,
            eigenvectors=self.base_eigenvectors,
            frequencies_hz=frequencies,
            angular_frequencies=omega,
            decay_times_seconds=decays,
            damping_rates=damping,
            mode_weights=self._default_weights(lambdas),
            metadata={
                "effective_wave_speed": self.config.effective_wave_speed,
                "operator": "cotangent_laplace_beltrami",
            },
        )


class TensionedMembraneModel(SurfaceResonanceModel):
    model_name = "tensioned_membrane"

    def solve(self, **fields: np.ndarray) -> SurfaceModalPacket:
        if self.config.surface_density <= 0:
            raise ValueError("surface_density must be positive")
        if self.config.surface_tension < 0:
            raise ValueError("surface_tension cannot be negative")

        lambdas = self.base_eigenvalues
        omega_sq = (
            self.config.surface_tension
            * lambdas
            / self.config.surface_density
        )
        omega = np.sqrt(np.maximum(omega_sq, 0.0))
        frequencies = omega / (2.0 * np.pi)
        damping, decays = self._generic_damping(frequencies)

        return SurfaceModalPacket(
            model=self.model_name,
            eigenvalues=lambdas,
            eigenvectors=self.base_eigenvectors,
            frequencies_hz=frequencies,
            angular_frequencies=omega,
            decay_times_seconds=decays,
            damping_rates=damping,
            mode_weights=self._default_weights(lambdas),
            metadata={
                "surface_tension": self.config.surface_tension,
                "surface_density": self.config.surface_density,
                "frequency_law": "sqrt(T * lambda / rho_s)",
            },
        )


class ElasticShellModel(SurfaceResonanceModel):
    model_name = "elastic_shell"

    def solve(self, **fields: np.ndarray) -> SurfaceModalPacket:
        if self.config.surface_density <= 0:
            raise ValueError("surface_density must be positive")
        if self.config.surface_tension < 0:
            raise ValueError("surface_tension cannot be negative")
        if self.config.bending_stiffness < 0:
            raise ValueError("bending_stiffness cannot be negative")

        lambdas = self.base_eigenvalues
        omega_sq = (
            self.config.surface_tension * lambdas
            + self.config.bending_stiffness * lambdas**2
        ) / self.config.surface_density
        omega = np.sqrt(np.maximum(omega_sq, 0.0))
        frequencies = omega / (2.0 * np.pi)
        damping, decays = self._generic_damping(
            frequencies,
            mode_shape_factor=lambdas**2,
        )

        return SurfaceModalPacket(
            model=self.model_name,
            eigenvalues=lambdas,
            eigenvectors=self.base_eigenvectors,
            frequencies_hz=frequencies,
            angular_frequencies=omega,
            decay_times_seconds=decays,
            damping_rates=damping,
            mode_weights=self._default_weights(lambdas),
            metadata={
                "surface_tension": self.config.surface_tension,
                "surface_density": self.config.surface_density,
                "bending_stiffness": self.config.bending_stiffness,
                "frequency_law": (
                    "sqrt((T * lambda + D * lambda^2) / rho_s)"
                ),
            },
        )


class BioelectricSurfaceModel(SurfaceResonanceModel):
    model_name = "bioelectric_surface"

    def _weighted_operator(
        self,
        voltage: np.ndarray,
        conductivity: np.ndarray | None,
        leakage: np.ndarray | None,
    ) -> tuple[sparse.csr_matrix, sparse.csr_matrix, np.ndarray]:
        n = len(self.vertices)
        voltage = np.asarray(voltage, dtype=np.float64).reshape(-1)
        if len(voltage) != n:
            raise ValueError("voltage field must have one value per vertex")

        if conductivity is None:
            conductivity_values = (
                self.config.conductivity_base
                * np.exp(
                    self.config.conductivity_gain
                    * self.config.voltage_gain
                    * np.tanh(voltage)
                )
            )
        else:
            conductivity_values = np.asarray(
                conductivity, dtype=np.float64
            ).reshape(-1)
            if len(conductivity_values) != n:
                raise ValueError(
                    "conductivity field must have one value per vertex"
                )
            conductivity_values = np.maximum(conductivity_values, 1e-8)

        if leakage is None:
            leakage_values = np.full(
                n, self.config.leakage_base, dtype=np.float64
            )
        else:
            leakage_values = np.asarray(
                leakage, dtype=np.float64
            ).reshape(-1)
            if len(leakage_values) != n:
                raise ValueError(
                    "leakage field must have one value per vertex"
                )
            leakage_values = np.maximum(leakage_values, 0.0)

        adjacency = mesh_adjacency(self.vertices, self.faces, 1.0)
        rows, cols = adjacency.nonzero()
        edge_data = []
        for i, j in zip(rows, cols):
            edge_data.append(
                adjacency[i, j]
                * 0.5
                * (conductivity_values[i] + conductivity_values[j])
            )
        weighted_adjacency = sparse.coo_matrix(
            (edge_data, (rows, cols)),
            shape=adjacency.shape,
        ).tocsr()

        degree = np.asarray(weighted_adjacency.sum(axis=1)).reshape(-1)
        operator = sparse.diags(degree) - weighted_adjacency
        areas = mesh_vertex_areas(self.vertices, self.faces)
        mass = sparse.diags(areas, format="csr")
        operator = operator + sparse.diags(
            leakage_values * areas,
            format="csr",
        )
        return operator.tocsr(), mass, conductivity_values

    def solve(self, **fields: np.ndarray) -> SurfaceModalPacket:
        if "voltage" not in fields:
            raise ValueError(
                "bioelectric_surface requires a vertex voltage field"
            )

        operator, mass, conductivity = self._weighted_operator(
            voltage=fields["voltage"],
            conductivity=fields.get("conductivity"),
            leakage=fields.get("leakage"),
        )
        values, vectors = solve_smallest_modes(
            operator,
            mass,
            self.config.n_modes,
            self.config.regularization,
        )

        # Eigenvalues are diffusion/leakage rates. Convert to oscillatory
        # frequencies through a configurable effective speed for sonification.
        omega = self.config.effective_wave_speed * np.sqrt(values)
        frequencies = omega / (2.0 * np.pi)
        damping, decays = self._generic_damping(
            frequencies,
            mode_shape_factor=values,
        )

        weights = self._default_weights(values)
        voltage = np.asarray(fields["voltage"], dtype=np.float64).reshape(-1)
        projections = np.abs(vectors.T @ voltage)
        if np.max(projections) > 0:
            projections /= np.max(projections)
            weights *= 0.25 + 0.75 * projections

        return SurfaceModalPacket(
            model=self.model_name,
            eigenvalues=values,
            eigenvectors=vectors,
            frequencies_hz=frequencies,
            angular_frequencies=omega,
            decay_times_seconds=decays,
            damping_rates=damping,
            mode_weights=weights,
            metadata={
                "conductivity_min": float(np.min(conductivity)),
                "conductivity_max": float(np.max(conductivity)),
                "leakage_base": self.config.leakage_base,
                "operator": (
                    "-div_M(sigma(x) grad_M) + leakage(x)"
                ),
            },
        )


class GraphDiffusionModel(SurfaceResonanceModel):
    model_name = "graph_diffusion"

    def solve(self, **fields: np.ndarray) -> SurfaceModalPacket:
        adjacency = mesh_adjacency(
            self.vertices,
            self.faces,
            self.config.graph_edge_scale,
        )
        degree = np.asarray(adjacency.sum(axis=1)).reshape(-1)

        if self.config.graph_normalized:
            safe = np.maximum(degree, 1e-12)
            inv_sqrt = sparse.diags(1.0 / np.sqrt(safe))
            operator = (
                sparse.eye(len(self.vertices), format="csr")
                - inv_sqrt @ adjacency @ inv_sqrt
            )
        else:
            operator = sparse.diags(degree) - adjacency

        values, vectors = solve_smallest_modes(
            operator,
            None,
            self.config.n_modes,
            self.config.regularization,
        )
        omega = self.config.effective_wave_speed * np.sqrt(values)
        frequencies = omega / (2.0 * np.pi)
        damping, decays = self._generic_damping(frequencies)

        return SurfaceModalPacket(
            model=self.model_name,
            eigenvalues=values,
            eigenvectors=vectors,
            frequencies_hz=frequencies,
            angular_frequencies=omega,
            decay_times_seconds=decays,
            damping_rates=damping,
            mode_weights=self._default_weights(values),
            metadata={
                "graph_normalized": self.config.graph_normalized,
                "graph_edge_scale": self.config.graph_edge_scale,
                "operator": "mesh_connectivity_graph_laplacian",
            },
        )


MODEL_REGISTRY: dict[str, type[SurfaceResonanceModel]] = {
    "surface_laplacian": SurfaceLaplacianModel,
    "tensioned_membrane": TensionedMembraneModel,
    "elastic_shell": ElasticShellModel,
    "bioelectric_surface": BioelectricSurfaceModel,
    "graph_diffusion": GraphDiffusionModel,
}


def create_surface_model(
    vertices: np.ndarray,
    faces: np.ndarray,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
    config: SurfaceMaterialConfig,
) -> SurfaceResonanceModel:
    if config.model not in MODEL_REGISTRY:
        raise ValueError(
            f"unknown model {config.model!r}; "
            f"choose from {', '.join(MODEL_ORDER)}"
        )
    return MODEL_REGISTRY[config.model](
        vertices=vertices,
        faces=faces,
        base_eigenvalues=eigenvalues,
        base_eigenvectors=eigenvectors,
        config=config,
    )


def export_packet(
    packet: SurfaceModalPacket,
    config: SurfaceMaterialConfig,
    prefix: str | Path,
) -> dict[str, Path]:
    prefix = Path(prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    npz_path = prefix.with_suffix(".npz")
    json_path = prefix.with_suffix(".json")

    np.savez_compressed(
        npz_path,
        model=np.array(packet.model),
        eigenvalues=packet.eigenvalues,
        eigenvectors=packet.eigenvectors,
        frequencies_hz=packet.frequencies_hz,
        angular_frequencies=packet.angular_frequencies,
        decay_times_seconds=packet.decay_times_seconds,
        t60_seconds=packet.t60_seconds,
        damping_rates=packet.damping_rates,
        mode_weights=packet.mode_weights,
        metadata_json=np.asarray(
            json.dumps(packet.metadata, sort_keys=True)
        ),
    )

    payload = {
        "config": asdict(config),
        "packet": packet.json_dict(),
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"npz": npz_path, "json": json_path}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spectrum", type=Path)
    parser.add_argument(
        "--model",
        choices=MODEL_ORDER,
        default="surface_laplacian",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--modes", type=int, default=32)
    parser.add_argument("--wave-speed", type=float, default=120.0)
    parser.add_argument("--tension", type=float, default=1.0)
    parser.add_argument("--density", type=float, default=1.0)
    parser.add_argument("--stiffness", type=float, default=0.0)
    parser.add_argument(
        "--damping",
        type=float,
        help="Amplitude damping rate in s^-1 (overrides --t60)",
    )
    parser.add_argument("--t60", type=float, default=DEFAULT_T60_SECONDS)
    parser.add_argument("--voltage", type=Path)
    parser.add_argument("--conductivity", type=Path)
    parser.add_argument("--leakage", type=Path)
    parser.add_argument("--graph-edge-scale", type=float, default=1.0)
    parser.add_argument("--unnormalized-graph", action="store_true")
    args = parser.parse_args()

    spectral = load_spectral_npz(args.spectrum)
    config = SurfaceMaterialConfig(
        model=args.model,
        n_modes=args.modes,
        effective_wave_speed=args.wave_speed,
        surface_tension=args.tension,
        surface_density=args.density,
        bending_stiffness=args.stiffness,
        damping_base=(
            args.damping
            if args.damping is not None
            else damping_rate_from_t60(args.t60)
        ),
        graph_edge_scale=args.graph_edge_scale,
        graph_normalized=not args.unnormalized_graph,
    )
    model = create_surface_model(
        vertices=spectral["vertices"],
        faces=spectral["faces"],
        eigenvalues=spectral["eigenvalues"],
        eigenvectors=spectral["eigenvectors"],
        config=config,
    )

    fields: dict[str, np.ndarray] = {}
    if args.voltage:
        fields["voltage"] = np.load(args.voltage)
    if args.conductivity:
        fields["conductivity"] = np.load(args.conductivity)
    if args.leakage:
        fields["leakage"] = np.load(args.leakage)

    packet = model.solve(**fields)
    paths = export_packet(packet, config, args.output)

    print("Surface Material Models v1 complete")
    print(f"  model:       {packet.model}")
    print(f"  modes:       {len(packet.eigenvalues)}")
    if len(packet.frequencies_hz):
        print(
            f"  frequencies: {packet.frequencies_hz[0]:.4f}"
            f"–{packet.frequencies_hz[-1]:.4f} Hz"
        )
    print(f"  state:       {paths['npz']}")
    print(f"  descriptors: {paths['json']}")


if __name__ == "__main__":
    main()
