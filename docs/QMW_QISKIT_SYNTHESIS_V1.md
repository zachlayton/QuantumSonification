# QMW Qiskit Synthesis v1

This layer exposes selected `qiskit.synthesis` algorithms as QMW circuit
sources. Qiskit performs discrete circuit synthesis and transpilation; the
result is reduced to the canonical QMW gate registry and imported as a
`ComposerCircuit` for Max, local simulation, OSC, and future MLX execution.

The implementation lives in `qmw/synthesis.py`. Run it with the project's
Qiskit-enabled Python environment.

## Commands

Full-connectivity QFT:

```bash
python -m qmw.synthesis qft --qubits 4
```

Linear-nearest-neighbor QFT without terminal swaps:

```bash
python -m qmw.synthesis qft --qubits 4 --topology line --no-swaps
```

Qubit permutation:

```bash
python -m qmw.synthesis permutation --pattern 2 0 3 1 --topology line
```

Hamiltonian evolution from Pauli terms:

```bash
python -m qmw.synthesis evolution \
  --term XX:0.7 --term ZI:0.2 \
  --time 1.5 --method suzuki_trotter --order 2 --reps 4
```

Available evolution methods are `lie_trotter`, `suzuki_trotter`, `qdrift`,
and `matrix`.

Arbitrary unitary synthesis from a NumPy `.npy` matrix:

```bash
python -m qmw.synthesis unitary --matrix operator.npy
```

Seeded random Clifford synthesis:

```bash
python -m qmw.synthesis clifford \
  --random-qubits 4 --seed 23 --method greedy
```

Synthesize the Clifford represented by an OpenQASM 2 circuit:

```bash
python -m qmw.synthesis clifford --qasm2 stabilizer_circuit.qasm
```

Terminal measurements in a QASM 2 input are removed before constructing the
unitary Clifford. Mid-circuit measurements remain unsupported and fail rather
than being silently changed.

Every command prints JSON containing circuit depth, size, operation counts,
and synthesis settings. Put global options before the subcommand. For example,
to optimize and save standards-compliant OpenQASM 3:

```bash
python -m qmw.synthesis \
  --optimization-level 2 \
  --qasm-out output/qft4.qasm \
  qft --qubits 4
```

Atomically publish a synthesized score to a running `QMWCircuitBridge`:

```bash
python -m qmw.synthesis \
  --publish --osc-host 127.0.0.1 --osc-port 7403 \
  qft --qubits 4
```

The publisher sends `/qmw/circuit/load/begin`, revisioned operation messages,
metadata, and `/qmw/circuit/load/commit`. The receiver assembles the new score
off to the side and only replaces its canonical `ComposerCircuit` after the
declared operation count has arrived. It responds on its configured output
port with `/qmw/circuit/load/accepted` or `/qmw/circuit/load/error`.

## Python API

The public functions are:

- `synthesize_qft`
- `synthesize_permutation`
- `synthesize_unitary`
- `synthesize_clifford`
- `load_clifford_qasm2`
- `synthesize_evolution`
- `normalize_to_qmw`

Each synthesis function returns a `SynthesisResult` containing the original
Qiskit circuit, the normalized Qiskit circuit, a `ComposerCircuit`, metadata,
and QASM 3 serialization.

## Current boundary

The importer accepts operations in the canonical QMW gate registry. Unknown
instructions fail explicitly and ask the caller to decompose or transpile.
Barriers are ignored by default because they do not alter circuit semantics.
Bare Qiskit parameters are retained; compound symbolic expressions are
rejected rather than silently converted into incorrectly named parameters.

The legacy live grid displays and executes only its existing H/X/Y/Z/S/T/CX
subset. The complete synthesized score is retained in the canonical registry,
but full live execution still requires the general MLX statevector backend.
