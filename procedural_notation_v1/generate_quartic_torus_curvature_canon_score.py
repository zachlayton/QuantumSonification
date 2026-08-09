"""Generate a torus canon accelerated and elongated by Gaussian curvature."""

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
        curvature_motion=True,
    )
    measures = math.ceil(canon.graph["total_ticks"] / 32)
    score = build_polyphonic_timed_score(
        canon,
        measures=measures,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title="Quartic Torus Curvature Canon No. 8",
        include_node_labels=False,
    )
    first_event_by_voice = {}
    for _, data in canon.nodes(data=True):
        first_event_by_voice.setdefault(data["voice"], data)
    for part, voice_id in zip(score.parts, sorted(canon.graph["voices"]), strict=True):
        data = first_event_by_voice[voice_id]
        family, number = voice_id.split("_")[1:]
        part.partName = (
            f"{family.title()} {int(number)} — entry "
            f"{data['canon_entry_index'] + 1}, ×{data['mensuration_factor']}"
        )
    output = (
        Path(__file__).parent
        / "output"
        / "quartic_torus_32_voice_curvature_canon_8.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
