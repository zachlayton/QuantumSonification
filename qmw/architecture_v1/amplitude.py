"""Declared, single-source note excitation downstream of feature extraction.

The supervisor's transition adapter supplies matrix-element magnitude,
state-weighted magnitude, and diagnostic activity from the actual engine.
This module never reconstructs transitions, samples events, or touches timbre.
The resulting scalar is a linear note excitation amplitude in [0, 1]. Route
it through SonificationRouter before assigning the actual note's ``strength``;
the resonator already uses that value directly as linear amplitude.

Frame-peak calibration is opt-in. Its denominator depends on every scalar of
the selected quantity in one supplied frame; all those dependencies remain in
the mapping and provenance. A selected derived feature may have multiple
physical ancestors without acquiring another independent audible destination.
"""
from __future__ import annotations

import hashlib
import json
from types import MappingProxyType

import numpy as np

from .contracts import FeatureFrame, FeatureId, FeatureValue, MappingSpec, finite, nonempty, plain


SOURCE_QUANTITIES = MappingProxyType({
    "matrix_element_magnitude": "matrix_element_magnitude",
    "state_weighted_magnitude": "state_weighted_magnitude",
    "diagnostic_activity": "diagnostic_activity",
    "lorentz_force_magnitude": "force_magnitude",
    "decay_survival": "survival_probability",
    "decay_envelope": "decay_envelope",
    "experimental_amplitude": "amplitude_estimate",
})
_DIMENSIONLESS = frozenset({"1", "dimensionless"})
_NORMALIZATIONS = frozenset({"fixed_reference", "frame_peak", "already_unit_interval"})


def _scalar(feature: FeatureValue) -> float:
    value = np.asarray(feature.require_available())
    if (feature.id.kind != "scalar" or value.ndim != 0 or value.dtype.kind not in "iuf"
            or not np.isfinite(value) or value < 0):
        raise ValueError("amplitude source must be a finite nonnegative real scalar")
    return float(value)


class TransitionAmplitudeProjector:
    """Map exactly one selected physical/derived quantity to note excitation.

    ``fixed_reference`` requires a positive calibration and its explicit unit;
    values above it clip or reject according to ``overflow``. ``frame_peak``
    requires a frame of comparable observations, with a zero cohort producing
    exact silence. ``already_unit_interval`` accepts declared dimensionless
    values in [0, 1] without rescaling.

    ``sqrt_survival`` is an explicit musical envelope curve applied after
    normalization. It is permitted only for a selected survival probability;
    it does not assert that a decay model supplies a quantum amplitude.

    Effective Lorentz fields retain their declared model units. No conversion
    to SI force is inferred. Experimental inputs must be available typed
    amplitude estimates; signed event weights are not accepted as estimates.
    """

    def __init__(self, source: str, *, normalization: str = "fixed_reference",
                 reference: float | None = None, reference_units: str | None = None,
                 curve: str = "linear", overflow: str = "clip",
                 mapping_id: str = "qmw.transition_amplitude", version: str = "1"):
        if source not in SOURCE_QUANTITIES:
            raise ValueError(f"unsupported amplitude source: {source}")
        if normalization not in _NORMALIZATIONS:
            raise ValueError("unsupported amplitude normalization")
        if curve not in ("linear", "sqrt_survival"):
            raise ValueError("unsupported amplitude curve")
        if curve == "sqrt_survival" and source != "decay_survival":
            raise ValueError("sqrt_survival requires the selected decay survival probability")
        if overflow not in ("clip", "reject"):
            raise ValueError("overflow must be clip or reject")
        if normalization == "fixed_reference":
            if reference is None or finite(reference, "reference") <= 0:
                raise ValueError("reference must be positive and finite")
            reference = float(reference)
            nonempty(reference_units, "reference units")
        elif reference is not None or reference_units is not None:
            raise ValueError("reference and reference_units apply only to fixed_reference")
        nonempty(mapping_id, "mapping_id")
        nonempty(version, "version")
        # One immutable configuration object supplies both execution and audit.
        self._config = MappingProxyType(dict(source=source, normalization=normalization,
            reference=reference, reference_units=reference_units, curve=curve, overflow=overflow))
        self.mapping_id = mapping_id
        self.version = version

    @property
    def configuration(self):
        return self._config

    def _resolve(self, feature, frame):
        if not isinstance(feature, FeatureValue):
            raise ValueError("shared FeatureValue required")
        source = self._config["source"]
        if feature.id.quantity != SOURCE_QUANTITIES[source]:
            raise ValueError(f"selected {source} requires quantity {SOURCE_QUANTITIES[source]}")
        value = _scalar(feature)
        normalization = self._config["normalization"]
        if source == "decay_survival" or normalization == "already_unit_interval":
            if feature.units not in _DIMENSIONLESS:
                raise ValueError("survival/unit-interval source must have dimensionless units")
            if value > 1:
                raise ValueError("source must lie in the unit interval [0, 1]")
        if frame is not None:
            if not isinstance(frame, FeatureFrame):
                raise ValueError("frame must use shared FeatureFrame")
            try:
                present = frame.get(feature.id)
            except KeyError as exc:
                raise ValueError("selected source must be present in the supplied frame") from exc
            if present.provenance.digest != feature.provenance.digest or _scalar(present) != value:
                raise ValueError("selected source differs from the supplied frame observation")
        inputs = (feature,)
        if normalization == "fixed_reference":
            if feature.units != self._config["reference_units"]:
                raise ValueError("source units must match explicit reference units")
            denominator = self._config["reference"]
        elif normalization == "already_unit_interval":
            denominator = 1.0
        else:
            if not isinstance(frame, FeatureFrame):
                raise ValueError("frame_peak requires an explicit FeatureFrame cohort")
            cohort = tuple(f for f in frame.features if f.id.quantity == feature.id.quantity)
            # The selected source comes first; frame order defines the remaining
            # normalization dependency order. No hidden filtering of missing data.
            inputs = (feature,) + tuple(f for f in cohort if f.id != feature.id)
            for f in inputs:
                if (f.units != feature.units or f.provenance.basis != feature.provenance.basis
                        or f.provenance.clock != feature.provenance.clock
                        or f.provenance.backend != feature.provenance.backend):
                    raise ValueError("frame_peak cohort requires matching units, basis, clock, and backend")
                amount = _scalar(f)
                if source == "decay_survival" and amount > 1:
                    raise ValueError("survival cohort must lie in the unit interval")
            denominator = max(_scalar(f) for f in inputs)
        return value, float(denominator), inputs

    def _spec(self, inputs):
        return MappingSpec(self.mapping_id, self.version, "amplitude_projection",
            tuple(f.id for f in inputs), "1", self._config["normalization"],
            dict(self._config) | {"input_units": tuple(f.units for f in inputs),
                "output_role": "linear_note_excitation", "invalid_input": "reject",
                "zero_input": "silence", "curve_order": "after_normalization"})

    def mapping_spec(self, feature: FeatureValue, *, frame: FeatureFrame | None = None) -> MappingSpec:
        """Inspect the exact selected inputs and musical policy without output."""
        _, _, inputs = self._resolve(feature, frame)
        return self._spec(inputs)

    def project(self, feature: FeatureValue, *, frame: FeatureFrame | None = None,
                record_id: str | None = None) -> FeatureValue:
        value, denominator, inputs = self._resolve(feature, frame)
        clipped = value > denominator
        if clipped and self._config["overflow"] == "reject":
            raise ValueError("amplitude source exceeds the declared reference")
        # Bound before division to avoid overflow for extreme physical units.
        normalized = 0.0 if denominator == 0 else min(value, denominator) / denominator
        output = float(np.sqrt(normalized)) if self._config["curve"] == "sqrt_survival" else normalized
        spec = self._spec(inputs)
        evaluation = {"source_value": value, "normalization_denominator": denominator,
                      "clipped": clipped, "zero_cohort": denominator == 0,
                      "normalized_before_curve": normalized}
        parameters = {"mapping_id": spec.mapping_id, "mapping_parameters": spec.parameters,
            "selected_source": feature.id.to_dict(), "input_ids": tuple(f.id.to_dict() for f in inputs),
            "source_record_ids": tuple(f.provenance.record_id for f in inputs),
            "source_frame_id": frame.frame_id if frame is not None else None,
            "input_uncertainties": tuple(f.uncertainty for f in inputs),
            "selection_probability": "not_used", "evaluation": evaluation}
        if record_id is None:
            identity = {"parameters": parameters, "version": spec.version,
                        "parents": tuple(f.provenance.digest for f in inputs)}
            digest = hashlib.sha256(json.dumps(plain(identity), sort_keys=True,
                separators=(",", ":"), allow_nan=False).encode()).hexdigest()
            record_id = f"{feature.provenance.record_id}:amplitude:{digest}"
        else:
            nonempty(record_id, "record_id")
        provenance = feature.provenance.derive(record_id, spec.operation, spec.version,
            parameters, units="1", normalization=spec.normalization,
            parents=tuple(f.provenance for f in inputs), source_path="note.amplitude",
            evidence="musical_mapping")
        uncertainty = None
        if any(f.uncertainty is not None for f in inputs):
            # Arbitrary estimates may carry covariance links rather than a
            # scalar standard error. Preserve them without inventing propagation.
            uncertainty = {"kind": "mapped_input_uncertainty", "status": "not_propagated",
                "reason": "source uncertainty retained; no output uncertainty model declared",
                "inputs": tuple({"source_id": f.id.to_dict(), "units": f.units,
                                  "uncertainty": f.uncertainty} for f in inputs)}
        return FeatureValue(FeatureId("note.amplitude", "excitation_amplitude"), output,
                            provenance, uncertainty=uncertainty)


__all__ = ["TransitionAmplitudeProjector", "SOURCE_QUANTITIES"]
