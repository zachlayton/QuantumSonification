"""Local read-only web panel for the live Quantum Chladni instrument.

The panel observes the same immutable modal frames and Laplace--Beltrami
eigenbasis sent to Max/SuperCollider.  It never mutates the density matrix,
modal profile, QPE result, event identity, or audio routing.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import threading
import time
from typing import Any

import numpy as np


SCHEMA = "qmw.sophie_germain.panel.v1"
ASSET_ROOT = Path(__file__).with_name("sophie_germain_panel")


def _finite(value: Any, name: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _finite_vector(value: Any, name: str) -> np.ndarray:
    vector = np.asarray(value, dtype=np.float64)
    if vector.ndim != 1 or np.any(~np.isfinite(vector)):
        raise ValueError(f"{name} must be a finite vector")
    return vector.copy()


class SophieGermainPanelStore:
    """Thread-safe JSON snapshots of an authoritative modal source.

    ``observe`` is deliberately duck-typed so the panel module does not create
    an import cycle with ``quantum_chladni_controller_v1``.  The controller's
    validated ``ModalProfile`` and ``QuantumChladniFrame`` are the intended
    source types.
    """

    def __init__(
        self,
        profile: Any,
        *,
        event_history: int = 96,
        source: str = "quantum_chladni_synth_v1",
    ) -> None:
        vertices = np.asarray(profile.vertices, dtype=np.float64)
        eigenvectors = np.asarray(profile.eigenvectors, dtype=np.float64)
        eigenvalues = _finite_vector(profile.eigenvalues, "eigenvalues")
        frequencies = _finite_vector(profile.frequencies_hz, "frequencies_hz")
        decays = _finite_vector(profile.decay_seconds, "decay_seconds")
        weights = _finite_vector(profile.mode_weights, "mode_weights")
        if vertices.ndim != 2 or vertices.shape[1] != 3:
            raise ValueError("vertices must have shape (samples, 3)")
        if eigenvectors.shape != (len(vertices), len(eigenvalues)):
            raise ValueError("eigenvectors must have shape (samples, modes)")
        if np.any(~np.isfinite(vertices)) or np.any(~np.isfinite(eigenvectors)):
            raise ValueError("geometry must be finite")
        if not (
            len(eigenvalues)
            == len(frequencies)
            == len(decays)
            == len(weights)
        ):
            raise ValueError("modal profile vectors must have equal lengths")
        if int(event_history) < 1:
            raise ValueError("event_history must be positive")
        source_name = str(source).strip()
        if not source_name:
            raise ValueError("source must be nonempty")

        self._lock = threading.RLock()
        self._source = source_name
        self._started = time.monotonic()
        self._latest_revision = 0
        self._latest_frame: dict[str, Any] | None = None
        self._qpe_events: deque[dict[str, Any]] = deque(maxlen=int(event_history))
        self._geodesic_events: deque[dict[str, Any]] = deque(
            maxlen=int(event_history)
        )
        self._geodesic_event_ids: set[str] = set()
        self._geometry = {
            "schema": SCHEMA,
            "source": self._source,
            "profile": str(profile.name),
            "geometry_revision": 1,
            "operator": "Laplace-Beltrami",
            "sample_count": int(len(vertices)),
            "mode_count": int(len(eigenvalues)),
            "vertices": vertices.tolist(),
            "eigenvectors": eigenvectors.tolist(),
            "eigenvalues": eigenvalues.tolist(),
            "frequencies_hz": frequencies.tolist(),
            "decay_seconds": decays.tolist(),
            "mode_weights": weights.tolist(),
            "camera_semantics": (
                "display-only; camera rotation does not alter the physical "
                "geometry, modal state, timing, or sound"
            ),
        }

    @property
    def latest_revision(self) -> int:
        with self._lock:
            return self._latest_revision

    def observe(self, frame: Any, *, observed_at: float | None = None) -> bool:
        """Commit one complete monotonic frame after copying every vector."""

        revision = int(frame.revision)
        frequencies = _finite_vector(frame.frequencies_hz, "frequencies_hz")
        decays = _finite_vector(frame.decay_seconds, "decay_seconds")
        weights = _finite_vector(frame.mode_weights, "mode_weights")
        probabilities = _finite_vector(frame.probabilities, "probabilities")
        phases = _finite_vector(frame.phases, "phases")
        pans = _finite_vector(frame.pans, "pans")
        populations = _finite_vector(frame.basis_populations, "basis_populations")
        basis_phases = _finite_vector(frame.basis_phases, "basis_phases")
        mode_count = int(self._geometry["mode_count"])
        if any(
            len(vector) != mode_count
            for vector in (frequencies, decays, weights, probabilities, phases, pans)
        ):
            raise ValueError("frame modal vectors must match the geometry mode count")
        if len(populations) != len(basis_phases):
            raise ValueError("basis populations and phases must have equal lengths")
        if np.any(probabilities < 0.0) or not math.isclose(
            float(np.sum(probabilities)), 1.0, rel_tol=1e-8, abs_tol=1e-8
        ):
            raise ValueError("modal probabilities must be normalized")
        if np.any(populations < 0.0) or not math.isclose(
            float(np.sum(populations)), 1.0, rel_tol=1e-8, abs_tol=1e-8
        ):
            raise ValueError("basis populations must be normalized")
        receipt_seconds = (
            time.monotonic() - self._started
            if observed_at is None
            else _finite(observed_at, "observed_at")
        )
        if receipt_seconds < 0.0:
            raise ValueError("observed_at must be nonnegative")
        current_value = getattr(frame, "probability_current", None)
        probability_current: np.ndarray | None = None
        if current_value is not None:
            probability_current = np.asarray(current_value, dtype=np.float64)
            expected_shape = (int(self._geometry["sample_count"]), 3)
            if probability_current.shape != expected_shape:
                raise ValueError(
                    "probability_current must have shape "
                    f"{expected_shape}"
                )
            if np.any(~np.isfinite(probability_current)):
                raise ValueError("probability_current must be finite")

        event = {
            "event_id": f"qpe:{revision}",
            "kind": "qpe_frame_sample",
            "revision": revision,
            "observer_elapsed_seconds": receipt_seconds,
            "qpe_bits": int(frame.qpe_bits),
            "qpe_integer": int(frame.qpe_integer),
            "qpe_phase": _finite(frame.qpe_phase, "qpe_phase"),
            "dominant_mode": int(frame.qpe_dominant_mode),
            "confidence": _finite(frame.qpe_confidence, "qpe_confidence"),
            "timing_semantics": (
                "observer receipt at the controller publication cadence; "
                "not a geodesic-rhythm onset"
            ),
        }
        snapshot = {
            "schema": SCHEMA,
            "source": self._source,
            "source_revision": revision,
            "observer_elapsed_seconds": receipt_seconds,
            "profile": self._geometry["profile"],
            "mode_count": mode_count,
            "basis_dimension": int(len(populations)),
            "diagnostics": {
                "purity": _finite(frame.purity, "purity"),
                "entropy_normalized": _finite(
                    frame.entropy_normalized, "entropy_normalized"
                ),
                "coherence_normalized": _finite(
                    frame.coherence_normalized, "coherence_normalized"
                ),
            },
            "modes": [
                {
                    "index": index,
                    "frequency_hz": float(frequencies[index]),
                    "decay_seconds": float(decays[index]),
                    "material_weight": float(weights[index]),
                    "probability": float(probabilities[index]),
                    "phase_radians": float(phases[index]),
                    "pan": float(pans[index]),
                }
                for index in range(mode_count)
            ],
            "basis": [
                {
                    "index": index,
                    "population": float(populations[index]),
                    "phase_radians": float(basis_phases[index]),
                }
                for index in range(len(populations))
            ],
            "qpe": {
                "bits": int(frame.qpe_bits),
                "integer": int(frame.qpe_integer),
                "bitstring": str(frame.qpe_bitstring),
                "phase": _finite(frame.qpe_phase, "qpe_phase"),
                "dominant_mode": int(frame.qpe_dominant_mode),
                "confidence": _finite(frame.qpe_confidence, "qpe_confidence"),
            },
            "projection": {
                "amplitude_definition": "sqrt(P(j|y)) * exp(i * phase_j)",
                "spatial_basis": "transmitted Laplace-Beltrami eigenvectors",
                "real_view": "Re(sum_j a_j phi_j)",
                "quadrature_view": "Im(sum_j a_j phi_j)",
                "mapping_status": "declared quantum-conditioned modal projection",
            },
            "flow": (
                None
                if probability_current is None
                else {
                    "kind": "instantaneous_probability_current",
                    "definition": str(frame.probability_current_definition),
                    "vectors": probability_current.tolist(),
                    "coordinate_system": "source normalized planar coordinates",
                    "boundary_flux_convention": (
                        "Dirichlet membrane boundary; psi=0 implies zero normal "
                        "probability current at the modeled edge"
                    ),
                    "continuity_residual": None,
                    "continuity_note": (
                        "not evaluated across frames because each QPE-conditioned "
                        "frame is a newly admitted conditional state"
                    ),
                }
            ),
            "availability": {
                "modal_geometry": {"available": True, "source": "live frame"},
                "phase_sensitive_projection": {
                    "available": True,
                    "source": "live complex modal amplitudes",
                },
                "probability_or_energy_flow": {
                    "available": probability_current is not None,
                    "source": (
                        "QuantumChladniController probability_current"
                        if probability_current is not None
                        else None
                    ),
                    "reason": (
                        "instantaneous QPE-conditioned probability current"
                        if probability_current is not None
                        else (
                            "the source geometry does not publish a compatible "
                            "surface-gradient operator or mesh connectivity"
                        )
                    ),
                },
                "geodesic_rhythm": {
                    "available": bool(self._geodesic_events),
                    "reason": (
                        "no authoritative geodesic pulse source has been observed"
                        if not self._geodesic_events
                        else "authoritative pulse records received"
                    ),
                },
            },
        }
        with self._lock:
            if revision <= self._latest_revision:
                return False
            self._latest_revision = revision
            self._latest_frame = snapshot
            self._qpe_events.append(event)
        return True

    def observe_geodesic_pulse(
        self,
        *,
        record_index: int,
        site: int,
        intrinsic_length: float,
        weighted_increment: float,
        source_revision: int | None = None,
        observed_at: float | None = None,
    ) -> bool:
        """Record an already-produced geodesic pulse without rescheduling it."""

        record = int(record_index)
        site_index = int(site)
        if record < 0 or site_index < 0:
            raise ValueError("record_index and site must be nonnegative")
        event_id = f"geodesic:{site_index}:{record}"
        event = {
            "event_id": event_id,
            "kind": "geodesic_pulse",
            "record_index": record,
            "site": site_index,
            "source_revision": (
                None if source_revision is None else int(source_revision)
            ),
            "intrinsic_length": _finite(intrinsic_length, "intrinsic_length"),
            "weighted_increment": _finite(
                weighted_increment, "weighted_increment"
            ),
            "observer_elapsed_seconds": (
                time.monotonic() - self._started
                if observed_at is None
                else _finite(observed_at, "observed_at")
            ),
            "timing_semantics": (
                "display of an admitted source pulse; the panel does not "
                "schedule or quantize the event"
            ),
        }
        if event["intrinsic_length"] < 0.0 or event["observer_elapsed_seconds"] < 0.0:
            raise ValueError("geodesic coordinates must be nonnegative")
        with self._lock:
            if event_id in self._geodesic_event_ids:
                return False
            self._geodesic_events.append(event)
            self._geodesic_event_ids.add(event_id)
            retained = {item["event_id"] for item in self._geodesic_events}
            self._geodesic_event_ids.intersection_update(retained)
            if self._latest_frame is not None:
                self._latest_frame["availability"]["geodesic_rhythm"] = {
                    "available": True,
                    "reason": "authoritative pulse records received",
                }
        return True

    def geometry_snapshot(self) -> dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self._geometry, allow_nan=False))

    def frame_snapshot(self) -> dict[str, Any]:
        with self._lock:
            if self._latest_frame is None:
                return {
                    "schema": SCHEMA,
                    "source": self._source,
                    "source_revision": 0,
                    "status": "waiting_for_complete_frame",
                    "qpe_events": [],
                    "geodesic_events": [],
                }
            snapshot = dict(self._latest_frame)
            snapshot["status"] = "live"
            snapshot["qpe_events"] = list(self._qpe_events)
            snapshot["geodesic_events"] = list(self._geodesic_events)
            return json.loads(json.dumps(snapshot, allow_nan=False))


class _PanelHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], store: SophieGermainPanelStore):
        self.store = store
        super().__init__(address, _PanelRequestHandler)


class _PanelRequestHandler(BaseHTTPRequestHandler):
    server: _PanelHTTPServer

    def _send(self, body: bytes, content_type: str, *, cache: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        path = self.path.split("?", 1)[0]
        if path == "/api/frame":
            body = json.dumps(
                self.server.store.frame_snapshot(), separators=(",", ":")
            ).encode("utf-8")
            self._send(body, "application/json; charset=utf-8", cache="no-store")
            return
        if path == "/api/geometry":
            body = json.dumps(
                self.server.store.geometry_snapshot(), separators=(",", ":")
            ).encode("utf-8")
            self._send(
                body,
                "application/json; charset=utf-8",
                cache="private, max-age=3600",
            )
            return
        asset = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/index.html": ("index.html", "text/html; charset=utf-8"),
            "/styles.css": ("styles.css", "text/css; charset=utf-8"),
            "/app.js": ("app.js", "text/javascript; charset=utf-8"),
        }.get(path)
        if asset is None:
            self.send_error(404)
            return
        filename, content_type = asset
        self._send(
            (ASSET_ROOT / filename).read_bytes(),
            content_type,
            cache="no-cache",
        )

    def log_message(self, _format: str, *_args: Any) -> None:
        return


@dataclass
class SophieGermainPanelServer:
    store: SophieGermainPanelStore
    server: _PanelHTTPServer
    thread: threading.Thread
    url: str

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2.0)


def start_sophie_germain_panel(
    profile: Any,
    *,
    host: str = "127.0.0.1",
    port: int = 8788,
    source: str = "quantum_chladni_synth_v1",
) -> SophieGermainPanelServer:
    """Start the local panel server; port 0 requests an ephemeral test port."""

    store = SophieGermainPanelStore(profile, source=source)
    server = _PanelHTTPServer((str(host), int(port)), store)
    thread = threading.Thread(
        target=server.serve_forever,
        name="qmw-sophie-germain-panel",
        daemon=True,
    )
    thread.start()
    bound_host, bound_port = server.server_address[:2]
    display_host = "127.0.0.1" if bound_host in {"", "0.0.0.0"} else bound_host
    return SophieGermainPanelServer(
        store=store,
        server=server,
        thread=thread,
        url=f"http://{display_host}:{bound_port}/",
    )
