#include "qmw/resonator.hpp"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <numbers>
#include <stdexcept>
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
void check_invalid_argument(Function&& function, const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const std::invalid_argument&) {
        check(true, name);
    } catch (...) {
        check(false, name);
    }
}

} // namespace

int main()
{
    {
        qmw::Resonator resonator;
        std::vector<double> silence(512, 0.0);
        std::vector<double> output(silence.size(), 1.0);
        resonator.process_block(silence.data(), output.data(), output.size());
        for (const double sample : output) {
            check(sample == 0.0, "resting resonator produces exact silence");
        }
    }

    {
        constexpr double sample_rate = 48000.0;
        constexpr double frequency = 1000.0;
        constexpr double decay = 1.0;
        constexpr double gain = 0.5;
        qmw::Resonator resonator({sample_rate, frequency, decay, gain});
        const double radius = std::pow(10.0, -3.0 / (decay * sample_rate));
        const double theta = 2.0 * std::numbers::pi * frequency / sample_rate;
        check_close(resonator.pole_radius(), radius, 1.0e-15, "T60 pole radius");
        check_close(resonator.process_sample(1.0), gain, 1.0e-15, "unit impulse starts at linear gain");
        check_close(
            resonator.process_sample(0.0),
            gain * radius * std::cos(theta),
            1.0e-14,
            "second impulse-response sample follows exact equation");

        resonator.reset();
        double sample = resonator.process_sample(1.0);
        for (int index = 1; index <= 48000; ++index) {
            sample = resonator.process_sample(0.0);
        }
        check_close(sample, gain * 0.001, 2.0e-13, "envelope is minus 60 dB after one T60");
    }

    {
        qmw::Resonator resonator({48000.0, 440.0, 2.0, 1.0});
        check(resonator.process_sample(1.0) == 1.0, "impulse excites body");
        check(resonator.process_sample(0.0) != 0.0, "unforced body rings");
        resonator.reset();
        check(resonator.process_sample(0.0) == 0.0, "reset removes the complete tail");
        std::vector<double> output(64, 1.0);
        resonator.process_block(nullptr, output.data(), output.size());
        for (const double sample : output) {
            check(sample == 0.0, "null excitation is silence after reset");
        }
    }

    {
        qmw::Resonator resonator({1.0, 1.0e9, -4.0, -2.0});
        const auto& bounded = resonator.parameters();
        check_close(
            bounded.sample_rate_hz,
            qmw::Resonator::minimum_sample_rate_hz,
            0.0,
            "sample rate lower bound");
        check_close(
            bounded.frequency_hz,
            qmw::Resonator::maximum_frequency_fraction * bounded.sample_rate_hz,
            0.0,
            "frequency remains below Nyquist");
        check_close(
            bounded.decay_seconds,
            qmw::Resonator::minimum_decay_seconds,
            0.0,
            "decay lower bound");
        check_close(bounded.gain, qmw::Resonator::minimum_gain, 0.0, "gain lower bound");

        resonator.set_sample_rate_hz(1.0e9);
        resonator.set_frequency_hz(-100.0);
        resonator.set_decay_seconds(1.0e9);
        resonator.set_gain(1.0e9);
        check_close(
            resonator.parameters().sample_rate_hz,
            qmw::Resonator::maximum_sample_rate_hz,
            0.0,
            "sample rate upper bound");
        check_close(
            resonator.parameters().frequency_hz,
            qmw::Resonator::minimum_frequency_hz,
            0.0,
            "frequency lower bound");
        check_close(
            resonator.parameters().decay_seconds,
            qmw::Resonator::maximum_decay_seconds,
            0.0,
            "decay upper bound");
        check_close(resonator.parameters().gain, qmw::Resonator::maximum_gain, 0.0, "gain upper bound");
        check(resonator.pole_radius() > 0.0 && resonator.pole_radius() < 1.0, "bounded pole is strictly stable");
    }

    check_invalid_argument(
        [] { qmw::Resonator resonator({std::numeric_limits<double>::quiet_NaN(), 440.0, 1.0, 1.0}); },
        "reject non-finite sample rate");
    check_invalid_argument(
        [] { qmw::Resonator resonator({48000.0, std::numeric_limits<double>::infinity(), 1.0, 1.0}); },
        "reject non-finite frequency");
    check_invalid_argument(
        [] { qmw::Resonator resonator({48000.0, 440.0, std::numeric_limits<double>::quiet_NaN(), 1.0}); },
        "reject non-finite decay");
    check_invalid_argument(
        [] { qmw::Resonator resonator({48000.0, 440.0, 1.0, std::numeric_limits<double>::infinity()}); },
        "reject non-finite gain");

    {
        qmw::Resonator resonator({48000.0, 440.0, 60.0, 4.0});
        double maximum_absolute_output = 0.0;
        bool all_finite = true;
        for (int index = 0; index < 500000; ++index) {
            const double excitation = std::sin(
                2.0 * std::numbers::pi * 440.0 * static_cast<double>(index) / 48000.0);
            const double output = resonator.process_sample(excitation);
            all_finite = all_finite && std::isfinite(output);
            maximum_absolute_output = std::max(maximum_absolute_output, std::abs(output));
        }
        check(all_finite, "long resonant drive remains finite");
        check(maximum_absolute_output > 1.0, "resonant drive accumulates audibly");
        const double rejected = resonator.process_sample(std::numeric_limits<double>::infinity());
        check(rejected == 0.0, "non-finite excitation emits safe zero");
        check(resonator.process_sample(0.0) == 0.0, "non-finite excitation resets state");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.resonator checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_RESONATOR_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
