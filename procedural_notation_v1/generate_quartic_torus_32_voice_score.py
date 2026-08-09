"""Generate a literal 32-voice musical mesh from a quartic torus."""

from pathlib import Path

from procedural_notation_v1 import build_polyphonic_timed_score, write_musicxml
from procedural_notation_v1.surface_mesh_ensemble import build_torus_32_voice_mesh
from procedural_notation_v1.surface_mesh_graph import build_quartic_torus_mesh


def main() -> Path:
    mesh = build_quartic_torus_mesh(major_segments=16, minor_segments=16)
    ensemble = build_torus_32_voice_mesh(mesh)
    score = build_polyphonic_timed_score(
        ensemble,
        measures=1,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title="Quartic Torus 32-Voice Mesh Study No. 6",
        include_node_labels=False,
    )
    for part, voice_id in zip(score.parts, sorted(ensemble.graph["voices"]), strict=True):
        family, number = voice_id.split("_")[1:]
        part.partName = f"{family.title()} {int(number)}"
    output = (
        Path(__file__).parent
        / "output"
        / "quartic_torus_32_voice_mesh_6.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
