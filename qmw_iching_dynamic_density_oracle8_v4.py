#!/usr/bin/env python3
"""Dynamic I Ching density oracle V4 with evolving Q6 gauge geometry.

V4 composes the unchanged V3 density engine with ``qmw_iching_gauge_bridge_v1``.
Every non-destructive observation derives rho_H(t), a complex Hermitian
adjacency, its positive-semidefinite magnetic Laplacian, all 240 elementary
plaquette phases, 15 line-pair summaries, and a low spectral descriptor.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import time
from typing import Iterator

from qmw_iching_dynamic_density_oracle8_v3 import (
    Consultation,
    DynamicFrame,
    DynamicIChingDensityOracle,
)
from qmw_iching_gauge_bridge_v1 import GaugeSnapshot, build_gauge_snapshot

V4_ROOT = "/qmw/iching/v4"


@dataclass
class DynamicGaugeFrame(DynamicFrame):
    revision: int
    gauge: GaugeSnapshot


def osc_messages(frame: DynamicGaugeFrame) -> Iterator[tuple[str, list]]:
    """Yield one bounded atomic V4 transaction.

    The 240 plaquettes are transmitted in 15 line-pair chunks.  Each chunk
    contains 16 canonical bases, then 16 phases, then 16 strengths.
    """
    root = V4_ROOT
    revision = int(frame.revision)
    descriptors = frame.gauge.descriptors
    yield root + "/begin", [
        revision, float(frame.time), descriptors.plaquette_count,
        len(frame.gauge.line_pairs), 6, len(descriptors.low_laplacian_eigenvalues),
    ]
    yield root + "/hexagram64", [revision, *frame.hexagram_probabilities]
    yield root + "/moving6", [revision, *frame.moving_probabilities]
    yield root + "/pauli81", [revision, *frame.pauli81_values.values()]
    yield root + "/information", [
        revision, frame.entropy_lower, frame.entropy_upper, frame.entropy_change,
        frame.entropy_hexagram, frame.mutual_information_lu, frame.purity,
        frame.d_entropy_lower, frame.d_entropy_upper, frame.d_entropy_change,
        frame.d_entropy_hexagram, frame.d_mutual_information_lu,
    ]
    yield root + "/gauge/summary", [
        revision, descriptors.active_plaquette_count,
        descriptors.mean_absolute_flux_radians,
        descriptors.circular_mean_phase_radians,
        descriptors.circular_variance, descriptors.chirality,
        descriptors.strongest_plaquette_index, descriptors.strongest_base,
        descriptors.strongest_line_a, descriptors.strongest_line_b,
        *descriptors.strongest_vertices,
        descriptors.strongest_flux_radians, descriptors.strongest_strength,
        descriptors.laplacian_trace, descriptors.laplacian_minimum_eigenvalue,
        descriptors.laplacian_hermiticity_error,
    ]
    yield root + "/gauge/spectrum", [
        revision, *descriptors.low_laplacian_eigenvalues
    ]
    for line in range(1, 7):
        group = [item for item in frame.gauge.edges if item.line == line]
        yield root + "/gauge/edge_line", [
            revision, line,
            *[item.source for item in group],
            *[item.weight for item in group],
            *[item.phase_radians for item in group],
        ]
    for pair in frame.gauge.line_pairs:
        yield root + "/gauge/pair_summary", [
            revision, pair.line_a, pair.line_b, pair.active_count,
            pair.mean_absolute_flux_radians, pair.circular_mean_phase_radians,
            pair.circular_variance, pair.chirality, pair.maximum_strength,
        ]
        group = [
            item for item in frame.gauge.plaquettes
            if item.line_a == pair.line_a and item.line_b == pair.line_b
        ]
        yield root + "/gauge/plaquette_pair", [
            revision, pair.line_a, pair.line_b,
            *[item.base for item in group],
            *[item.flux_radians for item in group],
            *[item.strength for item in group],
        ]
    yield root + "/end", [revision]


def consultation_message(revision: int, result: Consultation) -> tuple[str, list]:
    return V4_ROOT + "/consult", [
        int(revision), result.h0_index, result.h1_index,
        *result.traditional_lines, *result.moving_probabilities,
    ]


class DynamicIChingDensityOracleV4(DynamicIChingDensityOracle):
    """V3 dynamics plus a non-destructive gauge snapshot per observation."""

    def __init__(self, *args, gauge_low_modes: int = 8, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not 1 <= int(gauge_low_modes) <= 64:
            raise ValueError("gauge_low_modes must be between 1 and 64")
        self.gauge_low_modes = int(gauge_low_modes)
        self._v4_revision = 0

    def observe(self) -> DynamicGaugeFrame:
        # V3 observe owns the established metrics.  Suppress its legacy OSC
        # emission and publish only after the matching gauge snapshot exists.
        client = self._osc_client
        self._osc_client = None
        try:
            base_frame = super().observe()
        finally:
            self._osc_client = client
        snapshot = build_gauge_snapshot(
            self.density_matrix(), base_frame.moving_probabilities,
            low_mode_count=self.gauge_low_modes,
        )
        self._v4_revision = (self._v4_revision + 1) & 0x7FFFFFFF
        frame = DynamicGaugeFrame(
            **base_frame.__dict__, revision=self._v4_revision, gauge=snapshot
        )
        self._stream_v4_frame(frame)
        return frame

    def _stream_v4_frame(self, frame: DynamicGaugeFrame) -> None:
        if self._osc_client is None:
            return
        for address, arguments in osc_messages(frame):
            self._osc_client.send_message(address, arguments)

    def _stream_consultation(self, result: Consultation) -> None:
        if self._osc_client is not None:
            address, arguments = consultation_message(self._v4_revision, result)
            self._osc_client.send_message(address, arguments)


def frame_to_jsonable(frame: DynamicGaugeFrame) -> dict:
    """Return an archival payload without duplicating dense A/L matrices."""
    base = {
        key: value for key, value in frame.__dict__.items()
        if key != "gauge"
    }
    return {
        "schema": "qmw.iching.dynamic-gauge-frame.v4",
        "frame": base,
        "gauge": {
            "descriptors": asdict(frame.gauge.descriptors),
            "line_pairs": [asdict(item) for item in frame.gauge.line_pairs],
            "plaquettes": [asdict(item) for item in frame.gauge.plaquettes],
            "edges": [asdict(item) for item in frame.gauge.edges],
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("numpy", "mlx"), default="numpy")
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=8)
    parser.add_argument("--dephasing", type=float, default=0.0)
    parser.add_argument("--damping", type=float, default=0.0)
    parser.add_argument("--gauge-low-modes", type=int, default=8)
    parser.add_argument("--osc", action="store_true")
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=7403)
    parser.add_argument("--json", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    oracle = DynamicIChingDensityOracleV4(
        backend=args.backend, seed=args.seed, dephasing_rate=args.dephasing,
        damping_rate=args.damping, gauge_low_modes=args.gauge_low_modes,
    )
    if args.osc:
        oracle.enable_osc(args.osc_host, args.osc_port)
    started = time.perf_counter()
    frame = oracle.observe()
    for _ in range(args.steps):
        oracle.evolve(args.dt)
        frame = oracle.observe()
    elapsed = time.perf_counter() - started
    consultation = oracle.consult()
    descriptors = frame.gauge.descriptors
    payload = frame_to_jsonable(frame)
    payload["run"] = {
        "backend": oracle.backend.name,
        "requested_backend": args.backend,
        "steps": args.steps,
        "elapsed_seconds": elapsed,
        "frames_per_second": (args.steps + 1) / elapsed,
        "consultation": asdict(consultation),
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "schema": payload["schema"],
        "backend": oracle.backend.name,
        "revision": frame.revision,
        "time": frame.time,
        "plaquettes": descriptors.plaquette_count,
        "active_plaquettes": descriptors.active_plaquette_count,
        "mean_absolute_flux_radians": descriptors.mean_absolute_flux_radians,
        "circular_variance": descriptors.circular_variance,
        "chirality": descriptors.chirality,
        "strongest": {
            "base": descriptors.strongest_base,
            "lines": [descriptors.strongest_line_a, descriptors.strongest_line_b],
            "vertices": descriptors.strongest_vertices,
            "phase": descriptors.strongest_flux_radians,
            "strength": descriptors.strongest_strength,
        },
        "low_laplacian_eigenvalues": descriptors.low_laplacian_eigenvalues,
        "laplacian_minimum_eigenvalue": descriptors.laplacian_minimum_eigenvalue,
        "H0": consultation.h0_index,
        "H1": consultation.h1_index,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
