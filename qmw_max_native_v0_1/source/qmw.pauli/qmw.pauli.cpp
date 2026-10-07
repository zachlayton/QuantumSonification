#include "qmw/pauli.hpp"

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

struct QmwPauliObject {
    t_object object;
    qmw::RevisionedPauliStore* store;
    void* matrix_outlet;
    void* diagnostics_outlet;
    void* status_outlet;
};

t_class* qmw_pauli_class = nullptr;

[[nodiscard]] const char* axis_name(const qmw::PauliAxis axis) noexcept
{
    switch (axis) {
    case qmw::PauliAxis::x: return "X";
    case qmw::PauliAxis::y: return "Y";
    case qmw::PauliAxis::z: return "Z";
    }
    return "invalid";
}

[[nodiscard]] bool parse_axis(const t_atom* atom, qmw::PauliAxis& axis)
{
    if (atom_gettype(atom) != A_SYM) {
        return false;
    }
    const auto parsed = qmw::pauli_axis_from_name(atom_getsym(atom)->s_name);
    if (!parsed.has_value()) {
        return false;
    }
    axis = *parsed;
    return true;
}

void status(
    QmwPauliObject* object,
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

void output_active(QmwPauliObject* object, const char* status_selector)
{
    const auto* snapshot = object->store->active();
    if (snapshot == nullptr) {
        status(object, "empty", -1);
        return;
    }
    const long revision = object->store->active_revision();
    const auto& values = snapshot->values();
    std::vector<t_atom> real(values.size() + 1);
    std::vector<t_atom> imag(values.size() + 1);
    atom_setlong(real.data(), revision);
    atom_setlong(imag.data(), revision);
    for (std::size_t index = 0; index < values.size(); ++index) {
        atom_setfloat(real.data() + index + 1, values[index].real());
        atom_setfloat(imag.data() + index + 1, values[index].imag());
    }

    status(object, "frame_begin", revision);
    outlet_anything(
        object->matrix_outlet,
        gensym("operator_real"),
        static_cast<long>(real.size()),
        real.data());
    outlet_anything(
        object->matrix_outlet,
        gensym("operator_imag"),
        static_cast<long>(imag.size()),
        imag.data());

    const auto& metadata = snapshot->metadata();
    t_atom metadata_atoms[11];
    atom_setlong(metadata_atoms, revision);
    atom_setlong(metadata_atoms + 1, static_cast<long>(snapshot->dimension()));
    atom_setlong(metadata_atoms + 2, static_cast<long>(snapshot->qubits()));
    atom_setlong(metadata_atoms + 3, static_cast<long>(snapshot->factors().size()));
    atom_setsym(metadata_atoms + 4, gensym(snapshot->label().c_str()));
    atom_setsym(metadata_atoms + 5, gensym("row_major"));
    atom_setsym(metadata_atoms + 6, gensym("q0_lsb"));
    atom_setsym(metadata_atoms + 7, gensym(metadata.operator_unit.c_str()));
    atom_setsym(metadata_atoms + 8, gensym(metadata.basis_id.c_str()));
    atom_setsym(metadata_atoms + 9, gensym(metadata.source_id.c_str()));
    atom_setsym(metadata_atoms + 10, gensym(metadata.provenance.c_str()));
    outlet_anything(object->diagnostics_outlet, gensym("metadata"), 11, metadata_atoms);

    for (std::size_t index = 0; index < snapshot->factors().size(); ++index) {
        const auto& factor = snapshot->factors()[index];
        t_atom factor_atoms[4];
        atom_setlong(factor_atoms, revision);
        atom_setlong(factor_atoms + 1, static_cast<long>(index));
        atom_setsym(factor_atoms + 2, gensym(axis_name(factor.axis)));
        atom_setlong(factor_atoms + 3, static_cast<long>(factor.qubit));
        outlet_anything(object->diagnostics_outlet, gensym("factor"), 4, factor_atoms);
    }

    const auto& diagnostics = snapshot->diagnostics();
    t_atom metric_atoms[6];
    atom_setlong(metric_atoms, revision);
    atom_setfloat(metric_atoms + 1, diagnostics.trace.real());
    atom_setfloat(metric_atoms + 2, diagnostics.trace.imag());
    atom_setfloat(metric_atoms + 3, diagnostics.frobenius_norm);
    atom_setfloat(metric_atoms + 4, diagnostics.hermiticity_residual_fro);
    atom_setfloat(metric_atoms + 5, diagnostics.unitarity_residual_fro);
    outlet_anything(object->diagnostics_outlet, gensym("metrics"), 6, metric_atoms);
    status(object, status_selector, revision);
}

void report_install(QmwPauliObject* object, const qmw::PauliInstallResult& result)
{
    if (result.status == qmw::PauliInstallStatus::accepted) {
        output_active(object, "accepted");
        return;
    }
    object_error(
        &object->object,
        "Pauli revision %ld rejected: %s",
        result.revision,
        result.message.c_str());
    status(object, "rejected", result.revision, result.detail.c_str());
}

void qmw_pauli_identity(QmwPauliObject* object, const t_atom_long revision)
{
    report_install(object, object->store->install_identity(revision));
}

void qmw_pauli_local(
    QmwPauliObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    if (argc != 3 || atom_gettype(argv) != A_LONG
        || atom_gettype(argv + 2) != A_LONG) {
        object_error(&object->object, "local requires REVISION X|Y|Z QUBIT");
        status(object, "rejected", -1, "invalid_local_message");
        return;
    }
    qmw::PauliAxis axis;
    if (!parse_axis(argv + 1, axis)) {
        object_error(&object->object, "local axis must be X, Y, or Z");
        status(object, "rejected", atom_getlong(argv), "invalid_axis");
        return;
    }
    const long qubit = atom_getlong(argv + 2);
    if (qubit < 0) {
        object_error(&object->object, "local qubit must be nonnegative");
        status(object, "rejected", atom_getlong(argv), "invalid_qubit");
        return;
    }
    report_install(
        object,
        object->store->install_product(
            atom_getlong(argv),
            {{axis, static_cast<std::size_t>(qubit)}}));
}

void qmw_pauli_product(
    QmwPauliObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    if (argc < 3 || argc % 2 == 0 || atom_gettype(argv) != A_LONG) {
        object_error(
            &object->object,
            "product requires REVISION AXIS QUBIT [AXIS QUBIT ...]");
        status(object, "rejected", -1, "invalid_product_message");
        return;
    }
    const long revision = atom_getlong(argv);
    std::vector<qmw::PauliFactor> factors;
    factors.reserve(static_cast<std::size_t>((argc - 1) / 2));
    for (long index = 1; index < argc; index += 2) {
        qmw::PauliAxis axis;
        if (!parse_axis(argv + index, axis)) {
            object_error(&object->object, "product axes must be X, Y, or Z");
            status(object, "rejected", revision, "invalid_axis");
            return;
        }
        if (atom_gettype(argv + index + 1) != A_LONG
            || atom_getlong(argv + index + 1) < 0) {
            object_error(&object->object, "product qubits must be nonnegative integers");
            status(object, "rejected", revision, "invalid_qubit");
            return;
        }
        factors.push_back({axis, static_cast<std::size_t>(atom_getlong(argv + index + 1))});
    }
    report_install(object, object->store->install_product(revision, std::move(factors)));
}

void qmw_pauli_bang(QmwPauliObject* object)
{
    output_active(object, "active");
}

[[nodiscard]] bool optional_symbol(
    const long argc,
    const t_atom* argv,
    const long index,
    std::string& destination)
{
    if (argc <= index) return true;
    if (atom_gettype(argv + index) != A_SYM) return false;
    destination = atom_getsym(argv + index)->s_name;
    return true;
}

void qmw_pauli_assist(
    QmwPauliObject*,
    void*,
    const long message,
    const long index,
    char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "Pauli source: identity REV; local REV AXIS QUBIT; product REV AXIS QUBIT ...; bang";
    } else {
        const char* const outlets[] = {
            "Operator matrix: operator_real/operator_imag with revision",
            "Pauli factors, basis/unit/source metadata, and exact residuals",
            "Frame and revision status: accepted/rejected/active/empty",
        };
        label = index >= 0 && index < 3 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_pauli_new(t_symbol*, const long argc, t_atom* argv)
{
    auto* object = static_cast<QmwPauliObject*>(object_alloc(qmw_pauli_class));
    if (object == nullptr) return nullptr;
    object->store = nullptr;

    long qubits = 4;
    if (argc > 0) {
        if (atom_gettype(argv) != A_LONG) {
            object_error(&object->object, "qubit count must be an integer");
            object_free(&object->object);
            return nullptr;
        }
        qubits = atom_getlong(argv);
    }
    if (qubits < 1 || qubits > 6 || argc > 4) {
        object_error(
            &object->object,
            "usage: qmw.pauli [qubits 1..6] [basis_id] [source_id] [provenance]");
        object_free(&object->object);
        return nullptr;
    }
    qmw::PauliMetadata metadata;
    if (!optional_symbol(argc, argv, 1, metadata.basis_id)
        || !optional_symbol(argc, argv, 2, metadata.source_id)
        || !optional_symbol(argc, argv, 3, metadata.provenance)) {
        object_error(&object->object, "basis, source, and provenance must be symbols");
        object_free(&object->object);
        return nullptr;
    }
    try {
        object->store = new qmw::RevisionedPauliStore(
            std::size_t {1} << qubits,
            std::move(metadata));
    } catch (const std::exception& error) {
        object_error(&object->object, "%s", error.what());
        object_free(&object->object);
        return nullptr;
    }

    // Max creates outlets from right to left.
    object->status_outlet = outlet_new(object, nullptr);
    object->diagnostics_outlet = outlet_new(object, nullptr);
    object->matrix_outlet = outlet_new(object, nullptr);
    return object;
}

void qmw_pauli_free(QmwPauliObject* object)
{
    delete object->store;
    object->store = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.pauli",
        reinterpret_cast<method>(qmw_pauli_new),
        reinterpret_cast<method>(qmw_pauli_free),
        sizeof(QmwPauliObject),
        nullptr,
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_pauli_identity), "identity", A_LONG, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_pauli_local), "local", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_pauli_product), "product", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_pauli_bang), "bang", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_pauli_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_pauli_class = klass;
}
