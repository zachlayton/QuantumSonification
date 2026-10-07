#include "qmw/spectrum.hpp"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <string_view>
#include <vector>

namespace {

int checks = 0;
int failures = 0;

void check(const bool condition, const std::string_view name)
{
    ++checks;
    if (!condition) {
        ++failures;
        std::cerr << "FAIL: " << name << '\n';
    }
}

void check_close(
    const double actual,
    const double expected,
    const std::string_view name,
    const double tolerance = 1.0e-11)
{
    check(std::abs(actual - expected) <= tolerance, name);
}

template <typename Function>
void check_code(Function&& function, const qmw::SpectrumCode expected, const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const qmw::SpectrumError& error) {
        check(error.code() == expected, name);
    } catch (...) {
        check(false, name);
    }
}

std::vector<double> zeros(const std::size_t count)
{
    return std::vector<double>(count, 0.0);
}

qmw::HamiltonianSnapshot hamiltonian(
    const std::size_t dimension,
    const std::vector<double>& real,
    const std::vector<double>& imag,
    const char* basis = "computational_q0_lsb")
{
    return qmw::HamiltonianSnapshot::from_split(
        dimension,
        real,
        imag,
        qmw::HamiltonianMetadata {
            "joule", basis, "spectrum-fixture", "calibration-run-17"});
}

} // namespace

int main()
{
    {
        // rho=|0><0| and H=X. Energy populations come from V_H^H rho V_H,
        // not from pairing the independently sorted density spectrum.
        const auto state = qmw::DensityState::from_split(
            2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
        const auto h = hamiltonian(2, {0.0, 1.0, 1.0, 0.0}, zeros(4));
        const auto frame = qmw::analyze_quantum_spectrum(state, 7, h, 7);

        check(frame.dimension() == 2, "dimension retained");
        check_close(frame.energy().eigenvalues[0], -1.0, "ascending energy -1");
        check_close(frame.energy().eigenvalues[1], 1.0, "ascending energy +1");
        check_close(frame.density().eigenvalues[0], 0.0, "density eigenvalue zero");
        check_close(frame.density().eigenvalues[1], 1.0, "density eigenvalue one");
        check_close(frame.energy_populations()[0], 0.5, "energy population lower");
        check_close(frame.energy_populations()[1], 0.5, "energy population upper");
        check_close(frame.purity(), 1.0, "pure state purity");
        check_close(frame.entropy_nats(), 0.0, "pure state entropy nats");
        check_close(frame.participation_rank(), 1.0, "pure participation rank");
        check_close(frame.commutator_norm(), std::sqrt(2.0), "commutator Frobenius norm");
        check(frame.provenance().state_revision == 7, "state revision provenance");
        check(frame.provenance().hamiltonian_revision == 7, "Hamiltonian revision provenance");
        check(frame.provenance().energy_unit == "joule", "energy unit provenance");
        check(frame.provenance().basis_id == "computational_q0_lsb", "basis provenance");
        check(frame.provenance().hamiltonian_source_id == "spectrum-fixture", "source provenance");
        check(frame.provenance().hamiltonian_provenance == "calibration-run-17", "Hamiltonian provenance");
        check(frame.energy().relative_residual_frobenius < 1.0e-11, "energy eigensolver residual");

        for (std::size_t energy_mode = 0; energy_mode < 2; ++energy_mode) {
            double reconstructed = 0.0;
            for (std::size_t density_mode = 0; density_mode < 2; ++density_mode) {
                reconstructed += frame.basis_overlap()[energy_mode * 2 + density_mode]
                    * frame.density().eigenvalues[density_mode];
            }
            check_close(reconstructed, frame.energy_populations()[energy_mode], "overlap reconstructs energy population");
        }

        // Observer analysis does not mutate either raw matrix.
        check_close(state.at(0, 0).real(), 1.0, "raw rho preserved", 0.0);
        check_close(h.at(0, 1).real(), 1.0, "raw Hamiltonian preserved", 0.0);
    }

    {
        const auto state = qmw::DensityState::from_split(
            2, {0.5, 0.0, 0.0, 0.5}, zeros(4));
        const auto h = hamiltonian(2, {1.0, 0.0, 0.0, -1.0}, zeros(4));
        const auto frame = qmw::analyze_quantum_spectrum(state, 2, h, 2);
        check_close(frame.purity(), 0.5, "mixed purity");
        check_close(frame.entropy_nats(), std::log(2.0), "mixed von Neumann entropy in nats");
        check_close(frame.participation_rank(), 2.0, "mixed participation rank");
        check_close(frame.commutator_norm(), 0.0, "commuting state and Hamiltonian");
        check_close(frame.energy_populations()[0], 0.5, "mixed lower population");
        check_close(frame.energy_populations()[1], 0.5, "mixed upper population");
        check(!frame.density().mode_labels_stable, "degenerate density labels explicitly unstable");
        check(frame.density().near_degenerate_groups.size() == 1, "density degeneracy group emitted");
        check(frame.density().near_degenerate_groups[0].first == 0, "density group first index");
        check(frame.density().near_degenerate_groups[0].last == 1, "density group last index");
    }

    {
        // Complex sigma_y proves the eigensolver is not real-only. Its phase
        // convention makes each mode's largest component real nonnegative.
        const auto state = qmw::DensityState::from_split(
            2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
        const auto h = hamiltonian(2, zeros(4), {0.0, -1.0, 1.0, 0.0});
        const auto first = qmw::analyze_quantum_spectrum(state, 4, h, 4);
        const auto second = qmw::analyze_quantum_spectrum(state, 4, h, 4);
        check_close(first.energy().eigenvalues[0], -1.0, "sigma_y lower eigenvalue");
        check_close(first.energy().eigenvalues[1], 1.0, "sigma_y upper eigenvalue");
        check(first.energy().eigenvectors == second.energy().eigenvectors, "deterministic vectors repeat exactly");
        check(first.energy().eigenvalues == second.energy().eigenvalues, "deterministic ordering repeats exactly");
        for (std::size_t mode = 0; mode < 2; ++mode) {
            std::size_t pivot = 0;
            if (std::abs(first.energy().eigenvectors[2 + mode])
                > std::abs(first.energy().eigenvectors[mode])) {
                pivot = 1;
            }
            const auto value = first.energy().eigenvectors[pivot * 2 + mode];
            check_close(value.imag(), 0.0, "canonical pivot imaginary zero");
            check(value.real() >= 0.0, "canonical pivot nonnegative");
        }
    }

    {
        // Dense complex 4x4 Hermitian fixture H=U diag(E) U^H, where U is the
        // unitary DFT matrix. This exercises repeated complex Jacobi rotations.
        constexpr std::size_t n = 4;
        const std::vector<double> expected {-2.0, -0.5, 1.0, 3.0};
        constexpr double pi = 3.141592653589793238462643383279502884;
        std::vector<qmw::Complex> unitary(n * n);
        for (std::size_t row = 0; row < n; ++row) {
            for (std::size_t mode = 0; mode < n; ++mode) {
                const double angle = 2.0 * pi * static_cast<double>(row * mode) / 4.0;
                unitary[row * n + mode] = std::polar(0.5, angle);
            }
        }
        std::vector<double> h_real(n * n);
        std::vector<double> h_imag(n * n);
        for (std::size_t row = 0; row < n; ++row) {
            for (std::size_t column = 0; column < n; ++column) {
                qmw::Complex value {};
                for (std::size_t mode = 0; mode < n; ++mode) {
                    value += unitary[row * n + mode] * expected[mode]
                        * std::conj(unitary[column * n + mode]);
                }
                h_real[row * n + column] = value.real();
                h_imag[row * n + column] = value.imag();
            }
        }
        const auto h = hamiltonian(n, h_real, h_imag);
        std::vector<double> rho(n * n, 0.0);
        rho[0] = 1.0;
        const auto state = qmw::DensityState::from_split(n, rho, zeros(n * n));
        const auto frame = qmw::analyze_quantum_spectrum(state, 9, h, 9);
        for (std::size_t mode = 0; mode < n; ++mode) {
            check_close(frame.energy().eigenvalues[mode], expected[mode], "dense complex energy eigenvalue", 2.0e-11);
            check_close(frame.energy_populations()[mode], 0.25, "DFT energy population", 2.0e-11);
        }
        check(frame.energy().relative_residual_frobenius < 1.0e-11, "dense complex eigensolver residual");
    }

    {
        const auto state = qmw::DensityState::from_split(
            2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
        const auto zero_h = hamiltonian(2, zeros(4), zeros(4));
        const auto frame = qmw::analyze_quantum_spectrum(state, 1, zero_h, 1);
        check(!frame.energy().mode_labels_stable, "zero-H mode labels explicitly unstable");
        check(frame.energy().near_degenerate_groups.size() == 1, "zero-H degeneracy emitted");
        check(frame.energy().sweeps == 0, "diagonal zero H needs no Jacobi sweep");
    }

    check_code(
        [] {
            const auto state = qmw::DensityState::from_split(2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
            const auto h = hamiltonian(2, zeros(4), zeros(4));
            (void)qmw::analyze_quantum_spectrum(state, 1, h, 2);
        },
        qmw::SpectrumCode::revision_mismatch,
        "mismatched revisions rejected");

    check_code(
        [] {
            const auto state = qmw::DensityState::from_split(2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
            const auto h = hamiltonian(2, zeros(4), zeros(4));
            (void)qmw::analyze_quantum_spectrum(state, -1, h, -1);
        },
        qmw::SpectrumCode::invalid_revision,
        "negative revisions rejected");

    check_code(
        [] {
            const auto state = qmw::DensityState::from_split(2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
            const auto h = hamiltonian(2, zeros(4), zeros(4), "computational_q0_msb");
            (void)qmw::analyze_quantum_spectrum(state, 1, h, 1);
        },
        qmw::SpectrumCode::basis_mismatch,
        "wrong basis rejected rather than reordered");

    check_code(
        [] {
            const auto state = qmw::DensityState::from_split(2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
            const auto h = hamiltonian(4, zeros(16), zeros(16));
            (void)qmw::analyze_quantum_spectrum(state, 1, h, 1);
        },
        qmw::SpectrumCode::dimension_mismatch,
        "dimension mismatch rejected");

    check_code(
        [] {
            const auto state = qmw::DensityState::from_split(2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
            const auto h = hamiltonian(2, zeros(4), zeros(4));
            auto policy = qmw::SpectrumPolicy {};
            policy.relative_eigensolver_tolerance = 0.0;
            (void)qmw::analyze_quantum_spectrum(state, 1, h, 1, policy);
        },
        qmw::SpectrumCode::invalid_policy,
        "invalid policy rejected");

    check_code(
        [] {
            const auto state = qmw::DensityState::from_split(
                4,
                {1.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0},
                zeros(16));
            const auto h = hamiltonian(
                4,
                {0.0, 1.0, 2.0, 3.0,
                 1.0, 4.0, 5.0, 6.0,
                 2.0, 5.0, 7.0, 8.0,
                 3.0, 6.0, 8.0, 9.0},
                zeros(16));
            auto policy = qmw::SpectrumPolicy {};
            policy.maximum_sweeps = 1;
            policy.relative_eigensolver_tolerance = 1.0e-30;
            (void)qmw::analyze_quantum_spectrum(state, 1, h, 1, policy);
        },
        qmw::SpectrumCode::eigensolver_nonconvergence,
        "bounded eigensolver reports nonconvergence");

    {
        constexpr std::size_t n = 64;
        std::vector<double> rho(n * n, 0.0);
        std::vector<double> h_values(n * n, 0.0);
        for (std::size_t index = 0; index < n; ++index) {
            rho[index * n + index] = 1.0 / static_cast<double>(n);
            h_values[index * n + index] = static_cast<double>(index);
        }
        const auto state = qmw::DensityState::from_split(n, rho, zeros(n * n));
        const auto h = hamiltonian(n, h_values, zeros(n * n));
        const auto frame = qmw::analyze_quantum_spectrum(state, 64, h, 64);
        check(frame.dimension() == 64, "dimension-64 bound supported");
        check_close(frame.energy().eigenvalues[63], 63.0, "dimension-64 final energy");
        check_close(frame.entropy_nats(), std::log(64.0), "dimension-64 entropy");
        check_close(frame.participation_rank(), 64.0, "dimension-64 participation");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.spectrum checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_SPECTRUM_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
