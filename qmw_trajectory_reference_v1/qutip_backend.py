"""Optional QuTiP reference solver for the declared XY model.

The NumPy eigendecomposition remains the runnable baseline.  This backend is
an independent numerical comparison only when QuTiP is installed.
"""

from __future__ import annotations

import numpy as np

from .xy import FourQubitXYModel, QuantumTrajectory
from .open_system import run_xy_dephasing_trajectory


def run_xy_qutip_trajectory(
    *,
    samples: int = 2048,
    duration: float = 24.0,
    model: FourQubitXYModel | None = None,
) -> QuantumTrajectory:
    """Use QuTiP ``mesolve`` with no collapse operators for a closed reference."""
    try:
        import qutip
    except ImportError as exc:  # pragma: no cover - depends on optional package
        raise RuntimeError("QuTiP is not installed; use the exact NumPy backend or install qutip.") from exc
    selected = model if model is not None else FourQubitXYModel()
    if int(samples) != samples or int(samples) < 2 or not np.isfinite(float(duration)) or duration <= 0.0:
        raise ValueError("samples must be at least two and duration must be finite and positive.")
    time = np.linspace(0.0, float(duration), int(samples), dtype=float)
    result = qutip.mesolve(
        qutip.Qobj(selected.hamiltonian), qutip.Qobj(selected.initial_state), time, c_ops=[],
        options={"atol": 1.0e-12, "rtol": 1.0e-10, "nsteps": 10000},
    )
    state = np.stack([np.asarray(item.full(), dtype=np.complex128).reshape(-1) for item in result.states])
    rho = np.einsum("ti,tj->tij", state, state.conj())
    populations = np.stack(
        [np.real(np.einsum("tij,ji->t", rho, operator)) for operator in selected.site_number_operators], axis=1,
    )
    currents = []
    for bond, number_left in zip(selected.bond_hamiltonians, selected.site_number_operators):
        derivative = (-1.0j / selected.hbar) * (bond @ rho - rho @ bond)
        currents.append(-np.real(np.einsum("tij,ji->t", derivative, number_left)))
    return QuantumTrajectory(
        time=time, state=state, rho=rho, site_populations=populations,
        edge_current_left_to_right=np.stack(currents, axis=1), hamiltonian=selected.hamiltonian, model=selected,
        metadata={
            "backend": "qutip.mesolve_closed_reference",
            "initial_state": "|1000>",
            "basis_order": "q0 q1 q2 q3, q0 most-significant bit",
            "scientific_role": "optional offline reference trajectory",
        },
    )


def run_xy_qutip_dephasing_trajectory(*, gamma_phi: float, samples: int = 2048, duration: float = 24.0, model: FourQubitXYModel | None = None) -> QuantumTrajectory:
    """QuTiP reference for the same local pure-dephasing GKSL generator."""
    try:
        import qutip
    except ImportError as exc:
        raise RuntimeError("QuTiP is not installed.") from exc
    if not np.isfinite(gamma_phi) or gamma_phi < 0.0:
        raise ValueError("gamma_phi must be finite and nonnegative.")
    selected = model or FourQubitXYModel()
    time = np.linspace(0.0, duration, int(samples))
    operators = [np.eye(selected.dimension) - 2.0 * operator for operator in selected.site_number_operators]
    result = qutip.mesolve(qutip.Qobj(selected.hamiltonian), qutip.Qobj(selected.initial_state), time,
        c_ops=[np.sqrt(gamma_phi) * qutip.Qobj(operator) for operator in operators],
        options={"atol": 1e-12, "rtol": 1e-10, "nsteps": 10000})
    rho = np.stack([np.asarray(item.full(), dtype=complex) for item in result.states])
    populations = np.stack([np.real(np.einsum("tij,ji->t", rho, operator)) for operator in selected.site_number_operators], axis=1)
    currents = []
    for bond, number_left in zip(selected.bond_hamiltonians, selected.site_number_operators):
        derivative = -1j / selected.hbar * (bond @ rho - rho @ bond)
        currents.append(-np.real(np.einsum("tij,ji->t", derivative, number_left)))
    return QuantumTrajectory(time=time, state=None, rho=rho, site_populations=populations,
        edge_current_left_to_right=np.stack(currents, axis=1), hamiltonian=selected.hamiltonian, model=selected,
        metadata={"backend": "qutip.mesolve_gksl", "channel": "local_pure_dephasing", "gamma_phi": float(gamma_phi)})
