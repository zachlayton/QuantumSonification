# Quantum Geometry v1

This package implements a finite 4-qubit configuration space whose 16 basis states are complete candidate geometries. MLX is preferred for the constraint eigensolve when installed; NumPy is the deterministic compatibility backend. Qiskit and Qiskit Nature appear only in optional adapters.

Run the standalone validation:

```bash
python examples/run_quantum_geometry16_v1.py
python -m unittest discover -s tests -p 'test_quantum_geometry16_v1.py'
```

In a headless macOS session without Metal, set `QMW_DISABLE_MLX=1`; the report will identify the NumPy backend explicitly.

To use existing Living Spectral Geometry artifacts, repeat `--living-state path/to/state.json` exactly 16 times. The run emits the configuration Laplacian, constraint diagnostics, density matrix, Page-Wootters conditional states, 16 explicit geometry weights at each relational time, and a Living/IR artifact-selection sequence. Collapse hooks default to disabled.

Conductor registration is intentionally deferred until these standalone tests pass in the target environment.

The paired real-geometry experiment generates sixteen sequential Living Spectral Geometry states on a common topology, applies independently normalized spectrum/modal/material/geometry/IR descriptor families, and preserves the original synthetic benchmark as its control:

```bash
python examples/run_quantum_geometry16_real_v1.py
```

It records both amplitude-state and phase-free probability Dirichlet energies. GRW, convolution, and conductor registration remain disabled.

After that benchmark validates, render the synchronized population, parallel-transport-gauge-fixed complex-amplitude, and winner-only modal-lineage comparisons:

```bash
python examples/run_quantum_geometry16_modal_mix_v1.py
```

The complex renderer uses tracked lineage contributions `z_k(t) = sum_i c_i(t) a_ik`; it never applies complex weights directly to raw IR recordings.

The next non-audio experiment compares the fixed generator with causal population/coherence-conditioned feedback:

```bash
python examples/run_quantum_geometry16_conditioned_time_v1.py
```

This exploratory state-dependent evolution is explicitly reported as nonlinear mean-field feedback, not as a strict stationary Page-Wootters constraint solution.

Sweep population/coherence couplings and timestep over a fixed physical horizon, with a separate substep-convergence test:

```bash
python examples/run_quantum_geometry16_conditioned_sweep_v1.py
```

Render fixed versus converged geometry-conditioned trajectories with continuous resonators and accumulated inverse-distance relational timing:

```bash
python examples/run_quantum_geometry16_conditioned_audio_v1.py
```
