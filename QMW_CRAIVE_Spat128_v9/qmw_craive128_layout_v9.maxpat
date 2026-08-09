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
        "rect": [60.0, 90.0, 900.0, 470.0],
        "bglocked": 0,
        "openinpresentation": 0,
        "default_fontsize": 12.0,
        "default_fontface": 0,
        "default_fontname": "Arial",
        "gridonopen": 1,
        "gridsize": [15.0, 15.0],
        "gridsnaponopen": 1,
        "objectsnaponopen": 1,
        "description": "Deterministic loader for the official CRAIVE 128-speaker XYZ and orientation messages.",
        "digest": "Emits CRAIVE perimeter geometry followed by the reference inward-facing direction groups.",
        "tags": "CRAIVE Spat WFS speaker layout 128",
        "boxes": [
            {
                "box": {
                    "id": "obj-1",
                    "maxclass": "comment",
                    "fontsize": 20.0,
                    "fontface": 1,
                    "text": "CRAIVE 128-Speaker Layout — v9 loader",
                    "patching_rect": [30.0, 20.0, 520.0, 29.0]
                }
            },
            {
                "box": {
                    "id": "obj-2",
                    "maxclass": "comment",
                    "text": "The vendor abstraction emits XYZ from its inlet; this wrapper also emits its four official wall-direction groups on every bang.",
                    "patching_rect": [31.0, 53.0, 790.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-3",
                    "maxclass": "inlet",
                    "index": 1,
                    "comment": "bang to emit the complete CRAIVE 128 layout",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": ["bang"],
                    "patching_rect": [55.0, 105.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-4",
                    "maxclass": "newobj",
                    "text": "t b b b b b",
                    "numinlets": 1,
                    "numoutlets": 5,
                    "outlettype": ["bang", "bang", "bang", "bang", "bang"],
                    "patching_rect": [55.0, 160.0, 88.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-5",
                    "maxclass": "newobj",
                    "text": "CRAIVE128",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [610.0, 225.0, 78.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-6",
                    "maxclass": "message",
                    "text": "/speaker/[1-18]/direction/xyz 0 1 0",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [55.0, 225.0, 225.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-7",
                    "maxclass": "message",
                    "text": "/speaker/[24-54]/direction/xyz 1 0 0",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [55.0, 260.0, 235.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-8",
                    "maxclass": "message",
                    "text": "/speaker/[62-85]/direction/xyz 0 -1 0",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [55.0, 295.0, 240.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-9",
                    "maxclass": "message",
                    "text": "/speaker/[94-123]/direction/xyz -1 0 0",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [55.0, 330.0, 250.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-10",
                    "maxclass": "outlet",
                    "index": 1,
                    "comment": "official CRAIVE speaker geometry and orientation messages",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [430.0, 390.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-11",
                    "maxclass": "comment",
                    "text": "Channels 129–134 (ceiling HoA) and 135–136 (frontal stereo) are deliberately outside this 128-channel WFS renderer.",
                    "patching_rect": [31.0, 438.0, 790.0, 20.0]
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "source": ["obj-3", 0],
                    "destination": ["obj-4", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-4", 4],
                    "destination": ["obj-5", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-4", 3],
                    "destination": ["obj-6", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-4", 2],
                    "destination": ["obj-7", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-4", 1],
                    "destination": ["obj-8", 0]
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
                    "source": ["obj-6", 0],
                    "destination": ["obj-10", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-7", 0],
                    "destination": ["obj-10", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-8", 0],
                    "destination": ["obj-10", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-9", 0],
                    "destination": ["obj-10", 0]
                }
            }
        ],
        "dependency_cache": [
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
