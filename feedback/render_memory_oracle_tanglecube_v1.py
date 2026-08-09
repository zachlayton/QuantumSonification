#!/usr/bin/env python3
"""Sonify a quantum-memory oracle as rotations of the Tangle Cube reverb.

The Tangle Cube's measured surface-Laplacian frequencies and eigenvectors are
kept fixed.  Each oracle eigenphase produces an incremental SO(3) rotation.
Source and listener remain fixed in world coordinates, so rotating the surface
changes their coupling to every spatial eigenmode without changing the modal
spectrum itself.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from density.density_matrix_modal_renderer_v2 import write_wav
from density.render_grover_density_pauli64_v1 import (
    Pauli64RenderConfig,
    pauli_labels,
    render_pauli64_audio,
)
from density.render_grover_density_modal_v1 import GroverModalConfig, grover_modal_trajectory
from feedback.quantum_memory import QuantumMemory
from feedback.quantum_memory_oracle_v1 import QuantumMemoryOracleResult, build_quantum_memory_oracle


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TANGLE_PACKET = (
    PROJECT_ROOT
    / "algebraic_surfaces/tanglecube_v1/living/state_000002/spectral_geometry.npz"
)


@dataclass(frozen=True)
class TangleCubeOracleRenderConfig:
    output_path: Path = PROJECT_ROOT / "output/memory_oracle_tanglecube_frequency_morph_v1.wav"
    static_output_path: Path = PROJECT_ROOT / "output/memory_oracle_tanglecube_fixed_frequency_control_v1.wav"
    diagnostics_path: Path = PROJECT_ROOT / "output/memory_oracle_tanglecube_frequency_morph_v1.json"
    tangle_packet: Path = DEFAULT_TANGLE_PACKET
    sample_rate: int = 48_000
    duration_seconds: float = 14.0
    wet_gain: float = 0.7
    dry_gain: float = 0.055
    pauli64_source_gain: float = 0.42
    output_ceiling: float = 0.82
    ear_angle_degrees: float = 13.0
    rotation_slew_seconds: float = 1.15
    spatial_control_rate_hz: float = 72.0
    pan_depth: float = 0.92
    mode_morph_depth: float = 0.88
    geometry_surface_depth: float = 0.7
    geometry_modal_warp_depth: float = 0.65
    wet_ring_mod_depth: float = 0.8
    wet_ring_mod_max_hz: float = 42.0
    source_direction: tuple[float, float, float] = (0.82, 0.31, 0.48)
    listener_direction: tuple[float, float, float] = (-0.38, 0.86, 0.34)

    def __post_init__(self) -> None:
        if self.sample_rate < 8_000:
            raise ValueError("sample_rate must be at least 8000 Hz")
        if not math.isfinite(self.duration_seconds) or self.duration_seconds <= 0.0:
            raise ValueError("duration_seconds must be positive")
        if self.wet_gain <= 0.0 or self.dry_gain < 0.0:
            raise ValueError("wet_gain must be positive and dry_gain non-negative")
        if self.pauli64_source_gain <= 0.0:
            raise ValueError("pauli64_source_gain must be positive")
        if not 0.0 < self.output_ceiling <= 1.0:
            raise ValueError("output_ceiling must be in (0, 1]")
        if not math.isfinite(self.rotation_slew_seconds) or self.rotation_slew_seconds <= 0.0:
            raise ValueError("rotation_slew_seconds must be positive")
        if self.spatial_control_rate_hz < 10.0:
            raise ValueError("spatial_control_rate_hz must be at least 10 Hz")
        if not 0.0 <= self.pan_depth <= 1.0:
            raise ValueError("pan_depth must be in [0, 1]")
        if not 0.0 <= self.mode_morph_depth <= 1.0:
            raise ValueError("mode_morph_depth must be in [0, 1]")
        if not 0.0 <= self.geometry_surface_depth <= 0.85:
            raise ValueError("geometry_surface_depth must be in [0, 0.85]")
        if not 0.0 <= self.geometry_modal_warp_depth <= 1.0:
            raise ValueError("geometry_modal_warp_depth must be in [0, 1]")
        if not 0.0 <= self.wet_ring_mod_depth <= 1.0:
            raise ValueError("wet_ring_mod_depth must be in [0, 1]")
        if self.wet_ring_mod_max_hz < 0.0:
            raise ValueError("wet_ring_mod_max_hz must be non-negative")


@dataclass(frozen=True)
class TangleCubeModalField:
    vertices: np.ndarray
    directions: np.ndarray
    eigenvectors: np.ndarray
    frequencies_hz: np.ndarray
    decay_times_seconds: np.ndarray
    mode_weights: np.ndarray


def _unit(vector: np.ndarray | tuple[float, ...]) -> np.ndarray:
    value = np.asarray(vector, dtype=np.float64)
    norm = float(np.linalg.norm(value))
    if norm <= 1e-12:
        raise ValueError("direction vectors must be nonzero")
    return value / norm


def load_tanglecube_modal_field(path: str | Path) -> TangleCubeModalField:
    """Load the real Tangle Cube mesh and join it to its material decay data."""
    spectral_path = Path(path)
    with np.load(spectral_path, allow_pickle=False) as packet:
        vertices = np.asarray(packet["vertices"], dtype=np.float64)
        eigenvectors = np.asarray(packet["eigenvectors"], dtype=np.float64)
        frequencies = np.asarray(packet["frequencies_hz"], dtype=np.float64)
        weights = np.asarray(packet["mode_weights"], dtype=np.float64)
    material_path = spectral_path.with_name("surface_material.npz")
    with np.load(material_path, allow_pickle=False) as material:
        decay = np.asarray(material["decay_times_seconds"], dtype=np.float64)
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError("Tangle Cube vertices must have shape (N, 3)")
    if eigenvectors.shape != (len(vertices), len(frequencies)):
        raise ValueError("Tangle Cube eigenvector dimensions do not match the mesh")
    directions = vertices / np.maximum(np.linalg.norm(vertices, axis=1)[:, None], 1e-12)
    return TangleCubeModalField(
        vertices=vertices,
        directions=directions,
        eigenvectors=eigenvectors,
        frequencies_hz=frequencies,
        decay_times_seconds=decay,
        mode_weights=weights,
    )


def reference_memory_oracle() -> QuantumMemoryOracleResult:
    """Recreate the seven-state memory and near-return query used in Phase 3."""
    trajectory = grover_modal_trajectory(GroverModalConfig())
    memory = QuantumMemory(max_snapshots=32)
    for index, (rho, metrics) in enumerate(zip(trajectory.states, trajectory.metrics)):
        memory.encode(
            rho,
            events=[f"grover-state-{index}"],
            metrics={
                "marked_probability": metrics.marked_probability,
                "purity": metrics.purity,
                "coherence_l1": metrics.coherence_l1,
            },
        )
    dimension = trajectory.states[4].shape[0]
    query = 0.94 * trajectory.states[4] + 0.06 * np.eye(dimension) / dimension
    return build_quantum_memory_oracle(memory, query)


def _single_qubit_pauli(n_qubits: int, qubit: int, axis: str) -> np.ndarray:
    pauli = {
        "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
        "Y": np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128),
        "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
    }
    result = np.array([[1.0 + 0.0j]])
    for tensor_qubit in reversed(range(n_qubits)):
        result = np.kron(result, pauli[axis] if tensor_qubit == qubit else np.eye(2))
    return result


def oracle_rotation_axes(result: QuantumMemoryOracleResult) -> np.ndarray:
    """Derive one real 3-D axis from each memory-generator eigenvector.

    Weighted local Bloch vectors retain qubit identity.  Maximally entangled
    eigenvectors can have zero local polarization, so deterministic spherical
    fallback axes cover that physically meaningful degenerate case.
    """
    _, eigenvectors = np.linalg.eigh(result.resonance_generator)
    dimension = eigenvectors.shape[0]
    n_qubits = int(round(math.log2(dimension)))
    operators = {
        axis: [_single_qubit_pauli(n_qubits, qubit, axis) for qubit in range(n_qubits)]
        for axis in "XYZ"
    }
    qubit_weights = np.linspace(1.0, 1.7, n_qubits)
    axes: list[np.ndarray] = []
    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    for index, vector in enumerate(eigenvectors.T):
        components = np.array(
            [
                sum(
                    weight * float(np.vdot(vector, operator @ vector).real)
                    for weight, operator in zip(qubit_weights, operators[axis])
                )
                for axis in "XYZ"
            ]
        )
        if np.linalg.norm(components) <= 1e-9:
            z = 1.0 - 2.0 * (index + 0.5) / dimension
            radius = math.sqrt(max(0.0, 1.0 - z * z))
            components = np.array(
                [radius * math.cos(index * golden_angle), radius * math.sin(index * golden_angle), z]
            )
        axes.append(_unit(components))
    return np.asarray(axes)


def axis_angle_rotation(axis: np.ndarray, angle: float) -> np.ndarray:
    """Rodrigues rotation matrix for a right-handed axis-angle turn."""
    x, y, z = _unit(axis)
    skew = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + math.sin(angle) * skew + (1.0 - math.cos(angle)) * (skew @ skew)


def oracle_rotation_path(result: QuantumMemoryOracleResult) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return phases, axes, and cumulative noncommuting orientations."""
    phases = np.asarray(result.phase_angles, dtype=np.float64)
    axes = oracle_rotation_axes(result)
    orientation = np.eye(3)
    orientations: list[np.ndarray] = []
    for phase, axis in zip(phases, axes):
        orientation = axis_angle_rotation(axis, float(phase)) @ orientation
        orientations.append(orientation.copy())
    return phases, axes, np.asarray(orientations)


def slewed_oracle_orientations(
    times: np.ndarray,
    event_times: np.ndarray,
    phases: np.ndarray,
    axes: np.ndarray,
    slew_seconds: float,
) -> np.ndarray:
    """Evaluate the noncommuting rotation path with raised-cosine slews."""
    sample_times = np.asarray(times, dtype=np.float64)
    events = np.asarray(event_times, dtype=np.float64)
    if sample_times.ndim != 1 or events.shape != phases.shape or axes.shape != (len(phases), 3):
        raise ValueError("slew path dimensions do not match")
    if slew_seconds <= 0.0:
        raise ValueError("slew_seconds must be positive")
    orientations: list[np.ndarray] = []
    for time in sample_times:
        orientation = np.eye(3)
        for event_time, phase, axis in zip(events, phases, axes):
            progress = (float(time) - float(event_time)) / slew_seconds
            if progress <= 0.0:
                break
            if progress >= 1.0:
                amount = 1.0
            else:
                amount = 0.5 - 0.5 * math.cos(math.pi * progress)
            orientation = axis_angle_rotation(axis, float(phase) * amount) @ orientation
        orientations.append(orientation)
    return np.asarray(orientations)


def slewed_collective_phase(
    times: np.ndarray,
    event_times: np.ndarray,
    phases: np.ndarray,
    slew_seconds: float,
) -> np.ndarray:
    """Return the continuously accumulated scalar oracle winding."""
    values = np.zeros(len(times), dtype=np.float64)
    for index, time in enumerate(np.asarray(times, dtype=np.float64)):
        total = 0.0
        for event_time, phase in zip(event_times, phases):
            progress = (float(time) - float(event_time)) / slew_seconds
            if progress <= 0.0:
                break
            amount = 1.0 if progress >= 1.0 else 0.5 - 0.5 * math.cos(math.pi * progress)
            total += float(phase) * amount
        values[index] = total
    return values


def ideal_grover_angles(
    n_qubits: int, marked_count: int, state_count: int
) -> tuple[float, np.ndarray]:
    """Return theta and alpha_k=(2k+1)theta for Grover's amplitude plane."""
    dimension = 1 << n_qubits
    if not 0 < marked_count < dimension:
        raise ValueError("marked_count must be between zero and the Hilbert dimension")
    if state_count < 1:
        raise ValueError("state_count must be positive")
    theta = math.asin(math.sqrt(marked_count / dimension))
    return theta, np.asarray([(2 * index + 1) * theta for index in range(state_count)])


def smooth_state_trajectory(
    times: np.ndarray, event_times: np.ndarray, values: np.ndarray
) -> np.ndarray:
    """Raised-cosine interpolation through successive state values."""
    sample_times = np.asarray(times, dtype=np.float64)
    events = np.asarray(event_times, dtype=np.float64)
    states = np.asarray(values, dtype=np.float64)
    if events.ndim != 1 or states.ndim != 1 or len(events) != len(states) or len(events) == 0:
        raise ValueError("event_times and values must be matching non-empty vectors")
    output = np.empty_like(sample_times)
    for index, time in enumerate(sample_times):
        if time <= events[0]:
            output[index] = states[0]
            continue
        if time >= events[-1]:
            output[index] = states[-1]
            continue
        right = int(np.searchsorted(events, time, side="right"))
        left = right - 1
        fraction = (time - events[left]) / (events[right] - events[left])
        amount = 0.5 - 0.5 * math.cos(math.pi * float(fraction))
        output[index] = states[left] + amount * (states[right] - states[left])
    return output


def _rotate_about_z(direction: np.ndarray, angle: float) -> np.ndarray:
    return axis_angle_rotation(np.array([0.0, 0.0, 1.0]), angle) @ direction


def spatial_modal_coupling(
    field: TangleCubeModalField,
    orientation: np.ndarray,
    source_world: np.ndarray,
    listener_world: np.ndarray,
    ear_angle_radians: float,
) -> tuple[np.ndarray, tuple[int, int, int]]:
    """Interpolate phi(source)*phi(listener) after rotating into room space."""
    inverse = orientation.T
    source_room = inverse @ _unit(source_world)
    listener_left = inverse @ _rotate_about_z(_unit(listener_world), ear_angle_radians)
    listener_right = inverse @ _rotate_about_z(_unit(listener_world), -ear_angle_radians)

    def sample_modes(direction: np.ndarray, neighborhood: int = 24) -> tuple[np.ndarray, int]:
        similarity = field.directions @ direction
        nearest = np.argpartition(similarity, -neighborhood)[-neighborhood:]
        local = similarity[nearest]
        # A spherical Gaussian yields continuous sub-vertex motion while
        # remaining local enough to preserve the surface eigenfield pattern.
        weights = np.exp(240.0 * (local - float(np.max(local))))
        weights /= np.sum(weights)
        return weights @ field.eigenvectors[nearest], int(nearest[np.argmax(local)])

    source_modes, source_index = sample_modes(source_room)
    left_modes, left_index = sample_modes(listener_left)
    right_modes, right_index = sample_modes(listener_right)
    indices = (source_index, left_index, right_index)
    left = source_modes * left_modes * field.mode_weights
    right = source_modes * right_modes * field.mode_weights
    coupling = np.column_stack((left, right))
    scale = float(np.sqrt(np.mean(np.square(coupling))))
    if scale > 1e-15:
        coupling /= scale
    return coupling, indices


def orientation_sonification_controls(
    orientation: np.ndarray,
    mode_count: int,
    pan_depth: float,
    mode_morph_depth: float,
    sonic_angle: float | None = None,
    amplification: float | None = None,
) -> tuple[float, float, np.ndarray]:
    """Map room orientation to explicit pan and a moving modal aperture."""
    room_forward = np.asarray(orientation, dtype=np.float64) @ np.array([1.0, 0.0, 0.0])
    if sonic_angle is None:
        pan_position = room_forward[1]
        mode_position = room_forward[2]
    else:
        # The scalar winding gives an unmistakable circular auditory gesture;
        # the noncommuting matrix orientation still controls eigenfield pickup.
        pan_position = math.sin(float(sonic_angle))
        mode_position = math.sin(0.73 * float(sonic_angle))
    pan = float(np.clip(pan_depth * pan_position, -0.98, 0.98))
    if amplification is None:
        center_normalized = float(np.clip(0.5 + 0.46 * mode_position, 0.04, 0.96))
    else:
        # Approaching the marked axis opens progressively higher Tangle modes.
        center_normalized = float(np.clip(0.15 + 0.75 * amplification, 0.04, 0.96))
    center = center_normalized * (mode_count - 1)
    indices = np.arange(mode_count, dtype=np.float64)
    width = max(1.5, 0.22 * mode_count)
    aperture = np.exp(-0.5 * np.square((indices - center) / width))
    aperture /= max(float(np.mean(aperture)), 1e-12)
    aperture = (1.0 - mode_morph_depth) + mode_morph_depth * aperture
    return pan, center, aperture


def geometry_reverb_frequency_ratios(
    orientations: np.ndarray,
    collective_angles: np.ndarray,
    mode_count: int,
    *,
    surface_depth: float = 0.35,
    modal_warp_depth: float = 0.65,
) -> np.ndarray:
    """Port the realtime geometry reverb's rotation-to-delay deformation."""
    matrices = np.asarray(orientations, dtype=np.float64)
    angles = np.asarray(collective_angles, dtype=np.float64)
    if matrices.ndim != 3 or matrices.shape[1:] != (3, 3) or len(matrices) != len(angles):
        raise ValueError("orientation and collective-angle controls must align")
    if mode_count < 1:
        raise ValueError("mode_count must be positive")
    offsets = np.array([-0.42, 0.36, -0.28, 0.46, -0.22, 0.31, -0.49, 0.27])
    warp_coefficients = np.array([-0.18, 0.14, -0.10, 0.07, -0.05, 0.09, -0.13, 0.17])
    deform_amount = (0.04 + 1.28 * surface_depth) * 0.88
    delay_logs: list[np.ndarray] = []
    for orientation, collective in zip(matrices, angles):
        # XYZ Euler extraction for R = Rz Ry Rx, matching the Max controls.
        ry = math.asin(float(np.clip(-orientation[2, 0], -1.0, 1.0)))
        rx = math.atan2(float(orientation[2, 1]), float(orientation[2, 2]))
        rz = math.atan2(float(orientation[1, 0]), float(orientation[0, 0]))
        rxs, rxc = math.sin(rx), math.cos(rx)
        rys, ryc = math.sin(ry), math.cos(ry)
        rzs, rzc = math.sin(rz), math.cos(rz)
        rotation_lanes = np.array(
            [
                0.62 * rxs + 0.31 * rys + 0.18 * rzs,
                -0.48 * rxs + 0.46 * rys - 0.27 * rzs,
                0.35 * rxs - 0.58 * rys + 0.39 * rzs,
                -0.57 * rxs - 0.29 * rys - 0.36 * rzs,
                0.44 * rxc + 0.36 * rys - 0.31 * rzs,
                -0.38 * rxs + 0.51 * ryc + 0.28 * rzs,
                0.29 * rxs - 0.41 * rys + 0.52 * rzc,
                -0.53 * rxc - 0.34 * ryc - 0.26 * rzs,
            ]
        )
        geometry = 0.48 * rotation_lanes + offsets
        modal_warp = modal_warp_depth * math.sin(float(collective))
        delay_logs.append(deform_amount * geometry + warp_coefficients * modal_warp)
    lane_logs = np.asarray(delay_logs)
    baseline = lane_logs[0]
    lane_frequency_ratios = np.exp(baseline[None, :] - lane_logs)
    return lane_frequency_ratios[:, np.arange(mode_count) % 8]


def render_time_varying_modal_reverb(
    source: np.ndarray,
    frequencies_hz: np.ndarray,
    decay_seconds: np.ndarray,
    control_frequency_ratios: np.ndarray,
    control_couplings: np.ndarray,
    sample_rate: int,
    *,
    ring_mod_depth: float = 0.0,
    ring_mod_max_hz: float = 0.0,
) -> np.ndarray:
    """Run a stable modal bank whose resonance frequencies move over time."""
    excitation = np.asarray(source, dtype=np.float64).reshape(-1)
    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    decay = np.asarray(decay_seconds, dtype=np.float64)
    control_count, mode_count = control_frequency_ratios.shape
    if control_couplings.shape != (control_count, mode_count, 2):
        raise ValueError("frequency and spatial control dimensions do not match")
    if len(frequencies) != mode_count or len(decay) != mode_count:
        raise ValueError("modal arrays do not match control mode count")
    output = np.zeros((len(excitation), 2), dtype=np.float64)
    previous = np.zeros(mode_count, dtype=np.float64)
    previous2 = np.zeros(mode_count, dtype=np.float64)
    radius = np.exp(-1.0 / np.maximum(decay * sample_rate, 1.0))
    radius2 = radius * radius
    ring_phase = np.zeros(mode_count, dtype=np.float64)
    ring_spread = np.linspace(0.45, 1.0, mode_count)
    denominator = max(len(excitation) - 1, 1)
    for sample_index, sample in enumerate(excitation):
        control_position = sample_index * (control_count - 1) / denominator
        left_index = min(control_count - 2, int(control_position))
        fraction = control_position - left_index
        ratios = (
            (1.0 - fraction) * control_frequency_ratios[left_index]
            + fraction * control_frequency_ratios[left_index + 1]
        )
        coupling = (
            (1.0 - fraction) * control_couplings[left_index]
            + fraction * control_couplings[left_index + 1]
        )
        angular = 2.0 * math.pi * np.clip(
            frequencies * ratios, 20.0, sample_rate * 0.44
        ) / sample_rate
        # Equal-energy excitation keeps long-decay modes audible without the
        # severe attenuation produced by a unity-steady-state normalization.
        drive = np.sqrt(np.maximum(1.0 - radius2, 0.0)) * np.sin(angular) * sample
        current = drive + 2.0 * radius * np.cos(angular) * previous - radius2 * previous2
        ring_frequency = ring_mod_max_hz * (ratios - 1.0) * ring_spread
        ring_phase += 2.0 * math.pi * ring_frequency / sample_rate
        ring_phase = np.remainder(ring_phase + math.pi, 2.0 * math.pi) - math.pi
        ring_multiplier = (1.0 - ring_mod_depth) + ring_mod_depth * np.cos(ring_phase)
        wet_modes = current * ring_multiplier
        output[sample_index] = np.sum(coupling * wet_modes[:, None], axis=0) / math.sqrt(mode_count)
        previous2 = previous
        previous = current
    return output


def render_tanglecube_oracle_audio(
    config: TangleCubeOracleRenderConfig,
    *,
    rotate_geometry: bool = True,
) -> tuple[np.ndarray, dict[str, object]]:
    """Render eight oracle phase events through spatial Tangle Cube modes."""
    field = load_tanglecube_modal_field(config.tangle_packet)
    oracle = reference_memory_oracle()
    phases, axes, orientations = oracle_rotation_path(oracle)

    sample_rate = config.sample_rate
    total_samples = max(1, int(round(config.duration_seconds * sample_rate)))
    pauli_source, coefficient_history = render_pauli64_audio(
        Pauli64RenderConfig(
            sample_rate=sample_rate,
            duration_seconds=config.duration_seconds,
            output_ceiling=0.78,
        )
    )
    audio = config.pauli64_source_gain * pauli_source
    oracle_event_times = np.linspace(0.28, config.duration_seconds * 0.76, len(phases))
    visited: list[tuple[int, int, int]] = []
    coupling_signatures: list[tuple[float, ...]] = []

    control_count = max(2, int(math.ceil(config.duration_seconds * config.spatial_control_rate_hz)) + 1)
    control_times = np.linspace(0.0, config.duration_seconds, control_count)
    if rotate_geometry:
        control_orientations = slewed_oracle_orientations(
            control_times,
            oracle_event_times,
            phases,
            axes,
            config.rotation_slew_seconds,
        )
        control_sonic_angles = slewed_collective_phase(
            control_times,
            oracle_event_times,
            phases,
            config.rotation_slew_seconds,
        )
    else:
        control_orientations = np.repeat(np.eye(3)[None, :, :], control_count, axis=0)
        control_sonic_angles = np.zeros(control_count, dtype=np.float64)
    control_couplings = np.empty((control_count, len(field.frequencies_hz), 2), dtype=np.float64)
    control_indices: list[tuple[int, int, int]] = []
    control_pans = np.empty(control_count, dtype=np.float64)
    control_mode_centers = np.empty(control_count, dtype=np.float64)
    for control_index, orientation in enumerate(control_orientations):
        coupling, indices = spatial_modal_coupling(
            field,
            orientation,
            np.asarray(config.source_direction),
            np.asarray(config.listener_direction),
            math.radians(config.ear_angle_degrees),
        )
        pan, mode_center, aperture = orientation_sonification_controls(
            orientation,
            len(field.frequencies_hz),
            config.pan_depth,
            config.mode_morph_depth,
            float(control_sonic_angles[control_index]),
        )
        # Center is unity gain.  Moving away from center explicitly shifts the
        # reverberant image while preserving the eigenfield's own L/R detail.
        coupling[:, 0] *= math.sqrt(1.0 - pan) * aperture
        coupling[:, 1] *= math.sqrt(1.0 + pan) * aperture
        control_couplings[control_index] = coupling
        control_indices.append(indices)
        control_pans[control_index] = pan
        control_mode_centers[control_index] = mode_center

    for event_time in oracle_event_times:
        event_control_index = int(np.argmin(np.abs(control_times - event_time)))
        coupling = control_couplings[event_control_index]
        indices = control_indices[event_control_index]
        visited.append(indices)
        coupling_signatures.append(tuple(np.round(coupling.reshape(-1), 10)))

    # The exact 64-Pauli rendering is the source.  The realtime geometry
    # reverb's delay-deformation mapping now bends the measured Tangle modes.
    sample_times = np.arange(total_samples, dtype=np.float64) / sample_rate
    audio = config.pauli64_source_gain * pauli_source
    mono_source = np.mean(pauli_source, axis=1)
    control_frequency_ratios = geometry_reverb_frequency_ratios(
        control_orientations,
        control_sonic_angles,
        len(field.frequencies_hz),
        surface_depth=config.geometry_surface_depth,
        modal_warp_depth=config.geometry_modal_warp_depth,
    )
    wet = config.wet_gain * render_time_varying_modal_reverb(
        mono_source,
        field.frequencies_hz,
        field.decay_times_seconds,
        control_frequency_ratios,
        control_couplings,
        sample_rate,
        ring_mod_depth=config.wet_ring_mod_depth,
        ring_mod_max_hz=config.wet_ring_mod_max_hz,
    )
    audio += wet

    audio -= np.mean(audio, axis=0, keepdims=True)
    fade_samples = min(total_samples // 2, int(round(0.035 * sample_rate)))
    if fade_samples > 1:
        fade = np.linspace(0.0, 1.0, fade_samples)
        audio[:fade_samples] *= fade[:, None]
        audio[-fade_samples:] *= fade[::-1, None]
    peak = float(np.max(np.abs(audio)))
    if peak > 1e-12:
        audio *= config.output_ceiling / peak

    diagnostics: dict[str, object] = {
        "surface": "tanglecube",
        "rotate_geometry": rotate_geometry,
        "source_representation": "exact_pauli64",
        "source_mode_count": 64,
        "pauli_labels": list(pauli_labels(3)),
        "pauli_active_coefficients": [
            sum(abs(value) > 1e-6 for value in coefficients.values())
            for coefficients in coefficient_history
        ],
        "vertex_count": int(len(field.vertices)),
        "mode_count": int(len(field.frequencies_hz)),
        "oracle_effective_strength": oracle.effective_strength,
        "oracle_aggregate_resonance": oracle.aggregate_resonance,
        "phase_degrees": np.degrees(phases).tolist(),
        "collective_phase_degrees": float(np.degrees(np.sum(phases))),
        "rotation_axes": axes.tolist(),
        "final_orientation": orientations[-1].tolist(),
        "rotation_slew_seconds": config.rotation_slew_seconds,
        "spatial_control_rate_hz": config.spatial_control_rate_hz,
        "pan_range": [float(np.min(control_pans)), float(np.max(control_pans))],
        "mode_center_range": [
            float(np.min(control_mode_centers)),
            float(np.max(control_mode_centers)),
        ],
        "event_pan_positions": np.interp(oracle_event_times, control_times, control_pans).tolist(),
        "event_mode_centers": np.interp(
            oracle_event_times, control_times, control_mode_centers
        ).tolist(),
        "collective_phase_slew_degrees": np.degrees(control_sonic_angles).tolist(),
        "sampled_vertex_indices": [list(item) for item in visited],
        "unique_spatial_samples": len(set(visited)),
        "unique_modal_couplings": len(set(coupling_signatures)),
        "unique_control_vertex_samples": len(set(control_indices)),
        "frequencies_hz": field.frequencies_hz.tolist(),
        "tangle_reverb_mode_count": int(len(field.frequencies_hz)),
        "frequency_morph_model": "qmw_realtime_surface_reverb_delay_deformation",
        "frequency_ratio_range": [
            float(np.min(control_frequency_ratios)),
            float(np.max(control_frequency_ratios)),
        ],
        "morphed_frequency_range_hz": [
            float(np.min(control_frequency_ratios * field.frequencies_hz[None, :])),
            float(np.max(control_frequency_ratios * field.frequencies_hz[None, :])),
        ],
        "wet_ring_mod_depth": config.wet_ring_mod_depth,
        "wet_ring_mod_rate_range_hz": [
            float(np.min(config.wet_ring_mod_max_hz * (control_frequency_ratios - 1.0))),
            float(np.max(config.wet_ring_mod_max_hz * (control_frequency_ratios - 1.0))),
        ],
        "dry_source_rms": float(np.sqrt(np.mean(np.square(config.pauli64_source_gain * pauli_source)))),
        "wet_reverb_rms": float(np.sqrt(np.mean(np.square(wet)))),
    }
    return np.clip(audio, -1.0, 1.0), diagnostics


def render_to_wav(config: TangleCubeOracleRenderConfig) -> dict[str, object]:
    rotating, diagnostics = render_tanglecube_oracle_audio(config, rotate_geometry=True)
    static, _ = render_tanglecube_oracle_audio(config, rotate_geometry=False)
    write_wav(config.output_path, rotating, config.sample_rate)
    write_wav(config.static_output_path, static, config.sample_rate)
    config.diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
    config.diagnostics_path.write_text(
        json.dumps({"config": {**asdict(config), "output_path": str(config.output_path),
                               "static_output_path": str(config.static_output_path),
                               "diagnostics_path": str(config.diagnostics_path),
                               "tangle_packet": str(config.tangle_packet)},
                    "diagnostics": diagnostics}, indent=2),
        encoding="utf-8",
    )
    return diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=TangleCubeOracleRenderConfig.output_path)
    parser.add_argument("--static-output", type=Path, default=TangleCubeOracleRenderConfig.static_output_path)
    parser.add_argument("--diagnostics", type=Path, default=TangleCubeOracleRenderConfig.diagnostics_path)
    parser.add_argument("--duration", type=float, default=TangleCubeOracleRenderConfig.duration_seconds)
    args = parser.parse_args()
    config = TangleCubeOracleRenderConfig(
        output_path=args.output,
        static_output_path=args.static_output,
        diagnostics_path=args.diagnostics,
        duration_seconds=args.duration,
    )
    diagnostics = render_to_wav(config)
    print("Quantum-memory Tangle Cube render complete")
    print(f"  rotating: {config.output_path.resolve()}")
    print(f"  static:   {config.static_output_path.resolve()}")
    print(f"  surface:  {diagnostics['vertex_count']} vertices, {diagnostics['mode_count']} modes")
    print("  phase steps (degrees): " + " -> ".join(f"{v:.2f}" for v in diagnostics["phase_degrees"]))
    print(f"  frequency ratios: {diagnostics['frequency_ratio_range'][0]:.3f} .. {diagnostics['frequency_ratio_range'][1]:.3f}")
    print(f"  ring modulation: {diagnostics['wet_ring_mod_rate_range_hz'][0]:.2f} .. {diagnostics['wet_ring_mod_rate_range_hz'][1]:.2f} Hz")
    print(f"  unique modal couplings: {diagnostics['unique_modal_couplings']}/8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
