"""Explicit downstream mapping from GPE energy density to material controls.

The returned values are renderer controls, not changes to the GPE Hamiltonian,
transport, or density-matrix preparation.  Component shares use absolute
integrated energy so that an attractive interaction or negative external
potential remains observable without cancelling the material descriptor.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from qmw.gpe.field_frame import FieldFrame


@dataclass(frozen=True)
class EnergyMaterialConfig:
    """Declared renderer calibration for energy-derived material controls."""

    reference_energy_density: float = 1.0

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.reference_energy_density)) or self.reference_energy_density <= 0.0:
            raise ValueError("reference_energy_density must be finite and greater than zero.")


@dataclass(frozen=True)
class GPEEnergyMaterialControls:
    """Energy-derived material drivers, all downstream of physical evolution."""

    time: float
    total_energy: float
    energy_density_rms: float
    material_drive: float
    excitation_strength: float
    saturation_drive: float
    transducer_force: float
    brightness_drive: float
    decay_drive: float
    physical_model_tension: float
    gradient_share: float
    potential_share: float
    interaction_share: float


def energy_to_material(
    frame: FieldFrame,
    *,
    config: EnergyMaterialConfig | None = None,
) -> GPEEnergyMaterialControls:
    """Derive bounded material controls from one synchronized energy field."""

    settings = config or EnergyMaterialConfig()
    rms = float(np.sqrt(np.mean(np.square(frame.energy_density))))
    drive = float(np.clip(rms / settings.reference_energy_density, 0.0, 1.0))
    components = np.asarray((
        abs(float(np.sum(frame.gradient_energy))),
        abs(float(np.sum(frame.potential_energy))),
        abs(float(np.sum(frame.interaction_energy))),
    ))
    shares = components / max(float(np.sum(components)), 1.0e-12)
    return GPEEnergyMaterialControls(
        time=frame.time, total_energy=frame.total_energy, energy_density_rms=rms,
        material_drive=drive, excitation_strength=drive,
        saturation_drive=drive * float(shares[2]), transducer_force=drive,
        brightness_drive=drive * float(shares[0]), decay_drive=drive,
        physical_model_tension=drive * float(shares[1]),
        gradient_share=float(shares[0]), potential_share=float(shares[1]),
        interaction_share=float(shares[2]),
    )


__all__ = ["EnergyMaterialConfig", "GPEEnergyMaterialControls", "energy_to_material"]
