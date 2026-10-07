"""Gradient values for M(m, n, eta)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManifoldGradient:
    m: complex
    n: complex
    eta: complex

    def as_tuple(self) -> tuple[complex, complex, complex]:
        return self.m, self.n, self.eta

