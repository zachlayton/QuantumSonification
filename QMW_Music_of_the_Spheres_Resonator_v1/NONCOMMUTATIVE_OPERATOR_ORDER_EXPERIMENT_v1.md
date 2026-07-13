# QMW Noncommutative Operator-Order Experiment v1

This is a finite-dimensional listening prototype inspired by deformation
quantization. It is deliberately **not** presented as a numerical
implementation of the full Kontsevich star product.

Two noncommuting, volume-preserving linear deformation flows act on one fixed
Tanglecube mesh. All four results retain the same vertex/face topology and are
renormalized to the same 0.25 m radius before the existing spectral geometry
and impulse-response pipeline is run.

## Load the Max lab

Open `QMW_Operator_Ecology_Lab_v1.maxpat` and load the normalized files into
the correspondingly lettered IR slots:

- **A — A then B:** `noncommutative_geometry/operator_order_v1/slot_A_A_then_B/slot_A_A_then_B_normalized.wav`
- **B — B then A:** `noncommutative_geometry/operator_order_v1/slot_B_B_then_A/slot_B_B_then_A_normalized.wav`
- **C — commutator:** `noncommutative_geometry/operator_order_v1/slot_C_commutator/slot_C_commutator_normalized.wav`
- **D — classical joint flow:** `noncommutative_geometry/operator_order_v1/slot_D_classical/slot_D_classical_normalized.wav`

Start with each slot gain at 0 dB or below and the master well below unity.
The four listening files have equalized total energy and conservative peaks;
this leaves headroom for the Quantum GenExpr resonator and the C/D feedback
paths. The unnormalized pipeline IR remains beside each living state for
diagnosis, but the normalized files are the intended lab inputs.

Suggested first comparison:

1. Set C and D fully dry/bypassed and crossfade only between A and B.
2. Listen for the consequence of operator order, holding source audio and gain
   constant.
3. Bring C up as the isolated commutator contribution.
4. Compare D as the simultaneous/classical control condition.
5. Only then introduce the C/D ping-pong feedback, beginning at low feedback.

## What was generated

Each slot contains:

- a candidate JSON record;
- an OBJ in meters;
- a Rhino-friendly OBJ in millimeters;
- spectral, material, quantum, timing, and acoustic state files;
- the raw auto-trimmed IR;
- an equal-energy normalized listening IR.

The full configuration, operator matrices, mesh diagnostics, spectral
descriptors, normalization values, and paths are recorded in
`noncommutative_geometry/operator_order_v1/noncommutative_operator_order_manifest.json`.

For this render, A-then-B and B-then-A differ by approximately 6.57 mm RMS and
23.9 mm maximum at corresponding vertices. Every mesh has 8,896 vertices,
17,808 faces, zero boundary edges, zero nonmanifold edges, and one connected
component.

## Re-render

Renders are append-only at the experiment level. If the requested output
directory already contains a render, the pipeline automatically creates the
next sibling fork—for example `operator_order_v1_fork_000002`, then
`operator_order_v1_fork_000003`. It never writes new results into the earlier
directory. Every manifest records the requested directory, actual directory,
fork index, and lineage under `fork`.

From the project directory:

```sh
env NUMBA_CACHE_DIR=/private/tmp/numba_cache \
  /Users/zlayton/miniconda3/envs/music/bin/python \
  noncommutative_geometry_pipeline_v1.py
```

Useful exploration controls include `--deformation`, `--commutator-gain`,
`--t60`, `--ir-duration`, `--modes`, and `--resolution`. Use `--output` to keep
different parameter studies separate.

Run the fast invariant tests with:

```sh
/Users/zlayton/miniconda3/envs/music/bin/python -m unittest -v \
  test_noncommutative_geometry_pipeline_v1.py
```
