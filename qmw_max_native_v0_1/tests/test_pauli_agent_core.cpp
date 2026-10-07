#include "qmw/pauli.hpp"

#include <cmath>
#include <complex>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

int checks = 0;

void expect(const bool condition, const char* message)
{
    ++checks;
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}

void expect_close(const std::complex<double> actual, const std::complex<double> expected, const char* message)
{
    expect(std::abs(actual - expected) < 1.0e-12, message);
}

template <typename Function>
void expect_code(Function&& function, const qmw::PauliValidationCode code, const char* message)
{
    try {
        function();
    } catch (const qmw::PauliValidationError& error) {
        expect(error.code() == code, message);
        return;
    }
    expect(false, message);
}

void test_single_qubit_exact_matrices()
{
    const auto x = qmw::PauliSnapshot::product(2, {{qmw::PauliAxis::x, 0}});
    expect(x.label() == "X0", "X label");
    expect_close(x.at(0, 0), 0.0, "X00");
    expect_close(x.at(0, 1), 1.0, "X01");
    expect_close(x.at(1, 0), 1.0, "X10");
    expect_close(x.at(1, 1), 0.0, "X11");

    const auto y = qmw::PauliSnapshot::product(2, {{qmw::PauliAxis::y, 0}});
    expect_close(y.at(0, 1), {0.0, -1.0}, "Y01=-i");
    expect_close(y.at(1, 0), {0.0, 1.0}, "Y10=i");

    const auto z = qmw::PauliSnapshot::product(2, {{qmw::PauliAxis::z, 0}});
    expect_close(z.at(0, 0), 1.0, "Z00");
    expect_close(z.at(1, 1), -1.0, "Z11");
    expect_close(z.diagnostics().trace, 0.0, "Z trace");
    expect(std::abs(z.diagnostics().frobenius_norm - std::sqrt(2.0)) < 1.0e-12, "Z Frobenius norm");
    expect(z.diagnostics().hermiticity_residual_fro == 0.0, "Z Hermitian exactly");
    expect(z.diagnostics().unitarity_residual_fro == 0.0, "Z unitary exactly");
}

void test_q0_lsb_and_canonical_products()
{
    const auto x0 = qmw::PauliSnapshot::product(4, {{qmw::PauliAxis::x, 0}});
    expect_close(x0.at(1, 0), 1.0, "X0 maps 00 to 01");
    expect_close(x0.at(0, 1), 1.0, "X0 maps 01 to 00");
    expect_close(x0.at(3, 2), 1.0, "X0 maps 10 to 11");
    expect_close(x0.at(2, 3), 1.0, "X0 maps 11 to 10");

    const auto z1 = qmw::PauliSnapshot::product(4, {{qmw::PauliAxis::z, 1}});
    expect_close(z1.at(0, 0), 1.0, "Z1 00");
    expect_close(z1.at(1, 1), 1.0, "Z1 01");
    expect_close(z1.at(2, 2), -1.0, "Z1 10");
    expect_close(z1.at(3, 3), -1.0, "Z1 11");

    const auto product = qmw::PauliSnapshot::product(
        4,
        {{qmw::PauliAxis::z, 1}, {qmw::PauliAxis::x, 0}});
    expect(product.label() == "X0_Z1", "factors canonicalized by ascending q0-LSB target");
    expect(product.factors()[0].qubit == 0, "canonical factor 0");
    expect(product.factors()[1].qubit == 1, "canonical factor 1");
    expect_close(product.at(1, 0), 1.0, "X0Z1 maps 00 positively");
    expect_close(product.at(3, 2), -1.0, "X0Z1 maps 10 negatively");
    expect(product.diagnostics().hermiticity_residual_fro == 0.0, "product Hermitian exactly");
    expect(product.diagnostics().unitarity_residual_fro == 0.0, "product unitary exactly");
}

void test_identity_and_validation()
{
    const auto identity = qmw::PauliSnapshot::identity(4);
    expect(identity.label() == "I", "identity label");
    expect(identity.factors().empty(), "identity has no explicit factors");
    for (std::size_t row = 0; row < 4; ++row) {
        for (std::size_t column = 0; column < 4; ++column) {
            expect_close(identity.at(row, column), row == column ? 1.0 : 0.0, "identity entry");
        }
    }
    expect_close(identity.diagnostics().trace, 4.0, "identity trace");

    expect_code([] { (void)qmw::PauliSnapshot::identity(3); },
                qmw::PauliValidationCode::invalid_dimension, "reject non-power-of-two dimension");
    expect_code([] { (void)qmw::PauliSnapshot::product(2, {}); },
                qmw::PauliValidationCode::empty_product, "reject empty product");
    expect_code([] { (void)qmw::PauliSnapshot::product(2, {{qmw::PauliAxis::x, 1}}); },
                qmw::PauliValidationCode::invalid_qubit, "reject invalid target");
    expect_code([] {
        (void)qmw::PauliSnapshot::product(
            4, {{qmw::PauliAxis::x, 0}, {qmw::PauliAxis::z, 0}});
    }, qmw::PauliValidationCode::duplicate_qubit, "reject duplicate target");
    expect_code([] {
        qmw::PauliMetadata metadata;
        metadata.source_id = "   ";
        (void)qmw::PauliSnapshot::identity(2, metadata);
    }, qmw::PauliValidationCode::invalid_metadata, "reject blank metadata");
}

void test_revisioned_atomic_installation()
{
    qmw::RevisionedPauliStore store(4, {"computational_q0_lsb", "test", "fixture", "dimensionless"});
    expect(store.active() == nullptr, "store initially empty");
    const auto accepted = store.install_product(4, {{qmw::PauliAxis::y, 0}});
    expect(accepted.status == qmw::PauliInstallStatus::accepted, "first product accepted");
    expect(store.active_revision() == 4, "active revision installed");
    expect(store.active()->label() == "Y0", "active snapshot retained");

    const auto stale = store.install_identity(4);
    expect(stale.status == qmw::PauliInstallStatus::rejected, "equal revision rejected");
    expect(stale.detail == "stale_revision", "stale detail");
    expect(store.active_revision() == 4 && store.active()->label() == "Y0", "stale preserves active");

    const auto invalid = store.install_product(
        5, {{qmw::PauliAxis::x, 0}, {qmw::PauliAxis::z, 0}});
    expect(invalid.status == qmw::PauliInstallStatus::rejected, "invalid product rejected");
    expect(invalid.detail == "duplicate_qubit", "duplicate detail");
    expect(store.active_revision() == 4 && store.active()->label() == "Y0", "invalid preserves active");

    const auto identity = store.install_identity(6);
    expect(identity.status == qmw::PauliInstallStatus::accepted, "new identity accepted");
    expect(store.active_revision() == 6 && store.active()->label() == "I", "identity replaces active atomically");

    const auto negative = store.install_product(-1, {{qmw::PauliAxis::x, 0}});
    expect(negative.status == qmw::PauliInstallStatus::rejected, "negative revision rejected");
    expect(negative.detail == "invalid_revision", "negative revision detail");
    expect(store.active_revision() == 6, "negative revision preserves active");
}

} // namespace

int main()
{
    test_single_qubit_exact_matrices();
    test_q0_lsb_and_canonical_products();
    test_identity_and_validation();
    test_revisioned_atomic_installation();
    std::cout << "QMW_PAULI_AGENT_TESTS_OK (" << checks << " checks)\n";
}
