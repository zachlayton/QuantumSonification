# Spatial Bohm pilot: implemented v1 architecture

Implementation status: the dimension-independent core and the 1D, 2D,
two-particle, and 3D layers described below are now implemented and tested.
See `SPATIAL_BOHM_ENGINE_V1.md` for runnable examples and validation commands.

## Existing systems must remain distinct

`field/bohmian_pilot.py` constructs a periodic synthetic field from 16
amplitudes and phases. Its damping, mobility, `tanh` velocity clipping, and
field smoothing make it useful as a sonification projection, but not as a
literal Bohmian law for the four-qubit configuration space or a physical
particle.

`excitation/schrodinger_packet.py` already evolves a normalized physical 1D
wavefunction with a spectral kinetic propagator. It is the correct starting
point for spatial guidance.

The project should keep three explicit domains:

1. `guidance/four_qubit_configuration_guidance_v1.py`: discrete configuration
   jumps on the 16-state computational-Z graph.
2. A new `PilotWaveFieldND`: continuous particle guidance in 1D/2D/3D space.
3. `field/bohmian_pilot.py`: a labeled synthetic projection/renderer feature.

## Dimension-independent physics core

The implemented core stores axis arrays, grid spacing, `psi`, mass, hbar, time,
and boundary conditions. It computes directly from the complex field:

```
density = abs(psi)**2
current[d] = (hbar / mass[d]) * imag(conj(psi) * gradient(psi)[d])
velocity[d] = current[d] / density
quantum_potential = -(hbar**2 / (2*m)) * laplacian(abs(psi)) / abs(psi)
```

Phase should not be unwrapped to calculate velocity; `conj(psi)*grad(psi)` is
more stable at branch cuts. Near nodes, the engine should report a validity
mask and use a declared numerical floor. It must not add random noise,
inertia, damping, or musical smoothing to the physical trajectory.

Trajectory integration should interpolate the vector field at the actual
position and use midpoint or RK4 integration. Boundary behavior (`periodic`,
`reflecting`, or `absorbing`) is part of the physical configuration, not a
renderer option. Ensembles are sampled from `abs(psi)**2` for equivariance
tests; a single selected member can later drive sonification.

Suggested files:

```
guidance/
  pilot_wave_field_nd.py
  schrodinger_pilot_1d_v2.py
  schrodinger_pilot_2d_v1.py
  two_particle_pilot_1d_v1.py
  schrodinger_pilot_3d_v1.py
  test_pilot_wave_field_nd.py
  test_schrodinger_pilot_2d_v1.py
```

## Build 2D first

The first 2D model should be one particle in physical `(x,y)` space with a
split-step Fourier propagator. Initial experiments, in validation order:

1. Plane wave: spatially constant velocity equal to `hbar*k/m`.
2. Free Gaussian: norm conservation and trajectory-ensemble equivariance.
3. Harmonic oscillator: bounded evolution and energy stability.
4. Vortex state: circulation and phase winding around a node.
5. Double slit: current deflection, node avoidance, and final Born histogram.

The two-particle 1D model uses a 2D grid too, but its coordinates mean
`(x1,x2)` configuration space, not a physical plane. It should therefore be a
separate wrapper with `coordinate_semantics="two_particle_1d"`; that is the
most direct later demonstration of joint, nonlocal Bohmian guidance.

## Extend the tested core to 3D

The 3D wrapper changes grid construction, interpolation, gradient/Laplacian,
and propagation shape, not the guidance law. Start at `64^3`; a single
complex128 field is about 4 MiB, while currents, potentials, FFT work arrays,
and history multiply that footprint. Make resolution and retained history
explicit before moving toward `128^3`.

Initial 3D states should include a free Gaussian and complex spherical
harmonics/hydrogenic superpositions. Real stationary orbitals have constant
phase and zero Bohmian velocity, so audible orbital circulation must come from
complex `m != 0` states, superpositions, packets, or external driving.

Only after Cartesian tests pass should trajectory velocity be decomposed into
radial, polar, and azimuthal components for chamber/ambisonic mapping.

## Validation gates

Before any sonification adapter is connected, require:

- wavefunction norm conservation for unitary propagation;
- continuity-equation residual convergence under grid refinement;
- plane-wave velocity accuracy;
- Born-distributed trajectory equivariance;
- vortex circulation/winding consistency;
- deterministic seeded ensemble sampling;
- 1D/2D agreement for separable fields;
- 2D/3D agreement for fields constant along the extra dimension.

GRW remains a separately tested event family. A later spatial `guided_grw`
experiment can retain the actual position, multiply `psi` by a Born-sampled
Gaussian localization operator, renormalize, recompute the current, and let
the trajectory continue. That hybrid should be added only after both the
spatial guidance and spatial GRW localization tests pass independently.
