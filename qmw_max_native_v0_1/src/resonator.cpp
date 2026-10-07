#include "qmw/resonator.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>
#include <stdexcept>

namespace qmw {
namespace {

void require_finite(const double value, const char* name)
{
    if (!std::isfinite(value)) {
        throw std::invalid_argument(name);
    }
}

[[nodiscard]] double clamp_sample_rate(const double value) noexcept
{
    return std::clamp(
        value,
        Resonator::minimum_sample_rate_hz,
        Resonator::maximum_sample_rate_hz);
}

[[nodiscard]] double clamp_frequency(const double value, const double sample_rate_hz) noexcept
{
    return std::clamp(
        value,
        Resonator::minimum_frequency_hz,
        Resonator::maximum_frequency_fraction * sample_rate_hz);
}

} // namespace

Resonator::Resonator(const ResonatorParameters parameters)
{
    set_parameters(parameters);
}

void Resonator::set_parameters(ResonatorParameters parameters)
{
    require_finite(parameters.sample_rate_hz, "resonator sample rate must be finite");
    require_finite(parameters.frequency_hz, "resonator frequency must be finite");
    require_finite(parameters.decay_seconds, "resonator decay must be finite");
    require_finite(parameters.gain, "resonator gain must be finite");

    parameters.sample_rate_hz = clamp_sample_rate(parameters.sample_rate_hz);
    parameters.frequency_hz = clamp_frequency(
        parameters.frequency_hz,
        parameters.sample_rate_hz);
    parameters.decay_seconds = std::clamp(
        parameters.decay_seconds,
        minimum_decay_seconds,
        maximum_decay_seconds);
    parameters.gain = std::clamp(parameters.gain, minimum_gain, maximum_gain);
    parameters_ = parameters;
    update_coefficients();
}

void Resonator::set_sample_rate_hz(const double sample_rate_hz)
{
    require_finite(sample_rate_hz, "resonator sample rate must be finite");
    parameters_.sample_rate_hz = clamp_sample_rate(sample_rate_hz);
    parameters_.frequency_hz = clamp_frequency(
        parameters_.frequency_hz,
        parameters_.sample_rate_hz);
    update_coefficients();
}

void Resonator::set_frequency_hz(const double frequency_hz)
{
    require_finite(frequency_hz, "resonator frequency must be finite");
    parameters_.frequency_hz = clamp_frequency(frequency_hz, parameters_.sample_rate_hz);
    update_coefficients();
}

void Resonator::set_decay_seconds(const double decay_seconds)
{
    require_finite(decay_seconds, "resonator decay must be finite");
    parameters_.decay_seconds = std::clamp(
        decay_seconds,
        minimum_decay_seconds,
        maximum_decay_seconds);
    update_coefficients();
}

void Resonator::set_gain(const double gain)
{
    require_finite(gain, "resonator gain must be finite");
    parameters_.gain = std::clamp(gain, minimum_gain, maximum_gain);
}

void Resonator::update_coefficients() noexcept
{
    const double theta = 2.0 * std::numbers::pi
        * parameters_.frequency_hz / parameters_.sample_rate_hz;
    radius_ = std::pow(
        10.0,
        -3.0 / (parameters_.decay_seconds * parameters_.sample_rate_hz));
    cosine_ = std::cos(theta);
    sine_ = std::sin(theta);
}

double Resonator::process_sample(const double excitation) noexcept
{
    if (!std::isfinite(excitation)) {
        reset();
        return 0.0;
    }

    const double previous_real = state_real_;
    const double previous_imag = state_imag_;
    state_real_ = excitation
        + radius_ * (cosine_ * previous_real - sine_ * previous_imag);
    state_imag_ = radius_ * (sine_ * previous_real + cosine_ * previous_imag);
    const double output = parameters_.gain * state_real_;
    if (!std::isfinite(state_real_) || !std::isfinite(state_imag_)
        || !std::isfinite(output)) {
        reset();
        return 0.0;
    }

    // Prevent a completed tail from leaving subnormal state in the audio loop.
    constexpr double denormal_threshold = 1.0e-300;
    if (std::abs(state_real_) < denormal_threshold
        && std::abs(state_imag_) < denormal_threshold) {
        reset();
    }
    return output;
}

void Resonator::process_block(
    const double* excitation,
    double* output,
    const std::size_t frame_count) noexcept
{
    if (output == nullptr) {
        return;
    }
    for (std::size_t index = 0; index < frame_count; ++index) {
        output[index] = process_sample(excitation == nullptr ? 0.0 : excitation[index]);
    }
}

void Resonator::reset() noexcept
{
    state_real_ = 0.0;
    state_imag_ = 0.0;
}

} // namespace qmw
