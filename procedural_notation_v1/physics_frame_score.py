"""Offline musical projection of a captured live PhysicsFrame (no engine mutation)."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Sequence

import numpy as np

from qmw.core.physics_frame import PhysicsFrame
from procedural_notation_v1 import build_polyphonic_timed_score, write_musicxml
from procedural_notation_v1.density_matrix_canon import build_density_matrix_cable_net_canon
from procedural_notation_v1.tensile_surface_graph import build_tensile_saddle_mesh


def build_physics_frame_canon(
    frame: PhysicsFrame, *, snapshot_count: int = 4,
    sample_indices: Sequence[int] | None = None,
    ticks_per_time_unit: float | None = None,
    quantization_ticks: int = 1, slot_ticks: int = 4,
    coherence_threshold: float = 0.08,
):
    """Select actual samples, then project elapsed physical time to score ticks.

    Explicit indices override snapshot_count. Automatic selection spans the
    entire frame in sample-index space. No interpolation or state repair occurs.
    Default time scale makes the shortest selected interval 68 ticks (at the
    default slot size); all other intervals retain their relative lengths up
    to nearest-grid rounding. Explicit scales that cause overlap are rejected.
    """
    t = np.asarray(frame.t)
    if not np.all(np.isfinite(t)) or np.any(np.diff(t) <= 0):
        raise ValueError("frame times must be finite and strictly increasing")
    if frame.rho is None or frame.rho.shape != (frame.samples, 16, 16):
        raise ValueError("a four-qubit rho trajectory is required")
    for name, value in (("quantization_ticks", quantization_ticks), ("slot_ticks", slot_ticks)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    if slot_ticks < 4:
        raise ValueError("slot_ticks must be >= 4 to avoid phase/duration overlaps")
    if sample_indices is None:
        if (isinstance(snapshot_count, bool) or not isinstance(snapshot_count, int)
                or not 1 <= snapshot_count <= frame.samples):
            raise ValueError("snapshot_count must lie between 1 and frame.samples")
        indices = np.rint(np.linspace(0, frame.samples - 1, snapshot_count)).astype(int)
    else:
        raw = list(sample_indices)
        if not raw or any(isinstance(i, (bool, np.bool_)) or not isinstance(i, (int, np.integer)) for i in raw):
            raise ValueError("sample_indices must be nonempty integers")
        indices = np.asarray(raw, dtype=int)
        if np.any(indices < 0) or np.any(indices >= frame.samples) or np.any(np.diff(indices) <= 0):
            raise ValueError("sample_indices must be in range and strictly increasing")
    times = t[indices].copy()
    elapsed = times - times[0]
    if ticks_per_time_unit is None:
        scale = ((16 * slot_ticks + max(4, quantization_ticks)) / np.min(np.diff(times))
                 if len(times) > 1 else 1.0)
    else:
        scale = float(ticks_per_time_unit)
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("ticks_per_time_unit must be finite and positive")
    ideal = elapsed * scale
    quantized = np.floor(ideal / quantization_ticks + 0.5) * quantization_ticks
    if not np.all(np.isfinite(quantized)):
        raise ValueError("mapped score times must be finite")
    onsets = tuple(int(v) for v in quantized)
    graph = build_density_matrix_cable_net_canon(
        build_tensile_saddle_mesh(), [frame.rho[i].copy() for i in indices],
        coherence_threshold=coherence_threshold, slot_ticks=slot_ticks,
        snapshot_onset_ticks=onsets,
    )
    provenance = {
        "frame_samples": frame.samples,
        "frame_start_time": float(t[0]), "frame_end_time": float(t[-1]),
        "sample_indices": indices.tolist(), "physical_times": times.tolist(),
        "physical_elapsed": elapsed.tolist(), "ticks_per_time_unit": float(scale),
        "quantization_ticks": quantization_ticks, "snapshot_onset_ticks": list(onsets),
        "quantization_error_ticks": (quantized - ideal).tolist(),
        "slot_ticks": slot_ticks, "coherence_threshold": coherence_threshold,
        "ticks_per_quarter": 8,
    }
    graph.graph["physics_frame_projection"] = provenance
    for _, event in graph.nodes(data=True):
        i = event["snapshot_index"]
        event["source_sample_index"] = int(indices[i])
        event["source_physical_time"] = float(times[i])
    return graph


def write_physics_frame_score(frame: PhysicsFrame, output: str | Path, **options) -> Path:
    """Export MusicXML plus a .timing.json provenance sidecar."""
    graph = build_physics_frame_canon(frame, **options)
    score = build_polyphonic_timed_score(
        graph, measures=math.ceil(graph.graph["total_ticks"] / 32),
        beats_per_measure=4, ticks_per_quarter=8,
        title="QMW PhysicsFrame Cable-Net Canon", include_node_labels=False,
    )
    for part, voice in zip(score.parts, sorted(graph.graph["voices"]), strict=True):
        part.partName = voice
    output = write_musicxml(score, output)
    output.with_suffix(".timing.json").write_text(
        json.dumps(graph.graph["physics_frame_projection"], indent=2) + "\n",
        encoding="utf-8",
    )
    return output
