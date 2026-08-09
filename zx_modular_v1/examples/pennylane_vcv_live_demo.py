#!/usr/bin/env python3
"""Stream PennyLane state descriptors to VCV Rack and Max over OSC."""

from __future__ import annotations

import argparse
import json
import math
import time

import pennylane as qml
from pennylane import numpy as pnp

from zx_modular_v1 import pennylane_to_modular
from zx_modular_v1.rack_osc import OSCelotPublisher, rack_frame_from_state
from zx_modular_v1.rewrite_osc import RewriteOSCVerifier


DEVICE = qml.device("default.qubit", wires=2)


def entangled_rotation(theta: float) -> None:
    qml.RY(theta, wires=0)
    qml.CNOT(wires=[0, 1])


@qml.qnode(DEVICE)
def state_circuit(theta: float):
    entangled_rotation(theta)
    return qml.state()


@qml.qnode(DEVICE)
def z0_circuit(theta: float):
    entangled_rotation(theta)
    return qml.expval(qml.Z(0))


def quantum_frame(theta_value: float):
    theta = pnp.array(theta_value, requires_grad=True)
    state = state_circuit(theta)
    gradient = float(qml.grad(z0_circuit)(theta))
    return rack_frame_from_state(
        state,
        phase_radians=float(theta),
        parameter_gradient=gradient,
    ), gradient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theta", type=float, default=math.pi / 3.0)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7000)
    parser.add_argument("--max-host", default="127.0.0.1")
    parser.add_argument("--max-port", type=int, default=7496)
    parser.add_argument("--processing-host", default="127.0.0.1")
    parser.add_argument("--processing-port", type=int, default=7497)
    parser.add_argument(
        "--frames",
        type=int,
        default=1,
        help="Number of frames to compute; 0 streams until Control-C",
    )
    parser.add_argument("--interval", type=float, default=0.05)
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="Advance theta on every frame",
    )
    parser.add_argument("--theta-step", type=float, default=0.025)
    parser.add_argument(
        "--only-control",
        type=int,
        choices=range(1, 7),
        help="Send one control id while teaching an OSCelot mapping",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Send frames to VCV Rack/OSCelot",
    )
    parser.add_argument(
        "--send-max",
        action="store_true",
        help="Send the same frames to the Max monitor",
    )
    parser.add_argument(
        "--send-processing",
        action="store_true",
        help="Send the same frames to the Processing ZX canvas",
    )
    args = parser.parse_args()
    if args.frames < 0:
        parser.error("--frames must be zero or greater")
    if args.interval < 0.0:
        parser.error("--interval must be zero or greater")
    if args.frames == 0 and not (
        args.send or args.send_max or args.send_processing
    ):
        parser.error(
            "--frames 0 requires --send, --send-max, and/or --send-processing"
        )

    frame, gradient = quantum_frame(args.theta)
    topology = pennylane_to_modular(
        entangled_rotation,
        float(args.theta),
        name="pennylane_entangled_rotation",
    )
    selected_controls = (
        None if args.only_control is None else {args.only_control}
    )
    summary = {
        "theta": float(args.theta),
        "gradient_d_z0_d_theta": gradient,
        "zx_semantics_verified": topology.import_report.verified,
        "zx_modules": len(topology.patch_plan.modules),
        "zx_cables": len(topology.patch_plan.cables),
        "rack_target": f"{args.host}:{args.port}",
        "max_target": f"{args.max_host}:{args.max_port}",
        "processing_target": (
            f"{args.processing_host}:{args.processing_port}"
        ),
        "processing_rewrite_verifier": (
            "127.0.0.1:7499" if args.send_processing else None
        ),
        "send_rack": bool(args.send),
        "send_max": bool(args.send_max),
        "send_processing": bool(args.send_processing),
        "frames": args.frames,
        "interval_seconds": args.interval,
        "sweep": bool(args.sweep),
        "theta_step": args.theta_step,
        "only_control": args.only_control,
        "rack_messages": [
            {"address": address, "arguments": arguments}
            for address, arguments in frame.osc_messages(
                prefix="",
                control_ids=selected_controls,
            )
        ],
        "max_messages": [
            {"address": address, "arguments": arguments}
            for address, arguments in frame.osc_messages(
                prefix="/qmw/zx",
                control_ids=selected_controls
            )
        ],
        "metrics": {
            "expectation_z0": frame.expectation_z0,
            "population_entropy": frame.population_entropy,
            "coherence_l1": frame.coherence_l1,
            "dominant_probability": frame.dominant_probability,
        },
    }
    print(json.dumps(summary, indent=2))

    rack_publisher = (
        OSCelotPublisher(args.host, args.port, prefix="")
        if args.send
        else None
    )
    max_publisher = (
        OSCelotPublisher(args.max_host, args.max_port, prefix="/qmw/zx")
        if args.send_max
        else None
    )
    processing_publisher = (
        OSCelotPublisher(
            args.processing_host,
            args.processing_port,
            prefix="/qmw/zx",
        )
        if args.send_processing
        else None
    )
    rewrite_verifier = None
    if args.send_processing:
        rewrite_verifier = RewriteOSCVerifier(
            processing_host=args.processing_host,
            processing_port=args.processing_port,
        )
        rewrite_verifier.start()
    total_frames = math.inf if args.frames == 0 else args.frames
    theta_value = float(args.theta)
    frame_index = 0
    try:
        while frame_index < total_frames:
            if frame_index:
                frame, _ = quantum_frame(theta_value)
            if rack_publisher is not None:
                rack_publisher.publish(frame, control_ids=selected_controls)
            if max_publisher is not None:
                max_publisher.publish(frame, control_ids=selected_controls)
            if processing_publisher is not None:
                processing_publisher.publish(
                    frame,
                    control_ids=selected_controls,
                )
            frame_index += 1
            if args.sweep:
                theta_value += args.theta_step
            if frame_index < total_frames and args.interval:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        if rewrite_verifier is not None:
            rewrite_verifier.stop()
    if args.send or args.send_max or args.send_processing:
        print(f"stream complete: {frame_index} frame(s)")


if __name__ == "__main__":
    main()
