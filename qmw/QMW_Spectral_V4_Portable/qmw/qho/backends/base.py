"""Backend interface for oscillator execution paths."""

from __future__ import annotations

from typing import Protocol

import numpy as np

from ..schema import OscillatorFrame


class OscillatorBackend(Protocol):
    def run(
        self,
        state: np.ndarray,
        *,
        time: float = 0.0,
        include_rho: bool = False,
        include_wigner: bool = False,
    ) -> OscillatorFrame: ...


__all__ = ["OscillatorBackend"]
