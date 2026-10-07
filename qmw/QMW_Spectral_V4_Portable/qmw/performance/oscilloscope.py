"""Graphical read-only oscilloscope for unified performance snapshots."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
import queue
import time
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .inspector import InspectorFrame


BACKGROUND = "#080c12"
PANEL = "#101722"
GRID = "#263241"
TEXT = "#d8e2ec"
MUTED = "#7f91a4"
PHI = "#50d7ff"
PI = "#ff67d4"
ENERGY = "#ffbd59"
OCCUPATION = "#7ee787"
EVENT = "#ff765f"
RAW_PHASE = "#b99aff"
COVARIANT_PHASE = "#7ee787"


@dataclass(frozen=True)
class ScopeSample:
    revision: int
    logical_time: float
    phi: tuple[float, ...]
    pi: tuple[float, ...]
    energy: tuple[float, ...]
    occupations: tuple[float, ...]
    event_lanes: tuple[int | None, ...]


class OscilloscopeHistory:
    """Bounded history independent of the Tk renderer."""

    def __init__(self, max_frames: int = 360) -> None:
        if max_frames < 2:
            raise ValueError("max_frames must be at least 2")
        self.samples: deque[ScopeSample] = deque(maxlen=max_frames)
        self.selected_lane = 0
        self._selected_initial_lane = False

    def append(self, frame: "InspectorFrame") -> ScopeSample:
        sample = ScopeSample(
            revision=frame.source_revision,
            logical_time=frame.logical_time,
            phi=frame.mean_phi,
            pi=frame.mean_pi,
            energy=frame.local_energy,
            occupations=frame.occupations,
            event_lanes=tuple(event.lane for event in frame.events),
        )
        self.samples.append(sample)
        lanes = len(sample.phi)
        self.selected_lane = 0 if lanes == 0 else min(self.selected_lane, lanes - 1)
        if not self._selected_initial_lane and sample.energy:
            self.selected_lane = max(
                range(len(sample.energy)), key=lambda lane: sample.energy[lane]
            )
            self._selected_initial_lane = True
        return sample

    def select_lane(self, lane: int) -> int:
        lanes = len(self.samples[-1].phi) if self.samples else 0
        if lanes == 0:
            self.selected_lane = 0
        else:
            self.selected_lane = min(max(int(lane), 0), lanes - 1)
        return self.selected_lane

    def lane_series(self, name: str) -> tuple[float, ...]:
        if name not in {"phi", "pi", "energy"}:
            raise ValueError(f"unsupported lane series {name!r}")
        lane = self.selected_lane
        return tuple(
            float(getattr(sample, name)[lane])
            for sample in self.samples
            if lane < len(getattr(sample, name))
        )

    def lane_delta(self, name: str) -> float:
        series = self.lane_series(name)
        return 0.0 if len(series) < 2 else series[-1] - series[-2]

    def field_range(self) -> tuple[float, float]:
        values = (
            value
            for sample in self.samples
            for channel in (sample.phi, sample.pi)
            for value in channel
        )
        return _finite_range(values, symmetric=True)

    def energy_range(self) -> tuple[float, float]:
        values = tuple(
            value for sample in self.samples for value in sample.energy
        )
        if not values:
            return 0.0, 1.0
        _, high = _finite_range(values)
        return 0.0, max(high, 1e-9)


def _finite_range(values: Iterable[float], *, symmetric: bool = False) -> tuple[float, float]:
    finite = tuple(float(value) for value in values if math.isfinite(float(value)))
    if not finite:
        return (-1.0, 1.0) if symmetric else (0.0, 1.0)
    if symmetric:
        extent = max(max(abs(value) for value in finite), 1e-9)
        return -extent, extent
    low, high = min(finite), max(finite)
    if math.isclose(low, high, rel_tol=0.0, abs_tol=1e-12):
        padding = max(abs(low) * 0.05, 1e-9)
        return low - padding, high + padding
    return low, high


class QuantumOscilloscopeWindow:
    """Tk canvas renderer; it observes snapshots and never sends controls."""

    def __init__(self, root, *, history_frames: int = 360) -> None:
        import tkinter as tk

        self.root = root
        self.history = OscilloscopeHistory(history_frames)
        self.frames: queue.SimpleQueue[InspectorFrame] = queue.SimpleQueue()
        self.latest: InspectorFrame | None = None
        self.commit_times: deque[float] = deque()

        root.title("QMW Quantum Oscilloscope — Read Only")
        root.geometry("1120x760")
        root.minsize(820, 600)
        root.configure(bg=BACKGROUND)

        self.header = tk.Label(
            root,
            text="QMW QUANTUM OSCILLOSCOPE — WAITING FOR ATOMIC FRAMES",
            anchor="w",
            bg=BACKGROUND,
            fg=TEXT,
            font=("Menlo", 13, "bold"),
            padx=14,
            pady=9,
        )
        self.header.pack(fill="x")
        self.canvas = tk.Canvas(root, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _event: self.redraw())
        self.canvas.bind("<Button-1>", self._select_from_click)
        root.bind("<Left>", lambda _event: self._step_lane(-1))
        root.bind("<Right>", lambda _event: self._step_lane(1))
        root.after(16, self._drain_frames)

    def submit(self, frame: "InspectorFrame") -> None:
        self.frames.put(frame)

    def _drain_frames(self) -> None:
        changed = False
        while True:
            try:
                frame = self.frames.get_nowait()
            except queue.Empty:
                break
            self.latest = frame
            self.history.append(frame)
            now = time.monotonic()
            self.commit_times.append(now)
            while self.commit_times and self.commit_times[0] < now - 1.0:
                self.commit_times.popleft()
            changed = True
        if changed:
            self.redraw()
        self.root.after(16, self._drain_frames)

    def _step_lane(self, amount: int) -> None:
        self.history.select_lane(self.history.selected_lane + amount)
        self.redraw()

    def _select_from_click(self, event) -> None:
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        panels = self._panels(width, height)
        x0, y0, x1, y1 = panels[1]
        if self.latest is None or not (x0 <= event.x <= x1 and y0 <= event.y <= y1):
            return
        lanes = self._display_lane_count(self.latest)
        if lanes:
            fraction = (event.x - x0) / max(x1 - x0, 1)
            self.history.select_lane(round(fraction * (lanes - 1)))
            self.redraw()

    @staticmethod
    def _display_lane_count(frame: "InspectorFrame") -> int:
        if "view.density_population" in frame.capabilities:
            return len(frame.density_populations)
        if "view.hilbert_iq" in frame.capabilities:
            return len(frame.hilbert_in_phase)
        return len(frame.mean_phi)

    @staticmethod
    def _panels(width: int, height: int) -> tuple[tuple[float, float, float, float], ...]:
        margin = 14.0
        gap = 12.0
        usable_height = max(height - (2 * margin) - (2 * gap), 100.0)
        row_height = usable_height / 3.0
        usable_width = max(width - (2 * margin) - gap, 100.0)
        left_width = usable_width * 0.62
        right_width = usable_width - left_width
        return (
            (margin, margin, margin + left_width, margin + row_height),
            (margin + left_width + gap, margin, margin + left_width + gap + right_width, margin + row_height),
            (margin, margin + row_height + gap, margin + left_width, margin + (2 * row_height) + gap),
            (margin + left_width + gap, margin + row_height + gap, margin + left_width + gap + right_width, margin + (2 * row_height) + gap),
            (margin, margin + (2 * row_height) + (2 * gap), width - margin, height - margin),
        )

    def _panel(self, bounds, title: str) -> tuple[float, float, float, float]:
        x0, y0, x1, y1 = bounds
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=PANEL, outline=GRID)
        self.canvas.create_text(
            x0 + 10,
            y0 + 9,
            text=title,
            anchor="nw",
            fill=TEXT,
            font=("Menlo", 10, "bold"),
        )
        return x0 + 12, y0 + 35, x1 - 12, y1 - 14

    @staticmethod
    def _points(values: Iterable[float], bounds, value_range) -> list[float]:
        values = tuple(values)
        if not values:
            return []
        x0, y0, x1, y1 = bounds
        low, high = value_range
        span = max(high - low, 1e-12)
        points: list[float] = []
        for index, value in enumerate(values):
            x = x0 if len(values) == 1 else x0 + ((x1 - x0) * index / (len(values) - 1))
            y = y1 - ((float(value) - low) / span) * (y1 - y0)
            points.extend((x, y))
        return points

    def _grid(self, bounds, *, zero_range: tuple[float, float] | None = None) -> None:
        x0, y0, x1, y1 = bounds
        for index in range(1, 4):
            y = y0 + ((y1 - y0) * index / 4)
            self.canvas.create_line(x0, y, x1, y, fill=GRID)
        if zero_range is not None and zero_range[0] < 0.0 < zero_range[1]:
            zero_y = y1 - ((0.0 - zero_range[0]) / (zero_range[1] - zero_range[0])) * (y1 - y0)
            self.canvas.create_line(x0, zero_y, x1, zero_y, fill=MUTED, dash=(4, 4))

    def redraw(self) -> None:
        self.canvas.delete("all")
        if self.latest is None:
            self.canvas.create_text(
                24,
                30,
                anchor="nw",
                fill=MUTED,
                font=("Menlo", 12),
                text="Start QMW QFT V4.2 to feed UDP 17866.",
            )
            return

        frame = self.latest
        lane = self.history.selected_lane
        self.header.configure(
            text=(
                f"QMW QUANTUM OSCILLOSCOPE — READ ONLY   {frame.source_id}   "
                f"REV {frame.source_revision}   t={frame.logical_time:.5f}   "
                f"LIVE {len(self.commit_times):02d} fps   LANE {lane:02d}   "
                f"{frame.state_kind} / {frame.authority}"
            )
        )
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        history_panel, field_panel, energy_panel, mode_panel, gauge_panel = self._panels(width, height)

        if "view.density_population" in frame.capabilities and len(frame.density_populations) == frame.logical_audio_lanes:
            self._draw_density(history_panel, field_panel, energy_panel, mode_panel, frame, lane)
        elif "view.hilbert_iq" in frame.capabilities and len(frame.hilbert_in_phase) == frame.logical_audio_lanes:
            self._draw_hilbert_iq(history_panel, field_panel, energy_panel, mode_panel, frame, lane)
        elif "state.scalar_field" in frame.capabilities:
            self._draw_history(history_panel, lane)
            self._draw_field(field_panel, frame, lane)
            self._draw_energy(energy_panel, frame, lane)
            self._draw_modes(mode_panel, frame)
        else:
            self._draw_unsupported_body(history_panel, field_panel, energy_panel, mode_panel, frame)
        self._draw_gauge_phase(gauge_panel, frame)

    def _draw_unsupported_body(self, *panels, frame: "InspectorFrame") -> None:
        for index, panel in enumerate(panels):
            bounds = self._panel(panel, "CAPABILITY-GATED BODY" if index == 0 else "")
            if index == 0:
                self.canvas.create_text(
                    bounds[0], bounds[1], anchor="nw", fill=MUTED, font=("Menlo", 10),
                    text=("No graphical body is registered for this native state.\n"
                          "Declared capabilities: " + ", ".join(sorted(frame.capabilities))),
                )

    def _draw_density(self, history_panel, field_panel, energy_panel, mode_panel, frame: "InspectorFrame", lane: int) -> None:
        values = frame.density_populations
        purity = 0.0 if frame.density_purity is None else frame.density_purity
        coherence = 0.0 if frame.density_coherence_l1 is None else frame.density_coherence_l1
        self._draw_lane_bars(history_panel, values, lane, "DENSITY POPULATION — COMPUTATIONAL BASIS")
        self._draw_lane_line(field_panel, values, lane, "DENSITY POPULATIONS — CLICK TO SELECT BASIS WORD", OCCUPATION, (0.0, max(max(values), 1e-9)))
        bounds = self._panel(energy_panel, "DENSITY METRICS — READ-ONLY")
        self.canvas.create_text(bounds[0], bounds[1], anchor="nw", fill=TEXT, font=("Menlo", 11),
            text=f"purity                 {purity:.7g}\noff-diagonal L1 coherence {coherence:.7g}")
        bounds = self._panel(mode_panel, "SELECTED BASIS WORD")
        word = format(lane, "04b")
        self.canvas.create_text(bounds[0], bounds[1], anchor="nw", fill=OCCUPATION, font=("Menlo", 14, "bold"),
            text=f"|{word}>   population {values[lane]:.7g}")

    def _draw_hilbert_iq(self, history_panel, field_panel, energy_panel, mode_panel, frame: "InspectorFrame", lane: int) -> None:
        in_phase, quadrature = frame.hilbert_in_phase, frame.hilbert_quadrature
        extent = max(max((abs(value) for value in (*in_phase, *quadrature)), default=0.0), 1e-9)
        value_range = (-extent, extent)
        bounds = self._panel(history_panel, "HILBERT I/Q — EXPLICIT QUADRATURE OBSERVATION")
        self._grid(bounds, zero_range=value_range)
        for values, color in ((in_phase, PHI), (quadrature, PI)):
            points = self._points(values, bounds, value_range)
            if len(points) >= 4:
                self.canvas.create_line(*points, fill=color, width=2)
        self.canvas.create_text(bounds[0], bounds[1], anchor="nw", fill=PHI, font=("Menlo", 9), text="I")
        self.canvas.create_text(bounds[0] + 24, bounds[1], anchor="nw", fill=PI, font=("Menlo", 9), text="Q")
        magnitudes = tuple(math.hypot(i, q) for i, q in zip(in_phase, quadrature))
        self._draw_lane_bars(field_panel, magnitudes, lane, "I/Q MAGNITUDE — COMPUTATIONAL BASIS")
        phase = math.atan2(quadrature[lane], in_phase[lane])
        bounds = self._panel(energy_panel, "SELECTED I/Q LANE")
        self.canvas.create_text(bounds[0], bounds[1], anchor="nw", fill=TEXT, font=("Menlo", 11),
            text=f"|{format(lane, '04b')}>\nI {in_phase[lane]:+.7g}\nQ {quadrature[lane]:+.7g}\nphase {phase:+.7g} rad")
        phases = tuple(math.atan2(q, i) for i, q in zip(in_phase, quadrature))
        self._draw_lane_line(
            mode_panel, phases, lane, "I/Q PHASE — COMPUTATIONAL BASIS",
            RAW_PHASE, (-math.pi, math.pi),
        )

    def _draw_lane_bars(self, panel, values: tuple[float, ...], lane: int, title: str) -> None:
        bounds = self._panel(panel, title)
        if not values:
            return
        maximum = max(max(values), 1e-9)
        width = (bounds[2] - bounds[0]) / len(values)
        for index, value in enumerate(values):
            x0 = bounds[0] + index * width + 1
            x1 = bounds[0] + (index + 1) * width - 1
            y0 = bounds[3] - (value / maximum) * (bounds[3] - bounds[1])
            self.canvas.create_rectangle(x0, y0, x1, bounds[3], fill=TEXT if index == lane else OCCUPATION, outline="")

    def _draw_lane_line(self, panel, values: tuple[float, ...], lane: int, title: str, color: str, value_range) -> None:
        bounds = self._panel(panel, title)
        self._grid(bounds, zero_range=value_range)
        points = self._points(values, bounds, value_range)
        if len(points) >= 4:
            self.canvas.create_line(*points, fill=color, width=2)
            x = points[lane * 2]
            self.canvas.create_line(x, bounds[1], x, bounds[3], fill=TEXT, dash=(3, 3))

    def _draw_history(self, panel, lane: int) -> None:
        phi = self.history.lane_series("phi")
        pi = self.history.lane_series("pi")
        phi_now = phi[-1] if phi else 0.0
        pi_now = pi[-1] if pi else 0.0
        bounds = self._panel(
            panel,
            f"LANE {lane:02d} HISTORY   PHI {phi_now:+.4f}  d{self.history.lane_delta('phi'):+.4f}"
            f"   PI {pi_now:+.4f}  d{self.history.lane_delta('pi'):+.4f}",
        )
        value_range = self.history.field_range()
        self._grid(bounds, zero_range=value_range)
        for values, color in ((phi, PHI), (pi, PI)):
            points = self._points(values, bounds, value_range)
            if len(points) >= 4:
                self.canvas.create_line(*points, fill=color, width=2, smooth=True)
                self.canvas.create_oval(
                    points[-2] - 4,
                    points[-1] - 4,
                    points[-2] + 4,
                    points[-1] + 4,
                    fill=color,
                    outline=TEXT,
                )
        self.canvas.create_text(bounds[0], bounds[1], text="PHI", anchor="nw", fill=PHI, font=("Menlo", 9))
        self.canvas.create_text(bounds[0] + 42, bounds[1], text="PI", anchor="nw", fill=PI, font=("Menlo", 9))
        if any(sample.event_lanes for sample in self.history.samples):
            self.canvas.create_text(bounds[2], bounds[1], text="EVENTS PRESENT", anchor="ne", fill=EVENT, font=("Menlo", 9))

    def _draw_field(self, panel, frame: "InspectorFrame", lane: int) -> None:
        bounds = self._panel(panel, "CURRENT SITE FIELD   CLICK TO SELECT LANE")
        value_range = self.history.field_range()
        self._grid(bounds, zero_range=value_range)
        for values, color in ((frame.mean_phi, PHI), (frame.mean_pi, PI)):
            points = self._points(values, bounds, value_range)
            if len(points) >= 4:
                self.canvas.create_line(*points, fill=color, width=2)
                for index in range(0, len(points), 2):
                    self.canvas.create_oval(points[index] - 2, points[index + 1] - 2, points[index] + 2, points[index + 1] + 2, fill=color, outline="")
        if len(frame.mean_phi) > 1:
            x = bounds[0] + ((bounds[2] - bounds[0]) * lane / (len(frame.mean_phi) - 1))
            self.canvas.create_line(x, bounds[1], x, bounds[3], fill=TEXT, dash=(3, 3))

    def _draw_energy(self, panel, frame: "InspectorFrame", lane: int) -> None:
        values = frame.local_energy
        if not values:
            return
        selected = values[lane] if lane < len(values) else 0.0
        bounds = self._panel(
            panel,
            f"LOCAL ENERGY — SITE BASIS   LANE {lane:02d} {selected:.5g}  "
            f"d{self.history.lane_delta('energy'):+.3g}",
        )
        low, high = self.history.energy_range()
        baseline = bounds[3]
        width = (bounds[2] - bounds[0]) / len(values)
        span = max(high - low, 1e-12)
        for index, value in enumerate(values):
            fraction = (value - low) / span
            x0 = bounds[0] + index * width + 1
            x1 = bounds[0] + (index + 1) * width - 1
            y0 = baseline - fraction * (bounds[3] - bounds[1])
            color = TEXT if index == lane else ENERGY
            self.canvas.create_rectangle(x0, y0, x1, baseline, fill=color, outline="")
        self.canvas.create_text(bounds[0], bounds[1], text=f"fixed rolling scale: 0 .. {high:.5g}", anchor="nw", fill=MUTED, font=("Menlo", 9))

    def _draw_modes(self, panel, frame: "InspectorFrame") -> None:
        bounds = self._panel(
            panel,
            "NORMAL-MODE OCCUPATION — FREE-FIELD INVARIANT (EXPECTED STATIC)",
        )
        values = frame.occupations
        if not values:
            return
        maximum = max(max(values), 1e-12)
        baseline = bounds[3]
        width = (bounds[2] - bounds[0]) / len(values)
        for index, value in enumerate(values):
            x0 = bounds[0] + index * width + 1
            x1 = bounds[0] + (index + 1) * width - 1
            y0 = baseline - (value / maximum) * (bounds[3] - bounds[1])
            self.canvas.create_rectangle(x0, y0, x1, baseline, fill=OCCUPATION, outline="")
        self.canvas.create_text(bounds[0], bounds[1], text=f"max {maximum:.5g}", anchor="nw", fill=MUTED, font=("Menlo", 9))

    def _draw_gauge_phase(self, panel, frame: "InspectorFrame") -> None:
        view = frame.gauge_phase
        title = "GAUGE PHASE — RAW Δφ / A / COVARIANT Δφ (READ ONLY)"
        bounds = self._panel(panel, title)
        if view is None:
            self.canvas.create_text(bounds[0], bounds[1], anchor="nw", fill=MUTED, font=("Menlo", 10),
                text="Awaiting a revision-matched gauge phase frame. Raw phase is gauge-dependent; covariant phase and holonomy are invariant.")
            return
        node_text = "RAW NODE φ  " + "  ".join(f"{index}:{phase:+.2f}" for index, phase in enumerate(view.node_raw_phase[:10]))
        self.canvas.create_text(bounds[0], bounds[1], text=node_text, anchor="nw", fill=RAW_PHASE, font=("Menlo", 9))
        self.canvas.create_text(bounds[0], bounds[1] + 17, text="EDGE       RAW Δφ       A       COV Δφ       J", anchor="nw", fill=TEXT, font=("Menlo", 9, "bold"))
        row_y = bounds[1] + 33
        for edge in view.edges[:5]:
            self.canvas.create_text(bounds[0], row_y, anchor="nw", fill=RAW_PHASE, font=("Menlo", 9),
                text=f"{edge.source:02d}->{edge.destination:02d}    {edge.raw_phase_difference:+.3f}")
            self.canvas.create_text(bounds[0] + 220, row_y, anchor="nw", fill=MUTED, font=("Menlo", 9), text=f"{edge.connection_phase:+.3f}")
            self.canvas.create_text(bounds[0] + 315, row_y, anchor="nw", fill=COVARIANT_PHASE, font=("Menlo", 9), text=f"{edge.covariant_phase_difference:+.3f}")
            self.canvas.create_text(bounds[0] + 440, row_y, anchor="nw", fill=ENERGY, font=("Menlo", 9), text=f"{edge.current:+.4f}")
            row_y += 15
        if len(view.edges) > 5:
            self.canvas.create_text(bounds[0] + 510, bounds[1] + 17, anchor="nw", fill=MUTED, font=("Menlo", 9), text=f"+{len(view.edges) - 5} edges")
        faces = "  ".join(f"{name}={value:+.3f}" for name, value in view.face_holonomies.items()) or "none declared"
        self.canvas.create_text(bounds[0] + 550, bounds[1], anchor="nw", fill=COVARIANT_PHASE, font=("Menlo", 9), text="FACE HOLONOMY  " + faces)


def run_graphical_inspector(host: str, port: int, *, history_frames: int = 360) -> None:
    """Own one UDP receiver and render its committed frames on the Tk main thread."""

    import tkinter as tk
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import BlockingOSCUDPServer

    from .inspector import InstrumentInspectorModel
    from .osc import OSC_ROOT

    root = tk.Tk()
    window = QuantumOscilloscopeWindow(root, history_frames=history_frames)
    model = InstrumentInspectorModel(on_commit=window.submit)
    dispatcher = Dispatcher()
    dispatcher.map(f"{OSC_ROOT}/*", lambda address, *values: model.accept(address, *values))
    dispatcher.map(f"{OSC_ROOT}/*/*", lambda address, *values: model.accept(address, *values))
    # One snapshot is a transaction spread across ordered UDP datagrams.  The
    # receiver itself lives off the Tk thread, but packet handlers must remain
    # serial so begin/state/channel/end cannot overtake one another.
    server = BlockingOSCUDPServer((host, port), dispatcher)

    import threading

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    def close() -> None:
        server.shutdown()
        server.server_close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    print(f"QMW Quantum Oscilloscope listening on {host}:{port}", flush=True)
    root.mainloop()


__all__ = [
    "OscilloscopeHistory",
    "QuantumOscilloscopeWindow",
    "ScopeSample",
    "run_graphical_inspector",
]
