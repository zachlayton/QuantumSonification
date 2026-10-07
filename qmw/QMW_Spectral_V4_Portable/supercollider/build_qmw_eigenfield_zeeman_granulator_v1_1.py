#!/usr/bin/env python3
"""Write a fresh SC document name to avoid stale IDE buffers."""
from pathlib import Path

root = Path(__file__).resolve().parent
source = root / "qmw_eigenfield_zeeman_granulator_v1.scd"
target = root / "qmw_eigenfield_zeeman_granulator_v1_1.scd"
text = source.read_text()
required = (
    "semitones.neg.midiratio",
    "var y = i.div(4);",
    "* 0.7).neg.exp",
)
missing = [token for token in required if token not in text]
if missing:
    raise RuntimeError(f"source corrections missing: {missing}")
target.write_text(text)
print(f"generated {target.name}")
