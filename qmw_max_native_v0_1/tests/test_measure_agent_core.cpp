#include "qmw/measure.hpp"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <string_view>
#include <vector>

namespace {

int checks = 0;
int failures = 0;

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
void check_code(
    Function&& function,
    const qmw::MeasurementCode expected,
    const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const qmw::MeasurementError& error) {
        check(error.code() == expected, name);
    } catch (...) {
        check(false, name);
    }
}

std::vector<double> zeros(const std::size_t count)
{
    return std::vector<double>(count, 0.0);
}

qmw::MeasurementMetadata metadata(const char* basis = "computational_q0_lsb")
{
    return {
        basis,
        "declared-product-basis",
        "measurement-definition-fixture",
        "dimensionless",
        "measure-agent-test",
        "q0_lsb",
    };
}

qmw::MeasurementContext context(const long revision = 7, const char* basis = "computational_q0_lsb")
{
    return {
        revision,
        basis,
        "state-fixture",
        "dimensionless",
        "measure-agent-test-state",
    };
}

qmw::ProjectiveMeasurement z_measurement()
{
    return qmw::ProjectiveMeasurement::pauli_product(1, qmw::ProjectiveAxis::z, metadata());
}

} // namespace

int main()
{
    check(qmw::projective_axis_from_name("X") == qmw::ProjectiveAxis::x, "parse X basis");
    check(qmw::projective_axis_from_name("y") == qmw::ProjectiveAxis::y, "parse y basis");
    check(qmw::projective_axis_from_name("Z") == qmw::ProjectiveAxis::z, "parse Z basis");
    check(!qmw::projective_axis_from_name("XY").has_value(), "reject unknown basis");

    const auto plus = qmw::DensityState::from_split(
        2, {0.5, 0.5, 0.5, 0.5}, zeros(4));
    const auto plus_i = qmw::DensityState::from_split(
        2, {0.5, 0.0, 0.0, 0.5}, {0.0, -0.5, 0.5, 0.0});
    const auto zero = qmw::DensityState::from_split(
        2, {1.0, 0.0, 0.0, 0.0}, zeros(4));

    {
        const auto measurement = z_measurement();
        check(measurement.dimension() == 2, "Z measurement dimension");
        check(measurement.outcomes().size() == 2, "complete Z outcomes");
        check(measurement.outcomes()[0].label == "0", "outcome label zero");
        check(measurement.outcomes()[1].label == "1", "outcome label one");
        check(measurement.metadata().subsystem_order == "q0_lsb", "q0-LSB explicit");
        check_close(measurement.diagnostics().completeness_residual_fro, 0.0, 1.0e-14,
                    "projectors complete");
        check_close(measurement.diagnostics().maximum_pairwise_overlap_fro, 0.0, 1.0e-14,
                    "projectors orthogonal");
    }

    {
        qmw::MeasurementEngine engine(z_measurement(), 29);
        const auto distribution = engine.probabilities(plus, context());
        check(distribution.parent_revision == 7, "distribution retains parent revision");
        check_close(distribution.raw_probabilities[0], 0.5, 1.0e-14, "Z raw p0 exact");
        check_close(distribution.raw_probabilities[1], 0.5, 1.0e-14, "Z raw p1 exact");
        check_close(distribution.probabilities[0], 0.5, 1.0e-14, "Z normalized p0");
        check_close(distribution.raw_probability_sum, 1.0, 1.0e-14, "raw sum retained");
        check_close(distribution.normalization_denominator, 1.0, 1.0e-14,
                    "normalization denominator retained");
        check(distribution.probability_semantics == "exact_calculated_born_probability",
              "exact probability distinguished");
        check(distribution.estimate_semantics == "not_an_estimate", "estimate absence explicit");
        check(distribution.counts_semantics == "counts_not_available", "counts absence explicit");
        check(distribution.uncertainty_semantics.find("missing") != std::string::npos,
              "uncertainty absence explicit");

        const auto before = plus.values();
        const auto conditioned = engine.condition(plus, context(), 0, 41);
        check(engine.draw_index() == 0, "conditioning consumes no RNG draw");
        check(conditioned.selection == qmw::MeasurementSelection::specified_outcome,
              "conditioning selection named");
        check(conditioned.event_id == 1, "conditioning event id");
        check(conditioned.request_id == 41, "request id retained");
        check(conditioned.parent_revision == 7, "record parent revision retained");
        check(conditioned.outcome == 0 && conditioned.outcome_label == "0", "conditioned outcome retained");
        check_close(conditioned.probability, 0.5, 1.0e-14, "conditioned probability");
        check_close(conditioned.posterior.values[0].real(), 1.0, 1.0e-14, "posterior is |0><0|");
        check_close(conditioned.posterior.values[3].real(), 0.0, 1.0e-14, "posterior removes |1>");
        check(conditioned.posterior.parent_revision == 7, "candidate names parent revision");
        check(conditioned.posterior.provenance.find("not_committed") != std::string::npos,
              "candidate provenance denies commit");
        check(conditioned.state_installation == "caller_authority_only", "installation ownership explicit");
        check(!conditioned.authority_state_mutated, "measurement never claims state mutation");
        check(!conditioned.counts.has_value() && !conditioned.shots.has_value(),
              "calculation not mislabeled as counts");
        check(!conditioned.probability_standard_uncertainty.has_value(),
              "missing uncertainty represented as missing");
        check(plus.values() == before, "input density remains immutable");
    }

    {
        qmw::MeasurementEngine x_engine(qmw::ProjectiveMeasurement::pauli_product(
            1, qmw::ProjectiveAxis::x, metadata()), 9);
        const auto distribution = x_engine.probabilities(plus, context());
        check_close(distribution.probabilities[0], 1.0, 1.0e-13, "|+> has X outcome zero");
        check_close(distribution.probabilities[1], 0.0, 1.0e-13, "|+> excludes X outcome one");
        check_code(
            [&] { (void)x_engine.condition(plus, context(), 1); },
            qmw::MeasurementCode::zero_probability_outcome,
            "reject conditioning on zero-probability outcome");
    }

    {
        qmw::MeasurementEngine y_engine(qmw::ProjectiveMeasurement::pauli_product(
            1, qmw::ProjectiveAxis::y, metadata()), 9);
        const auto distribution = y_engine.probabilities(plus_i, context());
        check_close(distribution.probabilities[0], 1.0, 1.0e-13, "|+i> has Y outcome zero");
        check_close(distribution.probabilities[1], 0.0, 1.0e-13, "Y convention sign locked");
    }

    {
        // Basis index one means |q1 q0> = |01>; this locks q0-LSB.
        auto real = zeros(16);
        real[1 * 4 + 1] = 1.0;
        const auto state = qmw::DensityState::from_split(4, real, zeros(16));
        qmw::MeasurementEngine engine(qmw::ProjectiveMeasurement::pauli_product(
            2, qmw::ProjectiveAxis::z, metadata()), 3);
        const auto record = engine.condition(state, context(11), 1);
        check(record.outcome == 1, "two-qubit outcome index one");
        check(record.outcome_label == "01", "bit label is q1_q0");
        check_close(record.posterior.values[5].real(), 1.0, 1.0e-14,
                    "q0-LSB posterior matrix index retained");
    }

    {
        qmw::MeasurementEngine first(z_measurement(), 123456);
        qmw::MeasurementEngine second(z_measurement(), 123456);
        const auto conditioned = first.condition(plus, context(), 0);
        check(!conditioned.rng.used, "conditioned record marks RNG unused");
        check(conditioned.rng.draw_index_before == 0 && conditioned.rng.draw_index_after == 0,
              "conditioned RNG checkpoint unchanged");
        const auto first_sample = first.sample(plus, context(), 71);
        const auto second_sample = second.sample(plus, context(), 71);
        check(first_sample.outcome == second_sample.outcome, "same seed reproduces outcome");
        check_close(first_sample.rng.uniform_01, second_sample.rng.uniform_01, 0.0,
                    "same seed reproduces exact uniform");
        check_close(first_sample.rng.uniform_01, 0.22617122565625025, 0.0,
                    "SplitMix64 v1 first draw locked across platforms");
        check(first_sample.rng.algorithm == "splitmix64", "RNG algorithm recorded");
        check(first_sample.rng.version == "qmw-native-measure-v1", "RNG version recorded");
        check(first_sample.rng.seed == 123456, "RNG seed recorded");
        check(first_sample.rng.draw_index_before == 0 && first_sample.rng.draw_index_after == 1,
              "RNG draw interval recorded");
        check(first.draw_index() == 1, "one sample consumes exactly one draw");
        check(first_sample.event_id == 2, "conditioning and sampling have ordered event ids");
        check_code(
            [&] { (void)first.sample(plus, context(), -1); },
            qmw::MeasurementCode::invalid_request,
            "invalid sample request rejected before drawing");
        check(first.draw_index() == 1, "invalid sample request consumes no RNG draw");
    }

    {
        const std::vector<qmw::Complex> p0 {{1.0, 0.0}, {}, {}, {}};
        const std::vector<qmw::Complex> p1 {{}, {}, {}, {1.0, 0.0}};
        auto custom = qmw::ProjectiveMeasurement::from_projectors(
            2, {{10, "ground", p0}, {20, "excited", p1}}, metadata());
        qmw::MeasurementEngine engine(std::move(custom), 1);
        const auto record = engine.condition(zero, context(), 10);
        check(record.outcome == 10 && record.outcome_label == "ground",
              "declared projector ids and labels retained");

        check_code(
            [&] { (void)engine.condition(zero, context(), 99); },
            qmw::MeasurementCode::outcome_not_found,
            "reject undeclared outcome");
        check_code(
            [&] { (void)engine.condition(zero, context(), 10, -1); },
            qmw::MeasurementCode::invalid_request,
            "reject negative request id");
        check_code(
            [&] { (void)engine.probabilities(zero, context(-1)); },
            qmw::MeasurementCode::invalid_revision,
            "reject missing parent revision");
        check_code(
            [&] { (void)engine.probabilities(zero, context(7, "other-basis")); },
            qmw::MeasurementCode::basis_mismatch,
            "reject coordinate basis mismatch");
    }

    {
        const std::vector<qmw::Complex> p0 {{1.0, 0.0}, {}, {}, {}};
        const std::vector<qmw::Complex> p1 {{}, {}, {}, {1.0, 0.0}};
        auto nan = p0;
        nan[0] = {std::numeric_limits<double>::quiet_NaN(), 0.0};
        auto nonhermitian = p0;
        nonhermitian[1] = 1.0;
        auto half = p0;
        half[0] = 0.5;

        check_code(
            [&] { (void)qmw::ProjectiveMeasurement::from_projectors(
                2, {{0, "0", nan}, {1, "1", p1}}, metadata()); },
            qmw::MeasurementCode::non_finite,
            "reject non-finite projector");
        check_code(
            [&] { (void)qmw::ProjectiveMeasurement::from_projectors(
                2, {{0, "0", nonhermitian}, {1, "1", p1}}, metadata()); },
            qmw::MeasurementCode::non_hermitian_projector,
            "reject non-Hermitian projector");
        check_code(
            [&] { (void)qmw::ProjectiveMeasurement::from_projectors(
                2, {{0, "0", half}, {1, "1", p1}}, metadata()); },
            qmw::MeasurementCode::non_idempotent_projector,
            "reject non-idempotent effect");
        check_code(
            [&] { (void)qmw::ProjectiveMeasurement::from_projectors(
                2, {{0, "0", p0}, {1, "also-zero", p0}}, metadata()); },
            qmw::MeasurementCode::non_orthogonal_projectors,
            "reject overlapping projectors");
        check_code(
            [&] { (void)qmw::ProjectiveMeasurement::from_projectors(
                2, {{0, "0", p0}}, metadata()); },
            qmw::MeasurementCode::incomplete_projectors,
            "reject incomplete projector family");
        check_code(
            [&] { (void)qmw::ProjectiveMeasurement::from_projectors(
                2, {{0, "0", p0}, {0, "1", p1}}, metadata()); },
            qmw::MeasurementCode::duplicate_outcome,
            "reject duplicate outcome id");
        check_code(
            [&] { (void)qmw::ProjectiveMeasurement::from_projectors(
                2, {{0, "same", p0}, {1, "same", p1}}, metadata()); },
            qmw::MeasurementCode::duplicate_outcome,
            "reject duplicate outcome label");
        check_code(
            [&] { (void)qmw::ProjectiveMeasurement::from_projectors(
                2, {{0, "0", std::vector<qmw::Complex>(3)}, {1, "1", p1}}, metadata()); },
            qmw::MeasurementCode::wrong_element_count,
            "reject wrong projector size");
        auto bad_units = metadata();
        bad_units.units = "joule";
        check_code(
            [&] { (void)qmw::ProjectiveMeasurement::from_projectors(
                2, {{0, "0", p0}, {1, "1", p1}}, bad_units); },
            qmw::MeasurementCode::invalid_metadata,
            "reject dimensional projector units");
    }

    {
        const auto six_qubit = qmw::ProjectiveMeasurement::pauli_product(
            6, qmw::ProjectiveAxis::y, metadata());
        check(six_qubit.dimension() == 64 && six_qubit.outcomes().size() == 64,
              "declared maximum six-qubit product measurement validates");
        check(six_qubit.outcomes()[1].label == "000001", "six-qubit labels remain q5...q0");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.measure checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_MEASURE_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
