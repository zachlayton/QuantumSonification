from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

import numpy as np

from qmw.core.state_frame import QuantumStateFrame


DEFAULT_FRAME_SAMPLES = 2048


@dataclass
class PhysicsFrame:
    """Backend-independent time trajectory for QMW physics data.

    `QuantumStateFrame` remains the one-tick/live state object. `PhysicsFrame`
    is a contiguous trajectory or analysis block, conventionally 2048 samples.

    For a four-qubit quantum trajectory the canonical shapes are::

        t                              (2048,)
        psi                            (2048, 16)       optional
        rho                            (2048, 16, 16)   optional
        observables/site_populations   (2048, 4)
        observables/pauli_x            (2048, 4)
        observables/pauli_y            (2048, 4)
        observables/pauli_z            (2048, 4)
        observables/edge_currents      (2048, 3)
        diagnostics/energy             (2048,)
        diagnostics/commutator_activity (2048,)

    Purity, trace, and density-matrix eigenvalues are derived from `rho` so
    they are not stored redundantly.
    """

    t: np.ndarray
    psi: np.ndarray | None = None
    rho: np.ndarray | None = None
    observables: dict[str, np.ndarray] = field(default_factory=dict)
    diagnostics: dict[str, np.ndarray] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.t = np.asarray(self.t, dtype=float)
        if self.t.ndim != 1 or self.t.size == 0:
            raise ValueError("t must be a non-empty one-dimensional array")

        if self.psi is not None:
            self.psi = np.asarray(self.psi, dtype=complex)
            if self.psi.ndim != 2 or self.psi.shape[0] != self.samples:
                raise ValueError("psi must have shape (samples, hilbert_dim)")

        if self.rho is not None:
            self.rho = np.asarray(self.rho, dtype=complex)
            if self.rho.ndim != 3 or self.rho.shape[0] != self.samples:
                raise ValueError(
                    "rho must have shape (samples, hilbert_dim, hilbert_dim)"
                )
            if self.rho.shape[1] != self.rho.shape[2]:
                raise ValueError("rho matrices must be square")

        if (
            self.psi is not None
            and self.rho is not None
            and self.psi.shape[1] != self.rho.shape[1]
        ):
            raise ValueError("psi and rho Hilbert dimensions must agree")

        self.observables = self._coerce_sample_map(
            "observable", self.observables
        )
        self.diagnostics = self._coerce_sample_map(
            "diagnostic", self.diagnostics, allow_static=True
        )
        self.metadata.setdefault("samples", self.samples)
        if self.hilbert_dim is not None:
            self.metadata.setdefault("hilbert_dim", self.hilbert_dim)

    def _coerce_sample_map(
        self,
        kind: str,
        values: dict[str, np.ndarray],
        *,
        allow_static: bool = False,
    ) -> dict[str, np.ndarray]:
        out: dict[str, np.ndarray] = {}
        for name, value in values.items():
            arr = np.asarray(value)
            if arr.ndim == 0:
                if not allow_static:
                    raise ValueError(
                        f"{kind} '{name}' must have a sample dimension"
                    )
            elif arr.shape[0] != self.samples and not allow_static:
                raise ValueError(
                    f"{kind} '{name}' must begin with {self.samples} samples"
                )
            out[name] = arr
        return out

    @property
    def samples(self) -> int:
        return int(self.t.shape[0])

    @property
    def duration(self) -> float:
        return float(self.t[-1] - self.t[0]) if self.samples > 1 else 0.0

    @property
    def hilbert_dim(self) -> int | None:
        if self.rho is not None:
            return int(self.rho.shape[1])
        if self.psi is not None:
            return int(self.psi.shape[1])
        return None

    def trace(self) -> np.ndarray:
        if self.rho is None:
            raise ValueError("trace requires rho")
        return np.trace(self.rho, axis1=1, axis2=2)

    def purity(self) -> np.ndarray:
        if self.rho is None:
            raise ValueError("purity requires rho")
        return np.real(np.einsum("tij,tji->t", self.rho, self.rho))

    def density_eigenvalues(self) -> np.ndarray:
        if self.rho is None:
            raise ValueError("density eigenvalues require rho")
        return np.linalg.eigvalsh(self.rho)

    def expectation(self, operator: np.ndarray) -> np.ndarray:
        if self.rho is None:
            raise ValueError("expectation requires rho")
        operator = np.asarray(operator, dtype=complex)
        expected = (self.rho.shape[1], self.rho.shape[2])
        if operator.shape != expected:
            raise ValueError(f"operator must have shape {expected}")
        return np.real(np.einsum("tij,ji->t", self.rho, operator))

    def validate_quantum(
        self, *, atol: float = 1e-9
    ) -> dict[str, float | bool]:
        if self.rho is None:
            raise ValueError("quantum validation requires rho")

        hermiticity = self.rho - np.swapaxes(self.rho.conj(), 1, 2)
        eigs = self.density_eigenvalues()
        result: dict[str, float | bool] = {
            "trace_error_max": float(
                np.max(np.abs(self.trace() - 1.0))
            ),
            "hermiticity_error_max": float(
                np.max(np.linalg.norm(hermiticity, axis=(1, 2)))
            ),
            "min_density_eigenvalue": float(np.min(eigs)),
            "positive_semidefinite": bool(np.min(eigs) >= -atol),
        }

        if self.psi is not None:
            norms = np.sum(np.abs(self.psi) ** 2, axis=1)
            result["state_norm_error_max"] = float(
                np.max(np.abs(norms - 1.0))
            )

        return result

    @classmethod
    def from_state_frames(
        cls, frames: Iterable[QuantumStateFrame]
    ) -> "PhysicsFrame":
        """Stack live `QuantumStateFrame` ticks into one trajectory block.

        Numeric observables and arrays present with consistent shape in every
        tick are stacked automatically. If a tick stores a statevector under
        `arrays["psi"]`, it is promoted to the first-class `psi` trajectory.
        """
        items = list(frames)
        if not items:
            raise ValueError(
                "at least one QuantumStateFrame is required"
            )

        t = np.asarray([frame.t for frame in items], dtype=float)
        rho = np.stack(
            [
                np.asarray(frame.rho, dtype=complex)
                for frame in items
            ]
        )

        psi = None
        if all("psi" in frame.arrays for frame in items):
            psi = np.stack(
                [
                    np.asarray(frame.arrays["psi"], dtype=complex)
                    for frame in items
                ]
            )

        def common_stacked(
            source_name: str,
        ) -> dict[str, np.ndarray]:
            dicts = [
                getattr(frame, source_name)
                for frame in items
            ]
            common = set(dicts[0]).intersection(
                *(set(d) for d in dicts[1:])
            )
            out: dict[str, np.ndarray] = {}

            for key in common:
                if source_name == "arrays" and key == "psi":
                    continue
                try:
                    values = [
                        np.asarray(d[key]) for d in dicts
                    ]
                    shape = values[0].shape
                    if all(
                        value.shape == shape
                        for value in values
                    ):
                        out[key] = np.stack(values)
                except (TypeError, ValueError):
                    continue

            return out

        observables = common_stacked("observables")
        arrays = common_stacked("arrays")
        for key, value in arrays.items():
            observables.setdefault(key, value)

        metadata = {
            "source": "QuantumStateFrame",
            "samples": len(items),
            "source_names": sorted(
                {
                    frame.source_name
                    for frame in items
                    if frame.source_name
                }
            ),
        }

        return cls(
            t=t,
            psi=psi,
            rho=rho,
            observables=observables,
            metadata=metadata,
        )


# QuantumFrame is the quantum-oriented name for the same backend-independent
# trajectory container. Classical/acoustic engines can use PhysicsFrame with
# psi/rho left unset.
QuantumFrame = PhysicsFrame


class QuantumFrameAccumulator:
    """Collect live state ticks into a fixed-size trajectory block.

    The instance is callable so it can be passed directly to
    `StateBus.subscribe(accumulator)`.
    """

    def __init__(
        self, samples: int = DEFAULT_FRAME_SAMPLES
    ) -> None:
        if samples < 1:
            raise ValueError("samples must be >= 1")
        self.samples = int(samples)
        self._frames: list[QuantumStateFrame] = []

    def __call__(self, frame: QuantumStateFrame) -> None:
        self.append(frame)

    def append(self, frame: QuantumStateFrame) -> None:
        self._frames.append(frame)
        if len(self._frames) > self.samples:
            del self._frames[
                0 : len(self._frames) - self.samples
            ]

    @property
    def ready(self) -> bool:
        return len(self._frames) == self.samples

    @property
    def count(self) -> int:
        return len(self._frames)

    def clear(self) -> None:
        self._frames.clear()

    def to_physics_frame(
        self, *, require_full: bool = True
    ) -> PhysicsFrame:
        if require_full and not self.ready:
            raise ValueError(
                f"frame is not full: "
                f"{self.count}/{self.samples} samples"
            )
        if not self._frames:
            raise ValueError("accumulator is empty")
        return PhysicsFrame.from_state_frames(
            self._frames
        )
