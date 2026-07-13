#!/usr/bin/env python3
"""
qmw_complex_pauli_autoload_v1.py

Start the Complex Pauli Oscillator v1 chain with the correct OSC ports.

Default port map:
    Max listens on 7403
    Timing layer listens on 7420 and sends to Max on 7403
    Complex Pauli synth listens on 7410 and sends to timing on 7420
    Operator preset morpher listens on 7404 and sends to synth on 7410

Run:
    python synth/qmw_complex_pauli_autoload_v1.py

Direct synth-to-Max debug mode:
    python synth/qmw_complex_pauli_autoload_v1.py --no-timing
"""

from __future__ import annotations

import argparse
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional


ROOT = Path(__file__).resolve().parents[1]
SYNTH_SCRIPT = ROOT / "synth" / "qmw_complex_pauli_synth_v1.py"
MORPHER_SCRIPT = ROOT / "control" / "qmw_operator_preset_morpher_v1.py"
TIMING_SCRIPT = ROOT / "control" / "qmw_timing_probability_layer_v1.py"


def start_process(name: str, argv: List[str]) -> subprocess.Popen:
    print(f"Starting {name}: {' '.join(argv)}", flush=True)
    return subprocess.Popen(argv, cwd=str(ROOT))


def stop_process(name: str, proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    print(f"Stopping {name}...", flush=True)
    proc.terminate()
    try:
        proc.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=3.0)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Autoload the QMW Complex Pauli Oscillator v1 OSC chain."
    )
    parser.add_argument("--host", default="127.0.0.1", help="OSC output host")
    parser.add_argument("--max-port", type=int, default=7403, help="Max UDP receive port")
    parser.add_argument("--synth-port", type=int, default=7410, help="Synth OSC input port")
    parser.add_argument("--timing-port", type=int, default=7420, help="Timing-layer OSC input port")
    parser.add_argument("--morpher-port", type=int, default=7404, help="Morpher OSC control input port")
    parser.add_argument("--synth-rate", type=float, default=120.0, help="Synth output rate in Hz")
    parser.add_argument("--timing-rate", type=float, default=120.0, help="Timing-layer output rate in Hz")
    parser.add_argument("--morpher-rate", type=float, default=60.0, help="Morpher output rate in Hz")
    parser.add_argument("--f0", type=float, default=41.2, help="Synth fundamental frequency")
    parser.add_argument("--no-morpher", action="store_true", help="Do not start the morpher")
    parser.add_argument("--no-timing", action="store_true", help="Send synth directly to Max")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    python = sys.executable
    processes: List[tuple[str, subprocess.Popen]] = []
    stopping = False

    def request_stop(signum: int, frame: object) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    synth_cmd = [
        python,
        str(SYNTH_SCRIPT),
        "--host",
        args.host,
        "--out-port",
        str(args.max_port if args.no_timing else args.timing_port),
        "--in-port",
        str(args.synth_port),
        "--rate",
        str(args.synth_rate),
        "--f0",
        str(args.f0),
    ]
    processes.append(("synth", start_process("synth", synth_cmd)))

    if not args.no_timing:
        timing_cmd = [
            python,
            str(TIMING_SCRIPT),
            "--host",
            args.host,
            "--in-port",
            str(args.timing_port),
            "--out-port",
            str(args.max_port),
            "--morph-port",
            str(args.morpher_port),
            "--rate",
            str(args.timing_rate),
        ]
        processes.append(("timing", start_process("timing", timing_cmd)))

    if not args.no_morpher:
        morpher_cmd = [
            python,
            str(MORPHER_SCRIPT),
            "--host",
            args.host,
            "--out-port",
            str(args.synth_port),
            "--in-port",
            str(args.morpher_port),
            "--rate",
            str(args.morpher_rate),
        ]
        processes.append(("morpher", start_process("morpher", morpher_cmd)))

    print(
        "\nQMW Complex Pauli Oscillator chain running\n"
        f"  Max listens:      {args.max_port}\n"
        f"  Synth listens:    {args.synth_port}\n"
        f"  Timing listens:   {args.timing_port if not args.no_timing else 'disabled'}\n"
        f"  Morpher listens:  {args.morpher_port if not args.no_morpher else 'disabled'}\n"
        "Ctrl-C to stop all processes.",
        flush=True,
    )

    try:
        while not stopping:
            for name, proc in processes:
                code = proc.poll()
                if code is not None:
                    raise SystemExit(f"{name} exited with code {code}")
            time.sleep(0.25)
    finally:
        for name, proc in reversed(processes):
            stop_process(name, proc)


if __name__ == "__main__":
    main()
