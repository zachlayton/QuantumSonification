#!/usr/bin/env python3
"""Persistent orchestration for an evolving quantum-material surface spectrum."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field, replace
from enum import Enum, IntFlag, auto
from pathlib import Path
import argparse
import json
import threading
import time
from typing import Any, Callable, Mapping

import numpy as np
from scipy.optimize import linear_sum_assignment

from eigenfield_timing_layer_v1 import EigenfieldState
from geometry_acoustics_bridge_v2 import (
    AcousticBridgeConfig,
    GeometryAcousticsBridgeV2,
)
from quantum_eigenfield_engine_v1 import (
    QuantumEigenfieldConfig,
    QuantumEigenfieldEngine,
    demo_density_matrix,
    load_density_matrix,
)
from spectral_geometry_v1 import (
    MeshSpectralGeometry,
    SpectralGeometryConfig,
    SpectralGeometryResult,
    load_obj,
)
from surface_material_models_v1 import (
    MODEL_ORDER,
    SurfaceMaterialConfig,
    SurfaceModalPacket,
    create_surface_model,
    export_packet,
)


class DirtyDomain(IntFlag):
    NONE = 0
    GEOMETRY = auto()
    MATERIAL = auto()
    QUANTUM = auto()
    TIMING = auto()
    ACOUSTICS = auto()
    ALL = GEOMETRY | MATERIAL | QUANTUM | TIMING | ACOUSTICS


class LivingEventType(str, Enum):
    GEOMETRY = "geometry"
    MATERIAL = "material"
    QUANTUM = "quantum"
    MEASUREMENT = "measurement"
    RECALCULATE = "recalculate"


@dataclass(frozen=True)
class LivingOperatorEvent:
    type: LivingEventType
    payload: Mapping[str, Any] = field(default_factory=dict)
    reason: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class LivingSpectralConfig:
    spectral: SpectralGeometryConfig = field(
        default_factory=SpectralGeometryConfig
    )
    material: SurfaceMaterialConfig = field(
        default_factory=SurfaceMaterialConfig
    )
    quantum: QuantumEigenfieldConfig = field(
        default_factory=QuantumEigenfieldConfig
    )
    acoustic: AcousticBridgeConfig = field(
        default_factory=AcousticBridgeConfig
    )
    debounce_ms: float = 120.0
    source_position: tuple[float, float, float] | None = None
    listener_position: tuple[float, float, float] | None = None


@dataclass(frozen=True)
class LivingSpectralState:
    revision: int
    created_at: float
    reason: str
    invalidated_domains: tuple[str, ...]
    material_model: str
    mode_count: int
    spectral_gap: float
    frequency_min_hz: float
    frequency_max_hz: float
    mode_tracking_score: float | None
    paths: Mapping[str, str]
    descriptors: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "revision": self.revision,
            "created_at": self.created_at,
            "reason": self.reason,
            "invalidated_domains": list(self.invalidated_domains),
            "material_model": self.material_model,
            "mode_count": self.mode_count,
            "spectral_gap": self.spectral_gap,
            "frequency_min_hz": self.frequency_min_hz,
            "frequency_max_hz": self.frequency_max_hz,
            "mode_tracking_score": self.mode_tracking_score,
            "paths": dict(self.paths),
            "descriptors": dict(self.descriptors),
        }


@dataclass(frozen=True)
class _ComputationSnapshot:
    revision: int
    reason: str
    dirty: DirtyDomain
    vertices: np.ndarray
    faces: np.ndarray
    rho: np.ndarray
    material_fields: Mapping[str, np.ndarray]
    config: LivingSpectralConfig
    previous_spectral: SpectralGeometryResult | None
    previous_modal: SurfaceModalPacket | None


@dataclass(frozen=True)
class _ComputationResult:
    state: LivingSpectralState
    spectral: SpectralGeometryResult
    modal: SurfaceModalPacket


def _domain_names(domains: DirtyDomain) -> tuple[str, ...]:
    return tuple(
        domain.name.lower()
        for domain in (
            DirtyDomain.GEOMETRY,
            DirtyDomain.MATERIAL,
            DirtyDomain.QUANTUM,
            DirtyDomain.TIMING,
            DirtyDomain.ACOUSTICS,
        )
        if domains & domain
    )


def _latest_state_revision(output_directory: Path) -> int:
    latest = 0
    for candidate in output_directory.glob("state_[0-9]*"):
        if not candidate.is_dir():
            continue
        try:
            latest = max(latest, int(candidate.name.removeprefix("state_")))
        except ValueError:
            continue
    return latest


def height_field_to_mesh(
    height: np.ndarray,
    spatial_scale: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    height = np.asarray(height, dtype=np.float64)
    if height.ndim != 2 or min(height.shape) < 2:
        raise ValueError("height field must be a two-dimensional grid")
    rows, columns = height.shape
    yy, xx = np.mgrid[0:rows, 0:columns]
    vertices = np.column_stack(
        (
            (xx.reshape(-1) - 0.5 * (columns - 1)) * spatial_scale,
            (yy.reshape(-1) - 0.5 * (rows - 1)) * spatial_scale,
            height.reshape(-1),
        )
    )
    faces: list[tuple[int, int, int]] = []
    for y in range(rows - 1):
        for x in range(columns - 1):
            a = y * columns + x
            b = a + 1
            c = a + columns
            d = c + 1
            faces.extend(((a, b, d), (a, d, c)))
    return vertices, np.asarray(faces, dtype=np.int64)


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temporary.replace(path)


def _normalize_columns(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=0)
    return vectors / np.maximum(norms, 1e-15)


def track_modal_identity(
    previous: SurfaceModalPacket | None,
    current: SurfaceModalPacket,
) -> tuple[SurfaceModalPacket, float | None]:
    """Reorder and orient modes to maximize overlap with the last state."""
    if previous is None:
        return current, None
    old_vectors = np.asarray(previous.eigenvectors, dtype=np.float64)
    new_vectors = np.asarray(current.eigenvectors, dtype=np.float64)
    if old_vectors.shape[0] != new_vectors.shape[0]:
        return current, None
    overlap = np.abs(
        _normalize_columns(old_vectors).T @ _normalize_columns(new_vectors)
    )
    old_indices, new_indices = linear_sum_assignment(-overlap)
    pairs = sorted(zip(old_indices.tolist(), new_indices.tolist()))
    assigned = [new for _, new in pairs]
    order = assigned + [
        index for index in range(new_vectors.shape[1]) if index not in assigned
    ]
    order_array = np.asarray(order, dtype=np.int64)
    oriented = new_vectors[:, order_array].copy()
    for output_index, (old_index, new_index) in enumerate(pairs):
        sign = np.sign(np.dot(old_vectors[:, old_index], new_vectors[:, new_index]))
        oriented[:, output_index] *= 1.0 if sign == 0.0 else sign
    score = float(np.mean([overlap[old, new] for old, new in pairs]))
    metadata = dict(current.metadata)
    metadata.update(
        {
            "mode_tracking": "maximum_eigenvector_overlap",
            "mode_tracking_score": score,
        }
    )
    return (
        SurfaceModalPacket(
            model=current.model,
            eigenvalues=current.eigenvalues[order_array],
            eigenvectors=oriented,
            frequencies_hz=current.frequencies_hz[order_array],
            angular_frequencies=current.angular_frequencies[order_array],
            decay_times_seconds=current.decay_times_seconds[order_array],
            damping_rates=current.damping_rates[order_array],
            mode_weights=current.mode_weights[order_array],
            metadata=metadata,
        ),
        score,
    )


class LivingSpectralGeometry:
    """Coordinate evolving geometry, operators, spectra, timing, and IR state."""

    def __init__(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        output_directory: str | Path,
        config: LivingSpectralConfig = LivingSpectralConfig(),
        rho: np.ndarray | None = None,
        material_fields: Mapping[str, np.ndarray] | None = None,
    ) -> None:
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.config = config
        self._vertices = np.asarray(vertices, dtype=np.float64).copy()
        self._faces = np.asarray(faces, dtype=np.int64).copy()
        self._rho = (
            demo_density_matrix(4)
            if rho is None
            else np.asarray(rho, dtype=np.complex128).copy()
        )
        self._material_fields = {
            name: np.asarray(values, dtype=np.float64).copy()
            for name, values in (material_fields or {}).items()
        }
        self._dirty = DirtyDomain.ALL
        # Continue the on-disk revision sequence across process restarts.  A new
        # controller instance must never silently reuse state_000001.
        self._requested_revision = _latest_state_revision(self.output_directory)
        self._state: LivingSpectralState | None = None
        self._spectral_cache: SpectralGeometryResult | None = None
        self._modal_cache: SurfaceModalPacket | None = None
        self._last_error: BaseException | None = None
        self._last_reason = "initial state"
        self._listeners: list[Callable[[LivingSpectralState], None]] = []
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self._timer: threading.Timer | None = None
        self._executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="living-spectral"
        )
        self._latest_future: Future[_ComputationResult] | None = None
        self._closed = False

    @property
    def state(self) -> LivingSpectralState | None:
        with self._lock:
            return self._state

    @property
    def dirty_domains(self) -> DirtyDomain:
        with self._lock:
            return self._dirty

    def subscribe(
        self, listener: Callable[[LivingSpectralState], None]
    ) -> Callable[[], None]:
        with self._lock:
            self._listeners.append(listener)

        def unsubscribe() -> None:
            with self._lock:
                if listener in self._listeners:
                    self._listeners.remove(listener)

        return unsubscribe

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("living spectral geometry is closed")

    def _invalidate(
        self,
        domains: DirtyDomain,
        reason: str,
        schedule: bool,
    ) -> int | None:
        with self._lock:
            self._ensure_open()
            self._dirty |= domains
            self._last_reason = reason
            return self._schedule_locked() if schedule else None

    def update_geometry(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        *,
        schedule: bool = True,
        reason: str = "geometry mutation",
    ) -> int | None:
        with self._lock:
            self._vertices = np.asarray(vertices, dtype=np.float64).copy()
            self._faces = np.asarray(faces, dtype=np.int64).copy()
        return self._invalidate(DirtyDomain.ALL, reason, schedule)

    def update_height_field(
        self,
        height: np.ndarray,
        spatial_scale: float = 1.0,
        *,
        schedule: bool = True,
        reason: str = "developmental surface mutation",
    ) -> int | None:
        vertices, faces = height_field_to_mesh(height, spatial_scale)
        return self.update_geometry(
            vertices, faces, schedule=schedule, reason=reason
        )

    def update_from_emergent_engine(
        self,
        engine: Any,
        *,
        schedule: bool = True,
    ) -> int | None:
        height = np.asarray(engine.surface.height, dtype=np.float64)
        scale = float(engine.surface.parameters.spatial_scale)
        return self.update_height_field(
            height,
            scale,
            schedule=schedule,
            reason="emergent geometry update",
        )

    def update_material(
        self,
        *,
        schedule: bool = True,
        reason: str = "material mutation",
        **changes: Any,
    ) -> int | None:
        valid = SurfaceMaterialConfig.__dataclass_fields__
        unknown = set(changes).difference(valid)
        if unknown:
            raise ValueError(f"unknown material parameters: {sorted(unknown)}")
        if "model" in changes and changes["model"] not in MODEL_ORDER:
            raise ValueError(f"model must be one of {MODEL_ORDER}")
        with self._lock:
            self.config = replace(
                self.config,
                material=replace(self.config.material, **changes),
            )
        domains = (
            DirtyDomain.MATERIAL
            | DirtyDomain.QUANTUM
            | DirtyDomain.TIMING
            | DirtyDomain.ACOUSTICS
        )
        return self._invalidate(domains, reason, schedule)

    def update_material_fields(
        self,
        *,
        schedule: bool = True,
        reason: str = "material field mutation",
        **fields: np.ndarray,
    ) -> int | None:
        unknown = set(fields).difference({"voltage", "conductivity", "leakage"})
        if unknown:
            raise ValueError(f"unknown material fields: {sorted(unknown)}")
        with self._lock:
            self._material_fields.update(
                {
                    name: np.asarray(value, dtype=np.float64).copy()
                    for name, value in fields.items()
                }
            )
        return self._invalidate(
            DirtyDomain.MATERIAL
            | DirtyDomain.QUANTUM
            | DirtyDomain.TIMING
            | DirtyDomain.ACOUSTICS,
            reason,
            schedule,
        )

    def update_quantum_state(
        self,
        rho: np.ndarray,
        *,
        schedule: bool = True,
        reason: str = "quantum state mutation",
    ) -> int | None:
        with self._lock:
            self._rho = np.asarray(rho, dtype=np.complex128).copy()
        return self._invalidate(
            DirtyDomain.QUANTUM
            | DirtyDomain.TIMING
            | DirtyDomain.ACOUSTICS,
            reason,
            schedule,
        )

    def apply_event(
        self,
        event: LivingOperatorEvent,
        *,
        schedule: bool = True,
    ) -> int | None:
        payload = dict(event.payload)
        reason = event.reason or event.type.value
        if event.type is LivingEventType.GEOMETRY:
            if "height" in payload:
                return self.update_height_field(
                    payload["height"],
                    float(payload.get("spatial_scale", 1.0)),
                    schedule=schedule,
                    reason=reason,
                )
            return self.update_geometry(
                payload["vertices"],
                payload["faces"],
                schedule=schedule,
                reason=reason,
            )
        if event.type is LivingEventType.MATERIAL:
            fields = payload.pop("fields", None)
            if fields:
                self.update_material_fields(
                    schedule=False, reason=reason, **dict(fields)
                )
            return self.update_material(
                schedule=schedule, reason=reason, **payload
            )
        if event.type in (
            LivingEventType.QUANTUM,
            LivingEventType.MEASUREMENT,
        ):
            if "rho" not in payload:
                raise ValueError(f"{event.type.value} event requires rho")
            return self.update_quantum_state(
                payload["rho"], schedule=schedule, reason=reason
            )
        if event.type is LivingEventType.RECALCULATE:
            return self.schedule_recompute(reason=reason) if schedule else None
        raise ValueError(f"unsupported event type {event.type}")

    def _schedule_locked(self) -> int:
        self._requested_revision += 1
        revision = self._requested_revision
        self._last_error = None
        if self._timer is not None:
            self._timer.cancel()
        delay = max(0.0, self.config.debounce_ms) * 0.001
        self._timer = threading.Timer(delay, self._submit_revision, (revision,))
        self._timer.daemon = True
        self._timer.start()
        return revision

    def schedule_recompute(self, reason: str = "recalculate") -> int:
        with self._lock:
            self._ensure_open()
            self._last_reason = reason
            return self._schedule_locked()

    def _snapshot_locked(self, revision: int) -> _ComputationSnapshot:
        return _ComputationSnapshot(
            revision=revision,
            reason=self._last_reason,
            dirty=self._dirty,
            vertices=self._vertices.copy(),
            faces=self._faces.copy(),
            rho=self._rho.copy(),
            material_fields={
                name: values.copy()
                for name, values in self._material_fields.items()
            },
            config=self.config,
            previous_spectral=self._spectral_cache,
            previous_modal=self._modal_cache,
        )

    def _submit_revision(self, revision: int) -> None:
        with self._lock:
            if self._closed or revision != self._requested_revision:
                return
            snapshot = self._snapshot_locked(revision)
            future = self._executor.submit(self._compute, snapshot)
            self._latest_future = future
            future.add_done_callback(
                lambda completed, rev=revision: self._finish_future(
                    rev, completed
                )
            )

    def _finish_future(
        self,
        revision: int,
        future: Future[_ComputationResult],
    ) -> None:
        try:
            result = future.result()
        except BaseException as exc:
            with self._condition:
                if revision == self._requested_revision:
                    self._last_error = exc
                self._condition.notify_all()
            return
        self._publish(result)

    def recompute_now(self, reason: str = "synchronous recalculation") -> LivingSpectralState:
        with self._lock:
            self._ensure_open()
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            self._requested_revision += 1
            revision = self._requested_revision
            self._last_reason = reason
            self._last_error = None
            snapshot = self._snapshot_locked(revision)
        result = self._compute(snapshot)
        if not self._publish(result):
            raise RuntimeError("synchronous result became stale before publication")
        return result.state

    def wait(self, timeout: float | None = None) -> LivingSpectralState:
        deadline = None if timeout is None else time.monotonic() + timeout
        with self._condition:
            while True:
                if self._last_error is not None:
                    raise RuntimeError("living spectral recomputation failed") from self._last_error
                if (
                    self._state is not None
                    and self._state.revision == self._requested_revision
                    and self._dirty == DirtyDomain.NONE
                ):
                    return self._state
                remaining = (
                    None
                    if deadline is None
                    else max(0.0, deadline - time.monotonic())
                )
                if remaining == 0.0:
                    raise TimeoutError("living spectral recomputation timed out")
                self._condition.wait(remaining)

    def _solve_spectral(
        self, snapshot: _ComputationSnapshot
    ) -> SpectralGeometryResult:
        if (
            not (snapshot.dirty & DirtyDomain.GEOMETRY)
            and snapshot.previous_spectral is not None
        ):
            return snapshot.previous_spectral
        solver = MeshSpectralGeometry(
            snapshot.vertices, snapshot.faces, snapshot.config.spectral
        )
        return solver.solve(
            snapshot.config.source_position,
            snapshot.config.listener_position,
        )

    def _solve_material(
        self,
        snapshot: _ComputationSnapshot,
        spectral: SpectralGeometryResult,
    ) -> tuple[SurfaceModalPacket, float | None]:
        if (
            not (
                snapshot.dirty
                & (DirtyDomain.GEOMETRY | DirtyDomain.MATERIAL)
            )
            and snapshot.previous_modal is not None
        ):
            return snapshot.previous_modal, None
        model = create_surface_model(
            spectral.vertices,
            spectral.faces,
            spectral.eigenvalues,
            spectral.eigenvectors,
            snapshot.config.material,
        )
        fields = dict(snapshot.material_fields)
        if (
            snapshot.config.material.model == "bioelectric_surface"
            and "voltage" not in fields
        ):
            fields["voltage"] = np.zeros(
                len(spectral.vertices), dtype=np.float64
            )
        current = model.solve(**fields)
        return track_modal_identity(snapshot.previous_modal, current)

    @staticmethod
    def _export_spectral(
        spectral: SpectralGeometryResult,
        path: Path,
    ) -> Path:
        np.savez_compressed(
            path,
            geometry_kind=np.asarray("triangular_surface"),
            vertices=spectral.vertices,
            edges=np.empty((0, 2), dtype=np.int64),
            faces=spectral.faces,
            eigenvalues=spectral.eigenvalues,
            eigenvectors=spectral.eigenvectors,
            frequencies_hz=spectral.frequencies_hz,
            mode_weights=spectral.mode_weights,
            damping=np.empty(0, dtype=np.float64),
            vertex_labels=np.empty(0, dtype="U1"),
            edge_weights=np.empty(0, dtype=np.float64),
            metadata_json=np.asarray(
                json.dumps(
                    {
                        "solver": "spectral_geometry_v1",
                        "operator": "cotangent_laplace_beltrami",
                    },
                    sort_keys=True,
                )
            ),
        )
        return path

    @staticmethod
    def _export_timing(state: EigenfieldState, prefix: Path) -> dict[str, Path]:
        npz_path = prefix.with_suffix(".npz")
        json_path = prefix.with_suffix(".json")
        np.savez_compressed(
            npz_path,
            material_model=np.asarray(state.material_model),
            eigenvalues=state.eigenvalues,
            frequencies_hz=state.frequencies_hz,
            decay_times_seconds=state.decay_times_seconds,
            t60_seconds=state.t60_seconds,
            damping_rates=state.damping_rates,
            mode_weights=state.material_weights,
            mode_probabilities=state.probabilities,
            mode_amplitudes=state.amplitudes,
            cloud_xyz=np.asarray(
                [[p.cloud_x, p.cloud_y, p.cloud_z] for p in state.points],
                dtype=np.float64,
            ),
        )
        _atomic_json(
            json_path,
            {
                "material_model": state.material_model,
                "mode_count": len(state.points),
                "entropy_bits": state.entropy_bits,
                "effective_participation": state.effective_participation,
            },
        )
        return {"npz": npz_path, "json": json_path}

    def _compute(self, snapshot: _ComputationSnapshot) -> _ComputationResult:
        revision_dir = self.output_directory / f"state_{snapshot.revision:06d}"
        revision_dir.mkdir(parents=True, exist_ok=True)
        spectral = self._solve_spectral(snapshot)
        spectral_path = self._export_spectral(
            spectral, revision_dir / "spectral_geometry.npz"
        )
        modal, tracking_score = self._solve_material(snapshot, spectral)
        material_paths = export_packet(
            modal,
            snapshot.config.material,
            revision_dir / "surface_material",
        )

        quantum = QuantumEigenfieldEngine(
            snapshot.rho,
            modal_packet=modal,
            config=snapshot.config.quantum,
        )
        quantum_paths = quantum.export(revision_dir / "quantum_eigenfield")
        timing = EigenfieldState(quantum_paths["npz"])
        timing_paths = self._export_timing(
            timing, revision_dir / "timing_snapshot"
        )
        bridge = GeometryAcousticsBridgeV2(
            quantum_paths["npz"], snapshot.config.acoustic
        )
        ir_name = f"ir_{modal.model}_r{snapshot.revision:06d}"
        acoustic_paths = bridge.export(revision_dir / ir_name)

        bundle_path = revision_dir / "living_spectral_state.npz"
        np.savez_compressed(
            bundle_path,
            revision=np.asarray(snapshot.revision, dtype=np.int64),
            vertices=spectral.vertices,
            faces=spectral.faces,
            material_model=np.asarray(modal.model),
            eigenvalues=modal.eigenvalues,
            eigenvectors=modal.eigenvectors,
            frequencies_hz=modal.frequencies_hz,
            angular_frequencies=modal.angular_frequencies,
            decay_times_seconds=modal.decay_times_seconds,
            t60_seconds=modal.t60_seconds,
            damping_rates=modal.damping_rates,
            mode_weights=modal.mode_weights,
            mode_probabilities=quantum.mode_probabilities,
            mode_amplitudes=quantum.mode_amplitudes,
            spatial_eigenfield=quantum.spatial_eigenfield,
            developmental_drive=quantum.developmental_drive,
            material_metadata_json=np.asarray(
                json.dumps(modal.metadata, sort_keys=True)
            ),
        )
        flat_paths = {
            "directory": str(revision_dir),
            "spectral_npz": str(spectral_path),
            "material_npz": str(material_paths["npz"]),
            "material_json": str(material_paths["json"]),
            "quantum_npz": str(quantum_paths["npz"]),
            "quantum_json": str(quantum_paths["json"]),
            "timing_npz": str(timing_paths["npz"]),
            "timing_json": str(timing_paths["json"]),
            "ir_wav": str(acoustic_paths["wav"]),
            "ir_npz": str(acoustic_paths["npz"]),
            "ir_json": str(acoustic_paths["json"]),
            "bundle_npz": str(bundle_path),
        }
        frequencies = modal.frequencies_hz
        descriptors = {
            "quantum": quantum.quantum_descriptors.to_dict(),
            "timing": {
                "entropy_bits": timing.entropy_bits,
                "effective_participation": timing.effective_participation,
            },
            "acoustics": bridge.acoustic_descriptors(),
            "spectral": {
                "spectral_gap": spectral.spectral_gap,
                "mean_spacing": spectral.mean_spacing,
                "spacing_variance": spectral.spacing_variance,
                "spectral_entropy": spectral.spectral_entropy,
            },
        }
        state = LivingSpectralState(
            revision=snapshot.revision,
            created_at=time.time(),
            reason=snapshot.reason,
            invalidated_domains=_domain_names(snapshot.dirty),
            material_model=modal.model,
            mode_count=len(modal.eigenvalues),
            spectral_gap=spectral.spectral_gap,
            frequency_min_hz=float(np.min(frequencies)),
            frequency_max_hz=float(np.max(frequencies)),
            mode_tracking_score=tracking_score,
            paths=flat_paths,
            descriptors=descriptors,
        )
        _atomic_json(revision_dir / "state.json", state.to_dict())
        return _ComputationResult(state=state, spectral=spectral, modal=modal)

    def _publish(self, result: _ComputationResult) -> bool:
        with self._condition:
            if result.state.revision != self._requested_revision:
                self._condition.notify_all()
                return False
            self._state = result.state
            self._spectral_cache = result.spectral
            self._modal_cache = result.modal
            self._dirty = DirtyDomain.NONE
            self._last_error = None
            listeners = list(self._listeners)
            _atomic_json(
                self.output_directory / "current_state.json",
                result.state.to_dict(),
            )
            self._condition.notify_all()
        for listener in listeners:
            try:
                listener(result.state)
            except Exception:
                # State publication must not be rolled back by a UI listener.
                continue
        return True

    def close(self, wait: bool = True) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
        self._executor.shutdown(wait=wait, cancel_futures=True)

    def __enter__(self) -> "LivingSpectralGeometry":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rho", type=Path)
    parser.add_argument("--model", choices=MODEL_ORDER, default=MODEL_ORDER[0])
    parser.add_argument("--modes", type=int, default=32)
    parser.add_argument("--sample-rate", type=int, default=48000)
    parser.add_argument("--duration", type=float, default=6.0)
    args = parser.parse_args()
    vertices, faces = load_obj(args.mesh)
    rho = None if args.rho is None else load_density_matrix(args.rho)
    config = LivingSpectralConfig(
        spectral=SpectralGeometryConfig(n_modes=args.modes),
        material=SurfaceMaterialConfig(model=args.model, n_modes=args.modes),
        quantum=QuantumEigenfieldConfig(n_geometric_modes=args.modes),
        acoustic=AcousticBridgeConfig(
            sample_rate=args.sample_rate,
            duration_seconds=args.duration,
        ),
    )
    with LivingSpectralGeometry(
        vertices, faces, args.output, config=config, rho=rho
    ) as living:
        state = living.recompute_now("initial CLI state")
        print("Living Spectral Geometry v1")
        print(f"  revision: {state.revision}")
        print(f"  model:    {state.material_model}")
        print(f"  modes:    {state.mode_count}")
        print(f"  IR:       {state.paths['ir_wav']}")
        print(f"  state:    {args.output / 'current_state.json'}")


if __name__ == "__main__":
    main()
