#include "qmw/timbre.hpp"

#include <algorithm>
#include <cmath>

namespace qmw {

std::string_view interference_timbre_code_name(
    const InterferenceTimbreCode code) noexcept
{
    switch (code) {
    case InterferenceTimbreCode::accepted:
        return "accepted";
    case InterferenceTimbreCode::empty:
        return "empty";
    case InterferenceTimbreCode::too_many_modes:
        return "too_many_modes";
    case InterferenceTimbreCode::invalid_amplitude:
        return "invalid_amplitude";
    case InterferenceTimbreCode::invalid_phase:
        return "invalid_phase";
    case InterferenceTimbreCode::invalid_spread:
        return "invalid_spread";
    case InterferenceTimbreCode::invalid_depth:
        return "invalid_depth";
    case InterferenceTimbreCode::invalid_slew:
        return "invalid_slew";
    }
    return "unknown";
}

InterferenceTimbreProjection project_interference_timbre(
    const std::span<const double> base_amplitudes,
    const double phase_radians,
    const double phase_spread_radians,
    const double depth) noexcept
{
    InterferenceTimbreProjection result;
    result.mode_count = base_amplitudes.size();
    if (base_amplitudes.empty()) {
        result.code = InterferenceTimbreCode::empty;
        return result;
    }
    if (base_amplitudes.size() > maximum_interference_timbre_modes) {
        result.code = InterferenceTimbreCode::too_many_modes;
        return result;
    }
    if (!std::isfinite(phase_radians)) {
        result.code = InterferenceTimbreCode::invalid_phase;
        return result;
    }
    if (!std::isfinite(phase_spread_radians)) {
        result.code = InterferenceTimbreCode::invalid_spread;
        return result;
    }
    if (!std::isfinite(depth) || depth < 0.0 || depth > 1.0) {
        result.code = InterferenceTimbreCode::invalid_depth;
        return result;
    }

    for (const double amplitude : base_amplitudes) {
        if (!std::isfinite(amplitude) || amplitude < 0.0) {
            result.code = InterferenceTimbreCode::invalid_amplitude;
            return result;
        }
        result.base_power += amplitude * amplitude;
    }
    result.code = InterferenceTimbreCode::accepted;

    if (depth == 0.0) {
        result.output_power = result.base_power;
        result.interfered_power = 2.0 * result.base_power;
        result.complete_cancellation = result.base_power == 0.0;
        for (std::size_t index = 0; index < base_amplitudes.size(); ++index) {
            result.gain_factors[index] = 1.0;
            result.output_amplitudes[index] = base_amplitudes[index];
        }
        return result;
    }

    std::array<double, maximum_interference_timbre_modes> raw_factors {};
    for (std::size_t index = 0; index < base_amplitudes.size(); ++index) {
        const double lane_phase = phase_radians
            + static_cast<double>(index) * phase_spread_radians;
        // Clamp protects the exact cancellation case from tiny negative values
        // caused by cosine roundoff.
        const double raw_factor = std::max(
            0.0,
            2.0 * (1.0 + depth * std::cos(lane_phase)));
        raw_factors[index] = raw_factor;
        result.interfered_power += base_amplitudes[index]
            * base_amplitudes[index] * raw_factor;
    }

    if (result.base_power == 0.0 || result.interfered_power <= 1.0e-24) {
        result.complete_cancellation = true;
        return result;
    }

    const double normalization = std::sqrt(
        result.base_power / result.interfered_power);
    for (std::size_t index = 0; index < base_amplitudes.size(); ++index) {
        const double factor = std::sqrt(raw_factors[index]) * normalization;
        result.gain_factors[index] = factor;
        result.output_amplitudes[index] = base_amplitudes[index] * factor;
        result.output_power += result.output_amplitudes[index]
            * result.output_amplitudes[index];
    }
    return result;
}

} // namespace qmw
