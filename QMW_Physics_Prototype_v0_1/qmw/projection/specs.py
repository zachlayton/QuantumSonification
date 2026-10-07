"""Equation metadata consumed by the equation-aware inspector."""
from qmw.core import ModuleSpec, PortSpec, ParameterSpec


MODULE_SPECS = (
    ModuleSpec(
        id="regional_projection", title="Spatial regions and incoming flow",
        equation_latex=r"E_i=\Delta x\sum_n w_{in}\mathcal E_n,\quad F_i=-\Delta x\sum_n w_{in}\partial_x S_n",
        equation_text="E_i = dx sum_n w_i[n] e[n]; F_i = -dx sum_n w_i[n] d_x S[n]",
        inputs=(PortSpec("energy_density", "local energy", "scaled energy / length", "space_1d"),
                PortSpec("energy_flux", "energy flow", "scaled energy / time", "space_1d")),
        outputs=(PortSpec("regions.energy", "regional energy", "scaled energy", "region_index"),
                 PortSpec("regions.incoming_energy_flux", "incoming energy per simulation time", "scaled energy / time", "region_index")),
        parameters=(ParameterSpec("count", "Region count", 16, 1, 2048, "regions", "Number of contiguous bins in the projection, not simulation resolution."),),
        description="Masks partition the domain. Probability and charge use the same quadrature. Basis-index bins aggregate populations and have no spatial flux.",
        destinations=("flux_event_detector", "sonification_policy", "inspector"),
        assumptions=("Uniform periodic spatial domain", "sum_i w_i[n] = 1", "Incoming flow uses the observer's spectral derivative", "Sources/work are separate from transport"),
    ),
    ModuleSpec(
        id="modal_projection", title="Declared modal basis",
        equation_latex=r"c=B^\dagger W\psi,\quad M_j=|c_j|^2,\quad B^\dagger W B=I",
        equation_text="c = B† W psi; M_j = |c_j|²; B† W B = I",
        inputs=(PortSpec("state.psi", "pure-state field", "scaled amplitude", "space_1d"),),
        outputs=(PortSpec("modes.populations", "captured modal norm", "scaled norm", "mode_index"),),
        description="Periodic Fourier basis ordered 0,+1,-1,+2,-2… with eigenvalues k² of -d_x². These values are neither Hamiltonian energies nor audio Hz. Scalar field projections are L² amplitudes.",
        destinations=("sonification_policy", "inspector"),
        assumptions=("Fixed weighted orthonormal basis", "Spatial Fourier basis is not generally a potential-dependent Hamiltonian eigenbasis", "No dense spatial eigensystem"),
    ),
    ModuleSpec(
        id="mixed_modal_projection", title="Mixed-state basis populations",
        equation_latex=r"M_j=(B^\dagger\rho B)_{jj}",
        equation_text="M_j = diagonal(B† rho B)_j; coefficients = None",
        inputs=(PortSpec("state.rho", "density matrix", "probability", "basis_index"),),
        outputs=(PortSpec("modes.populations", "basis populations", "probability", "basis_index"),),
        description="Fixed computational basis by default; no complex coefficients or wavefunction phase are assigned to a mixed state. Basis labels do not set audible pitch.",
        destinations=("sonification_policy", "inspector"),
        assumptions=("Hermitian density matrix", "Unit-weight finite-dimensional inner product", "Basis index labels are not physical energies"),
    ),
    ModuleSpec(
        id="graph_modes", title="Undirected graph modes",
        equation_latex=r"L=D-A,\quad L\phi_j=\lambda_j\phi_j",
        equation_text="L = diagonal(A 1) - A; L phi_j = lambda_j phi_j",
        inputs=(PortSpec("adjacency", "symmetric nonnegative edge weights", "scaled coupling", "graph"),),
        outputs=(PortSpec("eigenvalues", "graph Laplacian spectrum", "scaled coupling", "mode_index"),),
        description="Includes every zero mode. Frequencies or Q require an explicit acoustic or musical mapping; geometry alone does not prescribe damping.",
        destinations=("graph_modal_projection", "inspector"),
        assumptions=("Real undirected graph", "Nonnegative edge weights", "No self loops", "Degenerate eigenvectors are basis dependent"),
    ),
)
