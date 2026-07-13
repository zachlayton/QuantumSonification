# QDK reference layer

This folder is deliberately **outside the real-time OSC path**. It establishes
an inspectable circuit score that QDK can visualize and a small independent
NumPy simulator that can validate the MLX density-matrix implementation.

## Files

- `four_qubit_16step.qasm` — OpenQASM 3 circuit score. Open it in VS Code
  with the QDK extension, then use the Command Palette (`QDK:`) to visualize
  the circuit.
- `qdk_reference_simulator.py` — NumPy reference implementation of exactly
  the same sixteen visible operations.
- `compare_mlx_reference.py` — comparison harness; wire one function to the
  existing `DensityMatrixEngine` after we identify its rho accessor.

## Verify the reference now

```bash
cd /Users/zlayton/QuantumSonification
python qdk_reference/qdk_reference_simulator.py
```

Expected invariant results for this closed, unitary circuit:

- trace = 1
- purity = 1
- von Neumann entropy = 0
- Hermiticity error approximately numerical zero

Those are properties of the complete four-qubit state. Individual qubits can
still be mixed because the circuit generates entanglement.

## How it will join the live system

1. Open `four_qubit_16step.qasm` in VS Code and inspect the QDK circuit diagram.
2. Use the score as the canonical gate ordering.
3. Add an optional `set_circuit_score()` or equivalent adapter to
   `QMWCircuitBridge`.
4. Run the MLX engine with the same fixed score, obtain `rho`, and connect
   `get_live_mlx_rho()` in the comparator.
5. Only after numerical agreement is established do we expose score
   parameters to Max.

## Important convention to verify

The reference uses tensor ordering `|q0 q1 q2 q3>` with q0 as the
most-significant bit. If our MLX engine instead stores q0 as the least-
significant bit, we should permute axes for comparison rather than call the
result wrong. Gate-order agreement is the first thing to test.
