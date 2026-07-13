# Operator Ecology Controller v1

The controller translates a density matrix, circuit result, or measurement
result into a typed event batch:

```text
MaterialMutationEvent
GeometryMutationEvent
QuantumStateEvent | MeasurementEvent
RecalculationEvent
```

`RecalculationEvent` terminates the batch. Dispatch applies every mutation to
`LivingSpectralGeometry` with scheduling disabled, then requests exactly one
new living revision.

The quantum analysis includes purity, von Neumann entropy, normalized
coherence, participation ratio, Pauli expectations, pairwise mutual
information, and two-qubit concurrence.

```python
controller = QuantumOperatorEcologyController(living_geometry=living)

batch = controller.process_circuit(
    rho,
    gates=["H(0)", "CX(0,1)"],
    circuit_id="bell",
)

state = living.wait(timeout=10.0)
```

Measurement input uses the post-measurement density matrix:

```python
controller.process_measurement(
    collapsed_rho,
    outcome="00",
    basis="ZZ",
    probability=0.5,
    strength=0.8,
)
```

Geometry events carry semantic organization values. Supply a
`geometry_adapter` when the developmental geometry engine should translate
those values into a concrete height-field or mesh mutation.

