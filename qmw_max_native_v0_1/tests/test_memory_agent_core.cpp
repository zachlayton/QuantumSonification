#include "qmw/memory.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string_view>
#include <type_traits>
#include <vector>

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

qmw::MemorySample process(
    qmw::SignalMemory& memory,
    const qmw::MemorySample input,
    bool* accepted = nullptr)
{
    qmw::MemorySample output {99.0, 99.0};
    const bool status = memory.process_sample(input, output);
    if (accepted != nullptr) {
        *accepted = status;
    }
    return output;
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
    using qmw::MemoryControlCode;
    using qmw::MemoryInterpolation;
    using qmw::MemorySample;
    using qmw::SignalMemory;
    using qmw::SignalMemoryParameters;

    static_assert(noexcept(std::declval<SignalMemory&>().process_sample(
        std::declval<MemorySample>(), std::declval<MemorySample&>())));
    static_assert(noexcept(std::declval<SignalMemory&>().process_block(
        nullptr, nullptr, nullptr, nullptr, 0)));
    static_assert(noexcept(std::declval<SignalMemory&>().reset()));
    static_assert(noexcept(std::declval<SignalMemory&>().set_parameters({})));

    check(qmw::memory_interpolation_name(MemoryInterpolation::nearest) == "nearest",
        "nearest interpolation name");
    check(qmw::memory_interpolation_name(MemoryInterpolation::linear) == "linear",
        "linear interpolation name");
    check(qmw::memory_control_code_name(MemoryControlCode::accepted) == "accepted",
        "accepted control name");
    check(qmw::memory_control_code_name(MemoryControlCode::invalid_delay_i)
            == "invalid_delay_i",
        "I delay rejection name");
    check(qmw::memory_control_code_name(MemoryControlCode::invalid_feedback)
            == "invalid_feedback",
        "feedback rejection name");

    check_invalid_argument(
        [] { SignalMemory memory(0); },
        "zero maximum delay rejected");
    check_invalid_argument(
        [] { SignalMemory memory(SignalMemory::maximum_supported_delay_samples + 1); },
        "oversized maximum delay rejected");
    check_invalid_argument(
        [] {
            SignalMemoryParameters parameters;
            parameters.delay_i_samples = 9.0;
            SignalMemory memory(8, parameters);
        },
        "constructor rejects delay beyond declared maximum");

    {
        SignalMemory memory(8);
        check(memory.maximum_delay_samples() == 8, "maximum delay is declared and observable");
        check(memory.parameters().delay_i_samples == 1.0
                && memory.parameters().delay_q_samples == 1.0,
            "default delays are strictly causal");
        check(memory.parameters().feedback == 0.0, "default feedback is zero");
        check(memory.parameters().wet == 1.0 && memory.parameters().dry == 0.0,
            "default mix is memory-only");
        check(memory.parameters().headroom == 0.5, "default reserves minus-six-dB headroom");
        for (int index = 0; index < 32; ++index) {
            const auto output = process(memory, {});
            check(output.in_phase == 0.0 && output.quadrature == 0.0,
                "resting signal memory emits exact I/Q silence");
        }
    }

    {
        SignalMemoryParameters parameters;
        parameters.delay_i_samples = 2.0;
        parameters.delay_q_samples = 3.0;
        parameters.headroom = 1.0;
        SignalMemory memory(8, parameters);
        std::array<MemorySample, 5> output {};
        output[0] = process(memory, {1.0, 1.0});
        for (std::size_t index = 1; index < output.size(); ++index) {
            output[index] = process(memory, {});
        }
        check(output[0].in_phase == 0.0 && output[0].quadrature == 0.0,
            "memory has no zero-delay feedthrough at wet-only mix");
        check(output[1].in_phase == 0.0 && output[1].quadrature == 0.0,
            "both impulse rails remain silent before I delay");
        check(output[2].in_phase == 1.0 && output[2].quadrature == 0.0,
            "I impulse arrives at independent two-sample delay");
        check(output[3].in_phase == 0.0 && output[3].quadrature == 1.0,
            "Q impulse arrives at independent three-sample delay");
        check(output[4].in_phase == 0.0 && output[4].quadrature == 0.0,
            "zero-feedback impulse tail terminates exactly");
    }

    {
        SignalMemoryParameters parameters;
        parameters.delay_i_samples = 4.0;
        parameters.delay_q_samples = 4.0;
        parameters.headroom = 1.0;
        SignalMemory memory(4, parameters);
        static_cast<void>(process(memory, {1.0, -1.0}));
        for (int age = 1; age < 4; ++age) {
            const auto output = process(memory, {});
            check(output.in_phase == 0.0 && output.quadrature == 0.0,
                "declared maximum delay remains silent before its exact age");
        }
        const auto output = process(memory, {});
        check(output.in_phase == 1.0 && output.quadrature == -1.0,
            "declared maximum delay addresses the oldest retained sample");
    }

    {
        SignalMemoryParameters linear;
        linear.delay_i_samples = 1.5;
        linear.delay_q_samples = 1.5;
        linear.headroom = 1.0;
        SignalMemory memory(8, linear);
        check(process(memory, {1.0, -1.0}).in_phase == 0.0,
            "fractional delay remains causal at impulse onset");
        auto output = process(memory, {});
        check(output.in_phase == 0.5 && output.quadrature == -0.5,
            "linear interpolation blends first fractional impulse sample");
        output = process(memory, {});
        check(output.in_phase == 0.5 && output.quadrature == -0.5,
            "linear interpolation blends second fractional impulse sample");
        output = process(memory, {});
        check(output.in_phase == 0.0 && output.quadrature == 0.0,
            "fractional impulse terminates after its two taps");

        memory.reset();
        check(memory.set_interpolation(MemoryInterpolation::nearest)
                == MemoryControlCode::accepted,
            "nearest interpolation selected");
        static_cast<void>(process(memory, {1.0, -1.0}));
        output = process(memory, {});
        check(output.in_phase == 0.0 && output.quadrature == 0.0,
            "nearest half-up does not emit at lower age");
        output = process(memory, {});
        check(output.in_phase == 1.0 && output.quadrature == -1.0,
            "nearest half-up emits at rounded age");
    }

    {
        SignalMemoryParameters parameters;
        parameters.feedback = 0.5;
        parameters.headroom = 1.0;
        SignalMemory memory(8, parameters);
        check_close(memory.normalization_gain(), 0.5, 0.0,
            "feedback normalization follows declared stability bound");
        static_cast<void>(process(memory, {1.0, -1.0}));
        auto output = process(memory, {});
        check(output.in_phase == 0.5 && output.quadrature == -0.5,
            "positive feedback first echo is normalized");
        output = process(memory, {});
        check(output.in_phase == 0.25 && output.quadrature == -0.25,
            "positive feedback tail decays geometrically");
        output = process(memory, {});
        check(output.in_phase == 0.125 && output.quadrature == -0.125,
            "positive feedback third echo follows equation");

        parameters.feedback = -0.5;
        SignalMemory alternating(8, parameters);
        static_cast<void>(process(alternating, {1.0, 1.0}));
        check(process(alternating, {}).in_phase == 0.5,
            "negative feedback first echo retains impulse sign");
        check(process(alternating, {}).in_phase == -0.25,
            "negative feedback alternates tail polarity");
    }

    {
        SignalMemory memory(16);
        const auto before = memory.parameters();
        const auto nan = std::numeric_limits<double>::quiet_NaN();
        check(memory.set_delay_i(0.0) == MemoryControlCode::invalid_delay_i,
            "zero I delay rejected to preserve causality");
        check(memory.set_delay_q(17.0) == MemoryControlCode::invalid_delay_q,
            "Q delay beyond declared capacity rejected");
        check(memory.set_delays(2.0, nan) == MemoryControlCode::invalid_delay_q,
            "paired delay update rejects non-finite Q atomically");
        check(memory.parameters().delay_i_samples == before.delay_i_samples
                && memory.parameters().delay_q_samples == before.delay_q_samples,
            "rejected paired delay leaves both prior values intact");
        check(memory.set_feedback(1.0) == MemoryControlCode::invalid_feedback,
            "unit feedback rejected");
        check(memory.set_feedback(-1.0) == MemoryControlCode::invalid_feedback,
            "negative unit feedback rejected");
        check(memory.set_feedback(0.99) == MemoryControlCode::accepted,
            "declared positive feedback boundary admitted");
        check(memory.set_feedback(-0.99) == MemoryControlCode::accepted,
            "declared negative feedback boundary admitted");
        check(memory.set_wet(-0.01) == MemoryControlCode::invalid_wet,
            "negative wet rejected");
        check(memory.set_dry(1.01) == MemoryControlCode::invalid_dry,
            "dry above one rejected");
        check(memory.set_mix(0.25, nan) == MemoryControlCode::invalid_dry,
            "paired mix rejects non-finite dry atomically");
        check(memory.set_headroom(1.01) == MemoryControlCode::invalid_headroom,
            "headroom above one rejected");
        check(memory.set_interpolation(static_cast<MemoryInterpolation>(99))
                == MemoryControlCode::invalid_interpolation,
            "unknown interpolation rejected");
    }

    {
        SignalMemoryParameters parameters;
        parameters.feedback = 0.99;
        parameters.wet = 1.0;
        parameters.dry = 1.0;
        parameters.headroom = 0.5;
        SignalMemory memory(4, parameters);
        double maximum = 0.0;
        bool all_finite = true;
        for (int index = 0; index < 100'000; ++index) {
            const auto output = process(memory, {1.0, -1.0});
            all_finite = all_finite
                && std::isfinite(output.in_phase)
                && std::isfinite(output.quadrature);
            maximum = std::max({maximum, std::abs(output.in_phase),
                std::abs(output.quadrature)});
        }
        check(all_finite, "long maximum-feedback drive remains finite");
        check(maximum <= parameters.headroom + 2.0e-14,
            "unit-bounded sustained drive respects per-rail headroom");
        check(memory.normalization_gain() > 0.0,
            "strict feedback margin keeps normalization finite and positive");
    }

    {
        SignalMemoryParameters parameters;
        parameters.feedback = 0.5;
        parameters.headroom = 1.0;
        SignalMemory memory(8, parameters);
        static_cast<void>(process(memory, {1.0, 1.0}));
        memory.set_muted(true);
        auto output = process(memory, {});
        check(output.in_phase == 0.0 && output.quadrature == 0.0,
            "mute emits exact complete-frame silence over an active tail");
        check(memory.muted(), "mute state is observable");
        memory.set_muted(false);
        output = process(memory, {});
        check(output.in_phase == 0.25 && output.quadrature == 0.25,
            "muted frame advances feedback memory causally");
        memory.reset();
        check(memory.valid_history_samples() == 0,
            "constant-time reset invalidates history bookkeeping");
        output = process(memory, {});
        check(output.in_phase == 0.0 && output.quadrature == 0.0,
            "reset removes the complete I/Q tail exactly");
        check(memory.parameters().feedback == 0.5,
            "reset preserves authored parameters");
    }

    {
        SignalMemoryParameters parameters;
        parameters.feedback = 0.5;
        parameters.headroom = 1.0;
        SignalMemory memory(8, parameters);
        static_cast<void>(process(memory, {1.0, 1.0}));
        bool accepted = true;
        auto output = process(memory,
            {std::numeric_limits<double>::quiet_NaN(), 0.0}, &accepted);
        check(!accepted, "non-finite I rejects the complete I/Q frame");
        check(output.in_phase == 0.0 && output.quadrature == 0.0,
            "non-finite input rejection emits exact I/Q silence");
        check(memory.rejected_sample_count() == 1,
            "non-finite frame rejection is counted");
        output = process(memory, {});
        check(std::isfinite(output.in_phase) && std::isfinite(output.quadrature),
            "finite frame after rejection has no NaN contamination");
        check(output.in_phase == 0.25 && output.quadrature == 0.25,
            "rejected frame advances existing tail using zero input");

        SignalMemory overflow_memory(2, parameters);
        const double huge = std::numeric_limits<double>::max();
        static_cast<void>(process(overflow_memory, {huge, huge}));
        output = process(overflow_memory, {huge, huge}, &accepted);
        check(!accepted, "non-finite internal sum rejects frame");
        check(output.in_phase == 0.0 && output.quadrature == 0.0,
            "overflow rejection clears history and emits exact silence");
        check(process(overflow_memory, {}).in_phase == 0.0,
            "overflow reset prevents contaminated tail recurrence");
    }

    {
        SignalMemoryParameters parameters;
        parameters.wet = 0.0;
        parameters.dry = 1.0;
        parameters.headroom = 1.0;
        SignalMemory memory(8, parameters);
        const auto output = process(memory, {0.25, -0.75});
        check(output.in_phase == 0.25 && output.quadrature == -0.75,
            "declared dry-only mix is exact dual-rail passthrough");
        check(memory.set_headroom(0.0) == MemoryControlCode::accepted,
            "zero headroom is an admitted explicit silence mapping");
        const auto silent = process(memory, {1.0, 1.0});
        check(silent.in_phase == 0.0 && silent.quadrature == 0.0,
            "zero headroom emits exact silence");
    }

    {
        constexpr std::size_t frames = 12;
        SignalMemoryParameters parameters;
        parameters.delay_i_samples = 2.0;
        parameters.delay_q_samples = 3.0;
        parameters.headroom = 1.0;
        SignalMemory memory(16, parameters);
        std::array<double, frames> input_i {};
        std::array<double, frames> input_q {};
        input_i[0] = 1.0;
        input_q[0] = -1.0;
        std::array<double, frames> output_i {};
        std::array<double, frames> output_q {};
        memory.process_block(input_i.data(), input_q.data(),
            output_i.data(), output_q.data(), frames);
        check(output_i[2] == 1.0 && output_q[2] == 0.0,
            "block processing preserves independent I delay");
        check(output_i[3] == 0.0 && output_q[3] == -1.0,
            "block processing preserves independent Q delay");

        memory.reset();
        output_i.fill(99.0);
        output_q.fill(99.0);
        memory.process_block(nullptr, nullptr,
            output_i.data(), output_q.data(), frames);
        check(std::all_of(output_i.begin(), output_i.end(),
                  [](const double value) { return value == 0.0; })
                && std::all_of(output_q.begin(), output_q.end(),
                    [](const double value) { return value == 0.0; }),
            "null block inputs produce exact I/Q silence after reset");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.memory checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_MEMORY_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
