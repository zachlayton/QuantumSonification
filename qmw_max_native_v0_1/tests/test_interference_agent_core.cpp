#include "qmw/interference.hpp"

#include <algorithm>
#include <array>
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

qmw::IQSample process(
    qmw::InterferenceMixer& mixer,
    const std::array<qmw::IQSample, qmw::InterferenceMixer::maximum_lane_count>& lanes,
    bool* accepted = nullptr)
{
    qmw::IQSample output {99.0, 99.0};
    const bool status = mixer.process_sample(lanes.data(), output);
    if (accepted != nullptr) {
        *accepted = status;
    }
    return output;
}

} // namespace

int main()
{
    using qmw::InterferenceControlCode;
    using qmw::InterferenceMixer;
    using qmw::IQSample;

    check(interference_control_code_name(InterferenceControlCode::accepted) == "accepted", "accepted status name");
    check(interference_control_code_name(InterferenceControlCode::invalid_lane) == "invalid_lane", "invalid lane status name");
    check(interference_control_code_name(InterferenceControlCode::invalid_amplitude) == "invalid_amplitude", "invalid amplitude status name");
    check(interference_control_code_name(InterferenceControlCode::invalid_phase) == "invalid_phase", "invalid phase status name");
    check(interference_control_code_name(InterferenceControlCode::invalid_headroom) == "invalid_headroom", "invalid headroom status name");

    for (const std::size_t invalid_count : {std::size_t {0}, std::size_t {17}}) {
        bool threw = false;
        try {
            InterferenceMixer mixer(invalid_count);
            static_cast<void>(mixer);
        } catch (const std::invalid_argument&) {
            threw = true;
        }
        check(threw, "invalid lane count rejected by constructor");
    }
    for (const double invalid_headroom : {
             -0.01,
             1.01,
             std::numeric_limits<double>::quiet_NaN(),
             std::numeric_limits<double>::infinity()}) {
        bool threw = false;
        try {
            InterferenceMixer mixer(2, invalid_headroom);
            static_cast<void>(mixer);
        } catch (const std::invalid_argument&) {
            threw = true;
        }
        check(threw, "invalid constructor headroom rejected");
    }

    {
        InterferenceMixer mixer;
        check(mixer.lane_count() == 2, "default mixer has two lanes");
        check(mixer.headroom() == 0.5, "default headroom is minus six dB");
        check(mixer.normalization_gain() == 0.25, "default normalization reserves both declared lanes");
        std::array<IQSample, InterferenceMixer::maximum_lane_count> lanes {};
        const auto output = process(mixer, lanes);
        check(output.in_phase == 0.0 && output.quadrature == 0.0, "zero inputs produce exact I/Q silence");
    }

    {
        InterferenceMixer mixer(2, 0.5);
        std::array<IQSample, InterferenceMixer::maximum_lane_count> lanes {};
        lanes[0] = {1.0, 0.0};
        lanes[1] = {1.0, 0.0};
        const auto output = process(mixer, lanes);
        check(output.in_phase == 0.5 && output.quadrature == 0.0, "equal zero-phase lanes interfere constructively at declared headroom");

        check(mixer.set_phase(1, std::numbers::pi) == InterferenceControlCode::accepted, "pi phase admitted");
        const auto cancelled = process(mixer, lanes);
        check(cancelled.in_phase == 0.0 && cancelled.quadrature == 0.0, "equal pi-opposed lanes cancel exactly");

        check(mixer.set_phase(1, -std::numbers::pi) == InterferenceControlCode::accepted, "negative pi phase admitted");
        const auto negative_pi_cancelled = process(mixer, lanes);
        check(negative_pi_cancelled.in_phase == 0.0 && negative_pi_cancelled.quadrature == 0.0, "negative pi canonicalizes to exact cancellation");
    }

    {
        InterferenceMixer mixer(2, 0.5);
        check(mixer.set_amplitude(1, 0.0) == InterferenceControlCode::accepted, "unused lane amplitude can be zero");
        check(mixer.normalization_gain() == 0.5, "normalization follows declared amplitude sum");
        check(mixer.set_phase(0, std::numbers::pi / 2.0) == InterferenceControlCode::accepted, "quadrature phase admitted");
        std::array<IQSample, InterferenceMixer::maximum_lane_count> lanes {};
        lanes[0] = {1.0, 0.0};
        const auto output = process(mixer, lanes);
        check(output.in_phase == 0.0 && output.quadrature == 0.5, "positive quarter turn maps I to positive Q exactly");

        check(mixer.set_phase(0, -std::numbers::pi / 2.0) == InterferenceControlCode::accepted, "negative quadrature phase admitted");
        const auto negative = process(mixer, lanes);
        check(negative.in_phase == 0.0 && negative.quadrature == -0.5, "negative quarter turn maps I to negative Q exactly");
    }

    {
        InterferenceMixer mixer(2, 1.0);
        check(mixer.set_lane(0, 0.25, 0.0) == InterferenceControlCode::accepted, "first weighted lane admitted");
        check(mixer.set_lane(1, 0.75, 0.0) == InterferenceControlCode::accepted, "second weighted lane admitted");
        check(mixer.normalization_gain() == 1.0, "amplitude sum of one needs no further normalization");
        std::array<IQSample, InterferenceMixer::maximum_lane_count> lanes {};
        lanes[0] = {0.5, -0.25};
        lanes[1] = {0.5, -0.25};
        const auto output = process(mixer, lanes);
        check(output.in_phase == 0.5 && output.quadrature == -0.25, "weighted coherent sum preserves a shared complex input");
    }

    {
        InterferenceMixer mixer(1, 1.0);
        check(mixer.set_phase(0, std::numbers::pi / 4.0) == InterferenceControlCode::accepted, "general finite phase admitted");
        std::array<IQSample, InterferenceMixer::maximum_lane_count> lanes {};
        lanes[0] = {0.6, -0.2};
        const auto output = process(mixer, lanes);
        const double c = std::sqrt(0.5);
        check_close(output.in_phase, 0.8 * c, 2.0e-15, "complex multiply real component is correct");
        check_close(output.quadrature, 0.4 * c, 2.0e-15, "complex multiply imaginary component is correct");
        check_close(
            std::hypot(output.in_phase, output.quadrature),
            std::hypot(lanes[0].in_phase, lanes[0].quadrature),
            2.0e-15,
            "phase rotation preserves complex magnitude");
    }

    {
        InterferenceMixer mixer(2, 0.5);
        const auto original_lane = mixer.lane(0);
        const auto nan = std::numeric_limits<double>::quiet_NaN();
        const auto infinity = std::numeric_limits<double>::infinity();
        check(mixer.set_lane(2, 0.5, 0.0) == InterferenceControlCode::invalid_lane, "out-of-range lane rejected");
        check(mixer.set_amplitude(0, -0.01) == InterferenceControlCode::invalid_amplitude, "negative amplitude rejected");
        check(mixer.set_amplitude(0, 1.01) == InterferenceControlCode::invalid_amplitude, "amplitude above unity rejected");
        check(mixer.set_amplitude(0, nan) == InterferenceControlCode::invalid_amplitude, "NaN amplitude rejected");
        check(mixer.set_phase(0, infinity) == InterferenceControlCode::invalid_phase, "infinite phase rejected");
        check(mixer.set_lane(0, 0.5, nan) == InterferenceControlCode::invalid_phase, "atomic lane update rejects NaN phase");
        check(mixer.lane(0).amplitude == original_lane.amplitude && mixer.lane(0).phase_radians == original_lane.phase_radians, "rejected lane controls leave prior pair intact");
        check(mixer.set_headroom(-0.01) == InterferenceControlCode::invalid_headroom, "negative headroom rejected");
        check(mixer.set_headroom(1.01) == InterferenceControlCode::invalid_headroom, "headroom above unity rejected");
        check(mixer.set_headroom(nan) == InterferenceControlCode::invalid_headroom, "NaN headroom rejected");
        check(mixer.headroom() == 0.5, "rejected headroom leaves prior value intact");
    }

    {
        InterferenceMixer mixer(2, 0.5);
        std::array<IQSample, InterferenceMixer::maximum_lane_count> lanes {};
        lanes[0] = {1.0, 0.0};
        lanes[1] = {1.0, 0.0};
        mixer.set_muted(true);
        const auto muted = process(mixer, lanes);
        check(muted.in_phase == 0.0 && muted.quadrature == 0.0, "mute produces exact I/Q silence");
        check(mixer.muted(), "mute state is observable");
        mixer.set_muted(false);
        check(process(mixer, lanes).in_phase == 0.5, "unmute restores coherent processing without stale state");

        check(mixer.set_lane(0, 0.2, 0.7) == InterferenceControlCode::accepted, "non-default lane set before reset");
        check(mixer.set_headroom(0.9) == InterferenceControlCode::accepted, "non-default headroom set before reset");
        mixer.set_muted(true);
        mixer.reset();
        check(!mixer.muted(), "reset unmutes");
        check(mixer.headroom() == InterferenceMixer::default_headroom, "reset restores default headroom");
        check(mixer.lane(0).amplitude == 1.0 && mixer.lane(0).phase_radians == 0.0, "reset restores neutral lane controls");
        check(process(mixer, lanes).in_phase == 0.5, "reset restores neutral coherent sum");
    }

    {
        InterferenceMixer mixer(2, 0.5);
        std::array<IQSample, InterferenceMixer::maximum_lane_count> lanes {};
        lanes[0] = {1.0, 0.0};
        lanes[1] = {std::numeric_limits<double>::quiet_NaN(), 0.0};
        bool accepted = true;
        const auto rejected = process(mixer, lanes, &accepted);
        check(!accepted, "non-finite active input rejects complete frame");
        check(rejected.in_phase == 0.0 && rejected.quadrature == 0.0, "rejected frame emits exact I/Q silence");
        check(mixer.rejected_frame_count() == 1, "non-finite rejection is counted");
        lanes[1] = {1.0, 0.0};
        check(process(mixer, lanes).in_phase == 0.5, "finite frame after rejection is unaffected");

        check(mixer.set_amplitude(1, 0.0) == InterferenceControlCode::accepted, "lane disabled for inactive nonfinite test");
        lanes[1] = {std::numeric_limits<double>::infinity(), std::numeric_limits<double>::quiet_NaN()};
        check(process(mixer, lanes, &accepted).in_phase == 0.5, "zero-amplitude lane is excluded before sample validation");
        check(accepted, "inactive nonfinite lane does not reject relevant frame");
    }

    {
        constexpr std::size_t frames = 8;
        InterferenceMixer mixer(2, 1.0);
        check(mixer.set_lane(0, 1.0, 0.0) == InterferenceControlCode::accepted, "block lane zero configured");
        check(mixer.set_lane(1, 1.0, std::numbers::pi) == InterferenceControlCode::accepted, "block lane one configured opposing");
        std::array<double, frames> i0 {1, 2, 3, 4, 0, -1, -2, -3};
        std::array<double, frames> q0 {0, 1, 0, -1, 0, 0.5, 0, -0.5};
        std::array<double, frames> i1 = i0;
        std::array<double, frames> q1 = q0;
        const double* i_inputs[] {i0.data(), i1.data()};
        const double* q_inputs[] {q0.data(), q1.data()};
        std::array<double, frames> output_i;
        std::array<double, frames> output_q;
        mixer.process_block(i_inputs, q_inputs, output_i.data(), output_q.data(), frames);
        check(std::all_of(output_i.begin(), output_i.end(), [](const double value) { return value == 0.0; }), "block destructive interference is exact on I");
        check(std::all_of(output_q.begin(), output_q.end(), [](const double value) { return value == 0.0; }), "block destructive interference is exact on Q");

        output_i.fill(99.0);
        output_q.fill(99.0);
        mixer.process_block(nullptr, nullptr, output_i.data(), output_q.data(), frames);
        check(std::all_of(output_i.begin(), output_i.end(), [](const double value) { return value == 0.0; }), "null block inputs mean exact I silence");
        check(std::all_of(output_q.begin(), output_q.end(), [](const double value) { return value == 0.0; }), "null block inputs mean exact Q silence");
    }

    {
        InterferenceMixer mixer(InterferenceMixer::maximum_lane_count, 0.5);
        std::array<IQSample, InterferenceMixer::maximum_lane_count> lanes {};
        for (std::size_t lane = 0; lane < lanes.size(); ++lane) {
            const double phase = 0.31 * static_cast<double>(lane);
            const double input_phase = 0.17 * static_cast<double>(lane);
            check(mixer.set_lane(lane, (static_cast<double>(lane) + 1.0) / 16.0, phase) == InterferenceControlCode::accepted, "maximum-lane control admitted");
            lanes[lane] = {std::cos(input_phase), std::sin(input_phase)};
        }
        const auto first = process(mixer, lanes);
        const auto second = process(mixer, lanes);
        check(first.in_phase == second.in_phase && first.quadrature == second.quadrature, "fixed ascending lane order is bit-repeatable");
        check(std::hypot(first.in_phase, first.quadrature) <= mixer.headroom() + 4.0e-16, "unit-disk inputs remain within complex headroom");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.interference checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_INTERFERENCE_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
