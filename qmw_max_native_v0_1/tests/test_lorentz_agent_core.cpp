#include "qmw/lorentz.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string_view>

namespace {

int failures = 0;
int checks = 0;

void check(const bool condition, const std::string_view name)
{
    ++checks;
    if (!condition) {
        ++failures;
        std::cerr << "FAIL: " << name << '\n';
    }
}

void check_close(
    const double actual,
    const double expected,
    const double tolerance,
    const std::string_view name)
{
    check(std::abs(actual - expected) <= tolerance, name);
}

template <typename Function>
void check_invalid_argument(Function&& function, const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const std::invalid_argument&) {
        check(true, name);
    } catch (...) {
        check(false, name);
    }
}

} // namespace

int main()
{
    using qmw::EffectiveLorentzModel;
    using qmw::LorentzControlCode;
    using qmw::LorentzModelControls;
    using qmw::LorentzSample;
    using qmw::LorentzSignalMapping;
    using qmw::Vector3;

    check(qmw::lorentz_control_code_name(LorentzControlCode::accepted) == "accepted", "accepted status name");
    check(qmw::lorentz_control_code_name(LorentzControlCode::invalid_charge) == "invalid_charge", "charge status name");
    check(qmw::lorentz_control_code_name(LorentzControlCode::invalid_electric) == "invalid_electric", "electric status name");
    check(qmw::lorentz_control_code_name(LorentzControlCode::invalid_magnetic) == "invalid_magnetic", "magnetic status name");
    check(qmw::lorentz_control_code_name(LorentzControlCode::invalid_reference) == "invalid_reference", "reference status name");
    check(qmw::lorentz_control_code_name(LorentzControlCode::invalid_headroom) == "invalid_headroom", "headroom status name");

    {
        EffectiveLorentzModel model;
        LorentzSample sample;
        check(model.process_sample({}, sample), "finite zero velocity admitted");
        check(sample.model_force.x == 0.0 && sample.model_force.y == 0.0
                && sample.model_force.z == 0.0 && sample.model_force_magnitude == 0.0,
            "default zero field yields exact zero model force");
        check(sample.signal.x == 0.0 && sample.signal.y == 0.0
                && sample.signal.z == 0.0 && sample.signal_magnitude == 0.0,
            "default zero field yields exact signal silence");
    }

    {
        const LorentzModelControls controls {
            2.0,
            {1.0, 2.0, 3.0},
            {0.0, 0.0, 4.0},
        };
        EffectiveLorentzModel model(controls, {100.0, 0.5});
        LorentzSample sample;
        check(model.process_sample({5.0, 6.0, 7.0}, sample), "declared equation sample admitted");
        check(sample.model_force.x == 50.0, "force x follows q(E+v cross B)");
        check(sample.model_force.y == -36.0, "force y follows q(E+v cross B)");
        check(sample.model_force.z == 6.0, "force z follows q(E+v cross B)");
        const double magnitude = std::sqrt(3832.0);
        check_close(sample.model_force_magnitude, magnitude, 2.0e-14, "model force magnitude is Euclidean norm");
        check_close(sample.signal.x, 0.25, 2.0e-16, "sub-reference x mapping is linear");
        check_close(sample.signal.y, -0.18, 2.0e-16, "sub-reference y mapping is linear");
        check_close(sample.signal.z, 0.03, 2.0e-16, "sub-reference z mapping is linear");
        check_close(sample.signal_magnitude, 0.5 * magnitude / 100.0, 2.0e-16, "sub-reference magnitude mapping is declared separately");
    }

    {
        EffectiveLorentzModel model({1.0, {0.0, 0.0, 0.0}, {0.0, 0.0, 1.0}}, {1.0, 0.5});
        LorentzSample sample;
        check(model.process_sample({3.0, 4.0, 0.0}, sample), "radially limited sample admitted");
        check(sample.model_force.x == 4.0 && sample.model_force.y == -3.0
                && sample.model_force.z == 0.0,
            "right-handed cross product orientation is explicit");
        check(sample.model_force_magnitude == 5.0, "unmapped magnitude remains five model-force units");
        check_close(sample.signal.x, 0.4, 1.0e-16, "radial limiter preserves x direction");
        check_close(sample.signal.y, -0.3, 1.0e-16, "radial limiter preserves y direction");
        check(sample.signal.z == 0.0, "radial limiter preserves exact zero z");
        check(sample.signal_magnitude == 0.5, "radial limiter reaches exact declared headroom");
    }

    {
        // Analytic vector retained from the authoritative Python milestone.
        EffectiveLorentzModel model({0.5, {}, {0.0, 0.0, 3.0}}, {100.0, 1.0});
        LorentzSample sample;
        check(model.process_sample({2.0, -1.0, 0.0}, sample),
            "authoritative constant-B vector admitted");
        check(sample.model_force.x == -1.5 && sample.model_force.y == -3.0,
            "authoritative constant-B cross-product result is preserved");
        check(sample.model_force.z == 0.0,
            "authoritative planar constant-B result has exact zero z");
    }

    {
        EffectiveLorentzModel model({-2.0, {1.0, -2.0, 0.5}, {}}, {100.0, 1.0});
        LorentzSample sample;
        check(model.process_sample({99.0, -22.0, 4.0}, sample), "negative effective charge admitted");
        check(sample.model_force.x == -2.0 && sample.model_force.y == 4.0
                && sample.model_force.z == -1.0,
            "charge polarity reverses every force component");
        check(model.set_charge(0.0) == LorentzControlCode::accepted, "zero charge admitted");
        check(model.process_sample({99.0, -22.0, 4.0}, sample), "zero charge sample admitted");
        check(sample.model_force_magnitude == 0.0 && sample.signal_magnitude == 0.0,
            "zero charge yields exact zero regardless of velocity and field");
        const double maximum = std::numeric_limits<double>::max();
        check(model.set_magnetic({maximum, maximum, maximum}) == LorentzControlCode::accepted,
            "finite extreme magnetic field admitted at zero charge");
        check(model.process_sample({maximum, -maximum, maximum}, sample),
            "zero charge short-circuits otherwise overflowing products");
        check(sample.model_force_magnitude == 0.0 && sample.signal_magnitude == 0.0,
            "zero charge with extreme finite inputs remains exact zero");
    }

    {
        EffectiveLorentzModel model({2.0, {1.0, 2.0, 3.0}, {4.0, 5.0, 6.0}}, {8.0, 0.25});
        const auto nan = std::numeric_limits<double>::quiet_NaN();
        const auto infinity = std::numeric_limits<double>::infinity();
        const auto before = model.controls();
        check(model.set_model({7.0, {nan, 0.0, 0.0}, {8.0, 9.0, 10.0}})
                == LorentzControlCode::invalid_electric,
            "nonfinite electric component rejects complete model tuple");
        check(model.controls().charge == before.charge
                && model.controls().electric.x == before.electric.x
                && model.controls().magnetic.x == before.magnetic.x,
            "rejected model tuple leaves every prior member intact");
        check(model.set_charge(infinity) == LorentzControlCode::invalid_charge,
            "infinite charge rejected");
        check(model.set_electric({0.0, infinity, 0.0}) == LorentzControlCode::invalid_electric,
            "infinite electric field rejected");
        check(model.set_magnetic({0.0, 0.0, nan}) == LorentzControlCode::invalid_magnetic,
            "NaN magnetic field rejected");
        const auto mapping_before = model.mapping();
        check(model.set_mapping({0.0, 0.5}) == LorentzControlCode::invalid_reference,
            "zero reference rejected");
        check(model.set_mapping({-1.0, 0.5}) == LorentzControlCode::invalid_reference,
            "negative reference rejected");
        check(model.set_mapping({1.0, 1.01}) == LorentzControlCode::invalid_headroom,
            "headroom above one rejected");
        check(model.set_mapping({1.0, nan}) == LorentzControlCode::invalid_headroom,
            "NaN headroom rejected");
        check(model.mapping().force_reference == mapping_before.force_reference
                && model.mapping().headroom == mapping_before.headroom,
            "rejected mapping tuple leaves both prior members intact");
    }

    check_invalid_argument(
        [] { EffectiveLorentzModel model({std::numeric_limits<double>::quiet_NaN(), {}, {}}); },
        "constructor rejects nonfinite charge");
    check_invalid_argument(
        [] { EffectiveLorentzModel model({}, {0.0, 0.5}); },
        "constructor rejects zero mapping reference");
    check_invalid_argument(
        [] { EffectiveLorentzModel model({}, {1.0, -0.1}); },
        "constructor rejects negative headroom");

    {
        EffectiveLorentzModel model({1.0, {1.0, 0.0, 0.0}, {}}, {1.0, 0.5});
        LorentzSample sample;
        const auto nan = std::numeric_limits<double>::quiet_NaN();
        check(!model.process_sample({nan, 0.0, 0.0}, sample), "NaN velocity rejects complete sample frame");
        check(sample.model_force_magnitude == 0.0 && sample.signal_magnitude == 0.0
                && sample.signal.x == 0.0 && sample.signal.y == 0.0 && sample.signal.z == 0.0,
            "rejected velocity produces exact complete-frame silence");
        check(model.rejected_frame_count() == 1, "rejected velocity is counted");
        check(model.process_sample({}, sample), "finite sample following rejection is admitted");
        check(sample.signal.x == 0.5, "rejection does not contaminate following sample");

        const double maximum = std::numeric_limits<double>::max();
        check(model.set_model({maximum, {}, {maximum, maximum, maximum}})
                == LorentzControlCode::accepted,
            "finite extreme controls are admitted as model inputs");
        check(!model.process_sample({maximum, maximum, -maximum}, sample),
            "overflowing effective-force calculation rejects complete frame");
        check(sample.signal_magnitude == 0.0, "overflow rejection is exact silence");
        check(model.rejected_frame_count() == 2, "overflow rejection is counted");
    }

    {
        EffectiveLorentzModel model({1.0, {2.0, 0.0, 0.0}, {}}, {2.0, 0.5});
        LorentzSample sample;
        model.set_muted(true);
        check(model.process_sample({}, sample), "finite muted sample admitted");
        check(sample.model_force_magnitude == 0.0 && sample.signal_magnitude == 0.0,
            "mute emits exact silence without exposing model force");
        model.set_muted(false);
        check(model.process_sample({}, sample) && sample.signal.x == 0.5,
            "unmute resumes memoryless model immediately");
        check(model.set_mapping({2.0, 0.0}) == LorentzControlCode::accepted,
            "zero headroom is an admitted explicit mapping");
        check(model.process_sample({}, sample), "zero-headroom sample admitted");
        check(sample.model_force.x == 2.0 && sample.signal_magnitude == 0.0,
            "zero headroom silences mapping while retaining model force");
        check(model.set_model({3.0, {1.0, 2.0, 3.0}, {4.0, 5.0, 6.0}})
                == LorentzControlCode::accepted,
            "nondefault model set before reset");
        model.set_muted(true);
        model.reset_model();
        check(model.controls().charge == 1.0
                && model.controls().electric.x == 0.0
                && model.controls().magnetic.z == 0.0,
            "reset restores neutral model controls");
        check(!model.muted(), "reset removes mute");
        check(model.mapping().force_reference == 2.0 && model.mapping().headroom == 0.0,
            "reset preserves authored signal mapping");
    }

    {
        constexpr std::size_t frames = 5;
        EffectiveLorentzModel model({1.0, {0.0, 0.0, 0.0}, {0.0, 0.0, 2.0}}, {10.0, 1.0});
        const std::array<double, frames> vx {0.0, 1.0, 2.0, 3.0, 4.0};
        const std::array<double, frames> vy {0.0, -1.0, -2.0, -3.0, -4.0};
        const std::array<double, frames> vz {};
        std::array<double, frames> x {};
        std::array<double, frames> y {};
        std::array<double, frames> z {};
        std::array<double, frames> magnitude {};
        model.process_block(vx.data(), vy.data(), vz.data(), x.data(), y.data(), z.data(), magnitude.data(), frames);
        for (std::size_t index = 0; index < frames; ++index) {
            const double raw_component = -2.0 * static_cast<double>(index);
            const double raw_magnitude = std::sqrt(2.0) * std::abs(raw_component);
            const double expected = raw_component / std::max(10.0, raw_magnitude);
            check_close(x[index], expected, 1.0e-15,
                "block x follows velocity cross magnetic field");
            check_close(y[index], expected, 1.0e-15,
                "block y follows velocity cross magnetic field");
            check(z[index] == 0.0, "block z remains exact zero");
            check(magnitude[index] <= 1.0, "block vector magnitude respects headroom");
        }

        x.fill(99.0);
        y.fill(99.0);
        z.fill(99.0);
        magnitude.fill(99.0);
        EffectiveLorentzModel electric_only({1.0, {1.0, 0.0, 0.0}, {}}, {1.0, 0.5});
        electric_only.process_block(nullptr, nullptr, nullptr, x.data(), y.data(), z.data(), magnitude.data(), frames);
        check(std::all_of(x.begin(), x.end(), [](const double value) { return value == 0.5; }),
            "null velocity inputs mean exact zero velocity, not missing electric force");
        check(std::all_of(y.begin(), y.end(), [](const double value) { return value == 0.0; }),
            "electric-only null-input y is exact zero");
    }

    {
        EffectiveLorentzModel model({0.7, {0.4, -0.3, 0.2}, {0.2, 0.1, -0.4}}, {0.75, 0.37});
        bool all_finite = true;
        bool all_bounded = true;
        for (int index = 0; index < 100000; ++index) {
            const double t = static_cast<double>(index);
            LorentzSample sample;
            const bool accepted = model.process_sample(
                {1000.0 * std::sin(t * 0.013), 800.0 * std::cos(t * 0.017), t * 0.001},
                sample);
            all_finite = all_finite && accepted
                && std::isfinite(sample.signal.x)
                && std::isfinite(sample.signal.y)
                && std::isfinite(sample.signal.z)
                && std::isfinite(sample.signal_magnitude);
            all_bounded = all_bounded && sample.signal_magnitude <= 0.37
                && std::hypot(sample.signal.x, sample.signal.y, sample.signal.z)
                    <= 0.37 + 3.0e-16;
        }
        check(all_finite, "long deterministic drive remains finite");
        check(all_bounded, "long deterministic drive stays within vector headroom");
        check(model.rejected_frame_count() == 0, "finite long drive has no hidden rejection");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.lorentz checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_LORENTZ_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
