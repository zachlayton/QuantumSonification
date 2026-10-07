#include "qmw/flow.hpp"

#include <cmath>
#include <complex>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <string_view>
#include <utility>
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
void check_code(Function&& function, const qmw::FlowCode expected, const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const qmw::FlowError& error) {
        check(error.code() == expected, name);
    } catch (...) {
        check(false, name);
    }
}

std::vector<double> zeros(const std::size_t count)
{
    return std::vector<double>(count, 0.0);
}

qmw::FlowMetadata metadata()
{
    return {
        "joule",
        "second",
        "computational_q0_lsb",
        "declared_discrete_site_basis",
        "flow-test-rho",
        "flow-test-H",
        "analytic-current-fixture",
        "row_target_column_source",
        "q0_lsb",
    };
}

struct Split {
    std::vector<double> real;
    std::vector<double> imag;
};

Split split(const std::vector<std::complex<double>>& values)
{
    Split result;
    result.real.reserve(values.size());
    result.imag.reserve(values.size());
    for (const auto value : values) {
        result.real.push_back(value.real());
        result.imag.push_back(value.imag());
    }
    return result;
}

qmw::FlowSnapshot two_site_fixture(const long revision = 7, const double hbar = 1.0)
{
    // H=X and rho=|+y><+y|. With J_target<-source =
    // 2 Im(H_target,source rho_source,target)/hbar:
    // J_0<-1=+1/hbar and J_1<-0=-1/hbar.
    return qmw::FlowSnapshot::evaluate(
        revision,
        2,
        {0.0, 1.0, 1.0, 0.0},
        zeros(4),
        {0.5, 0.0, 0.0, 0.5},
        {0.0, -0.5, 0.5, 0.0},
        hbar,
        metadata());
}

void stage_fixture(qmw::RevisionedFlowStore& store, const long revision)
{
    static_cast<void>(store.stage(
        qmw::FlowPart::hamiltonian_real,
        revision,
        {0.0, 1.0, 1.0, 0.0}));
    static_cast<void>(store.stage(
        qmw::FlowPart::hamiltonian_imag,
        revision,
        zeros(4)));
    static_cast<void>(store.stage(
        qmw::FlowPart::density_real,
        revision,
        {0.5, 0.0, 0.0, 0.5}));
    static_cast<void>(store.stage(
        qmw::FlowPart::density_imag,
        revision,
        {0.0, -0.5, 0.5, 0.0}));
}

} // namespace

int main()
{
    {
        const auto frame = two_site_fixture();
        check(frame.revision() == 7, "revision retained");
        check(frame.dimension() == 2 && frame.qubits() == 1, "dimension and qubits retained");
        check(frame.metadata().basis_id == "computational_q0_lsb", "basis explicit");
        check(frame.metadata().basis_kind == "declared_discrete_site_basis", "basis kind explicit");
        check(frame.metadata().index_orientation == "row_target_column_source", "index orientation explicit");
        check(frame.metadata().bit_order == "q0_lsb", "bit order explicit");
        check(frame.metadata().state_source_id == "flow-test-rho", "state source explicit");
        check(frame.metadata().hamiltonian_source_id == "flow-test-H", "Hamiltonian source explicit");
        check(frame.metadata().provenance == "analytic-current-fixture", "provenance explicit");
        check(frame.hbar_unit() == "joule*second", "hbar unit derived explicitly");
        check(frame.current_unit() == "1/second", "current unit explicit");
        check_close(frame.current(0, 1), 1.0, 1.0e-14, "positive current source 1 to target 0");
        check_close(frame.current(1, 0), -1.0, 1.0e-14, "reverse current antisymmetric");
        check_close(frame.current(0, 0), 0.0, 0.0, "diagonal current is zero");
        check_close(frame.population_derivative()[0], 1.0, 1.0e-14, "commutator population derivative target 0");
        check_close(frame.population_derivative()[1], -1.0, 1.0e-14, "commutator population derivative target 1");
        check_close(frame.divergence()[0], frame.population_derivative()[0], 1.0e-14, "target 0 continuity identity");
        check_close(frame.divergence()[1], frame.population_derivative()[1], 1.0e-14, "target 1 continuity identity");
        check(frame.directed_edges().size() == 2, "all ordered off-diagonal edges retained");
        check_close(frame.diagnostics().current_antisymmetry_max_abs, 0.0, 1.0e-14, "antisymmetry diagnostic");
        check_close(frame.diagnostics().continuity_residual_max_abs, 0.0, 1.0e-14, "continuity diagnostic");
        check_close(frame.diagnostics().total_population_derivative_abs, 0.0, 1.0e-14, "probability conserved");
        check_close(frame.density().at(1, 0).imag(), 0.5, 0.0, "immutable raw density retained");
        check_close(frame.hamiltonian().at(0, 1).real(), 1.0, 0.0, "immutable raw Hamiltonian retained");
    }

    {
        const auto frame = two_site_fixture(8, 2.0);
        check_close(frame.current(0, 1), 0.5, 1.0e-14, "hbar scales current");
        check_close(frame.population_derivative()[0], 0.5, 1.0e-14, "hbar scales derivative");
    }

    {
        // Local diagonal basis rephasing changes component phases but preserves
        // H_01 rho_10, the transport phase, and the probability current.
        const double coupling_phase = 0.37;
        const double state_phase = -0.81;
        const double theta0 = 0.2;
        const double theta1 = -0.55;
        const auto h01 = std::polar(0.7, coupling_phase);
        const auto rho10 = std::polar(0.5, state_phase);
        auto h = split({{0.0, 0.0}, h01, std::conj(h01), {0.0, 0.0}});
        auto rho = split({{0.5, 0.0}, std::conj(rho10), rho10, {0.5, 0.0}});
        const auto original = qmw::FlowSnapshot::evaluate(
            9, 2, h.real, h.imag, rho.real, rho.imag, 1.0, metadata());

        const auto h01_gauge = std::polar(1.0, theta1 - theta0) * h01;
        const auto rho10_gauge = std::polar(1.0, theta0 - theta1) * rho10;
        h = split({{0.0, 0.0}, h01_gauge, std::conj(h01_gauge), {0.0, 0.0}});
        rho = split({{0.5, 0.0}, std::conj(rho10_gauge), rho10_gauge, {0.5, 0.0}});
        const auto rephased = qmw::FlowSnapshot::evaluate(
            9, 2, h.real, h.imag, rho.real, rho.imag, 1.0, metadata());

        check_close(rephased.current(0, 1), original.current(0, 1), 1.0e-14, "current invariant under local rephasing");
        const auto& edge_original = original.directed_edges()[0];
        const auto& edge_rephased = rephased.directed_edges()[0];
        check(edge_original.coupling_phase.defined && edge_original.coherence_phase.defined, "component phases defined for nonzero factors");
        check(edge_original.transport_phase.defined, "transport phase defined for nonzero product");
        check(std::abs(edge_rephased.coupling_phase.radians - edge_original.coupling_phase.radians) > 0.1, "coupling phase changes with gauge");
        check(std::abs(edge_rephased.coherence_phase.radians - edge_original.coherence_phase.radians) > 0.1, "coherence phase changes with gauge");
        check_close(edge_rephased.transport_phase.radians, edge_original.transport_phase.radians, 1.0e-14, "transport phase is local-rephasing invariant");
        check(edge_original.component_phases_local_gauge_dependent, "component gauge caveat explicit");
        check(edge_original.transport_phase_local_rephasing_invariant, "transport gauge property explicit");
    }

    {
        const auto no_flow = qmw::FlowSnapshot::evaluate(
            10,
            2,
            {2.0, 0.0, 0.0, -2.0},
            zeros(4),
            {0.8, 0.0, 0.0, 0.2},
            zeros(4),
            1.0,
            metadata());
        check(no_flow.directed_edges().size() == 2, "zero-current edges are not threshold-pruned");
        check_close(no_flow.current(0, 1), 0.0, 0.0, "diagonal H has no site current");
        check(!no_flow.directed_edges()[0].transport_phase.defined, "zero transport product has no invented phase");
    }

    {
        // In a four-state q0-LSB basis, only the declared 0<->1 block flows.
        auto h_real = zeros(16);
        h_real[1] = 1.0;
        h_real[4] = 1.0;
        auto rho_real = zeros(16);
        auto rho_imag = zeros(16);
        rho_real[0] = 0.5;
        rho_real[5] = 0.5;
        rho_imag[1] = -0.5;
        rho_imag[4] = 0.5;
        const auto frame = qmw::FlowSnapshot::evaluate(
            11, 4, h_real, zeros(16), rho_real, rho_imag, 1.0, metadata());
        check(frame.qubits() == 2, "four sites retain two-qubit q0-LSB declaration");
        check_close(frame.current(0, 1), 1.0, 1.0e-14, "index 1 is q0 excitation in q0-LSB ordering");
        check_close(frame.current(0, 2), 0.0, 0.0, "unconnected q1 site has no flow");
    }

    check_code(
        [] { static_cast<void>(two_site_fixture(-1)); },
        qmw::FlowCode::invalid_revision,
        "negative revision rejected");
    check_code(
        [] { static_cast<void>(qmw::FlowSnapshot::evaluate(0, 3, zeros(9), zeros(9), zeros(9), zeros(9), 1.0)); },
        qmw::FlowCode::invalid_dimension,
        "non-power-of-two dimension rejected");
    check_code(
        [] { static_cast<void>(qmw::FlowSnapshot::evaluate(0, 2, zeros(3), zeros(3), {1.0, 0.0, 0.0, 0.0}, zeros(4), 1.0)); },
        qmw::FlowCode::wrong_element_count,
        "wrong matrix size rejected");
    check_code(
        [] { static_cast<void>(qmw::FlowSnapshot::evaluate(0, 2, {0.0, 1.0, 0.0, 0.0}, zeros(4), {1.0, 0.0, 0.0, 0.0}, zeros(4), 1.0)); },
        qmw::FlowCode::non_hermitian,
        "non-Hermitian Hamiltonian rejected");
    check_code(
        [] { static_cast<void>(qmw::FlowSnapshot::evaluate(0, 2, zeros(4), zeros(4), {0.75, 0.0, 0.0, 0.75}, zeros(4), 1.0)); },
        qmw::FlowCode::trace_not_one,
        "unnormalized density rejected");
    check_code(
        [] { static_cast<void>(qmw::FlowSnapshot::evaluate(0, 2, zeros(4), zeros(4), {1.1, 0.0, 0.0, -0.1}, zeros(4), 1.0)); },
        qmw::FlowCode::not_positive_semidefinite,
        "nonpositive density rejected");
    check_code(
        [] { auto bad = zeros(4); bad[0] = std::numeric_limits<double>::infinity(); static_cast<void>(qmw::FlowSnapshot::evaluate(0, 2, bad, zeros(4), {1.0, 0.0, 0.0, 0.0}, zeros(4), 1.0)); },
        qmw::FlowCode::non_finite,
        "non-finite matrix rejected");
    check_code(
        [] { static_cast<void>(qmw::FlowSnapshot::evaluate(0, 2, zeros(4), zeros(4), {1.0, 0.0, 0.0, 0.0}, zeros(4), 0.0)); },
        qmw::FlowCode::invalid_hbar,
        "nonpositive hbar rejected");
    check_code(
        [] { static_cast<void>(qmw::FlowSnapshot::evaluate(0, 2, {0.0, 1.0, 1.0, 0.0}, zeros(4), {0.5, 0.0, 0.0, 0.5}, {0.0, -0.5, 0.5, 0.0}, 1.0e-320)); },
        qmw::FlowCode::numerical_inconsistency,
        "non-finite derived current rejected");
    check_code(
        [] { auto bad = metadata(); bad.index_orientation = "row_source_column_target"; static_cast<void>(qmw::FlowSnapshot::evaluate(0, 2, zeros(4), zeros(4), {1.0, 0.0, 0.0, 0.0}, zeros(4), 1.0, bad)); },
        qmw::FlowCode::invalid_metadata,
        "ambiguous index orientation rejected");
    check_code(
        [] { auto bad = metadata(); bad.bit_order = "q0_msb"; static_cast<void>(qmw::FlowSnapshot::evaluate(0, 2, zeros(4), zeros(4), {1.0, 0.0, 0.0, 0.0}, zeros(4), 1.0, bad)); },
        qmw::FlowCode::invalid_metadata,
        "non-q0-LSB declaration rejected");

    {
        qmw::RevisionedFlowStore store(2, 1.0, metadata());
        check(store.stage(qmw::FlowPart::hamiltonian_real, 20, {0.0, 1.0, 1.0, 0.0}).status == qmw::FlowStageStatus::staged, "component stages invisibly");
        check(store.active() == nullptr, "staging does not publish a partial frame");
        check(store.commit(20).detail == "incomplete_transaction", "incomplete commit rejected");
        check(store.active() == nullptr, "incomplete commit leaves no active frame");
        stage_fixture(store, 20);
        const auto accepted = store.commit(20);
        check(accepted.status == qmw::FlowStageStatus::accepted, "complete transaction accepted atomically");
        check(store.active_revision() == 20, "active revision advances");
        check_close(store.active()->current(0, 1), 1.0, 1.0e-14, "active flow is correct");
        check(store.stage(qmw::FlowPart::density_real, 20, {0.5, 0.0, 0.0, 0.5}).detail == "stale_revision", "stale component rejected");

        stage_fixture(store, 21);
        static_cast<void>(store.stage(qmw::FlowPart::density_imag, 22, {0.0, -0.5, 0.5, 0.0}));
        check(store.commit(21).detail == "revision_mismatch", "mixed revisions rejected");
        check(store.active_revision() == 20, "revision mismatch preserves active frame");

        store.clear_candidate();
        stage_fixture(store, 22);
        static_cast<void>(store.stage(
            qmw::FlowPart::hamiltonian_real,
            22,
            {0.0, 1.0, 0.0, 0.0}));
        check(store.commit(22).detail == "non_hermitian", "invalid complete frame rejected");
        check(store.active_revision() == 20, "validation failure preserves active revision");
        check_close(store.active()->current(0, 1), 1.0, 1.0e-14, "validation failure preserves active data");

        store.clear_candidate();
        stage_fixture(store, 23);
        check(store.commit(23).status == qmw::FlowStageStatus::accepted, "clear permits clean later transaction");
        check(store.active_revision() == 23, "later accepted revision active");
    }

    {
        const auto frame = two_site_fixture();
        try {
            static_cast<void>(frame.current(2, 0));
            check(false, "current bounds checked");
        } catch (const std::out_of_range&) {
            check(true, "current bounds checked");
        } catch (...) {
            check(false, "current bounds checked");
        }
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.flow checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_FLOW_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
