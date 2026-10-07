#pragma once

#include <complex>
#include <cstddef>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace qmw {

using HamiltonianComplex = std::complex<double>;

enum class HamiltonianValidationCode {
    invalid_dimension,
    wrong_element_count,
    non_finite,
    non_hermitian,
    invalid_metadata,
    invalid_policy,
};

[[nodiscard]] std::string_view hamiltonian_validation_code_name(
    HamiltonianValidationCode code) noexcept;

class HamiltonianValidationError final : public std::runtime_error {
public:
    HamiltonianValidationError(HamiltonianValidationCode code, const char* message);

    [[nodiscard]] HamiltonianValidationCode code() const noexcept { return code_; }

private:
    HamiltonianValidationCode code_;
};

struct HamiltonianValidationPolicy {
    // Relative Frobenius tolerance, intentionally without a unit-sized floor.
    // This keeps small SI-valued Hamiltonians subject to the same test as
    // model-energy matrices.
    double relative_hermiticity_tolerance {1.0e-10};
    std::size_t maximum_dimension {64};
};

struct HamiltonianMetadata {
    std::string energy_unit {"model_energy"};
    std::string basis_id {"computational_q0_lsb"};
    std::string source_id {"unspecified-source"};
    std::string provenance {"unspecified-provenance"};
};

struct HamiltonianDiagnostics {
    HamiltonianComplex trace {};
    double frobenius_norm {};
    double maximum_absolute_element {};
    double hermiticity_residual_fro {};
    double relative_hermiticity_residual {};
};

class HamiltonianSnapshot final {
public:
    static HamiltonianSnapshot from_split(
        std::size_t dimension,
        const std::vector<double>& real,
        const std::vector<double>& imag,
        HamiltonianMetadata metadata = {},
        HamiltonianValidationPolicy policy = {});

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t qubits() const noexcept { return qubits_; }
    [[nodiscard]] const std::vector<HamiltonianComplex>& values() const noexcept { return values_; }
    [[nodiscard]] const HamiltonianMetadata& metadata() const noexcept { return metadata_; }
    [[nodiscard]] const HamiltonianDiagnostics& diagnostics() const noexcept { return diagnostics_; }
    [[nodiscard]] const HamiltonianComplex& at(std::size_t row, std::size_t column) const;

private:
    HamiltonianSnapshot(
        std::size_t dimension,
        std::size_t qubits,
        std::vector<HamiltonianComplex> values,
        HamiltonianMetadata metadata,
        HamiltonianDiagnostics diagnostics);

    std::size_t dimension_ {};
    std::size_t qubits_ {};
    std::vector<HamiltonianComplex> values_;
    HamiltonianMetadata metadata_;
    HamiltonianDiagnostics diagnostics_;
};

enum class HamiltonianPart { real, imag };
enum class HamiltonianStageStatus { staged, accepted, rejected };

struct HamiltonianStageResult {
    HamiltonianStageStatus status {HamiltonianStageStatus::rejected};
    long revision {-1};
    std::string detail;
    std::string message;
};

class RevisionedHamiltonianStore final {
public:
    RevisionedHamiltonianStore(
        std::size_t dimension,
        HamiltonianMetadata metadata = {},
        HamiltonianValidationPolicy policy = {});

    [[nodiscard]] HamiltonianStageResult stage(
        HamiltonianPart part,
        long revision,
        std::vector<double> values);
    void clear_candidate() noexcept;

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t qubits() const noexcept { return qubits_; }
    [[nodiscard]] std::size_t element_count() const noexcept { return element_count_; }
    [[nodiscard]] long active_revision() const noexcept { return active_revision_; }
    [[nodiscard]] const HamiltonianSnapshot* active() const noexcept { return active_.get(); }
    [[nodiscard]] const HamiltonianMetadata& metadata() const noexcept { return metadata_; }

private:
    struct CandidatePart {
        std::optional<long> revision;
        std::vector<double> values;

        void clear() noexcept;
    };

    std::size_t dimension_ {};
    std::size_t qubits_ {};
    std::size_t element_count_ {};
    HamiltonianMetadata metadata_;
    HamiltonianValidationPolicy policy_;
    long active_revision_ {-1};
    std::unique_ptr<HamiltonianSnapshot> active_;
    CandidatePart real_;
    CandidatePart imag_;
};

} // namespace qmw
