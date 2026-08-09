# QMW QPE Synthesizer v1

This instrument turns the actual finite-register outcome law of Quantum Phase
Estimation into a playable probabilistic sequencer. It does not simply round an
eigenphase: non-representable phases produce the correct Dirichlet-kernel side
lobes, and trial-state eigencomponents are selected with Born probabilities.

## Play it in Max 9

1. Open `QMW_QPE_Synthesizer_v1.maxpat`.
2. Enable the speaker button (`ezdac~`).
3. Toggle **RUN SHOTS**, or press the round button for one measurement.
4. Move the four eigenphase bars and four trial-state weight bars.
5. Change **estimation qubits** from 2–10. More qubits give finer phase and
   pitch resolution; off-grid phases can still produce neighboring outcomes.

The patch uses only standard Max objects and its local JavaScript controller.
The phase-register plot shows the conditional distribution for the eigenstate
that collapsed on the most recent shot.

## Quantum-to-sound mapping

For each eigencomponent,

```text
U|u_j> = exp(2*pi*i*phi_j)|u_j>
|psi> = sum_j c_j |u_j>
```

one clock pulse performs this joint sample:

```text
j ~ categorical(|c_j|^2)
y ~ |(1/N) sum_(k=0)^(N-1) exp(2*pi*i*k*(phi_j-y/N))|^2
measured phase = y/N,  N=2^m
```

The measured phase maps exponentially across the pitch span. The exact
eigenphase sets stereo position, Born weight contributes to note strength, and
the phase-register bit string is displayed after every shot. This makes the
instrument's uncertainty structural rather than decorative.

## Verify and render

From the repository root:

```text
python3 -m unittest qpe_synthesizer_v1.test_qpe_model
python3 qpe_synthesizer_v1/render_qpe_demo.py
```

The 18-second demo begins at three estimation qubits and adds one qubit every
three seconds, making the phase lattice progressively finer.

## Scope

This is an ideal, noiseless QPE measurement model. It models finite phase
register precision and trial-state overlap, but not gate errors, decoherence,
imperfect controlled-unitary synthesis, or iterative/Bayesian QPE variants.
