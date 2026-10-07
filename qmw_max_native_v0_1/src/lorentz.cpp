#include "qmw/lorentz.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <string>

namespace qmw {

namespace {

[[nodiscard]] bool representable_as_double(const long double value) noexcept
{
    constexpr auto limit = static_cast<long double>(std::numeric_limits<double>::max());
    return std::isfinite(value) && value >= -limit && value <= limit;
}

[[nodiscard]] double exact_zero(const double value) noexcept
{
    return value == 0.0 ? 0.0 : value;
}

} // namespace

std::string_view lorentz_control_code_name(const LorentzControlCode code) noexcept
{
    switch (code) {
    case LorentzControlCode::accepted:
        return "accepted";
    case LorentzControlCode::invalid_charge:
        return "invalid_charge";
    case LorentzControlCode::invalid_electric:
        return "invalid_electric";
    case LorentzControlCode::invalid_magnetic:
        return "invalid_magnetic";
    case LorentzControlCode::invalid_reference:
        return "invalid_reference";
    case LorentzControlCode::invalid_headroom:
        return "invalid_headroom";
    }
    return "unknown";
}

bool EffectiveLorentzModel::finite_vector(const Vector3 value) noexcept
{
    return std::isfinite(value.x) && std::isfinite(value.y) && std::isfinite(value.z);
}

LorentzControlCode EffectiveLorentzModel::validate_model(
    const LorentzModelControls& controls) noexcept
{
    if (!std::isfinite(controls.charge)) {
        return LorentzControlCode::invalid_charge;
    }
    if (!finite_vector(controls.electric)) {
        return LorentzControlCode::invalid_electric;
    }
    if (!finite_vector(controls.magnetic)) {
        return LorentzControlCode::invalid_magnetic;
    }
    return LorentzControlCode::accepted;
}

LorentzControlCode EffectiveLorentzModel::validate_mapping(
    const LorentzSignalMapping& mapping) noexcept
{
    if (!std::isfinite(mapping.force_reference) || mapping.force_reference <= 0.0) {
        return LorentzControlCode::invalid_reference;
    }
    if (!std::isfinite(mapping.headroom)
        || mapping.headroom < minimum_headroom
        || mapping.headroom > maximum_headroom) {
        return LorentzControlCode::invalid_headroom;
    }
    return LorentzControlCode::accepted;
}

EffectiveLorentzModel::EffectiveLorentzModel(
    const LorentzModelControls controls,
    const LorentzSignalMapping mapping)
    : controls_(controls)
    , mapping_(mapping)
{
    const auto model_code = validate_model(controls);
    if (model_code != LorentzControlCode::accepted) {
        throw std::invalid_argument(std::string(lorentz_control_code_name(model_code)));
    }
    const auto mapping_code = validate_mapping(mapping);
    if (mapping_code != LorentzControlCode::accepted) {
        throw std::invalid_argument(std::string(lorentz_control_code_name(mapping_code)));
    }
}

LorentzControlCode EffectiveLorentzModel::set_model(
    const LorentzModelControls& controls) noexcept
{
    const auto code = validate_model(controls);
    if (code == LorentzControlCode::accepted) {
        controls_ = controls;
    }
    return code;
}

LorentzControlCode EffectiveLorentzModel::set_charge(const double charge) noexcept
{
    auto candidate = controls_;
    candidate.charge = charge;
    return set_model(candidate);
}

LorentzControlCode EffectiveLorentzModel::set_electric(const Vector3 electric) noexcept
{
    auto candidate = controls_;
    candidate.electric = electric;
    return set_model(candidate);
}

LorentzControlCode EffectiveLorentzModel::set_magnetic(const Vector3 magnetic) noexcept
{
    auto candidate = controls_;
    candidate.magnetic = magnetic;
    return set_model(candidate);
}

LorentzControlCode EffectiveLorentzModel::set_mapping(
    const LorentzSignalMapping& mapping) noexcept
{
    const auto code = validate_mapping(mapping);
    if (code == LorentzControlCode::accepted) {
        mapping_ = mapping;
    }
    return code;
}

void EffectiveLorentzModel::reset_model() noexcept
{
    controls_ = {};
    muted_ = false;
}

bool EffectiveLorentzModel::process_sample(
    const Vector3 velocity,
    LorentzSample& output) noexcept
{
    output = {};
    if (!finite_vector(velocity)) {
        ++rejected_frame_count_;
        return false;
    }
    if (muted_) {
        return true;
    }
    // Preserve the exact algebraic zero before evaluating products that could
    // overflow despite their eventual multiplication by zero.
    if (controls_.charge == 0.0) {
        return true;
    }

    const auto vx = static_cast<long double>(velocity.x);
    const auto vy = static_cast<long double>(velocity.y);
    const auto vz = static_cast<long double>(velocity.z);
    const auto bx = static_cast<long double>(controls_.magnetic.x);
    const auto by = static_cast<long double>(controls_.magnetic.y);
    const auto bz = static_cast<long double>(controls_.magnetic.z);
    const auto q = static_cast<long double>(controls_.charge);

    const long double force_x = q
        * (static_cast<long double>(controls_.electric.x) + vy * bz - vz * by);
    const long double force_y = q
        * (static_cast<long double>(controls_.electric.y) + vz * bx - vx * bz);
    const long double force_z = q
        * (static_cast<long double>(controls_.electric.z) + vx * by - vy * bx);
    if (!representable_as_double(force_x)
        || !representable_as_double(force_y)
        || !representable_as_double(force_z)) {
        ++rejected_frame_count_;
        return false;
    }

    output.model_force = {
        exact_zero(static_cast<double>(force_x)),
        exact_zero(static_cast<double>(force_y)),
        exact_zero(static_cast<double>(force_z)),
    };
    output.model_force_magnitude = std::hypot(
        output.model_force.x,
        output.model_force.y,
        output.model_force.z);
    if (!std::isfinite(output.model_force_magnitude)) {
        output = {};
        ++rejected_frame_count_;
        return false;
    }
    if (output.model_force_magnitude == 0.0 || mapping_.headroom == 0.0) {
        return true;
    }

    const double denominator = std::max(
        mapping_.force_reference,
        output.model_force_magnitude);
    output.signal_magnitude = mapping_.headroom
        * (output.model_force_magnitude / denominator);
    const long double component_scale
        = static_cast<long double>(output.signal_magnitude)
        / static_cast<long double>(output.model_force_magnitude);
    output.signal = {
        exact_zero(static_cast<double>(force_x * component_scale)),
        exact_zero(static_cast<double>(force_y * component_scale)),
        exact_zero(static_cast<double>(force_z * component_scale)),
    };
    return true;
}

void EffectiveLorentzModel::process_block(
    const double* velocity_x,
    const double* velocity_y,
    const double* velocity_z,
    double* signal_x,
    double* signal_y,
    double* signal_z,
    double* signal_magnitude,
    const std::size_t frame_count) noexcept
{
    if (signal_x == nullptr || signal_y == nullptr || signal_z == nullptr
        || signal_magnitude == nullptr) {
        return;
    }
    for (std::size_t index = 0; index < frame_count; ++index) {
        const Vector3 velocity {
            velocity_x == nullptr ? 0.0 : velocity_x[index],
            velocity_y == nullptr ? 0.0 : velocity_y[index],
            velocity_z == nullptr ? 0.0 : velocity_z[index],
        };
        LorentzSample sample;
        static_cast<void>(process_sample(velocity, sample));
        signal_x[index] = sample.signal.x;
        signal_y[index] = sample.signal.y;
        signal_z[index] = sample.signal.z;
        signal_magnitude[index] = sample.signal_magnitude;
    }
}

} // namespace qmw
