"""Explicit musical transformation of a raw Hubbard descriptor."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import numpy as np


def musical_descriptor(raw_descriptor: dict[str, Any]) -> dict[str, Any]:
    """Add bounded performance controls without replacing the raw route."""
    descriptor = deepcopy(raw_descriptor)
    raw = descriptor["raw"]
    config = descriptor["config"]
    sites = int(config["num_sites"])
    hopping = max(float(config["hopping"]), 1e-12)
    gaps = np.asarray(raw["gaps_from_ground"], dtype=float)

    descriptor["schema"] = "qmw.hubbard.raw_and_musical.v1"
    gap_frequency_ratios = 1.0 + gaps / hopping
    descriptor["musical"] = {
        "voice_amplitudes": np.clip(np.asarray(raw["site_occupations"]) / 2.0, 0.0, 1.0).tolist(),
        "voice_pan": np.linspace(-0.75, 0.75, sites).tolist(),
        "timbre_polarity": np.clip(raw["site_spin_polarizations"], -1.0, 1.0).tolist(),
        "roughness": np.clip(raw["site_double_occupancies"], 0.0, 1.0).tolist(),
        "bond_activity": np.tanh(np.abs(raw["bond_coherences"])).tolist(),
        "gap_frequency_ratios": gap_frequency_ratios.tolist(),
        "gap_log2_ratios": np.log2(gap_frequency_ratios).tolist(),
    }
    descriptor["mapping_contract"] = {
        "voice_amplitudes": "site_occupations / 2",
        "voice_pan": "fixed spatial identity of each lattice site",
        "timbre_polarity": "site spin polarization clipped to [-1, 1]",
        "roughness": "site double occupancy",
        "bond_activity": "tanh(abs(bond coherence))",
        "gap_frequency_ratios": "1 + excitation_gap/t; continuous and unquantized",
        "gap_log2_ratios": "log2(gap frequency ratio); continuous octave coordinate",
    }
    return descriptor
