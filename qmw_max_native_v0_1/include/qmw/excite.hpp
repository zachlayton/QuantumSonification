#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace qmw {

enum class ExcitationShape {
    impulse,
    box,
    hann,
};

[[nodiscard]] std::string_view excitation_shape_name(ExcitationShape shape) noexcept;

// An event is an admitted, finite excitation command. Identity is monotonic and
// independent of source-state revision: distinct events may intentionally come
// from the same upstream revision.
struct ExcitationEvent {
    std::uint64_t event_id {};
    std::uint64_t revision {};
    // Delay from the Exciter's current sample clock at admission.
    std::uint64_t onset_samples {};
    // Signed peak amplitude. This is an authored mapping result, not a rate.
    double strength {1.0};
    std::uint64_t duration_samples {1};
    ExcitationShape shape {ExcitationShape::impulse};
};

enum class ExcitationAdmissionCode {
    accepted,
    stale_event_id,
    stale_revision,
    invalid_strength,
    invalid_duration,
    invalid_shape,
    onset_out_of_range,
    capacity_full,
};

[[nodiscard]] std::string_view excitation_admission_code_name(
    ExcitationAdmissionCode code) noexcept;

struct ExcitationAdmission {
    ExcitationAdmissionCode code {ExcitationAdmissionCode::capacity_full};
    std::uint64_t event_id {};
    std::uint64_t revision {};

    [[nodiscard]] bool accepted() const noexcept
    {
        return code == ExcitationAdmissionCode::accepted;
    }
};

// A deterministic finite-event excitation source. It contains no oscillator,
// resonator, noise source, quantum state, or note-selection logic.
//
// At sample clock t, event j contributes strength_j * w_j(t - start_j), where
//
//   impulse: w(0) = 1, duration must be 1
//   box:     w(n) = 1, 0 <= n < N
//   hann:    w(n) = [sin(pi (n+1)/(N+1)) / peak_N]^2, 0 <= n < N
//            peak_N = sin(pi (floor((N-1)/2)+1)/(N+1))
//
// and contributes exactly zero otherwise. Simultaneous events are summed in
// ascending fixed-slot order using long-double accumulation, then saturated to
// [-1, 1]. This overlap policy is stable and explicitly bounds the output.
class Exciter final {
public:
    static constexpr std::size_t event_capacity = 64;
    static constexpr std::uint64_t maximum_onset_samples = 7'680'000;
    static constexpr std::uint64_t maximum_duration_samples = 7'680'000;
    static constexpr double minimum_strength = -1.0;
    static constexpr double maximum_strength = 1.0;

    [[nodiscard]] ExcitationAdmission admit(const ExcitationEvent& event) noexcept;

    [[nodiscard]] double process_sample() noexcept;
    void process_block(double* output, std::size_t frame_count) noexcept;

    // Clears all scheduled and active events. The sample clock and replay
    // watermarks remain intact so reset cannot make a stale event admissible.
    void reset() noexcept;

    // Muting emits exact zeros while the sample clock and event lifetimes keep
    // advancing. An event that ends during mute does not reappear on unmute.
    void set_muted(bool muted) noexcept { muted_ = muted; }

    [[nodiscard]] bool muted() const noexcept { return muted_; }
    [[nodiscard]] std::uint64_t sample_clock() const noexcept { return sample_clock_; }
    [[nodiscard]] std::size_t active_event_count() const noexcept;
    [[nodiscard]] bool has_admitted_event() const noexcept { return has_watermark_; }
    [[nodiscard]] std::uint64_t last_event_id() const noexcept { return last_event_id_; }
    [[nodiscard]] std::uint64_t latest_revision() const noexcept { return latest_revision_; }

private:
    struct Slot {
        ExcitationEvent event {};
        std::uint64_t start_sample {};
        bool occupied {false};
    };

    [[nodiscard]] ExcitationAdmissionCode validate(
        const ExcitationEvent& event) const noexcept;
    [[nodiscard]] static double envelope(
        ExcitationShape shape,
        std::uint64_t position,
        std::uint64_t duration) noexcept;

    std::array<Slot, event_capacity> slots_ {};
    std::uint64_t sample_clock_ {};
    std::uint64_t last_event_id_ {};
    std::uint64_t latest_revision_ {};
    bool has_watermark_ {false};
    bool muted_ {false};
};

} // namespace qmw
