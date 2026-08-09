"""Generate numerically grouped phrases from the octave-displaced eigenfield."""

from pathlib import Path

from procedural_notation_v1 import build_timed_score, write_musicxml
from procedural_notation_v1.eigenfield_graph import (
    OCTAVE_DISPLACED_HEXATONIC_LINE,
    apply_eigenfield_line_mapping,
    build_laplacian_eigenfield_graph,
)
from procedural_notation_v1.eigenfield_phrase import build_numerical_phrase_graph


def main() -> Path:
    eigenfield = apply_eigenfield_line_mapping(
        build_laplacian_eigenfield_graph(),
        pitches=OCTAVE_DISPLACED_HEXATONIC_LINE,
    )
    phrases = build_numerical_phrase_graph(eigenfield)
    score = build_timed_score(
        phrases,
        measures=3,
        beats_per_measure=3,
        ticks_per_quarter=8,
        title="Eigenfield Numerical Phrases No. 3",
        include_node_labels=False,
    )
    output = (
        Path(__file__).parent
        / "output"
        / "laplacian_eigenfield_numerical_phrases_3.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
