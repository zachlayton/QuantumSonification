# Developmental Fields v1

Place `developmental_fields_v1.py` in:

```text
~/QuantumSonification/geometry/
```

The module provides a common MLX interface for:

- Gray–Scott reaction–diffusion
- classical Turing activator–inhibitor dynamics
- FitzHugh–Nagumo excitable media
- damped wave morphogenesis
- slow bioelectric memory

## Quick test

```python
from developmental_fields_v1 import create_developmental_field

field = create_developmental_field(
    "spiral_waves",
    size=192,
    seed=23,
)

for _ in range(1000):
    field.step(1)

u, v = field.geometry_fields()
print(field.descriptors())
```

## Available presets

```text
labyrinth
cellular
coral_growth
mitosis
solitons
turing_stripes
turing_spots
segmentation
excitable
spiral_waves
cardiac
standing_wave
chladni
slow_membrane
bioelectric_memory
regenerative
plastic
```

## Incremental integration

The module exports backward-compatible aliases:

```python
MorphogenParameters = GrayScottParameters
MorphogenField = GrayScottField
PRESETS = GRAY_SCOTT_PRESETS
```

So the current engine can first replace its local Gray–Scott declarations with:

```python
from developmental_fields_v1 import (
    MorphogenField,
    MorphogenParameters,
    PRESETS,
    laplacian,
)
```

A later engine revision can use `create_developmental_field()` and accept any
field model without assuming Gray–Scott-specific `u` and `v` semantics.
