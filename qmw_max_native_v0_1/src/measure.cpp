#include "qmw/measure.hpp"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <limits>
#include <set>
#include <utility>

namespace qmw {
namespace {

using Matrix = std::vector<Complex>;

[[nodiscard]] std::size_t at(const std::size_t n, const std::size_t row, const std::size_t column)
{
    return row * n + column;
}

[[nodiscard]] bool blank(const std::string& value)
{
    return value.empty() || std::all_of(value.begin(), value.end(), [](const unsigned char c) {
        return std::isspace(c) != 0;
    });
}

[[nodiscard]] bool finite(const Complex value)
{
    return std::isfinite(value.real()) && std::isfinite(value.imag());
}

[[nodiscard]] double frobenius(const Matrix& matrix)
{
    long double sum = 0.0L;
    for (const auto value : matrix) {
        sum += static_cast<long double>(std::norm(value));
    }
    return std::sqrt(static_cast<double>(sum));
}

[[nodiscard]] Matrix multiply(const Matrix& left, const Matrix& right, const std::size_t n)
{
    Matrix result(n * n, Complex {});
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t inner = 0; inner < n; ++inner) {
            const auto l = left[at(n, row, inner)];
            if (l == Complex {}) {
                continue;
            }
            for (std::size_t column = 0; column < n; ++column) {
                result[at(n, row, column)] += l * right[at(n, inner, column)];
            }
        }
    }
    return result;
}

[[nodiscard]] double residual(const Matrix& left, const Matrix& right)
{
    Matrix difference(left.size());
    for (std::size_t index = 0; index < left.size(); ++index) {
        difference[index] = left[index] - right[index];
    }
    return frobenius(difference);
}

[[nodiscard]] double hermiticity_residual(const Matrix& matrix, const std::size_t n)
{
    Matrix difference(matrix.size());
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t column = 0; column < n; ++column) {
            difference[at(n, row, column)] =
                matrix[at(n, row, column)] - std::conj(matrix[at(n, column, row)]);
        }
    }
    return frobenius(difference);
}

[[nodiscard]] Matrix identity(const std::size_t n)
{
    Matrix result(n * n, Complex {});
    for (std::size_t index = 0; index < n; ++index) {
        result[at(n, index, index)] = 1.0;
    }
    return result;
}

[[nodiscard]] double projector_product_frobenius(
    const Matrix& left,
    const Matrix& right,
    const std::size_t n)
{
    // For Hermitian idempotents, ||P Q||_F^2 = Tr(P Q). Computing that
    // trace directly avoids constructing every pairwise matrix product.
    Complex trace {};
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t column = 0; column < n; ++column) {
            trace += left[at(n, row, column)] * right[at(n, column, row)];
        }
    }
    return std::sqrt(std::abs(trace));
}

void validate_policy(const MeasurementPolicy& policy)
{
    if (!std::isfinite(policy.tolerance) || policy.tolerance <= 0.0
        || policy.tolerance > 1.0e-6 || policy.maximum_dimension == 0) {
        throw MeasurementError(MeasurementCode::invalid_policy, "invalid measurement validation policy");
    }
}

void validate_metadata(const MeasurementMetadata& metadata)
{
    if (blank(metadata.coordinate_basis_id) || blank(metadata.operator_basis_id)
        || blank(metadata.source_id) || blank(metadata.units) || blank(metadata.provenance)
        || metadata.subsystem_order != "q0_lsb") {
        throw MeasurementError(
            MeasurementCode::invalid_metadata,
            "measurement metadata must be nonblank and declare q0_lsb subsystem order");
    }
    if (metadata.units != "dimensionless" && metadata.units != "1") {
        throw MeasurementError(
            MeasurementCode::invalid_metadata,
            "projectors must have dimensionless units");
    }
}

void validate_context(
    const DensityState& state,
    const ProjectiveMeasurement& measurement,
    const MeasurementContext& context)
{
    if (context.parent_revision < 0) {
        throw MeasurementError(MeasurementCode::invalid_revision, "parent revision must be nonnegative");
    }
    if (blank(context.state_basis_id) || blank(context.state_source_id)
        || blank(context.state_units) || blank(context.state_provenance)) {
        throw MeasurementError(MeasurementCode::invalid_metadata, "state context metadata must be nonblank");
    }
    if (state.dimension() != measurement.dimension()) {
        throw MeasurementError(MeasurementCode::dimension_mismatch, "state and projectors differ in dimension");
    }
    if (context.state_basis_id != measurement.metadata().coordinate_basis_id) {
        throw MeasurementError(MeasurementCode::basis_mismatch, "state and projectors use different coordinates");
    }
    if (context.state_units != "dimensionless" && context.state_units != "1") {
        throw MeasurementError(MeasurementCode::invalid_metadata, "density state must be dimensionless");
    }
}

[[nodiscard]] std::string bit_label(const std::size_t value, const std::size_t qubits)
{
    std::string result(qubits, '0');
    for (std::size_t bit = 0; bit < qubits; ++bit) {
        if ((value & (std::size_t {1} << bit)) != 0) {
            result[qubits - 1 - bit] = '1';
        }
    }
    return result;
}

[[nodiscard]] Matrix rank_one_projector(
    const std::size_t qubits,
    const ProjectiveAxis axis,
    const std::size_t outcome)
{
    const std::size_t n = std::size_t {1} << qubits;
    std::vector<Complex> ket(n, Complex {});
    const double scale = 1.0 / std::sqrt(static_cast<double>(n));
    for (std::size_t row = 0; row < n; ++row) {
        if (axis == ProjectiveAxis::z) {
            ket[row] = row == outcome ? Complex {1.0, 0.0} : Complex {};
            continue;
        }
        Complex amplitude {scale, 0.0};
        for (std::size_t bit = 0; bit < qubits; ++bit) {
            const bool row_one = (row & (std::size_t {1} << bit)) != 0;
            const bool outcome_one = (outcome & (std::size_t {1} << bit)) != 0;
            if (!row_one) {
                continue;
            }
            if (axis == ProjectiveAxis::x) {
                if (outcome_one) {
                    amplitude = -amplitude;
                }
            } else {
                amplitude *= outcome_one ? Complex {0.0, -1.0} : Complex {0.0, 1.0};
            }
        }
        ket[row] = amplitude;
    }

    Matrix projector(n * n);
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t column = 0; column < n; ++column) {
            projector[at(n, row, column)] = ket[row] * std::conj(ket[column]);
        }
    }
    return projector;
}

} // namespace

std::string_view measurement_code_name(const MeasurementCode code) noexcept
{
    switch (code) {
    case MeasurementCode::invalid_policy: return "invalid_policy";
    case MeasurementCode::invalid_revision: return "invalid_revision";
    case MeasurementCode::invalid_request: return "invalid_request";
    case MeasurementCode::invalid_metadata: return "invalid_metadata";
    case MeasurementCode::invalid_dimension: return "invalid_dimension";
    case MeasurementCode::wrong_element_count: return "wrong_element_count";
    case MeasurementCode::non_finite: return "non_finite";
    case MeasurementCode::non_hermitian_projector: return "non_hermitian_projector";
    case MeasurementCode::non_idempotent_projector: return "non_idempotent_projector";
    case MeasurementCode::non_orthogonal_projectors: return "non_orthogonal_projectors";
    case MeasurementCode::incomplete_projectors: return "incomplete_projectors";
    case MeasurementCode::duplicate_outcome: return "duplicate_outcome";
    case MeasurementCode::dimension_mismatch: return "dimension_mismatch";
    case MeasurementCode::basis_mismatch: return "basis_mismatch";
    case MeasurementCode::invalid_probability: return "invalid_probability";
    case MeasurementCode::zero_probability_outcome: return "zero_probability_outcome";
    case MeasurementCode::outcome_not_found: return "outcome_not_found";
    case MeasurementCode::invalid_axis: return "invalid_axis";
    }
    return "unknown";
}

MeasurementError::MeasurementError(const MeasurementCode code, std::string message)
    : std::runtime_error(std::move(message)), code_(code)
{
}

std::optional<ProjectiveAxis> projective_axis_from_name(const std::string_view name) noexcept
{
    if (name == "X" || name == "x") return ProjectiveAxis::x;
    if (name == "Y" || name == "y") return ProjectiveAxis::y;
    if (name == "Z" || name == "z") return ProjectiveAxis::z;
    return std::nullopt;
}

std::string_view projective_axis_name(const ProjectiveAxis axis) noexcept
{
    switch (axis) {
    case ProjectiveAxis::x: return "X";
    case ProjectiveAxis::y: return "Y";
    case ProjectiveAxis::z: return "Z";
    }
    return "invalid";
}

ProjectiveMeasurement::ProjectiveMeasurement(
    const std::size_t dimension,
    std::vector<ProjectiveOutcome> outcomes,
    MeasurementMetadata metadata,
    const MeasurementPolicy policy,
    const ProjectorDiagnostics diagnostics)
    : dimension_(dimension), outcomes_(std::move(outcomes)), metadata_(std::move(metadata)),
      policy_(policy), diagnostics_(diagnostics)
{
}

ProjectiveMeasurement ProjectiveMeasurement::from_projectors(
    const std::size_t dimension,
    std::vector<ProjectiveOutcome> outcomes,
    MeasurementMetadata metadata,
    const MeasurementPolicy policy)
{
    validate_policy(policy);
    validate_metadata(metadata);
    if (dimension == 0 || dimension > policy.maximum_dimension) {
        throw MeasurementError(MeasurementCode::invalid_dimension, "invalid projective-measurement dimension");
    }
    if (outcomes.empty()) {
        throw MeasurementError(MeasurementCode::incomplete_projectors, "measurement requires projectors");
    }

    std::set<long> identifiers;
    std::set<std::string> labels;
    Matrix total(dimension * dimension, Complex {});
    ProjectorDiagnostics diagnostics;
    for (const auto& outcome : outcomes) {
        if (outcome.outcome < 0 || blank(outcome.label)
            || !identifiers.insert(outcome.outcome).second
            || !labels.insert(outcome.label).second) {
            throw MeasurementError(MeasurementCode::duplicate_outcome, "outcomes must have unique nonnegative ids and labels");
        }
        if (outcome.projector.size() != dimension * dimension) {
            throw MeasurementError(MeasurementCode::wrong_element_count, "projector must contain dimension squared elements");
        }
        for (const auto value : outcome.projector) {
            if (!finite(value)) {
                throw MeasurementError(MeasurementCode::non_finite, "projector contains a non-finite value");
            }
        }
        const double hermitian = hermiticity_residual(outcome.projector, dimension);
        diagnostics.maximum_hermiticity_residual_fro = std::max(
            diagnostics.maximum_hermiticity_residual_fro, hermitian);
        if (hermitian > policy.tolerance) {
            throw MeasurementError(MeasurementCode::non_hermitian_projector, "projector is not Hermitian");
        }
        const auto squared = multiply(outcome.projector, outcome.projector, dimension);
        const double idempotence = residual(squared, outcome.projector);
        diagnostics.maximum_idempotence_residual_fro = std::max(
            diagnostics.maximum_idempotence_residual_fro, idempotence);
        if (idempotence > policy.tolerance * std::max(1.0, frobenius(outcome.projector))) {
            throw MeasurementError(MeasurementCode::non_idempotent_projector, "effect is not an idempotent projector");
        }
        for (std::size_t index = 0; index < total.size(); ++index) {
            total[index] += outcome.projector[index];
        }
    }

    for (std::size_t left = 0; left < outcomes.size(); ++left) {
        for (std::size_t right = left + 1; right < outcomes.size(); ++right) {
            const double overlap = projector_product_frobenius(
                outcomes[left].projector, outcomes[right].projector, dimension);
            diagnostics.maximum_pairwise_overlap_fro = std::max(
                diagnostics.maximum_pairwise_overlap_fro, overlap);
            if (overlap > policy.tolerance) {
                throw MeasurementError(MeasurementCode::non_orthogonal_projectors, "projectors are not mutually orthogonal");
            }
        }
    }
    diagnostics.completeness_residual_fro = residual(total, identity(dimension));
    if (diagnostics.completeness_residual_fro > policy.tolerance * std::sqrt(static_cast<double>(dimension))) {
        throw MeasurementError(MeasurementCode::incomplete_projectors, "projectors do not sum to identity");
    }
    return ProjectiveMeasurement(
        dimension, std::move(outcomes), std::move(metadata), policy, diagnostics);
}

ProjectiveMeasurement ProjectiveMeasurement::pauli_product(
    const std::size_t qubits,
    const ProjectiveAxis axis,
    MeasurementMetadata metadata,
    const MeasurementPolicy policy)
{
    if (qubits == 0 || qubits >= std::numeric_limits<std::size_t>::digits) {
        throw MeasurementError(MeasurementCode::invalid_dimension, "invalid qubit count");
    }
    if (projective_axis_name(axis) == "invalid") {
        throw MeasurementError(MeasurementCode::invalid_axis, "basis axis must be X, Y, or Z");
    }
    const std::size_t dimension = std::size_t {1} << qubits;
    metadata.operator_basis_id = metadata.operator_basis_id.empty()
        ? metadata.coordinate_basis_id + ":measurement:" + std::string(projective_axis_name(axis))
        : metadata.operator_basis_id;
    std::vector<ProjectiveOutcome> outcomes;
    outcomes.reserve(dimension);
    for (std::size_t outcome = 0; outcome < dimension; ++outcome) {
        outcomes.push_back(ProjectiveOutcome {
            static_cast<long>(outcome), bit_label(outcome, qubits),
            rank_one_projector(qubits, axis, outcome),
        });
    }
    return from_projectors(dimension, std::move(outcomes), std::move(metadata), policy);
}

MeasurementEngine::MeasurementEngine(ProjectiveMeasurement measurement, const std::uint64_t seed)
    : measurement_(std::move(measurement)), seed_(seed), rng_state_(seed)
{
}

ProbabilityFrame MeasurementEngine::probabilities(
    const DensityState& state,
    const MeasurementContext& context) const
{
    validate_context(state, measurement_, context);
    ProbabilityFrame frame;
    frame.parent_revision = context.parent_revision;
    const auto n = state.dimension();
    const auto& rho = state.values();
    for (const auto& outcome : measurement_.outcomes()) {
        // Tr(P rho), in the declared common coordinate basis.
        Complex probability {};
        for (std::size_t row = 0; row < n; ++row) {
            for (std::size_t column = 0; column < n; ++column) {
                probability += outcome.projector[at(n, row, column)] * rho[at(n, column, row)];
            }
        }
        if (!finite(probability) || std::abs(probability.imag()) > measurement_.policy().tolerance
            || probability.real() < -measurement_.policy().tolerance
            || probability.real() > 1.0 + measurement_.policy().tolerance) {
            throw MeasurementError(MeasurementCode::invalid_probability, "invalid Born probability");
        }
        frame.outcomes.push_back(outcome.outcome);
        frame.labels.push_back(outcome.label);
        frame.raw_probabilities.push_back(probability.real());
        frame.raw_probability_sum += probability.real();
    }
    if (std::abs(frame.raw_probability_sum - 1.0)
        > measurement_.policy().tolerance * static_cast<double>(n)) {
        throw MeasurementError(MeasurementCode::invalid_probability, "Born probabilities do not sum to one");
    }
    frame.probabilities.reserve(frame.raw_probabilities.size());
    for (const double raw : frame.raw_probabilities) {
        frame.probabilities.push_back(std::clamp(raw, 0.0, 1.0));
        frame.normalization_denominator += frame.probabilities.back();
    }
    if (!(frame.normalization_denominator > 0.0)) {
        throw MeasurementError(MeasurementCode::invalid_probability, "zero total Born probability");
    }
    for (double& probability : frame.probabilities) {
        probability /= frame.normalization_denominator;
    }
    return frame;
}

std::uint64_t MeasurementEngine::next_u64() noexcept
{
    rng_state_ += UINT64_C(0x9e3779b97f4a7c15);
    std::uint64_t value = rng_state_;
    value = (value ^ (value >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    value = (value ^ (value >> 27U)) * UINT64_C(0x94d049bb133111eb);
    ++draw_index_;
    return value ^ (value >> 31U);
}

double MeasurementEngine::next_uniform() noexcept
{
    // Exactly 53 random bits mapped to [0,1), independent of libstdc++.
    return static_cast<double>(next_u64() >> 11U) * 0x1.0p-53;
}

MeasurementRecord MeasurementEngine::make_record(
    const DensityState& state,
    const MeasurementContext& context,
    const ProbabilityFrame& distribution,
    const std::size_t index,
    const long request_id,
    const MeasurementSelection selection,
    RngDrawMetadata rng)
{
    if (request_id < 0) {
        throw MeasurementError(MeasurementCode::invalid_request, "request id must be nonnegative");
    }
    const double probability = distribution.probabilities.at(index);
    const double raw_probability = distribution.raw_probabilities.at(index);
    if (!(probability > 0.0) || !(raw_probability > 0.0)) {
        throw MeasurementError(MeasurementCode::zero_probability_outcome, "cannot condition on a zero-probability outcome");
    }

    const auto n = state.dimension();
    const auto& projector = measurement_.outcomes().at(index).projector;
    const auto numerator = multiply(multiply(projector, state.values(), n), projector, n);
    std::vector<double> real(n * n);
    std::vector<double> imag(n * n);
    std::vector<Complex> posterior(n * n);
    for (std::size_t element = 0; element < posterior.size(); ++element) {
        posterior[element] = numerator[element] / raw_probability;
        real[element] = posterior[element].real();
        imag[element] = posterior[element].imag();
    }
    // Reuse the authoritative density validator, but retain the unmodified
    // computed candidate. Validation is not an installation transaction.
    ValidationPolicy posterior_policy;
    posterior_policy.hermiticity_tolerance = measurement_.policy().tolerance;
    posterior_policy.trace_tolerance = measurement_.policy().tolerance;
    posterior_policy.positivity_tolerance = measurement_.policy().tolerance;
    posterior_policy.maximum_dimension = measurement_.policy().maximum_dimension;
    (void)DensityState::from_split(n, real, imag, posterior_policy);

    ++event_count_;
    const auto& selected = measurement_.outcomes().at(index);
    PosteriorStateCandidate candidate {
        context.parent_revision,
        selected.outcome,
        selected.label,
        measurement_.metadata().coordinate_basis_id,
        measurement_.metadata().source_id,
        "dimensionless",
        measurement_.metadata().provenance + ":posterior_candidate_not_committed",
        std::move(posterior),
    };
    return MeasurementRecord {
        event_count_, request_id, context.parent_revision, selection,
        selected.outcome, selected.label, probability, distribution, std::move(rng),
        std::move(candidate), measurement_.metadata(), context,
        std::nullopt, std::nullopt, std::nullopt,
        "caller_authority_only", false,
    };
}

MeasurementRecord MeasurementEngine::condition(
    const DensityState& state,
    const MeasurementContext& context,
    const long outcome,
    const long request_id)
{
    if (request_id < 0) {
        throw MeasurementError(MeasurementCode::invalid_request, "request id must be nonnegative");
    }
    const auto distribution = probabilities(state, context);
    const auto found = std::find(distribution.outcomes.begin(), distribution.outcomes.end(), outcome);
    if (found == distribution.outcomes.end()) {
        throw MeasurementError(MeasurementCode::outcome_not_found, "requested outcome is not declared");
    }
    RngDrawMetadata rng;
    rng.seed = seed_;
    rng.draw_index_before = draw_index_;
    rng.draw_index_after = draw_index_;
    return make_record(
        state, context, distribution,
        static_cast<std::size_t>(std::distance(distribution.outcomes.begin(), found)),
        request_id, MeasurementSelection::specified_outcome, std::move(rng));
}

MeasurementRecord MeasurementEngine::sample(
    const DensityState& state,
    const MeasurementContext& context,
    const long request_id)
{
    if (request_id < 0) {
        throw MeasurementError(MeasurementCode::invalid_request, "request id must be nonnegative");
    }
    const auto distribution = probabilities(state, context);
    RngDrawMetadata rng;
    rng.used = true;
    rng.seed = seed_;
    rng.draw_index_before = draw_index_;
    rng.uniform_01 = next_uniform();
    rng.draw_index_after = draw_index_;

    double cumulative = 0.0;
    std::size_t selected = distribution.probabilities.size();
    for (std::size_t index = 0; index < distribution.probabilities.size(); ++index) {
        cumulative += distribution.probabilities[index];
        if (rng.uniform_01 < cumulative) {
            selected = index;
            break;
        }
    }
    if (selected == distribution.probabilities.size()) {
        for (std::size_t index = distribution.probabilities.size(); index-- > 0;) {
            if (distribution.probabilities[index] > 0.0) {
                selected = index;
                break;
            }
        }
    }
    return make_record(
        state, context, distribution, selected, request_id,
        MeasurementSelection::seeded_sample, std::move(rng));
}

} // namespace qmw
