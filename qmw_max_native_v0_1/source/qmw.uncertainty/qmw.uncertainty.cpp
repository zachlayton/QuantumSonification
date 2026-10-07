#include "qmw/uncertainty.hpp"

#include "ext.h"
#include "ext_obex.h"

#include <cmath>
#include <cstddef>
#include <cstdio>
#include <exception>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace {

struct Transaction {
    long revision {-1};
    std::string basis_id;
    std::string state_source_id;
    std::string observable_a_unit;
    std::string observable_a_source_id;
    std::optional<std::string> observable_b_unit;
    std::optional<std::string> observable_b_source_id;
    std::optional<std::vector<double>> rho_real;
    std::optional<std::vector<double>> rho_imag;
    std::optional<std::vector<double>> a_real;
    std::optional<std::vector<double>> a_imag;
    std::optional<std::vector<double>> b_real;
    std::optional<std::vector<double>> b_imag;

    [[nodiscard]] bool expects_b() const noexcept
    {
        return observable_b_unit.has_value();
    }
};

struct ActiveAnalysis {
    qmw::ObservableMoments a;
    std::optional<qmw::ObservableMoments> b;
    std::optional<qmw::RobertsonSchrodingerResult> robertson;
};

class UncertaintyAdapter final {
public:
    explicit UncertaintyAdapter(const std::size_t dimension)
        : dimension_(dimension)
    {
    }

    [[nodiscard]] std::size_t dimension() const noexcept { return dimension_; }
    [[nodiscard]] std::size_t element_count() const noexcept { return dimension_ * dimension_; }
    [[nodiscard]] std::optional<Transaction>& transaction() noexcept { return transaction_; }
    [[nodiscard]] const std::optional<ActiveAnalysis>& active() const noexcept { return active_; }

    void begin(Transaction transaction) { transaction_ = std::move(transaction); }
    void abort() noexcept { transaction_.reset(); }

    void commit()
    {
        if (!transaction_.has_value()) {
            throw std::logic_error("no open uncertainty transaction");
        }
        const auto& transaction = *transaction_;
        if (!transaction.rho_real.has_value() || !transaction.rho_imag.has_value()
            || !transaction.a_real.has_value() || !transaction.a_imag.has_value()) {
            throw std::logic_error("transaction requires complete rho and observable A components");
        }
        if (transaction.expects_b()
            && (!transaction.b_real.has_value() || !transaction.b_imag.has_value())) {
            throw std::logic_error("transaction declares observable B but its components are incomplete");
        }

        const auto state = qmw::DensityState::from_split(
            dimension_, *transaction.rho_real, *transaction.rho_imag);
        const qmw::StateAnalysisMetadata state_metadata {
            transaction.revision,
            transaction.basis_id,
            transaction.state_source_id,
        };
        const auto observable_a = qmw::HermitianObservable::from_split(
            dimension_, *transaction.a_real, *transaction.a_imag,
            {
                transaction.revision,
                transaction.basis_id,
                transaction.observable_a_unit,
                transaction.observable_a_source_id,
            });
        ActiveAnalysis candidate {
            qmw::observable_moments(state, state_metadata, observable_a),
            std::nullopt,
            std::nullopt,
        };
        if (transaction.expects_b()) {
            const auto observable_b = qmw::HermitianObservable::from_split(
                dimension_, *transaction.b_real, *transaction.b_imag,
                {
                    transaction.revision,
                    transaction.basis_id,
                    *transaction.observable_b_unit,
                    *transaction.observable_b_source_id,
                });
            candidate.b = qmw::observable_moments(state, state_metadata, observable_b);
            candidate.robertson = qmw::robertson_schrodinger(
                state, state_metadata, observable_a, observable_b);
        }
        active_ = std::move(candidate);
        transaction_.reset();
    }

private:
    std::size_t dimension_ {};
    std::optional<Transaction> transaction_;
    std::optional<ActiveAnalysis> active_;
};

struct QmwUncertaintyObject {
    t_object object;
    UncertaintyAdapter* adapter;
    void* result_outlet;
    void* status_outlet;
};

t_class* qmw_uncertainty_class = nullptr;

void status(
    QmwUncertaintyObject* object,
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

[[nodiscard]] bool numeric_atom(const t_atom* atom) noexcept
{
    const auto type = atom_gettype(atom);
    return type == A_LONG || type == A_FLOAT;
}

[[nodiscard]] bool symbol_atom(const t_atom* atom) noexcept
{
    return atom_gettype(atom) == A_SYM;
}

void output_moments(
    QmwUncertaintyObject* object,
    const char* selector,
    const qmw::ObservableMoments& result)
{
    t_atom atoms[10];
    atom_setlong(atoms, result.revision);
    atom_setsym(atoms + 1, gensym(result.basis_id.c_str()));
    atom_setsym(atoms + 2, gensym(result.state_source_id.c_str()));
    atom_setsym(atoms + 3, gensym(result.state_unit.c_str()));
    atom_setsym(atoms + 4, gensym(result.observable_source_id.c_str()));
    atom_setsym(atoms + 5, gensym(result.observable_unit.c_str()));
    atom_setfloat(atoms + 6, result.expectation);
    atom_setfloat(atoms + 7, result.variance);
    atom_setfloat(atoms + 8, result.standard_deviation);
    outlet_anything(object->result_outlet, gensym(selector), 9, atoms);
}

void output_active(QmwUncertaintyObject* object, const char* status_selector)
{
    if (!object->adapter->active().has_value()) {
        status(object, "empty", -1);
        return;
    }
    const auto& active = *object->adapter->active();
    output_moments(object, "moments_a", active.a);
    if (active.b.has_value()) {
        output_moments(object, "moments_b", *active.b);
    }
    if (active.robertson.has_value()) {
        const auto& result = *active.robertson;
        t_atom atoms[15];
        atom_setlong(atoms, result.revision);
        atom_setsym(atoms + 1, gensym(result.basis_id.c_str()));
        atom_setsym(atoms + 2, gensym(result.state_source_id.c_str()));
        atom_setsym(atoms + 3, gensym(result.state_unit.c_str()));
        atom_setsym(atoms + 4, gensym(result.observable_a_source_id.c_str()));
        atom_setsym(atoms + 5, gensym(result.observable_b_source_id.c_str()));
        atom_setsym(atoms + 6, gensym(result.observable_a_unit.c_str()));
        atom_setsym(atoms + 7, gensym(result.observable_b_unit.c_str()));
        atom_setfloat(atoms + 8, result.covariance);
        atom_setfloat(atoms + 9, result.commutator_component);
        atom_setfloat(atoms + 10, result.lower_bound);
        atom_setfloat(atoms + 11, result.variance_product);
        atom_setfloat(atoms + 12, result.slack);
        outlet_anything(object->result_outlet, gensym("robertson_schrodinger"), 13, atoms);
    }
    status(object, status_selector, active.a.revision);
}

void qmw_uncertainty_begin(
    QmwUncertaintyObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    if (argc != 5 && argc != 7) {
        object_error(
            &object->object,
            "begin requires revision basis state_source A_unit A_source [B_unit B_source]");
        status(object, "rejected", -1, "invalid_begin");
        return;
    }
    if (atom_gettype(argv) != A_LONG) {
        object_error(&object->object, "transaction revision must be a nonnegative integer");
        status(object, "rejected", -1, "invalid_revision");
        return;
    }
    const long revision = atom_getlong(argv);
    if (revision < 0) {
        object_error(&object->object, "transaction revision must be nonnegative");
        status(object, "rejected", revision, "invalid_revision");
        return;
    }
    for (long index = 1; index < argc; ++index) {
        if (!symbol_atom(argv + index)) {
            object_error(&object->object, "begin metadata fields must be symbols");
            status(object, "rejected", revision, "invalid_metadata_atom");
            return;
        }
    }

    Transaction transaction;
    transaction.revision = revision;
    transaction.basis_id = atom_getsym(argv + 1)->s_name;
    transaction.state_source_id = atom_getsym(argv + 2)->s_name;
    transaction.observable_a_unit = atom_getsym(argv + 3)->s_name;
    transaction.observable_a_source_id = atom_getsym(argv + 4)->s_name;
    if (argc == 7) {
        transaction.observable_b_unit = atom_getsym(argv + 5)->s_name;
        transaction.observable_b_source_id = atom_getsym(argv + 6)->s_name;
    }
    object->adapter->begin(std::move(transaction));
    status(object, "begun", revision, argc == 7 ? "rho_a_b" : "rho_a");
}

void stage_component(
    QmwUncertaintyObject* object,
    std::optional<std::vector<double>> Transaction::* member,
    const char* name,
    const long argc,
    const t_atom* argv,
    const bool requires_b)
{
    if (!object->adapter->transaction().has_value()) {
        object_error(&object->object, "%s requires an open begin transaction", name);
        status(object, "rejected", -1, "no_transaction");
        return;
    }
    auto& transaction = *object->adapter->transaction();
    if (requires_b && !transaction.expects_b()) {
        object_error(&object->object, "%s requires B metadata declared by begin", name);
        status(object, "rejected", transaction.revision, "b_not_declared");
        return;
    }
    if (argc != static_cast<long>(object->adapter->element_count())) {
        object_error(
            &object->object, "%s requires %zu row-major values",
            name, object->adapter->element_count());
        status(object, "rejected", transaction.revision, "wrong_element_count");
        return;
    }
    std::vector<double> values;
    values.reserve(object->adapter->element_count());
    for (long index = 0; index < argc; ++index) {
        if (!numeric_atom(argv + index)) {
            object_error(&object->object, "%s contains a nonnumeric atom", name);
            status(object, "rejected", transaction.revision, "nonnumeric_atom");
            return;
        }
        const double value = atom_getfloat(argv + index);
        if (!std::isfinite(value)) {
            object_error(&object->object, "%s contains a non-finite value", name);
            status(object, "rejected", transaction.revision, "non_finite");
            return;
        }
        values.push_back(value);
    }
    transaction.*member = std::move(values);
    status(object, "staged", transaction.revision, name);
}

#define QMW_STAGE_METHOD(function_name, field_name, display_name, needs_b) \
    void function_name(QmwUncertaintyObject* object, t_symbol*, long argc, t_atom* argv) \
    { \
        stage_component(object, &Transaction::field_name, display_name, argc, argv, needs_b); \
    }

QMW_STAGE_METHOD(qmw_uncertainty_rho_real, rho_real, "rho_real", false)
QMW_STAGE_METHOD(qmw_uncertainty_rho_imag, rho_imag, "rho_imag", false)
QMW_STAGE_METHOD(qmw_uncertainty_a_real, a_real, "a_real", false)
QMW_STAGE_METHOD(qmw_uncertainty_a_imag, a_imag, "a_imag", false)
QMW_STAGE_METHOD(qmw_uncertainty_b_real, b_real, "b_real", true)
QMW_STAGE_METHOD(qmw_uncertainty_b_imag, b_imag, "b_imag", true)

#undef QMW_STAGE_METHOD

void qmw_uncertainty_commit(QmwUncertaintyObject* object)
{
    const long revision = object->adapter->transaction().has_value()
        ? object->adapter->transaction()->revision
        : -1;
    try {
        object->adapter->commit();
        output_active(object, "accepted");
    } catch (const qmw::UncertaintyValidationError& error) {
        object_error(&object->object, "uncertainty revision %ld rejected: %s", revision, error.what());
        object->adapter->abort();
        const std::string detail(qmw::uncertainty_validation_code_name(error.code()));
        status(object, "rejected", revision, detail.c_str());
    } catch (const qmw::ValidationError& error) {
        object_error(&object->object, "density revision %ld rejected: %s", revision, error.what());
        object->adapter->abort();
        const std::string detail(qmw::validation_code_name(error.code()));
        status(object, "rejected", revision, detail.c_str());
    } catch (const std::exception& error) {
        object_error(&object->object, "transaction rejected: %s", error.what());
        status(object, "rejected", revision, "incomplete_transaction");
    }
}

void qmw_uncertainty_abort(QmwUncertaintyObject* object)
{
    const long revision = object->adapter->transaction().has_value()
        ? object->adapter->transaction()->revision
        : -1;
    object->adapter->abort();
    status(object, "aborted", revision);
}

void qmw_uncertainty_bang(QmwUncertaintyObject* object)
{
    output_active(object, "active");
}

bool parse_mt_common(
    QmwUncertaintyObject* object,
    const long argc,
    t_atom* argv,
    const long numeric_count,
    std::vector<double>& numbers,
    const char*& energy_unit,
    const char*& source_id)
{
    if (argc != numeric_count + 2) {
        object_error(&object->object, "Mandelstam-Tamm message has the wrong argument count");
        status(object, "rejected", -1, "invalid_mandelstam_tamm_input");
        return false;
    }
    numbers.clear();
    for (long index = 0; index < numeric_count; ++index) {
        if (!numeric_atom(argv + index)) {
            object_error(&object->object, "Mandelstam-Tamm numeric fields must be numbers");
            status(object, "rejected", -1, "invalid_mandelstam_tamm_input");
            return false;
        }
        numbers.push_back(atom_getfloat(argv + index));
    }
    if (!symbol_atom(argv + numeric_count) || !symbol_atom(argv + numeric_count + 1)) {
        object_error(&object->object, "energy unit and source must be symbols");
        status(object, "rejected", -1, "invalid_metadata_atom");
        return false;
    }
    energy_unit = atom_getsym(argv + numeric_count)->s_name;
    source_id = atom_getsym(argv + numeric_count + 1)->s_name;
    return true;
}

void qmw_uncertainty_mt(
    QmwUncertaintyObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    if (!object->adapter->active().has_value()) {
        status(object, "rejected", -1, "no_active_analysis");
        return;
    }
    std::vector<double> values;
    const char* energy_unit = nullptr;
    const char* source_id = nullptr;
    if (!parse_mt_common(object, argc, argv, 3, values, energy_unit, source_id)) {
        return;
    }
    const auto& moments = object->adapter->active()->a;
    try {
        const auto result = qmw::mandelstam_tamm_characteristic_time(
            moments.standard_deviation, values[1], values[0], values[2],
            {moments.revision, moments.basis_id, moments.observable_unit, energy_unit, source_id});
        t_atom atoms[14];
        atom_setlong(atoms, result.metadata.revision);
        atom_setsym(atoms + 1, gensym(result.metadata.basis_id.c_str()));
        atom_setsym(atoms + 2, gensym(result.metadata.observable_unit.c_str()));
        atom_setsym(atoms + 3, gensym(result.metadata.energy_unit.c_str()));
        atom_setsym(atoms + 4, gensym(result.metadata.source_id.c_str()));
        atom_setfloat(atoms + 5, result.delta_observable);
        atom_setfloat(atoms + 6, result.absolute_expectation_rate);
        atom_setfloat(atoms + 7, result.delta_energy);
        atom_setfloat(atoms + 8, result.hbar);
        if (result.characteristic_time.has_value()) {
            atom_setfloat(atoms + 9, *result.characteristic_time);
            atom_setfloat(atoms + 10, *result.energy_time_product);
        } else {
            atom_setsym(atoms + 9, gensym("none"));
            atom_setsym(atoms + 10, gensym("none"));
        }
        atom_setfloat(atoms + 11, result.lower_bound);
        atom_setlong(atoms + 12, result.satisfies_bound ? 1 : 0);
        outlet_anything(
            object->result_outlet, gensym("mandelstam_tamm_characteristic"), 13, atoms);
        status(object, "reported", result.metadata.revision, "mandelstam_tamm_characteristic");
    } catch (const qmw::UncertaintyValidationError& error) {
        const std::string detail(qmw::uncertainty_validation_code_name(error.code()));
        status(object, "rejected", moments.revision, detail.c_str());
    }
}

void qmw_uncertainty_mt_orthogonal(
    QmwUncertaintyObject* object,
    t_symbol*,
    const long argc,
    t_atom* argv)
{
    if (!object->adapter->active().has_value()) {
        status(object, "rejected", -1, "no_active_analysis");
        return;
    }
    std::vector<double> values;
    const char* energy_unit = nullptr;
    const char* source_id = nullptr;
    if (!parse_mt_common(object, argc, argv, 2, values, energy_unit, source_id)) {
        return;
    }
    const auto& moments = object->adapter->active()->a;
    try {
        const auto result = qmw::mandelstam_tamm_orthogonalization_bound(
            values[0], values[1],
            {moments.revision, moments.basis_id, moments.observable_unit, energy_unit, source_id});
        t_atom atoms[9];
        atom_setlong(atoms, result.metadata.revision);
        atom_setsym(atoms + 1, gensym(result.metadata.basis_id.c_str()));
        atom_setsym(atoms + 2, gensym(result.metadata.energy_unit.c_str()));
        atom_setsym(atoms + 3, gensym(result.metadata.source_id.c_str()));
        atom_setfloat(atoms + 4, result.delta_energy);
        atom_setfloat(atoms + 5, result.hbar);
        if (result.minimum_time.has_value()) {
            atom_setfloat(atoms + 6, *result.minimum_time);
        } else {
            atom_setsym(atoms + 6, gensym("none"));
        }
        outlet_anything(
            object->result_outlet, gensym("mandelstam_tamm_orthogonalization"), 7, atoms);
        status(object, "reported", result.metadata.revision, "mandelstam_tamm_orthogonalization");
    } catch (const qmw::UncertaintyValidationError& error) {
        const std::string detail(qmw::uncertainty_validation_code_name(error.code()));
        status(object, "rejected", moments.revision, detail.c_str());
    }
}

void qmw_uncertainty_assist(QmwUncertaintyObject*, void*, const long message, const long index, char* description)
{
    const char* label = "";
    if (message == ASSIST_INLET) {
        label = "begin; rho/A/B real+imag; commit/abort; Mandelstam-Tamm queries; bang";
    } else {
        const char* const outlets[] = {
            "Uncertainty moments, Robertson-Schrodinger, and named time bounds",
            "Transaction status and validation errors",
        };
        label = index >= 0 && index < 2 ? outlets[index] : "";
    }
    std::snprintf(description, 512, "%s", label);
}

void* qmw_uncertainty_new(t_symbol*, const long argc, t_atom* argv)
{
    auto* object = static_cast<QmwUncertaintyObject*>(object_alloc(qmw_uncertainty_class));
    if (object == nullptr) {
        return nullptr;
    }
    object->adapter = nullptr;

    long qubits = 1;
    if (argc > 1 || (argc == 1 && atom_gettype(argv) != A_LONG)) {
        object_error(&object->object, "usage: qmw.uncertainty [qubits]");
        object_free(&object->object);
        return nullptr;
    }
    if (argc == 1) {
        qubits = atom_getlong(argv);
    }
    if (qubits < 1 || qubits > 6) {
        object_error(&object->object, "require 1 <= qubits <= 6");
        object_free(&object->object);
        return nullptr;
    }
    try {
        object->adapter = new UncertaintyAdapter(std::size_t {1} << qubits);
    } catch (const std::exception& error) {
        object_error(&object->object, "could not create uncertainty analyzer: %s", error.what());
        object_free(&object->object);
        return nullptr;
    }
    object->status_outlet = outlet_new(object, nullptr);
    object->result_outlet = outlet_new(object, nullptr);
    return object;
}

void qmw_uncertainty_free(QmwUncertaintyObject* object)
{
    delete object->adapter;
    object->adapter = nullptr;
}

} // namespace

extern "C" void C74_EXPORT ext_main(void*)
{
    auto* klass = class_new(
        "qmw.uncertainty",
        reinterpret_cast<method>(qmw_uncertainty_new),
        reinterpret_cast<method>(qmw_uncertainty_free),
        sizeof(QmwUncertaintyObject),
        nullptr,
        A_GIMME,
        0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_begin), "begin", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_rho_real), "rho_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_rho_imag), "rho_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_a_real), "a_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_a_imag), "a_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_b_real), "b_real", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_b_imag), "b_imag", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_commit), "commit", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_abort), "abort", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_mt), "mandelstam_tamm", A_GIMME, 0);
    class_addmethod(
        klass, reinterpret_cast<method>(qmw_uncertainty_mt_orthogonal),
        "mandelstam_tamm_orthogonal", A_GIMME, 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_bang), "bang", 0);
    class_addmethod(klass, reinterpret_cast<method>(qmw_uncertainty_assist), "assist", A_CANT, 0);
    class_register(CLASS_BOX, klass);
    qmw_uncertainty_class = klass;
}
