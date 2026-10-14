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

Max must still compile the GenExpr in the actual host environment. Start at a
low monitoring level, with `noise_floor 0` and modest `noise_amount`, because
the burst energizes every active feedback-delay node.
