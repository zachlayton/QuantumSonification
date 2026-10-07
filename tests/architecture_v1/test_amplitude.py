"""Selected amplitude mappings around the actual transition engine and router."""
from dataclasses import replace

import numpy as np
import pytest

from qmw.architecture_v1.adapters import operator_feature, state_features, transition_features
from qmw.architecture_v1.amplitude import TransitionAmplitudeProjector
from qmw.architecture_v1.contracts import (
    BasisMetadata, ClockStamp, FeatureFrame, FeatureId, FeatureValue, MappingSpec,
    Provenance, RouteSpec, RoutingPreset,
)
from qmw.architecture_v1.router import SonificationRouter
from qmw.core.state_frame import QuantumStateFrame
from qmw.core.transition import FrameContext, QuantumUnits, TransitionEngine


def scalar(value, *, quantity="matrix_element_magnitude", units="operator_unit",
           path="source.value", uncertainty=None):
    p = Provenance("record:1", path, "declared_source", "1", {}, units, "none",
                   BasisMetadata("coordinate", 2, "computational"),
                   ClockStamp(0.1, "s", "simulation", "elapsed", "run:1"),
                   "numpy", "fixture")
    return FeatureValue(FeatureId(path, quantity), value, p, uncertainty=uncertainty)


def actual_transition_features():
    c = FrameContext("amplitude-test", 3, 0.1, 0.01, "computational")
    units = QuantumUnits(operator_unit="dipole_model")
    rho = np.diag([0.75, 0.25]).astype(complex)
    h = np.diag([0.0, 2.0])
    a = np.array([[0.0, 2.0j], [-2.0j, 0.0]])
    state = QuantumStateFrame(c.time, c.dt, rho, h, c.source_id)
    sources = state_features(state, c, units)
    transition = TransitionEngine(units=units).process(h, a, rho, c)
    features = transition_features(transition, sources.get("quantum.state.rho"),
                                   sources.get("quantum.state.hamiltonian"),
                                   operator_feature(a, c, units))
    return rho, a, transition, features


@pytest.mark.parametrize("source,raw,units,expected", [
    ("matrix_element_magnitude", 2.0, "dipole_model", 0.5),
    ("state_weighted_magnitude", np.sqrt(0.75)*2, "dipole_model", np.sqrt(0.75)/2),
    ("diagnostic_activity", 3.0, "dipole_model^2", 0.75),
])
def test_actual_transition_selectable_sources_preserve_raw_values(source, raw, units, expected):
    rho, a, transition, features = actual_transition_features()
    selected = features.get(f"transition.n0.m1.{source}")
    out = TransitionAmplitudeProjector(source, reference=4, reference_units=units).project(selected)
    assert selected.value == pytest.approx(raw)
    assert out.value == pytest.approx(expected)
    assert out.id == FeatureId("note.amplitude", "excitation_amplitude")
    assert out.units == "1"
    assert out.provenance.parents == (selected.provenance,)
    assert out.provenance.clock == selected.provenance.clock
    assert out.provenance.basis == selected.provenance.basis
    assert out.provenance.backend == selected.provenance.backend
    assert out.provenance.parameters["selected_source"]["quantity"] == source
    assert out.provenance.parameters["selection_probability"] == "not_used"
    if source != "matrix_element_magnitude":
        assert len(out.provenance.parents[0].parents) == 2
    np.testing.assert_array_equal(rho, np.diag([0.75, 0.25]))
    np.testing.assert_array_equal(a, [[0, 2j], [-2j, 0]])
    assert len(transition.edges) == 2


def test_source_quantity_must_match_and_probabilities_cannot_be_implicit_amplitude():
    projector = TransitionAmplitudeProjector("matrix_element_magnitude", reference=1,
                                             reference_units="1")
    with pytest.raises(ValueError, match="quantity"):
        projector.project(scalar(0.5, quantity="event_probability", units="1"))
    with pytest.raises(ValueError, match="source"):
        TransitionAmplitudeProjector("event_probability", reference=1, reference_units="1")


@pytest.mark.parametrize("reference", [0, -1, float("nan"), float("inf"), True])
def test_reference_must_be_positive_finite_and_not_boolean(reference):
    with pytest.raises(ValueError, match="reference"):
        TransitionAmplitudeProjector("matrix_element_magnitude", reference=reference,
                                     reference_units="operator_unit")


def test_reference_requires_explicit_matching_units():
    with pytest.raises(ValueError, match="units"):
        TransitionAmplitudeProjector("matrix_element_magnitude", reference=1)
    projector = TransitionAmplitudeProjector("matrix_element_magnitude", reference=1,
                                             reference_units="N")
    with pytest.raises(ValueError, match="units"):
        projector.project(scalar(1, units="effective_force"))


@pytest.mark.parametrize("value", [-0.1, True, 0.2j, [0.1], "0.2"])
def test_invalid_scalar_amplitude_is_rejected(value):
    projector = TransitionAmplitudeProjector("matrix_element_magnitude", reference=1,
                                             reference_units="operator_unit")
    with pytest.raises(ValueError, match="nonnegative real scalar"):
        projector.project(scalar(value))


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_nonfinite_values_are_rejected_at_shared_admission(value):
    with pytest.raises(ValueError, match="nonfinite"):
        scalar(value)


def test_missing_experimental_observable_is_rejected_without_fabrication():
    f = scalar(0.2, quantity="amplitude_estimate", units="calibrated_signal")
    absent = replace(f, value=None, availability="missing", reason="no amplitude estimate supplied")
    projector = TransitionAmplitudeProjector("experimental_amplitude", reference=1,
                                             reference_units="calibrated_signal")
    with pytest.raises(ValueError, match="no amplitude estimate"):
        projector.project(absent)


def test_zero_silence_clipping_and_overflow_rejection_are_explicit():
    projector = TransitionAmplitudeProjector("matrix_element_magnitude", reference=2,
                                             reference_units="operator_unit")
    assert projector.project(scalar(0)).value == 0
    out = projector.project(scalar(3))
    assert out.value == 1
    assert out.provenance.parameters["evaluation"]["clipped"] is True
    strict = TransitionAmplitudeProjector("matrix_element_magnitude", reference=2,
                                          reference_units="operator_unit", overflow="reject")
    with pytest.raises(ValueError, match="reference"):
        strict.project(scalar(3))
    # Comparing before division also avoids an overflow at extreme calibrations.
    tiny = TransitionAmplitudeProjector("matrix_element_magnitude", reference=1e-300,
                                        reference_units="operator_unit")
    assert tiny.project(scalar(1e300)).value == 1


def test_peak_requires_explicit_cohort_and_retains_all_dependencies():
    _, _, _, frame = actual_transition_features()
    selected = frame.get("transition.n1.m0.state_weighted_magnitude")
    projector = TransitionAmplitudeProjector("state_weighted_magnitude", normalization="frame_peak")
    with pytest.raises(ValueError, match="FeatureFrame"):
        projector.project(selected)
    out = projector.project(selected, frame=frame)
    assert out.value == pytest.approx(1/np.sqrt(3))
    assert len(out.provenance.parents) == 2
    params = out.provenance.parameters
    assert params["evaluation"]["normalization_denominator"] == pytest.approx(np.sqrt(3))
    assert params["source_frame_id"] == frame.frame_id
    assert len(params["input_ids"]) == 2
    with pytest.raises(ValueError, match="present"):
        projector.project(selected, frame=FeatureFrame("empty", ()))


def test_peak_zero_cohort_is_silent_and_mixed_units_basis_or_clock_are_rejected():
    a = scalar(0, path="a")
    b = scalar(0, path="b")
    projector = TransitionAmplitudeProjector("matrix_element_magnitude", normalization="frame_peak")
    frame = FeatureFrame("zero", (a, b))
    assert projector.project(a, frame=frame).value == 0
    changes = [{"units": "wrong"}, {"basis": BasisMetadata("other", 2, "computational")},
               {"clock": replace(b.provenance.clock, value=0.2)}, {"backend": "different"}]
    for change in changes:
        bad = replace(b, provenance=replace(b.provenance, **change))
        with pytest.raises(ValueError, match="cohort"):
            projector.project(a, frame=FeatureFrame("mixed", (a, bad)))


def test_unit_interval_mode_is_identity_for_declared_dimensionless_bounded_sources():
    projector = TransitionAmplitudeProjector("decay_survival", normalization="already_unit_interval")
    f = scalar(0.25, quantity="survival_probability", units="1")
    assert projector.project(f).value == 0.25
    with pytest.raises(ValueError, match="unit interval"):
        projector.project(replace(f, value=1.2))
    with pytest.raises(ValueError, match="dimensionless"):
        projector.project(replace(f, provenance=replace(f.provenance, units="s")))


def test_survival_envelope_curve_is_an_explicit_musical_transform():
    f = scalar(0.25, quantity="survival_probability", units="1")
    projector = TransitionAmplitudeProjector("decay_survival", normalization="already_unit_interval",
                                             curve="sqrt_survival")
    out = projector.project(f)
    assert out.value == 0.5
    assert out.provenance.parameters["mapping_parameters"]["curve"] == "sqrt_survival"
    assert out.provenance.evidence == "musical_mapping"
    assert projector.project(replace(f, value=0)).value == 0
    with pytest.raises(ValueError, match="survival"):
        TransitionAmplitudeProjector("diagnostic_activity", normalization="frame_peak", curve="sqrt_survival")


@pytest.mark.parametrize("source,quantity,units,value,reference,expected", [
    ("lorentz_force_magnitude", "force_magnitude", "effective_force", 3, 4, 0.75),
    ("decay_envelope", "decay_envelope", "1", 0.25, 1, 0.25),
    ("experimental_amplitude", "amplitude_estimate", "calibrated_signal", 0.6, 2, 0.3),
])
def test_nontransition_admission_seams_preserve_declared_model_units(source, quantity, units,
                                                                    value, reference, expected):
    f = scalar(value, quantity=quantity, units=units)
    projector = TransitionAmplitudeProjector(source, reference=reference, reference_units=units)
    out = projector.project(f)
    assert out.value == pytest.approx(expected)
    assert out.provenance.parents[0].units == units
    assert out.provenance.parameters["mapping_parameters"]["reference_units"] == units


def test_experimental_uncertainty_is_retained_without_invented_propagation():
    uncertainty = {"kind": "covariance_reference", "uri": "dataset:cov:3"}
    f = scalar(0.6, quantity="amplitude_estimate", units="calibrated_signal", uncertainty=uncertainty)
    out = TransitionAmplitudeProjector("experimental_amplitude", reference=2,
                                        reference_units="calibrated_signal").project(f)
    assert out.provenance.parameters["input_uncertainties"] == (f.uncertainty,)
    assert out.uncertainty["status"] == "not_propagated"
    assert out.uncertainty["inputs"][0]["uncertainty"]["uri"] == "dataset:cov:3"
    assert out.uncertainty["inputs"][0]["units"] == "calibrated_signal"


def test_projected_amplitude_routes_independently_from_body_and_rejects_conflict():
    _, _, _, frame = actual_transition_features()
    selected = frame.get("transition.n0.m1.matrix_element_magnitude")
    out = TransitionAmplitudeProjector("matrix_element_magnitude", reference=4,
                                        reference_units="dipole_model").project(selected)
    body = FeatureValue(FeatureId("body.modal_weights", "modal_probability_weights", "vector"),
                        [0.25, 0.75], replace(selected.provenance, units="1"))
    def route(f, destination):
        return RouteSpec(destination, f.id, MappingSpec("identity", "1", "identity", (f.id,),
                                                       "1", "none"))
    router = SonificationRouter(RoutingPreset("separate", (route(out, "note.amplitude"),
                                                            route(body, "body.modal_weights"))))
    result = router.route(FeatureFrame("junction", (out, body)))
    assert result.values["note.amplitude"].value == 0.5
    np.testing.assert_array_equal(result.values["body.modal_weights"].value, [0.25, 0.75])
    other = scalar(0.25, quantity="excitation_amplitude", units="1", path="other.amplitude")
    with pytest.raises(ValueError, match="destination.*note.amplitude"):
        router.set_preset(RoutingPreset("conflict", (route(out, "note.amplitude"),
                                                     route(other, "note.amplitude"))))


def test_mapping_spec_is_inspectable_and_output_identity_depends_on_policy():
    f = scalar(0.5)
    p = TransitionAmplitudeProjector("matrix_element_magnitude", reference=1,
                                    reference_units="operator_unit", mapping_id="calibration-1", version="2")
    spec = p.mapping_spec(f)
    assert isinstance(spec, MappingSpec)
    assert spec.input_ids == (f.id,)
    assert spec.parameters["reference"] == 1
    out = p.project(f)
    assert out.provenance.version == "2"
    assert out.provenance.parameters["mapping_id"] == "calibration-1"
    assert out.provenance.digest == p.project(f).provenance.digest
    different = TransitionAmplitudeProjector("matrix_element_magnitude", reference=2,
                                             reference_units="operator_unit").project(f)
    assert out.provenance.record_id != different.provenance.record_id


@pytest.mark.parametrize("kwargs", [
    {"normalization": "automatic"}, {"normalization": "frame_peak", "reference": 2},
    {"normalization": "already_unit_interval", "reference_units": "1"},
    {"normalization": "frame_peak", "overflow": "silent"},
    {"normalization": "frame_peak", "curve": "automatic"},
])
def test_unsupported_or_irrelevant_configuration_is_rejected(kwargs):
    with pytest.raises(ValueError):
        TransitionAmplitudeProjector("matrix_element_magnitude", **kwargs)
