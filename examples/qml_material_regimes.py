#!/usr/bin/env python3
"""Train a small QMW material-regime classifier and exercise live inference."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from qmw.core import QuantumStateFrame
from qmw.qml import QMLMaterialOSCSender, QuantumKernelMaterialClassifier


def frame_from_state(state: np.ndarray, time_value: float) -> QuantumStateFrame:
    state = np.asarray(state, dtype=np.complex128)
    state /= np.linalg.norm(state)
    return QuantumStateFrame(
        t=time_value,
        dt=0.1,
        rho=np.outer(state, state.conj()),
        source_name="qml-material-regime-demo",
    )


def product_state(theta: float, phase: float) -> np.ndarray:
    qubit = np.asarray(
        [math.cos(theta / 2.0), np.exp(1j * phase) * math.sin(theta / 2.0)]
    )
    return np.kron(qubit, qubit)


def bell_state(phase: float, balance: float = math.pi / 4.0) -> np.ndarray:
    state = np.zeros(4, dtype=np.complex128)
    state[0] = math.cos(balance)
    state[3] = np.exp(1j * phase) * math.sin(balance)
    return state


def training_corpus() -> tuple[list[QuantumStateFrame], list[str]]:
    states_and_labels: list[tuple[np.ndarray, str]] = []
    for theta, phase in ((0.05, 0.0), (0.12, 0.4), (3.05, 1.1), (2.98, 2.0)):
        states_and_labels.append((product_state(theta, phase), "localized"))
    for theta, phase in (
        (1.40, 0.0),
        (1.52, 0.6),
        (1.64, 1.2),
        (1.72, 2.0),
    ):
        states_and_labels.append((product_state(theta, phase), "coherent"))
    for phase, balance in (
        (0.0, 0.72),
        (0.5, 0.76),
        (1.2, 0.80),
        (2.0, 0.84),
    ):
        states_and_labels.append((bell_state(phase, balance), "entangled"))

    frames = [
        frame_from_state(state, index * 0.1)
        for index, (state, _label) in enumerate(states_and_labels)
    ]
    labels = [label for _state, label in states_and_labels]
    return frames, labels


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", type=Path, help="Optional output .dill model path"
    )
    parser.add_argument(
        "--osc",
        action="store_true",
        help="Send the query to Max on port 7400",
    )
    parser.add_argument("--port", type=int, default=7400)
    args = parser.parse_args()

    frames, labels = training_corpus()
    classifier = QuantumKernelMaterialClassifier().fit_frames(frames, labels)
    print(f"training accuracy: {classifier.score_frames(frames, labels):.3f}")

    query = frame_from_state(bell_state(0.8), time_value=2.0)
    prediction = classifier.predict_frame(query)
    print(f"prediction: {prediction.label} ({prediction.confidence:.3f})")
    print("probabilities:", prediction.probabilities)
    print(
        "QMW features:",
        dict(zip(prediction.feature_names, prediction.source_features)),
    )

    if args.model is not None:
        classifier.save(args.model)
        print(f"saved model: {args.model}")
    if args.osc:
        QMLMaterialOSCSender(port=args.port).send_prediction(query.t, prediction)
        print(f"sent /qmw/qml/* to 127.0.0.1:{args.port}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
