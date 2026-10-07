#pragma once

#include "qmw/state.hpp"

#include <cstddef>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace qmw {

enum class StatePart { real, imag };
enum class StageStatus { staged, accepted, rejected };

struct StageResult {
    StageStatus status {StageStatus::rejected};
    long revision {-1};
    std::string detail;
    std::string message;
};

class RevisionedStateStore final {
public:
    explicit RevisionedStateStore(std::size_t dimension, ValidationPolicy policy = {});

    [[nodiscard]] StageResult stage(StatePart part, long revision, std::vector<double> values);
    void clear_candidate() noexcept;

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t element_count() const noexcept { return element_count_; }
    [[nodiscard]] long active_revision() const noexcept { return active_revision_; }
    [[nodiscard]] const DensityState* active() const noexcept { return active_.get(); }

private:
    struct CandidatePart {
        std::optional<long> revision;
        std::vector<double> values;

        void clear() noexcept;
    };

    std::size_t dimension_ {};
    std::size_t element_count_ {};
    ValidationPolicy policy_;
    long active_revision_ {-1};
    std::unique_ptr<DensityState> active_;
    CandidatePart real_;
    CandidatePart imag_;
};

} // namespace qmw
