#pragma once

#include <array>
#include <cstddef>
#include <span>
#include <string_view>

namespace qmw {

inline constexpr std::size_t maximum_interference_timbre_modes = 64;

enum class InterferenceTimbreCode {
    accepted,
    empty,
    too_many_modes,
    invalid_amplitude,
    invalid_phase,
    invalid_spread,
    invalid_depth,
    invalid_slew,
};

[[nodiscard]] std::string_view interference_timbre_code_name(
    InterferenceTimbreCode code) noexcept;

struct InterferenceTimbreProjection {
    InterferenceTimbreCode code {InterferenceTimbreCode::empty};
    std::size_t mode_count {};
    std::array<double, maximum_interference_timbre_modes> gain_factors {};
    std::array<double, maximum_interference_timbre_modes> output_amplitudes {};
    double base_power {};
    double interfered_power {};
    double output_power {};
    bool complete_cancellation {false};

    [[nodiscard]] bool accepted() const noexcept
    {
        return code == InterferenceTimbreCode::accepted;
    }
};

// Designed timbre projection. Mode frequencies and the authoritative quantum
// state are untouched. For zero-based lane j:
//
//   raw_j = 2 (1 + depth cos(phase + j spread))
//   out_j = A_j sqrt(raw_j * sum(A^2) / sum(A^2 raw))
//
// This preserves base modal power except at complete cancellation. A depth of
// zero is an exact identity, avoiding a needless floating-point round trip.
[[nodiscard]] InterferenceTimbreProjection project_interference_timbre(
    std::span<const double> base_amplitudes,
    double phase_radians,
    double phase_spread_radians,
    double depth) noexcept;

} // namespace qmw
