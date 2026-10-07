"""Opt-in V4 sound adapter for canonical quantum spectral observations.

This is a musical adapter, not quantum evolution.  It consumes a completed
``QuantumSpectrumFrame`` and emits compact voice targets at a rate selected by
the caller; no QMW audio engine is modified or invoked here.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Callable

import numpy as np

from qmw.core.quantum_spectrum import QuantumSpectrumFrame

if TYPE_CHECKING:  # pragma: no cover
    from qmw.core.state_frame import QuantumStateFrame


@dataclass(frozen=True)
class SpectralFrequencyPolicyV4:
    """Map energy monotonically into a bounded pitch span.

    By default the current frame supplies the normalization bounds for backward
    compatibility.  Supplying both ``energy_min`` and ``energy_max`` creates a
    fixed calibration, so changing Hamiltonian bandwidth cannot make every
    voice glide merely because the frame extrema moved.
    """

    reference_hz: float = 110.0
    octave_span: float = 3.0
    degeneracy_spread_semitones: float = 0.6
    energy_min: float | None = None
    energy_max: float | None = None

    def __post_init__(self) -> None:
        if not np.isfinite(self.reference_hz) or self.reference_hz <= 0.0:
            raise ValueError("reference_hz must be positive and finite")
        if not np.isfinite(self.octave_span) or self.octave_span < 0.0:
            raise ValueError("octave_span must be non-negative and finite")
        if (not np.isfinite(self.degeneracy_spread_semitones)
                or self.degeneracy_spread_semitones < 0.0):
            raise ValueError("degeneracy_spread_semitones must be non-negative and finite")
        if (self.energy_min is None) != (self.energy_max is None):
            raise ValueError("energy_min and energy_max must be supplied together")
        if self.energy_min is not None:
            if not np.isfinite(self.energy_min) or not np.isfinite(self.energy_max):
                raise ValueError("energy calibration bounds must be finite")
            if self.energy_max <= self.energy_min:
                raise ValueError("energy_max must be greater than energy_min")

    def frequencies(self, energies: np.ndarray) -> np.ndarray:
        values = np.asarray(energies, dtype=float)
        if values.ndim != 1 or not values.size or not np.all(np.isfinite(values)):
            raise ValueError("energies must be a finite non-empty vector")
        lower = float(values[0] if self.energy_min is None else self.energy_min)
        upper = float(values[-1] if self.energy_max is None else self.energy_max)
        extent = upper - lower
        if extent <= 1e-12:
            frequencies = np.full(values.size, self.reference_hz, dtype=float)
        else:
            normalized = np.clip((values - lower) / extent, 0.0, 1.0)
            frequencies = self.reference_hz * np.exp2(self.octave_span * normalized)
        # Degenerate energy modes are physically equal in energy, but are
        # distinct basis labels.  Give their rendered voices a symmetric,
        # deterministic microtonal separation so they do not collapse into a
        # single oscillator.  The group's geometric-mean frequency remains
        # the energy-derived frequency; this is a display/audition convention,
        # not a claim of an energy splitting.
        start = 0
        while start < values.size:
            end = start + 1
            while end < values.size and np.isclose(
                values[end], values[start], rtol=0.0, atol=1.0e-9
            ):
                end += 1
            count = end - start
            if count > 1 and self.degeneracy_spread_semitones > 0.0:
                offsets = np.linspace(
                    -self.degeneracy_spread_semitones / 2.0,
                    self.degeneracy_spread_semitones / 2.0,
                    count,
                )
                frequencies[start:end] *= np.exp2(offsets / 12.0)
            start = end
        return frequencies


@dataclass(frozen=True)
class SpectralVoiceTargetV4:
    """One energy mode rendered as a downstream, non-authoritative voice target."""

    mode: int  # 1-based public mode label
    energy: float
    frequency_hz: float
    amplitude: float


@dataclass(frozen=True)
class SpectralSonificationPacketV4:
    """Small packet suitable for one OSC control update, not an audio buffer."""

    time: float
    voices: tuple[SpectralVoiceTargetV4, ...]
    purity: float
    entropy_nats: float
    participation_rank: float
    commutator_norm: float
    state_motion: float = 0.0

    def osc_payload(self) -> list[float]:
        """One atomic OSC payload with global descriptors before voice pairs.

        Layout: time, count, state motion, purity, entropy in nats,
        participation rank, commutator Frobenius norm, then frequency/amplitude
        pairs.  The values remain raw physical/derived descriptors; the
        downstream adapter owns bounded perceptual mappings.
        """

        payload: list[float] = [
            self.time,
            float(len(self.voices)),
            self.state_motion,
            self.purity,
            self.entropy_nats,
            self.participation_rank,
            self.commutator_norm,
        ]
        for voice in self.voices:
            payload.extend((voice.frequency_hz, voice.amplitude))
        return payload


def spectral_sonification_packet_v4(
    spectrum: QuantumSpectrumFrame,
    time: float,
    *,
    policy: SpectralFrequencyPolicyV4 | None = None,
) -> SpectralSonificationPacketV4:
    """Create a 16-mode-ready musical control packet from a validated spectrum.

    Frequencies use only the Hamiltonian energy ordering.  Amplitudes are
    exactly ``sqrt(max(p_i, 0))`` in the Hamiltonian basis; density eigenvalues
    are never paired to energy modes.
    """

    selected_policy = policy or SpectralFrequencyPolicyV4()
    frequencies = selected_policy.frequencies(spectrum.energy_eigenvalues)
    amplitudes = spectrum.modal_amplitudes
    voices = tuple(
        SpectralVoiceTargetV4(
            mode=index + 1,
            energy=float(spectrum.energy_eigenvalues[index]),
            frequency_hz=float(frequencies[index]),
            amplitude=float(amplitudes[index]),
        )
        for index in range(spectrum.dimension)
    )
    return SpectralSonificationPacketV4(
        time=float(time),
        voices=voices,
        purity=spectrum.purity,
        entropy_nats=spectrum.entropy,
        participation_rank=spectrum.participation_rank,
        commutator_norm=spectrum.commutator_norm,
    )


class SpectralV4OSCSender:
    """Publish compact V4 voice targets only when explicitly attached by a caller."""

    address = "/qmw/v4/spectral/frame"

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7404,
        *,
        client: Any | None = None,
    ) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, int(port))
        self.client = client

    def send_packet(self, packet: SpectralSonificationPacketV4) -> None:
        self.client.send_message(self.address, packet.osc_payload())


class SpectralV4StateSubscriber:
    """Rate-divided state-bus observer; it never holds up audio rendering."""

    def __init__(
        self,
        *,
        sender: SpectralV4OSCSender | None = None,
        policy: SpectralFrequencyPolicyV4 | None = None,
        every_n_frames: int = 4,
        on_packet: Callable[[SpectralSonificationPacketV4], None] | None = None,
    ) -> None:
        if every_n_frames <= 0:
            raise ValueError("every_n_frames must be positive")
        self.sender = sender
        self.policy = policy or SpectralFrequencyPolicyV4()
        self.every_n_frames = int(every_n_frames)
        self.on_packet = on_packet
        self.frame_count = 0
        self.latest: SpectralSonificationPacketV4 | None = None
        self._previous_rho: np.ndarray | None = None

    def __call__(self, frame: "QuantumStateFrame") -> None:
        frame_index = self.frame_count
        self.frame_count += 1
        if frame_index % self.every_n_frames or not isinstance(
            frame.spectrum, QuantumSpectrumFrame
        ):
            return
        packet = spectral_sonification_packet_v4(
            frame.spectrum, frame.t, policy=self.policy
        )
        rho = np.asarray(frame.rho, dtype=np.complex128)
        motion = 0.0 if self._previous_rho is None else min(
            float(np.linalg.norm(rho - self._previous_rho, ord="fro")) * 8.0,
            1.0,
        )
        self._previous_rho = np.array(rho, copy=True)
        packet = replace(packet, state_motion=motion)
        self.latest = packet
        if self.sender is not None:
            self.sender.send_packet(packet)
        if self.on_packet is not None:
            self.on_packet(packet)
