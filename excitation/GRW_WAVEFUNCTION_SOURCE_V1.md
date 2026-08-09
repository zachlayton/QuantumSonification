# GRW wavefunction source v1

`GRWWavefunctionSource` wraps a mutable numerical wavefunction and makes
spontaneous localization part of its dynamics.

For total rate `Lambda = rate_hz * constituent_scale`, successive waiting
times are independently sampled as

```text
Delta t ~ Exponential(1 / Lambda).
```

Evolution is split at the exact sampled time. For localization width `r_C`, a
candidate position `q` is sampled from the discrete probability measure and a
center is drawn as `x = q + Normal(0, r_C)`. This samples the Gaussian mixture
that gives the GRW center distribution for

```text
L_x(q) proportional to exp(-|q-x|^2 / (4 r_C^2)).
```

The post-jump field is `L_x psi / ||L_x psi||`. Each event records its exact
logical time, waiting time, center, pre/post frames, signed probability delta,
and total-variation displacement. The wrapper maintains norm and continues
ordinary Hamiltonian propagation from the collapsed field.

The renderer has no independent clock in GRW mode. It emits one instantaneous
micro-grain burst per committed jump and remains silent between jumps.

This spatial wrapper is distinct from the project's four-qubit
`GRWEventChannel`. Both use exponential jump clocks and state-changing
localization, but they act on different state spaces and are not silently
cross-coupled.
