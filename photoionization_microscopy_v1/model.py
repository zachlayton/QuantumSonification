"""Paper-reference magnetic focusing model for hydrogen microscopy."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from excitation.base import QuantumSource
from excitation.descriptor import QuantumDescriptor

from .reference_data import (
    REFERENCE_ENERGY_CM_INVERSE,
    REFERENCE_FIELDS_T,
    REFERENCE_PROFILES,
    REFERENCE_RHO_UM,
    REFERENCE_STATUS,
)


@dataclass(frozen=True)
class PhotoionizationConfig:
    electric_field_v_per_cm: float = 808.0
    magnetic_field_t: float = 0.0
    m: int = 0
    resonance_label: str = "(1,28,0)"
    detector_z_au: float = -8000.0
    propagation_time_ps: float = 500.0
    sweep_rate_t_per_second: float = 0.0
    loop_sweep: bool = True
    lane_count: int = 8

    def __post_init__(self) -> None:
        if not 0.0 <= self.magnetic_field_t <= 8.0:
            raise ValueError("paper_reference magnetic_field_t must be in [0, 8]")
        if self.electric_field_v_per_cm <= 0.0:
            raise ValueError("electric_field_v_per_cm must be positive")
        if self.propagation_time_ps <= 0.0:
            raise ValueError("propagation_time_ps must be positive")
        if self.sweep_rate_t_per_second < 0.0:
            raise ValueError("sweep_rate_t_per_second must be non-negative")
        if self.lane_count < 1:
            raise ValueError("lane_count must be positive")
        reference_conditions = (
            math.isclose(self.electric_field_v_per_cm, 808.0),
            self.m == 0,
            self.resonance_label == "(1,28,0)",
            math.isclose(self.detector_z_au, -8000.0),
            math.isclose(self.propagation_time_ps, 500.0),
        )
        if not all(reference_conditions):
            raise ValueError(
                "paper_reference supports only Figure 5 conditions: "
                "F=808 V/cm, m=0, resonance=(1,28,0), detector_z=-8000 a.u., "
                "and propagation_time=500 ps"
            )


@dataclass(frozen=True)
class PhotoionizationState:
    time_seconds: float
    magnetic_field_t: float
    electric_field_v_per_cm: float
    resonance_label: str
    resonance_energy_cm_inverse: float
    rho_um: np.ndarray
    detector_flux: np.ndarray
    peak_rho_um: np.ndarray
    peak_weights: np.ndarray
    fringe_minima_rho_um: np.ndarray
    radial_mean_um: float
    radial_rms_um: float
    radial_extent_um: float
    detector_lanes: np.ndarray
    reference_status: str


def interpolate_reference_profile(field_t: float) -> np.ndarray:
    if not 0.0 <= field_t <= 8.0:
        raise ValueError("paper_reference magnetic field must be in [0, 8] T")
    upper_index = int(np.searchsorted(REFERENCE_FIELDS_T, field_t, side="right"))
    if upper_index == 0:
        return REFERENCE_PROFILES[0.0].copy()
    if upper_index >= len(REFERENCE_FIELDS_T):
        return REFERENCE_PROFILES[8.0].copy()
    lower = float(REFERENCE_FIELDS_T[upper_index - 1])
    upper = float(REFERENCE_FIELDS_T[upper_index])
    fraction = (field_t - lower) / (upper - lower)
    profile = (1.0 - fraction) * REFERENCE_PROFILES[lower] + fraction * REFERENCE_PROFILES[upper]
    maximum = float(np.max(profile))
    return profile / maximum if maximum > 0.0 else profile


def detector_peaks(
    rho_um: np.ndarray,
    flux: np.ndarray,
    threshold: float = 0.12,
    min_distance_samples: int = 6,
) -> tuple[np.ndarray, np.ndarray]:
    if rho_um.shape != flux.shape or flux.ndim != 1:
        raise ValueError("rho_um and flux must be matching one-dimensional arrays")
    smooth = np.convolve(flux, np.ones(5, dtype=float) / 5.0, mode="same")
    candidates = []
    for index in range(2, len(smooth) - 2):
        local = smooth[index - 2 : index + 3]
        if smooth[index] >= threshold and smooth[index] == float(np.max(local)):
            candidates.append(index)
    selected: list[int] = []
    for index in sorted(candidates, key=lambda item: float(smooth[item]), reverse=True):
        if all(abs(index - other) >= min_distance_samples for other in selected):
            selected.append(index)
    selected.sort()
    indices = np.asarray(selected, dtype=int)
    return rho_um[indices].copy(), flux[indices].copy()


def fringe_minima(
    rho_um: np.ndarray,
    flux: np.ndarray,
    peak_rho_um: np.ndarray,
) -> np.ndarray:
    minima = []
    peak_indices = [int(np.argmin(np.abs(rho_um - peak))) for peak in peak_rho_um]
    for left, right in zip(peak_indices, peak_indices[1:]):
        if right - left > 1:
            index = left + int(np.argmin(flux[left : right + 1]))
            minima.append(float(rho_um[index]))
    return np.asarray(minima, dtype=float)


def detector_lanes(
    rho_um: np.ndarray,
    flux: np.ndarray,
    lane_count: int = 8,
) -> np.ndarray:
    edges = np.linspace(float(rho_um[0]), float(rho_um[-1]), lane_count + 1)
    lanes = np.zeros(lane_count, dtype=float)
    for index, (left, right) in enumerate(zip(edges[:-1], edges[1:])):
        mask = (rho_um >= left) & (rho_um <= right)
        if np.count_nonzero(mask) >= 2:
            lanes[index] = float(np.trapezoid(flux[mask], rho_um[mask]))
    total = float(np.sum(lanes))
    return lanes / total if total > 0.0 else lanes


class PhotoionizationMicroscopySource(QuantumSource):
    """Continuous morph through digitized Figure 5 detector distributions.

    This source is a paper-reference data instrument. It does not evolve a
    wavefunction and must not be described as a TDSE solver.
    """

    def __init__(self, config: PhotoionizationConfig | None = None) -> None:
        self.config = config or PhotoionizationConfig()
        self.time_seconds = 0.0
        self._field_t = float(self.config.magnetic_field_t)
        self._state = self._compute_state()
        self._descriptor = self._compute_descriptor(self._state)

    def set_magnetic_field(self, field_t: float) -> None:
        if not 0.0 <= field_t <= 8.0:
            raise ValueError("paper_reference magnetic field must be in [0, 8] T")
        self._field_t = float(field_t)
        self._refresh()

    def _refresh(self) -> None:
        self._state = self._compute_state()
        self._descriptor = self._compute_descriptor(self._state)

    def _compute_state(self) -> PhotoionizationState:
        rho = REFERENCE_RHO_UM.copy()
        flux = interpolate_reference_profile(self._field_t)
        peak_rho, peak_weights = detector_peaks(rho, flux)
        area = float(np.trapezoid(flux, rho))
        radial_mean = float(np.trapezoid(rho * flux, rho) / area)
        radial_rms = math.sqrt(float(np.trapezoid((rho**2) * flux, rho) / area))
        active = np.flatnonzero(flux >= 0.02 * float(np.max(flux)))
        radial_extent = float(rho[active[-1]]) if active.size else 0.0
        energy = float(
            np.interp(
                self._field_t,
                REFERENCE_FIELDS_T,
                REFERENCE_ENERGY_CM_INVERSE,
            )
        )
        return PhotoionizationState(
            time_seconds=self.time_seconds,
            magnetic_field_t=self._field_t,
            electric_field_v_per_cm=self.config.electric_field_v_per_cm,
            resonance_label=self.config.resonance_label,
            resonance_energy_cm_inverse=energy,
            rho_um=rho,
            detector_flux=flux,
            peak_rho_um=peak_rho,
            peak_weights=peak_weights,
            fringe_minima_rho_um=fringe_minima(rho, flux, peak_rho),
            radial_mean_um=radial_mean,
            radial_rms_um=radial_rms,
            radial_extent_um=radial_extent,
            detector_lanes=detector_lanes(rho, flux, self.config.lane_count),
            reference_status=REFERENCE_STATUS,
        )

    @staticmethod
    def _compute_descriptor(state: PhotoionizationState) -> QuantumDescriptor:
        energy = (state.resonance_energy_cm_inverse + 169.617) / (169.617 - 164.020)
        concentration = float(np.max(state.detector_lanes))
        roughness = float(np.mean(np.abs(np.diff(state.detector_flux))))
        return QuantumDescriptor(
            energy=float(np.clip(energy, 0.0, 1.0)),
            phase=float(state.magnetic_field_t / 8.0),
            probability=float(np.clip(concentration, 0.0, 1.0)),
            coherence=float(np.clip(1.0 - state.radial_rms_um / 0.15, 0.0, 1.0)),
            entanglement=0.0,
            spin=0.5,
            topology=float(np.clip(len(state.peak_rho_um) / 4.0, 0.0, 1.0)),
            curvature=float(np.clip(roughness * 8.0, 0.0, 1.0)),
        )

    def step(self, dt: float) -> None:
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        self.time_seconds += float(dt)
        if dt > 0.0 and self.config.sweep_rate_t_per_second > 0.0:
            next_field = self._field_t + self.config.sweep_rate_t_per_second * dt
            if self.config.loop_sweep:
                next_field %= 8.0
            else:
                next_field = min(next_field, 8.0)
            self._field_t = float(next_field)
        self._refresh()

    @property
    def descriptor(self) -> QuantumDescriptor:
        return self._descriptor

    @property
    def state(self) -> PhotoionizationState:
        return self._state

    def arrays(self) -> dict[str, np.ndarray]:
        return {
            "photoionization_rho_um": self.state.rho_um.copy(),
            "photoionization_detector_flux": self.state.detector_flux.copy(),
            "photoionization_detector_lanes": self.state.detector_lanes.copy(),
            "photoionization_peak_rho_um": self.state.peak_rho_um.copy(),
            "photoionization_peak_weights": self.state.peak_weights.copy(),
        }

    def observables(self) -> dict[str, float | str]:
        return {
            "photoionization_magnetic_field_t": self.state.magnetic_field_t,
            "photoionization_resonance_energy_cm_inverse": self.state.resonance_energy_cm_inverse,
            "photoionization_radial_mean_um": self.state.radial_mean_um,
            "photoionization_radial_rms_um": self.state.radial_rms_um,
            "photoionization_radial_extent_um": self.state.radial_extent_um,
            "photoionization_reference_status": self.state.reference_status,
        }
