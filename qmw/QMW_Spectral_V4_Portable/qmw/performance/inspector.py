"""Read-only graphical or terminal inspector for performance snapshots."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import math
from typing import Any, Callable

from .osc import OSC_ROOT, OUTPUT_PORT, SCHEMA
from .gauge_phase_osc import OSC_ROOT_GAUGE_PHASE, SCHEMA as GAUGE_PHASE_SCHEMA
from .gauge_phase_view import GaugePerformerPhaseView, GaugePhaseEdgeView


@dataclass(frozen=True)
class InspectorEvent:
    event_id: str
    event_type: str
    logical_time: float
    time_domain: str
    lane: int | None
    authority: str


@dataclass(frozen=True)
class InspectorFrame:
    source_revision: int
    source_id: str
    logical_time: float
    state_kind: str
    native_schema: str
    time_domain: str
    authority: str
    confidence: float
    complete: bool
    basis_name: str
    basis_shape: tuple[int, ...]
    basis_semantics: str
    basis_ordering: str
    capabilities: tuple[str, ...]
    observers: tuple[tuple[str, str, str, int | None], ...]
    logical_audio_lanes: int
    mean_phi: tuple[float, ...]
    mean_pi: tuple[float, ...]
    local_energy: tuple[float, ...]
    occupations: tuple[float, ...]
    mode_frequencies: tuple[float, ...]
    events: tuple[InspectorEvent, ...]
    gauge_phase: GaugePerformerPhaseView | None = None
    density_populations: tuple[float, ...] = ()
    density_purity: float | None = None
    density_coherence_l1: float | None = None
    hilbert_in_phase: tuple[float, ...] = ()
    hilbert_quadrature: tuple[float, ...] = ()


class InstrumentInspectorModel:
    """Assemble and validate one atomic inspector frame at a time."""

    def __init__(self, on_commit: Callable[[InspectorFrame], None] | None = None) -> None:
        self.on_commit = on_commit
        self.latest: InspectorFrame | None = None
        self.rejected_frames = 0
        self._pending: dict[str, Any] | None = None
        self._pending_gauge: dict[str, Any] | None = None
        self._gauge_by_revision: dict[int, GaugePerformerPhaseView] = {}

    def accept(self, address: str, *arguments: Any) -> None:
        suffix = address.removeprefix(f"{OSC_ROOT}/")
        handler_name = suffix.replace("/", "_").replace("-", "_")
        handler = getattr(self, f"_accept_{handler_name}", None)
        if handler is not None:
            handler(*arguments)

    def _matches(self, revision: Any) -> bool:
        return self._pending is not None and int(revision) == self._pending["revision"]

    def _accept_snapshot_begin(
        self,
        revision: Any,
        source_id: Any,
        logical_time: Any,
        schema: Any,
        observer_count: Any,
        event_count: Any,
        capability_count: Any,
        lanes: Any,
    ) -> None:
        if str(schema) != SCHEMA:
            self.rejected_frames += 1
            self._pending = None
            return
        self._pending = {
            "revision": int(revision),
            "source_id": str(source_id),
            "logical_time": float(logical_time),
            "observer_count": int(observer_count),
            "event_count": int(event_count),
            "capability_count": int(capability_count),
            "lanes": int(lanes),
            "observers": [],
            "events": [],
        }

    def _accept_state(self, revision: Any, *values: Any) -> None:
        if self._matches(revision) and len(values) == 6:
            self._pending["state"] = values

    def _accept_basis(self, revision: Any, *values: Any) -> None:
        if self._matches(revision) and len(values) == 4:
            self._pending["basis"] = values

    def _accept_capabilities(self, revision: Any, *values: Any) -> None:
        if self._matches(revision):
            self._pending["capabilities"] = tuple(str(value) for value in values)

    def _accept_observer(self, revision: Any, *values: Any) -> None:
        if self._matches(revision) and len(values) == 4:
            self._pending["observers"].append(values)

    def _accept_audio_lanes(self, revision: Any, lanes: Any) -> None:
        if self._matches(revision):
            self._pending["audio_lanes"] = int(lanes)

    def _accept_scalar_site_phi(self, revision: Any, *values: Any) -> None:
        self._accept_scalar_channel("phi", revision, values)

    def _accept_scalar_site_pi(self, revision: Any, *values: Any) -> None:
        self._accept_scalar_channel("pi", revision, values)

    def _accept_scalar_site_energy(self, revision: Any, *values: Any) -> None:
        self._accept_scalar_channel("energy", revision, values)

    def _accept_scalar_mode_occupations(self, revision: Any, *values: Any) -> None:
        self._accept_scalar_channel("occupations", revision, values)

    def _accept_scalar_mode_frequencies(self, revision: Any, *values: Any) -> None:
        self._accept_scalar_channel("mode_frequencies", revision, values)

    def _accept_density_populations(self, revision: Any, *values: Any) -> None:
        self._accept_scalar_channel("density_populations", revision, values)

    def _accept_density_metrics(self, revision: Any, *values: Any) -> None:
        if self._matches(revision) and len(values) == 2:
            try:
                metrics = tuple(float(value) for value in values)
            except (TypeError, ValueError):
                self.rejected_frames += 1
                return
            if all(math.isfinite(value) for value in metrics):
                self._pending["density_metrics"] = metrics

    def _accept_hilbert_in_phase(self, revision: Any, *values: Any) -> None:
        self._accept_scalar_channel("hilbert_in_phase", revision, values)

    def _accept_hilbert_quadrature(self, revision: Any, *values: Any) -> None:
        self._accept_scalar_channel("hilbert_quadrature", revision, values)

    def _accept_scalar_channel(
        self, name: str, revision: Any, values: tuple[Any, ...]
    ) -> None:
        if self._matches(revision):
            self._pending[name] = tuple(float(value) for value in values)

    def _accept_event(self, revision: Any, *values: Any) -> None:
        if self._matches(revision) and len(values) == 6:
            self._pending["events"].append(values)

    def _accept_snapshot_end(self, revision: Any, event_count: Any) -> None:
        if not self._matches(revision):
            return
        pending = self._pending
        self._pending = None
        required = {"state", "basis", "capabilities", "audio_lanes"}
        lanes = pending["lanes"]
        state_kind = str(pending.get("state", ("",))[0])
        if state_kind == "ScalarField":
            required.update(
                {"phi", "pi", "energy", "occupations", "mode_frequencies"}
            )
        elif state_kind == "DensityState":
            required.update({"density_populations", "density_metrics"})
        elif state_kind == "HilbertIQ":
            required.update({"hilbert_in_phase", "hilbert_quadrature"})
        complete = required.issubset(pending)
        complete = complete and pending["audio_lanes"] == lanes
        complete = complete and len(pending["capabilities"]) == pending["capability_count"]
        complete = complete and len(pending["observers"]) == pending["observer_count"]
        complete = complete and len(pending["events"]) == pending["event_count"]
        complete = complete and int(event_count) == pending["event_count"]
        for channel in ("phi", "pi", "energy", "occupations", "mode_frequencies"):
            if state_kind == "ScalarField":
                complete = complete and len(pending.get(channel, ())) == lanes
        if state_kind == "DensityState":
            complete = complete and len(pending.get("density_populations", ())) == lanes
            complete = complete and len(pending.get("density_metrics", ())) == 2
        if state_kind == "HilbertIQ":
            complete = complete and len(pending.get("hilbert_in_phase", ())) == lanes
            complete = complete and len(pending.get("hilbert_quadrature", ())) == lanes
        if not complete:
            self.rejected_frames += 1
            return

        state = pending["state"]
        basis = pending["basis"]
        shape = tuple(int(value) for value in str(basis[1]).split(",") if value)
        observers = tuple(
            (
                str(value[0]),
                str(value[1]),
                str(value[2]),
                None if int(value[3]) < 0 else int(value[3]),
            )
            for value in pending["observers"]
        )
        events = tuple(
            InspectorEvent(
                event_id=str(value[0]),
                event_type=str(value[1]),
                logical_time=float(value[2]),
                time_domain=str(value[3]),
                lane=None if int(value[4]) < 0 else int(value[4]),
                authority=str(value[5]),
            )
            for value in pending["events"]
        )
        frame = InspectorFrame(
            source_revision=pending["revision"],
            source_id=pending["source_id"],
            logical_time=pending["logical_time"],
            state_kind=str(state[0]),
            native_schema=str(state[1]),
            time_domain=str(state[2]),
            authority=str(state[3]),
            confidence=float(state[4]),
            complete=bool(int(state[5])),
            basis_name=str(basis[0]),
            basis_shape=shape,
            basis_semantics=str(basis[2]),
            basis_ordering=str(basis[3]),
            capabilities=tuple(pending["capabilities"]),
            observers=observers,
            logical_audio_lanes=lanes,
            mean_phi=tuple(pending.get("phi", ())),
            mean_pi=tuple(pending.get("pi", ())),
            local_energy=tuple(pending.get("energy", ())),
            occupations=tuple(pending.get("occupations", ())),
            mode_frequencies=tuple(pending.get("mode_frequencies", ())),
            events=events,
            gauge_phase=self._gauge_by_revision.get(pending["revision"]),
            density_populations=tuple(pending.get("density_populations", ())),
            density_purity=(None if "density_metrics" not in pending else pending["density_metrics"][0]),
            density_coherence_l1=(None if "density_metrics" not in pending else pending["density_metrics"][1]),
            hilbert_in_phase=tuple(pending.get("hilbert_in_phase", ())),
            hilbert_quadrature=tuple(pending.get("hilbert_quadrature", ())),
        )
        self.latest = frame
        if self.on_commit is not None:
            self.on_commit(frame)

    def _accept_gauge_phase_begin(
        self, revision: Any, logical_time: Any, schema: Any, node_count: Any, edge_count: Any, face_count: Any,
    ) -> None:
        if str(schema) != GAUGE_PHASE_SCHEMA:
            self.rejected_frames += 1
            self._pending_gauge = None
            return
        try:
            pending = {
                "revision": int(revision), "time": float(logical_time), "node_count": int(node_count),
                "edge_count": int(edge_count), "face_count": int(face_count), "nodes": None, "edges": [], "faces": {},
            }
        except (TypeError, ValueError):
            self.rejected_frames += 1
            self._pending_gauge = None
            return
        if pending["revision"] < 0 or not math.isfinite(pending["time"]) or min(pending["node_count"], pending["edge_count"], pending["face_count"]) < 0:
            self.rejected_frames += 1
            self._pending_gauge = None
            return
        self._pending_gauge = pending

    def _gauge_matches(self, revision: Any) -> bool:
        return self._pending_gauge is not None and int(revision) == self._pending_gauge["revision"]

    def _accept_gauge_phase_nodes(self, revision: Any, *values: Any) -> None:
        if self._gauge_matches(revision) and len(values) == self._pending_gauge["node_count"]:
            try:
                nodes = tuple(float(value) for value in values)
            except (TypeError, ValueError):
                self._pending_gauge = None
                self.rejected_frames += 1
                return
            if all(math.isfinite(value) for value in nodes):
                self._pending_gauge["nodes"] = nodes

    def _accept_gauge_phase_edge(self, revision: Any, *values: Any) -> None:
        if self._gauge_matches(revision) and len(values) == 6:
            try:
                source, destination = int(values[0]), int(values[1])
                numbers = tuple(float(value) for value in values[2:])
            except (TypeError, ValueError):
                self._pending_gauge = None
                self.rejected_frames += 1
                return
            if source < 0 or destination < 0 or source == destination or not all(math.isfinite(value) for value in numbers):
                self._pending_gauge = None
                self.rejected_frames += 1
                return
            self._pending_gauge["edges"].append(GaugePhaseEdgeView(source, destination, *numbers))

    def _accept_gauge_phase_face(self, revision: Any, *values: Any) -> None:
        if self._gauge_matches(revision) and len(values) == 2:
            try:
                name, holonomy = str(values[0]), float(values[1])
            except (TypeError, ValueError):
                self._pending_gauge = None
                self.rejected_frames += 1
                return
            if name and math.isfinite(holonomy) and name not in self._pending_gauge["faces"]:
                self._pending_gauge["faces"][name] = holonomy

    def _accept_gauge_phase_end(self, revision: Any) -> None:
        if not self._gauge_matches(revision):
            return
        pending = self._pending_gauge
        self._pending_gauge = None
        if pending["nodes"] is None or len(pending["edges"]) != pending["edge_count"] or len(pending["faces"]) != pending["face_count"]:
            self.rejected_frames += 1
            return
        if any(edge.source >= pending["node_count"] or edge.destination >= pending["node_count"] for edge in pending["edges"]):
            self.rejected_frames += 1
            return
        view = GaugePerformerPhaseView(
            time=pending["time"], node_raw_phase=pending["nodes"], edges=tuple(pending["edges"]),
            face_holonomies=dict(pending["faces"]),
        )
        self._gauge_by_revision[pending["revision"]] = view
        if len(self._gauge_by_revision) > 64:
            del self._gauge_by_revision[min(self._gauge_by_revision)]
        if self.latest is not None and self.latest.source_revision == pending["revision"]:
            self.latest = replace(self.latest, gauge_phase=view)
            if self.on_commit is not None:
                self.on_commit(self.latest)


def _relative_bar(value: float, minimum: float, maximum: float, width: int = 18) -> str:
    span = maximum - minimum
    fraction = 0.0 if span <= 0.0 else min(max((value - minimum) / span, 0.0), 1.0)
    count = int(round(width * fraction))
    return "█" * count + "·" * (width - count)


def render_inspector(frame: InspectorFrame) -> str:
    """Render one committed frame without claiming control over its source."""

    timing = sorted(
        capability.removeprefix("timing.")
        for capability in frame.capabilities
        if capability.startswith("timing.")
    )
    available_observers = sorted(
        capability.removeprefix("observer.")
        for capability in frame.capabilities
        if capability.startswith("observer.")
    )
    attached = {observer[0] for observer in frame.observers}
    lines = [
        "QMW UNIFIED QUANTUM INSTRUMENT — READ-ONLY INSPECTOR",
        f"SOURCE  {frame.source_id}    REV {frame.source_revision}    t={frame.logical_time:.5f}",
        f"STATE   {frame.state_kind} / {frame.authority}    schema={frame.native_schema}",
        f"TIME    {frame.time_domain}",
        f"BASIS   {frame.basis_name} {frame.basis_shape} — {frame.basis_semantics}",
        "TIMING  available: " + (", ".join(timing) if timing else "none declared"),
        "OBSERVERS  "
        + ", ".join(
            f"{name}:{'LIVE' if name in attached else 'available'}"
            for name in available_observers
        ),
        f"AUDIO   {frame.logical_audio_lanes} logical lanes (physical routing is separately protected)",
        "",
        "SITE LANES — bar is relative to this frame; energy value is raw",
        "SITE     RELATIVE ENERGY       LOCAL E         PHI          PI",
    ]
    if len(frame.local_energy) == frame.logical_audio_lanes:
        minimum = min(frame.local_energy, default=0.0)
        maximum = max(frame.local_energy, default=0.0)
        if not math.isfinite(minimum) or not math.isfinite(maximum):
            minimum = 0.0
            maximum = 0.0
        for lane in range(frame.logical_audio_lanes):
            energy = frame.local_energy[lane]
            lines.append(
                f"{lane:02d}  {_relative_bar(energy, minimum, maximum)}  "
                f"{energy:9.4g}  {frame.mean_phi[lane]:9.4g}  "
                f"{frame.mean_pi[lane]:9.4g}"
            )
    else:
        lines.append(f"No ScalarField lane readings for {frame.state_kind}.")
    if "view.density_population" in frame.capabilities and len(frame.density_populations) == frame.logical_audio_lanes:
        lines.extend(("", "DENSITY POPULATIONS — computational basis"))
        for lane, population in enumerate(frame.density_populations):
            lines.append(f"{lane:02d}  {population:9.5g}")
        lines.append(
            f"PURITY {frame.density_purity:.6g}   OFF-DIAGONAL L1 COHERENCE {frame.density_coherence_l1:.6g}"
        )
    if "view.hilbert_iq" in frame.capabilities and len(frame.hilbert_in_phase) == frame.logical_audio_lanes:
        lines.extend(("", "HILBERT I/Q — explicit quadrature observation"))
        for lane, (in_phase, quadrature) in enumerate(zip(frame.hilbert_in_phase, frame.hilbert_quadrature)):
            lines.append(f"{lane:02d}  I {in_phase:+9.5g}  Q {quadrature:+9.5g}")
    if len(frame.occupations) == frame.logical_audio_lanes:
        lines.extend(("", "NORMAL MODES — real-Fourier basis, not site lanes"))
        lines.append("MODE       FREQUENCY     OCCUPATION")
        for mode, (frequency, occupation) in enumerate(
            zip(frame.mode_frequencies, frame.occupations)
        ):
            lines.append(f"{mode:02d}         {frequency:9.4g}      {occupation:9.4g}")
    lines.extend(("", f"EVENTS  {len(frame.events)} in this source revision"))
    for event in frame.events[-8:]:
        lane = "global" if event.lane is None else f"lane {event.lane:02d}"
        lines.append(
            f"  {event.event_type}  {lane}  t={event.logical_time:.5g} "
            f"[{event.time_domain}]"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="QMW Unified Quantum Instrument inspector")
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, default=OUTPUT_PORT)
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="Use the legacy terminal table instead of the graphical oscilloscope.",
    )
    parser.add_argument(
        "--history-frames",
        type=int,
        default=360,
        help="Number of committed frames retained by the graphical scope.",
    )
    parser.add_argument("--no-clear", action="store_true")
    args = parser.parse_args()

    if not args.terminal:
        from .oscilloscope import run_graphical_inspector

        run_graphical_inspector(
            args.listen_host,
            args.listen_port,
            history_frames=args.history_frames,
        )
        return

    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import BlockingOSCUDPServer

    def display(frame: InspectorFrame) -> None:
        prefix = "" if args.no_clear else "\033[2J\033[H"
        print(prefix + render_inspector(frame), flush=True)

    model = InstrumentInspectorModel(on_commit=display)
    dispatcher = Dispatcher()
    dispatcher.map(f"{OSC_ROOT}/*", lambda address, *values: model.accept(address, *values))
    dispatcher.map(f"{OSC_ROOT}/*/*", lambda address, *values: model.accept(address, *values))
    server = BlockingOSCUDPServer((args.listen_host, args.listen_port), dispatcher)
    print(
        f"QMW Instrument Inspector listening on {args.listen_host}:{args.listen_port}",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()


__all__ = [
    "InspectorEvent",
    "InspectorFrame",
    "InstrumentInspectorModel",
    "render_inspector",
]
