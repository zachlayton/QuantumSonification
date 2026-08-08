#!/usr/bin/env python3
"""Publish one frozen I Ching network revision to engine and Processing."""
from __future__ import annotations

import argparse

from qmw_iching_density_laplacian_bridge_v1 import build_control_frame, osc_messages


def signed_int32(value: int) -> int:
    value = int(value) & 0xFFFFFFFF
    return value if value < 0x80000000 else value - 0x100000000


def osc_safe_arguments(arguments):
    result = []
    for value in arguments:
        if isinstance(value, int): result.append(signed_int32(value))
        else: result.append(value)
    return result


def publish_messages(messages, clients):
    count = 0
    for address, arguments in messages:
        safe = osc_safe_arguments(arguments)
        for client in clients: client.send_message(address, safe)
        count += 1
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


def main():
    parser = argparse.ArgumentParser(description="Mirror an I Ching network revision to engine and Processing")
    parser.add_argument("--seed", type=int); parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--revision", type=int); parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--engine-port", type=int, default=7403)
    parser.add_argument("--visual-port", type=int, default=7404)
    parser.add_argument("--no-engine", action="store_true")
    parser.add_argument("--no-visual", action="store_true")
    args = parser.parse_args()
    frame, rho, *_ = build_control_frame(args.seed, args.depth, args.revision)
    clients = make_clients(args.host, args.engine_port, args.visual_port,
                           not args.no_engine, not args.no_visual)
    count = publish_messages(osc_messages(frame, rho), clients)
    destinations = []
    if not args.no_engine: destinations.append(f"engine={args.host}:{args.engine_port}")
    if not args.no_visual: destinations.append(f"visual={args.host}:{args.visual_port}")
    print(f"published revision={frame.revision} seed={frame.seed} messages={count} " + " ".join(destinations))


if __name__ == "__main__": main()
