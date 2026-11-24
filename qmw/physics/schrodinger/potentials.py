"""Potentials V(x) on a 1-D grid (energy units of the model)."""
import numpy as np


def free(x):
    return np.zeros_like(x)


def harmonic(x, omega=1.0, mass=1.0, x0=0.0):
    return 0.5 * mass * omega**2 * (x - x0) ** 2


def barrier(x, height, center=0.0, width=1.0, smooth=0.0):
    if smooth <= 0:
        return np.where(np.abs(x - center) <= width / 2, float(height), 0.0)
    return height * 0.5 * (np.tanh((x - center + width / 2) / smooth) - np.tanh((x - center - width / 2) / smooth))


def double_well(x, depth=1.0, separation=4.0):
    a = separation / 2
    return depth * ((x / a) ** 2 - 1) ** 2


def absorbing_layer(x, width, strength):
    """Non-negative W(x) for a complex absorbing potential -iW: quadratic ramps at
    both ends. Probability entering the layer is removed and accounted as physical
    absorption, not numerical error."""
    lo, hi = x.min(), x.max()
    d = np.maximum(0.0, np.maximum(lo + width - x, x - (hi - width))) / max(width, 1e-12)
    return strength * d**2
