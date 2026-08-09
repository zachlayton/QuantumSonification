# Wilson Quantum Geometry v1

This package is the mathematical seed of a Wilson-inspired layer for QMW. It
implements two complementary geometries:

- **Melodic geometry:** Moments of Symmetry (MOS) and Scale-Tree addresses.
- **Harmonic geometry:** Combination-Product Sets (CPS) represented as
  fixed-excitation subspaces of qubit registers.
- **Perceptual geometry:** Tenney harmonic distance and tolerance, plus the
  Nicholson/Sabat harmonic-intersection and register-tuneability tests.

## The core correspondence

For a master set of `n` Wilson factors, a `k)n` CPS contains all products of
exactly `k` factors. An `n`-qubit register has exactly the same number of basis
states with Hamming weight `k`:

```text
Wilson                         Quantum
master-set factor i       <-> qubit / mode i
k-factor product          <-> weight-k computational basis state
C(n, k) CPS tones         <-> C(n, k)-dimensional excitation shell
replace one factor        <-> excitation-preserving exchange
CPS complement (n = 2k)  <-> bitwise particle-hole complement
tone probability          <-> basis-state probability
tone phase                <-> relative quantum phase
```

The `2)4 1-3-5-7` Hexany is therefore not a mapping of six arbitrarily chosen
states. It is the complete weight-two shell of four qubits. Its edge graph is
the Johnson graph `J(4, 2)`: six vertices, twelve edges, four neighbors per
vertex.

## Quick use

```python
from wilson_quantum_geometry_v1 import CombinationProductSet, make_mos, pascal_cps_row

hexany = CombinationProductSet((1, 3, 5, 7), 2)
print(hexany.name, hexany.dimension, hexany.edges())

scale = make_mos(4 / 3, 7)
print(scale.scale_type)                 # 3/7
print(scale.is_moment_of_symmetry)      # True

print([shell.dimension for shell in pascal_cps_row(6)])
# [1, 6, 15, 20, 15, 6, 1]
```

`CombinationProductSet.project_state()` accepts a normalized `2**n`
statevector. It reports both absolute probability and probability conditioned
on the selected CPS shell. This makes excitation leakage visible instead of
silently renormalizing it away.

Pitch ratios are period-folded relative to a user-selected audition anchor.
The anchor is a rendering convention, not a tonic or privileged graph centre.

## Hear the first study

```bash
python -m wilson_quantum_geometry_v1.hexany_study
```

This renders a stereo `2)4 1-3-5-7` Hexany composition in three operations:
coherent spreading through a perceptually weighted Johnson graph, a bitwise
complement/particle-hole transformation, and a seeded measurement followed by
a slower coda. Exact CPS ratios set pitch; probabilities set energy; relative
phase colors spectrum and stereo position. Notation is intentionally outside
the v1 audio path.

## Run the focused tests

```bash
python -m unittest wilson_quantum_geometry_v1.test_wilson_quantum_geometry_v1 -v
```

## QMW adapter

`WilsonStateAdapter` accepts normalized statevectors, density matrices, or the
canonical `qmw.core.state_frame.QuantumStateFrame`. It publishes exact shell
probability and leakage, conditional shell purity, per-vertex phase coherence,
and a separate attack/persistence activation field. `WilsonOSCPublisher`
exposes the same frame to Max, SuperCollider, and geometry clients through the
[OSC contract](OSC_CONTRACT.md).

## Play Phase 3

Open `max/QMW_Wilson_Hexany_Instrument_Phase3.maxpat` and run:

```bash
env NUMBA_CACHE_DIR=/private/tmp/numba_cache \
  /Users/zlayton/miniconda3/envs/music/bin/python \
  examples/qmw_wilson_hexany_phase3.py
```

Run `processing/QMW_Wilson_Hexany_Flow_v1` for the coupled geometry. Max on
UDP 7420 and Processing on UDP 7411 receive the same revisioned CPS frames;
the instrument sends recursion controls to the dedicated UDP 7433 port.

## Deliberate boundaries in v1

- Quantum phase remains phase. It is not converted into pitch deviation.
- Amplitudes are not added merely because two tones are nearby; interference
  requires an actual shared output mode or a declared quotient map.
- The tuning layer does not claim that Wilson's harmonic geometry is a
  physical model of quantum mechanics. It is a rigorous shared coordinate and
  interaction grammar for composition and sonification.
- The existing all-grades mapping in `qmw/synthesis.py` remains untouched.
  A later adapter should select a CPS grade explicitly and use this kernel.
