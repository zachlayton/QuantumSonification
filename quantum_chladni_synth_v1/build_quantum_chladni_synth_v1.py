#!/usr/bin/env python3
"""Build the Jitter-first Quantum Chladni Max instrument."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
MAX_DIR = HERE / "max"
OUTPUT = MAX_DIR / "QMW_Quantum_Chladni_Synth_v1_5.maxpat"


class Builder:
    def __init__(self) -> None:
        self.boxes: list[dict[str, Any]] = []
        self.lines: list[dict[str, Any]] = []
        self.counter = 0

    def add(self, maxclass: str, rect: list[float], *, text: str | None = None, **attrs: Any) -> str:
        self.counter += 1
        identifier = f"obj-{self.counter}"
        box: dict[str, Any] = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
        if text is not None:
            box["text"] = text
        box.update(attrs)
        self.boxes.append({"box": box})
        return identifier

    def connect(self, source: str, outlet: int, destination: str, inlet: int = 0, order: int | None = None) -> None:
        patchline: dict[str, Any] = {"source": [source, outlet], "destination": [destination, inlet]}
        if order is not None:
            patchline["order"] = order
        self.lines.append({"patchline": patchline})


def build_patch() -> dict[str, Any]:
    b = Builder()
    b.add("comment", [24, 18, 1020, 28], text="QMW QPE × QUANTUM CHLADNI SYNTH v1.5", fontsize=18, fontface=1)
    b.add("comment", [24, 48, 1080, 36], text="Finite-register phase estimation of Laplace–Beltrami eigenvalues conditions the eigenmode superposition. The same posterior drives resonator gains and jit.la.mult spatial shape.", linecount=2)

    udp = b.add("newobj", [24, 105, 130, 22], text="udpreceive 7400")
    qmw_root = b.add("newobj", [185, 105, 105, 22], text="OSC-route /qmw")
    root = b.add("newobj", [305, 105, 125, 22], text="OSC-route /chladni")
    temporal_root = b.add("newobj", [305, 75, 300, 22], text="OSC-route /temporal-mechanics/v1/density-clock")
    temporal_route = b.add("newobj", [620, 75, 150, 22], text="OSC-route /state /pulse")
    route = b.add("newobj", [450, 105, 520, 22], text="OSC-route /begin /mode /end /strike /status /populations /geometry")
    geo = b.add("newobj", [900, 105, 220, 22], text="OSC-route /begin /vertex /end")
    prepends = []
    for index, name in enumerate(("begin", "mode", "end", "strike", "status")):
        item = b.add("newobj", [24 + index * 116, 145, 104, 22], text=f"prepend {name}")
        b.connect(route, index, item)
        prepends.append(item)
    for index, name in enumerate(("geometry_begin", "geometry_vertex", "geometry_end")):
        item = b.add("newobj", [620 + index * 155, 145, 143, 22], text=f"prepend {name}")
        b.connect(geo, index, item)
        prepends.append(item)
    population_prepend = b.add("newobj", [510, 170, 130, 22], text="prepend populations")
    b.connect(route, 5, population_prepend)
    prepends.append(population_prepend)
    router = b.add("newobj", [425, 190, 270, 22], text="js qmw_quantum_chladni_router_v1.js", numinlets=5, numoutlets=25)
    for item in prepends:
        b.connect(item, 0, router)
    temporal_state = b.add("newobj", [785, 65, 145, 22], text="prepend temporal_state")
    temporal_pulse = b.add("newobj", [785, 90, 145, 22], text="prepend temporal_pulse")
    b.connect(temporal_route, 0, temporal_state)
    b.connect(temporal_route, 1, temporal_pulse)
    b.connect(temporal_state, 0, router)
    b.connect(temporal_pulse, 0, router)
    b.connect(udp, 0, qmw_root)
    b.connect(qmw_root, 0, root)
    b.connect(qmw_root, 0, temporal_root)
    b.connect(temporal_root, 0, temporal_route)
    b.connect(root, 0, route)
    b.connect(route, 6, geo)
    raw_revision = b.add("number", [965, 185, 72, 22])
    raw_geometry = b.add("number", [1050, 185, 72, 22])
    b.add("comment", [955, 212, 90, 20], text="OSC REV")
    b.add("comment", [1045, 212, 115, 20], text="GEOMETRY N")
    b.connect(route, 2, raw_revision)
    b.connect(geo, 2, raw_geometry)

    depth = b.add("flonum", [24, 215, 70, 22], minimum=0.0, maximum=1.0)
    depth_load = b.add("newobj", [24, 185, 70, 22], text="loadmess 1.")
    decay = b.add("flonum", [118, 215, 70, 22], minimum=0.1, maximum=8.0)
    decay_load = b.add("newobj", [118, 185, 70, 22], text="loadmess 1.")
    scale = b.add("flonum", [212, 215, 70, 22], minimum=0.125, maximum=8.0)
    scale_load = b.add("newobj", [212, 185, 70, 22], text="loadmess 1.")
    population_gate = b.add("flonum", [306, 280, 70, 22], minimum=0.0, maximum=1.0)
    population_gate_load = b.add("newobj", [306, 255, 92, 22], text="loadmess 0.01")
    b.add("comment", [24, 242, 78, 20], text="QUANTUM")
    b.add("comment", [118, 242, 72, 20], text="DECAY")
    b.add("comment", [212, 242, 92, 20], text="FREQ SCALE")
    b.add("comment", [306, 305, 112, 20], text="POPULATION GATE")
    for source, dest, inlet in ((depth_load, depth, 0), (decay_load, decay, 0), (scale_load, scale, 0)):
        b.connect(source, 0, dest, inlet)
    b.connect(depth, 0, router, 1)
    b.connect(decay, 0, router, 2)
    b.connect(scale, 0, router, 3)
    b.connect(population_gate_load, 0, population_gate)
    b.connect(population_gate, 0, router, 4)

    demo_button = b.add("button", [325, 220, 24, 24])
    demo = b.add("message", [358, 221, 42, 22], text="demo")
    demo_load = b.add("newobj", [325, 185, 92, 22], text="loadmess demo")
    b.connect(demo_button, 0, demo)
    b.connect(demo, 0, router)
    b.connect(demo_load, 0, router)
    b.add("comment", [325, 247, 105, 20], text="LOCAL DEMO")
    status = b.add("message", [425, 220, 510, 22], text="waiting for Python/Jitter matrices…")
    b.connect(router, 8, status, 1)

    # Jitter modal bus: one cell per mode, six planes.
    modal = b.add("newobj", [24, 300, 250, 22], text="jit.matrix qchladni_modes 6 float32 24 1")
    unpack = b.add("newobj", [24, 335, 108, 22], text="jit.unpack 6")
    spill = b.add("newobj", [145, 335, 190, 22], text="jit.spill @plane 0 @listlength 24")
    probabilities = b.add("multislider", [24, 370, 310, 110], size=24, setminmax=[0.0, 1.0], slidercolor=[0.2, 0.75, 1.0, 1.0])
    b.connect(router, 3, modal)
    b.connect(modal, 0, unpack)
    b.connect(unpack, 3, spill)
    b.connect(spill, 0, probabilities)
    b.add("comment", [24, 488, 320, 20], text="JITTER MODAL PROBABILITY PLANE → jit.spill")

    # Exact spatial field: complex eigenbasis matrix times amplitude vector.
    amplitudes = b.add("newobj", [380, 300, 275, 22], text="jit.matrix qchladni_amplitudes 2 float32 1 24")
    eigenvectors = b.add("newobj", [680, 300, 305, 22], text="jit.matrix qchladni_eigenvectors 2 float32 24 768")
    multiply = b.add("newobj", [560, 345, 120, 22], text="jit.la.mult")
    field_unpack = b.add("newobj", [560, 380, 72, 22], text="jit.unpack 2")
    field_normalize = b.add("newobj", [545, 410, 90, 22], text="jit.normalize")
    field_bipolar_scale = b.add("newobj", [535, 440, 110, 22], text="jit.op @op * @val 2.")
    field_bipolar_offset = b.add("newobj", [535, 470, 110, 22], text="jit.op @op - @val 1.")
    visual_depth = b.add("newobj", [410, 500, 100, 22], text="scale 0. 1. 0.04 0.55")
    visual_depth_message = b.add("newobj", [410, 530, 78, 22], text="prepend val")
    field_depth = b.add("newobj", [525, 500, 130, 22], text="jit.op @op * @val 0.55")
    field_smooth = b.add("newobj", [525, 535, 190, 22], text="jit.slide @slide_up 5 @slide_down 5")
    b.connect(router, 4, amplitudes)
    b.connect(amplitudes, 0, multiply, 1)
    b.connect(router, 6, eigenvectors)
    b.connect(eigenvectors, 0, multiply, 0)
    b.connect(multiply, 0, field_unpack)
    b.connect(field_unpack, 0, field_normalize)
    b.connect(field_normalize, 0, field_bipolar_scale)
    b.connect(field_bipolar_scale, 0, field_bipolar_offset)
    b.connect(field_bipolar_offset, 0, field_depth)
    b.connect(field_depth, 0, field_smooth)
    b.connect(depth, 0, visual_depth)
    b.connect(visual_depth, 0, visual_depth_message)
    b.connect(visual_depth_message, 0, field_depth)

    coordinates = b.add("newobj", [710, 430, 290, 22], text="jit.matrix qchladni_coordinates 3 float32 1 768")
    bfg = b.add("newobj", [370, 430, 275, 22], text="jit.bfg 1 float32 @basis noise.gradient")
    bfg_gain = b.add("newobj", [370, 465, 125, 22], text="jit.op @op * @val 0.08")
    displace = b.add(
        "newobj",
        [620, 510, 505, 22],
        text='jit.expr @expr "in[0].p[0]" "in[0].p[1]" "in[0].p[2]+in[1].p[0]"',
    )
    b.connect(router, 5, coordinates)
    b.connect(coordinates, 0, bfg)
    b.connect(router, 7, bfg)
    b.connect(bfg, 0, bfg_gain)
    b.connect(field_smooth, 0, displace, 1)
    b.connect(coordinates, 0, displace, 0)

    world_toggle = b.add("toggle", [1020, 300, 24, 24])
    world_on = b.add("newobj", [1055, 300, 78, 22], text="loadmess 1")
    world = b.add("newobj", [1020, 335, 250, 22], text="jit.world qchladni @enable 1 @size 700 560 @erase_color 0.015 0.02 0.035 1")
    raw_mesh = b.add("newobj", [710, 475, 430, 22], text="jit.gl.mesh qchladni @draw_mode points @point_size 2 @color 0.35 0.35 0.42 1.")
    mesh = b.add("newobj", [820, 555, 430, 22], text="jit.gl.mesh qchladni @draw_mode points @point_size 5 @color 0.15 0.72 1. 1.")
    origin = b.add("newobj", [1020, 370, 260, 22], text="jit.gl.gridshape qchladni @shape sphere @scale 0.035 @color 1. 0.35 0.1 1.")
    camera = b.add("newobj", [820, 590, 230, 22], text="jit.gl.handle qchladni @auto_rotate 1")
    b.connect(world_toggle, 0, world)
    b.connect(world_on, 0, world_toggle)
    b.connect(coordinates, 0, raw_mesh)
    b.connect(displace, 0, mesh)
    b.connect(camera, 0, mesh)
    b.add("comment", [710, 620, 540, 36], text="Gray = received coordinates (transport diagnostic). Blue = actual eigenfield displacement V × a. Orange origin marker proves the GL context is rendering.", linecount=2)

    # Stereo modal resonator boundary.
    fallback_resonances = (
        "resonators~ smooth 110. 0.45 3.5 164.81 0.32 3.1 "
        "220. 0.25 2.8 277.18 0.20 2.5 329.63 0.16 2.2 "
        "440. 0.13 1.9 554.37 0.10 1.6 659.25 0.08 1.4"
    )
    left_res = b.add("newobj", [185, 610, 390, 22], text=fallback_resonances)
    right_res = b.add("newobj", [595, 610, 390, 22], text=fallback_resonances)
    gain = b.add("live.gain~", [330, 655, 110, 120], parameter_enable=1)
    dac = b.add("newobj", [346, 795, 78, 22], text="ezdac~")
    strike_button = b.add("button", [24, 610, 28, 28])
    strike_trigger = b.add("newobj", [65, 580, 45, 22], text="t b 1")
    strike_value = b.add("message", [65, 613, 38, 22], text="0.72")
    quantum_change = b.add("newobj", [24, 535, 52, 22], text="change")
    quantum_speedlim = b.add("newobj", [82, 535, 88, 22], text="speedlim 140")
    quantum_audition = b.add("message", [176, 535, 38, 22], text="0.28")
    b.add("comment", [24, 646, 125, 20], text="STRIKE")
    b.connect(router, 0, left_res)
    b.connect(router, 1, right_res)
    b.connect(router, 2, left_res)
    b.connect(router, 2, right_res)
    b.connect(strike_button, 0, strike_trigger)
    # trigger outputs right-to-left: enable DSP, then emit the impulse.
    b.connect(strike_trigger, 1, dac)
    b.connect(strike_trigger, 0, strike_value)
    b.connect(strike_value, 0, left_res)
    b.connect(strike_value, 0, right_res)
    b.connect(depth, 0, quantum_change)
    b.connect(quantum_change, 0, quantum_speedlim)
    b.connect(quantum_speedlim, 0, quantum_audition)
    b.connect(quantum_audition, 0, left_res)
    b.connect(quantum_audition, 0, right_res)
    b.connect(left_res, 0, gain, 0)
    b.connect(right_res, 0, gain, 1)

    # Sixteen parallel resonator banks: one per four-qubit basis state.
    voice_fallback = (
        "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 "
        "220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
    )
    for voice in range(16):
        column = voice % 4
        row = voice // 4
        x = 24 + column * 305
        y = 875 + row * 70
        voice_res = b.add("newobj", [x, y, 290, 22], text=voice_fallback)
        pan = -1.0 + 2.0 * voice / 15.0
        left_gain = ((1.0 - pan) * 0.5) ** 0.5 * 0.42
        right_gain = ((1.0 + pan) * 0.5) ** 0.5 * 0.42
        voice_left = b.add("newobj", [x, y + 27, 64, 22], text=f"*~ {left_gain:.4f}")
        voice_right = b.add("newobj", [x + 70, y + 27, 64, 22], text=f"*~ {right_gain:.4f}")
        b.add("comment", [x + 142, y + 27, 140, 20], text=f"|{voice:04b}> BANK {voice + 1}")
        b.connect(router, 9 + voice, voice_res)
        b.connect(voice_res, 0, voice_left)
        b.connect(voice_res, 0, voice_right)
        b.connect(voice_left, 0, gain, 0)
        b.connect(voice_right, 0, gain, 1)
    b.connect(gain, 0, dac, 0)
    b.connect(gain, 1, dac, 1)

    # Controls sent back to the Python simulator.
    run_toggle = b.add("toggle", [24, 725, 24, 24])
    run_load = b.add("newobj", [24, 690, 70, 22], text="loadmess 1")
    run_osc = b.add("newobj", [60, 725, 235, 22], text="o.pack /qmw/chladni/control/run")
    entanglement_osc = b.add("newobj", [300, 725, 290, 22], text="o.pack /qmw/chladni/control/entanglement")
    measure = b.add("button", [24, 765, 24, 24])
    measure_osc = b.add("newobj", [60, 765, 270, 22], text="o.pack /qmw/chladni/control/measure")
    qpe_bits = b.add("number", [430, 795, 55, 22], minimum=2, maximum=10)
    qpe_bits_load = b.add("newobj", [430, 765, 78, 22], text="loadmess 5")
    qpe_bits_osc = b.add("newobj", [495, 795, 270, 22], text="o.pack /qmw/chladni/control/qpe-bits")
    b.add("comment", [430, 820, 150, 20], text="QPE REGISTER QUBITS")
    send = b.add("newobj", [165, 810, 145, 22], text="udpsend 127.0.0.1 7473")
    geometry_load = b.add("newobj", [320, 765, 62, 22], text="loadbang")
    geometry_request_value = b.add("message", [385, 765, 30, 22], text="1")
    geometry_request = b.add("newobj", [395, 765, 270, 22], text="o.pack /qmw/chladni/control/geometry")
    loopback_button = b.add("button", [660, 765, 24, 24])
    loopback_message = b.add("message", [695, 765, 64, 22], text="loopback")
    loopback_pack = b.add("newobj", [770, 765, 210, 22], text="o.pack /qmw/chladni/status")
    loopback_send = b.add("newobj", [995, 765, 145, 22], text="udpsend 127.0.0.1 7400")
    temporal_distance = b.add("flonum", [680, 700, 70, 22], minimum=0.001, maximum=1.0)
    temporal_distance_load = b.add("newobj", [680, 675, 92, 22], text="loadmess 0.08")
    temporal_distance_pack = b.add("newobj", [755, 700, 330, 22], text="o.pack /qmw/temporal-mechanics/v1/control/distance")
    temporal_coherence = b.add("flonum", [680, 735, 70, 22], minimum=0.0, maximum=1.0)
    temporal_coherence_load = b.add("newobj", [680, 760, 92, 22], text="loadmess 0.35")
    temporal_coherence_pack = b.add("newobj", [755, 735, 380, 22], text="o.pack /qmw/temporal-mechanics/v1/control/coherence-depth")
    temporal_send = b.add("newobj", [1090, 700, 145, 22], text="udpsend 127.0.0.1 7444")
    b.connect(run_load, 0, run_toggle)
    b.connect(run_toggle, 0, run_osc)
    b.connect(run_osc, 0, send)
    b.connect(depth, 0, entanglement_osc)
    b.connect(entanglement_osc, 0, send)
    b.connect(measure, 0, measure_osc)
    b.connect(measure_osc, 0, send)
    b.connect(qpe_bits_load, 0, qpe_bits)
    b.connect(qpe_bits, 0, qpe_bits_osc)
    b.connect(qpe_bits_osc, 0, send)
    b.connect(geometry_load, 0, geometry_request_value)
    b.connect(geometry_request_value, 0, geometry_request)
    b.connect(geometry_request, 0, send)
    b.connect(loopback_button, 0, loopback_message)
    b.connect(loopback_message, 0, loopback_pack)
    b.connect(loopback_pack, 0, loopback_send)
    b.connect(temporal_distance_load, 0, temporal_distance)
    b.connect(temporal_distance, 0, temporal_distance_pack)
    b.connect(temporal_distance_pack, 0, temporal_send)
    b.connect(temporal_coherence_load, 0, temporal_coherence)
    b.connect(temporal_coherence, 0, temporal_coherence_pack)
    b.connect(temporal_coherence_pack, 0, temporal_send)
    b.add("comment", [315, 835, 720, 20], text="Start Python: python -m quantum_chladni_synth_v1.quantum_chladni_controller_v1")

    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
            "classnamespace": "box",
            "rect": [70, 50, 1280, 1220],
            "gridsize": [15, 15],
            "boxes": b.boxes,
            "lines": b.lines,
            "dependency_cache": [
                {"name": "qmw_quantum_chladni_router_v1.js", "type": "TEXT"},
                {"name": "OSC-route.mxo", "type": "iLaX"},
                {"name": "o.pack.mxo", "type": "iLaX"},
                {"name": "jit.bfg.mxo", "type": "iLaX"},
                {"name": "jit.spill.mxo", "type": "iLaX"},
                {"name": "jit.la.mult.mxo", "type": "iLaX"},
                {"name": "resonators~.mxo", "type": "iLaX"},
            ],
            "autosave": 0,
        }
    }


def validate(payload: dict[str, Any]) -> None:
    texts = {entry["box"].get("text", "") for entry in payload["patcher"]["boxes"]}
    required = {
        "jit.matrix qchladni_modes 6 float32 24 1",
        "jit.spill @plane 0 @listlength 24",
        "jit.la.mult",
        "jit.bfg 1 float32 @basis noise.gradient",
        "js qmw_quantum_chladni_router_v1.js",
        "OSC-route /qmw",
        "OSC-route /chladni",
        "OSC-route /temporal-mechanics/v1/density-clock",
        "prepend temporal_pulse",
        "prepend populations",
        "o.pack /qmw/temporal-mechanics/v1/control/distance",
        "udpreceive 7400",
        "o.pack /qmw/chladni/control/run",
        "o.pack /qmw/chladni/control/geometry",
        "o.pack /qmw/chladni/control/qpe-bits",
        "loadmess demo",
        "t b 1",
        "speedlim 140",
    }
    missing = required.difference(texts)
    if missing:
        raise RuntimeError(f"incomplete Quantum Chladni patch: {sorted(missing)}")
    if not any(text.startswith("resonators~ smooth ") for text in texts):
        raise RuntimeError("resonators~ fallback model is missing")
    unsupported = {
        "oscparse",
        "list trim",
        "oscformat qchladni control run",
        "adc~ 1 2",
        "click~",
    }
    present = unsupported.intersection(texts)
    if present:
        raise RuntimeError(f"unsupported OSC objects present: {sorted(present)}")


def main() -> int:
    payload = build_patch()
    validate(payload)
    MAX_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
