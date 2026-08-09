# QMW Polyphonic Complex Hilbert Laboratory v6

Open `QMW_Polyphonic_Complex_Hilbert_Lab_v6.maxpat` with every bundled file
kept in the same Max search-path folder.

## What changed

- Eight MIDI-allocated voices now play independent fundamentals and ADSR
  envelopes. Each voice still generates sixteen harmonic lanes.
- Matching harmonic indices are summed across the notes before the shared
  Hilbert, density-matrix, and feedback field. The matrix therefore keeps its
  meaning: row/column indices are harmonic relationships, not voice numbers.
- A direct analytic audition path exposes Hilbert rotation before and after
  rho. It does not depend on a high feedback gain to become audible.
- Harmonic Phase Spread rotates successive harmonics by different angles.
- SSB Motion continuously rotates the analytic plane, producing controlled
  frequency translation instead of another arbitrary LFO.
- Matrix Delta outputs `(rho z) - z` after the same analytic projection. It is
  nearly silent for identity and makes off-diagonal matrix action explicit.

## First sound

1. Start the conductor and wait for the density indicator.
2. Turn on DSP and leave Harmonic Lock at `1`, Motion Drive at `0.1`.
3. Play a MIDI keyboard, click the onscreen keyboard, or press the chord-on
   message. Use the adjacent chord-off message to release it.
4. Set the audition menu to **ANALYTIC ROTATION**.
5. Start with Analytic Wet `1`, Hilbert Depth `1`, Phase Depth `1.5`, Harmonic
   Phase Spread `0.08`, and SSB Motion `0`.

Then compare:

- **RAW**: exact summed polyphonic source before Hilbert processing.
- **ANALYTIC ROTATION**: pre-rho I/Q rotation.
- **FULL MATRIX WET**: complete `rho(I+iQ)` projection.
- **MATRIX DELTA**: matrix contribution isolated from the aligned identity
  analytic path.
- **COMPLEX FEEDBACK**: the stable recursive bamboo-like v5 path.

For slow spectral movement, try SSB Motion between `-0.4` and `0.4` Hz. For a
clearer frequency shift, try `2` to `6` Hz. Harmonic Phase Spread is usually
most musical from `0.02` to `0.18` radians per lane. Phase Depth can safely be
explored from `0` to `4`.

## Polyphony and gain

Voice output is normalized to `0.32` before eight-voice summing. The existing
safe stereo clip remains outside the recursive loop. For dense chords, lower
the master rather than increasing feedback gain.

The feedback delay list remains a shared harmonic reference based on the
**feedback reference Hz** control. It is not retuned separately for every
polyphonic note; doing so would require a separate sixteen-channel feedback
operator per voice and would change the matrix from a shared field into eight
independent matrices.

## Console diagnostics

`qmw.rho16.status: status ...` is a valid matrix diagnostic. It reports trace,
Hermitian error, and Frobenius norm. It must never be followed by signal
objects saying they do not understand `status`. The bundled operator keeps its
diagnostic outlet physically to the right of all three signal outlets, because
Max resolves abstraction outlet order spatially when loading the patch.
