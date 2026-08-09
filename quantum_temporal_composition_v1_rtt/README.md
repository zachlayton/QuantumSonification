# QMW Quantum Temporal RTT Realizer v1

This Max 9 patch receives Quantum Temporal Composition v1 on UDP port 7442 and realizes three independent local-time processes with the Rhythm and Time Toolkit.

## Files

- `QMW_Quantum_Temporal_RTT_v1.maxpat` — standalone Max patch.
- `qmw_relational_phase_unwrap_v1.js` — unwraps radians across `2π` before signal interpolation.
- `build_qmw_quantum_temporal_rtt_v1.py` — deterministic patch generator.

Keep the `.maxpat` and `.js` in the same directory or add this directory to Max's search path.

## Run

From the QuantumSonification repository:

```bash
python -m quantum_temporal_composition_v1.quantum_temporal_composition_v1 \
  --config quantum_temporal_composition_v1/example_config_v1.json
```

Then open `QMW_Quantum_Temporal_RTT_v1.maxpat` and turn on DSP. The patch contains three simple internal oscillator voices at a conservative fixed level, so it is audible without an external MIDI destination; `midiout` remains available for external instruments.

- `/qmw/temporal/v1/clock`
- `/qmw/temporal/v1/conditional/purity`
- `/qmw/temporal/v1/process/resonance`
- `/qmw/temporal/v1/process/memory`
- `/qmw/temporal/v1/process/spatial`
- `/qmw/temporal/v1/event`
- `/qmw/temporal/v1/branch`

Each process phase is unwrapped to estimate its local relational velocity. That velocity controls the BPM of a dedicated `rtt.clock~` for resonance, memory, or spatial state. RTT therefore receives its native phasor contract without a `wrap~`, and there is no shared master clock. The three scopes display the three local RTT clocks directly. Salience is sent to `rtt.rprob~` using its documented `message probabilities` form. Trigger signals are also published inside Max as:

- `qmw.temporal.resonance.trigger`
- `qmw.temporal.memory.trigger`
- `qmw.temporal.spatial.trigger`

The patch expects the Rhythm and Time Toolkit and CNMAT `OSC-route` to be installed.
