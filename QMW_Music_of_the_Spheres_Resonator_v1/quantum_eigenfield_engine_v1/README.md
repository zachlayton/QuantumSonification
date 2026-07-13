# Quantum Eigenfield Engine v1

Place the file in:

```text
~/QuantumSonification/geometry/quantum_eigenfield_engine_v1.py
```

It consumes either the `.npz` spectrum produced by `spectral_geometry_v1.py`
or a material packet produced by `surface_material_models_v1.py`, plus a
density matrix produced by the quantum engine.

## Standalone test

This uses the built-in four-qubit GHZ-like mixed state:

```bash
cd ~/QuantumSonification/geometry

python quantum_eigenfield_engine_v1.py \
  output/emergent_labyrinth_spectrum.npz \
  --output output/emergent_labyrinth_quantum_eigenfield_v1 \
  --modes 32 \
  --coupling-mode hybrid
```

## With a saved density matrix

```bash
python quantum_eigenfield_engine_v1.py \
  output/emergent_labyrinth_spectrum.npz \
  --rho output/current_density_matrix.npz \
  --rho-key rho \
  --output output/current_quantum_eigenfield \
  --modes 32 \
  --coupling-mode pauli
```

Outputs:

```text
current_quantum_eigenfield.npz
current_quantum_eigenfield.json
```

The NPZ includes:

```text
rho
quantum_eigenvalues
quantum_eigenvectors
geometric_eigenvalues
geometric_eigenvectors
model / material_model
frequencies_hz
angular_frequencies
decay_times_seconds
damping_rates
mode_weights
coupling_matrix
mode_probabilities
mode_amplitudes
spatial_eigenfield
developmental_drive
```

Material fields are copied rather than recomputed. Both
`eigenvalues/eigenvectors` and the legacy
`geometric_eigenvalues/geometric_eigenvectors` schema are accepted.

## Coupling modes

`hybrid`
: deterministic orthogonal feature projection with geometric spectral shaping.

`spectral`
: cosine feature bank emphasizing ordered quantum/geometric mode relations.

`pauli`
: emphasizes local Pauli expectations and pairwise Pauli correlations.

## Developmental integration

For the bioelectric field:

```python
from developmental_fields_v1 import BioelectricMemoryField
from quantum_eigenfield_engine_v1 import QuantumEigenfieldEngine

drive = eigenfield_engine.create_developmental_drive()
bioelectric_field.set_external_drive(drive.reshape(
    bioelectric_field.size,
    bioelectric_field.size,
))
```

That reshape is valid only when the spectral mesh vertices correspond directly
to the field grid. For arbitrary meshes, interpolate the vertex drive back to
the developmental grid first.

## Mathematical boundary

The density matrix and Laplace–Beltrami operator act in different vector
spaces. The engine therefore does not evaluate an expression such as
`<phi|rho|phi>` unless an explicit common basis has first been constructed.
The exported `coupling_matrix` is that explicit bridge and can be inspected,
saved, replaced, learned, or driven by Pauli structure.
