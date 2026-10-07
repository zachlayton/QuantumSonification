#pragma once

#include <cstddef>
#include <cstdint>
#include <string_view>
#include <vector>

namespace qmw {

struct MemorySample {
    double in_phase {};
    double quadrature {};
};

enum class MemoryInterpolation {
    nearest,
    linear,
};

[[nodiscard]] std::string_view memory_interpolation_name(
    MemoryInterpolation interpolation) noexcept;

struct SignalMemoryParameters {
    // Both delays are measured in samples. A minimum of one sample makes the
    // feedback paths strictly causal. Fractional values use interpolation.
    double delay_i_samples {1.0};
    double delay_q_samples {1.0};
    double feedback {};
    double wet {1.0};
    double dry {};
    double headroom {0.5};
    MemoryInterpolation interpolation {MemoryInterpolation::linear};
};

enum class MemoryControlCode {
    accepted,
    invalid_delay_i,
    invalid_delay_q,
    invalid_feedback,
    invalid_wet,
    invalid_dry,
    invalid_headroom,
    invalid_interpolation,
};

[[nodiscard]] std::string_view memory_control_code_name(
    MemoryControlCode code) noexcept;

// A bounded, causal, dual-rail signal delay. It is signal memory only: it owns
// no density matrix, canonical quantum history, event schedule, oscillator, or
// resonant body.
//
// With write head w and rail R in {I, Q}, the delayed value is
//
//   r_R[n] = interpolate(B_R, w - d_R)
//   B_R[w] = x_R[n] + feedback * r_R[n]
//   y_R[n] = g * (dry * x_R[n] + wet * r_R[n])
//
// where d_R >= 1, |feedback| <= 0.99, and
//
//   g = headroom / max(1, dry + wet / (1 - |feedback|)).
//
// Consequently, for |x_R[n]| <= 1 and an initially empty memory,
// |y_R[n]| <= headroom on each rail. Linear interpolation is the convex blend
// of the floor- and ceiling-age samples; nearest rounds half upward. I and Q
// retain independent delay histories and are never projected to a real signal.
//
// The circular buffer allocates only in the constructor. Processing, parameter
// updates, mute, and constant-time reset allocate no memory and acquire no
// locks. A non-finite I or Q input rejects the complete frame to exact I/Q
// silence, advances time using zero input, and cannot contaminate the buffer.
// Mute emits exact silence while the finite input and feedback history continue
// causally. Reset invalidates all prior history without clearing the buffer.
class SignalMemory final {
public:
    static constexpr std::size_t minimum_maximum_delay_samples = 1;
    static constexpr std::size_t maximum_supported_delay_samples = 1'536'000;
    static constexpr double minimum_delay_samples = 1.0;
    static constexpr double maximum_feedback_magnitude = 0.99;
    static constexpr double minimum_mix = 0.0;
    static constexpr double maximum_mix = 1.0;
    static constexpr double minimum_headroom = 0.0;
    static constexpr double maximum_headroom = 1.0;
    static constexpr std::size_t default_maximum_delay_samples = 48'000;

    explicit SignalMemory(
        std::size_t maximum_delay_samples = default_maximum_delay_samples,
        SignalMemoryParameters parameters = {});

    [[nodiscard]] MemoryControlCode set_parameters(
        SignalMemoryParameters parameters) noexcept;
    [[nodiscard]] MemoryControlCode set_delays(
        double delay_i_samples,
        double delay_q_samples) noexcept;
    [[nodiscard]] MemoryControlCode set_delay_i(double delay_samples) noexcept;
    [[nodiscard]] MemoryControlCode set_delay_q(double delay_samples) noexcept;
    [[nodiscard]] MemoryControlCode set_feedback(double feedback) noexcept;
    [[nodiscard]] MemoryControlCode set_mix(double wet, double dry) noexcept;
    [[nodiscard]] MemoryControlCode set_wet(double wet) noexcept;
    [[nodiscard]] MemoryControlCode set_dry(double dry) noexcept;
    [[nodiscard]] MemoryControlCode set_headroom(double headroom) noexcept;
    [[nodiscard]] MemoryControlCode set_interpolation(
        MemoryInterpolation interpolation) noexcept;

    [[nodiscard]] bool process_sample(
        MemorySample input,
        MemorySample& output) noexcept;
    void process_block(
        const double* input_i,
        const double* input_q,
        double* output_i,
        double* output_q,
        std::size_t frame_count) noexcept;

    // Constant-time history invalidation. Parameters and rejection count remain.
    void reset() noexcept;
    void set_muted(bool muted) noexcept { muted_ = muted; }

    [[nodiscard]] std::size_t maximum_delay_samples() const noexcept
    {
        return maximum_delay_samples_;
    }
    [[nodiscard]] const SignalMemoryParameters& parameters() const noexcept
    {
        return parameters_;
    }
    [[nodiscard]] double normalization_gain() const noexcept
    {
        return normalization_gain_;
    }
    [[nodiscard]] bool muted() const noexcept { return muted_; }
    [[nodiscard]] std::uint64_t rejected_sample_count() const noexcept
    {
        return rejected_sample_count_;
    }
    [[nodiscard]] std::size_t valid_history_samples() const noexcept
    {
        return valid_history_samples_;
    }

private:
    [[nodiscard]] MemoryControlCode validate(
        const SignalMemoryParameters& parameters) const noexcept;
    [[nodiscard]] MemorySample read_delayed() const noexcept;
    [[nodiscard]] double read_rail(double delay, bool quadrature) const noexcept;
    [[nodiscard]] double read_age(std::size_t age, bool quadrature) const noexcept;
    void update_normalization() noexcept;

    std::vector<MemorySample> buffer_;
    std::size_t maximum_delay_samples_ {};
    std::size_t write_index_ {};
    std::size_t valid_history_samples_ {};
    SignalMemoryParameters parameters_ {};
    double normalization_gain_ {};
    std::uint64_t rejected_sample_count_ {};
    bool muted_ {false};
};

} // namespace qmw
