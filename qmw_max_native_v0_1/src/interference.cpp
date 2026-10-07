#include "qmw/interference.hpp"

#include <cmath>
#include <limits>
#include <numbers>
#include <stdexcept>

namespace qmw {

namespace {

constexpr double snap_tolerance = 16.0 * std::numeric_limits<double>::epsilon();

[[nodiscard]] double canonical_phase(const double phase) noexcept
{
    const double turn = 2.0 * std::numbers::pi;
    double wrapped = std::remainder(phase, turn);
    if (std::abs(wrapped) <= snap_tolerance) {
        return 0.0;
    }
    if (std::abs(std::abs(wrapped) - std::numbers::pi) <= snap_tolerance) {
        return std::numbers::pi;
    }
    if (std::abs(wrapped - std::numbers::pi / 2.0) <= snap_tolerance) {
        return std::numbers::pi / 2.0;
    }
    if (std::abs(wrapped + std::numbers::pi / 2.0) <= snap_tolerance) {
        return -std::numbers::pi / 2.0;
    }
    return wrapped;
}

} // namespace

std::string_view interference_control_code_name(
    const InterferenceControlCode code) noexcept
{
    switch (code) {
    case InterferenceControlCode::accepted:
        return "accepted";
    case InterferenceControlCode::invalid_lane:
        return "invalid_lane";
    case InterferenceControlCode::invalid_amplitude:
        return "invalid_amplitude";
    case InterferenceControlCode::invalid_phase:
        return "invalid_phase";
    case InterferenceControlCode::invalid_headroom:
        return "invalid_headroom";
    }
    return "unknown";
}

InterferenceMixer::InterferenceMixer(
    const std::size_t lane_count,
    const double headroom)
    : lane_count_(lane_count)
    , headroom_(headroom)
{
    if (lane_count < minimum_lane_count || lane_count > maximum_lane_count) {
        throw std::invalid_argument("interference lane count must be in [1, 16]");
    }
    if (!std::isfinite(headroom)
        || headroom < minimum_headroom
        || headroom > maximum_headroom) {
        throw std::invalid_argument("interference headroom must be finite and in [0, 1]");
    }
    reset();
    headroom_ = headroom;
    update_normalization();
}

InterferenceControlCode InterferenceMixer::set_lane(
    const std::size_t lane_index,
    const double amplitude,
    const double phase_radians) noexcept
{
    if (lane_index >= lane_count_) {
        return InterferenceControlCode::invalid_lane;
    }
    if (!std::isfinite(amplitude)
        || amplitude < minimum_amplitude
        || amplitude > maximum_amplitude) {
        return InterferenceControlCode::invalid_amplitude;
    }
    if (!std::isfinite(phase_radians)) {
        return InterferenceControlCode::invalid_phase;
    }

    lanes_[lane_index].amplitude = amplitude;
    lanes_[lane_index].phase_radians = canonical_phase(phase_radians);
    update_lane_coefficient(lane_index);
    update_normalization();
    return InterferenceControlCode::accepted;
}

InterferenceControlCode InterferenceMixer::set_amplitude(
    const std::size_t lane_index,
    const double amplitude) noexcept
{
    if (lane_index >= lane_count_) {
        return InterferenceControlCode::invalid_lane;
    }
    return set_lane(lane_index, amplitude, lanes_[lane_index].phase_radians);
}

InterferenceControlCode InterferenceMixer::set_phase(
    const std::size_t lane_index,
    const double phase_radians) noexcept
{
    if (lane_index >= lane_count_) {
        return InterferenceControlCode::invalid_lane;
    }
    return set_lane(lane_index, lanes_[lane_index].amplitude, phase_radians);
}

InterferenceControlCode InterferenceMixer::set_headroom(const double headroom) noexcept
{
    if (!std::isfinite(headroom)
        || headroom < minimum_headroom
        || headroom > maximum_headroom) {
        return InterferenceControlCode::invalid_headroom;
    }
    headroom_ = headroom;
    update_normalization();
    return InterferenceControlCode::accepted;
}

void InterferenceMixer::reset() noexcept
{
    for (std::size_t index = 0; index < maximum_lane_count; ++index) {
        lanes_[index] = {};
        coefficients_[index] = {};
    }
    headroom_ = default_headroom;
    muted_ = false;
    rejected_frame_count_ = 0;
    update_normalization();
}

const InterferenceLane& InterferenceMixer::lane(const std::size_t lane_index) const noexcept
{
    return lanes_[lane_index < lane_count_ ? lane_index : 0];
}

void InterferenceMixer::update_lane_coefficient(const std::size_t lane_index) noexcept
{
    const double phase = lanes_[lane_index].phase_radians;
    if (phase == 0.0) {
        coefficients_[lane_index] = {1.0, 0.0};
    } else if (phase == std::numbers::pi) {
        coefficients_[lane_index] = {-1.0, 0.0};
    } else if (phase == std::numbers::pi / 2.0) {
        coefficients_[lane_index] = {0.0, 1.0};
    } else if (phase == -std::numbers::pi / 2.0) {
        coefficients_[lane_index] = {0.0, -1.0};
    } else {
        coefficients_[lane_index] = {std::cos(phase), std::sin(phase)};
    }
}

void InterferenceMixer::update_normalization() noexcept
{
    long double amplitude_sum = 0.0L;
    for (std::size_t lane_index = 0; lane_index < lane_count_; ++lane_index) {
        amplitude_sum += static_cast<long double>(lanes_[lane_index].amplitude);
    }
    const long double denominator = amplitude_sum > 1.0L ? amplitude_sum : 1.0L;
    normalization_gain_ = static_cast<double>(
        static_cast<long double>(headroom_) / denominator);
}

bool InterferenceMixer::mix_frame(const IQSample* lane_samples, IQSample& output) noexcept
{
    if (muted_ || lane_samples == nullptr) {
        output = {};
        return lane_samples != nullptr;
    }

    long double sum_i = 0.0L;
    long double sum_q = 0.0L;
    for (std::size_t lane_index = 0; lane_index < lane_count_; ++lane_index) {
        const double amplitude = lanes_[lane_index].amplitude;
        if (amplitude == 0.0) {
            continue;
        }
        const double input_i = lane_samples[lane_index].in_phase;
        const double input_q = lane_samples[lane_index].quadrature;
        if (!std::isfinite(input_i) || !std::isfinite(input_q)) {
            output = {};
            ++rejected_frame_count_;
            return false;
        }
        const auto coefficient = coefficients_[lane_index];
        const long double weighted = static_cast<long double>(amplitude);
        sum_i += weighted
            * (static_cast<long double>(input_i) * coefficient.cosine
                - static_cast<long double>(input_q) * coefficient.sine);
        sum_q += weighted
            * (static_cast<long double>(input_i) * coefficient.sine
                + static_cast<long double>(input_q) * coefficient.cosine);
    }

    const long double gain = static_cast<long double>(normalization_gain_);
    sum_i *= gain;
    sum_q *= gain;
    output.in_phase = sum_i == 0.0L ? 0.0 : static_cast<double>(sum_i);
    output.quadrature = sum_q == 0.0L ? 0.0 : static_cast<double>(sum_q);
    return true;
}

bool InterferenceMixer::process_sample(
    const IQSample* lane_samples,
    IQSample& output) noexcept
{
    return mix_frame(lane_samples, output);
}

void InterferenceMixer::process_block(
    const double* const* in_phase_inputs,
    const double* const* quadrature_inputs,
    double* in_phase_output,
    double* quadrature_output,
    const std::size_t frame_count) noexcept
{
    if (in_phase_output == nullptr || quadrature_output == nullptr) {
        return;
    }

    std::array<IQSample, maximum_lane_count> frame {};
    for (std::size_t sample_index = 0; sample_index < frame_count; ++sample_index) {
        for (std::size_t lane_index = 0; lane_index < lane_count_; ++lane_index) {
            frame[lane_index].in_phase = in_phase_inputs != nullptr
                    && in_phase_inputs[lane_index] != nullptr
                ? in_phase_inputs[lane_index][sample_index]
                : 0.0;
            frame[lane_index].quadrature = quadrature_inputs != nullptr
                    && quadrature_inputs[lane_index] != nullptr
                ? quadrature_inputs[lane_index][sample_index]
                : 0.0;
        }
        IQSample output;
        static_cast<void>(mix_frame(frame.data(), output));
        in_phase_output[sample_index] = output.in_phase;
        quadrature_output[sample_index] = output.quadrature;
    }
}

} // namespace qmw
