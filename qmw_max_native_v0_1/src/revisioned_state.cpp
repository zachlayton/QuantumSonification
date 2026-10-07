#include "qmw/revisioned_state.hpp"

#include <cmath>
#include <utility>

namespace qmw {

void RevisionedStateStore::CandidatePart::clear() noexcept
{
    revision.reset();
    values.clear();
}

RevisionedStateStore::RevisionedStateStore(
    const std::size_t dimension,
    const ValidationPolicy policy)
    : dimension_(dimension)
    , element_count_(dimension * dimension)
    , policy_(policy)
{
    if (dimension == 0 || dimension > policy.maximum_dimension) {
        throw ValidationError(
            ValidationCode::invalid_dimension,
            "state-store dimension is zero or exceeds the configured limit");
    }
}

StageResult RevisionedStateStore::stage(
    const StatePart part,
    const long revision,
    std::vector<double> values)
{
    if (revision < 0 || revision <= active_revision_) {
        return {StageStatus::rejected, revision, "stale_revision", "revision is not newer than the active state"};
    }
    if (values.size() != element_count_) {
        return {StageStatus::rejected, revision, "wrong_element_count", "component does not contain dimension squared values"};
    }
    for (const double value : values) {
        if (!std::isfinite(value)) {
            return {StageStatus::rejected, revision, "non_finite", "component contains a non-finite value"};
        }
    }

    auto& target = part == StatePart::real ? real_ : imag_;
    target.revision = revision;
    target.values = std::move(values);

    if (!real_.revision.has_value() || !imag_.revision.has_value()
        || *real_.revision != *imag_.revision) {
        return {
            StageStatus::staged,
            revision,
            part == StatePart::real ? "real" : "imag",
            "candidate component staged"};
    }

    try {
        auto state = DensityState::from_split(dimension_, real_.values, imag_.values, policy_);
        active_ = std::make_unique<DensityState>(std::move(state));
        active_revision_ = revision;
        clear_candidate();
        return {StageStatus::accepted, revision, "accepted", "complete density revision accepted"};
    } catch (const ValidationError& error) {
        const std::string detail(validation_code_name(error.code()));
        const std::string message(error.what());
        clear_candidate();
        return {StageStatus::rejected, revision, detail, message};
    }
}

void RevisionedStateStore::clear_candidate() noexcept
{
    real_.clear();
    imag_.clear();
}

} // namespace qmw
