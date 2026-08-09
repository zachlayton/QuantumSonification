# QMW Hilbert Harmonic-Modal Monitor Host v3

Version 3 is designed as a musically coherent quantum-state monitor rather
than a maximally sensitive sonification.

Open:

```text
QMW_Hilbert_Harmonic_Modal_Monitor_Host_v3.maxpat
```

## Stable reference model

The fundamental and its first sixteen exact harmonics form an audible
reference lattice:

```text
f_i = fundamental * (i + 1),  i = 0..15
```

The conductor's Hamiltonian/gap ratios can deform that lattice, but the
**Harmonic Lock** control makes the amount explicit:

```text
effective ratio = mix(conductor gap, exact harmonic, Harmonic Lock)
```

The default lock is now `1`, preserving the completely fixed harmonic spectrum
that proved most musically legible. Lower it deliberately when gap deformation
is wanted.

## Interpretable quantum mapping

- Population magnitude determines which harmonic modes participate.
- Population change strikes the corresponding modes.
- Density-field velocity supplies restrained breath/bow articulation.
- Entropy increases damping and spectral diffusion.
- Purity and coherence extend ringing and modal definition.
- Phase primarily rotates the analytic field in the Hilbert feedback stage.
- A genuine 256-cell density matrix controls cross-basis complex coupling
  when that stream is available.

The reference tone does not receive the conductor's phase value. This avoids
the earlier theremin-like phase glide. Quantum phase is reserved for the
analytic Hilbert projection. Around the stable carrier, the noise-excited
modal component makes state motion physically expressive.

This separation is intentional. Pitch supplies a stable coordinate system;
quantum behavior supplies participation, energy, articulation, damping,
analytic phase, and coupling.

## Front-panel controls

- **fundamental Hz** — common musical pitch reference; default 55 Hz.
- **Harmonic Lock** — `1` is exact harmonics; `0` follows gap ratios fully;
  default `1.0`.
- **Reference Tone** — level of the stable harmonic carrier; default `0.20`.
- **Motion Drive** — sustained excitation from state velocity; default
  `0.10`.
- **Ring Decay ms** — modal temporal memory; default `1250` ms.
- **Noise Floor** — audibility of a static state; default `0.0002`, nearly
  silent.
- **Feedback Depth** — scales coherence-following feedback above the known
  `0.03` baseline; default `0.5`. Set it to `0` to reproduce the earlier fixed
  feedback amount exactly.

Feedback gain is generated from the conductor's coherence and entropy:

```text
gain = 0.03 + FeedbackDepth * 0.09 * coherence * (1 - 0.6 * entropy)
```

The result is emitted as an explicit sixteen-value gain list to inlet 5 and is
hard-capped at `0.15`. RAW SAFE and PANIC still close the feedback gate
independently of the calculated value.

The fundamental, Harmonic Lock, and the conductor's sixteen-value
`/qmw/density_field/harmonics` field feed
`qmw_harmonic_delay_list16_v1.js`. It calculates the same effective ratios as
the audio engine:

```text
ratio[i] = mix(engine_ratio[i], i + 1, Harmonic Lock)
delay[i] = 1000 / (fundamental * ratio[i]) ms
```

The resulting list is visibly connected to inlet 6 of the feedback
abstraction. It updates when the engine ratio field, fundamental, or Harmonic
Lock changes. The LOW FEEDBACK button re-emits the current engine-derived list
before opening mode 2. Delay control no longer relies on the hidden `tune`
message path.

## Listening sequence

1. Close v1 and v2 so only v3 owns UDP port 7400.
2. Start the conductor and open v3.
3. Turn the master down before enabling DSP.
4. Wait for the conductor indicator.
5. Click **RAW SAFE**, then enable `ezdac~`.
6. Listen with Harmonic Lock at `1` and Motion Drive at `0.10`.
7. Click **LOW FEEDBACK** with Feedback Depth at `0`; this reproduces the fixed
   `0.03` baseline.
8. Raise Feedback Depth toward `0.5`, then `1`, to hear coherence and entropy
   control the strength of analytic recirculation.
9. Lower Harmonic Lock only when you want controlled gap deformation.

This sequence separates three effects cleanly:

```text
fixed harmonic monitoring
-> controlled Hamiltonian deformation
-> complex Hilbert feedback
```

Use **PANIC + MUTE** if the feedback or level becomes unexpected.

## Hilbert location

The host labels the analytic path explicitly. The real object is nested here:

```text
qmw_density_matrix_resonator_feedback16_mc_v1
└─ qmw_density_matrix_hilbert_operator16_mc_v1
   └─ mc.hilbert~
```

Double-click the two abstractions to inspect it.
