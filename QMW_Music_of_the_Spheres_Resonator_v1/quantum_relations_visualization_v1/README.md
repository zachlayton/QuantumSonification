# Quantum Relations + Eigenfield Point Cloud V2

## Files

```text
quantum_relations_osc_v1.py
EigenfieldPointCloudV2/EigenfieldPointCloudV2.pde
```

## Python dependencies

```bash
pip install numpy python-osc
```

## Run the relation engine

```bash
cd ~/QuantumSonification/geometry

python quantum_relations_osc_v1.py \
  output/current_density_matrix.npz \
  --rho-key rho \
  --out-port 7450 \
  --control-port 7451 \
  --basis Z \
  --measurement-mode probe
```

Keep the eigenfield timing layer running on port 7440.

## Processing

Install `oscP5`, then open:

```text
EigenfieldPointCloudV2/EigenfieldPointCloudV2.pde
```

The sketch listens on:

```text
7440  eigenfield cloud and timing events
7450  superposition, entanglement, and measurement
```

## Measurement controls from Max or another OSC sender

```text
/quantum/relations/control/basis X
/quantum/relations/control/basis Y
/quantum/relations/control/basis Z

/quantum/relations/control/measurement_mode probe
/quantum/relations/control/measurement_mode collapse

/quantum/relations/control/measure X
/quantum/relations/control/measure Y
/quantum/relations/control/measure Z
```

Send these to UDP 7451.

## Visual semantics

```text
basis-dependent superposition -> cloud expansion and visibility
mutual information            -> relational edge strength
pair concurrence              -> explicitly quantum edge emphasis
measurement basis             -> projection plane orientation
measurement result            -> selected-region flash
collapse mode                 -> recomputed post-measurement metrics
probe mode                    -> flash without changing the saved state
```

## Important distinction

Reduced single-qubit entropy is a clean entanglement measure only when the full
state is pure. For mixed states, the visualizer also receives mutual information
and pairwise concurrence so classical correlation and pair entanglement are not
silently treated as the same quantity.
