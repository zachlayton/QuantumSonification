# Living Spectral Geometry v1

`living_spectral_geometry_v1.py` turns the validated one-shot surface pipeline
into a persistent, event-driven system.

```text
developmental surface
→ spectral operator
→ tracked eigensystem
→ surface material
→ quantum weighting
→ timing snapshot
→ modal IR
→ atomic state publication
```

## Command line

```bash
python living_spectral_geometry_v1.py surface.obj \
  --output output/living_surface \
  --model elastic_shell \
  --modes 32
```

Each accepted update creates a versioned `state_XXXXXX` directory. The file
`current_state.json` is replaced atomically and contains the current IR path,
bundle path, descriptors, material model, and revision. Max can watch this
file and crossfade to the new `ir_wav` only after publication.

Each revision also exports `spectral_history.npz`, a bounded, mode-aligned
history intended for spectral resynthesis and masking. The default depth is
eight accepted revisions and can be changed with
`LivingSpectralConfig.spectral_history_depth`.

```text
revisions             [frames]
magnitudes            [frames, modes]
phases                [frames, modes]
phase_deltas           [frames, modes]
frequencies_hz         [frames, modes]
decay_seconds          [frames, modes]
magnitude_transients   [frames]
phase_transients       [frames]
transients             [frames]
phase_domain           "complex_eigenfield_mode"
```

Magnitude transient is half the L1 distance between consecutive normalized
mode-magnitude distributions. Phase transient is the current-magnitude-
weighted mean wrapped phase change, normalized by pi. The combined transient
is `0.75 * magnitude + 0.25 * phase`, clipped to `[0, 1]`.

The stored phases are complex eigenfield-mode phases. They are control-domain
values, not STFT phase-vocoder phases. An audio processor may use them to
control masking, timing, or spatialization, but must define an explicit mapping
before applying them to audio FFT phase.

## Persistent API

```python
with LivingSpectralGeometry(vertices, faces, output_dir) as living:
    initial = living.recompute_now()
    living.update_material(model="elastic_shell", bending_stiffness=0.04)
    updated = living.wait(timeout=10.0)
```

Supported typed events are:

- `GEOMETRY`: vertices/faces or a height field;
- `MATERIAL`: material parameters and optional vertex fields;
- `QUANTUM`: a new density matrix;
- `MEASUREMENT`: a post-measurement density matrix and outcome metadata;
- `RECALCULATE`: publish a fresh downstream state.

Rapid asynchronous mutations are debounced. A completed computation is
published only if its revision is still current. Eigenmodes are matched to the
previous state using maximum absolute eigenvector overlap, then sign-aligned,
so downstream mode identities remain stable through crossings where possible.
