#include "qmw/evolve.hpp"

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
    const double tolerance,
    const std::string_view name)
{
    check(std::abs(actual - expected) <= tolerance, name);
}

template <typename Function>
void check_evolution_code(
    Function&& function,
    const qmw::EvolutionCode expected,
    const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const qmw::EvolutionError& error) {
        check(error.code() == expected, name);
    } catch (...) {
        check(false, name);
    }
}

std::vector<double> zeros(const std::size_t count)
{
    return std::vector<double>(count, 0.0);
}

qmw::EvolutionRequest request(
    const long state_revision = 7,
    const long hamiltonian_revision = 3,
    const long candidate_revision = 8,
    const double dt = 0.0,
    const char* time_unit = "model_time",
    const double hbar = 1.0)
{
    return {
        state_revision,
        hamiltonian_revision,
        candidate_revision,
        dt,
        time_unit,
        hbar,
    };
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
            "model_energy",
            basis,
            "evolve-test",
            "deterministic-fixture",
        });
}

} // namespace

int main()
{
    constexpr double pi = 3.141592653589793238462643383279502884;

    {
        // H=Z and rho=|+><+|: rho_01 -> rho_01 exp(-2 i dt).
        const auto state = qmw::DensityState::from_split(
            2,
            {0.5, 0.5, 0.5, 0.5},
            zeros(4));
        const auto h = hamiltonian(2, {1.0, 0.0, 0.0, -1.0}, zeros(4));
        const auto output = qmw::evolve_closed_system(
            state, h, request(7, 3, 8, pi / 4.0));

        check(output.request().state_revision == 7, "state revision retained");
        check(output.request().hamiltonian_revision == 3, "Hamiltonian revision retained");
        check(output.request().candidate_revision == 8, "candidate revision retained");
        check(output.request().time_unit == "model_time", "time unit retained");
        check(output.energy_unit() == "model_energy", "energy unit retained");
        check_close(output.state().at(0, 0).real(), 0.5, 1.0e-13, "Z evolution population 0");
        check_close(output.state().at(1, 1).real(), 0.5, 1.0e-13, "Z evolution population 1");
        check_close(output.state().at(0, 1).real(), 0.0, 1.0e-13, "Z evolution coherence real");
        check_close(output.state().at(0, 1).imag(), -0.5, 1.0e-13, "Z evolution coherence phase");
        check_close(output.state().at(1, 0).imag(), 0.5, 1.0e-13, "Hermitian conjugate phase");
        check(output.diagnostics().pade_order == 13, "Pad\u00e9 order is explicit");
        check(output.diagnostics().unitarity_residual_relative_fro < 1.0e-14, "unitarity diagnostic small");
        check(output.diagnostics().trace_drift < 1.0e-14, "trace drift diagnostic small");
        check(output.diagnostics().relative_frobenius_norm_drift < 1.0e-14, "norm drift diagnostic small");
        check(output.diagnostics().purity_drift < 1.0e-14, "purity drift diagnostic small");
        check_close(state.at(0, 1).real(), 0.5, 0.0, "input state remains immutable");
    }

    {
        // sigma_y contains a genuinely imaginary Hamiltonian and rotates
        // |0> to |1> at pi/2 without requiring a real-only shortcut.
        const auto state = qmw::DensityState::from_split(
            2,
            {1.0, 0.0, 0.0, 0.0},
            zeros(4));
        const auto h = hamiltonian(
            2,
            zeros(4),
            {0.0, -1.0, 1.0, 0.0});
        const auto output = qmw::evolve_closed_system(
            state, h, request(1, 9, 2, pi / 2.0));
        check_close(output.state().at(0, 0).real(), 0.0, 1.0e-13, "Y rotation removes ground population");
        check_close(output.state().at(1, 1).real(), 1.0, 1.0e-13, "Y rotation reaches excited population");
    }

    {
        // Four-dimensional X on q0 swaps adjacent row-major basis indices:
        // |q1 q0>=|00> evolves to |01>, index 1. No bit reversal occurs.
        const auto state = qmw::DensityState::from_split(
            4,
            {1.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0},
            zeros(16));
        const auto h = hamiltonian(
            4,
            {0.0, 1.0, 0.0, 0.0,
             1.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 1.0,
             0.0, 0.0, 1.0, 0.0},
            zeros(16));
        const auto output = qmw::evolve_closed_system(
            state, h, request(4, 5, 6, pi / 2.0));
        check_close(output.state().at(1, 1).real(), 1.0, 1.0e-13, "q0-LSB X0 reaches basis index 1");
        check_close(output.state().at(2, 2).real(), 0.0, 1.0e-13, "q0-LSB does not reverse to index 2");
    }

    {
        // A large generator exercises scaling and squaring. The analytic
        // coherence phase is still exact to floating-point tolerance.
        const auto state = qmw::DensityState::from_split(
            2,
            {0.5, 0.5, 0.5, 0.5},
            zeros(4));
        const auto h = hamiltonian(2, {1.0, 0.0, 0.0, -1.0}, zeros(4));
        constexpr double dt = 100.0;
        const auto output = qmw::evolve_closed_system(
            state, h, request(1, 1, 2, dt));
        check(output.diagnostics().scaling_squarings > 0, "large generator records scaling squarings");
        check_close(output.state().at(0, 1).real(), 0.5 * std::cos(2.0 * dt), 2.0e-13, "scaled large-step real phase");
        check_close(output.state().at(0, 1).imag(), -0.5 * std::sin(2.0 * dt), 2.0e-13, "scaled large-step imaginary phase");
    }

    {
        // Admission tolerances do not authorize repair. With dt=0, a tiny
        // admitted asymmetry must survive byte-for-byte through evolution.
        const auto state = qmw::DensityState::from_split(
            2,
            {0.5, 2.0e-12, 1.0e-12, 0.5},
            zeros(4));
        const auto h = hamiltonian(2, zeros(4), zeros(4));
        const auto output = qmw::evolve_closed_system(
            state, h, request(5, 6, 7, 0.0));
        check(output.state().at(0, 1).real() == 2.0e-12, "upper coherence is not repaired");
        check(output.state().at(1, 0).real() == 1.0e-12, "lower coherence is not repaired");
    }

    {
        // Zero H makes the 64-dimensional upper bound inexpensive while
        // proving that the admission and row-major paths handle the limit.
        constexpr std::size_t dimension = 64;
        std::vector<double> rho_real(dimension * dimension, 0.0);
        for (std::size_t index = 0; index < dimension; ++index) {
            rho_real[index * dimension + index] = 1.0 / static_cast<double>(dimension);
        }
        const auto state = qmw::DensityState::from_split(
            dimension, rho_real, zeros(dimension * dimension));
        const auto h = hamiltonian(
            dimension, zeros(dimension * dimension), zeros(dimension * dimension));
        const auto output = qmw::evolve_closed_system(
            state, h, request(10, 11, 12, 1.0, "s", 1.0));
        check(output.state().dimension() == 64, "dimension 64 is supported");
        check_close(output.state().at(63, 63).real(), 1.0 / 64.0, 0.0, "dimension-64 state unchanged");
    }

    {
        const auto state = qmw::DensityState::from_split(
            2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
        const auto h = hamiltonian(2, {1.0, 0.0, 0.0, -1.0}, zeros(4));
        const auto zero_step = qmw::evolve_closed_system(
            state, h, request(2, 3, 4, 0.0, "ns", 6.582119569e-7));
        check_close(zero_step.state().at(0, 0).real(), 1.0, 0.0, "zero dt is explicit identity evolution");
        check(zero_step.request().time_unit == "ns", "arbitrary explicit time symbol retained");
        check_close(zero_step.request().hbar, 6.582119569e-7, 0.0, "explicit hbar retained");

        check_evolution_code(
            [&] { static_cast<void>(qmw::evolve_closed_system(state, h, request(-1, 3, 4, 0.1))); },
            qmw::EvolutionCode::invalid_revision,
            "negative state revision rejected");
        check_evolution_code(
            [&] { static_cast<void>(qmw::evolve_closed_system(state, h, request(2, 3, 2, 0.1))); },
            qmw::EvolutionCode::invalid_revision,
            "non-new candidate revision rejected");
        check_evolution_code(
            [&] {
                static_cast<void>(qmw::evolve_closed_system(
                    state,
                    h,
                    request(2, 3, 4, std::numeric_limits<double>::infinity())));
            },
            qmw::EvolutionCode::invalid_step,
            "non-finite dt rejected");
        check_evolution_code(
            [&] { static_cast<void>(qmw::evolve_closed_system(state, h, request(2, 3, 4, 0.1, " "))); },
            qmw::EvolutionCode::invalid_time_unit,
            "blank time unit rejected");
        check_evolution_code(
            [&] { static_cast<void>(qmw::evolve_closed_system(state, h, request(2, 3, 4, 0.1, "s", 0.0))); },
            qmw::EvolutionCode::invalid_hbar,
            "nonpositive hbar rejected");

        auto bad_policy = qmw::EvolutionPolicy {};
        bad_policy.unitarity_tolerance = 0.0;
        check_evolution_code(
            [&] { static_cast<void>(qmw::evolve_closed_system(state, h, request(2, 3, 4, 0.1), bad_policy)); },
            qmw::EvolutionCode::invalid_policy,
            "invalid evolution policy rejected");

        auto bounded_policy = qmw::EvolutionPolicy {};
        bounded_policy.maximum_scaling_squarings = 0;
        check_evolution_code(
            [&] { static_cast<void>(qmw::evolve_closed_system(state, h, request(2, 3, 4, 100.0), bounded_policy)); },
            qmw::EvolutionCode::generator_too_large,
            "configured scaling bound enforced");
    }

    {
        const auto state2 = qmw::DensityState::from_split(
            2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
        const auto state1 = qmw::DensityState::from_split(1, {1.0}, {0.0});
        const auto h2 = hamiltonian(2, zeros(4), zeros(4));
        check_evolution_code(
            [&] { static_cast<void>(qmw::evolve_closed_system(state1, h2, request(1, 1, 2, 0.1))); },
            qmw::EvolutionCode::dimension_mismatch,
            "state and Hamiltonian dimension mismatch rejected");

        const auto wrong_basis = hamiltonian(
            2, zeros(4), zeros(4), "computational_q0_msb");
        check_evolution_code(
            [&] { static_cast<void>(qmw::evolve_closed_system(state2, wrong_basis, request(1, 1, 2, 0.1))); },
            qmw::EvolutionCode::basis_mismatch,
            "q0-MSB Hamiltonian rejected rather than reordered");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.evolve checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_EVOLVE_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
