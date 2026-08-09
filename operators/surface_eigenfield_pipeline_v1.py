#!/usr/bin/env python3
"""One-shot surface → material → quantum → timing → acoustic pipeline."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import argparse
import json
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent

from eigenfield_timing_layer_v1 import EigenfieldState
from geometry_acoustics_bridge_v2 import (
    AcousticBridgeConfig,
    GeometryAcousticsBridgeV2,
)
from quantum_eigenfield_engine_v1 import (
    QuantumEigenfieldConfig,
    QuantumEigenfieldEngine,
    demo_density_matrix,
    load_density_matrix,
)
from surface_material_models_v1 import (
    DEFAULT_T60_SECONDS,
    MODEL_ORDER,
    SurfaceMaterialConfig,
    create_surface_model,
    damping_rate_from_t60,
    export_packet,
    load_spectral_npz,
)


class SurfaceEigenfieldPipeline:
    def __init__(
        self,
        material_config: SurfaceMaterialConfig = SurfaceMaterialConfig(),
        quantum_config: QuantumEigenfieldConfig = QuantumEigenfieldConfig(),
        acoustic_config: AcousticBridgeConfig = AcousticBridgeConfig(),
    ) -> None:
        self.material_config = material_config
        self.quantum_config = quantum_config
        self.acoustic_config = acoustic_config

    @staticmethod
    def _load_spectral(
        packet: str | Path | dict[str, np.ndarray],
    ) -> dict[str, np.ndarray]:
        return (
            load_spectral_npz(packet)
            if isinstance(packet, (str, Path))
            else dict(packet)
        )

    @staticmethod
    def _export_timing_snapshot(
        state: EigenfieldState,
        prefix: Path,
    ) -> dict[str, Path]:
        npz_path = prefix.with_suffix(".npz")
        json_path = prefix.with_suffix(".json")
        np.savez_compressed(
            npz_path,
            material_model=np.array(state.material_model),
            eigenvalues=state.eigenvalues,
            frequencies_hz=state.frequencies_hz,
            decay_times_seconds=state.decay_times_seconds,
            damping_rates=state.damping_rates,
            mode_weights=state.material_weights,
            mode_probabilities=state.probabilities,
            mode_amplitudes=state.amplitudes,
            cloud_xyz=np.asarray(
                [[p.cloud_x, p.cloud_y, p.cloud_z] for p in state.points],
                dtype=np.float64,
            ),
        )
        json_path.write_text(
            json.dumps(
                {
                    "material_model": state.material_model,
                    "mode_count": len(state.points),
                    "entropy_bits": state.entropy_bits,
                    "effective_participation": state.effective_participation,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return {"npz": npz_path, "json": json_path}

    def run(
        self,
        spectral_packet: str | Path | dict[str, np.ndarray],
        output_directory: str | Path,
        rho: np.ndarray | None = None,
        material_fields: dict[str, np.ndarray] | None = None,
    ) -> dict[str, Any]:
        output = Path(output_directory)
        output.mkdir(parents=True, exist_ok=True)
        spectral = self._load_spectral(spectral_packet)
        required = {"vertices", "faces", "eigenvalues", "eigenvectors"}
        missing = required.difference(spectral)
        if missing:
            raise ValueError(
                f"spectral packet missing pipeline fields: {sorted(missing)}"
            )
        if np.asarray(spectral["faces"]).size == 0:
            raise ValueError(
                "surface_eigenfield_pipeline_v1 requires triangular faces; "
                "an edges-only molecular graph needs a graph-specific pipeline"
            )
        fields = {} if material_fields is None else dict(material_fields)
        if (
            self.material_config.model == "bioelectric_surface"
            and "voltage" not in fields
        ):
            fields["voltage"] = np.zeros(
                len(spectral["vertices"]), dtype=np.float64
            )

        model = create_surface_model(
            vertices=spectral["vertices"],
            faces=spectral["faces"],
            eigenvalues=spectral["eigenvalues"],
            eigenvectors=spectral["eigenvectors"],
            config=self.material_config,
        )
        material_packet = model.solve(**fields)
        material_paths = export_packet(
            material_packet,
            self.material_config,
            output / "surface_material",
        )

        density_matrix = demo_density_matrix(4) if rho is None else rho
        quantum = QuantumEigenfieldEngine(
            density_matrix,
            modal_packet=material_packet,
            config=self.quantum_config,
        )
        quantum_paths = quantum.export(output / "quantum_eigenfield")

        timing_state = EigenfieldState(quantum_paths["npz"])
        timing_paths = self._export_timing_snapshot(
            timing_state, output / "timing_snapshot"
        )

        bridge = GeometryAcousticsBridgeV2(
            quantum_paths["npz"], self.acoustic_config
        )
        acoustic_paths = bridge.export(output / "modal_ir")

        bundle_path = output / "surface_eigenfield_bundle.npz"
        np.savez_compressed(
            bundle_path,
            vertices=spectral["vertices"],
            faces=spectral["faces"],
            material_model=np.array(material_packet.model),
            eigenvalues=material_packet.eigenvalues,
            eigenvectors=material_packet.eigenvectors,
            frequencies_hz=material_packet.frequencies_hz,
            angular_frequencies=material_packet.angular_frequencies,
            decay_times_seconds=material_packet.decay_times_seconds,
            damping_rates=material_packet.damping_rates,
            mode_weights=material_packet.mode_weights,
            mode_probabilities=quantum.mode_probabilities,
            mode_amplitudes=quantum.mode_amplitudes,
            spatial_eigenfield=quantum.spatial_eigenfield,
            developmental_drive=quantum.developmental_drive,
            material_metadata_json=np.asarray(
                json.dumps(material_packet.metadata, sort_keys=True)
            ),
        )

        paths = {
            "material": material_paths,
            "quantum": quantum_paths,
            "timing": timing_paths,
            "acoustics": acoustic_paths,
            "bundle": bundle_path,
        }
        manifest_path = output / "manifest.json"
        manifest = {
            "pipeline": "surface_eigenfield_pipeline_v1",
            "material_config": asdict(self.material_config),
            "quantum_config": asdict(self.quantum_config),
            "acoustic_config": asdict(self.acoustic_config),
            "material_model": material_packet.model,
            "mode_count": len(material_packet.eigenvalues),
            "quantum": quantum.quantum_descriptors.to_dict(),
            "timing": {
                "entropy_bits": timing_state.entropy_bits,
                "effective_participation": timing_state.effective_participation,
            },
            "acoustics": bridge.acoustic_descriptors(),
            "paths": {
                section: (
                    {name: str(path) for name, path in value.items()}
                    if isinstance(value, dict)
                    else str(value)
                )
                for section, value in paths.items()
            },
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        paths["manifest"] = manifest_path
        return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spectrum", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rho", type=Path)
    parser.add_argument("--model", choices=MODEL_ORDER, default=MODEL_ORDER[0])
    parser.add_argument("--modes", type=int, default=32)
    parser.add_argument("--wave-speed", type=float, default=120.0)
    parser.add_argument("--tension", type=float, default=1.0)
    parser.add_argument("--density", type=float, default=1.0)
    parser.add_argument("--stiffness", type=float, default=0.0)
    parser.add_argument(
        "--damping",
        type=float,
        help="Amplitude damping rate in s^-1 (overrides --t60)",
    )
    parser.add_argument("--t60", type=float, default=DEFAULT_T60_SECONDS)
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--sample-rate", type=int, default=48000)
    parser.add_argument("--voltage", type=Path)
    args = parser.parse_args()

    modes = max(1, args.modes)
    pipeline = SurfaceEigenfieldPipeline(
        SurfaceMaterialConfig(
            model=args.model,
            n_modes=modes,
            effective_wave_speed=args.wave_speed,
            surface_tension=args.tension,
            surface_density=args.density,
            bending_stiffness=args.stiffness,
            damping_base=(
                args.damping
                if args.damping is not None
                else damping_rate_from_t60(args.t60)
            ),
        ),
        QuantumEigenfieldConfig(n_geometric_modes=modes),
        AcousticBridgeConfig(
            sample_rate=args.sample_rate,
            duration_seconds=args.duration,
        ),
    )
    fields = (
        {} if args.voltage is None else {"voltage": np.load(args.voltage)}
    )
    rho = None if args.rho is None else load_density_matrix(args.rho)
    paths = pipeline.run(args.spectrum, args.output, rho, fields)
    print("Surface Eigenfield Pipeline v1 complete")
    print(f"  model:  {args.model}")
    print(f"  bundle: {paths['bundle']}")
    print(f"  IR:     {paths['acoustics']['wav']}")


if __name__ == "__main__":
    main()
