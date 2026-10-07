#include "qmw/spectrum.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <utility>

namespace qmw {
namespace {

using Matrix = std::vector<Complex>;

[[nodiscard]] std::size_t at(const std::size_t n, const std::size_t row, const std::size_t column)
{
    return row * n + column;
}

[[nodiscard]] double frobenius_norm(const Matrix& matrix)
{
    long double sum = 0.0L;
    for (const auto value : matrix) {
        sum += static_cast<long double>(std::norm(value));
    }
    return std::sqrt(static_cast<double>(sum));
}

[[nodiscard]] Matrix hermitian_analysis_copy(const Matrix& input, const std::size_t n)
{
    Matrix output(input);
    for (std::size_t row = 0; row < n; ++row) {
        output[at(n, row, row)] = {input[at(n, row, row)].real(), 0.0};
        for (std::size_t column = row + 1; column < n; ++column) {
            const auto value = 0.5 * (
                input[at(n, row, column)] + std::conj(input[at(n, column, row)]));
            output[at(n, row, column)] = value;
            output[at(n, column, row)] = std::conj(value);
        }
    }
    return output;
}

[[nodiscard]] double off_diagonal_frobenius(const Matrix& matrix, const std::size_t n)
{
    long double sum = 0.0L;
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t column = 0; column < n; ++column) {
            if (row != column) {
                sum += static_cast<long double>(std::norm(matrix[at(n, row, column)]));
            }
        }
    }
    return std::sqrt(static_cast<double>(sum));
}

void canonicalize_phase(Matrix& vectors, const std::size_t n, const std::size_t mode)
{
    std::size_t pivot = 0;
    double pivot_magnitude = -1.0;
    for (std::size_t row = 0; row < n; ++row) {
        const double magnitude = std::abs(vectors[at(n, row, mode)]);
        if (magnitude > pivot_magnitude) {
            pivot = row;
            pivot_magnitude = magnitude;
        }
    }
    if (!(pivot_magnitude > 0.0)) {
        return;
    }
    const auto pivot_value = vectors[at(n, pivot, mode)];
    const auto phase = std::conj(pivot_value) / std::abs(pivot_value);
    for (std::size_t row = 0; row < n; ++row) {
        vectors[at(n, row, mode)] *= phase;
    }
    vectors[at(n, pivot, mode)] = {std::abs(vectors[at(n, pivot, mode)]), 0.0};
}

[[nodiscard]] double eigen_residual_relative(
    const Matrix& original,
    const std::vector<double>& values,
    const Matrix& vectors,
    const std::size_t n)
{
    long double residual = 0.0L;
    for (std::size_t mode = 0; mode < n; ++mode) {
        for (std::size_t row = 0; row < n; ++row) {
            Complex av {};
            for (std::size_t column = 0; column < n; ++column) {
                av += original[at(n, row, column)] * vectors[at(n, column, mode)];
            }
            residual += static_cast<long double>(std::norm(
                av - values[mode] * vectors[at(n, row, mode)]));
        }
    }
    const double scale = frobenius_norm(original);
    const double absolute = std::sqrt(static_cast<double>(residual));
    return scale == 0.0 ? absolute : absolute / scale;
}

[[nodiscard]] HermitianEigensystem hermitian_eigensystem(
    const Matrix& admitted,
    const std::size_t n,
    const SpectrumPolicy& policy)
{
    Matrix matrix = hermitian_analysis_copy(admitted, n);
    const Matrix original = matrix;
    Matrix vectors(n * n, Complex {});
    for (std::size_t index = 0; index < n; ++index) {
        vectors[at(n, index, index)] = 1.0;
    }

    const double scale = frobenius_norm(matrix);
    const double threshold = policy.relative_eigensolver_tolerance * scale;
    std::size_t sweeps = 0;
    double off_diagonal = off_diagonal_frobenius(matrix, n);
    for (; sweeps < policy.maximum_sweeps && off_diagonal > threshold; ++sweeps) {
        for (std::size_t p = 0; p + 1 < n; ++p) {
            for (std::size_t q = p + 1; q < n; ++q) {
                const auto apq = matrix[at(n, p, q)];
                const double magnitude = std::abs(apq);
                if (magnitude <= threshold / std::max<std::size_t>(1, n)) {
                    continue;
                }
                const double app = matrix[at(n, p, p)].real();
                const double aqq = matrix[at(n, q, q)].real();
                const double tau = (aqq - app) / (2.0 * magnitude);
                const double t = tau >= 0.0
                    ? 1.0 / (tau + std::hypot(1.0, tau))
                    : -1.0 / (-tau + std::hypot(1.0, tau));
                const double c = 1.0 / std::hypot(1.0, t);
                const double s = t * c;
                const Complex phase = apq / magnitude;
                const Complex jpp {c, 0.0};
                const Complex jpq {s, 0.0};
                const Complex jqp = -std::conj(phase) * s;
                const Complex jqq = std::conj(phase) * c;

                // matrix <- J^H matrix J, with a deterministic cyclic order.
                for (std::size_t row = 0; row < n; ++row) {
                    const auto left = matrix[at(n, row, p)];
                    const auto right = matrix[at(n, row, q)];
                    matrix[at(n, row, p)] = left * jpp + right * jqp;
                    matrix[at(n, row, q)] = left * jpq + right * jqq;
                }
                for (std::size_t column = 0; column < n; ++column) {
                    const auto top = matrix[at(n, p, column)];
                    const auto bottom = matrix[at(n, q, column)];
                    matrix[at(n, p, column)] = std::conj(jpp) * top + std::conj(jqp) * bottom;
                    matrix[at(n, q, column)] = std::conj(jpq) * top + std::conj(jqq) * bottom;
                }
                for (std::size_t row = 0; row < n; ++row) {
                    const auto left = vectors[at(n, row, p)];
                    const auto right = vectors[at(n, row, q)];
                    vectors[at(n, row, p)] = left * jpp + right * jqp;
                    vectors[at(n, row, q)] = left * jpq + right * jqq;
                }
            }
        }
        off_diagonal = off_diagonal_frobenius(matrix, n);
    }
    if (off_diagonal > threshold && scale != 0.0) {
        throw SpectrumError(
            SpectrumCode::eigensolver_nonconvergence,
            "bounded cyclic Jacobi eigensolver did not converge");
    }

    std::vector<double> unsorted(n);
    for (std::size_t index = 0; index < n; ++index) {
        unsorted[index] = matrix[at(n, index, index)].real();
    }
    std::vector<std::size_t> permutation(n);
    std::iota(permutation.begin(), permutation.end(), 0);
    std::stable_sort(permutation.begin(), permutation.end(), [&](const auto left, const auto right) {
        return unsorted[left] < unsorted[right];
    });

    std::vector<double> values(n);
    Matrix sorted_vectors(n * n);
    for (std::size_t mode = 0; mode < n; ++mode) {
        values[mode] = unsorted[permutation[mode]];
        for (std::size_t row = 0; row < n; ++row) {
            sorted_vectors[at(n, row, mode)] = vectors[at(n, row, permutation[mode])];
        }
        canonicalize_phase(sorted_vectors, n, mode);
    }

    std::vector<DegenerateGroup> groups;
    std::size_t first = 0;
    for (std::size_t index = 1; index <= n; ++index) {
        if (index < n && std::abs(values[index] - values[index - 1]) <= policy.degeneracy_tolerance) {
            continue;
        }
        if (index - first > 1) {
            groups.push_back({first, index - 1});
        }
        first = index;
    }
    const double residual = eigen_residual_relative(original, values, sorted_vectors, n);
    if (!std::isfinite(residual)) {
        throw SpectrumError(SpectrumCode::non_finite_result, "non-finite eigensolver residual");
    }
    const bool labels_stable = groups.empty();
    return {
        std::move(values),
        std::move(sorted_vectors),
        std::move(groups),
        sweeps,
        off_diagonal,
        residual,
        labels_stable,
    };
}

[[nodiscard]] Matrix transform_to_basis(
    const Matrix& matrix,
    const Matrix& basis,
    const std::size_t n)
{
    Matrix output(n * n);
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t column = 0; column < n; ++column) {
            Complex value {};
            for (std::size_t left = 0; left < n; ++left) {
                for (std::size_t right = 0; right < n; ++right) {
                    value += std::conj(basis[at(n, left, row)])
                        * matrix[at(n, left, right)]
                        * basis[at(n, right, column)];
                }
            }
            output[at(n, row, column)] = value;
        }
    }
    return output;
}

[[nodiscard]] std::vector<double> gaps(const std::vector<double>& values)
{
    std::vector<double> output;
    if (values.size() > 1) {
        output.reserve(values.size() - 1);
        for (std::size_t index = 1; index < values.size(); ++index) {
            output.push_back(values[index] - values[index - 1]);
        }
    }
    return output;
}

[[nodiscard]] double commutator_norm(
    const Matrix& hamiltonian,
    const Matrix& state,
    const std::size_t n)
{
    long double sum = 0.0L;
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t column = 0; column < n; ++column) {
            Complex value {};
            for (std::size_t inner = 0; inner < n; ++inner) {
                value += hamiltonian[at(n, row, inner)] * state[at(n, inner, column)]
                    - state[at(n, row, inner)] * hamiltonian[at(n, inner, column)];
            }
            sum += static_cast<long double>(std::norm(value));
        }
    }
    return std::sqrt(static_cast<double>(sum));
}

void validate_policy(const SpectrumPolicy& policy)
{
    if (!std::isfinite(policy.relative_eigensolver_tolerance)
        || !std::isfinite(policy.density_positivity_tolerance)
        || !std::isfinite(policy.degeneracy_tolerance)
        || !(policy.relative_eigensolver_tolerance > 0.0)
        || !(policy.density_positivity_tolerance > 0.0)
        || !(policy.degeneracy_tolerance > 0.0)
        || policy.maximum_sweeps == 0
        || policy.maximum_dimension == 0
        || policy.maximum_dimension > 64) {
        throw SpectrumError(SpectrumCode::invalid_policy, "invalid spectrum analysis policy");
    }
}

} // namespace

std::string_view spectrum_code_name(const SpectrumCode code) noexcept
{
    switch (code) {
    case SpectrumCode::invalid_policy: return "invalid_policy";
    case SpectrumCode::invalid_revision: return "invalid_revision";
    case SpectrumCode::revision_mismatch: return "revision_mismatch";
    case SpectrumCode::dimension_mismatch: return "dimension_mismatch";
    case SpectrumCode::basis_mismatch: return "basis_mismatch";
    case SpectrumCode::eigensolver_nonconvergence: return "eigensolver_nonconvergence";
    case SpectrumCode::invalid_density_spectrum: return "invalid_density_spectrum";
    case SpectrumCode::non_finite_result: return "non_finite_result";
    }
    return "unknown_spectrum_error";
}

SpectrumError::SpectrumError(const SpectrumCode code, std::string message)
    : std::runtime_error(std::move(message)), code_(code)
{
}

QuantumSpectrumFrame::QuantumSpectrumFrame(
    const std::size_t dimension,
    HermitianEigensystem density,
    HermitianEigensystem energy,
    std::vector<Complex> rho_in_energy_basis,
    std::vector<double> energy_populations,
    std::vector<double> basis_overlap,
    std::vector<double> density_gaps,
    std::vector<double> energy_gaps,
    const double purity,
    const double entropy_nats,
    const double participation_rank,
    const double commutator_norm_value,
    const SpectrumPolicy policy,
    SpectrumProvenance provenance)
    : dimension_(dimension)
    , density_(std::move(density))
    , energy_(std::move(energy))
    , rho_in_energy_basis_(std::move(rho_in_energy_basis))
    , energy_populations_(std::move(energy_populations))
    , basis_overlap_(std::move(basis_overlap))
    , density_gaps_(std::move(density_gaps))
    , energy_gaps_(std::move(energy_gaps))
    , purity_(purity)
    , entropy_nats_(entropy_nats)
    , participation_rank_(participation_rank)
    , commutator_norm_(commutator_norm_value)
    , policy_(policy)
    , provenance_(std::move(provenance))
{
}

QuantumSpectrumFrame analyze_quantum_spectrum(
    const DensityState& state,
    const long state_revision,
    const HamiltonianSnapshot& hamiltonian,
    const long hamiltonian_revision,
    const SpectrumPolicy policy)
{
    validate_policy(policy);
    if (state_revision < 0 || hamiltonian_revision < 0) {
        throw SpectrumError(SpectrumCode::invalid_revision, "spectrum revisions must be nonnegative");
    }
    if (state_revision != hamiltonian_revision) {
        throw SpectrumError(SpectrumCode::revision_mismatch, "state and Hamiltonian revisions must match");
    }
    if (state.dimension() != hamiltonian.dimension()
        || state.dimension() > policy.maximum_dimension) {
        throw SpectrumError(SpectrumCode::dimension_mismatch, "state and Hamiltonian dimensions must match within the configured limit");
    }
    if (hamiltonian.metadata().basis_id != "computational_q0_lsb") {
        throw SpectrumError(SpectrumCode::basis_mismatch, "Hamiltonian basis must match the admitted q0-LSB density matrix basis");
    }

    const auto n = state.dimension();
    auto density = hermitian_eigensystem(state.values(), n, policy);
    auto energy = hermitian_eigensystem(hamiltonian.values(), n, policy);
    if (density.eigenvalues.front() < -policy.density_positivity_tolerance) {
        throw SpectrumError(SpectrumCode::invalid_density_spectrum, "density eigenspectrum is negative beyond tolerance");
    }

    auto rho_energy = transform_to_basis(state.values(), energy.eigenvectors, n);
    std::vector<double> populations(n);
    for (std::size_t index = 0; index < n; ++index) {
        populations[index] = rho_energy[at(n, index, index)].real();
    }
    std::vector<double> overlap(n * n);
    for (std::size_t energy_mode = 0; energy_mode < n; ++energy_mode) {
        for (std::size_t density_mode = 0; density_mode < n; ++density_mode) {
            Complex inner {};
            for (std::size_t row = 0; row < n; ++row) {
                inner += std::conj(energy.eigenvectors[at(n, row, energy_mode)])
                    * density.eigenvectors[at(n, row, density_mode)];
            }
            overlap[at(n, energy_mode, density_mode)] = std::norm(inner);
        }
    }

    double entropy = 0.0;
    double density_square_sum = 0.0;
    for (const double raw : density.eigenvalues) {
        const double value = std::max(0.0, raw);
        density_square_sum += value * value;
        if (value > policy.density_positivity_tolerance) {
            entropy -= value * std::log(value);
        }
    }
    Complex purity_complex {};
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t inner = 0; inner < n; ++inner) {
            purity_complex += state.at(row, inner) * state.at(inner, row);
        }
    }
    const double purity = purity_complex.real();
    const double participation = 1.0 / density_square_sum;
    const double commutator = commutator_norm(hamiltonian.values(), state.values(), n);
    if (!std::isfinite(purity) || !std::isfinite(entropy)
        || !std::isfinite(participation) || !std::isfinite(commutator)) {
        throw SpectrumError(SpectrumCode::non_finite_result, "spectrum analysis produced a non-finite diagnostic");
    }

    SpectrumProvenance provenance {
        state_revision,
        hamiltonian_revision,
        "dimensionless",
        hamiltonian.metadata().energy_unit,
        hamiltonian.metadata().basis_id,
        hamiltonian.metadata().source_id,
        hamiltonian.metadata().provenance,
        "ascending_eigenvalue_stable_index",
        "largest_component_real_nonnegative",
    };
    const auto density_gap_values = gaps(density.eigenvalues);
    const auto energy_gap_values = gaps(energy.eigenvalues);
    return QuantumSpectrumFrame(
        n,
        std::move(density),
        std::move(energy),
        std::move(rho_energy),
        std::move(populations),
        std::move(overlap),
        std::move(density_gap_values),
        std::move(energy_gap_values),
        purity,
        entropy,
        participation,
        commutator,
        policy,
        std::move(provenance));
}

} // namespace qmw
