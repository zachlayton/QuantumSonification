#include "qmw/pauli.hpp"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <limits>
#include <sstream>
#include <utility>

namespace qmw {
namespace {

[[nodiscard]] bool is_power_of_two(const std::size_t value) noexcept
{
    return value != 0 && (value & (value - 1)) == 0;
}

[[nodiscard]] std::size_t qubit_count(std::size_t dimension) noexcept
{
    std::size_t qubits = 0;
    while (dimension > 1) {
        dimension >>= 1;
        ++qubits;
    }
    return qubits;
}

[[nodiscard]] bool nonblank(const std::string& value) noexcept
{
    return std::any_of(value.begin(), value.end(), [](const unsigned char character) {
        return !std::isspace(character);
    });
}

[[nodiscard]] bool valid_axis(const PauliAxis axis) noexcept
{
    switch (axis) {
    case PauliAxis::x:
    case PauliAxis::y:
    case PauliAxis::z:
        return true;
    }
    return false;
}

[[nodiscard]] char axis_character(const PauliAxis axis)
{
    switch (axis) {
    case PauliAxis::x: return 'X';
    case PauliAxis::y: return 'Y';
    case PauliAxis::z: return 'Z';
    }
    throw PauliValidationError(PauliValidationCode::invalid_axis, "invalid Pauli axis");
}

[[nodiscard]] PauliDiagnostics compute_diagnostics(
    const std::size_t dimension,
    const std::vector<PauliComplex>& values)
{
    PauliDiagnostics result;
    double frobenius_squared = 0.0;
    double hermiticity_squared = 0.0;
    for (std::size_t row = 0; row < dimension; ++row) {
        result.trace += values[row * dimension + row];
        for (std::size_t column = 0; column < dimension; ++column) {
            const auto value = values[row * dimension + column];
            frobenius_squared += std::norm(value);
            hermiticity_squared += std::norm(
                value - std::conj(values[column * dimension + row]));
        }
    }
    result.frobenius_norm = std::sqrt(frobenius_squared);
    result.hermiticity_residual_fro = std::sqrt(hermiticity_squared);

    double unitarity_squared = 0.0;
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            PauliComplex element {};
            for (std::size_t inner = 0; inner < dimension; ++inner) {
                element += std::conj(values[inner * dimension + row])
                    * values[inner * dimension + column];
            }
            if (row == column) {
                element -= 1.0;
            }
            unitarity_squared += std::norm(element);
        }
    }
    result.unitarity_residual_fro = std::sqrt(unitarity_squared);
    return result;
}

void validate_dimension(const std::size_t dimension)
{
    if (!is_power_of_two(dimension) || dimension > 64
        || dimension > std::numeric_limits<std::size_t>::max() / dimension) {
        throw PauliValidationError(
            PauliValidationCode::invalid_dimension,
            "Pauli dimension must be a power of two no greater than 64");
    }
}

void validate_metadata(const PauliMetadata& metadata)
{
    if (!nonblank(metadata.basis_id) || !nonblank(metadata.source_id)
        || !nonblank(metadata.provenance) || !nonblank(metadata.operator_unit)) {
        throw PauliValidationError(
            PauliValidationCode::invalid_metadata,
            "Pauli metadata fields must be nonblank");
    }
}

} // namespace

std::string_view pauli_validation_code_name(const PauliValidationCode code) noexcept
{
    switch (code) {
    case PauliValidationCode::invalid_dimension: return "invalid_dimension";
    case PauliValidationCode::invalid_revision: return "invalid_revision";
    case PauliValidationCode::stale_revision: return "stale_revision";
    case PauliValidationCode::invalid_axis: return "invalid_axis";
    case PauliValidationCode::invalid_qubit: return "invalid_qubit";
    case PauliValidationCode::duplicate_qubit: return "duplicate_qubit";
    case PauliValidationCode::empty_product: return "empty_product";
    case PauliValidationCode::invalid_metadata: return "invalid_metadata";
    }
    return "unknown";
}

PauliValidationError::PauliValidationError(
    const PauliValidationCode code,
    const char* message)
    : std::runtime_error(message)
    , code_(code)
{
}

PauliSnapshot PauliSnapshot::identity(
    const std::size_t dimension,
    PauliMetadata metadata)
{
    validate_dimension(dimension);
    validate_metadata(metadata);
    std::vector<PauliComplex> values(dimension * dimension);
    for (std::size_t index = 0; index < dimension; ++index) {
        values[index * dimension + index] = 1.0;
    }
    auto computed = compute_diagnostics(dimension, values);
    return PauliSnapshot(
        dimension,
        qubit_count(dimension),
        std::move(values),
        {},
        "I",
        std::move(metadata),
        computed);
}

PauliSnapshot PauliSnapshot::product(
    const std::size_t dimension,
    std::vector<PauliFactor> factors,
    PauliMetadata metadata)
{
    validate_dimension(dimension);
    validate_metadata(metadata);
    if (factors.empty()) {
        throw PauliValidationError(
            PauliValidationCode::empty_product,
            "Pauli product requires at least one explicit factor");
    }
    const auto qubits = qubit_count(dimension);
    std::sort(factors.begin(), factors.end(), [](const auto& left, const auto& right) {
        return left.qubit < right.qubit;
    });
    for (std::size_t index = 0; index < factors.size(); ++index) {
        if (!valid_axis(factors[index].axis)) {
            throw PauliValidationError(
                PauliValidationCode::invalid_axis,
                "Pauli factor axis must be X, Y, or Z");
        }
        if (factors[index].qubit >= qubits) {
            throw PauliValidationError(
                PauliValidationCode::invalid_qubit,
                "Pauli factor target is outside the declared register");
        }
        if (index > 0 && factors[index - 1].qubit == factors[index].qubit) {
            throw PauliValidationError(
                PauliValidationCode::duplicate_qubit,
                "Pauli product may contain at most one factor per qubit");
        }
    }

    std::ostringstream label;
    for (std::size_t index = 0; index < factors.size(); ++index) {
        if (index != 0) label << '_';
        label << axis_character(factors[index].axis) << factors[index].qubit;
    }

    std::vector<PauliComplex> values(dimension * dimension);
    for (std::size_t column = 0; column < dimension; ++column) {
        std::size_t row = column;
        PauliComplex coefficient {1.0, 0.0};
        for (const auto& factor : factors) {
            const bool bit = ((column >> factor.qubit) & std::size_t {1}) != 0;
            switch (factor.axis) {
            case PauliAxis::x:
                row ^= std::size_t {1} << factor.qubit;
                break;
            case PauliAxis::y:
                row ^= std::size_t {1} << factor.qubit;
                coefficient *= bit ? PauliComplex {0.0, -1.0} : PauliComplex {0.0, 1.0};
                break;
            case PauliAxis::z:
                if (bit) coefficient = -coefficient;
                break;
            }
        }
        values[row * dimension + column] = coefficient;
    }
    auto computed = compute_diagnostics(dimension, values);
    return PauliSnapshot(
        dimension,
        qubits,
        std::move(values),
        std::move(factors),
        label.str(),
        std::move(metadata),
        computed);
}

PauliSnapshot::PauliSnapshot(
    const std::size_t dimension,
    const std::size_t qubits,
    std::vector<PauliComplex> values,
    std::vector<PauliFactor> factors,
    std::string label,
    PauliMetadata metadata,
    PauliDiagnostics diagnostics_value)
    : dimension_(dimension)
    , qubits_(qubits)
    , values_(std::move(values))
    , factors_(std::move(factors))
    , label_(std::move(label))
    , metadata_(std::move(metadata))
    , diagnostics_(diagnostics_value)
{
}

const PauliComplex& PauliSnapshot::at(
    const std::size_t row,
    const std::size_t column) const
{
    if (row >= dimension_ || column >= dimension_) {
        throw std::out_of_range("Pauli matrix index is out of range");
    }
    return values_[row * dimension_ + column];
}

RevisionedPauliStore::RevisionedPauliStore(
    const std::size_t dimension,
    PauliMetadata metadata)
    : dimension_(dimension)
    , qubits_(qubit_count(dimension))
    , metadata_(std::move(metadata))
{
    validate_dimension(dimension_);
    validate_metadata(metadata_);
}

PauliInstallResult RevisionedPauliStore::install_identity(const long revision)
{
    if (revision < 0) {
        return {PauliInstallStatus::rejected, revision, "invalid_revision", "revision must be nonnegative"};
    }
    if (revision <= active_revision_) {
        return {PauliInstallStatus::rejected, revision, "stale_revision", "revision must increase"};
    }
    return install(revision, PauliSnapshot::identity(dimension_, metadata_));
}

PauliInstallResult RevisionedPauliStore::install_product(
    const long revision,
    std::vector<PauliFactor> factors)
{
    if (revision < 0) {
        return {PauliInstallStatus::rejected, revision, "invalid_revision", "revision must be nonnegative"};
    }
    if (revision <= active_revision_) {
        return {PauliInstallStatus::rejected, revision, "stale_revision", "revision must increase"};
    }
    try {
        return install(
            revision,
            PauliSnapshot::product(dimension_, std::move(factors), metadata_));
    } catch (const PauliValidationError& error) {
        return {
            PauliInstallStatus::rejected,
            revision,
            std::string(pauli_validation_code_name(error.code())),
            error.what(),
        };
    }
}

PauliInstallResult RevisionedPauliStore::install(
    const long revision,
    PauliSnapshot snapshot)
{
    active_ = std::make_unique<PauliSnapshot>(std::move(snapshot));
    active_revision_ = revision;
    return {PauliInstallStatus::accepted, revision, "accepted", "accepted"};
}

} // namespace qmw
