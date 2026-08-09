#!/usr/bin/env python3
"""Continuously stream the Figure 5 photoionization morph to Processing."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from photoionization_microscopy_v1 import (  # noqa: E402
    PhotoionizationConfig,
    PhotoionizationMicroscopySource,
    PhotoionizationOSCPublisher,
    UDPOSCClient,
)


def triangle_field(elapsed: float, cycle_seconds: float) -> float:
    """Return a 0..8..0 T triangular sweep."""
    phase = (elapsed % cycle_seconds) / cycle_seconds
    return 16.0 * phase if phase < 0.5 else 16.0 * (1.0 - phase)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=17620)
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--cycle-seconds", type=float, default=24.0)
    parser.add_argument("--duration", type=float, help="stop after this many seconds")
    parser.add_argument("--field", type=float, help="hold a fixed field in [0, 8] T")
    args = parser.parse_args()
    if args.fps <= 0.0 or args.cycle_seconds <= 0.0:
        parser.error("--fps and --cycle-seconds must be positive")
    if args.field is not None and not 0.0 <= args.field <= 8.0:
        parser.error("--field must be in [0, 8]")

    source = PhotoionizationMicroscopySource(PhotoionizationConfig())
    client = UDPOSCClient(args.host, args.port)
    publisher = PhotoionizationOSCPublisher(client)
    interval = 1.0 / args.fps
    started = time.monotonic()
    next_frame = started
    print(
        "QMW Photoionization -> Processing "
        f"udp://{args.host}:{args.port} at {args.fps:g} fps"
    )
    print("Ctrl-C to stop")
    try:
        while True:
            now = time.monotonic()
            elapsed = now - started
            if args.duration is not None and elapsed >= args.duration:
                break
            field_t = args.field if args.field is not None else triangle_field(
                elapsed, args.cycle_seconds
            )
            source.set_magnetic_field(field_t)
            publisher.publish(source)
            next_frame += interval
            time.sleep(max(0.0, next_frame - time.monotonic()))
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
