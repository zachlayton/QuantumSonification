"""Integrated Max interface for the stable v4 representation engine."""

VERSION = 5

from .osc_service import (
    RepresentationLiveConfig,
    RepresentationTransformFactory,
    RepresentationV5OSCService,
)

__all__ = [
    "RepresentationLiveConfig",
    "RepresentationTransformFactory",
    "RepresentationV5OSCService",
    "VERSION",
]
