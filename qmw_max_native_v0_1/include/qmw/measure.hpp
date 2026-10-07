#pragma once

#include "qmw/state.hpp"

#include <cstddef>
#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace qmw {

enum class MeasurementCode {
    invalid_policy,
    invalid_revision,
    invalid_request,
    invalid_metadata,
    invalid_dimension,
    wrong_element_count,
    non_finite,
    non_hermitian_projector,
    non_idempotent_projector,
    non_orthogonal_projectors,
    incomplete_projectors,
    duplicate_outcome,
    dimension_mismatch,
    basis_mismatch,
    invalid_probability,
    zero_probability_outcome,
    outcome_not_found,
    invalid_axis,
};

[[nodiscard]] std::string_view measurement_code_name(MeasurementCode code) noexcept;

class MeasurementError final : public std::runtime_error {
public:
    MeasurementError(MeasurementCode code, std::string message);
    [[nodiscard]] MeasurementCode code() const noexcept { return code_; }

private:
    MeasurementCode code_;
};

enum class ProjectiveAxis { x, y, z };

[[nodiscard]] std::optional<ProjectiveAxis> projective_axis_from_name(
    std::string_view name) noexcept;
[[nodiscard]] std::string_view projective_axis_name(ProjectiveAxis axis) noexcept;

struct MeasurementPolicy {
    double tolerance {1.0e-10};
    std::size_t maximum_dimension {64};
};

struct MeasurementMetadata {
    // Operators and rho must be expressed in this same coordinate basis.
    std::string coordinate_basis_id {"computational_q0_lsb"};
    std::string operator_basis_id;
    std::string source_id {"qmw.measure"};
    std::string units {"dimensionless"};
    std::string provenance {"declared-projective-measurement"};
    std::string subsystem_order {"q0_lsb"};
};

struct MeasurementContext {
    long parent_revision {-1};
    std::string state_basis_id {"computational_q0_lsb"};
    std::string state_source_id {"qmw.state"};
    std::string state_units {"dimensionless"};
    std::string state_provenance {"unspecified-provenance"};
};

struct ProjectiveOutcome {
    long outcome {};
    std::string label;
    // Row-major, in MeasurementMetadata::coordinate_basis_id.
    std::vector<Complex> projector;
};

struct ProjectorDiagnostics {
    double completeness_residual_fro {};
    double maximum_hermiticity_residual_fro {};
    double maximum_idempotence_residual_fro {};
    double maximum_pairwise_overlap_fro {};
};

class ProjectiveMeasurement final {
public:
    static ProjectiveMeasurement from_projectors(
        std::size_t dimension,
        std::vector<ProjectiveOutcome> outcomes,
        MeasurementMetadata metadata,
        MeasurementPolicy policy = {});

    // Full product-basis measurement. Computational basis indices use q0 as
    // the least-significant bit; labels are q_(n-1)...q0.
    static ProjectiveMeasurement pauli_product(
        std::size_t qubits,
        ProjectiveAxis axis,
        MeasurementMetadata metadata,
        MeasurementPolicy policy = {});

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] const std::vector<ProjectiveOutcome>& outcomes() const noexcept { return outcomes_; }
    [[nodiscard]] const MeasurementMetadata& metadata() const noexcept { return metadata_; }
    [[nodiscard]] const MeasurementPolicy& policy() const noexcept { return policy_; }
    [[nodiscard]] const ProjectorDiagnostics& diagnostics() const noexcept { return diagnostics_; }

private:
    ProjectiveMeasurement(
        std::size_t dimension,
        std::vector<ProjectiveOutcome> outcomes,
        MeasurementMetadata metadata,
        MeasurementPolicy policy,
        ProjectorDiagnostics diagnostics);

    std::size_t dimension_ {};
    std::vector<ProjectiveOutcome> outcomes_;
    MeasurementMetadata metadata_;
    MeasurementPolicy policy_;
    ProjectorDiagnostics diagnostics_;
};

struct ProbabilityFrame {
    long parent_revision {-1};
    std::vector<long> outcomes;
    std::vector<std::string> labels;
    std::vector<double> raw_probabilities;
    std::vector<double> probabilities;
    double raw_probability_sum {};
    double normalization_denominator {};
    std::string probability_semantics {"exact_calculated_born_probability"};
    std::string estimate_semantics {"not_an_estimate"};
    std::string counts_semantics {"counts_not_available"};
    std::string uncertainty_semantics {"input_uncertainty_missing_not_propagated"};
};

enum class MeasurementSelection { specified_outcome, seeded_sample };

struct RngDrawMetadata {
    bool used {false};
    std::string algorithm {"splitmix64"};
    std::string version {"qmw-native-measure-v1"};
    std::uint64_t seed {};
    std::uint64_t draw_index_before {};
    std::uint64_t draw_index_after {};
    double uniform_01 {};
};

struct PosteriorStateCandidate {
    long parent_revision {-1};
    long outcome {};
    std::string outcome_label;
    std::string basis_id;
    std::string source_id;
    std::string units {"dimensionless"};
    std::string provenance;
    std::vector<Complex> values;
};

struct MeasurementRecord {
    std::uint64_t event_id {};
    long request_id {};
    long parent_revision {-1};
    MeasurementSelection selection {MeasurementSelection::specified_outcome};
    long outcome {};
    std::string outcome_label;
    double probability {};
    ProbabilityFrame distribution;
    RngDrawMetadata rng;
    PosteriorStateCandidate posterior;
    MeasurementMetadata measurement_metadata;
    MeasurementContext state_context;
    std::optional<std::uint64_t> counts;
    std::optional<std::uint64_t> shots;
    std::optional<double> probability_standard_uncertainty;
    std::string state_installation {"caller_authority_only"};
    bool authority_state_mutated {false};
};

class MeasurementEngine final {
public:
    explicit MeasurementEngine(ProjectiveMeasurement measurement, std::uint64_t seed = 29);

    [[nodiscard]] ProbabilityFrame probabilities(
        const DensityState& state,
        const MeasurementContext& context) const;

    // Deterministic conditioning consumes no RNG draw.
    [[nodiscard]] MeasurementRecord condition(
        const DensityState& state,
        const MeasurementContext& context,
        long outcome,
        long request_id = 0);

    [[nodiscard]] MeasurementRecord sample(
        const DensityState& state,
        const MeasurementContext& context,
        long request_id = 0);

    [[nodiscard]] const ProjectiveMeasurement& measurement() const noexcept { return measurement_; }
    [[nodiscard]] std::uint64_t seed() const noexcept { return seed_; }
    [[nodiscard]] std::uint64_t draw_index() const noexcept { return draw_index_; }
    [[nodiscard]] std::uint64_t event_count() const noexcept { return event_count_; }

private:
    [[nodiscard]] std::uint64_t next_u64() noexcept;
    [[nodiscard]] double next_uniform() noexcept;
    [[nodiscard]] MeasurementRecord make_record(
        const DensityState& state,
        const MeasurementContext& context,
        const ProbabilityFrame& distribution,
        std::size_t index,
        long request_id,
        MeasurementSelection selection,
        RngDrawMetadata rng);

    ProjectiveMeasurement measurement_;
    std::uint64_t seed_ {};
    std::uint64_t rng_state_ {};
    std::uint64_t draw_index_ {};
    std::uint64_t event_count_ {};
};

} // namespace qmw
