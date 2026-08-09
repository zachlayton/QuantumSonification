from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


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


boxes = [
    box(
        "title",
        "comment",
        [25, 16, 930, 25],
        text="QMW ZX Processing Companion — exact OSC receiver + audible voice",
        fontsize=16,
    ),
    box(
        "help",
        "comment",
        [25, 47, 1020, 38],
        text=(
            "Processing sends normalized performance controls and diagram edits "
            "to UDP 7496. Click the speaker at the bottom after values appear."
        ),
    ),
    box(
        "udp",
        "newobj",
        [25, 105, 118, 22],
        text="udpreceive 7496",
        numinlets=0,
        numoutlets=1,
        outlettype=[""],
    ),
    box(
        "routes",
        "newobj",
        [165, 105, 865, 22],
        text=(
            "OSC-route /qmw/zx/fader /qmw/zx/node/position "
            "/qmw/zx/node/phase /qmw/zx/node/add /qmw/zx/node/delete "
            "/qmw/zx/edge/add /qmw/zx/rewrite/fuse "
            "/qmw/zx/graph/scalar /qmw/zx/rewrite/apply"
        ),
        numinlets=1,
        numoutlets=10,
        outlettype=[""] * 10,
    ),
    box(
        "fader_route",
        "newobj",
        [25, 150, 150, 22],
        text="route 1 2 3 4 5 6",
        numinlets=1,
        numoutlets=7,
        outlettype=[""] * 7,
    ),
]

lines = [
    line("udp", 0, "routes"),
    line("routes", 0, "fader_route"),
]

labels = [
    "phase",
    "Z expectation",
    "entropy",
    "coherence",
    "gradient",
    "probability",
]

for index, label in enumerate(labels, start=1):
    x = 25 + ((index - 1) % 3) * 220
    y = 195 + ((index - 1) // 3) * 70
    value_id = f"value_{index}"
    boxes.extend(
        [
            box(
                f"label_{index}",
                "comment",
                [x, y, 130, 20],
                text=f"{index}  {label}",
            ),
            box(
                value_id,
                "flonum",
                [x + 132, y - 2, 72, 22],
                minimum=0.0,
                maximum=1.0,
                numinlets=1,
                numoutlets=2,
                outlettype=["", "bang"],
            ),
        ]
    )
    lines.append(line("fader_route", index - 1, value_id))

event_specs = [
    ("position", 1, "/node/position  id x y"),
    ("phase_event", 2, "/node/phase  id kind radians"),
    ("add_event", 3, "/node/add  id kind x y phase"),
    ("delete_event", 4, "/node/delete  id"),
    ("edge_event", 5, "/edge/add  source target plain"),
    ("fusion_event", 6, "/rewrite/fuse  keep removed kind phase"),
    ("scalar_event", 7, "/graph/scalar  real imag"),
    ("rule_event", 8, "/rewrite/apply  rule error scalar-real scalar-imag"),
]

for row, (identifier, outlet, label) in enumerate(event_specs):
    y = 355 + row * 34
    boxes.extend(
        [
            box(
                f"{identifier}_label",
                "comment",
                [25, y + 2, 245, 20],
                text=label,
            ),
            box(
                identifier,
                "message",
                [280, y, 600, 22],
                text="waiting...",
                numinlets=2,
                numoutlets=1,
                outlettype=[""],
            ),
            box(
                f"{identifier}_print",
                "newobj",
                [900, y, 155, 22],
                text=f"print ZX_{identifier.upper()}",
                numinlets=1,
                numoutlets=0,
            ),
        ]
    )
    lines.extend(
        [
            line("routes", outlet, identifier, 1),
            line("routes", outlet, f"{identifier}_print"),
        ]
    )

boxes.extend(
    [
        box(
            "audio_label",
            "comment",
            [25, 625, 680, 20],
            text=(
                "Audible monitor: phase → carrier pitch · expectation → "
                "upper partial · coherence → partial level · probability → gain"
            ),
        ),
        box(
            "base_expr",
            "newobj",
            [25, 655, 185, 22],
            text="expr 110.*pow(2.,$f1*2.)",
            numinlets=1,
            numoutlets=1,
            outlettype=["float"],
        ),
        box(
            "base_pack",
            "newobj",
            [225, 655, 70, 22],
            text="pack f 40",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "base_line",
            "newobj",
            [310, 655, 42, 22],
            text="line~",
            numinlets=2,
            numoutlets=2,
            outlettype=["signal", "bang"],
        ),
        box(
            "carrier",
            "newobj",
            [370, 655, 55, 22],
            text="cycle~",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "carrier_gain",
            "newobj",
            [440, 655, 48, 22],
            text="*~ 0.65",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "upper_expr",
            "newobj",
            [25, 692, 175, 22],
            text="expr 165.+($f1*330.)",
            numinlets=1,
            numoutlets=1,
            outlettype=["float"],
        ),
        box(
            "upper_pack",
            "newobj",
            [215, 692, 70, 22],
            text="pack f 40",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "upper_line",
            "newobj",
            [300, 692, 42, 22],
            text="line~",
            numinlets=2,
            numoutlets=2,
            outlettype=["signal", "bang"],
        ),
        box(
            "upper",
            "newobj",
            [360, 692, 55, 22],
            text="cycle~",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "coherence_scale",
            "newobj",
            [505, 692, 52, 22],
            text="* 0.14",
            numinlets=2,
            numoutlets=1,
            outlettype=["float"],
        ),
        box(
            "coherence_pack",
            "newobj",
            [570, 692, 70, 22],
            text="pack f 60",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "coherence_line",
            "newobj",
            [655, 692, 42, 22],
            text="line~",
            numinlets=2,
            numoutlets=2,
            outlettype=["signal", "bang"],
        ),
        box(
            "upper_gain",
            "newobj",
            [430, 692, 38, 22],
            text="*~",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "sum",
            "newobj",
            [520, 655, 38, 22],
            text="+~",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "master_scale",
            "newobj",
            [720, 692, 130, 22],
            text="expr 0.015+($f1*0.09)",
            numinlets=1,
            numoutlets=1,
            outlettype=["float"],
        ),
        box(
            "master_pack",
            "newobj",
            [865, 692, 70, 22],
            text="pack f 80",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "master_line",
            "newobj",
            [950, 692, 42, 22],
            text="line~",
            numinlets=2,
            numoutlets=2,
            outlettype=["signal", "bang"],
        ),
        box(
            "master",
            "newobj",
            [590, 655, 38, 22],
            text="*~",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "fusion_trigger",
            "newobj",
            [25, 742, 48, 22],
            text="t b l",
            numinlets=1,
            numoutlets=2,
            outlettype=["bang", ""],
        ),
        box(
            "fusion_unpack",
            "newobj",
            [90, 742, 105, 22],
            text="unpack i i s f",
            numinlets=1,
            numoutlets=4,
            outlettype=["int", "int", "", "float"],
        ),
        box(
            "rewrite_freq",
            "newobj",
            [210, 742, 235, 22],
            text="expr 220.*pow(2.,$f1/6.283185*2.)",
            numinlets=1,
            numoutlets=1,
            outlettype=["float"],
        ),
        box(
            "rewrite_pack",
            "newobj",
            [460, 742, 70, 22],
            text="pack f 20",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "rewrite_line",
            "newobj",
            [545, 742, 42, 22],
            text="line~",
            numinlets=2,
            numoutlets=2,
            outlettype=["signal", "bang"],
        ),
        box(
            "rewrite_osc",
            "newobj",
            [605, 742, 55, 22],
            text="cycle~",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "rewrite_envelope_message",
            "message",
            [90, 780, 105, 22],
            text="0.2, 0. 700",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "rewrite_envelope",
            "newobj",
            [210, 780, 42, 22],
            text="line~",
            numinlets=2,
            numoutlets=2,
            outlettype=["signal", "bang"],
        ),
        box(
            "rewrite_gain",
            "newobj",
            [675, 742, 38, 22],
            text="*~",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "post_rewrite_sum",
            "newobj",
            [735, 655, 38, 22],
            text="+~",
            numinlets=2,
            numoutlets=1,
            outlettype=["signal"],
        ),
        box(
            "rewrite_label",
            "comment",
            [270, 780, 560, 22],
            text="Every verified fusion or named rule produces a confirmation chime.",
        ),
        box(
            "named_rewrite_trigger",
            "newobj",
            [835, 742, 42, 22],
            text="t b b",
            numinlets=1,
            numoutlets=2,
            outlettype=["bang", "bang"],
        ),
        box(
            "named_rewrite_freq",
            "message",
            [835, 780, 42, 22],
            text="440.",
            numinlets=2,
            numoutlets=1,
            outlettype=[""],
        ),
        box(
            "audio_prompt",
            "comment",
            [655, 842, 225, 22],
            text="Click speaker to start/stop Max audio →",
        ),
        box(
            "dac",
            "newobj",
            [895, 833, 65, 32],
            text="ezdac~",
            numinlets=2,
            numoutlets=0,
        ),
    ]
)

lines.extend(
    [
        line("value_1", 0, "base_expr"),
        line("base_expr", 0, "base_pack"),
        line("base_pack", 0, "base_line"),
        line("base_line", 0, "carrier"),
        line("carrier", 0, "carrier_gain"),
        line("value_2", 0, "upper_expr"),
        line("upper_expr", 0, "upper_pack"),
        line("upper_pack", 0, "upper_line"),
        line("upper_line", 0, "upper"),
        line("value_4", 0, "coherence_scale"),
        line("coherence_scale", 0, "coherence_pack"),
        line("coherence_pack", 0, "coherence_line"),
        line("upper", 0, "upper_gain"),
        line("coherence_line", 0, "upper_gain", 1),
        line("carrier_gain", 0, "sum"),
        line("upper_gain", 0, "sum", 1),
        line("value_6", 0, "master_scale"),
        line("master_scale", 0, "master_pack"),
        line("master_pack", 0, "master_line"),
        line("routes", 6, "fusion_trigger"),
        line("routes", 8, "named_rewrite_trigger"),
        line("fusion_trigger", 1, "fusion_unpack"),
        line("fusion_unpack", 3, "rewrite_freq"),
        line("rewrite_freq", 0, "rewrite_pack"),
        line("rewrite_pack", 0, "rewrite_line"),
        line("rewrite_line", 0, "rewrite_osc"),
        line("fusion_trigger", 0, "rewrite_envelope_message"),
        line("named_rewrite_trigger", 1, "named_rewrite_freq"),
        line("named_rewrite_freq", 0, "rewrite_pack"),
        line("named_rewrite_trigger", 0, "rewrite_envelope_message"),
        line("rewrite_envelope_message", 0, "rewrite_envelope"),
        line("rewrite_osc", 0, "rewrite_gain"),
        line("rewrite_envelope", 0, "rewrite_gain", 1),
        line("sum", 0, "post_rewrite_sum"),
        line("rewrite_gain", 0, "post_rewrite_sum", 1),
        line("post_rewrite_sum", 0, "master"),
        line("master_line", 0, "master", 1),
        line("master", 0, "dac"),
        line("master", 0, "dac", 1),
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
        "rect": [80, 35, 1100, 915],
        "gridsize": [15, 15],
        "boxes": boxes,
        "lines": lines,
        "dependency_cache": [
            {"name": "OSC-route.mxo", "type": "iLaX"},
        ],
        "autosave": 0,
    }
}

(ROOT / "QMW_ZX_Processing_Companion_v1.maxpat").write_text(
    json.dumps(patcher, indent=2) + "\n",
    encoding="utf-8",
)
