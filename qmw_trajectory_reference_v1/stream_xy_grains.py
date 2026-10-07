"""Run an XY trajectory and optionally publish its grain-control projection."""

from __future__ import annotations

import argparse
import json

from .granular import project_grains
from .osc import OSC_PORT, TrajectoryGrainOSCPublisher
from .xy import run_xy_trajectory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("exact", "qutip"), default="exact")
    parser.add_argument("--samples", type=int, default=2048)
    parser.add_argument("--duration", type=float, default=24.0)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=OSC_PORT)
    parser.add_argument("--publish-hz", type=float, default=60.0)
    parser.add_argument("--speed", type=float, default=8.0, help="simulation seconds per wall-clock second")
    parser.add_argument("--dry-run", action="store_true", help="validate and report without UDP publication")
    arguments = parser.parse_args()
    if arguments.backend == "qutip":
        from .qutip_backend import run_xy_qutip_trajectory
        trajectory = run_xy_qutip_trajectory(samples=arguments.samples, duration=arguments.duration)
    else:
        trajectory = run_xy_trajectory(samples=arguments.samples, duration=arguments.duration)
    controls = project_grains(trajectory)
    report = {
        "backend": trajectory.metadata["backend"],
        "trajectory": trajectory.validate(),
        "controls": controls.validate(),
        "samples": trajectory.samples,
        "duration": trajectory.duration,
        "dry_run": bool(arguments.dry_run),
    }
    if not arguments.dry_run:
        publisher = TrajectoryGrainOSCPublisher.from_udp(
            arguments.host, arguments.port, maximum_hz=arguments.publish_hz,
        )
        try:
            report["osc_messages_sent"] = publisher.publish(trajectory, controls, speed=arguments.speed)
        finally:
            publisher.close()
        report["osc_destination"] = f"{arguments.host}:{arguments.port}"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
