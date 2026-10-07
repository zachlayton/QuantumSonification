#include "qmw/qmm.hpp"

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

class QmmAdapter final {
public:
    QmmAdapter(
        const long qubits,
        const double hbar,
        qmw::QmmMetadata metadata)
        : store_(std::size_t {1} << qubits, hbar, std::move(metadata))
    {
    }

    [[nodiscard]] qmw::RevisionedQmmStore& store() noexcept { return store_; }
    [[nodiscard]] const qmw::RevisionedQmmStore& store() const noexcept { return store_; }

private:
    qmw::RevisionedQmmStore store_;
};

struct QmwQmmObject {
    t_object object;
    QmmAdapter* adapter;
    void* result_outlet;
    void* diagnostics_outlet;
    void* status_outlet;
};

t_class* qmw_qmm_class = nullptr;

void status(
    QmwQmmObject* object,
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

void output_matrix(
    void* outlet,
    const char* real_selector,
    const char* imag_selector,
    const long revision,
    const qmw::QmmMatrix& matrix)
{
    const auto& values = matrix.values();
    std::vector<t_atom> real(values.size() + 1);
    std::vector<t_atom> imag(values.size() + 1);
    atom_setlong(real.data(), revision);
    atom_setlong(imag.data(), revision);
    for (std::size_t index = 0; index < values.size(); ++index) {
        atom_setfloat(real.data() + index + 1, values[index].real());
        atom_setfloat(imag.data() + index + 1, values[index].imag());
    }
    outlet_anything(outlet, gensym(real_selector), static_cast<long>(real.size()), real.data());
    outlet_anything(outlet, gensym(imag_selector), static_cast<long>(imag.size()), imag.data());
}

void output_active(QmwQmmObject* object, const char* status_selector)
{
    const auto* snapshot = object->adapter->store().active();
    if (snapshot == nullptr) {
        status(object, "empty", -1);
        return;
    }

    const long revision = snapshot->revision();
    output_matrix(
        object->result_outlet,
        "commutator_real",
        "commutator_imag",
        revision,
        snapshot->commutator());
    output_matrix(
        object->result_outlet,
        "derivative_real",
        "derivative_imag",
        revision,
        snapshot->derivative());

    const auto expectation = snapshot->expectation_derivative();
    t_atom expectation_atoms[3];
    atom_setlong(expectation_atoms, revision);
    atom_setfloat(expectation_atoms + 1, expectation.real());
    atom_setfloat(expectation_atoms + 2, expectation.imag());
    outlet_anything(
        object->result_outlet,
        gensym("expectation_derivative"),
        3,
        expectation_atoms);

    const auto& metadata = snapshot->metadata();
    t_atom metadata_atoms[13];
    atom_setlong(metadata_atoms, revision);
    atom_setlong(metadata_atoms + 1, static_cast<long>(snapshot->dimension()));
    atom_setlong(metadata_atoms + 2, static_cast<long>(snapshot->qubits()));
    atom_setfloat(metadata_atoms + 3, snapshot->hbar());
    atom_setsym(metadata_atoms + 4, gensym(snapshot->hbar_unit().c_str()));
    atom_setsym(metadata_atoms + 5, gensym(metadata.energy_unit.c_str()));
    atom_setsym(metadata_atoms + 6, gensym(metadata.time_unit.c_str()));
    atom_setsym(metadata_atoms + 7, gensym(metadata.operator_unit.c_str()));
    atom_setsym(metadata_atoms + 8, gensym(snapshot->derivative_unit().c_str()));
    atom_setsym(metadata_atoms + 9, gensym(metadata.basis_id.c_str()));
    atom_setsym(metadata_atoms + 10, gensym(metadata.source_id.c_str()));
    atom_setsym(metadata_atoms + 11, gensym(metadata.provenance.c_str()));
    atom_setlong(metadata_atoms + 12, snapshot->has_explicit_partial() ? 1 : 0);
    outlet_anything(object->diagnostics_outlet, gensym("metadata"), 13, metadata_atoms);

    const auto& diagnostics = snapshot->diagnostics();
    t_atom metric_atoms[12];
    atom_setlong(metric_atoms, revision);
    atom_setfloat(metric_atoms + 1, diagnostics.hamiltonian_hermiticity_residual_fro);
    atom_setfloat(metric_atoms + 2, diagnostics.observable_hermiticity_residual_fro);
    atom_setfloat(metric_atoms + 3, diagnostics.partial_hermiticity_residual_fro);
    atom_setfloat(metric_atoms + 4, diagnostics.commutator_frobenius_norm);
    atom_setfloat(metric_atoms + 5, diagnostics.commutator_antihermiticity_residual_fro);
    atom_setfloat(metric_atoms + 6, diagnostics.derivative_hermiticity_residual_fro);
    atom_setfloat(metric_atoms + 7, diagnostics.density_trace.real());
    atom_setfloat(metric_atoms + 8, diagnostics.density_trace.imag());
    atom_setfloat(metric_atoms + 9, diagnostics.density_minimum_ldlt_pivot);
    atom_setfloat(metric_atoms + 10, diagnostics.expectation_imaginary_residual);
    atom_setsym(metric_atoms + 11, gensym("diagnostic_not_physical_rate"));
    outlet_anything(object->diagnostics_outlet, gensym("metrics"), 12, metric_atoms);
    status(object, status_selector, revision);
}

void stage_component(
    QmwQmmObject* object,
    const qmw::QmmPart part,
    const char* component,
    const long argc,
    const t_atom* argv)
{
    const auto count = object->adapter->store().element_count();
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

    const auto result = object->adapter->store().stage(part, revision, std::move(values));
    if (result.status == qmw::QmmStageStatus::rejected) {
        object_error(&object->object, "%s revision %ld rejected: %s", component, revision, result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        return;
    }
    status(object, "staged", revision, component);
}

#define QMW_QMM_STAGE_METHOD(function_name, part_name, component_name)                       \
    void function_name(QmwQmmObject* object, t_symbol*, const long argc, t_atom* argv)       \
    {                                                                                         \
        stage_component(object, qmw::QmmPart::part_name, component_name, argc, argv);         \
    }

QMW_QMM_STAGE_METHOD(qmw_qmm_hamiltonian_real, hamiltonian_real, "hamiltonian_real")
QMW_QMM_STAGE_METHOD(qmw_qmm_hamiltonian_imag, hamiltonian_imag, "hamiltonian_imag")
QMW_QMM_STAGE_METHOD(qmw_qmm_rho_real, density_real, "rho_real")
QMW_QMM_STAGE_METHOD(qmw_qmm_rho_imag, density_imag, "rho_imag")
QMW_QMM_STAGE_METHOD(qmw_qmm_operator_real, observable_real, "operator_real")
QMW_QMM_STAGE_METHOD(qmw_qmm_operator_imag, observable_imag, "operator_imag")
QMW_QMM_STAGE_METHOD(qmw_qmm_partial_real, partial_real, "partial_real")
QMW_QMM_STAGE_METHOD(qmw_qmm_partial_imag, partial_imag, "partial_imag")

#undef QMW_QMM_STAGE_METHOD

void qmw_qmm_commit(QmwQmmObject* object, t_symbol*, const long argc, t_atom* argv)
{
    if (argc != 1 || atom_gettype(argv) != A_LONG) {
        object_error(&object->object, "usage: commit revision");
        status(object, "rejected", -1, "invalid_commit_message");
        return;
    }
    const long revision = atom_getlong(argv);
    const auto result = object->adapter->store().commit(revision);
    if (result.status == qmw::QmmStageStatus::accepted) {
        output_active(object, "accepted");
        return;
    }
    object_error(&object->object, "revision %ld rejected: %s", revision, result.message.c_str());
    status(object, "rejected", revision, result.detail.c_str());
}

void qmw_qmm_bang(QmwQmmObject* object)
{
    output_active(object, "active");
}

void qmw_qmm_clear(QmwQmmObject* object)
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

void qmw_qmm_assist(QmwQmmObject*, void*, const long message, const long index, char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "H/rho/operator/partial real+imag; commit REVISION; bang; clear";
    } else {
        const char* const outlets[] = {
            "Commutator, Heisenberg operator derivative, and expectation derivative",
            "Units, provenance, and residual diagnostics",
            "Transaction status and validation errors",
        };
        label = index >= 0 && index < 3 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_qmm_new(t_symbol*, const long argc, t_atom* argv)
{
    auto* object = static_cast<QmwQmmObject*>(object_alloc(qmw_qmm_class));
    if (object == nullptr) {
        return nullptr;
    }
    object->adapter = nullptr;

    long qubits = 4;
    double hbar = 1.0;
    if (argc > 0 && atom_gettype(argv) != A_LONG) {
        object_error(&object->object, "qubit count must be an integer");
        object_free(&object->object);
        return nullptr;
    }
    if (argc > 0) {
        qubits = atom_getlong(argv);
    }
    if (argc > 1 && !numeric_atom(argv + 1)) {
        object_error(&object->object, "hbar must be numeric");
        object_free(&object->object);
        return nullptr;
    }
    if (argc > 1) {
        hbar = atom_getfloat(argv + 1);
    }
    if (argc > 8 || qubits < 1 || qubits > 6 || !std::isfinite(hbar) || !(hbar > 0.0)) {
        object_error(
            &object->object,
            "usage: qmw.qmm [qubits 1..6] [hbar] [energy_unit] [time_unit] [operator_unit] [basis_id] [source_id] [provenance]");
        object_free(&object->object);
        return nullptr;
    }

    qmw::QmmMetadata metadata;
    metadata.source_id = "qmw.qmm-input";
    metadata.provenance = "revision-locked-Max-transaction";
    if (!optional_symbol(argc, argv, 2, metadata.energy_unit)
        || !optional_symbol(argc, argv, 3, metadata.time_unit)
        || !optional_symbol(argc, argv, 4, metadata.operator_unit)
        || !optional_symbol(argc, argv, 5, metadata.basis_id)
        || !optional_symbol(argc, argv, 6, metadata.source_id)
        || !optional_symbol(argc, argv, 7, metadata.provenance)) {
        object_error(&object->object, "qmw.qmm unit and provenance arguments must be symbols");
        object_free(&object->object);
        return nullptr;
    }

    try {
        object->adapter = new QmmAdapter(qubits, hbar, std::move(metadata));
    } catch (const std::exception& error) {
        object_error(&object->object, "%s", error.what());
        object_free(&object->object);
        return nullptr;
    }
    // Max creates multiple outlets from right to left.
    object->status_outlet = outlet_new(object, nullptr);
    object->diagnostics_outlet = outlet_new(object, nullptr);
    object->result_outlet = outlet_new(object, nullptr);
    return object;
}

void qmw_qmm_free(QmwQmmObject* object)
{
    delete object->adapter;
    object->adapter = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.qmm",
        reinterpret_cast<method>(qmw_qmm_new),
        reinterpret_cast<method>(qmw_qmm_free),
        sizeof(QmwQmmObject),
        nullptr,
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_hamiltonian_real), "hamiltonian_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_hamiltonian_imag), "hamiltonian_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_rho_real), "rho_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_rho_imag), "rho_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_operator_real), "operator_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_operator_imag), "operator_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_partial_real), "partial_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_partial_imag), "partial_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_commit), "commit", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_bang), "bang", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_clear), "clear", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_qmm_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_qmm_class = klass;
}
