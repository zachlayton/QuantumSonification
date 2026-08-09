# QMW Pauli MuBu Corpus Instrument v1

This is a parallel MuBu rendering of the Pauli statistical instrument. It does
not replace the Grainflow version.

## Open and audition

1. Open `QMW_Pauli_MuBu_Corpus_Instrument_v1.maxpat` in Max 9.
2. The patch commits a fallback quantum atlas automatically. Click
   `SEED+CAPTURE` for the explicit test wavetable, or update the shared
   `qmw_wavetable` and click `CAPTURE`.
3. Enable `ezdac~`. The grain-event metro starts automatically.

The patch targets the locally installed **MuBu For Max 1.10.7** package and its
`mc.mubu.granular~` external.

## Why the MuBu version is structurally different

Grainflow's streams behave like persistent granular voices. MuBu captures its
parameters when each grain is created, so this version treats a grain as a
discrete event in an evolving corpus:

```text
allowed Pauli occupation
        |
        +--> position in six-region quantum atlas
        +--> Zeeman resampling + grain-time FM
        +--> duration / position / level variation
        +--> one-hot outputgains to one of six MC mode channels
        +--> bang: instantiate grain
        |
        +--> append state and event to MuBu corpus
```

Two `mc.mubu.granular~ 6` engines read atlas A and B. The inactive atlas is
rewritten and the engines crossfade over 120 ms. The six MuBu output channels
remain mode-addressed until the final stereo mixdown.

## MuBu corpus

The embedded `imubu` view exposes three predefined tracks:

- `modes`: the six `(m_l, 2m_s, g, atlas position, mode)` definitions.
- `states`: time-tagged `N`, `M`, `Omega`, `S/k_B`, field, and six occupations.
- `grains`: time-tagged requested mode, position, resampling, duration, and
  level for every emitted grain.

`states` and `grains` are bounded ring tracks, so the instrument can run
continuously without unbounded memory growth. Double-click a track object or
use the `imubu` tabs to inspect the corpus during performance.

The embedded inspector uses fixed vertical bounds, redraws at 2 Hz, and follows
a rolling 30-second time window. This is deliberately independent of the full
rate at which the tracks receive data; changing the visual refresh does not
change the synthesis or corpus event timing. The `freeze view` toggle stops
display rendering entirely while the audio engine and corpus tracks continue.

## MuBu parameters used

- `position` and `positionvar` select and explore a quantum-mode atlas region.
- `duration` and `durationvar` control event scale.
- `resampling` carries the Zeeman displacement in cents.
- `resamplingvar` carries per-grain energy deviation.
- `level` and `levelvar` normalize occupations and expose stochastic energy.
- `reverse` becomes possible as exploration rises.
- `window` selects cosine, trapezoid, or sine grains.
- `filtermode`, `filterfreq`, and `filterq` expose MuBu's grain filter.
- `outputgains` is captured per grain as a one-hot six-channel mode address.
- `microtiming`, `cyclic`, `centered`, and `outputposition` are enabled.
- `resetoutputs 100` safely fades all currently sounding grains.

The **grain FM cents** control is sampled at grain creation. Each mode has a
different sub-audio modulation rate, and its instantaneous value is added to
that grain's resampling. This is event-rate parameter modulation, not an
audio-rate multiplier.

## Statistical layer

For `M` accessible modes and `N` particles:

```text
fermion:   Omega = choose(M, N)
boson:     Omega = choose(M + N - 1, N)
classical: Omega = M^N
S / k_B = log(Omega)
```

Fermions are sampled without replacement. Bosons and classical particles can
bunch. A closed fermionic shell has `Omega=1`; an overfilled shell has no
allowed state and emits no grains.

## Natural next MuBu integrations

The corpus boundary is intentional. It permits later additions without
rewriting the statistical instrument:

1. Run `mubu.process` with PiPo loudness, spectral, MFCC, or pitch descriptors
   over longer quantum-derived source material.
2. Add a marker track and use MuBu's synchronous/PSOLA granular mode for
   transition-aligned grains.
3. Navigate descriptor space with `mubu.knn`, `mubu.gmm`, or concatenative
   synthesis instead of selecting atlas positions directly.
4. Record gesture or field trajectories as additional time-tagged tracks and
   learn their relationship to state transitions with XMM/GMR tools.

The current version establishes the stable audio/event/corpus contract those
extensions need.

## Verification

```sh
python3 pauli_mubu_instrument_v1/build_qmw_pauli_mubu_instrument_v1.py
node pauli_mubu_instrument_v1/test_max_js_runtime.js
```

The generator validates object identifiers, inlet/outlet ranges, both MuBu
engines, all three corpus tracks, the dual-buffer audio path, and the stereo
output chain.
