"""Live, read-only OSC publication of a 2-D GPE phase-collision field."""

from __future__ import annotations

import argparse
import signal
import time

import numpy as np

from qmw.gpe.live_observables import GPELiveObservablePublisher
from qmw.osc.gpe_osc import GPEOSCAdapter
from qmw.qmw_gpe import GPEConfig, GPEEngine


def _normalise(psi: np.ndarray, spacing: float) -> np.ndarray:
    return psi / np.sqrt(np.sum(np.abs(psi) ** 2) * spacing * spacing)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=17864, help="observable OSC receiver port")
    parser.add_argument("--rate", type=float, default=30.0, help="simulation/publication rate in Hz")
    parser.add_argument("--phase", type=float, default=0.0, help="relative phase of the right packet in radians")
    parser.add_argument("--interaction", type=float, default=0.3, help="dimensionless GPE interaction g")
    args = parser.parse_args()
    if args.rate <= 0.0:
        raise ValueError("--rate must be positive.")

    size, spacing = 64, 0.2
    axis = (np.arange(size) - size // 2) * spacing
    X, Y = np.meshgrid(axis, axis, indexing="ij")
    left = np.exp(-((X + 2.0) ** 2 + Y ** 2) / 0.9)
    right = np.exp(-((X - 2.0) ** 2 + Y ** 2) / 0.9)
    psi = _normalise(left + np.exp(1j * args.phase) * right, spacing)
    engine = GPEEngine(psi.shape, spacing=spacing, config=GPEConfig(interaction_strength=args.interaction, max_substep=1.0 / 240.0))
    engine.set_wavefunction(psi)
    # The standalone SuperCollider instrument has sixteen resonators; publish
    # all sixteen analysis modes rather than leaving its upper partials idle.
    publisher = GPELiveObservablePublisher(axis, axis, GPEOSCAdapter.from_udp(args.host, args.port), mode_count=16)
    running = True

    def stop(*_: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    period = 1.0 / args.rate
    print(f"QMW GPE live publisher: {args.host}:{args.port}, rate={args.rate:g} Hz; Ctrl-C to stop.")
    while running:
        started = time.monotonic()
        state = engine.step(period)
        publisher.publish(state)
        time.sleep(max(0.0, period - (time.monotonic() - started)))


if __name__ == "__main__":
    main()
