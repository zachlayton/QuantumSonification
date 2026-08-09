# ENNEADS RAVE corpus

This corpus is derived from seven ENNEADS 48 kHz/24-bit stereo masters and four
component stems for Track 05. The preparation script creates 44.1 kHz/16-bit
mono training copies and never modifies the source masters.

`07_05_fullmix_48k24.wav` is intentionally excluded because the corresponding
mastered Track 05 full mix is already included. Including both would duplicate
and overweight that composition.

The initial corpus contains 70.11 minutes of source audio:

- Seven mastered full mixes: approximately 46 minutes
- Bass, drums, piano, and distorted-piano stems: approximately 24 minutes

The preprocessed database contains 1,410 non-overlapping windows of 131,072
samples, representing 69 minutes 47.8 seconds. A few trailing seconds from each
source file are intentionally omitted when they do not fill a complete window.

## Rebuild

```bash
zsh rave_training/enneads/prepare_corpus.zsh
```

## RAVE environment

The local `music` Conda environment currently contains `acids-rave` 2.1.16 and
PyTorch 2.5.0. PyTorch reports that MPS is built but unavailable on this host.
Its TorchAudio binary is also ABI-incompatible with the installed Torch build.
The shared environment has not been modified; production training should run
in a clean environment on a CUDA-capable Linux machine.

