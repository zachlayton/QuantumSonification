# QMW Quantum Spectral Core Agent

## Mission
Implement and verify quantum spectral analysis as a foundational QMW subsystem. The agent must extend the existing QMW architecture rather than create a parallel implementation.

## Canonical mathematics
For a valid density matrix rho and Hamiltonian H:

- Hermitian eigendecompositions:
  - rho = V_rho diag(lambda) V_rho^dagger
  - H = V_H diag(E) V_H^dagger
- Energy-basis density matrix:
  - rho_E = V_H^dagger rho V_H
- Energy-basis populations:
  - p_i = Re[(rho_E)_{ii}] = <E_i|rho|E_i>
- Basis overlap:
  - B_ij = |<E_i|psi_j>|^2
  - p_i = sum_j lambda_j B_ij
- Purity:
  - Tr(rho^2) = sum_i lambda_i^2
- von Neumann entropy:
  - S(rho) = -sum_i lambda_i log(lambda_i), ignoring numerically zero eigenvalues
- Participation/effective rank diagnostic:
  - R_participation = 1 / sum_i lambda_i^2

## Required implementation components
1. QuantumSpectrumFrame
   - rho eigenvalues/eigenvectors
   - H eigenvalues/eigenvectors
   - rho_E
   - energy-basis populations p_i
   - basis-overlap matrix B
   - density and energy spectral gaps
   - purity, entropy, participation rank
   - commutator norm ||[H,rho]||_F

2. QMWEigenTracker
   - stable eigenmode identities across frames
   - overlap-based assignment between consecutive eigensystems
   - explicit handling of near-degenerate eigenspaces
   - no false discontinuities from naive per-frame sorting

3. QMWSpectralSonifier core mapping API
   - energy structure E_i -> frequency/resonance targets
   - population p_i -> acoustic energy with amplitude sqrt(max(p_i,0))
   - off-diagonal |rho_E,ij| -> optional inter-mode coupling magnitude
   - arg(rho_E,ij) -> optional coupling phase
   - keep mapping policy separate from quantum-state computation

4. QMWFrame integration
   - quantum spectral results attached to every validated frame
   - diagnostics accessible to OSC/GUI layers without recomputation

## Hard invariants / tests
The implementation must fail tests if any of these are violated beyond configured numerical tolerance:

### Density-matrix validity
- rho is Hermitian
- Tr(rho) ~= 1
- lambda_i >= -epsilon
- sum_i lambda_i ~= 1

### Spectral reconstruction
- V_rho diag(lambda) V_rho^dagger ~= rho
- V_H diag(E) V_H^dagger ~= H

### Spectral statistics
- purity_from_matrix ~= sum(lambda^2)
- entropy agrees with eigenvalue definition
- 1 <= participation_rank <= Hilbert dimension for physical states

### Unitary invariance
For rho' = U rho U^dagger:
- sorted eigenvalues(rho') ~= sorted eigenvalues(rho)
- purity and entropy invariant
- eigenvectors may change

### Open-system sensitivity
For at least one dephasing/amplitude-damping/depolarizing trajectory:
- verify that the density spectrum can change when physically expected
- verify trace and positivity remain valid

### Energy-basis bridge
- diag(V_H^dagger rho V_H) ~= p
- p_i >= -epsilon
- sum_i p_i ~= 1
- p_i ~= sum_j lambda_j |<E_i|psi_j>|^2

### Commuting case
If [H,rho] ~= 0 and the spectrum is nondegenerate:
- H and rho eigenspaces align up to phase/permutation
- basis overlap is permutation-diagonal within tolerance

### Degeneracy
- do not assert unique eigenvectors inside a degenerate subspace
- compare projectors/subspaces rather than individual vectors when gaps are below epsilon_deg

### Temporal tracking
- synthetic avoided crossings and crossings must not produce spurious eigenmode swaps where overlap tracking resolves identity

## Validation fixtures
Include deterministic fixtures for:
- |0000><0000| pure state
- maximally mixed I/16
- GHZ pure state
- Bell-pair product state
- classical mixed diagonal state with known lambda
- random PSD trace-one density matrices generated from A A^dagger / Tr(A A^dagger)
- commuting H,rho pair
- noncommuting H,rho pair
- degenerate H
- unitary trajectory
- at least one Lindblad/open-system trajectory already supported by QMW, if present

## Sonification correctness contract
The sonifier must not pair sorted lambda_i directly with sorted E_i unless rho and H share the same eigenbasis. Canonical bridge is rho_E = V_H^dagger rho V_H, with p_i = diag(rho_E).

For population-to-amplitude mapping use:
- A_i = sqrt(max(p_i,0))
so acoustic modal energy is proportional to p_i.

Quantum spectral computation must remain independent of FluCoMa. FluCoMa may later analyze the resulting acoustic spectrum for validation, but it is downstream of the canonical quantum spectral layer.

## Development protocol
1. Inspect existing QMW state-engine, frame, diagnostics, and tests.
2. Add the smallest compatible spectral data structure.
3. Implement pure numerical spectral computation with no audio dependencies.
4. Add invariant tests before sonification.
5. Add eigenmode tracking and degeneracy tests.
6. Integrate into QMWFrame.
7. Add a minimal clean spectral sonifier only after mathematical tests pass.
8. Add acoustic-spectrum validation later as a separate observer layer.

## Definition of done
- All pre-existing QMW tests pass.
- New quantum spectral tests pass deterministically.
- Spectral decomposition adds no invalid mutation of rho or H.
- Numerical tolerances are explicit and documented.
- The energy-basis population mapping is demonstrated with at least three analytic fixtures.
- A minimal 4-qubit demo produces 16 energy modes with amplitudes derived from p_i.
- Documentation clearly distinguishes H spectrum, rho spectrum, Pauli/operator spectrum, and acoustic spectrum.
