"""Bounded, causal acoustic analysis for the third optimization condition."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np

from .model import HexanyOptimizationModel


def _clip(value: float, low: float, high: float) -> float:
    return min(high, max(low, float(value)))


@dataclass(frozen=True)
class AcousticFeedbackFrame:
    step: int
    energy: float
    centroid: float
    flux: float
    stereo_balance: float
    resonance: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class FeedbackControls:
    source_step: int
    epsilon: float
    batch_size: int
    learning_rate: float
    perturbation_polarity: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def analyze_acoustic_response(
    model: HexanyOptimizationModel,
    state: np.ndarray,
    *,
    step: int,
    previous_probabilities: np.ndarray | None,
) -> AcousticFeedbackFrame:
    """Derive the five normalized descriptors used by the live listener."""

    state = np.asarray(state, dtype=np.complex128)
    probabilities = np.abs(state) ** 2
    metrics = model.metrics_from_state(state)
    cents = np.array([vertex.cents for vertex in model.problem.vertices])
    cents = (cents - np.min(cents)) / max(float(np.ptp(cents)), 1e-12)
    flux = (
        0.0
        if previous_probabilities is None
        else _clip(
            3.0 * 0.5 * np.sum(np.abs(probabilities - previous_probabilities)),
            0.0,
            1.0,
        )
    )
    reference = int(np.argmax(probabilities))
    relative_phase = np.angle(state * np.exp(-1j * np.angle(state[reference])))
    angles = np.linspace(-math.pi, math.pi, 6, endpoint=False)
    stereo = float(np.sum(probabilities * np.sin(relative_phase + angles)))
    concentration = _clip((6.0 - metrics.participation) / 5.0, 0.0, 1.0)
    return AcousticFeedbackFrame(
        step=int(step),
        energy=_clip(0.15 + 0.85 * (1.0 - metrics.objective), 0.0, 1.0),
        centroid=_clip(float(probabilities @ cents), 0.0, 1.0),
        flux=flux,
        stereo_balance=_clip(stereo, -1.0, 1.0),
        resonance=_clip(0.55 * metrics.phase_order + 0.45 * concentration, 0.0, 1.0),
    )


def controls_from_feedback(
    frame: AcousticFeedbackFrame,
    *,
    base_epsilon: float,
    base_batch_size: int,
    base_learning_rate: float,
    mix: float = 1.0,
    max_batch_size: int = 8,
) -> FeedbackControls:
    """Map the previous completed answer to bounded next-step controls."""

    mix = _clip(mix, 0.0, 1.0)
    epsilon_factor = 2.0 ** ((frame.centroid - 0.5) * 1.5 * mix)
    learning_factor = 1.0 + mix * (0.8 * frame.resonance - 0.4)
    extra_probes = round(mix * frame.flux * 4.0)
    return FeedbackControls(
        source_step=frame.step,
        epsilon=_clip(
            base_epsilon * epsilon_factor,
            base_epsilon * 0.5,
            base_epsilon * 2.0,
        ),
        batch_size=min(
            max_batch_size,
            max(1, int(base_batch_size) + extra_probes),
        ),
        learning_rate=_clip(
            base_learning_rate * learning_factor,
            base_learning_rate * 0.5,
            base_learning_rate * 1.5,
        ),
        perturbation_polarity=(
            -1.0 if mix > 0 and frame.stereo_balance > 0.12 else 1.0
        ),
    )
