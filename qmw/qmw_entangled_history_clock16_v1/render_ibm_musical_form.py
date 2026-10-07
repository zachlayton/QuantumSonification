#!/usr/bin/env python3
"""Render an intelligible sixteen-voice musical form from IBM shot data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ibm_musical_sonification import (
    IBMMusicalConfig,
    render_ibm_musical_form,
    write_ibm_musical_form,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=36.0)
    args = parser.parse_args(argv)

    archive = json.loads(args.archive.read_text())
    config = IBMMusicalConfig(duration_seconds=float(args.duration))
    render = render_ibm_musical_form(archive["shot_sequences"], config)
    paths = write_ibm_musical_form(
        render,
        args.output_directory,
        sample_rate=config.sample_rate,
    )
    for name, path in paths.items():
        print(f"{name}: {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
