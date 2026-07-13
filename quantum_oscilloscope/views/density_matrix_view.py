from __future__ import annotations

from typing import Any

import numpy as np

from qmw.core import QuantumStateFrame


class DensityMatrixView:
    """Publish density-matrix rows to the visual OSC surface."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        if not config.send_density_rows:
            return

        rho = np.asarray(frame.rho, dtype=np.complex128)
        for row_index, row in enumerate(rho):
            visual_osc.send_message(
                f"{config.density_namespace}/real/{row_index}",
                [float(value.real) for value in row],
            )
            visual_osc.send_message(
                f"{config.density_namespace}/imag/{row_index}",
                [float(value.imag) for value in row],
            )

