#!/usr/bin/env python3
"""Developmental Fields v1.

A common MLX field interface for morphogenetic and excitable-media models used
by the QuantumSonification emergent-geometry system.

Included models
---------------
- GrayScottField
- TuringActivatorInhibitorField
- FitzHughNagumoField
- WaveDevelopmentalField
- BioelectricMemoryField

Compatibility
-------------
`MorphogenParameters`, `MorphogenField`, and `PRESETS` remain available so the
current `emergent_geometry_engine_v1.py` can migrate incrementally.

The common geometry-facing contract is:

    field.primary_field
    field.secondary_field
    field.step(iterations)
    field.reset()
    field.perturb(x_norm, y_norm, radius_norm, amount)
    field.descriptors()
    field.geometry_fields()

`geometry_fields()` returns two normalized arrays `(u, v)` so the existing
surface mapper can continue to use:

    height <- growth_gain * (v - 0.42 * (1 - u)) + edge_gain * laplacian(v)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, ClassVar

try:
    import mlx.core as mx
except ImportError as exc:
    raise SystemExit(
        "MLX is required. On Apple silicon, activate the project environment "
        "and run: pip install mlx"
    ) from exc

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit("NumPy is required: pip install numpy") from exc


Array = mx.array


def scalar(value: Array) -> float:
    return float(value.item())


def to_numpy(value: Array) -> np.ndarray:
    return np.asarray(value, dtype=np.float32)


def normalize01(field: Array, epsilon: float = 1e-8) -> Array:
    lo = mx.min(field)
    hi = mx.max(field)
    return mx.clip((field - lo) / (hi - lo + epsilon), 0.0, 1.0)


def laplacian(field: Array) -> Array:
    """Periodic 9-point Laplacian."""
    axial = (
        mx.roll(field, 1, axis=0)
        + mx.roll(field, -1, axis=0)
        + mx.roll(field, 1, axis=1)
        + mx.roll(field, -1, axis=1)
    )
    diagonal = (
        mx.roll(mx.roll(field, 1, axis=0), 1, axis=1)
        + mx.roll(mx.roll(field, 1, axis=0), -1, axis=1)
        + mx.roll(mx.roll(field, -1, axis=0), 1, axis=1)
        + mx.roll(mx.roll(field, -1, axis=0), -1, axis=1)
    )
    return -field + 0.20 * axial + 0.05 * diagonal


def gradient_energy(field: Array) -> tuple[Array, Array]:
    dx = 0.5 * (mx.roll(field, -1, axis=1) - mx.roll(field, 1, axis=1))
    dy = 0.5 * (mx.roll(field, -1, axis=0) - mx.roll(field, 1, axis=0))
    return mx.mean(dx * dx), mx.mean(dy * dy)


def radial_envelope(
    size: int,
    x_norm: float,
    y_norm: float,
    radius_norm: float,
) -> np.ndarray:
    x_norm = float(np.clip(x_norm, 0.0, 1.0))
    y_norm = float(np.clip(y_norm, 0.0, 1.0))
    radius_norm = float(np.clip(radius_norm, 0.002, 0.5))

    cx = x_norm * (size - 1)
    cy = y_norm * (size - 1)
    radius = max(1.0, radius_norm * size)
    sigma = max(1.0, radius * 0.45)

    yy, xx = np.ogrid[:size, :size]
    envelope = np.exp(
        -((xx - cx) ** 2 + (yy - cy) ** 2) / (2.0 * sigma**2)
    )
    return envelope.astype(np.float32)


class DevelopmentalField(ABC):
    """Abstract common interface for fields that generate geometry."""

    model_name: ClassVar[str] = "developmental"

    def __init__(self, size: int, seed: int = 23) -> None:
        if size < 32:
            raise ValueError("size must be at least 32")
        self.size = int(size)
        self.seed_value = int(seed)
        self.step_count = 0
        self.reset()

    @property
    @abstractmethod
    def primary_field(self) -> Array:
        raise NotImplementedError

    @property
    @abstractmethod
    def secondary_field(self) -> Array:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def step(self, iterations: int = 1) -> None:
        raise NotImplementedError

    @abstractmethod
    def perturb(
        self,
        x_norm: float,
        y_norm: float,
        radius_norm: float,
        amount: float,
    ) -> None:
        raise NotImplementedError

    def geometry_fields(self) -> tuple[Array, Array]:
        """Return normalized substrate/growth fields for the surface mapper."""
        return normalize01(self.primary_field), normalize01(self.secondary_field)

    def descriptors(self) -> dict[str, float | int | str]:
        primary, secondary = self.geometry_fields()
        gx, gy = gradient_energy(secondary)
        anisotropy = mx.abs(gx - gy) / (gx + gy + 1e-8)
        occupancy = mx.mean((secondary > mx.mean(secondary)).astype(mx.float32))
        occ = mx.clip(occupancy, 1e-6, 1.0 - 1e-6)
        entropy = -(occ * mx.log2(occ) + (1.0 - occ) * mx.log2(1.0 - occ))

        return {
            "model": self.model_name,
            "step": self.step_count,
            "primary_mean": scalar(mx.mean(primary)),
            "primary_variance": scalar(mx.var(primary)),
            "secondary_mean": scalar(mx.mean(secondary)),
            "secondary_variance": scalar(mx.var(secondary)),
            "secondary_max": scalar(mx.max(secondary)),
            "pattern_entropy": scalar(entropy),
            "anisotropy": scalar(anisotropy),
            "field_energy": scalar(mx.mean(primary * primary + secondary * secondary)),
        }

    def parameter_dict(self) -> dict[str, Any]:
        parameters = getattr(self, "parameters", None)
        return asdict(parameters) if parameters is not None else {}


# ---------------------------------------------------------------------------
# Gray-Scott
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GrayScottParameters:
    diffusion_u: float = 0.16
    diffusion_v: float = 0.08
    feed: float = 0.060
    kill: float = 0.062
    dt: float = 1.0


GRAY_SCOTT_PRESETS: dict[str, GrayScottParameters] = {
    "labyrinth": GrayScottParameters(feed=0.0367, kill=0.0649),
    "cellular": GrayScottParameters(feed=0.0545, kill=0.0620),
    "coral_growth": GrayScottParameters(feed=0.0250, kill=0.0600),
    "mitosis": GrayScottParameters(feed=0.0367, kill=0.0649),
    "solitons": GrayScottParameters(feed=0.0300, kill=0.0620),
}


class GrayScottField(DevelopmentalField):
    model_name = "gray_scott"

    def __init__(
        self,
        size: int,
        parameters: GrayScottParameters = GrayScottParameters(),
        seed: int = 23,
        seed_count: int = 14,
        seed_radius: int = 4,
    ) -> None:
        self.parameters = parameters
        self.seed_count = int(seed_count)
        self.seed_radius = int(seed_radius)
        super().__init__(size=size, seed=seed)

    @property
    def primary_field(self) -> Array:
        return self.u

    @property
    def secondary_field(self) -> Array:
        return self.v

    def reset(self) -> None:
        rng = np.random.default_rng(self.seed_value)
        u = np.ones((self.size, self.size), dtype=np.float32)
        v = np.zeros((self.size, self.size), dtype=np.float32)

        margin = max(self.seed_radius + 2, self.size // 12)
        for _ in range(max(1, self.seed_count)):
            cy = int(rng.integers(margin, self.size - margin))
            cx = int(rng.integers(margin, self.size - margin))
            radius = int(
                rng.integers(max(2, self.seed_radius // 2), self.seed_radius + 1)
            )
            yy, xx = np.ogrid[: self.size, : self.size]
            mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius**2
            u[mask] = rng.uniform(0.35, 0.55)
            v[mask] = rng.uniform(0.65, 0.95)

        u += rng.normal(0.0, 0.006, u.shape).astype(np.float32)
        v += rng.normal(0.0, 0.006, v.shape).astype(np.float32)

        self.u = mx.array(np.clip(u, 0.0, 1.0))
        self.v = mx.array(np.clip(v, 0.0, 1.0))
        self.step_count = 0
        mx.eval(self.u, self.v)

    def step(self, iterations: int = 1) -> None:
        p = self.parameters
        for _ in range(max(1, int(iterations))):
            lu = laplacian(self.u)
            lv = laplacian(self.v)
            reaction = self.u * self.v * self.v
            du = p.diffusion_u * lu - reaction + p.feed * (1.0 - self.u)
            dv = p.diffusion_v * lv + reaction - (p.feed + p.kill) * self.v
            self.u = mx.clip(self.u + p.dt * du, 0.0, 1.0)
            self.v = mx.clip(self.v + p.dt * dv, 0.0, 1.0)
            self.step_count += 1
        mx.eval(self.u, self.v)

    def perturb(
        self,
        x_norm: float,
        y_norm: float,
        radius_norm: float,
        amount: float,
    ) -> None:
        env = radial_envelope(self.size, x_norm, y_norm, radius_norm)
        amount = float(np.clip(amount, -1.0, 1.0))
        u = to_numpy(self.u)
        v = to_numpy(self.v)
        v = np.clip(v + amount * env, 0.0, 1.0)
        u = np.clip(u - 0.55 * amount * env, 0.0, 1.0)
        self.u = mx.array(u)
        self.v = mx.array(v)
        mx.eval(self.u, self.v)


# ---------------------------------------------------------------------------
# Classical activator-inhibitor
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TuringParameters:
    diffusion_activator: float = 0.010
    diffusion_inhibitor: float = 0.200
    activator_growth: float = 0.70
    inhibitor_growth: float = 0.60
    activator_decay: float = 0.55
    inhibitor_decay: float = 0.45
    cross_inhibition: float = 0.80
    dt: float = 0.10


TURING_PRESETS: dict[str, TuringParameters] = {
    "turing_stripes": TuringParameters(),
    "turing_spots": TuringParameters(
        activator_growth=0.82,
        inhibitor_growth=0.52,
        cross_inhibition=0.95,
    ),
    "segmentation": TuringParameters(
        diffusion_activator=0.006,
        diffusion_inhibitor=0.260,
        activator_decay=0.48,
    ),
}


class TuringActivatorInhibitorField(DevelopmentalField):
    model_name = "turing_activator_inhibitor"

    def __init__(
        self,
        size: int,
        parameters: TuringParameters = TuringParameters(),
        seed: int = 23,
    ) -> None:
        self.parameters = parameters
        super().__init__(size=size, seed=seed)

    @property
    def primary_field(self) -> Array:
        return self.inhibitor

    @property
    def secondary_field(self) -> Array:
        return self.activator

    def reset(self) -> None:
        rng = np.random.default_rng(self.seed_value)
        a = 0.20 + rng.normal(0.0, 0.025, (self.size, self.size))
        h = 0.20 + rng.normal(0.0, 0.025, (self.size, self.size))

        # One broad disturbance gives the homogeneous state something to amplify.
        env = radial_envelope(self.size, 0.5, 0.5, 0.12)
        a += 0.25 * env
        h -= 0.08 * env

        self.activator = mx.array(np.clip(a, 0.0, 1.5).astype(np.float32))
        self.inhibitor = mx.array(np.clip(h, 0.0, 1.5).astype(np.float32))
        self.step_count = 0
        mx.eval(self.activator, self.inhibitor)

    def step(self, iterations: int = 1) -> None:
        p = self.parameters
        for _ in range(max(1, int(iterations))):
            a = self.activator
            h = self.inhibitor
            da = (
                p.diffusion_activator * laplacian(a)
                + p.activator_growth * a
                - p.activator_decay * a * a * a
                - p.cross_inhibition * h
            )
            dh = (
                p.diffusion_inhibitor * laplacian(h)
                + p.inhibitor_growth * a
                - p.inhibitor_decay * h
            )
            self.activator = mx.clip(a + p.dt * da, 0.0, 2.0)
            self.inhibitor = mx.clip(h + p.dt * dh, 0.0, 2.0)
            self.step_count += 1
        mx.eval(self.activator, self.inhibitor)

    def perturb(
        self,
        x_norm: float,
        y_norm: float,
        radius_norm: float,
        amount: float,
    ) -> None:
        env = radial_envelope(self.size, x_norm, y_norm, radius_norm)
        amount = float(np.clip(amount, -1.0, 1.0))
        a = np.clip(to_numpy(self.activator) + amount * env, 0.0, 2.0)
        h = np.clip(to_numpy(self.inhibitor) - 0.25 * amount * env, 0.0, 2.0)
        self.activator = mx.array(a)
        self.inhibitor = mx.array(h)
        mx.eval(self.activator, self.inhibitor)


# ---------------------------------------------------------------------------
# FitzHugh-Nagumo excitable medium
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FitzHughNagumoParameters:
    diffusion_v: float = 0.18
    diffusion_w: float = 0.015
    epsilon: float = 0.018
    beta: float = 0.75
    gamma: float = 0.80
    stimulus: float = 0.00
    dt: float = 0.20


FHN_PRESETS: dict[str, FitzHughNagumoParameters] = {
    "excitable": FitzHughNagumoParameters(),
    "spiral_waves": FitzHughNagumoParameters(
        diffusion_v=0.22,
        epsilon=0.014,
        beta=0.72,
    ),
    "cardiac": FitzHughNagumoParameters(
        diffusion_v=0.25,
        diffusion_w=0.010,
        epsilon=0.012,
        gamma=0.72,
    ),
}


class FitzHughNagumoField(DevelopmentalField):
    model_name = "fitzhugh_nagumo"

    def __init__(
        self,
        size: int,
        parameters: FitzHughNagumoParameters = FitzHughNagumoParameters(),
        seed: int = 23,
    ) -> None:
        self.parameters = parameters
        super().__init__(size=size, seed=seed)

    @property
    def primary_field(self) -> Array:
        return self.recovery

    @property
    def secondary_field(self) -> Array:
        return self.voltage

    def reset(self) -> None:
        rng = np.random.default_rng(self.seed_value)
        v = -1.0 + rng.normal(0.0, 0.015, (self.size, self.size))
        w = -0.45 + rng.normal(0.0, 0.015, (self.size, self.size))

        # Broken wavefront to encourage spiral-wave formation.
        v[self.size // 4 : self.size // 2, self.size // 5 : 4 * self.size // 5] = 1.0
        v[self.size // 2 :, : self.size // 2] = -1.2

        self.voltage = mx.array(v.astype(np.float32))
        self.recovery = mx.array(w.astype(np.float32))
        self.step_count = 0
        mx.eval(self.voltage, self.recovery)

    def step(self, iterations: int = 1) -> None:
        p = self.parameters
        for _ in range(max(1, int(iterations))):
            v = self.voltage
            w = self.recovery
            dv = (
                p.diffusion_v * laplacian(v)
                + v
                - (v * v * v) / 3.0
                - w
                + p.stimulus
            )
            dw = (
                p.diffusion_w * laplacian(w)
                + p.epsilon * (v + p.beta - p.gamma * w)
            )
            self.voltage = mx.clip(v + p.dt * dv, -2.5, 2.5)
            self.recovery = mx.clip(w + p.dt * dw, -2.5, 2.5)
            self.step_count += 1
        mx.eval(self.voltage, self.recovery)

    def perturb(
        self,
        x_norm: float,
        y_norm: float,
        radius_norm: float,
        amount: float,
    ) -> None:
        env = radial_envelope(self.size, x_norm, y_norm, radius_norm)
        voltage = to_numpy(self.voltage)
        voltage = np.clip(voltage + 2.0 * float(amount) * env, -2.5, 2.5)
        self.voltage = mx.array(voltage)
        mx.eval(self.voltage)


# ---------------------------------------------------------------------------
# Damped wave developmental field
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WaveParameters:
    wave_speed: float = 0.32
    damping: float = 0.018
    nonlinear_gain: float = 0.10
    dt: float = 0.30


WAVE_PRESETS: dict[str, WaveParameters] = {
    "standing_wave": WaveParameters(),
    "chladni": WaveParameters(wave_speed=0.42, damping=0.010),
    "slow_membrane": WaveParameters(wave_speed=0.18, damping=0.028),
}


class WaveDevelopmentalField(DevelopmentalField):
    model_name = "wave"

    def __init__(
        self,
        size: int,
        parameters: WaveParameters = WaveParameters(),
        seed: int = 23,
    ) -> None:
        self.parameters = parameters
        super().__init__(size=size, seed=seed)

    @property
    def primary_field(self) -> Array:
        return self.velocity

    @property
    def secondary_field(self) -> Array:
        return self.displacement

    def reset(self) -> None:
        rng = np.random.default_rng(self.seed_value)
        displacement = rng.normal(0.0, 0.002, (self.size, self.size)).astype(np.float32)
        displacement += 0.8 * radial_envelope(self.size, 0.38, 0.50, 0.05)
        displacement -= 0.6 * radial_envelope(self.size, 0.62, 0.50, 0.05)
        self.displacement = mx.array(displacement)
        self.velocity = mx.zeros((self.size, self.size), dtype=mx.float32)
        self.step_count = 0
        mx.eval(self.displacement, self.velocity)

    def step(self, iterations: int = 1) -> None:
        p = self.parameters
        for _ in range(max(1, int(iterations))):
            acceleration = (
                p.wave_speed * p.wave_speed * laplacian(self.displacement)
                - p.damping * self.velocity
                - p.nonlinear_gain * self.displacement**3
            )
            self.velocity = self.velocity + p.dt * acceleration
            self.displacement = self.displacement + p.dt * self.velocity
            self.step_count += 1
        mx.eval(self.displacement, self.velocity)

    def geometry_fields(self) -> tuple[Array, Array]:
        amplitude = mx.abs(self.displacement)
        velocity = mx.abs(self.velocity)
        return normalize01(velocity), normalize01(amplitude)

    def perturb(
        self,
        x_norm: float,
        y_norm: float,
        radius_norm: float,
        amount: float,
    ) -> None:
        env = radial_envelope(self.size, x_norm, y_norm, radius_norm)
        displacement = to_numpy(self.displacement)
        displacement += float(amount) * env
        self.displacement = mx.array(displacement.astype(np.float32))
        mx.eval(self.displacement)


# ---------------------------------------------------------------------------
# Slow bioelectric memory field
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BioelectricParameters:
    diffusion_voltage: float = 0.080
    leakage: float = 0.012
    bistability: float = 0.090
    coupling: float = 0.18
    memory_rate: float = 0.015
    memory_decay: float = 0.002
    dt: float = 0.25


BIOELECTRIC_PRESETS: dict[str, BioelectricParameters] = {
    "bioelectric_memory": BioelectricParameters(),
    "regenerative": BioelectricParameters(
        bistability=0.125,
        memory_rate=0.022,
        memory_decay=0.001,
    ),
    "plastic": BioelectricParameters(
        leakage=0.020,
        memory_rate=0.030,
        memory_decay=0.008,
    ),
}


class BioelectricMemoryField(DevelopmentalField):
    model_name = "bioelectric_memory"

    def __init__(
        self,
        size: int,
        parameters: BioelectricParameters = BioelectricParameters(),
        seed: int = 23,
    ) -> None:
        self.parameters = parameters
        self.external_drive = mx.zeros((size, size), dtype=mx.float32)
        super().__init__(size=size, seed=seed)

    @property
    def primary_field(self) -> Array:
        return self.memory

    @property
    def secondary_field(self) -> Array:
        return self.voltage

    def reset(self) -> None:
        rng = np.random.default_rng(self.seed_value)
        voltage = rng.normal(0.0, 0.025, (self.size, self.size)).astype(np.float32)
        voltage += 0.45 * radial_envelope(self.size, 0.35, 0.50, 0.10)
        voltage -= 0.45 * radial_envelope(self.size, 0.65, 0.50, 0.10)
        self.voltage = mx.array(voltage)
        self.memory = mx.zeros((self.size, self.size), dtype=mx.float32)
        self.external_drive = mx.zeros((self.size, self.size), dtype=mx.float32)
        self.step_count = 0
        mx.eval(self.voltage, self.memory, self.external_drive)

    def set_external_drive(self, drive: Array | np.ndarray | float) -> None:
        if np.isscalar(drive):
            self.external_drive = mx.full(
                (self.size, self.size), float(drive), dtype=mx.float32
            )
        else:
            array = mx.array(np.asarray(drive, dtype=np.float32))
            if tuple(array.shape) != (self.size, self.size):
                raise ValueError(
                    f"external drive must have shape {(self.size, self.size)}"
                )
            self.external_drive = array
        mx.eval(self.external_drive)

    def step(self, iterations: int = 1) -> None:
        p = self.parameters
        for _ in range(max(1, int(iterations))):
            v = self.voltage
            m = self.memory

            # Cubic bistability supplies two preferred voltage organizations.
            bistable_term = p.bistability * (v - v**3)
            dv = (
                p.diffusion_voltage * laplacian(v)
                - p.leakage * v
                + bistable_term
                + p.coupling * m
                + self.external_drive
            )
            dm = p.memory_rate * mx.tanh(v) - p.memory_decay * m

            self.voltage = mx.clip(v + p.dt * dv, -1.5, 1.5)
            self.memory = mx.clip(m + p.dt * dm, -1.5, 1.5)
            self.step_count += 1
        mx.eval(self.voltage, self.memory)

    def geometry_fields(self) -> tuple[Array, Array]:
        # Memory acts as substrate; voltage domains act as active growth.
        return normalize01(self.memory), normalize01(self.voltage)

    def perturb(
        self,
        x_norm: float,
        y_norm: float,
        radius_norm: float,
        amount: float,
    ) -> None:
        env = radial_envelope(self.size, x_norm, y_norm, radius_norm)
        voltage = np.clip(
            to_numpy(self.voltage) + float(amount) * env,
            -1.5,
            1.5,
        )
        self.voltage = mx.array(voltage.astype(np.float32))
        mx.eval(self.voltage)


# ---------------------------------------------------------------------------
# Registry and factory
# ---------------------------------------------------------------------------

FIELD_PRESETS: dict[str, tuple[type[DevelopmentalField], Any]] = {
    **{name: (GrayScottField, params) for name, params in GRAY_SCOTT_PRESETS.items()},
    **{
        name: (TuringActivatorInhibitorField, params)
        for name, params in TURING_PRESETS.items()
    },
    **{
        name: (FitzHughNagumoField, params)
        for name, params in FHN_PRESETS.items()
    },
    **{
        name: (WaveDevelopmentalField, params)
        for name, params in WAVE_PRESETS.items()
    },
    **{
        name: (BioelectricMemoryField, params)
        for name, params in BIOELECTRIC_PRESETS.items()
    },
}


def create_developmental_field(
    preset: str,
    *,
    size: int = 192,
    seed: int = 23,
    seed_count: int = 14,
    seed_radius: int = 4,
) -> DevelopmentalField:
    if preset not in FIELD_PRESETS:
        raise ValueError(
            f"unknown developmental-field preset {preset!r}; "
            f"choose from: {', '.join(sorted(FIELD_PRESETS))}"
        )

    field_class, parameters = FIELD_PRESETS[preset]
    if field_class is GrayScottField:
        return GrayScottField(
            size=size,
            parameters=parameters,
            seed=seed,
            seed_count=seed_count,
            seed_radius=seed_radius,
        )
    return field_class(size=size, parameters=parameters, seed=seed)


# Backward-compatible names for emergent_geometry_engine_v1.
MorphogenParameters = GrayScottParameters
MorphogenField = GrayScottField
PRESETS = GRAY_SCOTT_PRESETS


__all__ = [
    "DevelopmentalField",
    "GrayScottParameters",
    "GrayScottField",
    "TuringParameters",
    "TuringActivatorInhibitorField",
    "FitzHughNagumoParameters",
    "FitzHughNagumoField",
    "WaveParameters",
    "WaveDevelopmentalField",
    "BioelectricParameters",
    "BioelectricMemoryField",
    "FIELD_PRESETS",
    "create_developmental_field",
    "laplacian",
    "normalize01",
    "MorphogenParameters",
    "MorphogenField",
    "PRESETS",
]
