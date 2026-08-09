# Quantum Temporal Composition System v1

This package composes **relations among evolving states**, not notes against a master transport. A wall-clock observation loop only samples the system and carries OSC; it does not define musical position, bar, beat, or sequence.

## Architecture and reused seams

- `core.py`: incommensurate local processes, Page–Wootters-inspired conditioning, correlation event selection, JSONL snapshots.
- `quantum_sources.py`: deterministic entangled fallback; hot-reloaded NPY/NPZ/JSON density input; `StateBusSource` for the existing `qmw.core.StateBus` / `QuantumStateFrame` seam; and `ExistingEngineSource` for in-process density, MLX, and Qiskit process engines.
- `history.py`: optional bounded Everett-style possibility histories. These are compositional hypotheses, not a claim to simulate literal many-worlds physics.
- `osc_output.py`: versioned Max/MSP contract.
- `quantum_temporal_composition_v1.py`: CLI and JSON configuration.

Repository modules deliberately reused by interface rather than modified: `engine/quantum_engine.py` (public Qiskit circuit), `engine/mlx_quantum_engine.py` (density adapter), `engine/process_graph.py` (topology metadata), `qmw/core/quantum_data_bus.py`, `qmw/core/state_frame.py`, `qmw/core/state_bus.py`, `density/density_matrix_engine*.py`, `density/density_state_injection.py`, `qmw_circuit_bridge.py`, `qasm_circuit_bridge_v1.py`, `eigenfield_timing_layer_v1/`, `operators/living_spectral_geometry_v1.py`, and existing `python-osc` publishers. A running engine can publish a `QuantumStateFrame` into a shared `StateBusSource`; an in-process composer can wrap an engine with `ExistingEngineSource`; a separate process can point `--state-path` at an exported density file or living-state pointer. Sequential edges in `QuantumProcessGraph` describe circuit causality and are retained as metadata; they are not treated as a musical transport.

In-process engine integration:

```python
from engine.quantum_engine import QuantumProcessEngine
from quantum_temporal_composition_v1.core import QuantumTemporalCompositionSystem, TemporalConfig
from quantum_temporal_composition_v1.quantum_sources import ExistingEngineSource

quantum = QuantumProcessEngine(4)
quantum.prepare_zero()
quantum.h(0)
quantum.cx(0, 1)
temporal = QuantumTemporalCompositionSystem(
    TemporalConfig(osc_enabled=False),
    source=ExistingEngineSource(quantum, advance=False),
)
snapshot = temporal.observe()
```

The Page–Wootters estimator factors `rho` as `clock_dim × system_dim`, obtains a clock phase from the reduced clock coherence, constructs a phase-state POVM vector, and computes the conditional musical-system density `rho_system | clock phase`. It is inspired by the relational mechanism; it is not a quantum-gravity solver.

## Launch

From the repository root:

```bash
python -m quantum_temporal_composition_v1.quantum_temporal_composition_v1 --config quantum_temporal_composition_v1/example_config_v1.json
```

Deterministic ten-observation inspection without OSC or real-time pacing:

```bash
python -m quantum_temporal_composition_v1.quantum_temporal_composition_v1 --observations 10 --fast --no-osc --log /tmp/qtc_v1.jsonl --branches
```

Existing density/circuit output (NPY, NPZ with `rho`/`density_matrix`/`density`, or JSON):

```bash
python -m quantum_temporal_composition_v1.quantum_temporal_composition_v1 --source file --state-path path/to/rho.npz --branches
```

## OSC contract (default `127.0.0.1:7442`)

- `/qmw/temporal/v1/snapshot/begin` — observation id
- `/qmw/temporal/v1/clock` — phase, confidence, conditional probability
- `/qmw/temporal/v1/conditional/purity` — conditional system purity
- `/qmw/temporal/v1/process/<name>` — phase, energy, correlation, salience, quantum drive
- `/qmw/temporal/v1/event` — id, process, MIDI note, velocity, duration ms, correlation, relational phase
- `/qmw/temporal/v1/branch` — branch id, parent id, weight, compact history
- `/qmw/temporal/v1/snapshot/end` — observation id

In Max, use `udpreceive 7442` followed by `oscparse` and `route qmw`.

## Snapshot inspection and tests

Each JSONL row contains the clock estimate, conditional purity, source identity, every local process's proper-time increment and correlations, emitted events, and active branches.

```bash
python -m unittest quantum_temporal_composition_v1.test_quantum_temporal_composition_v1 -v
```
