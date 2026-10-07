#pragma once

#include "qmw/hamiltonian.hpp"
#include "qmw/state.hpp"

#include <cstddef>
#include <stdexcept>
#include <string>
#include <string_view>

namespace qmw {

enum class EvolutionCode {
    invalid_policy,
    invalid_revision,
    invalid_step,
    invalid_time_unit,
    invalid_hbar,
    dimension_mismatch,
    basis_mismatch,
    generator_too_large,
    linear_solve_failed,
    non_finite_result,
    unitarity_not_preserved,
    trace_not_preserved,
    norm_not_preserved,
    output_state_invalid,
};

[[nodiscard]] std::string_view evolution_code_name(EvolutionCode code) noexcept;

class EvolutionError final : public std::runtime_error {
public:
    EvolutionError(EvolutionCode code, std::string message);

    [[nodiscard]] EvolutionCode code() const noexcept { return code_; }

private:
    EvolutionCode code_;
};

struct EvolutionRequest {
    long state_revision {-1};
    long hamiltonian_revision {-1};
    long candidate_revision {-1};
    double dt {};
    // No conversion is implicit. hbar is expressed in
    // HamiltonianMetadata::energy_unit multiplied by this time unit.
    std::string time_unit {"model_time"};
    double hbar {1.0};
};

struct EvolutionPolicy {
    double unitarity_tolerance {1.0e-10};
    double trace_preservation_tolerance {1.0e-9};
    double frobenius_norm_preservation_tolerance {1.0e-9};
    std::size_t maximum_scaling_squarings {32};
    ValidationPolicy output_state_policy {
        1.0e-9,
        1.0e-9,
        1.0e-9,
        64,
    };
};

struct EvolutionDiagnostics {
    int pade_order {13};
    std::size_t scaling_squarings {};
    double dimensionless_generator_one_norm {};
    double unitarity_residual_relative_fro {};
    double trace_drift {};
    double frobenius_norm_drift {};
    double relative_frobenius_norm_drift {};
    double purity_drift {};
    double output_hermiticity_residual {};
    double output_minimum_ldlt_pivot {};
};

class EvolutionCandidate final {
public:
    EvolutionCandidate(
        DensityState state,
        EvolutionRequest request,
        std::string energy_unit,
        EvolutionDiagnostics diagnostics);

    [[nodiscard]] const DensityState& state() const noexcept { return state_; }
    [[nodiscard]] const EvolutionRequest& request() const noexcept { return request_; }
    [[nodiscard]] const std::string& energy_unit() const noexcept { return energy_unit_; }
    [[nodiscard]] const EvolutionDiagnostics& diagnostics() const noexcept { return diagnostics_; }

private:
    DensityState state_;
    EvolutionRequest request_;
    std::string energy_unit_;
    EvolutionDiagnostics diagnostics_;
};

// Computes rho' = exp(-i H dt / hbar) rho exp(+i H dt / hbar).
// Input and output matrices remain row-major and computational_q0_lsb.
// This returns a candidate only; it never mutates or commits the input state.
[[nodiscard]] EvolutionCandidate evolve_closed_system(
    const DensityState& state,
    const HamiltonianSnapshot& hamiltonian,
    EvolutionRequest request,
    EvolutionPolicy policy = {});

} // namespace qmw
