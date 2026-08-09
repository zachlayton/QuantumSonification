"""OSC control and paired Full4Q publication for Basis Laboratory v3."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pythonosc import dispatcher, osc_server

from full4q_tomography_v1.osc_service import TomographyOSCPublisher
from qmw_pauli_basis_laboratory_v2.basis_operator import BasisOperator
from qmw_pauli_basis_laboratory_v2.bases import (
    HadamardBasis,
    HamiltonianEigenbasis,
    IdentityBasis,
    QFTBasis,
    transverse_ising_hamiltonian,
)
from qmw_pauli_basis_laboratory_v2.laboratory import (
    BasisLaboratoryResult,
    run_basis_laboratory,
    save_laboratory_result,
)


CONTROL_ROOT = "/qmw/basis"
REVISION_MODULUS = 2_000_000_000


def basis_from_name(name: str, *, n_qubits: int = 4) -> BasisOperator:
    """Construct one of the v3 live-menu operators without changing v2."""
    normalized = str(name).strip().lower()
    if normalized in {"identity", "computational", "none"}:
        return IdentityBasis()
    if normalized in {"hadamard", "h"}:
        return HadamardBasis()
    if normalized == "qft":
        return QFTBasis()
    if normalized in {"inverse_qft", "iqft"}:
        return QFTBasis(inverse=True)
    if normalized in {"hamiltonian", "hamiltonian_eigenbasis", "energy"}:
        return HamiltonianEigenbasis(
            transverse_ising_hamiltonian(n_qubits)
        )
    raise ValueError(
        f"unknown basis {name!r}; choose identity, hadamard, qft, "
        "inverse_qft, or hamiltonian"
    )


@dataclass(frozen=True)
class BasisServiceConfig:
    preset: str = "ghz"
    basis: str = "qft"
    shots: int = 256
    seed: int = 23


class BasisLaboratoryOSCPublisher:
    """Publish both representations through the unchanged Full4Q contract."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7436,
        packet_delay_ms: float = 2.0,
    ) -> None:
        self.tomography = TomographyOSCPublisher(
            host,
            port,
            packet_delay_ms,
        )

    def status(self, *payload: Any) -> None:
        self.tomography.status(*payload)

    def error(self, message: str) -> None:
        self.tomography.error(message)

    def publish(
        self,
        result: BasisLaboratoryResult,
        revision: int,
    ) -> tuple[int, int]:
        computational_revision = int(revision) % REVISION_MODULUS
        experimental_revision = (
            computational_revision + 1
        ) % REVISION_MODULUS
        self.tomography.publish(
            result.computational_basis,
            computational_revision,
        )
        self.tomography.publish(
            result.experimental_basis,
            experimental_revision,
        )
        return computational_revision, experimental_revision


class BasisLaboratoryOSCService:
    """Receive v3 run requests and emit two complete tomography revisions."""

    def __init__(
        self,
        *,
        control_host: str = "127.0.0.1",
        control_port: int = 7435,
        output_host: str = "127.0.0.1",
        output_port: int = 7436,
        packet_delay_ms: float = 2.0,
        config: BasisServiceConfig | None = None,
        save_directory: Path | None = None,
    ) -> None:
        self.control_host = control_host
        self.control_port = control_port
        self.publisher = BasisLaboratoryOSCPublisher(
            output_host,
            output_port,
            packet_delay_ms,
        )
        self.config = config or BasisServiceConfig()
        self.save_directory = save_directory
        self.last_result: BasisLaboratoryResult | None = None
        self._run_lock = threading.Lock()
        self._revision = int(time.time() * 1000) % REVISION_MODULUS
        self._dispatcher = dispatcher.Dispatcher()
        self._dispatcher.map(f"{CONTROL_ROOT}/run", self._handle_run)
        self._dispatcher.map(f"{CONTROL_ROOT}/rerun", self._handle_rerun)
        self._dispatcher.map(f"{CONTROL_ROOT}/ping", self._handle_ping)
        self._server = osc_server.ThreadingOSCUDPServer(
            (control_host, control_port),
            self._dispatcher,
        )

    def _next_revision(self) -> int:
        self._revision = (self._revision + 2) % REVISION_MODULUS
        return self._revision

    def _handle_run(
        self,
        _address: str,
        preset: str = "ghz",
        basis: str = "qft",
        shots: int = 256,
        seed: int = 23,
    ) -> None:
        self.request_run(
            BasisServiceConfig(
                preset=str(preset),
                basis=str(basis),
                shots=int(shots),
                seed=int(seed),
            )
        )

    def _handle_rerun(self, _address: str, *_args: Any) -> None:
        self.request_run(self.config)

    def _handle_ping(self, _address: str, *_args: Any) -> None:
        self.publisher.status(
            "basis_v3_ready",
            self.config.preset,
            self.config.basis,
            self.config.shots,
            self.config.seed,
        )

    def request_run(self, config: BasisServiceConfig) -> bool:
        if config.shots <= 0:
            self.publisher.error("basis shots must be positive")
            return False
        if self._run_lock.locked():
            self.publisher.status("basis_v3_busy")
            return False
        self.config = config
        worker = threading.Thread(
            target=self._run_and_publish,
            args=(config,),
            daemon=True,
            name="qmw-basis-laboratory-v3-run",
        )
        worker.start()
        return True

    def _run_and_publish(self, config: BasisServiceConfig) -> None:
        with self._run_lock:
            try:
                basis = basis_from_name(config.basis)
                self.publisher.status(
                    "basis_v3_running",
                    config.preset,
                    basis.name,
                    config.shots,
                    config.seed,
                )
                result = run_basis_laboratory(
                    basis,
                    preset=config.preset,
                    shots=config.shots,
                    seed=config.seed,
                )
                revision = self._next_revision()
                revisions = self.publisher.publish(result, revision)
                self.last_result = result
                if self.save_directory is not None:
                    stamp = time.strftime("%Y%m%d-%H%M%S")
                    destination = self.save_directory / (
                        f"{stamp}-{config.preset}-{basis.name}.json"
                    )
                    save_laboratory_result(result, destination)
                self.publisher.status(
                    "basis_v3_complete",
                    config.preset,
                    basis.name,
                    revisions[0],
                    revisions[1],
                )
            except Exception as exc:
                self.publisher.error(f"basis v3 run failed: {exc}")

    def serve_forever(self) -> None:
        self._server.serve_forever()

    def shutdown(self) -> None:
        self._server.shutdown()
        self._server.server_close()
