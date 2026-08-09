# Geometric Quantum Optimization v2

This lab turns the Wilson `2)4 1-3-5-7` Hexany into a constrained quantum
optimization domain. Its six vertices are the balanced `2-of-4` decisions,
the weight-two sector of four qubits, and the Johnson graph `J(4,2)`.

A two-layer constrained QAOA ansatz alternates a diagonal balanced-cut cost
phase with an exchange mixer. The exchange graph never leaves the valid shell.

## Three controlled conditions

1. **SPSA** uses one stochastic two-sided probe per update.
2. **Acoustic-feedback SPSA** analyzes each completed answer and uses its five
   normalized descriptors to shape only the *next* complete probe batch.
3. **Quantum natural gradient** preconditions descent with the pullback
   Fubini--Study metric.

The simulated acoustic analyzer follows the live SuperCollider contract:

- activity becomes energy;
- Hexany pitch distribution becomes spectral centroid;
- probability redistribution becomes spectral flux;
- gauge-invariant phase/spatial structure becomes stereo balance;
- phase order and concentration become resonance.

The resulting feedback is bounded. Centroid changes perturbation radius,
resonance changes learning rate, flux requests more averaged probes, and a
strong rightward balance reverses the audible plus/minus orientation without
changing the symmetric SPSA estimate. Step `n` controls always identify
feedback step `n-1`, making the causal boundary testable.

## Run and verify

```bash
python -m geometric_quantum_optimization_v1.run_experiment

python -m unittest \
  geometric_quantum_optimization_v1.test_geometric_quantum_optimization_v1 -v
```

The default result is `output/geometric_quantum_optimization_v2.json`.

## Replay to SuperCollider, Max, or Processing

Evaluate `qmw_geometric_optimization_listener_v1.scd`, then run:

```bash
python -m geometric_quantum_optimization_v1.run_experiment \
  --osc \
  --osc-trace acoustic_feedback_spsa \
  --gesture-seconds 0.28 \
  --step-pause 0.12
```

Topology and optimizer frames are revisioned transactions. See
`OSC_CONTRACT.md` for the full packet schema.

## Scientific boundaries

- This is an exact six-dimensional simulation, not evidence of quantum
  advantage.
- The CPS/Johnson/weight-shell identity is exact; the weighted-cut cost is the
  chosen experiment on that space.
- Fubini--Study distance and Tenney harmonic distance remain distinct.
- The synthetic acoustic analyzer makes the feedback experiment reproducible.
  Live audio analysis should be treated as a separate condition.
- Comparisons report model evaluations because adaptive probe batching changes
  the cost per optimizer step.
