# QMW Temporal Crystal 16 → Spectral Wavetable v1

This instrument reuses the successful QAC/QFT spectral-synthesizer voice:
a normalized 256-sample harmonic table is read by `phasor~ → wave~`. Its input
is the live canonical four-qubit density state rather than a submitted circuit
QFT result.

The mapping is deterministic and explicitly representational:

- the density matrix is rotated into the current Hamiltonian energy basis;
- the square roots of its 16 populations become harmonic amplitudes;
- coherence relative to the strongest occupied state supplies harmonic phase;
- a gentle high-harmonic tilt produces a fuller, less brittle table;
- the resulting waveform is DC-removed and normalized to a peak of `0.95`.

Python publishes the table atomically as four 64-sample OSC chunks under
`/qmw/density/wavetable/*`. Max stages complete tables without changing the
sounding buffer. Each Chronos tick writes the newest table into the inactive
buffer and crossfades to it over 50 ms.

## Run

Close every other Max patch that binds UDP `7400`, open
`QMW_Temporal_Crystal16_Spectral_Wavetable_v1.maxpat`, enable audio, and start:

```bash
python quantumsonification_conductor.py \
  --with-temporal-crystal \
  --temporal-crystal-mode observer \
  --temporal-crystal-rate 2
```

This new OSC publisher requires one conductor restart after installation.
Afterward, use the four mode buttons in Max without restarting Python.

The fundamental initializes to `55 Hz`. Quick choices provide `27.5`, `55`,
and `110 Hz`; the continuous control accepts `10–1000 Hz`. The local `test`
button constructs and commits a warm 16-harmonic table without Python.
