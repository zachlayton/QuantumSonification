"""Solver-facing GPE API.

This is the stable solver seam.  The compatibility module ``qmw.qmw_gpe``
continues to expose the same implementation for existing callers.
"""

from ..qmw_gpe import GPEConfig, GPEEngine, GPEState

__all__ = ["GPEConfig", "GPEEngine", "GPEState"]
