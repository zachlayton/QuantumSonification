# QMW Density Matrix → CNMAT Resonant Body v1

This standalone Max instrument stores the canonical engine's live four-qubit
density matrix as one CNMAT `resonators~ smooth` model. All 256 ordered density
relations become `[frequency, gain, decay]` triples.

The model and its excitation are deliberately separate:

- `/qmw/cnmat/density_resonator/begin`, `/row`, and `/end` atomically retune
  the bank without sounding it;
- `/qmw/cnmat/density_resonator/trigger` mirrors the canonical engine's
  threshold-qualified resonance event;
- `/qmw/temporal-mechanics/v1/density-clock/pulse` excites the stored model
  from the independent Quantum Temporal Mechanics clock;
- the patch's manual button and local test remain available without either
  Python process.

## Run

From the repository root, start the canonical engine and QTM bridge together:

```bash
python quantumsonification_conductor.py --with-temporal-mechanics
```

Then open `QMW_Density_CNMAT_Resonator_v1.maxpat`, raise its `live.gain~`, and
enable `ezdac~`. The canonical engine and QTM publisher both arrive on UDP
port `7400`; the engine privately supplies density states to QTM on port
`7444`.

For an audio-path check without Python, press **local model + impulse test**.

## Mapping

The density operator is first rotated into the Hamiltonian energy basis. For
each ordered relation `(m, n)`:

```text
frequency = globally scaled |E_m - E_n|
gain      = L2-normalized |rho[m,n]|
decay     = increasing function of relative |rho[m,n]| and purity
```

Diagonal populations have zero physical transition frequency. They are put
on a low chromatic anchor ladder beginning at 36 Hz, rather than at DC.
Frequency is bounded to 30–8000 Hz, aggregate model gain defaults to `0.42`,
and decay is bounded to `0.08–6.0` seconds.

The triple model cannot carry complex phase directly. The converter retains
phase in its numerical frame so a later stereo/quadrature version can map it
without changing the density-to-resonance contract.
