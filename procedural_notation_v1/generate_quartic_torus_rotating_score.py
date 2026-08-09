"""Generate a 32-voice torus animated by rhythmic and registral motion."""

from __future__ import annotations

import math
from pathlib import Path

from procedural_notation_v1 import build_polyphonic_timed_score, write_musicxml
from procedural_notation_v1.surface_mesh_graph import build_quartic_torus_mesh
from procedural_notation_v1.surface_mesh_motion import build_torus_32_voice_rotating_mesh


def main() -> Path:
    surface = build_quartic_torus_mesh(major_segments=16, minor_segments=16)
    motion = build_torus_32_voice_rotating_mesh(surface, rotations=4)
    measure_ticks = 4 * 8
    measures = math.ceil(motion.graph["total_ticks"] / measure_ticks)
    score = build_polyphonic_timed_score(
        motion,
        measures=measures,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title="Quartic Torus Rotating Mesh Study No. 7",
        include_node_labels=False,
    )
    for part, voice_id in zip(score.parts, sorted(motion.graph["voices"]), strict=True):
        family, number = voice_id.split("_")[1:]
        part.partName = f"{family.title()} {int(number)}"
    output = (
        Path(__file__).parent
        / "output"
        / "quartic_torus_32_voice_rotating_mesh_7.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
