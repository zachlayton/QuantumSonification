# QMW Polyphonic Complex Hilbert Instrument v6.2

Open `QMW_Polyphonic_Complex_Hilbert_Instrument_v6_2.maxpat` from the extracted
bundle. v6.2 uses newly named dependencies so Max cannot reuse the earlier
cached engine.

## Corrections in v6.2

- Selecting **COMPLEX FEEDBACK** now opens the recursive mode gate, refreshes
  its harmonic delay list and gain, and closes the gate when another audition
  mode is selected.
- **Feedback Depth** now has a guaranteed manual range. Quantum coherence adds
  bounded variation rather than being a prerequisite for hearing feedback.
  Depth `0.5` produces roughly `0.09–0.15` loop gain; Depth `1` remains capped
  below `0.35`.
- **Complex Memory** now delays the imaginary rail by an additional `0–8 ms`
  before projection. This is a true dual-rail phase memory, rather than the
  previous crossfade between mathematically equivalent paths.
- **Imaginary Coupling** introduces a bounded Hermitian coherence ring when the
  selected matrix contains no imaginary cells. Pair and ring presets also use
  stronger, safety-bounded coefficients.
- The matrix editor v2 has explicit Re, Im, commit, and status port indices.
  Presets now update the `matrixctrl` display and the audio operator from the
  same canonical matrix.
- Clicking a matrix preset automatically selects **FULL MATRIX WET**. The four
  complexity buttons and feedback safety buttons likewise select the audition
  path they actually control.

## Fast validation

1. Turn on DSP and play a sustained chord.
2. Choose **COMPLEX FEEDBACK** and compare Feedback Depth `0`, `0.5`, and `1`.
3. At Depth `0.5`, compare Complex Memory `0` and `1`; the I/Q delay offset
   should cause an obvious resonant phase/timbre change.
4. Raise Imaginary Coupling, then compare Identity, Fundamental Fifth, and Ring.
5. Double-click the matrix editor and press the presets again. Its grid should
   visibly track every preset.

The source-level controls—keyboard pitch, Harmonic Lock, Ring Decay, and Field
Detection—retain their v6.1 mappings.
