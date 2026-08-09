from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Literal, Sequence

import numpy as np

from excitation.base import QuantumSource
from excitation.descriptor import QuantumDescriptor


PLANCK_EV_SECONDS = 4.135667696e-15
LIGHT_METRES_PER_SECOND = 299_792_458.0
HYDROGEN_RYDBERG_EV = 13.605693122994
HYDROGEN_IONIZATION_FREQUENCY_HZ = (
    HYDROGEN_RYDBERG_EV / PLANCK_EV_SECONDS
)


@dataclass(frozen=True)
class HydrogenicSpecies:
    """One-electron isotope preset used by the demonstration catalog."""

    key: str
    display_name: str
    nuclear_charge: int
    nuclear_mass_electron_ratio: float
    radioactive: bool = False

    @property
    def reduced_mass_factor(self) -> float:
        mass_ratio = self.nuclear_mass_electron_ratio
        return mass_ratio / (mass_ratio + 1.0)


# Nuclear/electron mass ratios are sufficient for the reduced-mass correction
# resolved by this model. The Li ratios are derived from NIST atomic isotope
# masses with the three electron masses removed; electronic binding corrections
# are well below the musical/display precision of this demonstration.
_ATOMIC_MASS_UNIT_ELECTRON_MASS_RATIO = 1822.888486209
HYDROGENIC_SPECIES = {
    "H-1": HydrogenicSpecies(
        "H-1", "hydrogen-1", 1, 1836.152673426
    ),
    "H-2": HydrogenicSpecies(
        "H-2", "deuterium", 1, 3670.482967655
    ),
    "H-3": HydrogenicSpecies(
        "H-3", "tritium", 1, 5496.92153573, radioactive=True
    ),
    "He-3+": HydrogenicSpecies(
        "He-3+", "helium-3 ion", 2, 5495.88527984
    ),
    "He-4+": HydrogenicSpecies(
        "He-4+", "helium-4 ion", 2, 7294.29954171
    ),
    "Li-6++": HydrogenicSpecies(
        "Li-6++",
        "lithium-6 doubly ionized",
        3,
        6.0151228874 * _ATOMIC_MASS_UNIT_ELECTRON_MASS_RATIO - 3.0,
    ),
    "Li-7++": HydrogenicSpecies(
        "Li-7++",
        "lithium-7 doubly ionized",
        3,
        7.0160034366 * _ATOMIC_MASS_UNIT_ELECTRON_MASS_RATIO - 3.0,
    ),
}
HYDROGENIC_SPECIES_ALIASES = {
    "H": "H-1",
    "He+": "He-4+",
    "Li2+": "Li-7++",
}


def resolve_hydrogenic_species(species: str) -> HydrogenicSpecies:
    key = HYDROGENIC_SPECIES_ALIASES.get(str(species), str(species))
    try:
        return HYDROGENIC_SPECIES[key]
    except KeyError as exc:
        available = ", ".join(HYDROGENIC_SPECIES)
        raise ValueError(
            f"unknown hydrogenic species {species!r}; use {available}"
        ) from exc


@dataclass(frozen=True)
class QuantumLevel:
    """One bound state participating in a transition ensemble."""

    label: str
    n: int
    l: int
    m: int
    energy_ev: float
    population: float
    phase_rad: float = 0.0
    lifetime_seconds: float = 1.0e-8
    coherence: float = 1.0
    spin: float = 0.5

    def __post_init__(self) -> None:
        if self.n < 1:
            raise ValueError("n must be >= 1")
        if not 0 <= self.l < self.n:
            raise ValueError("l must satisfy 0 <= l < n")
        if abs(self.m) > self.l:
            raise ValueError("m must satisfy -l <= m <= l")
        if self.population < 0.0:
            raise ValueError("population must be non-negative")
        if self.lifetime_seconds <= 0.0:
            raise ValueError("lifetime_seconds must be positive")
        if not 0.0 <= self.coherence <= 1.0:
            raise ValueError("coherence must be in 0..1")


@dataclass(frozen=True)
class BornTransition:
    """A physically filtered emission line and its sonic projection."""

    initial: QuantumLevel
    final: QuantumLevel
    delta_energy_ev: float
    photon_frequency_hz: float
    wavelength_nm: float
    radial_matrix_element_au: float
    line_strength: float
    spontaneous_rate_weight: float
    branching_probability: float
    event_probability: float
    relative_phase_rad: float
    physical_lifetime_seconds: float
    physical_linewidth_hz: float
    sonic_duration_seconds: float
    sonic_linewidth_hz: float
    audio_frequency_hz: float
    frequency_mapping: str
    audio_scale_factor: float
    octave_shift: int | None

    @property
    def delta_n(self) -> int:
        return self.initial.n - self.final.n

    @property
    def delta_l(self) -> int:
        return self.initial.l - self.final.l

    @property
    def delta_m(self) -> int:
        return self.initial.m - self.final.m


@dataclass(frozen=True)
class BornTransitionState:
    """Rich snapshot exposed alongside the compact QuantumDescriptor."""

    species: str
    species_name: str
    nuclear_charge: int
    reduced_mass_factor: float
    radioactive: bool
    event_id: int
    index: int
    initial_label: str
    final_label: str
    initial_n: int
    initial_l: int
    initial_m: int
    final_n: int
    final_l: int
    final_m: int
    delta_energy_ev: float
    photon_frequency_hz: float
    wavelength_nm: float
    audio_frequency_hz: float
    frequency_mapping: str
    audio_scale_factor: float
    octave_shift: int | None
    line_strength: float
    spontaneous_rate_weight: float
    branching_probability: float
    event_probability: float
    relative_phase_rad: float
    physical_lifetime_seconds: float
    physical_linewidth_hz: float
    sonic_duration_seconds: float
    sonic_linewidth_hz: float
    selection_rule: str


def hydrogen_energy_ev(
    n: int,
    nuclear_charge: int = 1,
    reduced_mass_factor: float = 1.0,
) -> float:
    """Hydrogenic bound-state energy in electron volts."""
    if n < 1:
        raise ValueError("n must be >= 1")
    if nuclear_charge < 1:
        raise ValueError("nuclear_charge must be >= 1")
    if not 0.0 < reduced_mass_factor <= 1.0:
        raise ValueError("reduced_mass_factor must be in 0..1")
    return (
        -(nuclear_charge**2)
        * reduced_mass_factor
        * HYDROGEN_RYDBERG_EV
        / (n * n)
    )


def electric_dipole_allowed(initial: QuantumLevel, final: QuantumLevel) -> bool:
    """Return whether an emission satisfies basic E1 selection rules.

    The model enforces an energy drop, delta-l = +/-1, delta-m = 0 or +/-1,
    and conservation of spin. Hyperfine structure and external fields are not
    included in this first version.
    """
    return (
        initial.energy_ev > final.energy_ev
        and abs(initial.l - final.l) == 1
        and abs(initial.m - final.m) <= 1
        and math.isclose(initial.spin, final.spin, abs_tol=1.0e-12)
    )


def octave_fold_frequency(
    frequency_hz: float,
    minimum_hz: float = 55.0,
    maximum_hz: float = 1_760.0,
) -> tuple[float, int]:
    """Transpose a positive frequency by octaves into an audible register."""
    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be positive")
    if minimum_hz <= 0.0 or maximum_hz <= minimum_hz:
        raise ValueError("audio bounds must satisfy 0 < minimum < maximum")

    folded = float(frequency_hz)
    shift = 0
    while folded > maximum_hz:
        folded *= 0.5
        shift -= 1
    while folded < minimum_hz:
        folded *= 2.0
        shift += 1
    return folded, shift


def global_ratio_scale_frequency(
    frequency_hz: float,
    *,
    photon_reference_hz: float = HYDROGEN_IONIZATION_FREQUENCY_HZ,
    audio_reference_hz: float = 1_760.0,
) -> tuple[float, float]:
    """Scale every frequency by one fixed factor, preserving all ratios."""
    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be positive")
    if photon_reference_hz <= 0.0 or audio_reference_hz <= 0.0:
        raise ValueError("reference frequencies must be positive")
    scale_factor = audio_reference_hz / photon_reference_hz
    return float(frequency_hz * scale_factor), float(scale_factor)


def _associated_laguerre(order: int, alpha: int, x: np.ndarray) -> np.ndarray:
    if order == 0:
        return np.ones_like(x)
    if order == 1:
        return 1.0 + alpha - x

    previous_previous = np.ones_like(x)
    previous = 1.0 + alpha - x
    for degree in range(2, order + 1):
        current = (
            (2 * degree - 1 + alpha - x) * previous
            - (degree - 1 + alpha) * previous_previous
        ) / degree
        previous_previous, previous = previous, current
    return previous


def _hydrogen_radial_wavefunction(
    n: int,
    l: int,
    radius_bohr: np.ndarray,
) -> np.ndarray:
    order = n - l - 1
    rho = 2.0 * radius_bohr / n
    normalization = (2.0 / (n * n)) * math.sqrt(
        math.factorial(order) / math.factorial(n + l)
    )
    return (
        normalization
        * np.exp(-radius_bohr / n)
        * np.power(rho, l)
        * _associated_laguerre(order, 2 * l + 1, rho)
    )


@lru_cache(maxsize=256)
def hydrogen_radial_dipole_au(
    initial_n: int,
    initial_l: int,
    final_n: int,
    final_l: int,
) -> float:
    """Numerically evaluate the hydrogen radial dipole integral in Bohr radii."""
    if abs(initial_l - final_l) != 1:
        return 0.0

    maximum_n = max(initial_n, final_n)
    radius_max = max(80.0, 20.0 * maximum_n * maximum_n)
    radius = np.linspace(0.0, radius_max, 16_385, dtype=np.float64)
    initial_radial = _hydrogen_radial_wavefunction(
        initial_n, initial_l, radius
    )
    final_radial = _hydrogen_radial_wavefunction(final_n, final_l, radius)
    integrand = initial_radial * final_radial * radius**3
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(integrand, radius))
    return float(np.trapz(integrand, radius))


def hydrogenic_demo_levels(species: str = "H-1") -> tuple[QuantumLevel, ...]:
    """Return a coherent, deliberately excited one-electron ensemble.

    Populations and phases are experimental controls, not a thermal-equilibrium
    model. Lifetimes use a simple hydrogenic n^3 scaling except for metastable
    2s, which has no E1 route to 1s in this model.
    """
    preset = resolve_hydrogenic_species(species)
    lifetime_scale = float(preset.nuclear_charge**4)
    specifications = (
        ("1s", 1, 0, 0, 0.05, 0.00, 1.0e9),
        ("2s", 2, 0, 0, 0.05, 0.18, 0.122),
        ("2p0", 2, 1, 0, 0.18, 0.34, 1.60e-9),
        ("3s", 3, 0, 0, 0.12, 0.53, 5.40e-9),
        ("3p0", 3, 1, 0, 0.18, 0.76, 5.40e-9),
        ("3d0", 3, 2, 0, 0.12, 1.02, 5.40e-9),
        ("4s", 4, 0, 0, 0.08, 1.31, 1.28e-8),
        ("4p0", 4, 1, 0, 0.10, 1.63, 1.28e-8),
        ("4d0", 4, 2, 0, 0.07, 1.98, 1.28e-8),
        ("4f0", 4, 3, 0, 0.05, 2.36, 1.28e-8),
    )
    return tuple(
        QuantumLevel(
            label=label,
            n=n,
            l=l,
            m=m,
            energy_ev=hydrogen_energy_ev(
                n,
                preset.nuclear_charge,
                preset.reduced_mass_factor,
            ),
            population=population,
            phase_rad=phase,
            lifetime_seconds=lifetime / lifetime_scale,
        )
        for label, n, l, m, population, phase, lifetime in specifications
    )


def hydrogen_demo_levels() -> tuple[QuantumLevel, ...]:
    """Backward-compatible alias for the neutral-hydrogen demonstration."""
    return hydrogenic_demo_levels("H-1")


class BornTransitionEngine(QuantumSource):
    """Transition-centred hydrogen excitation source for QMW.

    Photon frequency comes from the energy difference. E1 selection rules
    filter the line set. A numerical radial dipole integral ranks allowed
    lines, initial populations weight their occurrence, and state lifetime
    controls linewidth and held sonic duration.
    """

    def __init__(
        self,
        levels: Sequence[QuantumLevel] | None = None,
        *,
        species: str = "H-1",
        selection_mode: Literal["sequential", "stochastic"] = "sequential",
        frequency_mapping: Literal["global_ratio", "octave_fold"] = "global_ratio",
        seed: int | None = 23,
        time_scale: float = 100_000_000.0,
        minimum_duration_seconds: float = 0.08,
        maximum_duration_seconds: float = 2.0,
        minimum_audio_hz: float = 55.0,
        maximum_audio_hz: float = 1_760.0,
        photon_reference_hz: float = HYDROGEN_IONIZATION_FREQUENCY_HZ,
        audio_reference_hz: float = 1_760.0,
    ) -> None:
        if selection_mode not in ("sequential", "stochastic"):
            raise ValueError("selection_mode must be sequential or stochastic")
        if frequency_mapping not in ("global_ratio", "octave_fold"):
            raise ValueError(
                "frequency_mapping must be global_ratio or octave_fold"
            )
        if time_scale <= 0.0:
            raise ValueError("time_scale must be positive")
        if not 0.0 < minimum_duration_seconds <= maximum_duration_seconds:
            raise ValueError("duration bounds must satisfy 0 < minimum <= maximum")

        preset = resolve_hydrogenic_species(species)
        self.species = preset.key
        self.species_name = preset.display_name
        self.nuclear_charge = preset.nuclear_charge
        self.reduced_mass_factor = preset.reduced_mass_factor
        self.radioactive = preset.radioactive
        self.levels = tuple(levels or hydrogenic_demo_levels(preset.key))
        if len(self.levels) < 2:
            raise ValueError("at least two quantum levels are required")
        if sum(level.population for level in self.levels) <= 0.0:
            raise ValueError("at least one level must have non-zero population")

        self.selection_mode = selection_mode
        self.frequency_mapping = frequency_mapping
        self.rng = np.random.default_rng(seed)
        self.time_scale = float(time_scale)
        self.minimum_duration_seconds = float(minimum_duration_seconds)
        self.maximum_duration_seconds = float(maximum_duration_seconds)
        self.minimum_audio_hz = float(minimum_audio_hz)
        self.maximum_audio_hz = float(maximum_audio_hz)
        self.photon_reference_hz = float(photon_reference_hz)
        self.audio_reference_hz = float(audio_reference_hz)
        self.elapsed_seconds = 0.0

        self.transitions = self._build_transitions()
        if not self.transitions:
            raise ValueError("the level set contains no allowed E1 emissions")

        self._maximum_delta_energy = max(
            transition.delta_energy_ev for transition in self.transitions
        )
        self._maximum_quantum_distance = max(
            self._quantum_distance(transition)
            for transition in self.transitions
        )
        self._maximum_sonic_linewidth = max(
            transition.sonic_linewidth_hz for transition in self.transitions
        )

        self.index = 0
        self.event_id = 0
        if self.selection_mode == "stochastic":
            self.index = self._draw_index()
        self._state = self._state_from_transition(self.index)
        self._descriptor = self._descriptor_from_transition(
            self.transitions[self.index]
        )

    def _build_transitions(self) -> tuple[BornTransition, ...]:
        provisional: list[dict[str, object]] = []
        by_initial: dict[str, list[int]] = {}

        for initial in self.levels:
            for final in self.levels:
                if not electric_dipole_allowed(initial, final):
                    continue

                delta_energy = initial.energy_ev - final.energy_ev
                photon_frequency = delta_energy / PLANCK_EV_SECONDS
                wavelength_nm = (
                    LIGHT_METRES_PER_SECOND / photon_frequency * 1.0e9
                )
                radial = hydrogen_radial_dipole_au(
                    initial.n, initial.l, final.n, final.l
                ) / self.nuclear_charge

                # A rotationally averaged angular proxy keeps this dependency-
                # free MVP explicit about not resolving photon polarization.
                angular_weight = 1.0 / (2.0 * initial.l + 1.0)
                strength = max(radial * radial * angular_weight, 1.0e-18)
                spontaneous_rate_weight = strength * photon_frequency**3
                if self.frequency_mapping == "global_ratio":
                    audio_frequency, audio_scale_factor = (
                        global_ratio_scale_frequency(
                            photon_frequency,
                            photon_reference_hz=self.photon_reference_hz,
                            audio_reference_hz=self.audio_reference_hz,
                        )
                    )
                    octave_shift = None
                else:
                    audio_frequency, octave_shift = octave_fold_frequency(
                        photon_frequency,
                        self.minimum_audio_hz,
                        self.maximum_audio_hz,
                    )
                    audio_scale_factor = audio_frequency / photon_frequency
                sonic_duration = float(
                    np.clip(
                        initial.lifetime_seconds * self.time_scale,
                        self.minimum_duration_seconds,
                        self.maximum_duration_seconds,
                    )
                )
                physical_linewidth = 1.0 / (
                    2.0 * math.pi * initial.lifetime_seconds
                )
                sonic_linewidth = 1.0 / (2.0 * math.pi * sonic_duration)

                provisional.append(
                    {
                        "initial": initial,
                        "final": final,
                        "delta_energy_ev": delta_energy,
                        "photon_frequency_hz": photon_frequency,
                        "wavelength_nm": wavelength_nm,
                        "radial_matrix_element_au": radial,
                        "line_strength": strength,
                        "spontaneous_rate_weight": spontaneous_rate_weight,
                        "relative_phase_rad": math.remainder(
                            initial.phase_rad - final.phase_rad,
                            2.0 * math.pi,
                        ),
                        "physical_lifetime_seconds": initial.lifetime_seconds,
                        "physical_linewidth_hz": physical_linewidth,
                        "sonic_duration_seconds": sonic_duration,
                        "sonic_linewidth_hz": sonic_linewidth,
                        "audio_frequency_hz": audio_frequency,
                        "frequency_mapping": self.frequency_mapping,
                        "audio_scale_factor": audio_scale_factor,
                        "octave_shift": octave_shift,
                    }
                )
                by_initial.setdefault(initial.label, []).append(
                    len(provisional) - 1
                )

        if not provisional:
            return ()

        branch_probabilities = np.zeros(len(provisional), dtype=np.float64)
        raw_event_weights = np.zeros(len(provisional), dtype=np.float64)
        for initial_label, indices in by_initial.items():
            strength_sum = sum(
                float(provisional[index]["spontaneous_rate_weight"])
                for index in indices
            )
            for index in indices:
                branch = (
                    float(provisional[index]["spontaneous_rate_weight"])
                    / strength_sum
                )
                initial = provisional[index]["initial"]
                assert isinstance(initial, QuantumLevel)
                branch_probabilities[index] = branch
                raw_event_weights[index] = initial.population * branch

        total_event_weight = float(np.sum(raw_event_weights))
        if total_event_weight <= 0.0:
            raise ValueError("allowed transitions have zero populated weight")
        event_probabilities = raw_event_weights / total_event_weight

        transitions = []
        for index, values in enumerate(provisional):
            transitions.append(
                BornTransition(
                    **values,
                    branching_probability=float(branch_probabilities[index]),
                    event_probability=float(event_probabilities[index]),
                )
            )

        transitions.sort(
            key=lambda transition: (
                transition.initial.n,
                transition.initial.l,
                transition.initial.m,
                transition.final.n,
                transition.final.l,
                transition.final.m,
            )
        )
        return tuple(transitions)

    @staticmethod
    def _quantum_distance(transition: BornTransition) -> float:
        return math.sqrt(
            transition.delta_n**2
            + transition.delta_l**2
            + transition.delta_m**2
        )

    def _draw_index(self) -> int:
        probabilities = np.asarray(
            [transition.event_probability for transition in self.transitions]
        )
        probabilities /= np.sum(probabilities)
        return int(self.rng.choice(len(self.transitions), p=probabilities))

    def _advance(self) -> None:
        self.event_id += 1
        if self.selection_mode == "stochastic":
            self.index = self._draw_index()
        else:
            self.index = (self.index + 1) % len(self.transitions)
        self._state = self._state_from_transition(self.index)
        self._descriptor = self._descriptor_from_transition(
            self.transitions[self.index]
        )

    def _state_from_transition(self, index: int) -> BornTransitionState:
        transition = self.transitions[index]
        return BornTransitionState(
            species=self.species,
            species_name=self.species_name,
            nuclear_charge=self.nuclear_charge,
            reduced_mass_factor=self.reduced_mass_factor,
            radioactive=self.radioactive,
            event_id=self.event_id,
            index=index,
            initial_label=transition.initial.label,
            final_label=transition.final.label,
            initial_n=transition.initial.n,
            initial_l=transition.initial.l,
            initial_m=transition.initial.m,
            final_n=transition.final.n,
            final_l=transition.final.l,
            final_m=transition.final.m,
            delta_energy_ev=transition.delta_energy_ev,
            photon_frequency_hz=transition.photon_frequency_hz,
            wavelength_nm=transition.wavelength_nm,
            audio_frequency_hz=transition.audio_frequency_hz,
            frequency_mapping=transition.frequency_mapping,
            audio_scale_factor=transition.audio_scale_factor,
            octave_shift=transition.octave_shift,
            line_strength=transition.line_strength,
            spontaneous_rate_weight=transition.spontaneous_rate_weight,
            branching_probability=transition.branching_probability,
            event_probability=transition.event_probability,
            relative_phase_rad=transition.relative_phase_rad,
            physical_lifetime_seconds=transition.physical_lifetime_seconds,
            physical_linewidth_hz=transition.physical_linewidth_hz,
            sonic_duration_seconds=transition.sonic_duration_seconds,
            sonic_linewidth_hz=transition.sonic_linewidth_hz,
            selection_rule="E1: |delta_l|=1, |delta_m|<=1, delta_spin=0",
        )

    def _descriptor_from_transition(
        self,
        transition: BornTransition,
    ) -> QuantumDescriptor:
        relative_phase = (transition.relative_phase_rad / (2.0 * math.pi)) % 1.0
        topology_projection = self._quantum_distance(
            transition
        ) / self._maximum_quantum_distance
        linewidth_projection = (
            transition.sonic_linewidth_hz / self._maximum_sonic_linewidth
        )
        return QuantumDescriptor(
            energy=float(transition.delta_energy_ev / self._maximum_delta_energy),
            phase=float(relative_phase),
            probability=float(transition.event_probability),
            coherence=float(
                min(transition.initial.coherence, transition.final.coherence)
            ),
            entanglement=0.0,
            spin=0.5,
            topology=float(np.clip(topology_projection, 0.0, 1.0)),
            curvature=float(np.clip(linewidth_projection, 0.0, 1.0)),
        )

    def step(self, dt: float) -> None:
        """Advance after the current lifetime-scaled sonic duration elapses."""
        if dt < 0.0:
            raise ValueError("dt must be non-negative")
        self.elapsed_seconds += float(dt)
        while self.elapsed_seconds >= self.state.sonic_duration_seconds:
            self.elapsed_seconds -= self.state.sonic_duration_seconds
            self._advance()

    @property
    def descriptor(self) -> QuantumDescriptor:
        return self._descriptor

    @property
    def state(self) -> BornTransitionState:
        return self._state
