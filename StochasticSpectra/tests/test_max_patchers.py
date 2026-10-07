#!/usr/bin/env python3
"""Structural regression checks for the generated Max help and FrameLib lab."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))["patcher"]


def index(patcher: dict) -> tuple[dict[str, dict], list[dict]]:
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    return boxes, [entry["patchline"] for entry in patcher["lines"]]


def edge(lines: list[dict], source: str, source_outlet: int, destination: str, destination_inlet: int) -> bool:
    return any(
        item["source"] == [source, source_outlet]
        and item["destination"] == [destination, destination_inlet]
        for item in lines
    )


def require_text(boxes: dict[str, dict], text: str) -> None:
    assert any(box.get("text") == text for box in boxes.values()), f"missing Max object: {text}"


def test_help() -> None:
    first = load("help/stochspectra~.maxhelp")
    second = load("help/stochpacketenv~.maxhelp")
    assert first == second
    boxes, lines = index(first)
    for text in ("stochspectra~", "stochpacketenv~", "*~", "selector~ 3"):
        require_text(boxes, text)
    assert boxes["spectrogram"]["maxclass"] == "spectroscope~"
    assert boxes["spectrogram"]["sono"] == 1
    assert edge(lines, "stoch", 0, "multiply", 0)
    assert edge(lines, "env", 0, "multiply", 1)
    assert edge(lines, "multiply", 0, "select", 2)


def test_framelib_lab() -> None:
    patcher = load("patchers/StochasticSpectra_FrameLib_Lab.maxpat")
    boxes, lines = index(patcher)
    for text in (
        "stochspectra~",
        "stochpacketenv~",
        "fl-freeze-stoch",
        "delay~ 4096 4096",
        "matrix~ 2 1 0. @ramp 50",
        "*~",
        "sel 0 1",
        "prepend freq",
    ):
        require_text(boxes, text)
    assert boxes["spectrogram"]["maxclass"] == "spectroscope~"
    assert boxes["spectrogram"]["sono"] == 1
    assert edge(lines, "stoch", 0, "freeze", 0)
    assert edge(lines, "preset_load", 0, "morph_preset", 0)
    assert edge(lines, "freq_value", 0, "freq_prepend", 0)
    assert edge(lines, "freq_prepend", 0, "stoch", 0)
    assert edge(lines, "stoch", 0, "direct_delay", 0)
    assert edge(lines, "direct_delay", 0, "matrix", 0)
    assert edge(lines, "freeze", 0, "matrix", 1)
    assert edge(lines, "matrix", 0, "multiply", 0)
    assert edge(lines, "env", 0, "multiply", 1)
    assert not edge(lines, "env", 0, "freeze", 0)
    assert edge(lines, "voice_toggle", 0, "voice_select", 0)
    assert edge(lines, "env_toggle", 0, "env_select", 0)


if __name__ == "__main__":
    test_help()
    test_framelib_lab()
    print("PASS Max help and FrameLib companion patch graphs")
