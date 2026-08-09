from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "QMW_ZX_Density_Matrix_Engine_v1.maxpat"


def box(identifier, maxclass, rect, **values):
    data = {
        "id": identifier,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    data.update(values)
    return {"box": data}


def line(source, outlet, destination, inlet=0):
    return {
        "patchline": {
            "source": [source, outlet],
            "destination": [destination, inlet],
        }
    }


paths = [
    ("begin", "/qmw/zx/density/begin"),
    ("meta", "/qmw/zx/density/meta"),
    ("probabilities", "/qmw/zx/density/probabilities"),
    ("row", "/qmw/zx/density/row"),
    ("bloch", "/qmw/zx/density/bloch"),
    ("end", "/qmw/zx/density/end"),
    ("error", "/qmw/zx/density/error"),
    ("commit_sent", "/qmw/zx/density/commit_sent"),
    ("pauli_verified", "/qmw/zx/pauli/verified"),
    ("pauli_score_verified", "/qmw/zx/pauli/score_verified"),
    ("pauli_active", "/qmw/zx/pauli/active"),
    ("pauli_live", "/qmw/zx/pauli/live"),
    ("pauli_error", "/qmw/zx/pauli/error"),
    ("euler_result", "/qmw/zx/euler/result"),
]

boxes = [
    box(
        "title",
        "comment",
        [25, 15, 1040, 28],
        text="QMW ZX Density Matrix Engine — dynamic atomic complex OSC receiver",
        fontsize=17,
    ),
    box(
        "help",
        "comment",
        [25, 45, 1160, 40],
        text=(
            "Listens on UDP 7498 using CNMAT OSC-route (no oscparse). "
            "Complete 2×2 through 256×256 revisions drive five Jitter matrix "
            "buses, metrics, Bloch data, and a folded 16-voice instrument."
        ),
    ),
    box(
        "udp",
        "newobj",
        [25, 95, 120, 22],
        text="udpreceive 7498",
        numinlets=0,
        numoutlets=1,
        outlettype=[""],
    ),
    box(
        "routes",
        "newobj",
        [165, 95, 1055, 22],
        text=(
            "OSC-route "
            + " ".join(address for _name, address in paths)
        ),
        numinlets=1,
        numoutlets=len(paths) + 1,
        outlettype=[""] * (len(paths) + 1),
    ),
]

lines = [line("udp", 0, "routes")]

for index, (path, _address) in enumerate(paths):
    x = 25 + (index % 4) * 286
    y = 140 + (index // 4) * 34
    identifier = f"prepend_{path}"
    boxes.append(
        box(
            identifier,
            "newobj",
            [x, y, 160, 22],
            text=f"prepend {path}",
            numinlets=1,
            numoutlets=1,
            outlettype=[""],
        )
    )
    lines.extend(
        [
            line("routes", index, identifier),
            line(identifier, 0, "engine"),
        ]
    )

boxes.extend(
    [
        box(
            "engine",
            "newobj",
            [25, 220, 310, 22],
            text="js qmw_zx_density_matrix_engine_v1.js",
            numinlets=1,
            numoutlets=12,
            outlettype=[""] * 12,
        ),
        box(
            "revision_label",
            "comment",
            [355, 222, 60, 20],
            text="revision",
        ),
        box(
            "revision",
            "number",
            [418, 220, 78, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "status",
            "message",
            [515, 220, 690, 22],
            text="waiting for a complete density revision...",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "matrix_label",
            "comment",
            [25, 270, 375, 20],
            text="Normalized |ρᵢⱼ| — updates only after every dynamic row arrives",
        ),
        box(
            "matrix_view",
            "jit.pwindow",
            [25, 295, 390, 390],
            numinlets=1,
            numoutlets=2,
            outlettype=["jit_matrix", ""],
        ),
        box(
            "complex_send",
            "newobj",
            [440, 270, 210, 22],
            text="s qmw.zx.rho.complex.matrix",
            numinlets=1,
            numoutlets=0,
        ),
        box(
            "real_send",
            "newobj",
            [440, 300, 190, 22],
            text="s qmw.zx.rho.real.matrix",
            numinlets=1,
            numoutlets=0,
        ),
        box(
            "imag_send",
            "newobj",
            [440, 330, 190, 22],
            text="s qmw.zx.rho.imag.matrix",
            numinlets=1,
            numoutlets=0,
        ),
        box(
            "magnitude_send",
            "newobj",
            [440, 360, 225, 22],
            text="s qmw.zx.rho.magnitude.matrix",
            numinlets=1,
            numoutlets=0,
        ),
        box(
            "phase_send",
            "newobj",
            [440, 390, 195, 22],
            text="s qmw.zx.rho.phase.matrix",
            numinlets=1,
            numoutlets=0,
        ),
        box(
            "euler_panel",
            "panel",
            [430, 410, 245, 330],
            bgcolor=[0.94, 0.97, 0.94, 1.0],
            border=1,
            rounded=8,
            numinlets=1,
            numoutlets=0,
        ),
        box(
            "euler_title",
            "comment",
            [440, 420, 220, 22],
            text="Euler decomposition — radians",
            fontsize=14,
        ),
        box(
            "euler_receive",
            "newobj",
            [440, 446, 210, 22],
            text="r qmw.euler.result",
            numinlets=0,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "euler_unpack",
            "newobj",
            [440, 472, 225, 22],
            text="unpack i s i s f f f f f i f",
            numinlets=1,
            numoutlets=11,
            outlettype=[
                "int",
                "",
                "int",
                "",
                "float",
                "float",
                "float",
                "float",
                "float",
                "int",
                "float",
            ],
        ),
        box(
            "euler_request_label",
            "comment",
            [440, 499, 52, 18],
            text="request",
        ),
        box(
            "euler_request",
            "number",
            [493, 497, 52, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_qubit_label",
            "comment",
            [552, 499, 40, 18],
            text="qubit",
        ),
        box(
            "euler_qubit",
            "number",
            [595, 497, 60, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_source_label",
            "comment",
            [440, 524, 48, 18],
            text="source",
        ),
        box(
            "euler_source",
            "message",
            [490, 522, 85, 22],
            text="—",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "euler_basis_label",
            "comment",
            [582, 524, 35, 18],
            text="basis",
        ),
        box(
            "euler_basis",
            "message",
            [620, 522, 40, 22],
            text="—",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "euler_theta_label",
            "comment",
            [440, 574, 62, 18],
            text="theta θ",
        ),
        box(
            "euler_angle_columns",
            "comment",
            [505, 550, 150, 18],
            text="radians              × π",
        ),
        box(
            "euler_theta",
            "flonum",
            [505, 572, 70, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_theta_pi",
            "flonum",
            [585, 572, 70, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_phi_label",
            "comment",
            [440, 598, 62, 18],
            text="phi φ",
        ),
        box(
            "euler_phi",
            "flonum",
            [505, 596, 70, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_phi_pi",
            "flonum",
            [585, 596, 70, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_lambda_label",
            "comment",
            [440, 622, 62, 18],
            text="lambda λ",
        ),
        box(
            "euler_lambda",
            "flonum",
            [505, 620, 70, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_lambda_pi",
            "flonum",
            [585, 620, 70, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_gamma_label",
            "comment",
            [440, 646, 62, 18],
            text="gamma γ",
        ),
        box(
            "euler_gamma",
            "flonum",
            [505, 644, 70, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_gamma_pi",
            "flonum",
            [585, 644, 70, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_scalar_label",
            "comment",
            [440, 670, 62, 18],
            text="ZX scalar",
        ),
        box(
            "euler_scalar",
            "flonum",
            [505, 668, 70, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_scalar_pi",
            "flonum",
            [585, 668, 70, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_verified_label",
            "comment",
            [440, 698, 54, 18],
            text="verified",
        ),
        box(
            "euler_verified",
            "toggle",
            [495, 696, 22, 22],
            numinlets=1,
            numoutlets=1,
            outlettype=["int"],
        ),
        box(
            "euler_error_label",
            "comment",
            [525, 698, 32, 18],
            text="error",
        ),
        box(
            "euler_error",
            "flonum",
            [558, 696, 97, 22],
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        ),
        box(
            "euler_theta_pi_receive",
            "newobj",
            [440, 718, 200, 22],
            text="r qmw.euler.theta_pi",
            numinlets=0,
            numoutlets=1,
            outlettype=[""],
            hidden=1,
        ),
        box(
            "euler_phi_pi_receive",
            "newobj",
            [440, 718, 200, 22],
            text="r qmw.euler.phi_pi",
            numinlets=0,
            numoutlets=1,
            outlettype=[""],
            hidden=1,
        ),
        box(
            "euler_lambda_pi_receive",
            "newobj",
            [440, 718, 200, 22],
            text="r qmw.euler.lambda_pi",
            numinlets=0,
            numoutlets=1,
            outlettype=[""],
            hidden=1,
        ),
        box(
            "euler_gamma_pi_receive",
            "newobj",
            [440, 718, 200, 22],
            text="r qmw.euler.gamma_pi",
            numinlets=0,
            numoutlets=1,
            outlettype=[""],
            hidden=1,
        ),
        box(
            "euler_scalar_pi_receive",
            "newobj",
            [440, 718, 215, 22],
            text="r qmw.euler.zx_scalar_phase_pi",
            numinlets=0,
            numoutlets=1,
            outlettype=[""],
            hidden=1,
        ),
        box(
            "population_label",
            "comment",
            [690, 270, 275, 20],
            text="basis populations ρᵢᵢ",
        ),
        box(
            "populations",
            "multislider",
            [690, 295, 500, 105],
            size=16,
            setminmax=[0.0, 1.0],
            slidercolor=[0.37, 0.72, 0.48, 1.0],
            numinlets=1,
            numoutlets=2,
            outlettype=["", ""],
        ),
        box(
            "density_dimension_receive",
            "newobj",
            [690, 402, 205, 22],
            text="r qmw.zx.density.dimension",
            numinlets=0,
            numoutlets=1,
            outlettype=[""],
            hidden=1,
        ),
        box(
            "population_size",
            "newobj",
            [900, 402, 95, 22],
            text="prepend size",
            numinlets=1,
            numoutlets=1,
            outlettype=[""],
            hidden=1,
        ),
        box(
            "metrics_label",
            "comment",
            [690, 420, 500, 20],
            text="revision · trace · purity · coherence ℓ₁ · entropy · min λ · weight",
        ),
        box(
            "metrics_unpack",
            "newobj",
            [690, 445, 180, 22],
            text="unpack i f f f f f f",
            numinlets=1,
            numoutlets=7,
            outlettype=["int"] + ["float"] * 6,
        ),
        box(
            "bloch_label",
            "comment",
            [690, 515, 260, 20],
            text="q · Bloch x y z · local purity · entropy",
        ),
        box(
            "bloch_display",
            "message",
            [690, 540, 500, 22],
            text="waiting for local Bloch vectors...",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "voice_label",
            "comment",
            [440, 750, 750, 34],
            text=(
                "Folded 16-voice instrument: arbitrary-dimensional populations "
                "drive amplitude; coherence and phase drive excitation/detuning."
            ),
        ),
        box(
            "freq_apply",
            "newobj",
            [440, 795, 118, 22],
            text="prepend applyvalues",
            numinlets=1,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "frequency_signal",
            "newobj",
            [575, 795, 132, 22],
            text="mc.sig~ 110 @chans 16",
            numinlets=1,
            numoutlets=1,
            outlettype=["multichannelsignal"],
        ),
        box(
            "frequency_smooth",
            "newobj",
            [725, 795, 142, 22],
            text="mc.slide~ 2400 2400",
            numinlets=3,
            numoutlets=1,
            outlettype=["multichannelsignal"],
        ),
        box(
            "oscillators",
            "newobj",
            [885, 795, 128, 22],
            text="mc.cycle~ @chans 16",
            numinlets=2,
            numoutlets=1,
            outlettype=["multichannelsignal"],
        ),
        box(
            "amp_apply",
            "newobj",
            [440, 835, 118, 22],
            text="prepend applyvalues",
            numinlets=1,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "amplitude_signal",
            "newobj",
            [575, 835, 122, 22],
            text="mc.sig~ 0. @chans 16",
            numinlets=1,
            numoutlets=1,
            outlettype=["multichannelsignal"],
        ),
        box(
            "amplitude_smooth",
            "newobj",
            [715, 835, 142, 22],
            text="mc.slide~ 4800 4800",
            numinlets=3,
            numoutlets=1,
            outlettype=["multichannelsignal"],
        ),
        box(
            "voice_gain",
            "newobj",
            [885, 835, 58, 22],
            text="mc.*~",
            numinlets=2,
            numoutlets=1,
            outlettype=["multichannelsignal"],
        ),
        box(
            "mixdown",
            "newobj",
            [960, 835, 185, 22],
            text="mc.mixdown~ 2 @autogain 1",
            numinlets=2,
            numoutlets=1,
            outlettype=["multichannelsignal"],
        ),
        box(
            "unpack_audio",
            "newobj",
            [960, 875, 90, 22],
            text="mc.unpack~ 2",
            numinlets=1,
            numoutlets=2,
            outlettype=["signal", "signal"],
        ),
        box(
            "left_gain",
            "newobj",
            [930, 915, 55, 22],
            text="*~ 0.55",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "right_gain",
            "newobj",
            [1015, 915, 55, 22],
            text="*~ 0.55",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "audio_prompt",
            "comment",
            [730, 973, 330, 22],
            text="Click speaker after a matrix revision arrives →",
        ),
        box(
            "dac",
            "newobj",
            [1080, 960, 68, 36],
            text="ezdac~",
            numinlets=2,
            numoutlets=0,
        ),
    ]
)

for index, label in enumerate(
    ["rev", "trace", "purity", "coherence", "entropy", "min λ", "weight"]
):
    x = 690 + index * 72
    boxes.extend(
        [
            box(
                f"metric_label_{index}",
                "comment",
                [x, 474, 67, 18],
                text=label,
            ),
            box(
                f"metric_{index}",
                "number" if index == 0 else "flonum",
                [x, 492, 67, 22],
                numinlets=1,
                numoutlets=2,
                outlettype=["", "bang"],
            ),
        ]
    )
    lines.append(line("metrics_unpack", index, f"metric_{index}"))

lines.extend(
    [
        line("euler_receive", 0, "euler_unpack"),
        line("euler_unpack", 0, "euler_request"),
        line("euler_unpack", 1, "euler_source", 1),
        line("euler_unpack", 2, "euler_qubit"),
        line("euler_unpack", 3, "euler_basis", 1),
        line("euler_unpack", 4, "euler_theta"),
        line("euler_unpack", 5, "euler_phi"),
        line("euler_unpack", 6, "euler_lambda"),
        line("euler_unpack", 7, "euler_gamma"),
        line("euler_unpack", 8, "euler_scalar"),
        line("euler_unpack", 9, "euler_verified"),
        line("euler_unpack", 10, "euler_error"),
        line("euler_theta_pi_receive", 0, "euler_theta_pi"),
        line("euler_phi_pi_receive", 0, "euler_phi_pi"),
        line("euler_lambda_pi_receive", 0, "euler_lambda_pi"),
        line("euler_gamma_pi_receive", 0, "euler_gamma_pi"),
        line("euler_scalar_pi_receive", 0, "euler_scalar_pi"),
        line("density_dimension_receive", 0, "population_size"),
        line("population_size", 0, "populations"),
        line("engine", 0, "complex_send"),
        line("engine", 1, "real_send"),
        line("engine", 2, "imag_send"),
        line("engine", 3, "magnitude_send"),
        line("engine", 3, "matrix_view"),
        line("engine", 4, "phase_send"),
        line("engine", 5, "populations"),
        line("engine", 6, "metrics_unpack"),
        line("engine", 7, "bloch_display", 1),
        line("engine", 8, "freq_apply"),
        line("freq_apply", 0, "frequency_signal"),
        line("frequency_signal", 0, "frequency_smooth"),
        line("frequency_smooth", 0, "oscillators"),
        line("engine", 9, "amp_apply"),
        line("amp_apply", 0, "amplitude_signal"),
        line("amplitude_signal", 0, "amplitude_smooth"),
        line("oscillators", 0, "voice_gain"),
        line("amplitude_smooth", 0, "voice_gain", 1),
        line("voice_gain", 0, "mixdown"),
        line("mixdown", 0, "unpack_audio"),
        line("unpack_audio", 0, "left_gain"),
        line("unpack_audio", 1, "right_gain"),
        line("left_gain", 0, "dac"),
        line("right_gain", 0, "dac", 1),
        line("engine", 10, "revision"),
        line("engine", 11, "status", 1),
    ]
)

patcher = {
    "patcher": {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 0,
            "revision": 5,
            "architecture": "x64",
            "modernui": 1,
        },
        "classnamespace": "box",
        "rect": [60, 35, 1245, 1030],
        "gridsize": [15, 15],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
            {"name": "qmw_zx_density_matrix_engine_v1.js", "type": "TEXT"},
        ],
        "autosave": 0,
    }
}

texts = {
    item["box"].get("text", "")
    for item in boxes
    if isinstance(item.get("box"), dict)
}
assert "udpreceive 7498" in texts
assert "js qmw_zx_density_matrix_engine_v1.js" in texts
assert "mc.mixdown~ 2 @autogain 1" in texts
assert any(text.startswith("OSC-route /qmw/zx/density/begin") for text in texts)
assert any("/qmw/zx/pauli/live" in text for text in texts)
assert "r qmw.euler.result" in texts
assert "r qmw.euler.theta_pi" in texts
assert "r qmw.euler.zx_scalar_phase_pi" in texts

OUTPUT.write_text(json.dumps(patcher, indent=2) + "\n", encoding="utf-8")
print(OUTPUT)
