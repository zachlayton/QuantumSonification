"""Generate a three-voice, 12-EDO dodecahedral MusicXML score."""

from pathlib import Path

from procedural_notation_v1 import (
    build_dodecahedron_graph,
    build_polyphonic_timed_score,
    write_musicxml,
)
from procedural_notation_v1.dodecahedron_score import apply_polyphonic_dodecahedron_mapping


def main() -> Path:
    graph = apply_polyphonic_dodecahedron_mapping(build_dodecahedron_graph())
    score = build_polyphonic_timed_score(
        graph,
        measures=graph.graph["measures"],
        beats_per_measure=graph.graph["beats_per_measure"],
        ticks_per_quarter=graph.graph["rhythm_subdivisions_per_quarter"],
        title="Dodecahedral Pentatonic Cycles No. 1",
    )
    output = (
        Path(__file__).parent
        / "output"
        / "dodecahedral_pentatonic_cycles_1.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
