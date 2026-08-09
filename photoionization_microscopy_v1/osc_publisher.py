"""Dedicated OSC publication contract for photoionization microscopy."""

from __future__ import annotations

from typing import Any

from .model import PhotoionizationMicroscopySource


class PhotoionizationOSCPublisher:
    def __init__(self, client: Any, namespace: str = "/qmw/photoionization") -> None:
        self.client = client
        self.namespace = namespace.rstrip("/")

    def publish(self, source: PhotoionizationMicroscopySource) -> None:
        state = source.state
        prefix = self.namespace
        self.client.send_message(
            f"{prefix}/config",
            [
                state.electric_field_v_per_cm,
                state.magnetic_field_t,
                source.config.m,
                source.config.detector_z_au,
                source.config.propagation_time_ps,
            ],
        )
        self.client.send_message(
            f"{prefix}/resonance",
            [state.resonance_label, state.resonance_energy_cm_inverse],
        )
        self.client.send_message(
            f"{prefix}/detector/rho_um",
            [float(value) for value in state.rho_um],
        )
        self.client.send_message(
            f"{prefix}/detector/radial_flux",
            [float(value) for value in state.detector_flux],
        )
        peaks = []
        for rho, weight in zip(state.peak_rho_um, state.peak_weights):
            peaks.extend((float(rho), float(weight)))
        self.client.send_message(f"{prefix}/detector/peaks", peaks)
        self.client.send_message(
            f"{prefix}/detector/fringe_minima",
            [float(value) for value in state.fringe_minima_rho_um],
        )
        self.client.send_message(
            f"{prefix}/detector/lanes",
            [float(value) for value in state.detector_lanes],
        )
        self.client.send_message(
            f"{prefix}/observables",
            [state.radial_mean_um, state.radial_rms_um, state.radial_extent_um],
        )
        self.client.send_message(f"{prefix}/reference_status", state.reference_status)
