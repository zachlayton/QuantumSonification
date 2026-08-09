# Qiskit Nature molecular workflow v1

This phase adds a PySCF-backed H2 bond-length sweep. Each point preserves:

- Hartree-Fock, nuclear-repulsion, exact electronic, and exact total energies;
- particle-sector excited states and excitation gaps;
- electronic, nuclear, and total dipole data;
- Hartree-Fock orbital occupations;
- exact spin-orbital one- and two-body reduced density matrices;
- Hermiticity, particle-number, trace, and RDM-contraction checks.

The descriptor is raw molecular data. It contains no semitone or tuning-grid
quantization and no claim that sampled minimum is a fitted equilibrium geometry.

The dissociation study adds a dense compact `.npz` data archive and two WAVs:
`raw` maps the first three excitation gaps by a documented continuous ratio;
`shaped` applies smooth power-law range compression and correlation-sensitive
orchestration. Neither route rounds to semitones or a tuning grid. The `.npz`
archive, rather than either WAV, remains the canonical dissociation trajectory.

The v2 relational render responds to listening feedback that a gap-to-frequency
mapping produced little more than a descending sine. It uses four fixed carrier
identities. Molecular data changes amplitude, beating, coupling, inharmonic
color, and feature-space-derived articulation timing, but never carrier pitch.

The v3 complete-spectrum route takes all five nonzero excitations in the full
six-state, two-electron STO-3G sector and divides their physical frequencies by
one global constant. At 96 kHz, the maximum is placed at 90% of Nyquist. Ratios
and degeneracies are preserved; components may naturally become sub-audio or
ultrasonic, and nothing is folded into a preferred musical register.

The v4 spectral chamber route is explicitly compositional. It freezes three
H2-derived spectral chords at compressed, equilibrium, and dissociated reference
geometries; uses exact octave registration without a note grid; and articulates
recurring three-part resonant gestures at state-derived times. The v3 spectrum
remains the scientific baseline against which this perceptual layer is audited.

The v5 adapter stops inventing a parallel instrument. Each exact H2 ground-state
density matrix is transformed by the established QMW 16x16-density-to-256-sample
wavetable function. The resulting bank is compatible with the existing Max
wavetable address family. An optional preview uses the canonical grade-one shell
of the existing Wilson six-factor CPS as compositional pitch material; this is
explicitly not an oracle consultation or a physical molecular correspondence.

Run:

```bash
MPLCONFIGDIR=/private/tmp/qmw_h2_mpl \
/Users/zlayton/miniconda3/envs/music/bin/python \
  examples/qiskit_nature_h2_sweep_v1.py \
  --output outputs/qiskit_nature_h2_sweep_v1.json
```
