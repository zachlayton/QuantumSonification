import numpy as np


def gaussian_packet(x, x0=0.0, sigma=1.0, k0=0.0):
    psi = np.exp(-((x - x0) ** 2) / (4 * sigma**2) + 1j * k0 * x)
    dx = x[1] - x[0]
    return psi / np.sqrt(np.sum(np.abs(psi) ** 2) * dx)


def superposition(*psis, weights=None):
    w = np.ones(len(psis)) if weights is None else np.asarray(weights, complex)
    return sum(wi * p for wi, p in zip(w, psis))
