#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

#include "qmw/timbre.hpp"

namespace qmw {

static_assert(std::atomic<double>::is_always_lock_free);
static_assert(std::atomic<std::uint64_t>::is_always_lock_free);

struct ModalDescriptor {
    std::uint32_t mode_id {};
    double frequency_hz {440.0};
    // Amplitude T60 in seconds, identical to qmw::Resonator semantics.
    double decay_seconds {1.0};
    double gain {1.0};
    // Equal-power stereo position in [-1, 1].
    double pan {};
    // Excitation phase in radians, bounded to [-pi, pi].
    double phase_radians {};
};

enum class ModalFrameCode {
    published,
    stale_revision,
    empty_frequency_list,
    too_many_modes,
    duplicate_mode_id,
    invalid_frequency,
    invalid_decay,
    invalid_gain,
    invalid_pan,
    invalid_phase,
};

enum class ModalFrequencyCode {
    applied,
    no_active_frame,
    mode_not_found,
    invalid_frequency,
};

[[nodiscard]] std::string_view modal_frequency_code_name(
    ModalFrequencyCode code) noexcept;

[[nodiscard]] std::string_view modal_frame_code_name(ModalFrameCode code) noexcept;

struct ModalFrameAdmission {
    ModalFrameCode code {ModalFrameCode::too_many_modes};
    std::uint64_t revision {};
    std::size_t mode_count {};

    [[nodiscard]] bool published() const noexcept
    {
        return code == ModalFrameCode::published;
    }
};

// Fixed-capacity, stereo bank of damped complex pole pairs. Each mode follows
//
//   u_m[n] = x[n] [cos(phi_m), sin(phi_m)] + r_m R(theta_m) u_m[n-1]
//   r_m     = 10^(-3 / (T60_m sample_rate))
//   theta_m = 2 pi frequency_m / sample_rate
//
// Its real component is sent through equal-power pan. Mode outputs are scaled
// by headroom / max(1, sum(abs(gain_m))) and safety-clamped to [-1, 1].
//
// One control producer may call publish_frame while one audio consumer calls
// process_block. Published frames are transferred through an atomic seqlock;
// the audio path allocates no memory and acquires no locks. A complete frame is
// applied only at a process_block boundary. Stable mode IDs preserve resonant
// state across descriptor revisions; new modes begin at exact zero.
class ModalBank final {
public:
    static constexpr std::size_t maximum_modes = 64;
    static constexpr double minimum_sample_rate_hz = 8000.0;
    static constexpr double maximum_sample_rate_hz = 768000.0;
    static constexpr double minimum_frequency_hz = 1.0;
    static constexpr double maximum_frequency_fraction = 0.49;
    static constexpr double minimum_decay_seconds = 0.001;
    static constexpr double maximum_decay_seconds = 60.0;
    static constexpr double minimum_gain = 0.0;
    static constexpr double maximum_gain = 4.0;
    static constexpr double minimum_pan = -1.0;
    static constexpr double maximum_pan = 1.0;
    static constexpr double maximum_phase_radians = 3.14159265358979323846;
    static constexpr double simple_decay_seconds = 1.0;
    static constexpr double simple_gain = 1.0;
    static constexpr double simple_pan = 0.0;
    static constexpr double simple_phase_radians = 0.0;

    explicit ModalBank(double sample_rate_hz = 48000.0);

    [[nodiscard]] ModalFrameAdmission publish_frame(
        std::uint64_t revision,
        std::span<const ModalDescriptor> modes) noexcept;

    // Convenience frame constructor for Max's `frequencies F0 F1 ...`
    // message. Positions become stable mode IDs 0..N-1 and all remaining
    // descriptor fields use the simple_* defaults above. Admission stays
    // atomic and activation still occurs only at a process-block boundary.
    [[nodiscard]] ModalFrameAdmission publish_frequencies(
        std::uint64_t revision,
        std::span<const double> frequencies_hz) noexcept;

    // Returns true only when a newer complete frame was activated.
    [[nodiscard]] bool apply_pending_frame() noexcept;

    // Called at signal-vector boundaries. A rejected sample-rate request leaves
    // the current rate and coefficients unchanged.
    [[nodiscard]] bool set_sample_rate_hz(double sample_rate_hz) noexcept;
    // A non-revisioned live override for one stable mode ID. It is applied by
    // the audio thread at a vector boundary, preserves that mode's resonant
    // state, and is replaced by the next admitted descriptor frame.
    [[nodiscard]] ModalFrequencyCode set_mode_frequency_hz(
        std::uint32_t mode_id,
        double frequency_hz) noexcept;
    // Retunes the current lowest frequency to base_frequency_hz and scales all
    // other active mode frequencies by the same ratio. The update is atomic:
    // if any scaled mode would be invalid, no descriptor changes.
    [[nodiscard]] ModalFrequencyCode set_base_frequency_hz(
        double base_frequency_hz) noexcept;
    // Designed downstream timbre control. This changes per-mode gains only;
    // descriptor frequencies and upstream state authority remain untouched.
    [[nodiscard]] InterferenceTimbreCode set_interference_timbre(
        double phase_radians,
        double phase_spread_radians,
        double depth,
        double slew_seconds) noexcept;
    [[nodiscard]] InterferenceTimbreCode clear_interference_timbre(
        double slew_seconds = 0.0) noexcept;
    void set_headroom(double headroom) noexcept;
    void set_muted(bool muted) noexcept { muted_ = muted; }
    void set_solo_mode(std::uint32_t mode_id) noexcept;
    void clear_solo() noexcept;

    void process_block(
        const double* excitation,
        double* output_left,
        double* output_right,
        std::size_t frame_count) noexcept;
    void reset() noexcept;

    [[nodiscard]] double sample_rate_hz() const noexcept { return sample_rate_hz_; }
    [[nodiscard]] double headroom() const noexcept { return headroom_; }
    [[nodiscard]] bool muted() const noexcept { return muted_; }
    [[nodiscard]] bool solo_enabled() const noexcept { return solo_enabled_; }
    [[nodiscard]] std::uint32_t solo_mode_id() const noexcept { return solo_mode_id_; }
    [[nodiscard]] bool has_active_frame() const noexcept { return has_active_frame_; }
    [[nodiscard]] std::uint64_t active_revision() const noexcept { return active_revision_; }
    [[nodiscard]] std::size_t active_mode_count() const noexcept { return active_count_; }
    [[nodiscard]] const ModalDescriptor* active_descriptors() const noexcept
    {
        return active_descriptors_.data();
    }
    [[nodiscard]] double last_block_peak() const noexcept { return last_block_peak_; }

private:
    struct AtomicDescriptor {
        std::atomic<std::uint32_t> mode_id {};
        std::atomic<double> frequency_hz {};
        std::atomic<double> decay_seconds {};
        std::atomic<double> gain {};
        std::atomic<double> pan {};
        std::atomic<double> phase_radians {};
    };

    struct ModeState {
        double real {};
        double imag {};
        double radius {};
        double cosine {1.0};
        double sine {};
        double phase_cosine {1.0};
        double phase_sine {};
        double pan_left {0.70710678118654752440};
        double pan_right {0.70710678118654752440};
        double timbre_gain {1.0};
    };

    [[nodiscard]] ModalFrameCode validate_frame(
        std::span<const ModalDescriptor> modes) const noexcept;
    [[nodiscard]] bool read_published_frame(
        std::uint64_t& revision,
        std::size_t& count,
        std::array<ModalDescriptor, maximum_modes>& modes) const noexcept;
    void update_coefficients(std::size_t index) noexcept;
    [[nodiscard]] InterferenceTimbreCode update_interference_targets() noexcept;
    void update_normalization() noexcept;

    std::array<AtomicDescriptor, maximum_modes> published_descriptors_ {};
    std::atomic<std::uint64_t> publication_sequence_ {};
    std::atomic<std::uint64_t> published_revision_ {};
    std::atomic<std::size_t> published_count_ {};
    std::atomic<bool> has_published_frame_ {false};

    std::array<ModalDescriptor, maximum_modes> active_descriptors_ {};
    std::array<ModeState, maximum_modes> states_ {};
    double sample_rate_hz_ {48000.0};
    std::atomic<double> publication_sample_rate_hz_ {48000.0};
    double headroom_ {0.9};
    double normalization_ {0.9};
    double last_block_peak_ {};
    std::uint64_t active_revision_ {};
    std::size_t active_count_ {};
    bool has_active_frame_ {false};
    bool muted_ {false};
    bool solo_enabled_ {false};
    std::uint32_t solo_mode_id_ {};
    std::array<double, maximum_modes> interference_target_gains_ = [] {
        std::array<double, maximum_modes> values {};
        values.fill(1.0);
        return values;
    }();
    double interference_phase_radians_ {};
    double interference_phase_spread_radians_ {};
    double interference_depth_ {};
    double interference_slew_seconds_ {};
};

} // namespace qmw
