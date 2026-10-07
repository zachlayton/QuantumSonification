"""Live, revision-aware runtime controls for the Von Neumann Flow I source.

This is the authoritative two-qubit reference source only.  It does not
reinterpret the four-qubit Hilbert world or the separate QHO sidecar.  A
Hamiltonian change is scheduled as a generator intervention at the current
model-time boundary; an evolution-rate change only changes model-time per wall
second; Bures controls configure a read-only timing observer.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from threading import RLock, Thread

from .control import HamiltonianControl
from .dynamics import QuantumFrame, von_neumann_flow_i_hamiltonian
from .engine import QuantumFrameEngine
from .temporal import BuresFrameClock


VON_NEUMANN_FLOW_I_CONTROL_PORT = 17880
CONTROL_ROOT = "/qmw/quantum/v1/control"
HAMILTONIAN_ADDRESS = f"{CONTROL_ROOT}/von_neumann_flow_i/hamiltonian"
EVOLUTION_RATE_ADDRESS = f"{CONTROL_ROOT}/von_neumann_flow_i/evolution_rate"
BURES_DISTANCE_ADDRESS = f"{CONTROL_ROOT}/von_neumann_flow_i/bures_distance"
BURES_CLOCK_SCALE_ADDRESS = f"{CONTROL_ROOT}/von_neumann_flow_i/bures_clock_scale"


@dataclass(frozen=True)
class VonNeumannFlowIRuntimeState:
    """Requested source and observer configuration, separate by construction."""

    omega_1: float = 1.17
    omega_2: float = 0.73
    coupling: float = 0.61
    evolution_rate: float = 1.0
    bures_distance: float = 0.025
    bures_clock_scale: float = 1.0


class VonNeumannFlowIRuntime:
    """Serialize live controls and frame steps at sealed-frame boundaries."""

    def __init__(self, engine: QuantumFrameEngine, temporal_clock: BuresFrameClock) -> None:
        self.engine = engine
        self.temporal_clock = temporal_clock
        self._lock = RLock()
        terms = {term.label: float(term.coefficient.real) for term in engine.hamiltonian.pauli_terms}
        self._state = VonNeumannFlowIRuntimeState(
            omega_1=terms.get("ZI", 0.0), omega_2=terms.get("IZ", 0.0),
            coupling=terms.get("XX", 0.0),
            bures_distance=temporal_clock.distance_per_pulse,
            bures_clock_scale=temporal_clock.clock_scale,
        )

    @staticmethod
    def _coefficient(value: object, name: str) -> float:
        result = float(value)
        if not math.isfinite(result) or not -20.0 <= result <= 20.0:
            raise ValueError(f"{name} must be finite and lie in [-20, 20].")
        return result

    @staticmethod
    def _evolution_rate(value: object) -> float:
        result = float(value)
        if not math.isfinite(result) or not 0.05 <= result <= 8.0:
            raise ValueError("evolution rate must lie in [0.05, 8].")
        return result

    def snapshot(self) -> VonNeumannFlowIRuntimeState:
        with self._lock:
            return self._state

    def set_hamiltonian(self, omega_1: object, omega_2: object, coupling: object) -> VonNeumannFlowIRuntimeState:
        """Schedule the requested VNF-I generator after the current sealed frame."""

        with self._lock:
            values = (
                self._coefficient(omega_1, "omega_1"), self._coefficient(omega_2, "omega_2"),
                self._coefficient(coupling, "coupling"),
            )
            generator = von_neumann_flow_i_hamiltonian(*values, hbar=self.engine.hamiltonian.hbar)
            self.engine.schedule(HamiltonianControl(
                self.engine.state.time, generator,
                label="von_neumann_flow_i_hamiltonian_update",
            ))
            self._state = VonNeumannFlowIRuntimeState(
                omega_1=values[0], omega_2=values[1], coupling=values[2],
                evolution_rate=self._state.evolution_rate,
                bures_distance=self._state.bures_distance,
                bures_clock_scale=self._state.bures_clock_scale,
            )
            return self._state

    def set_evolution_rate(self, value: object) -> VonNeumannFlowIRuntimeState:
        with self._lock:
            self._state = VonNeumannFlowIRuntimeState(
                omega_1=self._state.omega_1, omega_2=self._state.omega_2, coupling=self._state.coupling,
                evolution_rate=self._evolution_rate(value), bures_distance=self._state.bures_distance,
                bures_clock_scale=self._state.bures_clock_scale,
            )
            return self._state

    def set_bures_distance(self, value: object) -> VonNeumannFlowIRuntimeState:
        with self._lock:
            self.temporal_clock.configure(distance_per_pulse=float(value))
            self._state = VonNeumannFlowIRuntimeState(
                omega_1=self._state.omega_1, omega_2=self._state.omega_2, coupling=self._state.coupling,
                evolution_rate=self._state.evolution_rate,
                bures_distance=self.temporal_clock.distance_per_pulse,
                bures_clock_scale=self._state.bures_clock_scale,
            )
            return self._state

    def set_bures_clock_scale(self, value: object) -> VonNeumannFlowIRuntimeState:
        with self._lock:
            self.temporal_clock.configure(clock_scale=float(value))
            self._state = VonNeumannFlowIRuntimeState(
                omega_1=self._state.omega_1, omega_2=self._state.omega_2, coupling=self._state.coupling,
                evolution_rate=self._state.evolution_rate, bures_distance=self._state.bures_distance,
                bures_clock_scale=self.temporal_clock.clock_scale,
            )
            return self._state

    def step(self, wall_duration: float, *, publish: bool = True) -> QuantumFrame:
        """Advance model time at the declared rate, then seal/publish one frame."""

        elapsed = float(wall_duration)
        if not math.isfinite(elapsed) or elapsed <= 0.0:
            raise ValueError("wall_duration must be finite and positive.")
        with self._lock:
            return self.engine.step(elapsed * self._state.evolution_rate, publish=publish)


class VonNeumannFlowIOSCControl:
    """Small validated OSC surface for the VNF-I generator and metric observer."""

    def __init__(
        self, runtime: VonNeumannFlowIRuntime, *, host: str = "127.0.0.1",
        port: int = VON_NEUMANN_FLOW_I_CONTROL_PORT,
    ) -> None:
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer

        self.runtime = runtime
        dispatcher = Dispatcher()
        dispatcher.map(HAMILTONIAN_ADDRESS, self._hamiltonian)
        dispatcher.map(EVOLUTION_RATE_ADDRESS, self._evolution_rate)
        dispatcher.map(BURES_DISTANCE_ADDRESS, self._bures_distance)
        dispatcher.map(BURES_CLOCK_SCALE_ADDRESS, self._bures_clock_scale)
        self.server = ThreadingOSCUDPServer((host, int(port)), dispatcher)
        self.server.daemon_threads = True
        self._thread: Thread | None = None

    @property
    def port(self) -> int:
        return int(self.server.server_address[1])

    def _apply(self, address: str, action, *values: object) -> None:
        try:
            state = action(*values)
            print(f"VNF I control {address}: {state}", flush=True)
        except (TypeError, ValueError) as error:
            print(f"rejected VNF I control {address}: {error}", flush=True)

    def _hamiltonian(self, address: str, *values: object) -> None:
        self._apply(address, self.runtime.set_hamiltonian, *values)

    def _evolution_rate(self, address: str, *values: object) -> None:
        self._apply(address, self.runtime.set_evolution_rate, *values)

    def _bures_distance(self, address: str, *values: object) -> None:
        self._apply(address, self.runtime.set_bures_distance, *values)

    def _bures_clock_scale(self, address: str, *values: object) -> None:
        self._apply(address, self.runtime.set_bures_clock_scale, *values)

    def start(self) -> "VonNeumannFlowIOSCControl":
        if self._thread is not None:
            raise RuntimeError("VNF I OSC control server is already running.")
        self._thread = Thread(target=self.server.serve_forever, name="qmw-von-neumann-flow-i", daemon=True)
        self._thread.start()
        return self

    def close(self) -> None:
        if self._thread is not None:
            self.server.shutdown()
            self._thread.join(timeout=2.0)
            self._thread = None
        self.server.server_close()


__all__ = [
    "BURES_CLOCK_SCALE_ADDRESS", "BURES_DISTANCE_ADDRESS", "CONTROL_ROOT",
    "EVOLUTION_RATE_ADDRESS", "HAMILTONIAN_ADDRESS", "VON_NEUMANN_FLOW_I_CONTROL_PORT",
    "VonNeumannFlowIOSCControl", "VonNeumannFlowIRuntime", "VonNeumannFlowIRuntimeState",
]
