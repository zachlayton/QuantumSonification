"""Read-only instantaneous energy-basis transition diagnostics, never rates.

The authority supplies H, A, rho in one declared orthonormal coordinate basis.
No state propagation, measurement, stochastic waiting time, or musical policy
lives here. ``compute`` requires a Hermitian observable; the existing
``process`` operator interface also accepts declared non-Hermitian couplings.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Protocol

import numpy as np

from qmw.core.quantum_spectrum import QuantumSpectrumFrame, analyze_quantum_spectrum
from qmw.core.state_frame import QuantumStateFrame


def readonly(value: object, dtype=None) -> np.ndarray:
    result = np.array(value, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


def positive(value: float, name: str, *, zero: bool = False) -> float:
    number = float(value)
    if not np.isfinite(number) or (number < 0 if zero else number <= 0):
        raise ValueError(f"{name} must be finite and {'nonnegative' if zero else 'positive'}")
    return number


def nonempty(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")


@dataclass(frozen=True)
class FrameContext:
    """Caller-owned identity; IDs must uniquely identify source snapshots.

    basis_id names the *coordinate representation*, not an energy eigenstate.
    Timing in this snapshot is source time. Pitch projection supports seconds
    only; other physical/model clocks need a future explicit timing adapter.
    """
    source_id: str
    frame_id: int
    time: float
    dt: float
    basis_id: str
    time_unit: str = "s"
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("source_id", "basis_id", "time_unit"):
            nonempty(getattr(self, name), name)
        if isinstance(self.frame_id, bool) or not isinstance(self.frame_id, (int, np.integer)) or self.frame_id < 0:
            raise ValueError("frame_id must be a nonnegative integer")
        if not np.isfinite(self.time):
            raise ValueError("time must be finite")
        positive(self.dt, "dt", zero=True)
        object.__setattr__(self, "time", float(self.time))
        object.__setattr__(self, "dt", float(self.dt))
        object.__setattr__(self, "frame_id", int(self.frame_id))
        provenance = tuple(self.provenance)
        for item in provenance:
            nonempty(item, "provenance entry")
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True)
class QuantumUnits:
    """H in energy_unit; hbar in energy_unit*time_unit; A in operator_unit.

    Defaults explicitly use model energy and hbar=1 model_energy*s. They are
    not SI joules or photon energies. omega is signed angular frequency, not Hz.
    Tolerance for zero energy gaps is always in energy_unit, never in Hz.
    """
    hbar: float = 1.0
    energy_unit: str = "model_energy"
    time_unit: str = "s"
    operator_unit: str = "dimensionless"

    def __post_init__(self) -> None:
        positive(self.hbar, "hbar")
        object.__setattr__(self, "hbar", float(self.hbar))
        for name in ("energy_unit", "time_unit", "operator_unit"):
            nonempty(getattr(self, name), name)

    @property
    def omega_unit(self) -> str:
        return f"rad/{self.time_unit}"

    @property
    def hbar_unit(self) -> str:
        return f"{self.energy_unit}*{self.time_unit}"


def validated_spectrum(rho, hamiltonian, tolerance: float, gap_tolerance: float):
    """Preserve raw inputs/eigenvalues; declare NumPy triangle roundoff policy.

    Density checks inherit the canonical observer: Hermitian Frobenius error
    <= tol*max(1,||rho||), trace atol=rtol=tol, lambda_min >= -tol. H additionally
    has a relative Hermiticity check with *no unit-sized floor*, so small SI
    energies are checked correctly. Accepted roundoff is not normalized away.
    eigh uses its lower triangle; reconstruction residual measures that effect.
    """
    h = np.array(hamiltonian, dtype=complex, copy=True)
    density = np.array(rho, dtype=complex, copy=True)
    if h.ndim != 2 or h.shape[0] != h.shape[1] or not h.size or not np.all(np.isfinite(h)):
        raise ValueError("H must be a finite nonempty square matrix")
    scale = float(np.max(np.abs(h)))
    if scale:
        scaled = h / scale
        if np.linalg.norm(scaled-scaled.conj().T) > tolerance*np.linalg.norm(scaled):
            raise ValueError("H must be Hermitian relative to its energy scale")
    spectrum = analyze_quantum_spectrum(density, h, tolerance=tolerance,
                                        degeneracy_tolerance=max(gap_tolerance, np.finfo(float).tiny))
    v, lam = spectrum.density_eigenvectors, spectrum.density_eigenvalues
    e, energies = spectrum.energy_eigenvectors, spectrum.energy_eigenvalues
    diagnostics = {
        "density_hermiticity_residual_fro": float(np.linalg.norm(density-density.conj().T)),
        "trace_error_abs": float(abs(np.trace(density)-1)),
        "minimum_density_eigenvalue": float(lam.min()),
        "negative_eigenvalue_mass": float(-np.minimum(lam, 0).sum()),
        "density_reconstruction_residual_fro": float(np.linalg.norm((v*lam)@v.conj().T-density)),
        "density_eigen_residual_fro": float(np.linalg.norm(density@v-v*lam)),
        "hamiltonian_residual_fro": float(np.linalg.norm(h@e-e*energies)),
        "hamiltonian_hermiticity_residual_fro": float(np.linalg.norm(h-h.conj().T)),
        "density_tolerance": tolerance,
        "energy_gap_tolerance": gap_tolerance,
        "entropy_log": "natural (nats)",
        "entropy_policy": "canonical: sum -lambda*ln(lambda) for lambda > tolerance; no renormalization",
        "roundoff_policy": "preserve raw rho/lambda; eigh lower triangle; clip only downstream gains/activity",
    }
    if not all(np.all(np.isfinite(x)) for x in (lam, energies, v, e, spectrum.rho_in_energy_basis)):
        raise ValueError("spectral analysis produced nonfinite values")
    return spectrum, diagnostics


class ActivityModel(Protocol):
    """Return a nonnegative finite matrix indexed [target, source].

    This plug-in receives isolated read-only analysis arrays, never the
    authority. It must be deterministic and side-effect free. The interface
    always labels output diagnostic; physical rate models need their own
    explicitly validated model-specific contract (e.g. the atomic engine).
    """
    name: str
    units: str

    def evaluate(self, spectrum: QuantumSpectrumFrame,
                 operator_in_energy_basis: np.ndarray) -> np.ndarray: ...


@dataclass(frozen=True)
class PopulationWeightedActivity:
    name: str = "population_weighted_matrix_element"
    units: str = "operator_unit_squared"

    def evaluate(self, spectrum, operator_in_energy_basis):
        # Negative populations within the density tolerance remain in the frame.
        # Only this nonnegative downstream diagnostic uses a roundoff floor.
        return np.abs(operator_in_energy_basis)**2 * np.maximum(spectrum.energy_populations, 0)[None, :]


@dataclass(frozen=True)
class TransitionEdge:
    source: int
    target: int
    delta_E: float
    omega: float
    A_mn: complex
    magnitude: float
    phase_rad: float | None
    source_population: float
    target_population: float
    coherence_mn: complex
    coherence_nm: complex
    activity: Mapping[str, float]
    diagonal: bool
    zero_gap: bool
    basis_dependent_degenerate_endpoint: bool


# One edge contract, also exposed under the name used by the compute API.
Transition = TransitionEdge


@dataclass(frozen=True)
class TransitionFrame:
    """Full energy-basis matrices and two compatible views of the same edges.

    ``transitions`` contains off-diagonal edges strictly above both admission
    thresholds, sorted by (source, target). ``edges`` retains the earlier
    unfiltered candidate contract for existing note/timbre consumers. Both
    respect the configured zero-gap policy. Matrix indices are [target, source].
    Filtering never removes matrix entries, populations, or coherences.
    """
    context: FrameContext
    units: QuantumUnits
    spectrum: QuantumSpectrumFrame
    operator_in_energy_basis: np.ndarray
    edges: tuple[TransitionEdge, ...]
    energy_degenerate_groups: tuple[tuple[int, ...], ...]
    activity_name: str
    activity_units: str
    diagnostics: Mapping[str, object]
    provenance: tuple[str, ...]
    transitions: tuple[TransitionEdge, ...] = field(kw_only=True)
    diagnostic_activity: np.ndarray = field(kw_only=True)
    label_convention: str = "frame-local ascending energy indices; no stable labels within degenerate subspaces or across crossings"
    phase_convention: str = "arg(<m|A|n>); eigenvector-gauge dependent; None for zero matrix elements"
    activity_interpretation: str = "diagnostic activity only; not a universal transition rate or spontaneous emission"

    @property
    def time(self) -> float:
        return self.context.time

    @property
    def energies(self) -> np.ndarray:
        return self.spectrum.energy_eigenvalues

    @property
    def eigenvectors(self) -> np.ndarray:
        return self.spectrum.energy_eigenvectors

    @property
    def delta_E(self) -> np.ndarray:
        return readonly(self.energies[:, None] - self.energies[None, :])

    @property
    def omega(self) -> np.ndarray:
        return readonly(self.delta_E / self.units.hbar)

    @property
    def amplitudes(self) -> np.ndarray:
        return self.operator_in_energy_basis

    @property
    def A_E(self) -> np.ndarray:
        return self.operator_in_energy_basis

    @property
    def magnitudes(self) -> np.ndarray:
        return readonly(np.abs(self.amplitudes))

    @property
    def phases(self) -> np.ndarray:
        """NumPy argument in radians; zero at zero amplitude (undefined phase)."""
        return readonly(np.angle(self.amplitudes))

    @property
    def rho_E(self) -> np.ndarray:
        return self.spectrum.rho_in_energy_basis

    @property
    def populations(self) -> np.ndarray:
        return self.spectrum.energy_populations

    @property
    def coherences(self) -> np.ndarray:
        """Off-diagonal rho_E, with a zero diagonal; rho_E retains all entries."""
        result = self.rho_E.copy()
        np.fill_diagonal(result, 0)
        return readonly(result)


class TransitionEngine:
    def __init__(self, hbar: float | None = None, amplitude_threshold: float = 1e-8,
                 activity_threshold: float = 1e-8, *,
                 units: QuantumUnits | None = None, tolerance: float = 1e-10,
                 gap_tolerance: float = 1e-9, include_diagonal: bool = False,
                 include_zero_gap: bool = False, activity_model: ActivityModel | None = None):
        if hbar is not None:
            hbar = positive(hbar, "hbar")
            if units is not None and hbar != units.hbar:
                raise ValueError("hbar and units.hbar must agree")
        self.units = units or QuantumUnits(hbar=1.0 if hbar is None else hbar)
        self.amplitude_threshold = positive(amplitude_threshold, "amplitude_threshold", zero=True)
        self.activity_threshold = positive(activity_threshold, "activity_threshold", zero=True)
        self.tolerance = positive(tolerance, "tolerance")
        self.gap_tolerance = positive(gap_tolerance, "gap_tolerance", zero=True)
        self.include_diagonal = bool(include_diagonal)
        self.include_zero_gap = bool(include_zero_gap)
        self.activity_model = activity_model or PopulationWeightedActivity()
        nonempty(self.activity_model.name, "activity model name")
        nonempty(self.activity_model.units, "activity model units")

    @property
    def hbar(self) -> float:
        return self.units.hbar

    def compute(self, H, rho, observable, time: float = 0.0, *,
                context: FrameContext | None = None) -> TransitionFrame:
        """Observe H/rho/A in their shared orthonormal coordinate basis.

        A is a Hermitian observable here. Use ``process`` for a general coupling
        operator. Without context, source/basis identity is explicitly unspecified
        and frame_id=0 is a local placeholder, not a durable snapshot identity.
        An explicit context supplies provenance and must agree with ``time``.
        """
        a = np.array(observable, dtype=complex, copy=True)
        if a.ndim != 2 or a.shape[0] != a.shape[1] or not a.size or not np.all(np.isfinite(a)):
            raise ValueError("observable must be a finite nonempty square matrix")
        scale = float(np.max(np.abs(a)))
        if scale:
            scaled = a / scale
            if np.linalg.norm(scaled-scaled.conj().T) > self.tolerance*np.linalg.norm(scaled):
                raise ValueError("observable must be Hermitian relative to its operator scale")
        if not np.isfinite(time):
            raise ValueError("time must be finite")
        if context is None:
            context = FrameContext("unspecified-source", 0, time, 0.0,
                                   "unspecified-orthonormal-basis", self.units.time_unit)
        elif context.time != time:
            raise ValueError("time and context.time must agree")
        return self.process(H, a, rho, context)

    def process_state(self, state: QuantumStateFrame, A, context: FrameContext) -> TransitionFrame:
        """Explicit older/newer QuantumStateFrame seam; does not attach outputs."""
        if state.hamiltonian is None:
            raise ValueError("state snapshot requires a Hamiltonian")
        if state.t != context.time or state.dt != context.dt or state.source_name != context.source_id:
            raise ValueError("state snapshot and context must agree on source and timing")
        return self.process(state.hamiltonian, A, state.rho, context)

    def process(self, H, A, rho, context: FrameContext) -> TransitionFrame:
        if context.time_unit != self.units.time_unit:
            raise ValueError("source context and hbar time units must agree")
        spectrum, diagnostics = validated_spectrum(rho, H, self.tolerance, self.gap_tolerance)
        a = np.array(A, dtype=complex, copy=True)
        count = spectrum.dimension
        if a.shape != (count, count) or not np.all(np.isfinite(a)):
            raise ValueError("A must be finite and have the same shape as H and rho")
        v = spectrum.energy_eigenvectors
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            a_energy = readonly(v.conj().T @ a @ v)
            energies = spectrum.energy_eigenvalues
            deltas = energies[:, None] - energies[None, :]
            omegas = deltas / self.units.hbar
            squares = np.abs(a_energy)**2
        if not all(np.all(np.isfinite(x)) for x in (a_energy, deltas, omegas, squares)):
            raise ValueError("transition matrices or delta_E/hbar are nonfinite")
        with np.errstate(over="ignore", invalid="ignore"):
            raw_activity = np.asarray(self.activity_model.evaluate(spectrum, a_energy))
        if np.iscomplexobj(raw_activity):
            raise ValueError("diagnostic activity must be real; complex values cannot be discarded")
        activities = np.asarray(raw_activity, dtype=float)
        if activities.shape != a.shape or not np.all(np.isfinite(activities)) or np.any(activities < 0):
            raise ValueError("activity model must return a finite nonnegative [target,source] matrix")
        groups, current = [], [0]
        for index in range(1, count):
            if energies[index]-energies[index-1] <= self.gap_tolerance:
                current.append(index)
            else:
                if len(current)>1:
                    groups.append(tuple(current))
                current = [index]
        if len(current)>1:
            groups.append(tuple(current))
        ambiguous = {j for group in groups for j in group}
        edges = []
        for n in range(count):
            for m in range(count):
                delta = float(deltas[m,n])
                zero_gap = abs(delta) <= self.gap_tolerance
                if (n == m and not self.include_diagonal) or (zero_gap and not self.include_zero_gap):
                    continue
                z = complex(a_energy[m,n])
                omega = float(omegas[m,n])
                edges.append(TransitionEdge(n, m, delta, omega, z, abs(z),
                    float(np.angle(z)) if abs(z)>0 else None,
                    float(spectrum.energy_populations[n]), float(spectrum.energy_populations[m]),
                    complex(spectrum.rho_in_energy_basis[m,n]), complex(spectrum.rho_in_energy_basis[n,m]),
                    MappingProxyType({"matrix_element_squared": float(squares[m,n]),
                                      self.activity_model.name: float(activities[m,n])}),
                    n == m, zero_gap, n in ambiguous or m in ambiguous))
        diagnostics["operator_transform_residual_fro"] = float(np.linalg.norm(v@a_energy@v.conj().T-a))
        diagnostics["include_diagonal"] = self.include_diagonal
        diagnostics["include_zero_gap"] = self.include_zero_gap
        diagnostics["amplitude_threshold"] = self.amplitude_threshold
        diagnostics["activity_threshold"] = self.activity_threshold
        diagnostics["transition_filter"] = "off-diagonal; magnitude > amplitude_threshold and diagnostic activity > activity_threshold"
        diagnostics["transition_sort"] = "ascending (source, target) energy-basis indices"
        diagnostics["degeneracy_policy"] = "adjacent gaps <= energy_gap_tolerance; subspace membership only, no invariant edge labels"
        transitions = tuple(sorted(
            (edge for edge in edges if not edge.diagonal
             and edge.magnitude > self.amplitude_threshold
             and edge.activity[self.activity_model.name] > self.activity_threshold),
            key=lambda edge: (edge.source, edge.target),
        ))
        return TransitionFrame(context, self.units, spectrum, a_energy, tuple(edges), tuple(groups),
            self.activity_model.name, self.activity_model.units, MappingProxyType(diagnostics),
            context.provenance + ("qmw.core.quantum_spectrum.analyze_quantum_spectrum",
                                  "qmw.core.transition.v1", f"diagnostic_activity:{self.activity_model.name}"),
            transitions=transitions, diagnostic_activity=readonly(activities))
