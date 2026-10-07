"""Graph Laplacian modes: geometry spectra, not quantum energies or audio Hz."""
import numpy as np
from qmw.core import Domain, PhysicsFrame, ModalData
from ._validation import require_count, require_frame_domain, require_density_matrix, real_values


class GraphModes:
    """Cached eigensystem of L=diag(A1)-A for a finite undirected graph.

    All modes, including the constant zero mode and disconnected-component
    zero modes, remain available. Any acoustic mapping must choose explicitly
    whether to exclude a zero mode. Degenerate eigenspaces have no canonical
    individual eigenvectors; the eigensystem is fixed after construction.
    """

    def __init__(self, adjacency):
        raw = np.asarray(adjacency)
        if raw.ndim != 2 or raw.shape[0] != raw.shape[1] or raw.shape[0] < 1:
            raise ValueError("Adjacency must be a nonempty square matrix")
        if not np.isfinite(raw).all() or np.iscomplexobj(raw):
            raise ValueError("Adjacency must be real and finite")
        a = raw.astype(float, copy=True)
        if np.any(a < 0) or not np.allclose(a, a.T, atol=1e-12, rtol=0.0):
            raise ValueError("Adjacency must be symmetric with nonnegative weights")
        if not np.allclose(np.diag(a), 0.0, atol=1e-12, rtol=0.0):
            raise ValueError("This graph model requires zero diagonal (no self loops)")
        self.adjacency = a
        self.laplacian = np.diag(a.sum(axis=1)) - a
        self.eigenvalues, self.basis = np.linalg.eigh(self.laplacian)
        # Remove sign ambiguity only; do not rotate degenerate subspaces.
        for column in range(a.shape[0]):
            nonzero = np.flatnonzero(np.abs(self.basis[:, column]) > 1e-12)
            if nonzero.size and self.basis[nonzero[0], column] < 0:
                self.basis[:, column] *= -1
        self.operator_semantics = "graph_laplacian_eigenvalues_not_quantum_energy_or_audio_hz"
        for values in (self.adjacency, self.laplacian, self.eigenvalues, self.basis):
            values.setflags(write=False)


class GraphModalProjector:
    def __init__(self, domain: Domain, graph_modes: GraphModes, count: int | None = None):
        if domain.kind not in ("graph", "basis_index") or len(domain.shape) != 1:
            raise ValueError("Graph projection requires graph or basis_index coordinates")
        if graph_modes.basis.shape[0] != domain.size:
            raise ValueError("Graph node count differs from domain size")
        self.count = domain.size if count is None else count
        require_count(self.count, domain.size)
        self.domain = domain
        self.graph_modes = graph_modes
        self.basis = graph_modes.basis[:, :self.count]
        self.eigenvalues = graph_modes.eigenvalues[:self.count]
        self.operator_semantics = graph_modes.operator_semantics
        self.basis_id = "undirected_graph_laplacian"
        self.mode_labels = [f"graph mode {index}" for index in range(self.count)]

    def project(self, frame: PhysicsFrame) -> ModalData:
        require_frame_domain(frame, self.domain)
        state = frame.state
        coefficients = None
        semantics = self.operator_semantics
        if state.rho is not None:
            rho = require_density_matrix(state.rho, self.domain.size)
            populations = real_values(np.diag(self.basis.conj().T @ rho @ self.basis),
                                      (self.count,), "graph populations").copy()
        else:
            values = state.psi if state.psi is not None else state.phi
            coefficients = self.basis.conj().T @ values
            populations = np.abs(coefficients) ** 2
            if state.phi is not None:
                semantics += ";scalar_field_l2_amplitudes_not_quantum_probabilities"
        return ModalData(self.basis_id, self.eigenvalues.copy(), coefficients,
                         populations, float(populations.sum()), semantics,
                         self.mode_labels.copy())
