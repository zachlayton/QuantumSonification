"""Command-line probe for AtomicOrbitalFrame V4."""

from __future__ import annotations

import argparse
import json

from .evolution import evolve_state
from .model import AtomicManifoldModel, AtomicManifoldSpec
from .observables import observe_state
from .states import basis_state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=2)
    parser.add_argument("--ell", type=int, default=1)
    parser.add_argument("--m-l", type=int, default=0)
    parser.add_argument("--spin", choices=("up", "down"), default="up")
    parser.add_argument("--time", type=float, default=0.0)
    parser.add_argument("--field", type=float, nargs=3, default=(0.0, 0.0, 0.0))
    parser.add_argument("--spin-orbit", type=float, default=0.0)
    args = parser.parse_args()
    spec = AtomicManifoldSpec(
        n=args.n,
        ell=args.ell,
        magnetic_field=tuple(args.field),
        spin_orbit_strength=args.spin_orbit,
    )
    model = AtomicManifoldModel.from_spec(spec)
    state = evolve_state(basis_state(model, m_l=args.m_l, spin=args.spin), model, args.time)
    print(json.dumps(observe_state(state, model, time=args.time).to_dict(), indent=2))


if __name__ == "__main__":
    main()
