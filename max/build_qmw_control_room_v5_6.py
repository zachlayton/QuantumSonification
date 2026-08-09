#!/usr/bin/env python3
"""Build v5.6 with click-free, quantum-addressable geometry size."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTROL_SOURCE = ROOT / "QMW_Control_Room_v5_5.maxpat"
RACK_SOURCE = ROOT / "QMW_Sonification_Rack_Module_v5_5.maxpat"
SURFACE_SOURCE = ROOT / "QMW_Realtime_Surface_Reverb_v5_5.maxpat"
CONTROL_OUTPUT = ROOT / "QMW_Control_Room_v5_6.maxpat"
RACK_OUTPUT = ROOT / "QMW_Sonification_Rack_Module_v5_6.maxpat"
SURFACE_OUTPUT = ROOT / "QMW_Realtime_Surface_Reverb_v5_6.maxpat"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def next_id(patcher: dict[str, Any]) -> str:
    values = [int(e["box"]["id"][4:]) for e in patcher.get("boxes", [])
              if e["box"]["id"].startswith("obj-") and e["box"]["id"][4:].isdigit()]
    return f"obj-{max(values, default=0) + 1}"


def add_box(patcher: dict[str, Any], **box: Any) -> str:
    identifier = next_id(patcher)
    box["id"] = identifier
    patcher.setdefault("boxes", []).append({"box": box})
    return identifier


def connect(patcher: dict[str, Any], source: str, outlet: int, destination: str, inlet: int = 0) -> None:
    patcher.setdefault("lines", []).append(
        {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}
    )


def tune_size(code: str) -> str:
    param_anchor = "Param size(0.45);"
    params = """Param size(0.45);
Param size_source(0);
Param size_depth(0.65);
Param size_slew_ms(1000);
Param size_entropy(0);
Param size_purity(1);
Param size_coherence(0);"""
    if code.count(param_anchor) != 1:
        raise RuntimeError("Could not locate v5.5 size parameter")
    code = code.replace(param_anchor, params)
    history_anchor = "History feedback_z(0.84);"
    if code.count(history_anchor) != 1:
        raise RuntimeError("Could not locate v5.5 history anchor")
    code = code.replace(history_anchor, history_anchor + "\nHistory size_z(0.45);")
    size_anchor = """s = clamp(size, 0, 1);
size_scale = pow(2, (s * 3) - 1.5);"""
    size_mapping = """size_mode = clamp(size_source, 0, 3);
size_data = (size_mode >= 0.5) * (size_mode < 1.5) * clamp(size_entropy, 0, 1)
    + (size_mode >= 1.5) * (size_mode < 2.5) * clamp(size_purity, 0, 1)
    + (size_mode >= 2.5) * clamp(size_coherence, 0, 1);
size_is_manual = size_mode < 0.5;
size_target = size_is_manual * clamp(size, 0, 1)
    + (1 - size_is_manual) * clamp(size + clamp(size_depth, 0, 1) * (size_data - 0.5), 0, 1);
size_seconds = max(size_slew_ms, 5) * 0.001;
size_coeff = 1 - exp(-1 / max(sr * size_seconds, 1));
size_z = size_z + size_coeff * (size_target - size_z);
s = clamp(size_z, 0, 1);
size_scale = pow(2, (s * 3) - 1.5);"""
    if code.count(size_anchor) != 1:
        raise RuntimeError("Could not locate v5.5 direct size mapping")
    return code.replace(size_anchor, size_mapping)


def add_bloch_harmonic_modal(code: str) -> str:
    """Add smoothed degree-2/3 controls to the regenerative v5.6 FDN."""
    parameter_anchor = "Param pauli_depth(0.16);"
    parameters = """Param pauli_depth(0.16);
Param harmonic_resonance(0.5);
Param spectral_tilt(0);
Param modal_warp(0);
Param harmonic_slew_ms(120);
Param mw1(1); Param mw2(1); Param mw3(1); Param mw4(1);
Param mw5(1); Param mw6(1); Param mw7(1); Param mw8(1);"""
    history_anchor = "History size_z(0.45);"
    histories = """History size_z(0.45);
History resonance_z(0.5); History tilt_z(0); History warp_z(0);
History mw1_z(1); History mw2_z(1); History mw3_z(1); History mw4_z(1);
History mw5_z(1); History mw6_z(1); History mw7_z(1); History mw8_z(1);"""
    smoothing_anchor = "size_scale = pow(2, (s * 3) - 1.5);"
    smoothing = """size_scale = pow(2, (s * 3) - 1.5);
harmonic_seconds = max(harmonic_slew_ms, 0.1) * 0.001;
harmonic_coeff = 1 - exp(-1 / max(sr * harmonic_seconds, 1));
resonance_z = resonance_z + harmonic_coeff * (clamp(harmonic_resonance, 0, 1) - resonance_z);
tilt_z = tilt_z + harmonic_coeff * (clamp(spectral_tilt, -1, 1) - tilt_z);
warp_z = warp_z + harmonic_coeff * (clamp(modal_warp, -1, 1) - warp_z);
mw1_z = mw1_z + harmonic_coeff * (clamp(mw1, 0.35, 1.65) - mw1_z);
mw2_z = mw2_z + harmonic_coeff * (clamp(mw2, 0.35, 1.65) - mw2_z);
mw3_z = mw3_z + harmonic_coeff * (clamp(mw3, 0.35, 1.65) - mw3_z);
mw4_z = mw4_z + harmonic_coeff * (clamp(mw4, 0.35, 1.65) - mw4_z);
mw5_z = mw5_z + harmonic_coeff * (clamp(mw5, 0.35, 1.65) - mw5_z);
mw6_z = mw6_z + harmonic_coeff * (clamp(mw6, 0.35, 1.65) - mw6_z);
mw7_z = mw7_z + harmonic_coeff * (clamp(mw7, 0.35, 1.65) - mw7_z);
mw8_z = mw8_z + harmonic_coeff * (clamp(mw8, 0.35, 1.65) - mw8_z);"""
    delay_block = """d1 = clamp(31 * size_scale * exp(deform_amount * geom1) * sr * 0.001, 16, 191999);
d2 = clamp(37 * size_scale * exp(deform_amount * geom2) * sr * 0.001, 16, 191999);
d3 = clamp(43 * size_scale * exp(deform_amount * geom3) * sr * 0.001, 16, 191999);
d4 = clamp(47 * size_scale * exp(deform_amount * geom4) * sr * 0.001, 16, 191999);
d5 = clamp(53 * size_scale * exp(deform_amount * geom5) * sr * 0.001, 16, 191999);
d6 = clamp(59 * size_scale * exp(deform_amount * geom6) * sr * 0.001, 16, 191999);
d7 = clamp(67 * size_scale * exp(deform_amount * geom7) * sr * 0.001, 16, 191999);
d8 = clamp(73 * size_scale * exp(deform_amount * geom8) * sr * 0.001, 16, 191999);"""
    warped_delays = """d1 = clamp(31 * size_scale * exp(deform_amount * geom1 - 0.18 * warp_z) * sr * 0.001, 16, 191999);
d2 = clamp(37 * size_scale * exp(deform_amount * geom2 + 0.14 * warp_z) * sr * 0.001, 16, 191999);
d3 = clamp(43 * size_scale * exp(deform_amount * geom3 - 0.10 * warp_z) * sr * 0.001, 16, 191999);
d4 = clamp(47 * size_scale * exp(deform_amount * geom4 + 0.07 * warp_z) * sr * 0.001, 16, 191999);
d5 = clamp(53 * size_scale * exp(deform_amount * geom5 - 0.05 * warp_z) * sr * 0.001, 16, 191999);
d6 = clamp(59 * size_scale * exp(deform_amount * geom6 + 0.09 * warp_z) * sr * 0.001, 16, 191999);
d7 = clamp(67 * size_scale * exp(deform_amount * geom7 - 0.13 * warp_z) * sr * 0.001, 16, 191999);
d8 = clamp(73 * size_scale * exp(deform_amount * geom8 + 0.17 * warp_z) * sr * 0.001, 16, 191999);"""
    write_block = """dl1.write(tanh( excite + feedback_gain * n1));
dl2.write(tanh(-excite + feedback_gain * n2));
dl3.write(tanh( excite + feedback_gain * n3));
dl4.write(tanh(-excite + feedback_gain * n4));
dl5.write(tanh(-excite + feedback_gain * n5));
dl6.write(tanh( excite + feedback_gain * n6));
dl7.write(tanh(-excite + feedback_gain * n7));
dl8.write(tanh( excite + feedback_gain * n8));"""
    harmonic_writes = """tmw1 = clamp(mw1_z * (1 - 0.16 * tilt_z), 0.35, 1.65);
tmw2 = clamp(mw2_z * (1 - 0.11 * tilt_z), 0.35, 1.65);
tmw3 = clamp(mw3_z * (1 - 0.06 * tilt_z), 0.35, 1.65);
tmw4 = clamp(mw4_z * (1 - 0.02 * tilt_z), 0.35, 1.65);
tmw5 = clamp(mw5_z * (1 + 0.02 * tilt_z), 0.35, 1.65);
tmw6 = clamp(mw6_z * (1 + 0.06 * tilt_z), 0.35, 1.65);
tmw7 = clamp(mw7_z * (1 + 0.11 * tilt_z), 0.35, 1.65);
tmw8 = clamp(mw8_z * (1 + 0.16 * tilt_z), 0.35, 1.65);
rg1 = clamp(feedback_gain + 0.045 * resonance_z * (tmw1 - 1), 0, 1.18);
rg2 = clamp(feedback_gain + 0.045 * resonance_z * (tmw2 - 1), 0, 1.18);
rg3 = clamp(feedback_gain + 0.045 * resonance_z * (tmw3 - 1), 0, 1.18);
rg4 = clamp(feedback_gain + 0.045 * resonance_z * (tmw4 - 1), 0, 1.18);
rg5 = clamp(feedback_gain + 0.045 * resonance_z * (tmw5 - 1), 0, 1.18);
rg6 = clamp(feedback_gain + 0.045 * resonance_z * (tmw6 - 1), 0, 1.18);
rg7 = clamp(feedback_gain + 0.045 * resonance_z * (tmw7 - 1), 0, 1.18);
rg8 = clamp(feedback_gain + 0.045 * resonance_z * (tmw8 - 1), 0, 1.18);
dl1.write(tanh( excite * tmw1 + rg1 * n1));
dl2.write(tanh(-excite * tmw2 + rg2 * n2));
dl3.write(tanh( excite * tmw3 + rg3 * n3));
dl4.write(tanh(-excite * tmw4 + rg4 * n4));
dl5.write(tanh(-excite * tmw5 + rg5 * n5));
dl6.write(tanh( excite * tmw6 + rg6 * n6));
dl7.write(tanh(-excite * tmw7 + rg7 * n7));
dl8.write(tanh( excite * tmw8 + rg8 * n8));"""
    replacements = (
        (parameter_anchor, parameters),
        (history_anchor, histories),
        (smoothing_anchor, smoothing),
        (delay_block, warped_delays),
        (write_block, harmonic_writes),
    )
    for old, new in replacements:
        if code.count(old) != 1:
            raise RuntimeError("Could not locate v5.6 harmonic-modal Gen anchor")
        code = code.replace(old, new)
    return code


def add_parameter_control(patcher, gen_id, label, parameter, default, x, maximum=1.0):
    add_box(patcher, maxclass="comment", text=label, patching_rect=[x, 980, 70, 18],
            presentation=1, presentation_rect=[x, 18, 70, 18], numinlets=1, numoutlets=0,
            textcolor=[0.72, 0.83, 0.96, 1.0])
    number = add_box(patcher, maxclass="flonum", format=6, patching_rect=[x, 1002, 62, 22],
                     presentation=1, presentation_rect=[x, 39, 62, 22], minimum=0.0,
                     maximum=maximum, parameter_enable=0, numinlets=1, numoutlets=2,
                     outlettype=["", "bang"])
    initial = add_box(patcher, maxclass="newobj", text=f"loadmess {default}",
                      patching_rect=[x, 1030, 88, 22], numinlets=1, numoutlets=1, outlettype=["float"])
    prepend = add_box(patcher, maxclass="newobj", text=f"prepend {parameter}",
                      patching_rect=[x, 1058, 135, 22], numinlets=1, numoutlets=1, outlettype=[""])
    connect(patcher, initial, 0, number)
    connect(patcher, number, 0, prepend)
    connect(patcher, prepend, 0, gen_id)


def add_acoustic_routes(patcher: dict[str, Any], gen_id: str) -> None:
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    raw = next(box for box in boxes if box.get("text") == "r qmw.osc.raw")
    qmw = add_box(patcher, maxclass="newobj", text="OSC-route /qmw",
                  patching_rect=[1080, 1180, 100, 22])
    acoustics = add_box(patcher, maxclass="newobj", text="OSC-route /acoustics",
                        patching_rect=[1195, 1180, 135, 22])
    domains = add_box(patcher, maxclass="newobj", text="OSC-route /reverb /modal",
                      patching_rect=[1345, 1180, 180, 22])
    reverb = add_box(patcher, maxclass="newobj",
                     text="OSC-route /resonance /decay /damping",
                     patching_rect=[1540, 1180, 270, 22])
    modal = add_box(patcher, maxclass="newobj",
                    text="OSC-route /tilt /warp /weights",
                    patching_rect=[1540, 1215, 230, 22])
    connect(patcher, raw["id"], 0, qmw)
    connect(patcher, qmw, 0, acoustics)
    connect(patcher, acoustics, 0, domains)
    connect(patcher, domains, 0, reverb)
    connect(patcher, domains, 1, modal)
    scalars = (
        (reverb, 0, "harmonic_resonance"),
        (reverb, 1, "decay"),
        (reverb, 2, "absorb"),
        (modal, 0, "spectral_tilt"),
        (modal, 1, "modal_warp"),
    )
    for index, (source, outlet, parameter) in enumerate(scalars):
        prepend = add_box(
            patcher, maxclass="newobj", text=f"prepend {parameter}",
            patching_rect=[1080 + (index % 3) * 180, 1250 + (index // 3) * 35, 165, 22],
        )
        connect(patcher, source, outlet, prepend)
        connect(patcher, prepend, 0, gen_id)
    unpack = add_box(
        patcher, maxclass="newobj", text="unpack 0. 0. 0. 0. 0. 0. 0. 0.",
        patching_rect=[1080, 1320, 270, 22],
    )
    connect(patcher, modal, 2, unpack)
    for index in range(8):
        prepend = add_box(
            patcher, maxclass="newobj", text=f"prepend mw{index + 1}",
            patching_rect=[1080 + (index % 4) * 135, 1355 + (index // 4) * 35, 112, 22],
        )
        connect(patcher, unpack, index, prepend)
        connect(patcher, prepend, 0, gen_id)


def build_surface() -> dict[str, Any]:
    surface = load(SURFACE_SOURCE)
    patcher = surface["patcher"]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    gen = next(box for box in boxes if box.get("maxclass") == "gen.codebox~")
    gen["code"] = add_bloch_harmonic_modal(tune_size(gen["code"]))

    # Compact the existing reverb controls to make a single coherent header strip.
    positions = {"FB · 1=HOLD": 280.0, "DAMPING": 365.0, "COMB": 450.0}
    for label, x in positions.items():
        box = next(b for b in boxes if b.get("text") == label)
        old_x = box["presentation_rect"][0]
        box["presentation_rect"][0] = x
        # Move the number directly beneath the label by following shared old x.
        number = next(b for b in boxes if b.get("maxclass") == "flonum"
                      and b.get("presentation_rect", [None])[0] == old_x
                      and b.get("presentation_rect", [0, 0])[1] == 39.0)
        number["presentation_rect"][0] = x
    for box in boxes:
        if box.get("text") == "QMW GEOMETRY REVERB v5.5":
            box["text"] = "QMW GEO REVERB v5.6"
            box["presentation_rect"][2] = 240.0

    source_label = add_box(patcher, maxclass="comment", text="SIZE SOURCE", patching_rect=[535, 980, 90, 18],
                           presentation=1, presentation_rect=[535, 18, 90, 18], numinlets=1, numoutlets=0,
                           textcolor=[0.95, 0.76, 0.11, 1.0])
    menu = add_box(patcher, maxclass="umenu", patching_rect=[535, 1002, 95, 22],
                   presentation=1, presentation_rect=[535, 39, 95, 22], items=["Manual", ",", "Entropy", ",", "Purity", ",", "Coherence"],
                   parameter_enable=0, numinlets=1, numoutlets=3, outlettype=["int", "", ""])
    menu_init = add_box(patcher, maxclass="newobj", text="loadmess 0", patching_rect=[535, 1030, 75, 22], numinlets=1, numoutlets=1, outlettype=["int"])
    menu_prepend = add_box(patcher, maxclass="newobj", text="prepend size_source", patching_rect=[535, 1058, 135, 22], numinlets=1, numoutlets=1, outlettype=[""])
    connect(patcher, menu_init, 0, menu)
    connect(patcher, menu, 0, menu_prepend)
    connect(patcher, menu_prepend, 0, gen["id"])
    add_parameter_control(patcher, gen["id"], "DEPTH", "size_depth", 0.65, 640.0, 1.0)
    add_parameter_control(patcher, gen["id"], "SLEW ms", "size_slew_ms", 1000, 700.0, 10000.0)

    route = next(b for b in boxes if b.get("text") == "OSC-route /magnitude /harmonics /entropy /purity /coherence")
    entropy_norm = next(b for b in boxes if b.get("text") == "expr min(1., max(0., $f1 / 4.))")
    coherence_norm = next(b for b in boxes if b.get("text") == "expr min(1., max(0., $f1 / 15.))")
    for parameter, source, outlet in (("size_entropy", entropy_norm, 0), ("size_purity", route, 3), ("size_coherence", coherence_norm, 0)):
        prepend = add_box(patcher, maxclass="newobj", text=f"prepend {parameter}", patching_rect=[900, 980 + 28 * outlet, 145, 22], numinlets=1, numoutlets=1, outlettype=[""])
        connect(patcher, source["id"], outlet, prepend)
        connect(patcher, prepend, 0, gen["id"])
    add_acoustic_routes(patcher, gen["id"])
    return surface


def main() -> int:
    control, rack, surface = load(CONTROL_SOURCE), load(RACK_SOURCE), build_surface()
    rack_matches = [e["box"] for e in control["patcher"]["boxes"] if e["box"].get("name") == RACK_SOURCE.name]
    surface_matches = [e["box"] for e in control["patcher"]["boxes"] if e["box"].get("name") == SURFACE_SOURCE.name]
    if len(rack_matches) != 1 or len(surface_matches) != 1:
        raise RuntimeError("Could not locate v5.5 embedded modules")
    rack_matches[0]["name"], rack_matches[0]["patcher"] = RACK_OUTPUT.name, deepcopy(rack["patcher"])
    surface_matches[0]["name"], surface_matches[0]["patcher"] = SURFACE_OUTPUT.name, deepcopy(surface["patcher"])
    adapter = add_box(
        control["patcher"],
        maxclass="bpatcher",
        name="QMW_Bloch_Harmonic_Spat_Modal_v1.maxpat",
        patching_rect=[1840, 915, 10, 10],
        numinlets=4,
        numoutlets=3,
        border=0,
        hidden=1,
    )
    del adapter
    control["patcher"].setdefault("dependency_cache", []).append(
        {
            "name": "QMW_Bloch_Harmonic_Spat_Modal_v1.maxpat",
            "bootpath": str(ROOT / "control_room_modules"),
            "patcherrelativepath": "control_room_modules",
            "type": "JSON",
            "implicit": 1,
        }
    )
    for entry in control["patcher"]["boxes"]:
        if entry["box"].get("text") == "QMW CONTROL ROOM v5.5 · REGENERATIVE GEOMETRY":
            entry["box"]["text"] = "QMW CONTROL ROOM v5.6 · QUANTUM SIZE"
    CONTROL_OUTPUT.write_text(json.dumps(control, indent=4) + "\n")
    RACK_OUTPUT.write_text(json.dumps(rack, indent=4) + "\n")
    SURFACE_OUTPUT.write_text(json.dumps(surface, indent=4) + "\n")
    print(f"Built {CONTROL_OUTPUT.name}; v5.5 remains unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
