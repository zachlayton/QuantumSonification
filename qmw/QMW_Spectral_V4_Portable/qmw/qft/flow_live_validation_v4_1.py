"""Live UDP capture and contract validation for the QFT V4.1 flow sidecar.

The validator is an observer of OSC datagrams.  It does not synthesize sound,
modify a QFT engine, or claim that a successful capture validates an audio
receiver.  It verifies the V4/V4.1 transport boundary only.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import math
from pathlib import Path
import threading
from typing import Any

from .flow_observer_v4_1 import OSC_ROOT, SCHEMA as FLOW_SCHEMA, SOURCE_SCHEMA
from .live_osc_v4 import OSC_VERSION, SITES


FIELD_ROOT = f"/qmw/qft/v{OSC_VERSION}"
FIELD_SCHEMA = SOURCE_SCHEMA
MODE_WAVE_NUMBERS = tuple([0, *[value for k in range(1, 8) for value in (k, k)], 8])
MODE_COMPONENT_CODES = (0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 3)


@dataclass
class _FlowCapture:
    revision: int
    source_revision: int
    time: float
    errors: list[str] = field(default_factory=list)
    site_indices: set[int] = field(default_factory=set)
    bonds: set[tuple[int, int]] = field(default_factory=set)
    mode_indices: set[int] = field(default_factory=set)
    site_basis_seen: bool = False
    mode_basis_seen: bool = False
    wave_numbers: tuple[int, ...] | None = None
    component_codes: tuple[int, ...] | None = None
    global_seen: bool = False


@dataclass(frozen=True)
class ValidatedFlowCapture:
    revision: int
    source_revision: int
    time: float
    valid: bool
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "revision": self.revision,
            "source_revision": self.source_revision,
            "time": self.time,
            "valid": self.valid,
            "errors": list(self.errors),
        }


class QFTV41LiveCaptureValidator:
    """Reconstruct V4 and V4.1 atomic frames from independently received OSC."""

    def __init__(self, *, sites: int = SITES) -> None:
        if sites != SITES:
            raise ValueError("V4.1 validation is defined for the sixteen-site V4 source")
        self.sites = sites
        self._field_open: dict[int, float] = {}
        self._field_complete: dict[int, float] = {}
        self._flow_open: dict[int, _FlowCapture] = {}
        self.completed: list[ValidatedFlowCapture] = []

    @staticmethod
    def _finite(value: Any) -> bool:
        try:
            return math.isfinite(float(value))
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _integer(value: Any) -> int | None:
        try:
            number = int(value)
        except (TypeError, ValueError):
            return None
        return number if number == value else None

    def _flow(self, args: tuple[Any, ...], expected: int, label: str) -> _FlowCapture | None:
        if len(args) != expected:
            return None
        revision = self._integer(args[0])
        if revision is None:
            return None
        capture = self._flow_open.get(revision)
        if capture is None:
            return None
        return capture

    def accept_field(self, address: str, *args: Any) -> None:
        if address == f"{FIELD_ROOT}/frame/begin":
            if len(args) != 3:
                return
            revision = self._integer(args[0])
            if revision is None or not self._finite(args[1]) or args[2] != FIELD_SCHEMA:
                return
            self._field_open[revision] = float(args[1])
        elif address == f"{FIELD_ROOT}/frame/end" and len(args) == 1:
            revision = self._integer(args[0])
            if revision is not None and revision in self._field_open:
                self._field_complete[revision] = self._field_open.pop(revision)

    def accept_flow(self, address: str, *args: Any) -> None:
        if address == f"{OSC_ROOT}/frame/begin":
            if len(args) != 5:
                return
            revision = self._integer(args[0])
            source_revision = self._integer(args[1])
            if revision is None or source_revision is None or not self._finite(args[2]):
                return
            capture = _FlowCapture(revision, source_revision, float(args[2]))
            if args[3] != FLOW_SCHEMA:
                capture.errors.append("unexpected V4.1 schema")
            if args[4] != FIELD_SCHEMA:
                capture.errors.append("unexpected V4 source schema")
            source_time = self._field_complete.get(source_revision)
            if source_time is None:
                capture.errors.append("V4 source revision was not atomically captured")
            elif not math.isclose(source_time, capture.time, abs_tol=1e-7):
                capture.errors.append("V4 source and V4.1 times differ")
            self._flow_open[revision] = capture
            return

        if not args:
            return
        revision = self._integer(args[0])
        if revision is None:
            return
        capture = self._flow_open.get(revision)
        if capture is None:
            return

        if address == f"{OSC_ROOT}/basis/site":
            if len(args) != 5 or args[1] != "site" or args[2] != self.sites or args[3] != "periodic" or not self._finite(args[4]):
                capture.errors.append("invalid site-basis metadata")
            else:
                capture.site_basis_seen = True
        elif address == f"{OSC_ROOT}/basis/mode":
            if len(args) != 3 or args[1] != "real_fourier" or args[2] != self.sites:
                capture.errors.append("invalid normal-mode-basis metadata")
            else:
                capture.mode_basis_seen = True
        elif address == f"{OSC_ROOT}/mode/wave-number":
            if len(args) != self.sites + 1:
                capture.errors.append("invalid mode wave-number payload length")
            else:
                capture.wave_numbers = tuple(int(value) for value in args[1:])
        elif address == f"{OSC_ROOT}/mode/component":
            if len(args) != self.sites + 1:
                capture.errors.append("invalid mode component payload length")
            else:
                capture.component_codes = tuple(int(value) for value in args[1:])
        elif address == f"{OSC_ROOT}/site":
            if len(args) != 6 or not all(self._finite(value) for value in args[2:]):
                capture.errors.append("invalid site payload")
            else:
                site = self._integer(args[1])
                if site is None or not 0 <= site < self.sites:
                    capture.errors.append("site index outside V4 lattice")
                elif site in capture.site_indices:
                    capture.errors.append("duplicate site payload")
                else:
                    capture.site_indices.add(site)
        elif address == f"{OSC_ROOT}/bond":
            if len(args) != 4 or not self._finite(args[3]):
                capture.errors.append("invalid bond payload")
            else:
                origin, destination = self._integer(args[1]), self._integer(args[2])
                if origin is None or destination is None or not 0 <= origin < self.sites or destination != (origin + 1) % self.sites:
                    capture.errors.append("bond is not a directed periodic V4 edge")
                elif (origin, destination) in capture.bonds:
                    capture.errors.append("duplicate bond payload")
                else:
                    capture.bonds.add((origin, destination))
        elif address == f"{OSC_ROOT}/mode":
            if len(args) != 7 or not all(self._finite(value) for value in args[2:]):
                capture.errors.append("invalid mode payload")
            else:
                mode = self._integer(args[1])
                if mode is None or not 0 <= mode < self.sites:
                    capture.errors.append("mode index outside V4 basis")
                elif mode in capture.mode_indices:
                    capture.errors.append("duplicate mode payload")
                elif args[2] != MODE_WAVE_NUMBERS[mode] or args[3] != MODE_COMPONENT_CODES[mode]:
                    capture.errors.append("mode metadata disagrees with V4 real-Fourier order")
                else:
                    capture.mode_indices.add(mode)
        elif address == f"{OSC_ROOT}/global":
            if len(args) != 8 or not all(self._finite(value) for value in args[1:]):
                capture.errors.append("invalid global diagnostics payload")
            elif capture.global_seen:
                capture.errors.append("duplicate global diagnostics payload")
            else:
                capture.global_seen = True
        elif address == f"{OSC_ROOT}/frame/end":
            if len(args) != 1:
                return
            self._finish(revision, capture)

    def _finish(self, revision: int, capture: _FlowCapture) -> None:
        expected_indices = set(range(self.sites))
        expected_bonds = {(site, (site + 1) % self.sites) for site in range(self.sites)}
        if not capture.site_basis_seen:
            capture.errors.append("missing site-basis metadata")
        if not capture.mode_basis_seen:
            capture.errors.append("missing normal-mode-basis metadata")
        if capture.wave_numbers != MODE_WAVE_NUMBERS:
            capture.errors.append("missing or incorrect real-Fourier wave-number order")
        if capture.component_codes != MODE_COMPONENT_CODES:
            capture.errors.append("missing or incorrect real-Fourier component order")
        if capture.site_indices != expected_indices:
            capture.errors.append("incomplete sixteen-site payload")
        if capture.bonds != expected_bonds:
            capture.errors.append("incomplete periodic bond ring")
        if capture.mode_indices != expected_indices:
            capture.errors.append("incomplete sixteen-mode payload")
        if not capture.global_seen:
            capture.errors.append("missing global diagnostics payload")
        self.completed.append(
            ValidatedFlowCapture(
                revision=capture.revision,
                source_revision=capture.source_revision,
                time=capture.time,
                valid=not capture.errors,
                errors=tuple(capture.errors),
            )
        )
        del self._flow_open[revision]

    def report(self) -> dict[str, Any]:
        return {
            "schema": "qmw.scalar_field.first_moment_flow.capture_report.v4_1",
            "field_schema": FIELD_SCHEMA,
            "flow_schema": FLOW_SCHEMA,
            "sites": self.sites,
            "completed_frames": [item.to_dict() for item in self.completed],
            "valid_frames": sum(item.valid for item in self.completed),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture and validate live QFT V4.1 OSC frames")
    parser.add_argument("--field-host", default="127.0.0.1")
    parser.add_argument("--field-port", type=int, default=17860)
    parser.add_argument("--flow-host", default="127.0.0.1")
    parser.add_argument("--flow-port", type=int, default=17862)
    parser.add_argument("--frames", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.frames < 1 or not math.isfinite(args.timeout) or args.timeout <= 0.0:
        parser.error("--frames must be positive and --timeout must be finite and positive")

    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer

    validator = QFTV41LiveCaptureValidator()
    completed = threading.Event()

    def accept_field(address: str, *payload: Any) -> None:
        validator.accept_field(address, *payload)

    def accept_flow(address: str, *payload: Any) -> None:
        validator.accept_flow(address, *payload)
        if len(validator.completed) >= args.frames:
            completed.set()

    field_dispatcher, flow_dispatcher = Dispatcher(), Dispatcher()
    field_dispatcher.set_default_handler(accept_field)
    flow_dispatcher.set_default_handler(accept_flow)
    field_server = ThreadingOSCUDPServer((args.field_host, args.field_port), field_dispatcher)
    flow_server = ThreadingOSCUDPServer((args.flow_host, args.flow_port), flow_dispatcher)
    threads = [
        threading.Thread(target=field_server.serve_forever, daemon=True),
        threading.Thread(target=flow_server.serve_forever, daemon=True),
    ]
    for thread in threads:
        thread.start()
    try:
        completed.wait(args.timeout)
    finally:
        for server in (field_server, flow_server):
            server.shutdown()
            server.server_close()

    report = validator.report()
    if len(validator.completed) < args.frames:
        report["error"] = f"timed out after {args.timeout:g}s before {args.frames} flow frame(s) completed"
    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(encoded)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded + "\n")
    return 0 if len(validator.completed) >= args.frames and all(item.valid for item in validator.completed) else 2


if __name__ == "__main__":
    raise SystemExit(main())
