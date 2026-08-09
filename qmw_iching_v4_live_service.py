#!/usr/bin/env python3
"""Persistent V4 evolution, consultation, OSC, and local modal sound service.

The service continuously publishes non-destructive V4 gauge observations.  A
consultation request freezes the current *pre-measurement* magnetic Laplacian,
collapses the same persistent density matrix, publishes the resulting H0/M/H1,
and excites that frozen Laplacian at the measured H0.  This ordering prevents
the consultation sound from being derived from the already-collapsed graph.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import threading
import time

from qmw_iching_dynamic_density_oracle8_v4 import (
    DynamicGaugeFrame,
    DynamicIChingDensityOracleV4,
    consultation_message,
    osc_messages,
)
from qmw_iching_laplacian_modal_renderer_v1 import RenderConfig
from qmw_iching_processing_visualizer_publisher_v1 import (
    OracleAudioPlayer,
    make_clients,
    publish_messages,
    signed_int32,
)


@dataclass(frozen=True)
class ConsultationAudioFrame:
    revision: int
    seed: int
    primary: int
    moving_mask: int
    transformed: int


class V4LiveService:
    """Own one persistent oracle and serialize evolution with consultation."""

    def __init__(
        self,
        oracle: DynamicIChingDensityOracleV4,
        clients,
        *,
        seed: int,
        evolution_dt: float = 0.025,
        substeps: int = 1,
        frames_per_second: float = 1.0,
        audio_player=None,
        inter_message_delay: float = 0.0002,
        reprepare_after_consultation: bool = True,
    ) -> None:
        if evolution_dt <= 0 or substeps < 1 or frames_per_second <= 0:
            raise ValueError("evolution_dt, substeps, and frames_per_second must be positive")
        self.oracle = oracle
        self.clients = list(clients)
        self.seed = int(seed)
        self.evolution_dt = float(evolution_dt)
        self.substeps = int(substeps)
        self.frame_interval = 1.0 / float(frames_per_second)
        self.audio_player = audio_player
        self.inter_message_delay = float(max(0.0, inter_message_delay))
        self.reprepare_after_consultation = bool(reprepare_after_consultation)
        self.current_frame: DynamicGaugeFrame | None = None
        self._state_lock = threading.Lock()
        self._publish_lock = threading.Lock()
        self._cycle_lock = threading.Lock()
        self._consult_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._evolution_thread: threading.Thread | None = None

    def _send(self, address: str, arguments) -> None:
        for client in self.clients:
            client.send_message(address, arguments)

    def publish_frame(self, frame: DynamicGaugeFrame) -> int:
        """Publish one complete, non-interleaved V4 transaction."""
        with self._publish_lock:
            return publish_messages(
                osc_messages(frame), self.clients,
                inter_message_delay=self.inter_message_delay,
            )

    def observe_and_publish(self) -> DynamicGaugeFrame:
        with self._cycle_lock:
            with self._state_lock:
                frame = self.oracle.observe()
                self.current_frame = frame
            self.publish_frame(frame)
        return frame

    def evolve_once(self) -> DynamicGaugeFrame:
        with self._cycle_lock:
            with self._state_lock:
                self.oracle.evolve(self.evolution_dt, steps=self.substeps)
                frame = self.oracle.observe()
                self.current_frame = frame
            self.publish_frame(frame)
        return frame

    def _evolution_loop(self) -> None:
        deadline = time.monotonic()
        while not self._stop_event.is_set():
            try:
                self.evolve_once()
            except Exception as exc:
                print(f"V4 evolution error: {exc}", flush=True)
            deadline += self.frame_interval
            wait = max(0.0, deadline - time.monotonic())
            if self._stop_event.wait(wait):
                break
            if wait == 0.0:
                deadline = time.monotonic()

    def start(self) -> DynamicGaugeFrame:
        frame = self.observe_and_publish()
        self._evolution_thread = threading.Thread(
            target=self._evolution_loop, name="iching-v4-evolution", daemon=True
        )
        self._evolution_thread.start()
        return frame

    def handle_request(self, _address, *_arguments) -> None:
        if not self._consult_lock.acquire(blocking=False):
            return
        request_id = int(_arguments[0]) if _arguments else 0
        try:
            self._send("/qmw/iching/consult/accepted", [request_id])
            with self._cycle_lock:
                with self._state_lock:
                    premeasurement = self.current_frame or self.oracle.observe()
                    self.current_frame = premeasurement
                    premeasurement_density = self.oracle.density_matrix()
                    result = self.oracle.consult()
                    moving_mask = sum(
                        int(value) << line for line, value in enumerate(result.moving_lines)
                    )
                    audio_frame = ConsultationAudioFrame(
                        revision=premeasurement.revision,
                        seed=self.seed,
                        primary=result.h0_index,
                        moving_mask=moving_mask,
                        transformed=result.h1_index,
                    )
                    postmeasurement = self.oracle.observe()
                    self.current_frame = postmeasurement

                # Commit the post-collapse field before its consultation markers.
                # The publish lock keeps the event contiguous, and Processing
                # only reports READY afterward.
                with self._publish_lock:
                    publish_messages(
                        osc_messages(postmeasurement), self.clients,
                        inter_message_delay=self.inter_message_delay,
                    )
                    address, arguments = consultation_message(
                        premeasurement.revision, result
                    )
                    self._send(address, arguments)
                    self._send(
                        "/qmw/iching/consult/published",
                        [request_id, signed_int32(postmeasurement.revision)],
                    )

                # The collapsed frame is presented as the consultation event,
                # then the evolving ensemble is re-prepared for the next cast.
                # This avoids treating rapid independent oracle consultations
                # as repeated measurements of one already-collapsed specimen.
                if self.reprepare_after_consultation:
                    with self._state_lock:
                        self.oracle.set_density_matrix(premeasurement_density)
                        self.current_frame = None

            if self.audio_player is not None:
                self.audio_player.play(audio_frame, premeasurement.gauge.laplacian)
            print(
                f"V4 consulted revision={premeasurement.revision} "
                f"post={postmeasurement.revision} H0={result.h0_index} "
                f"M={moving_mask} H1={result.h1_index}",
                flush=True,
            )
        except Exception as exc:
            self._send("/qmw/iching/consult/error", [request_id])
            print(f"V4 consultation error: {exc}", flush=True)
        finally:
            self._consult_lock.release()

    def stop_audio(self, _address=None, *_arguments) -> None:
        if self.audio_player is not None:
            self.audio_player.stop(_address, *_arguments)

    def close(self) -> None:
        self._stop_event.set()
        if self._evolution_thread is not None:
            self._evolution_thread.join(timeout=2.0)
        if self.audio_player is not None:
            self.audio_player.close()


def serve(service: V4LiveService, host: str, control_port: int) -> None:
    try:
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer
    except ImportError as exc:
        raise SystemExit("V4 live service requires: pip install python-osc") from exc
    dispatcher = Dispatcher()
    dispatcher.map("/qmw/iching/consult/request", service.handle_request)
    dispatcher.map("/qmw/iching/audio/stop", service.stop_audio)
    server = ThreadingOSCUDPServer((host, control_port), dispatcher)
    print(f"V4 live service listening on {host}:{control_port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=7405)
    parser.add_argument("--engine-port", type=int, default=7403)
    parser.add_argument("--visual-port", type=int, default=7404)
    parser.add_argument("--no-engine", action="store_true")
    parser.add_argument("--no-visual", action="store_true")
    parser.add_argument("--backend", choices=("numpy", "mlx"), default="numpy")
    parser.add_argument("--seed", type=int, default=8)
    parser.add_argument(
        "--dephasing", type=float, default=0.0,
        help="optional irreversible dephasing; zero preserves a persistent coherent field",
    )
    parser.add_argument("--damping", type=float, default=0.0)
    parser.add_argument(
        "--warmup-time", type=float, default=0.0,
        help="model time evolved before the first published frame",
    )
    parser.add_argument(
        "--warmup-substeps", type=int, default=20,
        help="unitary/open-system integration steps used during warm-up",
    )
    parser.add_argument("--evolution-dt", type=float, default=0.025)
    parser.add_argument("--substeps", type=int, default=1)
    parser.add_argument("--fps", type=float, default=1.0)
    parser.add_argument("--gauge-low-modes", type=int, default=8)
    parser.add_argument("--inter-message-delay", type=float, default=0.0002)
    parser.add_argument(
        "--reprepare-after-consultation",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="restore the evolving pre-cast ensemble after presenting collapse",
    )
    parser.add_argument("--sound", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--sound-duration", type=float, default=14.0)
    parser.add_argument("--sound-modes", type=int, default=24)
    parser.add_argument("--sound-base-frequency", type=float, default=90.0)
    parser.add_argument("--sound-maximum-frequency", type=float, default=20_000.0)
    parser.add_argument("--sound-volume", type=float, default=1.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.warmup_time < 0 or args.warmup_substeps < 1:
        raise SystemExit("warm-up time must be nonnegative and substeps positive")
    clients = make_clients(
        args.host, args.engine_port, args.visual_port,
        engine_enabled=not args.no_engine, visual_enabled=not args.no_visual,
    )
    audio_player = None
    if args.sound:
        audio_player = OracleAudioPlayer(
            RenderConfig(
                duration_seconds=args.sound_duration,
                mode_count=args.sound_modes,
                base_frequency_hz=args.sound_base_frequency,
                maximum_frequency_hz=args.sound_maximum_frequency,
            ),
            volume=args.sound_volume,
        )
    oracle = DynamicIChingDensityOracleV4(
        backend=args.backend,
        seed=args.seed,
        dephasing_rate=args.dephasing,
        damping_rate=args.damping,
        gauge_low_modes=args.gauge_low_modes,
    )
    if args.warmup_time > 0:
        oracle.evolve(args.warmup_time, steps=args.warmup_substeps)
        print(
            f"warmed V4 field to model time={oracle.time:.4f} "
            f"in {args.warmup_substeps} substeps",
            flush=True,
        )
    service = V4LiveService(
        oracle, clients, seed=args.seed,
        evolution_dt=args.evolution_dt, substeps=args.substeps,
        frames_per_second=args.fps, audio_player=audio_player,
        inter_message_delay=args.inter_message_delay,
        reprepare_after_consultation=args.reprepare_after_consultation,
    )
    initial = service.start()
    print(
        f"published V4 revision={initial.revision} time={initial.time:.4f} "
        f"visual={args.host}:{args.visual_port}",
        flush=True,
    )
    try:
        serve(service, args.host, args.control_port)
    except KeyboardInterrupt:
        print("V4 evolution, consultation, and sound service stopped", flush=True)
    finally:
        service.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
