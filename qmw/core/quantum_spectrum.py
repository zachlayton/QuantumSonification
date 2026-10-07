"""Canonical, non-mutating spectral analysis for QMW state frames.

This module remains an observer of the authoritative density matrix and
Hamiltonian.  It deliberately contains no synthesis or GUI policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:  # pragma: no cover
    from qmw.core.state_frame import QuantumStateFrame


Array = np.ndarray
SPECTRAL_OBSERVABLE_NAMES = frozenset(
    {
        "spectral_purity",
        "spectral_entropy_nats",
        "spectral_participation_rank",
        "spectral_commutator_norm",
    }
)


@dataclass(frozen=True)
class QuantumSpectrumFrame:
    """Spectral observation of ``rho`` and ``H``.

    Values are ascending as returned by ``numpy.linalg.eigh``.  Rows of
    ``basis_overlap`` are energy modes and columns are density modes, so
    ``energy_populations == basis_overlap @ density_eigenvalues``.
    """

    density_eigenvalues: Array
    density_eigenvectors: Array
    energy_eigenvalues: Array
    energy_eigenvectors: Array
    rho_in_energy_basis: Array
    energy_populations: Array
    basis_overlap: Array
    density_gaps: Array
    energy_gaps: Array
    purity: float
    entropy: float
    participation_rank: float
    commutator_norm: float
    tolerance: float
    degeneracy_tolerance: float

    @property
    def dimension(self) -> int:
        return int(self.density_eigenvalues.size)

    @property
    def modal_amplitudes(self) -> Array:
        """Population-preserving downstream amplitudes: ``sqrt(max(p, 0))``."""

        return np.sqrt(np.maximum(self.energy_populations, 0.0))

    def observables(self) -> dict[str, float]:
        return {
            "spectral_purity": self.purity,
            "spectral_entropy_nats": self.entropy,
            "spectral_participation_rank": self.participation_rank,
            "spectral_commutator_norm": self.commutator_norm,
        }


@dataclass(frozen=True)
class TrackedEigensystem:
    """Eigensystem ordered by its overlap with the preceding observation."""

    eigenvalues: Array
    eigenvectors: Array
    permutation: Array
    overlaps: Array
    near_degenerate_groups: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class SpectralStepRecord:
    """One immutable numerical spectral observation from a continuous QMW tick."""

    index: int
    t: float
    dt: float
    source_name: str | None
    spectrum: QuantumSpectrumFrame


class QMWSpectralTrace:
    """Bounded history of spectra, preserving one numerical record per frame."""

    def __init__(self, max_records: int = 4096) -> None:
        if max_records <= 0:
            raise ValueError("max_records must be positive")
        self.max_records = int(max_records)
        self._records: list[SpectralStepRecord] = []
        self._next_index = 0

    @property
    def records(self) -> tuple[SpectralStepRecord, ...]:
        return tuple(self._records)

    @property
    def latest(self) -> SpectralStepRecord | None:
        return self._records[-1] if self._records else None

    def append(
        self, frame: "QuantumStateFrame", spectrum: QuantumSpectrumFrame
    ) -> SpectralStepRecord:
        record = SpectralStepRecord(
            index=self._next_index,
            t=float(frame.t),
            dt=float(frame.dt),
            source_name=frame.source_name,
            spectrum=spectrum,
        )
        self._next_index += 1
        self._records.append(record)
        if len(self._records) > self.max_records:
            del self._records[: len(self._records) - self.max_records]
        return record

    def scalar_series(self, name: str) -> tuple[Array, Array]:
        """Return time/value arrays for a scalar spectral diagnostic."""

        if name not in SPECTRAL_OBSERVABLE_NAMES:
            raise KeyError(f"unknown spectral scalar: {name}")
        times = np.asarray([record.t for record in self._records], dtype=float)
        values = np.asarray(
            [record.spectrum.observables()[name] for record in self._records],
            dtype=float,
        )
        return times, values

    def to_text(self) -> str:
        """Render the complete retained trace as an auditable plain-text record."""

        lines = [_TEXT_LOG_HEADER]
        lines.extend(_format_step_record(record) for record in self._records)
        return "\n".join(lines) + "\n"

    def write_text(self, path: str | Path) -> Path:
        """Write the retained trace in one atomic snapshot operation."""

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.to_text(), encoding="utf-8")
        return destination


class QMWSpectralTextLogger:
    """Opt-in append-only numerical log for each valid QMW spectral frame."""

    def __init__(self, path: str | Path, *, overwrite: bool = True) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if overwrite:
            self.path.write_text(_TEXT_LOG_HEADER + "\n", encoding="utf-8")
        elif not self.path.exists():
            self.path.write_text(_TEXT_LOG_HEADER + "\n", encoding="utf-8")

    def append(self, record: SpectralStepRecord) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(_format_step_record(record) + "\n")


_TEXT_LOG_HEADER = (
    "# QMW Spectral Analysis V4 numerical trace\n"
    "# Spectra are separate: energy/p/amplitude are energy-basis quantities; "
    "lambda is the independently ordered density spectrum."
)


def _format_step_record(record: SpectralStepRecord) -> str:
    spectrum = record.spectrum
    return (
        f"step={record.index} t={record.t:.12g} dt={record.dt:.12g} "
        f"source={record.source_name or 'unnamed'} "
        f"purity={spectrum.purity:.12g} entropy_nats={spectrum.entropy:.12g} "
        f"participation={spectrum.participation_rank:.12g} "
        f"commutator_fro={spectrum.commutator_norm:.12g} "
        f"energy={_format_vector(spectrum.energy_eigenvalues)} "
        f"population={_format_vector(spectrum.energy_populations)} "
        f"amplitude={_format_vector(spectrum.modal_amplitudes)} "
        f"density_lambda={_format_vector(spectrum.density_eigenvalues)}"
    )


def _format_vector(values: Array) -> str:
    return "[" + ",".join(f"{value:.12g}" for value in values) + "]"


class QMWEigenTracker:
    """Follow mode identity using overlap rather than naïve eigenvalue sorting."""

    def __init__(self, degeneracy_tolerance: float = 1e-8) -> None:
        if degeneracy_tolerance <= 0:
            raise ValueError("degeneracy_tolerance must be positive")
        self.degeneracy_tolerance = float(degeneracy_tolerance)
        self._previous_vectors: Array | None = None

    def reset(self) -> None:
        self._previous_vectors = None

    def track(self, eigenvalues: Array, eigenvectors: Array) -> TrackedEigensystem:
        values = np.asarray(eigenvalues, dtype=float).copy()
        vectors = np.asarray(eigenvectors, dtype=np.complex128).copy()
        if values.ndim != 1 or vectors.shape != (values.size, values.size):
            raise ValueError("eigenvalues and eigenvectors have incompatible shapes")
        count = values.size
        if self._previous_vectors is None:
            permutation = np.arange(count, dtype=int)
            overlaps = np.eye(count, dtype=float)
        else:
            overlaps = np.abs(self._previous_vectors.conj().T @ vectors) ** 2
            permutation = self._overlap_assignment(overlaps)
            values = values[permutation]
            vectors = vectors[:, permutation]
            overlaps = overlaps[:, permutation]
            for mode in range(count):
                phase_overlap = np.vdot(self._previous_vectors[:, mode], vectors[:, mode])
                if abs(phase_overlap) > self.degeneracy_tolerance:
                    vectors[:, mode] *= np.exp(-1j * np.angle(phase_overlap))
        self._previous_vectors = vectors.copy()
        return TrackedEigensystem(
            eigenvalues=_readonly(values),
            eigenvectors=_readonly(vectors),
            permutation=_readonly(permutation),
            overlaps=_readonly(overlaps),
            near_degenerate_groups=_near_degenerate_groups(
                values, self.degeneracy_tolerance
            ),
        )

    @staticmethod
    def _overlap_assignment(overlaps: Array) -> Array:
        """Deterministic one-to-one greedy matching for QMW's small mode counts."""

        count = overlaps.shape[0]
        candidates = sorted(
            (-float(overlaps[previous, current]), previous, current)
            for previous in range(count)
            for current in range(count)
        )
        assignment = np.full(count, -1, dtype=int)
        used: set[int] = set()
        for _, previous, current in candidates:
            if assignment[previous] == -1 and current not in used:
                assignment[previous] = current
                used.add(current)
        return assignment


def analyze_quantum_spectrum(
    rho: Array,
    hamiltonian: Array,
    *,
    tolerance: float = 1e-10,
    degeneracy_tolerance: float = 1e-8,
) -> QuantumSpectrumFrame:
    """Validate and analyze ``rho`` and ``H`` without changing either input."""

    if tolerance <= 0 or degeneracy_tolerance <= 0:
        raise ValueError("tolerances must be positive")
    density = _square_complex_matrix("rho", rho)
    hamiltonian_array = _square_complex_matrix("hamiltonian", hamiltonian)
    if density.shape != hamiltonian_array.shape:
        raise ValueError("rho and hamiltonian must have the same dimension")
    _require_hermitian("rho", density, tolerance)
    _require_hermitian("hamiltonian", hamiltonian_array, tolerance)
    if not np.isclose(np.trace(density), 1.0, atol=tolerance, rtol=tolerance):
        raise ValueError("rho must have trace one")
    density_values, density_vectors = np.linalg.eigh(density)
    density_values = density_values.real
    if float(np.min(density_values)) < -tolerance:
        raise ValueError("rho must be positive semidefinite")
    energy_values, energy_vectors = np.linalg.eigh(hamiltonian_array)
    energy_values = energy_values.real
    rho_energy = energy_vectors.conj().T @ density @ energy_vectors
    populations = np.real(np.diag(rho_energy))
    overlap = np.abs(energy_vectors.conj().T @ density_vectors) ** 2
    clipped_values = np.clip(density_values, 0.0, None)
    positive_values = clipped_values[clipped_values > tolerance]
    purity = float(np.real(np.trace(density @ density)))
    entropy = float(-np.sum(positive_values * np.log(positive_values)))
    participation_rank = float(1.0 / np.sum(clipped_values**2))
    commutator = hamiltonian_array @ density - density @ hamiltonian_array
    return QuantumSpectrumFrame(
        density_eigenvalues=_readonly(density_values),
        density_eigenvectors=_readonly(density_vectors),
        energy_eigenvalues=_readonly(energy_values),
        energy_eigenvectors=_readonly(energy_vectors),
        rho_in_energy_basis=_readonly(rho_energy),
        energy_populations=_readonly(populations),
        basis_overlap=_readonly(overlap),
        density_gaps=_readonly(np.diff(density_values)),
        energy_gaps=_readonly(np.diff(energy_values)),
        purity=purity,
        entropy=entropy,
        participation_rank=participation_rank,
        commutator_norm=float(np.linalg.norm(commutator, ord="fro")),
        tolerance=float(tolerance),
        degeneracy_tolerance=float(degeneracy_tolerance),
    )


def attach_quantum_spectrum(
    frame: "QuantumStateFrame", spectrum: QuantumSpectrumFrame | None = None
) -> QuantumSpectrumFrame:
    """Attach observer outputs only; this never mutates the frame's ``rho`` or ``H``."""

    if spectrum is None:
        if frame.hamiltonian is None:
            raise ValueError("a Hamiltonian is required for spectral analysis")
        spectrum = analyze_quantum_spectrum(frame.rho, frame.hamiltonian)
    frame.spectrum = spectrum
    frame.arrays.update(
        {
            "spectral_density_eigenvalues": spectrum.density_eigenvalues,
            "spectral_energy_eigenvalues": spectrum.energy_eigenvalues,
            "spectral_energy_populations": spectrum.energy_populations,
            "spectral_modal_amplitudes": spectrum.modal_amplitudes,
        }
    )
    frame.observables.update(spectrum.observables())
    return spectrum


class QMWSpectralObserver:
    """Attach spectra at the bus boundary while preserving legacy frame sources."""

    def __init__(self, *, strict: bool = False, tolerance: float = 1e-10) -> None:
        self.strict = strict
        self.tolerance = tolerance
        self.last_error: str | None = None

    def observe(self, frame: "QuantumStateFrame") -> QuantumSpectrumFrame | None:
        if frame.hamiltonian is None:
            return None
        try:
            spectrum = analyze_quantum_spectrum(
                frame.rho, frame.hamiltonian, tolerance=self.tolerance
            )
        except ValueError as error:
            self.last_error = str(error)
            frame.metadata["spectral_error"] = self.last_error
            if self.strict:
                raise
            return None
        self.last_error = None
        return attach_quantum_spectrum(frame, spectrum)


def _square_complex_matrix(name: str, value: Array) -> Array:
    matrix = np.asarray(value, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] == 0:
        raise ValueError(f"{name} must be a non-empty square matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must contain only finite values")
    return matrix


def _require_hermitian(name: str, matrix: Array, tolerance: float) -> None:
    scale = max(1.0, float(np.linalg.norm(matrix, ord="fro")))
    if float(np.linalg.norm(matrix - matrix.conj().T, ord="fro")) > tolerance * scale:
        raise ValueError(f"{name} must be Hermitian")


def _readonly(value: Array) -> Array:
    result = np.array(value, copy=True)
    result.setflags(write=False)
    return result


def _near_degenerate_groups(
    values: Array, tolerance: float
) -> tuple[tuple[int, ...], ...]:
    groups: list[tuple[int, ...]] = []
    current = [0]
    for index in range(1, values.size):
        if abs(values[index] - values[index - 1]) <= tolerance:
            current.append(index)
        else:
            if len(current) > 1:
                groups.append(tuple(current))
            current = [index]
    if len(current) > 1:
        groups.append(tuple(current))
    return tuple(groups)
