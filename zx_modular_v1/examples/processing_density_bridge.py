#!/usr/bin/env python3
"""Run the Processing ZX semantic and density-matrix OSC bridge."""

from __future__ import annotations

import argparse
import signal
import threading

from zx_modular_v1.rewrite_osc import RewriteOSCVerifier


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Mirror the Processing ZX canvas, evaluate discard-ZX density "
            "matrices, and forward approved candidates to the QMW engine."
        )
    )
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, default=7499)
    parser.add_argument("--processing-host", default="127.0.0.1")
    parser.add_argument("--processing-port", type=int, default=7497)
    parser.add_argument("--max-density-host", default="127.0.0.1")
    parser.add_argument("--max-density-port", type=int, default=7498)
    parser.add_argument("--tomography-host", default="127.0.0.1")
    parser.add_argument("--tomography-port", type=int, default=7426)
    parser.add_argument("--engine-host", default="127.0.0.1")
    parser.add_argument("--engine-port", type=int, default=7402)
    args = parser.parse_args()

    verifier = RewriteOSCVerifier(
        listen_host=args.listen_host,
        listen_port=args.listen_port,
        processing_host=args.processing_host,
        processing_port=args.processing_port,
        max_density_host=args.max_density_host,
        max_density_port=args.max_density_port,
        tomography_host=args.tomography_host,
        tomography_port=args.tomography_port,
        engine_host=args.engine_host,
        engine_port=args.engine_port,
    )
    stopped = threading.Event()

    def stop(_signal: int, _frame: object) -> None:
        stopped.set()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    verifier.start()
    print(
        "ZX density bridge ready: "
        f"Processing {args.processing_host}:{args.processing_port}, "
        f"Max density {args.max_density_host}:{args.max_density_port}, "
        f"tomography {args.tomography_host}:{args.tomography_port}, "
        f"engine {args.engine_host}:{args.engine_port}"
    )
    try:
        stopped.wait()
    finally:
        verifier.stop()


if __name__ == "__main__":
    main()
