# Shared one-qubit Euler workflow

`qmw.euler` is the canonical decomposition service for circuit, conductor,
ZX, OSC, JSON, and Max workflows. The default basis is `ZXZ`:

```text
U = exp(i gamma) RZ(phi) RX(theta) RZ(lambda)
```

Because the right-most matrix acts first, the left-to-right Processing wire is:

```text
input -- Z(lambda) -- X(theta) -- Z(phi) -- output
```

Degree-two ZX spiders include their own phase factors. The additional exact
diagram scalar is:

```text
exp(i * (gamma - (phi + theta + lambda) / 2))
```

## Python API

```python
from qmw.euler import decompose_one_qubit, decompose_qiskit_circuit

single = decompose_one_qubit(matrix_2x2)
report = decompose_qiskit_circuit(qiskit_circuit)
```

`ComposerCircuit` exposes the same service:

```python
report = score.euler_decomposition_report()
messages = score.euler_osc_messages(revision=12)
```

Every decomposition is independently reconstructed and checked against its
source matrix. Circuit reports retain explicit skipped entries for entanglers,
measurements, and unresolved symbolic parameters.

## Circuit OSC transaction

```text
/qmw/circuit/euler/begin revision gate_count basis qubit_count
/qmw/circuit/euler/gate revision instruction operation qubit
    theta phi lambda gamma zx_scalar_phase verified absolute_error
/qmw/circuit/euler/end revision gate_count verified maximum_error skipped_count
```

QAC publishes this transaction with every accepted circuit on its normal Max
output port `7400`. When launched by the conductor, it also mirrors the same
transaction to the Processing instrument on `7497`.

## Processing Euler lens

Select a contiguous one-wire sequence of degree-two Z, X, or explicit H nodes
and press `E`. Python extracts its exact 2x2 tensor, performs the shared
decomposition, and returns:

```text
/qmw/zx/euler/result request source qubit basis
    theta phi lambda gamma zx_scalar_phase verified absolute_error
```

The Euler lens displays the time-ordered chain and all four angles. A verified
selection becomes live: changing a retained Z or X spider phase schedules a
new verified request after a 90 ms debounce, and the refreshed angles are
fanned out to Processing, Max, and tomography. Press `E` on another chain to
move the lens. Press `E` with no selection to show or hide it; hiding releases
the live selection. Branching, discard, boundaries, and Hadamard-edge cuts are
rejected rather than approximated.

## Conductor

Euler analysis is enabled by default whenever the QAC bridge is active:

```sh
python quantumsonification_conductor.py --with-qac-bridge
```

Relevant options:

```text
--euler-basis ZXZ
--euler-processing-port 7497
--no-euler
```

The corresponding configuration block is:

```json
{
  "euler": {
    "enabled": true,
    "basis": "ZXZ",
    "mirror_processing": true,
    "processing_host": "127.0.0.1",
    "processing_port": 7497
  }
}
```

## Numerical representation

Python retains 64-bit floating-point radians. Processing and normal OSC float
atoms are performance-resolution values. Familiar fractions of pi are a
display concern; arbitrary decompositions remain numeric. Global phase is
preserved for exact circuit/ZX semantics even though it cancels from an
ordinary density transformation `U rho U-dagger`.
