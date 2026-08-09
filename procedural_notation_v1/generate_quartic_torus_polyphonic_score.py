"""Generate a two-voice score from the torus's independent coordinate cycles."""

from pathlib import Path

from procedural_notation_v1 import build_polyphonic_timed_score, write_musicxml
from procedural_notation_v1.surface_mesh_graph import build_quartic_torus_mesh
from procedural_notation_v1.surface_mesh_polyphony import build_torus_dual_cycle_polyphony


def main() -> Path:
    polyphony = build_torus_dual_cycle_polyphony(build_quartic_torus_mesh())
    score = build_polyphonic_timed_score(
        polyphony,
        measures=5,
        beats_per_measure=3,
        ticks_per_quarter=8,
        title="Quartic Torus Dual-Cycle Study No. 5",
        include_node_labels=False,
    )
    score.parts[0].partName = "Major-cycle voice — hexatonic"
    score.parts[1].partName = "Minor-cycle voice — pentatonic"
    output = (
        Path(__file__).parent
        / "output"
        / "quartic_torus_dual_cycle_polyphony_5.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
