#!/usr/bin/env python3
"""Generate axisymmetric OBJ geometry from numerical rho/z density arrays."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from photoionization_microscopy_v1.geometry import (
    DensityArrayGeometryConfig,
    generate_density_array_geometry,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--density-npz", type=Path, required=True,
        help="NPZ with rho_um, z_um, and density_rho_z or complex psi_rho_z",
    )
    parser.add_argument("--level", type=float, default=1.0e-3)
    parser.add_argument("--axial-resolution", type=int, default=84)
    parser.add_argument("--transverse-resolution", type=int, default=50)
    parser.add_argument("--display-length-mm", type=float, default=240.0)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "photoionization_geometry_v1")
    args = parser.parse_args()
    config = DensityArrayGeometryConfig(
        relative_density_level=args.level,
        axial_resolution=args.axial_resolution,
        transverse_resolution=args.transverse_resolution,
        display_length_mm=args.display_length_mm,
    )
    generated = generate_density_array_geometry(
        args.density_npz,
        args.output,
        config,
    )
    for label, path in generated.items():
        print(f"{label}: {path}")


if __name__ == "__main__":
    main()
