"""Explicit sudden-generator interventions for QuantumFieldEngine."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from threading import RLock

import numpy as np

from qmw.qft.model import ScalarFieldModel, ScalarFieldSpec
from qmw.quantum_field import QuantumFieldEngine, QuantumFieldFrame


def _readonly(values: object) -> np.ndarray:
    result = np.array(values, dtype=float, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class QuenchRequest:
    """One queued change of mass and/or propagation speed."""

    request_id: int
    mass: float | None = None
    propagation_speed: float | None = None
    label: str = "field_generator_quench"

    def __post_init__(self) -> None:
        if isinstance(self.request_id, bool) or int(self.request_id) != self.request_id or self.request_id < 1:
            raise ValueError("request_id must be a positive integer")
        if self.mass is None and self.propagation_speed is None:
            raise ValueError("a quench must request mass or propagation speed")
        for name in ("mass", "propagation_speed"):
            value = getattr(self, name)
            if value is not None and (not math.isfinite(float(value)) or float(value) <= 0.0):
                raise ValueError(f"{name} must be finite and positive when supplied")
        if not str(self.label):
            raise ValueError("label must be nonempty")


@dataclass(frozen=True)
class QuenchFrame:
    """Auditable discontinuous generator change at one continuous field state."""

    revision: int
    time: float
    request: QuenchRequest
    source_field_revision: int
    result_field_revision: int
    before_spec: ScalarFieldSpec
    after_spec: ScalarFieldSpec
    before_frequencies: np.ndarray
    after_frequencies: np.ndarray
    bogoliubov_mu: np.ndarray
    bogoliubov_nu: np.ndarray
    mean_continuity_error: float
    covariance_continuity_error: float
    energy_before: float
    energy_after: float
    injected_work: float
    provenance: str = "explicit_free_scalar_generator_quench_v1"

    def __post_init__(self) -> None:
        if isinstance(self.revision, bool) or int(self.revision) != self.revision or self.revision < 1:
            raise ValueError("revision must be a positive integer")
        logical_time = float(self.time)
        if not math.isfinite(logical_time):
            raise ValueError("time must be finite")
        if not isinstance(self.request, QuenchRequest):
            raise TypeError("request must be a QuenchRequest")
        if not isinstance(self.before_spec, ScalarFieldSpec) or not isinstance(self.after_spec, ScalarFieldSpec):
            raise TypeError("before_spec and after_spec must be ScalarFieldSpec values")
        before = _readonly(self.before_frequencies)
        after = _readonly(self.after_frequencies)
        mu = _readonly(self.bogoliubov_mu)
        nu = _readonly(self.bogoliubov_nu)
        if not before.shape or after.shape != before.shape or mu.shape != before.shape or nu.shape != before.shape:
            raise ValueError("quench mode diagnostics must share one nonempty shape")
        if np.any(before <= 0.0) or np.any(after <= 0.0):
            raise ValueError("quench frequencies must be positive")
        if not np.allclose(mu * mu - nu * nu, 1.0, atol=1.0e-10, rtol=1.0e-10):
            raise ValueError("Bogoliubov coefficients must preserve the canonical relation")
        errors = (float(self.mean_continuity_error), float(self.covariance_continuity_error))
        if any(not math.isfinite(value) or value < 0.0 for value in errors):
            raise ValueError("continuity errors must be finite and nonnegative")
        energies = (float(self.energy_before), float(self.energy_after), float(self.injected_work))
        if any(not math.isfinite(value) for value in energies):
            raise ValueError("quench energies must be finite")
        if not math.isclose(energies[2], energies[1] - energies[0], abs_tol=1.0e-10, rel_tol=1.0e-10):
            raise ValueError("injected_work must equal energy_after - energy_before")
        if self.result_field_revision != self.source_field_revision + 1:
            raise ValueError("a quench must advance the field revision exactly once")
        if not self.provenance:
            raise ValueError("provenance must be nonempty")
        object.__setattr__(self, "revision", int(self.revision))
        object.__setattr__(self, "time", logical_time)
        object.__setattr__(self, "before_frequencies", before)
        object.__setattr__(self, "after_frequencies", after)
        object.__setattr__(self, "bogoliubov_mu", mu)
        object.__setattr__(self, "bogoliubov_nu", nu)
        object.__setattr__(self, "mean_continuity_error", errors[0])
        object.__setattr__(self, "covariance_continuity_error", errors[1])
        object.__setattr__(self, "energy_before", energies[0])
        object.__setattr__(self, "energy_after", energies[1])
        object.__setattr__(self, "injected_work", energies[2])


class QuenchEngine:
    """Queue and apply explicit scalar-field generator changes FIFO."""

    def __init__(self, field_engine: QuantumFieldEngine) -> None:
        if not isinstance(field_engine, QuantumFieldEngine):
            raise TypeError("field_engine must be a QuantumFieldEngine")
        self.field_engine = field_engine
        self._lock = RLock()
        self._pending: list[QuenchRequest] = []
        self._next_request_id = 1
        self._revision = 0

    @property
    def pending(self) -> tuple[QuenchRequest, ...]:
        with self._lock:
            return tuple(self._pending)

    def schedule(
        self,
        *,
        mass: float | None = None,
        propagation_speed: float | None = None,
        label: str = "field_generator_quench",
    ) -> QuenchRequest:
        with self._lock:
            request = QuenchRequest(
                request_id=self._next_request_id,
                mass=mass,
                propagation_speed=propagation_speed,
                label=label,
            )
            self._next_request_id += 1
            self._pending.append(request)
            return request

    def apply_next(self, *, time: float | None = None) -> tuple[QuenchFrame, QuantumFieldFrame]:
        with self._lock:
            if not self._pending:
                raise RuntimeError("no field quench is pending")
            request = self._pending[0]
            before = self.field_engine.snapshot()
            if time is not None and not math.isclose(float(time), before.time, rel_tol=0.0, abs_tol=1.0e-12):
                raise ValueError("quench time must equal the current quantum-field time")
            target = replace(
                before.spec,
                mass=before.spec.mass if request.mass is None else float(request.mass),
                propagation_speed=(
                    before.spec.propagation_speed
                    if request.propagation_speed is None
                    else float(request.propagation_speed)
                ),
            )
            before_model = ScalarFieldModel.from_spec(before.spec)
            after_model = ScalarFieldModel.from_spec(target)
            before_frequency = before_model.frequencies
            after_frequency = after_model.frequencies
            ratio = np.sqrt(after_frequency / before_frequency)
            inverse = 1.0 / ratio
            mu = 0.5 * (ratio + inverse)
            nu = 0.5 * (ratio - inverse)
            previous, after = self.field_engine.apply_generator_quench(target, label=request.label)
            mean_error = float(
                np.linalg.norm(after.scalar.mean_phi - previous.scalar.mean_phi)
                + np.linalg.norm(after.scalar.mean_pi - previous.scalar.mean_pi)
            )
            covariance_error = float(
                np.linalg.norm(after.scalar.covariance_phi - previous.scalar.covariance_phi)
                + np.linalg.norm(after.scalar.covariance_pi - previous.scalar.covariance_pi)
                + np.linalg.norm(after.scalar.covariance_phi_pi - previous.scalar.covariance_phi_pi)
            )
            self._revision += 1
            event = QuenchFrame(
                revision=self._revision,
                time=after.time,
                request=request,
                source_field_revision=previous.revision,
                result_field_revision=after.revision,
                before_spec=previous.spec,
                after_spec=after.spec,
                before_frequencies=before_frequency,
                after_frequencies=after_frequency,
                bogoliubov_mu=mu,
                bogoliubov_nu=nu,
                mean_continuity_error=mean_error,
                covariance_continuity_error=covariance_error,
                energy_before=previous.mean_energy,
                energy_after=after.mean_energy,
                injected_work=after.mean_energy - previous.mean_energy,
            )
            self._pending.pop(0)
            return event, after


__all__ = ["QuenchEngine", "QuenchFrame", "QuenchRequest"]
