#include "qmw/observe.hpp"

#include <cmath>
#include <stdexcept>
#include <utility>

namespace qmw {
namespace {

[[nodiscard]] bool valid_axis(const PauliAxis axis) noexcept
{
    switch (axis) {
    case PauliAxis::x:
    case PauliAxis::y:
    case PauliAxis::z:
        return true;
    }
    return false;
}

void validate_observation_request(
    const std::size_t dimension,
    const std::size_t qubit,
    const PauliAxis axis)
{
    if (!valid_axis(axis)) {
        throw std::invalid_argument("Pauli axis must be X, Y, or Z");
    }
    if (dimension == 0 || (dimension & (dimension - 1)) != 0) {
        throw std::invalid_argument("Pauli observation requires a power-of-two dimension");
    }

    std::size_t qubit_count = 0;
    for (auto value = dimension; value > 1; value >>= 1U) {
        ++qubit_count;
    }
    if (qubit >= qubit_count) {
        throw std::out_of_range("qubit index exceeds the state tensor factorization");
    }
}

} // namespace

std::optional<PauliAxis> pauli_axis_from_name(const std::string_view name) noexcept
{
    if (name == "X" || name == "x") {
        return PauliAxis::x;
    }
    if (name == "Y" || name == "y") {
        return PauliAxis::y;
    }
    if (name == "Z" || name == "z") {
        return PauliAxis::z;
    }
    return std::nullopt;
}

double pauli_expectation(
    const DensityState& state,
    const std::size_t qubit,
    const PauliAxis axis)
{
    const auto dimension = state.dimension();
    validate_observation_request(dimension, qubit, axis);

    const std::size_t mask = std::size_t {1} << qubit;
    double expectation = 0.0;
    for (std::size_t lower = 0; lower < dimension; ++lower) {
        if ((lower & mask) != 0) {
            continue;
        }
        const auto upper = lower | mask;
        switch (axis) {
        case PauliAxis::x:
            expectation += 2.0 * state.at(lower, upper).real();
            break;
        case PauliAxis::y:
            expectation -= 2.0 * state.at(lower, upper).imag();
            break;
        case PauliAxis::z:
            expectation += state.at(lower, lower).real() - state.at(upper, upper).real();
            break;
        }
    }
    return expectation;
}

RevisionedPauliObserver::RevisionedPauliObserver(
    const std::size_t dimension,
    const std::size_t qubit,
    const PauliAxis axis,
    const ValidationPolicy policy)
    : store_(dimension, policy)
    , qubit_(qubit)
    , axis_(axis)
{
    validate_observation_request(dimension, qubit, axis);
}

StageResult RevisionedPauliObserver::stage(
    const StatePart part,
    const long revision,
    std::vector<double> values)
{
    return store_.stage(part, revision, std::move(values));
}

void RevisionedPauliObserver::clear_candidate() noexcept
{
    store_.clear_candidate();
}

std::optional<PauliObservation> RevisionedPauliObserver::active() const
{
    const auto* state = store_.active();
    if (state == nullptr) {
        return std::nullopt;
    }
    return PauliObservation {
        store_.active_revision(),
        qubit_,
        axis_,
        pauli_expectation(*state, qubit_, axis_),
    };
}

} // namespace qmw
