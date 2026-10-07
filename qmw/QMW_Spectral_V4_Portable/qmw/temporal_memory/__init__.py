"""Read-only harmonic temporal-memory controls for QMW sound adapters.

The package observes a density frame and optional basis-indexed current.  It
does not evolve, measure, normalize, or otherwise write back to ``rho``.
"""

from .engine import (
    TemporalMemoryConfig,
    TemporalMemoryFrame,
    harmonic_weights,
    observe_quantum_frame_temporal_memory,
    observe_temporal_memory,
)
from .osc import (
    QMW_TEMPORAL_MEMORY_OSC_PORT,
    QMW_TEMPORAL_MEMORY_OSC_ROOT,
    QMW_TEMPORAL_MEMORY_OSC_SCHEMA,
    TemporalMemoryOSCPublisher,
)
from .control import (
    MAX_BASE_DELAY_SECONDS,
    MAX_FEEDBACK_AMOUNT,
    MAX_PHASE_WARP,
    MIN_BASE_DELAY_SECONDS,
    QMW_TEMPORAL_MEMORY_BASE_DELAY_ADDRESS,
    QMW_TEMPORAL_MEMORY_DIFFUSION_ADDRESS,
    QMW_TEMPORAL_MEMORY_FEEDBACK_AMOUNT_ADDRESS,
    QMW_TEMPORAL_MEMORY_CONTROL_PORT,
    QMW_TEMPORAL_MEMORY_CONTROL_ROOT,
    QMW_TEMPORAL_MEMORY_PHASE_WARP_ADDRESS,
    QMW_TEMPORAL_MEMORY_RATIO_PRESET_ADDRESS,
    RATIO_PRESETS,
    TemporalMemoryControl,
    TemporalMemoryOSCControl,
)
from .interference import (
    DEFAULT_HMI_BASE_DELAY_SECONDS,
    DEFAULT_HMI_RATIOS,
    HarmonicMemoryInterferenceSpec,
)
from .development import (
    HarmonicMemoryClock,
    HarmonicMemoryDevelopmentFrame,
    HarmonicMemoryEventObserver,
    HarmonicMemorySeries,
    harmonic_memory_series,
    observe_harmonic_memory_development,
)
from .development_osc import (
    HarmonicMemoryDevelopmentOSCPublisher,
    QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_PORT,
    QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_ROOT,
    QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_SCHEMA,
)

__all__ = [
    "QMW_TEMPORAL_MEMORY_OSC_PORT",
    "QMW_TEMPORAL_MEMORY_OSC_ROOT",
    "QMW_TEMPORAL_MEMORY_OSC_SCHEMA",
    "MAX_BASE_DELAY_SECONDS",
    "MAX_FEEDBACK_AMOUNT",
    "MAX_PHASE_WARP",
    "MIN_BASE_DELAY_SECONDS",
    "QMW_TEMPORAL_MEMORY_BASE_DELAY_ADDRESS",
    "QMW_TEMPORAL_MEMORY_DIFFUSION_ADDRESS",
    "QMW_TEMPORAL_MEMORY_FEEDBACK_AMOUNT_ADDRESS",
    "QMW_TEMPORAL_MEMORY_CONTROL_PORT",
    "QMW_TEMPORAL_MEMORY_CONTROL_ROOT",
    "QMW_TEMPORAL_MEMORY_PHASE_WARP_ADDRESS",
    "QMW_TEMPORAL_MEMORY_RATIO_PRESET_ADDRESS",
    "RATIO_PRESETS",
    "TemporalMemoryConfig",
    "TemporalMemoryControl",
    "TemporalMemoryFrame",
    "TemporalMemoryOSCControl",
    "DEFAULT_HMI_BASE_DELAY_SECONDS",
    "DEFAULT_HMI_RATIOS",
    "HarmonicMemoryInterferenceSpec",
    "HarmonicMemoryClock",
    "HarmonicMemoryDevelopmentFrame",
    "HarmonicMemoryDevelopmentOSCPublisher",
    "HarmonicMemoryEventObserver",
    "HarmonicMemorySeries",
    "QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_PORT",
    "QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_ROOT",
    "QMW_HARMONIC_MEMORY_DEVELOPMENT_OSC_SCHEMA",
    "TemporalMemoryOSCPublisher",
    "harmonic_weights",
    "harmonic_memory_series",
    "observe_harmonic_memory_development",
    "observe_quantum_frame_temporal_memory",
    "observe_temporal_memory",
]
