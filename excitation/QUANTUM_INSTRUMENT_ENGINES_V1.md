# Quantum instrument engines v1

The instrument registry now distinguishes scalar spatial wavefunctions from
native spinor and joint-state engines. A source keeps the state representation
required by its physics and is projected to OSC only after its native
observables have been calculated.

## Spin-1/2 precession

`SpinHalfPrecessionSource` evolves a normalized two-component spinor exactly
under the Pauli Hamiltonian. Its frame contains the spinor, density matrix,
Bloch vector, Z probabilities, magnetic and Larmor vectors, energy expectation,
and relative phase. With the default gyromagnetic ratio, a unit Z field gives
one complete Bloch rotation per second.

## EPR Bell pair

`EPRBellPairSource` evolves a two-qubit Bell state under independent local
unitaries. Its frame preserves the joint four-amplitude state and exposes both
reduced density matrices, local Bloch vectors, the complete 3x3 correlation
tensor, pure-state concurrence, and the maximal CHSH value. Local unitary
precession changes correlation orientation without changing entanglement.

## Identical particles

`IdenticalParticles1DSource` propagates two orbitals and constructs the
symmetric bosonic or antisymmetric fermionic joint field on `(x1, x2)`. The
frame contains joint probability, both marginals, swap expectation, same-cell
coincidence probability, and one-body purity. The fermionic diagonal vanishes
as an actual exchange hole; it is not imposed as an audio mapping.

## Morse potential

`morse_potential` is part of the split-step scalar wavefunction registry. It
uses `D_e (1 - exp[-a(x-x_e)])^2`, retaining the anharmonic asymmetry and
dissociation asymptote. It runs through the existing cloud and GRW wrappers.

## Aharonov-Bohm ring

`AharonovBohmRingSource` evolves angular modes with energies proportional to
`(m-alpha)^2`, where `alpha = q Phi / h`. Probability current, kinetic energy,
and mechanical angular momentum use the same gauge-covariant derivative. The
frame exposes flux ratio, holonomy phase, persistent current, and mechanical
angular momentum. Integer gauge shifts of `alpha` accompanied by the same
shift of `m` leave physical observables unchanged.

## External-field family

`LandauLevelSource` constructs analytic Landau-gauge orbitals on a continuous
2D grid and evolves level superpositions at the cyclotron frequency. Its
current and kinetic-energy density use the mechanical momentum
`p_y - q B x`, not the canonical momentum alone.

`HydrogenZeemanSource` applies the normal orbital Zeeman Hamiltonian
`(B/2)L_z` in atomic units to a continuous hydrogenic basis. The default
`m=-1,+1` superposition exposes the field splitting as rotating orbital
interference.

`HydrogenStarkSource` constructs matrix elements of `F z` numerically in the
degenerate `2s,2p_z` hydrogen subspace, diagonalizes that Hermitian
Hamiltonian, and projects its evolution back into a continuous 3D field.
Both hydrogen models label their truncated-basis approximation explicitly in
frame metadata.

## Helium and singular-shell engines

`HeliumVariationalTwoElectronSource` implements the textbook screened
hydrogenic `1s^2` variational ansatz. For neutral helium it minimizes at
`Z_eff=27/16` with energy `-729/256` Hartree. The emitted 2D field is the
angle-integrated joint radial amplitude. Its symmetric spatial state is paired
with the spin singlet, leaving the complete two-electron state
antisymmetric. This ground-state density is stationary by construction.

`DeltaFunctionShellSource` diagonalizes the s-wave radial Hamiltonian for
`V(r)=g delta(r-a)` on a finite grid. One shell cell preserves the integrated
strength `g`; metadata reports bound states and the residual of the continuum
derivative-jump condition.

## Relativistic engines

`DiracHydrogenFineStructureSource` uses the exact point-Coulomb Dirac energies
for selected `(n,kappa,m_j)` levels and evolves their complex amplitudes after
removing only the unobservable common rest-energy phase. Finite nuclear size,
recoil, the Lamb shift, and radiative QED corrections are explicitly omitted.

`DiracStepKleinSource` propagates a full two-component 1D Dirac spinor with an
exact momentum-space kinetic/mass exponential and split electrostatic step.
It reports current, spinor samples, left/right probability, and whether the
chosen step lies in the Klein zone. Left/right mass is not called a final
reflection/transmission coefficient until the scattered packets separate.

## OSC

Scalar `morse_potential` and `aharonov_bohm_effect` frames use the existing
wavefunction cloud OSC path. Native frames use dedicated addresses:

```text
/qmw/instrument/spin/frame
/qmw/instrument/epr/frame
/qmw/instrument/epr/correlation_tensor
/qmw/instrument/exchange/frame
/qmw/instrument/exchange/marginal_a
/qmw/instrument/exchange/marginal_b
/qmw/instrument/exchange/pair
/qmw/instrument/field/name
/qmw/instrument/field/frame
/qmw/instrument/relativistic/frame
/qmw/instrument/relativistic/level
/qmw/instrument/dirac/frame
/qmw/instrument/dirac/sample
```

The persistent wrapper listens for source changes on UDP 7483 at
`/qmw/instrument/control/select`. The unified Max `umenu` sends that command.
Spatial-field selections also publish the established cloud contract to Max
UDP 7480. Those grains sample continuous unitary fields; they are not treated
as physical collapse events.

Run a native engine with:

```bash
python examples/native_quantum_instruments_osc_v1.py \
  --instrument spin_1_2_precession
```

Open `max/QMW_Native_Quantum_Instruments_v1_6.maxpat` for the unified control
and native-observable receiver. Open the wavefunction-cloud patch alongside it
for spatial field grains on the separate scalar-field address contract.

The dedicated defaults are Max 7482, Processing 7402, and SuperCollider
57120, avoiding the GRW/main port 7400 and cloud port 7480.
