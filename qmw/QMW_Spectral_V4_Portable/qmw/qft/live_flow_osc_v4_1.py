"""Launch QFT V4 unchanged, plus its independent V4.1 flow observer stream."""

from __future__ import annotations

import argparse
import math
import threading
import time

from .flow_observer_v4_1 import (
    FirstMomentFlowObserver,
    FirstMomentFlowPublisher,
    OUTPUT_PORT as FLOW_OUTPUT_PORT,
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="QMW QFT V4 with V4.1 first-moment flow sidecar"
    )
    parser.add_argument("--output-host", default="127.0.0.1")
    parser.add_argument("--output-port", type=int, default=OUTPUT_PORT)
    parser.add_argument("--flow-output-host", default="127.0.0.1")
    parser.add_argument("--flow-output-port", type=int, default=FLOW_OUTPUT_PORT)
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int, default=CONTROL_PORT)
    parser.add_argument("--rate-hz", type=float, default=30.0)
    args = parser.parse_args()
    if not math.isfinite(args.rate_hz) or args.rate_hz <= 0.0:
        parser.error("--rate-hz must be finite and positive")

    from pythonosc.osc_server import ThreadingOSCUDPServer

    engine = LiveScalarFieldEngine(
        LiveScalarFieldParameters(sites=SITES, localized_site=SITES // 2)
    )
    field_publisher = ScalarFieldFramePublisher(
        host=args.output_host, port=args.output_port
    )
    flow_publisher = FirstMomentFlowPublisher(
        host=args.flow_output_host, port=args.flow_output_port
    )
    observer = FirstMomentFlowObserver()
    server = ThreadingOSCUDPServer(
        (args.control_host, args.control_port), _install_controls(engine)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    period = 1.0 / args.rate_hz
    previous = time.monotonic()
    print(
        "QMW QFT V4 + V4.1 first-moment flow: "
        f"field -> {args.output_host}:{args.output_port}; "
        f"flow -> {args.flow_output_host}:{args.flow_output_port}; "
        f"controls <- {args.control_host}:{args.control_port}",
        flush=True,
    )
    try:
        while not engine.should_quit:
            started = time.monotonic()
            dt = started - previous
            previous = started
            frame, parameters = engine.step(dt)
            source_revision = field_publisher.publish(
                frame, parameters, engine.temporal_frame, engine.temporal_config
            )
            model = ScalarFieldModel.from_spec(parameters.field_spec())
            flow_publisher.publish(
                observer.observe(frame, model), source_revision=source_revision
            )
            artifact = engine.consume_performance_artifact()
            if artifact is not None:
                field_publisher.publish_performance_saved(artifact)
            time.sleep(max(0.0, period - (time.monotonic() - started)))
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
