"""Stream a quasiperiodic Bloch clock to Max on UDP 7490.

The clock couples three irrationally related phases.  They drive crystal
momentum and lattice depth, while the lattice eigensystem supplies energy and
the reciprocal-mode spectrum.  This is temporal interference in a single
Bloch state, not a claim of many-particle quantum entanglement.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
import time

import numpy as np
from pythonosc.udp_client import SimpleUDPClient

from .model import BlochLattice1D, BlochState
from .osc_spectral_microscope import state_packet


GOLDEN_RATIO = (1.0 + math.sqrt(5.0)) / 2.0


@dataclass(frozen=True)
class ClockCoordinates:
    q: float
    depth: float
    transport_phase: float
    breath_phase: float
    memory_phase: float


def clock_coordinates(
    elapsed: float,
    period: float = 7.0,
    depth: float = 4.0,
    depth_span: float = 2.0,
    coupling: float = 0.72,
) -> ClockCoordinates:
    """Return the coupled quasiperiodic controls at an elapsed time."""
    if period <= 0.0:
        raise ValueError("period must be positive")
    if depth < 0.0 or depth_span < 0.0:
        raise ValueError("depth and depth-span must be non-negative")

    transport = math.tau * elapsed / period
    breath = transport / math.sqrt(2.0)
    memory = transport / GOLDEN_RATIO

    # Each phase alters another phase rather than acting as an independent LFO.
    nested_phase = transport + coupling * math.sin(
        breath + 0.35 * math.sin(memory)
    )
    q = 0.5 * math.sin(nested_phase)
    breathing = (
        0.62 * math.sin(breath + 0.45 * coupling * math.sin(transport))
        + 0.38 * math.sin(memory - 0.30 * coupling * math.sin(transport))
    )
    instantaneous_depth = max(0.01, depth + depth_span * breathing)
    return ClockCoordinates(q, instantaneous_depth, transport, breath, memory)


def parallel_transport(state: BlochState, previous: np.ndarray | None) -> BlochState:
    """Choose a continuous eigenvector phase relative to the prior frame."""
    coefficients = state.coefficients.copy()
    if previous is not None:
        overlap = np.vdot(previous, coefficients)
        if abs(overlap) > 1e-14:
            coefficients *= np.exp(-1j * np.angle(overlap))
    return BlochState(state.q, state.band, state.energy, coefficients)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7490)
    parser.add_argument("--band", type=int, default=0)
    parser.add_argument("--period", type=float, default=7.0,
                        help="seconds for the fastest clock")
    parser.add_argument("--rate", type=float, default=25.0,
                        help="OSC state updates per second")
    parser.add_argument("--depth", type=float, default=4.0,
                        help="mean lattice depth in recoil units")
    parser.add_argument("--depth-span", type=float, default=2.0,
                        help="quasiperiodic lattice-depth excursion")
    parser.add_argument("--coupling", type=float, default=0.72,
                        help="cross-modulation between the three clocks")
    args = parser.parse_args()
    if args.rate <= 0.0:
        parser.error("--rate must be positive")

    client = SimpleUDPClient(args.host, args.port)
    start = time.monotonic()
    deadline = start
    previous = None
    next_report = start
    frame_duration = 1.0 / args.rate

    print("Temporal entanglement clock: transport : breath : memory = "
          "1 : 1/sqrt(2) : 1/phi")
    print("Press Control-C to stop.")
    try:
        while True:
            now = time.monotonic()
            elapsed = now - start
            clock = clock_coordinates(
                elapsed, args.period, args.depth, args.depth_span, args.coupling
            )
            model = BlochLattice1D(clock.depth, 5)
            state = parallel_transport(model.state(clock.q, args.band), previous)
            previous = state.coefficients
            client.send_message("/qmw/blochband/state", state_packet(state))

            if now >= next_report:
                print(
                    f"t={elapsed:7.2f}s  q={clock.q:+.3f}  "
                    f"V={clock.depth:.3f} E_R  E={state.energy:.4f} E_R"
                )
                next_report = now + 1.0

            deadline += frame_duration
            remaining = deadline - time.monotonic()
            if remaining > 0.0:
                time.sleep(remaining)
            elif remaining < -frame_duration:
                deadline = time.monotonic()
    except KeyboardInterrupt:
        print("\nTemporal entanglement clock stopped.")


if __name__ == "__main__":
    main()
