# QMW Pauli Statistical Grainflow v1

**The Energy Shell** connects the quantum wavetable system to the installed
Grainflow 2.1.2 package through a six-mode statistical scheduler.

## Parameter-field v2

`QMW_Pauli_Parameter_Field_Grainflow_v2.maxpat` is the direct continuation of
the eight-voice parameter-buffer study. It expands the Pauli renderer into 24
stable slots:

```text
slot = stream * 4 + grain
6 streams * 4 grains = 24 voices
```

Three 25-sample buffers hold 24 voice values plus an endpoint:

```text
qmw_pauli_rates    energy-shell position and within-stream deviation
qmw_pauli_delays   stream/grain phase as source traversal time
qmw_pauli_windows  stable stream/grain window offsets
```

Occupation and transition strength determine a separate 24-channel amplitude
signal. Fermionic overfill produces an empty amplitude field, preserving the
exclusion rule rather than silently reducing particle number. Bosonic and
classical configurations allow repeated occupation.

Mode 1 assigns table slot `i` to voice `i`. Mode 2 samples the same fields
randomly, while entropy independently controls rate, delay, and window-offset
random depth. The original atlas-based v1 remains available for comparison.

## Open

1. Generate the patch if needed:
   `python3 pauli_statistical_grainflow_v1/build_qmw_pauli_statistical_grainflow_v1.py`
2. Open `QMW_Pauli_Statistical_Grainflow_v1.maxpat` in Max 9.
3. Enable `ezdac~`.

The patch captures the globally named `qmw_wavetable` buffer used by the QMW
wavetable generators. If it is empty, the first atlas commit uses a local
fallback without overwriting the shared buffer. `SEED+CAPTURE` explicitly
writes a test table when a standalone audition is wanted.

## Architecture

```text
qmw_wavetable (256 samples)
        |
        v
six-region atlas A/B (98,304 samples each)
        |
        v
two crossfaded grainflow.streams~ banks
        |
        v
24 preserved MC grain channels -> stereo mixdown
```

Each atlas contains six 16,384-sample regions, one for each complete 2p state
address. The renderer alternates between atlas A and B. A Grainflow bank never
reads the buffer being written; commits crossfade over 120 ms.

Each bank is instantiated as:

```max
grainflow.streams~ 6 4 qmw_pauli_atlas_A
```

Streams are quantum modes. Grains are scheduled events, never particle labels.

## Statistical scheduler

The energy shell selects modes using their perceptual strong-field factors
`(-2, 0, -1, +1, 0, +2)`. For `M` accessible modes and `N` particles:

```text
fermion:   Omega = choose(M, N)
boson:     Omega = choose(M + N - 1, N)
classical: Omega = M^N
S / k_B = log(Omega)
```

Fermionic configurations are sampled without replacement. Bosonic and
classical configurations may place multiple events in one stream. A closed
fermion shell has all six streams active but `Omega=1`, so exploration cannot
invent a second configuration.

## Grainflow mappings

- `density`: probability that an occupied stream emits a scheduled event.
- `space`: coherence-dependent empty fraction of the grain clock.
- `rate`: the Zeeman energy center for each mode.
- `rateRandom`: a bounded per-grain deviation derived from the semitone control.
- `windowRandom` and `delayRandom`: ensemble exploration.
- `direction`: becomes less fixed as exploration rises.
- envelopes: Hanning, Blackman, or Pluck buffers from Grainflow.
- `FM index`: scales a genuinely multiplied six-channel modulation signal at
  Grainflow's FM inlet; each mode has a distinct sub-audio modulation rate.
- the AM inlet receives an explicit six-channel unity signal and remains ready
  for transition-probability integration.

The macro named `exploration` is not presented as thermodynamic entropy itself.
The scheduler reports the actual combinatorial `S/k_B`; exploration controls
how rapidly and broadly the renderer samples those allowed configurations.

## Important operational distinction

Energy deviation is sampled inside Grainflow for individual grains, not only
when the ensemble state changes. Changing `density` does not change the grain clock or grain duration. Grainflow
defines density as the probability that a scheduled grain occurs. Clock rate
is controlled independently, while `space` controls the empty fraction inside
each grain period.
