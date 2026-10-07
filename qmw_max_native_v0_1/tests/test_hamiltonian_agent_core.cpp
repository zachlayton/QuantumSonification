#include "qmw/hamiltonian.hpp"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string_view>
#include <vector>

namespace {

int failures = 0;
int checks = 0;

void check(const bool condition, const std::string_view name)
{
    ++checks;
    if (!condition) {
        std::cerr << "FAIL: " << name << '\n';
        ++failures;
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
void check_validation_code(
    Function&& function,
    const qmw::HamiltonianValidationCode expected,
    const std::string_view name)
{
    try {
        function();
        check(false, name);
    } catch (const qmw::HamiltonianValidationError& error) {
        check(error.code() == expected, name);
    } catch (...) {
        check(false, name);
    }
}

std::vector<double> zeros(const std::size_t count)
{
    return std::vector<double>(count, 0.0);
}

} // namespace

int main()
{
    {
        qmw::HamiltonianMetadata metadata {
            "joule",
            "computational_q0_lsb",
            "laboratory-controller",
            "calibration-run-17",
        };
        std::vector<double> real {2.0, 0.5, 0.5, -2.0};
        const auto hamiltonian = qmw::HamiltonianSnapshot::from_split(
            2, real, zeros(4), metadata);
        real[0] = 99.0;
        metadata.energy_unit = "mutated";

        check(hamiltonian.dimension() == 2, "dimension retained");
        check(hamiltonian.qubits() == 1, "qubit count derived exactly");
        check_close(hamiltonian.at(0, 0).real(), 2.0, 1.0e-14, "input matrix copied immutably");
        check(hamiltonian.metadata().energy_unit == "joule", "metadata copied immutably");
        check(hamiltonian.metadata().basis_id == "computational_q0_lsb", "basis identity retained");
        check(hamiltonian.metadata().source_id == "laboratory-controller", "source identity retained");
        check(hamiltonian.metadata().provenance == "calibration-run-17", "provenance retained");
        check_close(hamiltonian.diagnostics().trace.real(), 0.0, 1.0e-14, "trace real diagnostic");
        check_close(hamiltonian.diagnostics().trace.imag(), 0.0, 1.0e-14, "trace imaginary diagnostic");
        check_close(
            hamiltonian.diagnostics().frobenius_norm,
            std::sqrt(8.5),
            1.0e-14,
            "Frobenius norm diagnostic");
        check_close(
            hamiltonian.diagnostics().maximum_absolute_element,
            2.0,
            1.0e-14,
            "maximum element diagnostic");
        check_close(
            hamiltonian.diagnostics().hermiticity_residual_fro,
            0.0,
            1.0e-14,
            "Hermiticity residual diagnostic");
    }

    {
        // sigma_y: row-major [[0,-i],[i,0]].
        const auto hamiltonian = qmw::HamiltonianSnapshot::from_split(
            2,
            zeros(4),
            {0.0, -1.0, 1.0, 0.0});
        check_close(hamiltonian.at(0, 1).imag(), -1.0, 1.0e-14, "complex upper triangle retained");
        check_close(hamiltonian.at(1, 0).imag(), 1.0, 1.0e-14, "complex lower triangle retained");
        check_close(hamiltonian.diagnostics().frobenius_norm, std::sqrt(2.0), 1.0e-14, "complex norm");
    }

    {
        const auto zero = qmw::HamiltonianSnapshot::from_split(2, zeros(4), zeros(4));
        check_close(zero.diagnostics().relative_hermiticity_residual, 0.0, 0.0, "zero H relative residual");
    }

    check_validation_code(
        [] { qmw::HamiltonianSnapshot::from_split(3, zeros(9), zeros(9)); },
        qmw::HamiltonianValidationCode::invalid_dimension,
        "reject non-power-of-two dimension");

    check_validation_code(
        [] {
            qmw::HamiltonianValidationPolicy policy;
            policy.maximum_dimension = 2;
            qmw::HamiltonianSnapshot::from_split(4, zeros(16), zeros(16), {}, policy);
        },
        qmw::HamiltonianValidationCode::invalid_dimension,
        "reject dimension above configured limit");

    check_validation_code(
        [] { qmw::HamiltonianSnapshot::from_split(2, zeros(3), zeros(3)); },
        qmw::HamiltonianValidationCode::wrong_element_count,
        "reject wrong element count");

    check_validation_code(
        [] {
            auto real = zeros(4);
            real[0] = std::numeric_limits<double>::infinity();
            qmw::HamiltonianSnapshot::from_split(2, real, zeros(4));
        },
        qmw::HamiltonianValidationCode::non_finite,
        "reject non-finite matrix");

    check_validation_code(
        [] {
            qmw::HamiltonianSnapshot::from_split(
                2,
                {1.0, 0.25, 0.0, -1.0},
                zeros(4));
        },
        qmw::HamiltonianValidationCode::non_hermitian,
        "reject non-Hermitian matrix");

    check_validation_code(
        [] {
            // The absolute defect is tiny, but it is large relative to the
            // Hamiltonian's declared energy scale and must still be rejected.
            qmw::HamiltonianSnapshot::from_split(
                2,
                {1.0e-24, 1.0e-24, 0.0, -1.0e-24},
                zeros(4));
        },
        qmw::HamiltonianValidationCode::non_hermitian,
        "relative Hermiticity check has no unit-sized floor");

    check_validation_code(
        [] {
            qmw::HamiltonianMetadata metadata;
            metadata.basis_id = "   ";
            qmw::HamiltonianSnapshot::from_split(2, zeros(4), zeros(4), metadata);
        },
        qmw::HamiltonianValidationCode::invalid_metadata,
        "reject blank basis metadata");

    check_validation_code(
        [] {
            qmw::HamiltonianValidationPolicy policy;
            policy.relative_hermiticity_tolerance = 0.0;
            qmw::HamiltonianSnapshot::from_split(2, zeros(4), zeros(4), {}, policy);
        },
        qmw::HamiltonianValidationCode::invalid_policy,
        "reject invalid validation policy");

    {
        const auto snapshot = qmw::HamiltonianSnapshot::from_split(2, zeros(4), zeros(4));
        try {
            static_cast<void>(snapshot.at(2, 0));
            check(false, "out-of-range matrix access rejected");
        } catch (const std::out_of_range&) {
            check(true, "out-of-range matrix access rejected");
        } catch (...) {
            check(false, "out-of-range matrix access rejected");
        }
    }

    {
        qmw::HamiltonianMetadata metadata {
            "model_energy",
            "computational_q0_lsb",
            "native-test",
            "deterministic-fixture",
        };
        qmw::RevisionedHamiltonianStore store(2, metadata);
        const std::vector<double> first_real {1.0, 0.0, 0.0, -1.0};
        const std::vector<double> second_real {0.0, 1.0, 1.0, 0.0};
        const std::vector<double> invalid_real {1.0, 0.5, 0.0, -1.0};
        const auto zero = zeros(4);

        const auto first = store.stage(qmw::HamiltonianPart::real, 7, first_real);
        check(first.status == qmw::HamiltonianStageStatus::staged, "real component stages");
        check(store.active() == nullptr, "partial Hamiltonian remains invisible");
        const auto committed = store.stage(qmw::HamiltonianPart::imag, 7, zero);
        check(committed.status == qmw::HamiltonianStageStatus::accepted, "matching components commit");
        check(store.active_revision() == 7, "Hamiltonian revision advances atomically");
        check_close(store.active()->at(1, 1).real(), -1.0, 1.0e-14, "active matrix exact");
        check(store.active()->metadata().provenance == "deterministic-fixture", "store carries provenance");

        const auto partial_imag = store.stage(qmw::HamiltonianPart::imag, 8, zero);
        check(partial_imag.status == qmw::HamiltonianStageStatus::staged, "next imaginary component stages");
        const auto mismatched_real = store.stage(qmw::HamiltonianPart::real, 9, second_real);
        check(mismatched_real.status == qmw::HamiltonianStageStatus::staged, "mismatched revisions remain partial");
        check(store.active_revision() == 7, "mismatch preserves active Hamiltonian");
        const auto newest_pair = store.stage(qmw::HamiltonianPart::imag, 9, zero);
        check(newest_pair.status == qmw::HamiltonianStageStatus::accepted, "newest matching pair commits");
        check(store.active_revision() == 9, "active revision skips abandoned partial");
        check_close(store.active()->at(0, 1).real(), 1.0, 1.0e-14, "new active matrix exact");

        const auto stale = store.stage(qmw::HamiltonianPart::real, 8, first_real);
        check(stale.status == qmw::HamiltonianStageStatus::rejected, "stale revision rejected");
        check(stale.detail == "stale_revision", "stale revision detail stable");

        check(
            store.stage(qmw::HamiltonianPart::real, 10, invalid_real).status
                == qmw::HamiltonianStageStatus::staged,
            "invalid matrix remains hidden until complete");
        const auto rejected = store.stage(qmw::HamiltonianPart::imag, 10, zero);
        check(rejected.status == qmw::HamiltonianStageStatus::rejected, "invalid pair rejected");
        check(rejected.detail == "non_hermitian", "validation detail crosses staging boundary");
        check(store.active_revision() == 9, "rejection preserves active revision");
        check_close(store.active()->at(0, 1).real(), 1.0, 1.0e-14, "rejection preserves active values");

        const auto malformed = store.stage(qmw::HamiltonianPart::real, 11, zeros(3));
        check(malformed.status == qmw::HamiltonianStageStatus::rejected, "malformed component rejected");
        check(malformed.detail == "wrong_element_count", "malformed component detail stable");

        check(
            store.stage(qmw::HamiltonianPart::real, 12, first_real).status
                == qmw::HamiltonianStageStatus::staged,
            "candidate stages before clear");
        store.clear_candidate();
        check(
            store.stage(qmw::HamiltonianPart::imag, 12, zero).status
                == qmw::HamiltonianStageStatus::staged,
            "clear removes uncommitted component");
        check(store.active_revision() == 9, "clear preserves active snapshot");
    }

    if (failures != 0) {
        std::cerr << failures << " qmw.hamiltonian checks failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "QMW_HAMILTONIAN_AGENT_TESTS_OK (" << checks << " checks)\n";
    return EXIT_SUCCESS;
}
