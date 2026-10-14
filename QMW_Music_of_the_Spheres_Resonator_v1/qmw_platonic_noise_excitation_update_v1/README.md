# QMW Platonic Noise Excitation Update v1

Adds onset-sensitive broadband excitation to a **fork** of Platonic Geometry
Reverb v1. Existing bundles should remain unchanged.

The integrated workspace fork is:

`../qmw_platonic_geometry_reverb_noise_excitation_v1/`

## Safety properties

- requires an explicit target directory;
- preflights every source anchor before writing anything;
- creates `.pre_noise_excitation_v1` backups inside the fork;
- can be run repeatedly without duplicating the update;
- preserves the newer cascaded geometry-morph and slew state;
- makes the forked generator regenerate its files in place;
- uses a fast-minus-slow envelope onset detector whose threshold remains
  comparable across sample rates.

Run a non-writing preflight from the QMW project directory:

```bash
python qmw_platonic_noise_excitation_update_v1/update_qmw_platonic_noise_excitation_v1.py \
  qmw_platonic_geometry_reverb_noise_excitation_v1 --dry-run
```

Apply the update:

```bash
python qmw_platonic_noise_excitation_update_v1/update_qmw_platonic_noise_excitation_v1.py \
  qmw_platonic_geometry_reverb_noise_excitation_v1
```

Suggested initial messages:

```text
noise_amount 0.22
noise_decay_ms 22
onset_threshold 0.012
onset_sensitivity 10
noise_color 0.72
noise_floor 0
```

The burst is injected before the four-stage allpass diffuser, energizing the
complete morphing FDN rather than adding output-layer noise. `noise_floor`
remains zero by default so quiet input does not produce a perpetual noise bed.
