"""Read-only QMW metric adapter for the repository's authoritative rho owner."""

from __future__ import annotations

from dataclasses import dataclass
import threading
import time as wall_time
from typing import Any

import numpy as np
from numpy.typing import NDArray

ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class RevisionedDensitySnapshot:
    """One complete external q0-LSB density frame; no inferred Hamiltonian."""

    rho: ComplexArray
    time: float
    revision: int
    event_type: str = "external_state_frame"
    source: str = "/qmw/state/rho/{real,imag}"
    basis_order: str = "q0-LSB; |q3 q2 q1 q0>; no bit reversal"

    def __post_init__(self) -> None:
        rho = np.asarray(self.rho, dtype=np.complex128).copy()
        if rho.shape != (16, 16):
            raise ValueError("authoritative QMW density input requires 16x16 rho")
        if not np.all(np.isfinite(rho)):
            raise ValueError("authoritative rho contains non-finite values")
        if not np.allclose(rho, rho.conj().T, atol=1e-8):
            raise ValueError("authoritative rho must be Hermitian")
        if not np.isclose(np.trace(rho), 1.0, atol=1e-8):
            raise ValueError("authoritative rho must have unit trace")
        if float(np.linalg.eigvalsh(rho).min()) < -1e-8:
            raise ValueError("authoritative rho must be positive semidefinite")
        if self.revision < 0 or not np.isfinite(self.time):
            raise ValueError("authoritative revision/time are invalid")
        rho.setflags(write=False)
        object.__setattr__(self, "rho", rho)


class RevisionedDensityPairReceiver:
    """Atomically pair revisioned OSC real/imag packets from the QMW owner."""

    def __init__(self, *, on_commit: Any = None):
        self.on_commit = on_commit
        self._parts: dict[int, dict[str, NDArray[np.float64]]] = {}
        self._revision = -1
        self._snapshot: RevisionedDensitySnapshot | None = None
        self._lock = threading.RLock()

    @property
    def snapshot(self) -> RevisionedDensitySnapshot | None:
        with self._lock:
            return self._snapshot

    def receive_real(self, _address: str, *arguments: object) -> None:
        self._receive("real", arguments)

    def receive_imag(self, _address: str, *arguments: object) -> None:
        self._receive("imag", arguments)

    def _receive(self, component: str, arguments: tuple[object, ...]) -> None:
        if len(arguments) != 257:
            raise ValueError(f"{component} packet requires revision plus 256 values")
        revision = int(arguments[0])
        values = np.asarray(arguments[1:], dtype=np.float64)
        if not np.all(np.isfinite(values)):
            raise ValueError(f"{component} packet contains non-finite values")
        committed: RevisionedDensitySnapshot | None = None
        with self._lock:
            if revision <= self._revision:
                return
            parts = self._parts.setdefault(revision, {})
            parts[component] = values
            if "real" in parts and "imag" in parts:
                rho = (parts["real"] + 1j * parts["imag"]).reshape(16, 16)
                committed = RevisionedDensitySnapshot(
                    rho=rho,
                    time=wall_time.monotonic(),
                    revision=revision,
                )
                self._snapshot = committed
                self._revision = revision
                self._parts = {key: value for key, value in self._parts.items() if key > revision}
        if committed is not None and self.on_commit is not None:
            self.on_commit(committed)


class _SilentOSCClient:
    """Explicitly suppress telemetry during offline acceptance renders."""

    def send_message(self, _address: str, _value: object) -> None:
        return None


@dataclass(frozen=True)
class AuthoritativeStateSnapshot:
    rho: ComplexArray
    hamiltonian: ComplexArray
    time: float
    revision: int
    event_type: str
    source: str = "density.density_matrix_engine_4q.DensityMatrixEngine"
    basis_order: str = "q0-LSB; rho and H bit-reversed from density-engine q0-MSB"

    def __post_init__(self) -> None:
        rho = np.asarray(self.rho, dtype=np.complex128).copy()
        hamiltonian = np.asarray(self.hamiltonian, dtype=np.complex128).copy()
        if rho.shape != (16, 16) or hamiltonian.shape != (16, 16):
            raise ValueError("authoritative QMW metric input requires 16x16 rho and H")
        if not np.allclose(rho, rho.conj().T, atol=1e-9):
            raise ValueError("authoritative rho must be Hermitian")
        if not np.isclose(np.trace(rho), 1.0, atol=1e-9):
            raise ValueError("authoritative rho must have unit trace")
        if self.revision < 0 or not np.isfinite(self.time):
            raise ValueError("authoritative revision/time are invalid")
        rho.setflags(write=False)
        hamiltonian.setflags(write=False)
        object.__setattr__(self, "rho", rho)
        object.__setattr__(self, "hamiltonian", hamiltonian)


class DensityMatrixEngineMetricAdapter:
    """Observe one existing owner; never install or evolve a second rho."""

    def __init__(self, owner: Any, *, silence_telemetry: bool = False):
        required = ("rho", "hamiltonian", "step", "perform_measurement")
        if any(not hasattr(owner, name) for name in required):
            raise TypeError("owner does not satisfy the DensityMatrixEngine contract")
        self.owner = owner
        if silence_telemetry:
            bridge = getattr(owner, "qmw_bridge", None)
            if bridge is not None:
                bridge.client = _SilentOSCClient()

    @classmethod
    def create_offline(cls, *, measurement_seed: int = 29) -> "DensityMatrixEngineMetricAdapter":
        """Create the canonical owner without OSC control or telemetry side effects."""
        from density.density_matrix_engine_4q import DensityMatrixEngine

        owner = DensityMatrixEngine(
            enable_circuit_bridge_control=False,
            osc_telemetry_hz=0,
            measurement_seed=measurement_seed,
        )
        owner.rng = np.random.default_rng(918273)
        return cls(owner, silence_telemetry=True)

    def snapshot(self) -> AuthoritativeStateSnapshot:
        from density.density_state_injection import bit_reversal_permutation

        permutation = bit_reversal_permutation(4)
        native_rho = np.asarray(self.owner.rho, dtype=np.complex128)
        native_hamiltonian = np.asarray(self.owner.hamiltonian(), dtype=np.complex128)
        return AuthoritativeStateSnapshot(
            rho=native_rho[np.ix_(permutation, permutation)],
            hamiltonian=native_hamiltonian[np.ix_(permutation, permutation)],
            time=float(self.owner.logical_time),
            revision=int(self.owner.state_revision),
            event_type=str(self.owner.last_event_type),
        )

    def advance(self, dt: float) -> AuthoritativeStateSnapshot:
        if not np.isfinite(dt) or dt <= 0.0:
            raise ValueError("authoritative step dt must be positive")
        self.owner.step(float(dt))
        return self.snapshot()

    def measure(
        self, *, basis: str = "X", request_id: int = 1
    ) -> tuple[AuthoritativeStateSnapshot, Any]:
        event = self.owner.perform_measurement(
            basis=basis, mode="collapse", request_id=request_id
        )
        return self.snapshot(), event
