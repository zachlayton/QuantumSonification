#!/usr/bin/env python3
"""Stream an evolving 3D wavefunction as short OSC grain events."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pythonosc.udp_client import SimpleUDPClient

from excitation.wavefunction_sonification_adapter_v1 import (
    WavefunctionGrainConfig,
    WavefunctionSonificationAdapter,
)
from excitation.grw_wavefunction_source_v1 import (
    GRWWavefunctionConfig,
    GRWWavefunctionSource,
)
from excitation.wavefunction_sources_v1 import (
    WAVEFUNCTION_SOURCE_NAMES,
    create_wavefunction_source,
)


def grid_parameters_for_source(source_name: str, grid: int) -> dict[str, int]:
    """Translate one CLI grid control into each source's native topology."""

    if source_name in {"particle_in_box", "quantum_rotor"}:
        return {"n_points": grid}
    if source_name == "spherical_harmonic":
        # Twice as many azimuth samples keeps angular cells approximately
        # balanced over theta in [0, pi] and phi in [0, 2*pi].
        return {"n_theta": grid, "n_phi": 2 * grid}
    return {"grid_shape": grid}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=WAVEFUNCTION_SOURCE_NAMES, default="schrodinger_packet_3d")
    parser.add_argument("--grid", type=int, default=32)
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--grains", type=int, default=16)
    parser.add_argument("--fixed-rate", action="store_true", help="Disable motion-responsive grain density.")
    parser.add_argument(
        "--renderer-poisson",
        action="store_true",
        help="Use synthetic irregular renderer timing (explicitly nonphysical; disabled by default).",
    )
    parser.add_argument("--min-grains", type=int, default=0)
    parser.add_argument("--max-grains", type=int, default=12)
    parser.add_argument("--rate-sensitivity", type=float, default=32.0)
    parser.add_argument("--current-weight", type=float, default=0.25)
    parser.add_argument("--grw", action="store_true", help="Apply genuine Poisson-timed Gaussian localizations directly to psi; emit only at jumps.")
    parser.add_argument("--grw-rate", type=float, default=1.0, help="Single-source GRW jump rate in Hz.")
    parser.add_argument("--grw-width", type=float, default=0.75, help="Gaussian localization width in source coordinate units.")
    parser.add_argument("--grw-constituent-scale", type=float, default=1.0)
    parser.add_argument("--grw-seed", type=int, default=23)
    parser.add_argument("--grw-min-grains", type=int, default=1)
    parser.add_argument("--grw-max-grains", type=int, default=48)
    parser.add_argument("--decay-ms", type=float, default=5.0)
    parser.add_argument("--amplitude", type=float, default=0.32)
    parser.add_argument("--duration", type=float, default=0.0, help="Seconds; zero streams until interrupted.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--max-port",
        type=int,
        default=7480,
        help="Dedicated cloud-grain Max port; 7400 remains reserved for the main/GRW engine.",
    )
    parser.add_argument("--processing-port", type=int, default=7401)
    parser.add_argument("--sc-port", type=int, default=57120)
    args = parser.parse_args()

    if args.fps <= 0.0:
        raise SystemExit("--fps must be positive")
    if args.grid < 8:
        raise SystemExit("--grid must be at least 8")

    source_parameters = grid_parameters_for_source(args.source, args.grid)
    base_source = create_wavefunction_source(args.source, **source_parameters)
    grid_description = "×".join(str(len(axis)) for axis in base_source.coordinates)
    if args.grw:
        try:
            source = GRWWavefunctionSource(
                base_source,
                GRWWavefunctionConfig(
                    rate_hz=args.grw_rate,
                    localization_width=args.grw_width,
                    constituent_scale=args.grw_constituent_scale,
                    seed=args.grw_seed,
                ),
            )
        except TypeError as error:
            raise SystemExit(f"--grw cannot wrap {args.source}: {error}") from error
    else:
        source = base_source
    ports = tuple(dict.fromkeys((args.max_port, args.processing_port, args.sc_port)))
    clients = tuple(SimpleUDPClient(args.host, port) for port in ports)
    adapter = WavefunctionSonificationAdapter(
        clients,
        WavefunctionGrainConfig(
            grains_per_frame=args.grains,
            decay_ms=args.decay_ms,
            amplitude_gain=args.amplitude,
            adaptive_rate=not args.fixed_rate,
            min_grains_per_frame=args.min_grains,
            max_grains_per_frame=args.max_grains,
            density_change_sensitivity=args.rate_sensitivity,
            current_weight=args.current_weight,
        ),
    )

    dt = 1.0 / args.fps
    started = time.monotonic()
    next_frame = started
    print(
        f"Streaming {args.source} grid {grid_description} at {args.fps:g} fps, "
        + (
            f"GRW-triggered {args.grw_min_grains}-{args.grw_max_grains} grains/jump, "
            if args.grw
            else (
                f"adaptive {args.min_grains}-{args.max_grains} grains/frame, "
                if not args.fixed_rate
                else f"fixed {args.grains} grains/frame, "
            )
        )
        + f"{args.decay_ms:g} ms decay "
        f"to ports {', '.join(map(str, ports))}"
    )
    if args.grw:
        print(
            f"GRW jump mode: rate={args.grw_rate * args.grw_constituent_scale:g} Hz, "
            f"width={args.grw_width:g}, seed={args.grw_seed}; silent between jumps"
        )
    try:
        while args.duration <= 0.0 or time.monotonic() - started < args.duration:
            frame_wall_start = time.monotonic()
            frame_logical_start = float(source.logical_time) if args.grw else 0.0
            frame = source.frame(dt)
            if args.grw:
                clouds = []
                for event in source.events:
                    target_wall_time = frame_wall_start + (event.logical_time - frame_logical_start)
                    time.sleep(max(0.0, target_wall_time - time.monotonic()))
                    cloud = adapter.publish_grw_event(
                        event,
                        min_grains=args.grw_min_grains,
                        max_grains=args.grw_max_grains,
                    )
                    clouds.append(cloud)
                    print(
                        f"\njump={event.event_id} t={event.logical_time:.6f} "
                        f"wait={event.waiting_time:.6f}s center={tuple(round(v, 3) for v in event.center)} "
                        f"delta={event.total_variation:.6f} grains={len(cloud.grains)}",
                        flush=True,
                    )
                cloud = clouds[-1] if clouds else None
            else:
                cloud = (
                    adapter.publish_frame_timed(frame, dt)
                    if args.renderer_poisson
                    else adapter.publish_frame(frame)
                )
            if (not args.grw and cloud is not None and cloud.frame_id % max(1, int(args.fps)) == 0):
                print(
                    f"\rframe={cloud.frame_id} t={cloud.time:.3f} "
                    f"norm={cloud.norm:.12f} grains={len(cloud.grains):02d} "
                    f"activity={cloud.activity:.3f} dRho={cloud.density_change:.5f}",
                    end="",
                    flush=True,
                )
            next_frame += dt
            time.sleep(max(0.0, next_frame - time.monotonic()))
    except KeyboardInterrupt:
        pass
    finally:
        print("\nWavefunction cloud stream stopped.")


if __name__ == "__main__":
    main()
