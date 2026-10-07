#pragma once

#include "qmw/hamiltonian.hpp"
#include "qmw/state.hpp"

#include <complex>
#include <cstddef>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace qmw {

enum class SpectrumCode {
    invalid_policy,
    invalid_revision,
    revision_mismatch,
    dimension_mismatch,
    basis_mismatch,
    eigensolver_nonconvergence,
    invalid_density_spectrum,
    non_finite_result,
};

[[nodiscard]] std::string_view spectrum_code_name(SpectrumCode code) noexcept;

class SpectrumError final : public std::runtime_error {
public:
    SpectrumError(SpectrumCode code, std::string message);
    [[nodiscard]] SpectrumCode code() const noexcept { return code_; }

private:
    SpectrumCode code_;
};

struct SpectrumPolicy {
    double relative_eigensolver_tolerance {1.0e-12};
    double density_positivity_tolerance {1.0e-10};
    // Absolute, expressed in the corresponding eigenvalue unit. This mirrors
    // quantum_spectrum.py and is intentionally exposed rather than inferred.
    double degeneracy_tolerance {1.0e-8};
    std::size_t maximum_sweeps {128};
    std::size_t maximum_dimension {64};
};

struct DegenerateGroup {
    std::size_t first {};
    std::size_t last {};
};

struct HermitianEigensystem {
    // Ascending eigenvalues. Eigenvectors are row-major with modes in columns.
    std::vector<double> eigenvalues;
    std::vector<Complex> eigenvectors;
    std::vector<DegenerateGroup> near_degenerate_groups;
    std::size_t sweeps {};
    double off_diagonal_frobenius {};
    double relative_residual_frobenius {};
    bool mode_labels_stable {true};
};

struct SpectrumProvenance {
    long state_revision {-1};
    long hamiltonian_revision {-1};
    std::string density_unit {"dimensionless"};
    std::string energy_unit;
    std::string basis_id;
    std::string hamiltonian_source_id;
    std::string hamiltonian_provenance;
    std::string ordering {"ascending_eigenvalue_stable_index"};
    std::string phase_convention {"largest_component_real_nonnegative"};
};

class QuantumSpectrumFrame final {
public:
    QuantumSpectrumFrame(
        std::size_t dimension,
        HermitianEigensystem density,
        HermitianEigensystem energy,
        std::vector<Complex> rho_in_energy_basis,
        std::vector<double> energy_populations,
        std::vector<double> basis_overlap,
        std::vector<double> density_gaps,
        std::vector<double> energy_gaps,
        double purity,
        double entropy_nats,
        double participation_rank,
        double commutator_norm,
        SpectrumPolicy policy,
        SpectrumProvenance provenance);

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] const HermitianEigensystem& density() const noexcept { return density_; }
    [[nodiscard]] const HermitianEigensystem& energy() const noexcept { return energy_; }
    [[nodiscard]] const std::vector<Complex>& rho_in_energy_basis() const noexcept { return rho_in_energy_basis_; }
    [[nodiscard]] const std::vector<double>& energy_populations() const noexcept { return energy_populations_; }
    [[nodiscard]] const std::vector<double>& basis_overlap() const noexcept { return basis_overlap_; }
    [[nodiscard]] const std::vector<double>& density_gaps() const noexcept { return density_gaps_; }
    [[nodiscard]] const std::vector<double>& energy_gaps() const noexcept { return energy_gaps_; }
    [[nodiscard]] double purity() const noexcept { return purity_; }
    [[nodiscard]] double entropy_nats() const noexcept { return entropy_nats_; }
    [[nodiscard]] double participation_rank() const noexcept { return participation_rank_; }
    [[nodiscard]] double commutator_norm() const noexcept { return commutator_norm_; }
    [[nodiscard]] const SpectrumPolicy& policy() const noexcept { return policy_; }
    [[nodiscard]] const SpectrumProvenance& provenance() const noexcept { return provenance_; }

private:
    std::size_t dimension_ {};
    HermitianEigensystem density_;
    HermitianEigensystem energy_;
    std::vector<Complex> rho_in_energy_basis_;
    std::vector<double> energy_populations_;
    std::vector<double> basis_overlap_;
    std::vector<double> density_gaps_;
    std::vector<double> energy_gaps_;
    double purity_ {};
    double entropy_nats_ {};
    double participation_rank_ {};
    double commutator_norm_ {};
    SpectrumPolicy policy_;
    SpectrumProvenance provenance_;
};

// Pure read-only analysis. Neither input is evolved, measured, reordered, or
// replaced. rho_in_energy_basis is computed from the original admitted rho.
[[nodiscard]] QuantumSpectrumFrame analyze_quantum_spectrum(
    const DensityState& state,
    long state_revision,
    const HamiltonianSnapshot& hamiltonian,
    long hamiltonian_revision,
    SpectrumPolicy policy = {});

} // namespace qmw
