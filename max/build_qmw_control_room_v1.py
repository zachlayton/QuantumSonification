#!/usr/bin/env python3
"""Build the first modular QMW Control Room patch and its shared-bus modules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_ROOT = PROJECT_ROOT / "max"
MODULE_ROOT = MAX_ROOT / "control_room_modules"
SONIFICATION_ROUTER_JS = "qmw_density_field_to_resonator_local.js"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def guard_nested_osc_routes(patcher: dict[str, Any]) -> int:
    """Keep decoded values from being sent into another OSC-route.

    CNMAT ``OSC-route`` uses the same outlet for an exact address match and
    for deeper addresses.  An exact message such as ``/qmw/entanglement 0.5``
    therefore emits a bare float from the ``/entanglement`` outlet.  If that
    outlet also feeds routers for ``/partition_...``, every child router posts
    a "doesn't understand float" error.

    A Max ``route float int list symbol`` object drops decoded payloads while
    forwarding address-selector messages through its unmatched outlet.  One
    guard is shared by every nested router attached to a source outlet.
    """
    boxes = patcher.get("boxes", [])
    lines = patcher.get("lines", [])
    by_id = {entry["box"]["id"]: entry["box"] for entry in boxes}

    nested_groups: dict[tuple[str, int], list[int]] = {}
    for index, entry in enumerate(lines):
        patchline = entry.get("patchline", {})
        source = patchline.get("source", [None, None])
        destination = patchline.get("destination", [None, None])
        source_box = by_id.get(source[0], {})
        destination_box = by_id.get(destination[0], {})
        if (
            str(source_box.get("text", "")).startswith("OSC-route ")
            and str(destination_box.get("text", "")).startswith(
                "OSC-route "
            )
        ):
            nested_groups.setdefault((source[0], int(source[1])), []).append(
                index
            )

    if not nested_groups:
        return 0

    right_edge = max(
        (
            float(box.get("patching_rect", [0.0, 0.0, 0.0, 0.0])[0])
            + float(box.get("patching_rect", [0.0, 0.0, 0.0, 0.0])[2])
            for box in by_id.values()
        ),
        default=0.0,
    )
    guard_x = right_edge + 80.0

    for guard_number, ((source_id, outlet), line_indexes) in enumerate(
        sorted(nested_groups.items()), start=1
    ):
        guard_id = f"obj-qmw-osc-type-guard-{guard_number}"
        boxes.append(
            {
                "box": {
                    "id": guard_id,
                    "maxclass": "newobj",
                    "text": "route float int list symbol",
                    "numinlets": 1,
                    "numoutlets": 5,
                    "outlettype": ["", "", "", "", ""],
                    "patching_rect": [
                        guard_x,
                        20.0 + 30.0 * (guard_number - 1),
                        162.0,
                        22.0,
                    ],
                }
            }
        )
        lines.append(
            {
                "patchline": {
                    "source": [source_id, outlet],
                    "destination": [guard_id, 0],
                }
            }
        )
        for line_index in line_indexes:
            # Outlet four is the unmatched outlet: OSC address selectors pass
            # through it, while scalar/list payloads leave via 0..3 and stop.
            lines[line_index]["patchline"]["source"] = [guard_id, 4]

    return len(nested_groups)


def shared_bus_module(source: Path, destination: Path) -> None:
    """Clone a standalone patch and replace its UDP receiver with the hub bus."""
    payload = load_json(source)
    patcher = payload["patcher"]
    # A bpatcher must show the module's patching canvas.  These source patches
    # do not define presentation coordinates of their own, so forcing their
    # presentation view would produce a correctly loaded but visually empty
    # module.
    patcher["openinpresentation"] = 0
    replaced = 0
    for entry in patcher.get("boxes", []):
        box = entry["box"]
        if box.get("text") == "udpreceive 7400":
            box["text"] = "r qmw.osc.raw"
            box["numinlets"] = 0
            box["numoutlets"] = 1
            box["outlettype"] = [""]
            replaced += 1
        if box.get("text") in {
            "js qmw_density_field_to_resonator.js",
            f"js {SONIFICATION_ROUTER_JS}",
        }:
            # The shared module is one directory below this JS file. Without
            # an explicit dependency Max resolves the object as a missing
            # one-inlet/one-outlet placeholder and deletes voice outlets 1..3
            # when the bpatcher is saved.
            box["numinlets"] = 4
            box["numoutlets"] = 4
            box["outlettype"] = ["", "", "", ""]
            box["text"] = f"js {SONIFICATION_ROUTER_JS}"
            attributes = box.setdefault("saved_object_attributes", {})
            attributes["filename"] = SONIFICATION_ROUTER_JS
    if replaced != 1:
        raise RuntimeError(f"Expected one UDP receiver in {source}; found {replaced}")
    if any(
        entry["box"].get("text") == f"js {SONIFICATION_ROUTER_JS}"
        for entry in patcher.get("boxes", [])
    ):
        dependencies = patcher.setdefault("dependency_cache", [])
        dependencies[:] = [
            dependency
            for dependency in dependencies
            if dependency.get("name")
            not in {
                "qmw_density_field_to_resonator.js",
                SONIFICATION_ROUTER_JS,
            }
        ]
        dependencies.append(
            {
                "name": SONIFICATION_ROUTER_JS,
                "bootpath": str(MODULE_ROOT),
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1,
            }
        )
    guard_nested_osc_routes(patcher)
    boxes_by_id = {
        entry["box"]["id"]: entry["box"]
        for entry in patcher.get("boxes", [])
    }
    router_ids = {
        identifier
        for identifier, box in boxes_by_id.items()
        if box.get("text") == f"js {SONIFICATION_ROUTER_JS}"
    }
    if router_ids:
        gen_ids = {
            identifier
            for identifier, box in boxes_by_id.items()
            if box.get("maxclass") == "gen.codebox~"
        }
        router_inlets = {
            int(line["patchline"]["destination"][1])
            for line in patcher.get("lines", [])
            if line["patchline"]["destination"][0] in router_ids
        }
        if router_inlets != {0, 1, 2, 3}:
            raise RuntimeError(
                "Sonification rack must connect magnitude, phase, speed, "
                f"and harmonics to JS inlets 0..3; found {sorted(router_inlets)}"
            )
        voice_outlets = {
            int(line["patchline"]["source"][1])
            for line in patcher.get("lines", [])
            if line["patchline"]["source"][0] in router_ids
            and line["patchline"]["destination"][0] in gen_ids
        }
        if voice_outlets != {0, 1, 2, 3}:
            raise RuntimeError(
                "Sonification rack must connect JS outlets 0..3 to four "
                f"Gen voices; found {sorted(voice_outlets)}"
            )
    write_json(destination, payload)


def resolve_manifest_path(manifest: Path, value: str | None) -> str | None:
    if not value:
        return None
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    return str(candidate.resolve())


def choose_asset(root: Path, pattern: str) -> str | None:
    candidates = sorted(root.glob(pattern))
    if not candidates:
        return None
    preferred = [path for path in candidates if "rhino" not in path.name.lower()]
    return str((preferred or candidates)[0].resolve())


def build_asset_registry() -> dict[str, Any]:
    assets: list[dict[str, Any]] = []
    for manifest in sorted(PROJECT_ROOT.rglob("current_state.json")):
        if ".git" in manifest.parts:
            continue
        try:
            state = load_json(manifest)
        except (OSError, json.JSONDecodeError):
            continue
        paths = state.get("paths", {})
        ir_path = resolve_manifest_path(manifest, paths.get("ir_wav"))
        if not ir_path:
            continue
        # Most generated assets store current_state.json in a ``living``
        # subdirectory, while Grasshopper candidates store it directly in the
        # candidate directory. Collapsing both layouts to parent.parent gave
        # every Grasshopper candidate the same registry ID.
        asset_root = (
            manifest.parent.parent
            if manifest.parent.name == "living"
            else manifest.parent
        )
        relative_root = asset_root.relative_to(PROJECT_ROOT)
        descriptors = state.get("descriptors", {})
        assets.append(
            {
                "id": str(relative_root).replace("/", "."),
                "label": asset_root.name.replace("_", " "),
                "family": relative_root.parts[0] if relative_root.parts else "geometry",
                "revision": int(state.get("revision", 0)),
                "current_state": str(manifest.resolve()),
                "mesh": choose_asset(asset_root, "*.obj"),
                "preview": choose_asset(asset_root, "*.png"),
                "ir": ir_path,
                "mode_count": int(state.get("mode_count", 0)),
                "spectral_gap": float(state.get("spectral_gap", 0.0)),
                "frequency_min_hz": float(state.get("frequency_min_hz", 0.0)),
                "frequency_max_hz": float(state.get("frequency_max_hz", 0.0)),
                "quantum": descriptors.get("quantum", {}),
                "acoustics": descriptors.get("acoustics", {}),
            }
        )
    return {
        "schema": "qmw.asset-registry.v1",
        "project_root": str(PROJECT_ROOT),
        "count": len(assets),
        "assets": assets,
    }


class MaxPatchBuilder:
    def __init__(self) -> None:
        self.boxes: list[dict[str, Any]] = []
        self.lines: list[dict[str, Any]] = []
        self.counter = 0

    def add(
        self,
        maxclass: str,
        rect: list[float],
        *,
        text: str | None = None,
        **properties: Any,
    ) -> str:
        self.counter += 1
        identifier = f"obj-{self.counter}"
        box: dict[str, Any] = {
            "id": identifier,
            "maxclass": maxclass,
            "patching_rect": rect,
            # The Control Room is intentionally laid out as a dashboard in
            # patching view. Mirror that layout into presentation mode so the
            # generated patch cannot open to a blank canvas.
            "presentation": 1,
            "presentation_rect": list(rect),
        }
        if text is not None:
            box["text"] = text
        box.update(properties)
        self.boxes.append({"box": box})
        return identifier

    def connect(
        self,
        source: str,
        outlet: int,
        destination: str,
        inlet: int = 0,
    ) -> None:
        self.lines.append(
            {
                "patchline": {
                    "source": [source, outlet],
                    "destination": [destination, inlet],
                }
            }
        )

    def patch(
        self, dependency_cache: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        return {
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
                "rect": [30.0, 50.0, 1880.0, 980.0],
                "openinpresentation": 1,
                "default_fontsize": 12.0,
                "default_fontface": 0,
                "default_fontname": "Arial",
                "gridonopen": 1,
                "gridsize": [10.0, 10.0],
                "boxes": self.boxes,
                "lines": self.lines,
                "dependency_cache": dependency_cache or [],
            }
        }


def ensure_family_monitors(patcher: dict[str, Any]) -> int:
    """Attach visible monitors and named buses to every QMW OSC family."""
    families = (
        "density",
        "bloch",
        "bohm",
        "circuit",
        "entanglement",
        "hamiltonian",
        "trajectory",
        "flucoma",
    )
    boxes = patcher.get("boxes", [])
    lines = patcher.get("lines", [])
    by_id = {entry["box"]["id"]: entry["box"] for entry in boxes}
    if any(box.get("text") == "s qmw.density" for box in by_id.values()):
        return 0

    family_router_id = next(
        (
            identifier
            for identifier, box in by_id.items()
            if str(box.get("text", "")).startswith(
                "OSC-route /density_field /density /bloch"
            )
        ),
        None,
    )
    if family_router_id is None:
        raise RuntimeError("Control Room family OSC router was not found")

    numeric_ids = [
        int(identifier[4:])
        for identifier in by_id
        if identifier.startswith("obj-") and identifier[4:].isdigit()
    ]
    next_id = max(numeric_ids, default=0) + 1

    def add_box(
        maxclass: str,
        rect: list[float],
        *,
        text: str | None = None,
        presentation: bool = True,
        **properties: Any,
    ) -> str:
        nonlocal next_id
        identifier = f"obj-{next_id}"
        next_id += 1
        box: dict[str, Any] = {
            "id": identifier,
            "maxclass": maxclass,
            "patching_rect": rect,
        }
        if presentation:
            box["presentation"] = 1
            box["presentation_rect"] = list(rect)
        else:
            box["presentation"] = 0
        if text is not None:
            box["text"] = text
        box.update(properties)
        boxes.append({"box": box})
        return identifier

    for index, family in enumerate(families):
        y = 82.0 + 35.0 * index
        add_box(
            "comment",
            [1495.0, y + 2.0, 105.0, 18.0],
            text=family.upper(),
            fontsize=9.0,
            fontface=1,
            textcolor=[0.68, 0.78, 0.90, 1.0],
        )
        activity = add_box("button", [1602.0, y, 22.0, 22.0])
        value = add_box(
            "message",
            [1632.0, y, 208.0, 22.0],
            text="waiting",
        )
        bus = add_box(
            "newobj",
            [1880.0, y, 145.0, 22.0],
            text=f"s qmw.{family}",
            presentation=False,
        )
        # Outlet zero is /density_field. The monitored families begin at one.
        outlet = index + 1
        for destination, inlet in ((activity, 0), (value, 1), (bus, 0)):
            lines.append(
                {
                    "patchline": {
                        "source": [family_router_id, outlet],
                        "destination": [destination, inlet],
                    }
                }
            )

    return len(families)


def make_panel(builder: MaxPatchBuilder, rect: list[float], color: list[float]) -> str:
    return builder.add(
        "panel",
        rect,
        background=1,
        bgcolor=color,
        border=1,
        rounded=12,
    )


def build_control_room() -> dict[str, Any]:
    b = MaxPatchBuilder()

    make_panel(b, [10.0, 10.0, 1850.0, 390.0], [0.08, 0.09, 0.12, 1.0])
    make_panel(b, [10.0, 410.0, 600.0, 520.0], [0.10, 0.13, 0.18, 1.0])
    make_panel(b, [620.0, 410.0, 560.0, 520.0], [0.12, 0.10, 0.17, 1.0])
    make_panel(b, [1190.0, 410.0, 670.0, 520.0], [0.10, 0.16, 0.13, 1.0])

    b.add(
        "comment",
        [30.0, 22.0, 620.0, 34.0],
        text="QMW CONTROL ROOM v1",
        fontsize=24.0,
        fontface=1,
        textcolor=[0.85, 0.93, 1.0, 1.0],
    )
    b.add(
        "comment",
        [30.0, 55.0, 760.0, 22.0],
        text="One OSC hub · full quantum telemetry · sonification · living geometry convolution",
        fontsize=13.0,
        textcolor=[0.60, 0.72, 0.86, 1.0],
    )

    udp = b.add("newobj", [30.0, 92.0, 105.0, 22.0], text="udpreceive 7400")
    trigger = b.add("newobj", [150.0, 92.0, 45.0, 22.0], text="t l b")
    raw_send = b.add("newobj", [210.0, 92.0, 105.0, 22.0], text="s qmw.osc.raw")
    activity = b.add("button", [330.0, 91.0, 24.0, 24.0])
    b.add("comment", [365.0, 94.0, 135.0, 20.0], text="OSC 7400 activity")
    qmw_route = b.add("newobj", [30.0, 127.0, 102.0, 22.0], text="OSC-route /qmw")
    family_route = b.add(
        "newobj",
        [150.0, 127.0, 665.0, 22.0],
        text=(
            "OSC-route /density_field /density /bloch /bohm /circuit "
            "/entanglement /hamiltonian /trajectory /flucoma"
        ),
    )
    b.connect(udp, 0, trigger)
    b.connect(trigger, 0, raw_send)
    b.connect(trigger, 0, qmw_route)
    b.connect(trigger, 1, activity)
    b.connect(qmw_route, 0, family_route)

    density_field_route = b.add(
        "newobj",
        [30.0, 168.0, 570.0, 22.0],
        text=(
            "OSC-route /magnitude /phase /speed /harmonics /entropy /purity /coherence"
        ),
    )
    b.connect(family_route, 0, density_field_route)

    slider_labels = ("MAGNITUDE", "PHASE", "SPEED", "HARMONICS")
    slider_ranges = ((0.0, 1.0), (-3.14159, 3.14159), (0.0, 4.0), (0.0, 64.0))
    for index, (label, value_range) in enumerate(zip(slider_labels, slider_ranges)):
        x = 30.0 + index * 205.0
        b.add("comment", [x, 198.0, 160.0, 18.0], text=label, fontsize=10.0)
        slider = b.add(
            "multislider",
            [x, 218.0, 190.0, 72.0],
            size=16,
            setminmax=list(value_range),
            parameter_enable=0,
        )
        b.connect(density_field_route, index, slider)

    metric_labels = (
        "ENTROPY (BITS)",
        "PURITY",
        "COHERENCE (L1)",
    )
    for index, label in enumerate(metric_labels):
        x = 30.0 + index * 150.0
        b.add("comment", [x, 304.0, 130.0, 18.0], text=label, fontsize=10.0)
        value = b.add(
            "flonum",
            [x, 325.0, 110.0, 22.0],
            format=6,
            ignoreclick=1,
            parameter_enable=0,
        )
        b.connect(density_field_route, 4 + index, value, 0)

    b.add("comment", [500.0, 304.0, 250.0, 18.0], text="ENGINE EXCITATION", fontsize=10.0)
    excitation_prepend = b.add(
        "newobj", [650.0, 355.0, 145.0, 22.0], text="prepend /qmw/excitation"
    )
    control_send = b.add("newobj", [810.0, 355.0, 150.0, 22.0], text="udpsend 127.0.0.1 7402")
    b.connect(excitation_prepend, 0, control_send)
    for index, source in enumerate(
        ("internal", "hydrogen_spectrum", "hydrogen_orbital", "schrodinger_packet", "schrodinger_interference")
    ):
        message = b.add("message", [500.0 + (index % 3) * 145.0, 325.0 + (index // 3) * 30.0, 137.0, 22.0], text=source)
        b.connect(message, 0, excitation_prepend)

    b.add("comment", [980.0, 82.0, 250.0, 20.0], text="GEOMETRY / IR ASSET REGISTRY", fontface=1)
    loadbang = b.add("newobj", [980.0, 108.0, 60.0, 22.0], text="loadbang")
    read_registry = b.add("message", [1050.0, 108.0, 220.0, 22.0], text="read qmw_asset_registry_v1.json")
    registry = b.add("newobj", [1280.0, 108.0, 205.0, 22.0], text="dict qmw.asset.registry @embed 0")
    b.add("newobj", [980.0, 140.0, 505.0, 235.0], text="dict.view qmw.asset.registry")
    b.connect(loadbang, 0, read_registry)
    b.connect(read_registry, 0, registry)

    b.add("comment", [25.0, 420.0, 360.0, 24.0], text="SONIFICATION RACK", fontsize=16.0, fontface=1)
    b.add("comment", [635.0, 420.0, 360.0, 24.0], text="QUANTUM / DENSITY MONITOR", fontsize=16.0, fontface=1)
    b.add("comment", [1205.0, 420.0, 520.0, 24.0], text="REALTIME IMPLICIT SURFACE REVERB", fontsize=16.0, fontface=1)

    b.add(
        "bpatcher",
        [25.0, 450.0, 570.0, 460.0],
        name="QMW_Sonification_Rack_Module_v1.maxpat",
        numinlets=0,
        numoutlets=0,
        offset=[0.0, 0.0],
        enablehscroll=1,
        enablevscroll=1,
        border=1,
        viewvisibility=1,
    )

    # Headless control adapter: it listens to the shared OSC bus, mirrors
    # Spat-native messages onto qmw.spat.control, and mirrors modal controls
    # to qmw.acoustic.modal.control. The full patch remains available standalone for
    # inspecting spat5.oper and its source trajectories.
    b.add(
        "bpatcher",
        [1840.0, 915.0, 10.0, 10.0],
        name="QMW_Bloch_Harmonic_Spat_Modal_v1.maxpat",
        numinlets=4,
        numoutlets=3,
        offset=[0.0, 0.0],
        border=0,
        viewvisibility=0,
        hidden=1,
        presentation=0,
    )
    b.add(
        "bpatcher",
        [635.0, 450.0, 530.0, 460.0],
        name="QMW_Density_Matrix_Module_v1.maxpat",
        numinlets=0,
        numoutlets=0,
        offset=[0.0, 0.0],
        enablehscroll=1,
        enablevscroll=1,
        border=1,
        viewvisibility=1,
    )
    b.add(
        "bpatcher",
        [1205.0, 450.0, 640.0, 460.0],
        name="QMW_Realtime_Surface_Reverb_v1.maxpat",
        numinlets=0,
        numoutlets=0,
        offset=[0.0, 0.0],
        enablehscroll=1,
        enablevscroll=1,
        border=1,
        viewvisibility=1,
    )

    b.add(
        "comment",
        [25.0, 940.0, 1200.0, 22.0],
        text=(
            "Start quantumsonification_conductor.py normally. The conductor now defaults to the full OSC profile; "
            "use --profile resonator only for the lean performance stream."
        ),
        textcolor=[0.65, 0.72, 0.82, 1.0],
    )
    dependencies = [
        {
            "name": "QMW_Sonification_Rack_Module_v1.maxpat",
            "bootpath": str(MODULE_ROOT),
            "patcherrelativepath": "control_room_modules",
            "type": "JSON",
            "implicit": 1,
        },
        {
            "name": "QMW_Density_Matrix_Module_v1.maxpat",
            "bootpath": str(MODULE_ROOT),
            "patcherrelativepath": "control_room_modules",
            "type": "JSON",
            "implicit": 1,
        },
        {
            "name": "QMW_Realtime_Surface_Reverb_v1.maxpat",
            "bootpath": str(MODULE_ROOT),
            "patcherrelativepath": "control_room_modules",
            "type": "JSON",
            "implicit": 1,
        },
        {
            "name": "QMW_Bloch_Harmonic_Spat_Modal_v1.maxpat",
            "bootpath": str(MODULE_ROOT),
            "patcherrelativepath": "control_room_modules",
            "type": "JSON",
            "implicit": 1,
        },
    ]
    payload = b.patch(dependency_cache=dependencies)
    ensure_family_monitors(payload["patcher"])
    return payload


def main() -> int:
    shared_bus_module(
        MAX_ROOT / "QMW_Music_of_the_Spheres_Resonator_v3_IRouts.maxpat",
        MODULE_ROOT / "QMW_Sonification_Rack_Module_v1.maxpat",
    )
    shared_bus_module(
        MAX_ROOT / "patches" / "quantum_population_DENSITYMATRIX.maxpat",
        MODULE_ROOT / "QMW_Density_Matrix_Module_v1.maxpat",
    )
    write_json(MAX_ROOT / "qmw_asset_registry_v1.json", build_asset_registry())
    write_json(MAX_ROOT / "QMW_Control_Room_v1.maxpat", build_control_room())
    print("Built QMW_Control_Room_v1.maxpat and shared-bus modules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
