"""Canonical quantum-observer layer for the integrated QMW instrument."""

from .diagnostics import HilbertDiagnostics, diagnose_hilbert_transport
from .hilbert_current import (
    CurrentEdge,
    continuity_residual,
    current_matrix,
    node_inflow,
    sparse_current_edges,
    von_neumann_population_rate,
)
from .observables import observable_derivative, pauli_expectation, pauli_expectations
from .pauli_basis import pauli_basis, pauli_labels, pauli_matrix, pauli_weight
from .pauli_decompose import PauliTerm, pauli_decomposition, reconstruct_pauli_sum
from .pauli_flow import PauliActivity, pauli_activities, rank_pauli_activity
from .dynamics import (
    Hamiltonian, LindbladChannel, PauliCoordinates, QuantumFrame,
    basis_current_inflow, conserved_pauli_labels, density_from_state,
    energy_expectation, energy_variance, lindblad_dissipator,
    pauli_coordinate_values, reconstruct_density_from_pauli,
    von_neumann_flow_i_frame, von_neumann_flow_i_hamiltonian,
    von_neumann_flow_i_initial_state,
)
from .engine import (
    AppliedControl, QuantumEngineState, QuantumFrameEngine, QuantumFramePublisher,
    evolve_lindblad_cptp,
)
from .control import (
    ChannelRateControl, ControlTransition, HamiltonianControl,
    ProjectiveMeasurementControl, RuntimeControl, UnitaryGateControl,
)
from .information import (
    LocalBlochVector, PairCorrelationTensor, QuantumInformationFrame,
    observe_quantum_information,
)
from .qho_configuration import (
    QHO_FOCK_BASIS, QHOConfigurationFrame, QHOConfigurationProjector,
)
from .adapters import (
    AdapterCapability, QuantumFrameAdapterConfig, QuantumFrameAdapterFrame,
    observe_quantum_frame_adapters,
)
from .nonabelian_path import (
    NonAbelianCommutatorFrame, OrderedPauliPathLedger, PauliPathOperation,
    observe_ordered_pauli_commutator,
)

__all__ = [
    "CurrentEdge", "HilbertDiagnostics", "PauliActivity", "PauliTerm",
    "continuity_residual", "current_matrix", "diagnose_hilbert_transport",
    "node_inflow", "observable_derivative", "pauli_activities", "pauli_basis",
    "pauli_decomposition", "pauli_expectation", "pauli_expectations",
    "pauli_labels", "pauli_matrix", "pauli_weight", "rank_pauli_activity",
    "reconstruct_pauli_sum", "sparse_current_edges",
    "NonAbelianCommutatorFrame", "OrderedPauliPathLedger", "PauliPathOperation",
    "observe_ordered_pauli_commutator",
    "von_neumann_population_rate",
    "Hamiltonian", "LindbladChannel", "PauliCoordinates", "QuantumFrame",
    "basis_current_inflow", "conserved_pauli_labels", "density_from_state",
    "energy_expectation", "energy_variance", "lindblad_dissipator",
    "pauli_coordinate_values", "reconstruct_density_from_pauli",
    "von_neumann_flow_i_frame", "von_neumann_flow_i_hamiltonian",
    "von_neumann_flow_i_initial_state",
    "AppliedControl", "QuantumEngineState", "QuantumFrameEngine", "QuantumFramePublisher",
    "evolve_lindblad_cptp",
    "ChannelRateControl", "ControlTransition", "HamiltonianControl",
    "ProjectiveMeasurementControl", "RuntimeControl", "UnitaryGateControl",
    "LocalBlochVector", "PairCorrelationTensor", "QuantumInformationFrame",
    "observe_quantum_information",
    "QHO_FOCK_BASIS", "QHOConfigurationFrame", "QHOConfigurationProjector",
    "AdapterCapability", "QuantumFrameAdapterConfig", "QuantumFrameAdapterFrame",
    "observe_quantum_frame_adapters",
]
