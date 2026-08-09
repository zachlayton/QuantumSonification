"""OSC publication for spinor and joint-state engines without scalar flattening."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable, Protocol

import numpy as np

from excitation.quantum_frames_v1 import (
    DiracSpinorFieldFrame,
    EntangledQubitFrame,
    JointWavefunctionFrame,
    RelativisticLevelFrame,
    SpinorFrame,
)
from excitation.wavefunction_sources_v1 import WavefunctionFrame


class OSCClient(Protocol):
    def send_message(self, address: str, value: Any) -> None: ...


@dataclass(frozen=True)
class NativeInstrumentOSCConfig:
    pair_samples_per_frame: int = 24
    dirac_samples_per_frame: int = 32

    def __post_init__(self) -> None:
        if not 1 <= self.pair_samples_per_frame <= 128:
            raise ValueError("pair_samples_per_frame must lie in [1, 128]")
        if not 1 <= self.dirac_samples_per_frame <= 128:
            raise ValueError("dirac_samples_per_frame must lie in [1, 128]")


class NativeQuantumInstrumentOSCAdapter:
    PREFIX = "/qmw/instrument"

    def __init__(
        self,
        clients: Iterable[OSCClient] = (),
        config: NativeInstrumentOSCConfig = NativeInstrumentOSCConfig(),
    ) -> None:
        self.clients = tuple(client for client in clients if client is not None)
        self.config = config
        self.frame_id = 0

    def _send(self, suffix: str, value: Any) -> None:
        for client in self.clients:
            client.send_message(f"{self.PREFIX}/{suffix}", value)

    def publish(
        self,
        frame: SpinorFrame
        | JointWavefunctionFrame
        | EntangledQubitFrame
        | WavefunctionFrame
        | RelativisticLevelFrame
        | DiracSpinorFieldFrame,
    ) -> None:
        if isinstance(frame, SpinorFrame):
            self._publish_spin(frame)
        elif isinstance(frame, JointWavefunctionFrame):
            self._publish_exchange(frame)
        elif isinstance(frame, EntangledQubitFrame):
            self._publish_epr(frame)
        elif isinstance(frame, WavefunctionFrame):
            self._publish_field(frame)
        elif isinstance(frame, RelativisticLevelFrame):
            self._publish_relativistic_levels(frame)
        elif isinstance(frame, DiracSpinorFieldFrame):
            self._publish_dirac_field(frame)
        else:
            raise TypeError(f"unsupported native quantum frame {type(frame).__name__}")
        self.frame_id += 1

    @staticmethod
    def _pad3(values: Any) -> tuple[float, float, float]:
        result = [float(value) for value in values][:3]
        result.extend([0.0] * (3 - len(result)))
        return tuple(result)  # type: ignore[return-value]

    def _publish_field(self, frame: WavefunctionFrame) -> None:
        metadata = frame.metadata
        if frame.source == "landau_levels":
            observables = (
                metadata.get("magnetic_field", 0.0),
                metadata.get("cyclotron_angular_frequency", 0.0),
                metadata.get("magnetic_length", 0.0),
            )
        elif frame.source == "hydrogen_zeeman":
            observables = (
                metadata.get("field_strength", 0.0),
                metadata.get("splitting", 0.0),
                metadata.get("angular_momentum_z", 0.0),
            )
        elif frame.source == "hydrogen_stark":
            observables = (
                metadata.get("field_strength", 0.0),
                metadata.get("splitting", 0.0),
                metadata.get("dipole_z", 0.0),
            )
        elif frame.source == "helium_variational_two_electron":
            observables = (
                metadata.get("effective_charge", 0.0),
                metadata.get("electron_repulsion", 0.0),
                metadata.get("variational_energy", 0.0),
            )
        elif frame.source == "delta_function_shell":
            observables = (
                metadata.get("shell_radius", 0.0),
                metadata.get("shell_strength", 0.0),
                metadata.get("bound_state_count", 0.0),
            )
        else:
            observables = (
                metadata.get("expectation_energy", 0.0),
                metadata.get("current_strength", 0.0),
                0.0,
            )
        descriptor = frame.descriptor
        self._send("field/name", frame.source)
        self._send(
            "field/frame",
            [
                self.frame_id,
                frame.time,
                frame.norm,
                frame.dimension,
                descriptor.energy,
                descriptor.phase,
                descriptor.probability,
                descriptor.structure,
                descriptor.coherence,
                descriptor.current,
                *self._pad3(descriptor.position),
                *self._pad3(descriptor.spread),
                *(float(value) for value in observables),
            ],
        )

    def _publish_relativistic_levels(self, frame: RelativisticLevelFrame) -> None:
        self._send(
            "relativistic/frame",
            [
                self.frame_id,
                frame.time,
                frame.norm,
                frame.energy_expectation,
                frame.fine_structure_splitting,
                frame.metadata.get("rest_energy", 0.0),
                frame.metadata.get("time_scale", 1.0),
                len(frame.amplitudes),
            ],
        )
        for index, ((principal, kappa, m_j), total, binding, probability, amplitude) in enumerate(
            zip(
                frame.quantum_numbers,
                frame.total_energies,
                frame.binding_energies,
                frame.probabilities,
                frame.amplitudes,
            )
        ):
            self._send(
                "relativistic/level",
                [
                    self.frame_id,
                    index,
                    principal,
                    kappa,
                    m_j,
                    float(total),
                    float(binding),
                    float(probability),
                    float(np.angle(amplitude) / math.pi),
                ],
            )
        self._send("relativistic/state_real", np.asarray(frame.amplitudes.real).tolist())
        self._send("relativistic/state_imag", np.asarray(frame.amplitudes.imag).tolist())

    def _publish_dirac_field(self, frame: DiracSpinorFieldFrame) -> None:
        klein_code = 1 if frame.metadata.get("klein_zone", False) else 0
        self._send(
            "dirac/frame",
            [
                self.frame_id,
                frame.time,
                frame.norm,
                frame.energy_expectation,
                frame.left_probability,
                frame.right_probability,
                frame.metadata.get("step_height", 0.0),
                frame.metadata.get("incoming_positive_energy", 0.0),
                klein_code,
            ],
        )
        count = self.config.dirac_samples_per_frame
        sample_indices = np.linspace(0, frame.coordinates.size - 1, count, dtype=int)
        peak_probability = max(float(np.max(frame.probability)), 1e-15)
        peak_current = max(float(np.max(np.abs(frame.probability_current))), 1e-15)
        for sample_id, index in enumerate(sample_indices):
            self._send(
                "dirac/sample",
                [
                    self.frame_id,
                    sample_id,
                    float(frame.coordinates[index]),
                    float(frame.probability[index] / peak_probability),
                    float(frame.probability_current[index] / peak_current),
                    float(frame.spinor[0, index].real),
                    float(frame.spinor[0, index].imag),
                    float(frame.spinor[1, index].real),
                    float(frame.spinor[1, index].imag),
                    float(frame.potential[index]),
                ],
            )
        self._send("dirac/end", [self.frame_id, count])

    def _publish_spin(self, frame: SpinorFrame) -> None:
        self._send(
            "spin/frame",
            [
                self.frame_id,
                frame.time,
                frame.norm,
                frame.larmor_angular_frequency,
                frame.energy_expectation,
                frame.relative_phase,
                *frame.magnetic_field,
                *frame.larmor_vector,
                *frame.bloch_vector,
                *frame.probabilities_z,
            ],
        )
        self._send("spin/state_real", np.asarray(frame.spinor.real).tolist())
        self._send("spin/state_imag", np.asarray(frame.spinor.imag).tolist())

    def _publish_epr(self, frame: EntangledQubitFrame) -> None:
        self._send(
            "epr/frame",
            [
                self.frame_id,
                frame.time,
                frame.norm,
                frame.concurrence,
                frame.chsh_maximum,
                *frame.bloch_a,
                *frame.bloch_b,
                *frame.conditional_a_given_b_x_plus,
                *frame.conditional_b_given_a_x_plus,
            ],
        )
        self._send("epr/correlation_tensor", frame.correlation_tensor.reshape(-1).tolist())
        self._send("epr/state_real", np.asarray(frame.state.real).tolist())
        self._send("epr/state_imag", np.asarray(frame.state.imag).tolist())

    def _publish_exchange(self, frame: JointWavefunctionFrame) -> None:
        symmetry_code = 1 if frame.exchange_symmetry == "boson" else -1
        self._send(
            "exchange/frame",
            [
                self.frame_id,
                frame.time,
                frame.norm,
                symmetry_code,
                frame.swap_expectation,
                frame.coincidence_probability,
                frame.one_body_purity,
                self.config.pair_samples_per_frame,
            ],
        )
        self._send("exchange/marginal_a", frame.marginal_a.tolist())
        self._send("exchange/marginal_b", frame.marginal_b.tolist())

        probability = np.maximum(np.asarray(frame.probability, dtype=np.float64), 0.0)
        weights = probability.reshape(-1)
        weights /= max(float(np.sum(weights)), 1e-15)
        cdf = np.cumsum(weights)
        count = self.config.pair_samples_per_frame
        offset = ((self.frame_id * 0.6180339887498949) % 1.0) / count
        quantiles = ((np.arange(count) + 0.5) / count + offset) % 1.0
        indices = np.minimum(np.searchsorted(cdf, quantiles), weights.size - 1)
        peak = max(float(np.max(probability)), 1e-15)
        x_axis, y_axis = frame.coordinates
        for pair_id, flat_index in enumerate(indices):
            i, j = np.unravel_index(int(flat_index), probability.shape)
            amplitude = math.sqrt(float(probability[i, j]) / peak)
            phase = float(np.angle(frame.psi[i, j]) / math.pi)
            self._send(
                "exchange/pair",
                [
                    self.frame_id,
                    pair_id,
                    float(x_axis[i]),
                    float(y_axis[j]),
                    amplitude,
                    phase,
                    symmetry_code,
                ],
            )
        self._send("exchange/end", [self.frame_id, count])


__all__ = ["NativeInstrumentOSCConfig", "NativeQuantumInstrumentOSCAdapter"]
