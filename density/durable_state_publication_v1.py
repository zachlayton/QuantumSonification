"""Atomic canonical-state publication and deterministic event replay.

The density engine remains the state owner.  This module only persists states
and transition descriptions supplied by that owner.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import time
from typing import Any, Dict, Iterator, Optional
import uuid

import numpy as np


class StatePublicationError(RuntimeError):
    pass


def _json_safe(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return {"real": value.real.tolist(), "imag": value.imag.tolist()}
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _json_safe(value),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def rho_sha256(rho: np.ndarray) -> str:
    state = np.ascontiguousarray(np.asarray(rho, dtype=np.complex128))
    return hashlib.sha256(state.view(np.uint8)).hexdigest()


def _validate_rho(rho: np.ndarray) -> np.ndarray:
    state = np.asarray(rho, dtype=np.complex128)
    if state.shape != (16, 16):
        raise ValueError("durable state v1 requires a 16x16 four-qubit rho")
    state = 0.5 * (state + state.conj().T)
    trace = float(np.trace(state).real)
    if trace <= 0.0:
        raise ValueError("rho must have positive trace")
    return np.ascontiguousarray(state / trace)


@dataclass(frozen=True)
class StatePublicationConfig:
    directory: Path | str
    write_revision_packets: bool = True
    checkpoint_interval_events: int = 0
    fsync: bool = True
    session_id: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "directory", Path(self.directory).expanduser())
        if self.checkpoint_interval_events < 0:
            raise ValueError("checkpoint_interval_events must be non-negative")


@dataclass(frozen=True)
class PublishedState:
    revision: int
    rho_sha256: str
    current_path: Path
    revision_path: Optional[Path]
    manifest_path: Path


@dataclass(frozen=True)
class ReplayFrame:
    sequence: int
    revision: int
    event_type: str
    logical_time: float
    rho: np.ndarray
    record: Dict[str, Any]


class DurableStatePublisher:
    """Publish canonical state and transitions with crash-safe replacement."""

    SCHEMA = "qmw.durable_state.v1"

    def __init__(self, config: StatePublicationConfig):
        self.config = config
        self.root = Path(config.directory)
        self.session_id = config.session_id or (
            time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            + "-"
            + uuid.uuid4().hex[:12]
        )
        self.states_dir = self.root / "states" / self.session_id
        self.checkpoints_dir = self.root / "checkpoints" / self.session_id
        self.root.mkdir(parents=True, exist_ok=True)
        self.states_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.current_path = self.root / "current_state.npz"
        self.manifest_path = self.root / "current_state.json"
        self.ledger_path = self.root / "events.jsonl"
        self._lock = threading.RLock()
        self._event_sequence = self._recover_last_sequence()

    def _recover_last_sequence(self) -> int:
        if not self.ledger_path.exists():
            return 0
        last = 0
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    last = max(last, int(record["sequence"]))
                except Exception as exc:
                    raise StatePublicationError(
                        f"invalid event ledger line {line_number}: {exc}"
                    ) from exc
        return last

    def _fsync_directory(self, directory: Path) -> None:
        if not self.config.fsync:
            return
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _atomic_npz(self, destination: Path, **payload: Any) -> None:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        try:
            with os.fdopen(descriptor, "wb") as handle:
                np.savez_compressed(handle, **payload)
                handle.flush()
                if self.config.fsync:
                    os.fsync(handle.fileno())
            os.replace(temporary_name, destination)
            self._fsync_directory(destination.parent)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise

    def _atomic_json(self, destination: Path, payload: Dict[str, Any]) -> None:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(_canonical_json(payload) + "\n")
                handle.flush()
                if self.config.fsync:
                    os.fsync(handle.fileno())
            os.replace(temporary_name, destination)
            self._fsync_directory(destination.parent)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise

    def publish_state(
        self,
        rho: np.ndarray,
        *,
        revision: int,
        logical_time: float,
        event_id: int = 0,
        event_type: str = "state",
        configuration_revision: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PublishedState:
        state = _validate_rho(rho)
        revision = int(revision)
        if revision < 0:
            raise ValueError("revision must be non-negative")
        digest = rho_sha256(state)
        metadata_json = _canonical_json(metadata or {})
        payload = {
            "schema": np.asarray(self.SCHEMA),
            "session_id": np.asarray(self.session_id),
            "rho": state,
            "revision": np.asarray(revision, dtype=np.int64),
            "configuration_revision": np.asarray(
                int(configuration_revision), dtype=np.int64
            ),
            "logical_time": np.asarray(float(logical_time), dtype=np.float64),
            "event_id": np.asarray(int(event_id), dtype=np.int64),
            "event_type": np.asarray(str(event_type)),
            "rho_sha256": np.asarray(digest),
            "metadata_json": np.asarray(metadata_json),
        }

        with self._lock:
            revision_path: Optional[Path] = None
            if self.config.write_revision_packets:
                revision_path = self.states_dir / f"state_{revision:012d}.npz"
                if revision_path.exists():
                    with np.load(revision_path, allow_pickle=False) as existing:
                        existing_digest = str(existing["rho_sha256"].item())
                    if existing_digest != digest:
                        raise StatePublicationError(
                            f"revision {revision} already exists with different rho"
                        )
                else:
                    self._atomic_npz(revision_path, **payload)

            self._atomic_npz(self.current_path, **payload)
            manifest = {
                "schema": self.SCHEMA,
                "session_id": self.session_id,
                "revision": revision,
                "configuration_revision": int(configuration_revision),
                "logical_time": float(logical_time),
                "event_id": int(event_id),
                "event_type": str(event_type),
                "rho_sha256": digest,
                "state_packet": (
                    str(revision_path.relative_to(self.root))
                    if revision_path is not None
                    else self.current_path.name
                ),
                "metadata": _json_safe(metadata or {}),
            }
            self._atomic_json(self.manifest_path, manifest)
            return PublishedState(
                revision=revision,
                rho_sha256=digest,
                current_path=self.current_path,
                revision_path=revision_path,
                manifest_path=self.manifest_path,
            )

    def _write_checkpoint(
        self,
        sequence: int,
        event_type: str,
        rho_before: np.ndarray,
        rho_after: np.ndarray,
        delta_rho: Optional[np.ndarray],
    ) -> Path:
        before = _validate_rho(rho_before)
        after = _validate_rho(rho_after)
        delta = (
            np.asarray(delta_rho, dtype=np.complex128)
            if delta_rho is not None
            else after - before
        )
        destination = (
            self.checkpoints_dir
            / f"event_{sequence:012d}_{str(event_type)}.npz"
        )
        self._atomic_npz(
            destination,
            schema=np.asarray(self.SCHEMA),
            session_id=np.asarray(self.session_id),
            sequence=np.asarray(sequence, dtype=np.int64),
            event_type=np.asarray(str(event_type)),
            rho_before=before,
            rho_after=after,
            delta_rho=delta,
        )
        return destination

    def append_transition(
        self,
        *,
        event_type: str,
        rho_after: np.ndarray,
        revision: int,
        logical_time: float,
        event_id: int,
        configuration_revision: int,
        metadata: Optional[Dict[str, Any]] = None,
        rho_before: Optional[np.ndarray] = None,
        delta_rho: Optional[np.ndarray] = None,
        force_checkpoint: bool = False,
    ) -> Dict[str, Any]:
        with self._lock:
            sequence = self._event_sequence + 1
            published = self.publish_state(
                rho_after,
                revision=revision,
                logical_time=logical_time,
                event_id=event_id,
                event_type=event_type,
                configuration_revision=configuration_revision,
                metadata=metadata,
            )
            checkpoint_path: Optional[Path] = None
            interval = self.config.checkpoint_interval_events
            checkpoint_due = force_checkpoint or (
                interval > 0 and sequence % interval == 0
            )
            if checkpoint_due and rho_before is not None:
                checkpoint_path = self._write_checkpoint(
                    sequence,
                    event_type,
                    rho_before,
                    rho_after,
                    delta_rho,
                )

            record: Dict[str, Any] = {
                "schema": self.SCHEMA,
                "session_id": self.session_id,
                "sequence": sequence,
                "event_id": int(event_id),
                "event_type": str(event_type),
                "logical_time": float(logical_time),
                "revision": int(revision),
                "configuration_revision": int(configuration_revision),
                "rho_sha256": published.rho_sha256,
                "state_packet": (
                    str(published.revision_path.relative_to(self.root))
                    if published.revision_path is not None
                    else published.current_path.name
                ),
                "checkpoint": (
                    str(checkpoint_path.relative_to(self.root))
                    if checkpoint_path is not None
                    else None
                ),
                "metadata": _json_safe(metadata or {}),
            }
            record_digest = hashlib.sha256(
                _canonical_json(record).encode("utf-8")
            ).hexdigest()
            record["record_sha256"] = record_digest
            line = (_canonical_json(record) + "\n").encode("utf-8")
            descriptor = os.open(
                self.ledger_path,
                os.O_APPEND | os.O_CREAT | os.O_WRONLY,
                0o644,
            )
            try:
                written = os.write(descriptor, line)
                if written != len(line):
                    raise StatePublicationError("short write to event ledger")
                if self.config.fsync:
                    os.fsync(descriptor)
            finally:
                os.close(descriptor)
            self._fsync_directory(self.root)
            self._event_sequence = sequence
            return record


class DurableStateReplay:
    """Read, verify, and exactly reconstruct a persisted state history."""

    def __init__(self, directory: Path | str, session_id: Optional[str] = None):
        self.root = Path(directory)
        self.ledger_path = self.root / "events.jsonl"
        self.session_id = session_id

    def events(self) -> Iterator[Dict[str, Any]]:
        previous_sequence = 0
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                sequence = int(record["sequence"])
                if sequence <= previous_sequence:
                    raise StatePublicationError(
                        f"non-monotonic ledger sequence at line {line_number}"
                    )
                previous_sequence = sequence
                expected_digest = record.pop("record_sha256")
                actual_digest = hashlib.sha256(
                    _canonical_json(record).encode("utf-8")
                ).hexdigest()
                record["record_sha256"] = expected_digest
                if actual_digest != expected_digest:
                    raise StatePublicationError(
                        f"event ledger hash mismatch at line {line_number}"
                    )
                if self.session_id is None or record["session_id"] == self.session_id:
                    yield record

    def load_state_packet(self, record: Dict[str, Any]) -> np.ndarray:
        path = self.root / str(record["state_packet"])
        with np.load(path, allow_pickle=False) as packet:
            rho = np.asarray(packet["rho"], dtype=np.complex128)
            revision = int(packet["revision"].item())
            digest = str(packet["rho_sha256"].item())
        if revision != int(record["revision"]):
            raise StatePublicationError("state packet revision mismatch")
        if digest != str(record["rho_sha256"]) or rho_sha256(rho) != digest:
            raise StatePublicationError("state packet rho hash mismatch")
        return rho

    def replay(self) -> Iterator[ReplayFrame]:
        for record in self.events():
            yield ReplayFrame(
                sequence=int(record["sequence"]),
                revision=int(record["revision"]),
                event_type=str(record["event_type"]),
                logical_time=float(record["logical_time"]),
                rho=self.load_state_packet(record),
                record=record,
            )

    def verify(self) -> int:
        count = 0
        for _frame in self.replay():
            count += 1
        return count

    def current_state(self) -> np.ndarray:
        path = self.root / "current_state.npz"
        with np.load(path, allow_pickle=False) as packet:
            rho = np.asarray(packet["rho"], dtype=np.complex128)
            digest = str(packet["rho_sha256"].item())
        if rho_sha256(rho) != digest:
            raise StatePublicationError("current state rho hash mismatch")
        return rho
