#pragma once

#include "qmw/observe.hpp"

#include <complex>
#include <cstddef>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace qmw {

using PauliComplex = std::complex<double>;

enum class PauliValidationCode {
    invalid_dimension,
    invalid_revision,
    stale_revision,
    invalid_axis,
    invalid_qubit,
    duplicate_qubit,
    empty_product,
    invalid_metadata,
};

[[nodiscard]] std::string_view pauli_validation_code_name(
    PauliValidationCode code) noexcept;

class PauliValidationError final : public std::runtime_error {
public:
    PauliValidationError(PauliValidationCode code, const char* message);

    [[nodiscard]] PauliValidationCode code() const noexcept { return code_; }

private:
    PauliValidationCode code_;
};

struct PauliFactor {
    PauliAxis axis {PauliAxis::z};
    std::size_t qubit {};
};

struct PauliMetadata {
    std::string basis_id {"computational_q0_lsb"};
    std::string source_id {"qmw.pauli"};
    std::string provenance {"explicit-Pauli-product"};
    std::string operator_unit {"dimensionless"};
};

struct PauliDiagnostics {
    PauliComplex trace {};
    double frobenius_norm {};
    double hermiticity_residual_fro {};
    double unitarity_residual_fro {};
};

class PauliSnapshot final {
public:
    static PauliSnapshot identity(
        std::size_t dimension,
        PauliMetadata metadata = {});

    static PauliSnapshot product(
        std::size_t dimension,
        std::vector<PauliFactor> factors,
        PauliMetadata metadata = {});

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t qubits() const noexcept { return qubits_; }
    [[nodiscard]] const std::vector<PauliComplex>& values() const noexcept { return values_; }
    [[nodiscard]] const std::vector<PauliFactor>& factors() const noexcept { return factors_; }
    [[nodiscard]] const std::string& label() const noexcept { return label_; }
    [[nodiscard]] const PauliMetadata& metadata() const noexcept { return metadata_; }
    [[nodiscard]] const PauliDiagnostics& diagnostics() const noexcept { return diagnostics_; }
    [[nodiscard]] const PauliComplex& at(std::size_t row, std::size_t column) const;

private:
    PauliSnapshot(
        std::size_t dimension,
        std::size_t qubits,
        std::vector<PauliComplex> values,
        std::vector<PauliFactor> factors,
        std::string label,
        PauliMetadata metadata,
        PauliDiagnostics diagnostics);

    std::size_t dimension_ {};
    std::size_t qubits_ {};
    std::vector<PauliComplex> values_;
    std::vector<PauliFactor> factors_;
    std::string label_;
    PauliMetadata metadata_;
    PauliDiagnostics diagnostics_;
};

enum class PauliInstallStatus { accepted, rejected };

struct PauliInstallResult {
    PauliInstallStatus status {PauliInstallStatus::rejected};
    long revision {-1};
    std::string detail;
    std::string message;
};

class RevisionedPauliStore final {
public:
    explicit RevisionedPauliStore(
        std::size_t dimension,
        PauliMetadata metadata = {});

    [[nodiscard]] PauliInstallResult install_identity(long revision);
    [[nodiscard]] PauliInstallResult install_product(
        long revision,
        std::vector<PauliFactor> factors);

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t qubits() const noexcept { return qubits_; }
    [[nodiscard]] long active_revision() const noexcept { return active_revision_; }
    [[nodiscard]] const PauliSnapshot* active() const noexcept { return active_.get(); }
    [[nodiscard]] const PauliMetadata& metadata() const noexcept { return metadata_; }

private:
    [[nodiscard]] PauliInstallResult install(long revision, PauliSnapshot snapshot);

    std::size_t dimension_ {};
    std::size_t qubits_ {};
    PauliMetadata metadata_;
    long active_revision_ {-1};
    std::unique_ptr<PauliSnapshot> active_;
};

} // namespace qmw
