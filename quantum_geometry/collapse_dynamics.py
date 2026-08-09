"""Optional collapse hooks. Disabled configurations are exact no-ops."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class CollapseConfig:
    enabled: bool = False
    model: str = "grw"
    rate: float = 0.0
    width: float = 1.0
    seed: int = 1604


class CollapseDynamics:
    def __init__(self, config: CollapseConfig = CollapseConfig()):
        self.config=config; self.rng=np.random.default_rng(config.seed)
        if config.model not in {"grw","csl"} or config.rate < 0 or config.width <= 0: raise ValueError("invalid collapse configuration")

    def step(self, psi: np.ndarray, positions: np.ndarray, dt: float) -> tuple[np.ndarray, dict | None]:
        psi=np.asarray(psi,dtype=np.complex128); psi/=np.linalg.norm(psi)
        if not self.config.enabled or self.config.rate == 0 or self.rng.random() >= 1-np.exp(-self.config.rate*dt): return psi, None
        p=np.abs(psi)**2; center=int(self.rng.choice(len(psi),p=p/p.sum()))
        envelope=np.exp(-0.25*((np.asarray(positions)-positions[center])/self.config.width)**2)
        out=psi*envelope; out/=np.linalg.norm(out)
        return out, {"model":self.config.model,"center_index":center,"center":float(positions[center])}
