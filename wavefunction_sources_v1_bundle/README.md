# QuantumSonification Wavefunction Sources v1

This bundle expands the original quantum-source layer into a common complex-field system. It retains the original source names, adds a non-destructive `mutator_quantum_sources_v2.py`, and generalizes the free Schrödinger packet from one spatial dimension to one, two, or three dimensions.

NumPy is the only new dependency.

## What is included

The factory currently exposes:

- `schrodinger_packet` / `free_packet_1d`
- `schrodinger_packet_3d` / `free_packet_3d`
- `harmonic_oscillator`
- `harmonic_oscillator_3d`
- `coherent_state`
- `squeezed_state`
- `particle_in_box`
- `quantum_rotor`
- `double_well`
- `barrier_scattering`
- `periodic_lattice`
- `hydrogen_orbital_field`
- `hydrogen_superposition_3d`
- `spherical_harmonic`

The potential-driven solver itself supports `free`, `harmonic`, `double_well`, `barrier`, `periodic_lattice`, `coulomb`, and `driven` potentials in 1D, 2D, or 3D.

`hydrogen_spectrum` remains available through the v2 mutator as a discrete transition/event source. It is kept outside the wavefunction factory because it does not emit a complex field ψ.

## Installation in QuantumSonification

Copy the files into the matching folders in the repository:

```text
QuantumSonification/
├── excitation/
│   └── wavefunction_sources_v1.py
└── hamiltonian/
    └── mutator_quantum_sources_v2.py
```

Keep `mutator_quantum_sources_v1.py`. The new v2 module is deliberately a separate file.

## First 3D packet

From the `QuantumSonification` repository root:

```bash
python examples/wavefunction_sources_demo_v1.py \
  --source schrodinger_packet_3d \
  --grid 32 \
  --steps 40 \
  --dt 0.01 \
  --output packet_3d_frame.npz
```

Or directly in Python:

```python
from excitation.wavefunction_sources_v1 import create_wavefunction_source

source = create_wavefunction_source(
    "schrodinger_packet_3d",
    grid_shape=32,
    center=(-3.0, 0.0, 0.0),
    momentum=(3.0, 1.0, 0.5),
    sigma=(0.9, 1.1, 1.3),
)

frame = source.frame(0.01)
print(frame.psi.shape)                 # (32, 32, 32)
print(frame.descriptor)
```

The 3D solver evolves

```text
ψ(x,y,z,t)
V(x,y,z,t)
|ψ|²
arg(ψ)
jx, jy, jz
energy density
```

using a unitary split-step Fourier propagator. The norm is recalculated for numerical safety after every step.

## Potential-driven sources

The important architectural shift is that “Schrödinger packet” is now one configuration of a general solver:

```python
from excitation.wavefunction_sources_v1 import PotentialWavefunctionSource

source = PotentialWavefunctionSource(
    dimensions=3,
    grid_shape=32,
    extent=16.0,
    potential="double_well",
    center=(-2.0, 0.0, 0.0),
    sigma=(0.7, 0.9, 0.9),
    potential_parameters={
        "axis": 0,
        "separation": 2.0,
        "height": 0.35,
    },
)
```

Changing `potential` changes the physical operation while preserving the same output contract.

## Analytic sources

The particle-in-a-box, rotor, spherical-harmonic, and hydrogen sources evolve exact eigenstate superpositions rather than using the FFT propagator. `hydrogen_superposition_3d` emits a complete continuous field; its default superposition is 1s + i·2p(z).

```python
source = create_wavefunction_source(
    "hydrogen_superposition_3d",
    grid_shape=40,
    states=[
        (1, 0, 0, 1.0),
        (2, 1, 0, 1.0j),
        (3, 2, 1, 0.35),
    ],
)
```

Each state tuple is `(n, l, m, complex_coefficient)`.

## Complete field contract

Every true wavefunction source returns a `WavefunctionFrame` containing:

```text
psi                    complex ndarray
probability            |psi|²
phase                  arg(psi)
probability_current     one array per spatial/angular axis
energy_density          local kinetic + potential energy
coordinates             one coordinate vector per axis
time, norm, dimension
descriptor              compact control-rate projection
metadata                model-specific physical values
```

The descriptor retains the original `energy`, `phase`, `probability`, and `structure` fields and adds `coherence`, `current`, position, spread, and momentum. Existing Hamiltonian mutation code can therefore consume the first four values without discarding access to the complete ψ field.

The descriptor phase is derived from neighboring relative phase coherence. A wavefunction's unobservable global phase is not used as a musical control.

## Mutator v2

```python
from hamiltonian.mutator_quantum_sources_v2 import HamiltonianMutator

mutator = HamiltonianMutator(
    amount=0.1,
    excitation_kind="schrodinger_packet_3d",
    source_parameters={"grid_shape": 32},
)

frame = mutator.source_frame(dt=0.01)       # complete ψ field
descriptor = mutator.source_descriptor(0.01) # compact projection
new_h = mutator.mutate_from_physics_source(old_h, dt=0.01)
```

Sources are allocated lazily. Selecting a one-dimensional model does not allocate any 3D arrays.

The old names remain available:

```text
audio
hydrogen_spectrum
hydrogen_orbital
schrodinger_packet
```

`hydrogen_orbital` preserves the original stochastic descriptor behavior. Select `hydrogen_orbital_field` for a continuous 3D orbital ψ.

## Musical projection principle

The complete field supports the established principle that ψ defines the instrument rather than its volume:

| Wavefunction quantity | Suggested operation |
| --- | --- |
| `|ψ|²` | Select excitation positions, grains, modes, or chamber nodes |
| relative phase | Complex quadrature and coupling orientation |
| probability current | Direction and circulation through resonator branches |
| energy density | Modal-family weighting without equal-tempered quantization |
| coherence | Global binding and feedback coherence |
| nodal structure | Grain clustering, articulation, and sparse excitation masks |
| position/spread | Spatial center and aperture rather than wandering pitch |

For Max/OSC, send descriptors, moments, slices, or modal projections at control rate. A complete 32³ complex array should remain local to Python and be projected before transmission.

## Grid sizes

| Grid | Intended use |
| --- | --- |
| 1D: 128–512 | Real-time control and high-resolution offline work |
| 2D: 48²–128² | Real-time fields, surfaces, and slices |
| 3D: 24³–32³ | Interactive/control-rate use |
| 3D: 48³–64³ | Slower control rates or offline rendering |

FFT cost and memory grow quickly in 3D. Begin with `32³`; increase only after measuring the intended update rate on the target machine.

## Validation

Run from the bundle root:

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

The tests cover 1D and 3D norm preservation, all seven numerical potentials, analytic sources, hydrogen interference, spherical coordinates, descriptor ranges, and reset behavior.
