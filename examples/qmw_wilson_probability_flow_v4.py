#!/usr/bin/env python3
"""Wilson Hexany probability-flow instrument for Max."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import signal
import sys
import threading

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from examples.qmw_recursive_wilson_instrument_v3 import RecursiveWilsonMaxHost
from qmw.recursive_wilson import HEXANY_MASKS, HexanyFlow, HexanyVoice, hexany_voices
from pythonosc.udp_client import SimpleUDPClient


class ProbabilityFlowWilsonMaxHost(RecursiveWilsonMaxHost):
    """Render directed probability current instead of six-note state chords."""

    def __init__(
        self,
        *args,
        max_flows_per_step: int = 1,
        visual_host: str = "127.0.0.1",
        visual_port: int = 7411,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.max_flows_per_step = max(1, int(max_flows_per_step))
        self.visual_client = SimpleUDPClient(visual_host, int(visual_port))
        self._flow_timers: list[threading.Timer] = []

    @staticmethod
    def _midi_for_voice(voice: HexanyVoice) -> tuple[int, int]:
        fractional_pitch = 60.0 + 12.0 * math.log2(voice.ratio)
        note_pitch = int(round(fractional_pitch))
        deviation = fractional_pitch - note_pitch
        bend = int(round(8192 + (deviation / 2.0) * 8191))
        return note_pitch, max(0, min(16383, bend))

    def _publish_state(self, *, publish_circuit: bool) -> None:
        """Publish circuit/status only; v4 does not replay the state as a chord."""
        shell_probability, voices = hexany_voices(self.engine.state)
        generation = self.engine.generation
        if publish_circuit:
            revision = self.publisher.publish(self.engine.synthesis_result())
        else:
            revision = -1
        probabilities = [voice.conditional_probability for voice in voices]
        entropy = -sum(p * math.log2(p) for p in probabilities if p > 1e-15)
        self._send(
            "/qmw/recursive/status",
            [
                generation,
                shell_probability,
                entropy,
                self.engine.temperature,
                self.engine.max_depth,
                self.engine.seed,
                revision,
                len(self.engine.logical_circuit.data),
            ],
        )
        self.visual_client.send_message(
            "/qmw/wilson/frame",
            [
                generation,
                shell_probability,
                entropy,
                self.engine.temperature,
                self.engine.max_depth,
                self.engine.seed,
            ],
        )
        for voice in voices:
            self.visual_client.send_message(
                "/qmw/wilson/vertex",
                [
                    generation,
                    voice.basis_index,
                    voice.ratio_numerator,
                    voice.ratio_denominator,
                    voice.conditional_probability,
                    voice.relative_phase,
                ],
            )
        amplitudes = self.engine.state.data
        for basis_index in range(16):
            amplitude = amplitudes[basis_index]
            self.visual_client.send_message(
                "/qmw/wilson/basis",
                [
                    generation,
                    basis_index,
                    basis_index.bit_count(),
                    float(abs(amplitude) ** 2),
                    float(math.atan2(amplitude.imag, amplitude.real)),
                ],
            )

    def _flow_note_payload(
        self,
        *,
        generation: int,
        role: int,
        voice: HexanyVoice,
        partner_basis: int,
        velocity: int,
        duration_ms: int,
        flow: HexanyFlow,
        theta: float,
        beta: float,
        phase: float,
    ) -> list[object]:
        note, bend = self._midi_for_voice(voice)
        voice_index = HEXANY_MASKS.index(voice.basis_index)
        cc74 = int(round((phase + math.pi) * 127 / (2 * math.pi)))
        return [
            generation,
            role,
            voice.basis_index,
            note,
            velocity,
            duration_ms,
            flow.conditional_probability_flow,
            theta,
            beta,
            phase,
            bend,
            max(0, min(127, cc74)),
            2 + voice_index,
            partner_basis,
        ]

    def _publish_flow(self, step) -> None:
        if not step.flows:
            return
        voice_by_basis = {voice.basis_index: voice for voice in step.voices}
        for flow in step.flows[: self.max_flows_per_step]:
            departure = voice_by_basis[flow.source_basis_index]
            arrival = voice_by_basis[flow.destination_basis_index]
            strength = math.sqrt(min(1.0, flow.conditional_probability_flow))
            arrival_velocity = max(12, min(127, int(round(24 + 150 * strength))))
            departure_velocity = max(8, int(round(arrival_velocity * 0.58)))
            travel_ms = int(round(24 + 180 * min(1.0, abs(step.theta) / math.pi)))
            duration_ms = max(70, min(self.interval_ms, travel_ms + 80))
            phase = float(
                math.atan2(
                    math.sin(flow.relative_phase + step.beta),
                    math.cos(flow.relative_phase + step.beta),
                )
            )
            self.visual_client.send_message(
                "/qmw/wilson/flow",
                [
                    step.generation,
                    flow.source_basis_index,
                    flow.destination_basis_index,
                    flow.conditional_probability_flow,
                    step.theta,
                    step.beta,
                    phase,
                ],
            )
            departure_payload = self._flow_note_payload(
                generation=step.generation,
                role=0,
                voice=departure,
                partner_basis=arrival.basis_index,
                velocity=departure_velocity,
                duration_ms=duration_ms,
                flow=flow,
                theta=step.theta,
                beta=step.beta,
                phase=phase,
            )
            arrival_payload = self._flow_note_payload(
                generation=step.generation,
                role=1,
                voice=arrival,
                partner_basis=departure.basis_index,
                velocity=arrival_velocity,
                duration_ms=duration_ms,
                flow=flow,
                theta=step.theta,
                beta=step.beta,
                phase=phase,
            )
            self._send("/qmw/recursive/wilson_flow_note", departure_payload)
            timer = threading.Timer(
                travel_ms / 1000.0,
                self._send,
                args=("/qmw/recursive/wilson_flow_note", arrival_payload),
            )
            timer.daemon = True
            timer.start()
            self._flow_timers.append(timer)
        self._flow_timers = [timer for timer in self._flow_timers if timer.is_alive()]

    def advance(self) -> None:
        with self._lock:
            step = self.engine.next()
            self._publish_state(
                publish_circuit=(
                    step.generation <= self.full_circuit_generation_limit
                )
            )
            self._publish_flow(step)
        strongest = (
            step.flows[0].conditional_probability_flow if step.flows else 0.0
        )
        print(
            f"flow generation={step.generation} {step.qubits} "
            f"theta={step.theta:.4f} beta={step.beta:.4f} "
            f"current={strongest:.6f} shell={step.shell_probability:.6f}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-port", type=int, default=7403)
    parser.add_argument("--max-port", type=int, default=7410)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--temperature", type=float, default=0.65)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--interval-ms", type=int, default=240)
    parser.add_argument("--max-flows-per-step", type=int, default=1)
    parser.add_argument("--visual-port", type=int, default=7411)
    args = parser.parse_args()
    host = ProbabilityFlowWilsonMaxHost(
        control_port=args.control_port,
        max_port=args.max_port,
        seed=args.seed,
        temperature=args.temperature,
        max_depth=args.max_depth,
        interval_ms=args.interval_ms,
        max_flows_per_step=args.max_flows_per_step,
        visual_port=args.visual_port,
    )
    stop_event = threading.Event()

    def request_stop(_signum=None, _frame=None):
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    host.start()
    print("QMW Wilson probability-flow instrument v4 ready")
    stop_event.wait()
    host.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
