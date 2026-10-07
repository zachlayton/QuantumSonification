#pragma once

#include "qmw/state.hpp"

#include <complex>
#include <cstddef>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace qmw {

enum class UncertaintyValidationCode {
    invalid_dimension,
    wrong_element_count,
    non_finite,
    non_hermitian,
    invalid_metadata,
    invalid_policy,
    dimension_mismatch,
    basis_mismatch,
    revision_mismatch,
    numerical_inconsistency,
    invalid_mandelstam_tamm_input,
};

[[nodiscard]] std::string_view uncertainty_validation_code_name(
    UncertaintyValidationCode code) noexcept;

class UncertaintyValidationError final : public std::runtime_error {
public:
    UncertaintyValidationError(UncertaintyValidationCode code, const char* message);

    [[nodiscard]] UncertaintyValidationCode code() const noexcept { return code_; }

private:
    UncertaintyValidationCode code_;
};

struct UncertaintyValidationPolicy {
    double relative_hermiticity_tolerance {1.0e-10};
    double reality_tolerance {1.0e-10};
    double nonnegative_tolerance {1.0e-10};
    std::size_t maximum_dimension {64};
};

struct StateAnalysisMetadata {
    long revision {-1};
    std::string basis_id;
    std::string source_id;
    std::string unit {"dimensionless"};
};

struct ObservableMetadata {
    long revision {-1};
    std::string basis_id;
    std::string unit;
    std::string source_id;
};

// Immutable validated observable. The matrix is copied on construction and is
// never written through an analysis path.
class HermitianObservable final {
public:
    static HermitianObservable from_split(
        std::size_t dimension,
        const std::vector<double>& real,
        const std::vector<double>& imag,
        ObservableMetadata metadata,
        UncertaintyValidationPolicy policy = {});

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] const std::vector<Complex>& values() const noexcept { return values_; }
    [[nodiscard]] const ObservableMetadata& metadata() const noexcept { return metadata_; }
    [[nodiscard]] double hermiticity_residual_fro() const noexcept { return hermiticity_residual_fro_; }
    [[nodiscard]] const Complex& at(std::size_t row, std::size_t column) const;

private:
    HermitianObservable(
        std::size_t dimension,
        std::vector<Complex> values,
        ObservableMetadata metadata,
        double hermiticity_residual_fro);

    std::size_t dimension_ {};
    std::vector<Complex> values_;
    ObservableMetadata metadata_;
    double hermiticity_residual_fro_ {};
};

struct ObservableMoments {
    long revision {-1};
    std::string basis_id;
    std::string state_source_id;
    std::string state_unit;
    std::string observable_source_id;
    std::string observable_unit;
    double expectation {};
    double variance {};
    double standard_deviation {};
};

struct RobertsonSchrodingerResult {
    long revision {-1};
    std::string basis_id;
    std::string state_source_id;
    std::string state_unit;
    std::string observable_a_source_id;
    std::string observable_b_source_id;
    std::string observable_a_unit;
    std::string observable_b_unit;
    ObservableMoments a;
    ObservableMoments b;
    // Re <{Delta A, Delta B}> / 2.
    double covariance {};
    // Real value of <[A,B]> / (2 i).
    double commutator_component {};
    // covariance^2 + commutator_component^2.
    double lower_bound {};
    double variance_product {};
    double slack {};
};

[[nodiscard]] ObservableMoments observable_moments(
    const DensityState& state,
    const StateAnalysisMetadata& state_metadata,
    const HermitianObservable& observable,
    UncertaintyValidationPolicy policy = {});

[[nodiscard]] RobertsonSchrodingerResult robertson_schrodinger(
    const DensityState& state,
    const StateAnalysisMetadata& state_metadata,
    const HermitianObservable& observable_a,
    const HermitianObservable& observable_b,
    UncertaintyValidationPolicy policy = {});

struct MandelstamTammMetadata {
    long revision {-1};
    std::string basis_id;
    std::string observable_unit;
    std::string energy_unit;
    std::string source_id;
};

// For an observable A with nonzero rate, tau_A = Delta A / |d<A>/dt| and
// Delta E * tau_A >= hbar/2. This is a characteristic-time statement, not a
// variance of a universal time operator. A zero rate yields no finite tau_A.
struct MandelstamTammCharacteristicTime {
    MandelstamTammMetadata metadata;
    double delta_observable {};
    double absolute_expectation_rate {};
    double delta_energy {};
    double hbar {};
    std::optional<double> characteristic_time;
    std::optional<double> energy_time_product;
    double lower_bound {};
    bool satisfies_bound {};
};

[[nodiscard]] MandelstamTammCharacteristicTime mandelstam_tamm_characteristic_time(
    double delta_observable,
    double absolute_expectation_rate,
    double delta_energy,
    double hbar,
    MandelstamTammMetadata metadata);

// Minimum orthogonalization time pi*hbar/(2 Delta E), also without introducing
// a time observable. Delta E == 0 has no finite orthogonalization bound.
struct MandelstamTammOrthogonalizationBound {
    MandelstamTammMetadata metadata;
    double delta_energy {};
    double hbar {};
    std::optional<double> minimum_time;
};

[[nodiscard]] MandelstamTammOrthogonalizationBound mandelstam_tamm_orthogonalization_bound(
    double delta_energy,
    double hbar,
    MandelstamTammMetadata metadata);

} // namespace qmw
