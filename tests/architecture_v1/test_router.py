"""Policy gates at the feature-to-musical-mapping boundary."""
from dataclasses import replace

import numpy as np
import pytest

from qmw.architecture_v1.contracts import (
    BasisMetadata, ClockStamp, FeatureFrame, FeatureId, FeatureValue,
    MappingSpec, Provenance, RouteSpec, RoutingMode, RoutingPreset,
)
from qmw.architecture_v1.router import FeatureBus, SonificationRouter


def feature(path="transition.amplitude", value=0.4, *, units="1", kind="scalar", parents=()):
    source = Provenance(
        "quantum:1", path, "source_observation", "1", {}, units, "none",
        BasisMetadata("computational", 16, "computational"),
        ClockStamp(0.5, "s", "simulation", "elapsed", "run:1"),
        "numpy", "simulated", parents,
    )
    return FeatureValue(FeatureId(path, path.rsplit(".", 1)[-1], kind), value, source)


def route(source, destination="note.amplitude", *, operation="identity", inputs=None,
          units=None, parameters=None, active=True):
    ids = (source.id,) if inputs is None else tuple(f.id for f in inputs)
    mapping = MappingSpec("test-map", "2", operation, ids, units or source.units,
                          "declared_test_normalization", parameters or {})
    return RouteSpec(destination, source.id, mapping, active)


def test_analysis_rejects_second_amplitude_source_before_route_and_preserves_preset():
    a, b = feature(), feature("force.magnitude", 0.3)
    valid = RoutingPreset("one", (route(a),))
    router = SonificationRouter(valid)
    conflict = RoutingPreset("two", (route(a), route(b)))
    with pytest.raises(ValueError, match="destination.*note.amplitude"):
        router.set_preset(conflict)
    assert router.preset is valid
    assert router.route(FeatureFrame("frame:1", (a, b))).values["note.amplitude"].value == 0.4


@pytest.mark.parametrize("mode", tuple(RoutingMode))
def test_no_mode_silently_overwrites_active_destination(mode):
    a, b = feature(), feature("other.amplitude", 0.2)
    with pytest.raises(ValueError, match="destination"):
        SonificationRouter(RoutingPreset("conflict", (route(a), route(b))), mode)


def test_unused_inactive_destinations_and_separate_modal_body_are_allowed():
    a, b = feature(), feature("density.modal_weights", np.array([0.2, 0.8]), kind="vector")
    unavailable = feature("unused.amplitude")
    router = SonificationRouter(RoutingPreset("split", (
        route(a), route(b, "body.modal_weights"), route(unavailable, active=False),
    )))
    out = router.route(FeatureFrame("frame:1", (a, b)))
    assert set(out.values) == {"note.amplitude", "body.modal_weights"}
    assert out.values["note.amplitude"].value == 0.4
    np.testing.assert_array_equal(out.values["body.modal_weights"].value, [0.2, 0.8])
    with pytest.raises(TypeError):
        out.values["note.amplitude"] = a
    with pytest.raises(ValueError):
        out.values["body.modal_weights"].value.setflags(write=True)
    assert SonificationRouter(RoutingPreset("silent", ())).route(FeatureFrame("empty", ())).values == {}


def test_analysis_accepts_one_derived_source_with_multiple_physical_ancestors():
    rho, operator = feature("rho.population", 0.25), feature("operator.strength", 0.8)
    weighted = feature("transition.weighted_amplitude", 0.4,
                       parents=(rho.provenance, operator.provenance))
    out = SonificationRouter(RoutingPreset("one-derived", (route(weighted),))).route(
        FeatureFrame("frame:1", (weighted,)))
    p = out.values["note.amplitude"].provenance
    assert p.parents == (weighted.provenance,)
    assert p.parents[0].parents == (rho.provenance, operator.provenance)
    assert p.parameters["mapping_id"] == "test-map"
    assert p.parameters["source_frame_id"] == "frame:1"
    assert p.parameters["primary_source"]["path"] == weighted.id.path
    assert p.version == "2"
    assert p.clock == weighted.provenance.clock
    assert p.basis == weighted.provenance.basis
    assert p.backend == "numpy"


@pytest.mark.parametrize("mode", (RoutingMode.ANALYSIS, RoutingMode.INSTRUMENT))
def test_compound_musical_mapping_requires_explicit_composite_mode(mode):
    a, b = feature(), feature("force.magnitude", 0.2)
    compound = route(a, operation="weighted_sum", inputs=(a, b),
                     parameters={"input_units": ("1", "1"), "weights": (0.25, 0.75)})
    with pytest.raises(ValueError, match="COMPOSITE"):
        SonificationRouter(RoutingPreset("compound", (compound,)), mode)


def test_composite_preserves_all_inputs_and_declared_parameters():
    a, b = feature(), feature("force.magnitude", 0.2)
    compound = route(a, operation="weighted_sum", inputs=(a, b),
                     parameters={"input_units": ("1", "1"), "weights": (0.25, 0.75)})
    router = SonificationRouter(RoutingPreset("compound", (compound,)), RoutingMode.COMPOSITE)
    output = router.route(FeatureFrame("frame:2", (a, b))).values["note.amplitude"]
    assert output.value == pytest.approx(0.25)
    assert output.provenance.parents == (a.provenance, b.provenance)
    assert output.provenance.parameters["mapping_parameters"]["weights"] == (0.25, 0.75)
    assert output.provenance.parameters["routing_mode"] == "COMPOSITE"


def test_feature_bus_snapshot_is_immutable_and_failed_publish_is_atomic():
    raw = np.array([0.25, 0.75])
    f = feature("density.weights", raw, kind="vector")
    first = FeatureFrame("first", (f,))
    bus = FeatureBus(first)
    snapshot = bus.snapshot()
    raw[0] = 99
    np.testing.assert_array_equal(snapshot.get(f.id).value, [0.25, 0.75])
    with pytest.raises(ValueError, match="scalar"):
        bus.publish(FeatureFrame("bad", (feature(value=[0.1, 0.2]),)))
    assert bus.snapshot() is first
    bus.publish(FeatureFrame("second", (feature(),)))
    assert snapshot.frame_id == "first"
    assert bus.snapshot().frame_id == "second"
    with pytest.raises(ValueError):
        bus.get(FeatureId("transition.amplitude", "wrong_quantity"))
    with pytest.raises(ValueError, match="published"):
        FeatureBus().snapshot()


def test_state_bus_adaptation_requires_explicit_extractor_and_no_implicit_state_change():
    from qmw.core.state_bus import StateBus

    state_bus, feature_bus = StateBus(), FeatureBus()
    observed = []
    raw = {"amplitude": 0.25}

    def extract(state):
        observed.append(state)
        return FeatureFrame("adapted", (feature(value=state["amplitude"]),))

    callback = feature_bus.connect(state_bus, extract)
    state_bus.publish(raw)
    assert feature_bus.get("transition.amplitude").value == 0.25
    assert observed == [raw]
    assert raw == {"amplitude": 0.25}
    state_bus.unsubscribe(callback)
    state_bus.publish({"amplitude": 0.5})
    assert feature_bus.get("transition.amplitude").value == 0.25


def test_missing_unavailable_and_incompatible_typed_inputs_are_rejected():
    a = feature()
    router = SonificationRouter(RoutingPreset("required", (route(a),)))
    with pytest.raises(KeyError):
        router.route(FeatureFrame("empty", ()))
    missing = replace(a, value=None, availability="missing", reason="not measured")
    with pytest.raises(ValueError, match="not measured"):
        router.route(FeatureFrame("missing", (missing,)))
    wrong = replace(a, id=FeatureId(a.id.path, "probability"))
    with pytest.raises(ValueError, match="quantity/type"):
        router.route(FeatureFrame("wrong", (wrong,)))


def test_identity_never_relabels_units_and_affine_requires_declared_input_units():
    energy = feature("transition.gap", 2.0, units="J")
    unsafe = SonificationRouter(RoutingPreset("bad-unit", (route(energy, "note.pitch", units="Hz"),)))
    with pytest.raises(ValueError, match="units"):
        unsafe.route(FeatureFrame("frame", (energy,)))
    with pytest.raises(ValueError, match="input_units"):
        SonificationRouter(RoutingPreset("undeclared", (route(energy, "note.pitch", operation="affine",
            units="Hz", parameters={"scale": 10.0, "offset": 100.0}),)))
    mapped = route(energy, "note.pitch", operation="affine", units="Hz",
                   parameters={"input_units": ("J",), "scale": 10.0, "offset": 100.0})
    result = SonificationRouter(RoutingPreset("energy-to-pitch", (mapped,)), RoutingMode.INSTRUMENT).route(
        FeatureFrame("frame", (energy,))).values["note.pitch"]
    assert result.value == 120.0 and result.units == "Hz"
    wrong = replace(energy, provenance=replace(energy.provenance, units="eV"))
    with pytest.raises(ValueError, match="units"):
        SonificationRouter(RoutingPreset("correct-source-only", (mapped,))).route(FeatureFrame("wrong", (wrong,)))


@pytest.mark.parametrize("value,destination,kind", [
    (1.2, "note.amplitude", "scalar"), (-0.1, "note.amplitude", "scalar"),
    ([0.2], "note.amplitude", "vector"), (0.2, "body.modal_weights", "scalar"),
    ([-0.1, 0.2], "body.modal_weights", "vector"),
])
def test_note_amplitude_and_body_weights_require_separate_normalized_shapes(value, destination, kind):
    a = feature(value=value, kind=kind)
    router = SonificationRouter(RoutingPreset("shape", (route(a, destination),)))
    with pytest.raises(ValueError, match="note.amplitude|body.modal_weights"):
        router.route(FeatureFrame("frame", (a,)))


def test_peak_normalization_zero_behavior_and_no_hidden_gain():
    a = feature("density.weights", np.array([2.0, 4.0]), kind="vector")
    norm = route(a, "body.modal_weights", operation="normalize_peak",
                 parameters={"input_units": ("1",), "denominator": "frame_peak"})
    router = SonificationRouter(RoutingPreset("normalize", (norm,)))
    output = router.route(FeatureFrame("frame", (a,))).values["body.modal_weights"]
    np.testing.assert_array_equal(output.value, [0.5, 1.0])
    assert output.provenance.parameters["evaluation"]["normalization_denominator"] == 4.0
    zeros = replace(a, value=np.zeros(2))
    np.testing.assert_array_equal(router.route(FeatureFrame("zeros", (zeros,))).values["body.modal_weights"].value, [0, 0])


def test_registry_rejects_unknown_operation_extra_parameters_and_shape_broadcasting():
    a, b = feature(), feature("other.vector", np.array([0.1, 0.2]), kind="vector")
    with pytest.raises(ValueError, match="operation"):
        SonificationRouter(RoutingPreset("unsafe", (route(a, operation="__import__('os')"),)))
    with pytest.raises(ValueError, match="parameters"):
        SonificationRouter(RoutingPreset("hidden", (route(a, parameters={"gain": 2}),)))
    mixed = route(a, operation="sum", inputs=(a, b), parameters={"input_units": ("1", "1")})
    router = SonificationRouter(RoutingPreset("mixed", (mixed,)), RoutingMode.COMPOSITE)
    with pytest.raises(ValueError, match="shape"):
        router.route(FeatureFrame("frame", (a, b)))


def test_failed_mode_change_does_not_alter_existing_composite_preset():
    a, b = feature(), feature("other.amplitude", 0.2)
    preset = RoutingPreset("sum", (route(a, operation="sum", inputs=(a, b),
        parameters={"input_units": ("1", "1")}),))
    router = SonificationRouter(preset, RoutingMode.COMPOSITE)
    with pytest.raises(ValueError, match="COMPOSITE"):
        router.set_preset(preset, mode=RoutingMode.ANALYSIS)
    assert router.mode is RoutingMode.COMPOSITE
    assert router.preset is preset
