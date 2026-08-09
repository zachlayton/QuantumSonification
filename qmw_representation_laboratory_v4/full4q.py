"""Compatibility export for the canonical protocols/full_pauli.py module."""

from .adapters import FULL4Q_DIMENSION, Full4QSynthesisAdapter
from .protocols import FullPauliTomography

__all__ = [
    "FULL4Q_DIMENSION",
    "Full4QSynthesisAdapter",
    "FullPauliTomography",
]
