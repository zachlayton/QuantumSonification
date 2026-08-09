# QMW Complex Matrix Performance Laboratory v5

Open:

```text
QMW_Complex_Matrix_Performance_Lab_v5.maxpat
```

Version 5 preserves the complete v4 harmonic, Hilbert, density-operator, and
dual-rail memory signal path. It inserts a canonical complex-matrix editor
between the conductor/preset stream and the four internal `mcs.matrix~`
networks.

Double-click this object in the host:

```text
qmw_complex_matrixctrl16_v1
```

## Matrix orientation

The 16 x 16 `matrixctrl` grid uses:

```text
column j = source/input harmonic
row i    = destination/output harmonic
cell     = magnitude of rho[i,j]
```

This matches the audio router. The row-major complex cell `rho[i,j]` becomes
the `mcs.matrix~` connection `input j -> output i`.

## Editing a complex cell

The grid displays magnitude. Clicking or dragging a cell selects it and edits
its magnitude. The selected-cell panel exposes:

- source column and destination row;
- magnitude;
- phase in radians;
- calculated real and imaginary values.

For magnitude `r` and phase `phi`:

```text
Re(rho[i,j]) = r * cos(phi)
Im(rho[i,j]) = r * sin(phi)
```

The real and imaginary 256-cell lists are emitted together, followed by one
`commit`. The existing density operator then updates all four complex audio
paths atomically:

```text
Re input -> Re output:  +Re(rho)
Im input -> Re output:  -Im(rho)
Re input -> Im output:  +Im(rho)
Im input -> Im output:  +Re(rho)
```

## Matrix sources

- **Follow** — display and apply the conductor or selected v4 preset.
- **Freeze** — capture the currently audible matrix into the manual layer.
- **Manual** — recall and apply the retained manual layer.
- **Morph** — interpolate from the current upstream matrix at `0` to the
  retained manual matrix at `1`.

Clicking the grid while following the conductor automatically captures the
currently audible matrix and enters manual editing. Preset and conductor
updates continue to be stored upstream, so **follow** or **morph** can return
to them immediately.

The source is now a persistent menu rather than four momentary messages. It is
synchronized from the matrix engine, so the displayed selection is the source
that actually produced the last applied matrix.

## Applied-state indicators

- **Hermitian Lock** is a persistent toggle reflecting the engine flag.
- **Safety** is a persistent toggle reflecting the normalization flag.
- **Scale** shows the multiplier applied by matrix safety. `1` means no
  normalization was required; a smaller value means the painted matrix was
  contracted before reaching the feedback operator.
- **Commits** counts complete paired Re/Im matrix applications.
- **Applied** flashes only when the complete matrix has been sent and the
  explicit `commit` message has followed it.

Selecting a cell silently refreshes column, row, magnitude, phase, computed
Re, and computed Im. Magnitude and phase are editable; Re and Im are read-only
derived values.

## Hermitian Lock

Hermitian Lock is enabled at startup. Editing one off-diagonal cell updates its
conjugate partner:

```text
Re(rho[j,i]) =  Re(rho[i,j])
Im(rho[j,i]) = -Im(rho[i,j])
Im(rho[i,i]) = 0
```

This makes a fundamental-to-fifth edit automatically create the reciprocal
fifth-to-fundamental coefficient with opposite imaginary sign.

`hermitian 0` enables free directional routing. That can be useful musically,
but it should be described as a complex audio operator rather than a physical
density matrix.

## Feedback safety

Safety is enabled at startup. Before every commit, the editor calculates the
sum of complex magnitudes in every row and column. If either maximum exceeds
one, the complete matrix is scaled so both are bounded by one.

This prevents a dense manually painted matrix from multiplying feedback energy
simply because many routes were enabled. The existing v4 feedback gain ceiling
of `0.15`, RAW SAFE gate, and PANIC behavior remain active independently.

Disabling matrix safety is intentionally possible with `safety 0`, but is not
recommended inside recursive mode.

## Suggested first experiment

1. Start the conductor and establish the familiar v4 state: Harmonic Lock `1`,
   Motion Drive `0.10`, Feedback Depth `0.5`, and RAW SAFE.
2. Select v4 **mode2** and the `fundamental_fifth` preset.
3. Open the matrix editor and click **follow**. The active diagonal and pair
   should appear in the grid.
4. Click **freeze**.
5. Select the fundamental/fifth cell, then move its phase while keeping its
   magnitude modest.
6. Paint a second pair, such as third/seventh. Hermitian Lock will create the
   conjugate partner.
7. Click **follow** to hear the upstream preset again.
8. Move Morph slowly from `0` to `1` to interpolate into the manual matrix.
9. Compare Complex Memory at `0`, `0.5`, and `1` without increasing feedback
   gain.

Use PANIC + MUTE if feedback energy becomes unexpected.

## Physical interpretation

Hermitian structure and bounded gain do not by themselves guarantee a valid
density matrix. A physical density matrix must also be positive semidefinite
and normally have trace one. V5 deliberately distinguishes:

- conductor-provided physical/state data;
- Hermitian coherence editing;
- unrestricted complex audio routing.

A later physical-matrix mode could add trace normalization and positive-
semidefinite projection, but v5 does not silently claim that arbitrary painted
audio matrices are quantum states.
