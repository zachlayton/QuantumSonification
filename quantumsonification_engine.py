#!/usr/bin/env python3
"""Canonical launcher for the QuantumSonification simulation engine.

The conductor, Max patches, and automation should invoke this file instead of
depending on a versioned implementation filename.  Versioned engines remain
available for reproducibility and are selected through the implementation
registry below.

All arguments not owned by this launcher are forwarded unchanged to the
selected engine.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_IMPLEMENTATION = "resonator_v9"
DEFAULT_PROTOCOL = "qmw-osc-v1"


@dataclass(frozen=True)
class EngineImplementation:
    """Metadata needed to launch one versioned engine implementation."""

    script: Path
    engine_name: str
    engine_version: str
    protocol: str
    capabilities: tuple[str, ...]


ENGINE_IMPLEMENTATIONS = {
    "resonator_v9": EngineImplementation(
        script=PROJECT_ROOT / "quantum_population_osc_v9_resonator.py",
        engine_name="resonator",
        engine_version="9",
        protocol=DEFAULT_PROTOCOL,
        capabilities=(
            "density",
            "mutual_information",
            "pauli",
            "bohmian",
            "external_clock",
            "circuit_bridge",
            "resonance_events",
            "born_transition",
            "density_state_injection",
            "temporal_crystal16",
        ),
    ),
}

IMPLEMENTATION_ALIASES = {
    "canonical": DEFAULT_IMPLEMENTATION,
    "default": DEFAULT_IMPLEMENTATION,
    "v9": "resonator_v9",
}


def resolve_implementation(name: str) -> tuple[str, EngineImplementation]:
    """Resolve an implementation name or stable alias."""
    canonical_name = IMPLEMENTATION_ALIASES.get(name, name)
    try:
        return canonical_name, ENGINE_IMPLEMENTATIONS[canonical_name]
    except KeyError as exc:
        available = ", ".join(sorted(ENGINE_IMPLEMENTATIONS))
        raise ValueError(
            f"Unknown engine implementation {name!r}; available: {available}"
        ) from exc


def implementation_description(
    name: str, implementation: EngineImplementation
) -> dict[str, object]:
    return {
        "implementation": name,
        "engine_name": implementation.engine_name,
        "engine_version": implementation.engine_version,
        "protocol": implementation.protocol,
        "capabilities": list(implementation.capabilities),
        "script": str(implementation.script),
    }


def parse_launcher_args(
    argv: Sequence[str],
) -> tuple[argparse.Namespace, list[str]]:
    # Deliberately do not claim --help: it belongs to the selected engine and
    # therefore always documents the actual forwarded command-line contract.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--implementation",
        default=os.environ.get(
            "QMW_ENGINE_IMPLEMENTATION", DEFAULT_IMPLEMENTATION
        ),
    )
    parser.add_argument("--protocol", default=DEFAULT_PROTOCOL)
    parser.add_argument("--list-implementations", action="store_true")
    parser.add_argument("--describe-implementation", action="store_true")
    return parser.parse_known_args(list(argv))


def main(argv: Sequence[str] | None = None) -> int:
    launcher_args, engine_args = parse_launcher_args(
        sys.argv[1:] if argv is None else argv
    )

    if launcher_args.list_implementations:
        for name in sorted(ENGINE_IMPLEMENTATIONS):
            implementation = ENGINE_IMPLEMENTATIONS[name]
            print(
                f"{name}\t{implementation.engine_name} "
                f"v{implementation.engine_version}\t"
                f"{implementation.protocol}"
            )
        return 0

    try:
        name, implementation = resolve_implementation(
            launcher_args.implementation
        )
    except ValueError as exc:
        print(f"quantumsonification_engine.py: error: {exc}", file=sys.stderr)
        return 2

    if launcher_args.protocol != implementation.protocol:
        print(
            "quantumsonification_engine.py: error: implementation "
            f"{name!r} provides {implementation.protocol!r}, not requested "
            f"protocol {launcher_args.protocol!r}",
            file=sys.stderr,
        )
        return 2

    if launcher_args.describe_implementation:
        print(
            json.dumps(
                implementation_description(name, implementation), indent=2
            )
        )
        return 0

    if not implementation.script.is_file():
        print(
            "quantumsonification_engine.py: error: engine script not found: "
            f"{implementation.script}",
            file=sys.stderr,
        )
        return 2

    environment = os.environ.copy()
    environment.update(
        {
            "QMW_ENGINE_IMPLEMENTATION": name,
            "QMW_ENGINE_NAME": implementation.engine_name,
            "QMW_ENGINE_VERSION": implementation.engine_version,
            "QMW_OSC_PROTOCOL": implementation.protocol,
            "QMW_ENGINE_CAPABILITIES": ",".join(
                implementation.capabilities
            ),
        }
    )

    command = [sys.executable, str(implementation.script), *engine_args]
    os.execve(sys.executable, command, environment)
    return 0  # pragma: no cover - os.execve replaces this process.


if __name__ == "__main__":
    raise SystemExit(main())
