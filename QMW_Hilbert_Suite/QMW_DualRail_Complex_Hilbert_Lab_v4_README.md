# QMW Dual-Rail Complex Hilbert Laboratory v4

Open:

```text
QMW_DualRail_Complex_Hilbert_Lab_v4.maxpat
```

Version 4 keeps the stable v3 instrument: a fundamental plus sixteen exact
harmonics, with **Harmonic Lock = 1** and **Motion Drive = 0.10** as the
reference listening state. It develops the feedback stage instead of adding a
larger cascade of Hilbert filters.

## Four modes

Click one of the four mode messages in the upper-right panel:

1. **Analytic rotation** — identity matrix, imaginary matrix depth zero, and
   the conductor's projection phase acting on each harmonic independently.
2. **Coherence pairs** — the fundamental/fifth-harmonic preset with complex
   off-diagonal exchange and half dual-rail memory.
3. **Full density operator** — selects the external 256-real + 256-imaginary
   matrix stream. The preset router waits for both lists before committing.
4. **Complex memory** — retains the selected matrix and moves the feedback
   fully to delay-before-projection dual-rail operation.

All four buttons open recursive mode. **RAW SAFE** still closes the feedback
gate and returns to the unprocessed harmonic monitor.

## Complex controls

- **Hilbert Depth** blends ordinary delayed real feedback with analytically
  transformed feedback. This affects the feedback branch, not the dry output.
- **Phase Depth** scales the conductor's sixteen projection angles before the
  sine/cosine rotation. `0` removes phase rotation; `1` uses the full angles.
- **Imaginary Coupling** scales Im(rho) from `0` to `1` and recommits the
  complete matrix.
- **Complex Memory** crossfades between projection-before-delay and separate
  real/imaginary delays followed by projection. At `1`, phase remains in the
  two rails for the entire delay interval before it is projected back to the
  real feedback input.
- **custom coherence pair** accepts two zero-based harmonic indices (`0..15`).
- **I/Q scope channel** selects a one-based harmonic channel (`1..16`) for
  both the PRE-rho and POST-rho XY monitors. Double-click each scope
  abstraction to view it.

The stable v3 resonator accepts a real excitation/feedback signal. Therefore,
the two rails remain separate through matrix action and delay, then are
projected to real audio at the loop boundary. Complex Memory does not pretend
that the Gen resonator itself has become a complex-valued state variable.

## Matrix presets

The preset buttons work without a full matrix from the conductor:

- `identity`
- `diagonal` — uses `/qmw/density/populations` when present; the live
  sixteen-harmonic magnitude field is the fallback
- `fundamental_octave`
- `fundamental_fifth`
- `third_seventh`
- `ring` — a Hermitian nearest-neighbor coherence ring
- `external` — the conductor's paired 256-cell real and imaginary lists

Pair and ring presets use antisymmetric imaginary off-diagonal entries, so the
resulting complex matrix is Hermitian. Every preset update sends Re(rho), then
scaled Im(rho), then one explicit `commit`.

## Delay and feedback

The delay inlet is not fixed or empty. The conductor's harmonic list,
fundamental, and Harmonic Lock feed `qmw_harmonic_delay_list16_v1.js`:

```text
ratio[i] = mix(engine_ratio[i], i + 1, Harmonic Lock)
delay[i] = 1000 / (fundamental * ratio[i]) ms
```

That sixteen-value list controls the ordinary feedback delay and all three v4
memory rails. Feedback amount remains bounded by the v3 mapping:

```text
gain = 0.03 + FeedbackDepth * 0.09 * coherence * (1 - 0.6 * entropy)
```

The hard ceiling remains `0.15`. Start with Feedback Depth around `0.5`; the
new modes should be compared before increasing gain.

## First listening pass

1. Close older hosts so only v4 owns UDP port 7400.
2. Start the conductor, open v4, and turn the master down.
3. Leave Harmonic Lock at `1`, Motion Drive at `0.10`, Hilbert Depth at `1`,
   Phase Depth at `1`, and Complex Memory at `0`.
4. Enable DSP and establish **RAW SAFE**.
5. Click **mode1** and compare it with RAW SAFE.
6. Click **mode2**, then move Imaginary Coupling slowly from `0` to `1`.
7. Compare `fundamental_octave`, `third_seventh`, and `ring` without changing
   Feedback Depth.
8. Raise Complex Memory gradually. Try `0.25`, `0.5`, then `1`.
9. Only after those comparisons, raise Feedback Depth toward `0.7` if the loop
   remains controlled.

Use **PANIC + MUTE** immediately if energy becomes unexpected.

## Where `mc.hilbert~` is located

Double-click:

```text
qmw_density_matrix_dualrail_feedback16_mc_v2
```

The visible `mc.hilbert~` near the left side supplies the PRE-rho I/Q monitor.
The processing Hilbert transformer remains inside:

```text
qmw_density_matrix_hilbert_operator16_mc_v1
```

That separation makes the before/after scopes independent of the operator's
matrix output while keeping the audible path unchanged.
