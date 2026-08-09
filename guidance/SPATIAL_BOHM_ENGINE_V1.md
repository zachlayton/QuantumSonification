# Spatial Bohm engine v1

This package implements continuous Bohmian particle trajectories separately
from both the 16-state Bohm--Bell configuration engine and the older synthetic
`field.BohmianPilot1D` renderer projection.

## Physics core

`PilotWaveFieldND` accepts a normalized complex Cartesian field in one, two,
or three dimensions. It computes

```text
rho = |psi|^2
J_d = (hbar / m_d) Im(conj(psi) partial_d psi)
v_d = J_d / rho
Q = -(hbar^2 / 2m) laplacian(|psi|) / |psi|
```

Velocity uses the complex derivative directly. Phase is never unwrapped for
guidance. Grid points below `node_density_floor` are marked invalid and report
zero numerical velocity; the mask remains available to the caller. The engine
does not add noise, damping, inertia, smoothing, or velocity clipping.

Uniform-grid interpolation is multilinear. Trajectories use midpoint or RK4
integration with explicit `periodic`, `reflecting`, or `absorbing` boundary
rules. Seeded ensembles are sampled from `|psi|^2`.

## Models

- `SchrodingerPilot1D`: free Gaussian packets and the harmonic ground state,
  including quantum potential and synchronized trajectory ensembles.
- `SchrodingerPilot2D`: commensurate plane waves, free Gaussians, quantized
  vortices, harmonic oscillator states, an explicit slit-barrier potential,
  and an emerging double-slit state.
- `TwoParticlePilot1D`: a joint `(x1,x2)` configuration-space field. Its
  entangled phase preset makes particle-one velocity depend explicitly on the
  simultaneous particle-two coordinate.
- `SchrodingerPilot3D`: free Gaussian propagation, complex spherical-harmonic
  shells, and exact-time hydrogenic superpositions. Real stationary orbitals
  give zero velocity; `m != 0` states give azimuthal circulation.

All numerical propagators use periodic split-step Fourier evolution in natural
units by default while retaining explicit `mass` and `hbar` values.

## Quick experiments

```bash
python -m guidance.spatial_bohm_experiments_v1 1d_gaussian
python -m guidance.spatial_bohm_experiments_v1 2d_vortex
python -m guidance.spatial_bohm_experiments_v1 2d_double_slit --steps 100 --dt 0.01
python -m guidance.spatial_bohm_experiments_v1 two_particle_nonlocal
python -m guidance.spatial_bohm_experiments_v1 3d_hydrogen_m1
```

## Validation

```bash
python -m unittest \
  guidance.test_pilot_wave_field_nd \
  guidance.test_schrodinger_pilot_1d_v2 \
  guidance.test_schrodinger_pilot_2d_v1 \
  guidance.test_two_particle_pilot_1d_v1 \
  guidance.test_schrodinger_pilot_3d_v1
```

The tests cover plane-wave velocity, node validity, deterministic Born
sampling, boundary behavior, continuity residual, dimensional agreement,
one- and two-dimensional equivariance, oscillator stability, vortex winding
and circulation, double-slit fringes, nonlocal configuration dependence, real
orbital stationarity, and complex hydrogenic circulation.

No GRW localization or sonification mapping is part of this module. Those are
later adapters and event families, after the independent spatial tests remain
green.

