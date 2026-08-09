"""Generate a four-qubit density-matrix cable-net score."""

from __future__ import annotations

import math
from pathlib import Path

from procedural_notation_v1 import build_polyphonic_timed_score, write_musicxml
from procedural_notation_v1.density_matrix_canon import build_density_matrix_cable_net_canon
from procedural_notation_v1.density_matrix_field import build_density_matrix_snapshots
from procedural_notation_v1.tensile_surface_graph import build_tensile_saddle_mesh


def main() -> Path:
    cable_net = build_tensile_saddle_mesh()
    density_canon = build_density_matrix_cable_net_canon(
        cable_net,
        build_density_matrix_snapshots(),
    )
    measures = math.ceil(density_canon.graph["total_ticks"] / 32)
    score = build_polyphonic_timed_score(
        density_canon,
        measures=measures,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title="Four-Qubit Density Matrix Cable-Net Canon No. 10",
        include_node_labels=False,
    )
    first_event_by_voice = {}
    for _, data in density_canon.nodes(data=True):
        first_event_by_voice.setdefault(data["voice"], data)
    for part, voice_id in zip(
        score.parts,
        sorted(density_canon.graph["voices"]),
        strict=True,
    ):
        data = first_event_by_voice[voice_id]
        family, number = voice_id.split("_")[1:]
        part.partName = (
            f"{family.title()} {int(number)} — entry {data['canon_entry_index'] + 1}"
        )
    output = (
        Path(__file__).parent
        / "output"
        / "four_qubit_density_matrix_cable_net_canon_10.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
