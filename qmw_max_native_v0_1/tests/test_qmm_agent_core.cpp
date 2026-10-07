#include "qmw/qmm.hpp"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <optional>
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
void check_code(Function&& function, const qmw::QmmCode expected, const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const qmw::QmmError& error) {
        check(error.code() == expected, name);
    } catch (...) {
        check(false, name);
    }
}

std::vector<double> zeros(const std::size_t count)
{
    return std::vector<double>(count, 0.0);
}

qmw::QmmMetadata metadata()
{
    return {
        "joule",
        "second",
        "magnetic_moment",
        "computational_q0_lsb",
        "qmm-test-source",
        "analytic-Pauli-fixture",
    };
}

qmw::QmmMatrixSplit split(
    std::vector<double> real,
    std::vector<double> imag = zeros(4))
{
    return {std::move(real), std::move(imag)};
}

qmw::QmmSnapshot pauli_fixture(const long revision = 7)
{
    // H=Z/2, rho=|+y><+y|, A=X, hbar=1.
    // [H,A]=iY and dA/dt=i[H,A]=-Y, hence d<X>/dt=-1.
    return qmw::QmmSnapshot::evaluate(
        revision,
        2,
        split({0.5, 0.0, 0.0, -0.5}),
        split({0.5, 0.0, 0.0, 0.5}, {0.0, -0.5, 0.5, 0.0}),
        split({0.0, 1.0, 1.0, 0.0}),
        std::nullopt,
        1.0,
        metadata());
}

void stage_required(
    qmw::RevisionedQmmStore& store,
    const long revision,
    const std::vector<double>& h_real,
    const std::vector<double>& rho_real,
    const std::vector<double>& rho_imag,
    const std::vector<double>& a_real)
{
    const auto zero = zeros(4);
    static_cast<void>(store.stage(qmw::QmmPart::hamiltonian_real, revision, h_real));
    static_cast<void>(store.stage(qmw::QmmPart::hamiltonian_imag, revision, zero));
    static_cast<void>(store.stage(qmw::QmmPart::density_real, revision, rho_real));
    static_cast<void>(store.stage(qmw::QmmPart::density_imag, revision, rho_imag));
    static_cast<void>(store.stage(qmw::QmmPart::observable_real, revision, a_real));
    static_cast<void>(store.stage(qmw::QmmPart::observable_imag, revision, zero));
}

} // namespace

int main()
{
    {
        auto h_real = std::vector<double> {0.5, 0.0, 0.0, -0.5};
        auto snapshot = qmw::QmmSnapshot::evaluate(
            7,
            2,
            split(h_real),
            split({0.5, 0.0, 0.0, 0.5}, {0.0, -0.5, 0.5, 0.0}),
            split({0.0, 1.0, 1.0, 0.0}),
            std::nullopt,
            1.0,
            metadata());
        h_real[0] = 99.0;

        check(snapshot.revision() == 7, "revision retained");
        check(snapshot.dimension() == 2 && snapshot.qubits() == 1, "dimension and qubits retained");
        check_close(snapshot.hamiltonian().at(0, 0).real(), 0.5, 0.0, "raw H copied immutably");
        check_close(snapshot.density().at(0, 1).imag(), -0.5, 0.0, "raw rho retained");
        check_close(snapshot.observable().at(0, 1).real(), 1.0, 0.0, "raw observable retained");
        check(!snapshot.has_explicit_partial(), "absent partial is explicit metadata");
        check(snapshot.hbar_unit() == "joule*second", "hbar unit is explicit");
        check(snapshot.derivative_unit() == "magnetic_moment/second", "derivative unit is explicit");
        check(snapshot.metadata().basis_id == "computational_q0_lsb", "basis retained");
        check(snapshot.metadata().source_id == "qmm-test-source", "source retained");
        check(snapshot.metadata().provenance == "analytic-Pauli-fixture", "provenance retained");
        check_close(snapshot.commutator().at(0, 1).real(), 1.0, 1.0e-14, "commutator upper entry");
        check_close(snapshot.commutator().at(1, 0).real(), -1.0, 1.0e-14, "commutator lower entry");
        check_close(snapshot.derivative().at(0, 1).imag(), 1.0, 1.0e-14, "Heisenberg derivative upper entry");
        check_close(snapshot.derivative().at(1, 0).imag(), -1.0, 1.0e-14, "Heisenberg derivative lower entry");
        check_close(snapshot.expectation_derivative().real(), -1.0, 1.0e-14, "expectation derivative analytic result");
        check_close(snapshot.expectation_derivative().imag(), 0.0, 1.0e-14, "expectation derivative is real");
        check_close(snapshot.diagnostics().commutator_antihermiticity_residual_fro, 0.0, 1.0e-14, "commutator anti-Hermitian");
        check_close(snapshot.diagnostics().derivative_hermiticity_residual_fro, 0.0, 1.0e-14, "derivative Hermitian");
        check_close(snapshot.diagnostics().density_trace.real(), 1.0, 1.0e-14, "density trace diagnostic");
    }

    {
        // H=0 isolates the explicit partial term. rho=|0><0| and
        // partial_t A=Z/4 give d<A>/dt=1/4 exactly.
        const auto snapshot = qmw::QmmSnapshot::evaluate(
            8,
            2,
            split(zeros(4)),
            split({1.0, 0.0, 0.0, 0.0}),
            split({0.0, 1.0, 1.0, 0.0}),
            split({0.25, 0.0, 0.0, -0.25}),
            3.0,
            metadata());
        check(snapshot.has_explicit_partial(), "explicit partial recorded");
        check_close(snapshot.partial()->at(1, 1).real(), -0.25, 0.0, "partial matrix preserved");
        check_close(snapshot.derivative().at(0, 0).real(), 0.25, 0.0, "partial contributes to derivative");
        check_close(snapshot.expectation_derivative().real(), 0.25, 0.0, "partial contributes to expectation derivative");
    }

    {
        const auto snapshot = qmw::QmmSnapshot::evaluate(
            9,
            2,
            split({1.0, 0.0, 0.0, -1.0}),
            split({0.5, 0.0, 0.0, 0.5}, {0.0, -0.5, 0.5, 0.0}),
            split({0.0, 1.0, 1.0, 0.0}),
            std::nullopt,
            2.0,
            metadata());
        check_close(snapshot.expectation_derivative().real(), -1.0, 1.0e-14, "explicit hbar scales commutator term");
    }

    check_code(
        [] { static_cast<void>(qmw::QmmSnapshot::evaluate(-1, 2, split(zeros(4)), split({1.0, 0.0, 0.0, 0.0}), split(zeros(4)), std::nullopt, 1.0)); },
        qmw::QmmCode::invalid_revision,
        "negative revision rejected");
    check_code(
        [] { static_cast<void>(qmw::QmmSnapshot::evaluate(0, 3, split(zeros(9), zeros(9)), split(zeros(9), zeros(9)), split(zeros(9), zeros(9)), std::nullopt, 1.0)); },
        qmw::QmmCode::invalid_dimension,
        "non-power-of-two dimension rejected");
    check_code(
        [] { static_cast<void>(qmw::QmmSnapshot::evaluate(0, 2, split(zeros(3), zeros(3)), split({1.0, 0.0, 0.0, 0.0}), split(zeros(4)), std::nullopt, 1.0)); },
        qmw::QmmCode::wrong_element_count,
        "wrong element count rejected");
    check_code(
        [] { static_cast<void>(qmw::QmmSnapshot::evaluate(0, 2, split({0.0, 1.0, 0.0, 0.0}), split({1.0, 0.0, 0.0, 0.0}), split(zeros(4)), std::nullopt, 1.0)); },
        qmw::QmmCode::non_hermitian,
        "non-Hermitian Hamiltonian rejected");
    check_code(
        [] { static_cast<void>(qmw::QmmSnapshot::evaluate(0, 2, split(zeros(4)), split({1.0, 0.0, 0.0, 0.0}), split({0.0, 1.0, 0.0, 0.0}), std::nullopt, 1.0)); },
        qmw::QmmCode::non_hermitian,
        "non-Hermitian observable rejected");
    check_code(
        [] { static_cast<void>(qmw::QmmSnapshot::evaluate(0, 2, split(zeros(4)), split({1.0, 0.0, 0.0, 0.0}), split(zeros(4)), split({0.0, 1.0, 0.0, 0.0}), 1.0)); },
        qmw::QmmCode::non_hermitian,
        "non-Hermitian partial rejected");
    check_code(
        [] { static_cast<void>(qmw::QmmSnapshot::evaluate(0, 2, split(zeros(4)), split({0.75, 0.0, 0.0, 0.75}), split(zeros(4)), std::nullopt, 1.0)); },
        qmw::QmmCode::trace_not_one,
        "unnormalized density rejected");
    check_code(
        [] { static_cast<void>(qmw::QmmSnapshot::evaluate(0, 2, split(zeros(4)), split({1.1, 0.0, 0.0, -0.1}), split(zeros(4)), std::nullopt, 1.0)); },
        qmw::QmmCode::not_positive_semidefinite,
        "nonpositive density rejected");
    check_code(
        [] { auto bad = zeros(4); bad[0] = std::numeric_limits<double>::infinity(); static_cast<void>(qmw::QmmSnapshot::evaluate(0, 2, split(bad), split({1.0, 0.0, 0.0, 0.0}), split(zeros(4)), std::nullopt, 1.0)); },
        qmw::QmmCode::non_finite,
        "non-finite input rejected");
    check_code(
        [] { static_cast<void>(qmw::QmmSnapshot::evaluate(0, 2, split(zeros(4)), split({1.0, 0.0, 0.0, 0.0}), split(zeros(4)), std::nullopt, 0.0)); },
        qmw::QmmCode::invalid_hbar,
        "nonpositive hbar rejected");
    check_code(
        [] { auto value = metadata(); value.time_unit = " "; static_cast<void>(qmw::QmmSnapshot::evaluate(0, 2, split(zeros(4)), split({1.0, 0.0, 0.0, 0.0}), split(zeros(4)), std::nullopt, 1.0, value)); },
        qmw::QmmCode::invalid_metadata,
        "blank unit metadata rejected");

    {
        qmw::RevisionedQmmStore store(2, 1.0, metadata());
        const auto zero = zeros(4);
        const std::vector<double> h {0.5, 0.0, 0.0, -0.5};
        const std::vector<double> rho {0.5, 0.0, 0.0, 0.5};
        const std::vector<double> rho_i {0.0, -0.5, 0.5, 0.0};
        const std::vector<double> a {0.0, 1.0, 1.0, 0.0};

        check(store.stage(qmw::QmmPart::hamiltonian_real, 10, h).status == qmw::QmmStageStatus::staged, "component stages invisibly");
        check(store.commit(10).detail == "incomplete_transaction", "incomplete transaction rejected");
        check(store.active() == nullptr, "incomplete transaction has no active snapshot");
        static_cast<void>(store.stage(qmw::QmmPart::hamiltonian_imag, 10, zero));
        static_cast<void>(store.stage(qmw::QmmPart::density_real, 10, rho));
        static_cast<void>(store.stage(qmw::QmmPart::density_imag, 10, rho_i));
        static_cast<void>(store.stage(qmw::QmmPart::observable_real, 10, a));
        static_cast<void>(store.stage(qmw::QmmPart::observable_imag, 10, zero));
        const auto accepted = store.commit(10);
        check(accepted.status == qmw::QmmStageStatus::accepted, "complete transaction commits atomically");
        check(store.active_revision() == 10, "active revision advances on commit");
        check_close(store.active()->expectation_derivative().real(), -1.0, 1.0e-14, "active result exact");
        check(store.stage(qmw::QmmPart::density_real, 9, rho).detail == "stale_revision", "stale component rejected");

        stage_required(store, 11, h, rho, rho_i, a);
        static_cast<void>(store.stage(qmw::QmmPart::partial_real, 11, zero));
        const auto incomplete_partial = store.commit(11);
        check(incomplete_partial.detail == "partial_pair_incomplete", "half-present partial rejected");
        check(store.active_revision() == 10, "partial failure preserves active revision");
        static_cast<void>(store.stage(qmw::QmmPart::partial_imag, 12, zero));
        check(store.commit(11).detail == "revision_mismatch", "partial revision mismatch rejected");
        check(store.active_revision() == 10, "revision mismatch preserves active snapshot");

        store.clear_candidate();
        stage_required(store, 12, h, rho, rho_i, a);
        const auto no_partial = store.commit(12);
        check(no_partial.status == qmw::QmmStageStatus::accepted, "cleared transaction commits without partial");
        check(!store.active()->has_explicit_partial(), "omitted partial remains distinguishable from explicit pair");

        stage_required(store, 13, {0.0, 1.0, 0.0, 0.0}, rho, rho_i, a);
        const auto invalid = store.commit(13);
        check(invalid.detail == "non_hermitian", "invalid complete transaction reports validation detail");
        check(store.active_revision() == 12, "invalid complete transaction preserves active revision");
        check_close(store.active()->hamiltonian().at(0, 0).real(), 0.5, 0.0, "invalid transaction preserves active data");
    }

    {
        const auto snapshot = pauli_fixture();
        try {
            static_cast<void>(snapshot.derivative().at(2, 0));
            check(false, "matrix bounds checked");
        } catch (const std::out_of_range&) {
            check(true, "matrix bounds checked");
        } catch (...) {
            check(false, "matrix bounds checked");
        }
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.qmm checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_QMM_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
