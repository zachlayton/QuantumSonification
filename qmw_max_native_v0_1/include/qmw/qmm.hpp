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

using QmmComplex = std::complex<double>;

enum class QmmCode {
    invalid_policy,
    invalid_dimension,
    wrong_element_count,
    non_finite,
    non_hermitian,
    trace_not_one,
    not_positive_semidefinite,
    invalid_metadata,
    invalid_hbar,
    invalid_revision,
    stale_revision,
    incomplete_transaction,
    partial_pair_incomplete,
    revision_mismatch,
};

[[nodiscard]] std::string_view qmm_code_name(QmmCode code) noexcept;

class QmmError final : public std::runtime_error {
public:
    QmmError(QmmCode code, std::string message);

    [[nodiscard]] QmmCode code() const noexcept { return code_; }

private:
    QmmCode code_;
};

struct QmmMetadata {
    // hbar is numerically expressed in energy_unit * time_unit. No conversion
    // or relation between these symbols is inferred by qmw.qmm.
    std::string energy_unit {"model_energy"};
    std::string time_unit {"model_time"};
    std::string operator_unit {"model_operator"};
    std::string basis_id {"computational_q0_lsb"};
    std::string source_id {"unspecified-source"};
    std::string provenance {"unspecified-provenance"};
};

struct QmmPolicy {
    double relative_hermiticity_tolerance {1.0e-10};
    double density_hermiticity_tolerance {1.0e-10};
    double density_trace_tolerance {1.0e-10};
    double density_positivity_tolerance {1.0e-10};
    std::size_t maximum_dimension {64};
};

struct QmmMatrixSplit {
    std::vector<double> real;
    std::vector<double> imag;
};

struct QmmDiagnostics {
    double hamiltonian_hermiticity_residual_fro {};
    double observable_hermiticity_residual_fro {};
    double partial_hermiticity_residual_fro {};
    double commutator_frobenius_norm {};
    double commutator_antihermiticity_residual_fro {};
    double derivative_hermiticity_residual_fro {};
    QmmComplex density_trace {};
    double density_minimum_ldlt_pivot {};
    double expectation_imaginary_residual {};
};

class QmmMatrix final {
public:
    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] const std::vector<QmmComplex>& values() const noexcept { return values_; }
    [[nodiscard]] const QmmComplex& at(std::size_t row, std::size_t column) const;

private:
    friend class QmmSnapshot;
    QmmMatrix(std::size_t dimension, std::vector<QmmComplex> values);

    std::size_t dimension_ {};
    std::vector<QmmComplex> values_;
};

// Immutable evaluation of the Heisenberg equation of motion
//   dA_H/dt = (i/hbar)[H_H, A_H] + (partial A/partial t)_H.
// This class neither evolves rho nor postulates a time operator.
class QmmSnapshot final {
public:
    static QmmSnapshot evaluate(
        long revision,
        std::size_t dimension,
        QmmMatrixSplit hamiltonian,
        QmmMatrixSplit density,
        QmmMatrixSplit observable,
        std::optional<QmmMatrixSplit> explicit_partial,
        double hbar,
        QmmMetadata metadata = {},
        QmmPolicy policy = {});

    [[nodiscard]] long revision() const noexcept { return revision_; }
    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t qubits() const noexcept { return qubits_; }
    [[nodiscard]] double hbar() const noexcept { return hbar_; }
    [[nodiscard]] const QmmMetadata& metadata() const noexcept { return metadata_; }
    [[nodiscard]] const std::string& hbar_unit() const noexcept { return hbar_unit_; }
    [[nodiscard]] const std::string& derivative_unit() const noexcept { return derivative_unit_; }
    [[nodiscard]] bool has_explicit_partial() const noexcept { return partial_.has_value(); }

    [[nodiscard]] const QmmMatrix& hamiltonian() const noexcept { return hamiltonian_; }
    [[nodiscard]] const QmmMatrix& density() const noexcept { return density_; }
    [[nodiscard]] const QmmMatrix& observable() const noexcept { return observable_; }
    [[nodiscard]] const std::optional<QmmMatrix>& partial() const noexcept { return partial_; }
    [[nodiscard]] const QmmMatrix& commutator() const noexcept { return commutator_; }
    [[nodiscard]] const QmmMatrix& derivative() const noexcept { return derivative_; }
    [[nodiscard]] QmmComplex expectation_derivative() const noexcept
    {
        return expectation_derivative_;
    }
    [[nodiscard]] const QmmDiagnostics& diagnostics() const noexcept { return diagnostics_; }

private:
    QmmSnapshot(
        long revision,
        std::size_t dimension,
        std::size_t qubits,
        double hbar,
        QmmMetadata metadata,
        std::string hbar_unit,
        std::string derivative_unit,
        QmmMatrix hamiltonian,
        QmmMatrix density,
        QmmMatrix observable,
        std::optional<QmmMatrix> partial,
        QmmMatrix commutator,
        QmmMatrix derivative,
        QmmComplex expectation_derivative,
        QmmDiagnostics diagnostics);

    long revision_ {-1};
    std::size_t dimension_ {};
    std::size_t qubits_ {};
    double hbar_ {1.0};
    QmmMetadata metadata_;
    std::string hbar_unit_;
    std::string derivative_unit_;
    QmmMatrix hamiltonian_;
    QmmMatrix density_;
    QmmMatrix observable_;
    std::optional<QmmMatrix> partial_;
    QmmMatrix commutator_;
    QmmMatrix derivative_;
    QmmComplex expectation_derivative_ {};
    QmmDiagnostics diagnostics_;
};

enum class QmmPart {
    hamiltonian_real,
    hamiltonian_imag,
    density_real,
    density_imag,
    observable_real,
    observable_imag,
    partial_real,
    partial_imag,
};

enum class QmmStageStatus { staged, accepted, rejected };

struct QmmStageResult {
    QmmStageStatus status {QmmStageStatus::rejected};
    long revision {-1};
    std::string detail;
    std::string message;
};

// All matrix components are staged invisibly. An explicit commit(revision)
// atomically replaces the active immutable snapshot only when the six required
// components match that revision. The partial pair is optional, but may never
// be half-present. Failed transactions preserve the preceding active snapshot.
class RevisionedQmmStore final {
public:
    RevisionedQmmStore(
        std::size_t dimension,
        double hbar,
        QmmMetadata metadata = {},
        QmmPolicy policy = {});

    [[nodiscard]] QmmStageResult stage(QmmPart part, long revision, std::vector<double> values);
    [[nodiscard]] QmmStageResult commit(long revision);
    void clear_candidate() noexcept;

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t element_count() const noexcept { return element_count_; }
    [[nodiscard]] long active_revision() const noexcept { return active_revision_; }
    [[nodiscard]] const QmmSnapshot* active() const noexcept { return active_.get(); }

private:
    struct CandidatePart {
        std::optional<long> revision;
        std::vector<double> values;

        void clear() noexcept;
    };

    [[nodiscard]] CandidatePart& candidate(QmmPart part) noexcept;
    [[nodiscard]] const CandidatePart& candidate(QmmPart part) const noexcept;

    std::size_t dimension_ {};
    std::size_t element_count_ {};
    double hbar_ {1.0};
    QmmMetadata metadata_;
    QmmPolicy policy_;
    long active_revision_ {-1};
    std::unique_ptr<QmmSnapshot> active_;
    CandidatePart hamiltonian_real_;
    CandidatePart hamiltonian_imag_;
    CandidatePart density_real_;
    CandidatePart density_imag_;
    CandidatePart observable_real_;
    CandidatePart observable_imag_;
    CandidatePart partial_real_;
    CandidatePart partial_imag_;
};

} // namespace qmw
