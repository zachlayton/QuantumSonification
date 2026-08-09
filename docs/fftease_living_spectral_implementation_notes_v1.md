# FFTease and Living Spectral Geometry

The installed FFTease 3.0 package contains 38 spectral externals and includes
native Apple Silicon and Intel binaries. It should complement the custom
`pfft~` processor, not be placed inside it: FFTease externals perform their own
FFT analysis/resynthesis.

## Highest-value implementation paths

### Spectral memory: `fftz.residency_buffer~` and `fftz.resent~`

`fftz.residency_buffer~` records an audio analysis into a named Max buffer and
resynthesizes it with independent speed and position signals. Multiple objects
can share the same recorded spectral buffer. This is the strongest ready-made
foundation for multi-frame freeze, scrubbing, slow playback, and parallel
voices.

The named buffer contains FFTease analysis data, not time-domain audio. It must
not be played through `groove~` or another ordinary audio-buffer reader.

`fftz.resent~` extends the same model with independent speed and phase control
for every FFT bin. Its messages include:

```text
bin bin_number speed
setspeed value
setphase value
setspeed_and_phase speed phase
randspeed minimum maximum
randphase minimum maximum
linespeed start_bin start_speed end_bin end_speed
linephase start_bin start_phase end_bin end_phase
```

This is the closest native implementation of the paper's stochastic
multi-frame blur. The living `blur_width`, `transition`, and `freeze` controls
can generate `resent~` speed/phase distributions while FFTease owns audio
phase continuity.

### Per-bin persistence: `fftz.bthresher~`, `fftz.thresher~`, and `fftz.pileup~`

`fftz.thresher~` holds low-energy bins. Damping `1.0` produces an infinite
freeze; lower damping creates a spectral tail.

`fftz.bthresher~` exposes damping and threshold for each bin and accepts
triplets:

```text
bin_number damping threshold
```

It can also dump and restore its complete state. The living eigenfield mask can
therefore map directly to per-bin threshold/damping values:

```text
mode magnitude  -> inverse hold threshold
decay_seconds   -> damping near 0..1
transient       -> global release from held state
freeze          -> infinite-hold policy
```

`fftz.pileup~` accumulates amplitude/phase pairs until stronger information
arrives. It is musically useful for melody-to-harmony and persistent modal
fields, but offers less external per-bin control than `bthresher~`.

### Spectral mosaicing: `fftz.reanimator~`

`fftz.reanimator~` analyzes a texture and replaces each driver frame with the
closest stored texture frame. This directly implements the paper's mosaicing
or spectral-reanimation proposal. Living spectral transient can control
freeze-and-march behavior, thresholds, and the rate at which the driver is
allowed to select new frames.

### Eigenfrequency tuning: `fftz.pvtuner~`

`fftz.pvtuner~` accepts a sorted list of arbitrary frequencies and resynthesizes
input energy on that scale. Sending the current living `frequencies_hz` list is
a direct, low-translation mapping from geometric eigenvalues to audible modal
tuning. Its scale-interpolation mode can smooth revision changes.

### Spectral events: `fftz.pvgrain~`

`fftz.pvgrain~` emits pitch/amplitude control lists rather than processed
audio. It is a natural bridge between live audio analysis and the existing
GrainFlow/event scheduler. Living mode probabilities can gate its event
probability; spectral transient can control grains per frame.

## Transform and composition objects

| Object | Useful living-spectral role |
| --- | --- |
| `fftz.schmear~` | Convolves the magnitude spectrum with a supplied kernel; direct spectral blur. |
| `fftz.leaker~` | Selects bins from two sources with ordered or random sieves; stochastic crossfade. |
| `fftz.morphine~` | Morphs two spectra with a controllable transition curve. |
| `fftz.ether~` | Chooses stronger or weaker corresponding bins from two sources. |
| `fftz.vacancy~` | Threshold-based two-source compositing with optional phase selection. |
| `fftz.loopsea~` | Gives every bin its own loop length, speed, and transposition. |
| `fftz.dentist~` | Retains a selected set of partials; mode occupancy becomes a bin set. |
| `fftz.pvwarpb~` | Reads a frequency-warp function from a Max buffer; topology can become a warp field. |
| `fftz.disarrain~` | Interpolated bin permutations; useful for operator-order or noncommutative states. |
| `fftz.cavoc27~` | Captures input spectra and evolves them with a 27-rule cellular automaton, with freeze and interpolation. |
| `fftz.enrich~` | Oscillator-bank resynthesis using an arbitrary waveform buffer. |
| `fftz.pvcompand~` | Controls spectral peakiness or whitening from entropy/coherence. |
| `fftz.pvharm~` | Two transposed oscillator-bank voices for quantum-weighted harmonic branches. |

## Recommended architecture

```text
LivingSpectralGeometry
  -> revision history + eigenfrequency/magnitude/decay/transient OSC
  -> Max control adapter
       -> custom pfft~ mask processor      exact external eigenfield mask
       -> fftz.bthresher~                  per-bin persistence/freeze
       -> fftz.resent~                     spectral memory and bin motion
       -> fftz.pvtuner~                    eigenfrequency quantization
       -> fftz.reanimator~                 corpus mosaicing
       -> fftz.pvgrain~ -> GrainFlow       event extraction/resynthesis
```

The custom `pfft~` path remains important because none of the surveyed FFTease
objects accepts the living revision-by-mode matrix as a general external
magnitude plane. FFTease should own the algorithms it already implements well,
while the custom path remains the exact matrix/mask renderer and a transparent
reference implementation.

## Phase and FFT boundaries

- Eigenfield phase remains control-domain data unless an explicit audio mapping
  is defined.
- `fftz.resent~`, `fftz.residency~`, and related objects should own the audio
  phase of the spectral memory they capture.
- `fftz.swinger~` swaps phase between two audio analyses; it does not accept an
  arbitrary eigenfield phase plane.
- Do not wrap an FFTease external inside `pfft~`; that would create nested FFT
  systems and unrelated frame clocks.
- Match `@fftsize` and `@overlap` across parallel FFTease processors when
  crossfading between them. FFTease defaults to FFT 1024 and overlap 8, whereas
  the current custom patch uses FFT 4096 and overlap 4.
- Larger FFTs improve frequency resolution and morph smoothness but increase
  latency and smear attacks. Living transient should select or crossfade
  processing behavior, not reconfigure FFT size while DSP is running.

## Build order

1. Keep the custom `pfft~` mask processor as the working reference.
2. Add `fftz.bthresher~` as the first FFTease voice because its per-bin triplet
   control maps cleanly to the exported history.
3. Add a shared `fftz.residency_buffer~` capture plus two readers for
   multi-frame freeze and time displacement.
4. Add `fftz.pvtuner~` using the published eigenfrequency list.
5. Build `fftz.reanimator~` and `fftz.pvgrain~` as separate composition voices,
   not as mandatory stages in the main audio chain.
