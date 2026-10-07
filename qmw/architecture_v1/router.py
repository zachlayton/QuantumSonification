"""Explicit feature-to-musical routing, with no engine or synth side effects.

``FeatureBus`` receives immutable feature snapshots extracted by a caller from
an existing QMW state/event bus. It neither owns nor evolves quantum state.

Every active destination has one route in all modes. ANALYSIS and INSTRUMENT
routes have one declared musical input; selecting an already-derived feature
does not erase its possibly composite physical ancestry. Multiple musical
inputs require COMPOSITE and a declared ``sum`` or ``weighted_sum`` operation.

Mapping parameters are inspectable data, never evaluated code. Non-identity
operations declare ``input_units`` in input order. ``affine`` uses scalar
``scale`` and ``offset`` as a declared unit conversion or perceptual mapping;
offset is in output units and scale has output-units/input-units. ``clip`` and
additive operations preserve units. ``normalize_peak`` produces dimensionless
values with a declared ``denominator``: ``frame_peak`` or a positive calibration
number in input units. Its measured denominator is retained in provenance.
There is no automatic normalization, gain, input broadcasting, or synth logic.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

import numpy as np

from .contracts import (
    FeatureFrame, FeatureId, FeatureValue, MappingSpec, RouteSpec, RoutedFrame,
    RoutingMode, RoutingPreset, finite,
)


OPERATIONS = frozenset({"identity", "affine", "clip", "normalize_peak", "sum", "weighted_sum"})
_SINGLE_INPUT = frozenset({"identity", "affine", "clip", "normalize_peak"})
_PARAMETERS = {
    "identity": frozenset({"input_units"}),
    "affine": frozenset({"input_units", "scale", "offset"}),
    "clip": frozenset({"input_units", "minimum", "maximum"}),
    "normalize_peak": frozenset({"input_units", "denominator"}),
    "sum": frozenset({"input_units"}),
    "weighted_sum": frozenset({"input_units", "weights"}),
}


def _validate_feature(feature: FeatureValue) -> None:
    """Validate the declared kind, including inputs bypassing FeatureBus."""
    if not isinstance(feature, FeatureValue):
        raise ValueError("FeatureBus requires shared FeatureValue contracts")
    if feature.availability != "available":
        return
    kind, value = feature.id.kind, feature.value
    if kind == "record":
        if not isinstance(value, Mapping):
            raise ValueError(f"{feature.id.path}: record requires mapping data")
        return
    if kind == "events":
        if not isinstance(value, tuple):
            raise ValueError(f"{feature.id.path}: events requires an immutable sequence")
        return
    try:
        array = np.asarray(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{feature.id.path}: {kind} requires rectangular numeric data") from exc
    expected = {"scalar": 0, "vector": 1, "matrix": 2}
    if array.dtype.kind not in "biufc" or not np.all(np.isfinite(array)):
        raise ValueError(f"{feature.id.path}: {kind} requires finite numeric data")
    if (kind in expected and array.ndim != expected[kind]) or (kind == "tensor" and array.ndim < 3):
        raise ValueError(f"{feature.id.path}: {kind} has incompatible value shape {array.shape}")


def _validate_frame(frame: FeatureFrame) -> None:
    if not isinstance(frame, FeatureFrame):
        raise ValueError("FeatureBus accepts a shared FeatureFrame, using explicit extraction from native state")
    for feature in frame.features:
        _validate_feature(feature)


class FeatureBus:
    """Latest immutable feature snapshot; publishing replaces it atomically.

    Retained snapshots remain valid after later publications. No private-field
    discovery or implicit conversion of native QMW frames occurs.
    """

    def __init__(self, initial: FeatureFrame | None = None):
        self._latest: FeatureFrame | None = None
        if initial is not None:
            self.publish(initial)

    @property
    def latest(self) -> FeatureFrame | None:
        return self._latest

    def publish(self, frame: FeatureFrame) -> FeatureFrame:
        _validate_frame(frame)
        self._latest = frame
        return frame

    def snapshot(self) -> FeatureFrame:
        if self._latest is None:
            raise ValueError("no feature frame has been published")
        return self._latest

    def get(self, path: str | FeatureId) -> FeatureValue:
        return self.snapshot().get(path)

    def connect(self, state_bus: Any, extractor: Callable[[Any], FeatureFrame]) -> Callable:
        """Subscribe an explicit extractor; returned callback can be unsubscribed.

        The existing StateBus (or another compatible publisher) owns publication.
        The extractor is upstream adapter code, separate from mapping operations;
        it must itself observe the native frame without modifying it.
        """
        subscribe = getattr(state_bus, "subscribe", None)
        if not callable(subscribe) or not callable(extractor):
            raise ValueError("connect requires a subscribable bus and an explicit callable extractor")

        def receive(frame):
            self.publish(extractor(frame))

        subscribe(receive)
        return receive


def _validate_mapping(mapping: MappingSpec) -> None:
    if not isinstance(mapping, MappingSpec):
        raise ValueError("route requires a shared MappingSpec")
    operation, params = mapping.operation, mapping.parameters
    if operation not in OPERATIONS:
        raise ValueError(f"unknown mapping operation: {operation}")
    if not isinstance(params, Mapping):
        raise ValueError("mapping parameters must be a mapping")
    extra = set(params) - _PARAMETERS[operation]
    if extra:
        raise ValueError(f"undeclared parameters for {operation}: {sorted(extra)}")
    count = len(mapping.input_ids)
    if len({f.path for f in mapping.input_ids}) != count:
        raise ValueError("one feature path cannot be declared with different quantity/types")
    if operation in _SINGLE_INPUT and count != 1:
        raise ValueError(f"{operation} requires exactly one input")
    if "input_units" not in params:
        if operation != "identity":
            raise ValueError(f"{operation} requires declared input_units in input order")
    else:
        units = params["input_units"]
        if (not isinstance(units, tuple) or len(units) != count
                or any(not isinstance(unit, str) or not unit.strip() for unit in units)):
            raise ValueError("input_units must declare one nonempty unit string per input")
        if operation in ("identity", "clip", "sum", "weighted_sum"):
            if any(unit != mapping.output_units for unit in units):
                raise ValueError(f"{operation} preserves units; input/output units must agree")
    if operation == "affine":
        finite(params.get("scale", 1.0), "scale")
        finite(params.get("offset", 0.0), "offset")
    elif operation == "clip":
        if "minimum" not in params or "maximum" not in params:
            raise ValueError("clip requires declared minimum and maximum")
        low = finite(params["minimum"], "minimum")
        high = finite(params["maximum"], "maximum")
        if low > high:
            raise ValueError("clip minimum must not exceed maximum")
    elif operation == "normalize_peak":
        if mapping.output_units != "1":
            raise ValueError("normalize_peak output units must be dimensionless '1'")
        denominator = params.get("denominator")
        if denominator != "frame_peak":
            if denominator is None or isinstance(denominator, str):
                raise ValueError("normalize_peak requires denominator='frame_peak' or positive calibration")
            if finite(denominator, "denominator") <= 0:
                raise ValueError("normalization denominator must be positive")
    elif operation == "weighted_sum":
        weights = params.get("weights")
        if not isinstance(weights, tuple) or len(weights) != count:
            raise ValueError("weighted_sum requires one declared weight per input")
        for weight in weights:
            finite(weight, "weight")


def _numeric(value: Any) -> np.ndarray:
    array = np.asarray(value)
    if array.dtype.kind not in "iuf" or not array.size or not np.all(np.isfinite(array)):
        raise ValueError("musical arithmetic requires finite nonempty real numeric inputs")
    return array.astype(float, copy=False)


def _evaluate(mapping: MappingSpec, features: tuple[FeatureValue, ...]) -> tuple[Any, dict]:
    operation, params = mapping.operation, mapping.parameters
    input_units = params.get("input_units")
    if input_units is not None and tuple(f.units for f in features) != input_units:
        raise ValueError("feature input units do not match the mapping's declared input_units")
    if operation == "identity":
        if features[0].units != mapping.output_units:
            raise ValueError("identity cannot relabel input units")
        return features[0].require_available(), {"uncertainty_policy": "identity_preserves_input"}
    arrays = tuple(_numeric(f.require_available()) for f in features)
    if any(array.shape != arrays[0].shape for array in arrays):
        raise ValueError("compound mapping inputs must have the same shape; implicit broadcasting is forbidden")
    evaluation = {"uncertainty_policy": "inputs_retained_in_provenance_not_propagated"}
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        if operation == "affine":
            value = arrays[0] * float(params.get("scale", 1.0)) + float(params.get("offset", 0.0))
        elif operation == "clip":
            value = np.clip(arrays[0], params["minimum"], params["maximum"])
        elif operation == "normalize_peak":
            denominator = params["denominator"]
            if denominator == "frame_peak":
                denominator = float(np.max(np.abs(arrays[0])))
            denominator = float(denominator)
            evaluation["normalization_denominator"] = denominator
            evaluation["zero_denominator_policy"] = "return_zero"
            value = np.zeros_like(arrays[0]) if denominator == 0 else arrays[0] / denominator
        elif operation == "sum":
            value = np.sum(np.stack(arrays), axis=0)
        else:  # Registry validation leaves only weighted_sum.
            value = np.sum(np.stack([weight * array for weight, array in zip(params["weights"], arrays)]), axis=0)
    if not np.all(np.isfinite(value)):
        raise ValueError("mapping produced nonfinite output; adjust the declared calibration")
    return value.item() if value.ndim == 0 else value, evaluation


def _validate_destination(route: RouteSpec, value: Any) -> None:
    destination = route.destination
    if destination not in ("note.amplitude", "body.modal_weights"):
        return
    array = np.asarray(value)
    dimension = 0 if destination == "note.amplitude" else 1
    if (route.mapping.output_units != "1" or array.dtype.kind not in "iuf"
            or array.ndim != dimension or not array.size
            or not np.all(np.isfinite(array)) or np.any(array < 0) or np.any(array > 1)):
        shape = "scalar" if dimension == 0 else "nonempty vector"
        raise ValueError(f"{destination} requires a dimensionless normalized {shape} in [0, 1]")


class SonificationRouter:
    """One explicit mapping per active audible destination, validated atomically."""

    def __init__(self, preset: RoutingPreset, mode: RoutingMode = RoutingMode.ANALYSIS):
        self.set_preset(preset, mode=mode)

    @property
    def preset(self) -> RoutingPreset:
        return self._preset

    @property
    def mode(self) -> RoutingMode:
        return self._mode

    def set_preset(self, preset: RoutingPreset, *, mode: RoutingMode | None = None) -> None:
        """Validate everything before replacing the active preset and mode."""
        if not isinstance(preset, RoutingPreset):
            raise ValueError("router requires a shared RoutingPreset")
        selected_mode = self._mode if mode is None and hasattr(self, "_mode") else RoutingMode(mode)
        destinations = set()
        for route in preset.routes:
            _validate_mapping(route.mapping)
            if not route.active:
                continue
            if route.destination in destinations:
                raise ValueError(f"destination {route.destination} already has an active primary source")
            destinations.add(route.destination)
            if len(route.mapping.input_ids) > 1 and selected_mode is not RoutingMode.COMPOSITE:
                raise ValueError("multiple musical inputs require explicit COMPOSITE mode")
            if route.destination != route.destination.strip() or any(c.isspace() for c in route.destination):
                raise ValueError("destination must be a typed path without whitespace")
        self._preset, self._mode = preset, selected_mode

    def route(self, bus: FeatureBus | FeatureFrame) -> RoutedFrame:
        """Return a complete immutable mapping result or raise without publication."""
        frame = bus.snapshot() if isinstance(bus, FeatureBus) else bus
        _validate_frame(frame)
        outputs = {}
        for route in self._preset.routes:
            if not route.active:
                continue
            mapping = route.mapping
            inputs = tuple(frame.get(identifier) for identifier in mapping.input_ids)
            for feature in inputs:
                feature.require_available()
            primary = frame.get(route.primary_source)
            value, evaluation = _evaluate(mapping, inputs)
            _validate_destination(route, value)
            provenance = primary.provenance.derive(
                f"{frame.frame_id}:{self._preset.preset_id}:{route.destination}:{mapping.mapping_id}",
                operation=mapping.operation, version=mapping.version,
                parameters={
                    "mapping_id": mapping.mapping_id,
                    "mapping_parameters": mapping.parameters,
                    "input_ids": tuple(f.id.to_dict() for f in inputs),
                    "primary_source": primary.id.to_dict(),
                    "source_frame_id": frame.frame_id,
                    "source_record_ids": tuple(f.provenance.record_id for f in inputs),
                    "input_uncertainties": tuple(f.uncertainty for f in inputs),
                    "destination": route.destination,
                    "routing_mode": self._mode.value,
                    "preset_id": self._preset.preset_id,
                    "evaluation": evaluation,
                },
                units=mapping.output_units, normalization=mapping.normalization,
                parents=tuple(f.provenance for f in inputs), source_path=route.destination,
                evidence="musical_mapping",
            )
            output = FeatureValue(
                FeatureId(route.destination, f"musical.{route.destination}", primary.id.kind),
                value, provenance,
                uncertainty=primary.uncertainty if mapping.operation == "identity" else None,
            )
            _validate_feature(output)
            outputs[route.destination] = output
        return RoutedFrame(frame.frame_id, outputs, self._mode, self._preset.preset_id)


__all__ = ["FeatureBus", "SonificationRouter", "OPERATIONS"]
