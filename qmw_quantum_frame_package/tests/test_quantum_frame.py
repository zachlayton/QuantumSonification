import numpy as np

from qmw.core.quantum_frame import QuantumFrame


def test_pure_state_frame():
    t = np.linspace(0, 1, 8)
    psi = np.zeros((8, 2), dtype=complex)
    psi[:, 0] = 1.0
    rho = np.einsum("ti,tj->tij", psi, psi.conj())

    frame = QuantumFrame(t=t, psi=psi, rho=rho)
    result = frame.validate()

    assert frame.samples == 8
    assert frame.hilbert_dim == 2
    assert result["trace_error_max"] < 1e-12
    assert result["state_norm_error_max"] < 1e-12
    assert result["positive_semidefinite"]
