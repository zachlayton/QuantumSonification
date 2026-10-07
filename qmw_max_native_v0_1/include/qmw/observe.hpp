#pragma once

#include "qmw/revisioned_state.hpp"

#include <cstddef>
#include <optional>
#include <string_view>
#include <vector>

namespace qmw {

enum class PauliAxis { x, y, z };

[[nodiscard]] std::optional<PauliAxis> pauli_axis_from_name(std::string_view name) noexcept;

struct PauliObservation {
    long revision {-1};
    std::size_t qubit {};
    PauliAxis axis {PauliAxis::z};
    double expectation {};
};

// The tensor contract is explicit: qubit zero is the least-significant bit of
// the row-major computational-basis index.
[[nodiscard]] double pauli_expectation(
    const DensityState& state,
    std::size_t qubit,
    PauliAxis axis);

// A downstream observer owns only its revision-matched copy of rho. Staged,
// mismatched, stale, and invalid candidates cannot mutate the preceding active
// observation and this class provides no measurement or collapse operation.
class RevisionedPauliObserver final {
public:
    RevisionedPauliObserver(
        std::size_t dimension,
        std::size_t qubit,
        PauliAxis axis,
        ValidationPolicy policy = {});

    [[nodiscard]] StageResult stage(StatePart part, long revision, std::vector<double> values);
    void clear_candidate() noexcept;

    [[nodiscard]] std::size_t dimension() const noexcept { return store_.dimension(); }
    [[nodiscard]] std::size_t element_count() const noexcept { return store_.element_count(); }
    [[nodiscard]] std::size_t qubit() const noexcept { return qubit_; }
    [[nodiscard]] PauliAxis axis() const noexcept { return axis_; }
    [[nodiscard]] std::optional<PauliObservation> active() const;

private:
    RevisionedStateStore store_;
    std::size_t qubit_ {};
    PauliAxis axis_ {PauliAxis::z};
};

} // namespace qmw
