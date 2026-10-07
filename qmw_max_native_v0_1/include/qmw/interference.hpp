#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace qmw {

struct IQSample {
    double in_phase {};
    double quadrature {};
};

struct InterferenceLane {
    // Non-negative magnitude. Polarity is represented by phase, not by a
    // second, ambiguous sign convention.
    double amplitude {1.0};
    double phase_radians {};
};

enum class InterferenceControlCode {
    accepted,
    invalid_lane,
    invalid_amplitude,
    invalid_phase,
    invalid_headroom,
};

[[nodiscard]] std::string_view interference_control_code_name(
    InterferenceControlCode code) noexcept;

// A deterministic coherent complex mixer. It owns no oscillator, density
// matrix, visual state, or note/event authority. For lane k,
//
//   z_k = I_k + i Q_k
//   y   = g sum_k a_k exp(i phi_k) z_k
//   g   = headroom / max(1, sum_k a_k)
//
// Thus, when every input obeys |z_k| <= 1, |y| <= headroom. The fixed
// sum-of-declared-amplitudes normalization reserves headroom even when a
// declared lane happens to be silent; it does not pump gain with the signal.
// I and Q remain separate through the output. No real projection is hidden.
//
// Lanes are accumulated in ascending index order with long-double
// accumulators. Processing and control updates allocate no memory and acquire
// no locks. A non-finite sample on an active lane rejects the complete frame to
// exact I/Q silence, preventing NaN/Inf contamination of downstream DSP.
class InterferenceMixer final {
public:
    static constexpr std::size_t minimum_lane_count = 1;
    static constexpr std::size_t maximum_lane_count = 16;
    static constexpr double minimum_amplitude = 0.0;
    static constexpr double maximum_amplitude = 1.0;
    static constexpr double minimum_headroom = 0.0;
    static constexpr double maximum_headroom = 1.0;
    static constexpr double default_headroom = 0.5; // -6.0206 dBFS

    explicit InterferenceMixer(
        std::size_t lane_count = 2,
        double headroom = default_headroom);

    [[nodiscard]] InterferenceControlCode set_lane(
        std::size_t lane,
        double amplitude,
        double phase_radians) noexcept;
    [[nodiscard]] InterferenceControlCode set_amplitude(
        std::size_t lane,
        double amplitude) noexcept;
    [[nodiscard]] InterferenceControlCode set_phase(
        std::size_t lane,
        double phase_radians) noexcept;
    [[nodiscard]] InterferenceControlCode set_headroom(double headroom) noexcept;

    // Restores unity-amplitude, zero-phase lanes, default headroom, and unmute.
    // The mixer has no delay/history state to clear.
    void reset() noexcept;
    void set_muted(bool muted) noexcept { muted_ = muted; }

    [[nodiscard]] std::size_t lane_count() const noexcept { return lane_count_; }
    [[nodiscard]] const InterferenceLane& lane(std::size_t lane) const noexcept;
    [[nodiscard]] double headroom() const noexcept { return headroom_; }
    [[nodiscard]] double normalization_gain() const noexcept { return normalization_gain_; }
    [[nodiscard]] bool muted() const noexcept { return muted_; }
    [[nodiscard]] std::uint64_t rejected_frame_count() const noexcept
    {
        return rejected_frame_count_;
    }

    [[nodiscard]] bool process_sample(
        const IQSample* lanes,
        IQSample& output) noexcept;
    void process_block(
        const double* const* in_phase_inputs,
        const double* const* quadrature_inputs,
        double* in_phase_output,
        double* quadrature_output,
        std::size_t frame_count) noexcept;

private:
    struct Coefficient {
        double cosine {1.0};
        double sine {};
    };

    void update_lane_coefficient(std::size_t lane) noexcept;
    void update_normalization() noexcept;
    [[nodiscard]] bool mix_frame(
        const IQSample* lanes,
        IQSample& output) noexcept;

    std::array<InterferenceLane, maximum_lane_count> lanes_ {};
    std::array<Coefficient, maximum_lane_count> coefficients_ {};
    std::size_t lane_count_ {2};
    double headroom_ {default_headroom};
    double normalization_gain_ {};
    std::uint64_t rejected_frame_count_ {};
    bool muted_ {false};
};

} // namespace qmw
