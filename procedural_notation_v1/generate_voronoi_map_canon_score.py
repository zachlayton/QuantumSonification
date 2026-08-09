"""Generate a twelve-voice score from a centroidal Voronoi map."""

from __future__ import annotations

import math
from pathlib import Path

from procedural_notation_v1 import build_polyphonic_timed_score, write_musicxml
from procedural_notation_v1.voronoi_map_canon import build_voronoi_adjacency_canon
from procedural_notation_v1.voronoi_map_graph import build_centroidal_voronoi_map


def main() -> Path:
    canon = build_voronoi_adjacency_canon(build_centroidal_voronoi_map())
    measures = math.ceil(canon.graph["total_ticks"] / 32)
    score = build_polyphonic_timed_score(
        canon,
        measures=measures,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title="Centroidal Voronoi Adjacency Canon No. 13",
        include_node_labels=False,
    )
    for part, voice_id in zip(score.parts, sorted(canon.graph["voices"]), strict=True):
        region_number = int(voice_id.split("_")[1])
        part.partName = f"Voronoi region {region_number}"
    output = (
        Path(__file__).parent
        / "output"
        / "centroidal_voronoi_12_voice_canon_13.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
