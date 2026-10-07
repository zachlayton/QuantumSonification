#include "qmw/hamiltonian.hpp"
#include "qmw/revisioned_state.hpp"
#include "qmw/spectrum.hpp"

#include "ext.h"
#include "ext_obex.h"

#include <cmath>
#include <cstddef>
#include <cstdio>
#include <exception>
#include <memory>
#include <string>
#include <utility>
#include <vector>

namespace {

class SpectrumAdapter final {
public:
    SpectrumAdapter(const long qubits, qmw::HamiltonianMetadata metadata)
        : state_(std::size_t {1} << qubits)
        , hamiltonian_(std::size_t {1} << qubits, std::move(metadata))
    {
    }

    [[nodiscard]] qmw::RevisionedStateStore& state() noexcept { return state_; }
    [[nodiscard]] qmw::RevisionedHamiltonianStore& hamiltonian() noexcept { return hamiltonian_; }
    [[nodiscard]] long published_revision() const noexcept { return published_revision_; }
    [[nodiscard]] const qmw::QuantumSpectrumFrame* frame() const noexcept { return frame_.get(); }

    void publish(qmw::QuantumSpectrumFrame frame)
    {
        published_revision_ = frame.provenance().state_revision;
        frame_ = std::make_unique<qmw::QuantumSpectrumFrame>(std::move(frame));
    }

private:
    qmw::RevisionedStateStore state_;
    qmw::RevisionedHamiltonianStore hamiltonian_;
    long published_revision_ {-1};
    std::unique_ptr<qmw::QuantumSpectrumFrame> frame_;
};

struct QmwSpectrumObject {
    t_object object;
    SpectrumAdapter* adapter;
    void* matrix_outlet;
    void* vector_outlet;
    void* diagnostics_outlet;
    void* status_outlet;
};

t_class* qmw_spectrum_class = nullptr;

void status(
    QmwSpectrumObject* object,
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

void waiting_status(QmwSpectrumObject* object)
{
    t_atom atoms[2];
    atom_setlong(atoms, object->adapter->state().active_revision());
    atom_setlong(atoms + 1, object->adapter->hamiltonian().active_revision());
    outlet_anything(object->status_outlet, gensym("waiting_revision_pair"), 2, atoms);
}

[[nodiscard]] bool numeric_atom(const t_atom* atom)
{
    const auto type = atom_gettype(atom);
    return type == A_LONG || type == A_FLOAT;
}

[[nodiscard]] bool collect_values(
    QmwSpectrumObject* object,
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

void output_real_vector(
    QmwSpectrumObject* object,
    const char* selector,
    const long revision,
    const std::vector<double>& values)
{
    std::vector<t_atom> atoms(values.size() + 1);
    atom_setlong(atoms.data(), revision);
    for (std::size_t index = 0; index < values.size(); ++index) {
        atom_setfloat(atoms.data() + index + 1, values[index]);
    }
    outlet_anything(
        object->vector_outlet,
        gensym(selector),
        static_cast<long>(atoms.size()),
        atoms.data());
}

void output_complex_matrix(
    QmwSpectrumObject* object,
    const char* real_selector,
    const char* imag_selector,
    const long revision,
    const std::size_t dimension,
    const std::vector<qmw::Complex>& values)
{
    std::vector<t_atom> real(values.size() + 2);
    std::vector<t_atom> imag(values.size() + 2);
    atom_setlong(real.data(), revision);
    atom_setlong(imag.data(), revision);
    atom_setlong(real.data() + 1, static_cast<long>(dimension));
    atom_setlong(imag.data() + 1, static_cast<long>(dimension));
    for (std::size_t index = 0; index < values.size(); ++index) {
        atom_setfloat(real.data() + index + 2, values[index].real());
        atom_setfloat(imag.data() + index + 2, values[index].imag());
    }
    outlet_anything(
        object->matrix_outlet,
        gensym(real_selector),
        static_cast<long>(real.size()),
        real.data());
    outlet_anything(
        object->matrix_outlet,
        gensym(imag_selector),
        static_cast<long>(imag.size()),
        imag.data());
}

void output_degeneracy(
    QmwSpectrumObject* object,
    const char* selector,
    const long revision,
    const qmw::HermitianEigensystem& eigensystem)
{
    std::vector<t_atom> atoms(3 + 2 * eigensystem.near_degenerate_groups.size());
    atom_setlong(atoms.data(), revision);
    atom_setlong(atoms.data() + 1, eigensystem.mode_labels_stable ? 1 : 0);
    atom_setlong(
        atoms.data() + 2,
        static_cast<long>(eigensystem.near_degenerate_groups.size()));
    for (std::size_t index = 0; index < eigensystem.near_degenerate_groups.size(); ++index) {
        atom_setlong(
            atoms.data() + 3 + 2 * index,
            static_cast<long>(eigensystem.near_degenerate_groups[index].first));
        atom_setlong(
            atoms.data() + 4 + 2 * index,
            static_cast<long>(eigensystem.near_degenerate_groups[index].last));
    }
    outlet_anything(
        object->diagnostics_outlet,
        gensym(selector),
        static_cast<long>(atoms.size()),
        atoms.data());
}

void output_frame(QmwSpectrumObject* object)
{
    const auto* frame = object->adapter->frame();
    if (frame == nullptr) {
        status(object, "empty", -1);
        return;
    }
    const auto& provenance = frame->provenance();
    const long revision = provenance.state_revision;

    // This begin/payload/accepted sequence is one revision-labelled frame.
    // Receivers must expose it only on the final accepted message.
    status(object, "frame_begin", revision);
    output_complex_matrix(
        object,
        "energy_eigenvectors_real",
        "energy_eigenvectors_imag",
        revision,
        frame->dimension(),
        frame->energy().eigenvectors);
    output_complex_matrix(
        object,
        "density_eigenvectors_real",
        "density_eigenvectors_imag",
        revision,
        frame->dimension(),
        frame->density().eigenvectors);
    output_complex_matrix(
        object,
        "rho_energy_real",
        "rho_energy_imag",
        revision,
        frame->dimension(),
        frame->rho_in_energy_basis());

    output_real_vector(object, "energy_eigenvalues", revision, frame->energy().eigenvalues);
    output_real_vector(object, "density_eigenvalues", revision, frame->density().eigenvalues);
    output_real_vector(object, "energy_populations", revision, frame->energy_populations());
    output_real_vector(object, "basis_overlap", revision, frame->basis_overlap());
    output_real_vector(object, "energy_gaps", revision, frame->energy_gaps());
    output_real_vector(object, "density_gaps", revision, frame->density_gaps());

    t_atom metrics[16];
    atom_setlong(metrics, revision);
    atom_setlong(metrics + 1, static_cast<long>(frame->dimension()));
    atom_setfloat(metrics + 2, frame->purity());
    atom_setfloat(metrics + 3, frame->entropy_nats());
    atom_setfloat(metrics + 4, frame->participation_rank());
    atom_setfloat(metrics + 5, frame->commutator_norm());
    atom_setlong(metrics + 6, static_cast<long>(frame->energy().sweeps));
    atom_setfloat(metrics + 7, frame->energy().off_diagonal_frobenius);
    atom_setfloat(metrics + 8, frame->energy().relative_residual_frobenius);
    atom_setlong(metrics + 9, static_cast<long>(frame->density().sweeps));
    atom_setfloat(metrics + 10, frame->density().off_diagonal_frobenius);
    atom_setfloat(metrics + 11, frame->density().relative_residual_frobenius);
    atom_setfloat(metrics + 12, frame->policy().relative_eigensolver_tolerance);
    atom_setfloat(metrics + 13, frame->policy().density_positivity_tolerance);
    atom_setfloat(metrics + 14, frame->policy().degeneracy_tolerance);
    atom_setlong(metrics + 15, static_cast<long>(frame->policy().maximum_sweeps));
    outlet_anything(object->diagnostics_outlet, gensym("metrics"), 16, metrics);

    t_atom provenance_atoms[10];
    atom_setlong(provenance_atoms, provenance.state_revision);
    atom_setlong(provenance_atoms + 1, provenance.hamiltonian_revision);
    atom_setsym(provenance_atoms + 2, gensym(provenance.density_unit.c_str()));
    atom_setsym(provenance_atoms + 3, gensym(provenance.energy_unit.c_str()));
    atom_setsym(provenance_atoms + 4, gensym(provenance.basis_id.c_str()));
    atom_setsym(provenance_atoms + 5, gensym("row_major_modes_in_columns"));
    atom_setsym(provenance_atoms + 6, gensym(provenance.hamiltonian_source_id.c_str()));
    atom_setsym(provenance_atoms + 7, gensym(provenance.hamiltonian_provenance.c_str()));
    atom_setsym(provenance_atoms + 8, gensym(provenance.ordering.c_str()));
    atom_setsym(provenance_atoms + 9, gensym(provenance.phase_convention.c_str()));
    outlet_anything(object->diagnostics_outlet, gensym("provenance"), 10, provenance_atoms);
    output_degeneracy(object, "energy_degeneracy", revision, frame->energy());
    output_degeneracy(object, "density_degeneracy", revision, frame->density());
    status(object, "accepted", revision);
}

void maybe_publish(QmwSpectrumObject* object)
{
    const auto* state = object->adapter->state().active();
    const auto* hamiltonian = object->adapter->hamiltonian().active();
    if (state == nullptr || hamiltonian == nullptr) {
        waiting_status(object);
        return;
    }
    const long state_revision = object->adapter->state().active_revision();
    const long hamiltonian_revision = object->adapter->hamiltonian().active_revision();
    if (state_revision != hamiltonian_revision) {
        waiting_status(object);
        return;
    }
    if (state_revision <= object->adapter->published_revision()) {
        return;
    }
    try {
        object->adapter->publish(qmw::analyze_quantum_spectrum(
            *state, state_revision, *hamiltonian, hamiltonian_revision));
        output_frame(object);
    } catch (const qmw::SpectrumError& error) {
        object_error(&object->object, "spectrum revision %ld rejected: %s", state_revision, error.what());
        const std::string detail(qmw::spectrum_code_name(error.code()));
        status(object, "rejected", state_revision, detail.c_str());
    }
}

void stage_state(
    QmwSpectrumObject* object,
    const qmw::StatePart part,
    const char* component,
    const long argc,
    const t_atom* argv)
{
    long revision = -1;
    std::vector<double> values;
    if (!collect_values(object, component, argc, argv, object->adapter->state().element_count(), revision, values)) {
        return;
    }
    const auto result = object->adapter->state().stage(part, revision, std::move(values));
    switch (result.status) {
    case qmw::StageStatus::staged:
        status(object, "state_staged", revision, result.detail.c_str());
        break;
    case qmw::StageStatus::accepted:
        status(object, "state_accepted", revision);
        maybe_publish(object);
        break;
    case qmw::StageStatus::rejected:
        object_error(&object->object, "state revision %ld rejected: %s", revision, result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        break;
    }
}

void stage_hamiltonian(
    QmwSpectrumObject* object,
    const qmw::HamiltonianPart part,
    const char* component,
    const long argc,
    const t_atom* argv)
{
    long revision = -1;
    std::vector<double> values;
    if (!collect_values(object, component, argc, argv, object->adapter->hamiltonian().element_count(), revision, values)) {
        return;
    }
    const auto result = object->adapter->hamiltonian().stage(part, revision, std::move(values));
    switch (result.status) {
    case qmw::HamiltonianStageStatus::staged:
        status(object, "hamiltonian_staged", revision, result.detail.c_str());
        break;
    case qmw::HamiltonianStageStatus::accepted:
        status(object, "hamiltonian_accepted", revision);
        maybe_publish(object);
        break;
    case qmw::HamiltonianStageStatus::rejected:
        object_error(&object->object, "Hamiltonian revision %ld rejected: %s", revision, result.message.c_str());
        status(object, "rejected", revision, result.detail.c_str());
        break;
    }
}

void qmw_spectrum_rho_real(QmwSpectrumObject* object, t_symbol*, const long argc, t_atom* argv)
{
    stage_state(object, qmw::StatePart::real, "rho_real", argc, argv);
}

void qmw_spectrum_rho_imag(QmwSpectrumObject* object, t_symbol*, const long argc, t_atom* argv)
{
    stage_state(object, qmw::StatePart::imag, "rho_imag", argc, argv);
}

void qmw_spectrum_hamiltonian_real(QmwSpectrumObject* object, t_symbol*, const long argc, t_atom* argv)
{
    stage_hamiltonian(object, qmw::HamiltonianPart::real, "hamiltonian_real", argc, argv);
}

void qmw_spectrum_hamiltonian_imag(QmwSpectrumObject* object, t_symbol*, const long argc, t_atom* argv)
{
    stage_hamiltonian(object, qmw::HamiltonianPart::imag, "hamiltonian_imag", argc, argv);
}

void qmw_spectrum_bang(QmwSpectrumObject* object)
{
    output_frame(object);
}

void qmw_spectrum_clear(QmwSpectrumObject* object)
{
    object->adapter->state().clear_candidate();
    object->adapter->hamiltonian().clear_candidate();
    status(object, "candidates_cleared", object->adapter->published_revision());
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

void qmw_spectrum_assist(QmwSpectrumObject*, void*, const long message, const long index, char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "rho_real/rho_imag and hamiltonian_real/imag revision pairs; bang; clear";
    } else {
        const char* const outlets[] = {
            "Energy/density eigenvectors and energy-basis density matrices",
            "Eigenvalues, populations, and degeneracy groups",
            "Purity, entropy, participation, commutator, and provenance",
            "Frame and revision transaction status",
        };
        label = index >= 0 && index < 4 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_spectrum_new(t_symbol*, const long argc, t_atom* argv)
{
    auto* object = static_cast<QmwSpectrumObject*>(object_alloc(qmw_spectrum_class));
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
            "usage: qmw.spectrum [qubits 1..6] [energy_unit] [basis_id] [source_id] [provenance]");
        object_free(&object->object);
        return nullptr;
    }

    qmw::HamiltonianMetadata metadata {
        "model_energy",
        "computational_q0_lsb",
        "qmw.spectrum-input",
        "revision-locked-Max-matrix-pair",
    };
    if (!optional_symbol(argc, argv, 1, metadata.energy_unit)
        || !optional_symbol(argc, argv, 2, metadata.basis_id)
        || !optional_symbol(argc, argv, 3, metadata.source_id)
        || !optional_symbol(argc, argv, 4, metadata.provenance)) {
        object_error(&object->object, "spectrum metadata arguments must be symbols");
        object_free(&object->object);
        return nullptr;
    }
    try {
        object->adapter = new SpectrumAdapter(qubits, std::move(metadata));
    } catch (const std::exception& error) {
        object_error(&object->object, "%s", error.what());
        object_free(&object->object);
        return nullptr;
    }

    // Max creates multiple outlets from right to left.
    object->status_outlet = outlet_new(object, nullptr);
    object->diagnostics_outlet = outlet_new(object, nullptr);
    object->vector_outlet = outlet_new(object, nullptr);
    object->matrix_outlet = outlet_new(object, nullptr);
    return object;
}

void qmw_spectrum_free(QmwSpectrumObject* object)
{
    delete object->adapter;
    object->adapter = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.spectrum",
        reinterpret_cast<method>(qmw_spectrum_new),
        reinterpret_cast<method>(qmw_spectrum_free),
        sizeof(QmwSpectrumObject),
        nullptr,
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_spectrum_rho_real), "rho_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_spectrum_rho_imag), "rho_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_spectrum_hamiltonian_real), "hamiltonian_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_spectrum_hamiltonian_imag), "hamiltonian_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_spectrum_bang), "bang", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_spectrum_clear), "clear", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_spectrum_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_spectrum_class = klass;
}
