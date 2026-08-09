# QMW Polyphonic Complex Hilbert Instrument v6.4

v6.4 adds a mathematically explicit, norm-preserving complex route without
removing the bounded expressive feedback that gives the instrument its more
volatile behavior.

## What changed

- The analytic phase stage now rotates and retains both I and Q rails:

  ```text
  I' = I cos(theta) - Q sin(theta)
  Q' = I sin(theta) + Q cos(theta)
  ```

  Real audio is produced only at the labelled final projection. The abstraction
  also exposes all four pre/post I/Q rails for later spatial or feedback work.

- Built-in matrix presets are products of complex phase and Givens rotations.
  `Complex Layer Morph` changes their rotation angles rather than interpolating
  matrix entries, so the preset matrix remains unitary throughout the sweep.

- The matrix editor's legacy absolute-row-sum safety scaler is disabled for the
  unitary preset path. That scaler is useful for arbitrary feedback matrices but
  incorrectly attenuates many valid unitary transformations.

- Arbitrary external matrices are rejected by the unitary preset module. They
  remain appropriate for the separately bounded expressive feedback route.

## Mathematical contract

For built-in presets, within floating-point tolerance:

```text
U^H U = I
sum_j |(U z)_j|^2 = sum_j |z_j|^2
```

The complete I/Q phase rotation likewise preserves `I*I + Q*Q` per lane.
The final real projection is deliberately lossy and is labelled as such.

This is an audio-domain complex-vector invariant. It does not claim that the
harmonic carrier bank is itself a complete quantum state or that the expressive
feedback implements physical density-matrix evolution.

## Performance notes

Start with `ANALYTIC ROTATION`, `Complex Layer Morph` around `0.5`, projection
angle `0`, and low feedback. Sweep phase depth and spread before adding feedback.
The built-in pair and ring presets should now redistribute energy without the
level collapse caused by the former safety scaling and linear matrix morph.

Use the matrix editor or complex feedback when nonunitary contraction, memory,
or instability is artistically desired; those effects are intentionally outside
the unitary contract.
