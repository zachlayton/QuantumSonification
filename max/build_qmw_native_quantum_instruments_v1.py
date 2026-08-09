from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def box(identifier, maxclass, rect, **values):
    data = {"id": identifier, "maxclass": maxclass, "patching_rect": rect}
    data.update(values)
    return {"box": data}


def line(source, outlet, destination, inlet=0):
    return {"patchline": {"source": [source, outlet], "destination": [destination, inlet]}}


boxes = [
    box("title", "comment", [25, 15, 900, 25], text="QMW Native Quantum Instruments v1 — spinor, EPR, exchange", fontsize=16),
    box("subtitle", "comment", [25, 44, 950, 32], text="State input 7482; source control output 7483. Python remains the physics engine while Max selects and resets its source."),
    box("source_label", "comment", [25, 68, 95, 20], text="excitation source"),
    box("source_menu", "umenu", [125, 66, 260, 22], items=["all_native", ",", "spin_1_2_precession", ",", "quantum_entanglement_epr", ",", "identical_particles_boson", ",", "identical_particles_fermion", ",", "morse_potential", ",", "aharonov_bohm_effect", ",", "landau_levels", ",", "hydrogen_zeeman", ",", "hydrogen_stark", ",", "helium_variational_two_electron", ",", "delta_function_shell", ",", "dirac_hydrogen_fine_structure", ",", "dirac_step_klein"], numinlets=1, numoutlets=3, outlettype=["int", "", ""]),
    box("control_format", "newobj", [395, 66, 275, 22], text="o.pack /qmw/instrument/control/select", numinlets=1, numoutlets=1, outlettype=["FullPacket"]),
    box("control_send", "newobj", [680, 66, 175, 22], text="udpsend 127.0.0.1 7483", numinlets=1, numoutlets=0),
    box("selected_label", "comment", [865, 68, 65, 20], text="selected:"),
    box("selected", "message", [925, 66, 190, 22], text="waiting", numinlets=2, numoutlets=1, outlettype=[""]),
    box("udp", "newobj", [25, 90, 115, 22], text="udpreceive 7482", numinlets=0, numoutlets=1, outlettype=[""]),
    box("activity", "button", [155, 89, 24, 24], numinlets=1, numoutlets=1, outlettype=["bang"]),
    box("activity_label", "comment", [185, 91, 130, 20], text="OSC packet activity"),
    box("root", "newobj", [325, 90, 190, 22], text="OSC-route /qmw/instrument", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("families", "newobj", [530, 90, 485, 22], text="OSC-route /spin /epr /exchange /field /relativistic /dirac /control", numinlets=1, numoutlets=8, outlettype=["", "", "", "", "", "", "", ""]),
    box("control_route", "newobj", [825, 90, 135, 22], text="OSC-route /selected", numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("selected_prepend", "newobj", [970, 90, 90, 22], text="prepend set", numinlets=1, numoutlets=1, outlettype=[""]),
    box("unmatched", "newobj", [1070, 90, 190, 22], text="print qmw_native_unmatched", numinlets=1, numoutlets=0),

    box("spin_header", "comment", [25, 145, 300, 22], text="SPIN-1/2 PRECESSION", fontsize=14),
    box("spin_route", "newobj", [25, 175, 240, 22], text="OSC-route /frame /state_real /state_imag", numinlets=1, numoutlets=4, outlettype=["", "", "", ""]),
    box("spin_trigger", "newobj", [25, 210, 45, 22], text="t l b", numinlets=1, numoutlets=2, outlettype=["list", "bang"]),
    box("spin_flash", "button", [78, 209, 24, 24], numinlets=1, numoutlets=1, outlettype=["bang"]),
    box("spin_unpack", "newobj", [25, 248, 420, 22], text="unpack i f f f f f f f f f f f f f f f f", numinlets=1, numoutlets=17, outlettype=["int"] + ["float"] * 16),
    box("spin_omega_label", "comment", [25, 282, 160, 20], text="Larmor angular frequency"),
    box("spin_omega", "flonum", [190, 280, 85, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("spin_bloch_label", "comment", [25, 318, 110, 20], text="Bloch vector"),
    box("spin_bloch_pack", "newobj", [140, 316, 82, 22], text="pak f f f", numinlets=3, numoutlets=1, outlettype=[""]),
    box("spin_bloch", "multislider", [235, 306, 260, 48], size=3, setminmax=[-1.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("spin_prob_label", "comment", [25, 370, 110, 20], text="Z probabilities"),
    box("spin_prob_pack", "newobj", [140, 368, 60, 22], text="pak f f", numinlets=2, numoutlets=1, outlettype=[""]),
    box("spin_prob", "multislider", [215, 360, 280, 48], size=2, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("spin_energy_label", "comment", [25, 418, 65, 20], text="energy"),
    box("spin_energy", "flonum", [92, 416, 75, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("spin_phase_label", "comment", [178, 418, 92, 20], text="relative phase"),
    box("spin_phase", "flonum", [275, 416, 85, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("spin_real_label", "comment", [25, 447, 78, 20], text="spinor Re"),
    box("spin_real", "multislider", [105, 442, 170, 34], size=2, setminmax=[-1.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("spin_imag_label", "comment", [285, 447, 78, 20], text="spinor Im"),
    box("spin_imag", "multislider", [365, 442, 130, 34], size=2, setminmax=[-1.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),

    box("epr_header", "comment", [540, 145, 300, 22], text="EPR / BELL PAIR", fontsize=14),
    box("epr_route", "newobj", [540, 175, 300, 22], text="OSC-route /frame /correlation_tensor /state_real /state_imag", numinlets=1, numoutlets=5, outlettype=["", "", "", "", ""]),
    box("epr_trigger", "newobj", [540, 210, 45, 22], text="t l b", numinlets=1, numoutlets=2, outlettype=["list", "bang"]),
    box("epr_flash", "button", [593, 209, 24, 24], numinlets=1, numoutlets=1, outlettype=["bang"]),
    box("epr_unpack", "newobj", [540, 248, 420, 22], text="unpack i f f f f f f f f f f f f f f f f", numinlets=1, numoutlets=17, outlettype=["int"] + ["float"] * 16),
    box("conc_label", "comment", [540, 282, 85, 20], text="concurrence"),
    box("concurrence", "flonum", [630, 280, 75, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("chsh_label", "comment", [720, 282, 75, 20], text="CHSH max"),
    box("chsh", "flonum", [800, 280, 75, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("epr_a_label", "comment", [540, 318, 170, 20], text="A | B measured +X"),
    box("epr_a_pack", "newobj", [640, 316, 82, 22], text="pak f f f", numinlets=3, numoutlets=1, outlettype=[""]),
    box("epr_a", "multislider", [730, 307, 230, 42], size=3, setminmax=[-1.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("epr_b_label", "comment", [540, 365, 170, 20], text="B | A measured +X"),
    box("epr_b_pack", "newobj", [640, 363, 82, 22], text="pak f f f", numinlets=3, numoutlets=1, outlettype=[""]),
    box("epr_b", "multislider", [730, 354, 230, 42], size=3, setminmax=[-1.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("epr_corr_label", "comment", [540, 402, 125, 20], text="correlation tensor"),
    box("epr_corr", "multislider", [670, 398, 290, 42], size=9, setminmax=[-1.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("epr_real_label", "comment", [540, 452, 68, 20], text="state Re"),
    box("epr_real", "multislider", [610, 446, 155, 36], size=4, setminmax=[-1.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("epr_imag_label", "comment", [775, 452, 68, 20], text="state Im"),
    box("epr_imag", "multislider", [845, 446, 115, 36], size=4, setminmax=[-1.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),

    box("exchange_header", "comment", [25, 505, 390, 22], text="IDENTICAL PARTICLES — BOSON / FERMION", fontsize=14),
    box("exchange_route", "newobj", [25, 535, 355, 22], text="OSC-route /frame /marginal_a /marginal_b /pair /end", numinlets=1, numoutlets=6, outlettype=["", "", "", "", "", ""]),
    box("exchange_trigger", "newobj", [25, 570, 45, 22], text="t l b", numinlets=1, numoutlets=2, outlettype=["list", "bang"]),
    box("exchange_flash", "button", [78, 569, 24, 24], numinlets=1, numoutlets=1, outlettype=["bang"]),
    box("exchange_unpack", "newobj", [25, 608, 250, 22], text="unpack i f f i f f f i", numinlets=1, numoutlets=8, outlettype=["int", "float", "float", "int", "float", "float", "float", "int"]),
    box("symmetry_label", "comment", [25, 642, 100, 20], text="symmetry ±1"),
    box("symmetry", "number", [130, 640, 60, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("swap_label", "comment", [205, 642, 90, 20], text="swap <P12>"),
    box("swap", "flonum", [300, 640, 70, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("coinc_label", "comment", [385, 642, 92, 20], text="coincidence"),
    box("coincidence", "flonum", [480, 640, 85, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("purity_label", "comment", [580, 642, 105, 20], text="one-body purity"),
    box("purity", "flonum", [690, 640, 85, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("pair_status", "message", [25, 680, 620, 22], text="waiting for joint-coordinate pair samples...", numinlets=2, numoutlets=1, outlettype=[""]),
    box("pair_prepend", "newobj", [395, 535, 105, 22], text="prepend set", numinlets=1, numoutlets=1, outlettype=[""]),
    box("note", "comment", [25, 730, 930, 44], text="Default +X spin in a Z field: Bloch X/Y and relative phase move; Z probabilities remain exactly 0.5. Use --magnetic-field 0 1 0 to rotate population through Z."),

    box("field_header", "comment", [25, 785, 500, 22], text="CONTINUOUS EXTERNAL-FIELD WAVEFUNCTION", fontsize=14),
    box("field_route", "newobj", [25, 815, 190, 22], text="OSC-route /name /frame", numinlets=1, numoutlets=3, outlettype=["", "", ""]),
    box("field_name_prepend", "newobj", [225, 815, 90, 22], text="prepend set", numinlets=1, numoutlets=1, outlettype=[""]),
    box("field_name", "message", [325, 815, 300, 22], text="inactive — select a spatial field source", numinlets=2, numoutlets=1, outlettype=[""]),
    box("field_unpack", "newobj", [25, 850, 535, 22], text="unpack i f f i f f f f f f f f f f f f f f f", numinlets=1, numoutlets=19, outlettype=["int", "float", "float", "int"] + ["float"] * 15),
    box("field_desc_label", "comment", [25, 883, 160, 20], text="E phase P structure C J"),
    box("field_desc_pack", "newobj", [190, 881, 145, 22], text="pak f f f f f f", numinlets=6, numoutlets=1, outlettype=[""]),
    box("field_desc", "multislider", [345, 875, 285, 42], size=6, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("field_pos_label", "comment", [25, 930, 75, 20], text="position"),
    box("field_pos_pack", "newobj", [105, 928, 82, 22], text="pak f f f", numinlets=3, numoutlets=1, outlettype=[""]),
    box("field_pos", "multislider", [195, 921, 190, 42], size=3, setminmax=[-10.0, 10.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("field_spread_label", "comment", [405, 930, 65, 20], text="spread"),
    box("field_spread_pack", "newobj", [475, 928, 82, 22], text="pak f f f", numinlets=3, numoutlets=1, outlettype=[""]),
    box("field_spread", "multislider", [565, 921, 190, 42], size=3, setminmax=[0.0, 10.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("field_obs_label", "comment", [25, 977, 340, 20], text="field/Zeff/radius, frequency/repulsion/g, scale/E/bound count"),
    box("field_obs_pack", "newobj", [290, 975, 82, 22], text="pak f f f", numinlets=3, numoutlets=1, outlettype=[""]),
    box("field_obs", "multislider", [380, 968, 375, 42], size=3, setminmax=[-2.0, 2.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("field_note", "comment", [775, 880, 430, 70], text="Spatial cloud/grains are also sent to the established cloud patch on UDP 7480. These grains sample continuous unitary evolution; they are renderer events, not physical collapses."),

    box("rel_header", "comment", [25, 1025, 500, 22], text="DIRAC HYDROGEN FINE STRUCTURE — LEVEL AMPLITUDES", fontsize=14),
    box("rel_route", "newobj", [25, 1055, 325, 22], text="OSC-route /frame /level /state_real /state_imag", numinlets=1, numoutlets=5, outlettype=["", "", "", "", ""]),
    box("rel_unpack", "newobj", [25, 1088, 245, 22], text="unpack i f f f f f f i", numinlets=1, numoutlets=8, outlettype=["int", "float", "float", "float", "float", "float", "float", "int"]),
    box("rel_energy_label", "comment", [285, 1090, 85, 20], text="binding <E>"),
    box("rel_energy", "flonum", [375, 1088, 95, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("rel_split_label", "comment", [485, 1090, 105, 20], text="fine splitting"),
    box("rel_split", "flonum", [595, 1088, 110, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("rel_scale_label", "comment", [720, 1090, 80, 20], text="time scale"),
    box("rel_scale", "flonum", [805, 1088, 100, 22], numinlets=1, numoutlets=2, outlettype=["", "bang"]),
    box("rel_level_prepend", "newobj", [365, 1055, 90, 22], text="prepend set", numinlets=1, numoutlets=1, outlettype=[""]),
    box("rel_level", "message", [465, 1055, 580, 22], text="inactive — select dirac_hydrogen_fine_structure", numinlets=2, numoutlets=1, outlettype=[""]),
    box("rel_real_label", "comment", [25, 1124, 60, 20], text="state Re"),
    box("rel_real", "multislider", [90, 1118, 210, 38], size=2, setminmax=[-1.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("rel_imag_label", "comment", [315, 1124, 60, 20], text="state Im"),
    box("rel_imag", "multislider", [380, 1118, 210, 38], size=2, setminmax=[-1.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),

    box("dirac_header", "comment", [25, 1175, 500, 22], text="DIRAC STEP / KLEIN SCATTERING — TWO-COMPONENT FIELD", fontsize=14),
    box("dirac_route", "newobj", [25, 1205, 205, 22], text="OSC-route /frame /sample /end", numinlets=1, numoutlets=4, outlettype=["", "", "", ""]),
    box("dirac_unpack", "newobj", [25, 1238, 285, 22], text="unpack i f f f f f f f i", numinlets=1, numoutlets=9, outlettype=["int", "float", "float", "float", "float", "float", "float", "float", "int"]),
    box("dirac_lr_label", "comment", [325, 1240, 115, 20], text="left / right mass"),
    box("dirac_lr_pack", "newobj", [445, 1238, 60, 22], text="pak f f", numinlets=2, numoutlets=1, outlettype=[""]),
    box("dirac_lr", "multislider", [515, 1232, 220, 38], size=2, setminmax=[0.0, 1.0], numinlets=1, numoutlets=2, outlettype=["", ""]),
    box("dirac_param_label", "comment", [25, 1278, 190, 20], text="energy, step, incoming E, zone"),
    box("dirac_param_pack", "newobj", [220, 1276, 105, 22], text="pak f f f i", numinlets=4, numoutlets=1, outlettype=[""]),
    box("dirac_param", "message", [335, 1276, 400, 22], text="inactive — select dirac_step_klein", numinlets=2, numoutlets=1, outlettype=[""]),
    box("dirac_sample_prepend", "newobj", [245, 1205, 90, 22], text="prepend set", numinlets=1, numoutlets=1, outlettype=[""]),
    box("dirac_sample", "message", [345, 1205, 690, 22], text="inactive — select dirac_step_klein", numinlets=2, numoutlets=1, outlettype=[""]),
]

lines = [
    line("source_menu", 1, "control_format"), line("control_format", 0, "control_send"),
    line("udp", 0, "activity"), line("udp", 0, "root"),
    line("root", 0, "families"), line("root", 1, "unmatched"),
    line("families", 0, "spin_route"), line("families", 1, "epr_route"), line("families", 2, "exchange_route"), line("families", 3, "field_route"), line("families", 4, "rel_route"), line("families", 5, "dirac_route"), line("families", 6, "control_route"), line("families", 7, "unmatched"),
    line("control_route", 0, "selected_prepend"), line("selected_prepend", 0, "selected"), line("control_route", 1, "unmatched"),
    line("spin_route", 0, "spin_trigger"), line("spin_trigger", 0, "spin_unpack"), line("spin_trigger", 1, "spin_flash"),
    line("spin_unpack", 3, "spin_omega"),
    line("spin_unpack", 12, "spin_bloch_pack", 0), line("spin_unpack", 13, "spin_bloch_pack", 1), line("spin_unpack", 14, "spin_bloch_pack", 2), line("spin_bloch_pack", 0, "spin_bloch"),
    line("spin_unpack", 15, "spin_prob_pack", 0), line("spin_unpack", 16, "spin_prob_pack", 1), line("spin_prob_pack", 0, "spin_prob"),
    line("spin_unpack", 4, "spin_energy"), line("spin_unpack", 5, "spin_phase"),
    line("spin_route", 1, "spin_real"), line("spin_route", 2, "spin_imag"),
    line("epr_route", 0, "epr_trigger"), line("epr_trigger", 0, "epr_unpack"), line("epr_trigger", 1, "epr_flash"),
    line("epr_unpack", 3, "concurrence"), line("epr_unpack", 4, "chsh"),
    line("epr_unpack", 11, "epr_a_pack", 0), line("epr_unpack", 12, "epr_a_pack", 1), line("epr_unpack", 13, "epr_a_pack", 2), line("epr_a_pack", 0, "epr_a"),
    line("epr_unpack", 14, "epr_b_pack", 0), line("epr_unpack", 15, "epr_b_pack", 1), line("epr_unpack", 16, "epr_b_pack", 2), line("epr_b_pack", 0, "epr_b"),
    line("epr_route", 1, "epr_corr"), line("epr_route", 2, "epr_real"), line("epr_route", 3, "epr_imag"),
    line("exchange_route", 0, "exchange_trigger"), line("exchange_trigger", 0, "exchange_unpack"), line("exchange_trigger", 1, "exchange_flash"),
    line("exchange_unpack", 3, "symmetry"), line("exchange_unpack", 4, "swap"), line("exchange_unpack", 5, "coincidence"), line("exchange_unpack", 6, "purity"),
    line("exchange_route", 3, "pair_prepend"), line("pair_prepend", 0, "pair_status", 1),
    line("field_route", 0, "field_name_prepend"), line("field_name_prepend", 0, "field_name"), line("field_route", 1, "field_unpack"), line("field_route", 2, "unmatched"),
    line("field_unpack", 4, "field_desc_pack", 0), line("field_unpack", 5, "field_desc_pack", 1), line("field_unpack", 6, "field_desc_pack", 2), line("field_unpack", 7, "field_desc_pack", 3), line("field_unpack", 8, "field_desc_pack", 4), line("field_unpack", 9, "field_desc_pack", 5), line("field_desc_pack", 0, "field_desc"),
    line("field_unpack", 10, "field_pos_pack", 0), line("field_unpack", 11, "field_pos_pack", 1), line("field_unpack", 12, "field_pos_pack", 2), line("field_pos_pack", 0, "field_pos"),
    line("field_unpack", 13, "field_spread_pack", 0), line("field_unpack", 14, "field_spread_pack", 1), line("field_unpack", 15, "field_spread_pack", 2), line("field_spread_pack", 0, "field_spread"),
    line("field_unpack", 16, "field_obs_pack", 0), line("field_unpack", 17, "field_obs_pack", 1), line("field_unpack", 18, "field_obs_pack", 2), line("field_obs_pack", 0, "field_obs"),
    line("rel_route", 0, "rel_unpack"), line("rel_route", 1, "rel_level_prepend"), line("rel_level_prepend", 0, "rel_level"), line("rel_route", 2, "rel_real"), line("rel_route", 3, "rel_imag"), line("rel_route", 4, "unmatched"),
    line("rel_unpack", 3, "rel_energy"), line("rel_unpack", 4, "rel_split"), line("rel_unpack", 6, "rel_scale"),
    line("dirac_route", 0, "dirac_unpack"), line("dirac_route", 1, "dirac_sample_prepend"), line("dirac_sample_prepend", 0, "dirac_sample"), line("dirac_route", 3, "unmatched"),
    line("dirac_unpack", 4, "dirac_lr_pack", 0), line("dirac_unpack", 5, "dirac_lr_pack", 1), line("dirac_lr_pack", 0, "dirac_lr"),
    line("dirac_unpack", 3, "dirac_param_pack", 0), line("dirac_unpack", 6, "dirac_param_pack", 1), line("dirac_unpack", 7, "dirac_param_pack", 2), line("dirac_unpack", 8, "dirac_param_pack", 3), line("dirac_param_pack", 0, "dirac_param"),
]

patcher = {
    "patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 5, "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [70, 35, 1280, 1330],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "o.pack.mxo", "type": "iLaX"},
        ],
        "autosave": 0,
    }
}

(ROOT / "QMW_Native_Quantum_Instruments_v1.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n", encoding="utf-8"
)
(ROOT / "QMW_Native_Quantum_Instruments_v1_1.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n", encoding="utf-8"
)
(ROOT / "QMW_Native_Quantum_Instruments_v1_2.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n", encoding="utf-8"
)
(ROOT / "QMW_Native_Quantum_Instruments_v1_3.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n", encoding="utf-8"
)
(ROOT / "QMW_Native_Quantum_Instruments_v1_4.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n", encoding="utf-8"
)
(ROOT / "QMW_Native_Quantum_Instruments_v1_5.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n", encoding="utf-8"
)
(ROOT / "QMW_Native_Quantum_Instruments_v1_6.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n", encoding="utf-8"
)
(ROOT / "QMW_Native_Quantum_Instruments_v1_7.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n", encoding="utf-8"
)
