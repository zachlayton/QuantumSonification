import numpy as np


def pauli_matrices():
    I = np.array([[1, 0], [0, 1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    return {"I": I, "X": X, "Y": Y, "Z": Z}


def pauli_string(label):
    mats = pauli_matrices()
    out = mats[label[0]]

    for char in label[1:]:
        out = np.kron(out, mats[char])

    return out


def make_four_qubit_hamiltonian(
    field_z=(1.00, 1.17, 1.37, 1.61),
    coupling_xx=0.35,
    coupling_zz=0.18,
    coupling_dm=0.30,
):
    """
    Four-qubit complex-Hermitian Hamiltonian.

    Includes:
    - local Z fields
    - nearest-neighbor XX coupling
    - nearest-neighbor ZZ coupling
    - Dzyaloshinskii-Moriya-like XY - YX term
    """
    H = np.zeros((16, 16), dtype=complex)

    for q, strength in enumerate(field_z):
        label = ["I"] * 4
        label[q] = "Z"
        H += strength * pauli_string("".join(label))

    for q in range(3):
        xx = ["I"] * 4
        xx[q] = "X"
        xx[q + 1] = "X"
        H += coupling_xx * pauli_string("".join(xx))

        zz = ["I"] * 4
        zz[q] = "Z"
        zz[q + 1] = "Z"
        H += coupling_zz * pauli_string("".join(zz))

        xy = ["I"] * 4
        xy[q] = "X"
        xy[q + 1] = "Y"

        yx = ["I"] * 4
        yx[q] = "Y"
        yx[q + 1] = "X"

        H += coupling_dm * (
            pauli_string("".join(xy)) - pauli_string("".join(yx))
        )

    herm_error = np.max(np.abs(H - H.conj().T))
    if herm_error > 1e-9:
        raise ValueError(f"Hamiltonian is not Hermitian: {herm_error}")

    return H


def make_measurement_operator():
    """
    Dipole/readout operator.

    This determines which transitions are bright or dark.
    """
    A = np.zeros((16, 16), dtype=complex)

    for q in range(4):
        label = ["I"] * 4
        label[q] = "X"
        A += pauli_string("".join(label))

    return A
