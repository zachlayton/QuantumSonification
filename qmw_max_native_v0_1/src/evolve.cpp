#include "qmw/evolve.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <complex>
#include <limits>
#include <utility>
#include <vector>

namespace qmw {
namespace {

using Matrix = std::vector<Complex>;

constexpr double pade_theta_13 = 5.371920351148152;
constexpr std::array<double, 14> pade_coefficients {
    64764752532480000.0,
    32382376266240000.0,
    7771770303897600.0,
    1187353796428800.0,
    129060195264000.0,
    10559470521600.0,
    670442572800.0,
    33522128640.0,
    1323241920.0,
    40840800.0,
    960960.0,
    16380.0,
    182.0,
    1.0,
};

[[nodiscard]] bool blank(const std::string& value)
{
    return value.empty() || std::all_of(
        value.begin(),
        value.end(),
        [](const unsigned char character) { return std::isspace(character) != 0; });
}

[[nodiscard]] Matrix identity(const std::size_t dimension)
{
    Matrix result(dimension * dimension, Complex {});
    for (std::size_t index = 0; index < dimension; ++index) {
        result[index * dimension + index] = Complex {1.0, 0.0};
    }
    return result;
}

[[nodiscard]] Matrix multiply(
    const Matrix& left,
    const Matrix& right,
    const std::size_t dimension)
{
    Matrix result(dimension * dimension, Complex {});
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t inner = 0; inner < dimension; ++inner) {
            const auto factor = left[row * dimension + inner];
            for (std::size_t column = 0; column < dimension; ++column) {
                result[row * dimension + column]
                    += factor * right[inner * dimension + column];
            }
        }
    }
    return result;
}

[[nodiscard]] Matrix adjoint(const Matrix& value, const std::size_t dimension)
{
    Matrix result(value.size());
    for (std::size_t row = 0; row < dimension; ++row) {
        for (std::size_t column = 0; column < dimension; ++column) {
            result[row * dimension + column]
                = std::conj(value[column * dimension + row]);
        }
    }
    return result;
}

[[nodiscard]] Matrix linear_combination(
    const std::size_t dimension,
    std::initializer_list<std::pair<double, const Matrix*>> terms)
{
    Matrix result(dimension * dimension, Complex {});
    for (const auto& [scale, matrix] : terms) {
        for (std::size_t index = 0; index < result.size(); ++index) {
            result[index] += scale * (*matrix)[index];
        }
    }
    return result;
}

[[nodiscard]] double one_norm(const Matrix& value, const std::size_t dimension)
{
    double norm = 0.0;
    for (std::size_t column = 0; column < dimension; ++column) {
        double sum = 0.0;
        for (std::size_t row = 0; row < dimension; ++row) {
            sum += std::abs(value[row * dimension + column]);
        }
        norm = std::max(norm, sum);
    }
    return norm;
}

[[nodiscard]] double frobenius_norm(const Matrix& value)
{
    double squared = 0.0;
    for (const auto& element : value) {
        squared += std::norm(element);
    }
    return std::sqrt(squared);
}

[[nodiscard]] bool finite_matrix(const Matrix& value)
{
    return std::all_of(value.begin(), value.end(), [](const Complex& element) {
        return std::isfinite(element.real()) && std::isfinite(element.imag());
    });
}

[[nodiscard]] Matrix solve(
    Matrix left,
    Matrix right,
    const std::size_t dimension)
{
    const double scale = std::max(one_norm(left, dimension), 1.0);
    const double pivot_floor = std::numeric_limits<double>::epsilon()
        * scale * static_cast<double>(dimension) * 8.0;

    for (std::size_t column = 0; column < dimension; ++column) {
        std::size_t pivot_row = column;
        double pivot_magnitude = std::abs(left[column * dimension + column]);
        for (std::size_t row = column + 1; row < dimension; ++row) {
            const double magnitude = std::abs(left[row * dimension + column]);
            if (magnitude > pivot_magnitude) {
                pivot_magnitude = magnitude;
                pivot_row = row;
            }
        }
        if (!(pivot_magnitude > pivot_floor) || !std::isfinite(pivot_magnitude)) {
            throw EvolutionError(
                EvolutionCode::linear_solve_failed,
                "Pad\u00e9 denominator solve encountered a singular numerical pivot");
        }
        if (pivot_row != column) {
            for (std::size_t index = 0; index < dimension; ++index) {
                std::swap(
                    left[column * dimension + index],
                    left[pivot_row * dimension + index]);
                std::swap(
                    right[column * dimension + index],
                    right[pivot_row * dimension + index]);
            }
        }

        const auto pivot = left[column * dimension + column];
        for (std::size_t row = column + 1; row < dimension; ++row) {
            const auto factor = left[row * dimension + column] / pivot;
            left[row * dimension + column] = Complex {};
            for (std::size_t index = column + 1; index < dimension; ++index) {
                left[row * dimension + index]
                    -= factor * left[column * dimension + index];
            }
            for (std::size_t index = 0; index < dimension; ++index) {
                right[row * dimension + index]
                    -= factor * right[column * dimension + index];
            }
        }
    }

    Matrix solution(dimension * dimension, Complex {});
    for (std::size_t right_column = 0; right_column < dimension; ++right_column) {
        for (std::size_t reverse = 0; reverse < dimension; ++reverse) {
            const std::size_t row = dimension - 1 - reverse;
            Complex value = right[row * dimension + right_column];
            for (std::size_t column = row + 1; column < dimension; ++column) {
                value -= left[row * dimension + column]
                    * solution[column * dimension + right_column];
            }
            solution[row * dimension + right_column]
                = value / left[row * dimension + row];
        }
    }
    if (!finite_matrix(solution)) {
        throw EvolutionError(
            EvolutionCode::non_finite_result,
            "Pad\u00e9 denominator solve produced a non-finite matrix");
    }
    return solution;
}

struct ExponentialResult {
    Matrix unitary;
    std::size_t scaling_squarings {};
    double generator_one_norm {};
};

[[nodiscard]] ExponentialResult exponential_pade_13(
    Matrix generator,
    const std::size_t dimension,
    const std::size_t maximum_scaling_squarings)
{
    const double generator_norm = one_norm(generator, dimension);
    if (!std::isfinite(generator_norm)) {
        throw EvolutionError(
            EvolutionCode::non_finite_result,
            "dimensionless generator norm is non-finite");
    }

    std::size_t squarings = 0;
    if (generator_norm > pade_theta_13) {
        const double required = std::ceil(std::log2(generator_norm / pade_theta_13));
        if (!std::isfinite(required)
            || required > static_cast<double>(maximum_scaling_squarings)) {
            throw EvolutionError(
                EvolutionCode::generator_too_large,
                "dimensionless generator exceeds the configured scaling bound");
        }
        squarings = static_cast<std::size_t>(required);
        const double divisor = std::ldexp(1.0, static_cast<int>(squarings));
        for (auto& element : generator) {
            element /= divisor;
        }
    }

    const auto id = identity(dimension);
    const auto a2 = multiply(generator, generator, dimension);
    const auto a4 = multiply(a2, a2, dimension);
    const auto a6 = multiply(a4, a2, dimension);

    const auto u_inner = linear_combination(
        dimension,
        {
            {pade_coefficients[13], &a6},
            {pade_coefficients[11], &a4},
            {pade_coefficients[9], &a2},
        });
    const auto u_high = multiply(a6, u_inner, dimension);
    const auto u_sum = linear_combination(
        dimension,
        {
            {1.0, &u_high},
            {pade_coefficients[7], &a6},
            {pade_coefficients[5], &a4},
            {pade_coefficients[3], &a2},
            {pade_coefficients[1], &id},
        });
    const auto u = multiply(generator, u_sum, dimension);

    const auto v_inner = linear_combination(
        dimension,
        {
            {pade_coefficients[12], &a6},
            {pade_coefficients[10], &a4},
            {pade_coefficients[8], &a2},
        });
    const auto v_high = multiply(a6, v_inner, dimension);
    const auto v = linear_combination(
        dimension,
        {
            {1.0, &v_high},
            {pade_coefficients[6], &a6},
            {pade_coefficients[4], &a4},
            {pade_coefficients[2], &a2},
            {pade_coefficients[0], &id},
        });

    const auto denominator = linear_combination(dimension, {{1.0, &v}, {-1.0, &u}});
    const auto numerator = linear_combination(dimension, {{1.0, &v}, {1.0, &u}});
    auto result = solve(denominator, numerator, dimension);
    for (std::size_t index = 0; index < squarings; ++index) {
        result = multiply(result, result, dimension);
        if (!finite_matrix(result)) {
            throw EvolutionError(
                EvolutionCode::non_finite_result,
                "matrix exponential squaring produced a non-finite result");
        }
    }
    return {std::move(result), squarings, generator_norm};
}

[[nodiscard]] double unitarity_residual(
    const Matrix& unitary,
    const std::size_t dimension)
{
    const auto product = multiply(adjoint(unitary, dimension), unitary, dimension);
    const auto id = identity(dimension);
    Matrix residual(product.size());
    for (std::size_t index = 0; index < product.size(); ++index) {
        residual[index] = product[index] - id[index];
    }
    return frobenius_norm(residual) / std::sqrt(static_cast<double>(dimension));
}

[[nodiscard]] Complex trace_of(const Matrix& matrix, const std::size_t dimension)
{
    Complex result {};
    for (std::size_t index = 0; index < dimension; ++index) {
        result += matrix[index * dimension + index];
    }
    return result;
}

void validate_policy(const EvolutionPolicy& policy)
{
    if (!std::isfinite(policy.unitarity_tolerance)
        || !std::isfinite(policy.trace_preservation_tolerance)
        || !std::isfinite(policy.frobenius_norm_preservation_tolerance)
        || !(policy.unitarity_tolerance > 0.0)
        || !(policy.trace_preservation_tolerance > 0.0)
        || !(policy.frobenius_norm_preservation_tolerance > 0.0)
        || policy.maximum_scaling_squarings > 32) {
        throw EvolutionError(
            EvolutionCode::invalid_policy,
            "evolution tolerances must be positive and finite, and scaling squarings must not exceed 32");
    }
}

} // namespace

std::string_view evolution_code_name(const EvolutionCode code) noexcept
{
    switch (code) {
    case EvolutionCode::invalid_policy:
        return "invalid_policy";
    case EvolutionCode::invalid_revision:
        return "invalid_revision";
    case EvolutionCode::invalid_step:
        return "invalid_step";
    case EvolutionCode::invalid_time_unit:
        return "invalid_time_unit";
    case EvolutionCode::invalid_hbar:
        return "invalid_hbar";
    case EvolutionCode::dimension_mismatch:
        return "dimension_mismatch";
    case EvolutionCode::basis_mismatch:
        return "basis_mismatch";
    case EvolutionCode::generator_too_large:
        return "generator_too_large";
    case EvolutionCode::linear_solve_failed:
        return "linear_solve_failed";
    case EvolutionCode::non_finite_result:
        return "non_finite_result";
    case EvolutionCode::unitarity_not_preserved:
        return "unitarity_not_preserved";
    case EvolutionCode::trace_not_preserved:
        return "trace_not_preserved";
    case EvolutionCode::norm_not_preserved:
        return "norm_not_preserved";
    case EvolutionCode::output_state_invalid:
        return "output_state_invalid";
    }
    return "unknown_evolution_error";
}

EvolutionError::EvolutionError(const EvolutionCode code, std::string message)
    : std::runtime_error(std::move(message))
    , code_(code)
{
}

EvolutionCandidate::EvolutionCandidate(
    DensityState state,
    EvolutionRequest request,
    std::string energy_unit,
    const EvolutionDiagnostics diagnostics)
    : state_(std::move(state))
    , request_(std::move(request))
    , energy_unit_(std::move(energy_unit))
    , diagnostics_(diagnostics)
{
}

EvolutionCandidate evolve_closed_system(
    const DensityState& state,
    const HamiltonianSnapshot& hamiltonian,
    EvolutionRequest request,
    EvolutionPolicy policy)
{
    validate_policy(policy);
    if (request.state_revision < 0 || request.hamiltonian_revision < 0
        || request.candidate_revision <= request.state_revision) {
        throw EvolutionError(
            EvolutionCode::invalid_revision,
            "state and Hamiltonian revisions must be nonnegative, and the candidate revision must be newer than the state");
    }
    if (!std::isfinite(request.dt)) {
        throw EvolutionError(EvolutionCode::invalid_step, "dt must be finite");
    }
    if (blank(request.time_unit)) {
        throw EvolutionError(
            EvolutionCode::invalid_time_unit,
            "time unit must be an explicit nonempty symbol");
    }
    if (!std::isfinite(request.hbar) || !(request.hbar > 0.0)) {
        throw EvolutionError(
            EvolutionCode::invalid_hbar,
            "hbar must be positive and finite in energy-unit times declared-time-unit");
    }
    if (state.dimension() != hamiltonian.dimension()) {
        throw EvolutionError(
            EvolutionCode::dimension_mismatch,
            "state and Hamiltonian dimensions do not match");
    }
    if (hamiltonian.metadata().basis_id != "computational_q0_lsb") {
        throw EvolutionError(
            EvolutionCode::basis_mismatch,
            "closed-system evolution requires computational_q0_lsb Hamiltonian ordering");
    }

    const auto dimension = state.dimension();
    if (dimension > policy.output_state_policy.maximum_dimension) {
        throw EvolutionError(
            EvolutionCode::dimension_mismatch,
            "state dimension exceeds the evolution output-policy limit");
    }
    const double scale = request.dt / request.hbar;
    if (!std::isfinite(scale)) {
        throw EvolutionError(
            EvolutionCode::invalid_step,
            "dt divided by hbar is non-finite");
    }

    Matrix generator(hamiltonian.values().size());
    const Complex generator_scale {0.0, -scale};
    for (std::size_t index = 0; index < generator.size(); ++index) {
        generator[index] = generator_scale * hamiltonian.values()[index];
    }
    if (!finite_matrix(generator)) {
        throw EvolutionError(
            EvolutionCode::non_finite_result,
            "dimensionless generator contains a non-finite value");
    }

    auto exponential = exponential_pade_13(
        std::move(generator), dimension, policy.maximum_scaling_squarings);
    const double unitary_residual = unitarity_residual(exponential.unitary, dimension);
    if (!std::isfinite(unitary_residual)
        || unitary_residual > policy.unitarity_tolerance) {
        throw EvolutionError(
            EvolutionCode::unitarity_not_preserved,
            "computed propagator failed the configured unitarity tolerance");
    }

    const Matrix input = state.values();
    const auto left = multiply(exponential.unitary, input, dimension);
    const auto output = multiply(left, adjoint(exponential.unitary, dimension), dimension);
    if (!finite_matrix(output)) {
        throw EvolutionError(
            EvolutionCode::non_finite_result,
            "evolved density matrix contains a non-finite value");
    }

    const double input_norm = frobenius_norm(input);
    const double output_norm = frobenius_norm(output);
    const double norm_drift = std::abs(output_norm - input_norm);
    const double relative_norm_drift = norm_drift / input_norm;
    const double trace_drift = std::abs(trace_of(output, dimension) - state.diagnostics().trace);
    if (trace_drift > policy.trace_preservation_tolerance) {
        throw EvolutionError(
            EvolutionCode::trace_not_preserved,
            "evolved density matrix failed the configured trace-preservation tolerance");
    }
    if (relative_norm_drift > policy.frobenius_norm_preservation_tolerance) {
        throw EvolutionError(
            EvolutionCode::norm_not_preserved,
            "evolved density matrix failed the configured Frobenius-norm tolerance");
    }

    std::vector<double> real(output.size());
    std::vector<double> imag(output.size());
    for (std::size_t index = 0; index < output.size(); ++index) {
        real[index] = output[index].real();
        imag[index] = output[index].imag();
    }

    DensityState candidate = [&]() {
        try {
            return DensityState::from_split(
                dimension, real, imag, policy.output_state_policy);
        } catch (const ValidationError& error) {
            throw EvolutionError(
                EvolutionCode::output_state_invalid,
                std::string("evolved density matrix failed admission: ") + error.what());
        }
    }();

    const double purity_drift = std::abs(
        candidate.diagnostics().purity - state.diagnostics().purity);
    const double output_hermiticity_residual
        = candidate.diagnostics().hermiticity_residual;
    const double output_minimum_ldlt_pivot
        = candidate.diagnostics().minimum_ldlt_pivot;
    return EvolutionCandidate(
        std::move(candidate),
        std::move(request),
        hamiltonian.metadata().energy_unit,
        EvolutionDiagnostics {
            13,
            exponential.scaling_squarings,
            exponential.generator_one_norm,
            unitary_residual,
            trace_drift,
            norm_drift,
            relative_norm_drift,
            purity_drift,
            output_hermiticity_residual,
            output_minimum_ldlt_pivot,
        });
}

} // namespace qmw
