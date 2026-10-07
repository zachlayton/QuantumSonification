#include "qmw/evolve.hpp"
#include "qmw/hamiltonian.hpp"
#include "qmw/revisioned_state.hpp"

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

class EvolveAdapter final {
public:
    EvolveAdapter(const long qubits, std::string energy_unit)
        : state_(std::size_t {1} << qubits)
        , hamiltonian_(
              std::size_t {1} << qubits,
              qmw::HamiltonianMetadata {
                  std::move(energy_unit),
                  "computational_q0_lsb",
                  "qmw.evolve-input",
                  "revision-locked-Max-matrix-pair",
              })
    {
    }

    [[nodiscard]] qmw::RevisionedStateStore& state() noexcept { return state_; }
    [[nodiscard]] qmw::RevisionedHamiltonianStore& hamiltonian() noexcept
    {
        return hamiltonian_;
    }
    [[nodiscard]] long last_candidate_revision() const noexcept
    {
        return last_candidate_revision_;
    }
    void set_last_candidate_revision(const long revision) noexcept
    {
        last_candidate_revision_ = revision;
    }

private:
    qmw::RevisionedStateStore state_;
    qmw::RevisionedHamiltonianStore hamiltonian_;
    long last_candidate_revision_ {-1};
};

struct QmwEvolveObject {
    t_object object;
    EvolveAdapter* adapter;
    void* matrix_outlet;
    void* diagnostics_outlet;
    void* status_outlet;
};

t_class* qmw_evolve_class = nullptr;

void status(
    QmwEvolveObject* object,
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

[[nodiscard]] bool collect_values(
    QmwEvolveObject* object,
    const char* component,
    const long argc,
    const t_atom* argv,
    const std::size_t element_count,
    long& revision,
    std::vector<double>& values)
{
    if (argc != static_cast<long>(element_count + 1)) {
        object_error(
            &object->object,
            "%s requires revision plus %zu row-major values",
            component,
            element_count);
        status(object, "rejected", -1, "wrong_element_count");
        return false;
    }
    if (atom_gettype(argv) != A_LONG) {
        object_error(&object->object, "%s revision must be an integer", component);
        status(object, "rejected", -1, "invalid_revision_atom");
        return false;
    }
    revision = atom_getlong(argv);
    values.reserve(element_count);
    for (long index = 1; index < argc; ++index) {
        if (!numeric_atom(argv + index)) {
            object_error(&object->object, "%s contains a nonnumeric atom", component);
            status(object, "rejected", revision, "nonnumeric_atom");
            return false;
        }
        const double value = atom_getfloat(argv + index);
        if (!std::isfinite(value)) {
            object_error(&object->object, "%s contains a non-finite value", component);
            status(object, "rejected", revision, "non_finite");
            return false;
        }
        values.push_back(value);
    }
    return true;
}

void stage_state(
    QmwEvolveObject* object,
    const qmw::StatePart part,
    const char* component,
    const long argc,
    const t_atom* argv)
{
    long revision = -1;
    std::vector<double> values;
    if (!collect_values(
            object,
            component,
            argc,
            argv,
            object->adapter->state().element_count(),
            revision,
            values)) {
        return;
    }
    const auto result = object->adapter->state().stage(part, revision, std::move(values));
    switch (result.status) {
    case qmw::StageStatus::staged:
        status(object, "state_staged", revision, result.detail.c_str());
        break;
    case qmw::StageStatus::accepted:
        status(object, "state_accepted", revision);
        break;
    case qmw::StageStatus::rejected:
        object_error(&object->object, "state revision %ld rejected: %s", revision, result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        break;
    }
}

void stage_hamiltonian(
    QmwEvolveObject* object,
    const qmw::HamiltonianPart part,
    const char* component,
    const long argc,
    const t_atom* argv)
{
    long revision = -1;
    std::vector<double> values;
    if (!collect_values(
            object,
            component,
            argc,
            argv,
            object->adapter->hamiltonian().element_count(),
            revision,
            values)) {
        return;
    }
    const auto result = object->adapter->hamiltonian().stage(
        part, revision, std::move(values));
    switch (result.status) {
    case qmw::HamiltonianStageStatus::staged:
        status(object, "hamiltonian_staged", revision, result.detail.c_str());
        break;
    case qmw::HamiltonianStageStatus::accepted:
        status(object, "hamiltonian_accepted", revision);
        break;
    case qmw::HamiltonianStageStatus::rejected:
        object_error(
            &object->object,
            "Hamiltonian revision %ld rejected: %s",
            revision,
            result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        break;
    }
}

void qmw_evolve_rho_real(
    QmwEvolveObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    stage_state(object, qmw::StatePart::real, "rho_real", argc, argv);
}

void qmw_evolve_rho_imag(
    QmwEvolveObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    stage_state(object, qmw::StatePart::imag, "rho_imag", argc, argv);
}

void qmw_evolve_hamiltonian_real(
    QmwEvolveObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    stage_hamiltonian(
        object, qmw::HamiltonianPart::real, "hamiltonian_real", argc, argv);
}

void qmw_evolve_hamiltonian_imag(
    QmwEvolveObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    stage_hamiltonian(
        object, qmw::HamiltonianPart::imag, "hamiltonian_imag", argc, argv);
}

void output_candidate(QmwEvolveObject* object, const qmw::EvolutionCandidate& candidate)
{
    const auto& values = candidate.state().values();
    const auto& request = candidate.request();
    const auto& diagnostics = candidate.diagnostics();
    std::vector<t_atom> real(values.size() + 1);
    std::vector<t_atom> imag(values.size() + 1);
    atom_setlong(real.data(), request.candidate_revision);
    atom_setlong(imag.data(), request.candidate_revision);
    for (std::size_t index = 0; index < values.size(); ++index) {
        atom_setfloat(real.data() + index + 1, values[index].real());
        atom_setfloat(imag.data() + index + 1, values[index].imag());
    }

    t_atom metric_atoms[17];
    atom_setlong(metric_atoms, request.candidate_revision);
    atom_setlong(metric_atoms + 1, request.state_revision);
    atom_setlong(metric_atoms + 2, request.hamiltonian_revision);
    atom_setfloat(metric_atoms + 3, request.dt);
    atom_setsym(metric_atoms + 4, gensym(request.time_unit.c_str()));
    atom_setfloat(metric_atoms + 5, request.hbar);
    atom_setsym(metric_atoms + 6, gensym(candidate.energy_unit().c_str()));
    atom_setlong(metric_atoms + 7, diagnostics.pade_order);
    atom_setlong(metric_atoms + 8, static_cast<long>(diagnostics.scaling_squarings));
    atom_setfloat(metric_atoms + 9, diagnostics.dimensionless_generator_one_norm);
    atom_setfloat(metric_atoms + 10, diagnostics.unitarity_residual_relative_fro);
    atom_setfloat(metric_atoms + 11, diagnostics.trace_drift);
    atom_setfloat(metric_atoms + 12, diagnostics.frobenius_norm_drift);
    atom_setfloat(metric_atoms + 13, diagnostics.relative_frobenius_norm_drift);
    atom_setfloat(metric_atoms + 14, diagnostics.purity_drift);
    atom_setfloat(metric_atoms + 15, diagnostics.output_hermiticity_residual);
    atom_setfloat(metric_atoms + 16, diagnostics.output_minimum_ldlt_pivot);

    // The pair is a candidate for an explicit downstream qmw.state commit.
    // Diagnostics retain both exact source revisions and unit declarations.
    outlet_anything(
        object->matrix_outlet,
        gensym("real"),
        static_cast<long>(real.size()),
        real.data());
    outlet_anything(
        object->matrix_outlet,
        gensym("imag"),
        static_cast<long>(imag.size()),
        imag.data());
    outlet_anything(object->diagnostics_outlet, gensym("evolution"), 17, metric_atoms);
    status(object, "candidate", request.candidate_revision);
}

void qmw_evolve_evolve(
    QmwEvolveObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    if (argc != 6
        || atom_gettype(argv) != A_LONG
        || atom_gettype(argv + 1) != A_LONG
        || atom_gettype(argv + 2) != A_LONG
        || !numeric_atom(argv + 3)
        || atom_gettype(argv + 4) != A_SYM
        || !numeric_atom(argv + 5)) {
        object_error(
            &object->object,
            "usage: evolve candidate_revision state_revision hamiltonian_revision dt time_unit hbar");
        status(object, "rejected", -1, "invalid_evolve_message");
        return;
    }

    qmw::EvolutionRequest request {
        atom_getlong(argv + 1),
        atom_getlong(argv + 2),
        atom_getlong(argv),
        atom_getfloat(argv + 3),
        atom_getsym(argv + 4)->s_name,
        atom_getfloat(argv + 5),
    };
    const auto* state = object->adapter->state().active();
    const auto* hamiltonian = object->adapter->hamiltonian().active();
    if (state == nullptr || hamiltonian == nullptr) {
        object_error(&object->object, "evolve requires active state and Hamiltonian revisions");
        status(object, "rejected", request.candidate_revision, "missing_input");
        return;
    }
    if (object->adapter->state().active_revision() != request.state_revision) {
        object_error(&object->object, "requested state revision is not active");
        status(object, "rejected", request.candidate_revision, "state_revision_mismatch");
        return;
    }
    if (object->adapter->hamiltonian().active_revision()
        != request.hamiltonian_revision) {
        object_error(&object->object, "requested Hamiltonian revision is not active");
        status(object, "rejected", request.candidate_revision, "hamiltonian_revision_mismatch");
        return;
    }
    if (request.candidate_revision <= object->adapter->last_candidate_revision()) {
        object_error(&object->object, "candidate revision is not newer than the last output");
        status(object, "rejected", request.candidate_revision, "stale_candidate_revision");
        return;
    }

    try {
        const auto candidate = qmw::evolve_closed_system(
            *state, *hamiltonian, request);
        object->adapter->set_last_candidate_revision(
            candidate.request().candidate_revision);
        output_candidate(object, candidate);
    } catch (const qmw::EvolutionError& error) {
        const std::string detail(qmw::evolution_code_name(error.code()));
        object_error(&object->object, "evolution rejected: %s", error.what());
        status(
            object,
            "rejected",
            request.candidate_revision,
            detail.c_str());
    }
}

void qmw_evolve_clear(QmwEvolveObject* object)
{
    object->adapter->state().clear_candidate();
    object->adapter->hamiltonian().clear_candidate();
    status(object, "candidates_cleared", object->adapter->last_candidate_revision());
}

void qmw_evolve_assist(QmwEvolveObject*, void*, const long message, const long index, char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "rho_real/rho_imag and hamiltonian_real/imag transactions; evolve; clear";
    } else {
        const char* const outlets[] = {
            "Evolved density candidate: rho_candidate_real/rho_candidate_imag",
            "Evolution metadata and numerical diagnostics",
            "Revision transaction and evolution status",
        };
        label = index >= 0 && index < 3 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_evolve_new(t_symbol*, const long argc, t_atom* argv)
{
    auto* object = static_cast<QmwEvolveObject*>(object_alloc(qmw_evolve_class));
    if (object == nullptr) {
        return nullptr;
    }
    object->adapter = nullptr;

    long qubits = 4;
    std::string energy_unit = "model_energy";
    if (argc > 0 && atom_gettype(argv) != A_LONG) {
        object_error(&object->object, "qubit count must be an integer");
        object_free(&object->object);
        return nullptr;
    }
    if (argc > 0) {
        qubits = atom_getlong(argv);
    }
    if (argc > 1 && atom_gettype(argv + 1) != A_SYM) {
        object_error(&object->object, "energy unit must be a symbol");
        object_free(&object->object);
        return nullptr;
    }
    if (argc > 1) {
        energy_unit = atom_getsym(argv + 1)->s_name;
    }
    if (argc > 2 || qubits < 1 || qubits > 6) {
        object_error(&object->object, "usage: qmw.evolve [qubits 1..6] [energy_unit]");
        object_free(&object->object);
        return nullptr;
    }

    try {
        object->adapter = new EvolveAdapter(qubits, std::move(energy_unit));
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

void qmw_evolve_free(QmwEvolveObject* object)
{
    delete object->adapter;
    object->adapter = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.evolve",
        reinterpret_cast<method>(qmw_evolve_new),
        reinterpret_cast<method>(qmw_evolve_free),
        sizeof(QmwEvolveObject),
        nullptr,
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_evolve_rho_real), "rho_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_evolve_rho_imag), "rho_imag", A_GIMME, 0);
    class_addmethod(
        klass,
        reinterpret_cast<method>(qmw_evolve_hamiltonian_real),
        "hamiltonian_real",
        A_GIMME,
        0);
    class_addmethod(
        klass,
        reinterpret_cast<method>(qmw_evolve_hamiltonian_imag),
        "hamiltonian_imag",
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_evolve_evolve), "evolve", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_evolve_clear), "clear", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_evolve_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_evolve_class = klass;
}
