# QuantumSonification

Private research and artistic-development workspace for quantum sonification,
spectral geometry, procedural acoustic spaces, Max/MSP instruments, and the
QMW Music of the Spheres Resonator.

The repository uses a domain-oriented top-level layout. The former
`QMW_Music_of_the_Spheres_Resonator_v1/` umbrella has been reorganized into
importable Python packages, operator pipelines, Max assets, generated state,
and versioned archives.

## Repository layout

- `operators/` — spectral, material, acoustic, living-geometry, and operator-ecology pipelines;
- `qmw/` — shared state/data buses, descriptor analysis, acoustics, and the optional Qiskit ML adapter;
- `max/` — Max/MSP patches, JavaScript controllers, and GenExpr-facing assets;
- `developmental_fields_v1/`, `emergent_geometry_v1_osc/`,
  `quantum_eigenfield_engine_v1/`, and `eigenfield_timing_layer_v1/` —
  importable geometry and timing packages;
- `qmw_temporal_crystal16_v1/` — four-qubit logical clocks, programmed
  recurrences, finite-size Floquet diagnostics, and the opt-in live density
  engine adapter;
- `surface_material_models_v1/`, `molecular_geometry_layer_v1/`, and
  `geometry_acoustics_bridge_v2/` — shared modal/material interchange packages;
- `eigenfield_processing_visualizer_v1/` and
  `quantum_relations_visualization_v1/` — Processing and OSC visualization packages;
- `procedural_chamber_mlx_v1/` and the Platonic reverb directories —
  procedural acoustic-space and reverb bundles;
- `algebraic_surfaces/`, `grasshopper_candidates/`, and
  `noncommutative_geometry/` — generated and experimental geometry state;
- `archives/` — refreshed distributable ZIP snapshots of standalone bundles.

Run Python entry points from the repository root with
`python package/module.py`. Importable APIs are exposed through each
package's `__init__.py`; operator tests use `python -m unittest` or a test
runner capable of importing the `operators` package.

## Current areas

- quantum population and density-field sonification;
- logical-time, rational-clock, and finite-size Floquet response experiments;
- quantum-kernel classification of learned sonic/material regimes;
- GenExpr and MC resonator instruments for Max/MSP;
- procedural and algebraic surface generation;
- spectral-geometry and material-response pipelines;
- auto-trimmed, revisioned impulse-response rendering;
- Grasshopper/Rhino geometry interchange;
- operator-order and noncommutative-geometry listening experiments;
- the QMW Operator Ecology Lab for comparing and combining IR families.

## Repository policy

This repository is intended to remain private while the work is being
developed. Source, patches, documentation, manifests, committed geometry, and
important listening artifacts are backed up together. Large audio, numerical,
archive, and rendered-media files are stored through Git LFS.

See `BACKUP_POLICY.md` before adding new generated families or publishing any
part of the repository.
