"""Compatibility wrapper for the first oscilloscope module name."""

from quantum_oscilloscope.frame_builder import frame_from_engine_snapshot
from quantum_oscilloscope.scope_engine import (
    QuantumOscilloscope,
    QuantumOscilloscopeConfig,
)

__all__ = [
    "QuantumOscilloscope",
    "QuantumOscilloscopeConfig",
    "frame_from_engine_snapshot",
]

