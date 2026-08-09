#!/usr/bin/env python3
"""Build the signal-rate 2-D wavetable edition of the Full4Q instrument."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
V1_PATCH = ROOT / "QMW_Full4Q_Tomography_81_v1.maxpat"
V1_RECEIVER = ROOT / "qmw_full4q_tomography_receiver_v1.js"
OUTPUT_PATCH = ROOT / "QMW_Full4Q_Tomography_81_v2.maxpat"
OUTPUT_RECEIVER = ROOT / "qmw_full4q_tomography_receiver_v2.js"


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


def build_receiver() -> None:
    source = V1_RECEIVER.read_text(encoding="utf-8")
    source = source.replace("outlets = 5;", "outlets = 6;", 1)
    source = source.replace(
        "// outlet 4: human-readable status\n",
        "// outlet 4: human-readable status\n"
        "// outlet 5: selected Pauli label for Processing/PyZX highlighting\n"
        "// Audio is stored as two independent 81-row x 256-sample surfaces.\n",
        1,
    )
    source = source.replace(
        "var pendingPaulis = [];\n",
        "var pendingPaulis = [];\nvar pendingPauliLabels = [];\n",
        1,
    )
    source = source.replace(
        "    pendingPaulis = new Array(255);\n",
        "    pendingPaulis = new Array(255);\n"
        "    pendingPauliLabels = new Array(255);\n",
        1,
    )
    source = source.replace(
        "    pendingPaulis[index] = parseFloat(a[4]);\n",
        "    pendingPauliLabels[index] = String(a[2]);\n"
        "    pendingPaulis[index] = parseFloat(a[4]);\n",
        1,
    )
    source = source.replace(
        "        paulis: pendingPaulis,\n",
        "        paulis: pendingPaulis,\n"
        "        pauliLabels: pendingPauliLabels,\n",
        1,
    )
    source = source.replace(
        "    _renderAll();\n"
        "    _status(\n"
        '        "stored " + pendingSource.toUpperCase() + " rev " + revision +\n',
        "    _writeSurface(pendingSource);\n"
        "    _renderAll();\n"
        "    _status(\n"
        '        "stored " + pendingSource.toUpperCase() + " 2D surface rev " + revision +\n',
        1,
    )
    source = source.replace("    _writeWavetable(probabilities);\n", "", 1)

    old_start = source.index("function _writeWavetable(probabilities) {")
    old_end = source.index("\nfunction status()", old_start)
    surface_functions = r"""function _makeWavetable(probabilities) {
    var frames = 256;
    var table = [];
    var mean = 0.0;
    var peak = 0.0;
    for (var frame = 0; frame < frames; frame++) {
        var phase = 2.0 * Math.PI * frame / frames;
        var value = 0.0;
        for (var harmonic = 0; harmonic < 16; harmonic++) {
            var amplitude = Math.sqrt(Math.max(0.0, probabilities[harmonic]));
            value += amplitude * Math.sin((harmonic + 1) * phase);
        }
        table[frame] = value;
        mean += value;
    }
    mean /= frames;
    for (var index = 0; index < frames; index++) {
        table[index] -= mean;
        peak = Math.max(peak, Math.abs(table[index]));
    }
    if (peak > 0.0) {
        for (var sample = 0; sample < frames; sample++)
            table[sample] = 0.9 * table[sample] / peak;
    }
    return table;
}

function _surfaceName(source) {
    return source === "ibm"
        ? "qmw_full4q_ibm_2d"
        : "qmw_full4q_local_2d";
}

function _writeSurface(source) {
    var state = states[source];
    if (!state)
        return;
    var surface = new Buffer(_surfaceName(source));
    for (var settingIndex = 0; settingIndex < 81; settingIndex++) {
        var row = state.settings[settingIndex];
        if (row)
            surface.poke(
                1,
                settingIndex * 256,
                _makeWavetable(row.probabilities)
            );
    }
}

function _clearSurface(source) {
    var zeroes = [];
    for (var index = 0; index < 81 * 256; index++)
        zeroes[index] = 0.0;
    new Buffer(_surfaceName(source)).poke(1, 0, zeroes);
}
"""
    source = source[:old_start] + surface_functions + source[old_end:]
    source = source.replace(
        'function clear() {\n'
        '    states = { local: null, ibm: null };\n',
        'function clear() {\n'
        '    states = { local: null, ibm: null };\n'
        '    _clearSurface("local");\n'
        '    _clearSurface("ibm");\n',
        1,
    )
    source = source.replace(
        'function clear_local() {\n'
        '    states.local = null;\n',
        'function clear_local() {\n'
        '    states.local = null;\n'
        '    _clearSurface("local");\n',
        1,
    )
    source = source.replace(
        'function clear_ibm() {\n'
        '    states.ibm = null;\n',
        'function clear_ibm() {\n'
        '    states.ibm = null;\n'
        '    _clearSurface("ibm");\n',
        1,
    )
    source += r"""

function select_pauli(value) {
    var index = Math.round(_clamp(Number(value), 0, 254));
    var state = states.local || states.ibm;
    if (!state || !state.pauliLabels || !state.pauliLabels[index]) {
        _status("Pauli term " + index + " is not loaded yet");
        return;
    }
    var label = state.pauliLabels[index];
    outlet(5, label);
    _status("selected Pauli " + label + " · term " + index + " → Processing");
}

function live_pauli() {
    var a = _args(arguments);
    if (a.length < 6)
        return;
    var label = String(a[1]);
    var expectation = Number(a[3]);
    var theta = Number(a[4]);
    var state = states.local || states.ibm;
    if (state && state.pauliLabels) {
        var index = state.pauliLabels.indexOf(label);
        if (index >= 0) {
            state.paulis[index] = expectation;
            _renderAll();
        }
    }
    _status(
        "live ZX " + label + "  expectation " + expectation.toFixed(6)
        + "  theta " + theta.toFixed(6)
        + (Number(a[5]) ? "  PyZX verified" : "  unverified")
    );
}
"""
    OUTPUT_RECEIVER.write_text(source, encoding="utf-8")


def build_patch() -> None:
    document = json.loads(V1_PATCH.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    boxes = patcher["boxes"]
    box_by_id = {item["box"]["id"]: item["box"] for item in boxes}

    patcher["rect"] = [40.0, 50.0, 1440.0, 1140.0]
    box_by_id["title"]["text"] = (
        "QMW · FULL FOUR-QUBIT TOMOGRAPHY · 2D WAVETABLE INSTRUMENT v2"
    )
    box_by_id["subtitle"]["text"] = (
        "Two 81 × 256 wavetable surfaces preserve LOCAL and IBM independently. "
        "X is oscillator phase; signal-rate Y scans the complete tomography score; "
        "Difference Only reveals the IBM − LOCAL spectral residue."
    )
    box_by_id["selectlabel"]["text"] = "SETTING / Y POSITION (0–80)"
    box_by_id["audiolabel"]["text"] = (
        "SONIFY THE 2D SCORE · 81 settings become rows; "
        "data can drive Y continuously at signal rate"
    )

    box_by_id["receiver"]["text"] = "js qmw_full4q_tomography_receiver_v2.js"
    box_by_id["receiver"]["patching_rect"] = [1160.0, 688.0, 214.0, 24.0]
    box_by_id["receiver"]["numoutlets"] = 6
    box_by_id["receiver"]["outlettype"] = [""] * 6

    box_by_id["buffer"]["text"] = (
        "buffer~ qmw_full4q_local_2d @samps 20736"
    )
    box_by_id["buffer"]["patching_rect"] = [30.0, 694.0, 290.0, 24.0]
    box_by_id["frequency"]["patching_rect"] = [30.0, 768.0, 76.0, 24.0]
    box_by_id["phasor"]["patching_rect"] = [122.0, 768.0, 72.0, 24.0]
    box_by_id["wave"]["text"] = (
        "2d.wave~ qmw_full4q_local_2d 0. 0. 1 81"
    )
    box_by_id["wave"]["patching_rect"] = [330.0, 744.0, 285.0, 24.0]
    box_by_id["gain"]["patching_rect"] = [1060.0, 938.0, 58.0, 24.0]
    box_by_id["dac"]["patching_rect"] = [1136.0, 930.0, 52.0, 36.0]
    box_by_id["route"]["text"] += (
        " /qmw/tomography/difference /qmw/zx/pauli/live"
    )
    box_by_id["route"]["numoutlets"] = 12
    box_by_id["route"]["outlettype"] = [""] * 11 + ["FullPacket"]

    # Move the archive controls below the expanded audio surface.
    box_by_id["warning"]["patching_rect"] = [30.0, 1000.0, 600.0, 22.0]
    box_by_id["replay_local"]["patching_rect"] = [30.0, 1028.0, 118.0, 24.0]
    box_by_id["replay_ibm"]["patching_rect"] = [160.0, 1028.0, 118.0, 24.0]
    box_by_id["opack_replay"]["patching_rect"] = [290.0, 1028.0, 220.0, 24.0]
    box_by_id["replay_help"]["patching_rect"] = [520.0, 1028.0, 390.0, 24.0]
    box_by_id["load_frequency"]["patching_rect"] = [30.0, 1066.0, 86.0, 24.0]
    box_by_id["load_select"]["patching_rect"] = [130.0, 1066.0, 78.0, 24.0]
    box_by_id["load_mix"]["patching_rect"] = [220.0, 1066.0, 78.0, 24.0]

    boxes.extend(
        [
            box(
                "buffer_ibm",
                "newobj",
                [30.0, 724.0, 290.0, 24.0],
                text="buffer~ qmw_full4q_ibm_2d @samps 20736",
            ),
            box(
                "wave_ibm",
                "newobj",
                [330.0, 794.0, 285.0, 24.0],
                text="2d.wave~ qmw_full4q_ibm_2d 0. 0. 1 81",
            ),
            box(
                "ylabel",
                "comment",
                [30.0, 808.0, 305.0, 20.0],
                text="Y row center = (setting position + 0.5) / 81",
                fontsize=10.0,
                textcolor=[0.7, 0.72, 0.76, 1.0],
            ),
            box(
                "select_norm",
                "newobj",
                [30.0, 834.0, 154.0, 24.0],
                text="expr ($f1 + 0.5) / 81.",
            ),
            box(
                "select_pack",
                "newobj",
                [198.0, 834.0, 86.0, 24.0],
                text="pack 0. 80",
            ),
            box(
                "select_line",
                "newobj",
                [298.0, 834.0, 48.0, 24.0],
                text="line~",
            ),
            box(
                "mix_pack",
                "newobj",
                [630.0, 804.0, 86.0, 24.0],
                text="pack 0. 80",
            ),
            box(
                "mix_line",
                "newobj",
                [730.0, 804.0, 48.0, 24.0],
                text="line~",
            ),
            box(
                "local_gain",
                "newobj",
                [860.0, 790.0, 48.0, 24.0],
                text="cos~",
            ),
            box(
                "ibm_gain",
                "newobj",
                [930.0, 850.0, 48.0, 24.0],
                text="cos~",
            ),
            box(
                "local_phase",
                "newobj",
                [790.0, 790.0, 58.0, 24.0],
                text="*~ 0.25",
            ),
            box(
                "ibm_invert",
                "newobj",
                [790.0, 850.0, 58.0, 24.0],
                text="!-~ 1.",
            ),
            box(
                "ibm_phase",
                "newobj",
                [860.0, 850.0, 58.0, 24.0],
                text="*~ 0.25",
            ),
            box(
                "local_mul",
                "newobj",
                [920.0, 790.0, 46.0, 24.0],
                text="*~",
            ),
            box(
                "ibm_mul",
                "newobj",
                [990.0, 850.0, 46.0, 24.0],
                text="*~",
            ),
            box(
                "audio_sum",
                "newobj",
                [1046.0, 826.0, 46.0, 24.0],
                text="+~",
            ),
            box(
                "source_audio_label",
                "comment",
                [630.0, 876.0, 470.0, 22.0],
                text=(
                    "Equal-power audio crossfade; LOCAL and IBM remain "
                    "separate 2D surfaces"
                ),
                fontsize=10.0,
                textcolor=[0.12, 0.82, 0.92, 1.0],
            ),
            box(
                "difference_mode",
                "toggle",
                [630.0, 908.0, 24.0, 24.0],
            ),
            box(
                "difference_label",
                "comment",
                [664.0, 908.0, 430.0, 24.0],
                text=(
                    "DIFFERENCE ONLY · IBM − LOCAL "
                    "(identical wavetable data cancels to silence)"
                ),
                fontsize=11.0,
                textcolor=[0.96, 0.56, 0.18, 1.0],
            ),
            box(
                "difference_sub",
                "newobj",
                [1046.0, 866.0, 46.0, 24.0],
                text="-~",
            ),
            box(
                "mode_pack",
                "newobj",
                [630.0, 942.0, 86.0, 24.0],
                text="pack 0. 60",
            ),
            box(
                "mode_line",
                "newobj",
                [730.0, 942.0, 48.0, 24.0],
                text="line~",
            ),
            box(
                "mode_invert",
                "newobj",
                [790.0, 922.0, 58.0, 24.0],
                text="!-~ 1.",
            ),
            box(
                "normal_mode_mul",
                "newobj",
                [860.0, 922.0, 46.0, 24.0],
                text="*~",
            ),
            box(
                "difference_mode_mul",
                "newobj",
                [860.0, 962.0, 46.0, 24.0],
                text="*~",
            ),
            box(
                "mode_sum",
                "newobj",
                [926.0, 942.0, 46.0, 24.0],
                text="+~",
            ),
            box(
                "load_difference",
                "newobj",
                [310.0, 1066.0, 78.0, 24.0],
                text="loadmess 0",
            ),
            box(
                "pauli_select_label",
                "comment",
                [1120.0, 1000.0, 270.0, 20.0],
                text="PAULI TERM 0–254 → ZX gadget highlight",
                fontsize=10.0,
            ),
            box(
                "pauli_select",
                "number",
                [1120.0, 1024.0, 72.0, 24.0],
                minimum=0,
                maximum=254,
                numinlets=1,
                numoutlets=2,
                outlettype=["", "bang"],
            ),
            box(
                "pauli_select_command",
                "newobj",
                [1205.0, 1024.0, 132.0, 24.0],
                text="prepend select_pauli",
            ),
            box(
                "pauli_selected_label",
                "message",
                [1120.0, 1056.0, 108.0, 24.0],
                text="—",
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                "pauli_select_osc",
                "newobj",
                [1240.0, 1056.0, 205.0, 24.0],
                text="prepend /qmw/zx/pauli/select",
            ),
            box(
                "pauli_select_udp",
                "newobj",
                [1240.0, 1088.0, 195.0, 24.0],
                text="udpsend 127.0.0.1 7497",
            ),
            box(
                "pauli_live_prepend",
                "newobj",
                [1010.0, 1088.0, 120.0, 24.0],
                text="prepend live_pauli",
                hidden=1,
            ),
        ]
    )

    replaced_ids = {"wave", "gain", "dac"}
    kept_lines = []
    for item in patcher["lines"]:
        patchline = item["patchline"]
        source_id = patchline["source"][0]
        destination_id = patchline["destination"][0]
        if source_id in replaced_ids or destination_id in replaced_ids:
            continue
        kept_lines.append(item)

    kept_lines.extend(
        [
            line("phasor", 0, "wave", 0),
            line("phasor", 0, "wave_ibm", 0),
            line("select", 0, "select_norm", 0),
            line("select_norm", 0, "select_pack", 0),
            line("select_pack", 0, "select_line", 0),
            line("select_line", 0, "wave", 1),
            line("select_line", 0, "wave_ibm", 1),
            line("mix", 0, "mix_pack", 0),
            line("mix_pack", 0, "mix_line", 0),
            line("mix_line", 0, "local_phase", 0),
            line("local_phase", 0, "local_gain", 0),
            line("mix_line", 0, "ibm_invert", 0),
            line("ibm_invert", 0, "ibm_phase", 0),
            line("ibm_phase", 0, "ibm_gain", 0),
            line("wave", 0, "local_mul", 0),
            line("local_gain", 0, "local_mul", 1),
            line("wave_ibm", 0, "ibm_mul", 0),
            line("ibm_gain", 0, "ibm_mul", 1),
            line("local_mul", 0, "audio_sum", 0),
            line("ibm_mul", 0, "audio_sum", 1),
            line("wave_ibm", 0, "difference_sub", 0),
            line("wave", 0, "difference_sub", 1),
            line("difference_mode", 0, "mode_pack", 0),
            line("mode_pack", 0, "mode_line", 0),
            line("mode_line", 0, "mode_invert", 0),
            line("audio_sum", 0, "normal_mode_mul", 0),
            line("mode_invert", 0, "normal_mode_mul", 1),
            line("difference_sub", 0, "difference_mode_mul", 0),
            line("mode_line", 0, "difference_mode_mul", 1),
            line("normal_mode_mul", 0, "mode_sum", 0),
            line("difference_mode_mul", 0, "mode_sum", 1),
            line("mode_sum", 0, "gain", 0),
            line("gain", 0, "dac", 0),
            line("gain", 0, "dac", 1),
            line("load_difference", 0, "difference_mode", 0),
            line("route", 10, "difference_mode", 0),
            line("pauli_select", 0, "pauli_select_command", 0),
            line("pauli_select_command", 0, "receiver", 0),
            line("receiver", 5, "pauli_selected_label", 0),
            line("receiver", 5, "pauli_select_osc", 0),
            line("pauli_select_osc", 0, "pauli_select_udp", 0),
            line("route", 11, "pauli_live_prepend", 0),
            line("pauli_live_prepend", 0, "receiver", 0),
        ]
    )
    patcher["lines"] = kept_lines

    for dependency in patcher["dependency_cache"]:
        if dependency.get("name") == "qmw_full4q_tomography_receiver_v1.js":
            dependency["name"] = "qmw_full4q_tomography_receiver_v2.js"

    OUTPUT_PATCH.write_text(
        json.dumps(document, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_outputs() -> None:
    document = json.loads(OUTPUT_PATCH.read_text(encoding="utf-8"))
    patcher = document["patcher"]
    texts = {
        item["box"].get("text", "")
        for item in patcher["boxes"]
    }
    assert "2d.wave~ qmw_full4q_local_2d 0. 0. 1 81" in texts
    assert "2d.wave~ qmw_full4q_ibm_2d 0. 0. 1 81" in texts
    assert "buffer~ qmw_full4q_local_2d @samps 20736" in texts
    assert "buffer~ qmw_full4q_ibm_2d @samps 20736" in texts
    assert "cos~" in texts
    assert "*~ 0.25" in texts
    assert "!-~ 1." in texts
    assert "-~" in texts
    assert "pack 0. 60" in texts
    assert any(text.startswith("DIFFERENCE ONLY") for text in texts)
    assert "udpsend 127.0.0.1 7497" in texts
    assert any("/qmw/zx/pauli/live" in text for text in texts)
    assert any(
        "/qmw/tomography/difference" in text
        for text in texts
    )
    assert not any(text.startswith("expr~ cos") for text in texts)
    assert not any(text.startswith("expr~ sin") for text in texts)
    receiver = OUTPUT_RECEIVER.read_text(encoding="utf-8")
    assert 'settingIndex * 256' in receiver
    assert 'qmw_full4q_local_2d' in receiver
    assert 'qmw_full4q_ibm_2d' in receiver
    assert "function select_pauli(value)" in receiver
    assert "function live_pauli()" in receiver


if __name__ == "__main__":
    build_receiver()
    build_patch()
    validate_outputs()
    print(f"Wrote {OUTPUT_RECEIVER}")
    print(f"Wrote {OUTPUT_PATCH}")
