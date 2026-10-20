# Hamiltonian projection backend

Run from the repository root:

```sh
python hybrid_packet_instrument_v1/python/hamiltonian_engine.py --diagnostics
python hybrid_packet_instrument_v1/python/hamiltonian_engine.py --self-check
python -m unittest discover -s hybrid_packet_instrument_v1/tests -v
```

Requires NumPy. `--duration 5` exits after five seconds; default runs until Ctrl-C.
The server binds only localhost. Default controls arrive on UDP 17921 and
projections go to SuperCollider on UDP 17920 at 30 Hz.

## Physics and interpretation

The interior grid spans x in (-1,1), with Dirichlet hard walls at both ends.
Units are dimensionless, hbar=m=1. The second-order centered finite-difference
kinetic operator is Hermitian. Harmonic mode adds V(x)=omega^2*x^2/2;
box mode has V=0 in the interior. Harmonic mode still has the hard walls:
large packets can encounter them. The initial packet is proportional to
exp(-(x-center)^2/(4*width^2)) * exp(i*(momentum*(x-center)+phase)).
Width is the probability-density sigma before truncation and normalization.

The finite Hamiltonian is diagonalized and propagated by exact eigenphases.
This preserves discrete norm and energy; it is not an exact continuum solver.
Narrow packets/high momenta require grid-convergence checks; use `--points 256`
or greater for these regimes. The default 128-point grid is appropriate for
initial demonstrations, not a claim of converged accuracy for all controls.

Sixteen complex overlaps against normalized sine modes are transmitted. These
are control coefficients for sonification, not PCM samples and not a simulated
acoustic field. The SC synthesis body adds its own carriers, envelopes, modal
frequencies and decay. Control-rate output can alias fast projection motion;
reduce `rate` for slower, more inspectable trajectories. Physical evolution
time and audible carrier time are explicitly different scales.

This release implements pure states only. It does not implement physical
temperature, a thermal bath, or phonon scattering. Global phase affects the
real/imaginary projection sonification, although it does not change a quantum
state's physical observables. K and V diagnostics use the same discrete H;
equal K/V is not enforced, and hard-wall boundary effects must be considered
before interpreting a harmonic virial comparison.

## OSC contract

`/qmw/hybrid/projection` has exactly 38 scalar arguments:

1. signed int32 sequence, wrapping after 2147483646;
2. model time (float32);
3. norm;
4. total energy;
5. kinetic energy;
6. potential energy;
7. sixteen real overlaps, modes 1..16;
8. sixteen imaginary overlaps, modes 1..16.

Arguments 2..38 are float32 on the wire; calculations use float64/complex128.

Controls are `/qmw/hybrid/physics/<name>` with one numeric argument:

| name | range | initial value |
|---|---|---|
| potential | 0 box, 1 harmonic | 1 |
| center | -0.8..0.8 | -0.35 |
| width | 0.02..0.8 | 0.12 |
| momentum | -80..80 | 2 |
| phase | -1000000..1000000 radians | 0 |
| omega | 0..30 | 8 |
| rate | 0..10 model seconds/wall second | 0.1 |

Changing a control resets the Gaussian state, except `rate`, which preserves
it. `potential` and `omega` also rebuild H. `/qmw/hybrid/physics/reset` and
`/qmw/hybrid/reset` accept no arguments or one numeric trigger. Unknown controls,
nonfinite numbers, unsupported OSC types/bundles, malformed packets and
out-of-range values are rejected without stopping the stream.
