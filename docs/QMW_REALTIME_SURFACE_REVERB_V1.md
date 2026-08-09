# QMW Realtime Implicit Surface Reverb v1

This module keeps geometry deformation inside Max/Gen~. It does not build a
mesh, solve a Laplacian, render a WAV, or reload a convolution buffer during
performance.

The audio engine extends the existing DC-safe Platonic twenty-node feedback
delay network with twenty smoothed implicit-field probes. The controller
evaluates algebraic and triply-periodic minimal-surface equations at those
probes and sends normalized field values to the corresponding Gen~ nodes.

Included equation families:

- algebraic: sphere, torus, tanglecube, heart;
- minimal/periodic: gyroid, Schwarz P, Schwarz D, Neovius.

The A/B menus select two equations. `EQUATION MORPH` interpolates their scalar
fields before normalization, allowing topology and resonant behavior to move
continuously. `FIELD DEFORMATION` controls the depth of the field contribution
to the delay ratios. `ANIMATE` rotates and phase-shifts the probe field at
20 Hz while Gen~ smooths the resulting control stream.

The rack receives `qmw_spectral_L/R`, emits stereo audio directly, and listens
to `/qmw/density_field` OSC for quantum spectral excitation.

An external 20% dry safety path is mixed with the 85% Gen~ output. `GEN WET
L/R` meters show the parametric reverb alone, while `OUT L/R` shows the final
mixed signal. This prevents a Gen compilation or initialization problem from
silencing otherwise valid input and makes the two stages independently
diagnosable.

## Emergent Geometry MLX

`emergent_geometry_v1_osc` remains useful as a slower morphology layer. Its
reaction-diffusion descriptors should be mapped to the real-time rack's morph,
deformation, diffusion, absorption, and topology parameters. MLX field/mesh
export should remain outside the audio thread. A later bridge can send those
descriptors over OSC without generating a new IR.

The v1 rack includes that descriptor bridge on UDP 7431. Turn on `MLX LINK`
after starting `emergent_geometry_osc_v1.py`. Labyrinth, cellular, and coral
presets select related implicit-surface pairs; variance, curvature, entropy,
anisotropy, and growth velocity continuously deform the Gen~ network.

The conductor can launch a deliberately reduced 96×96, 10 Hz, two-iteration
configuration suitable for trying this during a performance session:

```bash
python quantumsonification_conductor.py --with-emergent-geometry
```

The field size, update rate, and iteration count remain adjustable with
`--emergent-size`, `--emergent-rate`, and `--emergent-iterations`.

## Rebuild

```bash
python max/build_qmw_realtime_surface_reverb_v1.py
```
