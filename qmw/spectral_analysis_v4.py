"""Visible V4 observer window for QMW's canonical spectral analysis layer.

The window has no controls that mutate quantum state.  It renders a
``QuantumSpectrumFrame`` already attached by the QMW data bus, making the
boundary between quantum analysis and any future sound adapter explicit.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qmw.core.quantum_spectrum import QuantumSpectrumFrame, analyze_quantum_spectrum

if TYPE_CHECKING:  # pragma: no cover
    from qmw.core.quantum_data_bus import QuantumDataBus
    from qmw.core.state_frame import QuantumStateFrame


WINDOW_TITLE = "QMW Spectral Analysis V4 — observer"


def format_spectral_report(spectrum: QuantumSpectrumFrame, limit: int = 16) -> str:
    """Return the same compact, auditable report displayed by the V4 window."""

    count = min(spectrum.dimension, limit)
    lines = [
        "QMW Spectral Analysis V4  |  observer only",
        "rho_E = V_H† rho V_H; p_i = Re[rho_E(ii)]",
        (
            f"purity={spectrum.purity:.8f}  entropy={spectrum.entropy:.8f} nats  "
            f"participation={spectrum.participation_rank:.6f}"
        ),
        f"||[H,rho]||_F={spectrum.commutator_norm:.3e}",
        "rho spectrum lambda (independent ordering): "
        + ", ".join(f"{value:.6f}" for value in spectrum.density_eigenvalues),
        "",
        "energy mode       E_i        p_i      sqrt(p_i)",
    ]
    for mode in range(count):
        lines.append(
            f"{mode + 1:>11}  {spectrum.energy_eigenvalues[mode]:>10.5f}"
            f"  {spectrum.energy_populations[mode]:>9.6f}"
            f"  {spectrum.modal_amplitudes[mode]:>10.6f}"
        )
    if spectrum.dimension > count:
        lines.append(f"… {spectrum.dimension - count} additional modes")
    return "\n".join(lines)


class SpectralAnalysisWindowV4:
    """A small Tk window that observes, but never mutates, QMW state frames."""

    def __init__(self, parent: Any | None = None) -> None:
        import tkinter as tk
        from tkinter import ttk

        self._tk = tk
        self._owns_root = parent is None
        self.window = tk.Tk() if parent is None else tk.Toplevel(parent)
        self.window.title(WINDOW_TITLE)
        self.window.geometry("780x600")
        self.window.minsize(620, 420)
        outer = ttk.Frame(self.window, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(
            outer,
            text="V4 spectral observer — read-only; rho and H remain authoritative upstream",
        ).pack(anchor="w")
        self._diagnostics = ttk.Label(outer, justify="left")
        self._diagnostics.pack(anchor="w", pady=(8, 6))
        columns = ("mode", "energy", "population", "amplitude")
        self._table = ttk.Treeview(outer, columns=columns, show="headings", height=16)
        labels = ("energy mode", "E_i", "p_i", "sqrt(p_i)")
        for column, label in zip(columns, labels, strict=True):
            self._table.heading(column, text=label)
            self._table.column(column, width=130, anchor="e")
        self._table.column("mode", width=70, anchor="center")
        self._table.pack(fill="both", expand=True)
        self._coherence = tk.Text(outer, height=7, wrap="none", state="disabled")
        self._coherence.pack(fill="x", pady=(8, 0))
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def update_spectrum(self, spectrum: QuantumSpectrumFrame) -> None:
        """Render one already-computed spectrum; no quantum calculation happens here."""

        self._diagnostics.configure(
            text=(
                f"purity {spectrum.purity:.8f}   entropy {spectrum.entropy:.8f} nats   "
                f"participation {spectrum.participation_rank:.5f}   "
                f"||[H,rho]||_F {spectrum.commutator_norm:.3e}"
            )
        )
        for item in self._table.get_children():
            self._table.delete(item)
        for mode in range(spectrum.dimension):
            self._table.insert(
                "",
                "end",
                values=(
                    mode + 1,
                    f"{spectrum.energy_eigenvalues[mode]:.7g}",
                    f"{spectrum.energy_populations[mode]:.7g}",
                    f"{spectrum.modal_amplitudes[mode]:.7g}",
                ),
            )
        coherence = _coherence_preview(spectrum)
        self._coherence.configure(state="normal")
        self._coherence.delete("1.0", "end")
        self._coherence.insert("1.0", coherence)
        self._coherence.configure(state="disabled")

    def update_frame(self, frame: "QuantumStateFrame") -> None:
        if isinstance(frame.spectrum, QuantumSpectrumFrame):
            self.update_spectrum(frame.spectrum)
            source = frame.source_name or "unnamed source"
            self.window.title(
                f"{WINDOW_TITLE} — t={frame.t:.6f}, dt={frame.dt:.6g}, {source}"
            )

    def observe_bus(self, bus: "QuantumDataBus") -> None:
        """Subscribe to a bus; GUI updates use the GUI event queue safely."""

        def on_frame(frame: "QuantumStateFrame") -> None:
            if isinstance(frame.spectrum, QuantumSpectrumFrame):
                self.window.after(0, self.update_frame, frame)

        bus.state_bus.subscribe(on_frame)

    def show(self) -> None:
        self.window.deiconify()
        self.window.lift()

    def run(self) -> None:
        self.window.mainloop()

    def close(self) -> None:
        self.window.destroy()


def launch_spectral_analysis_window(
    bus: "QuantumDataBus | None" = None,
) -> SpectralAnalysisWindowV4:
    """Create a separate V4 window and optionally subscribe it to a QMW bus."""

    viewer = SpectralAnalysisWindowV4()
    if bus is not None:
        viewer.observe_bus(bus)
    viewer.show()
    return viewer


def _coherence_preview(spectrum: QuantumSpectrumFrame, limit: int = 6) -> str:
    count = min(spectrum.dimension, limit)
    matrix = spectrum.rho_in_energy_basis[:count, :count]
    rows = ["rho_E coherence preview (energy basis; complex entries):"]
    rows.extend(
        "  " + "  ".join(f"{entry.real:+.3f}{entry.imag:+.3f}i" for entry in row)
        for row in matrix
    )
    return "\n".join(rows)


def main() -> None:
    """Launch a visible 16-mode analytical fixture without starting audio."""

    rho = np.zeros((16, 16), dtype=np.complex128)
    rho[0, 0] = 1.0
    spectrum = analyze_quantum_spectrum(rho, np.diag(np.arange(16, dtype=float)))
    viewer = launch_spectral_analysis_window()
    viewer.update_spectrum(spectrum)
    viewer.run()


if __name__ == "__main__":  # pragma: no cover - manual GUI entry point
    main()
