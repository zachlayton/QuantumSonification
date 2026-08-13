#!/usr/bin/env python3
"""Realtime GUI: adjust an algebraic surface, hear it through Sonic Pi.

Every control edit is debounced and recomputed on a background thread so
the window never freezes; only controls that change the surface itself
(family, equation parameter, sampling resolution/bound, radius) trigger a
re-mesh and re-solve. Sound-design controls (active mode count, material
model, wave speed, T60, damping) reuse the cached mesh/eigensolve and are
effectively instant.

Turning on "Quantum drive" hands sound design over to a live 4-qubit
density matrix (quantum_conductor_v1.QuantumPhaseConductor): its
continuously evolving coherence phases shimmer each mode's amplitude and
pan at ~20 Hz, while smoothed coherence/Bloch-vector statistics drift the
wave speed, T60, and damping tilt sliders on their own -- the same
debounce/cache path manual dragging uses, just driven by the engine
instead of your hand.

Run:
    python -m algebraic_surface_sonicpi_gui_v1.gui_v1

Requires Sonic Pi running locally with "Enable OSC Server" turned on in
Preferences -> IO, and algebraic_surface_sonicpi_gui_v1/sonic_pi_receiver_v1.rb
pasted into a Sonic Pi buffer and running. See README.md in this package.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable

from .realtime_bridge_v1 import (
    MATERIAL_MODEL_NAMES,
    SURFACE_NAMES,
    RealtimeSurfaceConfig,
    SonicPiModeStreamer,
    SurfaceModeCache,
    compute_modal_packet,
)
from .osc_client_v1 import SonicPiOSCClient

# quantum_conductor_v1 pulls in density.density_matrix_engine_4q's full
# dependency chain (notably scikit-learn). The rest of this GUI has no
# dependency on it, so a missing chain only disables the "Quantum drive"
# section rather than the whole window.
try:
    from .quantum_conductor_v1 import (
        QuantumConductorConfig,
        QuantumPhaseConductor,
        SlowUpdate,
    )

    QUANTUM_DRIVE_IMPORT_ERROR: Exception | None = None
except ImportError as exc:
    QUANTUM_DRIVE_IMPORT_ERROR = exc

DEBOUNCE_MS = 180


class _SliderRow:
    """A labeled ttk.Scale with a live value readout."""

    def __init__(
        self,
        parent: tk.Widget,
        row: int,
        label: str,
        low: float,
        high: float,
        initial: float,
        on_change: Callable[[], None],
        as_int: bool = False,
        value_format: str = "{:.2f}",
    ) -> None:
        self.as_int = as_int
        self.value_format = value_format
        self.var = tk.DoubleVar(value=initial)
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8))
        self.scale = ttk.Scale(
            parent,
            from_=low,
            to=high,
            orient="horizontal",
            variable=self.var,
            command=lambda _v: self._on_move(on_change),
        )
        self.scale.grid(row=row, column=1, sticky="ew", padx=(0, 8))
        self.readout = ttk.Label(parent, width=8, anchor="e")
        self.readout.grid(row=row, column=2, sticky="e")
        self._update_readout()

    def _on_move(self, on_change: Callable[[], None]) -> None:
        self._update_readout()
        on_change()

    def _update_readout(self) -> None:
        text = (
            str(int(round(self.var.get())))
            if self.as_int
            else self.value_format.format(self.var.get())
        )
        self.readout.configure(text=text)

    def get(self) -> float:
        return int(round(self.var.get())) if self.as_int else self.var.get()


class RealtimeGuiApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Algebraic Surface -> Sonic Pi")
        self.cache = SurfaceModeCache()
        self.client: SonicPiOSCClient | None = None
        self.streamer: SonicPiModeStreamer | None = None
        self._generation = 0
        self._debounce_id: str | None = None
        # Worker threads never touch Tk objects directly (Tkinter's Tcl
        # interpreter is not thread-safe to call into from a non-main
        # thread); they post results here and the main thread drains it.
        self._results: "queue.Queue[tuple[int, str]]" = queue.Queue()
        self._quantum_updates: "queue.Queue[SlowUpdate]" = queue.Queue()

        # The most recently computed packet, kept for the quantum
        # conductor's fast path to shimmer without recomputing it.
        self._last_packet = None
        self._quantum_conductor: QuantumPhaseConductor | None = None

        self._build_ui()
        self._reconnect()
        self._schedule_recompute()
        self.root.after(50, self._poll_results)

    # -- UI construction ---------------------------------------------------
    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}
        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=0, sticky="nsew", **pad)
        frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        row = 0
        ttk.Label(frame, text="Surface").grid(row=row, column=0, sticky="w")
        self.surface_var = tk.StringVar(value=SURFACE_NAMES[0])
        surface_menu = ttk.Combobox(
            frame,
            textvariable=self.surface_var,
            values=SURFACE_NAMES,
            state="readonly",
        )
        surface_menu.grid(row=row, column=1, columnspan=2, sticky="ew")
        surface_menu.bind("<<ComboboxSelected>>", lambda _e: self._on_change())
        row += 1

        ttk.Label(frame, text="Material model").grid(row=row, column=0, sticky="w")
        self.model_var = tk.StringVar(value=MATERIAL_MODEL_NAMES[0])
        model_menu = ttk.Combobox(
            frame,
            textvariable=self.model_var,
            values=MATERIAL_MODEL_NAMES,
            state="readonly",
        )
        model_menu.grid(row=row, column=1, columnspan=2, sticky="ew")
        model_menu.bind("<<ComboboxSelected>>", lambda _e: self._on_change())
        row += 1

        self.parameter_row = _SliderRow(
            frame, row, "Equation parameter (a)", 6.0, 16.0, 11.8, self._on_change
        )
        row += 1
        self.resolution_row = _SliderRow(
            frame, row, "Mesh resolution", 12, 40, 20, self._on_change, as_int=True
        )
        row += 1
        self.bound_row = _SliderRow(
            frame, row, "Sampling bound", 2.0, 4.0, 3.0, self._on_change
        )
        row += 1
        self.radius_row = _SliderRow(
            frame, row, "Radius (m)", 0.1, 0.6, 0.25, self._on_change
        )
        row += 1
        self.max_modes_row = _SliderRow(
            frame, row, "Modes solved", 8, 64, 24, self._on_change, as_int=True
        )
        row += 1
        self.active_modes_row = _SliderRow(
            frame, row, "Active modes", 1, 48, 16, self._on_change, as_int=True
        )
        row += 1
        self.wave_speed_row = _SliderRow(
            frame, row, "Wave speed", 20.0, 400.0, 120.0, self._on_change
        )
        row += 1
        self.t60_row = _SliderRow(
            frame, row, "T60 (s)", 0.3, 10.0, 4.0, self._on_change
        )
        row += 1
        self.damping_tilt_row = _SliderRow(
            frame, row, "Damping freq. tilt", 0.0, 1.0, 0.35, self._on_change
        )
        row += 1

        ttk.Separator(frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=8
        )
        row += 1

        ttk.Label(frame, text="Sonic Pi host").grid(row=row, column=0, sticky="w")
        self.host_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(frame, textvariable=self.host_var).grid(
            row=row, column=1, sticky="ew"
        )
        ttk.Label(frame, text="port").grid(row=row, column=2, sticky="w")
        row += 1

        self.port_var = tk.StringVar(value="4560")
        ttk.Entry(frame, textvariable=self.port_var, width=8).grid(
            row=row, column=1, sticky="w"
        )
        ttk.Button(frame, text="Reconnect", command=self._reconnect).grid(
            row=row, column=2, sticky="e"
        )
        row += 1

        button_row = ttk.Frame(frame)
        button_row.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        ttk.Button(button_row, text="Recompute now", command=self._schedule_recompute).pack(
            side="left"
        )
        ttk.Button(button_row, text="Silence", command=self._silence).pack(
            side="left", padx=8
        )
        row += 1

        ttk.Separator(frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=8
        )
        row += 1

        ttk.Label(frame, text="Quantum drive", font=("", 9, "bold")).grid(
            row=row, column=0, columnspan=3, sticky="w"
        )
        row += 1

        self.mod_depth_row: _SliderRow | None = None
        self.pan_mod_row: _SliderRow | None = None
        self.quantum_toggle_button: ttk.Button | None = None
        self.quantum_status_var = tk.StringVar(value="quantum drive stopped")

        if QUANTUM_DRIVE_IMPORT_ERROR is not None:
            ttk.Label(
                frame,
                text=f"unavailable ({QUANTUM_DRIVE_IMPORT_ERROR})",
                foreground="#a00",
            ).grid(row=row, column=0, columnspan=3, sticky="w")
            row += 1
        else:
            self.mod_depth_row = _SliderRow(
                frame, row, "Modulation depth", 0.0, 1.0, 0.5, self._on_quantum_config_change
            )
            row += 1
            self.pan_mod_row = _SliderRow(
                frame, row, "Pan modulation", 0.0, 1.0, 0.6, self._on_quantum_config_change
            )
            row += 1

            quantum_button_row = ttk.Frame(frame)
            quantum_button_row.grid(
                row=row, column=0, columnspan=3, sticky="ew", pady=(4, 0)
            )
            self.quantum_toggle_button = ttk.Button(
                quantum_button_row,
                text="Start quantum drive",
                command=self._toggle_quantum,
            )
            self.quantum_toggle_button.pack(side="left")
            row += 1

            ttk.Label(
                frame, textvariable=self.quantum_status_var, foreground="#555"
            ).grid(row=row, column=0, columnspan=3, sticky="w", pady=(4, 0))
            row += 1

        self.status_var = tk.StringVar(value="starting…")
        ttk.Label(frame, textvariable=self.status_var, foreground="#555").grid(
            row=row, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )

    # -- Sonic Pi connection -------------------------------------------------
    def _reconnect(self) -> None:
        if self.client is not None:
            self.client.close()
        host = self.host_var.get().strip() or "127.0.0.1"
        try:
            port = int(self.port_var.get())
        except ValueError:
            port = 4560
            self.port_var.set(str(port))
        self.client = SonicPiOSCClient(host, port)
        self.streamer = SonicPiModeStreamer(self.client)
        if self._quantum_conductor is not None:
            self._quantum_conductor.streamer = self.streamer
        self.status_var.set(f"target set to {host}:{port}")

    def _silence(self) -> None:
        if self.streamer is not None:
            self.streamer.send_silence()
            self.status_var.set("silence sent")

    # -- Config / recompute ---------------------------------------------------
    def _read_config(self) -> RealtimeSurfaceConfig:
        return RealtimeSurfaceConfig(
            surface=self.surface_var.get(),
            parameter=self.parameter_row.get(),
            resolution=int(self.resolution_row.get()),
            bound=self.bound_row.get(),
            radius_m=self.radius_row.get(),
            max_modes=int(self.max_modes_row.get()),
            active_modes=min(
                int(self.active_modes_row.get()), int(self.max_modes_row.get())
            ),
            material_model=self.model_var.get(),
            effective_wave_speed=self.wave_speed_row.get(),
            t60_seconds=self.t60_row.get(),
            damping_frequency_tilt=self.damping_tilt_row.get(),
        )

    def _on_change(self) -> None:
        self._schedule_recompute()

    def _schedule_recompute(self) -> None:
        if self._debounce_id is not None:
            self.root.after_cancel(self._debounce_id)
        self._debounce_id = self.root.after(DEBOUNCE_MS, self._dispatch_recompute)

    def _dispatch_recompute(self) -> None:
        self._debounce_id = None
        self._generation += 1
        generation = self._generation
        config = self._read_config()
        streamer = self.streamer
        self.status_var.set("computing…")
        threading.Thread(
            target=self._recompute_worker,
            args=(config, streamer, generation),
            daemon=True,
        ).start()

    def _recompute_worker(
        self,
        config: RealtimeSurfaceConfig,
        streamer: SonicPiModeStreamer | None,
        generation: int,
    ) -> None:
        try:
            packet, solve = compute_modal_packet(config, self.cache)
            self._last_packet = packet
            count = len(packet.frequencies_hz)
            # While quantum drive is running, it owns sending mode data (at
            # its own faster, phase-shimmered cadence); this path only needs
            # to keep _last_packet current for it to read.
            if streamer is not None and self._quantum_conductor is None:
                count = streamer.send_packet(packet)
            message = (
                f"{config.surface} · {len(solve.vertices)}v/{len(solve.faces)}f "
                f"mesh ({solve.elapsed_seconds * 1000:.0f} ms) · "
                f"{count} modes · model={config.material_model}"
            )
        except Exception as exc:  # noqa: BLE001 - surfaced to the status bar
            message = f"error: {exc}"
        self._results.put((generation, message))

    def _poll_results(self) -> None:
        try:
            while True:
                generation, message = self._results.get_nowait()
                if generation == self._generation:
                    self.status_var.set(message)
        except queue.Empty:
            pass

        try:
            while True:
                self._apply_quantum_update(self._quantum_updates.get_nowait())
        except queue.Empty:
            pass

        self.root.after(50, self._poll_results)

    # -- Quantum drive ---------------------------------------------------
    def _on_quantum_config_change(self) -> None:
        if self._quantum_conductor is not None:
            self._quantum_conductor.config = self._read_quantum_config()

    def _read_quantum_config(self) -> QuantumConductorConfig:
        return QuantumConductorConfig(
            modulation_depth=self.mod_depth_row.get(),
            pan_modulation=self.pan_mod_row.get(),
        )

    def _toggle_quantum(self) -> None:
        if self._quantum_conductor is not None:
            self._quantum_conductor.stop()
            self._quantum_conductor = None
            self.quantum_toggle_button.configure(text="Start quantum drive")
            self.quantum_status_var.set("quantum drive stopped")
            return

        conductor = QuantumPhaseConductor(
            streamer=self.streamer,
            get_packet=lambda: self._last_packet,
            on_slow_update=self._quantum_updates.put,
            config=self._read_quantum_config(),
        )
        conductor.start()
        self._quantum_conductor = conductor
        self.quantum_toggle_button.configure(text="Stop quantum drive")
        self.quantum_status_var.set("quantum drive running…")

    def _apply_quantum_update(self, update: SlowUpdate) -> None:
        if self._quantum_conductor is None:
            return  # stopped since this update was queued; drop it
        self.wave_speed_row.var.set(update["wave_speed"])
        self.wave_speed_row._update_readout()
        self.t60_row.var.set(update["t60_seconds"])
        self.t60_row._update_readout()
        self.damping_tilt_row.var.set(update["damping_frequency_tilt"])
        self.damping_tilt_row._update_readout()
        self._on_change()
        self.quantum_status_var.set(
            f"coherence={update['coherence']:.2f} "
            f"bloch_spread={update['bloch_spread']:.2f} "
            f"mean|z|={update['mean_abs_z']:.2f}"
        )


def main() -> int:
    root = tk.Tk()
    RealtimeGuiApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
