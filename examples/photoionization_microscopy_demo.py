#!/usr/bin/env python3
"""Inspect or publish the Deng et al. Figure 5 magnetic-field sweep."""

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


def parse_fields(value: str) -> list[float]:
    fields = [float(item.strip()) for item in value.split(",") if item.strip()]
    if not fields or any(field < 0.0 or field > 8.0 for field in fields):
        raise argparse.ArgumentTypeError("fields must be comma-separated values in [0, 8]")
    return fields


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fields", type=parse_fields, default=parse_fields("0,2,4,6,8"))
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int)
    parser.add_argument("--realtime", action="store_true")
    args = parser.parse_args()

    source = PhotoionizationMicroscopySource(PhotoionizationConfig())
    publisher = None
    client = None
    if args.osc_port is not None:
        client = UDPOSCClient(args.osc_host, args.osc_port)
        publisher = PhotoionizationOSCPublisher(client)

    print("QMW Photoionization Microscopy v1")
    print(f"  {source.state.reference_status}")
    for field_t in args.fields:
        source.set_magnetic_field(field_t)
        state = source.state
        peaks = ", ".join(f"{value:.4f}" for value in state.peak_rho_um)
        lanes = " ".join(f"{value:.3f}" for value in state.detector_lanes)
        print(
            f"B={field_t:4.1f} T  E={state.resonance_energy_cm_inverse:8.3f} cm^-1  "
            f"rms={state.radial_rms_um:.4f} um  peaks=[{peaks}]"
        )
        print(f"           radial lanes: {lanes}")
        if publisher is not None:
            publisher.publish(source)
        if args.realtime:
            time.sleep(1.0)
    if client is not None:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
