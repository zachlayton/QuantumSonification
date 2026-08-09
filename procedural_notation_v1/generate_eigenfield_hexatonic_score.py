"""Generate an octave-displaced hexatonic Laplacian eigenfield line."""

from pathlib import Path

from procedural_notation_v1 import build_timed_score, write_musicxml
from procedural_notation_v1.eigenfield_graph import (
    OCTAVE_DISPLACED_HEXATONIC_LINE,
    apply_eigenfield_line_mapping,
    build_laplacian_eigenfield_graph,
)


def main() -> Path:
    graph = apply_eigenfield_line_mapping(
        build_laplacian_eigenfield_graph(),
        pitches=OCTAVE_DISPLACED_HEXATONIC_LINE,
    )
    score = build_timed_score(
        graph,
        measures=2,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title="Hexatonic Eigenfield Line No. 2",
        include_node_labels=False,
    )
    output = (
        Path(__file__).parent
        / "output"
        / "laplacian_eigenfield_hexatonic_octaves_2.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
