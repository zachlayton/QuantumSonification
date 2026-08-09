"""Bell--CHSH validation for discrete Bohm--Bell guidance.

This is a two-qubit experiment (the unused qubits of the four-qubit engine are
spectators).  Measurement settings are unfolded into short unitary segments;
the actual configuration always remains a computational-Z beable.

``grw_visibility`` is an accelerated finite-dimensional localization analogue:
it damps the Bell state's off-diagonal terms in the Z beable basis.  It is not
presented as a prediction at physical GRW parameters.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
import json
import math
from typing import Dict, Iterable, Tuple

import numpy as np

from .four_qubit_configuration_guidance_v1 import ConfigurationEnsemble, evolve_ensemble

I2 = np.eye(2, dtype=np.complex128)
Y = np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128)

SETTINGS = {
    "A0": 0.0,             # Z
    "A1": math.pi / 2.0,   # X
    "B0": math.pi / 4.0,   # (Z + X) / sqrt(2)
    "B1": -math.pi / 4.0,  # (Z - X) / sqrt(2)
}


def bell_density(grw_visibility: float = 1.0) -> np.ndarray:
    """Return Phi+ after Z-basis localization/dephasing of its coherence."""
    if not 0.0 <= grw_visibility <= 1.0:
        raise ValueError("grw_visibility must lie in [0, 1]")
    rho = np.zeros((4, 4), dtype=np.complex128)
    rho[0, 0] = rho[3, 3] = 0.5
    rho[0, 3] = rho[3, 0] = 0.5 * grw_visibility
    return rho


def measurement_generator(theta_a: float, theta_b: float) -> np.ndarray:
    """Generator whose unit-duration evolution rotates both settings to Z."""
    return -0.5 * (theta_a * np.kron(Y, I2) + theta_b * np.kron(I2, Y))


def outcomes_from_configurations(configurations: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Map |q0 q1> configuration indices to +/-1 Z outcomes."""
    a = 1 - 2 * ((configurations >> 1) & 1)
    b = 1 - 2 * (configurations & 1)
    return a.astype(float), b.astype(float)


@dataclass(frozen=True)
class PairStatistics:
    correlation: float
    mean_a: float
    mean_b: float
    trials: int


@dataclass(frozen=True)
class CHSHResult:
    s: float
    quantum_target: float
    grw_visibility: float
    pairs: Dict[str, PairStatistics]
    max_no_signaling_error: float
    beable_basis: str = "computational_z"

    def to_dict(self) -> dict:
        return asdict(self)


def run_pair(
    setting_a: str,
    setting_b: str,
    *,
    trials: int,
    microsteps: int,
    seed: int,
    grw_visibility: float,
) -> PairStatistics:
    rho = bell_density(grw_visibility)
    ensemble = ConfigurationEnsemble.from_rho(rho, trials, seed=seed)
    generator = measurement_generator(SETTINGS[setting_a], SETTINGS[setting_b])
    evolve_ensemble(rho, generator, ensemble, duration=1.0, microsteps=microsteps)
    a, b = outcomes_from_configurations(ensemble.configurations)
    return PairStatistics(
        correlation=float(np.mean(a * b)),
        mean_a=float(np.mean(a)),
        mean_b=float(np.mean(b)),
        trials=trials,
    )


def run_chsh(
    *,
    trials_per_pair: int = 20_000,
    microsteps: int = 128,
    seed: int = 2026,
    grw_visibility: float = 1.0,
) -> CHSHResult:
    pairs: Dict[str, PairStatistics] = {}
    pair_names: Iterable[Tuple[str, str]] = (
        ("A0", "B0"),
        ("A0", "B1"),
        ("A1", "B0"),
        ("A1", "B1"),
    )
    for index, (a_name, b_name) in enumerate(pair_names):
        pairs[f"{a_name}{b_name}"] = run_pair(
            a_name,
            b_name,
            trials=trials_per_pair,
            microsteps=microsteps,
            seed=seed + index,
            grw_visibility=grw_visibility,
        )

    s = (
        pairs["A0B0"].correlation
        + pairs["A0B1"].correlation
        + pairs["A1B0"].correlation
        - pairs["A1B1"].correlation
    )
    no_signaling_differences = (
        abs(pairs["A0B0"].mean_a - pairs["A0B1"].mean_a),
        abs(pairs["A1B0"].mean_a - pairs["A1B1"].mean_a),
        abs(pairs["A0B0"].mean_b - pairs["A1B0"].mean_b),
        abs(pairs["A0B1"].mean_b - pairs["A1B1"].mean_b),
    )
    # Z correlations survive localization; X correlations retain visibility.
    target = math.sqrt(2.0) * (1.0 + grw_visibility)
    return CHSHResult(
        s=float(s),
        quantum_target=target,
        grw_visibility=grw_visibility,
        pairs=pairs,
        max_no_signaling_error=max(no_signaling_differences),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=20_000, help="trials per setting pair")
    parser.add_argument("--microsteps", type=int, default=128)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--grw-visibility", type=float, default=1.0)
    args = parser.parse_args()
    result = run_chsh(
        trials_per_pair=args.trials,
        microsteps=args.microsteps,
        seed=args.seed,
        grw_visibility=args.grw_visibility,
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
