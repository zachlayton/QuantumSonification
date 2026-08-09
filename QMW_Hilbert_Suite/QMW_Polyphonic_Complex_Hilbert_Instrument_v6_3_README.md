# QMW Polyphonic Complex Hilbert Instrument v6.3

v6.3 preserves the locked sixteen-harmonic field as a persistent reference and
layers the selected Hilbert/matrix/feedback field against it.

## Complex Layer Morph

`Complex Layer Morph` is no longer a dry/wet crossfade. For morph value `m`:

```text
anchor coefficient  = 1 / sqrt(1 + m*m)
complex coefficient = m / sqrt(1 + m*m)
output               = anchor * locked_field + complex * selected_field
```

At `m = 0`, only the locked harmonic field is heard. At `m = 1`, the locked
field and complex layer are both retained at approximately -3 dB. This avoids
discarding the fundamental reference when the complex behavior becomes deep.

The same control moves the matrix continuously from identity toward the chosen
preset:

```text
rho(m) = (1 - m) * identity + m * preset
```

The matrixctrl display therefore shows the matrix that is actually sent to the
operator at the current morph value.

## Independent pitch geometry

`Quantum Spectrum Morph` remains a separate control. It changes the resonator
frequency geometry between the stable harmonic lattice and the conductor's raw
gap spectrum. It does not change the complex-layer balance.

## Suggested validation

1. Set `Harmonic Lock` to `1` and `Quantum Spectrum Morph` to `0`.
2. Choose `ANALYTIC ROTATION` and sweep `Complex Layer Morph` from `0` to `1`.
   The fundamental and locked harmonics should remain audible throughout.
3. Choose `FULL MATRIX WET`, select `Identity`, then `Hermitian Ring`.
4. Sweep `Complex Layer Morph`; the matrixctrl should move from a diagonal
   identity toward the ring while the locked layer remains underneath.
5. Select `COMPLEX FEEDBACK` only after establishing the reference. Begin with
   Feedback Depth below `0.4` and increase Complex Memory gradually.

Use `RAW SAFE` or `PANIC` immediately if a recursive state becomes too strong.
