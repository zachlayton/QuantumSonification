#include "qmw/hamiltonian.hpp"

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

class HamiltonianAdapter final {
public:
    HamiltonianAdapter(const long qubits, qmw::HamiltonianMetadata metadata)
        : store_(std::size_t {1} << qubits, std::move(metadata))
    {
    }

    [[nodiscard]] qmw::RevisionedHamiltonianStore& store() noexcept { return store_; }
    [[nodiscard]] const qmw::RevisionedHamiltonianStore& store() const noexcept { return store_; }

private:
    qmw::RevisionedHamiltonianStore store_;
};

struct QmwHamiltonianObject {
    t_object object;
    HamiltonianAdapter* adapter;
    void* matrix_outlet;
    void* diagnostics_outlet;
    void* status_outlet;
};

t_class* qmw_hamiltonian_class = nullptr;

void status(
    QmwHamiltonianObject* object,
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

void output_active(QmwHamiltonianObject* object)
{
    const auto* snapshot = object->adapter->store().active();
    if (snapshot == nullptr) {
        status(object, "empty", -1);
        return;
    }

    const auto revision = object->adapter->store().active_revision();
    const auto& values = snapshot->values();
    std::vector<t_atom> real(values.size() + 1);
    std::vector<t_atom> imag(values.size() + 1);
    atom_setlong(real.data(), revision);
    atom_setlong(imag.data(), revision);
    for (std::size_t index = 0; index < values.size(); ++index) {
        atom_setfloat(real.data() + index + 1, values[index].real());
        atom_setfloat(imag.data() + index + 1, values[index].imag());
    }

    const auto& metadata = snapshot->metadata();
    t_atom metadata_atoms[8];
    atom_setlong(metadata_atoms, revision);
    atom_setlong(metadata_atoms + 1, static_cast<long>(snapshot->dimension()));
    atom_setlong(metadata_atoms + 2, static_cast<long>(snapshot->qubits()));
    atom_setsym(metadata_atoms + 3, gensym("row_major"));
    atom_setsym(metadata_atoms + 4, gensym(metadata.energy_unit.c_str()));
    atom_setsym(metadata_atoms + 5, gensym(metadata.basis_id.c_str()));
    atom_setsym(metadata_atoms + 6, gensym(metadata.source_id.c_str()));
    atom_setsym(metadata_atoms + 7, gensym(metadata.provenance.c_str()));

    const auto& diagnostics = snapshot->diagnostics();
    t_atom metric_atoms[8];
    atom_setlong(metric_atoms, revision);
    atom_setlong(metric_atoms + 1, static_cast<long>(snapshot->dimension()));
    atom_setfloat(metric_atoms + 2, diagnostics.trace.real());
    atom_setfloat(metric_atoms + 3, diagnostics.trace.imag());
    atom_setfloat(metric_atoms + 4, diagnostics.frobenius_norm);
    atom_setfloat(metric_atoms + 5, diagnostics.maximum_absolute_element);
    atom_setfloat(metric_atoms + 6, diagnostics.hermiticity_residual_fro);
    atom_setfloat(metric_atoms + 7, diagnostics.relative_hermiticity_residual);

    // Publish the complete immutable matrix pair before metadata, diagnostics,
    // and final acceptance. Downstream objects still gate on the revision.
    outlet_anything(
        object->matrix_outlet,
        gensym("hamiltonian_real"),
        static_cast<long>(real.size()),
        real.data());
    outlet_anything(
        object->matrix_outlet,
        gensym("hamiltonian_imag"),
        static_cast<long>(imag.size()),
        imag.data());
    outlet_anything(object->diagnostics_outlet, gensym("metadata"), 8, metadata_atoms);
    outlet_anything(object->diagnostics_outlet, gensym("metrics"), 8, metric_atoms);
    status(object, "accepted", revision);
}

void stage_component(
    QmwHamiltonianObject* object,
    const qmw::HamiltonianPart part,
    const char* component_name,
    const long argc,
    const t_atom* argv)
{
    const auto required = static_cast<long>(object->adapter->store().element_count() + 1);
    if (argc != required) {
        object_error(
            &object->object,
            "%s requires revision plus %zu row-major values",
            component_name,
            object->adapter->store().element_count());
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

    const auto result = object->adapter->store().stage(part, revision, std::move(values));
    switch (result.status) {
    case qmw::HamiltonianStageStatus::staged:
        status(object, "staged", revision, result.detail.c_str());
        break;
    case qmw::HamiltonianStageStatus::accepted:
        output_active(object);
        break;
    case qmw::HamiltonianStageStatus::rejected:
        object_error(&object->object, "revision %ld rejected: %s", revision, result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        break;
    }
}

void qmw_hamiltonian_real(
    QmwHamiltonianObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    stage_component(object, qmw::HamiltonianPart::real, "real", argc, argv);
}

void qmw_hamiltonian_imag(
    QmwHamiltonianObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    stage_component(object, qmw::HamiltonianPart::imag, "imag", argc, argv);
}

void qmw_hamiltonian_bang(QmwHamiltonianObject* object)
{
    output_active(object);
}

void qmw_hamiltonian_clear(QmwHamiltonianObject* object)
{
    object->adapter->store().clear_candidate();
    status(object, "candidate_cleared", object->adapter->store().active_revision());
}

[[nodiscard]] bool optional_symbol(
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

void qmw_hamiltonian_assist(QmwHamiltonianObject*, void*, const long message, const long index, char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "Hamiltonian transaction: real/imag REVISION MATRIX; bang; clear";
    } else {
        const char* const outlets[] = {
            "Accepted Hamiltonian: hamiltonian_real/hamiltonian_imag",
            "Hamiltonian metadata and Hermiticity metrics",
            "Transaction status: staged/accepted/rejected/empty",
        };
        label = index >= 0 && index < 3 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_hamiltonian_new(t_symbol*, const long argc, t_atom* argv)
{
    auto* object = static_cast<QmwHamiltonianObject*>(object_alloc(qmw_hamiltonian_class));
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
    if (qubits < 1 || qubits > 6 || argc > 5) {
        object_error(
            &object->object,
            "usage: qmw.hamiltonian [qubits 1..6] [energy_unit] [basis_id] [source_id] [provenance]");
        object_free(&object->object);
        return nullptr;
    }

    qmw::HamiltonianMetadata metadata;
    if (!optional_symbol(argc, argv, 1, metadata.energy_unit)
        || !optional_symbol(argc, argv, 2, metadata.basis_id)
        || !optional_symbol(argc, argv, 3, metadata.source_id)
        || !optional_symbol(argc, argv, 4, metadata.provenance)) {
        object_error(&object->object, "Hamiltonian metadata arguments must be symbols");
        object_free(&object->object);
        return nullptr;
    }

    try {
        object->adapter = new HamiltonianAdapter(qubits, std::move(metadata));
    } catch (const std::exception& error) {
        object_error(&object->object, "%s", error.what());
        object_free(&object->object);
        return nullptr;
    }

    // Max creates multiple outlets from right to left.
    object->status_outlet = outlet_new(object, nullptr);
    object->diagnostics_outlet = outlet_new(object, nullptr);
    object->matrix_outlet = outlet_new(object, nullptr);
    return object;
}

void qmw_hamiltonian_free(QmwHamiltonianObject* object)
{
    delete object->adapter;
    object->adapter = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.hamiltonian",
        reinterpret_cast<method>(qmw_hamiltonian_new),
        reinterpret_cast<method>(qmw_hamiltonian_free),
        sizeof(QmwHamiltonianObject),
        nullptr,
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_hamiltonian_real), "real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_hamiltonian_imag), "imag", A_GIMME, 0);
    class_addmethod(
        klass,
        reinterpret_cast<method>(qmw_hamiltonian_real),
        "hamiltonian_real",
        A_GIMME,
        0);
    class_addmethod(
        klass,
        reinterpret_cast<method>(qmw_hamiltonian_imag),
        "hamiltonian_imag",
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_hamiltonian_bang), "bang", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_hamiltonian_clear), "clear", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_hamiltonian_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_hamiltonian_class = klass;
}
