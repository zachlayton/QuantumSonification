#!/usr/bin/env python3
"""Publish frozen I Ching revisions or serve local consultation requests."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path

from qmw_iching_density_laplacian_bridge_v1 import build_control_frame, osc_messages
from qmw_iching_laplacian_modal_renderer_v1 import (
    RenderConfig,
    render_audio_from_frame,
    write_wav,
)


def signed_int32(value: int) -> int:
    value = int(value) & 0xFFFFFFFF
    return value if value < 0x80000000 else value - 0x100000000


def osc_safe_arguments(arguments):
    result = []
    for value in arguments:
        if isinstance(value, int): result.append(signed_int32(value))
        else: result.append(value)
    return result


def publish_messages(messages, clients, inter_message_delay=0.0):
    count = 0
    for address, arguments in messages:
        safe = osc_safe_arguments(arguments)
        for client in clients: client.send_message(address, safe)
        count += 1
        if inter_message_delay > 0:
            time.sleep(inter_message_delay)
    return count


def make_clients(host, engine_port, visual_port, engine_enabled=True, visual_enabled=True):
    try:
        from pythonosc.udp_client import SimpleUDPClient
    except ImportError as exc:
        raise SystemExit("OSC requested: pip install python-osc") from exc
    clients = []
    if engine_enabled: clients.append(SimpleUDPClient(host, engine_port))
    if visual_enabled: clients.append(SimpleUDPClient(host, visual_port))
    if not clients: raise SystemExit("At least one destination must be enabled")
    return clients


def build_and_publish_consultation(depth, clients, seed=None, revision=None,
                                   inter_message_delay=0.0, on_consultation=None):
    """Cast once, then atomically mirror the resulting immutable frame."""
    frame, rho, _rho_lu, _adjacency, laplacian, _field = build_control_frame(
        seed, depth, revision
    )
    count = publish_messages(
        osc_messages(frame, rho), clients, inter_message_delay=inter_message_delay
    )
    if on_consultation is not None:
        on_consultation(frame, laplacian)
    return frame, count


class OracleAudioPlayer:
    """Render frozen consultations asynchronously and play them with afplay."""

    def __init__(self, config: RenderConfig, volume: float = 1.0):
        executable = shutil.which("afplay")
        if executable is None:
            raise RuntimeError("native audio playback requires /usr/bin/afplay")
        self.config = config
        self.volume = float(max(0.0, volume))
        self.executable = executable
        self._directory = tempfile.TemporaryDirectory(prefix="qmw_iching_audio_")
        self._lock = threading.Lock()
        self._generation = 0
        self._process: subprocess.Popen | None = None

    def play(self, frame, laplacian) -> None:
        """Schedule the newest reading; stale renders can never reach playback."""
        with self._lock:
            self._generation += 1
            generation = self._generation
        worker = threading.Thread(
            target=self._render_and_play,
            args=(generation, frame, laplacian.copy()),
            name=f"iching-audio-{frame.revision}",
            daemon=True,
        )
        worker.start()
        print(f"sound rendering revision={frame.revision}", flush=True)

    def _render_and_play(self, generation, frame, laplacian) -> None:
        try:
            audio, frequencies, _decays, _pans, retained = render_audio_from_frame(
                frame, laplacian, self.config
            )
            path = Path(self._directory.name) / f"reading_{frame.revision}_{generation}.wav"
            write_wav(path, audio, self.config.sample_rate)
            with self._lock:
                if generation != self._generation:
                    path.unlink(missing_ok=True)
                    return
                self._stop_locked()
                self._process = subprocess.Popen(
                    [self.executable, "--volume", str(self.volume), str(path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            print(f"sound playing revision={frame.revision} voices={len(frequencies)} "
                  f"frequency={frequencies.min():.1f}-{frequencies.max():.1f}Hz "
                  f"retained={retained:.4f}", flush=True)
        except Exception as exc:
            print(f"sound error revision={frame.revision}: {exc}", flush=True)

    def _stop_locked(self) -> None:
        if self._process is None or self._process.poll() is not None:
            return
        self._process.terminate()
        try:
            self._process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=1.0)

    def close(self) -> None:
        with self._lock:
            self._generation += 1
            self._stop_locked()
        self._directory.cleanup()

    def stop(self, _address=None, *_arguments) -> None:
        """Yield audio ownership to another I Ching renderer."""
        with self._lock:
            self._generation += 1
            self._stop_locked()
        print("consultation sound stopped for comparison playback", flush=True)


class ConsultationService:
    """Serialize GUI requests so consultations can never interleave on OSC."""

    def __init__(self, depth, clients, on_consultation=None):
        self.depth = int(depth)
        self.clients = list(clients)
        self.on_consultation = on_consultation
        self._lock = threading.Lock()

    def handle_request(self, _address, *_arguments):
        if not self._lock.acquire(blocking=False):
            return
        request_id = int(_arguments[0]) if _arguments else 0
        try:
            for client in self.clients:
                client.send_message("/qmw/iching/consult/accepted", [request_id])
            frame, count = build_and_publish_consultation(
                self.depth, self.clients, inter_message_delay=0.00075,
                on_consultation=self.on_consultation,
            )
            for client in self.clients:
                client.send_message(
                    "/qmw/iching/consult/published",
                    [request_id, signed_int32(frame.revision)],
                )
            print(f"consulted revision={frame.revision} seed={frame.seed} "
                  f"H0={frame.primary} M={frame.moving_mask} H1={frame.transformed} "
                  f"messages={count}", flush=True)
        except Exception:
            for client in self.clients:
                client.send_message("/qmw/iching/consult/error", [request_id])
            raise
        finally:
            self._lock.release()


def serve_consultations(host, control_port, depth, clients, on_consultation=None,
                        on_audio_stop=None):
    try:
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer
    except ImportError as exc:
        raise SystemExit("Consultation service requires: pip install python-osc") from exc
    service = ConsultationService(depth, clients, on_consultation=on_consultation)
    dispatcher = Dispatcher()
    dispatcher.map("/qmw/iching/consult/request", service.handle_request)
    if on_audio_stop is not None:
        dispatcher.map("/qmw/iching/audio/stop", on_audio_stop)
    server = ThreadingOSCUDPServer((host, control_port), dispatcher)
    print(f"consultation service listening on {host}:{control_port}", flush=True)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Mirror an I Ching network revision to engine and Processing")
    parser.add_argument("--seed", type=int); parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--revision", type=int); parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--engine-port", type=int, default=7403)
    parser.add_argument("--visual-port", type=int, default=7404)
    parser.add_argument("--control-port", type=int, default=7405)
    parser.add_argument("--serve", action="store_true",
                        help="listen for Processing consultation requests")
    parser.add_argument(
        "--sound", action=argparse.BooleanOptionalAction, default=None,
        help="play each consultation; defaults on with --serve",
    )
    parser.add_argument("--sound-duration", type=float, default=14.0)
    parser.add_argument("--sound-modes", type=int, default=24)
    parser.add_argument("--sound-base-frequency", type=float, default=90.0)
    parser.add_argument("--sound-maximum-frequency", type=float, default=20_000.0)
    parser.add_argument("--sound-volume", type=float, default=1.0)
    parser.add_argument("--no-engine", action="store_true")
    parser.add_argument("--no-visual", action="store_true")
    args = parser.parse_args()
    sound_enabled = args.serve if args.sound is None else args.sound
    if sound_enabled and not args.serve:
        raise SystemExit("--sound requires --serve so playback remains hosted")
    audio_player = None
    if sound_enabled:
        audio_player = OracleAudioPlayer(
            RenderConfig(
                duration_seconds=args.sound_duration,
                mode_count=args.sound_modes,
                base_frequency_hz=args.sound_base_frequency,
                maximum_frequency_hz=args.sound_maximum_frequency,
            ),
            volume=args.sound_volume,
        )
    sound_callback = audio_player.play if audio_player is not None else None
    clients = make_clients(args.host, args.engine_port, args.visual_port,
                           not args.no_engine, not args.no_visual)
    frame, count = build_and_publish_consultation(
        args.depth, clients, args.seed, args.revision,
        on_consultation=sound_callback,
    )
    destinations = []
    if not args.no_engine: destinations.append(f"engine={args.host}:{args.engine_port}")
    if not args.no_visual: destinations.append(f"visual={args.host}:{args.visual_port}")
    print(f"published revision={frame.revision} seed={frame.seed} messages={count} " + " ".join(destinations))
    if args.serve:
        try:
            serve_consultations(
                args.host, args.control_port, args.depth, clients,
                on_consultation=sound_callback,
                on_audio_stop=audio_player.stop if audio_player is not None else None,
            )
        except KeyboardInterrupt:
            print("consultation and sound service stopped", flush=True)
        finally:
            if audio_player is not None:
                audio_player.close()


if __name__ == "__main__": main()
