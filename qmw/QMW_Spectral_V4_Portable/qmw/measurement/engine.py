"""Born probabilities and exact state/aperture current decomposition."""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from qmw.quantum.hilbert_current import hermitian_matrix
from .basis_motion import ProjectorBasisMotion
from .projector import ProjectorBank


Array = np.ndarray


@dataclass(frozen=True)
class MeasurementFrame:
    revision: int
    time: float
    bank_id: str
    names: tuple[str, ...]
    probabilities: Array
    state_current: Array
    aperture_current: Array
    total_current: Array
    finite_difference_rate: Array | None
    finite_difference_residual: Array | None
    shannon_entropy: float
    complete: bool
    provenance: str = "projective_born_measurement_and_exact_flow_split_v1"


class ProjectiveMeasurementEngine:
    def __init__(self, *, tolerance: float = 1.0e-9) -> None:
        if not math.isfinite(float(tolerance)) or tolerance <= 0.0:
            raise ValueError("tolerance must be finite and positive.")
        self.tolerance = float(tolerance)
        self._previous: MeasurementFrame | None = None

    def observe(
        self,
        rho: object,
        bank: ProjectorBank,
        *,
        revision: int,
        time: float,
        rho_dot: object | None = None,
        projector_dots: tuple[object, ...] | None = None,
    ) -> MeasurementFrame:
        density = hermitian_matrix("rho", rho)
        if density.shape != (bank.dimension, bank.dimension):
            raise ValueError("rho and projector bank must share a dimension.")
        trace = np.trace(density)
        eigenvalues = np.linalg.eigvalsh(density)
        if abs(float(np.imag(trace))) > self.tolerance or not np.isclose(
            float(np.real(trace)), 1.0, rtol=0.0, atol=self.tolerance,
        ) or float(np.min(eigenvalues)) < -self.tolerance:
            raise ValueError("rho must be a positive semidefinite trace-one density matrix.")
        if not math.isfinite(float(time)):
            raise ValueError("time must be finite.")
        derivative = np.zeros_like(density) if rho_dot is None else np.asarray(rho_dot, dtype=np.complex128)
        if derivative.shape != density.shape or not np.all(np.isfinite(derivative)):
            raise ValueError("rho_dot must be finite and match rho.")
        if not np.allclose(derivative, derivative.conj().T, rtol=0.0, atol=self.tolerance):
            raise ValueError("rho_dot must be Hermitian.")
        dots = tuple(np.zeros_like(density) for _ in bank.projectors) if projector_dots is None else tuple(
            np.asarray(item, dtype=np.complex128) for item in projector_dots
        )
        if len(dots) != len(bank.projectors) or any(item.shape != density.shape or not np.all(np.isfinite(item)) for item in dots):
            raise ValueError("projector_dots must provide one finite matrix per projector.")
        if any(not np.allclose(item, item.conj().T, rtol=0.0, atol=self.tolerance) for item in dots):
            raise ValueError("projector derivatives must be Hermitian.")
        probabilities = np.asarray([np.real(np.trace(density @ item.matrix)) for item in bank.projectors])
        if np.any(probabilities < -self.tolerance) or np.any(probabilities > 1.0 + self.tolerance):
            raise ValueError("projective probabilities must lie in [0, 1].")
        probabilities = np.clip(probabilities, 0.0, 1.0)
        if bank.complete and not np.isclose(np.sum(probabilities), 1.0, rtol=0.0, atol=self.tolerance):
            raise ValueError("complete PVM probabilities must sum to one.")
        state = np.asarray([np.real(np.trace(derivative @ item.matrix)) for item in bank.projectors])
        aperture = np.asarray([np.real(np.trace(density @ dot)) for dot in dots])
        total = state + aperture
        fd_rate = fd_residual = None
        previous = self._previous
        if previous is not None and previous.bank_id == bank.identifier:
            dt = float(time) - previous.time
            if dt <= 0.0:
                raise ValueError("time must increase between measurement frames.")
            fd_rate = (probabilities - previous.probabilities) / dt
            fd_residual = fd_rate - total
        nonzero = probabilities[probabilities > 0.0]
        frame = MeasurementFrame(
            revision=int(revision), time=float(time), bank_id=bank.identifier,
            names=bank.names, probabilities=np.array(probabilities, copy=True),
            state_current=np.array(state, copy=True), aperture_current=np.array(aperture, copy=True),
            total_current=np.array(total, copy=True),
            finite_difference_rate=None if fd_rate is None else np.array(fd_rate, copy=True),
            finite_difference_residual=None if fd_residual is None else np.array(fd_residual, copy=True),
            shannon_entropy=float(-np.sum(nonzero * np.log2(nonzero))), complete=bank.complete,
        )
        self._previous = frame
        return frame

    def observe_motion(
        self, rho: object, motion: ProjectorBasisMotion, *, revision: int, time: float,
        rho_dot: object | None = None,
    ) -> MeasurementFrame:
        return self.observe(
            rho, motion.bank_at(time), revision=revision, time=time, rho_dot=rho_dot,
            projector_dots=motion.derivatives_at(time),
        )


__all__ = ["MeasurementFrame", "ProjectiveMeasurementEngine"]
