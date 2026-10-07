from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import numpy as np

from qmw.core.quantum_frame import QuantumFrame


@dataclass
class GrainControlFrame:
    """
    Musical control representation derived from a QuantumFrame.

    This is intentionally downstream of the physics state.
    """
    time: np.ndarray
    position: np.ndarray
    duration_ms: np.ndarray
    rate: np.ndarray
    amplitude: np.ndarray
    pan: np.ndarray
    density_hz: np.ndarray
    metadata: Dict[str, object]


def _normalize(x: np.ndarray, lo: float, hi: float, eps: float = 1e-12) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    xmin = np.nanmin(x)
    xmax = np.nanmax(x)
    if xmax - xmin < eps:
        return np.full_like(x, (lo + hi) * 0.5)
    return lo + (x - xmin) * (hi - lo) / (xmax - xmin)


class QuantumGranularProjector:
    """
    Explicit mapping from quantum transport observables to granular controls.

    Default mapping for the closed four-qubit XY transport model:
      population_center  -> grain position
      population_entropy -> grain duration
      current_direction  -> playback rate
      population_max     -> amplitude
      current_center     -> pan
      current_activity   -> grain density

    No mapping is asserted as a physical identity; these are inspectable
    musical projections.
    """

    def __init__(
        self,
        position_source: str = "population_center",
        duration_source: str = "population_entropy",
        rate_source: str = "current_direction",
        amplitude_source: str = "population_max",
        pan_source: str = "current_center",
        density_source: str = "current_activity",
    ):
        self.sources = {
            "position": position_source,
            "duration": duration_source,
            "rate": rate_source,
            "amplitude": amplitude_source,
            "pan": pan_source,
            "density": density_source,
        }

    def _derived_sources(self, frame: QuantumFrame) -> Dict[str, np.ndarray]:
        sources: Dict[str, np.ndarray] = {}
        sources["purity"] = frame.purity()

        if "commutator_activity" in frame.diagnostics:
            sources["hamiltonian_activity"] = np.asarray(
                frame.diagnostics["commutator_activity"], dtype=float
            )

        if "pauli_z" in frame.observables:
            z = np.asarray(frame.observables["pauli_z"], dtype=float)
            sources["pauli_z_mean"] = np.mean(z, axis=1)

        if "site_populations" in frame.observables:
            p = np.clip(np.asarray(frame.observables["site_populations"], dtype=float), 0.0, 1.0)
            sources["population_max"] = np.max(p, axis=1)

            sites = np.arange(p.shape[1], dtype=float)
            denom = np.sum(p, axis=1)
            denom = np.where(np.abs(denom) < 1e-12, 1.0, denom)
            center = np.sum(p * sites[None, :], axis=1) / denom
            if p.shape[1] > 1:
                center = center / (p.shape[1] - 1)
            sources["population_center"] = center

            # Normalized Shannon entropy of the site-population distribution.
            psafe = np.where(p > 1e-15, p, 1.0)
            entropy = -np.sum(np.where(p > 1e-15, p * np.log(psafe), 0.0), axis=1)
            if p.shape[1] > 1:
                entropy /= np.log(p.shape[1])
            sources["population_entropy"] = entropy

            # Spatial spread of the excitation distribution.
            centered = sites[None, :] / max(1, p.shape[1] - 1) - center[:, None]
            sources["population_spread"] = np.sum(p * centered**2, axis=1) / denom

        if "edge_currents" in frame.observables:
            j = np.asarray(frame.observables["edge_currents"], dtype=float)
            absj = np.abs(j)
            activity = np.sum(absj, axis=1)
            sources["current_activity"] = activity

            # -1 means net flow toward q0; +1 means net flow toward q3.
            signed = np.sum(j, axis=1)
            sources["current_direction"] = np.divide(
                signed,
                activity,
                out=np.zeros_like(signed),
                where=activity > 1e-12,
            )

            # Where along the chain the current is concentrated, normalized [0,1].
            edge_positions = (np.arange(j.shape[1], dtype=float) + 0.5) / j.shape[1]
            current_center = np.sum(absj * edge_positions[None, :], axis=1)
            current_center = np.divide(
                current_center,
                activity,
                out=np.full_like(current_center, 0.5),
                where=activity > 1e-12,
            )
            sources["current_center"] = current_center

        for name, arr in frame.observables.items():
            arr = np.asarray(arr)
            if arr.ndim == 1:
                sources.setdefault(name, arr.astype(float))

        for name, arr in frame.diagnostics.items():
            arr = np.asarray(arr)
            if arr.ndim == 1 and arr.shape[0] == frame.samples:
                sources.setdefault(name, arr.astype(float))

        return sources

    def project(self, frame: QuantumFrame) -> GrainControlFrame:
        src = self._derived_sources(frame)

        missing = [s for s in self.sources.values() if s not in src]
        if missing:
            raise KeyError("Missing granular source(s): " + ", ".join(sorted(set(missing))))

        # Musical ranges; deliberately separate from physics units.
        position = _normalize(src[self.sources["position"]], 0.0, 1.0)
        duration_ms = _normalize(src[self.sources["duration"]], 18.0, 180.0)
        rate = _normalize(src[self.sources["rate"]], 0.5, 2.0)
        amplitude = _normalize(src[self.sources["amplitude"]], 0.08, 0.9)
        pan = _normalize(src[self.sources["pan"]], -1.0, 1.0)
        density_hz = _normalize(src[self.sources["density"]], 2.0, 70.0)

        return GrainControlFrame(
            time=frame.t.copy(),
            position=position,
            duration_ms=duration_ms,
            rate=rate,
            amplitude=amplitude,
            pan=pan,
            density_hz=density_hz,
            metadata={
                "projector": "QuantumGranularProjector",
                "sources": dict(self.sources),
                "ranges": {
                    "position": [0.0, 1.0],
                    "duration_ms": [18.0, 180.0],
                    "rate": [0.5, 2.0],
                    "amplitude": [0.08, 0.9],
                    "pan": [-1.0, 1.0],
                    "density_hz": [2.0, 70.0],
                },
                "note": (
                    "Mappings are musical projections from quantum-derived observables; "
                    "they are not physical identities."
                ),
            },
        )
