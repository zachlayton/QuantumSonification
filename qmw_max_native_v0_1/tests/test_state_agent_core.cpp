#include "qmw/state.hpp"

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

} // namespace

int main()
{
    {
        // Rank-one PSD state with a population below the positivity tolerance.
        // Its coherence is much larger than that tolerance and must not be
        // mistaken for a nonzero entry below an actually zero pivot.
        constexpr double population = 1.0e-12;
        const double coherence = std::sqrt(population * (1.0 - population));
        const auto state = qmw::DensityState::from_split(
            2,
            {population, coherence, coherence, 1.0 - population},
            std::vector<double>(4, 0.0));
        check(std::abs(state.diagnostics().purity - 1.0) <= 1.0e-12,
            "tiny-population pure state is admitted");
        check(state.at(0, 1).real() == coherence,
            "tiny-population coherence is preserved exactly");
    }

    {
        // Admission validates but never symmetrizes or otherwise repairs rho.
        const auto state = qmw::DensityState::from_split(
            2,
            {0.5, 2.0e-12, 1.0e-12, 0.5},
            std::vector<double>(4, 0.0));
        check(state.at(0, 1).real() == 2.0e-12,
            "upper coherence is not repaired");
        check(state.at(1, 0).real() == 1.0e-12,
            "lower coherence is not repaired");
    }

    check_validation_code(
        [] {
            constexpr double population = 1.0e-12;
            constexpr double excessive_coherence = 2.0e-5;
            qmw::DensityState::from_split(
                2,
                {population, excessive_coherence, excessive_coherence, 1.0 - population},
                std::vector<double>(4, 0.0));
        },
        qmw::ValidationCode::not_positive_semidefinite,
        "tiny positive pivot does not admit an indefinite state");

    check_validation_code(
        [] {
            qmw::ValidationPolicy policy;
            policy.trace_tolerance = std::numeric_limits<double>::infinity();
            qmw::DensityState::from_split(
                2,
                {1.0, 0.0, 0.0, 0.0},
                std::vector<double>(4, 0.0),
                policy);
        },
        qmw::ValidationCode::invalid_policy,
        "infinite validation tolerance is rejected");

    check_validation_code(
        [] {
            qmw::ValidationPolicy policy;
            policy.maximum_dimension = std::numeric_limits<std::size_t>::max();
            qmw::DensityState::from_split(
                std::numeric_limits<std::size_t>::max(), {}, {}, policy);
        },
        qmw::ValidationCode::invalid_dimension,
        "dimension-square overflow is rejected before allocation");

    if (failures != 0) {
        std::cerr << failures << " qmw.state agent checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_STATE_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
