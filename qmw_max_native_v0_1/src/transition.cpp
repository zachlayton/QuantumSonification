#include "qmw/transition.hpp"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <limits>
#include <numeric>
#include <utility>

namespace qmw {
namespace {

[[nodiscard]] bool blank(const std::string& value)
{
    return value.empty() || std::all_of(
        value.begin(), value.end(),
        [](const unsigned char character) { return std::isspace(character) != 0; });
}

[[nodiscard]] bool finite(const Complex value) noexcept
{
    return std::isfinite(value.real()) && std::isfinite(value.imag());
}

[[nodiscard]] bool finite_matrix(const std::vector<Complex>& values) noexcept
{
    return std::all_of(values.begin(), values.end(), [](const Complex value) {
        return finite(value);
    });
}

[[nodiscard]] double frobenius_norm(const std::vector<Complex>& values)
{
    double squared = 0.0;
    for (const auto value : values) {
        squared += std::norm(value);
    }
    return std::sqrt(squared);
}

[[nodiscard]] double matrix_hermiticity_residual_fro(
    const std::vector<Complex>& values,
    const std::size_t dimension)
{
    double squared = 0.0;
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            squared += std::norm(
                values[row * dimension + column]
                - std::conj(values[column * dimension + row]));
        }
    }
    return std::sqrt(squared);
}

[[nodiscard]] std::vector<Complex> identity(const std::size_t dimension)
{
    std::vector<Complex> result(dimension * dimension, Complex {});
    for (std::size_t index = 0; index < dimension; ++index) {
        result[index * dimension + index] = Complex {1.0, 0.0};
    }
    return result;
}

[[nodiscard]] std::vector<Complex> multiply(
    const std::vector<Complex>& left,
    const std::vector<Complex>& right,
    const std::size_t dimension)
{
    std::vector<Complex> result(dimension * dimension, Complex {});
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t inner = 0; inner < dimension; ++inner) {
            const auto coefficient = left[row * dimension + inner];
            for (std::size_t column = 0; column < dimension; ++column) {
                result[row * dimension + column]
                    += coefficient * right[inner * dimension + column];
            }
        }
    }
    return result;
}

[[nodiscard]] std::vector<Complex> adjoint(const std::vector<Complex>& matrix,
                                            const std::size_t dimension)
{
    std::vector<Complex> result(matrix.size());
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            result[row * dimension + column]
                = std::conj(matrix[column * dimension + row]);
        }
    }
    return result;
}

[[nodiscard]] std::vector<Complex> transform_into_basis(
    const std::vector<Complex>& matrix,
    const std::vector<Complex>& basis,
    const std::size_t dimension)
{
    return multiply(adjoint(basis, dimension), multiply(matrix, basis, dimension), dimension);
}

[[nodiscard]] double difference_norm(
    const std::vector<Complex>& left,
    const std::vector<Complex>& right)
{
    double squared = 0.0;
    for (std::size_t index = 0; index < left.size(); ++index) {
        squared += std::norm(left[index] - right[index]);
    }
    return std::sqrt(squared);
}

[[nodiscard]] std::vector<Complex> lower_triangle_hermitian_copy(
    const std::vector<Complex>& raw,
    const std::size_t dimension)
{
    std::vector<Complex> result(raw.size(), Complex {});
    for (std::size_t row = 0; row < dimension; ++row) {
        result[row * dimension + row] = Complex {raw[row * dimension + row].real(), 0.0};
        for (std::size_t column = 0; column < row; ++column) {
            const auto value = raw[row * dimension + column];
            result[row * dimension + column] = value;
            result[column * dimension + row] = std::conj(value);
        }
    }
    return result;
}

void validate_policy(const TransitionPolicy& policy)
{
    if (!std::isfinite(policy.relative_hermiticity_tolerance)
        || !std::isfinite(policy.eigensolver_tolerance)
        || !std::isfinite(policy.energy_gap_tolerance)
        || !std::isfinite(policy.amplitude_threshold)
        || !std::isfinite(policy.activity_threshold)
        || !(policy.relative_hermiticity_tolerance > 0.0)
        || !(policy.eigensolver_tolerance > 0.0)
        || policy.energy_gap_tolerance < 0.0
        || policy.amplitude_threshold < 0.0
        || policy.activity_threshold < 0.0
        || policy.maximum_dimension == 0
        || policy.maximum_jacobi_iterations_per_element == 0) {
        throw TransitionValidationError(
            TransitionValidationCode::invalid_policy,
            "transition tolerances, thresholds, dimension, and iteration bound are invalid");
    }
}

void validate_units(const TransitionUnits& units)
{
    if (!std::isfinite(units.hbar) || !(units.hbar > 0.0)
        || blank(units.energy_unit) || blank(units.time_unit)
        || blank(units.operator_unit)) {
        throw TransitionValidationError(
            TransitionValidationCode::invalid_metadata,
            "transition units require positive finite hbar and nonempty names");
    }
}

void validate_context(const TransitionContext& context)
{
    if (context.revision < 0 || !std::isfinite(context.time)
        || !std::isfinite(context.dt) || context.dt < 0.0
        || blank(context.basis_id) || blank(context.time_unit)
        || blank(context.source_id) || blank(context.provenance)) {
        throw TransitionValidationError(
            TransitionValidationCode::invalid_metadata,
            "context requires revision, finite time/dt, basis, time unit, source, and provenance");
    }
}

void validate_operator_metadata(
    const TransitionOperatorMetadata& metadata,
    const bool allow_unset_revision = false)
{
    if ((!allow_unset_revision && metadata.revision < 0)
        || blank(metadata.basis_id) || blank(metadata.unit)
        || blank(metadata.source_id) || blank(metadata.provenance)) {
        throw TransitionValidationError(
            TransitionValidationCode::invalid_metadata,
            "operator requires revision, basis, unit, source, and provenance");
    }
}

[[nodiscard]] HermitianEigensystem hermitian_eigensystem(
    const std::vector<Complex>& raw,
    const std::size_t dimension,
    const TransitionPolicy& policy)
{
    auto matrix = lower_triangle_hermitian_copy(raw, dimension);
    const auto analysis_input = matrix;
    auto vectors = identity(dimension);
    const double scale = frobenius_norm(matrix);
    const double threshold = policy.eigensolver_tolerance * scale;
    const auto maximum_iterations = policy.maximum_jacobi_iterations_per_element
        * dimension * dimension;
    std::size_t iterations = 0;
    double maximum_off_diagonal = 0.0;

    for (; iterations < maximum_iterations; ++iterations) {
        std::size_t p = 0;
        std::size_t q = 0;
        maximum_off_diagonal = 0.0;
        for (std::size_t row = 0; row < dimension; ++row) {
            for (std::size_t column = row + 1; column < dimension; ++column) {
                const double magnitude = std::abs(matrix[row * dimension + column]);
                if (magnitude > maximum_off_diagonal) {
                    maximum_off_diagonal = magnitude;
                    p = row;
                    q = column;
                }
            }
        }
        if (maximum_off_diagonal <= threshold || maximum_off_diagonal == 0.0) {
            break;
        }

        const double a = matrix[p * dimension + p].real();
        const double d = matrix[q * dimension + q].real();
        const Complex b = matrix[p * dimension + q];
        const double magnitude = std::abs(b);
        const double tau = (d - a) / (2.0 * magnitude);
        const double t = tau >= 0.0
            ? 1.0 / (tau + std::hypot(1.0, tau))
            : -1.0 / (-tau + std::hypot(1.0, tau));
        const double cosine = 1.0 / std::hypot(1.0, t);
        const double sine = t * cosine;
        const Complex phase = b / magnitude;
        if (!std::isfinite(t) || !std::isfinite(cosine)
            || !std::isfinite(sine) || !finite(phase)) {
            throw TransitionValidationError(
                TransitionValidationCode::eigensolver_failed,
                "Hermitian Jacobi rotation could not form finite parameters");
        }
        // First remove arg(b) with D=diag(1,exp(-i arg(b))), then apply the
        // stable real Jacobi rotation [[c,s],[-s,c]]. This avoids the loss of
        // precision in eigenvector formulas containing lambda-a.
        const Complex g00 {cosine, 0.0};
        const Complex g01 {sine, 0.0};
        const Complex g10 = -std::conj(phase) * sine;
        const Complex g11 = std::conj(phase) * cosine;

        auto temporary = matrix;
        for (std::size_t row = 0; row < dimension; ++row) {
            temporary[row * dimension + p]
                = matrix[row * dimension + p] * g00
                + matrix[row * dimension + q] * g10;
            temporary[row * dimension + q]
                = matrix[row * dimension + p] * g01
                + matrix[row * dimension + q] * g11;
        }
        auto rotated = temporary;
        for (std::size_t column = 0; column < dimension; ++column) {
            rotated[p * dimension + column]
                = std::conj(g00) * temporary[p * dimension + column]
                + std::conj(g10) * temporary[q * dimension + column];
            rotated[q * dimension + column]
                = std::conj(g01) * temporary[p * dimension + column]
                + std::conj(g11) * temporary[q * dimension + column];
        }
        matrix = std::move(rotated);
        matrix[p * dimension + q] = Complex {};
        matrix[q * dimension + p] = Complex {};
        matrix[p * dimension + p] = Complex {matrix[p * dimension + p].real(), 0.0};
        matrix[q * dimension + q] = Complex {matrix[q * dimension + q].real(), 0.0};

        for (std::size_t row = 0; row < dimension; ++row) {
            const auto old_p = vectors[row * dimension + p];
            const auto old_q = vectors[row * dimension + q];
            vectors[row * dimension + p] = old_p * g00 + old_q * g10;
            vectors[row * dimension + q] = old_p * g01 + old_q * g11;
        }
    }

    if (iterations == maximum_iterations && maximum_off_diagonal > threshold) {
        throw TransitionValidationError(
            TransitionValidationCode::eigensolver_failed,
            "bounded Hermitian Jacobi eigensolver did not converge");
    }

    std::vector<std::size_t> order(dimension);
    std::iota(order.begin(), order.end(), std::size_t {});
    std::stable_sort(order.begin(), order.end(), [&](const auto left, const auto right) {
        return matrix[left * dimension + left].real()
            < matrix[right * dimension + right].real();
    });
    std::vector<double> eigenvalues(dimension);
    std::vector<Complex> sorted_vectors(vectors.size());
    for (std::size_t column = 0; column < dimension; ++column) {
        eigenvalues[column] = matrix[order[column] * dimension + order[column]].real();
        for (std::size_t row = 0; row < dimension; ++row) {
            sorted_vectors[row * dimension + column]
                = vectors[row * dimension + order[column]];
        }
    }

    std::vector<Complex> diagonal(matrix.size(), Complex {});
    for (std::size_t index = 0; index < dimension; ++index) {
        diagonal[index * dimension + index] = Complex {eigenvalues[index], 0.0};
    }
    const auto reconstructed = multiply(
        multiply(sorted_vectors, diagonal, dimension),
        adjoint(sorted_vectors, dimension),
        dimension);
    const auto applied = multiply(analysis_input, sorted_vectors, dimension);
    auto scaled_vectors = sorted_vectors;
    for (std::size_t column = 0; column < dimension; ++column) {
        for (std::size_t row = 0; row < dimension; ++row) {
            scaled_vectors[row * dimension + column] *= eigenvalues[column];
        }
    }
    const double eigen_residual = difference_norm(applied, scaled_vectors);
    const double reconstruction_residual = difference_norm(reconstructed, analysis_input);
    if (!finite_matrix(sorted_vectors)
        || !std::all_of(eigenvalues.begin(), eigenvalues.end(), [](const double value) {
            return std::isfinite(value);
        })
        || !std::isfinite(eigen_residual) || !std::isfinite(reconstruction_residual)) {
        throw TransitionValidationError(
            TransitionValidationCode::eigensolver_failed,
            "Hermitian eigensolver produced a non-finite result");
    }
    const double admitted_residual = 32.0 * policy.eigensolver_tolerance
        * std::max(scale, std::numeric_limits<double>::min());
    if (eigen_residual > admitted_residual || reconstruction_residual > admitted_residual) {
        throw TransitionValidationError(
            TransitionValidationCode::eigensolver_failed,
            "Hermitian eigensolver residual exceeds the configured tolerance");
    }
    return {
        std::move(eigenvalues),
        std::move(sorted_vectors),
        iterations,
        maximum_off_diagonal,
        eigen_residual,
        reconstruction_residual,
    };
}

} // namespace

std::string_view transition_validation_code_name(
    const TransitionValidationCode code) noexcept
{
    switch (code) {
    case TransitionValidationCode::invalid_dimension: return "invalid_dimension";
    case TransitionValidationCode::wrong_element_count: return "wrong_element_count";
    case TransitionValidationCode::non_finite: return "non_finite";
    case TransitionValidationCode::non_hermitian: return "non_hermitian";
    case TransitionValidationCode::invalid_metadata: return "invalid_metadata";
    case TransitionValidationCode::invalid_policy: return "invalid_policy";
    case TransitionValidationCode::dimension_mismatch: return "dimension_mismatch";
    case TransitionValidationCode::basis_mismatch: return "basis_mismatch";
    case TransitionValidationCode::revision_mismatch: return "revision_mismatch";
    case TransitionValidationCode::time_unit_mismatch: return "time_unit_mismatch";
    case TransitionValidationCode::eigensolver_failed: return "eigensolver_failed";
    case TransitionValidationCode::numerical_inconsistency: return "numerical_inconsistency";
    }
    return "unknown_transition_validation_error";
}

TransitionValidationError::TransitionValidationError(
    const TransitionValidationCode code,
    std::string message)
    : std::runtime_error(std::move(message))
    , code_(code)
{
}

std::string_view transition_operator_kind_name(const TransitionOperatorKind kind) noexcept
{
    return kind == TransitionOperatorKind::observable ? "observable" : "coupling";
}

TransitionOperator::TransitionOperator(
    const std::size_t dimension,
    std::vector<Complex> values,
    TransitionOperatorMetadata metadata,
    const double hermiticity_residual_fro)
    : dimension_(dimension)
    , values_(std::move(values))
    , metadata_(std::move(metadata))
    , hermiticity_residual_fro_(hermiticity_residual_fro)
{
}

TransitionOperator TransitionOperator::from_split(
    const std::size_t dimension,
    const std::vector<double>& real,
    const std::vector<double>& imag,
    TransitionOperatorMetadata metadata,
    const TransitionPolicy policy)
{
    validate_policy(policy);
    validate_operator_metadata(metadata);
    if (dimension == 0 || dimension > policy.maximum_dimension) {
        throw TransitionValidationError(
            TransitionValidationCode::invalid_dimension,
            "operator dimension is zero or exceeds the configured limit");
    }
    const auto element_count = dimension * dimension;
    if (real.size() != element_count || imag.size() != element_count) {
        throw TransitionValidationError(
            TransitionValidationCode::wrong_element_count,
            "operator parts must each contain dimension squared values");
    }
    std::vector<Complex> values;
    values.reserve(element_count);
    for (std::size_t index = 0; index < element_count; ++index) {
        const Complex value {real[index], imag[index]};
        if (!finite(value)) {
            throw TransitionValidationError(
                TransitionValidationCode::non_finite,
                "operator contains a non-finite value");
        }
        values.push_back(value);
    }
    const double residual = matrix_hermiticity_residual_fro(values, dimension);
    const double norm = frobenius_norm(values);
    if (metadata.kind == TransitionOperatorKind::observable
        && residual > policy.relative_hermiticity_tolerance * norm) {
        throw TransitionValidationError(
            TransitionValidationCode::non_hermitian,
            "declared observable is not Hermitian relative to its operator scale");
    }
    return TransitionOperator(
        dimension, std::move(values), std::move(metadata), residual);
}

const Complex& TransitionOperator::at(
    const std::size_t row,
    const std::size_t column) const
{
    if (row >= dimension_ || column >= dimension_) {
        throw std::out_of_range("transition operator index is outside the matrix dimension");
    }
    return values_[row * dimension_ + column];
}

TransitionFrame analyze_transitions(
    const DensityState& state,
    const HamiltonianSnapshot& hamiltonian,
    const TransitionOperator& declared_operator,
    TransitionContext context,
    TransitionUnits units,
    const TransitionPolicy policy)
{
    validate_policy(policy);
    validate_units(units);
    validate_context(context);
    validate_operator_metadata(declared_operator.metadata());
    if (state.dimension() != hamiltonian.dimension()
        || state.dimension() != declared_operator.dimension()) {
        throw TransitionValidationError(
            TransitionValidationCode::dimension_mismatch,
            "rho, H, and A dimensions must match");
    }
    if (state.dimension() > policy.maximum_dimension) {
        throw TransitionValidationError(
            TransitionValidationCode::invalid_dimension,
            "transition dimension exceeds the configured limit");
    }
    if (context.basis_id != hamiltonian.metadata().basis_id
        || context.basis_id != declared_operator.metadata().basis_id) {
        throw TransitionValidationError(
            TransitionValidationCode::basis_mismatch,
            "rho context, H, and A must name the same coordinate basis");
    }
    if (context.revision != declared_operator.metadata().revision) {
        throw TransitionValidationError(
            TransitionValidationCode::revision_mismatch,
            "rho/H context and A revisions must match");
    }
    if (context.time_unit != units.time_unit) {
        throw TransitionValidationError(
            TransitionValidationCode::time_unit_mismatch,
            "context and hbar time units must match");
    }
    if (hamiltonian.metadata().energy_unit != units.energy_unit
        || declared_operator.metadata().unit != units.operator_unit) {
        throw TransitionValidationError(
            TransitionValidationCode::invalid_metadata,
            "H/A units must agree with the declared transition units");
    }

    const auto eigensystem = hermitian_eigensystem(
        hamiltonian.values(), hamiltonian.dimension(), policy);
    const auto dimension = state.dimension();
    const auto rho_energy = transform_into_basis(
        state.values(), eigensystem.eigenvectors, dimension);
    const auto operator_energy = transform_into_basis(
        declared_operator.values(), eigensystem.eigenvectors, dimension);
    if (!finite_matrix(rho_energy) || !finite_matrix(operator_energy)) {
        throw TransitionValidationError(
            TransitionValidationCode::numerical_inconsistency,
            "energy-basis transformation produced a non-finite matrix");
    }

    std::vector<double> populations(dimension);
    for (std::size_t index = 0; index < dimension; ++index) {
        populations[index] = rho_energy[index * dimension + index].real();
    }
    std::vector<double> activity(dimension * dimension);
    for (std::size_t target = 0; target < dimension; ++target) {
        for (std::size_t source = 0; source < dimension; ++source) {
            activity[target * dimension + source]
                = std::norm(operator_energy[target * dimension + source])
                * std::max(populations[source], 0.0);
            if (!std::isfinite(activity[target * dimension + source])) {
                throw TransitionValidationError(
                    TransitionValidationCode::numerical_inconsistency,
                    "diagnostic activity is non-finite");
            }
        }
    }

    std::vector<std::vector<std::size_t>> groups;
    std::vector<std::size_t> current {0};
    for (std::size_t index = 1; index < dimension; ++index) {
        if (eigensystem.eigenvalues[index] - eigensystem.eigenvalues[index - 1]
            <= policy.energy_gap_tolerance) {
            current.push_back(index);
        } else {
            if (current.size() > 1) {
                groups.push_back(current);
            }
            current = {index};
        }
    }
    if (current.size() > 1) {
        groups.push_back(current);
    }
    std::vector<bool> ambiguous(dimension, false);
    for (const auto& group : groups) {
        for (const auto index : group) {
            ambiguous[index] = true;
        }
    }

    std::vector<TransitionEdge> edges;
    std::vector<TransitionEdge> admitted;
    for (std::size_t source = 0; source < dimension; ++source) {
        for (std::size_t target = 0; target < dimension; ++target) {
            const double delta = eigensystem.eigenvalues[target]
                - eigensystem.eigenvalues[source];
            const bool diagonal = source == target;
            const bool zero_gap = std::abs(delta) <= policy.energy_gap_tolerance;
            if ((diagonal && !policy.include_diagonal)
                || (zero_gap && !policy.include_zero_gap)) {
                continue;
            }
            const auto amplitude = operator_energy[target * dimension + source];
            const double magnitude = std::abs(amplitude);
            const double diagnostic_activity = activity[target * dimension + source];
            TransitionEdge edge {
                source,
                target,
                delta,
                delta / units.hbar,
                amplitude,
                magnitude,
                magnitude > 0.0 ? std::optional<double>(std::arg(amplitude)) : std::nullopt,
                populations[source],
                populations[target],
                rho_energy[target * dimension + source],
                rho_energy[source * dimension + target],
                std::norm(amplitude),
                diagnostic_activity,
                diagonal,
                zero_gap,
                ambiguous[source] || ambiguous[target],
            };
            edges.push_back(edge);
            if (!diagonal && magnitude > policy.amplitude_threshold
                && diagnostic_activity > policy.activity_threshold) {
                admitted.push_back(edge);
            }
        }
    }

    const auto reconstructed_operator = multiply(
        multiply(eigensystem.eigenvectors, operator_energy, dimension),
        adjoint(eigensystem.eigenvectors, dimension),
        dimension);
    const double density_residual = matrix_hermiticity_residual_fro(
        state.values(), dimension);
    const double trace_error = std::abs(state.diagnostics().trace - Complex {1.0, 0.0});
    return TransitionFrame {
        std::move(context),
        std::move(units),
        declared_operator.metadata(),
        dimension,
        eigensystem.eigenvalues,
        eigensystem.eigenvectors,
        rho_energy,
        operator_energy,
        std::move(populations),
        std::move(activity),
        std::move(groups),
        std::move(edges),
        std::move(admitted),
        TransitionDiagnostics {
            density_residual,
            trace_error,
            hamiltonian.diagnostics().hermiticity_residual_fro,
            declared_operator.hermiticity_residual_fro(),
            eigensystem.eigen_residual_fro,
            eigensystem.reconstruction_residual_fro,
            difference_norm(reconstructed_operator, declared_operator.values()),
            matrix_hermiticity_residual_fro(rho_energy, dimension),
            eigensystem.iterations,
            eigensystem.maximum_off_diagonal,
        },
    };
}

void RevisionedTransitionStore::CandidateMatrixPart::clear() noexcept
{
    revision.reset();
    values.clear();
}

void RevisionedTransitionStore::CandidateContextPart::clear() noexcept
{
    revision.reset();
    time = 0.0;
    dt = 0.0;
}

RevisionedTransitionStore::RevisionedTransitionStore(
    const std::size_t dimension,
    TransitionContext fixed_context,
    TransitionUnits units,
    TransitionOperatorMetadata operator_metadata,
    TransitionPolicy policy)
    : dimension_(dimension)
    , element_count_(dimension * dimension)
    , fixed_context_(std::move(fixed_context))
    , units_(std::move(units))
    , operator_metadata_(std::move(operator_metadata))
    , policy_(policy)
{
    validate_policy(policy_);
    validate_units(units_);
    if (dimension_ == 0 || dimension_ > policy_.maximum_dimension) {
        throw TransitionValidationError(
            TransitionValidationCode::invalid_dimension,
            "transition store dimension is zero or exceeds the configured limit");
    }
    fixed_context_.revision = 0;
    fixed_context_.time = 0.0;
    fixed_context_.dt = 0.0;
    validate_context(fixed_context_);
    validate_operator_metadata(operator_metadata_, true);
    if (fixed_context_.basis_id != operator_metadata_.basis_id
        || fixed_context_.time_unit != units_.time_unit
        || operator_metadata_.unit != units_.operator_unit) {
        throw TransitionValidationError(
            TransitionValidationCode::invalid_metadata,
            "fixed context, operator, and units metadata must agree");
    }
    fixed_context_.revision = -1;
    operator_metadata_.revision = -1;
}

TransitionStageResult RevisionedTransitionStore::stage_matrix(
    const TransitionInputPart part,
    const long revision,
    std::vector<double> values)
{
    if (revision < 0 || revision <= active_revision_) {
        return {TransitionStageStatus::rejected, revision, "stale_revision",
                "revision is not newer than the active transition frame"};
    }
    if (values.size() != element_count_) {
        return {TransitionStageStatus::rejected, revision, "wrong_element_count",
                "matrix component does not contain dimension squared values"};
    }
    if (!std::all_of(values.begin(), values.end(), [](const double value) {
            return std::isfinite(value);
        })) {
        return {TransitionStageStatus::rejected, revision, "non_finite",
                "matrix component contains a non-finite value"};
    }
    CandidateMatrixPart* target = nullptr;
    switch (part) {
    case TransitionInputPart::rho_real: target = &rho_real_; break;
    case TransitionInputPart::rho_imag: target = &rho_imag_; break;
    case TransitionInputPart::hamiltonian_real: target = &hamiltonian_real_; break;
    case TransitionInputPart::hamiltonian_imag: target = &hamiltonian_imag_; break;
    case TransitionInputPart::operator_real: target = &operator_real_; break;
    case TransitionInputPart::operator_imag: target = &operator_imag_; break;
    }
    target->revision = revision;
    target->values = std::move(values);
    return try_commit(revision);
}

TransitionStageResult RevisionedTransitionStore::stage_context(
    const long revision,
    const double time,
    const double dt)
{
    if (revision < 0 || revision <= active_revision_) {
        return {TransitionStageStatus::rejected, revision, "stale_revision",
                "revision is not newer than the active transition frame"};
    }
    if (!std::isfinite(time) || !std::isfinite(dt) || dt < 0.0) {
        return {TransitionStageStatus::rejected, revision, "invalid_context",
                "context time must be finite and dt finite and nonnegative"};
    }
    context_.revision = revision;
    context_.time = time;
    context_.dt = dt;
    return try_commit(revision);
}

TransitionStageResult RevisionedTransitionStore::try_commit(const long staged_revision)
{
    const std::optional<long> revisions[] {
        rho_real_.revision, rho_imag_.revision,
        hamiltonian_real_.revision, hamiltonian_imag_.revision,
        operator_real_.revision, operator_imag_.revision,
        context_.revision,
    };
    if (!std::all_of(std::begin(revisions), std::end(revisions), [&](const auto revision) {
            return revision.has_value() && *revision == staged_revision;
        })) {
        return {TransitionStageStatus::staged, staged_revision, "partial_transaction",
                "transition transaction component staged"};
    }

    try {
        const auto state = DensityState::from_split(
            dimension_, rho_real_.values, rho_imag_.values,
            ValidationPolicy {
                policy_.relative_hermiticity_tolerance,
                policy_.relative_hermiticity_tolerance,
                policy_.relative_hermiticity_tolerance,
                policy_.maximum_dimension,
            });
        HamiltonianMetadata hamiltonian_metadata {
            units_.energy_unit,
            fixed_context_.basis_id,
            fixed_context_.source_id,
            fixed_context_.provenance,
        };
        const auto hamiltonian = HamiltonianSnapshot::from_split(
            dimension_, hamiltonian_real_.values, hamiltonian_imag_.values,
            std::move(hamiltonian_metadata),
            HamiltonianValidationPolicy {
                policy_.relative_hermiticity_tolerance,
                policy_.maximum_dimension,
            });
        auto operator_metadata = operator_metadata_;
        operator_metadata.revision = staged_revision;
        const auto declared_operator = TransitionOperator::from_split(
            dimension_, operator_real_.values, operator_imag_.values,
            std::move(operator_metadata), policy_);
        auto context = fixed_context_;
        context.revision = staged_revision;
        context.time = context_.time;
        context.dt = context_.dt;
        auto frame = analyze_transitions(
            state, hamiltonian, declared_operator,
            std::move(context), units_, policy_);
        active_ = std::make_unique<TransitionFrame>(std::move(frame));
        active_revision_ = staged_revision;
        clear_candidate();
        return {TransitionStageStatus::accepted, staged_revision, "accepted",
                "complete transition transaction accepted"};
    } catch (const ValidationError& error) {
        const std::string detail = "rho_" + std::string(validation_code_name(error.code()));
        const std::string message(error.what());
        clear_candidate();
        return {TransitionStageStatus::rejected, staged_revision, detail, message};
    } catch (const HamiltonianValidationError& error) {
        const std::string detail = "hamiltonian_"
            + std::string(hamiltonian_validation_code_name(error.code()));
        const std::string message(error.what());
        clear_candidate();
        return {TransitionStageStatus::rejected, staged_revision, detail, message};
    } catch (const TransitionValidationError& error) {
        const std::string detail(transition_validation_code_name(error.code()));
        const std::string message(error.what());
        clear_candidate();
        return {TransitionStageStatus::rejected, staged_revision, detail, message};
    }
}

void RevisionedTransitionStore::clear_candidate() noexcept
{
    rho_real_.clear();
    rho_imag_.clear();
    hamiltonian_real_.clear();
    hamiltonian_imag_.clear();
    operator_real_.clear();
    operator_imag_.clear();
    context_.clear();
}

} // namespace qmw
