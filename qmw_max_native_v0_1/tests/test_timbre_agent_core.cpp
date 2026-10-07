#include "qmw/timbre.hpp"

#include <array>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <numbers>
#include <string_view>

namespace {

int failures = 0;
int checks = 0;

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

} // namespace

int main()
{
    using qmw::InterferenceTimbreCode;
    using qmw::project_interference_timbre;

    const std::array base {0.5, 0.5, 0.5, 0.5};
    {
        const auto result = project_interference_timbre(base, 1.3, -0.7, 0.0);
        check(result.code == InterferenceTimbreCode::accepted, "neutral projection accepted");
        check(result.mode_count == 4, "mode count retained");
        for (std::size_t index = 0; index < base.size(); ++index) {
            check(result.gain_factors[index] == 1.0, "zero depth is exact neutral factor");
            check(result.output_amplitudes[index] == base[index], "zero depth retains amplitude");
        }
        check(result.base_power == result.output_power, "neutral power is exact");
        check(!result.complete_cancellation, "neutral frame is not cancellation");
    }

    {
        const auto result = project_interference_timbre(
            base, 0.0, std::numbers::pi, 1.0);
        check(result.code == InterferenceTimbreCode::accepted, "alternating projection accepted");
        check_close(result.output_amplitudes[0], std::sqrt(0.5), 1.0e-14, "M1 constructive");
        check(result.output_amplitudes[1] == 0.0, "M2 cancelled");
        check_close(result.output_amplitudes[2], std::sqrt(0.5), 1.0e-14, "M3 constructive");
        check(result.output_amplitudes[3] == 0.0, "M4 cancelled");
        check_close(result.output_power, result.base_power, 1.0e-14, "power preserved");
    }

    {
        const auto result = project_interference_timbre(
            base, std::numbers::pi, 0.0, 1.0);
        check(result.code == InterferenceTimbreCode::accepted, "cancellation accepted");
        check(result.complete_cancellation, "complete cancellation explicit");
        check(result.output_power == 0.0, "complete cancellation is silence");
        for (std::size_t index = 0; index < base.size(); ++index) {
            check(result.gain_factors[index] == 0.0, "cancellation factor is exact zero");
        }
    }

    {
        const std::array<double, 3> zero {};
        const auto result = project_interference_timbre(zero, 0.0, 0.4, 1.0);
        check(result.code == InterferenceTimbreCode::accepted, "zero source accepted");
        check(result.complete_cancellation, "zero source remains explicit silence");
    }

    {
        const auto nan = std::numeric_limits<double>::quiet_NaN();
        auto invalid_base = base;
        invalid_base[1] = -0.1;
        check(project_interference_timbre(invalid_base, 0.0, 0.0, 1.0).code
                == InterferenceTimbreCode::invalid_amplitude,
            "negative base amplitude rejected");
        invalid_base[1] = nan;
        check(project_interference_timbre(invalid_base, 0.0, 0.0, 1.0).code
                == InterferenceTimbreCode::invalid_amplitude,
            "nonfinite base amplitude rejected");
        check(project_interference_timbre(base, nan, 0.0, 1.0).code
                == InterferenceTimbreCode::invalid_phase,
            "nonfinite phase rejected");
        check(project_interference_timbre(base, 0.0, nan, 1.0).code
                == InterferenceTimbreCode::invalid_spread,
            "nonfinite spread rejected");
        check(project_interference_timbre(base, 0.0, 0.0, -0.1).code
                == InterferenceTimbreCode::invalid_depth,
            "negative depth rejected");
        check(project_interference_timbre(base, 0.0, 0.0, 1.1).code
                == InterferenceTimbreCode::invalid_depth,
            "depth above one rejected");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.timbre checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_TIMBRE_AGENT_CORE_OK " << checks << " checks\n";
    return EXIT_SUCCESS;
}
