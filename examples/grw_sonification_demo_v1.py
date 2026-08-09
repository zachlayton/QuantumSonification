#!/usr/bin/env python3
"""Send one deterministic projective GHZ-localization render frame over OSC."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pythonosc.udp_client import SimpleUDPClient

from density.grw_event_channel_v1 import GRWConfig, GRWEventChannel, ghz_density
from density.grw_sonification_adapter_v1 import GRWSonificationAdapter


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--max-port", type=int, default=7400)
    parser.add_argument("--processing-port", type=int, default=7401)
    parser.add_argument("--sc-port", type=int, default=57120)
    parser.add_argument("--qubit", type=int, choices=range(4), default=2)
    parser.add_argument("--basis", choices=list("XYZ"), default="Z")
    parser.add_argument("--strength", type=float, default=1.0)
    parser.add_argument("--outcome", type=int, choices=(0, 1), default=0)
    args = parser.parse_args()

    channel = GRWEventChannel(GRWConfig(seed=23))
    event = channel.apply_hit(
        ghz_density(),
        revision_before=0,
        qubit=args.qubit,
        outcome=args.outcome,
        basis=args.basis,
        strength=args.strength,
    )
    ports = tuple(dict.fromkeys((args.max_port, args.processing_port, args.sc_port)))
    clients = tuple(SimpleUDPClient(args.host, port) for port in ports)
    frame = GRWSonificationAdapter(clients).publish_event(event)
    if frame is None:
        raise RuntimeError("Demo event was unexpectedly suppressed")

    print(f"event:          {frame.event_id}")
    print(f"branch/qubit:   {frame.branch}")
    print(f"excitation:     {frame.excitation_amplitude:.6f}")
    print(f"coherence loss: {frame.coherence_loss_fraction:.6f}")
    print(f"bandwidth:      {frame.bandwidth:.6f}")
    print(f"grain:          {frame.grain_structure:.6f}")
    print(
        "orientation:    "
        f"{frame.pauli_axis} {frame.orientation} "
        f"({frame.dominant_pauli}={frame.dominant_pauli_delta:+.6f})"
    )
    print(f"sent ports:     {', '.join(str(port) for port in ports)}")


if __name__ == "__main__":
    main()
