from __future__ import annotations

import numpy as np
import pytest


def random_unitary(rng: np.random.Generator, dimension: int = 16) -> np.ndarray:
    real = rng.normal(size=(dimension, dimension))
    imag = rng.normal(size=(dimension, dimension))
    q, r = np.linalg.qr(real + 1j * imag)
    phases = np.diag(r)
    phases = np.where(np.abs(phases) > 0.0, phases / np.abs(phases), 1.0)
    return q @ np.diag(phases.conj())


@pytest.fixture
def rng() -> np.random.Generator:
    return np.random.default_rng(20260906)


@pytest.fixture
def unitary_pair(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    return random_unitary(rng), random_unitary(rng)


@pytest.fixture
def hermitian_matrix(rng: np.random.Generator) -> np.ndarray:
    raw = rng.normal(size=(16, 16)) + 1j * rng.normal(size=(16, 16))
    return 0.5 * (raw + raw.conj().T)

