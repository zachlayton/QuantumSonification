"""Generate the first algebraic-surface MusicXML study."""

from pathlib import Path

from procedural_notation_v1 import build_timed_score, write_musicxml
from procedural_notation_v1.surface_mesh_graph import (
    apply_torus_hexatonic_mapping,
    build_quartic_torus_mesh,
)


def main() -> Path:
    mesh = apply_torus_hexatonic_mapping(build_quartic_torus_mesh())
    score = build_timed_score(
        mesh,
        measures=5,
        beats_per_measure=3,
        ticks_per_quarter=8,
        title="Quartic Torus Surface Study No. 4",
        include_node_labels=False,
    )
    output = (
        Path(__file__).parent
        / "output"
        / "quartic_torus_hexatonic_surface_4.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
