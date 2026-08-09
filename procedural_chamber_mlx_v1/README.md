# Procedural Chamber MLX v1

A first working prototype of a **procedural geometry → synthetic architectural acoustics** instrument.

The script creates a subdivided Platonic chamber, deforms it with a deterministic multiscale wave field, analyzes its weighted surface-graph spectrum, derives a geometry-conditioned orthogonal 16-line feedback matrix, and renders a stereo impulse response using MLX batched complex linear solves and MLX FFT.

## Why MLX

Dense arrays, eigendecomposition, QR factorization, Hadamard mixing, complex FDN transfer-function solves, and inverse FFT remain in MLX. Python's standard library handles mesh topology, JSON, OBJ, and WAV output. NumPy is not required.

## Install

In the QuantumSonification environment:

```bash
conda activate music
pip install -U "mlx>=0.31.2,<0.33"
```

## First render

From the repository root:

```bash
python procedural_chamber_mlx_v1/procedural_chamber_mlx_v1.py \
  --shape icosa \
  --subdivisions 2 \
  --radius-m 7.5 \
  --deformation 0.34 \
  --fractal-octaves 5 \
  --porosity 0.20 \
  --rt60 6.5 \
  --duration 8 \
  --name icosa_fractal_01
```

The output directory contains:

- `icosa_fractal_01.obj` — deformed chamber mesh
- `icosa_fractal_01.json` — geometry, Laplacian spectrum, delays, filters, vectors, and 16×16 feedback matrix
- `icosa_fractal_01_stereo_ir.wav` — 24-bit stereo impulse response

The JSON file is valid Max dictionary material and can be read by a `dict` object. The WAV can be loaded into Ableton Convolution Reverb, Max `buffer~`, FluCoMa buffers, or a convolution engine.

## Faster diagnostic render

```bash
python procedural_chamber_mlx_v1/procedural_chamber_mlx_v1.py \
  --shape tetra \
  --subdivisions 2 \
  --duration 2 \
  --sample-rate 24000 \
  --chunk-bins 512 \
  --name tetra_test
```

## Geometry only

```bash
python procedural_chamber_mlx_v1/procedural_chamber_mlx_v1.py \
  --shape cube \
  --subdivisions 3 \
  --geometry-only \
  --name cube_chamber_mesh
```

## Important interpretation

This v1 is a musical structural model. It does not claim to solve the full 3D acoustic wave equation or perform exact mesh ray tracing. The weighted **surface** graph Laplacian shapes the delay network and its coupling matrix. Exact volumetric cavity modes and physically validated boundary conditions belong to a later wave-simulation stage.

## Main controls

- `--shape`: `tetra`, `cube`, `octa`, `icosa`
- `--roundedness`: interpolate from faceted polyhedron toward a circumsphere
- `--deformation`: depth of multiscale radial deformation
- `--fractal-octaves`: number of procedural spatial scales
- `--lacunarity`, `--persistence`: fractal frequency and amplitude progression
- `--twist`: continuous rotational deformation around the z-axis
- `--porosity`: recessed pocket depth; v1 does not yet cut topological holes
- `--anisotropy-x/y/z`: stretch the chamber along each axis
- `--radius-m`: physical maximum chamber radius
- `--rt60`: target late decay time
- `--hf-cutoff`: base frequency-dependent feedback damping
- `--early-mix`, `--late-mix`: balance vertex-path early reflections and FDN tail
- `--seed`: produce repeatable chamber families

## Compatibility note

The frequency-domain FDN is complex-valued. For broad MLX device compatibility, v1 converts each complex 16×16 system into the equivalent real 32×32 block system before calling `mx.linalg.solve`. This remains an MLX batched solve and avoids relying on direct complex linear-system support.

## Tests

```bash
python -m unittest -v procedural_chamber_mlx_v1.test_procedural_chamber_mlx_v1
```

The regression suite checks mesh validity, feedback-matrix orthogonality, unique prime delay lengths, finite stereo IR output, and OBJ/JSON export.

## Recommended next integration

The JSON can drive a Max/Gen~ real-time renderer using the exported delay lengths, high-frequency cutoffs, injection/readout vectors, and feedback matrix. A later version can accept live Pauli/density-matrix descriptors and recompile chamber states A/B for click-free interpolation.
