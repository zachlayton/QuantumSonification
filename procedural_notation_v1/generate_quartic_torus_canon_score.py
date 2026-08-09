"""Generate a rotating 32-entry double canon from a quartic torus mesh."""

from __future__ import annotations

import math
from pathlib import Path

from procedural_notation_v1 import build_polyphonic_timed_score, write_musicxml
from procedural_notation_v1.surface_mesh_graph import build_quartic_torus_mesh
from procedural_notation_v1.surface_mesh_motion import build_torus_32_voice_rotating_mesh


def main() -> Path:
    surface = build_quartic_torus_mesh(major_segments=16, minor_segments=16)
    canon = build_torus_32_voice_rotating_mesh(
        surface,
        rotations=4,
        canon_entry_ticks=1,
    )
    measure_ticks = 4 * 8
    measures = math.ceil(canon.graph["total_ticks"] / measure_ticks)
    score = build_polyphonic_timed_score(
        canon,
        measures=measures,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title="Quartic Torus 32-Voice Spiral Canon No. 7",
        include_node_labels=False,
    )
    for part, voice_id in zip(score.parts, sorted(canon.graph["voices"]), strict=True):
        family, number = voice_id.split("_")[1:]
        entry_index = next(
            data["canon_entry_index"]
            for _, data in canon.nodes(data=True)
            if data["voice"] == voice_id
        )
        mensuration = next(
            data["mensuration_factor"]
            for _, data in canon.nodes(data=True)
            if data["voice"] == voice_id
        )
        part.partName = (
            f"{family.title()} {int(number)} — entry {entry_index + 1}, ×{mensuration}"
        )
    output = (
        Path(__file__).parent
        / "output"
        / "quartic_torus_32_voice_spiral_canon_7.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
