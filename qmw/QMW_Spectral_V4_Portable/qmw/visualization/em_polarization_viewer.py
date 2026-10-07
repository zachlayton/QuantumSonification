"""Matplotlib view of the transverse field, plane wave, and Poincare state."""

from __future__ import annotations

import math
import time
from typing import Callable

import numpy as np

from qmw.electromagnetic.polarization_state import PolarizationFrame


class EMPolarizationViewer:
    """A small synchronized V1 viewer with a relative-phase slider.

    Matplotlib is imported only when the viewer is constructed, keeping the
    electromagnetic package usable in headless and audio-only processes.
    """

    def __init__(
        self,
        frame_provider: Callable[[float], PolarizationFrame],
        set_relative_phase: Callable[[float], None],
        *,
        initial_relative_phase: float = math.pi / 2.0,
        frame_observer: Callable[[PolarizationFrame], None] | None = None,
    ) -> None:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from matplotlib.widgets import Slider

        self._plt = plt
        self._frame_provider = frame_provider
        self._frame_observer = frame_observer
        self._start_time = time.monotonic()
        self.figure = plt.figure(figsize=(15, 5.4))
        grid = self.figure.add_gridspec(1, 3, left=0.04, right=0.98, bottom=0.2)
        self.transverse_axis = self.figure.add_subplot(grid[0, 0])
        self.wave_axis = self.figure.add_subplot(grid[0, 1], projection="3d")
        self.poincare_axis = self.figure.add_subplot(grid[0, 2], projection="3d")
        slider_axis = self.figure.add_axes((0.17, 0.07, 0.66, 0.04))
        self.slider = Slider(
            slider_axis,
            "relative phase delta",
            -math.pi,
            math.pi,
            valinit=float(initial_relative_phase),
        )
        self.slider.on_changed(lambda value: set_relative_phase(float(value)))
        self._animation = FuncAnimation(
            self.figure,
            self._draw,
            interval=33,
            cache_frame_data=False,
        )

    @staticmethod
    def _ellipse(frame: PolarizationFrame, count: int = 256) -> np.ndarray:
        phase = np.linspace(0.0, math.tau, count, endpoint=True)
        rotation = np.exp(1j * phase)
        return np.column_stack(
            (
                np.real(frame.jones.ex * rotation),
                np.real(frame.jones.ey * rotation),
            )
        )

    @staticmethod
    def _sphere(count_u: int = 32, count_v: int = 18):
        u = np.linspace(0.0, math.tau, count_u)
        v = np.linspace(0.0, math.pi, count_v)
        return (
            np.outer(np.cos(u), np.sin(v)),
            np.outer(np.sin(u), np.sin(v)),
            np.outer(np.ones_like(u), np.cos(v)),
        )

    def _draw(self, _frame_index):
        elapsed = time.monotonic() - self._start_time
        frame = self._frame_provider(elapsed)
        if self._frame_observer is not None:
            self._frame_observer(frame)

        ellipse = self._ellipse(frame)
        limit = 1.15 * max(frame.jones.amplitude_x, frame.jones.amplitude_y, 1.0e-6)
        axis = self.transverse_axis
        axis.clear()
        axis.plot(ellipse[:, 0], ellipse[:, 1], color="#21b7c6", linewidth=2.0)
        axis.quiver(
            0.0,
            0.0,
            frame.electric_field[0],
            frame.electric_field[1],
            angles="xy",
            scale_units="xy",
            scale=1.0,
            color="#e34f6f",
            width=0.014,
        )
        axis.set(xlim=(-limit, limit), ylim=(-limit, limit), xlabel="E_x", ylabel="E_y")
        axis.set_aspect("equal")
        axis.grid(alpha=0.25)
        axis.set_title(
            f"Polarization ellipse\n{frame.poincare.polarization_kind}; "
            f"delta={frame.relative_phase:+.3f} rad"
        )

        wave_axis = self.wave_axis
        wave_axis.clear()
        z = np.linspace(0.0, 2.0, 240)
        phase = math.tau * z + frame.carrier_phase
        ex = np.real(frame.jones.ex * np.exp(1j * phase))
        ey = np.real(frame.jones.ey * np.exp(1j * phase))
        wave_axis.plot(z, ex, ey, color="#6f58c9", linewidth=2.0)
        wave_axis.plot(z, ex, np.zeros_like(z), color="#e34f6f", alpha=0.45)
        wave_axis.plot(z, np.zeros_like(z), ey, color="#21b7c6", alpha=0.45)
        wave_axis.set(xlabel="z / wavelength", ylabel="E_x", zlabel="E_y")
        wave_axis.set_title("Analytic +z plane wave")
        wave_axis.set_box_aspect((1.6, 1.0, 1.0))

        paxis = self.poincare_axis
        paxis.clear()
        sx, sy, sz = self._sphere()
        paxis.plot_wireframe(sx, sy, sz, color="#8f9aa8", alpha=0.22, linewidth=0.5)
        point = frame.poincare.vector()
        paxis.quiver(0.0, 0.0, 0.0, *point, color="#f2a93b", linewidth=2.5)
        paxis.scatter(*point, color="#f2a93b", s=55)
        paxis.set(
            xlim=(-1.05, 1.05),
            ylim=(-1.05, 1.05),
            zlim=(-1.05, 1.05),
            xlabel="S1/S0",
            ylabel="S2/S0",
            zlabel="S3/S0",
        )
        paxis.set_box_aspect((1.0, 1.0, 1.0))
        paxis.set_title("Poincare sphere")
        self.figure.suptitle(
            "QMW electromagnetic polarization V1 — Jones phase is authoritative"
        )
        return ()

    def show(self) -> None:
        self._plt.show()


__all__ = ["EMPolarizationViewer"]
