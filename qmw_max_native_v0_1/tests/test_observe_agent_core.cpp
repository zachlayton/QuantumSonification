#include "qmw/observe.hpp"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string_view>
#include <type_traits>
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
    const double tolerance = 1.0e-14)
{
    check(std::abs(actual - expected) <= tolerance, name);
}

template <typename Exception, typename Function>
void check_throws(Function&& function, const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const Exception&) {
        check(true, name);
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
    static_assert(std::is_same_v<
        decltype(std::declval<const qmw::RevisionedPauliObserver&>().active()),
        std::optional<qmw::PauliObservation>>);

    check(qmw::pauli_axis_from_name("X") == qmw::PauliAxis::x, "parse uppercase X argument");
    check(qmw::pauli_axis_from_name("y") == qmw::PauliAxis::y, "parse lowercase y argument");
    check(qmw::pauli_axis_from_name("Z") == qmw::PauliAxis::z, "parse uppercase Z argument");
    check(!qmw::pauli_axis_from_name("XX").has_value(), "reject unknown axis argument");
    check(!qmw::pauli_axis_from_name("").has_value(), "reject empty axis argument");

    {
        // |+i><+i| has rho_01=-i/2 and <Y>=+1.  This locks the sign
        // independently from real-only X fixtures.
        const auto plus_i = qmw::DensityState::from_split(
            2,
            {0.5, 0.0, 0.0, 0.5},
            {0.0, -0.5, 0.5, 0.0});
        const auto minus_i = qmw::DensityState::from_split(
            2,
            {0.5, 0.0, 0.0, 0.5},
            {0.0, 0.5, -0.5, 0.0});
        check_close(qmw::pauli_expectation(plus_i, 0, qmw::PauliAxis::y), 1.0, "complex Y positive sign");
        check_close(qmw::pauli_expectation(minus_i, 0, qmw::PauliAxis::y), -1.0, "complex Y negative sign");
    }

    {
        // (|01> + i|11>)/sqrt(2): q0 is fixed at one while q1 is |+i>.
        // Basis indices 1 and 3 explicitly lock q0-LSB tensor ordering.
        auto real = zeros(16);
        auto imag = zeros(16);
        real[1 * 4 + 1] = 0.5;
        real[3 * 4 + 3] = 0.5;
        imag[1 * 4 + 3] = -0.5;
        imag[3 * 4 + 1] = 0.5;
        const auto state = qmw::DensityState::from_split(4, real, imag);
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::z), -1.0, "q0-LSB target is fixed one");
        check_close(qmw::pauli_expectation(state, 1, qmw::PauliAxis::y), 1.0, "q1 complex target Y");
        check_close(qmw::pauli_expectation(state, 1, qmw::PauliAxis::x), 0.0, "q1 complex target X");
        check_close(qmw::pauli_expectation(state, 1, qmw::PauliAxis::z), 0.0, "q1 complex target Z");
        check_close(qmw::pauli_expectation(state, 0, qmw::PauliAxis::x), 0.0, "q0 has no local coherence");
    }

    {
        const auto qutrit_mixed = qmw::DensityState::from_split(
            3,
            {1.0 / 3.0, 0.0, 0.0, 0.0, 1.0 / 3.0, 0.0, 0.0, 0.0, 1.0 / 3.0},
            zeros(9));
        const auto qubit_zero = qmw::DensityState::from_split(2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
        check_throws<std::invalid_argument>(
            [&] { (void)qmw::pauli_expectation(qutrit_mixed, 0, qmw::PauliAxis::z); },
            "reject non-power-of-two observation dimension");
        check_throws<std::out_of_range>(
            [&] { (void)qmw::pauli_expectation(qubit_zero, 1, qmw::PauliAxis::z); },
            "reject target outside tensor factorization");
        check_throws<std::invalid_argument>(
            [&] { (void)qmw::pauli_expectation(qubit_zero, 0, static_cast<qmw::PauliAxis>(99)); },
            "reject invalid Pauli axis");
        check_throws<std::invalid_argument>(
            [] { qmw::RevisionedPauliObserver observer(3, 0, qmw::PauliAxis::z); },
            "observer rejects non-qubit dimension");
        check_throws<std::out_of_range>(
            [] { qmw::RevisionedPauliObserver observer(2, 1, qmw::PauliAxis::z); },
            "observer rejects invalid target");
        check_throws<std::invalid_argument>(
            [] { qmw::RevisionedPauliObserver observer(2, 0, static_cast<qmw::PauliAxis>(99)); },
            "observer rejects invalid axis");
    }

    {
        qmw::RevisionedPauliObserver observer(2, 0, qmw::PauliAxis::x);
        const std::vector<double> plus_real {0.5, 0.5, 0.5, 0.5};
        const std::vector<double> ground_real {1.0, 0.0, 0.0, 0.0};
        const std::vector<double> invalid_real {1.1, 0.0, 0.0, -0.1};
        const auto zero = zeros(4);

        check(!observer.active().has_value(), "observer begins empty");

        auto source_copy = plus_real;
        const auto staged = observer.stage(qmw::StatePart::real, 10, source_copy);
        source_copy.assign(4, 0.0);
        check(staged.status == qmw::StageStatus::staged, "first component stages");
        check(!observer.active().has_value(), "partial pair remains invisible");
        const auto accepted = observer.stage(qmw::StatePart::imag, 10, zero);
        check(accepted.status == qmw::StageStatus::accepted, "matching observer pair accepts");
        check(observer.active().has_value(), "accepted observation becomes visible");
        check(observer.active()->revision == 10, "observer reports accepted revision");
        check(observer.active()->qubit == 0, "observer reports target qubit");
        check(observer.active()->axis == qmw::PauliAxis::x, "observer reports axis");
        check_close(observer.active()->expectation, 1.0, "observer copied staged rho values");

        check(
            observer.stage(qmw::StatePart::imag, 11, zero).status == qmw::StageStatus::staged,
            "new incomplete revision stages");
        check(observer.active()->revision == 10, "incomplete candidate preserves preceding revision");
        check_close(observer.active()->expectation, 1.0, "incomplete candidate preserves preceding value");
        check(
            observer.stage(qmw::StatePart::real, 12, ground_real).status == qmw::StageStatus::staged,
            "mismatched real stages without commit");
        check(observer.active()->revision == 10, "mismatched revisions preserve preceding revision");
        check_close(observer.active()->expectation, 1.0, "mismatched revisions preserve preceding value");

        check(
            observer.stage(qmw::StatePart::real, 13, invalid_real).status == qmw::StageStatus::staged,
            "invalid candidate stages until paired");
        const auto rejected = observer.stage(qmw::StatePart::imag, 13, zero);
        check(rejected.status == qmw::StageStatus::rejected, "invalid complete candidate rejects");
        check(rejected.detail == "not_positive_semidefinite", "observer preserves validation code");
        check(observer.active()->revision == 10, "rejection preserves preceding revision");
        check_close(observer.active()->expectation, 1.0, "rejection preserves preceding value");

        const auto malformed = observer.stage(qmw::StatePart::real, 14, zeros(3));
        check(malformed.status == qmw::StageStatus::rejected, "wrong-size component rejects");
        check(malformed.detail == "wrong_element_count", "wrong-size detail crosses observer boundary");
        const auto stale = observer.stage(qmw::StatePart::real, 9, plus_real);
        check(stale.status == qmw::StageStatus::rejected, "stale observer component rejects");
        check(stale.detail == "stale_revision", "stale revision detail crosses observer boundary");
        check(observer.active()->revision == 10, "malformed and stale inputs preserve active revision");

        check(
            observer.stage(qmw::StatePart::real, 15, ground_real).status == qmw::StageStatus::staged,
            "next valid real stages");
        check(
            observer.stage(qmw::StatePart::imag, 15, zero).status == qmw::StageStatus::accepted,
            "next valid pair commits");
        check(observer.active()->revision == 15, "valid pair advances observer revision");
        check_close(observer.active()->expectation, 0.0, "valid pair advances observer value");

        check(
            observer.stage(qmw::StatePart::real, 16, plus_real).status == qmw::StageStatus::staged,
            "candidate exists before explicit clear");
        observer.clear_candidate();
        check(
            observer.stage(qmw::StatePart::imag, 16, zero).status == qmw::StageStatus::staged,
            "clear removes only staged candidate");
        check(observer.active()->revision == 15, "clear candidate preserves active observation");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.observe checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_OBSERVE_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
