#include "qmw/qmm.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <limits>
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
        dimension >>= 1U;
        ++qubits;
    }
    return qubits;
}

[[nodiscard]] bool blank(const std::string& value)
{
    return value.empty() || std::all_of(
        value.begin(), value.end(), [](const unsigned char character) {
            return std::isspace(character) != 0;
        });
}

void validate_definition(
    const std::size_t dimension,
    const double hbar,
    const QmmMetadata& metadata,
    const QmmPolicy& policy)
{
    if (!is_power_of_two(dimension) || dimension > policy.maximum_dimension) {
        throw QmmError(
            QmmCode::invalid_dimension,
            "qmw.qmm dimension must be a nonzero power of two within the configured limit");
    }
    if (!std::isfinite(policy.relative_hermiticity_tolerance)
        || !std::isfinite(policy.density_hermiticity_tolerance)
        || !std::isfinite(policy.density_trace_tolerance)
        || !std::isfinite(policy.density_positivity_tolerance)
        || !(policy.relative_hermiticity_tolerance > 0.0)
        || !(policy.density_hermiticity_tolerance > 0.0)
        || !(policy.density_trace_tolerance > 0.0)
        || !(policy.density_positivity_tolerance > 0.0)
        || policy.maximum_dimension == 0) {
        throw QmmError(QmmCode::invalid_policy, "qmw.qmm validation policy is invalid");
    }
    if (!std::isfinite(hbar) || !(hbar > 0.0)) {
        throw QmmError(QmmCode::invalid_hbar, "hbar must be positive and finite");
    }
    if (blank(metadata.energy_unit) || blank(metadata.time_unit)
        || blank(metadata.operator_unit) || blank(metadata.basis_id)
        || blank(metadata.source_id) || blank(metadata.provenance)) {
        throw QmmError(
            QmmCode::invalid_metadata,
            "energy, time, operator, basis, source, and provenance metadata must be nonempty");
    }
}

[[nodiscard]] std::vector<QmmComplex> collect_matrix(
    const std::size_t dimension,
    QmmMatrixSplit split)
{
    const auto count = dimension * dimension;
    if (split.real.size() != count || split.imag.size() != count) {
        throw QmmError(
            QmmCode::wrong_element_count,
            "each real and imaginary matrix component must contain dimension squared values");
    }
    std::vector<QmmComplex> values;
    values.reserve(count);
    for (std::size_t index = 0; index < count; ++index) {
        if (!std::isfinite(split.real[index]) || !std::isfinite(split.imag[index])) {
            throw QmmError(QmmCode::non_finite, "matrix contains a non-finite value");
        }
        values.emplace_back(split.real[index], split.imag[index]);
    }
    return values;
}

[[nodiscard]] double frobenius_norm(const std::vector<QmmComplex>& values)
{
    double squared = 0.0;
    for (const auto value : values) {
        squared += std::norm(value);
    }
    return std::sqrt(squared);
}

[[nodiscard]] double hermiticity_residual(
    const std::vector<QmmComplex>& values,
    const std::size_t dimension)
{
    double squared = 0.0;
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            const auto error = values[row * dimension + column]
                - std::conj(values[column * dimension + row]);
            squared += std::norm(error);
        }
    }
    return std::sqrt(squared);
}

[[nodiscard]] double antihermiticity_residual(
    const std::vector<QmmComplex>& values,
    const std::size_t dimension)
{
    double squared = 0.0;
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            const auto error = values[row * dimension + column]
                + std::conj(values[column * dimension + row]);
            squared += std::norm(error);
        }
    }
    return std::sqrt(squared);
}

void require_hermitian(
    const std::vector<QmmComplex>& values,
    const std::size_t dimension,
    const double tolerance,
    const char* name)
{
    const double residual = hermiticity_residual(values, dimension);
    const double norm = frobenius_norm(values);
    if (residual > tolerance * norm) {
        throw QmmError(QmmCode::non_hermitian, std::string(name) + " is not Hermitian");
    }
}

[[nodiscard]] double validate_density(
    const std::vector<QmmComplex>& values,
    const std::size_t dimension,
    const QmmPolicy& policy,
    QmmComplex& trace)
{
    if (hermiticity_residual(values, dimension) > policy.density_hermiticity_tolerance) {
        throw QmmError(QmmCode::non_hermitian, "rho is not Hermitian");
    }
    trace = {};
    for (std::size_t index = 0; index < dimension; ++index) {
        trace += values[index * dimension + index];
    }
    if (std::abs(trace - QmmComplex {1.0, 0.0}) > policy.density_trace_tolerance) {
        throw QmmError(QmmCode::trace_not_one, "rho trace is not one");
    }

    std::vector<QmmComplex> lower(dimension * dimension, QmmComplex {});
    std::vector<double> diagonal(dimension, 0.0);
    double minimum_pivot = std::numeric_limits<double>::infinity();
    for (std::size_t column = 0; column < dimension; ++column) {
        double pivot = values[column * dimension + column].real();
        for (std::size_t prior = 0; prior < column; ++prior) {
            pivot -= std::norm(lower[column * dimension + prior]) * diagonal[prior];
        }
        minimum_pivot = std::min(minimum_pivot, pivot);
        if (pivot < -policy.density_positivity_tolerance) {
            throw QmmError(QmmCode::not_positive_semidefinite, "rho has a negative LDL^H pivot");
        }
        if (pivot < 0.0) {
            pivot = 0.0;
        }
        diagonal[column] = pivot;
        lower[column * dimension + column] = {1.0, 0.0};
        for (std::size_t row = column + 1; row < dimension; ++row) {
            auto residual = values[row * dimension + column];
            for (std::size_t prior = 0; prior < column; ++prior) {
                residual -= lower[row * dimension + prior] * diagonal[prior]
                    * std::conj(lower[column * dimension + prior]);
            }
            if (pivot == 0.0) {
                if (std::abs(residual) > policy.density_positivity_tolerance) {
                    throw QmmError(
                        QmmCode::not_positive_semidefinite,
                        "rho has a nonzero column below a zero LDL^H pivot");
                }
            } else {
                lower[row * dimension + column] = residual / pivot;
            }
        }
    }
    return minimum_pivot;
}

[[nodiscard]] std::vector<QmmComplex> multiply(
    const std::vector<QmmComplex>& left,
    const std::vector<QmmComplex>& right,
    const std::size_t dimension)
{
    std::vector<QmmComplex> output(dimension * dimension, QmmComplex {});
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t inner = 0; inner < dimension; ++inner) {
            const auto value = left[row * dimension + inner];
            for (std::size_t column = 0; column < dimension; ++column) {
                output[row * dimension + column] += value * right[inner * dimension + column];
            }
        }
    }
    return output;
}

[[nodiscard]] QmmComplex trace_product(
    const std::vector<QmmComplex>& left,
    const std::vector<QmmComplex>& right,
    const std::size_t dimension)
{
    QmmComplex trace {};
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            trace += left[row * dimension + column] * right[column * dimension + row];
        }
    }
    return trace;
}

} // namespace

std::string_view qmm_code_name(const QmmCode code) noexcept
{
    switch (code) {
    case QmmCode::invalid_policy: return "invalid_policy";
    case QmmCode::invalid_dimension: return "invalid_dimension";
    case QmmCode::wrong_element_count: return "wrong_element_count";
    case QmmCode::non_finite: return "non_finite";
    case QmmCode::non_hermitian: return "non_hermitian";
    case QmmCode::trace_not_one: return "trace_not_one";
    case QmmCode::not_positive_semidefinite: return "not_positive_semidefinite";
    case QmmCode::invalid_metadata: return "invalid_metadata";
    case QmmCode::invalid_hbar: return "invalid_hbar";
    case QmmCode::invalid_revision: return "invalid_revision";
    case QmmCode::stale_revision: return "stale_revision";
    case QmmCode::incomplete_transaction: return "incomplete_transaction";
    case QmmCode::partial_pair_incomplete: return "partial_pair_incomplete";
    case QmmCode::revision_mismatch: return "revision_mismatch";
    }
    return "unknown_qmm_error";
}

QmmError::QmmError(const QmmCode code, std::string message)
    : std::runtime_error(std::move(message))
    , code_(code)
{
}

QmmMatrix::QmmMatrix(const std::size_t dimension, std::vector<QmmComplex> values)
    : dimension_(dimension)
    , values_(std::move(values))
{
}

const QmmComplex& QmmMatrix::at(const std::size_t row, const std::size_t column) const
{
    if (row >= dimension_ || column >= dimension_) {
        throw std::out_of_range("qmw.qmm matrix index is outside the dimension");
    }
    return values_[row * dimension_ + column];
}

QmmSnapshot::QmmSnapshot(
    const long revision,
    const std::size_t dimension,
    const std::size_t qubits,
    const double hbar,
    QmmMetadata metadata,
    std::string hbar_unit,
    std::string derivative_unit,
    QmmMatrix hamiltonian,
    QmmMatrix density,
    QmmMatrix observable,
    std::optional<QmmMatrix> partial,
    QmmMatrix commutator,
    QmmMatrix derivative,
    const QmmComplex expectation_derivative,
    const QmmDiagnostics diagnostics)
    : revision_(revision)
    , dimension_(dimension)
    , qubits_(qubits)
    , hbar_(hbar)
    , metadata_(std::move(metadata))
    , hbar_unit_(std::move(hbar_unit))
    , derivative_unit_(std::move(derivative_unit))
    , hamiltonian_(std::move(hamiltonian))
    , density_(std::move(density))
    , observable_(std::move(observable))
    , partial_(std::move(partial))
    , commutator_(std::move(commutator))
    , derivative_(std::move(derivative))
    , expectation_derivative_(expectation_derivative)
    , diagnostics_(diagnostics)
{
}

QmmSnapshot QmmSnapshot::evaluate(
    const long revision,
    const std::size_t dimension,
    QmmMatrixSplit hamiltonian,
    QmmMatrixSplit density,
    QmmMatrixSplit observable,
    std::optional<QmmMatrixSplit> explicit_partial,
    const double hbar,
    QmmMetadata metadata,
    const QmmPolicy policy)
{
    validate_definition(dimension, hbar, metadata, policy);
    if (revision < 0) {
        throw QmmError(QmmCode::invalid_revision, "qmw.qmm revision must be nonnegative");
    }

    auto h_values = collect_matrix(dimension, std::move(hamiltonian));
    auto rho_values = collect_matrix(dimension, std::move(density));
    auto a_values = collect_matrix(dimension, std::move(observable));
    std::optional<std::vector<QmmComplex>> partial_values;
    if (explicit_partial.has_value()) {
        partial_values = collect_matrix(dimension, std::move(*explicit_partial));
    }

    require_hermitian(
        h_values, dimension, policy.relative_hermiticity_tolerance, "Hamiltonian");
    require_hermitian(
        a_values, dimension, policy.relative_hermiticity_tolerance, "observable");
    if (partial_values.has_value()) {
        require_hermitian(
            *partial_values,
            dimension,
            policy.relative_hermiticity_tolerance,
            "explicit partial derivative");
    }
    QmmComplex density_trace {};
    const double minimum_pivot = validate_density(
        rho_values, dimension, policy, density_trace);

    auto h_times_a = multiply(h_values, a_values, dimension);
    auto a_times_h = multiply(a_values, h_values, dimension);
    std::vector<QmmComplex> commutator(dimension * dimension);
    std::vector<QmmComplex> derivative(dimension * dimension);
    const QmmComplex i_over_hbar {0.0, 1.0 / hbar};
    for (std::size_t index = 0; index < commutator.size(); ++index) {
        commutator[index] = h_times_a[index] - a_times_h[index];
        derivative[index] = i_over_hbar * commutator[index]
            + (partial_values.has_value() ? (*partial_values)[index] : QmmComplex {});
        if (!std::isfinite(derivative[index].real())
            || !std::isfinite(derivative[index].imag())) {
            throw QmmError(QmmCode::non_finite, "Heisenberg derivative is non-finite");
        }
    }
    const auto expectation_derivative = trace_product(rho_values, derivative, dimension);

    const QmmDiagnostics diagnostics {
        hermiticity_residual(h_values, dimension),
        hermiticity_residual(a_values, dimension),
        partial_values.has_value() ? hermiticity_residual(*partial_values, dimension) : 0.0,
        frobenius_norm(commutator),
        antihermiticity_residual(commutator, dimension),
        hermiticity_residual(derivative, dimension),
        density_trace,
        minimum_pivot,
        std::abs(expectation_derivative.imag()),
    };

    std::optional<QmmMatrix> partial_matrix;
    if (partial_values.has_value()) {
        partial_matrix = QmmMatrix(dimension, std::move(*partial_values));
    }
    const std::string hbar_unit = metadata.energy_unit + "*" + metadata.time_unit;
    const std::string derivative_unit = metadata.operator_unit + "/" + metadata.time_unit;
    return QmmSnapshot(
        revision,
        dimension,
        exact_qubit_count(dimension),
        hbar,
        std::move(metadata),
        hbar_unit,
        derivative_unit,
        QmmMatrix(dimension, std::move(h_values)),
        QmmMatrix(dimension, std::move(rho_values)),
        QmmMatrix(dimension, std::move(a_values)),
        std::move(partial_matrix),
        QmmMatrix(dimension, std::move(commutator)),
        QmmMatrix(dimension, std::move(derivative)),
        expectation_derivative,
        diagnostics);
}

void RevisionedQmmStore::CandidatePart::clear() noexcept
{
    revision.reset();
    values.clear();
}

RevisionedQmmStore::RevisionedQmmStore(
    const std::size_t dimension,
    const double hbar,
    QmmMetadata metadata,
    const QmmPolicy policy)
    : dimension_(dimension)
    , element_count_(dimension * dimension)
    , hbar_(hbar)
    , metadata_(std::move(metadata))
    , policy_(policy)
{
    validate_definition(dimension_, hbar_, metadata_, policy_);
}

RevisionedQmmStore::CandidatePart& RevisionedQmmStore::candidate(const QmmPart part) noexcept
{
    switch (part) {
    case QmmPart::hamiltonian_real: return hamiltonian_real_;
    case QmmPart::hamiltonian_imag: return hamiltonian_imag_;
    case QmmPart::density_real: return density_real_;
    case QmmPart::density_imag: return density_imag_;
    case QmmPart::observable_real: return observable_real_;
    case QmmPart::observable_imag: return observable_imag_;
    case QmmPart::partial_real: return partial_real_;
    case QmmPart::partial_imag: return partial_imag_;
    }
    return hamiltonian_real_;
}

const RevisionedQmmStore::CandidatePart& RevisionedQmmStore::candidate(
    const QmmPart part) const noexcept
{
    return const_cast<RevisionedQmmStore*>(this)->candidate(part);
}

QmmStageResult RevisionedQmmStore::stage(
    const QmmPart part,
    const long revision,
    std::vector<double> values)
{
    if (revision < 0) {
        return {QmmStageStatus::rejected, revision, "invalid_revision", "revision must be nonnegative"};
    }
    if (revision <= active_revision_) {
        return {QmmStageStatus::rejected, revision, "stale_revision", "revision is not newer than active"};
    }
    if (values.size() != element_count_) {
        return {
            QmmStageStatus::rejected,
            revision,
            "wrong_element_count",
            "component does not contain dimension squared values",
        };
    }
    for (const double value : values) {
        if (!std::isfinite(value)) {
            return {QmmStageStatus::rejected, revision, "non_finite", "component is non-finite"};
        }
    }
    auto& target = candidate(part);
    target.revision = revision;
    target.values = std::move(values);
    return {QmmStageStatus::staged, revision, "staged", "candidate component staged"};
}

QmmStageResult RevisionedQmmStore::commit(const long revision)
{
    if (revision < 0) {
        return {QmmStageStatus::rejected, revision, "invalid_revision", "revision must be nonnegative"};
    }
    if (revision <= active_revision_) {
        return {QmmStageStatus::rejected, revision, "stale_revision", "revision is not newer than active"};
    }

    const std::array<QmmPart, 6> required {
        QmmPart::hamiltonian_real,
        QmmPart::hamiltonian_imag,
        QmmPart::density_real,
        QmmPart::density_imag,
        QmmPart::observable_real,
        QmmPart::observable_imag,
    };
    for (const auto part : required) {
        const auto& value = candidate(part);
        if (!value.revision.has_value()) {
            return {
                QmmStageStatus::rejected,
                revision,
                "incomplete_transaction",
                "one or more required matrix components are absent",
            };
        }
        if (*value.revision != revision) {
            return {
                QmmStageStatus::rejected,
                revision,
                "revision_mismatch",
                "required matrix components do not match the committed revision",
            };
        }
    }

    const bool has_partial_real = partial_real_.revision.has_value();
    const bool has_partial_imag = partial_imag_.revision.has_value();
    if (has_partial_real != has_partial_imag) {
        return {
            QmmStageStatus::rejected,
            revision,
            "partial_pair_incomplete",
            "explicit partial derivative requires both real and imaginary components",
        };
    }
    if (has_partial_real
        && (*partial_real_.revision != revision || *partial_imag_.revision != revision)) {
        return {
            QmmStageStatus::rejected,
            revision,
            "revision_mismatch",
            "partial derivative components do not match the committed revision",
        };
    }

    try {
        std::optional<QmmMatrixSplit> partial;
        if (has_partial_real) {
            partial = QmmMatrixSplit {partial_real_.values, partial_imag_.values};
        }
        auto snapshot = QmmSnapshot::evaluate(
            revision,
            dimension_,
            {hamiltonian_real_.values, hamiltonian_imag_.values},
            {density_real_.values, density_imag_.values},
            {observable_real_.values, observable_imag_.values},
            std::move(partial),
            hbar_,
            metadata_,
            policy_);
        active_ = std::make_unique<QmmSnapshot>(std::move(snapshot));
        active_revision_ = revision;
        clear_candidate();
        return {QmmStageStatus::accepted, revision, "accepted", "qmw.qmm transaction accepted"};
    } catch (const QmmError& error) {
        const std::string detail(qmm_code_name(error.code()));
        const std::string message(error.what());
        clear_candidate();
        return {QmmStageStatus::rejected, revision, detail, message};
    }
}

void RevisionedQmmStore::clear_candidate() noexcept
{
    hamiltonian_real_.clear();
    hamiltonian_imag_.clear();
    density_real_.clear();
    density_imag_.clear();
    observable_real_.clear();
    observable_imag_.clear();
    partial_real_.clear();
    partial_imag_.clear();
}

} // namespace qmw
