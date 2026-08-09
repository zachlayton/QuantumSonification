"""Generate a repeated-note melodic line from a Laplacian eigenfield."""

from pathlib import Path

from procedural_notation_v1 import build_timed_score, write_musicxml
from procedural_notation_v1.eigenfield_graph import (
    apply_eigenfield_line_mapping,
    build_laplacian_eigenfield_graph,
)


def main() -> Path:
    graph = apply_eigenfield_line_mapping(build_laplacian_eigenfield_graph())
    score = build_timed_score(
        graph,
        measures=2,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title="Laplacian Eigenfield Line No. 1",
        include_node_labels=False,
    )
    output = Path(__file__).parent / "output" / "laplacian_eigenfield_line_1.musicxml"
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
