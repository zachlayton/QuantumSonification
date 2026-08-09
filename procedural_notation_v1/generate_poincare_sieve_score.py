"""Generate a Poincare-disk canon with Xenakis-style modular pitch sieves."""

from __future__ import annotations

import math
from pathlib import Path

from procedural_notation_v1 import build_polyphonic_timed_score, write_musicxml
from procedural_notation_v1.poincare_disk_graph import build_poincare_disk_graph
from procedural_notation_v1.poincare_sieve_canon import build_poincare_sieve_canon


def main() -> Path:
    canon = build_poincare_sieve_canon(build_poincare_disk_graph())
    measures = math.ceil(canon.graph["total_ticks"] / 32)
    score = build_polyphonic_timed_score(
        canon,
        measures=measures,
        beats_per_measure=4,
        ticks_per_quarter=8,
        title="Poincare Disk Quantum-Dynamic Sieve Canon No. 15",
        include_node_labels=False,
    )
    for part, voice_id in zip(score.parts, sorted(canon.graph["voices"]), strict=True):
        ray_number = int(voice_id.split("_")[1])
        part.partName = f"Hyperbolic ray {ray_number}"
    output = (
        Path(__file__).parent
        / "output"
        / "poincare_disk_quantum_dynamic_sieve_canon_15.musicxml"
    )
    return write_musicxml(score, output)


if __name__ == "__main__":
    print(main())
