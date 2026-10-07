#include "qmw/flow.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <limits>
#include <utility>

namespace qmw {
namespace {

[[nodiscard]] bool is_power_of_two(const std::size_t value) noexcept
{
    return value != 0 && (value & (value - 1)) == 0;
}

[[nodiscard]] std::size_t exact_qubit_count(std::size_t dimension) noexcept
{
    std::size_t count = 0;
    while (dimension > 1) {
        dimension >>= 1U;
        ++count;
    }
    return count;
}

[[nodiscard]] bool blank(const std::string& value)
{
    return value.empty() || std::all_of(
        value.begin(), value.end(), [](const unsigned char character) {
            return std::isspace(character) != 0;
        });
}

void validate_definition(
    const std::size_t dimension,
    const double hbar,
    const FlowMetadata& metadata,
    const FlowPolicy& policy)
{
    if (!is_power_of_two(dimension) || dimension > policy.maximum_dimension) {
        throw FlowError(
            FlowCode::invalid_dimension,
            "qmw.flow dimension must be a nonzero power of two within the configured limit");
    }
    if (!std::isfinite(hbar) || !(hbar > 0.0)) {
        throw FlowError(FlowCode::invalid_hbar, "hbar must be positive and finite");
    }
    if (!std::isfinite(policy.hamiltonian_relative_hermiticity_tolerance)
        || !std::isfinite(policy.density_hermiticity_tolerance)
        || !std::isfinite(policy.density_trace_tolerance)
        || !std::isfinite(policy.density_positivity_tolerance)
        || !std::isfinite(policy.conservation_tolerance)
        || !std::isfinite(policy.phase_definition_tolerance)
        || !(policy.hamiltonian_relative_hermiticity_tolerance > 0.0)
        || !(policy.density_hermiticity_tolerance > 0.0)
        || !(policy.density_trace_tolerance > 0.0)
        || !(policy.density_positivity_tolerance > 0.0)
        || !(policy.conservation_tolerance > 0.0)
        || policy.phase_definition_tolerance < 0.0
        || policy.maximum_dimension == 0) {
        throw FlowError(FlowCode::invalid_policy, "qmw.flow validation policy is invalid");
    }
    if (blank(metadata.energy_unit) || blank(metadata.time_unit)
        || blank(metadata.basis_id) || blank(metadata.basis_kind)
        || blank(metadata.state_source_id) || blank(metadata.hamiltonian_source_id)
        || blank(metadata.provenance) || blank(metadata.index_orientation)
        || blank(metadata.bit_order)) {
        throw FlowError(
            FlowCode::invalid_metadata,
            "flow units, basis, sources, provenance, orientation, and bit order must be nonempty");
    }
    if (metadata.index_orientation != "row_target_column_source") {
        throw FlowError(
            FlowCode::invalid_metadata,
            "qmw.flow requires row_target_column_source matrix orientation");
    }
    if (metadata.bit_order != "q0_lsb") {
        throw FlowError(FlowCode::invalid_metadata, "qmw.flow requires q0_lsb bit order");
    }
}

[[noreturn]] void translate_state_error(const ValidationError& error)
{
    switch (error.code()) {
    case ValidationCode::invalid_policy:
        throw FlowError(FlowCode::invalid_policy, error.what());
    case ValidationCode::invalid_dimension:
        throw FlowError(FlowCode::invalid_dimension, error.what());
    case ValidationCode::wrong_element_count:
        throw FlowError(FlowCode::wrong_element_count, error.what());
    case ValidationCode::non_finite:
        throw FlowError(FlowCode::non_finite, error.what());
    case ValidationCode::non_hermitian:
        throw FlowError(FlowCode::non_hermitian, error.what());
    case ValidationCode::trace_not_one:
        throw FlowError(FlowCode::trace_not_one, error.what());
    case ValidationCode::not_positive_semidefinite:
        throw FlowError(FlowCode::not_positive_semidefinite, error.what());
    }
    throw FlowError(FlowCode::numerical_inconsistency, error.what());
}

[[noreturn]] void translate_hamiltonian_error(const HamiltonianValidationError& error)
{
    switch (error.code()) {
    case HamiltonianValidationCode::invalid_dimension:
        throw FlowError(FlowCode::invalid_dimension, error.what());
    case HamiltonianValidationCode::wrong_element_count:
        throw FlowError(FlowCode::wrong_element_count, error.what());
    case HamiltonianValidationCode::non_finite:
        throw FlowError(FlowCode::non_finite, error.what());
    case HamiltonianValidationCode::non_hermitian:
        throw FlowError(FlowCode::non_hermitian, error.what());
    case HamiltonianValidationCode::invalid_metadata:
        throw FlowError(FlowCode::invalid_metadata, error.what());
    case HamiltonianValidationCode::invalid_policy:
        throw FlowError(FlowCode::invalid_policy, error.what());
    }
    throw FlowError(FlowCode::numerical_inconsistency, error.what());
}

[[nodiscard]] FlowPhase phase_of(const Complex value, const double tolerance)
{
    if (std::abs(value) <= tolerance) {
        return {};
    }
    return {std::atan2(value.imag(), value.real()), true};
}

[[nodiscard]] double scaled_tolerance(
    const double base,
    const double maximum_current,
    const std::size_t dimension)
{
    return base * std::max(1.0, maximum_current * static_cast<double>(dimension));
}

} // namespace

std::string_view flow_code_name(const FlowCode code) noexcept
{
    switch (code) {
    case FlowCode::invalid_policy: return "invalid_policy";
    case FlowCode::invalid_dimension: return "invalid_dimension";
    case FlowCode::wrong_element_count: return "wrong_element_count";
    case FlowCode::non_finite: return "non_finite";
    case FlowCode::non_hermitian: return "non_hermitian";
    case FlowCode::trace_not_one: return "trace_not_one";
    case FlowCode::not_positive_semidefinite: return "not_positive_semidefinite";
    case FlowCode::invalid_metadata: return "invalid_metadata";
    case FlowCode::invalid_hbar: return "invalid_hbar";
    case FlowCode::invalid_revision: return "invalid_revision";
    case FlowCode::stale_revision: return "stale_revision";
    case FlowCode::incomplete_transaction: return "incomplete_transaction";
    case FlowCode::revision_mismatch: return "revision_mismatch";
    case FlowCode::numerical_inconsistency: return "numerical_inconsistency";
    }
    return "unknown_flow_error";
}

FlowError::FlowError(const FlowCode code, std::string message)
    : std::runtime_error(std::move(message))
    , code_(code)
{
}

FlowSnapshot::FlowSnapshot(
    const long revision,
    const std::size_t dimension,
    const std::size_t qubits,
    const double hbar,
    FlowMetadata metadata,
    std::string hbar_unit,
    std::string current_unit,
    HamiltonianSnapshot hamiltonian,
    DensityState density,
    std::vector<double> current_matrix,
    std::vector<double> population_derivative,
    std::vector<double> divergence,
    std::vector<FlowEdge> directed_edges,
    const FlowDiagnostics diagnostics)
    : revision_(revision)
    , dimension_(dimension)
    , qubits_(qubits)
    , hbar_(hbar)
    , metadata_(std::move(metadata))
    , hbar_unit_(std::move(hbar_unit))
    , current_unit_(std::move(current_unit))
    , hamiltonian_(std::move(hamiltonian))
    , density_(std::move(density))
    , current_matrix_(std::move(current_matrix))
    , population_derivative_(std::move(population_derivative))
    , divergence_(std::move(divergence))
    , directed_edges_(std::move(directed_edges))
    , diagnostics_(diagnostics)
{
}

double FlowSnapshot::current(const std::size_t target, const std::size_t source) const
{
    if (target >= dimension_ || source >= dimension_) {
        throw std::out_of_range("qmw.flow current index is outside the dimension");
    }
    return current_matrix_[target * dimension_ + source];
}

FlowSnapshot FlowSnapshot::evaluate(
    const long revision,
    const std::size_t dimension,
    const std::vector<double>& hamiltonian_real,
    const std::vector<double>& hamiltonian_imag,
    const std::vector<double>& density_real,
    const std::vector<double>& density_imag,
    const double hbar,
    FlowMetadata metadata,
    const FlowPolicy policy)
{
    validate_definition(dimension, hbar, metadata, policy);
    if (revision < 0) {
        throw FlowError(FlowCode::invalid_revision, "qmw.flow revision must be nonnegative");
    }

    DensityState density = [&] {
        try {
            return DensityState::from_split(
                dimension,
                density_real,
                density_imag,
                ValidationPolicy {
                    policy.density_hermiticity_tolerance,
                    policy.density_trace_tolerance,
                    policy.density_positivity_tolerance,
                    policy.maximum_dimension,
                });
        } catch (const ValidationError& error) {
            translate_state_error(error);
        }
    }();

    HamiltonianSnapshot hamiltonian = [&] {
        try {
            return HamiltonianSnapshot::from_split(
                dimension,
                hamiltonian_real,
                hamiltonian_imag,
                HamiltonianMetadata {
                    metadata.energy_unit,
                    metadata.basis_id,
                    metadata.hamiltonian_source_id,
                    metadata.provenance,
                },
                HamiltonianValidationPolicy {
                    policy.hamiltonian_relative_hermiticity_tolerance,
                    policy.maximum_dimension,
                });
        } catch (const HamiltonianValidationError& error) {
            translate_hamiltonian_error(error);
        }
    }();

    const auto& h = hamiltonian.values();
    const auto& rho = density.values();
    std::vector<double> currents(dimension * dimension, 0.0);
    std::vector<double> divergence(dimension, 0.0);
    std::vector<double> population_derivative(dimension, 0.0);
    std::vector<FlowEdge> edges;
    edges.reserve(dimension * (dimension - 1));

    double maximum_current = 0.0;
    for (std::size_t target = 0; target < dimension; ++target) {
        for (std::size_t source = 0; source < dimension; ++source) {
            if (target == source) {
                continue;
            }
            const Complex coupling = h[target * dimension + source];
            const Complex coherence = rho[source * dimension + target];
            const Complex transport_product = coupling * coherence;
            const double current = (2.0 / hbar) * transport_product.imag();
            if (!std::isfinite(transport_product.real())
                || !std::isfinite(transport_product.imag())
                || !std::isfinite(current)) {
                throw FlowError(
                    FlowCode::numerical_inconsistency,
                    "probability-current evaluation produced a non-finite value");
            }
            currents[target * dimension + source] = current;
            divergence[target] += current;
            maximum_current = std::max(maximum_current, std::abs(current));
            edges.push_back(FlowEdge {
                source,
                target,
                current,
                std::abs(coupling),
                std::abs(coherence),
                phase_of(coupling, policy.phase_definition_tolerance),
                phase_of(coherence, policy.phase_definition_tolerance),
                phase_of(transport_product, policy.phase_definition_tolerance),
                true,
                true,
            });
        }
    }

    double derivative_imaginary_max = 0.0;
    for (std::size_t target = 0; target < dimension; ++target) {
        Complex h_rho {};
        Complex rho_h {};
        for (std::size_t inner = 0; inner < dimension; ++inner) {
            h_rho += h[target * dimension + inner] * rho[inner * dimension + target];
            rho_h += rho[target * dimension + inner] * h[inner * dimension + target];
        }
        const Complex derivative = Complex {0.0, -1.0 / hbar} * (h_rho - rho_h);
        if (!std::isfinite(derivative.real()) || !std::isfinite(derivative.imag())) {
            throw FlowError(
                FlowCode::numerical_inconsistency,
                "population-derivative evaluation produced a non-finite value");
        }
        population_derivative[target] = derivative.real();
        derivative_imaginary_max = std::max(
            derivative_imaginary_max, std::abs(derivative.imag()));
    }

    double antisymmetry_max = 0.0;
    double continuity_max = 0.0;
    double total_derivative = 0.0;
    for (std::size_t target = 0; target < dimension; ++target) {
        continuity_max = std::max(
            continuity_max,
            std::abs(population_derivative[target] - divergence[target]));
        total_derivative += population_derivative[target];
        for (std::size_t source = 0; source < dimension; ++source) {
            antisymmetry_max = std::max(
                antisymmetry_max,
                std::abs(currents[target * dimension + source]
                    + currents[source * dimension + target]));
        }
    }

    const double tolerance = scaled_tolerance(
        policy.conservation_tolerance, maximum_current, dimension);
    if (antisymmetry_max > tolerance || continuity_max > tolerance
        || derivative_imaginary_max > tolerance || std::abs(total_derivative) > tolerance) {
        throw FlowError(
            FlowCode::numerical_inconsistency,
            "probability current failed antisymmetry or continuity validation");
    }

    FlowDiagnostics diagnostics {
        hamiltonian.diagnostics().hermiticity_residual_fro,
        density.diagnostics().hermiticity_residual,
        std::abs(density.diagnostics().trace - Complex {1.0, 0.0}),
        density.diagnostics().minimum_ldlt_pivot,
        antisymmetry_max,
        continuity_max,
        derivative_imaginary_max,
        std::abs(total_derivative),
    };

    const std::string hbar_unit = metadata.energy_unit + "*" + metadata.time_unit;
    const std::string current_unit = "1/" + metadata.time_unit;
    return FlowSnapshot(
        revision,
        dimension,
        exact_qubit_count(dimension),
        hbar,
        std::move(metadata),
        hbar_unit,
        current_unit,
        std::move(hamiltonian),
        std::move(density),
        std::move(currents),
        std::move(population_derivative),
        std::move(divergence),
        std::move(edges),
        diagnostics);
}

void RevisionedFlowStore::CandidatePart::clear() noexcept
{
    revision.reset();
    values.clear();
}

RevisionedFlowStore::RevisionedFlowStore(
    const std::size_t dimension,
    const double hbar,
    FlowMetadata metadata,
    const FlowPolicy policy)
    : dimension_(dimension)
    , element_count_(dimension * dimension)
    , hbar_(hbar)
    , metadata_(std::move(metadata))
    , policy_(policy)
{
    validate_definition(dimension_, hbar_, metadata_, policy_);
}

RevisionedFlowStore::CandidatePart& RevisionedFlowStore::candidate(
    const FlowPart part) noexcept
{
    switch (part) {
    case FlowPart::hamiltonian_real: return hamiltonian_real_;
    case FlowPart::hamiltonian_imag: return hamiltonian_imag_;
    case FlowPart::density_real: return density_real_;
    case FlowPart::density_imag: return density_imag_;
    }
    return density_real_;
}

const RevisionedFlowStore::CandidatePart& RevisionedFlowStore::candidate(
    const FlowPart part) const noexcept
{
    return const_cast<RevisionedFlowStore*>(this)->candidate(part);
}

FlowStageResult RevisionedFlowStore::stage(
    const FlowPart part,
    const long revision,
    std::vector<double> values)
{
    if (revision < 0) {
        return {FlowStageStatus::rejected, revision, "invalid_revision", "revision must be nonnegative"};
    }
    if (revision <= active_revision_) {
        return {FlowStageStatus::rejected, revision, "stale_revision", "revision is not newer than active"};
    }
    if (values.size() != element_count_) {
        return {FlowStageStatus::rejected, revision, "wrong_element_count", "component must contain dimension squared values"};
    }
    if (!std::all_of(values.begin(), values.end(), [](const double value) {
            return std::isfinite(value);
        })) {
        return {FlowStageStatus::rejected, revision, "non_finite", "component contains a non-finite value"};
    }
    auto& destination = candidate(part);
    destination.revision = revision;
    destination.values = std::move(values);
    return {FlowStageStatus::staged, revision, "component_staged", "component staged invisibly"};
}

FlowStageResult RevisionedFlowStore::commit(const long revision)
{
    if (revision < 0) {
        return {FlowStageStatus::rejected, revision, "invalid_revision", "revision must be nonnegative"};
    }
    if (revision <= active_revision_) {
        return {FlowStageStatus::rejected, revision, "stale_revision", "revision is not newer than active"};
    }

    const std::array<const CandidatePart*, 4> parts {
        &hamiltonian_real_, &hamiltonian_imag_, &density_real_, &density_imag_};
    if (std::any_of(parts.begin(), parts.end(), [](const CandidatePart* part) {
            return !part->revision.has_value();
        })) {
        return {FlowStageStatus::rejected, revision, "incomplete_transaction", "all four matrix components are required"};
    }
    if (std::any_of(parts.begin(), parts.end(), [revision](const CandidatePart* part) {
            return *part->revision != revision;
        })) {
        return {FlowStageStatus::rejected, revision, "revision_mismatch", "all components must match the committed revision"};
    }

    try {
        auto snapshot = std::make_unique<FlowSnapshot>(FlowSnapshot::evaluate(
            revision,
            dimension_,
            hamiltonian_real_.values,
            hamiltonian_imag_.values,
            density_real_.values,
            density_imag_.values,
            hbar_,
            metadata_,
            policy_));
        active_ = std::move(snapshot);
        active_revision_ = revision;
        clear_candidate();
        return {FlowStageStatus::accepted, revision, "accepted", "flow frame accepted atomically"};
    } catch (const FlowError& error) {
        return {
            FlowStageStatus::rejected,
            revision,
            std::string(flow_code_name(error.code())),
            error.what(),
        };
    }
}

void RevisionedFlowStore::clear_candidate() noexcept
{
    hamiltonian_real_.clear();
    hamiltonian_imag_.clear();
    density_real_.clear();
    density_imag_.clear();
}

} // namespace qmw
