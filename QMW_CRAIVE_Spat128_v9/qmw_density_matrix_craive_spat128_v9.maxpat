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
        "rect": [25.0, 40.0, 1580.0, 980.0],
        "bglocked": 0,
        "openinpresentation": 0,
        "default_fontsize": 12.0,
        "default_fontface": 0,
        "default_fontname": "Arial",
        "gridonopen": 1,
        "gridsize": [15.0, 15.0],
        "gridsnaponopen": 1,
        "objectsnaponopen": 1,
        "description": "Complete QMW v9 wrapper: sixteen-lane complex density-matrix feedback followed by CRAIVE 128-channel WFS.",
        "digest": "Preserves the full v8 feedback state and spatializes all sixteen unsummed basis streams with the exact CRAIVE speaker geometry.",
        "tags": "QMW density matrix feedback CRAIVE IRCAM Spat WFS MC v9",
        "boxes": [
            {
                "box": {
                    "id": "obj-1",
                    "maxclass": "comment",
                    "fontsize": 24.0,
                    "fontface": 1,
                    "text": "QMW Density-Matrix Feedback → CRAIVE Spat 128 — v9",
                    "patching_rect": [30.0, 18.0, 760.0, 34.0]
                }
            },
            {
                "box": {
                    "id": "obj-2",
                    "maxclass": "comment",
                    "fontsize": 13.0,
                    "text": "Full complex rho coupling remains inside the sixteen resonator branches; only the selected 16ch state enters the WFS stage.",
                    "patching_rect": [31.0, 55.0, 910.0, 21.0]
                }
            },
            {
                "box": {
                    "id": "obj-3",
                    "maxclass": "inlet",
                    "index": 1,
                    "comment": "raw 16-channel MC resonator output",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": ["multichannelsignal"],
                    "patching_rect": [55.0, 120.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-4",
                    "maxclass": "inlet",
                    "index": 2,
                    "comment": "Re(rho), 256 row-major values",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [220.0, 120.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-5",
                    "maxclass": "inlet",
                    "index": 3,
                    "comment": "Im(rho), 256 row-major values",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [375.0, 120.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-6",
                    "maxclass": "inlet",
                    "index": 4,
                    "comment": "sixteen projection phases in radians",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [530.0, 120.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-7",
                    "maxclass": "inlet",
                    "index": 5,
                    "comment": "sixteen feedback gains",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [685.0, 120.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-8",
                    "maxclass": "inlet",
                    "index": 6,
                    "comment": "sixteen feedback delay times in milliseconds",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [840.0, 120.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-9",
                    "maxclass": "inlet",
                    "index": 7,
                    "comment": "feedback control messages",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [995.0, 120.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-10",
                    "maxclass": "inlet",
                    "index": 8,
                    "comment": "voice azimuth elevation distance spread or supported OSC spatial message",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [1160.0, 120.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-11",
                    "maxclass": "inlet",
                    "index": 9,
                    "comment": "CRAIVE renderer control messages",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [1330.0, 120.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-12",
                    "maxclass": "comment",
                    "text": "raw 16ch",
                    "patching_rect": [30.0, 158.0, 80.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-13",
                    "maxclass": "comment",
                    "text": "Re(rho)",
                    "patching_rect": [204.0, 158.0, 70.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-14",
                    "maxclass": "comment",
                    "text": "Im(rho)",
                    "patching_rect": [359.0, 158.0, 70.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-15",
                    "maxclass": "comment",
                    "text": "phase",
                    "patching_rect": [520.0, 158.0, 60.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-16",
                    "maxclass": "comment",
                    "text": "gain",
                    "patching_rect": [678.0, 158.0, 55.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-17",
                    "maxclass": "comment",
                    "text": "delay",
                    "patching_rect": [832.0, 158.0, 55.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-18",
                    "maxclass": "comment",
                    "text": "feedback ctl",
                    "patching_rect": [972.0, 158.0, 90.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-19",
                    "maxclass": "comment",
                    "text": "spatial",
                    "patching_rect": [1148.0, 158.0, 70.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-20",
                    "maxclass": "comment",
                    "text": "renderer ctl",
                    "patching_rect": [1306.0, 158.0, 95.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-21",
                    "maxclass": "newobj",
                    "text": "qmw_density_matrix_resonator_feedback16_mc_v1",
                    "numinlets": 7,
                    "numoutlets": 6,
                    "outlettype": [
                        "multichannelsignal",
                        "multichannelsignal",
                        "multichannelsignal",
                        "multichannelsignal",
                        "multichannelsignal",
                        ""
                    ],
                    "patching_rect": [250.0, 245.0, 340.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-22",
                    "maxclass": "newobj",
                    "text": "qmw_craive_spat128_renderer16_v9",
                    "numinlets": 3,
                    "numoutlets": 3,
                    "outlettype": ["multichannelsignal", "multichannelsignal", ""],
                    "patching_rect": [760.0, 380.0, 250.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-23",
                    "maxclass": "newobj",
                    "text": "prepend feedback",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [450.0, 570.0, 115.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-24",
                    "maxclass": "newobj",
                    "text": "prepend spatial",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [""],
                    "patching_rect": [1020.0, 570.0, 105.0, 22.0]
                }
            },
            {
                "box": {
                    "id": "obj-25",
                    "maxclass": "outlet",
                    "index": 1,
                    "comment": "CRAIVE channels 1 through 128 as a 128-channel MC signal",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [700.0, 685.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-26",
                    "maxclass": "outlet",
                    "index": 2,
                    "comment": "two-channel MC monitoring fold-down after WFS",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [850.0, 685.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-27",
                    "maxclass": "outlet",
                    "index": 3,
                    "comment": "selected 16-channel state entering the renderer",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [55.0, 685.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-28",
                    "maxclass": "outlet",
                    "index": 4,
                    "comment": "coupled state, 16-channel MC signal",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [160.0, 685.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-29",
                    "maxclass": "outlet",
                    "index": 5,
                    "comment": "feedback return, 16-channel MC signal",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [265.0, 685.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-30",
                    "maxclass": "outlet",
                    "index": 6,
                    "comment": "real component of rho times analytic state, 16-channel MC signal",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [370.0, 685.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-31",
                    "maxclass": "outlet",
                    "index": 7,
                    "comment": "imaginary component of rho times analytic state, 16-channel MC signal",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [475.0, 685.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-32",
                    "maxclass": "outlet",
                    "index": 8,
                    "comment": "feedback and spatial renderer diagnostics",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [1100.0, 685.0, 30.0, 30.0]
                }
            },
            {
                "box": {
                    "id": "obj-33",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "selected",
                    "patching_rect": [37.0, 725.0, 70.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-34",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "coupled",
                    "patching_rect": [142.0, 725.0, 70.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-35",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "feedback",
                    "patching_rect": [247.0, 725.0, 75.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-36",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "y real",
                    "patching_rect": [357.0, 725.0, 65.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-37",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "y imag",
                    "patching_rect": [462.0, 725.0, 65.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-38",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "128ch CRAIVE",
                    "patching_rect": [665.0, 725.0, 120.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-39",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "stereo monitor",
                    "patching_rect": [815.0, 725.0, 120.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-40",
                    "maxclass": "comment",
                    "fontface": 1,
                    "text": "diagnostics",
                    "patching_rect": [1069.0, 725.0, 100.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-41",
                    "maxclass": "comment",
                    "text": "Basis ordering is unchanged: MC channels 1...16 correspond to |0000>...|1111>. No pitch quantization or pre-Spat fold-down is introduced.",
                    "patching_rect": [31.0, 805.0, 900.0, 20.0]
                }
            },
            {
                "box": {
                    "id": "obj-42",
                    "maxclass": "comment",
                    "text": "Connect outlet 1 to CRAIVE's 128-channel hardware sink. Use outlet 2 only for off-room monitoring.",
                    "patching_rect": [31.0, 835.0, 720.0, 20.0]
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "source": ["obj-3", 0],
                    "destination": ["obj-21", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-4", 0],
                    "destination": ["obj-21", 1]
                }
            },
            {
                "patchline": {
                    "source": ["obj-5", 0],
                    "destination": ["obj-21", 2]
                }
            },
            {
                "patchline": {
                    "source": ["obj-6", 0],
                    "destination": ["obj-21", 3]
                }
            },
            {
                "patchline": {
                    "source": ["obj-7", 0],
                    "destination": ["obj-21", 4]
                }
            },
            {
                "patchline": {
                    "source": ["obj-8", 0],
                    "destination": ["obj-21", 5]
                }
            },
            {
                "patchline": {
                    "source": ["obj-9", 0],
                    "destination": ["obj-21", 6]
                }
            },
            {
                "patchline": {
                    "source": ["obj-10", 0],
                    "destination": ["obj-22", 1]
                }
            },
            {
                "patchline": {
                    "source": ["obj-11", 0],
                    "destination": ["obj-22", 2]
                }
            },
            {
                "patchline": {
                    "source": ["obj-21", 0],
                    "destination": ["obj-22", 0],
                    "order": 0
                }
            },
            {
                "patchline": {
                    "source": ["obj-21", 0],
                    "destination": ["obj-27", 0],
                    "order": 1
                }
            },
            {
                "patchline": {
                    "source": ["obj-21", 1],
                    "destination": ["obj-28", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-21", 2],
                    "destination": ["obj-29", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-21", 3],
                    "destination": ["obj-30", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-21", 4],
                    "destination": ["obj-31", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-21", 5],
                    "destination": ["obj-23", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-22", 0],
                    "destination": ["obj-25", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-22", 1],
                    "destination": ["obj-26", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-22", 2],
                    "destination": ["obj-24", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-23", 0],
                    "destination": ["obj-32", 0]
                }
            },
            {
                "patchline": {
                    "source": ["obj-24", 0],
                    "destination": ["obj-32", 0]
                }
            }
        ],
        "dependency_cache": [
            {
                "name": "qmw_density_matrix_resonator_feedback16_mc_v1.maxpat",
                "bootpath": ".",
                "patcherrelativepath": ".",
                "type": "JSON",
                "implicit": 1
            },
            {
                "name": "qmw_craive_spat128_renderer16_v9.maxpat",
                "bootpath": ".",
                "patcherrelativepath": ".",
                "type": "JSON",
                "implicit": 1
            }
        ],
        "autosave": 0
    }
}
