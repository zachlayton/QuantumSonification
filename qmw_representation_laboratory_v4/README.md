# QMW Representation Laboratory v4

V4 is the extensible representation-and-measurement architecture. It is
isolated from the working v2 basis laboratory and v3 Max comparator.

## Canonical structure

```text
qmw_representation_laboratory_v4/
├── core/
│   ├── state_transform.py
│   ├── unitary_operator.py
│   ├── measurement_protocol.py
│   ├── experiment.py
│   └── registry.py
├── transforms/
│   ├── identity.py
│   ├── hadamard.py
│   ├── qft.py
│   ├── hamiltonian.py
│   ├── graph_laplacian.py
│   ├── floquet.py
│   ├── grover.py
│   └── epistrophe.py
├── protocols/
│   ├── full_pauli.py
│   └── classical_shadows.py
└── adapters/
    └── full4q_synthesis.py
```

The older flat v4 module names remain as compatibility exports. Canonical new
code should import from `core`, `transforms`, `protocols`, and `adapters`.

## Composition

```text
canonical density
      |
      +-- reference StateTransform (Identity by default)
      |
      +-- experimental StateTransform
                   |
          shared MeasurementProtocol
                   |
          exact + sampled observable comparison
```

`UnitaryOperator` specializes `StateTransform` with:

```text
rho_prime = U rho U_dagger
```

Measurement is intentionally separate. Full Pauli tomography and classical
shadows can therefore measure the same transformed state without pretending
that shadows are a basis transformation.

## Sampling policies

The protocol owns one of three policies:

- `fixed`: every run resolves to the selected seed
- `resample`: every run receives a fresh system-random seed
- `sequence`: a long-lived protocol advances deterministically from its base
  seed

One resolved seed is shared by the reference and experimental sides. This
keeps stochastic differences attributable to the representations rather than
to unrelated random-number streams. Every archived result records the resolved
seed and policy.

Try fixed and resampled Full Pauli experiments:

```bash
python -m qmw_representation_laboratory_v4 \
  --operator graph_laplacian --graph cycle --seed 23

python -m qmw_representation_laboratory_v4 \
  --operator graph_laplacian --graph cycle --resample
```

The exact section remains stable. The sampled section, resolved seed, and
tomography error change under resampling.

## Protocols

### Full Pauli

`FullPauliTomography` delegates density-to-Full4Q conversion to
`Full4QSynthesisAdapter`. Its `shots` value means shots per each of 81 settings,
and its output preserves the established 256-entry Pauli result, including the
identity term.

### Classical shadows

`ClassicalShadowTomography` performs independent random local X/Y/Z
measurements and constructs unbiased Pauli estimators. Its `shots` value means
total random snapshots, not shots per setting:

```bash
python -m qmw_representation_laboratory_v4 \
  --operator graph_laplacian \
  --protocol classical_shadows \
  --shots 4096 \
  --resample
```

Shadow estimates are expected to be noisier at equal numerical shot values
because Full Pauli uses `81 × shots` circuit executions while shadows uses
`shots` total snapshots.

## Transform plug-ins

- Identity
- tensor-product Hadamard
- QFT and inverse QFT
- Hamiltonian eigenbasis
- Graph Laplacian eigenbasis
- Floquet periodic evolution
- Grover oracle/diffusion amplification
- Epistrophē reversible return-map adapter

The CLI provides transverse-Ising Floquet, marked-state Grover, and cyclic-shift
Epistrophē demonstrations:

```bash
python -m qmw_representation_laboratory_v4 \
  --operator floquet --period 0.25 --steps 3

python -m qmw_representation_laboratory_v4 \
  --operator grover_amplified --marked 0,7 --steps 2

python -m qmw_representation_laboratory_v4 \
  --operator epistrophe --steps 4
```

The Epistrophē class does not invent a final theory. It accepts and validates an
explicit user-supplied unitary return map. The CLI cyclic shift is clearly
marked as a demonstration definition.

## Live Hamiltonian control from Max

Start the v4 control service:

```bash
python workshop_lightweight/qmw_representation_hamiltonian_v4.py
```

Then open:

```text
max/QMW_Hamiltonian_Transform_Control_v4.maxpat
```

The controller sends atomic bundles to UDP `7445`:

```text
/qmw/v4/hamiltonian/preview
/qmw/v4/hamiltonian/commit
/qmw/v4/hamiltonian/reset_tracking
```

Each preview or commit bundle contains:

```text
revision
coupling
transverse_field
longitudinal_field
evolution_time
mode
boundary
preset
shots
sampling
seed
```

Preview changes are throttled in Max and recompute the exact density, energy
spectrum, and 255-Pauli difference without running tomography. `COMMIT
TOMOGRAPHY` performs the stochastic 81-setting measurement and publishes the
reference and experimental revisions to UDP `7436` through the existing
`/qmw/tomography/*` contract. The v3 comparator can therefore receive committed
v4 Hamiltonian experiments without any change to its code.

The eigenbasis tracker matches consecutive eigenvectors by overlap, aligns
their complex phases, and aligns degenerate subspaces. Use `reset tracking`
when an intentional discontinuous basis restart is desired.

## Graph Laplacian convention

For adjacency `A`, v4 constructs `L = D - A` or the normalized Laplacian. If:

```text
L = V Lambda V_dagger
```

then:

```text
U_graph = V_dagger
rho_graph = V_dagger rho V
```

Degenerate eigenspaces are stabilized by projecting the computational basis
into each eigenspace. Metadata records connected components and a zero spectral
gap for disconnected graphs. Four-qubit Full4Q experiments require 16 graph
nodes.

## Validation

```bash
python -m unittest \
  qmw_representation_laboratory_v4.test_representation_laboratory_v4 \
  qmw_pauli_basis_laboratory_v3.test_basis_laboratory_v3 \
  qmw_pauli_basis_laboratory_v2.test_basis_laboratory_v2 \
  full4q_tomography_v1.test_full4q_tomography_v1
```
