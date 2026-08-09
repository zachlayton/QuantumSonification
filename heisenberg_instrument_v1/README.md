# QMW Heisenberg Laboratory

## Musical matrix instrument: sixteen Rings bodies

`QMW_Heisenberg_Rings_Matrix_Instrument_v1.maxpat` is the first matrix-native
instrument rather than a compatibility monitor. Start the full four-qubit
publisher from the project root:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  -m heisenberg_instrument_v1.heisenberg_lab_v1
```

Open the Rings instrument, enable audio, select `XZ0`, and compare coherent,
unread, and recorded modes. It requires the installed `vb.mi-objects-Jan2026`
package; the external's object name is `vb.mi.rngs~`.

The mapping is relational:

- each of the sixteen matrix rows controls one monophonic `vb.mi.rngs~` body;
- the row's sixteen magnitudes determine its energy and off-diagonal coupling;
- energy-gap frequencies determine pitch;
- off-diagonal ratio controls structure;
- phase dispersion controls brightness;
- change from the previous matrix controls damping and articulation;
- the row's weighted pan controls position;
- all 256 complex coefficients produce a 2048-point rotating-quadrature
  wavetable read at signal rate by `jit.peek~` inside every voice.

The summed Rings output is written by `jit.poke~` into the separate
`qmb_heisenberg_rings_memory` matrix. This is acoustic performance memory only;
the committed quantum matrices remain immutable.

## Try the Quantum Matrix Bus compatibility path

`QMW_Heisenberg_Measurement_Lab_v4_QMB.maxpat` keeps the complete v3 audio
renderer intact and attaches a second data path to the same OSC matrix frame.
The QMB path assembles real and imaginary contributions into a two-plane
`float64` Jitter matrix and publishes magnitude, phase, frequency, and pan as
one-plane matrices.

Start the existing clear-lab publisher:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  -m heisenberg_instrument_v1.clear_measurement_lab_v3
```

Open `QMW_Heisenberg_Measurement_Lab_v4_QMB.maxpat`. The original contribution
table remains at center-left; the QMB real and imaginary matrices appear in the
right-hand panel. Every accepted update reports `commit <revision> <dimension>
<bank>`. Click **selftest** to exercise the QMB path without starting Python.

The adapter is double-buffered. Incoming fields populate an inactive bank, and
the active bank changes only when `/matrix/end` carries the matching revision
and all six required matrix fields are present. A malformed or incomplete frame
is rejected without changing the matrices used by consumers.

## Start with the clear one-qubit laboratory

`QMW_Heisenberg_Measurement_Lab_v3_Clear.maxpat` is now the recommended first
instrument. It separates measurement backaction from the later 16 by 16 matrix
mechanics work. Start its independent publisher with:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  -m heisenberg_instrument_v1.clear_measurement_lab_v3
```

Then open the clear Max patch and enable audio. It uses UDP 7420 for state and
7421 for controls, so it can coexist with the earlier lab.

The experiment is deliberately one qubit and four cells. Preparation,
post-measurement evolution, observable `A=(X+Z)/sqrt(2)`, cell frequencies,
gain, panning, and the two `sinusoids~ bwe` renderers remain unchanged. Only
the intermediate protocol changes:

```text
coherent  no intermediate measurement
unread    Z measurement with the result discarded
recorded  Z measurement with one result retained
```

The four cells are exactly `rho[m,n] * A[n,m]`; their sum is `Tr(rho A)`.
Diagonal cells render population at 110 and 165 Hz. The two off-diagonal cells
render coherence at 440 Hz on opposite sides of the stereo field. The slow
comparison control holds each protocol for six seconds.

The first laboratory implements the three intermediate-observation protocols
distinguished in Heisenberg's *Physical Principles of the Quantum Theory*:

1. `coherent`: no intermediate observation;
2. `unread`: a projective observation is performed and its result discarded;
3. `recorded`: one result is sampled and the future state is conditioned on it.

The same final density matrix is translated into a 16 by 16 relational field.
For observable `A`, energy-basis cell `(m,n)` is exactly

```text
rho[m,n] * A[n,m]
```

and the complex sum of all 256 cells reconstructs `Tr(rho A)`. Off-diagonal
resonator frequencies use Hamiltonian energy gaps under one global audio scale.
The sixteen diagonal cells have zero physical transition frequency and are
placed on a separate, declared low-frequency anchor ladder.

## Run

Start the standalone publisher from the project root:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  -m heisenberg_instrument_v1.heisenberg_lab_v1
```

Then open `QMW_Heisenberg_Laboratory_v2_CNMAT.maxpat` and enable `ezdac~`.
The original `QMW_Heisenberg_Laboratory_v1.maxpat` remains available as the
256-voice reference implementation.

For the clearest first audition, leave the observable on `XZ0` and enable
**run comparison**. The patch holds each protocol for four seconds. Everything
except the status of the intermediate measurement remains fixed:

1. `coherent`: no intermediate measurement; alternatives remain available to
   interfere;
2. `unread`: a measurement occurs but its outcome is discarded; interference
   is lost without selecting one audible history;
3. `recorded`: one outcome is retained and conditions the later state.

The local **test** button is only an audio-path diagnostic. It now sustains a
CNMAT test field until **resume** is pressed, rather than being overwritten by
the next periodic OSC frame.

The publisher sends the transition field to UDP port 7400 and listens for lab
controls on port 7412.

## CNMAT spectral architecture

The v2 patch follows the installed CNMAT Spectral Tutorials rather than
treating every matrix entry as an isolated oscillator:

- two `sinusoids~ bwe` banks render the left/right partial models;
- two `resonators~ smooth` banks render the left/right measurement apparatus;
- `coherent` is primarily sustained sinusoidal structure;
- `unread` continuously excites the resonators with noise, whose BWE noisiness
  follows the actual density-matrix disturbance;
- `recorded` sends one impulse into the resonators when a result is recorded or
  changes, making outcome acquisition an audible event;
- row/column position supplies equal-power stereo placement, while all 256
  ordered cells remain present in each bank.

Every complete transition field is also inserted into two named SDIF buffers
with `SDIF-listpoke`:

- `qmw_heisenberg_trc`: `1TRC` rows `[index, frequency, amplitude, phase]`;
- `qmw_heisenberg_res`: `1RES` rows `[frequency, amplitude, decay, phase]`.

The two **write** messages in the patch save those evolving buffers as
`QMW_Heisenberg_1TRC.sdif` and `QMW_Heisenberg_1RES.sdif`. Phase is preserved in
SDIF even though the CNMAT BWE synthesizer consumes frequency, amplitude, and
noisiness rather than arbitrary initial phase.

## OSC contract

The three complete cases are published below:

```text
/qmw/heisenberg/coherent/...
/qmw/heisenberg/unread/...
/qmw/heisenberg/recorded/...
```

The selected resonator field is mirrored to:

```text
/qmw/heisenberg/active/mode
/qmw/heisenberg/active/outcome
/qmw/heisenberg/active/probabilities
/qmw/heisenberg/active/disturbance
/qmw/heisenberg/active/coherence_before
/qmw/heisenberg/active/coherence_after
/qmw/heisenberg/active/matrix/magnitude
/qmw/heisenberg/active/matrix/magnitude_normalized
/qmw/heisenberg/active/matrix/phase
/qmw/heisenberg/active/matrix/signed_gap
/qmw/heisenberg/active/matrix/frequency_hz
/qmw/heisenberg/active/matrix/pan
/qmw/heisenberg/active/matrix/real
/qmw/heisenberg/active/matrix/imag
```

Each matrix transmission is bracketed by `/matrix/begin` and `/matrix/end`,
so the Max bank commits one complete 256-cell frame rather than briefly mixing
values from adjacent revisions.

Controls:

```text
/qmw/heisenberg/mode coherent|unread|recorded
/qmw/heisenberg/record 1
/qmw/heisenberg/observable X0|Y0|Z0|XZ0
```

`XZ0 = (X0 + Z0) / sqrt(2)` is the default audition observable. A pure `X0`
made both the coherent and unread matrices exactly silent in the default
experiment; the tilted axis distinguishes all three final-state classes with
one unchanged observable.

The standalone separation is intentional: it lets the measurement semantics
and 256-cell gain structure be auditioned before the process is allowed to
mutate the canonical continuously evolving density engine.
