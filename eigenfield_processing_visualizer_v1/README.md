# Eigenfield Processing Visualizer v1

A Processing 4 visualization for `eigenfield_timing_layer_v1.py`.

## Install oscP5

In Processing:

```text
Sketch → Import Library → Manage Libraries
```

Search for and install:

```text
oscP5
```

## Folder placement

Processing requires the sketch folder and `.pde` file to have matching names:

```text
EigenfieldPointCloudV1/
└── EigenfieldPointCloudV1.pde
```

The supplied package already follows this structure.

## Run the Python timing layer

```bash
cd ~/QuantumSonification

python eigenfield_timing_layer_v1/eigenfield_timing_layer_v1.py \
  output/current_quantum_eigenfield.npz \
  --out-port 7440 \
  --control-port 7441 \
  --event-rate 8
```

Then open and run the Processing sketch.

## Visualization mapping

```text
x position     = normalized logarithmic eigenvalue
y position     = quantum mode probability
z position     = complex phase

sphere size    = probability + mode amplitude
sphere pulse   = current amplitude envelope
brightness     = trigger/envelope activity
connections    = adjacent spectral modes
```

## Controls

```text
mouse drag     rotate
mouse wheel    zoom
space          auto-rotation
c              spectral connections
l              labels
a              axes
r              reset view
```

## OSC input

```text
/eigenfield/cloud/count
/eigenfield/cloud/x
/eigenfield/cloud/y
/eigenfield/cloud/z
/eigenfield/cloud/eigenvalues
/eigenfield/cloud/probabilities
/eigenfield/cloud/amplitudes
/eigenfield/cloud/phases
/eigenfield/time/event
```
