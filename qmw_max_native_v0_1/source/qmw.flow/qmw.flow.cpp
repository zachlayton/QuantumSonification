#include "qmw/flow.hpp"

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

struct QmwFlowObject {
    t_object object;
    qmw::RevisionedFlowStore* store;
    void* frame_outlet;
    void* edge_outlet;
    void* diagnostics_outlet;
    void* status_outlet;
};

t_class* qmw_flow_class = nullptr;

void status(
    QmwFlowObject* object,
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

void output_active(QmwFlowObject* object, const char* status_selector)
{
    const auto* frame = object->store->active();
    if (frame == nullptr) {
        status(object, "empty", -1, "no_active_flow_frame");
        return;
    }

    const long revision = frame->revision();
    const auto& metadata = frame->metadata();
    t_atom metadata_atoms[18];
    atom_setlong(metadata_atoms, revision);
    atom_setlong(metadata_atoms + 1, static_cast<long>(frame->dimension()));
    atom_setlong(metadata_atoms + 2, static_cast<long>(frame->qubits()));
    atom_setsym(metadata_atoms + 3, gensym(metadata.basis_id.c_str()));
    atom_setsym(metadata_atoms + 4, gensym(metadata.basis_kind.c_str()));
    atom_setsym(metadata_atoms + 5, gensym(metadata.index_orientation.c_str()));
    atom_setsym(metadata_atoms + 6, gensym(metadata.bit_order.c_str()));
    atom_setsym(metadata_atoms + 7, gensym(metadata.energy_unit.c_str()));
    atom_setsym(metadata_atoms + 8, gensym(metadata.time_unit.c_str()));
    atom_setfloat(metadata_atoms + 9, frame->hbar());
    atom_setsym(metadata_atoms + 10, gensym(frame->hbar_unit().c_str()));
    atom_setsym(metadata_atoms + 11, gensym(frame->current_unit().c_str()));
    atom_setsym(metadata_atoms + 12, gensym(metadata.state_source_id.c_str()));
    atom_setsym(metadata_atoms + 13, gensym(metadata.hamiltonian_source_id.c_str()));
    atom_setsym(metadata_atoms + 14, gensym(metadata.provenance.c_str()));
    atom_setsym(metadata_atoms + 15, gensym("discrete_hamiltonian_basis_probability_current"));
    atom_setsym(metadata_atoms + 16, gensym("component_phases_local_gauge_dependent"));
    atom_setsym(metadata_atoms + 17, gensym("transport_product_local_rephasing_invariant"));
    outlet_anything(object->diagnostics_outlet, gensym("metadata"), 18, metadata_atoms);

    const auto& diagnostics = frame->diagnostics();
    t_atom metric_atoms[9];
    atom_setlong(metric_atoms, revision);
    atom_setfloat(metric_atoms + 1, diagnostics.hamiltonian_hermiticity_residual_fro);
    atom_setfloat(metric_atoms + 2, diagnostics.density_hermiticity_residual_fro);
    atom_setfloat(metric_atoms + 3, diagnostics.density_trace_error_abs);
    atom_setfloat(metric_atoms + 4, diagnostics.density_minimum_ldlt_pivot);
    atom_setfloat(metric_atoms + 5, diagnostics.current_antisymmetry_max_abs);
    atom_setfloat(metric_atoms + 6, diagnostics.continuity_residual_max_abs);
    atom_setfloat(metric_atoms + 7, diagnostics.population_derivative_imaginary_max_abs);
    atom_setfloat(metric_atoms + 8, diagnostics.total_population_derivative_abs);
    outlet_anything(object->diagnostics_outlet, gensym("metrics"), 9, metric_atoms);

    // Every off-diagonal ordered edge is emitted; no magnitude threshold turns
    // continuous current into an invented event stream.
    for (const auto& edge : frame->directed_edges()) {
        t_atom atoms[14];
        atom_setlong(atoms, revision);
        atom_setlong(atoms + 1, static_cast<long>(edge.source));
        atom_setlong(atoms + 2, static_cast<long>(edge.target));
        atom_setfloat(atoms + 3, edge.current);
        atom_setfloat(atoms + 4, edge.coupling_magnitude);
        atom_setfloat(atoms + 5, edge.coherence_magnitude);
        atom_setfloat(atoms + 6, edge.coupling_phase.radians);
        atom_setlong(atoms + 7, edge.coupling_phase.defined ? 1 : 0);
        atom_setfloat(atoms + 8, edge.coherence_phase.radians);
        atom_setlong(atoms + 9, edge.coherence_phase.defined ? 1 : 0);
        atom_setfloat(atoms + 10, edge.transport_phase.radians);
        atom_setlong(atoms + 11, edge.transport_phase.defined ? 1 : 0);
        atom_setlong(atoms + 12, edge.component_phases_local_gauge_dependent ? 1 : 0);
        atom_setlong(atoms + 13, edge.transport_phase_local_rephasing_invariant ? 1 : 0);
        outlet_anything(object->edge_outlet, gensym("edge"), 14, atoms);
    }

    std::vector<t_atom> derivative(frame->dimension() + 1);
    std::vector<t_atom> divergence(frame->dimension() + 1);
    atom_setlong(derivative.data(), revision);
    atom_setlong(divergence.data(), revision);
    for (std::size_t index = 0; index < frame->dimension(); ++index) {
        atom_setfloat(derivative.data() + index + 1, frame->population_derivative()[index]);
        atom_setfloat(divergence.data() + index + 1, frame->divergence()[index]);
    }
    outlet_anything(
        object->frame_outlet,
        gensym("population_derivative"),
        static_cast<long>(derivative.size()),
        derivative.data());
    outlet_anything(
        object->frame_outlet,
        gensym("divergence"),
        static_cast<long>(divergence.size()),
        divergence.data());

    for (std::size_t target = 0; target < frame->dimension(); ++target) {
        std::vector<t_atom> row(frame->dimension() + 2);
        atom_setlong(row.data(), revision);
        atom_setlong(row.data() + 1, static_cast<long>(target));
        for (std::size_t source = 0; source < frame->dimension(); ++source) {
            atom_setfloat(row.data() + source + 2, frame->current(target, source));
        }
        outlet_anything(
            object->frame_outlet,
            gensym("current_row"),
            static_cast<long>(row.size()),
            row.data());
    }
    status(object, status_selector, revision);
}

void stage_component(
    QmwFlowObject* object,
    const qmw::FlowPart part,
    const char* component,
    const long argc,
    const t_atom* argv)
{
    const auto count = object->store->element_count();
    if (argc != static_cast<long>(count + 1)) {
        object_error(
            &object->object,
            "%s requires revision plus %zu row-major values",
            component,
            count);
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
    values.reserve(count);
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
    const auto result = object->store->stage(part, revision, std::move(values));
    if (result.status == qmw::FlowStageStatus::rejected) {
        object_error(
            &object->object,
            "%s revision %ld rejected: %s",
            component,
            revision,
            result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        return;
    }
    status(object, "staged", revision, component);
}

#define QMW_FLOW_MATRIX_METHOD(function_name, input_part, label) \
    void function_name(QmwFlowObject* object, t_symbol*, const long argc, t_atom* argv) \
    { \
        stage_component(object, input_part, label, argc, argv); \
    }

QMW_FLOW_MATRIX_METHOD(
    qmw_flow_rho_real, qmw::FlowPart::density_real, "rho_real")
QMW_FLOW_MATRIX_METHOD(
    qmw_flow_rho_imag, qmw::FlowPart::density_imag, "rho_imag")
QMW_FLOW_MATRIX_METHOD(
    qmw_flow_hamiltonian_real,
    qmw::FlowPart::hamiltonian_real,
    "hamiltonian_real")
QMW_FLOW_MATRIX_METHOD(
    qmw_flow_hamiltonian_imag,
    qmw::FlowPart::hamiltonian_imag,
    "hamiltonian_imag")

#undef QMW_FLOW_MATRIX_METHOD

void qmw_flow_commit(
    QmwFlowObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    if (argc != 1 || atom_gettype(argv) != A_LONG) {
        object_error(&object->object, "commit requires exactly one integer revision");
        status(object, "rejected", -1, "invalid_commit_message");
        return;
    }
    const long revision = atom_getlong(argv);
    const auto result = object->store->commit(revision);
    if (result.status == qmw::FlowStageStatus::accepted) {
        output_active(object, "accepted");
        return;
    }
    object_error(
        &object->object,
        "flow revision %ld rejected: %s",
        revision,
        result.message.c_str());
    status(object, "rejected", revision, result.detail.c_str());
}

void qmw_flow_bang(QmwFlowObject* object)
{
    output_active(object, "active");
}

void qmw_flow_clear(QmwFlowObject* object)
{
    object->store->clear_candidate();
    status(object, "candidate_cleared", object->store->active_revision());
}

[[nodiscard]] bool optional_symbol(
    const long argc,
    const t_atom* argv,
    const long index,
    std::string& destination)
{
    if (argc <= index) {
        return true;
    }
    if (atom_gettype(argv + index) != A_SYM) {
        return false;
    }
    destination = atom_getsym(argv + index)->s_name;
    return true;
}

void qmw_flow_assist(QmwFlowObject*, void*, const long message, const long index, char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "rho/H real+imag; commit REVISION; bang; clear";
    } else {
        const char* const outlets[] = {
            "Current matrix, divergence, and population derivative frame",
            "Ordered source-to-target edge records and phases",
            "Continuity, conservation, units, basis, and provenance diagnostics",
            "Transaction status and validation errors",
        };
        label = index >= 0 && index < 4 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_flow_new(t_symbol*, const long argc, t_atom* argv)
{
    auto* object = static_cast<QmwFlowObject*>(object_alloc(qmw_flow_class));
    if (object == nullptr) {
        return nullptr;
    }
    object->store = nullptr;

    long qubits = 4;
    double hbar = 1.0;
    qmw::FlowMetadata metadata;
    if (argc > 0 && atom_gettype(argv) != A_LONG) {
        object_error(&object->object, "qubit count must be an integer");
        object_free(&object->object);
        return nullptr;
    }
    if (argc > 0) {
        qubits = atom_getlong(argv);
    }
    if (!optional_symbol(argc, argv, 1, metadata.energy_unit)
        || !optional_symbol(argc, argv, 2, metadata.time_unit)
        || (argc > 3 && !numeric_atom(argv + 3))
        || !optional_symbol(argc, argv, 4, metadata.basis_id)
        || !optional_symbol(argc, argv, 5, metadata.state_source_id)
        || !optional_symbol(argc, argv, 6, metadata.hamiltonian_source_id)
        || !optional_symbol(argc, argv, 7, metadata.provenance)
        || argc > 8 || qubits < 1 || qubits > 6) {
        object_error(
            &object->object,
            "usage: qmw.flow [qubits 1..6] [energy_unit] [time_unit] [hbar] [basis_id] [state_source] [hamiltonian_source] [provenance]");
        object_free(&object->object);
        return nullptr;
    }
    if (argc > 3) {
        hbar = atom_getfloat(argv + 3);
    }

    try {
        object->store = new qmw::RevisionedFlowStore(
            std::size_t {1} << qubits,
            hbar,
            std::move(metadata));
    } catch (const std::exception& error) {
        object_error(&object->object, "%s", error.what());
        object_free(&object->object);
        return nullptr;
    }

    // Max creates outlets from right to left.
    object->status_outlet = outlet_new(object, nullptr);
    object->diagnostics_outlet = outlet_new(object, nullptr);
    object->edge_outlet = outlet_new(object, nullptr);
    object->frame_outlet = outlet_new(object, nullptr);
    return object;
}

void qmw_flow_free(QmwFlowObject* object)
{
    delete object->store;
    object->store = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.flow",
        reinterpret_cast<method>(qmw_flow_new),
        reinterpret_cast<method>(qmw_flow_free),
        sizeof(QmwFlowObject),
        nullptr,
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_flow_rho_real), "rho_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_flow_rho_imag), "rho_imag", A_GIMME, 0);
    class_addmethod(
        klass,
        reinterpret_cast<method>(qmw_flow_hamiltonian_real),
        "hamiltonian_real",
        A_GIMME,
        0);
    class_addmethod(
        klass,
        reinterpret_cast<method>(qmw_flow_hamiltonian_imag),
        "hamiltonian_imag",
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_flow_commit), "commit", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_flow_bang), "bang", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_flow_clear), "clear", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_flow_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_flow_class = klass;
}
