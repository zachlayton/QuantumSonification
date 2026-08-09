# QMW Living Spectral PFFT v1

This Max 9 prototype applies the living eigenfield revision history as a
stochastic magnitude mask inside `pfft~`.

Open:

```text
max/QMW_Living_Spectral_PFFT_v1.maxpat
```

Drop an audio file into `playlist~`, start DSP, and run the living OSC publisher
on port 7460. The parent patch receives the flattened history, and
`qmw_living_spectral_mask_v1.js` converts it into the 2,048-bin buffer used by:

```text
udpreceive 7460 cnmat
-> OpenSoundControl
-> OSC-route /living
-> OSC-route /spectral /publication
-> OSC-route /history /playback
```

This follows the repository's CNMAT OSC convention and preserves OSC address
hierarchy while each `OSC-route` strips its matched prefix.

```text
pfft~ qmw_living_spectral_mask_pfft_v1 4096 4
```

With FFT size 4,096 and overlap 4, the hop size is 1,024 samples and the
`pfft~` I/O latency is 3,072 samples. Inside the spectral patch:

```text
fftin~ 1
-> cartopol~
-> magnitude * index~ qmw_living_spectral_mask
-> poltocar~
-> fftout~ 1
```

`fftin~` supplies real, imaginary, and current half-spectrum bin-index signals.
The mask is smoothed before multiplication. Every bin stochastically selects a
revision from the effective blur range; the newest spectral transient narrows
that range toward one frame so attacks remain articulate.

The mask buffer initializes to unity so the patch passes audio before the first
living revision. `TEST MASK` writes a visible diagnostic curve and
`PASSTHROUGH` restores unity. The generated modal mask retains a floor of 0.02
outside the published eigenfrequency range; this prevents a low-frequency
modal set from appearing completely blank across the full 2,048-bin display.

The original audio phase from `cartopol~` passes directly to `poltocar~`.
Eigenfield phase deltas are not audio STFT phase and are never injected into
that signal path. A later time-stretch/freeze phase-vocoder processor should
derive audio phase deviations with `framedelta~` and reconstruct running audio
phase with `frameaccum~ 1`.

FFTease provides stronger native paths for several related operations. In
particular, use `fftz.bthresher~` for per-bin persistence, `fftz.resent~` or
`fftz.residency_buffer~` for spectral memory, and `fftz.reanimator~` for
mosaicing. These externals perform their own FFT and belong beside this
processor as parallel voices, not inside its `pfft~` subpatch. See
`docs/fftease_living_spectral_implementation_notes_v1.md`.

Regenerate the patches after editing the builder:

```bash
python max/build_qmw_living_spectral_pfft_v1.py
```
