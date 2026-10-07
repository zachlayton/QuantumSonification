#include "qmw/transition.hpp"

#include "ext.h"
#include "ext_obex.h"

#include <cmath>
#include <cstddef>
#include <cstdio>
#include <exception>
#include <string>
#include <utility>
#include <vector>

namespace {

class TransitionAdapter final {
public:
    TransitionAdapter(
        const long qubits,
        qmw::TransitionContext context,
        qmw::TransitionUnits units,
        qmw::TransitionOperatorMetadata operator_metadata)
        : store_(
            std::size_t {1} << qubits,
            std::move(context),
            std::move(units),
            std::move(operator_metadata))
    {
    }

    [[nodiscard]] qmw::RevisionedTransitionStore& store() noexcept { return store_; }
    [[nodiscard]] const qmw::RevisionedTransitionStore& store() const noexcept { return store_; }

private:
    qmw::RevisionedTransitionStore store_;
};

struct QmwTransitionObject {
    t_object object;
    TransitionAdapter* adapter;
    void* edge_outlet;
    void* frame_outlet;
    void* status_outlet;
};

t_class* qmw_transition_class = nullptr;

void status(
    QmwTransitionObject* object,
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

void output_complex_matrix(
    QmwTransitionObject* object,
    const char* real_selector,
    const char* imag_selector,
    const long revision,
    const std::vector<qmw::Complex>& values)
{
    std::vector<t_atom> real(values.size() + 1);
    std::vector<t_atom> imag(values.size() + 1);
    atom_setlong(real.data(), revision);
    atom_setlong(imag.data(), revision);
    for (std::size_t index = 0; index < values.size(); ++index) {
        atom_setfloat(real.data() + index + 1, values[index].real());
        atom_setfloat(imag.data() + index + 1, values[index].imag());
    }
    outlet_anything(
        object->frame_outlet, gensym(real_selector),
        static_cast<long>(real.size()), real.data());
    outlet_anything(
        object->frame_outlet, gensym(imag_selector),
        static_cast<long>(imag.size()), imag.data());
}

void output_edge(
    QmwTransitionObject* object,
    const qmw::TransitionFrame& frame,
    const qmw::TransitionEdge& edge,
    const char* selector)
{
    t_atom atoms[24];
    atom_setlong(atoms, frame.context.revision);
    atom_setlong(atoms + 1, static_cast<long>(edge.source));
    atom_setlong(atoms + 2, static_cast<long>(edge.target));
    atom_setfloat(atoms + 3, edge.delta_E);
    atom_setfloat(atoms + 4, edge.omega);
    atom_setfloat(atoms + 5, edge.A_mn.real());
    atom_setfloat(atoms + 6, edge.A_mn.imag());
    atom_setfloat(atoms + 7, edge.magnitude);
    atom_setfloat(atoms + 8, edge.phase_rad.value_or(0.0));
    atom_setlong(atoms + 9, edge.phase_rad.has_value() ? 1 : 0);
    atom_setfloat(atoms + 10, edge.source_population);
    atom_setfloat(atoms + 11, edge.target_population);
    atom_setfloat(atoms + 12, edge.coherence_mn.real());
    atom_setfloat(atoms + 13, edge.coherence_mn.imag());
    atom_setfloat(atoms + 14, edge.coherence_nm.real());
    atom_setfloat(atoms + 15, edge.coherence_nm.imag());
    atom_setfloat(atoms + 16, edge.matrix_element_squared);
    atom_setfloat(atoms + 17, edge.diagnostic_activity);
    atom_setlong(atoms + 18, edge.diagonal ? 1 : 0);
    atom_setlong(atoms + 19, edge.zero_gap ? 1 : 0);
    atom_setlong(atoms + 20, edge.basis_dependent_degenerate_endpoint ? 1 : 0);
    atom_setsym(atoms + 21, gensym(frame.units.energy_unit.c_str()));
    const std::string omega_unit = "rad/" + frame.units.time_unit;
    atom_setsym(atoms + 22, gensym(omega_unit.c_str()));
    atom_setsym(atoms + 23, gensym(frame.units.operator_unit.c_str()));
    outlet_anything(object->edge_outlet, gensym(selector), 24, atoms);
}

void output_active(QmwTransitionObject* object, const char* status_selector)
{
    const auto* frame = object->adapter->store().active();
    if (frame == nullptr) {
        status(object, "empty", -1);
        return;
    }
    const long revision = frame->context.revision;

    std::vector<t_atom> energies(frame->energies.size() + 1);
    atom_setlong(energies.data(), revision);
    for (std::size_t index = 0; index < frame->energies.size(); ++index) {
        atom_setfloat(energies.data() + index + 1, frame->energies[index]);
    }
    outlet_anything(
        object->frame_outlet, gensym("energies"),
        static_cast<long>(energies.size()), energies.data());
    output_complex_matrix(
        object, "rho_energy_real", "rho_energy_imag",
        revision, frame->rho_in_energy_basis);
    output_complex_matrix(
        object, "operator_energy_real", "operator_energy_imag",
        revision, frame->operator_in_energy_basis);

    std::vector<t_atom> activity(frame->diagnostic_activity.size() + 3);
    atom_setlong(activity.data(), revision);
    atom_setsym(activity.data() + 1, gensym(frame->activity_name.c_str()));
    atom_setsym(activity.data() + 2, gensym(frame->activity_units.c_str()));
    for (std::size_t index = 0; index < frame->diagnostic_activity.size(); ++index) {
        atom_setfloat(activity.data() + index + 3, frame->diagnostic_activity[index]);
    }
    outlet_anything(
        object->frame_outlet, gensym("diagnostic_activity"),
        static_cast<long>(activity.size()), activity.data());

    for (const auto& group : frame->energy_degenerate_groups) {
        std::vector<t_atom> atoms(group.size() + 1);
        atom_setlong(atoms.data(), revision);
        for (std::size_t index = 0; index < group.size(); ++index) {
            atom_setlong(atoms.data() + index + 1, static_cast<long>(group[index]));
        }
        outlet_anything(
            object->frame_outlet, gensym("degenerate_group"),
            static_cast<long>(atoms.size()), atoms.data());
    }

    for (const auto& edge : frame->edges) {
        output_edge(object, *frame, edge, "edge");
    }
    for (const auto& edge : frame->transitions) {
        output_edge(object, *frame, edge, "transition");
    }

    const auto& operator_metadata = frame->operator_metadata;
    t_atom metadata[16];
    atom_setlong(metadata, revision);
    atom_setlong(metadata + 1, static_cast<long>(frame->dimension));
    atom_setfloat(metadata + 2, frame->context.time);
    atom_setfloat(metadata + 3, frame->context.dt);
    atom_setsym(metadata + 4, gensym(frame->context.basis_id.c_str()));
    atom_setsym(metadata + 5, gensym(frame->context.source_id.c_str()));
    atom_setsym(metadata + 6, gensym(frame->context.provenance.c_str()));
    atom_setsym(metadata + 7, gensym(frame->units.energy_unit.c_str()));
    atom_setsym(metadata + 8, gensym(frame->units.time_unit.c_str()));
    atom_setsym(metadata + 9, gensym(frame->units.operator_unit.c_str()));
    atom_setfloat(metadata + 10, frame->units.hbar);
    atom_setsym(metadata + 11, gensym(
        std::string(qmw::transition_operator_kind_name(operator_metadata.kind)).c_str()));
    atom_setsym(metadata + 12, gensym(operator_metadata.source_id.c_str()));
    atom_setsym(metadata + 13, gensym(operator_metadata.provenance.c_str()));
    atom_setsym(metadata + 14, gensym(frame->activity_name.c_str()));
    atom_setsym(metadata + 15, gensym("diagnostic_not_physical_rate"));
    outlet_anything(object->frame_outlet, gensym("metadata"), 16, metadata);

    const auto& diagnostics = frame->diagnostics;
    t_atom metrics[11];
    atom_setlong(metrics, revision);
    atom_setfloat(metrics + 1, diagnostics.density_hermiticity_residual_fro);
    atom_setfloat(metrics + 2, diagnostics.trace_error_abs);
    atom_setfloat(metrics + 3, diagnostics.hamiltonian_hermiticity_residual_fro);
    atom_setfloat(metrics + 4, diagnostics.operator_hermiticity_residual_fro);
    atom_setfloat(metrics + 5, diagnostics.hamiltonian_eigen_residual_fro);
    atom_setfloat(metrics + 6, diagnostics.hamiltonian_reconstruction_residual_fro);
    atom_setfloat(metrics + 7, diagnostics.operator_transform_residual_fro);
    atom_setfloat(metrics + 8, diagnostics.density_transform_hermiticity_residual_fro);
    atom_setlong(metrics + 9, static_cast<long>(diagnostics.jacobi_iterations));
    atom_setfloat(metrics + 10, diagnostics.jacobi_maximum_off_diagonal);
    outlet_anything(object->frame_outlet, gensym("metrics"), 11, metrics);
    status(object, status_selector, revision);
}

void stage_component(
    QmwTransitionObject* object,
    const qmw::TransitionInputPart part,
    const char* component_name,
    const long argc,
    const t_atom* argv)
{
    const auto required = static_cast<long>(object->adapter->store().element_count() + 1);
    if (argc != required) {
        object_error(
            &object->object, "%s requires revision plus %zu row-major values",
            component_name, object->adapter->store().element_count());
        status(object, "rejected", -1, "wrong_element_count");
        return;
    }
    if (atom_gettype(argv) != A_LONG) {
        object_error(&object->object, "%s revision must be an integer", component_name);
        status(object, "rejected", -1, "invalid_revision_atom");
        return;
    }
    const long revision = atom_getlong(argv);
    std::vector<double> values;
    values.reserve(object->adapter->store().element_count());
    for (long index = 1; index < argc; ++index) {
        const auto type = atom_gettype(argv + index);
        if (type != A_LONG && type != A_FLOAT) {
            object_error(&object->object, "%s contains a nonnumeric atom", component_name);
            status(object, "rejected", revision, "nonnumeric_atom");
            return;
        }
        const double value = atom_getfloat(argv + index);
        if (!std::isfinite(value)) {
            object_error(&object->object, "%s contains a non-finite value", component_name);
            status(object, "rejected", revision, "non_finite");
            return;
        }
        values.push_back(value);
    }
    const auto result = object->adapter->store().stage_matrix(
        part, revision, std::move(values));
    switch (result.status) {
    case qmw::TransitionStageStatus::staged:
        status(object, "staged", revision, component_name);
        break;
    case qmw::TransitionStageStatus::accepted:
        output_active(object, "accepted");
        break;
    case qmw::TransitionStageStatus::rejected:
        object_error(&object->object, "revision %ld rejected: %s", revision, result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        break;
    }
}

#define QMW_TRANSITION_MATRIX_METHOD(function_name, input_part, label) \
    void function_name(QmwTransitionObject* object, t_symbol*, const long argc, t_atom* argv) \
    { \
        stage_component(object, input_part, label, argc, argv); \
    }

QMW_TRANSITION_MATRIX_METHOD(
    qmw_transition_rho_real, qmw::TransitionInputPart::rho_real, "rho_real")
QMW_TRANSITION_MATRIX_METHOD(
    qmw_transition_rho_imag, qmw::TransitionInputPart::rho_imag, "rho_imag")
QMW_TRANSITION_MATRIX_METHOD(
    qmw_transition_hamiltonian_real,
    qmw::TransitionInputPart::hamiltonian_real, "hamiltonian_real")
QMW_TRANSITION_MATRIX_METHOD(
    qmw_transition_hamiltonian_imag,
    qmw::TransitionInputPart::hamiltonian_imag, "hamiltonian_imag")
QMW_TRANSITION_MATRIX_METHOD(
    qmw_transition_operator_real, qmw::TransitionInputPart::operator_real, "operator_real")
QMW_TRANSITION_MATRIX_METHOD(
    qmw_transition_operator_imag, qmw::TransitionInputPart::operator_imag, "operator_imag")

#undef QMW_TRANSITION_MATRIX_METHOD

void qmw_transition_context(
    QmwTransitionObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    if (argc != 3 || atom_gettype(argv) != A_LONG
        || (atom_gettype(argv + 1) != A_LONG && atom_gettype(argv + 1) != A_FLOAT)
        || (atom_gettype(argv + 2) != A_LONG && atom_gettype(argv + 2) != A_FLOAT)) {
        object_error(&object->object, "context requires integer revision, numeric time, numeric dt");
        status(object, "rejected", -1, "invalid_context_atoms");
        return;
    }
    const long revision = atom_getlong(argv);
    const auto result = object->adapter->store().stage_context(
        revision, atom_getfloat(argv + 1), atom_getfloat(argv + 2));
    switch (result.status) {
    case qmw::TransitionStageStatus::staged:
        status(object, "staged", revision, "context");
        break;
    case qmw::TransitionStageStatus::accepted:
        output_active(object, "accepted");
        break;
    case qmw::TransitionStageStatus::rejected:
        object_error(&object->object, "revision %ld rejected: %s", revision, result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        break;
    }
}

void qmw_transition_bang(QmwTransitionObject* object)
{
    output_active(object, "active");
}

void qmw_transition_clear(QmwTransitionObject* object)
{
    object->adapter->store().clear_candidate();
    status(object, "candidate_cleared", object->adapter->store().active_revision());
}

[[nodiscard]] bool symbol_argument(
    const long argc,
    const t_atom* argv,
    const long index,
    std::string& target)
{
    if (argc <= index) {
        return true;
    }
    if (atom_gettype(argv + index) != A_SYM) {
        return false;
    }
    target = atom_getsym(argv + index)->s_name;
    return true;
}

void qmw_transition_assist(QmwTransitionObject*, void*, const long message, const long index, char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "rho/H/operator real+imag transactions; context; bang; clear";
    } else {
        const char* const outlets[] = {
            "Transition edges: signed gaps, omega, elements, populations/coherences",
            "Eigensystem frame, diagnostic activity, metadata, and metrics",
            "Revision transaction status and errors",
        };
        label = index >= 0 && index < 3 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_transition_new(t_symbol*, const long argc, t_atom* argv)
{
    auto* object = static_cast<QmwTransitionObject*>(object_alloc(qmw_transition_class));
    if (object == nullptr) {
        return nullptr;
    }
    object->adapter = nullptr;

    long qubits = 4;
    if (argc > 0) {
        if (atom_gettype(argv) != A_LONG) {
            object_error(&object->object, "qubit count must be an integer");
            object_free(&object->object);
            return nullptr;
        }
        qubits = atom_getlong(argv);
    }
    qmw::TransitionOperatorKind kind = qmw::TransitionOperatorKind::coupling;
    if (argc > 1) {
        if (atom_gettype(argv + 1) != A_SYM) {
            object_error(&object->object, "operator kind must be coupling or observable");
            object_free(&object->object);
            return nullptr;
        }
        const std::string name = atom_getsym(argv + 1)->s_name;
        if (name == "observable") {
            kind = qmw::TransitionOperatorKind::observable;
        } else if (name != "coupling") {
            object_error(&object->object, "operator kind must be coupling or observable");
            object_free(&object->object);
            return nullptr;
        }
    }
    double hbar = 1.0;
    if (argc > 2) {
        const auto type = atom_gettype(argv + 2);
        if (type != A_LONG && type != A_FLOAT) {
            object_error(&object->object, "hbar must be numeric");
            object_free(&object->object);
            return nullptr;
        }
        hbar = atom_getfloat(argv + 2);
    }
    if (qubits < 1 || qubits > 6 || argc > 11) {
        object_error(
            &object->object,
            "usage: qmw.transition [qubits 1..6] [coupling|observable] [hbar] "
            "[energy_unit] [time_unit] [operator_unit] [basis_id] [source_id] "
            "[provenance] [operator_source] [operator_provenance]");
        object_free(&object->object);
        return nullptr;
    }

    qmw::TransitionUnits units;
    units.hbar = hbar;
    qmw::TransitionContext context;
    context.revision = -1;
    qmw::TransitionOperatorMetadata operator_metadata;
    operator_metadata.revision = -1;
    operator_metadata.kind = kind;
    if (!symbol_argument(argc, argv, 3, units.energy_unit)
        || !symbol_argument(argc, argv, 4, units.time_unit)
        || !symbol_argument(argc, argv, 5, units.operator_unit)
        || !symbol_argument(argc, argv, 6, context.basis_id)
        || !symbol_argument(argc, argv, 7, context.source_id)
        || !symbol_argument(argc, argv, 8, context.provenance)
        || !symbol_argument(argc, argv, 9, operator_metadata.source_id)
        || !symbol_argument(argc, argv, 10, operator_metadata.provenance)) {
        object_error(&object->object, "unit and provenance arguments must be symbols");
        object_free(&object->object);
        return nullptr;
    }
    context.time_unit = units.time_unit;
    operator_metadata.basis_id = context.basis_id;
    operator_metadata.unit = units.operator_unit;

    try {
        object->adapter = new TransitionAdapter(
            qubits, std::move(context), std::move(units), std::move(operator_metadata));
    } catch (const std::exception& error) {
        object_error(&object->object, "could not create transition observer: %s", error.what());
        object_free(&object->object);
        return nullptr;
    }
    // Max creates multiple outlets from right to left.
    object->status_outlet = outlet_new(object, nullptr);
    object->frame_outlet = outlet_new(object, nullptr);
    object->edge_outlet = outlet_new(object, nullptr);
    return object;
}

void qmw_transition_free(QmwTransitionObject* object)
{
    delete object->adapter;
    object->adapter = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.transition",
        reinterpret_cast<method>(qmw_transition_new),
        reinterpret_cast<method>(qmw_transition_free),
        sizeof(QmwTransitionObject),
        nullptr,
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_rho_real),
                    "rho_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_rho_imag),
                    "rho_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_hamiltonian_real),
                    "hamiltonian_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_hamiltonian_imag),
                    "hamiltonian_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_operator_real),
                    "operator_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_operator_imag),
                    "operator_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_operator_real),
                    "coupling_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_operator_imag),
                    "coupling_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_operator_real),
                    "observable_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_operator_imag),
                    "observable_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_context),
                    "context", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_bang), "bang", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_clear), "clear", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_transition_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_transition_class = klass;
}
