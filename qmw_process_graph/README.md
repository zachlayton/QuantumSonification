# QMW Process Graph

A process-graph layer for the Quantum Material Workstation.

It separates:

1. **Quantum process graph** — state preparation, gates, entanglers, and circuit topology.
2. **Sonic realization graph** — Max/MSP feedback, resonators, spectral freeze, convolution, and spatialization.

The simulator produces OSC descriptors from a statevector:

- per-qubit Bloch vectors;
- pairwise mutual information and ZZ correlation;
- process complexity and phase dispersion;
- a `QuantumMaterialDescriptor`-style material map.

## Install

Inside the `music` conda environment:

```bash
pip install -r requirements.txt
```

## Run

```bash
python examples/process_graph_to_max.py --host 127.0.0.1 --port 7400
```

## Max receiver

```text
[udpreceive 7400]
|
[oscparse]
|
[route qmw]
|
[route process]
|
[route begin node edge end frame qubit joint material state]
```

### OSC messages

```text
/qmw/process/begin    name nodeCount edgeCount
/qmw/process/node     id kind label depth qubitCount q0 q1 ...
/qmw/process/edge     source target relation system
/qmw/process/end      name

/qmw/process/frame    frame entropy phaseDispersion processComplexity purityProxy
/qmw/process/qubit    frame qubit x y z
/qmw/process/joint    frame q0 q1 mutualInformation zzCorrelation sharedResonance
/qmw/process/material frame modeFamily decay brightness damping density space
/qmw/process/state    frame stateDimension schmidtProxy phaseCentroid entanglingPower
```

## Immediate Max mappings

- `/joint ... sharedResonance` -> shared feedback coefficient / spectral-freeze duration.
- `/qubit ... x y z` -> local oscillator mix, pan trajectory, or filter geometry.
- `/material ...` -> physical model, resonator bank, convolution, and density controls.
- `/state ... entanglingPower` -> spatial diffusion / cross-synthesis amount.

## Important constraint

The `sonic` edges in the graph are only documentation and control topology.
They are not sent into the Qiskit circuit. Quantum-circuit causality remains
feed-forward; feedback belongs in the sonic realization layer.
