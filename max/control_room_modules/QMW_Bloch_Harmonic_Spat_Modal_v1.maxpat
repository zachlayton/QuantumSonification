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
        "rect": [
            80.0,
            80.0,
            980.0,
            820.0
        ],
        "openinpresentation": 0,
        "boxes": [
            {
                "box": {
                    "id": "obj-1",
                    "maxclass": "comment",
                    "patching_rect": [
                        25.0,
                        20.0,
                        760.0,
                        28.0
                    ],
                    "text": "QMW BLOCH HARMONICS \u2192 SPAT5 + MODAL REVERB v1",
                    "fontsize": 18.0,
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-2",
                    "maxclass": "comment",
                    "patching_rect": [
                        25.0,
                        52.0,
                        920.0,
                        36.0
                    ],
                    "text": "Degree 1 steers four Spat sources. Degrees 2\u20133 control bounded FDN resonance, decay, damping, spectral tilt, warp, and mode weights.",
                    "linecount": 2
                }
            },
            {
                "box": {
                    "id": "obj-3",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        105.0,
                        100.0,
                        22.0
                    ],
                    "text": "r qmw.osc.raw"
                }
            },
            {
                "box": {
                    "id": "obj-4",
                    "maxclass": "newobj",
                    "patching_rect": [
                        145.0,
                        105.0,
                        100.0,
                        22.0
                    ],
                    "text": "OSC-route /qmw"
                }
            },
            {
                "box": {
                    "id": "obj-5",
                    "maxclass": "newobj",
                    "patching_rect": [
                        265.0,
                        105.0,
                        135.0,
                        22.0
                    ],
                    "text": "OSC-route /acoustics"
                }
            },
            {
                "box": {
                    "id": "obj-6",
                    "maxclass": "newobj",
                    "patching_rect": [
                        420.0,
                        105.0,
                        205.0,
                        22.0
                    ],
                    "text": "OSC-route /spat /reverb /modal"
                }
            },
            {
                "box": {
                    "id": "obj-7",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        165.0,
                        118.0,
                        22.0
                    ],
                    "text": "OSC-route /source"
                }
            },
            {
                "box": {
                    "id": "obj-8",
                    "maxclass": "newobj",
                    "patching_rect": [
                        165.0,
                        165.0,
                        190.0,
                        22.0
                    ],
                    "text": "OSC-route /1 /2 /3 /4"
                }
            },
            {
                "box": {
                    "id": "obj-9",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        430.0,
                        560.0,
                        22.0
                    ],
                    "text": "spat5.oper @initwith \"/source/number 4, /source/*/aperture/visible 1, /source/*/constraint/circular 0\"",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-10",
                    "maxclass": "newobj",
                    "patching_rect": [
                        610.0,
                        430.0,
                        125.0,
                        22.0
                    ],
                    "text": "s qmw.spat.control"
                }
            },
            {
                "box": {
                    "id": "obj-11",
                    "maxclass": "outlet",
                    "patching_rect": [
                        760.0,
                        430.0,
                        30.0,
                        30.0
                    ],
                    "comment": "Spat5 OSC control"
                }
            },
            {
                "box": {
                    "id": "obj-12",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        210.0,
                        225.0,
                        22.0
                    ],
                    "text": "OSC-route /aed /aperture /spread"
                }
            },
            {
                "box": {
                    "id": "obj-13",
                    "maxclass": "newobj",
                    "patching_rect": [
                        275.0,
                        210.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/1/aed"
                }
            },
            {
                "box": {
                    "id": "obj-14",
                    "maxclass": "newobj",
                    "patching_rect": [
                        480.0,
                        210.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/1/aperture"
                }
            },
            {
                "box": {
                    "id": "obj-15",
                    "maxclass": "newobj",
                    "patching_rect": [
                        685.0,
                        210.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/1/spread"
                }
            },
            {
                "box": {
                    "id": "obj-16",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        258.0,
                        225.0,
                        22.0
                    ],
                    "text": "OSC-route /aed /aperture /spread"
                }
            },
            {
                "box": {
                    "id": "obj-17",
                    "maxclass": "newobj",
                    "patching_rect": [
                        275.0,
                        258.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/2/aed"
                }
            },
            {
                "box": {
                    "id": "obj-18",
                    "maxclass": "newobj",
                    "patching_rect": [
                        480.0,
                        258.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/2/aperture"
                }
            },
            {
                "box": {
                    "id": "obj-19",
                    "maxclass": "newobj",
                    "patching_rect": [
                        685.0,
                        258.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/2/spread"
                }
            },
            {
                "box": {
                    "id": "obj-20",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        306.0,
                        225.0,
                        22.0
                    ],
                    "text": "OSC-route /aed /aperture /spread"
                }
            },
            {
                "box": {
                    "id": "obj-21",
                    "maxclass": "newobj",
                    "patching_rect": [
                        275.0,
                        306.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/3/aed"
                }
            },
            {
                "box": {
                    "id": "obj-22",
                    "maxclass": "newobj",
                    "patching_rect": [
                        480.0,
                        306.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/3/aperture"
                }
            },
            {
                "box": {
                    "id": "obj-23",
                    "maxclass": "newobj",
                    "patching_rect": [
                        685.0,
                        306.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/3/spread"
                }
            },
            {
                "box": {
                    "id": "obj-24",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        354.0,
                        225.0,
                        22.0
                    ],
                    "text": "OSC-route /aed /aperture /spread"
                }
            },
            {
                "box": {
                    "id": "obj-25",
                    "maxclass": "newobj",
                    "patching_rect": [
                        275.0,
                        354.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/4/aed"
                }
            },
            {
                "box": {
                    "id": "obj-26",
                    "maxclass": "newobj",
                    "patching_rect": [
                        480.0,
                        354.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/4/aperture"
                }
            },
            {
                "box": {
                    "id": "obj-27",
                    "maxclass": "newobj",
                    "patching_rect": [
                        685.0,
                        354.0,
                        185.0,
                        22.0
                    ],
                    "text": "prepend /source/4/spread"
                }
            },
            {
                "box": {
                    "id": "obj-28",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        510.0,
                        275.0,
                        22.0
                    ],
                    "text": "OSC-route /resonance /decay /damping"
                }
            },
            {
                "box": {
                    "id": "obj-29",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        555.0,
                        245.0,
                        22.0
                    ],
                    "text": "OSC-route /tilt /warp /weights"
                }
            },
            {
                "box": {
                    "id": "obj-30",
                    "maxclass": "newobj",
                    "patching_rect": [
                        725.0,
                        535.0,
                        190.0,
                        22.0
                    ],
                    "text": "s qmw.acoustic.modal.control"
                }
            },
            {
                "box": {
                    "id": "obj-31",
                    "maxclass": "newobj",
                    "patching_rect": [
                        330.0,
                        510.0,
                        130.0,
                        22.0
                    ],
                    "text": "prepend resonance"
                }
            },
            {
                "box": {
                    "id": "obj-32",
                    "maxclass": "newobj",
                    "patching_rect": [
                        460.0,
                        510.0,
                        130.0,
                        22.0
                    ],
                    "text": "prepend decay"
                }
            },
            {
                "box": {
                    "id": "obj-33",
                    "maxclass": "newobj",
                    "patching_rect": [
                        570.0,
                        510.0,
                        130.0,
                        22.0
                    ],
                    "text": "prepend damping"
                }
            },
            {
                "box": {
                    "id": "obj-34",
                    "maxclass": "newobj",
                    "patching_rect": [
                        300.0,
                        555.0,
                        130.0,
                        22.0
                    ],
                    "text": "prepend spectral_tilt"
                }
            },
            {
                "box": {
                    "id": "obj-35",
                    "maxclass": "newobj",
                    "patching_rect": [
                        455.0,
                        555.0,
                        130.0,
                        22.0
                    ],
                    "text": "prepend modal_warp"
                }
            },
            {
                "box": {
                    "id": "obj-36",
                    "maxclass": "newobj",
                    "patching_rect": [
                        600.0,
                        555.0,
                        130.0,
                        22.0
                    ],
                    "text": "prepend modal_weights"
                }
            },
            {
                "box": {
                    "id": "obj-37",
                    "maxclass": "comment",
                    "patching_rect": [
                        25.0,
                        620.0,
                        860.0,
                        54.0
                    ],
                    "text": "Connect r qmw.spat.control to spat5.spat~ (or use the outlet). The modal branch is mirrored to qmw.acoustic.modal.control. Feedback gains remain clipped to each renderer's established stability ceiling.",
                    "linecount": 3
                }
            },
            {
                "box": {
                    "id": "obj-38",
                    "maxclass": "inlet",
                    "patching_rect": [
                        25.0,
                        690.0,
                        30.0,
                        30.0
                    ],
                    "comment": "Spat source 1",
                    "index": 1,
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-39",
                    "maxclass": "inlet",
                    "patching_rect": [
                        95.0,
                        690.0,
                        30.0,
                        30.0
                    ],
                    "comment": "Spat source 2",
                    "index": 2,
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-40",
                    "maxclass": "inlet",
                    "patching_rect": [
                        165.0,
                        690.0,
                        30.0,
                        30.0
                    ],
                    "comment": "Spat source 3",
                    "index": 3,
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-41",
                    "maxclass": "inlet",
                    "patching_rect": [
                        235.0,
                        690.0,
                        30.0,
                        30.0
                    ],
                    "comment": "Spat source 4",
                    "index": 4,
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-42",
                    "maxclass": "newobj",
                    "patching_rect": [
                        330.0,
                        690.0,
                        590.0,
                        22.0
                    ],
                    "text": "spat5.spat~ @inputs 4 @internals 8 @outputs 2 @rooms 1 @initwith \"/panning/type binaural\"",
                    "numinlets": 4,
                    "numoutlets": 3,
                    "outlettype": [
                        "signal",
                        "signal",
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-43",
                    "maxclass": "outlet",
                    "patching_rect": [
                        420.0,
                        750.0,
                        30.0,
                        30.0
                    ],
                    "comment": "Binaural left",
                    "index": 1,
                    "numinlets": 1,
                    "numoutlets": 0
                }
            },
            {
                "box": {
                    "id": "obj-44",
                    "maxclass": "outlet",
                    "patching_rect": [
                        490.0,
                        750.0,
                        30.0,
                        30.0
                    ],
                    "comment": "Binaural right",
                    "index": 2,
                    "numinlets": 1,
                    "numoutlets": 0
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "source": [
                        "obj-3",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-4",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-5",
                        0
                    ],
                    "destination": [
                        "obj-6",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-6",
                        0
                    ],
                    "destination": [
                        "obj-7",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-7",
                        0
                    ],
                    "destination": [
                        "obj-8",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-9",
                        0
                    ],
                    "destination": [
                        "obj-11",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-8",
                        0
                    ],
                    "destination": [
                        "obj-12",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-12",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-13",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-13",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-12",
                        1
                    ],
                    "destination": [
                        "obj-14",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-14",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-14",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-12",
                        2
                    ],
                    "destination": [
                        "obj-15",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-15",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-15",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-8",
                        1
                    ],
                    "destination": [
                        "obj-16",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-16",
                        0
                    ],
                    "destination": [
                        "obj-17",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-17",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-17",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-16",
                        1
                    ],
                    "destination": [
                        "obj-18",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-18",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-18",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-16",
                        2
                    ],
                    "destination": [
                        "obj-19",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-19",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-19",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-8",
                        2
                    ],
                    "destination": [
                        "obj-20",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-20",
                        0
                    ],
                    "destination": [
                        "obj-21",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-21",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-21",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-20",
                        1
                    ],
                    "destination": [
                        "obj-22",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-22",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-22",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-20",
                        2
                    ],
                    "destination": [
                        "obj-23",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-23",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-23",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-8",
                        3
                    ],
                    "destination": [
                        "obj-24",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-24",
                        0
                    ],
                    "destination": [
                        "obj-25",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-25",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-25",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-24",
                        1
                    ],
                    "destination": [
                        "obj-26",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-26",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-26",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-24",
                        2
                    ],
                    "destination": [
                        "obj-27",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-27",
                        0
                    ],
                    "destination": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-27",
                        0
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-6",
                        1
                    ],
                    "destination": [
                        "obj-28",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-6",
                        2
                    ],
                    "destination": [
                        "obj-29",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-28",
                        0
                    ],
                    "destination": [
                        "obj-31",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-31",
                        0
                    ],
                    "destination": [
                        "obj-30",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-28",
                        1
                    ],
                    "destination": [
                        "obj-32",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-32",
                        0
                    ],
                    "destination": [
                        "obj-30",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-28",
                        2
                    ],
                    "destination": [
                        "obj-33",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-33",
                        0
                    ],
                    "destination": [
                        "obj-30",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-29",
                        0
                    ],
                    "destination": [
                        "obj-34",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-34",
                        0
                    ],
                    "destination": [
                        "obj-30",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-29",
                        1
                    ],
                    "destination": [
                        "obj-35",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-35",
                        0
                    ],
                    "destination": [
                        "obj-30",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-29",
                        2
                    ],
                    "destination": [
                        "obj-36",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-36",
                        0
                    ],
                    "destination": [
                        "obj-30",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-38",
                        0
                    ],
                    "destination": [
                        "obj-42",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-39",
                        0
                    ],
                    "destination": [
                        "obj-42",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-40",
                        0
                    ],
                    "destination": [
                        "obj-42",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-41",
                        0
                    ],
                    "destination": [
                        "obj-42",
                        3
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-9",
                        0
                    ],
                    "destination": [
                        "obj-42",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-42",
                        0
                    ],
                    "destination": [
                        "obj-43",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-42",
                        1
                    ],
                    "destination": [
                        "obj-44",
                        0
                    ]
                }
            }
        ],
        "dependency_cache": [
            {
                "name": "OSC-route.mxo",
                "type": "iLaX"
            },
            {
                "name": "spat5.oper.mxo",
                "type": "iLaX"
            },
            {
                "name": "spat5.spat~.mxo",
                "type": "iLaX"
            }
        ],
        "autosave": 0
    }
}
