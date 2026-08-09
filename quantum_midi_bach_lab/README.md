# Quantum MIDI / bach Lab

This Max 9 patch represents a single qubit under a live, three-axis Hamiltonian or follows qubit 0 from the QuantumSonification Conductor.

- `|0>` is MIDI note C4 on channel 1.
- `|1>` is MIDI note G4 on channel 2.
- MIDI velocity is `sqrt(probability) * 127`, corresponding to amplitude magnitude.
- In LOCAL mode, `Hx`, `Hy`, and `Hz` define the Hamiltonian rotation vector in radians per step.
- In LOCAL mode, `MEASURE AXIS` selects X, Y, or Z and `MEASURE` samples the corresponding Born probability. Evolution resumes from the collapsed state on the next step.
- `T1` relaxes toward `|0>` and `T2` damps transverse coherence; zero disables either process.
- `RESET` prepares the local qubit in `|0>` again.
- `bach.roll` accumulates a two-voice history. Note slots 1 and 2 retain probability and phase.
- The optional `RAVE / nn~` branch maps the Bloch vector `(x, y, z)` onto the first three latent dimensions of the installed `wheel` neural-audio model.
- CONDUCTOR mode receives `/qmw/qubit/0/bloch` from UDP port 7400 and bypasses the local Hamiltonian integrator.

## Run

1. Open `Quantum_MIDI_Bach_Lab.maxpat` in Max 9.
2. In edit mode, double-click `noteout` and select a synth or virtual MIDI destination.
3. Lock the patch and enable `RUN`.
4. Leave `CONDUCTOR` enabled to follow the running engine, or disable it to use the local `Hx/Hy/Hz` controls.
5. In LOCAL mode, change the Hamiltonian, add optional `T1/T2`, select a measurement axis, and press `MEASURE`.
6. Enable `RAVE / nn~` to hear the same trajectory as a neural timbre. Begin at low monitor volume.

The patch requires bach, odot (`o.route`), and nn~ plus `wheel.ts`; all are already present in this Max setup. The MIDI and neural-audio paths are independent, so either one can be used alone.

Conductor currently publishes state but does not expose a remote measurement/collapse endpoint. Therefore `MEASURE` is deliberately local-only. In CONDUCTOR mode it reports this limitation without fabricating a state change.
