from __future__ import annotations

from typing import Any

import numpy as np

from qmw.core import QuantumStateFrame


class WavepacketView:
    """Publish source wavepacket arrays when the selected source exposes them."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        if not config.send_wavepacket:
            return

        probability = frame.array("wavepacket_probability")
        wavefunction = frame.array("wavefunction")
        if probability is None and wavefunction is None:
            visual_osc.send_message(
                f"{config.source_namespace}/wavepacket/available",
                0,
            )
            return

        visual_osc.send_message(
            f"{config.source_namespace}/wavepacket/available",
            1,
        )

        if probability is not None:
            probability = np.asarray(probability, dtype=float)
            print(
                "WAVEPACKET SEND:",
                frame.source_name or "unknown",
                len(probability),
            )
            visual_osc.send_message(
                f"{config.source_namespace}/wavepacket/probability",
                [float(value) for value in probability],
            )

        if wavefunction is None and probability is not None:
            descriptor = frame.source_descriptor
            phase_offset = float(getattr(descriptor, "phase", 0.0))
            curvature = float(getattr(descriptor, "curvature", 0.0))
            phase = phase_offset + curvature * np.linspace(-np.pi, np.pi, len(probability))
            wavefunction = np.sqrt(np.maximum(probability, 0.0)) * np.exp(1j * phase)

        if wavefunction is not None:
            wavefunction = np.asarray(wavefunction, dtype=np.complex128)
            spectrum_complex = np.fft.fftshift(np.fft.fft(wavefunction))
            spectrum = np.abs(spectrum_complex) ** 2
            spectrum_phase = np.angle(spectrum_complex)
            spectrum_peak = float(np.max(spectrum))
            if spectrum_peak > 1e-15:
                spectrum = spectrum / spectrum_peak

            visual_osc.send_message(
                f"{config.source_namespace}/wavepacket/real",
                [float(value) for value in np.real(wavefunction)],
            )
            visual_osc.send_message(
                f"{config.source_namespace}/wavepacket/imag",
                [float(value) for value in np.imag(wavefunction)],
            )
            visual_osc.send_message(
                f"{config.source_namespace}/wavepacket/spectrum",
                [float(value) for value in spectrum],
            )
            visual_osc.send_message(
                f"{config.source_namespace}/wavepacket/spectrum_phase",
                [float(value) for value in spectrum_phase],
            )
            visual_osc.send_message(
                f"{config.source_namespace}/wavepacket/phase",
                [float(value) for value in np.angle(wavefunction)],
            )
