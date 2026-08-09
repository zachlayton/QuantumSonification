#!/usr/bin/env python3
"""Add a non-destructive stereo MSP bus to the QMW resonator Max patches."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PATCHES = (
    ROOT.parent / "max/QMW_Music_of_the_Spheres_Resonator_v1.maxpat",
    ROOT.parent / "max/QMW_Music_of_the_Spheres_Resonator_v2.maxpat",
)
PREFIX = "qmw-spectral-bus-"


def add_bus(path: Path) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    boxes = patcher["boxes"]
    lines = patcher["lines"]

    # Make rerunning deterministic.
    removed = {
        entry["box"]["id"]
        for entry in boxes
        if entry["box"]["id"].startswith(PREFIX)
    }
    boxes[:] = [entry for entry in boxes if entry["box"]["id"] not in removed]
    lines[:] = [
        entry for entry in lines
        if entry["patchline"]["source"][0] not in removed
        and entry["patchline"]["destination"][0] not in removed
    ]

    indexed = {entry["box"]["id"]: entry["box"] for entry in boxes}
    dac_ids = {
        identifier
        for identifier, box in indexed.items()
        if box.get("maxclass") == "ezdac~"
    }
    if len(dac_ids) != 1:
        raise RuntimeError(f"expected one ezdac~ in {path.name}")
    dac_id = next(iter(dac_ids))

    sources = {0: [], 1: []}
    for entry in lines:
        line = entry["patchline"]
        if line["destination"][0] == dac_id and line["destination"][1] in sources:
            sources[line["destination"][1]].append(line["source"])
    if not sources[0] or not sources[1]:
        raise RuntimeError(f"no stereo output mix found in {path.name}")

    def new_object(identifier: str, text: str, rect: list[float]) -> None:
        boxes.append({
            "box": {
                "id": identifier,
                "maxclass": "newobj",
                "classnamespace": "box",
                "text": text,
                "patching_rect": rect,
            }
        })

    def connect(source: list, destination: list) -> None:
        lines.append({"patchline": {"source": source, "destination": destination}})

    for channel, name, x in (
        (0, "qmw_spectral_L", 1160.0),
        (1, "qmw_spectral_R", 1320.0),
    ):
        channel_sources = sources[channel]
        signal = channel_sources[0]
        for index, next_source in enumerate(channel_sources[1:]):
            sum_id = f"{PREFIX}sum-{channel}-{index}"
            new_object(sum_id, "+~", [x, 1040.0 + index * 32.0, 32.0, 23.0])
            connect(signal, [sum_id, 0])
            connect(next_source, [sum_id, 1])
            signal = [sum_id, 0]
        send_id = f"{PREFIX}send-{channel}"
        new_object(send_id, f"send~ {name}", [x, 1110.0, 142.0, 23.0])
        connect(signal, [send_id, 0])

    path.write_text(json.dumps(document, indent=2), encoding="utf-8")
    print(path)


def main() -> None:
    for patch in PATCHES:
        add_bus(patch)


if __name__ == "__main__":
    main()
