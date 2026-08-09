# QMW SPSA Sonification v1

This prototype makes the hidden two-sided probes inside Qiskit's
`SPSAEstimatorGradient` audible. Each optimizer step is articulated as:

1. `f(theta + epsilon * delta)` on the left;
2. `f(theta - epsilon * delta)` on the right;
3. the inferred, batch-averaged gradient as a centered chord;
4. a low update pulse (lower when the step descends, higher when it ascends).

It is a closed loop. SuperCollider analyzes the answer it produces and returns
normalized energy, centroid, flux, stereo balance, and resonance on UDP `17421`.
Those features shape the *next* question while leaving the current plus/minus
pair intact:

- centroid broadens or narrows `epsilon`;
- resonance scales the next learning rate;
- flux requests additional probe pairs for a steadier average;
- strong rightward balance reverses the next pair's orientation.

All mappings are bounded to prevent runaway parameter jumps. Set
`--feedback-mix 0` to hear the same instrument open-loop, or `--no-feedback` to
disable the return OSC server entirely.

The demo uses a four-parameter, two-qubit entangled circuit and an exact local
`StatevectorEstimator`. Its exposed probe calculation is tested numerically
against Qiskit Machine Learning's `SPSAEstimatorGradient` with the same seed.

## Run it

First evaluate `qmw_spsa_listener_v1.scd` in SuperCollider. Then, from the
repository root, run:

```bash
/Users/zlayton/miniconda3/envs/music/bin/python -m \
  spsa_sonification_v1.spsa_osc
```

The listener opens UDP port `17420`. Useful variations:

```bash
# One stochastic probe pair per step: sparse and unstable
/Users/zlayton/miniconda3/envs/music/bin/python -m \
  spsa_sonification_v1.spsa_osc --batch-size 1 --epsilon 0.18

# Eight averaged probe pairs: denser, steadier gradient gestures
/Users/zlayton/miniconda3/envs/music/bin/python -m \
  spsa_sonification_v1.spsa_osc --batch-size 8 --gesture-seconds 0.22

# Inspect optimization without UDP or real-time gesture delays
/Users/zlayton/miniconda3/envs/music/bin/python -m \
  spsa_sonification_v1.spsa_osc --no-osc --gesture-seconds 0 --step-pause 0

# Exaggerate or soften the acoustic influence (range is clamped to 0..1)
/Users/zlayton/miniconda3/envs/music/bin/python -m \
  spsa_sonification_v1.spsa_osc --feedback-mix 1
```

## OSC contract

```text
/qmw/spsa/step/begin      step, batch_size, parameter_count
/qmw/spsa/theta/before    step, theta...
/qmw/spsa/probe/begin     step, batch
/qmw/spsa/probe/delta     step, batch, delta...
/qmw/spsa/probe/plus      step, batch, expectation_plus
/qmw/spsa/probe/minus     step, batch, expectation_minus
/qmw/spsa/probe/gradient  step, batch, gradient...
/qmw/spsa/probe/end       step, batch, plus_minus_difference
/qmw/spsa/gradient        step, gradient_norm, averaged_gradient...
/qmw/spsa/update          step, objective_before, objective_after, theta_after...
/qmw/spsa/step/end        step
/qmw/spsa/feedback        energy, centroid, flux, stereo_balance, resonance
```

The raw scientific values are transmitted without musical normalization. The
SuperCollider listener owns the first mapping, allowing Max, another synth, or
a visualizer to interpret the same stream differently.
