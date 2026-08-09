# Qiskit Nature Fermi-Hubbard v1

This package constructs a small open Fermi-Hubbard chain with Qiskit Nature,
maps it through Jordan-Wigner, and exactly diagonalizes a selected particle-number
sector. The output keeps raw physical observables separate from bounded musical
controls.

Energy gaps are represented as continuous frequency ratios and logarithmic
octave coordinates. The core descriptor does not quantize them to semitones or
to any tuning system; tuning belongs in an optional downstream performance layer.

The default is the two-site, two-particle (half-filled) Hubbard dimer with
`t = 1` and `U = 4`. This is small enough to validate against its analytic
ground-state energy before any OSC, synthesis, approximate eigensolver, or
hardware layer is introduced.

Run:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  examples/qiskit_nature_hubbard_demo_v1.py \
  --output outputs/qiskit_nature_hubbard_v1.json
```

Validate:

```bash
MPLCONFIGDIR=/private/tmp/qmw_hubbard_mpl \
/Users/zlayton/miniconda3/envs/music/bin/python -m unittest \
  discover -s tests -p 'test_qiskit_nature_hubbard_v1.py' -v
```

Dependencies: `qiskit-nature==0.8.*`, `qiskit-algorithms>=0.4,<0.5`, and
the existing Qiskit/NumPy/SciPy stack. Qiskit Nature is Apache-2.0 licensed.
