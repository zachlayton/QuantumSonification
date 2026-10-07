"""Deterministic parent-level toy kinematics, NOT a collider event generator."""

import math
import random
import platform

from .model import ColliderDataset, ColliderEvent, FourMomentum, Provenance

TOP_MASS_GEV = 172.5  # Toy input parameter, not a fitted/claimed measurement.


def generate_synthetic(count: int = 10_000, seed: int = 1001) -> ColliderDataset:
    if type(count) is not int or count < 0:
        raise ValueError("count must be a nonnegative integer")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    rng = random.Random(seed)  # Never modify the caller's global random state.
    events = []
    for index in range(count):
        # Invented spectrum for navigation coverage. Not a cross section or MC truth.
        mass = 2 * TOP_MASS_GEV - 180.0 * math.log1p(-rng.random())
        energy = mass / 2
        momentum = math.sqrt((energy - TOP_MASS_GEV) * (energy + TOP_MASS_GEV))
        costheta = 2 * rng.random() - 1
        phi = 2 * math.pi * rng.random()
        sintheta = math.sqrt(max(0.0, 1 - costheta * costheta))
        px = momentum * sintheta * math.cos(phi)
        py = momentum * sintheta * math.sin(phi)
        pz = momentum * costheta
        rapidity = 3 * rng.random() - 1.5
        ch, sh = math.cosh(rapidity), math.sinh(rapidity)
        # A common longitudinal Lorentz boost gives lab-like parent momenta.
        top = FourMomentum(energy * ch + pz * sh, px, py, pz * ch + energy * sh)
        antitop = FourMomentum(energy * ch - pz * sh, -px, -py, -pz * ch + energy * sh)
        events.append(ColliderEvent(f"toy-{index:06d}", index, top, antitop))
    provenance = Provenance(
        dataset_id=f"toy-ttbar-v1-seed-{seed}-n-{count}", source_kind="synthetic",
        source_uri="generator://collider_001a/toy-ttbar-v1",
        description="Synthetic top/antitop parent kinematics only. No decays, detector, "
                    "matrix elements, PDFs, or physical cross-section model.",
        selection="No dilepton selection performed; no daughter particles generated. "
                  "Mock input for the planned dileptonic workflow.",
        generator={"name": "toy-ttbar-v1", "seed": seed, "count": count,
                   "python_version": platform.python_version(),
                   "rng": "random.Random / MT19937; 4 uniform draws per event",
                   "top_mass_gev": TOP_MASS_GEV,
                   "mass_model": "2*top_mass + Exponential(scale=180 GeV)",
                   "orientation": "isotropic in pair rest frame",
                   "pair_rapidity": "Uniform(-1.5, 1.5)", "pair_pt_gev": 0,
                   "event_weight": 1.0},
    )
    return ColliderDataset(provenance, tuple(events))
