"""Read-only observations of physical state, without sound mappings."""
from .schrodinger import schrodinger_observables
from .scalar import scalar_observables
from .specs import module_specs

__all__ = ["schrodinger_observables", "scalar_observables", "module_specs"]
