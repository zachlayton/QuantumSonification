"""Controlled scientific scenes for isolating QMW metric-field causes."""

from __future__ import annotations

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Mapping

import numpy as np
from numpy.typing import NDArray

from .config import PotentialConfig, QuantumMetricConfig
from .engine import QuantumMetricEngine
from .frames import QMWMetricFrame
from .grid import Grid2D, RealArray
from .quantum_projector import localized_gaussian_basis, validate_density_matrix

ComplexArray = NDArray[np.complex128]


def _readonly(value: np.ndarray, dtype: np.dtype) -> np.ndarray:
    result = np.asarray(value, dtype=dtype).copy()
    result.setflags(write=False)
    return result


def coherence_l1(rho: ComplexArray) -> float:
    """Entrywise off-diagonal l1 coherence in the declared projection basis."""
    value = np.asarray(rho, dtype=np.complex128)
    return float(np.sum(np.abs(value - np.diag(np.diag(value)))))


def completely_dephase(rho: ComplexArray) -> ComplexArray:
    """Apply complete dephasing in the current projection-basis coordinates."""
    value = np.asarray(rho, dtype=np.complex128)
    result = np.diag(np.diag(value)).astype(np.complex128)
    return result


@dataclass(frozen=True)
class ScientificScene:
    name: str
    controlled_change: str
    rho: ComplexArray
    populations: RealArray
    coherence_l1: float
    purity: float
    potential_coupling: float
    frame: QMWMetricFrame

    def __post_init__(self) -> None:
        dimension = self.rho.shape[0]
        state = validate_density_matrix(self.rho, dimension)
        populations = np.real(np.diag(state))
        if not np.allclose(populations, self.populations):
            raise ValueError("scene populations do not match rho")
        if not np.isclose(self.coherence_l1, coherence_l1(state)):
            raise ValueError("scene coherence diagnostic does not match rho")
        if not np.isclose(self.purity, np.trace(state @ state).real):
            raise ValueError("scene purity diagnostic does not match rho")
        object.__setattr__(self, "rho", _readonly(state, np.complex128))
        object.__setattr__(self, "populations", _readonly(populations, np.float64))


@dataclass(frozen=True)
class ControlledScientificScenes:
    flat: ScientificScene
    one_well: ScientificScene
    coherent: ScientificScene
    decohered: ScientificScene
    diagnostics: Mapping[str, float]

    def __post_init__(self) -> None:
        object.__setattr__(self, "diagnostics", MappingProxyType(dict(self.diagnostics)))

    def ordered(self) -> tuple[ScientificScene, ...]:
        return (self.flat, self.one_well, self.coherent, self.decohered)


def _make_scene(
    name: str,
    controlled_change: str,
    rho: ComplexArray,
    engine: QuantumMetricEngine,
    source_revision: int,
    time: float,
) -> ScientificScene:
    engine.update_quantum_frame(
        rho, time=time, force_modes=True, source_revision=source_revision
    )
    state = np.asarray(rho, dtype=np.complex128)
    return ScientificScene(
        name=name,
        controlled_change=controlled_change,
        rho=state,
        populations=np.real(np.diag(state)),
        coherence_l1=coherence_l1(state),
        purity=float(np.trace(state @ state).real),
        potential_coupling=engine.config.potential.coupling,
        frame=engine.system_frame,
    )


def build_controlled_scientific_scenes(
    config: QuantumMetricConfig | None = None,
) -> ControlledScientificScenes:
    """Build four scenes with one declared causal change per comparison.

    ``flat -> one_well`` changes only Poisson coupling. ``coherent ->
    decohered`` changes only off-diagonal entries through complete dephasing in
    the declared localized-Gaussian projection basis.
    """
    base = QuantumMetricConfig() if config is None else config
    if base.quantum_dimension != 16:
        raise ValueError("controlled scenes require the four-qubit dimension 16")
    if base.potential.coupling <= 0.0:
        raise ValueError("non-flat controlled scenes require positive potential coupling")
    grid = Grid2D.periodic(base.grid_size, base.extent)
    basis = localized_gaussian_basis(grid, base.quantum_dimension)

    localized = np.zeros((16, 16), dtype=np.complex128)
    localized[5, 5] = 1.0

    amplitudes = np.zeros(16, dtype=np.complex128)
    amplitudes[[5, 6, 9, 10]] = np.array((1.0, 0.85, -0.70, 0.55))
    amplitudes /= np.linalg.norm(amplitudes)
    coherent = np.outer(amplitudes, amplitudes.conj())
    decohered = completely_dephase(coherent)

    flat_config = replace(
        base,
        potential=PotentialConfig(
            coupling=0.0,
            screening_length=base.potential.screening_length,
            remove_mean=base.potential.remove_mean,
        ),
    )
    flat_engine = QuantumMetricEngine(
        flat_config,
        basis=basis,
        basis_id="localized_gaussians.controlled_scenes.v1",
    )
    curved_engine = QuantumMetricEngine(
        base,
        basis=basis,
        basis_id="localized_gaussians.controlled_scenes.v1",
    )
    flat = _make_scene(
        "flat_geometry",
        "baseline: localized population with potential coupling kappa = 0",
        localized,
        flat_engine,
        1,
        0.0,
    )
    one_well = _make_scene(
        "one_localized_well",
        "same localized population as flat baseline; only kappa is enabled",
        localized,
        curved_engine,
        2,
        0.0,
    )
    coherent_scene = _make_scene(
        "coherent_multi_well",
        "four populated sites with signed coherent off-diagonal terms",
        coherent,
        curved_engine,
        3,
        0.2,
    )
    decohered_scene = _make_scene(
        "decohered_same_populations",
        "complete dephasing of the coherent scene; populations unchanged",
        decohered,
        curved_engine,
        4,
        0.4,
    )

    coherent_field = coherent_scene.frame.field
    decohered_field = decohered_scene.frame.field
    diagnostics = {
        "flat_well_population_max_difference": float(
            np.max(np.abs(flat.populations - one_well.populations))
        ),
        "flat_potential_max_abs": float(np.max(np.abs(flat.frame.field.potential))),
        "one_well_potential_max_abs": float(
            np.max(np.abs(one_well.frame.field.potential))
        ),
        "coherent_decohered_population_max_difference": float(
            np.max(np.abs(coherent_scene.populations - decohered_scene.populations))
        ),
        "coherent_coherence_l1": coherent_scene.coherence_l1,
        "decohered_coherence_l1": decohered_scene.coherence_l1,
        "interference_density_signed_integral": float(
            np.sum(coherent_field.density - decohered_field.density) * grid.cell_area
        ),
        "interference_density_l1": float(
            np.sum(np.abs(coherent_field.density - decohered_field.density))
            * grid.cell_area
        ),
        "interference_potential_l2": float(
            np.sqrt(
                np.sum((coherent_field.potential - decohered_field.potential) ** 2)
                * grid.cell_area
            )
        ),
        "interference_frequency_rms_hz": float(
            np.sqrt(
                np.mean(
                    (coherent_scene.frame.modes.frequencies
                     - decohered_scene.frame.modes.frequencies) ** 2
                )
            )
        ),
    }
    return ControlledScientificScenes(
        flat=flat,
        one_well=one_well,
        coherent=coherent_scene,
        decohered=decohered_scene,
        diagnostics=diagnostics,
    )
