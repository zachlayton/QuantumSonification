# Eigenfield Timing Layer v1

This module turns the output of `quantum_eigenfield_engine_v1.py` into:

- point-density clouds for visualization;
- probabilistic mode triggers;
- eigenvalue-driven durations;
- probability-driven amplitude;
- phase-driven timing displacement;
- ADSR-style envelope parameters.
- internal, GRW-driven, or hybrid event clocks;
- pre/post-GRW eigenfield comparison;
- deterministic excitation of the mode most strengthened by each GRW hit.

Repository package:

```text
eigenfield_timing_layer_v1/
```

Install:

```bash
pip install numpy python-osc
```

Run:

```bash
cd ~/QuantumSonification

python eigenfield_timing_layer_v1/eigenfield_timing_layer_v1.py \
  output/current_quantum_eigenfield.npz \
  --out-port 7440 \
  --control-port 7441 \
  --event-clock hybrid \
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

Internal events retain the original 14-value packet exactly. A GRW-triggered
event appends five fields after those 14 values:

```text
source="grw"
grw_event_id
mode_probability_increase
mode_probability_before
mode_probability_after
```

## Event clocks

```text
event_clock internal
event_clock grw
event_clock hybrid
```

- `internal` is the original seeded probabilistic clock. GRW transitions are
  compared and published, but do not create timing events.
- `grw` disables autonomous timing events. Each audible GRW transition
  excites the geometric mode with the largest positive probability change.
- `hybrid` retains internal events and adds the deterministic GRW events.

Choose the clock at startup with `--event-clock`, or live over OSC:

```text
/eigenfield/time/control/event_clock internal
/eigenfield/time/control/event_clock grw
/eigenfield/time/control/event_clock hybrid
```

The main resonator conductor mirrors committed GRW frames to port `7441` by
default. Use `--grw-timing-port -1` on that conductor to disable the mirror.

## GRW eigenfield comparison

The timing layer does not guess a correspondence between matrix cells and
geometric modes. It loads the `channel_isometry` saved by the quantum
eigenfield engine and applies the same geometry-conditioned quantum channel to
both states:

```text
rho_before = rho_after - delta_rho
Gamma_before = channel(rho_before)
Gamma_after  = channel(rho_after)
mode_delta   = diag(Gamma_after) - diag(Gamma_before)
trigger_mode = argmax(mode_delta)
```

Comparison streams are published before any GRW timing trigger:

```text
/eigenfield/time/grw/pre/probabilities
/eigenfield/time/grw/post/probabilities
/eigenfield/time/grw/delta/probabilities
/eigenfield/time/grw/comparison
```

The compact comparison packet is:

```text
grw_event_id
strongest_mode
probability_increase
probability_before
probability_after
total_variation_distance
excitation_amplitude
audible
```

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
/eigenfield/time/control/event_clock hybrid
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
