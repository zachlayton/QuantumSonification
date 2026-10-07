#pragma once

#include <cstddef>
#include <cstdint>
#include <string_view>

namespace qmw {

struct Vector3 {
    double x {};
    double y {};
    double z {};
};

struct LorentzModelControls {
    // Effective-model charge, electric field, and magnetic field. Their units
    // and source identity belong to the host adapter's mandatory declaration;
    // this core never infers SI units.
    double charge {1.0};
    Vector3 electric {};
    Vector3 magnetic {};
};

struct LorentzSignalMapping {
    // Positive magnitude of model force corresponding to full-scale input to
    // the radial limiter. This is an authored mapping calibration, not physics.
    double force_reference {1.0};
    // Maximum Euclidean magnitude of the mapped xyz signal vector.
    double headroom {0.5};
};

struct LorentzSample {
    // Exact accepted result of F_model = q_model (E_model + v_model x B_model).
    Vector3 model_force {};
    double model_force_magnitude {};

    // Audio-safe authored projection:
    // signal = headroom * model_force / max(force_reference, |model_force|).
    Vector3 signal {};
    double signal_magnitude {};
};

enum class LorentzControlCode {
    accepted,
    invalid_charge,
    invalid_electric,
    invalid_magnetic,
    invalid_reference,
    invalid_headroom,
};

[[nodiscard]] std::string_view lorentz_control_code_name(
    LorentzControlCode code) noexcept;

// A memoryless, deterministic effective Lorentz-model evaluator. It owns no
// density matrix, event source, oscillator, field extraction, or physical-unit
// calibration. Controls are copied as complete scalar/vector records; a host
// adapter is responsible for installing those records only at signal-vector
// boundaries.
//
// For every admitted finite velocity v:
//
//   F_model = q_model (E_model + v_model x B_model)
//   y       = h F_model / max(R, |F_model|)
//
// where R > 0 is the declared mapping reference and 0 <= h <= 1 is signal
// headroom. Consequently |y| <= h. The second equation is explicitly a
// sonification mapping and is not presented as Lorentz physics. Non-finite or
// overflowing sample calculations reject the complete xyz frame to exact zero.
class EffectiveLorentzModel final {
public:
    static constexpr double minimum_headroom = 0.0;
    static constexpr double maximum_headroom = 1.0;
    static constexpr double default_headroom = 0.5; // -6.0206 dBFS vector magnitude

    explicit EffectiveLorentzModel(
        LorentzModelControls controls = {},
        LorentzSignalMapping mapping = {});

    [[nodiscard]] LorentzControlCode set_model(
        const LorentzModelControls& controls) noexcept;
    [[nodiscard]] LorentzControlCode set_charge(double charge) noexcept;
    [[nodiscard]] LorentzControlCode set_electric(Vector3 electric) noexcept;
    [[nodiscard]] LorentzControlCode set_magnetic(Vector3 magnetic) noexcept;
    [[nodiscard]] LorentzControlCode set_mapping(
        const LorentzSignalMapping& mapping) noexcept;

    // Restores q=1 and zero E/B, preserving the explicitly authored mapping.
    // There is no signal history to clear.
    void reset_model() noexcept;
    void set_muted(bool muted) noexcept { muted_ = muted; }

    [[nodiscard]] const LorentzModelControls& controls() const noexcept
    {
        return controls_;
    }
    [[nodiscard]] const LorentzSignalMapping& mapping() const noexcept
    {
        return mapping_;
    }
    [[nodiscard]] bool muted() const noexcept { return muted_; }
    [[nodiscard]] std::uint64_t rejected_frame_count() const noexcept
    {
        return rejected_frame_count_;
    }

    [[nodiscard]] bool process_sample(
        Vector3 velocity,
        LorentzSample& output) noexcept;
    void process_block(
        const double* velocity_x,
        const double* velocity_y,
        const double* velocity_z,
        double* signal_x,
        double* signal_y,
        double* signal_z,
        double* signal_magnitude,
        std::size_t frame_count) noexcept;

private:
    [[nodiscard]] static bool finite_vector(Vector3 value) noexcept;
    [[nodiscard]] static LorentzControlCode validate_model(
        const LorentzModelControls& controls) noexcept;
    [[nodiscard]] static LorentzControlCode validate_mapping(
        const LorentzSignalMapping& mapping) noexcept;

    LorentzModelControls controls_ {};
    LorentzSignalMapping mapping_ {};
    std::uint64_t rejected_frame_count_ {};
    bool muted_ {false};
};

} // namespace qmw
