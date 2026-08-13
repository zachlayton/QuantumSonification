"""Algebraic surface -> Laplace-Beltrami modes -> Sonic Pi OSC stream.

Reuses the existing marching-tetrahedra mesher and cotangent-Laplacian
solver (``operators.algebraic_surface_pipeline_v1``,
``operators.spectral_geometry_v1``) and material models
(``surface_material_models_v1``) rather than re-deriving them. The mesh and
eigensolve are cached by geometry parameters so dragging a
sound-design-only control (mode count, wave speed, T60, damping, material
model) does not re-mesh or re-solve the surface -- only parameters that
change the surface itself (surface family, equation parameter, sampling
resolution/bound, physical radius) invalidate the cache.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any

import numpy as np

from operators.algebraic_surface_pipeline_v1 import (
    AlgebraicSurfaceConfig,
    marching_tetrahedra,
)
from operators.spectral_geometry_v1 import (
    MeshSpectralGeometry,
    SpectralGeometryConfig,
)
from surface_material_models_v1 import (
    SurfaceMaterialConfig,
    SurfaceModalPacket,
    create_surface_model,
    damping_rate_from_t60,
)

from .osc_client_v1 import SonicPiOSCClient

# Surfaces implemented by algebraic_field() in the pipeline module.
SURFACE_NAMES: tuple[str, ...] = ("tanglecube", "heart")

# Material models that solve from mesh geometry alone (no external vertex
# fields). "bioelectric_surface" is intentionally excluded: it requires a
# vertex voltage field this realtime bridge has no source for.
MATERIAL_MODEL_NAMES: tuple[str, ...] = (
    "surface_laplacian",
    "tensioned_membrane",
    "elastic_shell",
    "graph_diffusion",
)

MODES_ADDRESS = "/algebraic/modes"
SILENCE_ADDRESS = "/algebraic/silence"


@dataclass(frozen=True)
class RealtimeSurfaceConfig:
    surface: str = "tanglecube"
    parameter: float = 11.8
    # Kept modest by default so a parameter change resolves in about a
    # second; raise resolution/max_modes for higher fidelity at the cost of
    # responsiveness (see this package's README for measured timings).
    resolution: int = 20
    bound: float = 3.0
    radius_m: float = 0.25

    # Modes solved and cached per mesh; active_modes <= max_modes is a cheap
    # truncation applied in the material step, so raising max_modes is the
    # only mode-count change that forces a re-solve.
    max_modes: int = 24
    active_modes: int = 16

    material_model: str = "surface_laplacian"
    effective_wave_speed: float = 120.0
    t60_seconds: float = 4.0
    damping_frequency_tilt: float = 0.35
    damping_curvature_gain: float = 0.0

    def geometry_key(self) -> tuple[Any, ...]:
        """Identifies the (mesh, eigensolve) pair this config would produce."""
        return (
            self.surface,
            round(float(self.parameter), 6),
            int(self.resolution),
            round(float(self.bound), 6),
            round(float(self.radius_m), 6),
            int(self.max_modes),
        )


@dataclass
class GeometrySolve:
    vertices: np.ndarray
    faces: np.ndarray
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    elapsed_seconds: float


class SurfaceModeCache:
    """Caches the expensive mesh + eigensolve step by geometry key."""

    def __init__(self) -> None:
        self._key: tuple[Any, ...] | None = None
        self._solve: GeometrySolve | None = None

    def solve(self, config: RealtimeSurfaceConfig) -> GeometrySolve:
        key = config.geometry_key()
        if self._solve is not None and key == self._key:
            return self._solve

        started = time.monotonic()
        surface_config = AlgebraicSurfaceConfig(
            surface=config.surface,
            parameter=config.parameter,
            resolution=config.resolution,
            bound=config.bound,
            radius_m=config.radius_m,
        )
        vertices, faces = marching_tetrahedra(surface_config)
        spectral = MeshSpectralGeometry(
            vertices,
            faces,
            SpectralGeometryConfig(n_modes=config.max_modes),
        )
        result = spectral.solve()
        solve = GeometrySolve(
            vertices=vertices,
            faces=faces,
            eigenvalues=result.eigenvalues,
            eigenvectors=result.eigenvectors,
            elapsed_seconds=time.monotonic() - started,
        )
        self._key = key
        self._solve = solve
        return solve


def compute_modal_packet(
    config: RealtimeSurfaceConfig, cache: SurfaceModeCache
) -> tuple[SurfaceModalPacket, GeometrySolve]:
    """Returns the current sound-design packet and the (cached) mesh solve."""
    solve = cache.solve(config)
    material_config = SurfaceMaterialConfig(
        model=config.material_model,
        n_modes=config.active_modes,
        effective_wave_speed=config.effective_wave_speed,
        damping_base=damping_rate_from_t60(config.t60_seconds),
        damping_frequency_tilt=config.damping_frequency_tilt,
        damping_curvature_gain=config.damping_curvature_gain,
    )
    model = create_surface_model(
        solve.vertices,
        solve.faces,
        solve.eigenvalues,
        solve.eigenvectors,
        material_config,
    )
    packet = model.solve()
    return packet, solve


def build_mode_payload(
    packet: SurfaceModalPacket, seed: int, stereo_width: float
) -> list[float]:
    """Flattens a modal packet into [freq, decay, amp, pan] * mode_count."""
    count = len(packet.frequencies_hz)
    rng = np.random.default_rng(seed)
    pans = np.clip(rng.uniform(-1.0, 1.0, count) * stereo_width, -1.0, 1.0)
    payload: list[float] = []
    for frequency, decay, weight, pan in zip(
        packet.frequencies_hz,
        packet.decay_times_seconds,
        packet.mode_weights,
        pans,
    ):
        payload.extend(
            [float(frequency), float(decay), float(weight), float(pan)]
        )
    return payload


class SonicPiModeStreamer:
    """Sends a modal packet to Sonic Pi as one flattened OSC message.

    A single message keeps the mode set atomic on the receiving end -- the
    Sonic Pi live_loop either gets a complete new chord or keeps the
    previous one, never a half-updated one.
    """

    def __init__(
        self,
        client: SonicPiOSCClient,
        address: str = MODES_ADDRESS,
        silence_address: str = SILENCE_ADDRESS,
        seed: int = 23,
        stereo_width: float = 0.85,
    ) -> None:
        self.client = client
        self.address = address
        self.silence_address = silence_address
        self.seed = seed
        self.stereo_width = stereo_width

    def send_packet(self, packet: SurfaceModalPacket) -> int:
        payload = build_mode_payload(packet, self.seed, self.stereo_width)
        count = len(packet.frequencies_hz)
        self.client.send(self.address, [count, *payload])
        return count

    def send_silence(self) -> None:
        self.client.send(self.silence_address, [])
