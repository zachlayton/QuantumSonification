# QMW Quantum Statistics Instrument v1

**Pauli's Ideal Gas** extends the Pauli State Instrument from exclusion at one
complete electron address to the thermodynamics of many indistinguishable
particles. Its single primary control is

```text
D = n * lambda_T^3
lambda_T = h / sqrt(2*pi*m*k_B*T)
```

At small `D`, both fields converge to the classical Maxwell-Boltzmann gas. As
`D` approaches and exceeds one, exchange symmetry becomes audible even though
the model contains no interparticle potential.

The original `pauli_state_instrument_v1` remains the finite, address-level
instrument; this directory is its many-particle equation-of-state continuation.

## Open the instrument

1. Regenerate the patch and its thermodynamic lookup table if needed:
   `python3 quantum_statistics_instrument_v1/build_qmw_quantum_statistics_instrument_v1.py`
2. Open `QMW_Quantum_Statistics_Instrument_v1.maxpat` in Max 9.
3. Enable `ezdac~` and click the 30-second sweep.

The left event field is fermionic and the right field is bosonic. The patch
starts at `log10(D) = 0` (`D=1`), where both sides produce immediately audible
detections. The sweep begins at `D=0.1`; use a direct value of `-3` only when
you intentionally want the nearly silent, deeply dilute classical limit.

## Physical model

For internal degeneracy `g`, the model solves

```text
D/g = F_3/2(z)                 fermions
D/g = G_3/2(z)                 noncondensed bosons
P/(n*k_B*T) = F_5/2(z)/F_3/2(z)
P/(n*k_B*T) = G_5/2(z)/G_3/2(z)
```

where `F_s(z) = -Li_s(-z)` and `G_s(z) = Li_s(z)`. For a spinless Bose gas,
the excited states saturate at

```text
D_c = zeta(3/2) = 2.612375...
N_0/N = 1 - D_c/D              D >= D_c
P/(n*k_B*T) = zeta(5/2)/D     D >= D_c
```

The Python model uses numerical complete Fermi/Bose integrals and a solved
fugacity. The Max controller contains a generated 122-state interpolation table
from that model; it does not substitute an artistic curve for the equation of
state.

## Sonification mapping

Ten event carriers on each side represent samples of reduced single-particle
energy `epsilon/(k_B*T)`. A 20 ms detector clock samples the actual one-state
occupation-number distributions:

```text
Fermi: n in {0,1},       Var(n) = mean(n) * (1 - mean(n))
Bose:  n in {0,1,2,...}, Var(n) = mean(n) * (1 + mean(n))
```

Consequently, a fermionic mode can emit at most one short detection pip per
window. A bosonic mode can emit a multiparticle event; multiplicity controls
both burst strength and duration. Detection efficiency changes event density
without changing the Bernoulli or geometric family. The multisliders retain
the equilibrium 3D energy-shell particle populations

```text
w(epsilon) proportional to sqrt(epsilon) * mean_occupation(epsilon).
```

- **Fermi / left:** every one-state occupation is bounded by one. The result is
  a field of separated singleton pips rather than same-mode bursts. Increasing
  `D` also fills a low-energy plateau and pushes population upward. Carrier
  spacing is multiplied by the exact `P/(n*k_B*T) > 1`, so degeneracy pressure
  expands the field.
- **Bose / right:** population concentrates into the lowest energy shells and
  geometric occupation creates accented, longer multiparticle clusters.
  `P/(n*k_B*T) < 1` compresses their carrier field. Above `D_c`, thermal-event
  probability falls with the excited fraction and a centered 55 Hz coherent
  condensate voice grows as `sqrt(N_0/N)`.

This makes the contrast structural: antisymmetry limits each state and stiffens
the gas; symmetry permits bunching and ultimately a macroscopic ground mode.

## Python use

```python
from quantum_statistics_instrument_v1 import compare_statistics

states = compare_statistics(3.0)
print(states["fermi"].pressure_ratio)
print(states["bose"].condensate_fraction)
```

`state_from_physical_controls()` converts number density, temperature, and mass
in atomic-mass units into the same state. `internal_degeneracy` defaults to one
and remains explicit throughout the model.

## Offline audition

Run

```text
python3 quantum_statistics_instrument_v1/render_quantum_statistics_demo.py
```

The 24-second stereo render begins in the classical regime, sweeps through the
degenerate and condensation thresholds, then holds at `D=20`. Fermionic
Bernoulli detections remain left, geometrically distributed Bose bursts remain
right, and the coherent condensate emerges in the center.

## Scope

This is the homogeneous, nonrelativistic, three-dimensional **ideal** gas in
the thermodynamic limit. It does not include interactions, finite-size traps,
relativistic corrections, superfluid dynamics, or helium's strong interaction
physics. The emitted events exactly sample the single-mode Bernoulli and
geometric occupation laws, but the detector windows are independent. A future
spatiotemporal layer could impose a specified first-order coherence function
and thereby synthesize the full measured `g^(2)(r,tau)` curve.
