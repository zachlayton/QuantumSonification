"""Small OSC launcher between the workshop Max patch and Python modules.

Start this once before opening the Max patch:

    python workshop_max_launcher.py

The bridge deliberately uses only Python's standard library for OSC/UDP. The
module scripts still own all quantum calculation and audio rendering.
"""

from __future__ import annotations

import argparse
import socket
import struct
import subprocess
import sys
import threading
from pathlib import Path
from typing import Sequence

from workshop_audio import (
    _osc_message,
    bloch_vectors,
    probabilities_for,
    statevector_for,
)


WORKSHOP_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = WORKSHOP_DIR / "outputs"
DEFAULT_LISTEN_PORT = 7498
DEFAULT_REPLY_PORT = 7499
PROCESSING_PORT = 7497

MODULE_SCRIPTS = {
    1: "01_superposition.py",
    2: "02_bloch_sphere.py",
    3: "03_circuit_design.py",
    4: "04_entanglement.py",
    5: "05_entropy_and_measurement.py",
}


def _read_osc_string(packet: bytes, offset: int) -> tuple[str, int]:
    end = packet.find(b"\0", offset)
    if end < 0:
        raise ValueError("OSC string is not null-terminated.")
    value = packet[offset:end].decode("utf-8")
    offset = (end + 4) & ~3
    return value, offset


def parse_osc_message(packet: bytes) -> tuple[str, list[int | float | str]]:
    """Parse one OSC message using the workshop's small value-type subset."""

    address, offset = _read_osc_string(packet, 0)
    tags, offset = _read_osc_string(packet, offset)
    if not tags.startswith(","):
        raise ValueError("OSC type tag string is missing.")
    values: list[int | float | str] = []
    for tag in tags[1:]:
        if tag == "i":
            values.append(struct.unpack_from(">i", packet, offset)[0])
            offset += 4
        elif tag == "f":
            values.append(struct.unpack_from(">f", packet, offset)[0])
            offset += 4
        elif tag == "s":
            value, offset = _read_osc_string(packet, offset)
            values.append(value)
        else:
            raise ValueError(f"Unsupported OSC type tag: {tag}")
    return address, values


def parse_osc_packet(
    packet: bytes,
) -> list[tuple[str, list[int | float | str]]]:
    """Parse either one OSC message or the bundle emitted by Max `o.pack`."""

    if not packet.startswith(b"#bundle\0"):
        return [parse_osc_message(packet)]

    # OSC bundles begin with "#bundle", an eight-byte timetag, then one or more
    # size-prefixed message/bundle elements. o.pack normally sends one element,
    # but accepting all of them makes the bridge predictable.
    messages: list[tuple[str, list[int | float | str]]] = []
    offset = 16
    while offset < len(packet):
        if offset + 4 > len(packet):
            raise ValueError("OSC bundle element size is truncated.")
        size = struct.unpack_from(">i", packet, offset)[0]
        offset += 4
        if size < 0 or offset + size > len(packet):
            raise ValueError("OSC bundle element is truncated.")
        messages.extend(parse_osc_packet(packet[offset : offset + size]))
        offset += size
    return messages


def normalize_gates(value: str | Sequence[str]) -> list[str]:
    if isinstance(value, str):
        gates = value.replace(",", " ").lower().split()
    else:
        gates = [str(gate).lower() for gate in value]
    if not gates:
        raise ValueError("Place at least one H, X, Y, or Z gate before testing.")
    if len(gates) > 6:
        raise ValueError("The beginner challenge has six gate slots.")
    unknown = [gate for gate in gates if gate not in {"h", "x", "y", "z"}]
    if unknown:
        raise ValueError("This challenge uses only H, X, Y, and Z.")
    return gates


def module_command(
    module: int,
    *,
    python: str = sys.executable,
    play: bool = True,
    gates: Sequence[str] | None = None,
) -> list[str]:
    if module not in MODULE_SCRIPTS:
        raise ValueError("Choose a module from 1 through 5.")
    output = OUTPUT_DIR / f"max_module_{module}.wav"
    command = [python, str(WORKSHOP_DIR / MODULE_SCRIPTS[module]), "--output", str(output)]
    if not play:
        command.append("--no-play")
    if module == 2:
        command.extend(["--osc-port", str(PROCESSING_PORT)])
    if module == 3 and gates is not None:
        command.extend(["--gates", *normalize_gates(gates)])
        command[command.index(str(output))] = str(OUTPUT_DIR / "max_circuit_challenge.wav")
    return command


def circuit_feedback(gates: Sequence[str]) -> tuple[float, float, float, float, float]:
    # Import by filename because the participant module intentionally begins
    # with a number and is meant to be run, not installed as a package.
    import importlib.util

    path = WORKSHOP_DIR / "03_circuit_design.py"
    spec = importlib.util.spec_from_file_location("workshop_circuit_design", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    state = statevector_for(module.build_circuit(list(gates)))
    p0, p1 = probabilities_for(state)
    x, y, z = bloch_vectors(state)[0]
    return float(p0), float(p1), x, y, z


class WorkshopLauncher:
    def __init__(
        self,
        *,
        host: str = "127.0.0.1",
        listen_port: int = DEFAULT_LISTEN_PORT,
        reply_port: int = DEFAULT_REPLY_PORT,
        play: bool = True,
    ) -> None:
        self.host = host
        self.listen_port = listen_port
        self.reply_port = reply_port
        self.play = play
        self._busy = threading.Lock()
        self._send_warning_shown = False

    def send(self, address: str, values: Sequence[int | float | str]) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(
                    _osc_message(address, values),
                    (self.host, self.reply_port),
                )
        except OSError as error:
            # Terminal-only and sandboxed runs should still render their WAV.
            if not self._send_warning_shown:
                print(f"OSC status unavailable ({error}); continuing in Terminal.", flush=True)
                self._send_warning_shown = True

    def status(self, text: str) -> None:
        print(text, flush=True)
        self.send("/workshop/status", [text])

    def run(
        self,
        module: int,
        gates: Sequence[str] | None = None,
    ) -> int:
        if not self._busy.acquire(blocking=False):
            self.status("A module is already running; wait for its sound to finish.")
            return 2
        try:
            command = module_command(
                module,
                play=self.play,
                gates=gates,
            )
            label = f"Module {module}"
            if gates is not None:
                label = "Circuit " + " → ".join(gate.upper() for gate in gates)
            self.status(f"Running {label}…")
            completed = subprocess.run(command, cwd=WORKSHOP_DIR, check=False)
            if completed.returncode:
                self.status(f"{label} stopped with code {completed.returncode}. See Terminal.")
            else:
                self.status(f"{label} finished. WAV saved in outputs/.")
            return completed.returncode
        finally:
            self._busy.release()

    def handle(self, address: str, values: Sequence[int | float | str]) -> None:
        if address == "/workshop/ping":
            self.status("Python launcher connected.")
            return
        if address == "/workshop/run":
            try:
                module = int(values[0])
                threading.Thread(target=self.run, args=(module,), daemon=True).start()
            except (IndexError, TypeError, ValueError) as error:
                self.status(str(error))
            return
        if address == "/workshop/circuit":
            try:
                gates = normalize_gates(str(values[0]))
                p0, p1, x, y, z = circuit_feedback(gates)
                self.send("/workshop/feedback", [p0, p1, x, y, z])
                threading.Thread(
                    target=self.run,
                    args=(3, gates),
                    daemon=True,
                ).start()
            except (IndexError, TypeError, ValueError) as error:
                self.status(str(error))
            return
        self.status(f"Ignored unknown workshop message: {address}")

    def serve_forever(self) -> None:
        self.status(
            f"Workshop launcher ready on UDP {self.listen_port}; "
            f"Max replies use {self.reply_port}."
        )
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.listen_port))
            while True:
                packet, _sender = sock.recvfrom(65535)
                try:
                    for address, values in parse_osc_packet(packet):
                        self.handle(address, values)
                except (UnicodeDecodeError, ValueError, struct.error) as error:
                    self.status(f"Could not read OSC message: {error}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, default=DEFAULT_LISTEN_PORT)
    parser.add_argument("--reply-port", type=int, default=DEFAULT_REPLY_PORT)
    parser.add_argument("--no-play", action="store_true")
    parser.add_argument("--once", type=int, choices=MODULE_SCRIPTS)
    parser.add_argument("--circuit", nargs="+", choices=("h", "x", "y", "z"))
    args = parser.parse_args()
    launcher = WorkshopLauncher(
        host=args.host,
        listen_port=args.listen_port,
        reply_port=args.reply_port,
        play=not args.no_play,
    )
    if args.circuit:
        gates = normalize_gates(args.circuit)
        raise SystemExit(launcher.run(3, gates))
    if args.once:
        raise SystemExit(launcher.run(args.once))
    launcher.serve_forever()


if __name__ == "__main__":
    main()
