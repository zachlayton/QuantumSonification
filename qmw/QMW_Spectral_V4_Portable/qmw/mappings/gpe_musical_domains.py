"""Keep GPE flow, modes, and energy as separate musical-domain controls."""

from __future__ import annotations

from dataclasses import dataclass

from qmw.gpe.field_frame import FieldFrame

from .energy_to_material import EnergyMaterialConfig, GPEEnergyMaterialControls, energy_to_material
from .flow_to_sound import GPEFlowSoundControls, flow_to_sound
from .modes_to_sound import GPEModeSoundControls, modes_to_sound


@dataclass(frozen=True)
class GPEMusicalDomains:
    """Three non-interchangeable renderer domains from one FieldFrame."""

    time: float
    flow_time: GPEFlowSoundControls
    modes_spectrum: GPEModeSoundControls
    energy_materiality: GPEEnergyMaterialControls
    provenance: str = "separate_flow_mode_energy_gpe_sonification_domains"


def map_gpe_musical_domains(
    frame: FieldFrame,
    *,
    energy_config: EnergyMaterialConfig | None = None,
) -> GPEMusicalDomains:
    """Map one physical frame without blending flow, mode, and energy meaning."""

    flow = flow_to_sound(frame)
    modes = modes_to_sound(frame)
    material = energy_to_material(frame, config=energy_config)
    if flow.time != frame.time or modes.time != frame.time or material.time != frame.time:
        raise RuntimeError("GPE musical-domain mapping lost FieldFrame time alignment.")
    return GPEMusicalDomains(
        time=frame.time, flow_time=flow, modes_spectrum=modes, energy_materiality=material,
    )


__all__ = ["GPEMusicalDomains", "map_gpe_musical_domains"]
