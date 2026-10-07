"""State-owning free scalar quantum-field engine for synchronized QMW ticks.

The engine composes the existing qmw.qft Klein-Gordon lattice,
Gaussian-state validation, symplectic evolution, and observable frame. It is
independent of the authoritative finite-qubit density matrix and of the GPE
mean-field engine. It contains no OSC, UI, sonification, quench, or feedback.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from threading import RLock
from types import MappingProxyType

import numpy as np

from qmw.qft.gaussian import GaussianFieldState, evolve_gaussian, vacuum_state
from qmw.qft.model import ScalarFieldModel, ScalarFieldSpec
from qmw.qft.observables import frame_from_gaussian
from qmw.qft.schema import ScalarFieldFrame


_ARRAY_FIELDS = (
    "mean_phi",
    "mean_pi",
    "covariance_phi",
    "covariance_pi",
    "covariance_phi_pi",
    "frequencies",
    "mode_occupations",
    "local_energy_density",
)


def _sealed_scalar_frame(frame: ScalarFieldFrame) -> ScalarFieldFrame:
    """Copy one native scalar frame into a deeply read-only publication."""

    changes: dict[str, object] = {}
    for name in _ARRAY_FIELDS:
        values = np.array(getattr(frame, name), copy=True)
        values.setflags(write=False)
        changes[name] = values
    if frame.rho is not None:
        density = np.array(frame.rho, copy=True)
        density.setflags(write=False)
        changes["rho"] = density
    changes["backend_metadata"] = MappingProxyType(dict(frame.backend_metadata))
    return replace(frame, **changes)


@dataclass(frozen=True)
class QuantumFieldFrame:
    """One immutable revision of the independent free scalar field."""

    revision: int
    time: float
    spec: ScalarFieldSpec
    scalar: ScalarFieldFrame
    provenance: str = "qmw_free_scalar_quantum_field_engine_v1"
    intervention_label: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.revision, bool) or int(self.revision) != self.revision or self.revision < 0:
            raise ValueError("revision must be a nonnegative integer")
        logical_time = float(self.time)
        if not math.isfinite(logical_time):
            raise ValueError("time must be finite")
        if not isinstance(self.spec, ScalarFieldSpec):
            raise TypeError("spec must be a ScalarFieldSpec")
        if not isinstance(self.scalar, ScalarFieldFrame):
            raise TypeError("scalar must be a ScalarFieldFrame")
        if not math.isclose(self.scalar.time, logical_time, rel_tol=0.0, abs_tol=1.0e-12):
            raise ValueError("scalar frame time must equal quantum-field time")
        if self.scalar.sites != self.spec.sites:
            raise ValueError("scalar frame sites must match the field specification")
        if any(np.asarray(getattr(self.scalar, name)).flags.writeable for name in _ARRAY_FIELDS):
            raise ValueError("published scalar-field arrays must be read-only")
        if self.scalar.rho is not None and np.asarray(self.scalar.rho).flags.writeable:
            raise ValueError("published exact-backend rho must be read-only")
        if not isinstance(self.scalar.backend_metadata, MappingProxyType):
            raise ValueError("published backend metadata must be read-only")
        if not self.provenance:
            raise ValueError("provenance must be nonempty")
        if self.intervention_label is not None and not str(self.intervention_label):
            raise ValueError("intervention_label must be nonempty when supplied")
        object.__setattr__(self, "revision", int(self.revision))
        object.__setattr__(self, "time", logical_time)

    @property
    def mean_energy(self) -> float:
        return float(self.scalar.mean_energy)

    @property
    def purity(self) -> float:
        return float(self.scalar.purity)


class QuantumFieldEngine:
    """Own and evolve one finite-lattice Gaussian quantum field.

    Evolution is exact for the declared free quadratic lattice Hamiltonian.
    advance updates only the engine's Gaussian field state. It never reads or
    writes a QMW qubit rho and never evolves a GPE psi.
    """

    def __init__(
        self,
        spec: ScalarFieldSpec | None = None,
        *,
        initial_state: GaussianFieldState | None = None,
        initial_time: float = 0.0,
    ) -> None:
        logical_time = float(initial_time)
        if not math.isfinite(logical_time):
            raise ValueError("initial_time must be finite")
        self._lock = RLock()
        self._model = ScalarFieldModel.from_spec(spec)
        self._state = (
            vacuum_state(self._model)
            if initial_state is None
            else initial_state.validated(self._model)
        )
        self._time = logical_time
        self._revision = 0
        self._frame = self._observe()

    @property
    def spec(self) -> ScalarFieldSpec:
        return self._model.spec

    @property
    def time(self) -> float:
        with self._lock:
            return self._time

    @property
    def revision(self) -> int:
        with self._lock:
            return self._revision

    @staticmethod
    def _make_frame(
        model: ScalarFieldModel,
        state: GaussianFieldState,
        *,
        time: float,
        revision: int,
        intervention_label: str | None = None,
    ) -> QuantumFieldFrame:
        scalar = frame_from_gaussian(
            state,
            model,
            time=time,
            backend="gaussian_free_scalar_runtime",
            backend_metadata={
                "authoritative_for_field": True,
                "independent_of_qubit_rho": True,
                "independent_of_gpe_psi": True,
                "representation": "lattice_canonical_covariance",
                "phase_space_order": "phi[0:L],pi[0:L]",
                "boundary": model.spec.boundary,
                "interaction": "free_nearest_neighbor_klein_gordon",
                "quench_applied": intervention_label is not None,
                "intervention_label": intervention_label,
                "physical_qubit_field_claim": False,
            },
        )
        return QuantumFieldFrame(
            revision=revision,
            time=time,
            spec=model.spec,
            scalar=_sealed_scalar_frame(scalar),
            intervention_label=intervention_label,
        )

    def _observe(self) -> QuantumFieldFrame:
        return self._make_frame(
            self._model,
            self._state,
            time=self._time,
            revision=self._revision,
        )

    def snapshot(self) -> QuantumFieldFrame:
        """Return the already-sealed current field frame."""

        with self._lock:
            return self._frame

    def advance(self, duration: float) -> QuantumFieldFrame:
        """Advance by a finite nonnegative model-time duration."""

        elapsed = float(duration)
        if not math.isfinite(elapsed) or elapsed < 0.0:
            raise ValueError("duration must be finite and nonnegative")
        with self._lock:
            if elapsed == 0.0:
                return self._frame
            next_state = evolve_gaussian(self._state, self._model, elapsed)
            self._state = next_state
            self._time += elapsed
            self._revision += 1
            self._frame = self._observe()
            return self._frame

    def advance_to(self, time: float) -> QuantumFieldFrame:
        """Advance monotonically to the supplied synchronized model time."""

        target = float(time)
        if not math.isfinite(target):
            raise ValueError("target time must be finite")
        with self._lock:
            delta = target - self._time
            if delta < -1.0e-12:
                raise ValueError("quantum field cannot advance backward in time")
            return self.advance(max(0.0, delta))

    def apply_generator_quench(
        self,
        spec: ScalarFieldSpec,
        *,
        label: str,
    ) -> tuple[QuantumFieldFrame, QuantumFieldFrame]:
        """Atomically replace the free-field generator at the current time."""

        if not isinstance(spec, ScalarFieldSpec):
            raise TypeError("spec must be a ScalarFieldSpec")
        if not str(label):
            raise ValueError("label must be nonempty")
        with self._lock:
            current = self._model.spec
            invariant_names = ("sites", "lattice_spacing", "hbar", "boundary")
            if any(getattr(spec, name) != getattr(current, name) for name in invariant_names):
                raise ValueError(
                    "a v1 quench must preserve sites, lattice spacing, hbar, and boundary"
                )
            if spec.mass == current.mass and spec.propagation_speed == current.propagation_speed:
                raise ValueError("quench must change mass or propagation speed")
            next_model = ScalarFieldModel.from_spec(spec)
            continuous_state = self._state.validated(next_model)
            next_revision = self._revision + 1
            next_frame = self._make_frame(
                next_model,
                continuous_state,
                time=self._time,
                revision=next_revision,
                intervention_label=str(label),
            )
            previous = self._frame
            self._model = next_model
            self._state = continuous_state
            self._revision = next_revision
            self._frame = next_frame
            return previous, next_frame


__all__ = ["QuantumFieldEngine", "QuantumFieldFrame"]
