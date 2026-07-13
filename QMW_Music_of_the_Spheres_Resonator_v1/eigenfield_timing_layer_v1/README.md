# Eigenfield Timing Layer v1

This module turns the output of `quantum_eigenfield_engine_v1.py` into:

- point-density clouds for visualization;
- probabilistic mode triggers;
- eigenvalue-driven durations;
- probability-driven amplitude;
- phase-driven timing displacement;
- ADSR-style envelope parameters.

Place it in:

```text
~/QuantumSonification/geometry/eigenfield_timing_layer_v1.py
```

Install:

```bash
pip install numpy python-osc
```

Run:

```bash
cd ~/QuantumSonification/geometry

python eigenfield_timing_layer_v1.py \
  output/current_quantum_eigenfield.npz \
  --out-port 7440 \
  --control-port 7441 \
  --event-rate 8 \
  --duration-min 35 \
  --duration-max 1800
```

Max:

```text
[udpreceive 7440]
[udpsend 127.0.0.1 7441]
```

## Point-cloud streams

```text
/eigenfield/cloud/x
/eigenfield/cloud/y
/eigenfield/cloud/z
/eigenfield/cloud/eigenvalues
/eigenfield/cloud/frequencies_hz
/eigenfield/cloud/decay_seconds
/eigenfield/cloud/damping_rates
/eigenfield/cloud/material_weights
/eigenfield/cloud/probabilities
/eigenfield/cloud/amplitudes
/eigenfield/cloud/phases
```

The default point coordinates are:

```text
x = normalized log eigenvalue
y = quantum mode probability
z = complex mode phase
```

## Event packet

```text
/eigenfield/time/event
```

Packet order:

```text
mode_index
eigenvalue
probability
phase
amplitude
attack_ms
duration_ms
release_ms
sustain
jitter_ms
frequency_hz
decay_seconds
material_weight
damping_rate
```

The original first ten positions remain unchanged; material fields are
appended for backward-compatible Max `unpack` workflows.

## Controls

```text
/eigenfield/time/control/run 0
/eigenfield/time/control/run 1
/eigenfield/time/control/reload 1
/eigenfield/time/control/status 1
/eigenfield/time/control/event_rate 12.
/eigenfield/time/control/density_gain 0.7
/eigenfield/time/control/duration_min_ms 20.
/eigenfield/time/control/duration_max_ms 2500.
/eigenfield/time/control/phase_jitter_ms 45.
/eigenfield/time/control/amplitude_gamma 0.6
```

## Mapping

```text
quantum mode probability -> event-selection density
mode amplitude magnitude -> envelope peak
eigenvalue spacing       -> duration and release
eigenvalue scale         -> attack
complex phase            -> timing displacement
mode entropy             -> temporal irregularity
effective participation  -> active cloud breadth
```

The layer watches the NPZ file by default. When the quantum eigenfield engine
rewrites it, the point cloud and event distribution are updated automatically.
