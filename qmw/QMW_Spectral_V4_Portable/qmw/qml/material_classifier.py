"""Quantum-kernel classification of QMW sonic/material state regimes.

The QMW core deliberately has no Qiskit dependency.  This module preserves
that boundary: Qiskit Machine Learning is imported only when a model is
created or loaded.  Existing ``QuantumStateFrame`` producers can therefore
continue running when the optional QML environment is not installed.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from qmw.core import QuantumStateFrame
from qmw.flucoma import DescriptorVector, QuantumDescriptorExtractor


DEFAULT_QML_FEATURES = (
    "coherence_l1",
    "participation",
    "mean_spin_length",
    "pair_abs_mean",
)


class QMLDependencyError(RuntimeError):
    """Raised when the optional Qiskit Machine Learning runtime is absent."""


def _qiskit_ml_types() -> tuple[type[Any], type[Any]]:
    try:
        from qiskit_machine_learning.algorithms import QSVC
        from qiskit_machine_learning.kernels import FidelityStatevectorKernel
    except ImportError as exc:
        raise QMLDependencyError(
            "Qiskit Machine Learning is required for model training and "
            "inference. Install qmw/qml/requirements.txt in the Python "
            "environment used to run QuantumSonification."
        ) from exc
    return QSVC, FidelityStatevectorKernel


@dataclass(frozen=True)
class QMLFeatureProjector:
    """Select bounded descriptors and encode them as circuit angles."""

    feature_names: tuple[str, ...] = DEFAULT_QML_FEATURES
    lower_bounds: tuple[float, ...] = (0.0, 0.0, 0.0, 0.0)
    upper_bounds: tuple[float, ...] = (1.0, 1.0, 1.0, 1.0)
    angle_scale: float = math.pi

    def __post_init__(self) -> None:
        width = len(self.feature_names)
        if width == 0:
            raise ValueError("At least one QML feature is required.")
        if len(self.lower_bounds) != width or len(self.upper_bounds) != width:
            raise ValueError("Feature names and bounds must have equal lengths.")
        if any(
            high <= low
            for low, high in zip(self.lower_bounds, self.upper_bounds)
        ):
            raise ValueError("Every QML feature upper bound must exceed its lower bound.")
        if not math.isfinite(self.angle_scale) or self.angle_scale <= 0.0:
            raise ValueError("angle_scale must be finite and positive.")

    def select(self, descriptor: DescriptorVector) -> np.ndarray:
        values = descriptor.to_dict()
        missing = [name for name in self.feature_names if name not in values]
        if missing:
            raise ValueError(
                f"Descriptor is missing QML features: {', '.join(missing)}"
            )

        selected = np.asarray(
            [values[name] for name in self.feature_names], dtype=float
        )
        if not np.all(np.isfinite(selected)):
            raise ValueError("QML descriptor features must be finite.")

        low = np.asarray(self.lower_bounds, dtype=float)
        high = np.asarray(self.upper_bounds, dtype=float)
        return np.clip((selected - low) / (high - low), 0.0, 1.0)

    def encode(self, descriptor: DescriptorVector) -> np.ndarray:
        """Return feature-map angles in ``[0, angle_scale]``."""
        return self.select(descriptor) * self.angle_scale

    def metadata(self) -> dict[str, Any]:
        return {
            "feature_names": list(self.feature_names),
            "lower_bounds": list(self.lower_bounds),
            "upper_bounds": list(self.upper_bounds),
            "angle_scale": self.angle_scale,
        }

    @classmethod
    def from_metadata(cls, metadata: dict[str, Any]) -> "QMLFeatureProjector":
        return cls(
            feature_names=tuple(metadata["feature_names"]),
            lower_bounds=tuple(float(value) for value in metadata["lower_bounds"]),
            upper_bounds=tuple(float(value) for value in metadata["upper_bounds"]),
            angle_scale=float(metadata["angle_scale"]),
        )


@dataclass(frozen=True)
class MaterialRegimePrediction:
    """One QML classification result ready for buses, OSC, or automation."""

    label: str
    confidence: float
    probabilities: dict[str, float]
    feature_names: tuple[str, ...]
    source_features: tuple[float, ...]
    encoded_features: tuple[float, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "confidence": self.confidence,
            "probabilities": dict(self.probabilities),
            "features": dict(
                zip(self.feature_names, self.source_features, strict=True)
            ),
            "encoded_features": dict(
                zip(self.feature_names, self.encoded_features, strict=True)
            ),
        }


class QuantumKernelMaterialClassifier:
    """Classify QMW frames with a Qiskit fidelity-kernel SVM.

    The default exact statevector kernel is intended for local rehearsal and
    low-rate control inference.  A compatible pre-built QSVC-like model can be
    injected for testing or for a future hardware-backed kernel.
    """

    MODEL_SCHEMA = "qmw-qml-material-regime-v1"

    def __init__(
        self,
        *,
        projector: QMLFeatureProjector | None = None,
        extractor: QuantumDescriptorExtractor | None = None,
        probability: bool = False,
        shots: int | None = None,
        cache_size: int | None = 256,
        random_state: int = 7,
        model: Any | None = None,
    ) -> None:
        if shots is not None and shots <= 0:
            raise ValueError("shots must be positive or None.")
        self.projector = projector or QMLFeatureProjector()
        self.extractor = extractor or QuantumDescriptorExtractor()
        self.probability = bool(probability)
        self.shots = shots
        self.cache_size = cache_size
        self.random_state = int(random_state)
        self._model = model

    @property
    def model(self) -> Any:
        if self._model is None:
            self._model = self._build_model()
        return self._model

    @property
    def is_fitted(self) -> bool:
        return self._model is not None and hasattr(self._model, "classes_")

    @property
    def classes(self) -> tuple[str, ...]:
        if not self.is_fitted:
            return ()
        return tuple(str(label) for label in self._model.classes_)

    def _build_model(self) -> Any:
        QSVC, FidelityStatevectorKernel = _qiskit_ml_types()
        # qiskit-machine-learning 0.9.0 documents a default feature map, but
        # its BaseKernel rejects ``None`` with some Qiskit 2.x combinations.
        # Building it explicitly also freezes the QMW feature width and
        # entanglement topology instead of relying on version-specific resize
        # behavior.
        from qiskit.circuit.library import zz_feature_map

        feature_map = zz_feature_map(
            feature_dimension=len(self.projector.feature_names),
            reps=2,
            entanglement="linear",
        )
        kernel = FidelityStatevectorKernel(
            feature_map=feature_map,
            shots=self.shots,
            cache_size=self.cache_size,
            auto_clear_cache=False,
        )
        qsvc_options: dict[str, Any] = {
            "quantum_kernel": kernel,
            "random_state": self.random_state,
        }
        if self.probability:
            # This asks libsvm for calibrated probabilities and is more
            # expensive than the normalized decision weights used by default.
            qsvc_options["probability"] = True
        return QSVC(
            **qsvc_options,
        )

    def fit_descriptors(
        self,
        descriptors: Iterable[DescriptorVector],
        labels: Sequence[str],
    ) -> "QuantumKernelMaterialClassifier":
        descriptor_list = list(descriptors)
        label_array = np.asarray([str(label) for label in labels], dtype=str)
        if len(descriptor_list) != len(label_array):
            raise ValueError(
                "Training descriptors and labels must have equal lengths."
            )
        if len(descriptor_list) < 2:
            raise ValueError("At least two training descriptors are required.")
        if len(np.unique(label_array)) < 2:
            raise ValueError("At least two material-regime labels are required.")

        samples = np.vstack(
            [self.projector.encode(descriptor) for descriptor in descriptor_list]
        )
        self.model.fit(samples, label_array)
        return self

    def fit_frames(
        self,
        frames: Iterable[QuantumStateFrame],
        labels: Sequence[str],
    ) -> "QuantumKernelMaterialClassifier":
        descriptors = [self.extractor.extract(frame) for frame in frames]
        return self.fit_descriptors(descriptors, labels)

    def predict_descriptor(
        self, descriptor: DescriptorVector
    ) -> MaterialRegimePrediction:
        if not self.is_fitted:
            raise RuntimeError(
                "The QML material classifier must be fitted before inference."
            )

        source = self.projector.select(descriptor)
        encoded = source * self.projector.angle_scale
        sample = encoded.reshape(1, -1)
        label = str(self.model.predict(sample)[0])

        probabilities = self._probabilities(sample, label)
        confidence = float(probabilities.get(label, max(probabilities.values())))
        return MaterialRegimePrediction(
            label=label,
            confidence=float(np.clip(confidence, 0.0, 1.0)),
            probabilities=probabilities,
            feature_names=self.projector.feature_names,
            source_features=tuple(float(value) for value in source),
            encoded_features=tuple(float(value) for value in encoded),
        )

    def _probabilities(self, sample: np.ndarray, label: str) -> dict[str, float]:
        if hasattr(self.model, "predict_proba") and self.probability:
            values = np.asarray(self.model.predict_proba(sample)[0], dtype=float)
            return {
                str(name): float(np.clip(value, 0.0, 1.0))
                for name, value in zip(self.model.classes_, values, strict=True)
            }

        classes = self.classes
        if hasattr(self.model, "decision_function"):
            decision = np.asarray(self.model.decision_function(sample), dtype=float)
            scores = decision.reshape(-1)
            if len(classes) == 2 and scores.size == 1:
                scores = np.asarray([-scores[0], scores[0]], dtype=float)
            if scores.size == len(classes):
                scores -= np.max(scores)
                weights = np.exp(scores)
                weights /= max(float(np.sum(weights)), np.finfo(float).eps)
                return {
                    name: float(weight)
                    for name, weight in zip(classes, weights, strict=True)
                }

        return {name: 1.0 if name == label else 0.0 for name in classes}

    def predict_frame(self, frame: QuantumStateFrame) -> MaterialRegimePrediction:
        return self.predict_descriptor(self.extractor.extract(frame))

    __call__ = predict_frame

    def score_frames(
        self,
        frames: Iterable[QuantumStateFrame],
        labels: Sequence[str],
    ) -> float:
        if not self.is_fitted:
            raise RuntimeError(
                "The QML material classifier must be fitted before scoring."
            )
        descriptors = [self.extractor.extract(frame) for frame in frames]
        samples = np.vstack([self.projector.encode(item) for item in descriptors])
        return float(self.model.score(samples, np.asarray(labels, dtype=str)))

    def save(self, path: str | Path) -> Path:
        """Save the QSVC dill file and a JSON projection sidecar."""
        if not self.is_fitted:
            raise RuntimeError(
                "The QML material classifier must be fitted before saving."
            )
        if not hasattr(self.model, "to_dill"):
            raise TypeError("The injected model does not support Qiskit ML dill export.")

        model_path = Path(path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        self.model.to_dill(str(model_path))
        metadata = {
            "schema": self.MODEL_SCHEMA,
            "projector": self.projector.metadata(),
            "probability": self.probability,
            "shots": self.shots,
            "cache_size": self.cache_size,
            "random_state": self.random_state,
            "classes": list(self.classes),
        }
        self.metadata_path(model_path).write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
        return model_path

    @classmethod
    def load(cls, path: str | Path) -> "QuantumKernelMaterialClassifier":
        model_path = Path(path)
        metadata = json.loads(
            cls.metadata_path(model_path).read_text(encoding="utf-8")
        )
        if metadata.get("schema") != cls.MODEL_SCHEMA:
            raise ValueError(
                "Unsupported QML model metadata schema: "
                f"{metadata.get('schema')!r}"
            )

        QSVC, _kernel_type = _qiskit_ml_types()
        model = QSVC.from_dill(str(model_path))
        return cls(
            projector=QMLFeatureProjector.from_metadata(metadata["projector"]),
            probability=bool(metadata["probability"]),
            shots=metadata["shots"],
            cache_size=metadata["cache_size"],
            random_state=int(metadata["random_state"]),
            model=model,
        )

    @staticmethod
    def metadata_path(path: str | Path) -> Path:
        model_path = Path(path)
        return model_path.with_suffix(model_path.suffix + ".json")


class QMLMaterialOSCSender:
    """Publish material-regime inference on the stable ``/qmw/qml`` subtree."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7400,
        *,
        client: Any | None = None,
    ) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, port)
        self.client = client

    def send_prediction(
        self,
        time_value: float,
        prediction: MaterialRegimePrediction,
    ) -> None:
        timestamp = float(time_value)
        self.client.send_message(
            "/qmw/qml/regime",
            [timestamp, prediction.label, prediction.confidence],
        )

        probability_payload: list[str | float] = [timestamp]
        for label, probability in prediction.probabilities.items():
            probability_payload.extend((label, probability))
        self.client.send_message("/qmw/qml/probabilities", probability_payload)
        self.client.send_message(
            "/qmw/qml/features",
            [timestamp, *prediction.source_features],
        )


class QMLStateSubscriber:
    """StateBus callback that performs rate-divided inference and OSC output."""

    def __init__(
        self,
        classifier: QuantumKernelMaterialClassifier,
        *,
        osc_sender: QMLMaterialOSCSender | None = None,
        every_n_frames: int = 1,
        on_prediction: Callable[[QuantumStateFrame, MaterialRegimePrediction], None]
        | None = None,
    ) -> None:
        if every_n_frames <= 0:
            raise ValueError("every_n_frames must be positive.")
        self.classifier = classifier
        self.osc_sender = osc_sender
        self.every_n_frames = int(every_n_frames)
        self.on_prediction = on_prediction
        self.frame_count = 0
        self.latest: MaterialRegimePrediction | None = None

    def __call__(self, frame: QuantumStateFrame) -> None:
        frame_index = self.frame_count
        self.frame_count += 1
        if frame_index % self.every_n_frames:
            return

        prediction = self.classifier.predict_frame(frame)
        self.latest = prediction
        if self.osc_sender is not None:
            self.osc_sender.send_prediction(frame.t, prediction)
        if self.on_prediction is not None:
            self.on_prediction(frame, prediction)
