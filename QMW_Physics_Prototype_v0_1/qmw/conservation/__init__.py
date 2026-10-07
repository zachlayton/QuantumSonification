"""Invariant and continuity diagnostics; this package never repairs a state."""
from .monitor import ConservationMonitor
from .specs import module_specs

__all__ = ["ConservationMonitor", "module_specs"]
