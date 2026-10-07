"""Read-only physical observations and perceptual resonant-body mapping."""

from __future__ import annotations

import math

import numpy as np

from .frames import (
    MODE_LABELS,
    OneQubitObservationFrame,
    OneQubitQuantumFrame,
    ResonantBodyFrame,
    SoundAdapterControls,
)
from .physics import PAULI


# Fixed, declared acoustic design constants. They are not energy levels.
BODY_FREQUENCY_RATIOS = np.asarray(
    (1.000, 1.347, 1.521, 1.803, 2.117, 2.431, 2.781, 3.168, 3.599),
    dtype=float,
)


def observe_one_qubit(frame: OneQubitQuantumFrame) -> OneQubitObservationFrame:
    if not isinstance(frame, OneQubitQuantumFrame):
        raise TypeError("frame must be an authoritative OneQubitQuantumFrame")
    bloch = np.asarray(
        [float(np.trace(frame.rho @ pauli).real) for pauli in PAULI], dtype=float
    )
    radius = float(min(1.0, np.linalg.norm(bloch)))
    populations = np.clip(np.real(np.diag(frame.rho)), 0.0, 1.0)
    eigenvalues = np.clip(np.linalg.eigvalsh(frame.rho), 0.0, 1.0)
    nonzero = eigenvalues[eigenvalues > 1e-15]
    entropy = float(-np.sum(nonzero * np.log(nonzero)))
    return OneQubitObservationFrame(
        revision=frame.revision,
        time=frame.time,
        quantum_revision=frame.revision,
        bloch_xyz=bloch,
        radius=radius,
        population_0=float(populations[0]),
        population_1=float(populations[1]),
        coherence_l1=float(2.0 * abs(frame.rho[0, 1])),
        purity=float(np.trace(frame.rho @ frame.rho).real),
        entropy_nats=entropy,
        energy_gap_over_hbar_rad_per_second=float(
            np.linalg.norm(frame.omega_rad_per_second)
        ),
        omega_rad_per_second=frame.omega_rad_per_second,
        t1_seconds=frame.t1_seconds,
        tphi_seconds=frame.tphi_seconds,
    )


def signed_body_weights(
    observation: OneQubitObservationFrame, *, body_detail: float
) -> np.ndarray:
    """Return unit-energy monopole/dipole/quadrupole excitation weights."""

    beta = float(body_detail)
    if not 0.0 <= beta <= 1.0:
        raise ValueError("body_detail must lie in [0, 1]")
    radius = float(np.clip(observation.radius, 0.0, 1.0))
    weights = np.zeros(9, dtype=float)
    weights[0] = math.sqrt(max(0.0, 1.0 - radius * radius))
    if radius > 1e-12:
        x, y, z = observation.bloch_xyz / radius
        dipole = np.asarray((x, y, z), dtype=float)
        quadrupole = np.asarray(
            (
                math.sqrt(3.0) * x * y,
                math.sqrt(3.0) * y * z,
                math.sqrt(3.0) * z * x,
                (math.sqrt(3.0) / 2.0) * (x * x - y * y),
                0.5 * (3.0 * z * z - 1.0),
            ),
            dtype=float,
        )
        # Addition-theorem normalization: each directional group has norm one.
        dipole /= max(float(np.linalg.norm(dipole)), 1e-15)
        quadrupole /= max(float(np.linalg.norm(quadrupole)), 1e-15)
        weights[1:4] = radius * math.sqrt(1.0 - beta) * dipole
        weights[4:9] = radius * math.sqrt(beta) * quadrupole
    weights /= max(float(np.linalg.norm(weights)), 1e-15)
    weights.flags.writeable = False
    return weights


def resonant_body_frame(
    observation: OneQubitObservationFrame,
    controls: SoundAdapterControls | None = None,
    *,
    revision: int | None = None,
) -> ResonantBodyFrame:
    if not isinstance(observation, OneQubitObservationFrame):
        raise TypeError("observation must be a OneQubitObservationFrame")
    selected = (controls or SoundAdapterControls()).validated()
    frequencies = selected.base_frequency_hz * BODY_FREQUENCY_RATIOS
    decays = selected.base_decay_seconds * BODY_FREQUENCY_RATIOS ** (-selected.decay_tilt)
    return ResonantBodyFrame(
        revision=observation.revision if revision is None else revision,
        time=observation.time,
        observation_revision=observation.revision,
        mode_labels=MODE_LABELS,
        frequencies_hz=frequencies,
        decay_seconds=decays,
        signed_weights=signed_body_weights(
            observation, body_detail=selected.body_detail
        ),
        controls=selected,
    )
