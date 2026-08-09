# QMW Density-Matrix Hilbert Operator 16 MC v1

This Max abstraction turns a 16-channel real MC signal into a 16-channel analytic signal and lets the complete complex density matrix act directly on it.

It implements

```text
z = I + iQ
rho = R + iM

y = rho z
y_re = R I - M Q
y_im = R Q + M I
```

This is cross-basis complex mixing, not sixteen independent gain controls. Every matrix element `rho[i,j]` can transfer analytic signal from basis input `j` to basis output `i`.

## Files

- `qmw_density_matrix_hilbert_operator16_mc_v1.maxpat` — the MC audio operator
- `qmw_density_matrix16_to_mcs_matrix_v1.js` — converts full matrix lists to `mcs.matrix~` control messages and reports validation metrics

Keep both files in the same Max search path or project folder.

## Abstraction interface

### Inlets

1. 16-channel MC audio from the direct basis-state synth
2. `Re(rho)` as exactly 256 floats
3. `Im(rho)` as exactly 256 floats
4. optional control messages

### Outlets

1. 16-channel `y_re`
2. 16-channel `y_im`
3. 16-channel audition signal
4. status and matrix diagnostics

The audition outlet starts in mode `1`, an exact RAW input path. Mode `2` selects the dry/wet blend; its wet value starts at zero.

## Matrix convention

Both 256-float lists are row-major:

```text
rho[0,0] rho[0,1] ... rho[0,15]
rho[1,0] rho[1,1] ... rho[1,15]
...
rho[15,0] ...       rho[15,15]
```

The operator computes

```text
y[i] = sum_j rho[i,j] z[j]
```

Max's `mcs.matrix~` control protocol is `input output gain`, so the JavaScript router deliberately emits each `rho[row,column]` as `column row gain`. Do not transpose the lists before sending them.

## Control inlet

```text
wet 0.0..1.0        dry/wet value used by audition mode 2
mode 1              exact RAW audition path (default)
mode 2              dry/wet audition path
ramp 25.            coefficient interpolation time in milliseconds
identity            set Re(rho) to identity and Im(rho) to zero
clear               set both matrices to zero
autocommit 1        emit each real or imaginary list as it arrives (default)
autocommit 0        store both lists until a commit message
commit              emit the stored real and imaginary matrices together
threshold 0.        zero only coefficients smaller than this on output
status              report current matrix diagnostics
```

For the tightest real/imag synchronization, send:

```text
autocommit 0
<256-real-value list to inlet 2>
<256-imag-value list to inlet 3>
commit
```

The threshold defaults to zero. The operator never normalizes, symmetrizes, transposes, or otherwise repairs quantum data silently.

## Cell-stream input

The operator's `Re(rho)` inlet (the JavaScript router's first inlet) also accepts:

```text
realcell row column value
imagcell row column value
cell row column real_value imaginary_value
```

With `autocommit 0`, a sequence of cell updates can be followed by one `commit`.

## Integration

Wire the 16-channel output of `qmw_density_field_quantum_resonator16_mc_v1` (or the equivalent direct-basis synth) to inlet 1. Route the full real and imaginary density-matrix lists already produced by `quantum_population_osc_v6_shadow.py` to inlets 2 and 3.

Do not add a second `udpreceive`: branch the decoded density packets inside the existing OSC ingress patch. The Complex Pauli Synth remains a data-to-parameter mapper; this abstraction is the separate density-operator audio layer.

## First validation sequence

1. Start with `mode 1`. The audition outlet must null against the source when polarity-inverted and summed.
2. Send `identity`. `y_re` should match the Hilbert in-phase output and `y_im` should match its quadrature output.
3. Send a real diagonal matrix. Each analytic basis channel should be weighted independently, with no cross-basis transfer.
4. Add one Hermitian off-diagonal pair. For `i != j`, use `R[i,j] = R[j,i]` and `M[i,j] = -M[j,i]`. Energy should now transfer between the two basis channels with the expected complex phase relation.
5. Move audition to `mode 2`, then raise `wet` slowly.

The status outlet reports `trace_re`, `trace_im`, maximum Hermitian-structure error, and the matrix Frobenius norm squared. These are diagnostics only; they do not alter the audio coefficients.

## Density matrix versus square root

Version 1 applies `rho` directly. This makes the sonic operator literal and easy to audit. A later mode can apply a precomputed principal square root `sqrt(rho)` if the research goal changes from density weighting to amplitude preparation; that decomposition belongs in the Python quantum-data layer, not in a Max control-rate approximation.

## Monitoring

Keep `y_re` and `y_im` separate for complex analysis, XY display, or downstream coherent operations. For ordinary listening, use the audition outlet or explicitly monitor a documented projection. If a stereo monitor is needed, follow the operator with `mc.mixdown~ 2 @autogain 1`; do not mistake that monitoring fold-down for the 16-channel quantum state.
