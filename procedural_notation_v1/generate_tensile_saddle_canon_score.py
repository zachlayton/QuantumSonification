"""Generate a Frei Otto-inspired 32-voice tensile membrane canon."""

from __future__ import annotations

import math
from pathlib import Path

from procedural_notation_v1 import build_polyphonic_timed_score, write_musicxml
from procedural_notation_v1.tensile_surface_canon import build_tensile_saddle_32_voice_canon
from procedural_notation_v1.tensile_surface_graph import build_tensile_saddle_mesh


def main() -> Path:
    surface = build_tensile_saddle_mesh()
    canon = build_tensile_saddle_32_voice_canon(surface, passes=4)
    measures = math.ceil(canon.graph["total_ticks"] / 32)
    score = build_polyphonic_timed_score(
        canon,
        measures=measures,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title="Tensile Saddle Reflection Canon No. 9",
        include_node_labels=False,
    )
    first_event_by_voice = {}
    for _, data in canon.nodes(data=True):
        first_event_by_voice.setdefault(data["voice"], data)
    for part, voice_id in zip(score.parts, sorted(canon.graph["voices"]), strict=True):
        data = first_event_by_voice[voice_id]
        family, number = voice_id.split("_")[1:]
        part.partName = (
            f"{family.title()} {int(number)} — entry "
            f"{data['canon_entry_index'] + 1}, ×{data['mensuration_factor']}"
        )
    output = (
        Path(__file__).parent
        / "output"
        / "frei_otto_tensile_saddle_32_voice_canon_9.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
