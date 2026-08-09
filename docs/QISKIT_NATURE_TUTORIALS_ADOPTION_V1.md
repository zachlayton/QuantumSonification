# Qiskit Nature tutorial adoption notes

Reviewed against the Qiskit Nature 0.8 tutorial set at commit
`25eff2741c63a4d15df82b5047d834973b125502`.

## Adopted now

- **Electronic structure:** PySCF-backed `ElectronicStructureProblem`, explicit
  electronic and nuclear energy contributions, dipole observables.
- **Ground and excited-state solvers:** exact eigensolvers as the validation
  reference, with a fixed particle-number sector for the reported branches.
- **Properties:** particle number and electronic density concepts; the local
  implementation additionally verifies 1-RDM trace/Hermiticity and 2-RDM
  contraction explicitly.
- **Quadratic Hamiltonians and Slater determinants:** Hartree-Fock/Slater data
  is kept as a named baseline rather than conflated with the correlated state.
- **Lattice models and qubit mapping:** the Hubbard prototype and explicit
  Jordan-Wigner mapping remain the validated precursor.

## Relevant later, not folded into H2 electronic audio

- **Vibrational structure:** valuable as a genuinely vibrational model, but its
  force-field/driver inputs and bosonic modal truncation require a separate
  validated workflow.
- **Problem transformers:** active-space and freeze-core transformations become
  important for molecules larger than H2; each reduction must retain a visible
  provenance record.
- **QCSchema:** a strong interchange format for external chemistry workflows.
- **VQE/UCC and QEOM:** useful comparison routes after the exact small-system
  reference remains fixed; they should not replace the exact baseline.
- **Deuteron binding:** a distinct nuclear-physics model and possible later
  instrument, not evidence about molecular H2.

## Sonification consequence

Excited-state branches and natural orbitals are treated as persistent identities.
Their physical quantities change internal relations—amplitude, beating,
cross-modulation, color, and state-derived articulation timing—rather than
forcing every changing scalar into pitch.
