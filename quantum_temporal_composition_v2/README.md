# Quantum Temporal Composition v2 — Correlation / Differentiation Clock

V2 replaces autonomous musical clocks with relational event clocks. The observation loop samples state and carries OSC, but an observation is **not** a tick.

For every clock–subsystem and subsystem–subsystem edge:

```text
C_ij(n)       = instantaneous relational correlation
Delta C_ij(n) = C_ij(n) - C_ij(n-1)
```

Positive change accumulates in a correlation reservoir. Negative change accumulates in a differentiation reservoir. A tick occurs only when one reservoir crosses `change_quantum`; constant state produces no ticks even if sampled indefinitely. Each edge keeps its own integer relational time, and the system also records a causal global tick count.

This is the intended distinction:

- wall time tells the software when to observe;
- Page–Wootters conditioning supplies a clock-relative quantum state;
- correlation and differentiation create musical time;
- Max realizes ticks but does not generate the clock.

## Live launch with the canonical conductor

From the `QuantumSonification` repository root:

```bash
python quantumsonification_conductor.py --with-correlation-clock --daemon
```

Then open:

```text
quantum_temporal_composition_v2/max/QMW_Correlation_Differentiation_Clock_v2.maxpat
```

The conductor launches two connected processes:

1. The canonical engine publishes its live 16 x 16 density matrix privately on UDP 7444.
2. The v2 bridge computes normalized pairwise quantum mutual information for `q0:q1`, `q0:q2`, `q0:q3`, `q1:q2`, `q1:q3`, and `q2:q3`, then publishes relations and event ticks to Max on UDP 7442.

Do not combine `--with-correlation-clock` with `--with-temporal-mechanics`; both consume the private density stream, and the conductor deliberately rejects that ambiguous configuration.

Useful sensitivity controls:

```bash
# Denser clock events
python quantumsonification_conductor.py --with-correlation-clock \
  --correlation-change-quantum 0.005 --daemon

# Isolated ports for testing
python quantumsonification_conductor.py --with-correlation-clock \
  --correlation-state-port 17444 --correlation-clock-port 17442 --daemon
```

The threshold can also be changed while running by sending one float to `/qmw/temporal/v2/control/change-quantum` on the private state port (7444 by default).

## Standalone deterministic launch

```bash
python -m quantum_temporal_composition_v2.quantum_temporal_composition_v2 \
  --config quantum_temporal_composition_v2/example_config_v2.json --print-ticks
```

Fast deterministic inspection:

```bash
python -m quantum_temporal_composition_v2.quantum_temporal_composition_v2 \
  --observations 120 --fast --no-osc --no-log
```

This standalone mode uses the deterministic local source and retains the named `clock`, `resonance`, `memory`, and `spatial` relations visible in printed tick logs. Live conductor mode instead labels relations by the actual qubit pair being measured.

Lower `change_quantum` for denser relational ticks; raise it for sparser time.

## OSC, default `127.0.0.1:7442`

- `/qmw/temporal/v2/snapshot/begin` — observation, global relational time
- `/qmw/temporal/v2/condition` — Page–Wootters phase, confidence, conditional purity
- `/qmw/temporal/v2/relation` — edge, correlation, signed differentiation, two reservoirs, edge time
- `/qmw/temporal/v2/tick` — id, edge, kind, edge time, global time, correlation, differentiation, strength, MIDI, velocity, duration
- `/qmw/temporal/v2/snapshot/end` — observation, global relational time, ticks in snapshot
- `/qmw/temporal/v2/config` — acknowledgement of a live configuration change
- `/qmw/temporal/v2/error` — rejected state or control payload

## Test

```bash
python -m unittest quantum_temporal_composition_v2.test_quantum_temporal_composition_v2 -v
```
