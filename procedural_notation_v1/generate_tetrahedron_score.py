"""Generate a 32nd-note musical cell from a regular 3D tetrahedron."""

from pathlib import Path

from procedural_notation_v1 import (
    apply_pitch_mapping,
    build_score,
    build_tetrahedron_graph,
    write_musicxml,
)


TETRAHEDRON_PITCHES = ("C5", "C4", "E4", "G#4")
TETRAHEDRON_PATH = (1, 2, 0, 3)


def main() -> Path:
    graph = build_tetrahedron_graph()
    graph.graph.update(
        pitch_system="24-EDO",
        pitch_divisions=24,
        rhythm_subdivisions_per_quarter=8,
        rhythm_note_value=32,
    )
    graph = apply_pitch_mapping(graph, TETRAHEDRON_PITCHES)
    score = build_score(
        graph,
        node_path=TETRAHEDRON_PATH,
        quarter_length=0.125,
        time_signature="1/8",
        title="Tetrahedral Cell No. 1",
    )
    output = Path(__file__).parent / "output" / "tetrahedral_cell_1.musicxml"
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
