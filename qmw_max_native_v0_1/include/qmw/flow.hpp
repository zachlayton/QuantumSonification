#pragma once

#include "qmw/hamiltonian.hpp"
#include "qmw/state.hpp"

#include <cstddef>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace qmw {

enum class FlowCode {
    invalid_policy,
    invalid_dimension,
    wrong_element_count,
    non_finite,
    non_hermitian,
    trace_not_one,
    not_positive_semidefinite,
    invalid_metadata,
    invalid_hbar,
    invalid_revision,
    stale_revision,
    incomplete_transaction,
    revision_mismatch,
    numerical_inconsistency,
};

[[nodiscard]] std::string_view flow_code_name(FlowCode code) noexcept;

class FlowError final : public std::runtime_error {
public:
    FlowError(FlowCode code, std::string message);

    [[nodiscard]] FlowCode code() const noexcept { return code_; }

private:
    FlowCode code_;
};

struct FlowMetadata {
    // H is expressed in energy_unit and hbar in energy_unit*time_unit.
    // Matrix indices are computational/site basis indices, never eigenmode IDs.
    std::string energy_unit {"model_energy"};
    std::string time_unit {"model_time"};
    std::string basis_id {"computational_q0_lsb"};
    std::string basis_kind {"declared_discrete_site_basis"};
    std::string state_source_id {"unspecified-state-source"};
    std::string hamiltonian_source_id {"unspecified-hamiltonian-source"};
    std::string provenance {"unspecified-provenance"};
    std::string index_orientation {"row_target_column_source"};
    std::string bit_order {"q0_lsb"};
};

struct FlowPolicy {
    double hamiltonian_relative_hermiticity_tolerance {1.0e-10};
    double density_hermiticity_tolerance {1.0e-10};
    double density_trace_tolerance {1.0e-10};
    double density_positivity_tolerance {1.0e-10};
    double conservation_tolerance {1.0e-10};
    // Only controls whether a phase coordinate is mathematically defined.
    // It never removes an edge or creates an event.
    double phase_definition_tolerance {1.0e-15};
    std::size_t maximum_dimension {64};
};

struct FlowPhase {
    double radians {};
    bool defined {};
};

struct FlowEdge {
    // Positive current means transport from source to target.
    std::size_t source {};
    std::size_t target {};
    double current {};
    double coupling_magnitude {};
    double coherence_magnitude {};
    FlowPhase coupling_phase;
    FlowPhase coherence_phase;
    FlowPhase transport_phase;
    // The two component phases depend on local basis rephasing. Their sum,
    // arg(H_target,source * rho_source,target), and current do not.
    bool component_phases_local_gauge_dependent {true};
    bool transport_phase_local_rephasing_invariant {true};
};

struct FlowDiagnostics {
    double hamiltonian_hermiticity_residual_fro {};
    double density_hermiticity_residual_fro {};
    double density_trace_error_abs {};
    double density_minimum_ldlt_pivot {};
    double current_antisymmetry_max_abs {};
    double continuity_residual_max_abs {};
    double population_derivative_imaginary_max_abs {};
    double total_population_derivative_abs {};
};

// Immutable instantaneous current analysis in one explicitly declared discrete
// basis. This is not a geometric, gauge-field, GPE, or thresholded event-flow
// model, and it never evolves or mutates rho.
class FlowSnapshot final {
public:
    static FlowSnapshot evaluate(
        long revision,
        std::size_t dimension,
        const std::vector<double>& hamiltonian_real,
        const std::vector<double>& hamiltonian_imag,
        const std::vector<double>& density_real,
        const std::vector<double>& density_imag,
        double hbar,
        FlowMetadata metadata = {},
        FlowPolicy policy = {});

    [[nodiscard]] long revision() const noexcept { return revision_; }
    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t qubits() const noexcept { return qubits_; }
    [[nodiscard]] double hbar() const noexcept { return hbar_; }
    [[nodiscard]] const FlowMetadata& metadata() const noexcept { return metadata_; }
    [[nodiscard]] const std::string& hbar_unit() const noexcept { return hbar_unit_; }
    [[nodiscard]] const std::string& current_unit() const noexcept { return current_unit_; }
    [[nodiscard]] const HamiltonianSnapshot& hamiltonian() const noexcept
    {
        return hamiltonian_;
    }
    [[nodiscard]] const DensityState& density() const noexcept { return density_; }
    [[nodiscard]] const std::vector<double>& current_matrix() const noexcept
    {
        return current_matrix_;
    }
    [[nodiscard]] double current(std::size_t target, std::size_t source) const;
    [[nodiscard]] const std::vector<double>& population_derivative() const noexcept
    {
        return population_derivative_;
    }
    [[nodiscard]] const std::vector<double>& divergence() const noexcept
    {
        return divergence_;
    }
    [[nodiscard]] const std::vector<FlowEdge>& directed_edges() const noexcept
    {
        return directed_edges_;
    }
    [[nodiscard]] const FlowDiagnostics& diagnostics() const noexcept
    {
        return diagnostics_;
    }

private:
    FlowSnapshot(
        long revision,
        std::size_t dimension,
        std::size_t qubits,
        double hbar,
        FlowMetadata metadata,
        std::string hbar_unit,
        std::string current_unit,
        HamiltonianSnapshot hamiltonian,
        DensityState density,
        std::vector<double> current_matrix,
        std::vector<double> population_derivative,
        std::vector<double> divergence,
        std::vector<FlowEdge> directed_edges,
        FlowDiagnostics diagnostics);

    long revision_ {-1};
    std::size_t dimension_ {};
    std::size_t qubits_ {};
    double hbar_ {1.0};
    FlowMetadata metadata_;
    std::string hbar_unit_;
    std::string current_unit_;
    HamiltonianSnapshot hamiltonian_;
    DensityState density_;
    std::vector<double> current_matrix_;
    std::vector<double> population_derivative_;
    std::vector<double> divergence_;
    std::vector<FlowEdge> directed_edges_;
    FlowDiagnostics diagnostics_;
};

enum class FlowPart {
    hamiltonian_real,
    hamiltonian_imag,
    density_real,
    density_imag,
};

enum class FlowStageStatus { staged, accepted, rejected };

struct FlowStageResult {
    FlowStageStatus status {FlowStageStatus::rejected};
    long revision {-1};
    std::string detail;
    std::string message;
};

// Four matrix components stage invisibly. Only commit(revision) may atomically
// replace the active immutable flow frame, and failed commits retain the prior
// active frame.
class RevisionedFlowStore final {
public:
    RevisionedFlowStore(
        std::size_t dimension,
        double hbar,
        FlowMetadata metadata = {},
        FlowPolicy policy = {});

    [[nodiscard]] FlowStageResult stage(
        FlowPart part,
        long revision,
        std::vector<double> values);
    [[nodiscard]] FlowStageResult commit(long revision);
    void clear_candidate() noexcept;

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t element_count() const noexcept { return element_count_; }
    [[nodiscard]] long active_revision() const noexcept { return active_revision_; }
    [[nodiscard]] const FlowSnapshot* active() const noexcept { return active_.get(); }

private:
    struct CandidatePart {
        std::optional<long> revision;
        std::vector<double> values;
        void clear() noexcept;
    };

    [[nodiscard]] CandidatePart& candidate(FlowPart part) noexcept;
    [[nodiscard]] const CandidatePart& candidate(FlowPart part) const noexcept;

    std::size_t dimension_ {};
    std::size_t element_count_ {};
    double hbar_ {1.0};
    FlowMetadata metadata_;
    FlowPolicy policy_;
    long active_revision_ {-1};
    std::unique_ptr<FlowSnapshot> active_;
    CandidatePart hamiltonian_real_;
    CandidatePart hamiltonian_imag_;
    CandidatePart density_real_;
    CandidatePart density_imag_;
};

} // namespace qmw
