"""Generate the Max 9 Heisenberg Three Experiments / 16 x 16 Resonator lab."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def box(identifier, maxclass, rect, **values):
    data = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    data.update(values)
    return {"box": data}


def line(source, outlet, destination, inlet=0):
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [destination, inlet],
        }
    }


def voice_patch():
    boxes = [
        box("in", "newobj", [28.0, 27.0, 42.0, 22.0], text="in 1", numinlets=0, numoutlets=1, outlettype=[""]),
        box("route", "newobj", [78.0, 27.0, 292.0, 22.0], text="route frequency amplitude phase pan decay", numinlets=1, numoutlets=6, outlettype=["", "", "", "", "", ""]),
        box("freq", "flonum", [78.0, 72.0, 72.0, 22.0], valueof=55.0),
        box("osc", "newobj", [78.0, 112.0, 76.0, 22.0], text="cycle~ 55.", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("amp_pack", "newobj", [168.0, 72.0, 94.0, 22.0], text="pack 0. 80.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("amp_line", "newobj", [168.0, 112.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("phase_expr", "newobj", [278.0, 72.0, 190.0, 22.0], text="expr ($f1 + 3.14159265) / 6.2831853", numinlets=1, numoutlets=1, outlettype=["float"]),
        box("phase_sig", "newobj", [278.0, 112.0, 42.0, 22.0], text="sig~", numinlets=1, numoutlets=1, outlettype=["signal"]),
        box("multiply", "newobj", [78.0, 160.0, 42.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("pan_l", "newobj", [344.0, 112.0, 170.0, 22.0], text="expr sqrt((1.-$f1)*0.5)", numinlets=1, numoutlets=1, outlettype=["float"]),
        box("pan_r", "newobj", [526.0, 112.0, 170.0, 22.0], text="expr sqrt((1.+$f1)*0.5)", numinlets=1, numoutlets=1, outlettype=["float"]),
        box("pan_l_pack", "newobj", [344.0, 151.0, 90.0, 22.0], text="pack 0. 40.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("pan_r_pack", "newobj", [526.0, 151.0, 90.0, 22.0], text="pack 0. 40.", numinlets=2, numoutlets=1, outlettype=[""]),
        box("pan_l_line", "newobj", [344.0, 189.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("pan_r_line", "newobj", [526.0, 189.0, 42.0, 22.0], text="line~", numinlets=2, numoutlets=2, outlettype=["signal", "bang"]),
        box("left", "newobj", [116.0, 230.0, 42.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("right", "newobj", [190.0, 230.0, 42.0, 22.0], text="*~", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("out_l", "newobj", [116.0, 280.0, 52.0, 22.0], text="out~ 1", numinlets=1, numoutlets=0),
        box("out_r", "newobj", [190.0, 280.0, 52.0, 22.0], text="out~ 2", numinlets=1, numoutlets=0),
        box("thispoly", "newobj", [650.0, 27.0, 70.0, 22.0], text="thispoly~", numinlets=2, numoutlets=3, outlettype=["", "", ""]),
    ]
    lines = [
        line("in", 0, "route"),
        line("route", 0, "freq"), line("freq", 0, "osc"),
        line("route", 1, "amp_pack"), line("route", 4, "amp_pack", 1), line("amp_pack", 0, "amp_line"),
        line("route", 2, "phase_expr"), line("phase_expr", 0, "phase_sig"), line("phase_sig", 0, "osc", 1),
        line("osc", 0, "multiply"), line("amp_line", 0, "multiply", 1),
        line("route", 3, "pan_l"), line("route", 3, "pan_r"),
        line("pan_l", 0, "pan_l_pack"), line("pan_r", 0, "pan_r_pack"),
        line("pan_l_pack", 0, "pan_l_line"), line("pan_r_pack", 0, "pan_r_line"),
        line("multiply", 0, "left"), line("multiply", 0, "right"),
        line("pan_l_line", 0, "left", 1), line("pan_r_line", 0, "right", 1),
        line("left", 0, "out_l"), line("right", 0, "out_r"),
    ]
    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
            "classnamespace": "box",
            "rect": [120.0, 120.0, 760.0, 340.0],
            "boxes": boxes,
            "lines": lines,
            "autosave": 0,
        }
    }


def main_patch():
    boxes = [
        box("title", "comment", [25.0, 16.0, 900.0, 28.0], text="QMW HEISENBERG LAB v1 — THREE EXPERIMENTS / 16 × 16 TRANSITION RESONATOR", fontsize=17.0),
        box("description", "comment", [25.0, 48.0, 1050.0, 40.0], text="Each resonant cell is one ordered energy-basis relation (m,n): rho[m,n] A[n,m]. COHERENT preserves alternatives; UNREAD performs and discards an intermediate measurement; RECORDED conditions the future on one outcome."),
        box("udp", "newobj", [25.0, 102.0, 126.0, 22.0], text="udpreceive 7400", numinlets=1, numoutlets=1, outlettype=[""]),
        box("route_qmw", "newobj", [170.0, 102.0, 104.0, 22.0], text="OSC-route /qmw", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_h", "newobj", [292.0, 102.0, 145.0, 22.0], text="OSC-route /heisenberg", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_active", "newobj", [455.0, 102.0, 125.0, 22.0], text="OSC-route /active", numinlets=1, numoutlets=2, outlettype=["", ""]),
        box("route_meta", "newobj", [25.0, 144.0, 650.0, 22.0], text="OSC-route /mode /outcome /disturbance /coherence_before /coherence_after /matrix", numinlets=1, numoutlets=7, outlettype=["", "", "", "", "", "", ""]),
        box("route_matrix", "newobj", [25.0, 184.0, 810.0, 22.0], text="OSC-route /begin /end /magnitude_normalized /frequency_hz /phase /pan /real /imag", numinlets=1, numoutlets=9, outlettype=["", "", "", "", "", "", "", "", ""]),
        box("pre_begin", "newobj", [850.0, 184.0, 105.0, 22.0], text="prepend begin", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_end", "newobj", [970.0, 184.0, 95.0, 22.0], text="prepend end", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_mag", "newobj", [25.0, 222.0, 185.0, 22.0], text="prepend magnitude_normalized", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_freq", "newobj", [225.0, 222.0, 150.0, 22.0], text="prepend frequency_hz", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_phase", "newobj", [390.0, 222.0, 110.0, 22.0], text="prepend phase", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_pan", "newobj", [515.0, 222.0, 100.0, 22.0], text="prepend pan", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_mode", "newobj", [700.0, 144.0, 105.0, 22.0], text="prepend mode", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_outcome", "newobj", [815.0, 144.0, 125.0, 22.0], text="prepend outcome", numinlets=1, numoutlets=1, outlettype=[""]),
        box("pre_disturbance", "newobj", [950.0, 144.0, 145.0, 22.0], text="prepend disturbance", numinlets=1, numoutlets=1, outlettype=[""]),
        box("js", "newobj", [25.0, 270.0, 285.0, 22.0], text="js qmw_heisenberg_matrix_resonator_v1.js", numinlets=1, numoutlets=3, outlettype=["", "", ""]),
        box("poly", "newobj", [25.0, 315.0, 340.0, 22.0], text="poly~ qmw_heisenberg_cell_voice_v1 256 @parallel 1", numinlets=1, numoutlets=2, outlettype=["signal", "signal"]),
        box("gain_l", "newobj", [25.0, 360.0, 42.0, 22.0], text="*~ 0.7", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("gain_r", "newobj", [90.0, 360.0, 42.0, 22.0], text="*~ 0.7", numinlets=2, numoutlets=1, outlettype=["signal"]),
        box("dac", "newobj", [25.0, 405.0, 52.0, 32.0], text="ezdac~", numinlets=2, numoutlets=0),
        box("matrix", "jit.cellblock", [410.0, 270.0, 685.0, 430.0], cols=16, rows=16, colhead=0, rowhead=0, numinlets=2, numoutlets=4, outlettype=["", "", "", ""]),
        box("status", "message", [25.0, 470.0, 350.0, 42.0], text="waiting for Heisenberg field...", numinlets=2, numoutlets=1, outlettype=[""]),
        box("mode_label", "comment", [25.0, 540.0, 280.0, 20.0], text="Intermediate observation protocol"),
        box("coherent", "message", [25.0, 570.0, 230.0, 22.0], text="/qmw/heisenberg/mode coherent", numinlets=2, numoutlets=1, outlettype=[""]),
        box("unread", "message", [25.0, 602.0, 220.0, 22.0], text="/qmw/heisenberg/mode unread", numinlets=2, numoutlets=1, outlettype=[""]),
        box("recorded", "message", [25.0, 634.0, 235.0, 22.0], text="/qmw/heisenberg/mode recorded", numinlets=2, numoutlets=1, outlettype=[""]),
        box("record", "message", [25.0, 676.0, 195.0, 22.0], text="/qmw/heisenberg/record 1", numinlets=2, numoutlets=1, outlettype=[""]),
        box("send", "newobj", [25.0, 718.0, 155.0, 22.0], text="udpsend 127.0.0.1 7412", numinlets=1, numoutlets=0),
        box("obs_label", "comment", [25.0, 760.0, 280.0, 20.0], text="Observable addressed by the matrix"),
        box("obs_x", "message", [25.0, 790.0, 205.0, 22.0], text="/qmw/heisenberg/observable X0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("obs_y", "message", [25.0, 822.0, 205.0, 22.0], text="/qmw/heisenberg/observable Y0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("obs_z", "message", [25.0, 854.0, 205.0, 22.0], text="/qmw/heisenberg/observable Z0", numinlets=2, numoutlets=1, outlettype=[""]),
        box("test", "message", [270.0, 676.0, 42.0, 22.0], text="test", numinlets=2, numoutlets=1, outlettype=[""]),
    ]
    lines = [
        line("udp", 0, "route_qmw"), line("route_qmw", 0, "route_h"), line("route_h", 0, "route_active"), line("route_active", 0, "route_meta"),
        line("route_meta", 0, "pre_mode"), line("route_meta", 1, "pre_outcome"), line("route_meta", 2, "pre_disturbance"), line("route_meta", 5, "route_matrix"),
        line("route_matrix", 0, "pre_begin"), line("route_matrix", 1, "pre_end"),
        line("route_matrix", 2, "pre_mag"), line("route_matrix", 3, "pre_freq"), line("route_matrix", 4, "pre_phase"), line("route_matrix", 5, "pre_pan"),
        line("pre_begin", 0, "js"), line("pre_end", 0, "js"),
        line("pre_mag", 0, "js"), line("pre_freq", 0, "js"), line("pre_phase", 0, "js"), line("pre_pan", 0, "js"),
        line("pre_mode", 0, "js"), line("pre_outcome", 0, "js"), line("pre_disturbance", 0, "js"),
        line("js", 0, "poly"), line("js", 1, "matrix"), line("js", 2, "status", 1),
        line("poly", 0, "gain_l"), line("poly", 1, "gain_r"), line("gain_l", 0, "dac"), line("gain_r", 0, "dac", 1),
        line("coherent", 0, "send"), line("unread", 0, "send"), line("recorded", 0, "send"), line("record", 0, "send"),
        line("obs_x", 0, "send"), line("obs_y", 0, "send"), line("obs_z", 0, "send"), line("test", 0, "js"),
    ]
    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
            "classnamespace": "box",
            "rect": [80.0, 55.0, 1130.0, 920.0],
            "gridsize": [15.0, 15.0],
            "boxes": boxes,
            "lines": lines,
            "dependency_cache": [
                {"name": "OSC-route.mxo", "type": "iLaX"},
                {"name": "qmw_heisenberg_matrix_resonator_v1.js", "type": "TEXT"},
                {"name": "qmw_heisenberg_cell_voice_v1.maxpat", "type": "JSON"},
            ],
            "autosave": 0,
        }
    }


def write_patch(path: Path, patch: dict) -> None:
    path.write_text(json.dumps(patch, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    write_patch(ROOT / "qmw_heisenberg_cell_voice_v1.maxpat", voice_patch())
    write_patch(ROOT / "QMW_Heisenberg_Laboratory_v1.maxpat", main_patch())
    print("generated QMW_Heisenberg_Laboratory_v1.maxpat and 256-cell voice")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
