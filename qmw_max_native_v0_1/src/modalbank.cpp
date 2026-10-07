#include "qmw/modalbank.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>

namespace qmw {

std::string_view modal_frame_code_name(const ModalFrameCode code) noexcept
{
    switch (code) {
    case ModalFrameCode::published:
        return "published";
    case ModalFrameCode::stale_revision:
        return "stale_revision";
    case ModalFrameCode::empty_frequency_list:
        return "empty_frequency_list";
    case ModalFrameCode::too_many_modes:
        return "too_many_modes";
    case ModalFrameCode::duplicate_mode_id:
        return "duplicate_mode_id";
    case ModalFrameCode::invalid_frequency:
        return "invalid_frequency";
    case ModalFrameCode::invalid_decay:
        return "invalid_decay";
    case ModalFrameCode::invalid_gain:
        return "invalid_gain";
    case ModalFrameCode::invalid_pan:
        return "invalid_pan";
    case ModalFrameCode::invalid_phase:
        return "invalid_phase";
    }
    return "unknown";
}

std::string_view modal_frequency_code_name(const ModalFrequencyCode code) noexcept
{
    switch (code) {
    case ModalFrequencyCode::applied:
        return "applied";
    case ModalFrequencyCode::no_active_frame:
        return "no_active_frame";
    case ModalFrequencyCode::mode_not_found:
        return "mode_not_found";
    case ModalFrequencyCode::invalid_frequency:
        return "invalid_frequency";
    }
    return "unknown";
}

ModalBank::ModalBank(const double sample_rate_hz)
{
    if (!set_sample_rate_hz(sample_rate_hz)) {
        sample_rate_hz_ = 48000.0;
        publication_sample_rate_hz_.store(sample_rate_hz_, std::memory_order_relaxed);
    }
}

ModalFrameCode ModalBank::validate_frame(
    const std::span<const ModalDescriptor> modes) const noexcept
{
    if (modes.size() > maximum_modes) {
        return ModalFrameCode::too_many_modes;
    }
    const double sample_rate = publication_sample_rate_hz_.load(std::memory_order_acquire);
    for (std::size_t index = 0; index < modes.size(); ++index) {
        const auto& mode = modes[index];
        if (!std::isfinite(mode.frequency_hz)
            || mode.frequency_hz < minimum_frequency_hz
            || mode.frequency_hz > maximum_frequency_fraction * sample_rate) {
            return ModalFrameCode::invalid_frequency;
        }
        if (!std::isfinite(mode.decay_seconds)
            || mode.decay_seconds < minimum_decay_seconds
            || mode.decay_seconds > maximum_decay_seconds) {
            return ModalFrameCode::invalid_decay;
        }
        if (!std::isfinite(mode.gain)
            || mode.gain < minimum_gain
            || mode.gain > maximum_gain) {
            return ModalFrameCode::invalid_gain;
        }
        if (!std::isfinite(mode.pan)
            || mode.pan < minimum_pan || mode.pan > maximum_pan) {
            return ModalFrameCode::invalid_pan;
        }
        if (!std::isfinite(mode.phase_radians)
            || mode.phase_radians < -maximum_phase_radians
            || mode.phase_radians > maximum_phase_radians) {
            return ModalFrameCode::invalid_phase;
        }
        for (std::size_t other = 0; other < index; ++other) {
            if (modes[other].mode_id == mode.mode_id) {
                return ModalFrameCode::duplicate_mode_id;
            }
        }
    }
    return ModalFrameCode::published;
}

ModalFrameAdmission ModalBank::publish_frame(
    const std::uint64_t revision,
    const std::span<const ModalDescriptor> modes) noexcept
{
    if (has_published_frame_.load(std::memory_order_acquire)
        && revision <= published_revision_.load(std::memory_order_acquire)) {
        return {ModalFrameCode::stale_revision, revision, modes.size()};
    }
    const auto validation = validate_frame(modes);
    if (validation != ModalFrameCode::published) {
        return {validation, revision, modes.size()};
    }

    std::array<ModalDescriptor, maximum_modes> ordered {};
    std::copy(modes.begin(), modes.end(), ordered.begin());
    std::sort(
        ordered.begin(), ordered.begin() + static_cast<std::ptrdiff_t>(modes.size()),
        [](const ModalDescriptor& left, const ModalDescriptor& right) {
            return left.mode_id < right.mode_id;
        });

    // One message-thread producer. Odd marks an in-progress publication; even
    // marks a complete immutable snapshot for the audio-thread consumer.
    publication_sequence_.fetch_add(1, std::memory_order_acq_rel);
    for (std::size_t index = 0; index < modes.size(); ++index) {
        const auto& source = ordered[index];
        auto& destination = published_descriptors_[index];
        destination.mode_id.store(source.mode_id, std::memory_order_relaxed);
        destination.frequency_hz.store(source.frequency_hz, std::memory_order_relaxed);
        destination.decay_seconds.store(source.decay_seconds, std::memory_order_relaxed);
        destination.gain.store(source.gain, std::memory_order_relaxed);
        destination.pan.store(source.pan, std::memory_order_relaxed);
        destination.phase_radians.store(source.phase_radians, std::memory_order_relaxed);
    }
    published_count_.store(modes.size(), std::memory_order_relaxed);
    published_revision_.store(revision, std::memory_order_relaxed);
    has_published_frame_.store(true, std::memory_order_relaxed);
    publication_sequence_.fetch_add(1, std::memory_order_release);
    return {ModalFrameCode::published, revision, modes.size()};
}

ModalFrameAdmission ModalBank::publish_frequencies(
    const std::uint64_t revision,
    const std::span<const double> frequencies_hz) noexcept
{
    if (frequencies_hz.empty()) {
        return {ModalFrameCode::empty_frequency_list, revision, 0};
    }
    if (frequencies_hz.size() > maximum_modes) {
        return {ModalFrameCode::too_many_modes, revision, frequencies_hz.size()};
    }

    std::array<ModalDescriptor, maximum_modes> modes {};
    for (std::size_t index = 0; index < frequencies_hz.size(); ++index) {
        modes[index] = {
            static_cast<std::uint32_t>(index),
            frequencies_hz[index],
            simple_decay_seconds,
            simple_gain,
            simple_pan,
            simple_phase_radians,
        };
    }
    return publish_frame(
        revision,
        std::span<const ModalDescriptor>(modes.data(), frequencies_hz.size()));
}

bool ModalBank::read_published_frame(
    std::uint64_t& revision,
    std::size_t& count,
    std::array<ModalDescriptor, maximum_modes>& modes) const noexcept
{
    const auto sequence_before = publication_sequence_.load(std::memory_order_acquire);
    if ((sequence_before & 1U) != 0U
        || !has_published_frame_.load(std::memory_order_relaxed)) {
        return false;
    }
    count = published_count_.load(std::memory_order_relaxed);
    revision = published_revision_.load(std::memory_order_relaxed);
    if (count > maximum_modes) {
        return false;
    }
    for (std::size_t index = 0; index < count; ++index) {
        const auto& source = published_descriptors_[index];
        modes[index] = {
            source.mode_id.load(std::memory_order_relaxed),
            source.frequency_hz.load(std::memory_order_relaxed),
            source.decay_seconds.load(std::memory_order_relaxed),
            source.gain.load(std::memory_order_relaxed),
            source.pan.load(std::memory_order_relaxed),
            source.phase_radians.load(std::memory_order_relaxed),
        };
    }
    const auto sequence_after = publication_sequence_.load(std::memory_order_acquire);
    return sequence_before == sequence_after && (sequence_after & 1U) == 0U;
}

bool ModalBank::apply_pending_frame() noexcept
{
    std::array<ModalDescriptor, maximum_modes> pending {};
    std::uint64_t revision = 0;
    std::size_t count = 0;
    if (!read_published_frame(revision, count, pending)
        || (has_active_frame_ && revision <= active_revision_)) {
        return false;
    }
    if (validate_frame(std::span<const ModalDescriptor>(pending.data(), count))
        != ModalFrameCode::published) {
        return false;
    }

    std::array<ModeState, maximum_modes> next_states {};
    for (std::size_t next = 0; next < count; ++next) {
        next_states[next].timbre_gain = 1.0;
        for (std::size_t current = 0; current < active_count_; ++current) {
            if (pending[next].mode_id == active_descriptors_[current].mode_id) {
                next_states[next].real = states_[current].real;
                next_states[next].imag = states_[current].imag;
                next_states[next].timbre_gain = states_[current].timbre_gain;
                break;
            }
        }
    }
    active_descriptors_ = pending;
    states_ = next_states;
    active_count_ = count;
    active_revision_ = revision;
    has_active_frame_ = true;
    for (std::size_t index = 0; index < active_count_; ++index) {
        update_coefficients(index);
    }
    static_cast<void>(update_interference_targets());
    update_normalization();
    return true;
}

bool ModalBank::set_sample_rate_hz(const double sample_rate_hz) noexcept
{
    if (!std::isfinite(sample_rate_hz)
        || sample_rate_hz < minimum_sample_rate_hz
        || sample_rate_hz > maximum_sample_rate_hz) {
        return false;
    }
    for (std::size_t index = 0; index < active_count_; ++index) {
        if (active_descriptors_[index].frequency_hz
            > maximum_frequency_fraction * sample_rate_hz) {
            return false;
        }
    }
    sample_rate_hz_ = sample_rate_hz;
    publication_sample_rate_hz_.store(sample_rate_hz, std::memory_order_release);
    for (std::size_t index = 0; index < active_count_; ++index) {
        update_coefficients(index);
    }
    return true;
}

ModalFrequencyCode ModalBank::set_mode_frequency_hz(
    const std::uint32_t mode_id,
    const double frequency_hz) noexcept
{
    if (!std::isfinite(frequency_hz)
        || frequency_hz < minimum_frequency_hz
        || frequency_hz > maximum_frequency_fraction * sample_rate_hz_) {
        return ModalFrequencyCode::invalid_frequency;
    }
    if (!has_active_frame_) {
        return ModalFrequencyCode::no_active_frame;
    }
    for (std::size_t index = 0; index < active_count_; ++index) {
        if (active_descriptors_[index].mode_id == mode_id) {
            active_descriptors_[index].frequency_hz = frequency_hz;
            update_coefficients(index);
            return ModalFrequencyCode::applied;
        }
    }
    return ModalFrequencyCode::mode_not_found;
}

ModalFrequencyCode ModalBank::set_base_frequency_hz(
    const double base_frequency_hz) noexcept
{
    if (!std::isfinite(base_frequency_hz)
        || base_frequency_hz < minimum_frequency_hz
        || base_frequency_hz > maximum_frequency_fraction * sample_rate_hz_) {
        return ModalFrequencyCode::invalid_frequency;
    }
    if (!has_active_frame_ || active_count_ == 0) {
        return ModalFrequencyCode::no_active_frame;
    }
    double current_base = active_descriptors_[0].frequency_hz;
    for (std::size_t index = 1; index < active_count_; ++index) {
        current_base = std::min(current_base, active_descriptors_[index].frequency_hz);
    }
    const double ratio = base_frequency_hz / current_base;
    std::array<double, maximum_modes> scaled {};
    for (std::size_t index = 0; index < active_count_; ++index) {
        scaled[index] = active_descriptors_[index].frequency_hz * ratio;
        if (!std::isfinite(scaled[index])
            || scaled[index] < minimum_frequency_hz
            || scaled[index] > maximum_frequency_fraction * sample_rate_hz_) {
            return ModalFrequencyCode::invalid_frequency;
        }
    }
    for (std::size_t index = 0; index < active_count_; ++index) {
        active_descriptors_[index].frequency_hz = scaled[index];
        update_coefficients(index);
    }
    return ModalFrequencyCode::applied;
}

InterferenceTimbreCode ModalBank::set_interference_timbre(
    const double phase_radians,
    const double phase_spread_radians,
    const double depth,
    const double slew_seconds) noexcept
{
    if (!std::isfinite(phase_radians)) {
        return InterferenceTimbreCode::invalid_phase;
    }
    if (!std::isfinite(phase_spread_radians)) {
        return InterferenceTimbreCode::invalid_spread;
    }
    if (!std::isfinite(depth) || depth < 0.0 || depth > 1.0) {
        return InterferenceTimbreCode::invalid_depth;
    }
    if (!std::isfinite(slew_seconds) || slew_seconds < 0.0 || slew_seconds > 10.0) {
        return InterferenceTimbreCode::invalid_slew;
    }
    interference_phase_radians_ = phase_radians;
    interference_phase_spread_radians_ = phase_spread_radians;
    interference_depth_ = depth;
    interference_slew_seconds_ = slew_seconds;
    return update_interference_targets();
}

InterferenceTimbreCode ModalBank::clear_interference_timbre(
    const double slew_seconds) noexcept
{
    return set_interference_timbre(0.0, 0.0, 0.0, slew_seconds);
}

InterferenceTimbreCode ModalBank::update_interference_targets() noexcept
{
    if (active_count_ == 0) {
        interference_target_gains_.fill(1.0);
        return InterferenceTimbreCode::accepted;
    }
    std::array<double, maximum_modes> amplitudes {};
    for (std::size_t index = 0; index < active_count_; ++index) {
        amplitudes[index] = active_descriptors_[index].gain;
    }
    const auto projection = project_interference_timbre(
        std::span<const double>(amplitudes.data(), active_count_),
        interference_phase_radians_,
        interference_phase_spread_radians_,
        interference_depth_);
    if (!projection.accepted()) {
        return projection.code;
    }
    std::copy_n(
        projection.gain_factors.begin(),
        active_count_,
        interference_target_gains_.begin());
    if (interference_slew_seconds_ == 0.0) {
        for (std::size_t index = 0; index < active_count_; ++index) {
            states_[index].timbre_gain = interference_target_gains_[index];
        }
    }
    update_normalization();
    return InterferenceTimbreCode::accepted;
}

void ModalBank::set_headroom(const double headroom) noexcept
{
    if (!std::isfinite(headroom)) {
        return;
    }
    headroom_ = std::clamp(headroom, 0.0, 1.0);
    update_normalization();
}

void ModalBank::set_solo_mode(const std::uint32_t mode_id) noexcept
{
    solo_mode_id_ = mode_id;
    solo_enabled_ = true;
    update_normalization();
}

void ModalBank::clear_solo() noexcept
{
    solo_enabled_ = false;
    update_normalization();
}

void ModalBank::update_coefficients(const std::size_t index) noexcept
{
    const auto& descriptor = active_descriptors_[index];
    auto& state = states_[index];
    const double theta = 2.0 * std::numbers::pi
        * descriptor.frequency_hz / sample_rate_hz_;
    state.radius = std::pow(
        10.0,
        -3.0 / (descriptor.decay_seconds * sample_rate_hz_));
    state.cosine = std::cos(theta);
    state.sine = std::sin(theta);
    state.phase_cosine = std::cos(descriptor.phase_radians);
    state.phase_sine = std::sin(descriptor.phase_radians);
    const double pan_angle = (descriptor.pan + 1.0) * std::numbers::pi / 4.0;
    state.pan_left = std::cos(pan_angle);
    state.pan_right = std::sin(pan_angle);
}

void ModalBank::update_normalization() noexcept
{
    long double gain_sum = 0.0L;
    for (std::size_t index = 0; index < active_count_; ++index) {
        if (!solo_enabled_ || active_descriptors_[index].mode_id == solo_mode_id_) {
            gain_sum += std::abs(static_cast<long double>(active_descriptors_[index].gain)
                * static_cast<long double>(states_[index].timbre_gain));
        }
    }
    normalization_ = headroom_
        / static_cast<double>(std::max(1.0L, gain_sum));
}

void ModalBank::process_block(
    const double* excitation,
    double* output_left,
    double* output_right,
    const std::size_t frame_count) noexcept
{
    (void)apply_pending_frame();
    last_block_peak_ = 0.0;
    for (std::size_t frame = 0; frame < frame_count; ++frame) {
        const double input = excitation == nullptr ? 0.0 : excitation[frame];
        if (!std::isfinite(input)) {
            reset();
            if (output_left != nullptr) {
                output_left[frame] = 0.0;
            }
            if (output_right != nullptr) {
                output_right[frame] = 0.0;
            }
            continue;
        }

        long double left = 0.0L;
        long double right = 0.0L;
        const double slew_coefficient = interference_slew_seconds_ == 0.0
            ? 1.0
            : -std::expm1(-1.0 / (interference_slew_seconds_ * sample_rate_hz_));
        bool normalization_changed = false;
        for (std::size_t index = 0; index < active_count_; ++index) {
            auto& state = states_[index];
            const auto& descriptor = active_descriptors_[index];
            const double previous_timbre_gain = state.timbre_gain;
            state.timbre_gain += slew_coefficient
                * (interference_target_gains_[index] - state.timbre_gain);
            normalization_changed = normalization_changed
                || state.timbre_gain != previous_timbre_gain;
            const double previous_real = state.real;
            const double previous_imag = state.imag;
            state.real = input * state.phase_cosine
                + state.radius
                    * (state.cosine * previous_real - state.sine * previous_imag);
            state.imag = input * state.phase_sine
                + state.radius
                    * (state.sine * previous_real + state.cosine * previous_imag);
            if (!std::isfinite(state.real) || !std::isfinite(state.imag)) {
                state.real = 0.0;
                state.imag = 0.0;
                continue;
            }
            if (!solo_enabled_ || descriptor.mode_id == solo_mode_id_) {
                const long double modal_output = static_cast<long double>(descriptor.gain)
                    * static_cast<long double>(state.timbre_gain)
                    * static_cast<long double>(state.real);
                left += modal_output * static_cast<long double>(state.pan_left);
                right += modal_output * static_cast<long double>(state.pan_right);
            }
            constexpr double denormal_threshold = 1.0e-300;
            if (std::abs(state.real) < denormal_threshold
                && std::abs(state.imag) < denormal_threshold) {
                state.real = 0.0;
                state.imag = 0.0;
            }
        }

        if (normalization_changed) {
            update_normalization();
        }

        double left_sample = static_cast<double>(left * normalization_);
        double right_sample = static_cast<double>(right * normalization_);
        if (!std::isfinite(left_sample) || !std::isfinite(right_sample)) {
            reset();
            left_sample = 0.0;
            right_sample = 0.0;
        } else {
            left_sample = std::clamp(left_sample, -1.0, 1.0);
            right_sample = std::clamp(right_sample, -1.0, 1.0);
        }
        if (muted_) {
            left_sample = 0.0;
            right_sample = 0.0;
        }
        last_block_peak_ = std::max(
            last_block_peak_, std::max(std::abs(left_sample), std::abs(right_sample)));
        if (output_left != nullptr) {
            output_left[frame] = left_sample;
        }
        if (output_right != nullptr) {
            output_right[frame] = right_sample;
        }
    }
}

void ModalBank::reset() noexcept
{
    for (auto& state : states_) {
        state.real = 0.0;
        state.imag = 0.0;
    }
    last_block_peak_ = 0.0;
}

} // namespace qmw
