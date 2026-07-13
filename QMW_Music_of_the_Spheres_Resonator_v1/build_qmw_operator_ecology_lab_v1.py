#!/usr/bin/env python3
"""Build QMW_Operator_Ecology_Lab_v1.maxpat deterministically."""

from __future__ import annotations

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "QMW_Operator_Ecology_Lab_v1.maxpat"
TANGLE_IR = ROOT / "algebraic_surfaces/tanglecube_v1/living/state_000002/ir_surface_laplacian_r000002.wav"
HEART_IR = ROOT / "algebraic_surfaces/heart_v1/living/state_000001/ir_surface_laplacian_r000001.wav"


class PatchBuilder:
    def __init__(self) -> None:
        self.boxes: list[dict] = []
        self.lines: list[dict] = []
        self.counter = 0

    def box(
        self,
        maxclass: str,
        rect: list[float],
        *,
        text: str | None = None,
        presentation: bool = False,
        presentation_rect: list[float] | None = None,
        **attributes,
    ) -> str:
        self.counter += 1
        identifier = f"obj-{self.counter}"
        payload: dict = {
            "id": identifier,
            "maxclass": maxclass,
            "patching_rect": rect,
        }
        if text is not None:
            payload["text"] = text
        if maxclass == "newobj":
            payload["classnamespace"] = "box"
        if maxclass == "panel":
            # Decorative presentation panels must never obscure or intercept
            # controls such as dropfile, buttons, menus, and number boxes.
            payload["background"] = 1
            payload["ignoreclick"] = 1
        if presentation:
            payload["presentation"] = 1
            payload["presentation_rect"] = presentation_rect or rect
        payload.update(attributes)
        self.boxes.append({"box": payload})
        return identifier

    def connect(
        self,
        source: str,
        source_outlet: int,
        destination: str,
        destination_inlet: int,
        *,
        hidden: bool = False,
    ) -> None:
        line: dict = {
            "source": [source, source_outlet],
            "destination": [destination, destination_inlet],
        }
        if hidden:
            line["hidden"] = 1
        self.lines.append({"patchline": line})


def build() -> dict:
    p = PatchBuilder()
    title = p.box(
        "comment", [24, 18, 900, 34],
        text="QMW OPERATOR ECOLOGY LAB v1 — geometry / operator / quantum candidate audition",
        presentation=True,
        fontsize=20.0,
        fontface=1,
        textcolor=[0.92, 0.96, 1.0, 1.0],
    )
    p.box(
        "comment", [24, 54, 1220, 42],
        text="Four equally privileged candidate slots. Drag an IR onto any slot, use X/Y to interpolate, or let /living/ir/candidate safely load the selected LIVE TARGET slot.",
        presentation=True,
        fontsize=12.0,
        textcolor=[0.68, 0.75, 0.84, 1.0],
    )

    # Candidate panels and controls.
    colors = (
        [0.16, 0.29, 0.42, 1.0],
        [0.40, 0.18, 0.29, 1.0],
        [0.18, 0.37, 0.28, 1.0],
        [0.34, 0.27, 0.14, 1.0],
    )
    labels = ("A  TANGLECUBE", "B  HEART", "C  CANDIDATE", "D  CANDIDATE")
    slot_x = (24, 352, 680, 1008)
    dropfiles: list[str] = []
    path_displays: list[str] = []
    weight_displays: list[str] = []
    audition_messages: list[str] = []
    open_messages: list[str] = []
    for index, x in enumerate(slot_x):
        p.box(
            "panel", [x, 112, 304, 178],
            presentation=True,
            bgcolor=colors[index],
            border=1,
            rounded=10,
        )
        p.box(
            "comment", [x + 14, 124, 270, 24],
            text=labels[index], presentation=True,
            fontsize=15.0, fontface=1,
            textcolor=[1.0, 1.0, 1.0, 1.0],
        )
        dropfiles.append(
            p.box(
                "dropfile", [x + 14, 154, 276, 44],
                presentation=True,
                types=["WAVE", "AIFF", "FLAC"],
            )
        )
        initial_path = (
            str(TANGLE_IR) if index == 0 else
            str(HEART_IR) if index == 1 else
            "drop an IR file here"
        )
        path_displays.append(
            p.box(
                "message", [x + 14, 206, 276, 32],
                text=initial_path, presentation=True,
                fontsize=10.0,
            )
        )
        audition_messages.append(
            p.box(
                "message", [x + 14, 250, 94, 24],
                text=f"audition {index} 250", presentation=True,
            )
        )
        open_messages.append(
            p.box(
                "message", [x + 122, 250, 68, 24],
                text="open", presentation=True,
            )
        )
        weight_displays.append(
            p.box(
                "flonum", [x + 204, 250, 86, 24], presentation=True,
                minimum=0.0, maximum=1.0, ignoreclick=1,
            )
        )

    # XY and live target controls.
    p.box("panel", [24, 310, 420, 220], presentation=True,
          bgcolor=[0.09, 0.11, 0.15, 1.0], border=1, rounded=10)
    p.box("comment", [40, 326, 370, 24], text="CANDIDATE FIELD", presentation=True,
          fontsize=15.0, fontface=1, textcolor=[0.9, 0.95, 1.0, 1.0])
    p.box("comment", [40, 364, 70, 22], text="X  A ↔ B", presentation=True)
    x_float = p.box("flonum", [116, 362, 80, 24], presentation=True,
                    minimum=0.0, maximum=1.0, parameter_enable=1,
                    varname="candidate_x")
    p.box("comment", [40, 400, 70, 22], text="Y  AB ↔ CD", presentation=True)
    y_float = p.box("flonum", [116, 398, 80, 24], presentation=True,
                    minimum=0.0, maximum=1.0, parameter_enable=1,
                    varname="candidate_y")
    xy_pak = p.box("newobj", [218, 380, 78, 23], text="pak 0. 0.")
    xy_prepend = p.box("newobj", [310, 380, 75, 23], text="prepend xy")
    p.connect(x_float, 0, xy_pak, 0)
    p.connect(y_float, 0, xy_pak, 1)
    p.connect(xy_pak, 0, xy_prepend, 0)

    p.box("comment", [40, 442, 100, 22], text="LIVE TARGET", presentation=True)
    target_menu = p.box(
        "umenu", [146, 440, 100, 24], presentation=True,
        items=["AUTO C/D", ",", "A", ",", "B", ",", "C", ",", "D"],
        parameter_enable=1, varname="live_target",
    )
    target_prepend = p.box("newobj", [270, 440, 78, 23], text="prepend slot")
    p.connect(target_menu, 0, target_prepend, 0)
    reset_message = p.box("message", [40, 480, 54, 24], text="reset", presentation=True)

    # Metadata / OSC panel.
    p.box("panel", [468, 310, 844, 220], presentation=True,
          bgcolor=[0.09, 0.11, 0.15, 1.0], border=1, rounded=10)
    p.box("comment", [484, 326, 310, 24], text="LIVING SPECTRAL GEOMETRY — OSC 7460 / ACK 7461",
          presentation=True, fontsize=15.0, fontface=1,
          textcolor=[0.9, 0.95, 1.0, 1.0])
    p.box("comment", [484, 364, 64, 22], text="MODEL", presentation=True)
    model_display = p.box("message", [552, 362, 210, 24], text="none", presentation=True)
    p.box("comment", [780, 364, 76, 22], text="REVISION", presentation=True)
    revision_display = p.box("number", [858, 362, 72, 24], presentation=True)
    p.box("comment", [484, 400, 90, 22], text="FREQUENCIES", presentation=True)
    frequency_display = p.box("message", [578, 398, 716, 24], text="none", presentation=True)
    p.box("comment", [484, 436, 90, 22], text="QUANTUM P", presentation=True)
    quantum_display = p.box("message", [578, 434, 716, 24], text="none", presentation=True)
    p.box("comment", [484, 472, 64, 22], text="STATUS", presentation=True)
    status_display = p.box("message", [552, 470, 742, 34], text="initializing", presentation=True)

    # Source and output strip.
    p.box("panel", [24, 552, 1288, 124], presentation=True,
          bgcolor=[0.08, 0.09, 0.12, 1.0], border=1, rounded=10)
    p.box("comment", [40, 568, 170, 22], text="EXCITATION INPUT", presentation=True,
          fontsize=13.0, fontface=1)
    input_meter_l = p.box("meter~", [42, 596, 190, 18], presentation=True)
    input_meter_r = p.box("meter~", [42, 622, 190, 18], presentation=True)
    source_menu = p.box(
        "umenu", [270, 568, 150, 24], presentation=True,
        items=["QUANTUM GENEXPR", ",", "AUDIO INPUT"],
        parameter_enable=1, varname="excitation_source",
    )
    impulse_button = p.box("button", [270, 606, 28, 28], presentation=True)
    p.box("comment", [306, 610, 180, 22], text="IMPULSE TEST", presentation=True)
    p.box("comment", [520, 568, 120, 22], text="MASTER", presentation=True,
          fontsize=13.0, fontface=1)
    master_float = p.box("flonum", [520, 596, 80, 24], presentation=True,
                         minimum=0.0, maximum=1.0, parameter_enable=1,
                         varname="master_gain")
    p.box("comment", [624, 600, 240, 22], text="equal-power slot interpolation", presentation=True)
    output_meter_l = p.box("meter~", [1088, 588, 190, 18], presentation=True)
    output_meter_r = p.box("meter~", [1088, 620, 190, 18], presentation=True)
    dac = p.box("ezdac~", [988, 588, 48, 48], presentation=True)

    # Core controller.
    controller = p.box("newobj", [430, 760, 220, 23], text="js qmw_operator_ecology_lab_v1.js")
    p.connect(xy_prepend, 0, controller, 2)
    p.connect(target_prepend, 0, controller, 2)
    p.connect(reset_message, 0, controller, 2)
    status_set = p.box("newobj", [430, 792, 74, 23], text="prepend set")
    p.connect(controller, 9, status_set, 0)
    p.connect(status_set, 0, status_display, 0)

    # Slot convolution engines and gain lines.
    spectral_l = p.box("newobj", [40, 692, 146, 23], text="receive~ qmw_spectral_L")
    spectral_r = p.box("newobj", [40, 724, 146, 23], text="receive~ qmw_spectral_R")
    adc = p.box("newobj", [204, 692, 68, 23], text="adc~ 1 2")
    source_index = p.box("newobj", [204, 724, 29, 23], text="+ 1")
    select_l = p.box("newobj", [290, 692, 72, 23], text="selector~ 2")
    select_r = p.box("newobj", [290, 724, 72, 23], text="selector~ 2")
    click = p.box("newobj", [128, 724, 42, 23], text="click~")
    click_gain = p.box("newobj", [182, 724, 48, 23], text="*~ 0.2")
    source_l = p.box("newobj", [382, 692, 32, 23], text="+~")
    source_r = p.box("newobj", [382, 724, 32, 23], text="+~")
    p.connect(source_menu, 0, source_index, 0)
    p.connect(source_index, 0, select_l, 0)
    p.connect(source_index, 0, select_r, 0)
    p.connect(spectral_l, 0, select_l, 1)
    p.connect(spectral_r, 0, select_r, 1)
    p.connect(adc, 0, select_l, 2)
    p.connect(adc, 1, select_r, 2)
    p.connect(impulse_button, 0, click, 0)
    p.connect(click, 0, click_gain, 0)
    p.connect(select_l, 0, source_l, 0)
    p.connect(select_r, 0, source_r, 0)
    p.connect(click_gain, 0, source_l, 1)
    p.connect(click_gain, 0, source_r, 1)
    p.connect(source_l, 0, input_meter_l, 0)
    p.connect(source_r, 0, input_meter_r, 0)

    # One shared HIRT matrix: two live inputs feeding four stereo IR candidates.
    # Outputs 1/2=A, 3/4=B, 5/6=C, 7/8=D.
    convolver = p.box(
        "newobj", [40, 810, 180, 23],
        text="multiconvolve~ 2 8 medium",
    )
    p.connect(source_l, 0, convolver, 0)
    p.connect(source_r, 0, convolver, 1)

    wet_l: list[str] = []
    wet_r: list[str] = []
    gain_lines: list[str] = []
    for index in range(4):
        y = 850 + index * 72
        buffer_name = f"qmw_ecology_{'ABCD'[index]}"
        ir_buffer = p.box(
            "newobj", [40, y, 190, 23],
            text=f"buffer~ {buffer_name}",
        )
        line = p.box("newobj", [676, y, 72, 23], text="line 0.")
        gain_lines.append(line)
        signal_gain = p.box("newobj", [762, y, 38, 23], text="sig~")
        left = p.box("newobj", [330, y, 38, 23], text="*~")
        right = p.box("newobj", [382, y, 38, 23], text="*~")
        wet_l.append(left)
        wet_r.append(right)
        set_matrix = p.box(
            "message", [246, y, 360, 23],
            text=(
                f"set 1 {index * 2 + 1} {buffer_name} 1, "
                f"set 2 {index * 2 + 2} {buffer_name} 2"
            ),
        )
        load_trigger = p.box("newobj", [246, y + 28, 42, 23], text="t b b")
        loaded_message = p.box("message", [590, y, 64, 23], text=f"loaded {index}")
        done_message = p.box("message", [676, y + 28, 54, 23], text=f"done {index}")
        p.connect(convolver, index * 2, left, 0)
        p.connect(convolver, index * 2 + 1, right, 0)
        p.connect(controller, index, ir_buffer, 0)
        route_replace = p.box("newobj", [40, y + 28, 88, 23], text="route replace")
        display_set = p.box("newobj", [138, y + 28, 74, 23], text="prepend set")
        p.connect(controller, index, route_replace, 0)
        p.connect(route_replace, 0, display_set, 0)
        p.connect(display_set, 0, path_displays[index], 0)
        # buffer~ outlet 1 bangs when an asynchronous read/replace completes.
        p.connect(ir_buffer, 1, load_trigger, 0)
        # trigger executes right-to-left: install the matrix IR, then report ready.
        p.connect(load_trigger, 1, set_matrix, 0)
        p.connect(set_matrix, 0, convolver, 0)
        p.connect(load_trigger, 0, loaded_message, 0)
        p.connect(loaded_message, 0, controller, 1)
        p.connect(controller, 4 + index, line, 0)
        p.connect(line, 0, weight_displays[index], 0)
        p.connect(line, 0, signal_gain, 0)
        p.connect(signal_gain, 0, left, 1)
        p.connect(signal_gain, 0, right, 1)
        p.connect(line, 1, done_message, 0)
        p.connect(done_message, 0, controller, 1)
        p.connect(open_messages[index], 0, ir_buffer, 0)
        load_prepend = p.box("newobj", [40 + index * 110, 1120, 100, 23], text=f"prepend loadslot {index}")
        p.connect(dropfiles[index], 0, load_prepend, 0)
        p.connect(load_prepend, 0, controller, 2)
        p.connect(audition_messages[index], 0, controller, 2)

    # Sum all candidate outputs.
    sum_l1 = p.box("newobj", [840, 820, 32, 23], text="+~")
    sum_l2 = p.box("newobj", [890, 820, 32, 23], text="+~")
    sum_l3 = p.box("newobj", [940, 820, 32, 23], text="+~")
    sum_r1 = p.box("newobj", [840, 860, 32, 23], text="+~")
    sum_r2 = p.box("newobj", [890, 860, 32, 23], text="+~")
    sum_r3 = p.box("newobj", [940, 860, 32, 23], text="+~")
    for wet, sums in ((wet_l, (sum_l1, sum_l2, sum_l3)), (wet_r, (sum_r1, sum_r2, sum_r3))):
        p.connect(wet[0], 0, sums[0], 0)
        p.connect(wet[1], 0, sums[0], 1)
        p.connect(sums[0], 0, sums[1], 0)
        p.connect(wet[2], 0, sums[1], 1)
        p.connect(sums[1], 0, sums[2], 0)
        p.connect(wet[3], 0, sums[2], 1)

    master_pack = p.box("newobj", [520, 700, 76, 23], text="pack 0. 50")
    master_line = p.box("newobj", [610, 700, 42, 23], text="line~")
    master_l = p.box("newobj", [1000, 820, 38, 23], text="*~")
    master_r = p.box("newobj", [1000, 860, 38, 23], text="*~")
    p.connect(master_float, 0, master_pack, 0)
    p.connect(master_pack, 0, master_line, 0)
    p.connect(sum_l3, 0, master_l, 0)
    p.connect(sum_r3, 0, master_r, 0)
    p.connect(master_line, 0, master_l, 1)
    p.connect(master_line, 0, master_r, 1)
    p.connect(master_l, 0, output_meter_l, 0)
    p.connect(master_r, 0, output_meter_r, 0)
    p.connect(master_l, 0, dac, 0)
    p.connect(master_r, 0, dac, 1)

    # CNMAT OSC input parsing and metadata routing.
    udp_receive = p.box("newobj", [1040, 720, 142, 23], text="udpreceive 7460 cnmat")
    osc_decode = p.box("newobj", [1040, 752, 116, 23], text="OpenSoundControl")
    osc_route = p.box(
        "newobj", [1040, 784, 690, 23],
        text=(
            "OSC-route /living/ir/candidate /living/ir/crossfade "
            "/living/model /living/revision /living/spectrum/frequencies "
            "/living/quantum/probabilities"
        ),
    )
    p.connect(udp_receive, 0, osc_decode, 0)
    # OpenSoundControl's middle outlet emits decoded address/argument lists.
    p.connect(osc_decode, 1, osc_route, 0)

    candidate_prepend = p.box("newobj", [1040, 824, 116, 23], text="prepend candidate")
    route_start = p.box("newobj", [1170, 824, 92, 23], text="OSC-route /start")
    crossfade_prepend = p.box("newobj", [1170, 856, 144, 23], text="prepend crossfade_start")
    p.connect(osc_route, 0, candidate_prepend, 0)
    p.connect(candidate_prepend, 0, controller, 0)
    p.connect(osc_route, 1, route_start, 0)
    p.connect(route_start, 0, crossfade_prepend, 0)
    p.connect(crossfade_prepend, 0, controller, 0)

    set_model = p.box("newobj", [1040, 896, 74, 23], text="prepend set")
    p.connect(osc_route, 2, set_model, 0)
    p.connect(set_model, 0, model_display, 0)
    p.connect(osc_route, 3, revision_display, 0)
    set_freq = p.box("newobj", [1130, 896, 74, 23], text="prepend set")
    p.connect(osc_route, 4, set_freq, 0)
    p.connect(set_freq, 0, frequency_display, 0)
    set_quantum = p.box("newobj", [1220, 896, 74, 23], text="prepend set")
    p.connect(osc_route, 5, set_quantum, 0)
    p.connect(set_quantum, 0, quantum_display, 0)

    # Acknowledgments to Python through CNMAT OpenSoundControl.
    route_ack = p.box("newobj", [720, 760, 174, 23], text="route ready committed failed")
    ack_prepend: list[str] = []
    ack_trigger: list[str] = []
    for index, address in enumerate((
        "/living/ir/ready",
        "/living/ir/committed",
        "/living/ir/failed",
    )):
        y = 792 + index * 32
        prepend = p.box("newobj", [720, y, 190, 23], text=f"prepend {address}")
        trigger = p.box("newobj", [924, y, 38, 23], text="t b l")
        ack_prepend.append(prepend)
        ack_trigger.append(trigger)
        p.connect(route_ack, index, prepend, 0)
        p.connect(prepend, 0, trigger, 0)
    osc_encode = p.box("newobj", [980, 824, 116, 23], text="OpenSoundControl")
    udp_send = p.box("newobj", [1110, 824, 152, 23], text="udpsend 127.0.0.1 7461")
    p.connect(controller, 8, route_ack, 0)
    for trigger in ack_trigger:
        # t b l sends the OSC address/list first, then bangs the packet out.
        p.connect(trigger, 1, osc_encode, 0)
        p.connect(trigger, 0, osc_encode, 0)
    p.connect(osc_encode, 0, udp_send, 0)

    # Initialization: A/B reference geometries and master gain.
    loadbang = p.box("newobj", [40, 1160, 58, 23], text="loadbang")
    init_a = p.box("message", [112, 1160, 400, 23], text=f"loadslot 0 {TANGLE_IR}")
    init_b = p.box("message", [112, 1192, 400, 23], text=f"loadslot 1 {HEART_IR}")
    init_master = p.box("message", [530, 1160, 34, 23], text="0.8")
    init_x = p.box("message", [580, 1160, 29, 23], text="0.")
    init_y = p.box("message", [620, 1160, 29, 23], text="0.")
    init_target = p.box("message", [660, 1160, 29, 23], text="0")
    init_source = p.box("message", [704, 1160, 29, 23], text="0")
    p.connect(loadbang, 0, init_a, 0)
    p.connect(loadbang, 0, init_b, 0)
    p.connect(loadbang, 0, init_master, 0)
    p.connect(loadbang, 0, init_x, 0)
    p.connect(loadbang, 0, init_y, 0)
    p.connect(loadbang, 0, init_target, 0)
    p.connect(loadbang, 0, init_source, 0)
    p.connect(init_a, 0, controller, 2)
    p.connect(init_b, 0, controller, 2)
    p.connect(init_master, 0, master_float, 0)
    p.connect(init_x, 0, x_float, 0)
    p.connect(init_y, 0, y_float, 0)
    p.connect(init_target, 0, target_menu, 0)
    p.connect(init_source, 0, source_menu, 0)

    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {
                "major": 9,
                "minor": 0,
                "revision": 0,
                "architecture": "x64",
                "modernui": 1,
            },
            "classnamespace": "box",
            "rect": [40.0, 60.0, 1380.0, 760.0],
            "openinpresentation": 1,
            "default_fontsize": 12.0,
            "default_fontface": 0,
            "default_fontname": "Arial",
            "gridonopen": 1,
            "gridsize": [8.0, 8.0],
            "gridsnaponopen": 1,
            "objectsnaponopen": 1,
            "statusbarvisible": 2,
            "toolbarvisible": 1,
            "lefttoolbarpinned": 0,
            "toptoolbarpinned": 0,
            "righttoolbarpinned": 0,
            "bottomtoolbarpinned": 0,
            "boxanimatetime": 200,
            "enablehscroll": 1,
            "enablevscroll": 1,
            "boxes": p.boxes,
            "lines": p.lines,
            "dependency_cache": [
                {"name": "qmw_operator_ecology_lab_v1.js", "bootpath": ".", "type": "TEXT", "implicit": 1},
                {"name": "multiconvolve~.mxo", "type": "iLaX", "implicit": 1},
                {"name": "OSC-route.mxo", "type": "iLaX", "implicit": 1},
                {"name": "OpenSoundControl.mxo", "type": "iLaX", "implicit": 1},
            ],
            "autosave": 0,
        }
    }


def main() -> None:
    OUTPUT.write_text(json.dumps(build(), indent=2), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
