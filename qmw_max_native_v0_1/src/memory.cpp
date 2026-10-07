#include "qmw/memory.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

namespace qmw {

namespace {

[[nodiscard]] bool valid_interpolation(
    const MemoryInterpolation interpolation) noexcept
{
    switch (interpolation) {
    case MemoryInterpolation::nearest:
    case MemoryInterpolation::linear:
        return true;
    }
    return false;
}

[[nodiscard]] double canonical_zero(const double value) noexcept
{
    return value == 0.0 ? 0.0 : value;
}

[[nodiscard]] double flush_denormal(const double value) noexcept
{
    constexpr double threshold = 1.0e-300;
    return std::abs(value) < threshold ? 0.0 : value;
}

} // namespace

std::string_view memory_interpolation_name(
    const MemoryInterpolation interpolation) noexcept
{
    switch (interpolation) {
    case MemoryInterpolation::nearest:
        return "nearest";
    case MemoryInterpolation::linear:
        return "linear";
    }
    return "unknown";
}

std::string_view memory_control_code_name(const MemoryControlCode code) noexcept
{
    switch (code) {
    case MemoryControlCode::accepted:
        return "accepted";
    case MemoryControlCode::invalid_delay_i:
        return "invalid_delay_i";
    case MemoryControlCode::invalid_delay_q:
        return "invalid_delay_q";
    case MemoryControlCode::invalid_feedback:
        return "invalid_feedback";
    case MemoryControlCode::invalid_wet:
        return "invalid_wet";
    case MemoryControlCode::invalid_dry:
        return "invalid_dry";
    case MemoryControlCode::invalid_headroom:
        return "invalid_headroom";
    case MemoryControlCode::invalid_interpolation:
        return "invalid_interpolation";
    }
    return "unknown";
}

SignalMemory::SignalMemory(
    const std::size_t maximum_delay_samples,
    const SignalMemoryParameters parameters)
    : maximum_delay_samples_(maximum_delay_samples)
{
    if (maximum_delay_samples < minimum_maximum_delay_samples
        || maximum_delay_samples > maximum_supported_delay_samples) {
        throw std::invalid_argument(
            "signal-memory maximum delay must be in [1, 1536000] samples");
    }
    buffer_.resize(maximum_delay_samples + 1);
    const auto code = set_parameters(parameters);
    if (code != MemoryControlCode::accepted) {
        throw std::invalid_argument(memory_control_code_name(code).data());
    }
}

MemoryControlCode SignalMemory::validate(
    const SignalMemoryParameters& parameters) const noexcept
{
    if (!std::isfinite(parameters.delay_i_samples)
        || parameters.delay_i_samples < minimum_delay_samples
        || parameters.delay_i_samples > static_cast<double>(maximum_delay_samples_)) {
        return MemoryControlCode::invalid_delay_i;
    }
    if (!std::isfinite(parameters.delay_q_samples)
        || parameters.delay_q_samples < minimum_delay_samples
        || parameters.delay_q_samples > static_cast<double>(maximum_delay_samples_)) {
        return MemoryControlCode::invalid_delay_q;
    }
    if (!std::isfinite(parameters.feedback)
        || std::abs(parameters.feedback) > maximum_feedback_magnitude) {
        return MemoryControlCode::invalid_feedback;
    }
    if (!std::isfinite(parameters.wet)
        || parameters.wet < minimum_mix || parameters.wet > maximum_mix) {
        return MemoryControlCode::invalid_wet;
    }
    if (!std::isfinite(parameters.dry)
        || parameters.dry < minimum_mix || parameters.dry > maximum_mix) {
        return MemoryControlCode::invalid_dry;
    }
    if (!std::isfinite(parameters.headroom)
        || parameters.headroom < minimum_headroom
        || parameters.headroom > maximum_headroom) {
        return MemoryControlCode::invalid_headroom;
    }
    if (!valid_interpolation(parameters.interpolation)) {
        return MemoryControlCode::invalid_interpolation;
    }
    return MemoryControlCode::accepted;
}

MemoryControlCode SignalMemory::set_parameters(
    const SignalMemoryParameters parameters) noexcept
{
    const auto code = validate(parameters);
    if (code != MemoryControlCode::accepted) {
        return code;
    }
    parameters_ = parameters;
    update_normalization();
    return MemoryControlCode::accepted;
}

MemoryControlCode SignalMemory::set_delays(
    const double delay_i_samples,
    const double delay_q_samples) noexcept
{
    auto parameters = parameters_;
    parameters.delay_i_samples = delay_i_samples;
    parameters.delay_q_samples = delay_q_samples;
    return set_parameters(parameters);
}

MemoryControlCode SignalMemory::set_delay_i(const double delay_samples) noexcept
{
    return set_delays(delay_samples, parameters_.delay_q_samples);
}

MemoryControlCode SignalMemory::set_delay_q(const double delay_samples) noexcept
{
    return set_delays(parameters_.delay_i_samples, delay_samples);
}

MemoryControlCode SignalMemory::set_feedback(const double feedback) noexcept
{
    auto parameters = parameters_;
    parameters.feedback = feedback;
    return set_parameters(parameters);
}

MemoryControlCode SignalMemory::set_mix(const double wet, const double dry) noexcept
{
    auto parameters = parameters_;
    parameters.wet = wet;
    parameters.dry = dry;
    return set_parameters(parameters);
}

MemoryControlCode SignalMemory::set_wet(const double wet) noexcept
{
    return set_mix(wet, parameters_.dry);
}

MemoryControlCode SignalMemory::set_dry(const double dry) noexcept
{
    return set_mix(parameters_.wet, dry);
}

MemoryControlCode SignalMemory::set_headroom(const double headroom) noexcept
{
    auto parameters = parameters_;
    parameters.headroom = headroom;
    return set_parameters(parameters);
}

MemoryControlCode SignalMemory::set_interpolation(
    const MemoryInterpolation interpolation) noexcept
{
    auto parameters = parameters_;
    parameters.interpolation = interpolation;
    return set_parameters(parameters);
}

void SignalMemory::update_normalization() noexcept
{
    const double feedback_margin = 1.0 - std::abs(parameters_.feedback);
    const double worst_case_sum = parameters_.dry
        + parameters_.wet / feedback_margin;
    normalization_gain_ = parameters_.headroom / std::max(1.0, worst_case_sum);
}

double SignalMemory::read_age(
    const std::size_t age,
    const bool quadrature) const noexcept
{
    if (age == 0 || age > valid_history_samples_) {
        return 0.0;
    }
    const std::size_t size = buffer_.size();
    const std::size_t offset = age % size;
    const std::size_t index = (write_index_ + size - offset) % size;
    return quadrature ? buffer_[index].quadrature : buffer_[index].in_phase;
}

double SignalMemory::read_rail(
    const double delay,
    const bool quadrature) const noexcept
{
    if (parameters_.interpolation == MemoryInterpolation::nearest) {
        const auto age = static_cast<std::size_t>(std::floor(delay + 0.5));
        return read_age(std::min(age, maximum_delay_samples_), quadrature);
    }

    const auto lower_age = static_cast<std::size_t>(std::floor(delay));
    const auto upper_age = std::min(lower_age + 1, maximum_delay_samples_);
    const double fraction = delay - static_cast<double>(lower_age);
    const double lower = read_age(lower_age, quadrature);
    if (fraction == 0.0 || upper_age == lower_age) {
        return lower;
    }
    const double upper = read_age(upper_age, quadrature);
    return (1.0 - fraction) * lower + fraction * upper;
}

MemorySample SignalMemory::read_delayed() const noexcept
{
    return {
        read_rail(parameters_.delay_i_samples, false),
        read_rail(parameters_.delay_q_samples, true),
    };
}

bool SignalMemory::process_sample(
    MemorySample input,
    MemorySample& output) noexcept
{
    const bool input_is_finite = std::isfinite(input.in_phase)
        && std::isfinite(input.quadrature);
    if (!input_is_finite) {
        input = {};
        ++rejected_sample_count_;
    }

    const MemorySample delayed = read_delayed();
    MemorySample stored {
        input.in_phase + parameters_.feedback * delayed.in_phase,
        input.quadrature + parameters_.feedback * delayed.quadrature,
    };
    const MemorySample candidate {
        normalization_gain_
            * (parameters_.dry * input.in_phase + parameters_.wet * delayed.in_phase),
        normalization_gain_
            * (parameters_.dry * input.quadrature + parameters_.wet * delayed.quadrature),
    };

    if (!std::isfinite(stored.in_phase) || !std::isfinite(stored.quadrature)
        || !std::isfinite(candidate.in_phase)
        || !std::isfinite(candidate.quadrature)) {
        ++rejected_sample_count_;
        reset();
        output = {};
        return false;
    }

    stored.in_phase = flush_denormal(stored.in_phase);
    stored.quadrature = flush_denormal(stored.quadrature);
    buffer_[write_index_] = stored;
    write_index_ = (write_index_ + 1) % buffer_.size();
    valid_history_samples_ = std::min(
        valid_history_samples_ + 1,
        maximum_delay_samples_);

    if (muted_ || !input_is_finite) {
        output = {};
        return input_is_finite;
    }
    output.in_phase = canonical_zero(candidate.in_phase);
    output.quadrature = canonical_zero(candidate.quadrature);
    return true;
}

void SignalMemory::process_block(
    const double* input_i,
    const double* input_q,
    double* output_i,
    double* output_q,
    const std::size_t frame_count) noexcept
{
    if (output_i == nullptr || output_q == nullptr) {
        return;
    }
    for (std::size_t index = 0; index < frame_count; ++index) {
        const MemorySample input {
            input_i == nullptr ? 0.0 : input_i[index],
            input_q == nullptr ? 0.0 : input_q[index],
        };
        MemorySample output;
        static_cast<void>(process_sample(input, output));
        output_i[index] = output.in_phase;
        output_q[index] = output.quadrature;
    }
}

void SignalMemory::reset() noexcept
{
    // Old samples remain physically allocated but are unreachable until every
    // corresponding slot has been overwritten after this reset.
    valid_history_samples_ = 0;
}

} // namespace qmw
