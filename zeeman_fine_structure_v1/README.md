# Zeeman field and fine structure v1

A magnetic field B and a weak spin–spin coupling acting on the 4-qubit engine,
so the instrument splits its 16 voices the way a field splits spectral lines.
Companion to `zeeman_resonator_v1` (atomic line model in Max); this module
works on the qubit Hamiltonian itself.

```text
H      = H_fine + H_Z                       (audible Hz)
H_Z    = (nu_L / 2) sum_q g_q Z_q           nu_L = B * hz_per_tesla (40 Hz/T default)
H_fine = (J / 4)    sum_ring (XX + YY + ZZ) ring 0-1-2-3-0
```

Both terms conserve total magnetisation M, so every eigenstate has a definite
M and the polarisation labels are exact: sigma lines (ΔM = ±1, matrix elements
of S+) and pi lines (ΔM = 0, matrix elements of Sz).

## What it reproduces (all tested)

| Case | Result |
|---|---|
| Equal g, J = 0 | levels by M with degeneracies 1, 4, 6, 4, 1, equally spaced |
| Equal g, J ≠ 0 | one sigma line at g·nu_L (Larmor's theorem: isotropic coupling does not shift it) |
| Unequal g (anomalous) | the sigma line breaks into many |
| Weak field, J ≫ spread | strongest line at the mean g (coupled multiplet) |
| Strong field (Paschen–Back analogue) | lines cluster at each qubit's own g, split by the coupling |
| Field sweep | levels tracked by overlap (Hungarian assignment) through avoided crossings |
| Quantum beats | coherent x-pulse precesses at g·nu_L; sublevels beat as they dephase |
| Hanle effect | P(B)/P(0) = 1 / (1 + (2 ω_L τ)²) |
| Directivity | pi ∝ sin²θ, sigma ∝ (1 + cos²θ)/2, sum isotropic; 2nd-order AmbiX coefficients around any field axis |

## Presets

- `normal`: g = 2 for every qubit, J = 6 Hz.
- `anomalous`: Landé values 2, 4/3, 2/3, 1; J = 6 Hz.
- `alpha_squared`: anomalous g, J = α² of a nominal 1 kHz gross structure (≈ 0.053 Hz).
- `free_spins`: anomalous g, J = 0.

## Use

```python
from zeeman_fine_structure_v1 import PRESETS, frame, sweep, directivity_ambisonics

fr = frame(PRESETS["anomalous"], field_t=3.0)
snapshot = fr.as_dict(carrier_hz=220.0)      # lines: polarisation, shift, strength
frames = sweep(PRESETS["anomalous"], [0.0, 0.1, 0.2])   # tracked levels
b_format = directivity_ambisonics("pi", field_axis=(0, 0, 1))
```

Live engine (adds the terms to every tick, leaves fields, feedback and noise alone):

```python
from zeeman_fine_structure_v1 import ZeemanFineLayer, attach
layer = attach(engine, ZeemanFineLayer(field_t=0.0))
layer.set_field(2.5); layer.set_preset("normal"); layer.set_g(2, 0.667)
```

Inside the full engine the engine's own X/Y fields break magnetisation
conservation, so polarisation labels there are approximate; `frame()` on the
added terms gives the exact ones. `scale` (default 2π) converts Hz to engine
units and should be checked against the engine's dt convention.

## Audition

```bash
python3 -m zeeman_fine_structure_v1.render_demo out.wav
python3 -m pytest zeeman_fine_structure_v1/test_model.py
```

16 s field sweep (anomalous, 0 → 6 T) with sigma+ right, sigma− left, pi centre,
then 6 s of quantum beats at 3 T. Lines are drawn at carrier ± shift, as in
resonator v1; at high field the lower sigma lines pass through 0 Hz and fold
back (through-zero), which is kept as a sound.

## Not yet

- OSC namespace (`/zeeman/field`, `/zeeman/preset`, `/zeeman/g`, `/zeeman/coupling`) and Max patch.
- Polarisation labels on emission events in the quantum clock; pi/sigma directivity in the HOA renderer.
- Matching `scale` to the engine's units.
