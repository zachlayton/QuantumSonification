#include "qmw/state.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <utility>

namespace qmw {
namespace {

[[nodiscard]] bool finite_complex(const Complex& value) noexcept
{
    return std::isfinite(value.real()) && std::isfinite(value.imag());
}

[[nodiscard]] double hermiticity_residual(
    const std::vector<Complex>& values,
    const std::size_t dimension)
{
    double residual = 0.0;
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            const auto error = values[row * dimension + column]
                - std::conj(values[column * dimension + row]);
            residual = std::max(residual, std::abs(error));
        }
    }
    return residual;
}

[[nodiscard]] double validate_positive_semidefinite(
    const std::vector<Complex>& values,
    const std::size_t dimension,
    const double tolerance)
{
    // Unpivoted LDL^H is sufficient for an admitted Hermitian PSD matrix. A
    // zero pivot in a PSD matrix requires the remaining entry in that column
    // to be zero; enforcing that condition also handles rank-deficient states.
    std::vector<Complex> lower(dimension * dimension, Complex {});
    std::vector<double> diagonal(dimension, 0.0);
    double minimum_pivot = std::numeric_limits<double>::infinity();

    for (std::size_t column = 0; column < dimension; ++column) {
        double pivot = values[column * dimension + column].real();
        for (std::size_t prior = 0; prior < column; ++prior) {
            pivot -= std::norm(lower[column * dimension + prior]) * diagonal[prior];
        }
        minimum_pivot = std::min(minimum_pivot, pivot);
        if (pivot < -tolerance) {
            throw ValidationError(
                ValidationCode::not_positive_semidefinite,
                "rho has a negative LDL^H pivot");
        }
        // Preserve every positive pivot, however small.  Clamping a small
        // positive pivot to zero falsely rejects legitimate rank-deficient
        // states such as |psi><psi| when one basis population is tiny but its
        // coherence is much larger than the absolute validation tolerance.
        // Only a small negative pivot is admitted as numerical roundoff.
        if (pivot < 0.0) {
            pivot = 0.0;
        }
        diagonal[column] = pivot;
        lower[column * dimension + column] = Complex {1.0, 0.0};

        for (std::size_t row = column + 1; row < dimension; ++row) {
            Complex residual = values[row * dimension + column];
            for (std::size_t prior = 0; prior < column; ++prior) {
                residual -= lower[row * dimension + prior] * diagonal[prior]
                    * std::conj(lower[column * dimension + prior]);
            }
            if (pivot == 0.0) {
                if (std::abs(residual) > tolerance) {
                    throw ValidationError(
                        ValidationCode::not_positive_semidefinite,
                        "rho has a nonzero column below a zero LDL^H pivot");
                }
            } else {
                lower[row * dimension + column] = residual / pivot;
            }
        }
    }

    return minimum_pivot;
}

} // namespace

std::string_view validation_code_name(const ValidationCode code) noexcept
{
    switch (code) {
    case ValidationCode::invalid_policy:
        return "invalid_policy";
    case ValidationCode::invalid_dimension:
        return "invalid_dimension";
    case ValidationCode::wrong_element_count:
        return "wrong_element_count";
    case ValidationCode::non_finite:
        return "non_finite";
    case ValidationCode::non_hermitian:
        return "non_hermitian";
    case ValidationCode::trace_not_one:
        return "trace_not_one";
    case ValidationCode::not_positive_semidefinite:
        return "not_positive_semidefinite";
    }
    return "unknown_validation_error";
}

ValidationError::ValidationError(const ValidationCode code, const char* message)
    : std::runtime_error(message)
    , code_(code)
{
}

DensityState::DensityState(
    const std::size_t dimension,
    std::vector<Complex> values,
    StateDiagnostics diagnostics)
    : dimension_(dimension)
    , values_(std::move(values))
    , diagnostics_(diagnostics)
{
}

DensityState DensityState::from_split(
    const std::size_t dimension,
    const std::vector<double>& real,
    const std::vector<double>& imag,
    const ValidationPolicy policy)
{
    if (!std::isfinite(policy.hermiticity_tolerance)
        || !std::isfinite(policy.trace_tolerance)
        || !std::isfinite(policy.positivity_tolerance)
        || !(policy.hermiticity_tolerance > 0.0)
        || !(policy.trace_tolerance > 0.0)
        || !(policy.positivity_tolerance > 0.0)
        || policy.maximum_dimension == 0) {
        throw ValidationError(
            ValidationCode::invalid_policy,
            "validation tolerances must be finite and positive, and maximum dimension must be nonzero");
    }
    if (dimension == 0 || dimension > policy.maximum_dimension) {
        throw ValidationError(
            ValidationCode::invalid_dimension,
            "rho dimension is zero or exceeds the configured limit");
    }
    if (dimension > std::numeric_limits<std::size_t>::max() / dimension) {
        throw ValidationError(
            ValidationCode::invalid_dimension,
            "rho dimension squared cannot be represented");
    }
    const auto element_count = dimension * dimension;
    if (real.size() != element_count || imag.size() != element_count) {
        throw ValidationError(
            ValidationCode::wrong_element_count,
            "rho real and imaginary parts must each contain dimension squared values");
    }
    std::vector<Complex> values;
    values.reserve(element_count);
    for (std::size_t index = 0; index < element_count; ++index) {
        const Complex value {real[index], imag[index]};
        if (!finite_complex(value)) {
            throw ValidationError(
                ValidationCode::non_finite,
                "rho contains a non-finite value");
        }
        values.push_back(value);
    }

    const double residual = hermiticity_residual(values, dimension);
    if (residual > policy.hermiticity_tolerance) {
        throw ValidationError(
            ValidationCode::non_hermitian,
            "rho is not Hermitian within tolerance");
    }

    Complex trace {};
    double purity = 0.0;
    for (std::size_t row = 0; row < dimension; ++row) {
        trace += values[row * dimension + row];
        for (std::size_t column = 0; column < dimension; ++column) {
            purity += std::norm(values[row * dimension + column]);
        }
    }
    if (std::abs(trace - Complex {1.0, 0.0}) > policy.trace_tolerance) {
        throw ValidationError(
            ValidationCode::trace_not_one,
            "rho trace is not one within tolerance");
    }

    const double minimum_pivot = validate_positive_semidefinite(
        values,
        dimension,
        policy.positivity_tolerance);

    return DensityState(
        dimension,
        std::move(values),
        StateDiagnostics {trace, purity, residual, minimum_pivot});
}

const Complex& DensityState::at(const std::size_t row, const std::size_t column) const
{
    if (row >= dimension_ || column >= dimension_) {
        throw std::out_of_range("density-matrix index is outside the state dimension");
    }
    return values_[row * dimension_ + column];
}

} // namespace qmw
