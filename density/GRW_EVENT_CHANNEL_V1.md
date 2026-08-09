# GRW event channel v1

`grw_event_channel_v1.py` implements a finite-dimensional, four-qubit
spontaneous-localization instrument. Version 1 uses one-qubit local hits: a
hit selects one constituent and applies one of two unsharp Kraus operators.
Entanglement allows that local event to reorganize the complete state.

The module is a physics/state-transition layer. It has no OSC, synthesis,
pitch, resonator, or geometry mapping.

## Model

For strength `eta`, the Z-frame one-qubit operators are

```
M0 = diag(sqrt((1 + eta)/2), sqrt((1 - eta)/2))
M1 = diag(sqrt((1 - eta)/2), sqrt((1 + eta)/2))
```

and `K(i,b)` embeds `Mb` on qubit `i`. X and Y hits are unitary rotations of
the same complete instrument. `eta=0` is an identity-strength hit and
`eta=1` is projective.

The public configuration retains the requested Hamming-Gaussian `width`.
For a one-bit Hamming distance it maps to strength as

```
eta = tanh(1 / (4 * width**2))
```

`rate_hz` is the per-constituent rate. With four equal qubits, the total event
rate is `4 * rate_hz * constituent_scale`. The scheduler is state independent,
seeded, supports multiple events per processing frame, and advances to each
exact event time before applying a hit.

## State and events

The conductor passes its canonical density matrix to `advance()` and installs
the returned state. Each `GRWEvent` retains `rho_before`, `rho_after`, and
`delta_rho`, plus trace distance, coherence, purity, entropy, population,
local Bloch, mutual-information, concurrence, and the canonical 34 Pauli
deltas. Low-salience events remain in the history with `audible=False`.

The in-memory history can be exported as deterministic JSONL with the RNG
seed. Matrix checkpoints are optional.

## Validation and demo

From the repository root:

```bash
python -m unittest density.test_grw_event_channel_v1
python -m density.grw_event_channel_v1
```

The demo compares no hit, weak hit, strong hit, and projective localization on
the four-qubit GHZ-like state `(0000 + i*1111)/sqrt(2)`.

This is a musically accelerated finite-dimensional analogue. It is not a
claim that qubit basis labels are physical particle positions or that the
configured rates are original GRW parameters.

## Authoritative engine integration

`DensityMatrixEngine` accepts an optional `grw_config`. During `step(dt)` it
applies any due circuit column, evolves the canonical `self.rho` to each exact
GRW event time, installs each `rho_after`, and evolves the frame remainder.
All entanglement metrics, pilot telemetry, and `circuit_state` data are then
derived from that same resulting state.

The state packet includes monotonic `revision`, `logical_time`,
`last_event_id`, `last_event_type`, `configuration_revision`, and a `grw`
record. Event OSC includes `/quantum/grw/event/*` descriptors and the unified
`/quantum/event/type spontaneous_localization` source. The full matrices and
`delta_rho` remain available on `engine.last_grw_event` for an internal
resonator adapter; they are not flattened into the physics channel or mapped
to pitches there.

The existing circuit-control UDP server also routes these controls directly
to the authoritative engine:

```
/quantum/grw/enabled 0|1
/quantum/grw/rate_hz float
/quantum/grw/strength 0..1
/quantum/grw/width positive_float
/quantum/grw/basis X|Y|Z|circuit
/quantum/grw/seed integer
```

Changing a scheduling parameter resamples the next waiting time from the
current logical time. Status values and `next_event_ms` are echoed over OSC.
