"""Numerical parity checks between QMW's exact XY reference and QuTiP."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .qutip_backend import run_xy_qutip_trajectory, run_xy_qutip_dephasing_trajectory
from .open_system import run_xy_dephasing_trajectory
from .xy import QuantumTrajectory, run_xy_trajectory


@dataclass(frozen=True)
class XYParityReport:
    samples: int
    tolerance: float
    state_error_max: float | None
    rho_error_max: float
    population_error_max: float
    current_error_max: float

    @property
    def accepted(self) -> bool:
        values = [self.rho_error_max, self.population_error_max, self.current_error_max]
        if self.state_error_max is not None: values.append(self.state_error_max)
        return max(values) <= self.tolerance

    def as_dict(self) -> dict[str, float | int | bool]:
        return {"samples": self.samples, "tolerance": self.tolerance, "state_error_max": self.state_error_max,
                "rho_error_max": self.rho_error_max, "population_error_max": self.population_error_max,
                "current_error_max": self.current_error_max, "accepted": self.accepted}


def compare_trajectories(reference: QuantumTrajectory, candidate: QuantumTrajectory, *, tolerance: float = 1.0e-8) -> XYParityReport:
    if reference.samples != candidate.samples or not np.array_equal(reference.time, candidate.time):
        raise ValueError("parity comparison requires the identical time grid.")
    if not np.isfinite(float(tolerance)) or tolerance <= 0.0:
        raise ValueError("tolerance must be finite and positive.")
    # Global ket phase is immaterial; rho is the authoritative comparison.
    state_error = None
    if reference.state is not None and candidate.state is not None:
        overlaps = np.sum(reference.state.conj() * candidate.state, axis=1)
        phase = np.where(np.abs(overlaps) > 1.0e-14, overlaps.conj() / np.abs(overlaps), 1.0)
        state_error = float(np.max(np.abs(reference.state - candidate.state * phase[:, None])))
    return XYParityReport(
        samples=reference.samples, tolerance=float(tolerance), state_error_max=state_error,
        rho_error_max=float(np.max(np.abs(reference.rho - candidate.rho))),
        population_error_max=float(np.max(np.abs(reference.site_populations - candidate.site_populations))),
        current_error_max=float(np.max(np.abs(reference.edge_current_left_to_right - candidate.edge_current_left_to_right))),
    )


def run_xy_qutip_parity(*, samples: int = 2048, duration: float = 24.0, tolerance: float = 1.0e-8) -> XYParityReport:
    """Compare the exact NumPy reference with QuTiP ``mesolve`` on one grid."""
    return compare_trajectories(
        run_xy_trajectory(samples=samples, duration=duration),
        run_xy_qutip_trajectory(samples=samples, duration=duration),
        tolerance=tolerance,
    )


def run_xy_dephasing_qutip_parity(*, gamma_phi: float = 0.08, samples: int = 1024, duration: float = 12.0, tolerance: float = 1.0e-8) -> XYParityReport:
    return compare_trajectories(run_xy_dephasing_trajectory(gamma_phi=gamma_phi, samples=samples, duration=duration),
        run_xy_qutip_dephasing_trajectory(gamma_phi=gamma_phi, samples=samples, duration=duration), tolerance=tolerance)
