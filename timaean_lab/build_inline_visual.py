#!/usr/bin/env python3
"""Embed a completed Timaean run into the canvas visual template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("template", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    archive = np.load(args.run_directory / "timaean_lab_data.npz")
    manifest = json.loads((args.run_directory / "manifest.json").read_text())
    names = ("pure", "coherent", "dephased", "maximally_mixed", "coherence_only")
    payload = {
        "vertices": np.round(archive["vertices"], 7).tolist(),
        "faces": archive["faces"].tolist(),
        "displacements": {
            name: np.round(archive[f"u_{name}"], 7).tolist() for name in names
        },
        "metrics": {name: manifest["states"][name] for name in names},
    }
    template = args.template.read_text(encoding="utf-8")
    marker = "__TIMAEAN_L4_DATA__"
    if template.count(marker) != 1:
        raise ValueError("template must contain exactly one data marker")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        template.replace(marker, json.dumps(payload, separators=(",", ":"))),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
