"""QMW V3 finite-lattice quantum field theory public API."""

from .backends import (
    ExactTruncatedScalarFieldBackend,
    GaussianScalarFieldBackend,
    exact_product_coherent,
    exact_product_vacuum,
    exact_single_particle_wavepacket,
)
from .gaussian import (
    GaussianFieldState,
    bogoliubov_coefficients,
    coherent_mode_state,
    evolve_gaussian,
    localized_displacement_state,
    squeezed_mode_state,
    symplectic_evolution,
    thermal_state,
    vacuum_state,
)
from .model import ScalarFieldModel, ScalarFieldSpec
from .impulse_response import (
    QuantumFieldIRArtifact,
    QuantumFieldIRSpec,
    render_quantum_field_ir,
    write_quantum_field_ir,
)
from .gaussian_temporal import (
    GaussianClockReading,
    GaussianFieldTemporalEngine,
    GaussianFieldTemporalFrame,
    GaussianGeodesicReading,
    GaussianSiteClockReading,
    single_mode_bures_angle,
    single_mode_gaussian_fidelity,
)
from .observables import frame_from_gaussian, gaussian_purity
from .performance import FieldPerformanceRecorder, PerformanceEvent
from .schema import ScalarFieldFrame
from .sonification import (
    GaussianHarmonicDescriptor,
    gaussian_harmonic_descriptor,
    gaussian_pitch_deviation_control,
)
from .validation import ScalarFieldValidationReport, validate_exact_against_gaussian

__all__ = [name for name in globals() if not name.startswith("_")]
