#!/usr/bin/env python3
"""Replay a saved IBM Pauli-15 archive into the QMW V5 Max instrument."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from pythonosc.udp_client import SimpleUDPClient

from qac_ibm_wavetable_bridge import PAULI15


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7412)
    parser.add_argument("--revision", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    archive_path = args.archive.expanduser().resolve()
    payload = json.loads(archive_path.read_text(encoding="utf-8"))
    if payload.get("schema") != "qmw.ibm.pauli15.archive.v1":
        raise SystemExit(f"Unsupported archive schema: {payload.get('schema')!r}")

    try:
        coefficients = [float(payload["pauli15"][term]) for term in PAULI15]
        features = payload["features"]
        descriptors = [
            float(features["z_polarization"]),
            float(features["concurrence"]),
            float(features["correlation_rms"]),
            float(features["entropy_bits"]),
        ]
        job_id = str(payload["job"]["id"])
        backend = str(payload["job"]["backend"])
        transform = str(payload["experiment"]["transform"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"Incomplete Pauli-15 archive: {exc}") from exc

    revision = (
        args.revision
        if args.revision is not None
        else int(time.time() * 1000) % 2_000_000_000
    )
    client = SimpleUDPClient(args.host, args.port)
    client.send_message(
        "/qmw/wavetable/status",
        ["archive_replay", revision, "ibm", backend, job_id],
    )
    # The compact-state renderer expects exactly:
    # revision, source, 15 Pauli coefficients, and four feature descriptors.
    client.send_message(
        "/qmw/quantum/state",
        [revision, "ibm", *coefficients, *descriptors],
    )
    client.send_message(
        "/qmw/quantum/features",
        [revision, *descriptors],
    )
    # The ZZ tomography PUB has no final X/Y rotation on q0 or q1; q2 and q3
    # are always measured in Z. It is therefore also the sixteen-bin
    # computational-basis histogram of the transformed four-qubit state.
    zz_setting = next(
        (setting for setting in payload.get("settings", [])
         if setting.get("basis") == "ZZ"),
        None,
    )
    qft_bins_sent = False
    if zz_setting is not None:
        # Rendering the compact state also builds a 262,144-sample IR inside
        # Max's single JavaScript thread. Give that render time to finish before
        # sending the spectrum packets so localhost UDP does not outrun Max.
        time.sleep(2.0)
        shots = float(zz_setting["shots"])
        counts = zz_setting["counts"]
        probabilities = [
            float(counts.get(f"{index:04b}", 0)) / shots for index in range(16)
        ]
        magnitudes = [math.sqrt(value) for value in probabilities]
        # Shot counts contain no phase information. Zero phase is the same
        # explicit fallback used by the bridge for IBM count-only spectra.
        phases = [0.0] * 16
        prefix = [revision, "ibm", transform]
        client.send_message("/qmw/qft/bins", [*prefix, *probabilities])
        client.send_message("/qmw/qft/amplitudes", [*prefix, *magnitudes])
        client.send_message("/qmw/qft/phases", [*prefix, *phases])
        # V5 also accepts one atomic compatibility frame on the long-proven
        # correlations route. This protects replay into an already-open patch
        # whose o.route object predates the three dedicated QFT addresses.
        client.send_message(
            "/qmw/wavetable/correlations",
            [
                revision,
                "qft_frame",
                "ibm",
                transform,
                *probabilities,
                *magnitudes,
                *phases,
            ],
        )
        qft_bins_sent = True
    print(
        f"Replayed IBM job {job_id} to udp://{args.host}:{args.port} "
        f"as revision {revision}"
    )
    print("Max buffers targeted: qmw_v5_ibm and qmw_v5_ir_ibm")
    if qft_bins_sent:
        print(
            "QFT spectrum restored from the ZZ counts with zero phase; "
            "targeted qmw_v5_qft_wave"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
