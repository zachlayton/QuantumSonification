#include "qmw/hamiltonian.hpp"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <utility>

namespace qmw {
namespace {

[[nodiscard]] bool is_power_of_two(const std::size_t value) noexcept
{
    return value != 0 && (value & (value - 1)) == 0;
}

[[nodiscard]] std::size_t exact_qubit_count(std::size_t dimension) noexcept
{
    std::size_t qubits = 0;
    while (dimension > 1) {
        dimension >>= 1;
        ++qubits;
    }
    return qubits;
}

[[nodiscard]] bool blank(const std::string& value)
{
    return value.empty() || std::all_of(
        value.begin(),
        value.end(),
        [](const unsigned char character) { return std::isspace(character) != 0; });
}

void validate_definition(
    const std::size_t dimension,
    const HamiltonianMetadata& metadata,
    const HamiltonianValidationPolicy policy)
{
    if (!is_power_of_two(dimension) || dimension > policy.maximum_dimension) {
        throw HamiltonianValidationError(
            HamiltonianValidationCode::invalid_dimension,
            "Hamiltonian dimension must be a nonzero power of two within the configured limit");
    }
    if (!std::isfinite(policy.relative_hermiticity_tolerance)
        || !(policy.relative_hermiticity_tolerance > 0.0)
        || policy.maximum_dimension == 0) {
        throw HamiltonianValidationError(
            HamiltonianValidationCode::invalid_policy,
            "Hamiltonian validation policy must have a positive finite tolerance and dimension limit");
    }
    if (blank(metadata.energy_unit) || blank(metadata.basis_id)
        || blank(metadata.source_id) || blank(metadata.provenance)) {
        throw HamiltonianValidationError(
            HamiltonianValidationCode::invalid_metadata,
            "Hamiltonian energy unit, basis, source, and provenance must be nonempty");
    }
}

} // namespace

std::string_view hamiltonian_validation_code_name(
    const HamiltonianValidationCode code) noexcept
{
    switch (code) {
    case HamiltonianValidationCode::invalid_dimension:
        return "invalid_dimension";
    case HamiltonianValidationCode::wrong_element_count:
        return "wrong_element_count";
    case HamiltonianValidationCode::non_finite:
        return "non_finite";
    case HamiltonianValidationCode::non_hermitian:
        return "non_hermitian";
    case HamiltonianValidationCode::invalid_metadata:
        return "invalid_metadata";
    case HamiltonianValidationCode::invalid_policy:
        return "invalid_policy";
    }
    return "unknown_hamiltonian_validation_error";
}

HamiltonianValidationError::HamiltonianValidationError(
    const HamiltonianValidationCode code,
    const char* message)
    : std::runtime_error(message)
    , code_(code)
{
}

HamiltonianSnapshot::HamiltonianSnapshot(
    const std::size_t dimension,
    const std::size_t qubits,
    std::vector<HamiltonianComplex> values,
    HamiltonianMetadata metadata,
    const HamiltonianDiagnostics diagnostics)
    : dimension_(dimension)
    , qubits_(qubits)
    , values_(std::move(values))
    , metadata_(std::move(metadata))
    , diagnostics_(diagnostics)
{
}

HamiltonianSnapshot HamiltonianSnapshot::from_split(
    const std::size_t dimension,
    const std::vector<double>& real,
    const std::vector<double>& imag,
    HamiltonianMetadata metadata,
    const HamiltonianValidationPolicy policy)
{
    validate_definition(dimension, metadata, policy);
    const auto element_count = dimension * dimension;
    if (real.size() != element_count || imag.size() != element_count) {
        throw HamiltonianValidationError(
            HamiltonianValidationCode::wrong_element_count,
            "Hamiltonian real and imaginary parts must each contain dimension squared values");
    }

    std::vector<HamiltonianComplex> values;
    values.reserve(element_count);
    double norm_squared = 0.0;
    double maximum_absolute_element = 0.0;
    HamiltonianComplex trace {};
    for (std::size_t index = 0; index < element_count; ++index) {
        const HamiltonianComplex value {real[index], imag[index]};
        if (!std::isfinite(value.real()) || !std::isfinite(value.imag())) {
            throw HamiltonianValidationError(
                HamiltonianValidationCode::non_finite,
                "Hamiltonian contains a non-finite value");
        }
        norm_squared += std::norm(value);
        maximum_absolute_element = std::max(maximum_absolute_element, std::abs(value));
        if (index / dimension == index % dimension) {
            trace += value;
        }
        values.push_back(value);
    }

    double residual_squared = 0.0;
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            const auto error = values[row * dimension + column]
                - std::conj(values[column * dimension + row]);
            residual_squared += std::norm(error);
        }
    }
    const double frobenius_norm = std::sqrt(norm_squared);
    const double residual = std::sqrt(residual_squared);
    const double relative_residual = frobenius_norm == 0.0
        ? 0.0
        : residual / frobenius_norm;
    if (residual > policy.relative_hermiticity_tolerance * frobenius_norm) {
        throw HamiltonianValidationError(
            HamiltonianValidationCode::non_hermitian,
            "Hamiltonian is not Hermitian relative to its energy scale");
    }

    return HamiltonianSnapshot(
        dimension,
        exact_qubit_count(dimension),
        std::move(values),
        std::move(metadata),
        HamiltonianDiagnostics {
            trace,
            frobenius_norm,
            maximum_absolute_element,
            residual,
            relative_residual,
        });
}

const HamiltonianComplex& HamiltonianSnapshot::at(
    const std::size_t row,
    const std::size_t column) const
{
    if (row >= dimension_ || column >= dimension_) {
        throw std::out_of_range("Hamiltonian index is outside the matrix dimension");
    }
    return values_[row * dimension_ + column];
}

void RevisionedHamiltonianStore::CandidatePart::clear() noexcept
{
    revision.reset();
    values.clear();
}

RevisionedHamiltonianStore::RevisionedHamiltonianStore(
    const std::size_t dimension,
    HamiltonianMetadata metadata,
    const HamiltonianValidationPolicy policy)
    : dimension_(dimension)
    , qubits_(is_power_of_two(dimension) ? exact_qubit_count(dimension) : 0)
    , element_count_(dimension * dimension)
    , metadata_(std::move(metadata))
    , policy_(policy)
{
    validate_definition(dimension_, metadata_, policy_);
}

HamiltonianStageResult RevisionedHamiltonianStore::stage(
    const HamiltonianPart part,
    const long revision,
    std::vector<double> values)
{
    if (revision < 0 || revision <= active_revision_) {
        return {
            HamiltonianStageStatus::rejected,
            revision,
            "stale_revision",
            "revision is not newer than the active Hamiltonian",
        };
    }
    if (values.size() != element_count_) {
        return {
            HamiltonianStageStatus::rejected,
            revision,
            "wrong_element_count",
            "component does not contain dimension squared values",
        };
    }
    for (const double value : values) {
        if (!std::isfinite(value)) {
            return {
                HamiltonianStageStatus::rejected,
                revision,
                "non_finite",
                "component contains a non-finite value",
            };
        }
    }

    auto& target = part == HamiltonianPart::real ? real_ : imag_;
    target.revision = revision;
    target.values = std::move(values);

    if (!real_.revision.has_value() || !imag_.revision.has_value()
        || *real_.revision != *imag_.revision) {
        return {
            HamiltonianStageStatus::staged,
            revision,
            part == HamiltonianPart::real ? "real" : "imag",
            "candidate Hamiltonian component staged",
        };
    }

    try {
        auto snapshot = HamiltonianSnapshot::from_split(
            dimension_, real_.values, imag_.values, metadata_, policy_);
        active_ = std::make_unique<HamiltonianSnapshot>(std::move(snapshot));
        active_revision_ = revision;
        clear_candidate();
        return {
            HamiltonianStageStatus::accepted,
            revision,
            "accepted",
            "complete Hamiltonian revision accepted",
        };
    } catch (const HamiltonianValidationError& error) {
        const std::string detail(hamiltonian_validation_code_name(error.code()));
        const std::string message(error.what());
        clear_candidate();
        return {HamiltonianStageStatus::rejected, revision, detail, message};
    }
}

void RevisionedHamiltonianStore::clear_candidate() noexcept
{
    real_.clear();
    imag_.clear();
}

} // namespace qmw
