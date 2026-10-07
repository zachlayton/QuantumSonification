"""Fixed periodic Fourier modes and fixed computational basis populations."""
import numpy as np
from qmw.core import Domain, PhysicsFrame, ModalData
from ._validation import require_count, require_frame_domain, require_density_matrix, real_values


class ModalProjector:
    """Project in a declared cached basis without inferring audible frequencies.

    Spatial eigenvalues belong to -d_x². Computational-basis 'eigenvalues'
    are the eigenvalues of the bookkeeping label operator diag(0,1,...),
    explicitly marked as basis indices rather than energies or frequencies.
    The basis remains fixed for rho: mixed states have no unique phase.
    """

    def __init__(self, domain: Domain, count: int = 16):
        if domain.kind not in ("space_1d", "basis_index"):
            raise ValueError("Modal projection requires space_1d or basis_index")
        if len(domain.shape) != 1:
            raise ValueError("Modal projection requires a one-dimensional sample array")
        require_count(count, domain.size)
        self.domain = domain
        self.count = count
        if domain.kind == "space_1d":
            domain.require_periodic_space()
            # Generate FFT-supported indices exactly once; even-N Nyquist is -N/2.
            supported = set(np.rint(np.fft.fftfreq(domain.size) * domain.size).astype(int))
            ordered = [0]
            for magnitude in range(1, domain.size // 2 + 1):
                for candidate in (magnitude, -magnitude):
                    if candidate in supported:
                        ordered.append(candidate)
            self.mode_indices = np.asarray(ordered[:count], dtype=int)
            self.wavenumbers = 2 * np.pi * self.mode_indices / domain.length
            self.basis = np.exp(1j * domain.coordinates[:, None] * self.wavenumbers[None, :]) / np.sqrt(domain.length)
            self.eigenvalues = self.wavenumbers ** 2
            self.basis_id = "periodic_fourier"
            self.operator_semantics = "negative_spatial_laplacian_k_squared_not_energy_or_audio_hz"
            self.mode_labels = ["k=0" if k == 0 else f"k={k:+d}" for k in self.mode_indices]
        else:
            self.mode_indices = np.arange(count, dtype=int)
            self.wavenumbers = None
            self.basis = np.eye(domain.size, count, dtype=complex)
            self.eigenvalues = self.mode_indices.astype(float)
            self.basis_id = "computational"
            self.operator_semantics = "basis_index_not_energy"
            self.mode_labels = [f"basis {index}" for index in self.mode_indices]
        for a in (self.mode_indices, self.basis, self.eigenvalues, self.wavenumbers):
            if a is not None:
                a.setflags(write=False)
        self._weighted_adjoint = self.basis.conj().T * domain.weights[None, :]
        self._weighted_adjoint.setflags(write=False)

    def project(self, frame: PhysicsFrame) -> ModalData:
        require_frame_domain(frame, self.domain)
        state = frame.state
        coefficients = None
        semantics = self.operator_semantics
        if state.rho is not None:
            if self.domain.kind != "basis_index":
                raise ValueError("rho modal projection requires basis_index coordinates")
            rho = require_density_matrix(state.rho, self.domain.size)
            projected = self.basis.conj().T @ rho @ self.basis
            populations = real_values(np.diag(projected), (self.count,), "modal populations").copy()
        else:
            values = state.psi if state.psi is not None else state.phi
            coefficients = self._weighted_adjoint @ values
            populations = np.abs(coefficients) ** 2
            if state.phi is not None:
                semantics += ";scalar_field_l2_amplitudes_not_quantum_probabilities"
        return ModalData(
            basis_id=self.basis_id,
            eigenvalues=self.eigenvalues.copy(),
            coefficients=coefficients,
            populations=populations,
            captured_norm=float(populations.sum()),
            operator_semantics=semantics,
            mode_labels=self.mode_labels.copy(),
        )
