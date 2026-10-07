#include "qmw/uncertainty.hpp"

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
    const std::string_view name,
    const double tolerance = 1.0e-13)
{
    check(std::abs(actual - expected) <= tolerance, name);
}

template <typename Function>
void check_code(
    Function&& function,
    const qmw::UncertaintyValidationCode expected,
    const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const qmw::UncertaintyValidationError& error) {
        check(error.code() == expected, name);
    } catch (...) {
        check(false, name);
    }
}

std::vector<double> zeros(const std::size_t count)
{
    return std::vector<double>(count, 0.0);
}

qmw::ObservableMetadata observable_metadata(
    const long revision,
    const char* basis,
    const char* unit,
    const char* source)
{
    return {revision, basis, unit, source};
}

qmw::StateAnalysisMetadata state_metadata(const long revision, const char* basis)
{
    return {revision, basis, "test-rho-source"};
}

qmw::HermitianObservable pauli_x(const long revision = 4)
{
    return qmw::HermitianObservable::from_split(
        2, {0.0, 1.0, 1.0, 0.0}, zeros(4),
        observable_metadata(revision, "computational_q0_lsb", "spin", "fixture-X"));
}

qmw::HermitianObservable pauli_y(const long revision = 4)
{
    return qmw::HermitianObservable::from_split(
        2, zeros(4), {0.0, -1.0, 1.0, 0.0},
        observable_metadata(revision, "computational_q0_lsb", "spin", "fixture-Y"));
}

qmw::HermitianObservable pauli_z(const long revision = 4)
{
    return qmw::HermitianObservable::from_split(
        2, {1.0, 0.0, 0.0, -1.0}, zeros(4),
        observable_metadata(revision, "computational_q0_lsb", "spin", "fixture-Z"));
}

} // namespace

int main()
{
    const auto zero_state = qmw::DensityState::from_split(
        2, {1.0, 0.0, 0.0, 0.0}, zeros(4));
    const auto mixed_state = qmw::DensityState::from_split(
        2, {0.5, 0.0, 0.0, 0.5}, zeros(4));
    const auto metadata = state_metadata(4, "computational_q0_lsb");

    {
        auto real = std::vector<double> {0.0, 1.0, 1.0, 0.0};
        auto source_metadata = observable_metadata(
            4, "computational_q0_lsb", "hbar/2", "calibration-17");
        const auto observable = qmw::HermitianObservable::from_split(
            2, real, zeros(4), source_metadata);
        real[1] = 99.0;
        source_metadata.unit = "mutated";
        check_close(observable.at(0, 1).real(), 1.0, "observable values copied immutably");
        check(observable.metadata().unit == "hbar/2", "observable metadata copied immutably");
        check(observable.metadata().source_id == "calibration-17", "observable source retained");
        check_close(observable.hermiticity_residual_fro(), 0.0, "Hermiticity diagnostic retained");
    }

    {
        const auto x = qmw::observable_moments(zero_state, metadata, pauli_x());
        check_close(x.expectation, 0.0, "<X> for |0>");
        check_close(x.variance, 1.0, "Var X for |0>");
        check_close(x.standard_deviation, 1.0, "Delta X for |0>");
        check(x.revision == 4, "moments preserve matched revision");
        check(x.basis_id == "computational_q0_lsb", "moments preserve basis");
        check(x.state_source_id == "test-rho-source", "moments preserve state source");
        check(x.state_unit == "dimensionless", "moments declare density-matrix unit");
        check(x.observable_source_id == "fixture-X", "moments preserve observable source");
        check(x.observable_unit == "spin", "moments preserve unit");

        const auto z = qmw::observable_moments(zero_state, metadata, pauli_z());
        check_close(z.expectation, 1.0, "<Z> for |0>");
        check_close(z.variance, 0.0, "Var Z for eigenstate");
        check_close(z.standard_deviation, 0.0, "Delta Z for eigenstate");

        const auto mixed_x = qmw::observable_moments(mixed_state, metadata, pauli_x());
        check_close(mixed_x.expectation, 0.0, "<X> for maximally mixed state");
        check_close(mixed_x.variance, 1.0, "Var X for maximally mixed state");
    }

    {
        const auto result = qmw::robertson_schrodinger(
            zero_state, metadata, pauli_x(), pauli_y());
        check_close(result.a.variance, 1.0, "Robertson X variance");
        check_close(result.b.variance, 1.0, "Robertson Y variance");
        check_close(result.covariance, 0.0, "Robertson covariance");
        check_close(result.commutator_component, 1.0, "<[X,Y]>/(2i) sign");
        check_close(result.lower_bound, 1.0, "Robertson-Schrodinger lower bound");
        check_close(result.variance_product, 1.0, "Robertson variance product");
        check_close(result.slack, 0.0, "Robertson equality for |0>");
        check(result.observable_a_source_id == "fixture-X", "Robertson A source metadata");
        check(result.observable_b_source_id == "fixture-Y", "Robertson B source metadata");
    }

    {
        const double inverse_sqrt_two = 1.0 / std::sqrt(2.0);
        const auto diagonal_state = qmw::DensityState::from_split(
            2,
            {0.5 * (1.0 + inverse_sqrt_two), 0.5 * inverse_sqrt_two,
             0.5 * inverse_sqrt_two, 0.5 * (1.0 - inverse_sqrt_two)},
            zeros(4));
        const auto result = qmw::robertson_schrodinger(
            diagonal_state, metadata, pauli_x(), pauli_z());
        check_close(result.a.expectation, inverse_sqrt_two, "tilted state <X>");
        check_close(result.b.expectation, inverse_sqrt_two, "tilted state <Z>");
        check_close(result.covariance, -0.5, "nonzero symmetrized covariance");
        check_close(result.commutator_component, 0.0, "zero commutator expectation");
        check_close(result.lower_bound, 0.25, "covariance contributes to lower bound");
        check_close(result.variance_product, 0.25, "tilted pure state saturates bound");
    }

    check_code(
        [] {
            qmw::HermitianObservable::from_split(
                2, zeros(3), zeros(3),
                observable_metadata(1, "basis", "unit", "source"));
        },
        qmw::UncertaintyValidationCode::wrong_element_count,
        "reject wrong observable element count");
    check_code(
        [] {
            qmw::HermitianObservable::from_split(
                2, {0.0, 1.0e-24, 0.0, 0.0}, zeros(4),
                observable_metadata(1, "basis", "joule", "source"));
        },
        qmw::UncertaintyValidationCode::non_hermitian,
        "relative Hermiticity validation has no unit-sized floor");
    check_code(
        [] {
            auto values = zeros(4);
            values[0] = std::numeric_limits<double>::infinity();
            qmw::HermitianObservable::from_split(
                2, values, zeros(4),
                observable_metadata(1, "basis", "unit", "source"));
        },
        qmw::UncertaintyValidationCode::non_finite,
        "reject non-finite observable");
    check_code(
        [] {
            auto values = zeros(4);
            values[0] = std::numeric_limits<double>::max();
            qmw::HermitianObservable::from_split(
                2, values, zeros(4),
                observable_metadata(1, "basis", "unit", "source"));
        },
        qmw::UncertaintyValidationCode::non_finite,
        "reject finite elements whose aggregate scale overflows");
    check_code(
        [] {
            qmw::HermitianObservable::from_split(
                2, zeros(4), zeros(4),
                observable_metadata(1, "basis", " ", "source"));
        },
        qmw::UncertaintyValidationCode::invalid_metadata,
        "reject blank observable unit");
    check_code(
        [&] {
            (void)qmw::observable_moments(
                zero_state, state_metadata(5, "computational_q0_lsb"), pauli_x(4));
        },
        qmw::UncertaintyValidationCode::revision_mismatch,
        "reject mismatched state and observable revisions");
    check_code(
        [&] {
            const auto other_basis = qmw::HermitianObservable::from_split(
                2, {0.0, 1.0, 1.0, 0.0}, zeros(4),
                observable_metadata(4, "energy_basis", "spin", "fixture"));
            (void)qmw::observable_moments(zero_state, metadata, other_basis);
        },
        qmw::UncertaintyValidationCode::basis_mismatch,
        "reject mismatched state and observable bases");
    check_code(
        [&] {
            const auto dimension_four = qmw::HermitianObservable::from_split(
                4, zeros(16), zeros(16),
                observable_metadata(4, "computational_q0_lsb", "spin", "fixture"));
            (void)qmw::observable_moments(zero_state, metadata, dimension_four);
        },
        qmw::UncertaintyValidationCode::dimension_mismatch,
        "reject mismatched state and observable dimensions");

    {
        qmw::MandelstamTammMetadata mt_metadata {
            4, "computational_q0_lsb", "spin", "joule", "dynamics-fixture"};
        const auto result = qmw::mandelstam_tamm_characteristic_time(
            1.0, 2.0, 1.0, 1.0, mt_metadata);
        check(result.characteristic_time.has_value(), "nonzero rate yields finite characteristic time");
        check_close(*result.characteristic_time, 0.5, "tau_A = DeltaA / rate");
        check_close(*result.energy_time_product, 0.5, "DeltaE tau_A product");
        check_close(result.lower_bound, 0.5, "Mandelstam-Tamm hbar/2 bound");
        check(result.satisfies_bound, "saturating characteristic time satisfies bound");
        check(result.metadata.energy_unit == "joule", "Mandelstam-Tamm energy unit retained");

        const auto violation = qmw::mandelstam_tamm_characteristic_time(
            1.0, 4.0, 1.0, 1.0, mt_metadata);
        check(!violation.satisfies_bound, "inconsistent supplied rate is reported, not hidden");

        const auto stationary = qmw::mandelstam_tamm_characteristic_time(
            0.0, 0.0, 0.0, 1.0, mt_metadata);
        check(!stationary.characteristic_time.has_value(), "zero rate does not invent finite time");
        check(!stationary.energy_time_product.has_value(), "stationary case has no finite product");
        check(stationary.satisfies_bound, "stationary case is not labeled a violation");

        const auto orthogonal = qmw::mandelstam_tamm_orthogonalization_bound(
            2.0, 1.0, mt_metadata);
        check_close(*orthogonal.minimum_time, std::acos(-1.0) / 4.0, "orthogonalization lower bound");
        const auto no_finite_orthogonal = qmw::mandelstam_tamm_orthogonalization_bound(
            0.0, 1.0, mt_metadata);
        check(!no_finite_orthogonal.minimum_time.has_value(), "zero DeltaE has no finite orthogonalization bound");
    }

    check_code(
        [] {
            (void)qmw::mandelstam_tamm_characteristic_time(
                1.0, -1.0, 1.0, 1.0,
                {1, "basis", "unit", "joule", "source"});
        },
        qmw::UncertaintyValidationCode::invalid_mandelstam_tamm_input,
        "reject negative expectation rate");
    check_code(
        [] {
            (void)qmw::mandelstam_tamm_orthogonalization_bound(
                1.0, 0.0,
                {1, "basis", "unit", "joule", "source"});
        },
        qmw::UncertaintyValidationCode::invalid_mandelstam_tamm_input,
        "reject nonpositive hbar");

    if (failures != 0) {
        std::cerr << failures << " qmw.uncertainty checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_UNCERTAINTY_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
