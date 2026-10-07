#!/usr/bin/env python3
"""Build a V1 density patch with a dedicated return port for V2 comparison."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "QMW_Four_Qubit_256_Density_Morph_Workshop_v1.maxpat"
OUTPUT = ROOT / "QMW_Four_Qubit_256_Density_Morph_Workshop_v1_Compare.maxpat"


def main() -> int:
    document = json.loads(SOURCE.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    boxes = {
        entry["box"]["id"]: entry["box"]
        for entry in patcher["boxes"]
    }
    boxes["title"]["text"] = "V1 LOCAL DENSITY MORPH · SIDE-BY-SIDE RETURN"
    boxes["instructions"]["text"] = (
        "This comparison copy keeps the V1 instrument unchanged but receives "
        "its frames on UDP 7422 while V2 receives IBM comparison data on 7412."
    )
    boxes["density-udp"]["text"] = "udpreceive 7422"
    boxes["status"]["text"] = (
        "Run only qac_density_ibm_compare_bridge_v2.py, then SEND QASM "
        "from either comparison patch."
    )
    boxes["density-command"]["text"] = (
        "shared engine: qac_density_ibm_compare_bridge_v2.py · "
        "V1 return UDP 7422 · no second bridge"
    )
    OUTPUT.write_text(
        json.dumps(document, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Built {OUTPUT.name} from {SOURCE.name}; "
        "the original V1 patch was not modified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
