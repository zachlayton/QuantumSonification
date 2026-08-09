# QMW Temporal Crystal 16 v1

This bundle establishes a dynamic temporal layer for the four-qubit Quantum
Material Workstation while preserving the canonical live state:

```text
four-qubit musical system S
        =
16 basis states
        =
16 x 16 density matrix rho
        =
256 complex values
```

Python wall time only paces calls to `step()`. The state changes through an
explicit unitary/channel law at a fixed logical interval. Clock registers,
history snapshots, and temporal analyses remain separate from `rho`.

## Included modules

- `qmw_temporal_core16_v1.py`
  - q0 is the least-significant basis bit.
  - Pauli/operator construction, unitary evolution, density validation.
  - `BasisClock16`, `RevisionedDensityState`, `ClockFrame`, `HistoryBank`.
  - One writer commits the central density matrix by revision.

- `qmw_lfsr_clock4_v1.py`
  - Primitive polynomial `x^4 + x + 1`.
  - Exact 15-state nonzero orbit with `0000` fixed.
  - `P_A ~= X_15 direct-sum 1`.
  - `rho -> P_A rho P_A^dagger`.
  - The 120 Hermitian coherence edges form eight 15-edge orbits.
  - Builds the 256 x 256 eight-qubit internal clock-system unitary using
    `joint_index = system_index + 16 * clock_index`.

- `qmw_debruijn_clock4_v1.py`
  - Nonlinear/table-defined full sixteen-state alternative.
  - Every four-bit word, including `0000`, occurs once per cycle.

- `qmw_subharmonic_pythagorean_quantum_time_v1.py`
  - Exact rational period ratios and integer phase positions.
  - `tau_(p:q) = (p/q)T`, `omega_(p:q) = (q/p)Omega`.
  - Optional Hamiltonian coupler using cosine/sine phase quadratures.
  - Exact Pythagorean comma helper.

- `qmw_floquet_time_crystal16_v1.py`
  - One fixed kicked-Ising `U_F` repeated each drive period.
  - Four-spin interactions, disorder, imperfect global pi pulse.
  - Magnetization trajectory, rational-frequency order parameter, rigidity
    sweep, interaction comparison, return overlap, and quasienergy pairing.
  - Reports finite-size candidate signatures only.

- `qmw_temporal_engine16_v1.py`
  - Unified logical-step engine with one density-state writer.
  - Explicit protocol provenance:
    - observer-only,
    - programmed LFSR recurrence,
    - programmed Pythagorean drive,
    - repeated single-period Floquet map.
  - Read-only Kairos event detector and Aion spectrum summary.

- `qmw_temporal_osc16_v1.py`
  - Optional `python-osc` publication on port 7400.
  - Publishes temporal descriptors under `/qmw/time/*`.
  - Does not replace the existing authoritative density-matrix OSC stream.

- `qmw_live_integration16_v1.py`
  - Adapter for `density.DensityMatrixEngine`.
  - Accepts the live canonical `rho` and revision instead of creating a second
    state owner.
  - Reuses the density engine's existing OSC client.
  - Observer mode advances clocks and descriptors without mutating `rho`.

## Scientific claim boundary

Three forms of recurrence are intentionally kept distinct.

### Programmed LFSR recurrence

The register follows a known finite-field permutation. Its period and spectral
roots are exact consequences of the feedback polynomial.

### Programmed Subharmonic Pythagorean Time

The phase advance `2*pi*q/p` is deliberately supplied. It is a compositional
rational clock and Hamiltonian-control geometry.

### Floquet candidate response

The same `U_F` is applied every base period. A peak at `Omega/n`, quasienergy
`n`-tuple structure, perturbation locking, interaction dependence, lifetime
scaling, and system-size scaling are the relevant evidence. This four-qubit
module can test the first four items but cannot establish a thermodynamic
discrete time-crystalline phase.

`Aion detects periodicity; robustness and many-body scaling establish its
origin.`

## Exact clock relations

The score clock and maximal four-bit LFSR have periods 16 and 15:

```text
Z_16 x Z_15 ~= Z_240
```

They visit 240 joint positions before returning. Adding only the triadic
three-cycle does not extend this because 3 divides 15.

The default SPQT ratio collection also includes the `9:8` period orbit. With
the 16-position basis clock and 15-state LFSR its full least-common-multiple is
720 ticks.

## Run

From the bundle directory:

```bash
python examples/run_temporal_bundle_demo.py
```

With a finite pulse error and a JSON report:

```bash
python examples/run_temporal_bundle_demo.py \
  --periods 64 \
  --pulse-error 0.03 \
  --json temporal_demo_report.json
```

Run all tests:

```bash
python -m unittest discover -s tests -v
```

Only NumPy is required. `python-osc` is optional.

## Integration into the existing QMW engine

The existing population/density-matrix engine remains authoritative. The live
engine now accepts an optional `temporal_layer` and applies it after its
circuit, measurement, environmental, Hamiltonian, and GRW stages but before
metrics and OSC publication.

The normal live entry point is the conductor. Begin with observer mode:

```bash
python quantumsonification_conductor.py \
  --with-temporal-crystal \
  --temporal-crystal-mode observer \
  --temporal-crystal-rate 2
```

Observer mode advances logical clocks and `/qmw/time/*` descriptors but does
not mutate `rho`. Once that stream is visible in Max, select `floquet`, `lfsr`,
or `pythagorean`. The temporal rate is accumulated independently from the
canonical engine frame rate.

For the first audible test, open:

```text
max/QMW_Temporal_Crystal16_CNMAT_Resonator_v1.maxpat
```

It retunes 256 CNMAT resonances from canonical `rho` and converts each
`/qmw/time/chronos/tick` into one bounded impulse. Close other Max patches that
bind UDP `7400` before opening it.

Observer-only integration changes no density-matrix physics:

```python
from density.density_matrix_engine_4q import DensityMatrixEngine
from qmw_temporal_crystal16_v1 import build_live_temporal_layer

engine = DensityMatrixEngine(
    temporal_layer=build_live_temporal_layer("observer", rate_hz=2.0),
    enable_circuit_bridge_control=False,
)
for _ in range(50):
    rho = engine.step(0.01)
```

To apply the repeated single-period Floquet map to the live canonical state:

```python
from density.density_matrix_engine_4q import DensityMatrixEngine
from qmw_temporal_crystal16_v1 import build_live_temporal_layer

engine = DensityMatrixEngine(
    temporal_layer=build_live_temporal_layer("floquet", rate_hz=2.0),
    enable_circuit_bridge_control=False,
)
for _ in range(50):
    rho = engine.step(0.01)
```

The opt-in layer records its protocol, clocks, Kairos events, and revision in
`engine.circuit_state["temporal"]` and publishes descriptors under
`/qmw/time/*`. The existing density OSC stream remains authoritative.

For the MLX engine, use these NumPy modules as the reference and port the
operations into MLX arrays inside its canonical `step(dt)`. Preserve the
intended ordering:

```text
drift / Hamiltonian construction
    -> explicit circuit column, measurement, or collapse mutation
    -> selected temporal evolver
    -> validate and commit one rho revision
    -> metrics / memory / trajectory / EventDetector
    -> OSC publication
```

Temporal analyzers remain observers until a deliberate feedback route is added.

## OSC namespace

Selected addresses:

```text
/qmw/time/revision
/qmw/time/protocol
/qmw/time/chronos/tick
/qmw/time/chronos/index
/qmw/time/lfsr/state
/qmw/time/lfsr/bits
/qmw/time/lfsr/phase
/qmw/time/spqt/macrocycle_position
/qmw/time/spqt/<ratio>/phase
/qmw/time/kairos/event
/qmw/time/aion/target_frequency
/qmw/time/aion/target_amplitude
/qmw/time/aion/peak_to_background
```

The established `rho_real` and `rho_imag` 256-value row-major messages should
continue to come from the central state server.

## Next research modules

The shared analyzer already accepts arbitrary rational target frequencies
`q/p`. The next model-specific additions should be:

1. Higher-order `Z_n` Floquet models using qudits or clock variables.
2. Clean/prethermal and disordered comparisons across increasing system size.
3. Two-frequency quasiperiodic drives with a frequency-lattice analyzer.
4. Process-tensor/open-system histories for cross-time coherence.
5. Non-Abelian internal/topological sectors kept distinct from ordinary
   one-generator time translation.
