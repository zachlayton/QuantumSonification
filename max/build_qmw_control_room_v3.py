#!/usr/bin/env python3
"""Build Control Room v3 from the preserved working v2 files.

The standalone v3 module files remain the editable sources, but the generated
Control Room embeds freshly built copies of the resonator and surface modules.
This mirrors Max's reliable manual "Embed in Patcher" state and avoids the
first-open dependency race that otherwise leaves both DSP graphs silent.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


MAX_ROOT = Path(__file__).resolve().parent
MODULE_ROOT = MAX_ROOT / "control_room_modules"
CONTROL_V2 = MAX_ROOT / "QMW_Control_Room_v2.maxpat"
RACK_V2 = MODULE_ROOT / "QMW_Sonification_Rack_Module_v2.maxpat"
SURFACE_V2 = MODULE_ROOT / "QMW_Realtime_Surface_Reverb_v2.maxpat"
CONTROL_V3 = MAX_ROOT / "QMW_Control_Room_v3.maxpat"
RACK_V3 = MAX_ROOT / "QMW_Sonification_Rack_Module_v3.maxpat"
SURFACE_V3 = MAX_ROOT / "QMW_Realtime_Surface_Reverb_v3.maxpat"
SCHEDULER_V2 = "qmw_resonance_grain_scheduler_v2.js"
SCHEDULER_V3 = "qmw_resonance_grain_scheduler_v3.js"

DENSITY_FIELD_ROUTE = (
    "OSC-route /speed /magnitude /phase /harmonics "
    "/entropy /purity /coherence"
)
CONTROL_DENSITY_FIELD_ROUTE = (
    "OSC-route /magnitude /phase /speed /harmonics "
    "/entropy /purity /coherence"
)
SURFACE_DENSITY_FIELD_ROUTE = (
    "OSC-route /magnitude /harmonics /entropy /purity /coherence"
)
LOCAL_PAULI_GROUPS = (
    ("XIII", "IXII", "IIXI", "IIIX"),
    ("YIII", "IYII", "IIYI", "IIIY"),
    ("ZIII", "IZII", "IIZI", "IIIZ"),
)
PAULI_CORRELATIONS = (
    "XXII",
    "YYII",
    "ZZII",
    "IXXI",
    "IYYI",
    "IZZI",
    "IIXX",
    "IIYY",
    "IIZZ",
)
PAULI_STRINGS = tuple(
    name for group in LOCAL_PAULI_GROUPS for name in group
) + PAULI_CORRELATIONS
PAULI_ROUTE_TEXT = "OSC-route " + " ".join(f"/{name}" for name in PAULI_STRINGS)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def next_id(patcher: dict[str, Any]) -> str:
    numeric = [
        int(entry["box"]["id"][4:])
        for entry in patcher.get("boxes", [])
        if entry["box"]["id"].startswith("obj-")
        and entry["box"]["id"][4:].isdigit()
    ]
    return f"obj-{max(numeric, default=0) + 1}"


def find_box(boxes: list[dict[str, Any]], *, text: str) -> dict[str, Any]:
    matches = [box for box in boxes if box.get("text") == text]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one Max box {text!r}; found {len(matches)}")
    return matches[0]


def connect(
    patcher: dict[str, Any],
    source: str,
    outlet: int,
    destination: str,
    inlet: int = 0,
) -> None:
    patcher.setdefault("lines", []).append(
        {
            "patchline": {
                "source": [source, outlet],
                "destination": [destination, inlet],
            }
        }
    )


def add_normalizer(
    patcher: dict[str, Any],
    *,
    divisor: float,
    rect: list[float],
) -> str:
    identifier = next_id(patcher)
    patcher.setdefault("boxes", []).append(
        {
            "box": {
                "id": identifier,
                "maxclass": "newobj",
                "text": f"expr min(1., max(0., $f1 / {divisor:g}.))",
                "patching_rect": rect,
                "numinlets": 1,
                "numoutlets": 1,
                "outlettype": ["float"],
            }
        }
    )
    return identifier


def add_box(
    patcher: dict[str, Any],
    maxclass: str,
    rect: list[float],
    *,
    text: str | None = None,
    presentation: bool = False,
    **properties: Any,
) -> str:
    identifier = next_id(patcher)
    box: dict[str, Any] = {
        "id": identifier,
        "maxclass": maxclass,
        "patching_rect": rect,
    }
    if text is not None:
        box["text"] = text
    if presentation:
        box["presentation"] = 1
        box["presentation_rect"] = list(rect)
    box.update(properties)
    patcher.setdefault("boxes", []).append({"box": box})
    return identifier


def routed_destination(
    patcher: dict[str, Any], source: str, outlet: int
) -> str:
    matches = [
        line["patchline"]["destination"][0]
        for line in patcher.get("lines", [])
        if line["patchline"]["source"] == [source, outlet]
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one destination from {source} outlet {outlet}; found {len(matches)}"
        )
    return matches[0]


def build_rack() -> dict[str, Any]:
    payload = deepcopy(load(RACK_V2))
    patcher = payload["patcher"]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    texts = [box.get("text", "") for box in boxes]
    if patcher.get("openinpresentation") != 1:
        raise RuntimeError("V2 rack presentation layout is not available")
    if sum(box.get("presentation") == 1 for box in boxes) < 25:
        raise RuntimeError("V2 rack presentation objects are missing")

    # The source v2 rack had its density-field outlets shifted by one:
    # magnitude reached speed, phase reached magnitude, and so on. Rebuild
    # only the route-to-prepend fanout and keep its diagnostic displays.
    density_route = find_box(boxes, text=DENSITY_FIELD_ROUTE)["id"]
    prepend_by_name = {
        name: find_box(boxes, text=f"prepend {name}")["id"]
        for name in ("speed", "magnitude", "phase", "harmonics", "entropy", "coherence")
    }
    prepend_ids = set(prepend_by_name.values())
    patcher["lines"] = [
        line
        for line in patcher.get("lines", [])
        if not (
            line["patchline"]["source"][0] == density_route
            and line["patchline"]["destination"][0] in prepend_ids
        )
    ]
    for outlet, name in enumerate(("speed", "magnitude", "phase", "harmonics")):
        connect(patcher, density_route, outlet, prepend_by_name[name])

    # Python publishes entropy in bits (0..4 for four qubits) and raw l1
    # coherence (0..15 for a 16-dimensional state). The dashboard retains
    # those physical values; Gen receives normalized modulation signals.
    entropy_normalizer = add_normalizer(
        patcher, divisor=4.0, rect=[467.0, 143.0, 190.0, 22.0]
    )
    coherence_normalizer = add_normalizer(
        patcher, divisor=15.0, rect=[665.0, 143.0, 195.0, 22.0]
    )
    connect(patcher, density_route, 4, entropy_normalizer)
    connect(patcher, entropy_normalizer, 0, prepend_by_name["entropy"])
    connect(patcher, density_route, 6, coherence_normalizer)
    connect(patcher, coherence_normalizer, 0, prepend_by_name["coherence"])

    purity_prepend = next_id(patcher)
    patcher["boxes"].append(
        {
            "box": {
                "id": purity_prepend,
                "maxclass": "newobj",
                "text": "prepend purity",
                "patching_rect": [760.0, 171.0, 90.0, 22.0],
                "numinlets": 1,
                "numoutlets": 1,
                "outlettype": [""],
            }
        }
    )
    connect(patcher, density_route, 5, purity_prepend)
    gen_ids = [
        box["id"] for box in boxes if box.get("maxclass") == "gen.codebox~"
    ]
    if len(gen_ids) != 4:
        raise RuntimeError(f"Expected four Gen resonator voices; found {len(gen_ids)}")
    for gen_id in gen_ids:
        connect(patcher, purity_prepend, 0, gen_id)

    for box in boxes:
        if box.get("maxclass") == "comment" and "SONIFICATION" in str(
            box.get("text", "")
        ).upper():
            box["text"] = str(box.get("text", "")).replace("v2", "v3")

    router = next(
        box["id"] for box in boxes
        if box.get("text") == "js qmw_density_field_to_resonator_local.js"
    )
    seed = next(box["id"] for box in boxes if box.get("text") == "test")
    loadbang = next(box["id"] for box in boxes if box.get("text") == "loadbang")
    late_delay = next_id(patcher)
    patcher["boxes"].append(
        {
            "box": {
                "id": late_delay,
                "maxclass": "newobj",
                "text": "delay 1500",
                "patching_rect": [1240.0, 390.0, 76.0, 22.0],
                "numinlets": 2,
                "numoutlets": 1,
                "outlettype": ["bang"],
            }
        }
    )
    patcher.setdefault("lines", []).extend(
        [
            {
                "patchline": {
                    "source": [loadbang, 0],
                    "destination": [late_delay, 0],
                }
            },
            {
                "patchline": {
                    "source": [late_delay, 0],
                    "destination": [seed, 0],
                }
            },
        ]
    )

    # The visible seed must still address the live four-outlet router.
    if not any(
        line["patchline"]["source"] == [seed, 0]
        and line["patchline"]["destination"] == [router, 0]
        for line in patcher["lines"]
    ):
        raise RuntimeError("V3 rack seed is disconnected from its router")
    if not all(texts.count(f"send~ qmw_qubit_{voice}") == 1 for voice in range(4)):
        raise RuntimeError("V3 rack is missing independent qbit signal buses")
    router_dependencies = patcher.setdefault("dependency_cache", [])
    router_dependencies[:] = [
        entry
        for entry in router_dependencies
        if entry.get("name") != "qmw_density_field_to_resonator_local.js"
    ]
    router_dependencies.append(
        {
            "name": "qmw_density_field_to_resonator_local.js",
            "bootpath": str(MAX_ROOT),
            "patcherrelativepath": ".",
            "type": "TEXT",
            "implicit": 1,
        }
    )
    return payload


def build_surface() -> dict[str, Any]:
    payload = deepcopy(load(SURFACE_V2))
    patcher = payload["patcher"]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    for box in boxes:
        if box.get("text") == "QMW REALTIME IMPLICIT SURFACE REVERB v2":
            box["text"] = "QMW REALTIME IMPLICIT SURFACE REVERB v3"
        if box.get("text") == f"js {SCHEDULER_V2}":
            box["text"] = f"js {SCHEDULER_V3}"

    density_route = find_box(boxes, text=SURFACE_DENSITY_FIELD_ROUTE)["id"]
    entropy_prepend = routed_destination(patcher, density_route, 2)
    coherence_prepend = routed_destination(patcher, density_route, 4)
    patcher["lines"] = [
        line
        for line in patcher.get("lines", [])
        if not (
            line["patchline"]["source"] in ([density_route, 2], [density_route, 4])
            and line["patchline"]["destination"][0]
            in {entropy_prepend, coherence_prepend}
        )
    ]
    entropy_normalizer = add_normalizer(
        patcher, divisor=4.0, rect=[1400.0, 440.0, 190.0, 22.0]
    )
    coherence_normalizer = add_normalizer(
        patcher, divisor=15.0, rect=[1595.0, 440.0, 195.0, 22.0]
    )
    connect(patcher, density_route, 2, entropy_normalizer)
    connect(patcher, entropy_normalizer, 0, entropy_prepend)
    connect(patcher, density_route, 4, coherence_normalizer)
    connect(patcher, coherence_normalizer, 0, coherence_prepend)
    dependencies = patcher.setdefault("dependency_cache", [])
    dependencies[:] = [
        entry
        for entry in dependencies
        if entry.get("name")
        not in {
            SCHEDULER_V2,
            SCHEDULER_V3,
            "qmw_implicit_surface_controller_v1.js",
        }
    ]
    dependencies.append(
        {
            "name": SCHEDULER_V3,
            "bootpath": str(MAX_ROOT),
            "patcherrelativepath": ".",
            "type": "TEXT",
            "implicit": 1,
        }
    )
    dependencies.append(
        {
            "name": "qmw_implicit_surface_controller_v1.js",
            "bootpath": str(MAX_ROOT),
            "patcherrelativepath": ".",
            "type": "TEXT",
            "implicit": 1,
        }
    )
    return payload


def replace_dependency(
    dependencies: list[dict[str, Any]], old_name: str, new_name: str
) -> None:
    dependencies[:] = [entry for entry in dependencies if entry.get("name") != old_name]
    dependencies.append(
        {
            "name": new_name,
            "bootpath": str(MODULE_ROOT),
            "patcherrelativepath": "control_room_modules",
            "type": "JSON",
            "implicit": 1,
        }
    )


def build_control(
    rack: dict[str, Any], surface: dict[str, Any]
) -> dict[str, Any]:
    payload = deepcopy(load(CONTROL_V2))
    patcher = payload["patcher"]
    boxes = [entry["box"] for entry in patcher.get("boxes", [])]
    title = next(box for box in boxes if box.get("text") == "QMW CONTROL ROOM v2")
    title["text"] = "QMW CONTROL ROOM v3"

    density_route = find_box(boxes, text=CONTROL_DENSITY_FIELD_ROUTE)["id"]
    quantum_monitors: list[str] = []
    for outlet, label in enumerate(
        ("ENTROPY (BITS)", "PURITY", "COHERENCE (L1)"), start=4
    ):
        comment = find_box(boxes, text=label.split(" (")[0])
        comment["text"] = label
        comment_rect = comment.get("patching_rect", [0.0, 0.0, 0.0, 0.0])
        monitor = next(
            box
            for box in boxes
            if box.get("maxclass") == "flonum"
            and box.get("patching_rect", [None, None])[0] == comment_rect[0]
            and box.get("patching_rect", [None, None])[1] > comment_rect[1]
        )
        monitor["ignoreclick"] = 1
        monitor["parameter_enable"] = 0
        quantum_monitors.append(monitor["id"])
        connect(patcher, density_route, outlet, monitor["id"])

    # A compact Pauli field makes every qubit's local Bloch orientation
    # visible instead of reducing the state to one aggregate vector. The
    # nearest-neighbor rows expose the correlations that distinguish four
    # independent Bloch vectors from an entangled state. Named buses make the
    # same values available to later geometry, grain, and resonator mappings.
    qmw_route = find_box(boxes, text="OSC-route /qmw")["id"]
    pauli_namespace = add_box(
        patcher,
        "newobj",
        [1900.0, 80.0, 100.0, 22.0],
        text="OSC-route /pauli",
        numinlets=1,
        numoutlets=2,
        outlettype=["", ""],
    )
    pauli_route = add_box(
        patcher,
        "newobj",
        [1900.0, 110.0, 1050.0, 22.0],
        text=PAULI_ROUTE_TEXT,
        numinlets=1,
        numoutlets=len(PAULI_STRINGS) + 1,
        outlettype=[""] * (len(PAULI_STRINGS) + 1),
    )
    connect(patcher, qmw_route, 0, pauli_namespace)
    connect(patcher, pauli_namespace, 0, pauli_route)

    add_box(
        patcher,
        "comment",
        [980.0, 242.0, 475.0, 18.0],
        text="LOCAL PAULI FIELD     Q0          Q1          Q2          Q3",
        presentation=True,
        fontsize=10.0,
        fontface=1,
    )
    group_specs = (
        ("X", LOCAL_PAULI_GROUPS[0], 264.0),
        ("Y", LOCAL_PAULI_GROUPS[1], 295.0),
        ("Z", LOCAL_PAULI_GROUPS[2], 326.0),
    )
    pauli_outlet = {name: index for index, name in enumerate(PAULI_STRINGS)}
    for axis, names, y in group_specs:
        add_box(
            patcher,
            "comment",
            [980.0, y + 2.0, 30.0, 18.0],
            text=axis,
            presentation=True,
            fontsize=10.0,
            fontface=1,
        )
        pack = add_box(
            patcher,
            "newobj",
            [2020.0, y, 145.0, 22.0],
            text="pak 0. 0. 0. 0.",
            numinlets=4,
            numoutlets=1,
            outlettype=["list"],
        )
        meter = add_box(
            patcher,
            "multislider",
            [1020.0, y, 435.0, 24.0],
            presentation=True,
            size=4,
            setminmax=[-1.0, 1.0],
            parameter_enable=0,
            ignoreclick=1,
            annotation=f"<{axis}> for qubits Q0, Q1, Q2, Q3",
        )
        group_send = add_box(
            patcher,
            "newobj",
            [2180.0, y, 115.0, 22.0],
            text=f"s qmw.pauli.{axis.lower()}",
            numinlets=1,
            numoutlets=0,
        )
        for inlet, name in enumerate(names):
            connect(patcher, pauli_route, pauli_outlet[name], pack, inlet)
        connect(patcher, pack, 0, meter)
        connect(patcher, pack, 0, group_send)

    add_box(
        patcher,
        "comment",
        [980.0, 361.0, 105.0, 18.0],
        text="CORR 01|12|23",
        presentation=True,
        fontsize=10.0,
        fontface=1,
    )
    correlation_pack = add_box(
        patcher,
        "newobj",
        [2020.0, 360.0, 315.0, 22.0],
        text="pak 0. 0. 0. 0. 0. 0. 0. 0. 0.",
        numinlets=9,
        numoutlets=1,
        outlettype=["list"],
    )
    correlation_meter = add_box(
        patcher,
        "multislider",
        [1090.0, 358.0, 365.0, 24.0],
        presentation=True,
        size=9,
        setminmax=[-1.0, 1.0],
        parameter_enable=0,
        ignoreclick=1,
        annotation=(
            "Nearest-neighbor order: Q01 XX YY ZZ, "
            "Q12 XX YY ZZ, Q23 XX YY ZZ"
        ),
    )
    correlation_send = add_box(
        patcher,
        "newobj",
        [2350.0, 360.0, 165.0, 22.0],
        text="s qmw.pauli.correlations",
        numinlets=1,
        numoutlets=0,
    )
    for inlet, name in enumerate(PAULI_CORRELATIONS):
        connect(patcher, pauli_route, pauli_outlet[name], correlation_pack, inlet)
    connect(patcher, correlation_pack, 0, correlation_meter)
    connect(patcher, correlation_pack, 0, correlation_send)

    for name in PAULI_STRINGS:
        named_send = add_box(
            patcher,
            "newobj",
            [2550.0, 80.0 + 25.0 * pauli_outlet[name], 150.0, 22.0],
            text=f"s qmw.pauli.{name}",
            numinlets=1,
            numoutlets=0,
        )
        connect(patcher, pauli_route, pauli_outlet[name], named_send)

    replacements: dict[str, tuple[str, dict[str, Any]]] = {
        RACK_V2.name: (RACK_V3.name, rack),
        SURFACE_V2.name: (SURFACE_V3.name, surface),
    }
    found: set[str] = set()
    for box in boxes:
        old_name = box.get("name")
        if box.get("maxclass") != "bpatcher" or old_name not in replacements:
            continue
        new_name, module = replacements[old_name]
        box["name"] = new_name
        box["embed"] = 1
        box["patcher"] = deepcopy(module["patcher"])
        found.add(old_name)
    if found != set(replacements):
        raise RuntimeError(f"Could not embed both v3 bpatchers: {sorted(found)}")
    dependencies = patcher.setdefault("dependency_cache", [])
    dependencies[:] = [
        entry
        for entry in dependencies
        if (
            entry.get("name")
            not in {
                RACK_V2.name,
                SURFACE_V2.name,
                RACK_V3.name,
                SURFACE_V3.name,
                SCHEDULER_V2,
            }
            and "control_room_modules" not in str(entry.get("bootpath", ""))
            and "control_room_modules"
            not in str(entry.get("patcherrelativepath", ""))
        )
    ]
    dependencies.append(
        {
            "name": SCHEDULER_V3,
            "bootpath": str(MAX_ROOT),
            "patcherrelativepath": ".",
            "type": "TEXT",
            "implicit": 1,
        }
    )
    return payload


def validate(control: dict[str, Any], rack: dict[str, Any], surface: dict[str, Any]) -> None:
    control_boxes = [entry["box"] for entry in control["patcher"].get("boxes", [])]
    for name in (RACK_V3.name, SURFACE_V3.name):
        matches = [box for box in control_boxes if box.get("name") == name]
        if len(matches) != 1 or matches[0].get("embed") != 1:
            raise RuntimeError(f"V3 embedded bpatcher is invalid: {name}")
        if "patcher" not in matches[0]:
            raise RuntimeError(f"V3 embedded patcher data is missing: {name}")
    rack_boxes = [entry["box"] for entry in rack["patcher"].get("boxes", [])]
    rack_texts = [box.get("text", "") for box in rack_boxes]
    if rack_texts.count("delay 1500") != 1:
        raise RuntimeError("V3 late resonator seed is missing")
    surface_texts = [
        entry["box"].get("text", "")
        for entry in surface["patcher"].get("boxes", [])
    ]
    if "QMW REALTIME IMPLICIT SURFACE REVERB v3" not in surface_texts:
        raise RuntimeError("V3 surface title is missing")
    if f"js {SCHEDULER_V3}" not in surface_texts:
        raise RuntimeError("V3 independent-lane grain scheduler is missing")

    control_route = find_box(control_boxes, text=CONTROL_DENSITY_FIELD_ROUTE)["id"]
    control_by_id = {box["id"]: box for box in control_boxes}
    live_monitor_lines = {
        (line["patchline"]["source"][1], line["patchline"]["destination"][0])
        for line in control["patcher"].get("lines", [])
        if line["patchline"]["source"][0] == control_route
        and line["patchline"]["source"][1] in {4, 5, 6}
    }
    if {outlet for outlet, _ in live_monitor_lines} != {4, 5, 6}:
        raise RuntimeError("V3 live entropy/purity/coherence monitors are disconnected")
    if not all(
        control_by_id[destination].get("ignoreclick") == 1
        for _, destination in live_monitor_lines
    ):
        raise RuntimeError("V3 live quantum monitors must be read-only")

    control_texts = [box.get("text", "") for box in control_boxes]
    if control_texts.count(PAULI_ROUTE_TEXT) != 1:
        raise RuntimeError("V3 Pauli field router is missing")
    for name in PAULI_STRINGS:
        if control_texts.count(f"s qmw.pauli.{name}") != 1:
            raise RuntimeError(f"V3 named Pauli bus is missing: {name}")
    for axis in ("x", "y", "z", "correlations"):
        if control_texts.count(f"s qmw.pauli.{axis}") != 1:
            raise RuntimeError(f"V3 grouped Pauli bus is missing: {axis}")
    pauli_meters = [
        box
        for box in control_boxes
        if box.get("maxclass") == "multislider"
        and box.get("setminmax") == [-1.0, 1.0]
    ]
    if sorted(box.get("size") for box in pauli_meters) != [4, 4, 4, 9]:
        raise RuntimeError("V3 Pauli meters are incomplete")
    if not all(box.get("ignoreclick") == 1 for box in pauli_meters):
        raise RuntimeError("V3 Pauli meters must be read-only")

    rack_route = find_box(rack_boxes, text=DENSITY_FIELD_ROUTE)["id"]
    rack_by_id = {box["id"]: box for box in rack_boxes}
    direct_prepend_routes = {
        (line["patchline"]["source"][1], rack_by_id[line["patchline"]["destination"][0]].get("text"))
        for line in rack["patcher"].get("lines", [])
        if line["patchline"]["source"][0] == rack_route
        and line["patchline"]["destination"][0] in rack_by_id
        and str(rack_by_id[line["patchline"]["destination"][0]].get("text", "")).startswith("prepend ")
    }
    if direct_prepend_routes != {
        (0, "prepend speed"),
        (1, "prepend magnitude"),
        (2, "prepend phase"),
        (3, "prepend harmonics"),
        (5, "prepend purity"),
    }:
        raise RuntimeError(f"V3 density-field routing is misaligned: {direct_prepend_routes}")
    if rack_texts.count("prepend purity") != 1:
        raise RuntimeError("V3 purity mapping is missing")
    for divisor in (4, 15):
        expected = f"expr min(1., max(0., $f1 / {divisor}.))"
        if rack_texts.count(expected) != 1 or surface_texts.count(expected) != 1:
            raise RuntimeError(f"V3 DSP normalization is missing: {expected}")


def main() -> int:
    rack = build_rack()
    surface = build_surface()
    control = build_control(rack, surface)
    validate(control, rack, surface)
    RACK_V3.write_text(json.dumps(rack, indent=4) + "\n", encoding="utf-8")
    SURFACE_V3.write_text(json.dumps(surface, indent=4) + "\n", encoding="utf-8")
    CONTROL_V3.write_text(json.dumps(control, indent=4) + "\n", encoding="utf-8")
    print(f"Built embedded {CONTROL_V3}; v2 files were not modified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
