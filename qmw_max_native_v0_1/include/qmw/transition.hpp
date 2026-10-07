#pragma once

#include "qmw/hamiltonian.hpp"
#include "qmw/state.hpp"

#include <complex>
#include <cstddef>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace qmw {

enum class TransitionValidationCode {
    invalid_dimension,
    wrong_element_count,
    non_finite,
    non_hermitian,
    invalid_metadata,
    invalid_policy,
    dimension_mismatch,
    basis_mismatch,
    revision_mismatch,
    time_unit_mismatch,
    eigensolver_failed,
    numerical_inconsistency,
};

[[nodiscard]] std::string_view transition_validation_code_name(
    TransitionValidationCode code) noexcept;

class TransitionValidationError final : public std::runtime_error {
public:
    TransitionValidationError(TransitionValidationCode code, std::string message);

    [[nodiscard]] TransitionValidationCode code() const noexcept { return code_; }

private:
    TransitionValidationCode code_;
};

enum class TransitionOperatorKind { coupling, observable };

[[nodiscard]] std::string_view transition_operator_kind_name(
    TransitionOperatorKind kind) noexcept;

struct TransitionUnits {
    // H is in energy_unit and hbar is in energy_unit*time_unit. Therefore
    // omega = delta_E/hbar is a signed angular frequency in rad/time_unit.
    double hbar {1.0};
    std::string energy_unit {"model_energy"};
    std::string time_unit {"s"};
    std::string operator_unit {"dimensionless"};
};

struct TransitionContext {
    long revision {-1};
    double time {};
    double dt {};
    std::string basis_id {"computational_q0_lsb"};
    std::string time_unit {"s"};
    std::string source_id {"unspecified-source"};
    std::string provenance {"unspecified-provenance"};
};

struct TransitionOperatorMetadata {
    long revision {-1};
    TransitionOperatorKind kind {TransitionOperatorKind::coupling};
    std::string basis_id {"computational_q0_lsb"};
    std::string unit {"dimensionless"};
    std::string source_id {"unspecified-operator-source"};
    std::string provenance {"unspecified-operator-provenance"};
};

struct TransitionPolicy {
    double relative_hermiticity_tolerance {1.0e-10};
    double eigensolver_tolerance {1.0e-12};
    double energy_gap_tolerance {1.0e-9};
    double amplitude_threshold {1.0e-8};
    double activity_threshold {1.0e-8};
    bool include_diagonal {false};
    bool include_zero_gap {false};
    std::size_t maximum_dimension {64};
    std::size_t maximum_jacobi_iterations_per_element {128};
};

// Immutable declared A. Couplings may be non-Hermitian; observables must be
// Hermitian relative to their own operator scale.
class TransitionOperator final {
public:
    static TransitionOperator from_split(
        std::size_t dimension,
        const std::vector<double>& real,
        const std::vector<double>& imag,
        TransitionOperatorMetadata metadata,
        TransitionPolicy policy = {});

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] const std::vector<Complex>& values() const noexcept { return values_; }
    [[nodiscard]] const TransitionOperatorMetadata& metadata() const noexcept { return metadata_; }
    [[nodiscard]] double hermiticity_residual_fro() const noexcept
    {
        return hermiticity_residual_fro_;
    }
    [[nodiscard]] const Complex& at(std::size_t row, std::size_t column) const;

private:
    TransitionOperator(
        std::size_t dimension,
        std::vector<Complex> values,
        TransitionOperatorMetadata metadata,
        double hermiticity_residual_fro);

    std::size_t dimension_ {};
    std::vector<Complex> values_;
    TransitionOperatorMetadata metadata_;
    double hermiticity_residual_fro_ {};
};

struct HermitianEigensystem {
    // Ascending frame-local energies and column eigenvectors, row-major.
    std::vector<double> eigenvalues;
    std::vector<Complex> eigenvectors;
    std::size_t iterations {};
    double maximum_off_diagonal {};
    double eigen_residual_fro {};
    double reconstruction_residual_fro {};
};

struct TransitionEdge {
    // All matrix indices use [target=m, source=n].
    std::size_t source {};
    std::size_t target {};
    double delta_E {};
    double omega {};
    Complex A_mn {};
    double magnitude {};
    std::optional<double> phase_rad;
    double source_population {};
    double target_population {};
    Complex coherence_mn {};
    Complex coherence_nm {};
    double matrix_element_squared {};
    // |A_mn|^2 max(p_source,0): diagnostic only, never a physical rate.
    double diagnostic_activity {};
    bool diagonal {};
    bool zero_gap {};
    bool basis_dependent_degenerate_endpoint {};
};

struct TransitionDiagnostics {
    double density_hermiticity_residual_fro {};
    double trace_error_abs {};
    double hamiltonian_hermiticity_residual_fro {};
    double operator_hermiticity_residual_fro {};
    double hamiltonian_eigen_residual_fro {};
    double hamiltonian_reconstruction_residual_fro {};
    double operator_transform_residual_fro {};
    double density_transform_hermiticity_residual_fro {};
    std::size_t jacobi_iterations {};
    double jacobi_maximum_off_diagonal {};
};

class TransitionFrame final {
public:
    // Const data members make an admitted frame a non-assignable immutable
    // snapshot. Analysis always copies caller-owned context and units into it.
    const TransitionContext context;
    const TransitionUnits units;
    const TransitionOperatorMetadata operator_metadata;
    const std::size_t dimension {};
    const std::vector<double> energies;
    const std::vector<Complex> energy_eigenvectors;
    const std::vector<Complex> rho_in_energy_basis;
    const std::vector<Complex> operator_in_energy_basis;
    const std::vector<double> energy_populations;
    const std::vector<double> diagnostic_activity;
    const std::vector<std::vector<std::size_t>> energy_degenerate_groups;
    // Candidate edges after diagonal/zero-gap policy.
    const std::vector<TransitionEdge> edges;
    // Off-diagonal edges strictly above both admission thresholds.
    const std::vector<TransitionEdge> transitions;
    const TransitionDiagnostics diagnostics;
    const std::string activity_name {"population_weighted_matrix_element"};
    const std::string activity_units {"operator_unit_squared"};
    const std::string activity_interpretation {
        "diagnostic activity only; not a universal transition rate or spontaneous emission"};
};

// Read-only instantaneous energy-basis analysis. It neither evolves nor
// measures the state and has no event scheduling or sound-mapping authority.
[[nodiscard]] TransitionFrame analyze_transitions(
    const DensityState& state,
    const HamiltonianSnapshot& hamiltonian,
    const TransitionOperator& declared_operator,
    TransitionContext context,
    TransitionUnits units = {},
    TransitionPolicy policy = {});

enum class TransitionInputPart {
    rho_real,
    rho_imag,
    hamiltonian_real,
    hamiltonian_imag,
    operator_real,
    operator_imag,
};

enum class TransitionStageStatus { staged, accepted, rejected };

struct TransitionStageResult {
    TransitionStageStatus status {TransitionStageStatus::rejected};
    long revision {-1};
    std::string detail;
    std::string message;
};

// Seven-part revision gate: rho/H/A split matrices plus (time,dt) context.
// The previous immutable frame remains active until every part has the same
// newer revision and the complete scientific analysis succeeds.
class RevisionedTransitionStore final {
public:
    RevisionedTransitionStore(
        std::size_t dimension,
        TransitionContext fixed_context,
        TransitionUnits units,
        TransitionOperatorMetadata operator_metadata,
        TransitionPolicy policy = {});

    [[nodiscard]] TransitionStageResult stage_matrix(
        TransitionInputPart part,
        long revision,
        std::vector<double> values);
    [[nodiscard]] TransitionStageResult stage_context(
        long revision,
        double time,
        double dt);
    void clear_candidate() noexcept;

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t element_count() const noexcept { return element_count_; }
    [[nodiscard]] long active_revision() const noexcept { return active_revision_; }
    [[nodiscard]] const TransitionFrame* active() const noexcept { return active_.get(); }
    [[nodiscard]] const TransitionUnits& units() const noexcept { return units_; }
    [[nodiscard]] const TransitionContext& fixed_context() const noexcept { return fixed_context_; }
    [[nodiscard]] const TransitionOperatorMetadata& operator_metadata() const noexcept
    {
        return operator_metadata_;
    }

private:
    struct CandidateMatrixPart {
        std::optional<long> revision;
        std::vector<double> values;
        void clear() noexcept;
    };
    struct CandidateContextPart {
        std::optional<long> revision;
        double time {};
        double dt {};
        void clear() noexcept;
    };

    [[nodiscard]] TransitionStageResult try_commit(long staged_revision);

    std::size_t dimension_ {};
    std::size_t element_count_ {};
    TransitionContext fixed_context_;
    TransitionUnits units_;
    TransitionOperatorMetadata operator_metadata_;
    TransitionPolicy policy_;
    long active_revision_ {-1};
    std::unique_ptr<TransitionFrame> active_;
    CandidateMatrixPart rho_real_;
    CandidateMatrixPart rho_imag_;
    CandidateMatrixPart hamiltonian_real_;
    CandidateMatrixPart hamiltonian_imag_;
    CandidateMatrixPart operator_real_;
    CandidateMatrixPart operator_imag_;
    CandidateContextPart context_;
};

} // namespace qmw
