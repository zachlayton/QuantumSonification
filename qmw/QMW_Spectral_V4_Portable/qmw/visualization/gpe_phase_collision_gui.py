"""Direct-manipulation GUI for prepared 2-D GPE phase collisions."""

from __future__ import annotations

import math
from queue import Empty, SimpleQueue
from threading import Thread
from typing import Any

import numpy as np

from qmw.gpe.live_observables import GPELiveObservablePublisher
from qmw.gpe.phase_collision import PhaseCollisionExperiment2D
from qmw.osc.gpe_field_frame_osc import GPEFieldFrameOSCAdapter
from qmw.osc.gpe_osc import GPEOSCAdapter


class GPEPhaseCollisionGUI:
    """Animate density/phase while sliders restart a declared field preparation."""
    def __init__(self, experiment: PhaseCollisionExperiment2D | None = None, *, fps: float = 30.0, osc_port: int | None = None, field_frame_port: int | None = None, control_port: int | None = None) -> None:
        if fps <= 0.0:
            raise ValueError("fps must be positive.")
        self.experiment = experiment or PhaseCollisionExperiment2D()
        self.fps = float(fps)
        self.running = True
        self.gpe_enabled = self.experiment.engine.evolution_enabled
        self._images: tuple[Any, Any] | None = None
        self._timer = None
        self._control_port = control_port
        self._control_updates: SimpleQueue[tuple[str, float]] = SimpleQueue()
        self._control_server = None
        self._control_thread: Thread | None = None
        self.publisher = None if osc_port is None else GPELiveObservablePublisher(
            self.experiment.axis, self.experiment.axis, GPEOSCAdapter.from_udp(port=int(osc_port)), mode_count=8,
        )
        # Four physical regions keep the FieldFrame's regional population and
        # flux lanes meaningful without changing the evolving GPE field.
        axis = self.experiment.axis
        self._field_frame_regions = ((axis[:, None] >= 0.0).astype(int) * 2) + (axis[None, :] >= 0.0).astype(int)
        self._previous_field_frame = None
        self.field_frame_publisher = None if field_frame_port is None else GPEFieldFrameOSCAdapter.from_udp(
            port=int(field_frame_port), mode_count=16,
        )

    def queue_control(self, name: str, value: float) -> None:
        """Stage a local OSC phase-collision control for the GUI thread."""
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f"GPE control {name!r} must be finite.")
        if name == "phase" and not 0.0 <= value <= 2.0 * math.pi:
            raise ValueError("GPE phase control must lie in [0, 2*pi].")
        if name == "interaction" and not -1.0 <= value <= 2.0:
            raise ValueError("GPE interaction control must lie in [-1, 2].")
        if name == "enabled" and value not in {0.0, 1.0}:
            raise ValueError("GPE enabled control must be exactly 0 or 1.")
        if name not in {"phase", "interaction", "enabled"}:
            raise ValueError(f"unsupported GPE control: {name!r}")
        self._control_updates.put((name, value))

    def set_gpe_enabled(self, enabled: bool):
        """Set the master GPE evolution gate and suppress downstream GPE frames when off."""

        self.gpe_enabled = bool(enabled)
        if self._previous_field_frame is not None and not self.gpe_enabled:
            # A resumed GPE episode should not claim a finite-difference
            # continuity residual across an intentionally disabled interval.
            self._previous_field_frame = None
        return self.experiment.engine.set_evolution_enabled(self.gpe_enabled)

    def consume_control_updates(self) -> dict[str, float]:
        """Return the latest queued value of each control without touching Qt."""
        updates: dict[str, float] = {}
        while True:
            try:
                name, value = self._control_updates.get_nowait()
            except Empty:
                return updates
            updates[name] = value

    def _start_control_server(self) -> None:
        if self._control_port is None:
            return
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer

        dispatcher = Dispatcher()
        dispatcher.map("/qmw/gpe/control/phase", lambda _address, value: self.queue_control("phase", value))
        dispatcher.map("/qmw/gpe/control/interaction", lambda _address, value: self.queue_control("interaction", value))
        dispatcher.map("/qmw/gpe/control/enabled", lambda _address, value: self.queue_control("enabled", value))
        self._control_server = ThreadingOSCUDPServer(("127.0.0.1", int(self._control_port)), dispatcher)
        self._control_thread = Thread(target=self._control_server.serve_forever, daemon=True)
        self._control_thread.start()

    def _stop_control_server(self) -> None:
        if self._control_server is not None:
            self._control_server.shutdown()
            self._control_server.server_close()
            self._control_server = None

    def _refresh(self, state) -> None:
        density, phase = state.density, state.phase
        images = self._images
        if images is None:
            raise RuntimeError("GPE display must be initialized before it is refreshed.")
        images[0].set_data(density)
        images[1].set_data(phase)
        mode = "GPE ON" if state.evolution_enabled else "GPE OFF — field held; no GPE output"
        images[0].axes.set_title(f"density |psi| squared  t={state.time:.2f}  {mode}")
        images[0].figure.canvas.draw_idle()
        if state.evolution_enabled and self.publisher is not None:
            self.publisher.publish(state)
        if state.evolution_enabled and self.field_frame_publisher is not None:
            frame = self.experiment.engine.field_frame(
                coordinates=(self.experiment.axis, self.experiment.axis),
                regions=self._field_frame_regions,
                previous=self._previous_field_frame,
            )
            self.field_frame_publisher.publish(frame, phase=self.experiment.parameters.phase)
            self._previous_field_frame = frame

    def run(self) -> None:
        """Open the GUI. Phase and g sliders restart the explicit t=0 preparation."""
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Button, Slider

        state = self.experiment.engine.state()
        figure, axes = plt.subplots(1, 2, num="QMW GPE phase collision")
        figure.subplots_adjust(bottom=0.28)
        density = axes[0].imshow(state.density, origin="lower", cmap="magma", aspect="equal")
        phase = axes[1].imshow(state.phase, origin="lower", cmap="twilight", aspect="equal", vmin=-math.pi, vmax=math.pi)
        axes[0].set_title("density |psi| squared")
        axes[1].set_title("phase arg psi")
        figure.colorbar(density, ax=axes[0])
        figure.colorbar(phase, ax=axes[1])
        self._images = (density, phase)
        # Deliver a complete observation immediately after the display exists.
        # The timer continues the live stream; this first transaction prevents
        # the downstream FieldFrame panel from depending on a backend's first
        # timer callback.
        self._refresh(state)
        phase_slider = Slider(figure.add_axes((0.18, 0.15, 0.56, 0.03)), "relative phase theta", 0.0, 2.0 * math.pi, valinit=self.experiment.parameters.phase)
        g_slider = Slider(figure.add_axes((0.18, 0.09, 0.56, 0.03)), "interaction g", -1.0, 2.0, valinit=self.experiment.parameters.interaction)
        gpe_button = Button(figure.add_axes((0.77, 0.135, 0.17, 0.055)), "GPE: ON")
        button = Button(figure.add_axes((0.77, 0.065, 0.17, 0.055)), "pause")

        def reset_from_values(phase_value: float, interaction_value: float) -> None:
            parameters = self.experiment.parameters
            self._previous_field_frame = None
            state = self.experiment.reset(type(parameters)(
                phase=phase_value, interaction=interaction_value,
                separation=parameters.separation, width=parameters.width,
                incident_wavenumber=parameters.incident_wavenumber,
            ))
            state = self.set_gpe_enabled(self.gpe_enabled)
            self._refresh(state)

        def reset_from_controls(_: float) -> None:
            reset_from_values(phase_slider.val, g_slider.val)

        def toggle(_: object) -> None:
            self.running = not self.running
            button.label.set_text("pause" if self.running else "play")

        def toggle_gpe(_: object) -> None:
            state = self.set_gpe_enabled(not self.gpe_enabled)
            gpe_button.label.set_text("GPE: ON" if self.gpe_enabled else "GPE: OFF")
            self._refresh(state)

        phase_slider.on_changed(reset_from_controls)
        g_slider.on_changed(reset_from_controls)
        button.on_clicked(toggle)
        gpe_button.on_clicked(toggle_gpe)

        def apply_queued_controls() -> None:
            updates = self.consume_control_updates()
            if not updates:
                return
            phase_value = updates.get("phase", phase_slider.val)
            interaction_value = updates.get("interaction", g_slider.val)
            enabled = updates.get("enabled")
            phase_slider.eventson = False
            g_slider.eventson = False
            phase_slider.set_val(phase_value)
            g_slider.set_val(interaction_value)
            phase_slider.eventson = True
            g_slider.eventson = True
            if "phase" in updates or "interaction" in updates:
                reset_from_values(phase_value, interaction_value)
            if enabled is not None:
                state = self.set_gpe_enabled(bool(enabled))
                gpe_button.label.set_text("GPE: ON" if self.gpe_enabled else "GPE: OFF")
                self._refresh(state)

        self._start_control_server()
        self._timer = figure.canvas.new_timer(interval=int(1000.0 / self.fps))
        self._timer.add_callback(lambda: (apply_queued_controls(), self._refresh(self.experiment.step(1.0 / self.fps)) if self.running and self.gpe_enabled else None))
        self._timer.start()
        try:
            plt.show()
        finally:
            self._stop_control_server()


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--osc-port", type=int, help="optionally publish GPE observables to this local UDP port")
    parser.add_argument("--field-frame-port", type=int, help="optionally publish synchronized FieldFrame v2 observations to this local UDP port")
    parser.add_argument("--control-port", type=int, help="optionally receive local phase, interaction, and GPE enabled controls on this UDP port")
    args = parser.parse_args()
    GPEPhaseCollisionGUI(
        osc_port=args.osc_port, field_frame_port=args.field_frame_port, control_port=args.control_port,
    ).run()


if __name__ == "__main__":
    main()
