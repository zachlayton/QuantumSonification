{
    "patcher": {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 0,
            "revision": 0,
            "architecture": "x64",
            "modernui": 1
        },
        "classnamespace": "box",
        "rect": [30.0, 45.0, 1420.0, 900.0],
        "bglocked": 0,
        "openinpresentation": 0,
        "default_fontsize": 12.0,
        "default_fontface": 0,
        "default_fontname": "Arial",
        "gridonopen": 1,
        "gridsize": [15.0, 15.0],
        "gridsnaponopen": 1,
        "objectsnaponopen": 1,
        "description": "Sixteen-source IRCAM Spat WFS renderer using the authoritative CRAIVE 128-speaker geometry.",
        "digest": "Routes sixteen unsummed MC sources to CRAIVE WFS and accepts QMW voice/azimuth/elevation/distance/spread tuples.",
        "tags": "CRAIVE IRCAM Spat WFS MC 16 sources 128 speakers QMW",
        "boxes": [
            {
                "box": {
                    "id": "obj-1",
                    "maxclass": "comment",
                    "fontsize": 22.0,
                    "fontface": 1,
                    "text": "QMW → CRAIVE Spat 128 Renderer — 16 sources, v9",
                    "patching_rect": [30.0, 18.0, 650.0, 31.0]
                }
            },
            {
                "box": {
                    "id": "obj-2",
                    "maxclass": "comment",
                    "fontsize": 13.0,
                    "text": "Sixteen MC channels remain discrete through spat5.wfs~; CRAIVE channels 1–128 are emitted as one MC signal.",
                    "patching_rect": [31.0, 52.0, 840.0, 21.0]
                }
            },
            {
                "box": {
                    "id": "obj-3",
                    "maxclass": "inlet",
                    "index": 1,
                    "comment": "sixteen-channel MC source signal, one channel per Spat source",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": ["multichannelsignal"],
                    "patching_rect": [65.0, 115.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-4",
                    "maxclass": "inlet",
                    "index": 2,
                    "comment": "voice azimuth elevation distance spread, /qks/spat, /qqt/spat, /qmw/spat, or native Spat source OSC",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [395.0, 115.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-5",
                    "maxclass": "inlet",
                    "index": 3,
                    "comment": "renderer control: layout, defaults, viewer ..., wfs ..., source ..., status, or native Spat OSC",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [730.0, 115.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-6",
                    "maxclass": "comment",
                    "text": "16ch MC audio",
                    "patching_rect": [105.0, 120.0, 110.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-7",
                    "maxclass": "comment",
                    "text": "QMW spatial tuple / existing decoded OSC branch",
                    "patching_rect": [435.0, 120.0, 270.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-8",
                    "maxclass": "comment",
                    "text": "layout / viewer / WFS control",
                    "patching_rect": [770.0, 120.0, 205.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-9",
                    "maxclass": "newobj",
                    "text": "js qmw_craive_source_router16_v9.js",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": ["", "", ""],
                    "patching_rect": [395.0, 185.0, 255.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-10",
                    "maxclass": "newobj",
                    "text": "route layout defaults viewer wfs source status",
                    "numinlets": 1,
                    "numoutlets": 7,
                    "outlettype": ["", "", "", "", "", "", ""],
                    "patching_rect": [730.0, 185.0, 305.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-11",
                    "maxclass": "newobj",
                    "text": "qmw_craive128_layout_v9",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [1045.0, 250.0, 180.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-12",
                    "maxclass": "message",
                    "text": "/speaker/number 128, /source/number 16, /speaker/*/vumeter/visible 1, /speaker/*/orientation/visible 1",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [730.0, 285.0, 650.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-13",
                    "maxclass": "message",
                    "text": "/source/*/window/size 100, /source/*/blend/method focus+nonfocus, /dump/area",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [730.0, 320.0, 495.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-14",
                    "maxclass": "newobj",
                    "text": "t b b",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": ["bang", "bang"],
                    "patching_rect": [810.0, 245.0, 42.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-15",
                    "maxclass": "newobj",
                    "text": "loadbang",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": ["bang"],
                    "patching_rect": [1045.0, 115.0, 60.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-16",
                    "maxclass": "newobj",
                    "text": "t b b b",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": ["bang", "bang", "bang"],
                    "patching_rect": [1045.0, 150.0, 58.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-17",
                    "maxclass": "button",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": ["bang"],
                    "patching_rect": [1045.0, 215.0, 24.0, 24.0]
                }
            },
            {
                "box": {
                    "id": "obj-18",
                    "maxclass": "comment",
                    "text": "reload exact CRAIVE geometry",
                    "patching_rect": [1078.0, 217.0, 190.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-19",
                    "maxclass": "message",
                    "text": "ring 2. 0.",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [395.0, 225.0, 72.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-20",
                    "maxclass": "comment",
                    "text": "manual deterministic 2 m source ring (never automatic)",
                    "patching_rect": [475.0, 227.0, 310.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-21",
                    "maxclass": "newobj",
                    "text": "spat5.viewer",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": ["", "", ""],
                    "patching_rect": [815.0, 390.0, 440.0, 300.0],
                    "saved_object_attributes": {
                        "parameter_enable": 0
                    }
                }
            },
            {
                "box": {
                    "id": "obj-22",
                    "maxclass": "comment",
                    "text": "IRCAM convention: +Y is front; azimuth/elevation are degrees; distance and CRAIVE XYZ are metres.",
                    "patching_rect": [815.0, 700.0, 560.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-23",
                    "maxclass": "newobj",
                    "text": "spat5.wfs~ @mc 1 @sources 16 @speakers 128",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": ["multichannelsignal", ""],
                    "patching_rect": [65.0, 455.0, 315.0, 22.0],
                    "saved_object_attributes": {
                        "parameter_enable": 0
                    }
                }
            },
            {
                "box": {
                    "id": "obj-24",
                    "maxclass": "newobj",
                    "text": "mc.mixdown~ 2 @autogain 1",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": ["multichannelsignal"],
                    "patching_rect": [310.0, 525.0, 195.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-25",
                    "maxclass": "comment",
                    "text": "monitor only — fold-down occurs after WFS",
                    "patching_rect": [515.0, 527.0, 235.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-26",
                    "maxclass": "newobj",
                    "text": "prepend source_metadata",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [395.0, 275.0, 155.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-27",
                    "maxclass": "newobj",
                    "text": "prepend source_router",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [565.0, 275.0, 145.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-28",
                    "maxclass": "newobj",
                    "text": "prepend wfs",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [210.0, 490.0, 85.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-29",
                    "maxclass": "message",
                    "text": "status",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [955.0, 245.0, 50.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-30",
                    "maxclass": "outlet",
                    "index": 1,
                    "comment": "CRAIVE physical feeds, 128-channel MC signal for channels 1 through 128",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [65.0, 605.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-31",
                    "maxclass": "outlet",
                    "index": 2,
                    "comment": "two-channel MC monitor fold-down after WFS, not for CRAIVE playback",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [310.0, 605.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-32",
                    "maxclass": "outlet",
                    "index": 3,
                    "comment": "WFS, source-router, and source-metadata status messages",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [565.0, 605.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-33",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "OUT 1: 128ch CRAIVE WFS",
                    "patching_rect": [30.0, 650.0, 190.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-34",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "OUT 2: stereo MC monitor",
                    "patching_rect": [275.0, 650.0, 190.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-35",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "OUT 3: diagnostics",
                    "patching_rect": [530.0, 650.0, 170.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-36",
                    "maxclass": "comment",
                    "text": "No udpreceive is instantiated here. Branch /qks/spat or /qqt/spat from the system's existing decoded OSC ingress into inlet 2.",
                    "patching_rect": [31.0, 760.0, 780.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-37",
                    "maxclass": "comment",
                    "text": "The loadbang configures speaker/source counts, the exact CRAIVE XYZ layout, official wall orientations, and the reference WFS defaults. It does not move sources.",
                    "patching_rect": [31.0, 790.0, 940.0, 20.0]
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "source": ["obj-3", 0],
                    "destination": ["obj-23", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-4", 0],
                    "destination": ["obj-9", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-5", 0],
                    "destination": ["obj-10", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-9", 0],
                    "destination": ["obj-21", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-9", 1],
                    "destination": ["obj-26", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-9", 2],
                    "destination": ["obj-27", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-10", 0],
                    "destination": ["obj-11", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-10", 1],
                    "destination": ["obj-14", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-10", 2],
                    "destination": ["obj-21", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-10", 3],
                    "destination": ["obj-23", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-10", 4],
                    "destination": ["obj-9", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-10", 5],
                    "destination": ["obj-29", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-10", 6],
                    "destination": ["obj-21", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-11", 0],
                    "destination": ["obj-21", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-12", 0],
                    "destination": ["obj-21", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-13", 0],
                    "destination": ["obj-23", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-14", 1],
                    "destination": ["obj-12", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-14", 0],
                    "destination": ["obj-13", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-15", 0],
                    "destination": ["obj-16", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-16", 2],
                    "destination": ["obj-11", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-16", 1],
                    "destination": ["obj-12", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-16", 0],
                    "destination": ["obj-13", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-17", 0],
                    "destination": ["obj-11", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-19", 0],
                    "destination": ["obj-9", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-21", 0],
                    "destination": ["obj-23", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-23", 0],
                    "destination": ["obj-24", 0],
                    "order": 1
                }
            },
            {
                "patchline": {
                    "source": ["obj-23", 0],
                    "destination": ["obj-30", 0],
                    "order": 0
                }
            },
            {
                "patchline": {
                    "source": ["obj-23", 1],
                    "destination": ["obj-28", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-24", 0],
                    "destination": ["obj-31", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-26", 0],
                    "destination": ["obj-32", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-27", 0],
                    "destination": ["obj-32", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-28", 0],
                    "destination": ["obj-32", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-29", 0],
                    "destination": ["obj-9", 0]
                }
            }
        ],
        "dependency_cache": [
            {
                "name": "qmw_craive_source_router16_v9.js",
                "bootpath": ".",
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1
            },
            {
                "name": "qmw_craive128_layout_v9.maxpat",
                "bootpath": ".",
                "patcherrelativepath": ".",
                "type": "JSON",
                "implicit": 1
            },
            {
                "name": "CRAIVE128.maxpat",
                "bootpath": ".",
                "patcherrelativepath": ".",
                "type": "JSON",
                "implicit": 1
            }
        ],
        "autosave": 0
    }
}
