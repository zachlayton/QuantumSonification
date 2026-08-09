# QMW Pauli Basis Laboratory v2

This package introduces the representation layer between canonical quantum
material and the existing Full4Q tomography instrument:

```text
Quantum source
    ↓
canonical density matrix ρ
    ↓
BasisOperator representation
    ↓
unchanged 81-setting Full4Q tomography
    ↓
unchanged 255-Pauli / shell / synthesis data
```

The first implementation deliberately covers Layers 2–4 and 7 of the larger
instrument architecture. Observable-family browsers, free mapping, Wong
presets, historical memory operators, and the final sound layer remain future
consumers of the same interface.

## Representation semantics

Every basis implements:

```python
rho_prime = basis.transform(rho)
```

using:

```text
ρ' = U ρ U†
```

This is a **passive representation convention** in the laboratory. The
canonical physical density matrix remains the source material; `rho_prime` is
the same material written in the active laboratory coordinates.

The distinction matters for observables:

- `basis.transform_observable(O)` returns `U O U†`, the same physical
  observable carried into the new coordinates. Its expectation is invariant.
- `basis.pullback_observable(P)` returns `U† P U`, which explains what a fixed
  Pauli axis in the experimental coordinates measures in canonical
  coordinates.

The second operation is why an unchanged 81-Pauli measurement family produces
a different observable landscape after a basis selection.

## Initial operators

- `IdentityBasis` — canonical computational representation
- `HadamardBasis` — tensor-product Hadamard on all four qubits
- `QFTBasis` — full 16-dimensional QFT using Qiskit's phase convention
- `HamiltonianEigenbasis` — ascending energy eigenvectors for a supplied
  Hermitian Hamiltonian

The `HamiltonianEigenbasis` stores `V†` when the columns of `V` are the
Hamiltonian eigenvectors. Therefore `U H U†` is diagonal in energy order.

## Run a comparison

From the repository root:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  -m qmw_pauli_basis_laboratory_v2 \
  --preset ghz \
  --basis qft \
  --shots 256 \
  --seed 23 \
  --output qmw_pauli_basis_laboratory_v2/runs/ghz_qft.json
```

Other initial basis names are `identity`, `hadamard`, and `hamiltonian`.

The saved laboratory archive contains:

- the canonical and experimental exact density matrices;
- `computational_basis`, a normal
  `qmw.full4q.tomography.v1` `TomographyResult`;
- `experimental_basis`, a second normal `TomographyResult`;
- exact and sampled comparisons for all 255 non-identity Pauli terms;
- density distance, observable-change, and tomography-error metrics.

## Python API

```python
from qmw_pauli_basis_laboratory_v2 import QFTBasis, run_basis_laboratory

laboratory = run_basis_laboratory(
    QFTBasis(),
    preset="ghz",
    shots=256,
    seed=23,
)

computational, experimental = laboratory.tomography_outputs()
```

Both returned objects retain the exact v1 Full4Q shape:

- 81 `XXXX` … `ZZZZ` setting rows;
- 16 count bins per row in Qiskit integer order;
- 256 saved Pauli coefficients, including `IIII`;
- 255 musically variable coefficients when published by the v1 OSC publisher;
- five correlation shells and the existing reconstruction metrics.

This means a consumer that already accepts `TomographyResult` does not need a
new data schema.

## Full4Q / OSC integration

The package reuses `full4q_tomography_v1.reconstruct_tomography` for each side
of the comparison. The established setting-to-Pauli reconstruction, physical
density projection, shell calculation, and `TomographyOSCPublisher` transaction
remain unchanged.

Each result can be sent through the existing publisher:

```python
from full4q_tomography_v1.osc_service import TomographyOSCPublisher

computational, experimental = laboratory.tomography_outputs()
TomographyOSCPublisher(port=7436).publish(computational, revision=100)
TomographyOSCPublisher(port=7438).publish(experimental, revision=100)
```

Use separate receivers or ports for simultaneous views. The current
`QMW_Full4Q_Tomography_81_v1/v2` Max receivers intentionally classify sources
as **local** versus **IBM**; feeding both basis results into that one receiver
would conflate basis comparison with hardware comparison. A later
basis-laboratory Max view should label the two streams **Computational** and
**Experimental**, while retaining the same atomic `begin`/81 settings/255
Paulis/5 shells/metrics/`end` transaction on each side.

## Validate the interface

Run all four initial operators through invariant checks and sampled Full4Q
comparisons:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  -m qmw_pauli_basis_laboratory_v2.validation \
  --preset ghz \
  --shots 1024 \
  --output qmw_pauli_basis_laboratory_v2/runs/validation.json
```

Validation checks:

- `U U† = I`;
- Hermiticity, trace, positivity, and spectrum preservation;
- covariant-observable expectation invariance;
- fixed-Pauli/pullback expectation equivalence;
- sampled tomography error against the exact Pauli landscape;
- the largest computational-to-experimental observable changes.

Focused tests:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python \
  -m unittest qmw_pauli_basis_laboratory_v2.test_basis_laboratory_v2
```

## Adding a future basis

Only `unitary(dimension)` is required:

```python
from qmw_pauli_basis_laboratory_v2 import BasisOperator


class FutureBasis(BasisOperator):
    name = "future"
    description = "A new playable representation."

    def unitary(self, dimension):
        return build_unitary_for_dimension(dimension)
```

The inherited `transform`, observable covariance, pullback, unitary
validation, laboratory comparison, and Full4Q reconstruction then work without
changing the downstream synthesis pipeline. Graph Laplacian, Floquet,
Page–Wootters, Grover-amplified, shadow-tomography, and epistrophē/history
operators can all enter through this boundary.
