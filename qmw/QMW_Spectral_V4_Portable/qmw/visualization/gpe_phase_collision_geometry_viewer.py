"""Read-only py5 graphs for a completed Phase Collision I geometry sweep.

The viewer renders data already stored in ``PhaseCollisionISweep``.  It never
steps the GPE, modifies a potential, starts OSC, or turns a geometry spectrum
into an acoustic scale.  Use the number keys ``1`` through ``4`` to select the
relative phase whose material-drive and final geometry-mode distribution are
shown in the lower panels.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from qmw.gpe.phase_collision_i import PhaseCollisionISweep


@dataclass(frozen=True)
class GeometryCollisionTraceData:
    """Plot-ready read-only measurements from one relative-phase trace."""

    label: str
    time: np.ndarray
    regional_flux: np.ndarray
    material_drive: np.ndarray
    final_geometry_power: np.ndarray
    eigenvalues: np.ndarray | None
    initial_energy: float
    final_energy: float


def geometry_collision_trace_data(sweep: PhaseCollisionISweep) -> tuple[GeometryCollisionTraceData, ...]:
    """Extract bounded scalar plot data without retaining or changing ``psi``."""

    phase_names = ((0.0, "0"), (float(np.pi / 4.0), "π/4"), (float(np.pi / 2.0), "π/2"), (float(np.pi), "π"))
    result: list[GeometryCollisionTraceData] = []
    for index, trace in enumerate(sweep.traces):
        if not trace.frames or any(frame.geometry_modes is None for frame in trace.frames):
            raise ValueError("each trace must contain FieldFrames with verified geometry-mode observations.")
        final_modes = trace.frames[-1].geometry_modes
        assert final_modes is not None
        result.append(GeometryCollisionTraceData(
            label=next((name for value, name in phase_names if np.isclose(trace.phase, value)), f"θ={trace.phase:.3f}"),
            time=np.array([frame.time for frame in trace.frames], dtype=float),
            regional_flux=np.array([frame.region_flux[1] for frame in trace.frames], dtype=float),
            material_drive=np.array(
                [domain.energy_materiality.material_drive for domain in trace.musical_domains], dtype=float,
            ),
            final_geometry_power=np.array(final_modes.power, dtype=float),
            eigenvalues=None if final_modes.eigenvalues is None else np.array(final_modes.eigenvalues, dtype=float),
            initial_energy=float(trace.frames[0].total_energy),
            final_energy=float(trace.frames[-1].total_energy),
        ))
    return tuple(result)


class GPEPhaseCollisionGeometryViewer:
    """A py5 window for flow, geometry modes, and materiality of one sweep."""

    PHASE_COLORS = ((61, 145, 64), (34, 133, 211), (245, 146, 44), (191, 72, 88))

    def __init__(self, sweep: PhaseCollisionISweep, *, width: int = 1180, height: int = 840) -> None:
        if width < 720 or height < 560:
            raise ValueError("viewer width and height must leave room for three labeled graphs.")
        self.traces = geometry_collision_trace_data(sweep)
        if len(self.traces) < 2:
            raise ValueError("Phase Collision I viewer requires at least two relative-phase traces.")
        self.width = int(width)
        self.height = int(height)
        self.selected_phase = 0
        self.py5: Any = None

    def run(self, py5_module: Any) -> None:
        """Open the local py5 window with a deliberately injected runtime."""

        self.py5 = py5_module
        py5_module.run_sketch(sketch_functions={
            "settings": self.settings,
            "setup": self.setup,
            "draw": self.draw,
            "key_pressed": self.key_pressed,
        }, block=True)

    def settings(self) -> None:
        self.py5.size(self.width, self.height)

    def setup(self) -> None:
        p = self.py5
        p.window_title("QMW GPE Phase Collision I — Geometry Modes")
        p.text_font(p.create_font("SansSerif", 14))
        p.no_loop()

    def key_pressed(self) -> None:
        try:
            requested = int(str(self.py5.key)) - 1
        except ValueError:
            return
        if 0 <= requested < len(self.traces):
            self.selected_phase = requested
            self.py5.redraw()

    @staticmethod
    def _range(values: np.ndarray, *, include_zero: bool = False) -> tuple[float, float]:
        low, high = float(np.min(values)), float(np.max(values))
        if include_zero:
            low, high = min(low, 0.0), max(high, 0.0)
        if abs(high - low) < 1.0e-12:
            return low - 0.5, high + 0.5
        padding = 0.06 * (high - low)
        return low - padding, high + padding

    @staticmethod
    def _map(value: float, source: tuple[float, float], target: tuple[float, float]) -> float:
        return target[0] + (value - source[0]) * (target[1] - target[0]) / (source[1] - source[0])

    def _panel(self, x: float, y: float, width: float, height: float, title: str, y_label: str) -> tuple[float, float, float, float]:
        p = self.py5
        p.stroke(82)
        p.stroke_weight(1)
        p.fill(22)
        p.rect(x, y, width, height)
        p.fill(232)
        p.text_size(16)
        p.text(title, x + 12, y + 23)
        p.push_matrix()
        p.translate(x + 16, y + height / 2)
        p.rotate(-p.HALF_PI)
        p.text_size(12)
        p.text(y_label, 0, 0)
        p.pop_matrix()
        return x + 62, y + 38, width - 82, height - 74

    def _axes(
        self,
        bounds: tuple[float, float, float, float],
        x_range: tuple[float, float],
        y_range: tuple[float, float],
        *,
        x_label: str = "time",
        zero_line: bool = False,
    ) -> None:
        p = self.py5
        x, y, width, height = bounds
        p.stroke(72)
        p.fill(172)
        p.text_size(11)
        for fraction in np.linspace(0.0, 1.0, 5):
            chart_y = y + height * (1.0 - fraction)
            value = y_range[0] + fraction * (y_range[1] - y_range[0])
            p.line(x, chart_y, x + width, chart_y)
            p.no_stroke()
            p.text(f"{value:.3f}", x - 8, chart_y + 4)
            p.stroke(72)
        if zero_line and y_range[0] <= 0.0 <= y_range[1]:
            zero_y = self._map(0.0, y_range, (y + height, y))
            p.stroke(190)
            p.line(x, zero_y, x + width, zero_y)
        p.no_stroke()
        for fraction in np.linspace(0.0, 1.0, 5):
            chart_x = x + width * fraction
            value = x_range[0] + fraction * (x_range[1] - x_range[0])
            p.text(f"{value:.2f}", chart_x - 10, y + height + 18)
        p.text(x_label, x + width / 2 - 12, y + height + 38)

    def _line(self, values: np.ndarray, x_values: np.ndarray, bounds: tuple[float, float, float, float], x_range: tuple[float, float], y_range: tuple[float, float], color: tuple[int, int, int], *, weight: float, alpha: int = 255) -> None:
        p = self.py5
        x, y, width, height = bounds
        p.no_fill()
        p.stroke(*color, alpha)
        p.stroke_weight(weight)
        p.begin_shape()
        for time, value in zip(x_values, values):
            p.vertex(self._map(float(time), x_range, (x, x + width)), self._map(float(value), y_range, (y + height, y)))
        p.end_shape()

    def _draw_flux(self) -> None:
        p = self.py5
        panel = self._panel(22, 70, self.width - 44, 290, "Regional boundary flux — all phase preparations", "net inward flux")
        all_flux = np.concatenate([trace.regional_flux for trace in self.traces])
        x_range = self._range(self.traces[0].time)
        y_range = self._range(all_flux, include_zero=True)
        self._axes(panel, x_range, y_range, zero_line=True)
        x, y, width, height = panel
        for index, trace in enumerate(self.traces):
            color = self.PHASE_COLORS[index % len(self.PHASE_COLORS)]
            active = index == self.selected_phase
            self._line(trace.regional_flux, trace.time, panel, x_range, y_range, color, weight=3.0 if active else 1.5, alpha=255 if active else 135)
            p.fill(*color)
            p.text_size(12)
            end_y = self._map(float(trace.regional_flux[-1]), y_range, (y + height, y))
            p.text(trace.label, x + width - 24, end_y - 4)

    def _draw_materiality(self) -> None:
        trace = self.traces[self.selected_phase]
        panel = self._panel(22, 394, self.width * 0.52 - 32, self.height - 420, f"Materiality drive — θ = {trace.label}", "material drive")
        x_range = self._range(trace.time)
        y_range = self._range(trace.material_drive)
        self._axes(panel, x_range, y_range)
        self._line(trace.material_drive, trace.time, panel, x_range, y_range, self.PHASE_COLORS[self.selected_phase % len(self.PHASE_COLORS)], weight=2.5)
        p = self.py5
        p.fill(220)
        p.text_size(12)
        p.text(f"E: {trace.initial_energy:.5f} → {trace.final_energy:.5f}", panel[0], panel[1] + 14)

    def _draw_modes(self) -> None:
        p = self.py5
        trace = self.traces[self.selected_phase]
        x0 = self.width * 0.52 + 10
        panel = self._panel(x0, 394, self.width - x0 - 22, self.height - 420, f"Final geometry-mode power — θ = {trace.label}", "|aₙ|²")
        x, y, width, height = panel
        y_range = self._range(trace.final_geometry_power, include_zero=True)
        self._axes(panel, (0.0, float(trace.final_geometry_power.size - 1)), y_range, x_label="geometry mode index")
        bar_width = width / trace.final_geometry_power.size
        color = self.PHASE_COLORS[self.selected_phase % len(self.PHASE_COLORS)]
        p.no_stroke()
        for index, power in enumerate(trace.final_geometry_power):
            left = x + index * bar_width + 2
            top = self._map(float(power), y_range, (y + height, y))
            p.fill(*color, 210)
            p.rect(left, top, max(bar_width - 4, 1.0), y + height - top)
            p.fill(185)
            p.text_size(10)
            p.text(str(index), left + 2, y + height + 16)
        leader = int(np.argmax(trace.final_geometry_power))
        eigenvalue = "unavailable" if trace.eigenvalues is None else f"{trace.eigenvalues[leader]:.4f}"
        p.fill(220)
        p.text_size(12)
        p.text(f"dominant mode {leader}; eigenvalue {eigenvalue}; power {trace.final_geometry_power[leader]:.4f}", x, y + 14)

    def draw(self) -> None:
        p = self.py5
        p.background(12)
        p.fill(244)
        p.text_size(22)
        p.text("QMW GPE Phase Collision I — Verified Double-Well Geometry Modes", 22, 32)
        p.fill(170)
        p.text_size(13)
        choices = "   ".join(f"[{index + 1}] θ={trace.label}" for index, trace in enumerate(self.traces))
        p.text(f"Select phase: {choices}     current θ={self.traces[self.selected_phase].label}", 22, 54)
        self._draw_flux()
        self._draw_materiality()
        self._draw_modes()


__all__ = ["GeometryCollisionTraceData", "GPEPhaseCollisionGeometryViewer", "geometry_collision_trace_data"]
