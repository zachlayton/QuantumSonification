"""Emit intrinsic events from a unitary lattice-quench simulation.

A prepared wavepacket is suddenly placed in a fixed periodic potential.  The
Hamiltonian is not modulated after the quench.  Max receives packets only at
novel local maxima of reciprocal-bond probability current and at exceptionally
deep minima of the return probability.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import time

import numpy as np
from pythonosc.udp_client import SimpleUDPClient

from .model import BlochLattice1D


@dataclass(frozen=True)
class QuenchFrame:
    time: float
    coefficients: np.ndarray
    populations: np.ndarray
    phases: np.ndarray
    population_speeds: np.ndarray
    bond_currents: np.ndarray
    activity: float
    signed_current: float
    fidelity: float
    participation: float


class LatticeQuench:
    """Exact unitary evolution under one fixed truncated Bloch Hamiltonian."""

    def __init__(
        self,
        depth_recoil: float = 4.0,
        q: float = 0.18,
        basis_order: int = 5,
        initial_order: int = 0,
        initial_width: float = 1.8,
        initial_position: float = 0.271,
        initial_chirp: float = 0.37,
    ) -> None:
        self.model = BlochLattice1D(depth_recoil, basis_order)
        if not -0.5 <= q <= 0.5:
            raise ValueError("q must lie in [-0.5, 0.5]")
        if not -basis_order <= initial_order <= basis_order:
            raise ValueError("initial order lies outside the reciprocal basis")
        if initial_width < 0.0:
            raise ValueError("initial width must be non-negative")
        self.q = float(q)
        self.hamiltonian = self.model.hamiltonian(q)
        self.energies, self.eigenvectors = np.linalg.eigh(self.hamiltonian)
        relative_orders = self.model.orders - initial_order
        if initial_width == 0.0:
            self.initial = np.zeros(2 * basis_order + 1, dtype=np.complex128)
            self.initial[initial_order + basis_order] = 1.0
        else:
            envelope = np.exp(-0.5 * (relative_orders / initial_width) ** 2)
            displacement = np.exp(-1j * 2.0 * np.pi * initial_position * relative_orders)
            curvature = np.exp(1j * initial_chirp * relative_orders ** 2)
            self.initial = (envelope * displacement * curvature).astype(np.complex128)
            self.initial /= np.linalg.norm(self.initial)
        self.eigen_amplitudes = self.eigenvectors.conj().T @ self.initial
        self.coupling = -float(depth_recoil) / 4.0

    def frame(self, simulation_time: float) -> QuenchFrame:
        phases = np.exp(-1j * self.energies * float(simulation_time))
        coefficients = self.eigenvectors @ (self.eigen_amplitudes * phases)
        populations = np.abs(coefficients) ** 2
        derivative = -1j * (self.hamiltonian @ coefficients)
        population_derivative = 2.0 * np.real(np.conj(coefficients) * derivative)
        bond_currents = 2.0 * self.coupling * np.imag(
            np.conj(coefficients[:-1]) * coefficients[1:]
        )
        activity = float(np.sum(np.abs(bond_currents)))
        signed_current = float(np.sum(bond_currents) / max(activity, 1e-12))
        fidelity = float(abs(np.vdot(self.initial, coefficients)) ** 2)
        participation = float(1.0 / np.sum(populations * populations))
        motion = np.abs(population_derivative)
        motion /= max(float(np.max(motion)), 1e-12)
        return QuenchFrame(
            float(simulation_time),
            coefficients,
            populations,
            np.angle(coefficients),
            motion,
            bond_currents,
            activity,
            signed_current,
            fidelity,
            participation,
        )


def transfer_peak(left: QuenchFrame, center: QuenchFrame, right: QuenchFrame,
                  threshold: float) -> bool:
    return (
        center.activity > threshold
        and center.activity > left.activity
        and center.activity >= right.activity
    )


def departure_minimum(left: QuenchFrame, center: QuenchFrame, right: QuenchFrame,
                      threshold: float) -> bool:
    return (
        center.fidelity < threshold
        and center.fidelity < left.fidelity
        and center.fidelity <= right.fidelity
    )


def state_novelty(populations: np.ndarray,
                  previous_populations: np.ndarray | None) -> float:
    """Hellinger distance from the last sounded reciprocal distribution."""
    if previous_populations is None:
        return 1.0
    return float(np.sqrt(
        0.5 * np.sum(
            (np.sqrt(populations) - np.sqrt(previous_populations)) ** 2
        )
    ))


def event_packet(event_id: int, kind: int, frame: QuenchFrame) -> list[float]:
    """Serialize one event; kind 0 is transfer and kind 1 is departure."""
    if kind == 0:
        amplitude = min(1.0, frame.activity / 0.9)
    else:
        amplitude = min(1.0, (1.0 - frame.fidelity) / 0.45) * 0.82
    packet = [
        float(event_id), float(kind), frame.time, amplitude,
        frame.fidelity, frame.participation, frame.signed_current,
    ]
    packet.extend(float(value) for value in frame.populations)
    packet.extend(float(value) for value in frame.phases)
    packet.extend(float(value) for value in frame.population_speeds)
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7490)
    parser.add_argument("--depth", type=float, default=4.0)
    parser.add_argument("--q", type=float, default=0.18)
    parser.add_argument("--initial-order", type=int, default=0)
    parser.add_argument("--initial-width", type=float, default=1.8)
    parser.add_argument("--initial-position", type=float, default=0.271,
                        help="initial position as a fraction of one lattice cell")
    parser.add_argument("--initial-chirp", type=float, default=0.37)
    parser.add_argument("--sim-rate", type=float, default=0.25,
                        help="recoil-time units advanced per real second")
    parser.add_argument("--sample-rate", type=float, default=120.0,
                        help="internal event-detector samples per real second")
    parser.add_argument("--activity-threshold", type=float, default=0.16)
    parser.add_argument("--novelty-threshold", type=float, default=0.16,
                        help="minimum Hellinger distance from the prior transfer")
    parser.add_argument("--departure-threshold", type=float, default=0.02)
    parser.add_argument("--transfer-gap", type=float, default=0.22,
                        help="minimum simulation-time gap between transfer events")
    parser.add_argument("--departure-gap", type=float, default=1.5,
                        help="minimum simulation-time gap between departure events")
    args = parser.parse_args()
    if args.sim_rate <= 0.0 or args.sample_rate <= 0.0:
        parser.error("--sim-rate and --sample-rate must be positive")

    simulation = LatticeQuench(
        args.depth,
        args.q,
        5,
        args.initial_order,
        args.initial_width,
        args.initial_position,
        args.initial_chirp,
    )
    client = SimpleUDPClient(args.host, args.port)
    real_start = time.monotonic()
    frame_duration = 1.0 / args.sample_rate
    deadline = real_start
    event_id = 0
    last_transfer = -1e12
    last_departure = -1e12
    last_transfer_populations = None
    frames: list[QuenchFrame] = []

    print("Fixed-Hamiltonian lattice quench: no q sweep, no lattice LFO.")
    print("Events: probability-current peaks + return-probability minima.")
    print("Press Control-C to stop.")
    try:
        while True:
            elapsed = time.monotonic() - real_start
            frame = simulation.frame(elapsed * args.sim_rate)
            frames.append(frame)
            if len(frames) >= 3:
                left, center, right = frames[-3:]
                novelty = state_novelty(
                    center.populations, last_transfer_populations
                )
                if (
                    transfer_peak(left, center, right, args.activity_threshold)
                    and center.time - last_transfer >= args.transfer_gap
                    and novelty >= args.novelty_threshold
                ):
                    event_id += 1
                    client.send_message(
                        "/qmw/bloch/event", event_packet(event_id, 0, center)
                    )
                    last_transfer = center.time
                    last_transfer_populations = center.populations.copy()
                    print(
                        f"{event_id:05d} TRANSFER  t={center.time:7.3f}  "
                        f"J={center.activity:.3f}  F={center.fidelity:.3f}  "
                        f"N={center.participation:.2f}  D={novelty:.3f}"
                    )
                if (
                    departure_minimum(left, center, right, args.departure_threshold)
                    and center.time - last_departure >= args.departure_gap
                ):
                    event_id += 1
                    client.send_message(
                        "/qmw/bloch/event", event_packet(event_id, 1, center)
                    )
                    last_departure = center.time
                    print(
                        f"{event_id:05d} DEPARTURE t={center.time:7.3f}  "
                        f"J={center.activity:.3f}  F={center.fidelity:.3f}  "
                        f"N={center.participation:.2f}"
                    )
                if len(frames) > 3:
                    frames.pop(0)

            deadline += frame_duration
            remaining = deadline - time.monotonic()
            if remaining > 0.0:
                time.sleep(remaining)
            elif remaining < -frame_duration:
                deadline = time.monotonic()
    except KeyboardInterrupt:
        print("\nBloch quench event simulation stopped.")


if __name__ == "__main__":
    main()
