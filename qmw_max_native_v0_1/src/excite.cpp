#include "qmw/excite.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <numbers>

namespace qmw {

std::string_view excitation_shape_name(const ExcitationShape shape) noexcept
{
    switch (shape) {
    case ExcitationShape::impulse:
        return "impulse";
    case ExcitationShape::box:
        return "box";
    case ExcitationShape::hann:
        return "hann";
    }
    return "invalid_shape";
}

std::string_view excitation_admission_code_name(
    const ExcitationAdmissionCode code) noexcept
{
    switch (code) {
    case ExcitationAdmissionCode::accepted:
        return "accepted";
    case ExcitationAdmissionCode::stale_event_id:
        return "stale_event_id";
    case ExcitationAdmissionCode::stale_revision:
        return "stale_revision";
    case ExcitationAdmissionCode::invalid_strength:
        return "invalid_strength";
    case ExcitationAdmissionCode::invalid_duration:
        return "invalid_duration";
    case ExcitationAdmissionCode::invalid_shape:
        return "invalid_shape";
    case ExcitationAdmissionCode::onset_out_of_range:
        return "onset_out_of_range";
    case ExcitationAdmissionCode::capacity_full:
        return "capacity_full";
    }
    return "unknown";
}

ExcitationAdmissionCode Exciter::validate(const ExcitationEvent& event) const noexcept
{
    if (!std::isfinite(event.strength)
        || event.strength < minimum_strength
        || event.strength > maximum_strength) {
        return ExcitationAdmissionCode::invalid_strength;
    }
    if (event.duration_samples == 0
        || event.duration_samples > maximum_duration_samples
        || (event.shape == ExcitationShape::impulse && event.duration_samples != 1)) {
        return ExcitationAdmissionCode::invalid_duration;
    }
    switch (event.shape) {
    case ExcitationShape::impulse:
    case ExcitationShape::box:
    case ExcitationShape::hann:
        break;
    default:
        return ExcitationAdmissionCode::invalid_shape;
    }
    if (event.onset_samples > maximum_onset_samples) {
        return ExcitationAdmissionCode::onset_out_of_range;
    }
    if (event.onset_samples > std::numeric_limits<std::uint64_t>::max() - sample_clock_
        || event.duration_samples - 1
            > std::numeric_limits<std::uint64_t>::max()
                - (sample_clock_ + event.onset_samples)) {
        return ExcitationAdmissionCode::onset_out_of_range;
    }
    return ExcitationAdmissionCode::accepted;
}

ExcitationAdmission Exciter::admit(const ExcitationEvent& event) noexcept
{
    const auto invalid = validate(event);
    if (invalid != ExcitationAdmissionCode::accepted) {
        return {invalid, event.event_id, event.revision};
    }
    if (has_watermark_ && event.event_id <= last_event_id_) {
        return {ExcitationAdmissionCode::stale_event_id, event.event_id, event.revision};
    }
    if (has_watermark_ && event.revision < latest_revision_) {
        return {ExcitationAdmissionCode::stale_revision, event.event_id, event.revision};
    }

    auto* destination = static_cast<Slot*>(nullptr);
    for (auto& slot : slots_) {
        if (!slot.occupied) {
            destination = &slot;
            break;
        }
    }
    if (destination == nullptr) {
        return {ExcitationAdmissionCode::capacity_full, event.event_id, event.revision};
    }

    destination->event = event;
    destination->start_sample = sample_clock_ + event.onset_samples;
    destination->occupied = true;
    last_event_id_ = event.event_id;
    latest_revision_ = event.revision;
    has_watermark_ = true;
    return {ExcitationAdmissionCode::accepted, event.event_id, event.revision};
}

double Exciter::envelope(
    const ExcitationShape shape,
    const std::uint64_t position,
    const std::uint64_t duration) noexcept
{
    switch (shape) {
    case ExcitationShape::impulse:
    case ExcitationShape::box:
        return 1.0;
    case ExcitationShape::hann: {
        if (duration == 1) {
            return 1.0;
        }
        const long double denominator = static_cast<long double>(duration) + 1.0L;
        const auto peak_position = (duration - 1) / 2;
        const long double phase = std::numbers::pi_v<long double>
            * (static_cast<long double>(position) + 1.0L) / denominator;
        const long double peak_phase = std::numbers::pi_v<long double>
            * (static_cast<long double>(peak_position) + 1.0L) / denominator;
        const long double numerator = std::sin(phase);
        const long double peak = std::sin(peak_phase);
        const long double ratio = numerator / peak;
        return static_cast<double>(ratio * ratio);
    }
    }
    return 0.0;
}

double Exciter::process_sample() noexcept
{
    long double sum = 0.0L;
    for (auto& slot : slots_) {
        if (!slot.occupied || sample_clock_ < slot.start_sample) {
            continue;
        }
        const auto position = sample_clock_ - slot.start_sample;
        if (position >= slot.event.duration_samples) {
            slot.occupied = false;
            continue;
        }
        if (!muted_) {
            sum += static_cast<long double>(slot.event.strength)
                * envelope(slot.event.shape, position, slot.event.duration_samples);
        }
        if (position + 1 == slot.event.duration_samples) {
            slot.occupied = false;
        }
    }

    if (sample_clock_ != std::numeric_limits<std::uint64_t>::max()) {
        ++sample_clock_;
    }
    if (muted_) {
        return 0.0;
    }
    return static_cast<double>(std::clamp(sum, -1.0L, 1.0L));
}

void Exciter::process_block(double* output, const std::size_t frame_count) noexcept
{
    if (output == nullptr) {
        return;
    }
    for (std::size_t index = 0; index < frame_count; ++index) {
        output[index] = process_sample();
    }
}

void Exciter::reset() noexcept
{
    for (auto& slot : slots_) {
        slot.occupied = false;
    }
}

std::size_t Exciter::active_event_count() const noexcept
{
    return static_cast<std::size_t>(std::count_if(
        slots_.begin(), slots_.end(), [](const Slot& slot) { return slot.occupied; }));
}

} // namespace qmw
