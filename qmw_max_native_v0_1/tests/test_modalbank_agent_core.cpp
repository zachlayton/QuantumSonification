#include "qmw/modalbank.hpp"

#include <array>
#include <atomic>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <numbers>
#include <string_view>
#include <thread>

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

qmw::ModalDescriptor mode(
    const std::uint32_t id,
    const double frequency = 1000.0,
    const double decay = 1.0,
    const double gain = 1.0,
    const double pan = -1.0,
    const double phase = 0.0)
{
    return {id, frequency, decay, gain, pan, phase};
}

void apply(qmw::ModalBank& bank)
{
    bank.process_block(nullptr, nullptr, nullptr, 0);
}

} // namespace

int main()
{
    {
        qmw::ModalBank bank;
        std::array<double, 64> silence {};
        std::array<double, 64> left {};
        std::array<double, 64> right {};
        left.fill(1.0);
        right.fill(1.0);
        bank.process_block(silence.data(), left.data(), right.data(), left.size());
        for (std::size_t index = 0; index < left.size(); ++index) {
            check(left[index] == 0.0, "empty bank left is exact silence");
            check(right[index] == 0.0, "empty bank right is exact silence");
        }
    }

    {
        qmw::ModalBank bank;
        const std::array modes {mode(7)};
        const auto admission = bank.publish_frame(1, modes);
        check(admission.published(), "valid frame publishes");
        check(!bank.has_active_frame(), "publication is not active on message boundary");
        apply(bank);
        check(bank.has_active_frame(), "publication activates at vector boundary");
        check(bank.active_revision() == 1, "active revision is explicit");

        constexpr double sample_rate = 48000.0;
        constexpr double frequency = 1000.0;
        constexpr double decay = 1.0;
        const double radius = std::pow(10.0, -3.0 / (decay * sample_rate));
        const double theta = 2.0 * std::numbers::pi * frequency / sample_rate;
        const std::array<double, 2> input {1.0, 0.0};
        std::array<double, 2> left {};
        std::array<double, 2> right {};
        bank.set_headroom(1.0);
        bank.process_block(input.data(), left.data(), right.data(), input.size());
        check_close(left[0], 1.0, 1.0e-15, "single-mode impulse starts at gain");
        check_close(left[1], radius * std::cos(theta), 1.0e-14, "single mode matches resonator pole equation");
        check_close(right[0], 0.0, 1.0e-15, "hard-left pan has exact-zero right impulse");
    }

    {
        qmw::ModalBank bank;
        const std::array unordered {mode(30, 900.0), mode(10, 300.0), mode(20, 600.0)};
        check(bank.publish_frame(3, unordered).published(), "unordered frame publishes");
        apply(bank);
        check(bank.active_descriptors()[0].mode_id == 10, "mode order first ID");
        check(bank.active_descriptors()[1].mode_id == 20, "mode order second ID");
        check(bank.active_descriptors()[2].mode_id == 30, "mode order third ID");
    }

    {
        qmw::ModalBank bank;
        const std::array<double, 0> empty {};
        check(
            bank.publish_frequencies(1, empty).code
                == qmw::ModalFrameCode::empty_frequency_list,
            "simple frequency list rejects empty input");
        const std::array invalid {220.0, std::numeric_limits<double>::infinity()};
        check(
            bank.publish_frequencies(1, invalid).code
                == qmw::ModalFrameCode::invalid_frequency,
            "simple frequency list rejects its whole invalid frame");
        check(!bank.has_active_frame(), "rejected simple list leaves bank empty");

        const std::array frequencies {220.0, 330.0, 440.0};
        const auto admission = bank.publish_frequencies(1, frequencies);
        check(admission.published(), "simple frequency list publishes atomically");
        check(admission.mode_count == frequencies.size(), "simple list reports its mode count");
        check(!bank.has_active_frame(), "simple list waits for a vector boundary");
        apply(bank);
        check(bank.active_revision() == 1, "simple list keeps its assigned revision");
        check(bank.active_mode_count() == frequencies.size(), "simple list creates every mode");
        for (std::size_t index = 0; index < frequencies.size(); ++index) {
            const auto& descriptor = bank.active_descriptors()[index];
            check(
                descriptor.mode_id == static_cast<std::uint32_t>(index),
                "simple list position becomes stable mode ID");
            check_close(descriptor.frequency_hz, frequencies[index], 0.0, "simple list frequency is exact");
            check_close(
                descriptor.decay_seconds,
                qmw::ModalBank::simple_decay_seconds,
                0.0,
                "simple list uses default T60");
            check_close(descriptor.gain, qmw::ModalBank::simple_gain, 0.0, "simple list uses equal gain");
            check_close(descriptor.pan, qmw::ModalBank::simple_pan, 0.0, "simple list uses center pan");
            check_close(
                descriptor.phase_radians,
                qmw::ModalBank::simple_phase_radians,
                0.0,
                "simple list uses zero excitation phase");
        }
        check(
            bank.publish_frequencies(1, frequencies).code
                == qmw::ModalFrameCode::stale_revision,
            "simple list obeys the revision gate");
    }

    {
        qmw::ModalBank bank;
        std::array<qmw::ModalDescriptor, 20> modes {};
        for (std::size_t index = 0; index < modes.size(); ++index) {
            modes[index] = mode(static_cast<std::uint32_t>(index), 500.0);
        }
        check(bank.publish_frame(1, modes).published(), "twenty-mode frame publishes");
        bank.set_headroom(1.0);
        const double input = 1.0;
        double left = 0.0;
        double right = 0.0;
        bank.process_block(&input, &left, &right, 1);
        check_close(left, 1.0, 1.0e-14, "twenty coincident modes normalize to headroom");
        check_close(right, 0.0, 1.0e-14, "twenty hard-left modes stay left");
        check(std::abs(left) <= 1.0 && std::abs(right) <= 1.0, "multimode output is bounded");
    }

    {
        qmw::ModalBank bank;
        std::array<qmw::ModalDescriptor, qmw::ModalBank::maximum_modes> modes {};
        for (std::size_t index = 0; index < modes.size(); ++index) {
            modes[index] = mode(
                static_cast<std::uint32_t>(index),
                100.0 + 17.0 * static_cast<double>(index),
                60.0,
                4.0,
                index % 2 == 0 ? -0.5 : 0.5);
        }
        check(bank.publish_frame(1, modes).published(), "maximum-capacity frame publishes");
        bool bounded_and_finite = true;
        double phase = 0.0;
        for (int block = 0; block < 300; ++block) {
            std::array<double, 64> input {};
            std::array<double, 64> left {};
            std::array<double, 64> right {};
            for (double& sample : input) {
                sample = std::sin(phase);
                phase += 2.0 * std::numbers::pi * 440.0 / 48000.0;
            }
            bank.process_block(input.data(), left.data(), right.data(), input.size());
            for (std::size_t index = 0; index < left.size(); ++index) {
                bounded_and_finite = bounded_and_finite
                    && std::isfinite(left[index]) && std::isfinite(right[index])
                    && std::abs(left[index]) <= 1.0 && std::abs(right[index]) <= 1.0;
            }
        }
        check(bounded_and_finite, "maximum-capacity sustained drive remains finite and bounded");
    }

    {
        qmw::ModalBank bank;
        const std::array modes {
            mode(1, 800.0, 1.0, 1.0, -1.0),
            mode(2, 800.0, 1.0, 1.0, 1.0),
        };
        check(bank.publish_frame(1, modes).published(), "stereo frame publishes");
        bank.set_headroom(1.0);
        bank.set_solo_mode(2);
        const double input = 1.0;
        double left = 1.0;
        double right = 0.0;
        bank.process_block(&input, &left, &right, 1);
        check_close(left, 0.0, 1.0e-14, "solo selects mode by stable ID");
        check_close(right, 1.0, 1.0e-14, "solo renormalizes selected mode");
        bank.clear_solo();
    }

    {
        qmw::ModalBank bank;
        bank.set_headroom(1.0);
        const std::array modes {
            mode(10, 800.0, 1.0, 1.0, -1.0),
            mode(20, 800.0, 1.0, 1.0, 1.0),
        };
        check(bank.publish_frame(1, modes).published(), "interference timbre frame publishes");
        apply(bank);
        check(
            bank.set_interference_timbre(0.0, std::numbers::pi, 1.0, 0.0)
                == qmw::InterferenceTimbreCode::accepted,
            "interference timbre applies");
        const double impulse = 1.0;
        double left = 0.0;
        double right = 0.0;
        bank.process_block(&impulse, &left, &right, 1);
        check_close(left, 1.0, 1.0e-14, "constructive lane retains normalized headroom");
        check_close(right, 0.0, 1.0e-14, "destructive lane reaches exact silence");
        check_close(
            bank.active_descriptors()[0].gain,
            1.0,
            0.0,
            "timbre projection does not mutate descriptor gain");
        check(
            bank.set_interference_timbre(0.0, 0.0, 1.1, 0.0)
                == qmw::InterferenceTimbreCode::invalid_depth,
            "invalid timbre depth is rejected");
        check(
            bank.clear_interference_timbre()
                == qmw::InterferenceTimbreCode::accepted,
            "interference timbre clears to neutral");
    }

    {
        qmw::ModalBank bank;
        bank.set_headroom(1.0);
        const std::array initial {mode(9)};
        check(bank.publish_frame(1, initial).published(), "initial continuity frame publishes");
        const double impulse = 1.0;
        double left = 0.0;
        double right = 0.0;
        bank.process_block(&impulse, &left, &right, 1);

        const std::array revised {mode(9, 1000.0, 1.0, 0.5)};
        check(bank.publish_frame(2, revised).published(), "same-ID revision publishes");
        const double zero = 0.0;
        bank.process_block(&zero, &left, &right, 1);
        const double radius = std::pow(10.0, -3.0 / 48000.0);
        const double theta = 2.0 * std::numbers::pi * 1000.0 / 48000.0;
        check_close(left, 0.5 * radius * std::cos(theta), 1.0e-14, "same mode ID preserves resonant state");

        const std::array<qmw::ModalDescriptor, 0> empty {};
        check(bank.publish_frame(3, empty).published(), "empty replacement frame publishes");
        bank.process_block(&zero, &left, &right, 1);
        check(left == 0.0 && right == 0.0, "removed modes cannot retain audible tails");
    }

    {
        qmw::ModalBank bank;
        check(
            bank.set_mode_frequency_hz(10, 440.0)
                == qmw::ModalFrequencyCode::no_active_frame,
            "frequency override requires an active frame");
        const std::array modes {
            mode(10, 440.0, 1.0, 1.0, -1.0),
            mode(20, 660.0, 1.0, 1.0, 1.0),
        };
        check(bank.publish_frame(1, modes).published(), "frequency override frame publishes");
        apply(bank);
        check(
            bank.set_mode_frequency_hz(99, 550.0)
                == qmw::ModalFrequencyCode::mode_not_found,
            "frequency override addresses stable mode ID");
        check(
            bank.set_mode_frequency_hz(10, 0.0)
                == qmw::ModalFrequencyCode::invalid_frequency,
            "frequency override rejects an invalid value");
        check_close(
            bank.active_descriptors()[0].frequency_hz,
            440.0,
            0.0,
            "rejected frequency override preserves descriptor");

        bank.set_headroom(1.0);
        const double impulse = 1.0;
        double left = 0.0;
        double right = 0.0;
        bank.process_block(&impulse, &left, &right, 1);
        check(
            bank.set_mode_frequency_hz(10, 880.0)
                == qmw::ModalFrequencyCode::applied,
            "frequency override applies to named active mode");
        check_close(
            bank.active_descriptors()[0].frequency_hz,
            880.0,
            0.0,
            "frequency override updates active descriptor");
        check_close(
            bank.active_descriptors()[1].frequency_hz,
            660.0,
            0.0,
            "frequency override leaves other modes unchanged");
        const double zero = 0.0;
        bank.process_block(&zero, &left, &right, 1);
        const double radius = std::pow(10.0, -3.0 / 48000.0);
        const double theta = 2.0 * std::numbers::pi * 880.0 / 48000.0;
        check_close(
            left,
            0.5 * radius * std::cos(theta),
            2.0e-14,
            "frequency override preserves state and changes the next pole rotation");

        const std::array replacement {mode(10, 330.0)};
        check(bank.publish_frame(2, replacement).published(), "new descriptor frame follows override");
        apply(bank);
        check_close(
            bank.active_descriptors()[0].frequency_hz,
            330.0,
            0.0,
            "new descriptor frame replaces live frequency override");
    }

    {
        qmw::ModalBank bank;
        const std::array modes {
            mode(10, 220.0),
            mode(20, 330.0),
        };
        check(bank.publish_frame(1, modes).published(), "base-frequency frame publishes");
        apply(bank);
        check(
            bank.set_base_frequency_hz(440.0) == qmw::ModalFrequencyCode::applied,
            "single frequency control retunes modal base");
        check_close(
            bank.active_descriptors()[0].frequency_hz,
            440.0,
            0.0,
            "base-frequency control retunes lowest mode");
        check_close(
            bank.active_descriptors()[1].frequency_hz,
            660.0,
            0.0,
            "base-frequency control preserves modal ratio");
        check(
            bank.set_base_frequency_hz(20000.0)
                == qmw::ModalFrequencyCode::invalid_frequency,
            "base-frequency control rejects an out-of-band scaled mode");
        check_close(
            bank.active_descriptors()[0].frequency_hz,
            440.0,
            0.0,
            "rejected base-frequency control is atomic");
        check_close(
            bank.active_descriptors()[1].frequency_hz,
            660.0,
            0.0,
            "rejected base-frequency control preserves all modes");
    }

    {
        qmw::ModalBank bank;
        const std::array modes {mode(1, 1000.0)};
        check(bank.publish_frame(1, modes).published(), "mute frame publishes");
        bank.set_headroom(1.0);
        const double impulse = 1.0;
        double left = 0.0;
        double right = 0.0;
        bank.process_block(&impulse, &left, &right, 1);
        bank.set_muted(true);
        const double zero = 0.0;
        bank.process_block(&zero, &left, &right, 1);
        check(left == 0.0 && right == 0.0, "mute emits exact silence");
        bank.set_muted(false);
        bank.process_block(&zero, &left, &right, 1);
        const double radius = std::pow(10.0, -3.0 / 48000.0);
        const double theta = 2.0 * std::numbers::pi * 1000.0 / 48000.0;
        check_close(left, radius * radius * std::cos(2.0 * theta), 2.0e-14, "muted state advances causally");
        bank.reset();
        bank.process_block(&zero, &left, &right, 1);
        check(left == 0.0 && right == 0.0, "reset removes all modal state");
    }

    {
        qmw::ModalBank bank;
        const std::array duplicate {mode(1), mode(1)};
        check(
            bank.publish_frame(1, duplicate).code == qmw::ModalFrameCode::duplicate_mode_id,
            "duplicate IDs reject whole frame");
        const std::array invalid_frequency {mode(1, 30000.0)};
        check(
            bank.publish_frame(1, invalid_frequency).code == qmw::ModalFrameCode::invalid_frequency,
            "super-Nyquist frequency rejects whole frame");
        const std::array invalid_decay {mode(1, 100.0, 0.0)};
        check(
            bank.publish_frame(1, invalid_decay).code == qmw::ModalFrameCode::invalid_decay,
            "nonpositive decay rejects whole frame");
        const std::array invalid_gain {mode(1, 100.0, 1.0, -0.1)};
        check(
            bank.publish_frame(1, invalid_gain).code == qmw::ModalFrameCode::invalid_gain,
            "negative gain rejects whole frame");
        const std::array invalid_pan {mode(1, 100.0, 1.0, 1.0, 2.0)};
        check(
            bank.publish_frame(1, invalid_pan).code == qmw::ModalFrameCode::invalid_pan,
            "out-of-range pan rejects whole frame");
        const std::array invalid_phase {mode(1, 100.0, 1.0, 1.0, 0.0, 4.0)};
        check(
            bank.publish_frame(1, invalid_phase).code == qmw::ModalFrameCode::invalid_phase,
            "out-of-range phase rejects whole frame");
        std::array<qmw::ModalDescriptor, qmw::ModalBank::maximum_modes + 1> excessive {};
        check(
            bank.publish_frame(1, excessive).code == qmw::ModalFrameCode::too_many_modes,
            "over-capacity frame rejects atomically");

        const std::array valid {mode(1)};
        check(bank.publish_frame(4, valid).published(), "valid revision publishes after rejection");
        check(
            bank.publish_frame(4, valid).code == qmw::ModalFrameCode::stale_revision,
            "duplicate revision rejects");
        check(
            bank.publish_frame(3, valid).code == qmw::ModalFrameCode::stale_revision,
            "older revision rejects");
    }

    {
        qmw::ModalBank bank;
        const std::array high_mode {mode(1, 22000.0)};
        check(bank.publish_frame(1, high_mode).published(), "high-frequency frame publishes at 48 kHz");
        check(bank.set_sample_rate_hz(44100.0), "empty bank admits 44.1 kHz sample rate");
        apply(bank);
        check(!bank.has_active_frame(), "frame invalidated by sample-rate change cannot activate");
        const std::array replacement {mode(1, 10000.0)};
        check(bank.publish_frame(2, replacement).published(), "new valid sample-rate revision publishes");
        apply(bank);
        check(bank.active_revision() == 2, "valid replacement activates after rate rejection");
        check(!bank.set_sample_rate_hz(8000.0), "sample rate rejecting active frequency preserves coefficients");
        check(bank.sample_rate_hz() == 44100.0, "rejected sample rate leaves active rate unchanged");
    }

    {
        qmw::ModalBank bank;
        const std::array modes {mode(1)};
        check(bank.publish_frame(1, modes).published(), "finite-input safety frame publishes");
        const double impulse = 1.0;
        double left = 0.0;
        double right = 0.0;
        bank.process_block(&impulse, &left, &right, 1);
        const double invalid = std::numeric_limits<double>::infinity();
        bank.process_block(&invalid, &left, &right, 1);
        check(left == 0.0 && right == 0.0, "non-finite excitation emits safe zero");
        const double zero = 0.0;
        bank.process_block(&zero, &left, &right, 1);
        check(left == 0.0 && right == 0.0, "non-finite excitation resets all mode state");
    }

    {
        qmw::ModalBank bank;
        const std::array initial {mode(1, 200.0)};
        check(bank.publish_frame(1, initial).published(), "concurrency initial frame publishes");
        apply(bank);
        std::atomic<bool> start {false};
        std::thread publisher([&] {
            while (!start.load(std::memory_order_acquire)) {
            }
            for (std::uint64_t revision = 2; revision <= 1000; ++revision) {
                const std::array next {mode(
                    static_cast<std::uint32_t>((revision % 20) + 1),
                    200.0 + static_cast<double>(revision % 100))};
                (void)bank.publish_frame(revision, next);
            }
        });
        start.store(true, std::memory_order_release);
        bool finite = true;
        for (int block = 0; block < 2000; ++block) {
            std::array<double, 8> input {};
            std::array<double, 8> left {};
            std::array<double, 8> right {};
            input[0] = block == 0 ? 1.0 : 0.0;
            bank.process_block(input.data(), left.data(), right.data(), input.size());
            for (std::size_t index = 0; index < left.size(); ++index) {
                finite = finite && std::isfinite(left[index]) && std::isfinite(right[index]);
            }
        }
        publisher.join();
        apply(bank);
        check(finite, "concurrent publication keeps audio finite");
        check(bank.active_revision() == 1000, "latest complete concurrent revision activates");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.modalbank checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_MODALBANK_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
