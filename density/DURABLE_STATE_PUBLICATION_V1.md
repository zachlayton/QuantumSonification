# Durable state publication v1

The four-qubit density engine can optionally persist its canonical state and
event history through `DurableStatePublisher`.

```python
from density.density_matrix_engine_4q import DensityMatrixEngine
from density.durable_state_publication_v1 import StatePublicationConfig

engine = DensityMatrixEngine(
    state_publication=StatePublicationConfig(
        directory="output/authoritative_state",
        checkpoint_interval_events=16,
    )
)
```

Persistence is opt-in for backward compatibility. When configured, the output
layout is:

```text
authoritative_state/
  current_state.npz
  current_state.json
  events.jsonl
  states/<session-id>/state_000000000000.npz
  checkpoints/<session-id>/event_000000000016_<type>.npz
```

## Atomic state packets

`current_state.npz` contains canonical `rho`, revision, configuration
revision, logical time, event identity/type, session ID, metadata JSON, and a
SHA-256 of the normalized complex128 matrix. It is written to a temporary file
in the same directory, flushed, and installed with `os.replace`. The JSON
manifest is replaced independently with the same durability procedure.

Immutable revision packets use session-specific paths. Reusing one revision
for a different matrix in the same session is rejected rather than silently
overwriting history.

## Event ledger and checkpoints

Circuit gates, explicit measurement/probe requests, GRW hits, resets, explicit
rotations, and enabled open-system channels append one JSON object to
`events.jsonl`. A single `O_APPEND` write installs each complete record. Every
record has a global monotonic sequence, session ID, state-packet reference,
matrix hash, event metadata, and its own record hash.

`checkpoint_interval_events=0` disables full transition checkpoints. A
positive interval stores `rho_before`, `rho_after`, and `delta_rho` at that
cadence. Reset can force a checkpoint independently.

Continuous frame evolution updates atomic current/revision state packets but
does not create synthetic discrete events in the ledger.

## Deterministic replay

```python
from density.durable_state_publication_v1 import DurableStateReplay

replay = DurableStateReplay("output/authoritative_state")
replay.verify()
for frame in replay.replay():
    use(frame.record, frame.rho)
```

Replay checks ledger ordering and hashes, then checks every state packet's
revision and density-matrix SHA-256. It reconstructs the exact persisted state
for circuit, measurement, and GRW event histories. Session filtering allows
multiple performances to share one append-only ledger without revision-name
collisions.
