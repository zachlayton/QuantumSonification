"""Atomic JSON/OSC serialization for complete observer/body frames."""

from __future__ import annotations

from typing import Any

from .frames import OneQubitObservationFrame, ResonantBodyFrame


SCHEMA = "qmw.one_qubit_resonant_body.v1"
FRAME_ADDRESS = "/qmw/one_qubit/v1/frame"


def frame_payload(
    observation: OneQubitObservationFrame,
    body: ResonantBodyFrame,
    *,
    running: bool,
    measurement: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if observation.revision != body.observation_revision:
        raise ValueError("observation/body revisions must match")
    x, y, z = (float(value) for value in observation.bloch_xyz)
    ox, oy, oz = (float(value) for value in observation.omega_rad_per_second)
    return {
        "schema": SCHEMA,
        "revision": body.revision,
        "quantum_revision": observation.quantum_revision,
        "time": observation.time,
        "running": bool(running),
        "physics": {
            "bloch": [x, y, z],
            "omega_rad_per_second": [ox, oy, oz],
            "energy_gap_over_hbar_rad_per_second": (
                observation.energy_gap_over_hbar_rad_per_second
            ),
            "t1_seconds": observation.t1_seconds,
            "tphi_seconds": observation.tphi_seconds,
        },
        "observables": {
            "radius": observation.radius,
            "population_0": observation.population_0,
            "population_1": observation.population_1,
            "coherence_l1": observation.coherence_l1,
            "purity": observation.purity,
            "entropy_nats": observation.entropy_nats,
        },
        "sound_adapter": {
            "sound_locked": body.controls.sound_locked,
            "master": body.controls.master,
            "probe_rate_hz": body.controls.probe_rate_hz,
            "probe_brightness": body.controls.probe_brightness,
            "body_detail": body.controls.body_detail,
            "base_frequency_hz": body.controls.base_frequency_hz,
            "base_decay_seconds": body.controls.base_decay_seconds,
            "decay_tilt": body.controls.decay_tilt,
            "mapping_label": body.mapping_label,
            "modes": [
                {
                    "label": label,
                    "frequency_hz": float(frequency),
                    "decay_seconds": float(decay),
                    "signed_weight": float(weight),
                }
                for label, frequency, decay, weight in zip(
                    body.mode_labels,
                    body.frequencies_hz,
                    body.decay_seconds,
                    body.signed_weights,
                )
            ],
        },
        "last_measurement": measurement,
    }


def osc_arguments(
    observation: OneQubitObservationFrame, body: ResonantBodyFrame
) -> list[float | int]:
    """Return one all-or-nothing OSC frame consumed by the SC body."""

    if observation.revision != body.observation_revision:
        raise ValueError("observation/body revisions must match")
    values: list[float | int] = [
        body.revision,
        observation.time,
        *[float(value) for value in observation.bloch_xyz],
        observation.radius,
        observation.population_0,
        observation.population_1,
        observation.purity,
        observation.coherence_l1,
        observation.entropy_nats,
        *[float(value) for value in observation.omega_rad_per_second],
        observation.energy_gap_over_hbar_rad_per_second,
        int(body.controls.sound_locked),
        body.controls.master,
        body.controls.probe_rate_hz,
        body.controls.probe_brightness,
        body.controls.base_decay_seconds,
    ]
    for frequency, decay, weight in zip(
        body.frequencies_hz, body.decay_seconds, body.signed_weights
    ):
        values.extend((float(frequency), float(decay), float(weight)))
    return values
