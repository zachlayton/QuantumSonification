"""Reusable read-only observable publication for a running 2-D GPE field."""

from __future__ import annotations

import numpy as np

from qmw.gpe.geometry_engine import GeometryPotentialEngine2D
from qmw.gpe.modal_engine import GPEModalProjector2D
from qmw.gpe.vortices import detect_vortices_2d
from qmw.osc.gpe_osc import GPEOSCAdapter
from qmw.qmw_gpe import GPEState
from qmw.qmw_probability_flow import flow_from_wavefunction_2d


def fourier_modes_2d(x: np.ndarray, y: np.ndarray, count: int = 16) -> list[np.ndarray]:
    """Return normalized periodic analysis modes; they are not acoustic pitches.

    Modes are selected from the full discrete Fourier lattice, ordered from
    low to high spatial wave number. The requested count is therefore bounded
    by the grid's actual number of independent periodic samples, not by a
    hand-written short list.
    """
    X, Y = np.meshgrid(x, y, indexing="ij")
    dx, dy = float(x[1] - x[0]), float(y[1] - y[0])
    length_x, length_y = x.size * dx, y.size * dy
    area = length_x * length_y
    x_indices = np.rint(np.fft.fftfreq(x.size) * x.size).astype(int)
    y_indices = np.rint(np.fft.fftfreq(y.size) * y.size).astype(int)
    indices = [(int(nx), int(ny)) for nx in x_indices for ny in y_indices]
    indices.sort(key=lambda pair: (pair[0] ** 2 + pair[1] ** 2, abs(pair[0]) + abs(pair[1]), pair[0], pair[1]))
    if not 1 <= int(count) <= len(indices):
        raise ValueError(f"count must be in 1..{len(indices)} for this grid.")
    return [np.exp(2j * np.pi * (nx * X / length_x + ny * Y / length_y)) / np.sqrt(area) for nx, ny in indices[:count]]


class GPELiveObservablePublisher:
    """Derive flow, modes, and vortices then publish one GPE observation frame."""
    def __init__(self, x: np.ndarray, y: np.ndarray, adapter: GPEOSCAdapter, *, mode_count: int = 16) -> None:
        self.x, self.y, self.adapter = np.asarray(x, dtype=float), np.asarray(y, dtype=float), adapter
        X, _ = np.meshgrid(self.x, self.y, indexing="ij")
        self.regions = (X >= 0.0).astype(int)
        basis = GeometryPotentialEngine2D(self.x, self.y).bind_eigenbasis(fourier_modes_2d(self.x, self.y, mode_count))
        self.projector = GPEModalProjector2D(basis)

    def publish(self, state: GPEState) -> int:
        flow = flow_from_wavefunction_2d(state.psi, self.x, self.y, time=state.time, regions=self.regions)
        return self.adapter.publish(
            state, flow=flow, modal=self.projector.project(state.psi, time=state.time),
            vortices=detect_vortices_2d(state.psi, self.x, self.y),
        )


__all__ = ["GPELiveObservablePublisher", "fourier_modes_2d"]
