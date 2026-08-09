# Bohm--Bell configuration guidance v1

This module separates the four-qubit configuration ontology from the older
one-dimensional projected pilot field.

- `four_qubit_configuration_guidance_v1.py` implements the Bell jump law from
  the Hamiltonian probability current, with an explicit computational-Z
  beable basis and no renderer noise.
- `bell_bohm_grw_experiment_v1.py` unfolds CHSH measurement rotations over
  microsteps, validates the quantum Bell correlation and no-signaling
  marginals, and supplies an accelerated Z-localization/dephasing analogue for
  comparison.
- `live_bohm_guidance_v1.py` gives `DensityMatrixEngine` one authoritative
  computational-Z configuration. It unfolds live circuit unitaries through
  Hermitian generators, applies the tested Bell jump rates during every
  microstep, and records causal event families without renderer noise.
- `density/open_system_trajectory_v1.py` supplies local Kraus-outcome
  trajectories for dephasing, amplitude damping, and depolarizing channels.
  Their trajectory averages reconstruct the corresponding density channel.

The live event families are deliberately separate:

- `circuit_generated_current`
- `hamiltonian_current`
- `environmental_jump`
- `explicit_measurement`
- `spontaneous_localization`

GRW retains the actual configuration and changes the future guidance field.
Explicit measurement repairs the configuration only when its post-measurement
branch has zero support at the previous configuration. Environmental Kraus
branches use their configuration-space transition law directly.

The engine constructor remains backwards compatible. Optional controls are:

```python
from density.density_matrix_engine_4q import DensityMatrixEngine
from guidance.live_bohm_guidance_v1 import BohmGuidanceConfig

engine = DensityMatrixEngine(
    bohm_config=BohmGuidanceConfig(
        gate_duration_seconds=0.125,
        gate_microsteps=24,
        hamiltonian_microsteps=8,
        environment_trajectory_enabled=True,
    )
)
```

Environmental trajectories default to disabled so existing performances do
not silently acquire a dissipative process that was previously commented out.
They can be activated with `/quantum/bohm/environment/enabled 1`. Other live
controls are `/quantum/bohm/enabled`, `/quantum/bohm/gate_duration`, and
`/quantum/bohm/gate_microsteps`.

## Spatial Bohm engine

The continuous spatial engine is now implemented independently of the
four-qubit configuration ontology:

- `pilot_wave_field_nd.py`: 1D/2D/3D current, velocity, quantum potential,
  node masks, interpolation, Born sampling, trajectory integration, and
  boundary rules.
- `schrodinger_pilot_1d_v2.py`: physical 1D packets and oscillator states.
- `schrodinger_pilot_2d_v1.py`: Gaussian, plane-wave, vortex, oscillator, and
  double-slit experiments.
- `two_particle_pilot_1d_v1.py`: joint `(x1,x2)` configuration space for a
  direct nonlocal-guidance experiment.
- `schrodinger_pilot_3d_v1.py`: free packets plus complex spherical-harmonic
  and hydrogenic states.

See `SPATIAL_BOHM_ENGINE_V1.md` for the model contract and runnable commands.

Run from the repository root:

```bash
python -m unittest guidance.test_four_qubit_guidance_v1 \
  guidance.test_live_bohm_guidance_v1 \
  guidance.test_bell_bohm_grw_experiment_v1 \
  density.test_open_system_trajectory_v1 \
  density.test_live_bohm_engine_v1

python -m guidance.bell_bohm_grw_experiment_v1 --trials 20000
python -m guidance.bell_bohm_grw_experiment_v1 \
  --trials 20000 --grw-visibility 0
```

`grw_visibility` is deliberately labeled as a finite-dimensional,
musically accelerated localization analogue. It does not claim to reproduce
the dimensional parameters or event ontology of spatial GRW.
