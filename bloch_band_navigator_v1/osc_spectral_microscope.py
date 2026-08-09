"""Send fixed Bloch spectral specimens to Max on UDP 7490."""

from __future__ import annotations
import argparse
import time
from pythonosc.udp_client import SimpleUDPClient
from .model import BlochLattice1D, BlochState

DEFAULT_STATIONS = (-0.5, -0.25, 0.0, 0.25, 0.5)


def state_packet(state: BlochState) -> list[float]:
    packet = [float(state.q), float(state.energy)]
    for coefficient in state.coefficients:
        packet.extend((float(coefficient.real), float(coefficient.imag)))
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7490)
    parser.add_argument("--depth", type=float, default=4.0)
    parser.add_argument("--band", type=int, default=0)
    parser.add_argument("--hold", type=float, default=4.0)
    parser.add_argument("--q", type=float)
    repetition = parser.add_mutually_exclusive_group()
    repetition.add_argument(
        "--repeat",
        dest="repeat",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    repetition.add_argument(
        "--once",
        dest="repeat",
        action="store_false",
        help="play one traversal of the five q stations, then stop",
    )
    parser.set_defaults(repeat=True)
    args = parser.parse_args()
    model = BlochLattice1D(args.depth, 5)
    client = SimpleUDPClient(args.host, args.port)
    stations = (args.q,) if args.q is not None else DEFAULT_STATIONS
    try:
        while True:
            for q in stations:
                if not -0.5 <= q <= 0.5:
                    raise ValueError("q must lie in [-0.5, 0.5]")
                state = model.state(q, args.band)
                client.send_message("/qmw/blochband/state", state_packet(state))
                print(f"q={q:+.3f}  band={args.band}  E={state.energy:.6f} E_R")
                if len(stations) > 1 or args.repeat:
                    time.sleep(max(args.hold, 0.0))
            if not args.repeat:
                break
    except KeyboardInterrupt:
        print("\nBloch spectral microscope stopped.")


if __name__ == "__main__":
    main()
