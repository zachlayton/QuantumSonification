"""Generate a four-measure MusicXML study from a regular dodecahedron."""

from pathlib import Path

from procedural_notation_v1 import build_dodecahedron_graph, build_timed_score, write_musicxml
from procedural_notation_v1.dodecahedron_score import apply_dodecahedron_mapping


def main() -> Path:
    graph = apply_dodecahedron_mapping(build_dodecahedron_graph())
    score = build_timed_score(
        graph,
        measures=graph.graph["measures"],
        beats_per_measure=graph.graph["beats_per_measure"],
        ticks_per_quarter=graph.graph["rhythm_subdivisions_per_quarter"],
        title="Dodecahedral Time Field No. 1",
    )
    output = Path(__file__).parent / "output" / "dodecahedral_time_field_1.musicxml"
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
