"""Attach the Zeeman and fine-structure terms to a running DensityMatrixEngine.

The engine builds its Hamiltonian in its own units each tick.  The bridge adds
``scale * (H_fine + H_Z)`` on top, leaving the engine's fields, feedback and
noise untouched.  ``scale`` converts audible Hz into engine units; the default
2*pi assumes the engine integrates exp(-i H dt) with dt in seconds.

The engine's own X/Y fields do not conserve magnetisation, so inside the full
engine the polarisation labels from ``model.line_list`` become approximate:
use ``model.frame`` on the added terms alone for exact labels, or read the
engine's state for populations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .model import ZeemanFineConfig, PRESETS, hamiltonian


@dataclass
class ZeemanFineLayer:
    config: ZeemanFineConfig = field(default_factory=lambda: PRESETS["anomalous"])
    field_t: float = 0.0
    scale: float = 2.0 * np.pi
    enabled: bool = True

    def operator(self) -> np.ndarray:
        if not self.enabled:
            return np.zeros((16, 16), dtype=np.complex128)
        return self.scale * hamiltonian(self.config, self.field_t)

    # OSC-style setters, so a /zeeman/... namespace can drive the layer
    def set_field(self, field_t: float) -> None:
        self.field_t = float(field_t)

    def set_preset(self, key: str) -> None:
        self.config = PRESETS[key]

    def set_coupling(self, coupling_hz: float) -> None:
        self.config = ZeemanFineConfig(self.config.g, float(coupling_hz), self.config.hz_per_tesla)

    def set_g(self, qubit: int, value: float) -> None:
        g = list(self.config.g)
        g[int(qubit)] = float(value)
        self.config = ZeemanFineConfig(tuple(g), self.config.coupling_hz, self.config.hz_per_tesla)


def attach(engine, layer: ZeemanFineLayer) -> ZeemanFineLayer:
    """Wrap ``engine.hamiltonian`` so each tick includes the layer's terms.

    Returns the layer; call ``detach(engine)`` to restore the original.
    """
    if getattr(engine, "_zeeman_original_hamiltonian", None) is None:
        engine._zeeman_original_hamiltonian = engine.hamiltonian
    original = engine._zeeman_original_hamiltonian
    engine.hamiltonian = lambda: original() + layer.operator()
    engine.zeeman_layer = layer
    return layer


def detach(engine) -> None:
    original = getattr(engine, "_zeeman_original_hamiltonian", None)
    if original is not None:
        engine.hamiltonian = original
        engine._zeeman_original_hamiltonian = None
        engine.zeeman_layer = None
