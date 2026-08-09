#!/usr/bin/env python3
"""Build the simultaneous QMW Pauli Basis Laboratory v3 Max patch."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "QMW_Pauli_Basis_Laboratory_v3.maxpat"
RECEIVER = ROOT / "qmw_pauli_basis_laboratory_receiver_v3.js"


def box(
    box_id: str,
    maxclass: str,
    rect: list[float],
    *,
    text: str | None = None,
    **attributes: object,
) -> dict:
    value: dict[str, object] = {
        "id": box_id,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    if text is not None:
        value["text"] = text
    value.update(attributes)
    return {"box": value}


def line(source: str, outlet: int, destination: str, inlet: int) -> dict:
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [destination, inlet],
        }
    }


def build_patch() -> dict:
    cyan = [0.12, 0.82, 0.92, 1.0]
    gold = [0.9, 0.72, 0.22, 1.0]
    violet = [0.78, 0.32, 0.88, 1.0]
    orange = [0.96, 0.56, 0.18, 1.0]
    dark = [0.08, 0.09, 0.12, 1.0]

    boxes = [
        box(
            "title",
            "comment",
            [28.0, 16.0, 1200.0, 32.0],
            text="QMW · PAULI BASIS LABORATORY v3 · REPRESENTATION COMPARATOR",
            fontsize=20.0,
            textcolor=cyan,
        ),
        box(
            "subtitle",
            "comment",
            [30.0, 48.0, 1540.0, 22.0],
            text=(
                "One canonical density matrix · two simultaneous 81-setting "
                "tomographies · unchanged 255-Pauli synthesis contract"
            ),
            fontsize=12.0,
        ),
        box(
            "launch",
            "comment",
            [30.0, 76.0, 1540.0, 20.0],
            text=(
                "Start: /Users/zlayton/miniconda3/envs/music/bin/python "
                "workshop_lightweight/qmw_pauli_basis_laboratory_v3.py "
                "--save-dir qmw_pauli_basis_laboratory_v3/runs"
            ),
            fontsize=10.0,
            textcolor=[0.68, 0.7, 0.75, 1.0],
        ),
        box("ghz_qft", "message", [30.0, 106.0, 138.0, 24.0], text="ghz qft 256 23"),
        box(
            "ghz_hadamard",
            "message",
            [178.0, 106.0, 172.0, 24.0],
            text="ghz hadamard 256 23",
        ),
        box(
            "ghz_hamiltonian",
            "message",
            [360.0, 106.0, 190.0, 24.0],
            text="ghz hamiltonian 256 23",
        ),
        box(
            "weave_qft",
            "message",
            [560.0, 106.0, 148.0, 24.0],
            text="weave qft 256 23",
        ),
        box(
            "identity",
            "message",
            [718.0, 106.0, 168.0, 24.0],
            text="ghz identity 256 23",
        ),
        box(
            "opack_run",
            "newobj",
            [906.0, 106.0, 184.0, 24.0],
            text="o.pack /qmw/basis/run",
        ),
        box(
            "udpsend",
            "newobj",
            [1106.0, 106.0, 164.0, 24.0],
            text="udpsend 127.0.0.1 7435",
        ),
        box("ping", "button", [1290.0, 106.0, 24.0, 24.0]),
        box(
            "opack_ping",
            "newobj",
            [1328.0, 106.0, 190.0, 24.0],
            text="o.pack /qmw/basis/ping",
        ),
        box(
            "status",
            "message",
            [30.0, 140.0, 1540.0, 26.0],
            text="Start the v3 Python service, then choose a basis comparison.",
        ),
        box(
            "computational_label",
            "comment",
            [30.0, 180.0, 760.0, 22.0],
            text="COMPUTATIONAL REPRESENTATION · Identity(ρ)",
            fontsize=13.0,
            textcolor=cyan,
        ),
        box(
            "experimental_label",
            "comment",
            [830.0, 180.0, 760.0, 22.0],
            text="EXPERIMENTAL REPRESENTATION · UρU†",
            fontsize=13.0,
            textcolor=violet,
        ),
        box(
            "computational_heatmap",
            "jit.pwindow",
            [30.0, 204.0, 760.0, 250.0],
            sync=1,
        ),
        box(
            "experimental_heatmap",
            "jit.pwindow",
            [830.0, 204.0, 760.0, 250.0],
            sync=1,
        ),
        box(
            "select_label",
            "comment",
            [30.0, 468.0, 230.0, 20.0],
            text="SYNCHRONIZED SETTING / Y (0–80)",
            fontsize=11.0,
            textcolor=gold,
        ),
        box(
            "select",
            "flonum",
            [270.0, 466.0, 76.0, 24.0],
            minimum=0.0,
            maximum=80.0,
            valueof=0.0,
        ),
        box(
            "prepend_select",
            "newobj",
            [358.0, 466.0, 100.0, 24.0],
            text="prepend select",
        ),
        box(
            "mix_label",
            "comment",
            [500.0, 468.0, 360.0, 20.0],
            text="COMPUTATIONAL  ← AUDIO CROSSFADE →  EXPERIMENTAL",
            fontsize=11.0,
            textcolor=cyan,
        ),
        box(
            "mix",
            "flonum",
            [875.0, 466.0, 82.0, 24.0],
            minimum=0.0,
            maximum=1.0,
            valueof=0.5,
        ),
        box(
            "difference_mode",
            "toggle",
            [990.0, 466.0, 24.0, 24.0],
        ),
        box(
            "difference_mode_label",
            "comment",
            [1024.0, 468.0, 360.0, 20.0],
            text="DIFFERENCE ONLY · experimental − computational",
            fontsize=11.0,
            textcolor=orange,
        ),
        box(
            "computational_hist_label",
            "comment",
            [30.0, 506.0, 760.0, 20.0],
            text="Selected row · 16 computational-basis probabilities",
            fontsize=10.0,
        ),
        box(
            "experimental_hist_label",
            "comment",
            [830.0, 506.0, 760.0, 20.0],
            text="Selected row · 16 experimental-basis probabilities",
            fontsize=10.0,
        ),
        box(
            "computational_histogram",
            "multislider",
            [30.0, 528.0, 760.0, 90.0],
            size=16,
            setstyle=1,
            setminmax=[0.0, 1.0],
            slidercolor=cyan,
            bgcolor=dark,
        ),
        box(
            "experimental_histogram",
            "multislider",
            [830.0, 528.0, 760.0, 90.0],
            size=16,
            setstyle=1,
            setminmax=[0.0, 1.0],
            slidercolor=violet,
            bgcolor=dark,
        ),
        box(
            "computational_pauli_label",
            "comment",
            [30.0, 634.0, 760.0, 20.0],
            text="COMPUTATIONAL · 255 non-identity Pauli coefficients",
            fontsize=10.0,
            textcolor=gold,
        ),
        box(
            "experimental_pauli_label",
            "comment",
            [830.0, 634.0, 760.0, 20.0],
            text="EXPERIMENTAL · 255 non-identity Pauli coefficients",
            fontsize=10.0,
            textcolor=gold,
        ),
        box(
            "computational_paulis",
            "multislider",
            [30.0, 656.0, 760.0, 116.0],
            size=255,
            setstyle=1,
            setminmax=[-1.0, 1.0],
            slidercolor=cyan,
            bgcolor=dark,
        ),
        box(
            "experimental_paulis",
            "multislider",
            [830.0, 656.0, 760.0, 116.0],
            size=255,
            setstyle=1,
            setminmax=[-1.0, 1.0],
            slidercolor=violet,
            bgcolor=dark,
        ),
        box(
            "difference_pauli_label",
            "comment",
            [30.0, 788.0, 1200.0, 20.0],
            text=(
                "REPRESENTATION RESIDUE · 255 Pauli deltas "
                "(experimental − computational, range −2…+2)"
            ),
            fontsize=10.0,
            textcolor=orange,
        ),
        box(
            "difference_paulis",
            "multislider",
            [30.0, 810.0, 1560.0, 86.0],
            size=255,
            setstyle=1,
            setminmax=[-2.0, 2.0],
            slidercolor=orange,
            bgcolor=dark,
        ),
        box(
            "computational_shell_label",
            "comment",
            [30.0, 910.0, 500.0, 20.0],
            text="COMPUTATIONAL correlation shells · weights 0–4",
            fontsize=10.0,
        ),
        box(
            "experimental_shell_label",
            "comment",
            [830.0, 910.0, 500.0, 20.0],
            text="EXPERIMENTAL correlation shells · weights 0–4",
            fontsize=10.0,
        ),
        box(
            "computational_shells",
            "multislider",
            [30.0, 932.0, 500.0, 62.0],
            size=5,
            setstyle=1,
            setminmax=[0.0, 1.0],
            slidercolor=cyan,
            bgcolor=dark,
        ),
        box(
            "experimental_shells",
            "multislider",
            [830.0, 932.0, 500.0, 62.0],
            size=5,
            setstyle=1,
            setminmax=[0.0, 1.0],
            slidercolor=violet,
            bgcolor=dark,
        ),
        box(
            "buffer_computational",
            "newobj",
            [30.0, 1014.0, 330.0, 24.0],
            text="buffer~ qmw_basis_computational_v3_2d @samps 20736",
        ),
        box(
            "buffer_experimental",
            "newobj",
            [30.0, 1044.0, 330.0, 24.0],
            text="buffer~ qmw_basis_experimental_v3_2d @samps 20736",
        ),
        box(
            "frequency",
            "flonum",
            [390.0, 1028.0, 76.0, 24.0],
            valueof=110.0,
        ),
        box("phasor", "newobj", [480.0, 1028.0, 72.0, 24.0], text="phasor~ 110."),
        box(
            "select_norm",
            "newobj",
            [570.0, 1028.0, 154.0, 24.0],
            text="expr ($f1 + 0.5) / 81.",
        ),
        box("select_pack", "newobj", [738.0, 1028.0, 86.0, 24.0], text="pack 0. 80"),
        box("select_line", "newobj", [838.0, 1028.0, 48.0, 24.0], text="line~"),
        box(
            "wave_computational",
            "newobj",
            [910.0, 1010.0, 300.0, 24.0],
            text="2d.wave~ qmw_basis_computational_v3_2d 0. 0. 1 81",
        ),
        box(
            "wave_experimental",
            "newobj",
            [910.0, 1050.0, 300.0, 24.0],
            text="2d.wave~ qmw_basis_experimental_v3_2d 0. 0. 1 81",
        ),
        box("mix_pack", "newobj", [390.0, 1080.0, 86.0, 24.0], text="pack 0. 80"),
        box("mix_line", "newobj", [490.0, 1080.0, 48.0, 24.0], text="line~"),
        box("comp_phase", "newobj", [550.0, 1070.0, 58.0, 24.0], text="*~ 0.25"),
        box("comp_gain", "newobj", [620.0, 1070.0, 48.0, 24.0], text="cos~"),
        box("exp_invert", "newobj", [550.0, 1110.0, 58.0, 24.0], text="!-~ 1."),
        box("exp_phase", "newobj", [620.0, 1110.0, 58.0, 24.0], text="*~ 0.25"),
        box("exp_gain", "newobj", [680.0, 1110.0, 48.0, 24.0], text="cos~"),
        box("comp_mul", "newobj", [1230.0, 1010.0, 46.0, 24.0], text="*~"),
        box("exp_mul", "newobj", [1230.0, 1050.0, 46.0, 24.0], text="*~"),
        box("normal_sum", "newobj", [1290.0, 1030.0, 46.0, 24.0], text="+~"),
        box("difference_sub", "newobj", [1230.0, 1090.0, 46.0, 24.0], text="-~"),
        box("mode_pack", "newobj", [760.0, 1090.0, 86.0, 24.0], text="pack 0. 60"),
        box("mode_line", "newobj", [860.0, 1090.0, 48.0, 24.0], text="line~"),
        box("mode_invert", "newobj", [920.0, 1090.0, 58.0, 24.0], text="!-~ 1."),
        box("normal_mode_mul", "newobj", [1290.0, 1070.0, 46.0, 24.0], text="*~"),
        box("difference_mode_mul", "newobj", [1290.0, 1110.0, 46.0, 24.0], text="*~"),
        box("mode_sum", "newobj", [1350.0, 1090.0, 46.0, 24.0], text="+~"),
        box("gain", "newobj", [1410.0, 1090.0, 58.0, 24.0], text="*~ 0.12"),
        box("dac", "ezdac~", [1490.0, 1080.0, 52.0, 36.0]),
        box("load_frequency", "newobj", [30.0, 1090.0, 88.0, 24.0], text="loadmess 110."),
        box("load_select", "newobj", [130.0, 1090.0, 78.0, 24.0], text="loadmess 0."),
        box("load_mix", "newobj", [220.0, 1090.0, 78.0, 24.0], text="loadmess 0.5"),
        box("load_difference", "newobj", [310.0, 1090.0, 70.0, 24.0], text="loadmess 0"),
        box(
            "receiver",
            "newobj",
            [30.0, 1160.0, 300.0, 24.0],
            text="js qmw_pauli_basis_laboratory_receiver_v3.js",
            hidden=1,
        ),
        box(
            "udpreceive",
            "newobj",
            [350.0, 1160.0, 140.0, 24.0],
            text="udpreceive 7436",
            hidden=1,
        ),
        box(
            "route",
            "newobj",
            [510.0, 1160.0, 1040.0, 24.0],
            text=(
                "o.route /qmw/tomography/begin /qmw/tomography/setting "
                "/qmw/tomography/pauli /qmw/tomography/shell "
                "/qmw/tomography/metrics /qmw/tomography/end "
                "/qmw/tomography/status /qmw/tomography/error"
            ),
            hidden=1,
        ),
    ]

    prepend_names = (
        "begin",
        "setting",
        "pauli",
        "shell",
        "metrics",
        "end",
        "status",
        "error",
    )
    for index, name in enumerate(prepend_names):
        boxes.append(
            box(
                f"prepend_{name}",
                "newobj",
                [510.0 + 110.0 * index, 1190.0, 100.0, 24.0],
                text=f"prepend {name}",
                hidden=1,
            )
        )

    run_messages = (
        "ghz_qft",
        "ghz_hadamard",
        "ghz_hamiltonian",
        "weave_qft",
        "identity",
    )
    lines = [line(name, 0, "opack_run", 0) for name in run_messages]
    lines.extend(
        [
            line("opack_run", 0, "udpsend", 0),
            line("ping", 0, "opack_ping", 0),
            line("opack_ping", 0, "udpsend", 0),
            line("select", 0, "prepend_select", 0),
            line("prepend_select", 0, "receiver", 0),
            line("receiver", 0, "computational_heatmap", 0),
            line("receiver", 1, "experimental_heatmap", 0),
            line("receiver", 2, "computational_histogram", 0),
            line("receiver", 3, "experimental_histogram", 0),
            line("receiver", 4, "computational_paulis", 0),
            line("receiver", 5, "experimental_paulis", 0),
            line("receiver", 6, "difference_paulis", 0),
            line("receiver", 7, "computational_shells", 0),
            line("receiver", 8, "experimental_shells", 0),
            line("receiver", 9, "status", 0),
            line("frequency", 0, "phasor", 0),
            line("phasor", 0, "wave_computational", 0),
            line("phasor", 0, "wave_experimental", 0),
            line("select", 0, "select_norm", 0),
            line("select_norm", 0, "select_pack", 0),
            line("select_pack", 0, "select_line", 0),
            line("select_line", 0, "wave_computational", 1),
            line("select_line", 0, "wave_experimental", 1),
            line("mix", 0, "mix_pack", 0),
            line("mix_pack", 0, "mix_line", 0),
            line("mix_line", 0, "comp_phase", 0),
            line("comp_phase", 0, "comp_gain", 0),
            line("mix_line", 0, "exp_invert", 0),
            line("exp_invert", 0, "exp_phase", 0),
            line("exp_phase", 0, "exp_gain", 0),
            line("wave_computational", 0, "comp_mul", 0),
            line("comp_gain", 0, "comp_mul", 1),
            line("wave_experimental", 0, "exp_mul", 0),
            line("exp_gain", 0, "exp_mul", 1),
            line("comp_mul", 0, "normal_sum", 0),
            line("exp_mul", 0, "normal_sum", 1),
            line("wave_experimental", 0, "difference_sub", 0),
            line("wave_computational", 0, "difference_sub", 1),
            line("difference_mode", 0, "mode_pack", 0),
            line("mode_pack", 0, "mode_line", 0),
            line("mode_line", 0, "mode_invert", 0),
            line("normal_sum", 0, "normal_mode_mul", 0),
            line("mode_invert", 0, "normal_mode_mul", 1),
            line("difference_sub", 0, "difference_mode_mul", 0),
            line("mode_line", 0, "difference_mode_mul", 1),
            line("normal_mode_mul", 0, "mode_sum", 0),
            line("difference_mode_mul", 0, "mode_sum", 1),
            line("mode_sum", 0, "gain", 0),
            line("gain", 0, "dac", 0),
            line("gain", 0, "dac", 1),
            line("load_frequency", 0, "frequency", 0),
            line("load_select", 0, "select", 0),
            line("load_mix", 0, "mix", 0),
            line("load_difference", 0, "difference_mode", 0),
            line("udpreceive", 0, "route", 0),
        ]
    )
    for index, name in enumerate(prepend_names):
        lines.append(line("route", index, f"prepend_{name}", 0))
        lines.append(line(f"prepend_{name}", 0, "receiver", 0))

    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {
                "major": 9,
                "minor": 0,
                "revision": 8,
                "architecture": "x64",
                "modernui": 1,
            },
            "classnamespace": "box",
            "rect": [20.0, 30.0, 1640.0, 1240.0],
            "bglocked": 0,
            "openinpresentation": 0,
            "default_fontsize": 12.0,
            "default_fontface": 0,
            "default_fontname": "Arial",
            "gridonopen": 1,
            "gridsize": [15.0, 15.0],
            "boxes": boxes,
            "lines": lines,
            "dependency_cache": [
                {
                    "name": RECEIVER.name,
                    "type": "TEXT",
                    "implicit": 1,
                },
                {"name": "o.pack.mxo", "type": "iLaX", "implicit": 1},
                {"name": "o.route.mxo", "type": "iLaX", "implicit": 1},
            ],
            "autosave": 0,
        }
    }


def validate_patch(document: dict) -> None:
    patcher = document["patcher"]
    values = [item["box"] for item in patcher["boxes"]]
    texts = {value.get("text", "") for value in values}
    ids = {value["id"] for value in values}
    assert "QMW_Pauli_Basis_Laboratory_v3.maxpat" not in texts
    assert "o.pack /qmw/basis/run" in texts
    assert "udpsend 127.0.0.1 7435" in texts
    assert "udpreceive 7436" in texts
    assert "js qmw_pauli_basis_laboratory_receiver_v3.js" in texts
    assert (
        "buffer~ qmw_basis_computational_v3_2d @samps 20736"
        in texts
    )
    assert "buffer~ qmw_basis_experimental_v3_2d @samps 20736" in texts
    assert "computational_heatmap" in ids
    assert "experimental_heatmap" in ids
    assert "difference_paulis" in ids
    assert "difference_mode" in ids
    assert sum(value["maxclass"] == "jit.pwindow" for value in values) == 2
    assert RECEIVER.exists()
    receiver = RECEIVER.read_text(encoding="utf-8")
    assert "outlets = 10" in receiver
    assert 'name.indexOf("experimental")' in receiver
    assert "states = { computational: null, experimental: null }" in receiver
    assert "experimental" in receiver
    assert "qmw_basis_computational_v3_2d" in receiver
    assert "qmw_basis_experimental_v3_2d" in receiver


def main() -> int:
    document = build_patch()
    validate_patch(document)
    OUTPUT.write_text(
        json.dumps(document, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
