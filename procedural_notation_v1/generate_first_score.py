"""Generate the first deterministic graph-derived MusicXML score."""

from pathlib import Path

from procedural_notation_v1 import (
    apply_pitch_mapping,
    build_regular_polygon_graph,
    build_score,
    write_musicxml,
)


def main() -> Path:
    graph = apply_pitch_mapping(build_regular_polygon_graph())
    score = build_score(graph)
    output = Path(__file__).parent / "output" / "regular_octagon_study_1.musicxml"
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
