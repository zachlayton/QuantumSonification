from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from qmw.flucoma.audio_corpus import AUDIO_FEATURE_NAMES, _clip01
from qmw.flucoma.quantum_descriptors import DescriptorVector


@dataclass(frozen=True)
class DensityMosaicTile:
    """One density-matrix cell interpreted as an audio-mosaicing target tile."""

    row: int
    column: int
    basis_from: str
    basis_to: str
    amplitude: float
    phase: float
    phase_unit: float
    probability: float
    coherence: float
    distance: float
    salience: float
    query: DescriptorVector

    @property
    def role(self) -> str:
        if self.row == self.column:
            return "probability_anchor"
        if self.distance >= 0.75:
            return "long_range_coherence"
        return "coherence_transition"

    @property
    def explanation(self) -> str:
        return explain_density_mosaic_tile(self)

    @property
    def reason_codes(self) -> list[float]:
        return tile_reason_codes(self)

    def osc_summary(self) -> list[float]:
        return [
            float(self.row),
            float(self.column),
            self.salience,
            self.amplitude,
            self.phase_unit,
            self.probability,
            self.coherence,
            self.distance,
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "row": self.row,
            "column": self.column,
            "basis_from": self.basis_from,
            "basis_to": self.basis_to,
            "amplitude": self.amplitude,
            "phase": self.phase,
            "phase_unit": self.phase_unit,
            "probability": self.probability,
            "coherence": self.coherence,
            "distance": self.distance,
            "salience": self.salience,
            "role": self.role,
            "explanation": self.explanation,
            "query": self.query.to_dict(),
        }


@dataclass(frozen=True)
class DensityMosaicSequence:
    """A contiguous density-matrix run interpreted as an activation sequence."""

    direction: str
    start_row: int
    start_column: int
    end_row: int
    end_column: int
    length: int
    basis_start: str
    basis_end: str
    amplitude: float
    phase_unit: float
    phase_slope: float
    probability: float
    coherence: float
    distance: float
    salience: float
    continuity: float
    query: DescriptorVector

    @property
    def role(self) -> str:
        if self.direction == "diagonal":
            return "source_continuity_run"
        return "mirrored_transition_run"

    @property
    def explanation(self) -> str:
        return explain_density_mosaic_sequence(self)

    @property
    def reason_codes(self) -> list[float]:
        return sequence_reason_codes(self)

    def osc_summary(self) -> list[float]:
        direction_code = 1.0 if self.direction == "diagonal" else -1.0
        return [
            float(self.start_row),
            float(self.start_column),
            float(self.end_row),
            float(self.end_column),
            float(self.length),
            direction_code,
            self.salience,
            self.amplitude,
            self.phase_unit,
            self.phase_slope,
            self.coherence,
            self.distance,
            self.continuity,
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "direction": self.direction,
            "start_row": self.start_row,
            "start_column": self.start_column,
            "end_row": self.end_row,
            "end_column": self.end_column,
            "length": self.length,
            "basis_start": self.basis_start,
            "basis_end": self.basis_end,
            "amplitude": self.amplitude,
            "phase_unit": self.phase_unit,
            "phase_slope": self.phase_slope,
            "probability": self.probability,
            "coherence": self.coherence,
            "distance": self.distance,
            "salience": self.salience,
            "continuity": self.continuity,
            "role": self.role,
            "explanation": self.explanation,
            "query": self.query.to_dict(),
        }


def density_matrix_to_mosaic_tiles(
    rho: np.ndarray,
    *,
    max_tiles: int = 16,
    include_diagonal: bool = True,
    salience_floor: float = 1e-6,
) -> list[DensityMosaicTile]:
    """Convert density-matrix cells into audio-mosaicing target tiles.

    Diagonal cells behave like stable source/grain anchors. Off-diagonal cells
    behave like transitions or cross-synthesis targets whose phase and coherence
    can drive timbral choice.
    """
    rho = np.asarray(rho, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        return []

    dim = rho.shape[0]
    n_qubits = _infer_n_qubits(dim)
    populations = np.clip(np.real(np.diag(rho)), 0.0, 1.0)
    max_amplitude = max(float(np.max(np.abs(rho))), 1e-12)
    tiles: list[DensityMosaicTile] = []

    for row in range(dim):
        for column in range(dim):
            if row == column and not include_diagonal:
                continue
            value = rho[row, column]
            amplitude = float(abs(value) / max_amplitude)
            if amplitude < salience_floor:
                continue
            phase = float(np.angle(value))
            phase_unit = _phase_unit(phase)
            probability = float((populations[row] + populations[column]) * 0.5)
            coherence = 0.0 if row == column else amplitude
            distance = _basis_distance(row, column, n_qubits)
            salience = _cell_salience(row, column, amplitude, probability, coherence)
            query = density_cell_to_audio_query(
                row=row,
                column=column,
                dim=dim,
                n_qubits=n_qubits,
                amplitude=amplitude,
                phase_unit=phase_unit,
                probability=probability,
                coherence=coherence,
                distance=distance,
                salience=salience,
            )
            tiles.append(
                DensityMosaicTile(
                    row=row,
                    column=column,
                    basis_from=format(row, f"0{n_qubits}b") if n_qubits else str(row),
                    basis_to=format(column, f"0{n_qubits}b") if n_qubits else str(column),
                    amplitude=amplitude,
                    phase=phase,
                    phase_unit=phase_unit,
                    probability=probability,
                    coherence=coherence,
                    distance=distance,
                    salience=salience,
                    query=query,
                )
            )

    tiles.sort(key=lambda tile: tile.salience, reverse=True)
    return tiles[:max_tiles]


def density_matrix_to_activation_sequences(
    rho: np.ndarray,
    *,
    max_sequences: int = 8,
    min_length: int = 2,
    salience_floor: float = 0.04,
) -> list[DensityMosaicSequence]:
    """Find sparse diagonal activation runs in a density matrix.

    This mirrors the continuity idea in NMF-inspired audio mosaicing: long,
    salient diagonal structures are treated as better musical targets than
    unrelated isolated cells.
    """
    rho = np.asarray(rho, dtype=np.complex128)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        return []

    dim = rho.shape[0]
    all_tiles = density_matrix_to_mosaic_tiles(
        rho,
        max_tiles=dim * dim,
        include_diagonal=True,
        salience_floor=1e-12,
    )
    tile_by_cell = {(tile.row, tile.column): tile for tile in all_tiles}
    active = {
        cell
        for cell, tile in tile_by_cell.items()
        if tile.salience >= salience_floor
    }

    sequences: list[DensityMosaicSequence] = []
    for direction, starts, step in _sequence_scans(dim):
        for start in starts:
            run: list[DensityMosaicTile] = []
            row, column = start
            while 0 <= row < dim and 0 <= column < dim:
                tile = tile_by_cell.get((row, column))
                if tile is not None and (row, column) in active:
                    run.append(tile)
                else:
                    sequences.extend(
                        _sequence_from_run(direction, run, dim, min_length)
                    )
                    run = []
                row += step[0]
                column += step[1]
            sequences.extend(_sequence_from_run(direction, run, dim, min_length))

    sequences.sort(key=lambda sequence: sequence.salience, reverse=True)
    return sequences[:max_sequences]


def density_sequence_to_audio_query(
    sequence: DensityMosaicSequence | None,
    tiles: list[DensityMosaicTile],
    *,
    dim: int,
) -> DescriptorVector:
    """Map a density-matrix activation sequence into audio descriptor space."""
    if not tiles:
        values = np.zeros(len(AUDIO_FEATURE_NAMES), dtype=float)
        metadata = {"kind": "density_mosaic_sequence_query", "empty": True}
        identifier = "rho_sequence_empty_query"
    else:
        weights = np.asarray([max(tile.salience, 1e-9) for tile in tiles], dtype=float)
        weights = weights / np.sum(weights)
        tile_values = np.vstack([tile.query.values for tile in tiles])
        values = np.average(tile_values, axis=0, weights=weights)
        if sequence is not None:
            values[1] = _clip01(0.25 + 0.70 * sequence.continuity)
            values[2] = _clip01(0.10 + 0.80 * sequence.amplitude)
            values[4] = _clip01(0.15 + 0.60 * sequence.distance + 0.20 * sequence.length / dim)
            values[7] = _clip01(0.20 + 0.70 * sequence.salience)
            values[9] = _clip01(0.10 + 0.75 * abs(sequence.phase_slope))
            values[-1] = _clip01(0.10 + 0.70 * sequence.length / dim + 0.25 * sequence.coherence)
            identifier = (
                f"rho_sequence_{sequence.start_row}_{sequence.start_column}_"
                f"{sequence.end_row}_{sequence.end_column}_query"
            )
            metadata = {
                "kind": "density_mosaic_sequence_query",
                "direction": sequence.direction,
                "length": sequence.length,
            }
        else:
            identifier = "rho_sequence_query"
            metadata = {"kind": "density_mosaic_sequence_query"}

    return DescriptorVector(
        identifier=identifier,
        names=AUDIO_FEATURE_NAMES,
        values=np.asarray(values, dtype=float),
        metadata=metadata,
    )


def explain_density_mosaic_tile(tile: DensityMosaicTile) -> str:
    """Short human-readable reason for a density-mosaic tile selection."""
    cell = f"rho[{tile.row},{tile.column}]"
    if tile.row == tile.column:
        return (
            f"{cell} is a diagonal probability anchor for |{tile.basis_from}>; "
            f"salience {tile.salience:.2f} comes from population {tile.probability:.2f} "
            f"and amplitude {tile.amplitude:.2f}."
        )

    transition = f"|{tile.basis_from}> -> |{tile.basis_to}>"
    if tile.distance >= 0.75:
        distance_reason = "large basis distance suggests a dramatic transition"
    elif tile.distance >= 0.35:
        distance_reason = "moderate basis distance suggests a related transition"
    else:
        distance_reason = "small basis distance suggests a close-neighbour transition"

    if tile.phase_unit > 0.66:
        phase_reason = "positive phase biases the query brighter/forward"
    elif tile.phase_unit < 0.34:
        phase_reason = "negative phase biases the query darker/reversed"
    else:
        phase_reason = "near-centre phase keeps the query stable"

    return (
        f"{cell} is off-diagonal coherence for {transition}; "
        f"coherence {tile.coherence:.2f} and amplitude {tile.amplitude:.2f} make it active, "
        f"{distance_reason}, and {phase_reason}."
    )


def explain_density_mosaic_sequence(sequence: DensityMosaicSequence) -> str:
    """Short human-readable reason for an activation-sequence selection."""
    start = f"rho[{sequence.start_row},{sequence.start_column}]"
    end = f"rho[{sequence.end_row},{sequence.end_column}]"
    if sequence.direction == "diagonal":
        direction_reason = "a diagonal activation run, so it can preserve source continuity"
    else:
        direction_reason = "an anti-diagonal run, so it behaves like a mirrored transition"

    if abs(sequence.phase_slope) >= 0.4:
        phase_reason = "strong phase slope suggests a changing spectral color"
    elif abs(sequence.phase_slope) >= 0.15:
        phase_reason = "gentle phase slope suggests gradual color motion"
    else:
        phase_reason = "flat phase keeps the sequence stable"

    return (
        f"{start} to {end} is {direction_reason}; length {sequence.length}, "
        f"continuity {sequence.continuity:.2f}, salience {sequence.salience:.2f}, "
        f"and {phase_reason}."
    )


def tile_reason_codes(tile: DensityMosaicTile) -> list[float]:
    """Numeric explanation vector for Max/Processing.

    [is_diagonal, salience, amplitude, probability, coherence, distance, phase_unit]
    """
    return [
        1.0 if tile.row == tile.column else 0.0,
        tile.salience,
        tile.amplitude,
        tile.probability,
        tile.coherence,
        tile.distance,
        tile.phase_unit,
    ]


def sequence_reason_codes(sequence: DensityMosaicSequence) -> list[float]:
    """Numeric explanation vector for Max/Processing.

    [is_diagonal_run, salience, amplitude, coherence, distance, continuity, phase_slope]
    """
    return [
        1.0 if sequence.direction == "diagonal" else 0.0,
        sequence.salience,
        sequence.amplitude,
        sequence.coherence,
        sequence.distance,
        sequence.continuity,
        sequence.phase_slope,
    ]


def density_mosaic_explanation(
    rho: np.ndarray,
    *,
    max_tiles: int = 4,
    max_sequences: int = 2,
) -> dict[str, Any]:
    """Build a compact pedagogical explanation of the current density mosaic."""
    tiles = density_matrix_to_mosaic_tiles(rho, max_tiles=max_tiles)
    sequences = density_matrix_to_activation_sequences(rho, max_sequences=max_sequences)
    return {
        "tiles": [tile.to_dict() for tile in tiles],
        "sequences": [sequence.to_dict() for sequence in sequences],
        "summary": summarize_density_mosaic(tiles, sequences),
    }


def summarize_density_mosaic(
    tiles: list[DensityMosaicTile],
    sequences: list[DensityMosaicSequence],
) -> str:
    if not tiles and not sequences:
        return "No salient density-mosaic activity is currently available."

    diagonal_tiles = sum(1 for tile in tiles if tile.row == tile.column)
    coherence_tiles = len(tiles) - diagonal_tiles
    longest = max((sequence.length for sequence in sequences), default=0)
    strongest_tile = tiles[0] if tiles else None
    strongest_sequence = sequences[0] if sequences else None

    parts = [
        f"{diagonal_tiles} probability anchors and {coherence_tiles} coherence tiles are active"
    ]
    if strongest_tile is not None:
        parts.append(
            f"strongest cell rho[{strongest_tile.row},{strongest_tile.column}] "
            f"has salience {strongest_tile.salience:.2f}"
        )
    if strongest_sequence is not None:
        parts.append(
            f"strongest sequence spans {strongest_sequence.length} cells "
            f"with continuity {strongest_sequence.continuity:.2f}"
        )
    elif longest:
        parts.append(f"longest sequence spans {longest} cells")
    return "; ".join(parts) + "."


def density_cell_to_audio_query(
    *,
    row: int,
    column: int,
    dim: int,
    n_qubits: int,
    amplitude: float,
    phase_unit: float,
    probability: float,
    coherence: float,
    distance: float,
    salience: float,
) -> DescriptorVector:
    """Map one density-matrix cell into the audio descriptor space."""
    row_unit = row / max(dim - 1, 1)
    column_unit = column / max(dim - 1, 1)
    diagonal = 1.0 if row == column else 0.0
    transition = 1.0 - diagonal
    mirror = 1.0 - abs(row - column) / max(dim - 1, 1)

    mfcc_shape = [
        row_unit,
        column_unit,
        phase_unit,
        amplitude,
        probability,
        coherence,
        distance,
        salience,
        diagonal,
        transition,
        mirror,
        _clip01((row ^ column) / max(dim - 1, 1)),
        _clip01((row + column) / max(2 * (dim - 1), 1)),
    ]

    values = np.asarray(
        [
            _clip01(0.15 + 0.70 * row_unit),
            _clip01(0.25 + 0.65 * probability),
            _clip01(0.08 + 0.82 * amplitude),
            _clip01(0.15 + 0.65 * phase_unit + 0.20 * column_unit),
            _clip01(0.12 + 0.60 * distance + 0.20 * coherence),
            _clip01(phase_unit * 2.0 - 1.0),
            _clip01(0.18 + 0.72 * coherence),
            _clip01(0.15 + 0.65 * salience),
            _clip01(0.10 + 0.70 * transition + 0.15 * distance),
            _clip01(0.10 + 0.70 * salience + 0.20 * coherence),
            *[_clip01(value) for value in mfcc_shape],
            _clip01(0.08 + 0.72 * distance + 0.25 * coherence),
        ],
        dtype=float,
    )

    return DescriptorVector(
        identifier=f"rho_{row}_{column}_query",
        names=AUDIO_FEATURE_NAMES,
        values=values,
        metadata={
            "kind": "density_mosaic_query",
            "row": row,
            "column": column,
            "n_qubits": n_qubits,
        },
    )


def _sequence_scans(
    dim: int,
) -> list[tuple[str, list[tuple[int, int]], tuple[int, int]]]:
    diagonal_starts = [(0, column) for column in range(dim)]
    diagonal_starts.extend((row, 0) for row in range(1, dim))
    anti_starts = [(0, column) for column in range(dim)]
    anti_starts.extend((row, dim - 1) for row in range(1, dim))
    return [
        ("diagonal", diagonal_starts, (1, 1)),
        ("anti_diagonal", anti_starts, (1, -1)),
    ]


def _sequence_from_run(
    direction: str,
    run: list[DensityMosaicTile],
    dim: int,
    min_length: int,
) -> list[DensityMosaicSequence]:
    if len(run) < min_length:
        return []

    phases = np.unwrap([tile.phase for tile in run])
    phase_slope = 0.0
    if len(phases) > 1:
        phase_slope = float(np.clip(np.mean(np.diff(phases)) / math.pi, -1.0, 1.0))
    phase_unit = _phase_unit(float(np.angle(np.mean([np.exp(1j * tile.phase) for tile in run]))))

    amplitude = float(np.mean([tile.amplitude for tile in run]))
    probability = float(np.mean([tile.probability for tile in run]))
    coherence = float(np.mean([tile.coherence for tile in run]))
    distance = float(np.mean([tile.distance for tile in run]))
    base_salience = float(np.mean([tile.salience for tile in run]))
    continuity = float(np.clip((len(run) - 1) / max(dim - 1, 1), 0.0, 1.0))
    length_bonus = math.sqrt(min(len(run), dim) / dim)
    salience = _clip01(base_salience * (0.72 + 0.28 * length_bonus) + 0.18 * continuity)

    sequence_shell = DensityMosaicSequence(
        direction=direction,
        start_row=run[0].row,
        start_column=run[0].column,
        end_row=run[-1].row,
        end_column=run[-1].column,
        length=len(run),
        basis_start=run[0].basis_from,
        basis_end=run[-1].basis_to,
        amplitude=amplitude,
        phase_unit=phase_unit,
        phase_slope=phase_slope,
        probability=probability,
        coherence=coherence,
        distance=distance,
        salience=salience,
        continuity=continuity,
        query=DescriptorVector(
            identifier="pending_sequence_query",
            names=AUDIO_FEATURE_NAMES,
            values=np.zeros(len(AUDIO_FEATURE_NAMES), dtype=float),
        ),
    )
    query = density_sequence_to_audio_query(sequence_shell, run, dim=dim)
    return [
        DensityMosaicSequence(
            direction=sequence_shell.direction,
            start_row=sequence_shell.start_row,
            start_column=sequence_shell.start_column,
            end_row=sequence_shell.end_row,
            end_column=sequence_shell.end_column,
            length=sequence_shell.length,
            basis_start=sequence_shell.basis_start,
            basis_end=sequence_shell.basis_end,
            amplitude=sequence_shell.amplitude,
            phase_unit=sequence_shell.phase_unit,
            phase_slope=sequence_shell.phase_slope,
            probability=sequence_shell.probability,
            coherence=sequence_shell.coherence,
            distance=sequence_shell.distance,
            salience=sequence_shell.salience,
            continuity=sequence_shell.continuity,
            query=query,
        )
    ]


def _infer_n_qubits(dim: int) -> int:
    n_qubits = int(round(math.log2(dim))) if dim > 0 else 0
    return n_qubits if 2**n_qubits == dim else 0


def _phase_unit(phase: float) -> float:
    return float(np.clip((phase + math.pi) / (2.0 * math.pi), 0.0, 1.0))


def _basis_distance(row: int, column: int, n_qubits: int) -> float:
    if n_qubits <= 0:
        return 0.0 if row == column else 1.0
    return float((row ^ column).bit_count() / n_qubits)


def _cell_salience(
    row: int,
    column: int,
    amplitude: float,
    probability: float,
    coherence: float,
) -> float:
    if row == column:
        return _clip01(0.55 * probability + 0.45 * amplitude)
    return _clip01(0.20 * probability + 0.50 * coherence + 0.30 * amplitude)
