# Wavefunction cloud sonification v1

This renderer sonifies the evolving 3D probability cloud itself. It does not
reduce the field to four held branch amplitudes.

## Grain mapping

| Wavefunction value | Grain operation |
| --- | --- |
| `|psi|^2` | Importance-sampling probability and amplitude |
| `arg(psi)` | Initial oscillator phase |
| `(x, y, z)` | Spatial position |
| Probability current | Directional drift, pan, and particulate content |
| Local energy density | Exponential frequency position |
| Norm, center, spread | Frame integrity and Processing moment ellipsoid |

The adapter uses deterministic stratified probability-mass sampling. The OSC
demo now defaults to an adaptive 0--12 grains per frame. Total-variation
distance between consecutive probability fields measures redistributed mass;
probability current contributes a smaller transport term. A smoothed mixture
drives event density while every grain retains its 5 ms decay. The default
renderer does not invent stochastic event times. An explicitly nonphysical
`--renderer-poisson` diagnostic is available for comparison, but it is not a
wavefunction or GRW observable. In ordinary cloud mode, fast transport,
interference, or scattering therefore produces denser sound than a nearly
stationary cloud.

Every OSC grain packet contains:

```text
/qmw/wavefunction/cloud/grain
    frame_id grain_id x y z amplitude phase
    current_x current_y current_z energy decay_ms
```

The frame packet contains time, grain count, norm, center, and spread. The
same packets are sent to Max on the dedicated cloud port 7480, Processing on
7401, and SuperCollider on 57120. Port 7400 remains owned by the main
density/GRW engine; keeping one Max `udpreceive` per UDP port prevents the two
standalone renderers from starving each other.

## Run

1. Run `processing/QMW_WavefunctionCloud3D`.
2. Open `max/QMW_Wavefunction_Cloud_Grains_v1.maxpat`, or evaluate
   `supercollider/qmw_wavefunction_cloud_grains_v1.scd`.
3. Start the stream:

```bash
python examples/wavefunction_cloud_osc_v1.py \
  --source schrodinger_packet_3d \
  --grid 32 \
  --fps 30 \
  --decay-ms 5
```

Use `--min-grains`, `--max-grains`, `--rate-sensitivity`, and
`--current-weight` to shape the adaptive response. Add `--fixed-rate --grains
16` to restore the original fixed density. Use `--amplitude` to change
grain level without changing probability selection. Keeping duration at 5 ms
preserves the requested micro-event articulation.

The older GRW persistent sine bed now defaults to zero gain in both Max and
SuperCollider. GRW remains an event/reconfiguration layer over this cloud.

## Wavefunction instruments

The same OSC/grain renderer accepts all thirteen canonical instruments:
`schrodinger_packet_3d`, `harmonic_oscillator`, `harmonic_oscillator_3d`,
`coherent_state`, `squeezed_state`, `particle_in_box`, `quantum_rotor`,
`double_well`, `barrier_scattering`, `periodic_lattice`,
`hydrogen_orbital_field`, `hydrogen_superposition_3d`, and
`spherical_harmonic`. The CLI's single `--grid` value is translated to a
Cartesian grid, a one-dimensional point count, or a theta/phi angular grid as
required by the selected source.

## Genuine GRW wavefunction mode

`--grw` changes the physical source, not merely the renderer timing. The
wrapper evolves psi to every exact exponentially distributed jump time,
samples a localization center from the GRW center distribution, applies

```text
L_x(q) proportional to exp(-|q-x|^2 / (4 r_C^2))
```

to the complex field, and renormalizes before evolution continues. OSC is
silent between jumps. At a jump, grain positions and amplitudes are sampled
from `abs(Delta |psi|^2)`, current comes from the pre/post current difference,
phase and energy come from the post-jump field, and burst size follows the
total-variation distance between the pre/post probability measures.

```bash
python examples/wavefunction_cloud_osc_v1.py \
  --source schrodinger_packet_3d \
  --grid 32 \
  --fps 60 \
  --grw \
  --grw-rate 1.0 \
  --grw-width 0.75 \
  --grw-seed 23 \
  --decay-ms 5
```

The v1 wrapper supports mutable split-step sources: free packets, harmonic
oscillators, coherent and squeezed states, double wells, barrier scattering,
and periodic lattices. Closed-form analytic sources are rejected because they
would reconstruct their uncollapsed formula on the following frame; they need
a numerical continuation model before a GRW jump can persist honestly.
