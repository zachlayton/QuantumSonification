#include "qmw/observe.hpp"
#include "qmw/revisioned_state.hpp"
#include "qmw/state.hpp"

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
void check_validation_code(
    Function&& function,
    const qmw::ValidationCode expected,
    const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const qmw::ValidationError& error) {
        check(error.code() == expected, name);
    } catch (...) {
        check(false, name);
    }
}

std::vector<double> zeros(const std::size_t count)
{
    return std::vector<double>(count, 0.0);
}

} // namespace

int main()
{
    {
        auto real = zeros(256);
        auto imag = zeros(256);
        real[0] = 1.0;
        const auto state = qmw::DensityState::from_split(16, real, imag);
        check_close(state.diagnostics().trace.real(), 1.0, 1.0e-14, "ground trace");
        check_close(state.diagnostics().purity, 1.0, 1.0e-14, "ground purity");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::z), 1.0, 1.0e-14, "ground q0 z");
        check_close(qmw::pauli_expectation(state, 3, qmw::PauliAxis::z), 1.0, 1.0e-14, "ground q3 z");
    }

    {
        auto real = zeros(256);
        auto imag = zeros(256);
        real[17] = 1.0; // |0001><0001| in q0-LSB coordinates.
        const auto state = qmw::DensityState::from_split(16, real, imag);
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::z), -1.0, 1.0e-14, "q0 is least significant");
        check_close(qmw::pauli_expectation(state, 1, qmw::PauliAxis::z), 1.0, 1.0e-14, "q1 remains zero");
    }

    {
        auto real = zeros(16);
        auto imag = zeros(16);
        for (std::size_t index = 0; index < 4; ++index) {
            real[index * 4 + index] = 0.25;
        }
        const auto state = qmw::DensityState::from_split(4, real, imag);
        check_close(state.diagnostics().purity, 0.25, 1.0e-14, "maximally mixed purity");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::x), 0.0, 1.0e-14, "mixed q0 x");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::y), 0.0, 1.0e-14, "mixed q0 y");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::z), 0.0, 1.0e-14, "mixed q0 z");
    }

    {
        const auto state = qmw::DensityState::from_split(
            2,
            {0.5, 0.5, 0.5, 0.5},
            zeros(4));
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::x), 1.0, 1.0e-14, "plus x");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::y), 0.0, 1.0e-14, "plus y");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::z), 0.0, 1.0e-14, "plus z");
    }

    {
        const auto state = qmw::DensityState::from_split(
            2,
            {0.5, 0.0, 0.0, 0.5},
            {0.0, -0.5, 0.5, 0.0});
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::x), 0.0, 1.0e-14, "plus-i x");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::y), 1.0, 1.0e-14, "plus-i y");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::z), 0.0, 1.0e-14, "plus-i z");
    }

    {
        // (|00> + i|11>)/sqrt(2): rank-deficient PSD with complex coherence.
        auto real = zeros(16);
        auto imag = zeros(16);
        real[0] = 0.5;
        real[15] = 0.5;
        imag[3] = -0.5;
        imag[12] = 0.5;
        const auto state = qmw::DensityState::from_split(4, real, imag);
        check_close(state.diagnostics().purity, 1.0, 1.0e-14, "complex Bell purity");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::x), 0.0, 1.0e-14, "Bell local x");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::y), 0.0, 1.0e-14, "Bell local y");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::z), 0.0, 1.0e-14, "Bell local z");
    }

    check_validation_code(
        [] {
            qmw::DensityState::from_split(2, {1.0, 0.2, 0.0, 0.0}, zeros(4));
        },
        qmw::ValidationCode::non_hermitian,
        "reject non-Hermitian state");

    check_validation_code(
        [] {
            qmw::DensityState::from_split(2, {0.75, 0.0, 0.0, 0.75}, zeros(4));
        },
        qmw::ValidationCode::trace_not_one,
        "reject non-unit trace");

    check_validation_code(
        [] {
            qmw::DensityState::from_split(2, {1.1, 0.0, 0.0, -0.1}, zeros(4));
        },
        qmw::ValidationCode::not_positive_semidefinite,
        "reject negative state");

    check_validation_code(
        [] {
            qmw::DensityState::from_split(2, {0.0, 0.1, 0.1, 1.0}, zeros(4));
        },
        qmw::ValidationCode::not_positive_semidefinite,
        "reject nonzero column below zero PSD pivot");

    check_validation_code(
        [] {
            auto real = zeros(4);
            real[0] = std::numeric_limits<double>::quiet_NaN();
            qmw::DensityState::from_split(2, real, zeros(4));
        },
        qmw::ValidationCode::non_finite,
        "reject non-finite state");

    check_validation_code(
        [] {
            qmw::DensityState::from_split(2, zeros(3), zeros(3));
        },
        qmw::ValidationCode::wrong_element_count,
        "reject wrong element count");

    {
        qmw::RevisionedStateStore store(2);
        const std::vector<double> pure {1.0, 0.0, 0.0, 0.0};
        const std::vector<double> mixed {0.5, 0.0, 0.0, 0.5};
        const std::vector<double> invalid {1.1, 0.0, 0.0, -0.1};
        const auto zero = zeros(4);

        const auto first = store.stage(qmw::StatePart::real, 1, pure);
        check(first.status == qmw::StageStatus::staged, "real component stages without commit");
        check(store.active() == nullptr, "partial revision is invisible");
        const auto committed = store.stage(qmw::StatePart::imag, 1, zero);
        check(committed.status == qmw::StageStatus::accepted, "matching pair commits");
        check(store.active_revision() == 1, "active revision advances atomically");
        check_close(store.active()->at(0, 0).real(), 1.0, 1.0e-14, "committed state is exact");

        const auto unmatched_imag = store.stage(qmw::StatePart::imag, 2, zero);
        check(unmatched_imag.status == qmw::StageStatus::staged, "new imaginary component stages");
        check(store.active_revision() == 1, "incomplete candidate preserves active revision");
        const auto unmatched_real = store.stage(qmw::StatePart::real, 3, mixed);
        check(unmatched_real.status == qmw::StageStatus::staged, "mismatched revisions do not commit");
        check(store.active_revision() == 1, "mismatched candidate remains invisible");
        const auto newest_pair = store.stage(qmw::StatePart::imag, 3, zero);
        check(newest_pair.status == qmw::StageStatus::accepted, "newest matching pair commits");
        check(store.active_revision() == 3, "active revision skips abandoned partial candidate");
        check_close(store.active()->diagnostics().purity, 0.5, 1.0e-14, "new active state metrics");

        const auto stale = store.stage(qmw::StatePart::real, 2, mixed);
        check(stale.status == qmw::StageStatus::rejected, "stale revision rejected");
        check(stale.detail == "stale_revision", "stale revision code");

        check(store.stage(qmw::StatePart::real, 4, invalid).status == qmw::StageStatus::staged, "invalid real stages until complete");
        const auto rejected = store.stage(qmw::StatePart::imag, 4, zero);
        check(rejected.status == qmw::StageStatus::rejected, "invalid complete pair rejected");
        check(rejected.detail == "not_positive_semidefinite", "validation code crosses adapter boundary");
        check(store.active_revision() == 3, "rejection preserves active revision");
        check_close(store.active()->diagnostics().purity, 0.5, 1.0e-14, "rejection preserves active values");

        const auto malformed = store.stage(qmw::StatePart::real, 5, zeros(3));
        check(malformed.status == qmw::StageStatus::rejected, "malformed component rejected immediately");
        check(malformed.detail == "wrong_element_count", "malformed component code");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw core checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_LIBQMW_STATE_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
