import numpy as np

from core.hamiltonian import make_four_qubit_hamiltonian, make_measurement_operator


def parse_temperature(value):
    if value is None:
        return None

    if isinstance(value, str):
        v = value.lower()

        if v in ["none", "ground", "0"]:
            return None

        if v in ["inf", "infinity", "infinite"]:
            return np.inf

        return float(value)

    return float(value)


def thermal_populations(energies, temperature="inf"):
    """
    None / ground / 0 = ground state only
    inf = equal population of all levels
    finite number = Boltzmann distribution
    """
    temperature = parse_temperature(temperature)
    n = len(energies)

    if temperature is None:
        p = np.zeros(n)
        p[0] = 1.0
        return p

    if np.isinf(temperature):
        return np.ones(n) / n

    shifted = energies - np.min(energies)
    beta = 1.0 / max(float(temperature), 1e-9)
    weights = np.exp(-beta * shifted)

    return weights / np.sum(weights)


def transition_spectrum(
    field_z=(1.00, 1.17, 1.37, 1.61),
    coupling_xx=0.35,
    coupling_zz=0.18,
    coupling_dm=0.30,
    temperature="inf",
    min_intensity=1e-8,
    max_lines=64,
):
    """
    Computes the allowed Bohr transitions of the 4-qubit Hamiltonian.

    Frequencies are energy differences:

        delta_e = E_m - E_n

    Intensities are transition matrix elements:

        population_n * |A_nm|^2

    where A is the measurement/dipole operator.
    """
    H = make_four_qubit_hamiltonian(
        field_z=field_z,
        coupling_xx=coupling_xx,
        coupling_zz=coupling_zz,
        coupling_dm=coupling_dm,
    )

    A = make_measurement_operator()

    energies, vecs = np.linalg.eigh(H)

    # Transform measurement operator into the energy eigenbasis.
    A_energy = vecs.conj().T @ A @ vecs

    populations = thermal_populations(energies, temperature)

    lines = []

    for n in range(len(energies)):
        for m in range(n + 1, len(energies)):
            delta_e = float(np.real(energies[m] - energies[n]))

            matrix_element = A_energy[n, m]
            matrix_abs = float(abs(matrix_element))

            intensity = float(np.real(populations[n] * matrix_abs**2))

            if intensity > min_intensity:
                lines.append(
                    {
                        "n": n,
                        "m": m,
                        "delta_e": delta_e,
                        "ratio": None,
                        "intensity": intensity,
                        "phase": float(np.angle(matrix_element)),
                        "matrix_abs": matrix_abs,
                        "population": float(populations[n]),
                    }
                )

    lines.sort(key=lambda line: line["delta_e"])

    if lines:
        fundamental = lines[0]["delta_e"]
        for line in lines:
            line["ratio"] = line["delta_e"] / fundamental

    return lines[: int(max_lines)], energies


def print_transition_spectrum(lines):
    print()
    print("Transition spectrum:")
    print("idx | n->m | ratio | intensity | phase | |A_nm| | pop")
    print("-" * 68)

    for i, line in enumerate(lines):
        print(
            f"{i:02d}  | "
            f"{line['n']:02d}->{line['m']:02d} | "
            f"{line['ratio']:6.3f} | "
            f"{line['intensity']:.6f} | "
            f"{line['phase']:+.3f} | "
            f"{line['matrix_abs']:.6f} | "
            f"{line['population']:.4f}"
        )

    print()
