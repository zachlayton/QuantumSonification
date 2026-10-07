"""Publish the explicit XY pure-dephasing grain-control experiment."""
from __future__ import annotations
import argparse
import json
from .granular import project_grains
from .open_system import run_xy_dephasing_trajectory
from .osc import OSC_PORT, TrajectoryGrainOSCPublisher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--gamma-phi", type=float, default=0.08)
parser.add_argument("--samples", type=int, default=2048)
parser.add_argument("--duration", type=float, default=24.0)
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=OSC_PORT)
parser.add_argument("--publish-hz", type=float, default=60.0)
parser.add_argument("--speed", type=float, default=8.0)
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()
trajectory = run_xy_dephasing_trajectory(gamma_phi=args.gamma_phi, samples=args.samples, duration=args.duration)
controls = project_grains(trajectory)
report = {"gamma_phi": args.gamma_phi, "trajectory": trajectory.validate(), "controls": controls.validate(), "dry_run": args.dry_run}
if not args.dry_run:
    publisher = TrajectoryGrainOSCPublisher.from_udp(args.host, args.port, maximum_hz=args.publish_hz)
    try:
        report["osc_messages_sent"] = publisher.publish(trajectory, controls, speed=args.speed)
    finally:
        publisher.close()
print(json.dumps(report, indent=2, sort_keys=True))
