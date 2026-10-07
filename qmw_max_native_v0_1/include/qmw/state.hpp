#pragma once

#include <complex>
#include <cstddef>
#include <stdexcept>
#include <string_view>
#include <vector>

namespace qmw {

using Complex = std::complex<double>;

enum class ValidationCode {
    invalid_policy,
    invalid_dimension,
    wrong_element_count,
    non_finite,
    non_hermitian,
    trace_not_one,
    not_positive_semidefinite,
};

[[nodiscard]] std::string_view validation_code_name(ValidationCode code) noexcept;

class ValidationError final : public std::runtime_error {
public:
    ValidationError(ValidationCode code, const char* message);

    [[nodiscard]] ValidationCode code() const noexcept { return code_; }

private:
    ValidationCode code_;
};

struct ValidationPolicy {
    double hermiticity_tolerance {1.0e-10};
    double trace_tolerance {1.0e-10};
    double positivity_tolerance {1.0e-10};
    std::size_t maximum_dimension {64};
};

struct StateDiagnostics {
    Complex trace {};
    double purity {};
    double hermiticity_residual {};
    // This is a validation diagnostic from the unpivoted LDL^H factorization,
    // not the minimum eigenvalue of rho.
    double minimum_ldlt_pivot {};
};

class DensityState final {
public:
    static DensityState from_split(
        std::size_t dimension,
        const std::vector<double>& real,
        const std::vector<double>& imag,
        ValidationPolicy policy = {});

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] const std::vector<Complex>& values() const noexcept { return values_; }
    [[nodiscard]] const StateDiagnostics& diagnostics() const noexcept { return diagnostics_; }
    [[nodiscard]] const Complex& at(std::size_t row, std::size_t column) const;

private:
    DensityState(
        std::size_t dimension,
        std::vector<Complex> values,
        StateDiagnostics diagnostics);

    std::size_t dimension_ {};
    std::vector<Complex> values_;
    StateDiagnostics diagnostics_;
};

} // namespace qmw
