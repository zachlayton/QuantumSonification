"""Launch V4 plus attached V4.1/V4.2 read-only flow observers."""

from __future__ import annotations

import argparse
import math
import threading
import time

import numpy as np

from density.density_matrix_engine import DensityMatrixEngine as RelationalDensityEngine
from excitation.wavefunction_sources_v1 import create_wavefunction_source
from qmw.qmw_probability_flow import (
    FluxEventState,
    emit_flux_events,
    flow_from_observed_current_1d,
)
from qmw.performance.adapters.qft_v4_2 import SOURCE_DESCRIPTOR, adapt_qft_v4_2
from qmw.performance.osc import PerformanceSnapshotPublisher
from qmw.performance.osc import OUTPUT_PORT as INSPECTOR_OUTPUT_PORT

from .flow_observer_v4_1 import (
    FirstMomentFlowObserver,
    FirstMomentFlowPublisher,
    OUTPUT_PORT as ENERGY_FLOW_OUTPUT_PORT,
)
from .effective_terrain_osc_v4_2 import (
    DensityTerrainObserver,
    EffectiveTerrainPublisher,
)
from .live_osc_v3 import _install_controls
from .live_osc_v4 import (
    CONTROL_PORT,
    OUTPUT_PORT,
    SITES,
    LiveScalarFieldEngine,
    LiveScalarFieldParameters,
    ScalarFieldFramePublisher,
)
from .model import ScalarFieldModel
from .probability_flow_osc_v4_2 import (
    OUTPUT_PORT as PROBABILITY_FLOW_OUTPUT_PORT,
    ProbabilityFlowPublisher,
)


def equal_coordinate_regions(coordinates: np.ndarray, count: int) -> np.ndarray:
    """Partition a 1D provider grid into stable, equal coordinate regions."""

    if count < 1:
        raise ValueError("region count must be positive")
    extent = float(coordinates[-1] - coordinates[0])
    if not math.isfinite(extent) or extent <= 0.0:
        raise ValueError("coordinates must be strictly increasing")
    values = np.floor(((coordinates - coordinates[0]) / extent) * count).astype(int)
    return np.clip(values, 0, count - 1)


def main() -> None:
    from pythonosc.osc_server import ThreadingOSCUDPServer

    parser = argparse.ArgumentParser(
        description="QMW QFT V4 + V4.1 energy flow + V4.2 probability-flow excitation"
    )
    parser.add_argument("--output-host", default="127.0.0.1")
    parser.add_argument("--output-port", type=int, default=OUTPUT_PORT)
    parser.add_argument("--monitor-host", default=None)
    parser.add_argument("--monitor-port", type=int, default=None)
    parser.add_argument("--energy-flow-output-host", default="127.0.0.1")
    parser.add_argument("--energy-flow-output-port", type=int, default=ENERGY_FLOW_OUTPUT_PORT)
    parser.add_argument("--probability-flow-output-host", default="127.0.0.1")
    parser.add_argument("--probability-flow-output-port", type=int, default=PROBABILITY_FLOW_OUTPUT_PORT)
    parser.add_argument("--probability-flow-source", choices=("coherent_state", "barrier_scattering"), default="coherent_state")
    parser.add_argument("--probability-flow-grid", type=int, default=128)
    parser.add_argument("--probability-flow-regions", type=int, default=16)
    parser.add_argument("--probability-flow-event-threshold", type=float, default=0.025)
    parser.add_argument("--terrain-event-threshold", type=float, default=0.005)
    parser.add_argument("--inspector-output-host", default="127.0.0.1")
    parser.add_argument("--inspector-output-port", type=int, default=INSPECTOR_OUTPUT_PORT)
    parser.add_argument("--disable-instrument-inspector", action="store_true")
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=CONTROL_PORT)
    parser.add_argument("--rate-hz", type=float, default=30.0)
    parser.add_argument(
        "--frames",
        type=int,
        default=0,
        help="Stop after this many frames (0 runs until quit).",
    )
    args = parser.parse_args()
    if not math.isfinite(args.rate_hz) or args.rate_hz <= 0.0:
        parser.error("--rate-hz must be finite and positive")
    if args.frames < 0:
        parser.error("--frames must be nonnegative")
    if args.probability_flow_grid < 3:
        parser.error("--probability-flow-grid must be at least 3")
    if args.probability_flow_regions < 1:
        parser.error("--probability-flow-regions must be positive")
    if not math.isfinite(args.probability_flow_event_threshold) or args.probability_flow_event_threshold <= 0.0:
        parser.error("--probability-flow-event-threshold must be finite and positive")
    if not math.isfinite(args.terrain_event_threshold) or args.terrain_event_threshold <= 0.0:
        parser.error("--terrain-event-threshold must be finite and positive")

    engine = LiveScalarFieldEngine(LiveScalarFieldParameters(sites=SITES, localized_site=SITES // 2))
    field_publisher = ScalarFieldFramePublisher(host=args.output_host, port=args.output_port)
    monitor_publisher = (
        ScalarFieldFramePublisher(host=args.monitor_host or "127.0.0.1", port=args.monitor_port)
        if args.monitor_port is not None
        else None
    )
    energy_publisher = FirstMomentFlowPublisher(host=args.energy_flow_output_host, port=args.energy_flow_output_port)
    probability_publisher = ProbabilityFlowPublisher(host=args.probability_flow_output_host, port=args.probability_flow_output_port)
    terrain_publisher = EffectiveTerrainPublisher(
        host=args.probability_flow_output_host,
        port=args.probability_flow_output_port,
    )
    terrain_observer = DensityTerrainObserver(
        terrain_publisher,
        event_threshold=args.terrain_event_threshold,
    )
    inspector_publisher = (
        None
        if args.disable_instrument_inspector
        else PerformanceSnapshotPublisher(
            host=args.inspector_output_host,
            port=args.inspector_output_port,
        )
    )
    density_engine = RelationalDensityEngine()
    energy_observer = FirstMomentFlowObserver()
    excitation = create_wavefunction_source(args.probability_flow_source, grid_shape=args.probability_flow_grid)
    previous_probability_flow = None
    flux_events = FluxEventState()
    server = ThreadingOSCUDPServer((args.control_host, args.control_port), _install_controls(engine))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    period = 1.0 / args.rate_hz
    previous = time.monotonic()
    inspector_status = (
        "inspector disabled; "
        if inspector_publisher is None
        else f"inspector -> {args.inspector_output_host}:{args.inspector_output_port}; "
    )
    launch_summary = (
        "QMW QFT V4 + V4.1 energy flow + V4.2 independent probability-flow excitation: "
        f"field -> {args.output_host}:{args.output_port}; energy -> {args.energy_flow_output_host}:{args.energy_flow_output_port}; "
        f"probability ({args.probability_flow_source}) + density terrain -> "
        f"{args.probability_flow_output_host}:{args.probability_flow_output_port}; "
        + inspector_status
        + f"controls <- {args.control_host}:{args.control_port}"
    )
    print(launch_summary, flush=True)
    try:
        frame_count = 0
        while not engine.should_quit and (
            args.frames == 0 or frame_count < args.frames
        ):
            started = time.monotonic()
            dt = started - previous
            previous = started
            frame, parameters = engine.step(dt)
            source_revision = field_publisher.publish(
                frame, parameters, engine.temporal_frame, engine.temporal_config
            )
            if monitor_publisher is not None:
                monitor_publisher.publish(
                    frame, parameters, engine.temporal_frame, engine.temporal_config
                )
            model = ScalarFieldModel.from_spec(parameters.field_spec())
            energy_flow = energy_observer.observe(frame, model)
            energy_publisher.publish(energy_flow, source_revision=source_revision)
            excitation_frame = excitation.frame(dt)
            regions = equal_coordinate_regions(excitation_frame.coordinates[0], args.probability_flow_regions)
            probability_flow = flow_from_observed_current_1d(
                excitation_frame.probability,
                excitation_frame.phase,
                excitation_frame.probability_current[0],
                excitation_frame.coordinates[0],
                time=excitation_frame.time,
                regions=regions,
                previous=previous_probability_flow,
            )
            probability_flow, flux_events = emit_flux_events(
                probability_flow,
                flux_events,
                dt=dt,
                threshold=args.probability_flow_event_threshold,
            )
            probability_publisher.publish(
                probability_flow,
                source_revision=source_revision,
                provider=args.probability_flow_source,
            )
            previous_probability_flow = probability_flow
            if inspector_publisher is not None:
                try:
                    snapshot = adapt_qft_v4_2(
                        frame,
                        source_revision=source_revision,
                        temporal=engine.temporal_frame,
                        energy_flow=energy_flow,
                        probability_flow=probability_flow,
                    )
                    inspector_publisher.publish(
                        snapshot,
                        logical_audio_lanes=SOURCE_DESCRIPTOR.logical_audio_lanes,
                    )
                except Exception as exc:
                    print(
                        f"instrument inspector disabled after sidecar error: {exc}",
                        flush=True,
                    )
                    inspector_publisher = None
            rho = density_engine.step(dt)
            terrain_observer.observe(
                rho,
                time=frame.time,
                dt=dt,
                source_revision=source_revision,
                provider="density_matrix_engine_v2",
            )
            artifact = engine.consume_performance_artifact()
            if artifact is not None:
                field_publisher.publish_performance_saved(artifact)
            frame_count += 1
            time.sleep(max(0.0, period - (time.monotonic() - started)))
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
