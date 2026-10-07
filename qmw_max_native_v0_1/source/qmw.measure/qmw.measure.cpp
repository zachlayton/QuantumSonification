#include "qmw/measure.hpp"
#include "qmw/revisioned_state.hpp"

#include "ext.h"
#include "ext_obex.h"

#include <cmath>
#include <cstddef>
#include <cstdio>
#include <cstdint>
#include <exception>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace {

class MeasureAdapter final {
public:
    MeasureAdapter(
        const long qubits,
        const qmw::ProjectiveAxis axis,
        const std::uint64_t seed,
        qmw::MeasurementMetadata measurement_metadata,
        qmw::MeasurementContext state_context)
        : state_(std::size_t {1} << qubits)
        , engine_(qmw::ProjectiveMeasurement::pauli_product(
              static_cast<std::size_t>(qubits), axis, std::move(measurement_metadata)), seed)
        , context_(std::move(state_context))
    {
    }

    [[nodiscard]] qmw::RevisionedStateStore& state() noexcept { return state_; }
    [[nodiscard]] const qmw::RevisionedStateStore& state() const noexcept { return state_; }
    [[nodiscard]] qmw::MeasurementEngine& engine() noexcept { return engine_; }
    [[nodiscard]] const qmw::MeasurementContext& context_template() const noexcept { return context_; }
    [[nodiscard]] const std::optional<qmw::MeasurementRecord>& last_record() const noexcept { return last_; }
    void retain(qmw::MeasurementRecord record) { last_ = std::move(record); }

private:
    qmw::RevisionedStateStore state_;
    qmw::MeasurementEngine engine_;
    qmw::MeasurementContext context_;
    std::optional<qmw::MeasurementRecord> last_;
};

struct QmwMeasureObject {
    t_object object;
    MeasureAdapter* adapter;
    void* candidate_outlet;
    void* record_outlet;
    void* status_outlet;
};

t_class* qmw_measure_class = nullptr;

void status(
    QmwMeasureObject* object,
    const char* selector,
    const long revision,
    const char* detail = nullptr)
{
    t_atom atoms[2];
    atom_setlong(atoms, revision);
    long count = 1;
    if (detail != nullptr) {
        atom_setsym(atoms + 1, gensym(detail));
        count = 2;
    }
    outlet_anything(object->status_outlet, gensym(selector), count, atoms);
}

[[nodiscard]] bool numeric_atom(const t_atom* atom)
{
    const auto type = atom_gettype(atom);
    return type == A_LONG || type == A_FLOAT;
}

void output_record(QmwMeasureObject* object, const qmw::MeasurementRecord& record)
{
    const auto event_id = static_cast<long>(record.event_id);
    t_atom begin[3];
    atom_setlong(begin, event_id);
    atom_setlong(begin + 1, record.request_id);
    atom_setlong(begin + 2, record.parent_revision);
    outlet_anything(object->status_outlet, gensym("measurement_begin"), 3, begin);

    std::vector<t_atom> probabilities(4 + 2 * record.distribution.probabilities.size());
    atom_setlong(probabilities.data(), event_id);
    atom_setlong(probabilities.data() + 1, record.request_id);
    atom_setlong(probabilities.data() + 2, record.parent_revision);
    atom_setlong(
        probabilities.data() + 3,
        static_cast<long>(record.distribution.probabilities.size()));
    for (std::size_t index = 0; index < record.distribution.probabilities.size(); ++index) {
        atom_setlong(probabilities.data() + 4 + 2 * index, record.distribution.outcomes[index]);
        atom_setfloat(probabilities.data() + 5 + 2 * index, record.distribution.probabilities[index]);
    }
    outlet_anything(
        object->record_outlet, gensym("probabilities_exact"),
        static_cast<long>(probabilities.size()), probabilities.data());

    t_atom summary[8];
    atom_setlong(summary, event_id);
    atom_setlong(summary + 1, record.request_id);
    atom_setlong(summary + 2, record.parent_revision);
    atom_setsym(summary + 3, gensym(
        record.selection == qmw::MeasurementSelection::seeded_sample
            ? "seeded_sample" : "specified_outcome_conditioning"));
    atom_setlong(summary + 4, record.outcome);
    atom_setsym(summary + 5, gensym(record.outcome_label.c_str()));
    atom_setfloat(summary + 6, record.probability);
    atom_setsym(summary + 7, gensym("posterior_candidate_not_committed"));
    outlet_anything(object->record_outlet, gensym("measurement_record"), 8, summary);

    const auto& rng = record.rng;
    t_atom rng_atoms[9];
    atom_setlong(rng_atoms, event_id);
    atom_setlong(rng_atoms + 1, rng.used ? 1 : 0);
    atom_setsym(rng_atoms + 2, gensym(rng.algorithm.c_str()));
    atom_setsym(rng_atoms + 3, gensym(rng.version.c_str()));
    atom_setlong(rng_atoms + 4, static_cast<long>(rng.seed));
    atom_setlong(rng_atoms + 5, static_cast<long>(rng.draw_index_before));
    atom_setlong(rng_atoms + 6, static_cast<long>(rng.draw_index_after));
    atom_setfloat(rng_atoms + 7, rng.uniform_01);
    atom_setsym(rng_atoms + 8, gensym("one_u64_upper_53_bits_to_unit_interval"));
    outlet_anything(object->record_outlet, gensym("rng"), 9, rng_atoms);

    const auto& distribution = record.distribution;
    t_atom semantics[9];
    atom_setlong(semantics, event_id);
    atom_setsym(semantics + 1, gensym(distribution.probability_semantics.c_str()));
    atom_setsym(semantics + 2, gensym(distribution.estimate_semantics.c_str()));
    atom_setsym(semantics + 3, gensym(distribution.counts_semantics.c_str()));
    atom_setsym(semantics + 4, gensym(distribution.uncertainty_semantics.c_str()));
    atom_setfloat(semantics + 5, distribution.raw_probability_sum);
    atom_setfloat(semantics + 6, distribution.normalization_denominator);
    atom_setlong(semantics + 7, record.counts.has_value() ? 1 : 0);
    atom_setlong(semantics + 8, record.probability_standard_uncertainty.has_value() ? 1 : 0);
    outlet_anything(object->record_outlet, gensym("data_semantics"), 9, semantics);

    const auto& measurement = record.measurement_metadata;
    const auto& state = record.state_context;
    t_atom provenance[12];
    atom_setlong(provenance, event_id);
    atom_setlong(provenance + 1, record.parent_revision);
    atom_setsym(provenance + 2, gensym(state.state_basis_id.c_str()));
    atom_setsym(provenance + 3, gensym(measurement.operator_basis_id.c_str()));
    atom_setsym(provenance + 4, gensym(measurement.subsystem_order.c_str()));
    atom_setsym(provenance + 5, gensym(state.state_units.c_str()));
    atom_setsym(provenance + 6, gensym(state.state_source_id.c_str()));
    atom_setsym(provenance + 7, gensym(state.state_provenance.c_str()));
    atom_setsym(provenance + 8, gensym(measurement.source_id.c_str()));
    atom_setsym(provenance + 9, gensym(measurement.provenance.c_str()));
    atom_setsym(provenance + 10, gensym(record.state_installation.c_str()));
    atom_setlong(provenance + 11, record.authority_state_mutated ? 1 : 0);
    outlet_anything(object->record_outlet, gensym("provenance"), 12, provenance);

    const auto& posterior = record.posterior;
    std::vector<t_atom> real(posterior.values.size() + 5);
    std::vector<t_atom> imag(posterior.values.size() + 5);
    for (auto* atoms : {&real, &imag}) {
        atom_setlong(atoms->data(), event_id);
        atom_setlong(atoms->data() + 1, record.request_id);
        atom_setlong(atoms->data() + 2, posterior.parent_revision);
        atom_setlong(atoms->data() + 3, posterior.outcome);
        atom_setlong(atoms->data() + 4, static_cast<long>(object->adapter->state().dimension()));
    }
    for (std::size_t index = 0; index < posterior.values.size(); ++index) {
        atom_setfloat(real.data() + index + 5, posterior.values[index].real());
        atom_setfloat(imag.data() + index + 5, posterior.values[index].imag());
    }
    outlet_anything(
        object->candidate_outlet, gensym("posterior_candidate_real"),
        static_cast<long>(real.size()), real.data());
    outlet_anything(
        object->candidate_outlet, gensym("posterior_candidate_imag"),
        static_cast<long>(imag.size()), imag.data());

    outlet_anything(object->status_outlet, gensym("measurement_accepted"), 3, begin);
}

void stage_component(
    QmwMeasureObject* object,
    const qmw::StatePart part,
    const char* component,
    const long argc,
    const t_atom* argv)
{
    const auto required = static_cast<long>(object->adapter->state().element_count() + 1);
    if (argc != required) {
        object_error(
            &object->object, "%s requires revision plus %zu row-major values",
            component, object->adapter->state().element_count());
        status(object, "rejected", -1, "wrong_element_count");
        return;
    }
    if (atom_gettype(argv) != A_LONG) {
        object_error(&object->object, "%s revision must be an integer", component);
        status(object, "rejected", -1, "invalid_revision_atom");
        return;
    }
    const long revision = atom_getlong(argv);
    std::vector<double> values;
    values.reserve(object->adapter->state().element_count());
    for (long index = 1; index < argc; ++index) {
        if (!numeric_atom(argv + index)) {
            object_error(&object->object, "%s contains a nonnumeric atom", component);
            status(object, "rejected", revision, "nonnumeric_atom");
            return;
        }
        const double value = atom_getfloat(argv + index);
        if (!std::isfinite(value)) {
            object_error(&object->object, "%s contains a non-finite value", component);
            status(object, "rejected", revision, "non_finite");
            return;
        }
        values.push_back(value);
    }
    const auto result = object->adapter->state().stage(part, revision, std::move(values));
    switch (result.status) {
    case qmw::StageStatus::staged:
        status(object, "staged", revision, component);
        break;
    case qmw::StageStatus::accepted:
        // Admission never triggers measurement. A sample/condition message is
        // a separate explicit intervention.
        status(object, "rho_accepted", revision);
        break;
    case qmw::StageStatus::rejected:
        object_error(&object->object, "rho revision %ld rejected: %s", revision, result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        break;
    }
}

void qmw_measure_rho_real(QmwMeasureObject* object, t_symbol*, const long argc, t_atom* argv)
{
    stage_component(object, qmw::StatePart::real, "rho_real", argc, argv);
}

void qmw_measure_rho_imag(QmwMeasureObject* object, t_symbol*, const long argc, t_atom* argv)
{
    stage_component(object, qmw::StatePart::imag, "rho_imag", argc, argv);
}

[[nodiscard]] std::optional<long> request_id(
    QmwMeasureObject* object,
    const char* method,
    const long argc,
    const t_atom* argv)
{
    if (argc > 1 || (argc == 1 && atom_gettype(argv) != A_LONG)) {
        object_error(&object->object, "%s accepts one optional integer request id", method);
        status(object, "rejected", object->adapter->state().active_revision(), "invalid_request_atoms");
        return std::nullopt;
    }
    const long value = argc == 0 ? 0 : atom_getlong(argv);
    if (value < 0) {
        object_error(&object->object, "request id must be nonnegative");
        status(object, "rejected", object->adapter->state().active_revision(), "invalid_request");
        return std::nullopt;
    }
    return value;
}

void qmw_measure_sample(QmwMeasureObject* object, t_symbol*, const long argc, t_atom* argv)
{
    const auto request = request_id(object, "sample", argc, argv);
    if (!request.has_value()) return;
    const auto* state = object->adapter->state().active();
    if (state == nullptr) {
        status(object, "empty", -1, "no_accepted_rho");
        return;
    }
    auto context = object->adapter->context_template();
    context.parent_revision = object->adapter->state().active_revision();
    try {
        object->adapter->retain(object->adapter->engine().sample(*state, context, *request));
        output_record(object, *object->adapter->last_record());
    } catch (const qmw::MeasurementError& error) {
        object_error(&object->object, "measurement rejected: %s", error.what());
        const std::string detail(qmw::measurement_code_name(error.code()));
        status(object, "rejected", context.parent_revision, detail.c_str());
    } catch (const std::exception& error) {
        object_error(&object->object, "measurement rejected: %s", error.what());
        status(object, "rejected", context.parent_revision, "measurement_error");
    }
}

void qmw_measure_condition(QmwMeasureObject* object, t_symbol*, const long argc, t_atom* argv)
{
    if (argc != 2 || atom_gettype(argv) != A_LONG || atom_gettype(argv + 1) != A_LONG) {
        object_error(&object->object, "condition requires integer request_id and outcome");
        status(object, "rejected", object->adapter->state().active_revision(), "invalid_condition_atoms");
        return;
    }
    const auto* state = object->adapter->state().active();
    if (state == nullptr) {
        status(object, "empty", -1, "no_accepted_rho");
        return;
    }
    auto context = object->adapter->context_template();
    context.parent_revision = object->adapter->state().active_revision();
    try {
        object->adapter->retain(object->adapter->engine().condition(
            *state, context, atom_getlong(argv + 1), atom_getlong(argv)));
        output_record(object, *object->adapter->last_record());
    } catch (const qmw::MeasurementError& error) {
        object_error(&object->object, "conditioning rejected: %s", error.what());
        const std::string detail(qmw::measurement_code_name(error.code()));
        status(object, "rejected", context.parent_revision, detail.c_str());
    } catch (const std::exception& error) {
        object_error(&object->object, "conditioning rejected: %s", error.what());
        status(object, "rejected", context.parent_revision, "measurement_error");
    }
}

void qmw_measure_bang(QmwMeasureObject* object)
{
    if (!object->adapter->last_record().has_value()) {
        status(object, "empty", object->adapter->state().active_revision(), "no_measurement_record");
        return;
    }
    output_record(object, *object->adapter->last_record());
}

void qmw_measure_clear(QmwMeasureObject* object)
{
    object->adapter->state().clear_candidate();
    status(object, "candidate_cleared", object->adapter->state().active_revision());
}

[[nodiscard]] bool symbol_arg(
    const long argc,
    const t_atom* argv,
    const long index,
    std::string& target)
{
    if (argc <= index) return true;
    if (atom_gettype(argv + index) != A_SYM) return false;
    target = atom_getsym(argv + index)->s_name;
    return true;
}

void qmw_measure_assist(QmwMeasureObject*, void*, const long message, const long index, char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "rho_real/rho_imag transaction; sample [request]; condition request outcome; bang; clear";
    } else {
        const char* const outlets[] = {
            "Posterior density candidate (never auto-committed)",
            "Born probabilities, outcome record, RNG, and provenance",
            "Measurement framing, transaction status, and errors",
        };
        label = index >= 0 && index < 3 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_measure_new(t_symbol*, const long argc, t_atom* argv)
{
    auto* object = static_cast<QmwMeasureObject*>(object_alloc(qmw_measure_class));
    if (object == nullptr) return nullptr;
    object->adapter = nullptr;

    if (argc < 2 || argc > 8 || atom_gettype(argv) != A_SYM
        || atom_gettype(argv + 1) != A_LONG) {
        object_error(
            &object->object,
            "usage: qmw.measure X|Y|Z qubits [seed] [coordinate_basis] [state_source] [state_provenance] [measurement_source] [measurement_provenance]");
        object_free(&object->object);
        return nullptr;
    }
    const auto axis = qmw::projective_axis_from_name(atom_getsym(argv)->s_name);
    const long qubits = atom_getlong(argv + 1);
    if (!axis.has_value() || qubits < 1 || qubits > 6) {
        object_error(&object->object, "require basis X, Y, or Z and 1 <= qubits <= 6");
        object_free(&object->object);
        return nullptr;
    }
    long seed = 29;
    if (argc > 2) {
        if (atom_gettype(argv + 2) != A_LONG || atom_getlong(argv + 2) < 0) {
            object_error(&object->object, "seed must be a nonnegative integer");
            object_free(&object->object);
            return nullptr;
        }
        seed = atom_getlong(argv + 2);
    }

    qmw::MeasurementMetadata measurement;
    qmw::MeasurementContext context;
    if (!symbol_arg(argc, argv, 3, measurement.coordinate_basis_id)
        || !symbol_arg(argc, argv, 4, context.state_source_id)
        || !symbol_arg(argc, argv, 5, context.state_provenance)
        || !symbol_arg(argc, argv, 6, measurement.source_id)
        || !symbol_arg(argc, argv, 7, measurement.provenance)) {
        object_error(&object->object, "basis, sources, and provenance arguments must be symbols");
        object_free(&object->object);
        return nullptr;
    }
    context.state_basis_id = measurement.coordinate_basis_id;
    measurement.operator_basis_id = measurement.coordinate_basis_id
        + ":measurement:" + std::string(qmw::projective_axis_name(*axis));

    try {
        object->adapter = new MeasureAdapter(
            qubits, *axis, static_cast<std::uint64_t>(seed),
            std::move(measurement), std::move(context));
    } catch (const std::exception& error) {
        object_error(&object->object, "could not create measurement instrument: %s", error.what());
        object_free(&object->object);
        return nullptr;
    }
    // Max creates multiple outlets from right to left.
    object->status_outlet = outlet_new(object, nullptr);
    object->record_outlet = outlet_new(object, nullptr);
    object->candidate_outlet = outlet_new(object, nullptr);
    return object;
}

void qmw_measure_free(QmwMeasureObject* object)
{
    delete object->adapter;
    object->adapter = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.measure",
        reinterpret_cast<method>(qmw_measure_new),
        reinterpret_cast<method>(qmw_measure_free),
        sizeof(QmwMeasureObject),
        nullptr,
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_measure_rho_real), "rho_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_measure_rho_imag), "rho_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_measure_sample), "sample", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_measure_condition), "condition", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_measure_bang), "bang", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_measure_clear), "clear", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_measure_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_measure_class = klass;
}
