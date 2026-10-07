#include "qmw/uncertainty.hpp"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <limits>
#include <numbers>
#include <utility>

namespace qmw {
namespace {

[[nodiscard]] bool blank(const std::string& value)
{
    return value.empty() || std::all_of(
        value.begin(), value.end(),
        [](const unsigned char character) { return std::isspace(character) != 0; });
}

void validate_policy(const UncertaintyValidationPolicy& policy)
{
    if (!std::isfinite(policy.relative_hermiticity_tolerance)
        || !std::isfinite(policy.reality_tolerance)
        || !std::isfinite(policy.nonnegative_tolerance)
        || !(policy.relative_hermiticity_tolerance > 0.0)
        || !(policy.reality_tolerance > 0.0)
        || !(policy.nonnegative_tolerance > 0.0)
        || policy.maximum_dimension == 0) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::invalid_policy,
            "uncertainty validation tolerances and dimension limit must be positive and finite");
    }
}

void validate_observable_metadata(const ObservableMetadata& metadata)
{
    if (metadata.revision < 0 || blank(metadata.basis_id)
        || blank(metadata.unit) || blank(metadata.source_id)) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::invalid_metadata,
            "observable revision, basis, unit, and source metadata must be explicit");
    }
}

void validate_pairing(
    const DensityState& state,
    const StateAnalysisMetadata& state_metadata,
    const HermitianObservable& observable)
{
    if (state_metadata.revision < 0 || blank(state_metadata.basis_id)
        || blank(state_metadata.source_id) || blank(state_metadata.unit)) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::invalid_metadata,
            "state revision, basis, source, and unit metadata must be explicit");
    }
    if (state.dimension() != observable.dimension()) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::dimension_mismatch,
            "state and observable dimensions do not match");
    }
    if (state_metadata.basis_id != observable.metadata().basis_id) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::basis_mismatch,
            "state and observable basis identifiers do not match");
    }
    if (state_metadata.revision != observable.metadata().revision) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::revision_mismatch,
            "state and observable revisions do not match");
    }
}

[[nodiscard]] std::vector<Complex> multiply(
    const std::vector<Complex>& left,
    const std::vector<Complex>& right,
    const std::size_t dimension)
{
    std::vector<Complex> result(dimension * dimension, Complex {});
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t inner = 0; inner < dimension; ++inner) {
            const auto left_value = left[row * dimension + inner];
            for (std::size_t column = 0; column < dimension; ++column) {
                result[row * dimension + column]
                    += left_value * right[inner * dimension + column];
            }
        }
    }
    return result;
}

[[nodiscard]] Complex trace_rho_times(
    const DensityState& state,
    const std::vector<Complex>& matrix)
{
    Complex result {};
    const auto dimension = state.dimension();
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            result += state.at(row, column) * matrix[column * dimension + row];
        }
    }
    return result;
}

[[nodiscard]] double require_real(
    const Complex value,
    const UncertaintyValidationPolicy& policy,
    const char* message)
{
    if (!std::isfinite(value.real()) || !std::isfinite(value.imag())) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::numerical_inconsistency,
            "uncertainty matrix operation produced a non-finite value");
    }
    const double scale = std::max(std::abs(value), std::numeric_limits<double>::min());
    if (std::abs(value.imag()) > policy.reality_tolerance * scale) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::numerical_inconsistency,
            message);
    }
    return value.real();
}

[[nodiscard]] double clamp_nonnegative(
    const double value,
    const double scale,
    const UncertaintyValidationPolicy& policy,
    const char* message)
{
    if (!std::isfinite(value) || !std::isfinite(scale)) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::numerical_inconsistency,
            "uncertainty calculation produced a non-finite variance");
    }
    if (value < -policy.nonnegative_tolerance
            * std::max(scale, std::numeric_limits<double>::min())) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::numerical_inconsistency,
            message);
    }
    return std::max(0.0, value);
}

void validate_mt_metadata(const MandelstamTammMetadata& metadata)
{
    if (metadata.revision < 0 || blank(metadata.basis_id)
        || blank(metadata.observable_unit) || blank(metadata.energy_unit)
        || blank(metadata.source_id)) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::invalid_metadata,
            "Mandelstam-Tamm metadata must identify revision, basis, units, and source");
    }
}

} // namespace

std::string_view uncertainty_validation_code_name(
    const UncertaintyValidationCode code) noexcept
{
    switch (code) {
    case UncertaintyValidationCode::invalid_dimension: return "invalid_dimension";
    case UncertaintyValidationCode::wrong_element_count: return "wrong_element_count";
    case UncertaintyValidationCode::non_finite: return "non_finite";
    case UncertaintyValidationCode::non_hermitian: return "non_hermitian";
    case UncertaintyValidationCode::invalid_metadata: return "invalid_metadata";
    case UncertaintyValidationCode::invalid_policy: return "invalid_policy";
    case UncertaintyValidationCode::dimension_mismatch: return "dimension_mismatch";
    case UncertaintyValidationCode::basis_mismatch: return "basis_mismatch";
    case UncertaintyValidationCode::revision_mismatch: return "revision_mismatch";
    case UncertaintyValidationCode::numerical_inconsistency: return "numerical_inconsistency";
    case UncertaintyValidationCode::invalid_mandelstam_tamm_input:
        return "invalid_mandelstam_tamm_input";
    }
    return "unknown_uncertainty_validation_error";
}

UncertaintyValidationError::UncertaintyValidationError(
    const UncertaintyValidationCode code,
    const char* message)
    : std::runtime_error(message)
    , code_(code)
{
}

HermitianObservable::HermitianObservable(
    const std::size_t dimension,
    std::vector<Complex> values,
    ObservableMetadata metadata,
    const double hermiticity_residual_fro)
    : dimension_(dimension)
    , values_(std::move(values))
    , metadata_(std::move(metadata))
    , hermiticity_residual_fro_(hermiticity_residual_fro)
{
}

HermitianObservable HermitianObservable::from_split(
    const std::size_t dimension,
    const std::vector<double>& real,
    const std::vector<double>& imag,
    ObservableMetadata metadata,
    const UncertaintyValidationPolicy policy)
{
    validate_policy(policy);
    validate_observable_metadata(metadata);
    if (dimension == 0 || dimension > policy.maximum_dimension) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::invalid_dimension,
            "observable dimension is zero or exceeds the configured limit");
    }
    const auto element_count = dimension * dimension;
    if (real.size() != element_count || imag.size() != element_count) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::wrong_element_count,
            "observable components must each contain dimension squared values");
    }

    std::vector<Complex> values;
    values.reserve(element_count);
    double norm_squared = 0.0;
    for (std::size_t index = 0; index < element_count; ++index) {
        const Complex value {real[index], imag[index]};
        if (!std::isfinite(value.real()) || !std::isfinite(value.imag())) {
            throw UncertaintyValidationError(
                UncertaintyValidationCode::non_finite,
                "observable contains a non-finite value");
        }
        norm_squared += std::norm(value);
        values.push_back(value);
    }

    double residual_squared = 0.0;
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            residual_squared += std::norm(
                values[row * dimension + column]
                - std::conj(values[column * dimension + row]));
        }
    }
    const double norm = std::sqrt(norm_squared);
    const double residual = std::sqrt(residual_squared);
    if (!std::isfinite(norm) || !std::isfinite(residual)) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::non_finite,
            "observable scale or Hermiticity residual overflowed");
    }
    if (residual > policy.relative_hermiticity_tolerance * norm) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::non_hermitian,
            "observable is not Hermitian relative to its scale");
    }
    return HermitianObservable(
        dimension, std::move(values), std::move(metadata), residual);
}

const Complex& HermitianObservable::at(
    const std::size_t row,
    const std::size_t column) const
{
    if (row >= dimension_ || column >= dimension_) {
        throw std::out_of_range("observable index is outside the matrix dimension");
    }
    return values_[row * dimension_ + column];
}

ObservableMoments observable_moments(
    const DensityState& state,
    const StateAnalysisMetadata& state_metadata,
    const HermitianObservable& observable,
    const UncertaintyValidationPolicy policy)
{
    validate_policy(policy);
    validate_pairing(state, state_metadata, observable);
    const auto squared = multiply(
        observable.values(), observable.values(), observable.dimension());
    const double expectation = require_real(
        trace_rho_times(state, observable.values()), policy,
        "Hermitian observable expectation has a material imaginary component");
    const double second_moment = require_real(
        trace_rho_times(state, squared), policy,
        "observable second moment has a material imaginary component");
    const double raw_variance = second_moment - expectation * expectation;
    const double variance = clamp_nonnegative(
        raw_variance,
        std::max(std::abs(second_moment), expectation * expectation),
        policy,
        "observable variance is materially negative");

    return ObservableMoments {
        state_metadata.revision,
        state_metadata.basis_id,
        state_metadata.source_id,
        state_metadata.unit,
        observable.metadata().source_id,
        observable.metadata().unit,
        expectation,
        variance,
        std::sqrt(variance),
    };
}

RobertsonSchrodingerResult robertson_schrodinger(
    const DensityState& state,
    const StateAnalysisMetadata& state_metadata,
    const HermitianObservable& observable_a,
    const HermitianObservable& observable_b,
    const UncertaintyValidationPolicy policy)
{
    validate_policy(policy);
    validate_pairing(state, state_metadata, observable_a);
    validate_pairing(state, state_metadata, observable_b);
    const auto a = observable_moments(state, state_metadata, observable_a, policy);
    const auto b = observable_moments(state, state_metadata, observable_b, policy);
    const auto ab = multiply(observable_a.values(), observable_b.values(), state.dimension());
    const auto ba = multiply(observable_b.values(), observable_a.values(), state.dimension());

    std::vector<Complex> anti_commutator(ab.size());
    std::vector<Complex> commutator(ab.size());
    for (std::size_t index = 0; index < ab.size(); ++index) {
        anti_commutator[index] = 0.5 * (ab[index] + ba[index]);
        commutator[index] = Complex {0.0, -0.5} * (ab[index] - ba[index]);
    }
    const double covariance = require_real(
        trace_rho_times(state, anti_commutator), policy,
        "symmetrized covariance term has a material imaginary component")
        - a.expectation * b.expectation;
    const double commutator_component = require_real(
        trace_rho_times(state, commutator), policy,
        "commutator component has a material imaginary component");
    const double lower_bound = covariance * covariance
        + commutator_component * commutator_component;
    const double variance_product = a.variance * b.variance;
    double slack = variance_product - lower_bound;
    if (!std::isfinite(covariance) || !std::isfinite(commutator_component)
        || !std::isfinite(lower_bound) || !std::isfinite(variance_product)
        || !std::isfinite(slack)) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::numerical_inconsistency,
            "Robertson-Schrodinger calculation produced a non-finite value");
    }
    const double scale = std::max(variance_product, lower_bound);
    if (slack < -policy.nonnegative_tolerance
            * std::max(scale, std::numeric_limits<double>::min())) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::numerical_inconsistency,
            "Robertson-Schrodinger inequality is materially violated by the inputs");
    }
    slack = std::max(0.0, slack);

    return RobertsonSchrodingerResult {
        state_metadata.revision,
        state_metadata.basis_id,
        state_metadata.source_id,
        state_metadata.unit,
        observable_a.metadata().source_id,
        observable_b.metadata().source_id,
        observable_a.metadata().unit,
        observable_b.metadata().unit,
        a,
        b,
        covariance,
        commutator_component,
        lower_bound,
        variance_product,
        slack,
    };
}

MandelstamTammCharacteristicTime mandelstam_tamm_characteristic_time(
    const double delta_observable,
    const double absolute_expectation_rate,
    const double delta_energy,
    const double hbar,
    MandelstamTammMetadata metadata)
{
    validate_mt_metadata(metadata);
    if (!std::isfinite(delta_observable) || !std::isfinite(absolute_expectation_rate)
        || !std::isfinite(delta_energy) || !std::isfinite(hbar)
        || delta_observable < 0.0 || absolute_expectation_rate < 0.0
        || delta_energy < 0.0 || !(hbar > 0.0)) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::invalid_mandelstam_tamm_input,
            "Mandelstam-Tamm inputs must be finite and nonnegative, with positive hbar");
    }

    MandelstamTammCharacteristicTime result {
        std::move(metadata),
        delta_observable,
        absolute_expectation_rate,
        delta_energy,
        hbar,
        std::nullopt,
        std::nullopt,
        0.5 * hbar,
        false,
    };
    if (absolute_expectation_rate == 0.0) {
        // No finite characteristic time is inferable from a stationary expectation.
        result.satisfies_bound = true;
        return result;
    }
    result.characteristic_time = delta_observable / absolute_expectation_rate;
    result.energy_time_product = delta_energy * *result.characteristic_time;
    if (!std::isfinite(*result.characteristic_time)
        || !std::isfinite(*result.energy_time_product)) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::invalid_mandelstam_tamm_input,
            "Mandelstam-Tamm inputs do not produce finite derived values");
    }
    const double tolerance = 1.0e-12 * std::max(result.lower_bound, *result.energy_time_product);
    result.satisfies_bound = *result.energy_time_product + tolerance >= result.lower_bound;
    return result;
}

MandelstamTammOrthogonalizationBound mandelstam_tamm_orthogonalization_bound(
    const double delta_energy,
    const double hbar,
    MandelstamTammMetadata metadata)
{
    validate_mt_metadata(metadata);
    if (!std::isfinite(delta_energy) || !std::isfinite(hbar)
        || delta_energy < 0.0 || !(hbar > 0.0)) {
        throw UncertaintyValidationError(
            UncertaintyValidationCode::invalid_mandelstam_tamm_input,
            "orthogonalization inputs require finite nonnegative Delta E and positive hbar");
    }
    MandelstamTammOrthogonalizationBound result {
        std::move(metadata), delta_energy, hbar, std::nullopt};
    if (delta_energy > 0.0) {
        result.minimum_time = std::numbers::pi * hbar / (2.0 * delta_energy);
        if (!std::isfinite(*result.minimum_time)) {
            throw UncertaintyValidationError(
                UncertaintyValidationCode::invalid_mandelstam_tamm_input,
                "orthogonalization inputs do not produce a finite derived bound");
        }
    }
    return result;
}

} // namespace qmw
