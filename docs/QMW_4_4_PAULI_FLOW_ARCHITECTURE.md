# QMW 4_4 Pauli-Flow Architecture

## Goal

Extend the current SuperCollider 4_4 instrument without turning it into a separate Pauli synthesizer. The quantum layer should determine how excitation energy moves through the existing temporal / modal / surface / spatial instrument.

Core principle:

`quantum state -> interaction geometry -> directed transport -> excitation transfer -> existing 4_4 resonant field`

## Mathematical core

For four qubits:

- Hilbert dimension: 16 computational basis states.
- Full Pauli basis: 256 strings, 255 non-identity strings.
- Weight-4 X/Y/Z-only sector: 81 strings.

Hamiltonian decomposition:

`H = sum_P h_P P`

Density-matrix Pauli coordinates:

`r_P = Tr(rho P)`

Closed-system evolution:

`drho/dt = -(i/hbar) [H, rho]`

Directed basis-state current:

`J(i -> j) = (2/hbar) Im(H_ij * rho_ji)`

Pauli-resolved current contribution:

`J_P(i -> j) = (2/hbar) Im(h_P * P_ij * rho_ji)`

Observable / Pauli-coordinate flow:

`d< Q >/dt = (i/hbar) Tr(rho [H,Q])`

For `Q = P`:

`dr_P/dt = (i/hbar) <[H,P]>`

## Architectural rule

Do not map Pauli strings directly to oscillators, pitches, or arbitrary control parameters.

Instead, derive four classes of control data:

1. **State** — where excitation is distributed now.
2. **Current** — where excitation is moving.
3. **Pauli field** — which interaction/correlation structures are active and changing.
4. **Events** — sparse threshold/crossing events extracted from current.

The existing 4_4 sound engine remains the acoustic body.

## Proposed code structure

```text
qmw/
  quantum/
    pauli_basis.py
    pauli_decompose.py
    hilbert_current.py
    pauli_flow.py
    observables.py
    diagnostics.py

  flow/
    frame.py
    spatial_current.py          # existing GPE/current implementation
    regional_flux.py            # existing region/continuity implementation
    hilbert_current.py          # discrete 16-node current graph facade
    current_events.py

  bridge/
    qmw_4_4_frame.py
    qmw_4_4_mapping.py
    qmw_4_4_osc.py

supercollider/
  4_4/
    qmw_4_4.scd                # existing instrument entry point
    qmw_4_4_quantum_buses.scd
    qmw_4_4_current_router.scd
    qmw_4_4_pauli_field.scd
    qmw_4_4_event_router.scd
```

Names should be adapted to the actual repository layout rather than imposed blindly.

## Python-side data model

### `QuantumTransportFrame`

```python
@dataclass(frozen=True)
class QuantumTransportFrame:
    t: float
    populations: np.ndarray          # shape (16,)
    coherence_norm: float
    purity: float

    # Sparse directed edge representation
    currents: tuple[CurrentEdge, ...]

    # Aggregates by Pauli weight 1..4
    pauli_weight_activity: np.ndarray  # shape (4,)

    # Only top-K dynamically significant strings for OSC
    active_paulis: tuple[PauliActivity, ...]

    continuity_error: float
```

### `CurrentEdge`

```python
@dataclass(frozen=True)
class CurrentEdge:
    src: int
    dst: int
    current: float
    dominant_pauli: str | None
    dominant_contribution: float
```

### `PauliActivity`

```python
@dataclass(frozen=True)
class PauliActivity:
    label: str              # e.g. "XYXY"
    weight: int
    expectation: float      # r_P
    derivative: float       # dr_P/dt
    h_coeff: float
    transport_activity: float
```

## Module responsibilities

### `pauli_basis.py`

- Generate / cache the four-qubit tensor-Pauli basis.
- Encode labels and weight.
- Distinguish diagonal strings (`I/Z` only) from transport-capable strings containing `X` or `Y`.
- Cache matrices or sparse action tables where useful.

### `pauli_decompose.py`

- Compute `h_P` for a supplied Hamiltonian if needed.
- Compute `r_P = Tr(rho P)`.
- Support full 255-string analysis internally.
- Avoid streaming all 255 values over OSC.

### `hilbert_current.py`

Primary new physics module.

```python
def current_matrix(rho, H, hbar=1.0) -> np.ndarray:
    """Return antisymmetric 16x16 directed probability-current matrix."""


def sparse_currents(rho, H, eps=1e-9) -> list[CurrentEdge]:
    """Return only dynamically active edges."""


def pauli_resolved_current(rho, pauli_term, coeff, hbar=1.0):
    """Return J_P(i,j) for one Hamiltonian Pauli term."""
```

Required invariant:

`J[i,j] = -J[j,i]`

Node continuity:

`d rho_ii / dt ~= sum_j J[j,i]`

### `pauli_flow.py`

```python
def pauli_expectations(rho, basis): ...
def pauli_derivatives(rho, H, basis, hbar=1.0): ...
def rank_pauli_activity(..., top_k=8): ...
```

Ranking should initially use a physically interpretable score rather than a hand-tuned sonic heuristic, for example:

`score_P = |dr_P/dt| + lambda * sum_ij |J_P(i,j)|`

Keep each component available separately so the ranking can be changed later.

### `diagnostics.py`

Add tests analogous to the existing GPE continuity diagnostics:

1. Hermiticity of `rho` and `H`.
2. Trace preservation.
3. Current antisymmetry.
4. Node continuity.
5. Numerical derivative of `<Q>` agrees with `(i/hbar)<[H,Q]>` for controlled unitary tests.
6. Sum of all node-population derivatives is zero for closed-system unitary evolution.

## 4_4 mapping layer

The bridge must keep **quantum state space** distinct from **acoustic mode space**.

Do not require 16 quantum states = 16 oscillators.

Recommended first version:

- 16 computational-state reservoirs.
- 32 acoustic/modal voices remain possible.
- Each reservoir maps to a pair or geometry-selected family of modal voices.
- Population determines available excitation energy, not raw oscillator amplitude.
- Current transfers energy between reservoirs / modal families.
- Pauli weight determines spatial / structural scale of transformation.
- `dr_P/dt` drives slower spectral morphology after current-triggered transients.

### Suggested mapping semantics

| Quantum quantity | 4_4 role |
|---|---|
| `rho_ii` | reservoir energy / excitation availability |
| `J_ij` | directed transfer between modal families |
| `abs(J_ij)` | transfer strength / excitation energy |
| `sign(J_ij)` | direction |
| `r_P` | active relational pressure / interaction presence |
| `dr_P/dt` | continuing spectral / morphological trajectory |
| Pauli weight 1 | local transformation |
| Pauli weight 2 | pair coupling / sympathetic exchange |
| Pauli weight 3 | cluster deformation |
| Pauli weight 4 | whole-field transformation |
| commuting sector | stable / invariant resonant skeleton |
| noncommuting sector | transformation / movement |

## SuperCollider control architecture

Create four conceptual control groups rather than a 255-channel Pauli bus:

```text
QuantumStateBus
QuantumCurrentBus
PauliFieldBus
QuantumEventBus
```

### State bus

Slow controls:

- 16 populations (or compressed reservoir controls if needed)
- purity
- coherence summary

### Current bus

Use sparse active edges. SuperCollider should receive only the strongest `K` currents per frame or event window.

Each edge carries:

```text
src, dst, signed_current, dominant_pauli_id
```

### Pauli field bus

Transmit top-K active strings only:

```text
pauli_id, weight, expectation, derivative, h_coeff, transport_activity
```

### Event bus

Sparse onset / crossing message:

```text
src, dst, magnitude, sign, pauli_id
```

This bus should create articulations without forcing every current fluctuation to become a note onset.

## OSC proposal

Keep the synchronized / atomic-frame principle already used elsewhere in QMW.

Possible address family:

```text
/qmw/4_4/frame/meta
/qmw/4_4/state/pop
/qmw/4_4/state/summary
/qmw/4_4/current/edge
/qmw/4_4/pauli/active
/qmw/4_4/event/transfer
/qmw/4_4/diagnostics
```

Do not finalize addresses until the current 4_4 OSC contract is inspected.

## Phased implementation

### Phase 1 — physics-only prototype

Implement and test:

- Pauli basis utilities.
- `J_ij` current matrix.
- sparse edge extraction.
- Pauli expectations `r_P`.
- Pauli derivatives `dr_P/dt`.
- node continuity and commutator diagnostics.

No SuperCollider changes yet.

### Phase 2 — transport frame / OSC contract

Create one atomic `QuantumTransportFrame` and bounded OSC serialization.

Requirements:

- stable ordering;
- bounded top-K outputs;
- no full-density-matrix transmission;
- no 255-value continuous Pauli dump;
- explicit diagnostics.

### Phase 3 — 4_4 integration

Add SuperCollider buses and event routing while preserving the existing synthesis architecture.

First perceptual test:

- keep modal frequencies fixed;
- let quantum current alter only excitation transfer and spatial trajectory;
- compare against current 4_4 behavior.

### Phase 4 — Pauli morphology

Add slow `dr_P/dt`-driven spectral / surface transformations.

This is where weight-4 strings such as `XYXY` and `ZZXX` should affect whole-field morphology rather than become independent voices.

## First acceptance experiment

Use a deliberately small Hamiltonian:

```text
H = a * XYXY + b * IXXX + c * ZZXX
```

Prepare several controlled initial states and verify:

1. Which computational-basis pairs each term connects.
2. The sign and magnitude of `J_ij`.
3. Pauli-resolved contributions sum to total current.
4. Node continuity holds.
5. 4_4 produces transfer / spectral evolution rather than a simple note-per-Pauli mapping.
6. The same instantaneous populations can sound dynamically different when the current directions differ.

## Non-goals

- Do not build another Complex Pauli Synth.
- Do not map 81 strings to 81 oscillators.
- Do not increase qubit count merely to obtain more acoustic voices.
- Do not replace geometry-derived modal frequencies with Pauli expectation values.
- Do not turn every current fluctuation into an impulse.
- Do not break the existing synchronized flow / frame architecture.

## Immediate next coding task

Before touching SuperCollider, locate the current `4_4` entry point and its OSC/control-bus contract. Then implement `hilbert_current.py` and a minimal deterministic unit test using a 2-qubit toy case followed by the full 4-qubit 16-node case.
