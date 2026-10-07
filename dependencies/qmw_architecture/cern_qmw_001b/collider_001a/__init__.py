"""CERN/QMW 001A: event kinematics and phase-space navigation only."""

from .model import ColliderDataset, ColliderEvent, FourMomentum, Provenance, invariant_mass
from .backend import ColliderBackend, PhaseSpaceFrame
from .io import JsonEventLoader, load_dataset, save_dataset
from .synthetic import generate_synthetic

__version__ = "0.1.0"
__all__ = [
    "ColliderDataset", "ColliderEvent", "FourMomentum", "Provenance",
    "invariant_mass", "ColliderBackend", "PhaseSpaceFrame", "JsonEventLoader",
    "load_dataset", "save_dataset", "generate_synthetic",
]
