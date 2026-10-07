"""Known resource states, basis/tensor contracts, and unsupported capabilities."""
from dataclasses import replace

import numpy as np
import pytest

from qmw.architecture_v1.basis import BasisProjector
from qmw.architecture_v1.contracts import BasisMetadata, ClockStamp, FeatureId, FeatureValue, Provenance
from qmw.architecture_v1.resources import ResourceAnalyzer


def state_feature(value, *, basis=None, uncertainty=None):
    d = np.shape(value)[0]
    p = Provenance("rho:fixture", "quantum.state.rho", "declared_state", "1", {}, "1", "none",
                   basis or BasisMetadata("computational", d, "computational"),
                   ClockStamp(0.2, "s", "simulation", "elapsed", "resource-fixture"),
                   "numpy", "fixture")
    return FeatureValue(FeatureId("quantum.state.rho", "density_matrix", "matrix"), value, p,
                        uncertainty=uncertainty)


def pure(psi):
    psi = np.asarray(psi, complex)
    return np.outer(psi, psi.conj())


def metric(frame, name):
    return frame.get("resources." + name)


def value(frame, name):
    return metric(frame, name).require_available()


DEFAULT = ("purity", "entropy_nats", "coherence_l1", "coherence_relative_entropy_nats")
ENTANGLEMENT = ("negativity", "log_negativity", "reduced_entropy_nats", "entanglement_entropy_nats")
MAGIC = ("stabilizer_renyi2_bits", "stabilizer_diagnostics")


@pytest.mark.parametrize("rho,purity,entropy,l1,relative", [
    (np.diag([1., 0.]), 1., 0., 0., 0.),
    (np.eye(2)/2, 0.5, np.log(2), 0., 0.),
    (np.ones((2, 2))/2, 1., 0., 1., np.log(2)),
    (np.ones((3, 3))/3, 1., 0., 2., np.log(3)),
])
def test_known_purity_entropy_and_basis_coherence(rho, purity, entropy, l1, relative):
    frame = ResourceAnalyzer().analyze(state_feature(rho))
    for name, expected in zip(DEFAULT, (purity, entropy, l1, relative)):
        assert value(frame, name) == pytest.approx(expected, abs=1e-12)
    assert metric(frame, "entropy_nats").units == "nat"
    assert metric(frame, "coherence_l1").units == "1"


def test_coherence_follows_basis_projection_without_mutating_authority():
    original = state_feature(np.ones((2, 2))/2)
    before = original.value.copy()
    projector = BasisProjector()
    basis = projector.qft(2, original.provenance)
    projected = projector.project(original, basis)
    transformed = FeatureValue(original.id, projected.rho, projected.provenance)
    analyzer = ResourceAnalyzer()
    computational = analyzer.analyze(original)
    fourier = analyzer.analyze(transformed)
    assert value(computational, "coherence_l1") == pytest.approx(1)
    assert value(fourier, "coherence_l1") == pytest.approx(0, abs=1e-12)
    assert value(fourier, "purity") == pytest.approx(1)
    assert metric(fourier, "coherence_l1").provenance.basis == basis.metadata
    np.testing.assert_array_equal(original.value, before)


def test_bell_state_has_entanglement_but_zero_stabilizer_magic():
    rho = pure(np.array([1, 0, 0, 1])/np.sqrt(2))
    frame = ResourceAnalyzer().analyze(state_feature(rho), metrics=ENTANGLEMENT + MAGIC,
                                      subsystem_dimensions=(2, 2), partition=(0,))
    assert value(frame, "negativity") == pytest.approx(0.5)
    assert value(frame, "log_negativity") == pytest.approx(1)
    assert value(frame, "reduced_entropy_nats") == pytest.approx(np.log(2))
    assert value(frame, "entanglement_entropy_nats") == pytest.approx(np.log(2))
    assert value(frame, "stabilizer_renyi2_bits") == pytest.approx(0, abs=1e-12)
    assert value(frame, "stabilizer_diagnostics")["signed_stabilizer_count"] == 4
    assert value(frame, "stabilizer_diagnostics")["is_stabilizer_within_tolerance"]


def test_product_state_has_no_bipartite_entanglement():
    rho = pure(np.kron([0, 1], np.array([1, 1])/np.sqrt(2)))
    frame = ResourceAnalyzer().analyze(state_feature(rho), metrics=ENTANGLEMENT,
                                      subsystem_dimensions=(2, 2), partition=(1,))
    for name in ENTANGLEMENT:
        assert value(frame, name) == pytest.approx(0, abs=1e-12)


def test_classically_correlated_mixed_state_does_not_gain_entanglement_label():
    rho = np.diag([0.5, 0., 0., 0.5])
    frame = ResourceAnalyzer().analyze(state_feature(rho), metrics=ENTANGLEMENT + MAGIC,
                                      subsystem_dimensions=(2, 2), partition=(0,))
    assert value(frame, "negativity") == 0
    assert value(frame, "log_negativity") == 0
    assert value(frame, "reduced_entropy_nats") == pytest.approx(np.log(2))
    unsupported = metric(frame, "entanglement_entropy_nats")
    assert unsupported.availability == "unsupported" and unsupported.value is None
    assert "globally pure" in unsupported.reason
    for name in MAGIC:
        assert metric(frame, name).availability == "unsupported"
        assert "mixed" in metric(frame, name).reason


def test_mixed_entangled_state_negativity_agrees_with_known_werner_threshold():
    bell = pure(np.array([1, 0, 0, 1])/np.sqrt(2))
    for p in (0.2, 0.5, 1.0):
        rho = p*bell + (1-p)*np.eye(4)/4
        frame = ResourceAnalyzer().analyze(state_feature(rho), metrics=("negativity",),
                                          subsystem_dimensions=(2, 2), partition=(1,))
        assert value(frame, "negativity") == pytest.approx(max(0., (3*p-1)/4), abs=1e-12)


def test_four_qubit_ghz_supports_noncontiguous_bipartition_and_stabilizer_count():
    psi = np.zeros(16); psi[[0, 15]] = 1/np.sqrt(2)
    frame = ResourceAnalyzer().analyze(state_feature(pure(psi)), metrics=ENTANGLEMENT + MAGIC,
                                      subsystem_dimensions=(2, 2, 2, 2), partition=(0, 2))
    assert value(frame, "negativity") == pytest.approx(0.5)
    assert value(frame, "entanglement_entropy_nats") == pytest.approx(np.log(2))
    assert value(frame, "stabilizer_renyi2_bits") == pytest.approx(0, abs=1e-12)
    assert value(frame, "stabilizer_diagnostics")["signed_stabilizer_count"] == 16


def test_tensor_order_uses_q0_as_least_significant_subsystem():
    rho = np.diag([0.3, 0.7, 0., 0.])
    analyzer = ResourceAnalyzer()
    q0 = analyzer.analyze(state_feature(rho), metrics=("reduced_entropy_nats",),
                          subsystem_dimensions=(2, 2), partition=(0,))
    q1 = analyzer.analyze(state_feature(rho), metrics=("reduced_entropy_nats",),
                          subsystem_dimensions=(2, 2), partition=(1,))
    assert value(q0, "reduced_entropy_nats") == pytest.approx(-0.3*np.log(0.3)-0.7*np.log(0.7))
    assert value(q1, "reduced_entropy_nats") == 0


@pytest.mark.parametrize("dimensions,indices,negativity", [
    ((2, 3), [0, 3], 0.5), ((3, 3), [0, 4, 8], 1.),
])
def test_qudit_bipartitions_use_declared_dimension_not_qubit_assumptions(dimensions, indices, negativity):
    psi = np.zeros(np.prod(dimensions)); psi[indices] = 1/np.sqrt(len(indices))
    frame = ResourceAnalyzer().analyze(state_feature(pure(psi)), metrics=("negativity",) + MAGIC,
                                      subsystem_dimensions=dimensions, partition=(0,))
    assert value(frame, "negativity") == pytest.approx(negativity)
    assert metric(frame, "stabilizer_renyi2_bits").availability == "unsupported"
    assert "qubit" in metric(frame, "stabilizer_renyi2_bits").reason


def test_t_state_magic_formula_additivity_and_clifford_invariance():
    psi = np.array([1, np.exp(1j*np.pi/4)])/np.sqrt(2)
    h = np.array([[1, 1], [1, -1]])/np.sqrt(2)
    analyzer = ResourceAnalyzer()
    t = analyzer.analyze(state_feature(pure(psi)), metrics=MAGIC, subsystem_dimensions=(2,))
    rotated = analyzer.analyze(state_feature(pure(h@psi)), metrics=MAGIC, subsystem_dimensions=(2,))
    product = analyzer.analyze(state_feature(pure(np.kron(psi, psi))), metrics=MAGIC,
                               subsystem_dimensions=(2, 2))
    expected = np.log2(4/3)
    assert value(t, "stabilizer_renyi2_bits") == pytest.approx(expected)
    assert value(rotated, "stabilizer_renyi2_bits") == pytest.approx(expected)
    assert value(product, "stabilizer_renyi2_bits") == pytest.approx(2*expected)
    assert not value(t, "stabilizer_diagnostics")["is_stabilizer_within_tolerance"]
    assert value(t, "stabilizer_diagnostics")["signed_stabilizer_count"] == 1


def test_magic_and_contextuality_require_distinct_adequate_information():
    f = state_feature(pure(np.array([1, np.exp(1j*np.pi/4)])/np.sqrt(2)))
    frame = ResourceAnalyzer().analyze(f, metrics=MAGIC + ("contextuality",),
                                      subsystem_dimensions=(2,))
    assert value(frame, "stabilizer_renyi2_bits") > 0
    c = metric(frame, "contextuality")
    assert c.availability == "unsupported" and c.value is None
    assert "measurement scenario" in c.reason


def test_optional_pauli_enumeration_cap_is_reported_without_blocking_cheap_metrics():
    rho = np.zeros((32, 32)); rho[0, 0] = 1
    frame = ResourceAnalyzer().analyze(state_feature(rho), metrics=DEFAULT + MAGIC,
                                      subsystem_dimensions=(2,)*5)
    assert value(frame, "purity") == 1
    assert metric(frame, "stabilizer_renyi2_bits").availability == "unsupported"
    assert "cap" in metric(frame, "stabilizer_renyi2_bits").reason


def test_tensor_structure_is_never_inferred_and_transformed_basis_is_not_factorized_implicitly():
    f = state_feature(np.eye(4)/4)
    without = ResourceAnalyzer().analyze(f, metrics=("negativity", "stabilizer_renyi2_bits"))
    assert all(item.availability == "unsupported" for item in without.features)
    basis = replace(f.provenance.basis, kind="hamiltonian", basis_id="energy")
    transformed = replace(f, provenance=replace(f.provenance, basis=basis))
    frame = ResourceAnalyzer().analyze(transformed, metrics=("negativity", "stabilizer_renyi2_bits"),
                                      subsystem_dimensions=(2, 2), partition=(0,))
    assert all(item.availability == "unsupported" for item in frame.features)
    assert "computational" in metric(frame, "negativity").reason


@pytest.mark.parametrize("dimensions,partition", [
    ((2, 3), (0,)), ((2, 2), (2,)), ((2, 2), (0, 0)), ((2, 2), ()),
    ((2, 2), (0, 1)), ((2, 2), (True,)), ((True, 4), (0,)), ((4,), (0,)),
])
def test_invalid_partitions_or_factorizations_are_rejected(dimensions, partition):
    with pytest.raises(ValueError, match="dimension|partition"):
        ResourceAnalyzer().analyze(state_feature(np.eye(4)/4), metrics=("negativity",),
                                   subsystem_dimensions=dimensions, partition=partition)


@pytest.mark.parametrize("rho", [np.diag([1.2, -0.2]), np.diag([0.2, 0.2]), [[1, 1], [0, 0]]])
def test_invalid_density_rejected_by_canonical_spectral_validation(rho):
    with pytest.raises(ValueError, match="positive|trace|Hermitian"):
        ResourceAnalyzer().analyze(state_feature(rho))


def test_missing_wrong_units_quantity_shape_and_basis_dimension_reject():
    f = state_feature(np.eye(2)/2)
    cases = [
        replace(f, value=None, availability="missing", reason="hardware counts only"),
        replace(f, id=FeatureId("correlations", "correlation_matrix", "matrix")),
        replace(f, provenance=replace(f.provenance, units="GeV")),
        replace(f, value=np.zeros((2, 3))),
        replace(f, provenance=replace(f.provenance, basis=BasisMetadata("wrong", 4, "computational"))),
    ]
    for case in cases:
        with pytest.raises(ValueError):
            ResourceAnalyzer().analyze(case)


def test_output_provenance_keeps_formula_clock_source_uncertainty_and_immutable_dependencies():
    f = state_feature(np.ones((2, 2))/2, uncertainty={"kind": "covariance_reference", "uri": "cov:rho"})
    frame = ResourceAnalyzer().analyze(f)
    out = metric(frame, "coherence_relative_entropy_nats")
    assert len(out.provenance.parents) == 2
    assert out.provenance.clock == f.provenance.clock
    assert out.provenance.backend == f.provenance.backend
    assert "1311.0275" in out.provenance.parameters["definition_source"]
    assert out.uncertainty["status"] == "not_propagated"
    assert out.uncertainty["input"]["uri"] == "cov:rho"
    assert out.provenance.digest == metric(ResourceAnalyzer().analyze(f), out.id.quantity).provenance.digest
    with pytest.raises(TypeError):
        out.provenance.parameters["formula"] = "modified"
    assert not f.value.flags.writeable


@pytest.mark.parametrize("kwargs", [{"max_dimension": 1}, {"max_magic_qubits": 0},
                                    {"tolerance": 0}, {"tolerance": float("nan")}])
def test_invalid_analyzer_configuration_rejected(kwargs):
    with pytest.raises(ValueError):
        ResourceAnalyzer(**kwargs)


def test_dimension_cap_unknown_and_duplicate_metrics_reject():
    f = state_feature(np.eye(4)/4)
    with pytest.raises(ValueError, match="dimension cap"):
        ResourceAnalyzer(max_dimension=2).analyze(f)
    for metrics in [("magic_from_correlation",), ("purity", "purity")]:
        with pytest.raises(ValueError, match="metric"):
            ResourceAnalyzer().analyze(f, metrics=metrics)
