# QMB Rings Instrument v2

This directory is the experimental successor to `heisenberg_instrument_v1`.
The v1 directory is the frozen known-good proof-of-concept line and should not
be modified while v2 develops.

## v2 scope

- sixteen individually addressed `vb.mi.rngs~` voices;
- conductor density-field to transactional QMB bridge;
- four-qubit phase observable;
- complex smoothing and musical commit-rate controls;
- relational/component mapping crossfade;
- per-voice aggregate feature mappings;
- direct realtime matrix-cell mappings;
- integrated density-matrix temporal clock using Bures-angle displacement;
- quantum/fixed-rate A/B timing, fixed/Poisson thresholds, and coherence-sensitive timing;
- immediate recommit when the observation basis or phase is changed;
- adjustable phase-to-Rings depth driven by each row's strongest off-diagonal relation.

## Live routing

```text
conductor --osc-engine-port 7421
    -> qmb_conductor_density_bridge_v2 listens 7421
    -> Max QMW_Heisenberg_Rings_Matrix_Instrument_v2 listens 7400
```

The v2 bridge is started with:

```bash
cd /Users/zlayton/QuantumSonification
/Users/zlayton/miniconda3/envs/music/bin/python \
  -m heisenberg_instrument_v2.qmb_conductor_density_bridge_v2 \
  --listen-port 7421 --output-port 7400 \
  --timing-mode quantum --temporal-process poisson \
  --temporal-distance 0.025 --coherence-depth 0.35
```

The first valid density matrix is committed immediately so the instrument can
sound. After that, `quantum` timing commits only when accumulated state-space
motion crosses the temporal threshold; elapsed wall time by itself produces no
event. The Max controls send these live messages to the bridge:

```text
/qmw/bridge/clock/timing quantum|rate
/qmw/bridge/clock/distance <positive Bures-angle distance>
/qmw/bridge/clock/process poisson|fixed
/qmw/bridge/clock/coherence_depth <0..1>
```

Smaller distance values create more frequent commits. `fixed` makes crossings
deterministic; `poisson` varies each next distance around the selected mean.
Coherence depth determines how strongly changing off-diagonal relationships
modulate the clock. In `rate` mode, `/qmw/bridge/output_hz` remains the fallback
wall-clock rate.

## Phase observation

Changing the observable, global phase, or any qubit phase offset forces an
immediate re-observation commit. It does not advance intrinsic quantum time.
The Max `PHASE → RINGS DEPTH` control sets how strongly the observed
off-diagonal phase moves structure, brightness, damping, and position. The
controller default is `0.65`; use `1.0` for diagnosis or pronounced motion and
`0.0` to compare against the magnitude-dominant mapping.
