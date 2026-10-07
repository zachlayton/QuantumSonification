#include "qmw/excite.hpp"

#include <algorithm>
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

void check_close(
    const double actual,
    const double expected,
    const double tolerance,
    const std::string_view name)
{
    check(std::abs(actual - expected) <= tolerance, name);
}

qmw::ExcitationEvent event(
    const std::uint64_t id,
    const std::uint64_t revision,
    const std::uint64_t onset,
    const double strength,
    const std::uint64_t duration,
    const qmw::ExcitationShape shape)
{
    return {id, revision, onset, strength, duration, shape};
}

void check_silence(const std::vector<double>& values, const std::string_view name)
{
    check(
        std::all_of(values.begin(), values.end(), [](const double value) {
            return value == 0.0;
        }),
        name);
}

} // namespace

int main()
{
    check(qmw::excitation_shape_name(qmw::ExcitationShape::impulse) == "impulse", "impulse shape name");
    check(qmw::excitation_shape_name(qmw::ExcitationShape::box) == "box", "box shape name");
    check(qmw::excitation_shape_name(qmw::ExcitationShape::hann) == "hann", "hann shape name");

    {
        qmw::Exciter exciter;
        std::vector<double> output(128, 1.0);
        exciter.process_block(output.data(), output.size());
        check_silence(output, "resting source emits exact silence");
        check(exciter.sample_clock() == output.size(), "silent processing advances sample clock");
        const auto clock = exciter.sample_clock();
        exciter.process_block(nullptr, 100);
        check(exciter.sample_clock() == clock, "null output does not consume event time");
    }

    {
        qmw::Exciter exciter;
        const auto admitted = exciter.admit(event(1, 7, 3, 0.75, 1, qmw::ExcitationShape::impulse));
        check(admitted.accepted(), "finite impulse admitted");
        std::vector<double> output(8, 99.0);
        exciter.process_block(output.data(), output.size());
        const std::vector<double> expected {0.0, 0.0, 0.0, 0.75, 0.0, 0.0, 0.0, 0.0};
        check(output == expected, "impulse lands at exact sample offset and stops");
        check(exciter.active_event_count() == 0, "completed impulse releases slot");
    }

    {
        qmw::Exciter exciter;
        check(exciter.admit(event(4, 8, 2, -0.25, 4, qmw::ExcitationShape::box)).accepted(), "box admitted");
        std::vector<double> output(9, 99.0);
        exciter.process_block(output.data(), output.size());
        const std::vector<double> expected {0.0, 0.0, -0.25, -0.25, -0.25, -0.25, 0.0, 0.0, 0.0};
        check(output == expected, "box has exact declared support");
    }

    {
        qmw::Exciter exciter;
        check(exciter.admit(event(10, 8, 1, 0.8, 5, qmw::ExcitationShape::hann)).accepted(), "hann admitted");
        std::vector<double> output(8, 99.0);
        exciter.process_block(output.data(), output.size());
        const std::vector<double> envelope {0.25, 0.75, 1.0, 0.75, 0.25};
        check(output.front() == 0.0, "hann is silent before onset");
        for (std::size_t index = 0; index < envelope.size(); ++index) {
            check_close(output[index + 1], 0.8 * envelope[index], 2.0e-15, "normalized hann sample");
        }
        check(output[6] == 0.0 && output[7] == 0.0, "hann is silent after duration");
    }

    {
        qmw::Exciter exciter;
        check(exciter.admit(event(1, 1, 0, 0.8, 3, qmw::ExcitationShape::box)).accepted(), "first overlap event admitted");
        check(exciter.admit(event(2, 1, 0, 0.7, 3, qmw::ExcitationShape::box)).accepted(), "same-revision overlap admitted");
        check(exciter.process_sample() == 1.0, "positive overlap saturates at one");
        check(exciter.process_sample() == 1.0, "positive overlap policy is stable");
        check(exciter.admit(event(3, 2, 0, -1.0, 2, qmw::ExcitationShape::box)).accepted(), "opposite event admitted");
        check_close(exciter.process_sample(), 0.5, 0.0, "opposing overlap sums before saturation");
        check(exciter.process_sample() == -1.0, "remaining negative event is bounded");
        check(exciter.process_sample() == 0.0, "all overlap tails end in exact silence");
    }

    {
        qmw::Exciter exciter;
        check(exciter.admit(event(20, 4, 0, 1.0, 1, qmw::ExcitationShape::impulse)).accepted(), "watermark source event admitted");
        check(
            exciter.admit(event(20, 4, 0, 1.0, 1, qmw::ExcitationShape::impulse)).code
                == qmw::ExcitationAdmissionCode::stale_event_id,
            "duplicate event id rejected");
        check(
            exciter.admit(event(19, 5, 0, 1.0, 1, qmw::ExcitationShape::impulse)).code
                == qmw::ExcitationAdmissionCode::stale_event_id,
            "decreasing event id rejected");
        check(
            exciter.admit(event(21, 3, 0, 1.0, 1, qmw::ExcitationShape::impulse)).code
                == qmw::ExcitationAdmissionCode::stale_revision,
            "decreasing upstream revision rejected");
        check(
            exciter.admit(event(21, 4, 0, 1.0, 1, qmw::ExcitationShape::impulse)).accepted(),
            "new event may share upstream revision");
        check(exciter.last_event_id() == 21 && exciter.latest_revision() == 4, "watermarks update only on acceptance");
    }

    {
        qmw::Exciter exciter;
        const auto nan = std::numeric_limits<double>::quiet_NaN();
        const auto infinity = std::numeric_limits<double>::infinity();
        check(
            exciter.admit(event(1, 0, 0, nan, 1, qmw::ExcitationShape::impulse)).code
                == qmw::ExcitationAdmissionCode::invalid_strength,
            "NaN strength rejected");
        check(
            exciter.admit(event(1, 0, 0, infinity, 1, qmw::ExcitationShape::impulse)).code
                == qmw::ExcitationAdmissionCode::invalid_strength,
            "infinite strength rejected");
        check(
            exciter.admit(event(1, 0, 0, 1.0001, 1, qmw::ExcitationShape::impulse)).code
                == qmw::ExcitationAdmissionCode::invalid_strength,
            "out-of-range strength rejected rather than clamped");
        check(
            exciter.admit(event(1, 0, 0, 1.0, 0, qmw::ExcitationShape::box)).code
                == qmw::ExcitationAdmissionCode::invalid_duration,
            "zero duration rejected");
        check(
            exciter.admit(event(1, 0, 0, 1.0, 2, qmw::ExcitationShape::impulse)).code
                == qmw::ExcitationAdmissionCode::invalid_duration,
            "impulse duration must be one sample");
        check(
            exciter.admit(event(
                1,
                0,
                qmw::Exciter::maximum_onset_samples + 1,
                1.0,
                1,
                qmw::ExcitationShape::impulse)).code
                == qmw::ExcitationAdmissionCode::onset_out_of_range,
            "excessive onset rejected");
        check(
            exciter.admit(event(
                1,
                0,
                0,
                1.0,
                qmw::Exciter::maximum_duration_samples + 1,
                qmw::ExcitationShape::box)).code
                == qmw::ExcitationAdmissionCode::invalid_duration,
            "excessive duration rejected");
        check(
            exciter.admit(event(1, 0, 0, 1.0, 1, static_cast<qmw::ExcitationShape>(99))).code
                == qmw::ExcitationAdmissionCode::invalid_shape,
            "invalid shape enum rejected");
        check(!exciter.has_admitted_event(), "invalid inputs do not advance watermarks");
    }

    {
        qmw::Exciter exciter;
        for (std::size_t index = 0; index < qmw::Exciter::event_capacity; ++index) {
            check(
                exciter.admit(event(
                    index + 1,
                    1,
                    qmw::Exciter::maximum_onset_samples,
                    0.1,
                    1,
                    qmw::ExcitationShape::impulse)).accepted(),
                "fixed event capacity accepts available slot");
        }
        check(exciter.active_event_count() == qmw::Exciter::event_capacity, "all fixed slots occupied");
        check(
            exciter.admit(event(65, 1, 0, 0.1, 1, qmw::ExcitationShape::impulse)).code
                == qmw::ExcitationAdmissionCode::capacity_full,
            "full scheduler rejects without allocation");
        check(exciter.last_event_id() == 64, "capacity rejection does not advance watermark");
    }

    {
        qmw::Exciter exciter;
        check(exciter.admit(event(50, 12, 0, 0.5, 8, qmw::ExcitationShape::box)).accepted(), "reset test event admitted");
        check(exciter.process_sample() == 0.5, "event is active before reset");
        const auto clock = exciter.sample_clock();
        exciter.reset();
        check(exciter.process_sample() == 0.0, "reset forces exact silence");
        check(exciter.sample_clock() == clock + 1, "reset preserves timeline");
        check(exciter.active_event_count() == 0, "reset clears every slot");
        check(
            exciter.admit(event(50, 12, 0, 0.5, 1, qmw::ExcitationShape::impulse)).code
                == qmw::ExcitationAdmissionCode::stale_event_id,
            "reset preserves replay guard");
    }

    {
        qmw::Exciter exciter;
        check(exciter.admit(event(1, 0, 0, 0.6, 4, qmw::ExcitationShape::box)).accepted(), "mute test event admitted");
        exciter.set_muted(true);
        std::vector<double> muted(4, 99.0);
        exciter.process_block(muted.data(), muted.size());
        check_silence(muted, "mute emits exact zeros");
        check(exciter.active_event_count() == 0, "event lifetime advances while muted");
        exciter.set_muted(false);
        check(exciter.process_sample() == 0.0, "completed muted event does not reappear");
    }

    {
        qmw::Exciter exciter;
        std::vector<double> output(250000, 99.0);
        std::uint64_t id = 1;
        for (std::uint64_t block = 0; block < 100; ++block) {
            check(exciter.admit(event(id++, block, block % 17, block % 2 == 0 ? 1.0 : -1.0, 33, qmw::ExcitationShape::hann)).accepted(), "long deterministic run admits bounded event");
            exciter.process_block(output.data() + block * 2500, 2500);
        }
        check(
            std::all_of(output.begin(), output.end(), [](const double sample) {
                return std::isfinite(sample) && sample >= -1.0 && sample <= 1.0;
            }),
            "long run remains finite and bounded");
        check(output.back() == 0.0, "long run returns to exact silence");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.excite checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_EXCITE_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
