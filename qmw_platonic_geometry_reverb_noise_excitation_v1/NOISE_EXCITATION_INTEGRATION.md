# Noise excitation integration

This directory is a fork of `qmw_platonic_geometry_reverb_v1_bundle`. The
source bundle remains unchanged.

The reviewed integration adds onset-sensitive broadband excitation before the
existing four-stage input diffuser. It retains the newer bundle's cascaded
geometry-morph smoothing, rotation smoothing, diffusion smoothing, and
geometry-depth smoothing.

Compared with the originally supplied updater, this fork uses a fast-minus-
slow envelope detector rather than a per-sample envelope derivative. Both
envelopes use time constants expressed in seconds and multiplied by the active
sample rate, keeping `onset_threshold` behavior comparable at 44.1, 48, 88.2,
and 96 kHz. Noise low-pass color is likewise calculated from a frequency in
hertz rather than a fixed per-sample coefficient.

The builder writes generated files back into this directory. Run:

```bash
env NUMBA_CACHE_DIR=/private/tmp/numba_cache \
  /Users/zlayton/miniconda3/envs/music/bin/python \
  build_qmw_platonic_geometry_reverb_v1.py
```

The generated GenExpr, controller, and README are covered by parity tests in
`../qmw_platonic_noise_excitation_update_v1/`.

Open `QMW_Platonic_Noise_Excitation_v1.maxpat` to audition the fork. Its Gen
codebox embeds this directory's generated DSP, and the six noise-excitation
message boxes feed the controller stored beside it. Regenerate that patch with:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  build_qmw_platonic_noise_excitation_patch_v1.py
```

## Max-clocked quantum engine

`QMW_Platonic_Noise_Excitation_v3.maxpat` preserves the existing v1 and v2
patches and adds a Max-owned external clock. The clock panel uses `qmetro`,
`OpenSoundControl`, and `udpsend 127.0.0.1 7402` to send
`/qmw/engine/tick <interval_ms>`. The default interval is 33.333 ms (about
30 Hz). Its CNMAT packet path sends the address/value list through `t b l`,
which loads `OpenSoundControl` before banging out the encoded UDP packet.

Start the workspace engine in external-clock mode:

```bash
cd /Users/zlayton/QuantumSonification

env NUMBA_CACHE_DIR=/private/tmp/numba_cache \
  /Users/zlayton/miniconda3/envs/music/bin/python \
  quantum_population_osc_v9_resonator.py \
  --clock-source external \
  --status-hz 0.5 \
  --disable-circuit-bridge-control
```

Then open v3 and enable **RUN EXTERNAL CLOCK**. The Python engine advances only
when Max sends a tick. If computation takes longer than the clock interval,
incoming ticks are coalesced into one newest pending step rather than queued.
Max audio therefore continues from the latest received quantum state without
waiting for Python.

The Bash status line reports measured `tick=...Hz`, total ticks received, and
ticks coalesced while Python was busy. Add `--quiet` only when this telemetry
is not needed. Port 7402 is the incoming control/tick port; visual OSC is sent
separately on 7401 and the density/Pauli stream is sent on 7400.

## Dual spectral noise fork

`QMW_Platonic_Noise_Excitation_v4.maxpat` adds two switchable interpretations
of spectral noise while leaving v1–v3 unchanged:

- Mode **0 QUANTUM** (the default) passes noise through eight resonant bands.
  Their gains follow the first eight `/qmw/density_field/magnitude` values and
  their frequencies follow the first eight Hamiltonian ratios from
  `/qmw/density_field/harmonics`.
- Mode **1 INPUT** measures an eight-band envelope from the incoming audio and
  transfers that spectral shape onto the noise.

The `amount` control crossfades between the original colored noise and the
selected spectral version. `Q`, `gain`, and `base Hz` tune the quantum filter
bank; the input-spectrum mode uses fixed octave-spaced crossover bands. Both
modes remain inside Gen at audio rate, while quantum targets are smoothed over
80 ms to avoid OSC-rate zippering.

Regenerate v4 with:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  build_qmw_platonic_dual_spectral_patch_v1.py
```

Max must still compile the GenExpr in the actual host environment. Start at a
low monitoring level, with `noise_floor 0` and modest `noise_amount`, because
the burst energizes every active feedback-delay node.

## Click-resistant / DC-safe fork

`QMW_Platonic_Noise_Excitation_v5.maxpat` preserves v4 and adds three layers
of protection against clicks:

- `attack ms` replaces the one-sample noise-onset jump with an asymmetric
  attack/release envelope. The default is 3 ms.
- `xfade ms` smooths both the spectral-mode switch and spectral-amount
  changes. The default is 40 ms.
- `DC block Hz` drives matched first-order DC blockers before the feedback
  network and at both stereo outputs. The default is 18 Hz.

If a sharp transient remains, first raise `attack ms` to 5–10 ms. If it occurs
only while switching QUANTUM/INPUT or changing spectral amount, raise
`xfade ms` to 80–150 ms. Keep `DC block Hz` near 12–25 Hz; raising it much
further removes audible bass rather than merely suppressing DC.

Regenerate v5 with:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  build_qmw_platonic_dc_safe_patch_v1.py
```
