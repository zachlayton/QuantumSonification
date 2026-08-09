#!/usr/bin/env python3
"""CLI for the QMW correlation/differentiation clock."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path

from .core import CorrelationDifferentiationClockSystem, TemporalV2Config
from .osc_output import CorrelationClockOSCPublisher


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Correlation / differentiation event clock"
    )
    result.add_argument("--config", type=Path)
    result.add_argument("--source", choices=("fallback", "file", "density-file"))
    result.add_argument("--state-path")
    result.add_argument("--change-quantum", type=float)
    result.add_argument("--observations", type=int)
    result.add_argument("--rate", type=float)
    result.add_argument("--osc-port", type=int)
    result.add_argument("--no-osc", action="store_true")
    result.add_argument("--log", dest="log_path")
    result.add_argument("--no-log", action="store_true")
    result.add_argument("--fast", action="store_true")
    result.add_argument(
        "--print-ticks", action="store_true", help="Print every relational tick"
    )
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    config = (
        TemporalV2Config.from_json(args.config)
        if args.config
        else TemporalV2Config()
    )
    updates = {}
    for value, name in (
        (args.source, "source"),
        (args.state_path, "state_path"),
        (args.change_quantum, "change_quantum"),
        (args.rate, "observation_hz"),
        (args.osc_port, "osc_port"),
        (args.log_path, "log_path"),
    ):
        if value is not None:
            updates[name] = value
    if args.no_osc:
        updates["osc_enabled"] = False
    if args.no_log:
        updates["log_path"] = None
    config = replace(config, **updates)
    publishers = []
    if config.osc_enabled:
        publishers.append(
            CorrelationClockOSCPublisher(config.osc_host, config.osc_port)
        )
    if args.print_ticks:
        publishers.append(ConsoleTickPublisher())
    publisher = CompositePublisher(publishers) if publishers else None
    system = CorrelationDifferentiationClockSystem(config, publisher=publisher)
    try:
        snapshots = system.run(args.observations, realtime=not args.fast)
    except KeyboardInterrupt:
        return 0
    if snapshots:
        kinds = {"correlate": 0, "differentiate": 0}
        for snapshot in snapshots:
            for tick in snapshot.ticks:
                kinds[tick.kind] += 1
        print(
            json.dumps(
                {
                    "observations": len(snapshots),
                    "relational_time": snapshots[-1].relational_time,
                    "ticks": kinds,
                    "source": snapshots[-1].source,
                    "log": config.log_path,
                },
                indent=2,
            )
        )
    return 0


class ConsoleTickPublisher:
    def publish(self, snapshot) -> None:
        for tick in snapshot.ticks:
            print(
                f"T={tick.relational_time:06d} {tick.kind:13s} "
                f"{tick.edge:28s} dC={tick.differentiation:+.5f} "
                f"C={tick.correlation:.5f} note={tick.midi}",
                flush=True,
            )


class CompositePublisher:
    def __init__(self, publishers) -> None:
        self.publishers = tuple(publishers)

    def publish(self, snapshot) -> None:
        for publisher in self.publishers:
            publisher.publish(snapshot)


if __name__ == "__main__":
    raise SystemExit(main())
