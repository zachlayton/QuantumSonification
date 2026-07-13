from dataclasses import dataclass


@dataclass
class MaterialComparison:
    brightness_match: float
    loudness_match: float
    density_match: float
    stability_match: float
    overall: float


def clamp01(x):
    return max(0.0, min(1.0, x))


def compare_quantum_audio(q, a):
    brightness_target = q.brightness
    loudness_target = 0.5
    density_target = q.density
    stability_target = 1.0 - q.damping

    brightness_actual = clamp01(a.brightness / 8000.0)
    loudness_actual = clamp01(a.loudness / 0.2)
    density_actual = clamp01(a.onset_density / 8.0)
    stability_actual = a.groove_stability

    brightness_match = 1.0 - abs(brightness_target - brightness_actual)
    loudness_match = 1.0 - abs(loudness_target - loudness_actual)
    density_match = 1.0 - abs(density_target - density_actual)
    stability_match = 1.0 - abs(stability_target - stability_actual)

    overall = (
        brightness_match
        + loudness_match
        + density_match
        + stability_match
    ) / 4.0

    return MaterialComparison(
        brightness_match=brightness_match,
        loudness_match=loudness_match,
        density_match=density_match,
        stability_match=stability_match,
        overall=overall,
    )