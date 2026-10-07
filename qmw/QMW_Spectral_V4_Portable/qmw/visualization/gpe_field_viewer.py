"""Read-only density/phase viewer for complete GPE field frames."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Any

import numpy as np

from qmw.osc.gpe_field_osc import reconstruct_gpe_field
from qmw.qmw_gpe import GPEState


@dataclass(frozen=True)
class GPEFieldVisualFrame:
    """A visualization snapshot; it cannot mutate the source engine."""
    time: float
    density: np.ndarray
    phase: np.ndarray


class GPEFieldViewer:
    """Optional Matplotlib GUI with explicit field-frame ingestion."""
    def __init__(self) -> None:
        self.frame: GPEFieldVisualFrame | None = None
        self._images: tuple[Any, Any] | None = None

    def update(self, state: GPEState) -> GPEFieldVisualFrame:
        self.frame = GPEFieldVisualFrame(float(state.time), np.array(state.density, copy=True), np.array(state.phase, copy=True))
        return self.frame

    def update_from_transport(self, messages: Iterable[tuple[str, list[Any]]]) -> GPEFieldVisualFrame:
        _, time, psi = reconstruct_gpe_field(messages)
        self.frame = GPEFieldVisualFrame(time, np.abs(psi) ** 2, np.angle(psi))
        return self.frame

    def show(self) -> None:
        """Open/update a local GUI; Matplotlib remains an optional dependency."""
        if self.frame is None:
            raise RuntimeError("update with a GPE state before showing the viewer.")
        import matplotlib.pyplot as plt
        density = self.frame.density
        phase = self.frame.phase
        if density.ndim == 1:
            density, phase = density[None, :], phase[None, :]
        if self._images is None:
            figure, axes = plt.subplots(1, 2, num="QMW GPE field viewer")
            density_image = axes[0].imshow(density, origin="lower", aspect="auto", cmap="magma")
            phase_image = axes[1].imshow(phase, origin="lower", aspect="auto", cmap="twilight", vmin=-np.pi, vmax=np.pi)
            axes[0].set_title("density |psi| squared")
            axes[1].set_title("phase arg psi")
            figure.colorbar(density_image, ax=axes[0])
            figure.colorbar(phase_image, ax=axes[1])
            self._images = (density_image, phase_image)
            plt.show(block=False)
        else:
            self._images[0].set_data(density)
            self._images[1].set_data(phase)
            self._images[0].figure.canvas.draw_idle()


__all__ = ["GPEFieldViewer", "GPEFieldVisualFrame"]
