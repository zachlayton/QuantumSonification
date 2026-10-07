"""Explicit quadrature-aware spatial, basis and graph projections."""
from .regions import RegionProjector
from .modal import ModalProjector
from .graph import GraphModes, GraphModalProjector
from .specs import MODULE_SPECS

__all__ = ["RegionProjector", "ModalProjector", "GraphModes", "GraphModalProjector", "MODULE_SPECS"]
