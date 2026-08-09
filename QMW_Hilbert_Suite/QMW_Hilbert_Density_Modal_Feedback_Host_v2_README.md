# QMW Hilbert Density Modal Feedback Host v2

Version 2 replaces the continuously running sine-partial bank with sixteen
true excitation-driven modal resonators.

Open:

```text
QMW_Hilbert_Density_Modal_Feedback_Host_v2.maxpat
```

## What changed

Version 1 produced each lane with a continuously running sine oscillator:

```text
magnitude * sin(2 pi frequency t + phase)
```

That architecture naturally produced gliding, theremin-like sound. Version 2
contains no free-running oscillator. Each basis lane is now:

```text
quantum-field motion
-> noise excitation envelope
-> damped state-variable resonant mode
-> analytic Hilbert pair
-> complex density operator
-> phase projection
-> causal bounded feedback
```

Magnitude determines modal participation. Changes in magnitude create
strikes. Density-field speed provides sustained breath/bow-like energy. Phase
change contributes a smaller transient. Harmonic ratios set the sixteen modal
frequencies. Purity, entropy, and coherence influence ringing and damping.

## Where is `hilbert~`?

The actual MC object is `mc.hilbert~`; it creates a matched analytic pair for
all sixteen channels. It is nested deliberately:

```text
QMW_Hilbert_Density_Modal_Feedback_Host_v2
└─ qmw_density_matrix_resonator_feedback16_mc_v1
   └─ qmw_density_matrix_hilbert_operator16_mc_v1
      └─ mc.hilbert~
```

Double-click the feedback abstraction in the host, then double-click the
density-matrix Hilbert operator to inspect it. The host face also labels this
path explicitly.

## Safe startup and A/B test

1. Turn the master down from any unusually high setting used with v1.
2. Close other Max patches using UDP port 7400.
3. Start the conductor.
4. Open the v2 host.
5. Wait for the conductor indicator to flash.
6. Click **RAW SAFE**.
7. Enable `ezdac~`.
8. Listen in RAW mode first.
9. Click **LOW FEEDBACK** and compare.

RAW should now sound like struck, breathed, or bowed resonant matter rather
than a phase-gliding oscillator bank. LOW FEEDBACK adds analytic recirculation
after the modal sound has formed.

Click **PANIC + MUTE** if the level or feedback becomes unexpected.

## Important matrix distinction

The active conductor's sixteen-sample analytic `density_field/real` and
`density_field/imag` streams are not a 16×16 density matrix and remain
disconnected from the matrix operator. The complex operator stays on identity
until a genuine 256-cell `/qmw/state/rho/...` or `/qmw/qac/rho/...` pair
arrives.
