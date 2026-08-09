# Lightweight Quantum Sonification Workshop

This folder contains one-qubit teaching examples that generate their own WAV
files. They require Python and NumPy only—no Max, OSC, Qiskit, audio interface,
or quantum-computing account.

The code performs a **classical simulation** of a qubit and maps selected
quantum observables to sound. The mappings are design decisions, not claims
that a qubit has an intrinsic sound. The convolution is conventional DSP;
quantum-derived values select or mix the acoustic responses.

## Setup

From this directory:

```bash
python -m pip install -r requirements.txt
python quantum_sonification.py all
```

WAV files appear in `generated_audio/`. They are deliberately pre-rendered so
the demonstrations work in a lecture room without real-time audio setup.

## The seven examples

### 1. Hear four states

```bash
python quantum_sonification.py states
```

The amplitudes of 220 Hz and 440 Hz tones are driven by `sqrt(P(0))` and
`sqrt(P(1))`. Compare `|0>`, `|1>`, `|+>`, and `|y+>`.

Teaching question: which properties are lost if we sonify probabilities only?
The comparison between `|+>` and `|y+>` introduces phase and Pauli observables.

### 2. Hear a qubit rotate

```bash
python quantum_sonification.py sweep
```

An `RY` rotation sweeps theta from 0 to 2 pi. Probability moves smoothly
between the low and high tones.

### 3. Hear measurement statistics

```bash
python quantum_sonification.py measure --shots 64 --seed 7
```

Measurements of `|+>` become low or high percussive events. Change `--shots`
to compare small samples with stable long-run statistics. The seed makes a
conference performance repeatable; change it to demonstrate a new sample.

### 4. Move from one qubit to two

```bash
python quantum_sonification.py two-qubit
```

The joint outcomes `|00>`, `|01>`, `|10>`, and `|11>` become four notes. Play
the states in this order: `|00>`, `|+0>`, `|++>`, then the Bell state
`(|00> + |11>)/sqrt(2)`. The Bell chord contains only the `00` and `11` notes.

### 5. Hear why local probabilities do not reveal entanglement

```bash
python quantum_sonification.py entanglement --shots 64 --seed 7
```

Both `|++>` and the Bell state give each qubit a 50/50 local measurement
distribution. Listening to either qubit alone cannot distinguish them. Their
joint behavior does: `|++>` produces all four bit pairs independently, while
the Bell state produces only correlated `00` and `11` outcomes.

This is the core entanglement lesson: entanglement is visible in correlations,
not merely in each subsystem's local probabilities. These computational-basis
correlations demonstrate the selected Bell state, but are not by themselves a
Bell-inequality test.

### 6. Build a 256-point quantum-derived wavetable

```bash
python quantum_sonification.py wavetable
```

This converts complex computational-basis amplitudes into harmonic
coefficients. Basis amplitude `k` controls harmonic `k + 1`: its magnitude
controls harmonic magnitude and its complex argument controls harmonic phase.
The raw `wavetable_256_*.wav` files contain exactly 256 mono samples; the
`wavetable_preview_*.wav` files play each table at 110 Hz for easy listening.

For one qubit, `|0>` supplies the fundamental and `|1>` supplies the second
harmonic. For two qubits, `|00>`, `|01>`, `|10>`, and `|11>` supply harmonics
1–4. The Bell table therefore contains harmonics 1 and 4, while the separable
`|++>` table contains all four. This is an explicit compositional mapping, not
a claim that the quantum state is itself an audio waveform.

### 7. Quantum-derived convolution reverb

```bash
python quantum_sonification.py reverb --theta 1.5708
```

The script synthesizes a dry phrase and two deliberately contrasting impulse
responses. It convolves the phrase with both IRs, then performs an equal-power
mix controlled by the one-qubit probabilities:

```text
wet = sqrt(P(0)) * bright_room + sqrt(P(1)) * dark_room
```

Try `--theta 0`, `--theta 1.5708`, and `--theta 3.14159` to move from the
bright room through a balanced superposition mapping to the dark room.

## Suggested live walkthrough (36 minutes)

1. Play `state_0.wav`, `state_1.wav`, and `state_plus.wav` (4 minutes).
2. Reveal `qubit()`, `observables()`, and the two-tone mapping (6 minutes).
3. Play the rotation, then change one mapping frequency (4 minutes).
4. Render 16 and 256 one-qubit measurement shots and compare them (4 minutes).
5. Compare `|++>` and Bell chords, then their measurement streams (7 minutes).
6. Compare the `|++>` and Bell wavetable previews (4 minutes).
7. Play dry, bright, dark, and qubit-morphed reverbs (6 minutes).

Before presenting, run `python quantum_sonification.py all` and keep the entire
`generated_audio/` folder as the playback fallback.

## QAC and IBM Quantum wavetable bridge

`qac_ibm_wavetable_bridge.py` accepts the existing chunked QAC QASM protocol.
It sends an immediate local table and, in `both` mode, asynchronously replaces
it with a table derived from IBM hardware counts.

```bash
python qac_ibm_wavetable_bridge.py --mode local --shots 256
```

Defaults:

```text
QAC QASM input:  127.0.0.1:7411
Wavetable output: 127.0.0.1:7412
```

Point the existing `qac_qasm_sender_v1` Max abstraction at port 7411. Receive
port 7412 and route `/qmw/wavetable/points`; its payload is the revision followed
by exactly 256 floats. Load those floats into a 256-frame `buffer~` and read it
with `wave~` driven by `phasor~`.

If a sender is reloaded with an older revision, restart the bridge or send
`/qmw/wavetable/reset` to port 7411. This clears only in-memory revision state.

For a no-network check using the supplied QAC Bell circuit:

```bash
python qac_ibm_wavetable_bridge.py --qasm \
  ../qac_quantumsonification_bridge_v1/example_qac_bell_4q.qasm
```

IBM Sampler results contain measurement counts, not statevector phase. The
hardware table therefore maps `sqrt(count / shots)` to harmonic magnitude.
The workshop default is deliberately limited to 256 shots. Use `local` mode
for rehearsals and submit only one `both`-mode hardware job for validation.

Hardware submission requires an explicit acknowledgement:

```bash
python qac_ibm_wavetable_bridge.py --mode both --shots 256 --confirm-ibm
```

### QFT transform

Append a quantum Fourier transform after the QAC state-preparation circuit and
before measurement with:

```bash
python qac_ibm_wavetable_bridge.py --mapping counts --transform qft
```

Use `--transform iqft` for the inverse transform and `--transform none` for the
original circuit. The same transformed circuit is used by the local reference
and IBM execution paths, so `both` mode gives a direct ideal-versus-hardware
comparison:

```bash
python qac_ibm_wavetable_bridge.py --mapping counts --transform qft \
  --mode both --shots 256 --confirm-ibm
```

QAC-exported final measurements are removed before the QFT and recreated after
it. Rehearse in local mode before making the single deliberate IBM submission.

### Integrated Max circuit designer

Open `../max/QMW_QAC_Wavetable_Circuit_Designer_v1.maxpat`. It combines the
four-qubit grid, QAC QASM export, wavetable receiver, 256-point buffer, and
oscillator. Choose gates or a preset, then press **SEND QASM**.

- With the Python bridge in its default `local` mode, send as often as needed.
- With the bridge in confirmed `both` mode, every **SEND QASM** creates one IBM
  job. Submit once, wait for the IBM table, then stop the bridge.
- The QAC designer's local simulator and the cloud bridge both use 256 shots in
  this workshop version. The canonical circuit-programmer patches are unchanged.

### Correlation-spectrum mode

For a more quantum-native mapping, derive XX, YY, and ZZ correlations for q0/q1:

```bash
python qac_ibm_wavetable_bridge.py --mapping correlations
```

The three signed correlations control harmonics 1, 2, and 3. An ideal Bell
state has the signature `XX=+1, YY=-1, ZZ=+1`; a separable state has a
different signature even when selected local measurement probabilities look
similar. Local mode uses an ideal statevector and consumes no quota.

One deliberate hardware comparison submits all three basis circuits together
as one Sampler job:

```bash
python qac_ibm_wavetable_bridge.py --mapping correlations \
  --mode both --shots 256 --confirm-ibm
```

### Pauli-15 surface

```bash
python qac_ibm_wavetable_bridge.py --mapping pauli15
```

This fills four audibly distinct 256-sample spectral views of the same 15
Pauli expectations for `2d.wave~`.

For one deliberate local-versus-hardware comparison, submit the nine X/Y/Z
pair-basis circuits together in a single Sampler job:

```bash
python qac_ibm_wavetable_bridge.py --mapping pauli15 \
  --mode both --shots 256 --confirm-ibm
```

The local surface is published immediately and the IBM surface replaces it
when the job finishes. The bridge permits one IBM job per process by default;
restart it for another deliberate submission.

### Optional TEM executor

The `correlations` and `pauli15` mappings can use Algorithmiq's
Tensor-Network Error Mitigation Qiskit Function instead of the direct Runtime
Sampler:

```bash
python qac_ibm_wavetable_bridge.py --mapping correlations \
  --ibm-executor tem --tem-precision 0.1 \
  --mode both --confirm-ibm
```

TEM is lazy-loaded, so ordinary local and Runtime use does not require the
optional `qiskit-ibm-catalog` package. Before a real TEM run, install that
package in the active environment and confirm that `algorithmiq/tem` is enabled
for the default saved IBM Quantum Platform instance. The bridge resolves that
instance's CRN automatically; `--ibm-instance <crn>` can select a different
eligible instance explicitly. The bridge preserves the
existing explicit hardware confirmation and one-job-per-process limit. TEM's
mitigated expectations feed the existing IBM renderer; mitigated values,
standard errors, and unmitigated references are also emitted on
`/qmw/tem/result`.

### V3 compact dual renderer

`QMW_QAC_Wavetable_Circuit_Designer_v3.maxpat` keeps independent local and
IBM buffers and renders them in Max from the compact Pauli-15 descriptor.
Normal V3 operation omits WAV files and 256-value OSC arrays:

```bash
python qac_ibm_wavetable_bridge.py --mapping pauli15 --compact-state
```

For a single hardware comparison add `--mode both --shots 256 --confirm-ibm`.
V3 provides IFFT-like, cyclic-spline, density-matrix-scan, and hybrid modes,
plus local/IBM, spectral/spatial, smooth/detailed, and stable/nonlinear
crossfades. Eigenmode rendering remains a planned mode rather than an
unverified approximation.
