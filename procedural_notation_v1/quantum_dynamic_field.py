"""Map four-qubit density-matrix evolution to notated dynamic contrast."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

import networkx as nx
import numpy as np

from procedural_notation_v1.density_matrix_field import (
    build_density_matrix_snapshots,
    density_matrix_purity,
)


DEFAULT_EVOLUTION_TIMES = tuple(0.2 + 0.25 * index for index in range(8))
DYNAMIC_LEVELS = ("ppp", "pp", "p", "mp", "mf", "f", "ff")
DYNAMIC_QUANTILES = (0.10, 0.25, 0.40, 0.60, 0.75, 0.90)


def apply_quantum_dynamic_contrast(
    graph: nx.DiGraph,
    density_snapshots: Sequence[np.ndarray] | None = None,
) -> nx.DiGraph:
    """Return a copy with density-derived dynamics, accents, and provenance.

    Population supplies most of the intensity.  Coherence supplies the rest,
    allowing off-diagonal quantum structure to articulate local peaks that the
    pitch/rhythm mappings do not already expose.
    """
    snapshots = tuple(
        build_density_matrix_snapshots(DEFAULT_EVOLUTION_TIMES)
        if density_snapshots is None
        else density_snapshots
    )
    if not snapshots:
        raise ValueError("density_snapshots must not be empty")
    for density in snapshots:
        if density.shape != (16, 16) or not np.all(np.isfinite(density)):
            raise ValueError("each density snapshot must be a finite 16 by 16 matrix")

    required = {
        "pitch_digit",
        "sector",
        "path_index",
        "rotation_index",
        "canon_entry_index",
        "source_vertex",
        "voice",
        "onset_tick",
    }
    mapped = graph.copy()
    measurements: dict[object, dict[str, float | int]] = {}
    for node_id, data in mapped.nodes(data=True):
        if not required <= data.keys():
            raise ValueError(f"node {node_id!r} lacks quantum-dynamic coordinates")
        snapshot_index = int(data["rotation_index"]) % len(snapshots)
        density = snapshots[snapshot_index]
        basis_index = (
            int(data["pitch_digit"])
            + 2 * int(data["sector"])
            + int(data["path_index"])
        ) % 16
        ring_index = int(data["source_vertex"][0])
        partner_index = (
            basis_index
            + 1
            + int(data["canon_entry_index"])
            + ring_index
        ) % 16

        populations = np.real(np.diag(density))
        maximum_population = float(np.max(populations))
        coherences = np.abs(density - np.diag(np.diag(density)))
        maximum_coherence = float(np.max(coherences))
        normalized_population = float(populations[basis_index] / maximum_population)
        normalized_coherence = (
            float(abs(density[basis_index, partner_index]) / maximum_coherence)
            if maximum_coherence > 0.0
            else 0.0
        )
        intensity = (
            0.68 * np.sqrt(max(0.0, normalized_population))
            + 0.32 * np.sqrt(max(0.0, normalized_coherence))
        )
        measurements[node_id] = {
            "snapshot_index": snapshot_index,
            "basis_index": basis_index,
            "partner_index": partner_index,
            "population": normalized_population,
            "coherence": normalized_coherence,
            "intensity": float(intensity),
        }

    intensities = np.asarray(
        [measurement["intensity"] for measurement in measurements.values()],
        dtype=float,
    )
    thresholds = np.quantile(intensities, DYNAMIC_QUANTILES)
    for node_id, measurement in measurements.items():
        dynamic_index = int(
            np.searchsorted(thresholds, measurement["intensity"], side="right")
        )
        mapped.nodes[node_id].update(
            quantum_snapshot_index=measurement["snapshot_index"],
            quantum_basis_index=measurement["basis_index"],
            quantum_partner_index=measurement["partner_index"],
            quantum_population=measurement["population"],
            quantum_coherence=measurement["coherence"],
            quantum_intensity=measurement["intensity"],
            dynamic_level=DYNAMIC_LEVELS[dynamic_index],
            dynamic_level_index=dynamic_index,
            dynamic_mark=None,
            accent_type=None,
        )

    # Dynamic symbols occur at each radial breath and at its outer boundary.
    # Repeated levels are suppressed, leaving a legible phrase-scale contour.
    voices = sorted({data["voice"] for _, data in mapped.nodes(data=True)})
    for voice_id in voices:
        last_notated_level = None
        for node_id, data in _voice_events(mapped, voice_id):
            level = data["dynamic_level"]
            if data["path_index"] in (0, 3) and level != last_notated_level:
                mapped.nodes[node_id]["dynamic_mark"] = level
                last_notated_level = level

    deltas = []
    for voice_id in voices:
        previous_intensity = None
        for _, data in _voice_events(mapped, voice_id):
            intensity = float(data["quantum_intensity"])
            if previous_intensity is not None:
                deltas.append(intensity - previous_intensity)
            previous_intensity = intensity
    accent_delta = float(np.quantile(np.asarray(deltas), 0.82))
    strong_threshold = float(np.quantile(intensities, 0.94))
    median_intensity = float(np.median(intensities))
    for voice_id in voices:
        previous_intensity = None
        for node_id, data in _voice_events(mapped, voice_id):
            intensity = float(data["quantum_intensity"])
            delta = 0.0 if previous_intensity is None else intensity - previous_intensity
            if intensity >= strong_threshold:
                mapped.nodes[node_id]["accent_type"] = "strong-accent"
            elif delta >= accent_delta and intensity >= median_intensity:
                mapped.nodes[node_id]["accent_type"] = "accent"
            previous_intensity = intensity

    accent_counts = Counter(
        data["accent_type"]
        for _, data in mapped.nodes(data=True)
        if data["accent_type"] is not None
    )
    mapped.graph.update(
        quantum_dynamic_source="four-qubit interacting density-matrix evolution",
        quantum_dynamic_evolution_times=DEFAULT_EVOLUTION_TIMES,
        quantum_dynamic_snapshot_count=len(snapshots),
        quantum_dynamic_snapshot_purities=tuple(
            density_matrix_purity(density) for density in snapshots
        ),
        quantum_dynamic_formula=(
            "0.68*sqrt(normalized population) + "
            "0.32*sqrt(normalized coherence)"
        ),
        quantum_dynamic_levels=DYNAMIC_LEVELS,
        quantum_dynamic_thresholds=tuple(float(value) for value in thresholds),
        quantum_dynamic_mark_count=sum(
            data["dynamic_mark"] is not None for _, data in mapped.nodes(data=True)
        ),
        quantum_accent_counts=dict(accent_counts),
        quantum_accent_delta_threshold=accent_delta,
        quantum_strong_accent_threshold=strong_threshold,
    )
    return mapped


def _voice_events(graph: nx.DiGraph, voice_id: str) -> list[tuple[object, dict]]:
    return sorted(
        (
            (node_id, data)
            for node_id, data in graph.nodes(data=True)
            if data["voice"] == voice_id
        ),
        key=lambda item: item[1]["onset_tick"],
    )
