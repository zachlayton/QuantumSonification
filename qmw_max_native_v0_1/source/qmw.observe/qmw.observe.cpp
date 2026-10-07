#include "qmw/observe.hpp"
#include "qmw/revisioned_state.hpp"

#include "ext.h"
#include "ext_obex.h"

#include <cmath>
#include <cstddef>
#include <cstdio>
#include <exception>
#include <vector>

namespace {

class ObserveAdapter final {
public:
    ObserveAdapter(const long qubits, const std::size_t qubit, const qmw::PauliAxis axis)
        : observer_(std::size_t {1} << qubits, qubit, axis)
    {
    }

    [[nodiscard]] qmw::RevisionedPauliObserver& observer() noexcept { return observer_; }
    [[nodiscard]] const qmw::RevisionedPauliObserver& observer() const noexcept { return observer_; }

private:
    qmw::RevisionedPauliObserver observer_;
};

struct QmwObserveObject {
    t_object object;
    ObserveAdapter* adapter;
    void* value_outlet;
    void* status_outlet;
};

t_class* qmw_observe_class = nullptr;

const char* axis_name(const qmw::PauliAxis axis)
{
    switch (axis) {
    case qmw::PauliAxis::x:
        return "X";
    case qmw::PauliAxis::y:
        return "Y";
    case qmw::PauliAxis::z:
        return "Z";
    }
    return "Z";
}

bool parse_axis(const t_atom* atom, qmw::PauliAxis& axis)
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

void status(QmwObserveObject* object, const char* selector, const long revision, const char* detail = nullptr)
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

void output_active(QmwObserveObject* object, const char* status_selector)
{
    const auto observation = object->adapter->observer().active();
    if (!observation.has_value()) {
        status(object, "empty", -1);
        return;
    }

    t_atom atoms[4];
    atom_setlong(atoms, observation->revision);
    atom_setsym(atoms + 1, gensym(axis_name(observation->axis)));
    atom_setlong(atoms + 2, static_cast<long>(observation->qubit));
    atom_setfloat(atoms + 3, observation->expectation);
    outlet_anything(object->value_outlet, gensym("expectation"), 4, atoms);
    status(object, status_selector, observation->revision);
}

void stage_component(
    QmwObserveObject* object,
    const qmw::StatePart part,
    const char* component_name,
    const long argc,
    const t_atom* argv)
{
    const auto required = static_cast<long>(object->adapter->observer().element_count() + 1);
    if (argc != required) {
        object_error(
            &object->object,
            "%s requires revision plus %zu row-major values",
            component_name,
            object->adapter->observer().element_count());
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
    values.reserve(object->adapter->observer().element_count());
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

    const auto result = object->adapter->observer().stage(part, revision, std::move(values));
    switch (result.status) {
    case qmw::StageStatus::staged:
        status(object, "staged", revision, result.detail.c_str());
        break;
    case qmw::StageStatus::accepted:
        output_active(object, "accepted");
        break;
    case qmw::StageStatus::rejected:
        object_error(&object->object, "revision %ld rejected: %s", revision, result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        break;
    }
}

void qmw_observe_real(QmwObserveObject* object, t_symbol*, const long argc, t_atom* argv)
{
    stage_component(object, qmw::StatePart::real, "rho_real", argc, argv);
}

void qmw_observe_imag(QmwObserveObject* object, t_symbol*, const long argc, t_atom* argv)
{
    stage_component(object, qmw::StatePart::imag, "rho_imag", argc, argv);
}

void qmw_observe_bang(QmwObserveObject* object)
{
    output_active(object, "active");
}

void qmw_observe_assist(QmwObserveObject*, void*, const long message, const long index, char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "Accepted density copy: rho_real/rho_imag REVISION MATRIX; bang";
    } else {
        const char* const outlets[] = {
            "Pauli expectation: expectation REVISION AXIS QUBIT VALUE",
            "Observer transaction status",
        };
        label = index >= 0 && index < 2 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_observe_new(t_symbol*, const long argc, t_atom* argv)
{
    auto* object = static_cast<QmwObserveObject*>(object_alloc(qmw_observe_class));
    if (object == nullptr) {
        return nullptr;
    }
    object->adapter = nullptr;

    qmw::PauliAxis axis = qmw::PauliAxis::z;
    long qubit = 0;
    long qubits = 4;
    if (argc > 0 && !parse_axis(argv, axis)) {
        object_error(&object->object, "axis must be X, Y, or Z");
        object_free(&object->object);
        return nullptr;
    }
    if (argc > 1 && atom_gettype(argv + 1) != A_LONG) {
        object_error(&object->object, "target qubit must be an integer");
        object_free(&object->object);
        return nullptr;
    }
    if (argc > 1) {
        qubit = atom_getlong(argv + 1);
    }
    if (argc > 2 && atom_gettype(argv + 2) != A_LONG) {
        object_error(&object->object, "source qubit count must be an integer");
        object_free(&object->object);
        return nullptr;
    }
    if (argc > 2) {
        qubits = atom_getlong(argv + 2);
    }
    if (argc > 3) {
        object_error(&object->object, "usage: qmw.observe [X|Y|Z] [qubit] [qubits]");
        object_free(&object->object);
        return nullptr;
    }
    if (qubits < 1 || qubits > 6 || qubit < 0 || qubit >= qubits) {
        object_error(&object->object, "require 1 <= qubits <= 6 and 0 <= qubit < qubits");
        object_free(&object->object);
        return nullptr;
    }

    try {
        object->adapter = new ObserveAdapter(qubits, static_cast<std::size_t>(qubit), axis);
    } catch (const std::exception& error) {
        object_error(&object->object, "could not create observer: %s", error.what());
        object_free(&object->object);
        return nullptr;
    }
    // Max creates multiple outlets from right to left.
    object->status_outlet = outlet_new(object, nullptr);
    object->value_outlet = outlet_new(object, nullptr);
    return object;
}

void qmw_observe_free(QmwObserveObject* object)
{
    delete object->adapter;
    object->adapter = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.observe",
        reinterpret_cast<method>(qmw_observe_new),
        reinterpret_cast<method>(qmw_observe_free),
        sizeof(QmwObserveObject),
        nullptr,
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_observe_real), "rho_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_observe_imag), "rho_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_observe_real), "real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_observe_imag), "imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_observe_bang), "bang", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_observe_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_observe_class = klass;
}
