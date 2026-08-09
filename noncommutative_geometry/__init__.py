"""Public package interface for noncommutative geometry experiments.

The public objects are loaded lazily so the pipeline can also be executed with
``python -m noncommutative_geometry.noncommutative_geometry_pipeline_v1``
without importing the target module twice.
"""

from importlib import import_module
from typing import Any

__all__ = [
    "OperatorOrderConfig",
    "apply_operator",
    "deformation_generators",
    "experiment_operators",
    "reserve_output_fork",
]


def __getattr__(name: str) -> Any:
    """Load public pipeline objects on first access."""
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(".noncommutative_geometry_pipeline_v1", __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
