# Emergent Geometry Engine v1

This is the autonomous first stage of the morphogenetic chamber system. It evolves a Gray–Scott reaction–diffusion field in MLX, converts the field into a deformable height surface, computes morphology descriptors, and exports state, images, and a Wavefront OBJ mesh.

## Install

```bash
conda activate music
pip install mlx numpy pillow
```

## Repository package

```text
emergent_geometry_v1_osc/
```

## First run

```bash
cd ~/QuantumSonification

python emergent_geometry_v1_osc/emergent_geometry_engine_v1.py \
  --preset labyrinth \
  --size 192 \
  --steps 12000 \
  --export-state output/emergent_labyrinth_v1.npz \
  --export-descriptors output/emergent_labyrinth_v1.json \
  --export-obj output/emergent_labyrinth_v1.obj \
  --export-png-prefix output/emergent_labyrinth_v1
```

The PNG files are:

```text
emergent_labyrinth_v1_v.png
emergent_labyrinth_v1_height.png
```

## Faster diagnostic run

```bash
python emergent_geometry_v1_osc/emergent_geometry_engine_v1.py \
  --preset labyrinth \
  --size 96 \
  --steps 2000 \
  --report-every 500 \
  --export-png-prefix output/test_v1
```

## Presets

- `labyrinth`
- `cellular`
- `coral_growth`

## Current output descriptors

- surface area
- mean height
- height variance
- mean absolute curvature
- curvature variance
- binary pattern entropy
- anisotropy
- growth velocity
- morphogen U mean
- morphogen V mean and maximum

## Next module

`emergent_geometry_osc_v1.py` will expose parameters and descriptors over OSC. After that, `bioelectric_memory_v1.py` will add the slow regulatory field and hysteresis layer.

## Live OSC bridge

Install:

```bash
pip install python-osc
```

Run:

```bash
cd ~/QuantumSonification

python emergent_geometry_v1_osc/emergent_geometry_osc_v1.py \
  --preset labyrinth \
  --size 192 \
  --rate 20 \
  --iterations 4 \
  --control-port 7430 \
  --out-port 7431
```

Max objects:

```text
[udpsend 127.0.0.1 7430]
[udpreceive 7431]
```

First control messages:

```text
/emergent/control/preset cellular
/emergent/control/feed 0.042
/emergent/control/kill 0.061
/emergent/control/perturb 0.5 0.5 0.08 0.9
/emergent/control/run 0
/emergent/control/run 1
/emergent/control/reset 1
/emergent/control/export first_living_chamber
```
