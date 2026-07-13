# Geometry Acoustics Bridge v2

This bridge consumes a material-aware modal NPZ. It does not recalculate
frequency or decay from geometric eigenvalues.

Required arrays:

```text
frequencies_hz
decay_times_seconds
mode_weights
```

Optional arrays include `eigenvalues`, `eigenvectors`,
`angular_frequencies`, `damping_rates`, `mode_probabilities`, and
`mode_amplitudes`. The bridge multiplies material weights by normalized
quantum gains when quantum fields are present.

`decay_times_seconds` is an amplitude time constant: each mode uses
`exp(-time / decay_time)`. The corresponding reverberation time is exported as
`t60_seconds = log(1000) * decay_times_seconds`. This preserves very long rooms
without confusing an e-folding time with T60.

By default, modes begin with coherent cosine phase so modal energy is strongest
at the onset. `direct_gain` adds an excitation impulse at sample zero and
`tail_fade_seconds` removes truncation discontinuities. Set `phase_mode` to
`random` to restore a diffuse, beating onset.

```bash
python geometry_acoustics_bridge_v2.py quantum_eigenfield.npz \
  --output output/modal_ir \
  --sample-rate 48000 \
  --duration 6
```

Outputs are a stereo floating-point WAV, an NPZ containing the IR and modal
fields, and a JSON descriptor file.
