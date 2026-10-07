#pragma once

#include <cstddef>

namespace qmw {

struct ResonatorParameters {
    double sample_rate_hz {48000.0};
    double frequency_hz {440.0};
    // Amplitude T60: the unforced state envelope falls to 0.001 after this time.
    double decay_seconds {1.0};
    // Linear output gain. A unit impulse produces this value at n = 0.
    double gain {1.0};
};

// A real-output resonant body implemented as one damped complex pole pair.
//
//   u[n] = x[n] + r R(theta) u[n-1]
//   y[n] = gain * u_real[n]
//   theta = 2 pi frequency_hz / sample_rate_hz
//   r = 10^(-3 / (decay_seconds * sample_rate_hz))
//
// Therefore a unit impulse produces
//   y[n] = gain * r^n * cos(n theta), n >= 0,
// and the state-amplitude envelope reaches -60 dB at decay_seconds. The pole
// radius is always strictly below one. This class owns no quantum state and
// performs no density-to-sound mapping: x[n] is its sole excitation.
class Resonator final {
public:
    static constexpr double minimum_sample_rate_hz = 8000.0;
    static constexpr double maximum_sample_rate_hz = 768000.0;
    static constexpr double minimum_frequency_hz = 1.0;
    static constexpr double maximum_frequency_fraction = 0.49;
    static constexpr double minimum_decay_seconds = 0.001;
    static constexpr double maximum_decay_seconds = 60.0;
    static constexpr double minimum_gain = 0.0;
    static constexpr double maximum_gain = 4.0;

    explicit Resonator(ResonatorParameters parameters = {});

    void set_parameters(ResonatorParameters parameters);
    void set_sample_rate_hz(double sample_rate_hz);
    void set_frequency_hz(double frequency_hz);
    void set_decay_seconds(double decay_seconds);
    void set_gain(double gain);

    [[nodiscard]] const ResonatorParameters& parameters() const noexcept { return parameters_; }
    [[nodiscard]] double pole_radius() const noexcept { return radius_; }
    [[nodiscard]] double rotation_cosine() const noexcept { return cosine_; }
    [[nodiscard]] double rotation_sine() const noexcept { return sine_; }

    [[nodiscard]] double process_sample(double excitation) noexcept;
    void process_block(const double* excitation, double* output, std::size_t frame_count) noexcept;
    void reset() noexcept;

private:
    void update_coefficients() noexcept;

    ResonatorParameters parameters_ {};
    double radius_ {};
    double cosine_ {1.0};
    double sine_ {};
    double state_real_ {};
    double state_imag_ {};
};

} // namespace qmw
