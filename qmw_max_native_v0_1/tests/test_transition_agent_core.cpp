#include "qmw/transition.hpp"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <string_view>
#include <vector>

namespace {

int failures = 0;
int checks = 0;

void check(const bool condition, const std::string_view name)
{
    ++checks;
    if (!condition) {
        std::cerr << "FAIL: " << name << '\n';
        ++failures;
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
void check_code(
    Function&& function,
    const qmw::TransitionValidationCode expected,
    const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const qmw::TransitionValidationError& error) {
        check(error.code() == expected, name);
    } catch (...) {
        check(false, name);
    }
}

std::vector<double> zeros(const std::size_t count)
{
    return std::vector<double>(count, 0.0);
}

qmw::TransitionContext context(
    const long revision = 7,
    const char* basis = "computational_q0_lsb")
{
    return {
        revision,
        0.25,
        0.01,
        basis,
        "s",
        "state-and-H-fixture",
        "transition-agent-test",
    };
}

qmw::TransitionUnits units(
    const double hbar = 1.0,
    const char* energy_unit = "model_energy")
{
    return {hbar, energy_unit, "s", "dipole"};
}

qmw::HamiltonianSnapshot hamiltonian(
    const std::vector<double>& real,
    const std::vector<double>& imag = zeros(4),
    const char* basis = "computational_q0_lsb",
    const char* energy_unit = "model_energy")
{
    return qmw::HamiltonianSnapshot::from_split(
        2, real, imag,
        {energy_unit, basis, "H-fixture", "transition-agent-test"});
}

qmw::TransitionOperator declared_operator(
    const std::vector<double>& real,
    const std::vector<double>& imag = zeros(4),
    const qmw::TransitionOperatorKind kind = qmw::TransitionOperatorKind::coupling,
    const long revision = 7,
    const char* basis = "computational_q0_lsb")
{
    return qmw::TransitionOperator::from_split(
        2, real, imag,
        {revision, kind, basis, "dipole", "A-fixture", "transition-agent-test"});
}

const qmw::TransitionEdge* find_edge(
    const std::vector<qmw::TransitionEdge>& edges,
    const std::size_t source,
    const std::size_t target)
{
    for (const auto& edge : edges) {
        if (edge.source == source && edge.target == target) {
            return &edge;
        }
    }
    return nullptr;
}

} // namespace

int main()
{
    const auto ground = qmw::DensityState::from_split(
        2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
    const auto h_z = hamiltonian({-1.0, 0.0, 0.0, 1.0});
    const auto a_x = declared_operator({0.0, 1.0, 1.0, 0.0});

    {
        const auto frame = qmw::analyze_transitions(
            ground, h_z, a_x, context(), units(2.0));
        check(frame.dimension == 2, "frame dimension");
        check(frame.context.revision == 7, "frame revision");
        check(frame.context.source_id == "state-and-H-fixture", "frame source provenance");
        check(frame.operator_metadata.source_id == "A-fixture", "operator source provenance");
        check(frame.units.energy_unit == "model_energy", "energy unit retained");
        check_close(frame.energies[0], -1.0, 1.0e-12, "ascending ground energy");
        check_close(frame.energies[1], 1.0, 1.0e-12, "ascending excited energy");
        check_close(frame.energy_populations[0], 1.0, 1.0e-12, "ground population");
        check_close(frame.energy_populations[1], 0.0, 1.0e-12, "excited population");
        check(frame.edges.size() == 2, "off-diagonal candidate edges");
        const auto* upward = find_edge(frame.edges, 0, 1);
        const auto* downward = find_edge(frame.edges, 1, 0);
        check(upward != nullptr && downward != nullptr, "signed directed edges present");
        check_close(upward->delta_E, 2.0, 1.0e-12, "delta_E = E_target-E_source");
        check_close(upward->omega, 1.0, 1.0e-12, "omega = delta_E/hbar");
        check_close(downward->delta_E, -2.0, 1.0e-12, "downward delta_E signed");
        check_close(downward->omega, -1.0, 1.0e-12, "downward omega signed");
        check_close(upward->magnitude, 1.0, 1.0e-12, "A_mn magnitude");
        check(upward->phase_rad.has_value(), "nonzero A_mn has phase");
        check_close(*upward->phase_rad, 0.0, 1.0e-12, "A_mn phase");
        check_close(upward->matrix_element_squared, 1.0, 1.0e-12, "matrix element squared");
        check_close(upward->diagnostic_activity, 1.0, 1.0e-12, "population-weighted diagnostic");
        check_close(downward->diagnostic_activity, 0.0, 1.0e-12, "empty source diagnostic");
        check(frame.transitions.size() == 1, "threshold admits only populated-source edge");
        check(frame.transitions[0].source == 0 && frame.transitions[0].target == 1,
              "filtered transition order source then target");
        check(frame.activity_name == "population_weighted_matrix_element",
              "diagnostic activity explicitly named");
        check(frame.activity_interpretation.find("not a universal transition rate")
                  != std::string::npos,
              "diagnostic never labeled physical rate");
        check_close(frame.diagnostics.hamiltonian_eigen_residual_fro, 0.0, 1.0e-12,
                    "diagonal eigensystem residual");
    }

    {
        const auto plus = qmw::DensityState::from_split(
            2, {0.5, 0.5, 0.5, 0.5}, zeros(4));
        const auto frame = qmw::analyze_transitions(
            plus, h_z, a_x, context(), units());
        const auto* upward = find_edge(frame.edges, 0, 1);
        check_close(upward->source_population, 0.5, 1.0e-12, "endpoint source population");
        check_close(upward->target_population, 0.5, 1.0e-12, "endpoint target population");
        check_close(upward->coherence_mn.real(), 0.5, 1.0e-12, "rho_mn coherence");
        check_close(upward->coherence_nm.real(), 0.5, 1.0e-12, "rho_nm coherence");
        check(frame.transitions.size() == 2, "both populated directions admitted");
    }

    {
        // Non-diagonal real H exercises the eigensolver and basis transforms.
        const auto h_x = hamiltonian({0.0, 1.0, 1.0, 0.0});
        const auto a_z = declared_operator({1.0, 0.0, 0.0, -1.0});
        const auto frame = qmw::analyze_transitions(
            ground, h_x, a_z, context(), units());
        check_close(frame.energies[0], -1.0, 1.0e-11, "Jacobi low eigenvalue");
        check_close(frame.energies[1], 1.0, 1.0e-11, "Jacobi high eigenvalue");
        check_close(frame.energy_populations[0], 0.5, 1.0e-11, "rotated ground population");
        check_close(frame.energy_populations[1], 0.5, 1.0e-11, "rotated excited population");
        check_close(std::abs(frame.operator_in_energy_basis[1]), 1.0, 1.0e-11,
                    "operator transformed to energy basis");
        check(frame.diagnostics.jacobi_iterations > 0, "Jacobi rotation occurred");
        check(frame.diagnostics.hamiltonian_eigen_residual_fro < 1.0e-11,
              "Jacobi eigen residual bounded");
        check(frame.diagnostics.hamiltonian_reconstruction_residual_fro < 1.0e-11,
              "Jacobi reconstruction residual bounded");
        check(frame.diagnostics.operator_transform_residual_fro < 1.0e-11,
              "operator transform residual bounded");
    }

    {
        // sigma_y exercises a genuinely complex Hermitian eigensystem.
        const auto h_y = hamiltonian(zeros(4), {0.0, -1.0, 1.0, 0.0});
        const auto frame = qmw::analyze_transitions(
            ground, h_y, a_x, context(), units());
        check_close(frame.energies[0], -1.0, 1.0e-11, "complex Jacobi low eigenvalue");
        check_close(frame.energies[1], 1.0, 1.0e-11, "complex Jacobi high eigenvalue");
        check(frame.diagnostics.hamiltonian_eigen_residual_fro < 1.0e-11,
              "complex Jacobi eigen residual bounded");
    }

    {
        // Two independent real/complex blocks exercise sorting and rotations
        // beyond the analytically trivial two-dimensional implementation path.
        const auto rho4 = qmw::DensityState::from_split(
            4,
            {0.25, 0.0, 0.0, 0.0,
             0.0, 0.25, 0.0, 0.0,
             0.0, 0.0, 0.25, 0.0,
             0.0, 0.0, 0.0, 0.25},
            zeros(16));
        const auto h4 = qmw::HamiltonianSnapshot::from_split(
            4,
            {0.0, 1.0, 0.0, 0.0,
             1.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 2.0, 0.0,
             0.0, 0.0, 0.0, 2.0},
            {0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, -1.0,
             0.0, 0.0, 1.0, 0.0},
            {"model_energy", "computational_q0_lsb", "H4", "block-fixture"});
        const auto a4 = qmw::TransitionOperator::from_split(
            4,
            {1.0, 0.0, 0.0, 0.0,
             0.0, 1.0, 0.0, 0.0,
             0.0, 0.0, 1.0, 0.0,
             0.0, 0.0, 0.0, 1.0},
            zeros(16),
            {7, qmw::TransitionOperatorKind::observable,
             "computational_q0_lsb", "dipole", "I4", "block-fixture"});
        const auto frame = qmw::analyze_transitions(
            rho4, h4, a4, context(), units());
        check_close(frame.energies[0], -1.0, 1.0e-11, "4D sorted energy 0");
        check_close(frame.energies[1], 1.0, 1.0e-11, "4D sorted energy 1");
        check_close(frame.energies[2], 1.0, 1.0e-11, "4D sorted energy 2");
        check_close(frame.energies[3], 3.0, 1.0e-11, "4D sorted energy 3");
        check(frame.diagnostics.hamiltonian_eigen_residual_fro < 1.0e-10,
              "4D complex eigensystem residual bounded");
        check(frame.energy_degenerate_groups.size() == 1,
              "4D exact degeneracy grouped");
        check(frame.energy_degenerate_groups[0][0] == 1
                  && frame.energy_degenerate_groups[0][1] == 2,
              "4D degenerate indices follow sorted energies");
    }

    {
        // Dense complex Hermitian fixture exercises repeated Jacobi rotations.
        const auto rho4 = qmw::DensityState::from_split(
            4,
            {0.25, 0.0, 0.0, 0.0,
             0.0, 0.25, 0.0, 0.0,
             0.0, 0.0, 0.25, 0.0,
             0.0, 0.0, 0.0, 0.25},
            zeros(16));
        const auto dense_h = qmw::HamiltonianSnapshot::from_split(
            4,
            {-2.0, 0.3, -0.4, 0.2,
             0.3, -0.5, 0.7, -0.15,
             -0.4, 0.7, 1.0, 0.33,
             0.2, -0.15, 0.33, 3.0},
            {0.0, 0.2, 0.1, -0.3,
             -0.2, 0.0, 0.25, 0.05,
             -0.1, -0.25, 0.0, -0.21,
             0.3, -0.05, 0.21, 0.0},
            {"model_energy", "computational_q0_lsb", "dense-H4", "dense-fixture"});
        const auto identity4 = qmw::TransitionOperator::from_split(
            4,
            {1.0, 0.0, 0.0, 0.0,
             0.0, 1.0, 0.0, 0.0,
             0.0, 0.0, 1.0, 0.0,
             0.0, 0.0, 0.0, 1.0},
            zeros(16),
            {7, qmw::TransitionOperatorKind::observable,
             "computational_q0_lsb", "dipole", "dense-I4", "dense-fixture"});
        const auto frame = qmw::analyze_transitions(
            rho4, dense_h, identity4, context(), units());
        check(frame.diagnostics.jacobi_iterations > 4,
              "dense complex eigensystem uses repeated rotations");
        check(frame.diagnostics.hamiltonian_eigen_residual_fro < 1.0e-10,
              "dense complex eigen residual bounded");
        check(frame.diagnostics.hamiltonian_reconstruction_residual_fro < 1.0e-10,
              "dense complex reconstruction residual bounded");
        check(frame.energies[0] <= frame.energies[1]
                  && frame.energies[1] <= frame.energies[2]
                  && frame.energies[2] <= frame.energies[3],
              "dense complex eigenvalues sorted ascending");
        check_close(frame.energy_populations[0] + frame.energy_populations[1]
                        + frame.energy_populations[2] + frame.energy_populations[3],
                    1.0, 1.0e-11, "dense transform preserves population sum");
    }

    {
        // General coupling is permitted and its zero/nonzero phase policy is explicit.
        const auto lowering = declared_operator({0.0, 1.0, 0.0, 0.0});
        const auto frame = qmw::analyze_transitions(
            ground, h_z, lowering, context(), units());
        check(lowering.hermiticity_residual_fro() > 0.0,
              "non-Hermitian coupling preserved");
        const auto* zero_amplitude = find_edge(frame.edges, 0, 1);
        check(zero_amplitude != nullptr && !zero_amplitude->phase_rad.has_value(),
              "zero amplitude phase is undefined");
    }

    check_code(
        [] {
            (void)declared_operator(
                {0.0, 1.0, 0.0, 0.0}, zeros(4),
                qmw::TransitionOperatorKind::observable);
        },
        qmw::TransitionValidationCode::non_hermitian,
        "declared observable must be Hermitian");

    {
        const auto degenerate_h = hamiltonian(zeros(4));
        const auto no_zero_gap = qmw::analyze_transitions(
            ground, degenerate_h, a_x, context(), units());
        check(no_zero_gap.edges.empty(), "default excludes all zero-gap edges");
        check(no_zero_gap.energy_degenerate_groups.size() == 1,
              "degenerate group reported");
        check(no_zero_gap.energy_degenerate_groups[0].size() == 2,
              "degenerate group membership");

        qmw::TransitionPolicy policy;
        policy.include_zero_gap = true;
        const auto off_diagonal = qmw::analyze_transitions(
            ground, degenerate_h, a_x, context(), units(), policy);
        check(off_diagonal.edges.size() == 2, "zero-gap policy includes off-diagonal edges");
        check(off_diagonal.edges[0].basis_dependent_degenerate_endpoint,
              "degenerate edge labels marked basis-dependent");

        policy.include_diagonal = true;
        const auto including_diagonal = qmw::analyze_transitions(
            ground, degenerate_h, a_x, context(), units(), policy);
        check(including_diagonal.edges.size() == 4,
              "diagonal and zero-gap policies independently explicit");
        check(including_diagonal.transitions.size() == 1,
              "filtered transitions remain strictly off-diagonal");
    }

    {
        // No unit-sized eigensolver floor: tiny SI-valued H remains resolvable.
        const auto tiny_h = hamiltonian(
            {0.0, 1.0e-24, 1.0e-24, 0.0}, zeros(4),
            "computational_q0_lsb", "joule");
        auto si_policy = qmw::TransitionPolicy {};
        // Gap tolerance is expressed in energy_unit, never in Hz.
        si_policy.energy_gap_tolerance = 1.0e-30;
        const auto frame = qmw::analyze_transitions(
            ground, tiny_h, a_x, context(), units(1.0e-34, "joule"), si_policy);
        check_close(frame.energies[0], -1.0e-24, 1.0e-35,
                    "tiny energy low eigenvalue");
        check_close(frame.energies[1], 1.0e-24, 1.0e-35,
                    "tiny energy high eigenvalue");
        check(std::isfinite(frame.edges[0].omega), "tiny SI omega remains finite");
    }

    check_code(
        [&] {
            auto bad = context();
            bad.basis_id = "other-basis";
            (void)qmw::analyze_transitions(ground, h_z, a_x, bad, units());
        },
        qmw::TransitionValidationCode::basis_mismatch,
        "reject basis mismatch");
    check_code(
        [&] {
            auto bad = context(8);
            (void)qmw::analyze_transitions(ground, h_z, a_x, bad, units());
        },
        qmw::TransitionValidationCode::revision_mismatch,
        "reject revision mismatch");
    check_code(
        [&] {
            auto bad = context();
            bad.time_unit = "ms";
            (void)qmw::analyze_transitions(ground, h_z, a_x, bad, units());
        },
        qmw::TransitionValidationCode::time_unit_mismatch,
        "reject time-unit mismatch");
    check_code(
        [&] {
            auto bad_units = units();
            bad_units.hbar = 0.0;
            (void)qmw::analyze_transitions(ground, h_z, a_x, context(), bad_units);
        },
        qmw::TransitionValidationCode::invalid_metadata,
        "reject nonpositive hbar");
    check_code(
        [&] {
            auto bad_policy = qmw::TransitionPolicy {};
            bad_policy.energy_gap_tolerance = -1.0;
            (void)qmw::analyze_transitions(
                ground, h_z, a_x, context(), units(), bad_policy);
        },
        qmw::TransitionValidationCode::invalid_policy,
        "reject negative gap tolerance");

    {
        qmw::RevisionedTransitionStore store(
            2,
            context(-1),
            units(),
            {-1, qmw::TransitionOperatorKind::coupling,
             "computational_q0_lsb", "dipole", "A-stream", "test-transaction"});
        const auto zero = zeros(4);
        check(store.stage_matrix(qmw::TransitionInputPart::rho_real, 20,
                                 {1.0, 0.0, 0.0, 0.0}).status
                  == qmw::TransitionStageStatus::staged,
              "rho real stages");
        check(store.stage_matrix(qmw::TransitionInputPart::rho_imag, 20, zero).status
                  == qmw::TransitionStageStatus::staged,
              "rho imag stages");
        check(store.stage_matrix(qmw::TransitionInputPart::hamiltonian_real, 20,
                                 {-1.0, 0.0, 0.0, 1.0}).status
                  == qmw::TransitionStageStatus::staged,
              "H real stages");
        check(store.stage_matrix(qmw::TransitionInputPart::hamiltonian_imag, 20, zero).status
                  == qmw::TransitionStageStatus::staged,
              "H imag stages");
        check(store.stage_matrix(qmw::TransitionInputPart::operator_real, 20,
                                 {0.0, 1.0, 1.0, 0.0}).status
                  == qmw::TransitionStageStatus::staged,
              "A real stages");
        check(store.stage_matrix(qmw::TransitionInputPart::operator_imag, 20, zero).status
                  == qmw::TransitionStageStatus::staged,
              "A imag stages");
        check(store.active() == nullptr, "six matrices remain invisible without context");
        const auto committed = store.stage_context(20, 3.0, 0.05);
        check(committed.status == qmw::TransitionStageStatus::accepted,
              "seven matching parts commit atomically");
        check(store.active_revision() == 20, "transaction advances active revision");
        check_close(store.active()->context.time, 3.0, 1.0e-14, "transaction time retained");
        check_close(store.active()->context.dt, 0.05, 1.0e-14, "transaction dt retained");
        check(store.active()->operator_metadata.source_id == "A-stream",
              "transaction operator provenance retained");

        const auto stale = store.stage_context(19, 4.0, 0.1);
        check(stale.status == qmw::TransitionStageStatus::rejected,
              "stale transaction context rejected");
        check(stale.detail == "stale_revision", "stale detail stable");

        check(store.stage_matrix(qmw::TransitionInputPart::rho_real, 21,
                                 {1.0, 0.0, 0.0, 0.0}).status
                  == qmw::TransitionStageStatus::staged,
              "new partial transaction stages");
        check(store.stage_matrix(qmw::TransitionInputPart::rho_imag, 22, zero).status
                  == qmw::TransitionStageStatus::staged,
              "mismatched newer transaction stages");
        check(store.active_revision() == 20, "mismatch preserves active frame");
        store.clear_candidate();

        const long bad_revision = 23;
        (void)store.stage_matrix(qmw::TransitionInputPart::rho_real, bad_revision,
                                 {1.0, 0.0, 0.0, 0.0});
        (void)store.stage_matrix(qmw::TransitionInputPart::rho_imag, bad_revision, zero);
        (void)store.stage_matrix(qmw::TransitionInputPart::hamiltonian_real, bad_revision,
                                 {-1.0, 0.5, 0.0, 1.0});
        (void)store.stage_matrix(qmw::TransitionInputPart::hamiltonian_imag, bad_revision, zero);
        (void)store.stage_matrix(qmw::TransitionInputPart::operator_real, bad_revision,
                                 {0.0, 1.0, 1.0, 0.0});
        (void)store.stage_matrix(qmw::TransitionInputPart::operator_imag, bad_revision, zero);
        const auto rejected = store.stage_context(bad_revision, 4.0, 0.1);
        check(rejected.status == qmw::TransitionStageStatus::rejected,
              "invalid complete transaction rejected");
        check(rejected.detail == "hamiltonian_non_hermitian",
              "validation authority visible across transaction boundary");
        check(store.active_revision() == 20, "rejection preserves active revision");
        check_close(store.active()->energies[0], -1.0, 1.0e-12,
                    "rejection preserves active frame values");

        const auto malformed = store.stage_matrix(
            qmw::TransitionInputPart::rho_real, 24, zeros(3));
        check(malformed.status == qmw::TransitionStageStatus::rejected,
              "wrong-size component rejected immediately");
        check(malformed.detail == "wrong_element_count", "wrong-size detail stable");

        auto nonfinite = zeros(4);
        nonfinite[0] = std::numeric_limits<double>::infinity();
        const auto invalid_number = store.stage_matrix(
            qmw::TransitionInputPart::operator_real, 24, nonfinite);
        check(invalid_number.status == qmw::TransitionStageStatus::rejected,
              "nonfinite component rejected immediately");
        check(invalid_number.detail == "non_finite", "nonfinite detail stable");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.transition checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_TRANSITION_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
