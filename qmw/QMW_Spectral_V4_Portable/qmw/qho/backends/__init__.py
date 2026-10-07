"""Execution adapters for the canonical QHO model."""

from .base import OscillatorBackend
from .numpy_bosonic import NumPyBosonicBackend
from .numpy_coupled import NumPyCoupledOscillatorBackend

__all__ = [
    "NumPyBosonicBackend",
    "NumPyCoupledOscillatorBackend",
    "OscillatorBackend",
]
