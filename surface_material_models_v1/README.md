# Surface Material Models v1

Canonical model order:

```text
1. surface_laplacian
2. tensioned_membrane
3. elastic_shell
4. bioelectric_surface
5. graph_diffusion
```

Repository entry point:

```text
surface_material_models_v1/
```

Install:

```bash
pip install numpy scipy
```

## 1. Surface Laplacian

```bash
python surface_material_models_v1/surface_material_models_v1.py \
  output/emergent_labyrinth_spectrum.npz \
  --model surface_laplacian \
  --wave-speed 120 \
  --output output/labyrinth_surface_laplacian
```

## 2. Tensioned membrane

```bash
python surface_material_models_v1/surface_material_models_v1.py \
  output/emergent_labyrinth_spectrum.npz \
  --model tensioned_membrane \
  --tension 3.0 \
  --density 0.8 \
  --output output/labyrinth_membrane
```

## 3. Elastic shell

```bash
python surface_material_models_v1/surface_material_models_v1.py \
  output/emergent_labyrinth_spectrum.npz \
  --model elastic_shell \
  --tension 0.8 \
  --density 1.2 \
  --stiffness 0.035 \
  --output output/labyrinth_shell
```

## 4. Bioelectric surface

The voltage field must contain one value per mesh vertex:

```bash
python surface_material_models_v1/surface_material_models_v1.py \
  output/emergent_labyrinth_spectrum.npz \
  --model bioelectric_surface \
  --voltage output/current_vertex_voltage.npy \
  --wave-speed 90 \
  --output output/labyrinth_bioelectric
```

## 5. Graph diffusion

```bash
python surface_material_models_v1/surface_material_models_v1.py \
  output/emergent_labyrinth_spectrum.npz \
  --model graph_diffusion \
  --graph-edge-scale 1.0 \
  --wave-speed 70 \
  --output output/labyrinth_graph
```

## Common output packet

Every model exports the same keys:

```text
model
eigenvalues
eigenvectors
frequencies_hz
angular_frequencies
decay_times_seconds
t60_seconds
damping_rates
mode_weights
metadata_json
```

That allows the quantum eigenfield engine, timing layer, visualization, and
convolution bridge to consume any of the five models without changing their
basic interface.

`damping_rates` are amplitude-decay rates in s^-1 and
`decay_times_seconds = 1 / damping_rates` contains the corresponding e-folding
time. `t60_seconds = log(1000) / damping_rates` is the audible reverberation
time. The default is 4 seconds. Use `--t60` for direct musical control or
`--damping` for low-level rate control. Values are deliberately not clamped:
the normal operating region is 1–10 seconds, while sub-second and 20–60+ second
responses remain available to geometry, material, and quantum modulation.

## Interpretation

```text
surface_laplacian  intrinsic manifold spectrum
tensioned_membrane tension and surface-density scaling
elastic_shell      tension plus bending-stiffness scaling
bioelectric_surface conductivity/leakage modifies the operator
graph_diffusion    connectivity replaces continuous metric geometry
```
