# QMW Complex Pauli Hilbert Integration v1

This integration places a four-channel Hilbert/complex-multiplication layer after the four existing Complex Pauli or direct density-field Gen~ voices and before their final sum or spatialization.

## Files

- `qmw_complex_pauli_hilbert_router_v1.maxpat`: converts the existing Complex Pauli Synth OSC `x/y` outputs into two four-element lists.
- `qmw_complex_pauli_hilbert_4voice_v1.maxpat`: packs the four audio voices into MC, constructs their analytic signals with `mc.hilbert~`, and applies four complex coefficients.

## Main-patch wiring

Keep the current `udpreceive 7403`. Branch its FullPacket output to the router abstraction:

```text
udpreceive 7403
├── existing OSC routing
└── qmw_complex_pauli_hilbert_router_v1
        ├── outlet 1: [x0 x1 x2 x3]
        └── outlet 2: [y0 y1 y2 y3]
```

Connect the existing four audio voices and the router lists to the processor:

```text
q0 gen~ audio ─────────────── inlet 1
q1 gen~ audio ─────────────── inlet 2
q2 gen~ audio ─────────────── inlet 3
q3 gen~ audio ─────────────── inlet 4
router real [x0..x3] ──────── inlet 5
router imag [y0..y3] ──────── inlet 6
                              qmw_complex_pauli_hilbert_4voice_v1
                              ├── outlet 1: four-channel complex real MC
                              ├── outlet 2: four-channel complex imaginary MC
                              └── outlet 3: four-channel dry/wet audition MC
```

For stereo monitoring, connect outlet 3 to:

```text
mc.mixdown~ 2 @autogain 1
|
mc.live.gain~
|
mc.dac~ 1 2
```

Keep outlets 1 and 2 unsummed when sending the field to Spat or another multichannel stage.

## Complex operation

For each qubit voice `k`, `mc.hilbert~` creates

\[
z_k(t)=I_k(t)+iQ_k(t).
\]

The control pair defines

\[
c_k(t)=a_k(t)+ib_k(t).
\]

The processor outputs

\[
z_kc_k=(I_ka_k-Q_kb_k)+i(I_kb_k+Q_ka_k).
\]

All four coefficient pairs are smoothed by `mc.rampsmooth~ 960 960`. This prevents list-rate clicking without adding an LFO or synthetic trajectory.

## Three operating meanings

### 1. Identity / analytic observation

Use these coefficient lists:

```text
a = 1. 1. 1. 1.
b = 0. 0. 0. 0.
```

No additional quantum coefficient is applied. The exact RAW BASELINE is `Hilbert wet = 0`, which passes the original four voices unchanged. At `Hilbert wet = 1`, the coefficient operation is neutral but the audition output uses the phase-matched real outlet of `mc.hilbert~`; the complex real and imaginary outlets remain available throughout.

### 2. Recursive Pauli mode

Connect the supplied router, which maps:

```text
/qmw/pauli/q/0/x ... /qmw/pauli/q/3/x -> a0..a3
/qmw/pauli/q/0/y ... /qmw/pauli/q/3/y -> b0..b3
```

If those same `x/y` values already shaped the source voice, this second application is intentionally recursive. At the abstract level it approaches a `c × c` or `c²` operation: magnitudes square and phases double. It should be treated as a distinct synthesis mode, not the RAW BASELINE preset.

### 3. Relational density-coherence mode

For the most structurally informative use, leave the existing voice synthesis driven by its normal population/Pauli data and feed a distinct density-matrix off-diagonal stream into processor inlets 5 and 6. Then the source state and the relational coherence are separate operators:

```text
voice state -> analytic audio
density relation rho_ij -> complex transformation
```

This avoids redundant encoding and makes the density matrix audible as an operation on the voice field.

## Scope behavior

The voice selector chooses q0-q3 for both XY displays:

- cyan: the selected voice's original Hilbert trajectory `(I,Q)`
- orange: the trajectory after complex Pauli/density multiplication

Unit-magnitude coefficients rotate the figure. Magnitude contracts or expands it. Time-varying complex coefficients move the entire audio geometry.

## First test

1. Install both `.maxpat` files beside the main synth patch or in the Max search path.
2. Connect q0-q3 audio to processor inlets 1-4.
3. Leave the identity coefficient lists in place. `Hilbert wet` initializes at `0` for the exact RAW BASELINE.
4. Move `Hilbert wet` between `0` and `1`; the output should crossfade cleanly between the original MC voices and the transformed real field.
5. Connect the router list outlets to processor inlets 5 and 6.
6. Select scope voices `1` through `4` and compare the cyan and orange trajectories.

The processor does not create a second UDP receiver and does not modify the separate `quantum_population_osc_v6_shadow.py` full-density-matrix path.
