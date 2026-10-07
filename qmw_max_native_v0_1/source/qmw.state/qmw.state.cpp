#include "qmw/revisioned_state.hpp"

#include "ext.h"
#include "ext_obex.h"

#include <cmath>
#include <cstddef>
#include <cstdio>
#include <exception>
#include <vector>

namespace {

class StateAdapter final {
public:
    explicit StateAdapter(const long qubits)
        : store_(std::size_t {1} << qubits)
    {
    }

    [[nodiscard]] qmw::RevisionedStateStore& store() noexcept { return store_; }
    [[nodiscard]] const qmw::RevisionedStateStore& store() const noexcept { return store_; }

private:
    qmw::RevisionedStateStore store_;
};

struct QmwStateObject {
    t_object object;
    StateAdapter* adapter;
    void* rho_outlet;
    void* metrics_outlet;
    void* status_outlet;
};

t_class* qmw_state_class = nullptr;

void status(QmwStateObject* object, const char* selector, const long revision, const char* detail = nullptr)
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

void output_active(QmwStateObject* object)
{
    const auto* state = object->adapter->store().active();
    if (state == nullptr) {
        status(object, "empty", -1);
        return;
    }

    const auto revision = object->adapter->store().active_revision();
    const auto& values = state->values();
    std::vector<t_atom> real(values.size() + 1);
    std::vector<t_atom> imag(values.size() + 1);
    atom_setlong(real.data(), revision);
    atom_setlong(imag.data(), revision);
    for (std::size_t index = 0; index < values.size(); ++index) {
        atom_setfloat(real.data() + index + 1, values[index].real());
        atom_setfloat(imag.data() + index + 1, values[index].imag());
    }

    const auto& diagnostics = state->diagnostics();
    t_atom metrics[7];
    atom_setlong(metrics, revision);
    atom_setlong(metrics + 1, static_cast<long>(state->dimension()));
    atom_setfloat(metrics + 2, diagnostics.trace.real());
    atom_setfloat(metrics + 3, diagnostics.trace.imag());
    atom_setfloat(metrics + 4, diagnostics.purity);
    atom_setfloat(metrics + 5, diagnostics.hermiticity_residual);
    atom_setfloat(metrics + 6, diagnostics.minimum_ldlt_pivot);

    // Complete state first, derived diagnostics second, acceptance last.
    outlet_anything(object->rho_outlet, gensym("rho_real"), static_cast<long>(real.size()), real.data());
    outlet_anything(object->rho_outlet, gensym("rho_imag"), static_cast<long>(imag.size()), imag.data());
    outlet_anything(object->metrics_outlet, gensym("metrics"), 7, metrics);
    status(object, "accepted", revision);
}

void stage_component(
    QmwStateObject* object,
    const qmw::StatePart part,
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
    case qmw::StageStatus::staged:
        status(object, "staged", revision, result.detail.c_str());
        break;
    case qmw::StageStatus::accepted:
        output_active(object);
        break;
    case qmw::StageStatus::rejected:
        object_error(&object->object, "revision %ld rejected: %s", revision, result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        break;
    }
}

void qmw_state_real(QmwStateObject* object, t_symbol*, const long argc, t_atom* argv)
{
    stage_component(object, qmw::StatePart::real, "real", argc, argv);
}

void qmw_state_imag(QmwStateObject* object, t_symbol*, const long argc, t_atom* argv)
{
    stage_component(object, qmw::StatePart::imag, "imag", argc, argv);
}

void qmw_state_bang(QmwStateObject* object)
{
    output_active(object);
}

void qmw_state_clear(QmwStateObject* object)
{
    object->adapter->store().clear_candidate();
    status(object, "candidate_cleared", object->adapter->store().active_revision());
}

void qmw_state_assist(QmwStateObject*, void*, const long message, const long index, char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "Density transaction: real/imag REVISION MATRIX; bang; clear";
    } else {
        const char* const outlets[] = {
            "Accepted density matrix: rho_real/rho_imag with revision",
            "Density admission metrics",
            "Transaction status: staged/accepted/rejected/empty",
        };
        label = index >= 0 && index < 3 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_state_new(const long qubits)
{
    auto* object = static_cast<QmwStateObject*>(object_alloc(qmw_state_class));
    if (object == nullptr) {
        return nullptr;
    }
    object->adapter = nullptr;

    const long checked_qubits = qubits == 0 ? 4 : qubits;
    if (checked_qubits < 1 || checked_qubits > 6) {
        object_error(&object->object, "qubit count must be in [1, 6]");
        object_free(&object->object);
        return nullptr;
    }

    try {
        object->adapter = new StateAdapter(checked_qubits);
    } catch (const std::exception& error) {
        object_error(&object->object, "could not initialize state authority: %s", error.what());
        object_free(&object->object);
        return nullptr;
    } catch (...) {
        object_error(&object->object, "could not initialize state authority");
        object_free(&object->object);
        return nullptr;
    }
    // Max creates multiple outlets from right to left.
    object->status_outlet = outlet_new(object, nullptr);
    object->metrics_outlet = outlet_new(object, nullptr);
    object->rho_outlet = outlet_new(object, nullptr);
    return object;
}

void qmw_state_free(QmwStateObject* object)
{
    delete object->adapter;
    object->adapter = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.state",
        reinterpret_cast<method>(qmw_state_new),
        reinterpret_cast<method>(qmw_state_free),
        sizeof(QmwStateObject),
        nullptr,
        A_DEFLONG,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_state_real), "real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_state_imag), "imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_state_bang), "bang", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_state_clear), "clear", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_state_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_state_class = klass;
}
