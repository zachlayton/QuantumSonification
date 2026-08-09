#!/usr/bin/env python3
"""CLI for Quantum Temporal Composition System v1."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path

if __package__ in {None, ""}:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from quantum_temporal_composition_v1.core import QuantumTemporalCompositionSystem, TemporalConfig
    from quantum_temporal_composition_v1.osc_output import OSCPublisher
else:
    from .core import QuantumTemporalCompositionSystem, TemporalConfig
    from .osc_output import OSCPublisher


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Emergent relational-time composition engine")
    p.add_argument("--config", type=Path)
    p.add_argument("--source", choices=("fallback", "file", "density-file"))
    p.add_argument("--state-path")
    p.add_argument("--observations", type=int, default=None, help="Stop after N observations (default: run until Ctrl-C)")
    p.add_argument("--rate", type=float)
    p.add_argument("--seed", type=int)
    p.add_argument("--osc-host")
    p.add_argument("--osc-port", type=int)
    p.add_argument("--no-osc", action="store_true")
    p.add_argument("--branches", action="store_true")
    p.add_argument("--log", dest="log_path")
    p.add_argument("--no-log", action="store_true")
    p.add_argument("--fast", action="store_true", help="Do not wall-clock pace (demo/testing)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    config = TemporalConfig.from_json(args.config) if args.config else TemporalConfig()
    updates = {}
    for arg, field in ((args.source, "source"), (args.state_path, "state_path"), (args.rate, "observation_hz"), (args.seed, "seed"), (args.osc_host, "osc_host"), (args.osc_port, "osc_port"), (args.log_path, "log_path")):
        if arg is not None:
            updates[field] = arg
    if args.no_osc:
        updates["osc_enabled"] = False
    if args.branches:
        updates["branch_tracking"] = True
    if args.no_log:
        updates["log_path"] = None
    config = replace(config, **updates)
    publisher = OSCPublisher(config.osc_host, config.osc_port) if config.osc_enabled else None
    engine = QuantumTemporalCompositionSystem(config, publisher=publisher)
    try:
        snapshots = engine.run(args.observations, realtime=not args.fast)
    except KeyboardInterrupt:
        return 0
    if snapshots:
        last = snapshots[-1]
        print(json.dumps({"observations": len(snapshots), "source": last.source, "clock_phase": last.clock_phase, "clock_confidence": last.clock_confidence, "events_last": len(last.events), "branches": len(last.branches), "log": config.log_path}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
