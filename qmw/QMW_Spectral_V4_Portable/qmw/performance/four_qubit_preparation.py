"""Validated live preparation authority for the integrated four-qubit world."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from threading import RLock, Thread

import numpy as np


FOUR_QUBIT_PREPARATION_CONTROL_PORT = 17878
CONTROL_ROOT = "/qmw/4_4/preparation/control"
APPLY_ADDRESS = f"{CONTROL_ROOT}/apply"
PREPARATION_MODES = ("localized", "coherent", "squeezed", "thermal", "vacuum")


@dataclass(frozen=True)
class FourQubitPreparationState:
    """One requested and subsequently acknowledged source preparation."""

    mode: str = "coherent"
    localized_index: int = 0
    coherent_theta: float = 0.95
    coherent_phase: float = 0.55
    squeeze_magnitude: float = 0.62
    squeeze_phase: float = math.pi / 2.0
    temperature: float = 0.8
    revision: int = 0

    def validated(self) -> "FourQubitPreparationState":
        mode = str(self.mode).strip().lower()
        values = (
            self.coherent_theta, self.coherent_phase, self.squeeze_magnitude,
            self.squeeze_phase, self.temperature,
        )
        if mode not in PREPARATION_MODES:
            raise ValueError(f"mode must be one of {PREPARATION_MODES}.")
        if int(self.localized_index) != self.localized_index or not 0 <= int(self.localized_index) < 16:
            raise ValueError("localized index must be an integer in [0, 15].")
        if not np.isfinite(values).all():
            raise ValueError("preparation parameters must be finite.")
        if not 0.0 <= float(self.coherent_theta) <= math.pi:
            raise ValueError("coherent theta must lie in [0, pi].")
        if not -math.pi <= float(self.coherent_phase) <= math.pi:
            raise ValueError("coherent phase must lie in [-pi, pi].")
        if not 0.0 <= float(self.squeeze_magnitude) <= math.pi / 2.0:
            raise ValueError("squeeze magnitude must lie in [0, pi/2].")
        if not -math.pi <= float(self.squeeze_phase) <= math.pi:
            raise ValueError("squeeze phase must lie in [-pi, pi].")
        if not 0.01 <= float(self.temperature) <= 10.0:
            raise ValueError("temperature must lie in [0.01, 10].")
        return replace(
            self, mode=mode, localized_index=int(self.localized_index),
            coherent_theta=float(self.coherent_theta),
            coherent_phase=float(self.coherent_phase),
            squeeze_magnitude=float(self.squeeze_magnitude),
            squeeze_phase=float(self.squeeze_phase),
            temperature=float(self.temperature), revision=int(self.revision),
        )


class FourQubitPreparationControl:
    """Thread-safe owner; changes take effect only through explicit apply."""

    def __init__(self, initial: FourQubitPreparationState | None = None) -> None:
        self._state = (initial or FourQubitPreparationState()).validated()
        self._lock = RLock()

    def snapshot(self) -> FourQubitPreparationState:
        with self._lock:
            return self._state

    def apply(self, *values: object) -> FourQubitPreparationState:
        if len(values) != 7:
            raise ValueError("preparation apply requires mode plus six parameters.")
        with self._lock:
            candidate = FourQubitPreparationState(
                mode=str(values[0]), localized_index=int(values[1]),
                coherent_theta=float(values[2]), coherent_phase=float(values[3]),
                squeeze_magnitude=float(values[4]), squeeze_phase=float(values[5]),
                temperature=float(values[6]), revision=self._state.revision + 1,
            ).validated()
            self._state = candidate
            return candidate


class FourQubitPreparationOSCControl:
    def __init__(self, authority: FourQubitPreparationControl, *, host: str = "127.0.0.1", port: int = FOUR_QUBIT_PREPARATION_CONTROL_PORT) -> None:
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer

        self.authority = authority
        dispatcher = Dispatcher()
        dispatcher.map(APPLY_ADDRESS, self._apply)
        self.server = ThreadingOSCUDPServer((host, int(port)), dispatcher)
        self.server.daemon_threads = True
        self._thread: Thread | None = None

    @property
    def port(self) -> int:
        return int(self.server.server_address[1])

    def _apply(self, address: str, *values: object) -> None:
        try:
            state = self.authority.apply(*values)
            print(
                f"four-qubit preparation {address}: mode={state.mode} "
                f"index={state.localized_index} revision={state.revision}",
                flush=True,
            )
        except (TypeError, ValueError) as error:
            print(f"rejected four-qubit preparation {address}: {error}", flush=True)

    def start(self) -> "FourQubitPreparationOSCControl":
        if self._thread is not None:
            raise RuntimeError("four-qubit preparation server is already running.")
        self._thread = Thread(target=self.server.serve_forever, name="qmw-four-qubit-preparation", daemon=True)
        self._thread.start()
        return self

    def close(self) -> None:
        if self._thread is not None:
            self.server.shutdown()
            self._thread.join(timeout=2.0)
            self._thread = None
        self.server.server_close()


def prepare_four_qubit_density(
    state: FourQubitPreparationState, hamiltonian: np.ndarray,
) -> np.ndarray:
    """Build rho without confusing finite spin/GHZ analogues with a CV QHO."""
    state = state.validated()
    if state.mode == "localized":
        psi = np.zeros(16, dtype=np.complex128)
        psi[state.localized_index] = 1.0
        return np.outer(psi, psi.conj())
    if state.mode == "coherent":
        qubit = np.array([
            math.cos(state.coherent_theta / 2.0),
            np.exp(1j * state.coherent_phase) * math.sin(state.coherent_theta / 2.0),
        ], dtype=np.complex128)
        psi = qubit
        for _ in range(3):
            psi = np.kron(psi, qubit)
        return np.outer(psi, psi.conj())
    if state.mode == "squeezed":
        psi = np.zeros(16, dtype=np.complex128)
        psi[0] = math.cos(state.squeeze_magnitude)
        psi[15] = np.exp(1j * state.squeeze_phase) * math.sin(state.squeeze_magnitude)
        return np.outer(psi, psi.conj())
    energies, vectors = np.linalg.eigh(np.asarray(hamiltonian, dtype=np.complex128))
    if state.mode == "vacuum":
        psi = vectors[:, int(np.argmin(energies))]
        return np.outer(psi, psi.conj())
    weights = np.exp(-(energies - float(np.min(energies))) / state.temperature)
    weights /= np.sum(weights)
    return (vectors * weights) @ vectors.conj().T


__all__ = [
    "APPLY_ADDRESS", "CONTROL_ROOT", "FOUR_QUBIT_PREPARATION_CONTROL_PORT",
    "FourQubitPreparationControl", "FourQubitPreparationOSCControl",
    "FourQubitPreparationState", "PREPARATION_MODES", "prepare_four_qubit_density",
]
