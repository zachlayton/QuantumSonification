from __future__ import annotations

import importlib.util
import math
import unittest

import numpy as np

from qmw.core import QuantumStateFrame
from qmw.flucoma import DescriptorVector
from qmw.qml import (
    MaterialRegimePrediction,
    QMLFeatureProjector,
    QMLMaterialOSCSender,
    QMLStateSubscriber,
    QuantumKernelMaterialClassifier,
)


class FakeQSVC:
    def __init__(self) -> None:
        self.classes_ = np.asarray(["coherent", "diffuse"])
        self.fit_shape: tuple[int, int] | None = None

    def fit(self, samples: np.ndarray, labels: np.ndarray) -> "FakeQSVC":
        self.fit_shape = samples.shape
        self.classes_ = np.unique(labels)
        return self

    def predict(self, samples: np.ndarray) -> np.ndarray:
        return np.asarray(
            [
                "coherent" if row[0] >= math.pi / 2 else "diffuse"
                for row in samples
            ]
        )

    def predict_proba(self, samples: np.ndarray) -> np.ndarray:
        rows = []
        for row in samples:
            coherent = float(np.clip(row[0] / math.pi, 0.0, 1.0))
            by_label = {"coherent": coherent, "diffuse": 1.0 - coherent}
            rows.append([by_label[str(label)] for label in self.classes_])
        return np.asarray(rows)

    def score(self, samples: np.ndarray, labels: np.ndarray) -> float:
        return float(np.mean(self.predict(samples) == labels))


class RecordingOSCClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, payload: object) -> None:
        self.messages.append((address, payload))


def descriptor(coherence: float) -> DescriptorVector:
    names = (
        "coherence_l1",
        "participation",
        "mean_spin_length",
        "pair_abs_mean",
    )
    return DescriptorVector(
        identifier="test",
        names=names,
        values=np.asarray([coherence, 0.25, 0.5, 0.75]),
    )


def frame(time_value: float = 0.0) -> QuantumStateFrame:
    state = np.asarray([1.0, 1.0], dtype=np.complex128) / math.sqrt(2.0)
    return QuantumStateFrame(
        t=time_value,
        dt=1.0 / 30.0,
        rho=np.outer(state, state.conj()),
        source_name="qml-test",
    )


class QMLMaterialClassifierTests(unittest.TestCase):
    def test_projection_selects_clips_and_encodes_angles(self) -> None:
        projector = QMLFeatureProjector()
        item = descriptor(1.5)
        np.testing.assert_allclose(
            projector.select(item), [1.0, 0.25, 0.5, 0.75]
        )
        np.testing.assert_allclose(
            projector.encode(item),
            np.asarray([1.0, 0.25, 0.5, 0.75]) * math.pi,
        )

    def test_classifier_fits_and_predicts_with_adapter_model(self) -> None:
        model = FakeQSVC()
        classifier = QuantumKernelMaterialClassifier(model=model, probability=True)
        classifier.fit_descriptors(
            [descriptor(0.1), descriptor(0.9)],
            ["diffuse", "coherent"],
        )
        self.assertEqual(model.fit_shape, (2, 4))

        prediction = classifier.predict_descriptor(descriptor(0.8))
        self.assertEqual(prediction.label, "coherent")
        self.assertAlmostEqual(prediction.confidence, 0.8)
        self.assertEqual(prediction.feature_names[0], "coherence_l1")

    def test_frame_prediction_uses_existing_descriptor_extractor(self) -> None:
        classifier = QuantumKernelMaterialClassifier(model=FakeQSVC())
        prediction = classifier.predict_frame(frame())
        self.assertEqual(prediction.label, "coherent")
        self.assertGreaterEqual(prediction.confidence, 0.99)

    def test_osc_sender_uses_qmw_qml_namespace(self) -> None:
        recorder = RecordingOSCClient()
        sender = QMLMaterialOSCSender(client=recorder)
        prediction = MaterialRegimePrediction(
            label="entangled",
            confidence=0.8,
            probabilities={"coherent": 0.2, "entangled": 0.8},
            feature_names=("a", "b"),
            source_features=(0.25, 0.75),
            encoded_features=(0.25 * math.pi, 0.75 * math.pi),
        )
        sender.send_prediction(1.25, prediction)

        messages = dict(recorder.messages)
        self.assertEqual(messages["/qmw/qml/regime"], [1.25, "entangled", 0.8])
        self.assertEqual(messages["/qmw/qml/features"], [1.25, 0.25, 0.75])
        self.assertIn("entangled", messages["/qmw/qml/probabilities"])

    def test_state_subscriber_rate_divides_inference(self) -> None:
        classifier = QuantumKernelMaterialClassifier(model=FakeQSVC())
        received: list[str] = []
        subscriber = QMLStateSubscriber(
            classifier,
            every_n_frames=2,
            on_prediction=lambda _frame, prediction: received.append(prediction.label),
        )
        subscriber(frame(0.0))
        subscriber(frame(0.1))
        subscriber(frame(0.2))
        self.assertEqual(received, ["coherent", "coherent"])
        self.assertEqual(subscriber.frame_count, 3)

    def test_training_validation_rejects_one_label(self) -> None:
        classifier = QuantumKernelMaterialClassifier(model=FakeQSVC())
        with self.assertRaisesRegex(ValueError, "two material-regime labels"):
            classifier.fit_descriptors(
                [descriptor(0.1), descriptor(0.2)],
                ["same", "same"],
            )

    @unittest.skipUnless(
        importlib.util.find_spec("qiskit_machine_learning") is not None,
        "optional qiskit-machine-learning runtime is not installed",
    )
    def test_real_qiskit_kernel_uses_qmw_feature_width(self) -> None:
        classifier = QuantumKernelMaterialClassifier(probability=False)
        self.assertEqual(classifier.model.quantum_kernel.num_features, 4)


if __name__ == "__main__":
    unittest.main()
