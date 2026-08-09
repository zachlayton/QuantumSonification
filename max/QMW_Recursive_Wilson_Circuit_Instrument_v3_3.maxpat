{
    "patcher": {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 0,
            "revision": 5,
            "architecture": "x64",
            "modernui": 1
        },
        "classnamespace": "box",
        "rect": [
            70.0,
            70.0,
            1480.0,
            850.0
        ],
        "openinpresentation": 1,
        "gridsize": [
            15.0,
            15.0
        ],
        "boxes": [
            {
                "box": {
                    "id": "title",
                    "maxclass": "comment",
                    "patching_rect": [
                        20.0,
                        15.0,
                        1200.0,
                        30.0
                    ],
                    "text": "QMW \u00b7 RECURSIVE WILSON HEXANY CIRCUIT INSTRUMENT v3.3",
                    "fontsize": 20.0,
                    "presentation": 1,
                    "presentation_rect": [
                        20.0,
                        15.0,
                        1200.0,
                        30.0
                    ]
                }
            },
            {
                "box": {
                    "id": "instructions",
                    "maxclass": "comment",
                    "patching_rect": [
                        20.0,
                        48.0,
                        1380.0,
                        42.0
                    ],
                    "text": "Run examples/qmw_recursive_wilson_instrument_v3.py \u00b7 choose the same MPE MIDI output below \u00b7 pitch-bend range \u00b12 \u00b7 RESEED changes the recursive grammar; INTERVENE changes the live state",
                    "fontsize": 12.0,
                    "presentation": 1,
                    "presentation_rect": [
                        20.0,
                        48.0,
                        1380.0,
                        42.0
                    ]
                }
            },
            {
                "box": {
                    "id": "programmer",
                    "maxclass": "bpatcher",
                    "patching_rect": [
                        20.0,
                        95.0,
                        865.0,
                        675.0
                    ],
                    "name": "QMW_QAC_Circuit_Programmer_Recursive_v3_3.maxpat",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "presentation": 1,
                    "presentation_rect": [
                        20.0,
                        95.0,
                        865.0,
                        675.0
                    ]
                }
            },
            {
                "box": {
                    "id": "controls_label",
                    "maxclass": "comment",
                    "patching_rect": [
                        910.0,
                        95.0,
                        420.0,
                        20.0
                    ],
                    "text": "RECURSION FIELD",
                    "fontsize": 14.0,
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        95.0,
                        420.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "temp_label",
                    "maxclass": "comment",
                    "patching_rect": [
                        910.0,
                        125.0,
                        110.0,
                        20.0
                    ],
                    "text": "temperature 0\u20132",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        125.0,
                        110.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "temp",
                    "maxclass": "flonum",
                    "patching_rect": [
                        1030.0,
                        124.0,
                        70.0,
                        22.0
                    ],
                    "valueof": 0.65,
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "presentation": 1,
                    "presentation_rect": [
                        1030.0,
                        124.0,
                        70.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "temp_pack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1110.0,
                        124.0,
                        205.0,
                        22.0
                    ],
                    "text": "o.pack /qmw/recursive/temperature",
                    "presentation": 1,
                    "presentation_rect": [
                        1110.0,
                        124.0,
                        205.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "seed_label",
                    "maxclass": "comment",
                    "patching_rect": [
                        910.0,
                        157.0,
                        110.0,
                        20.0
                    ],
                    "text": "random seed",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        157.0,
                        110.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "seed",
                    "maxclass": "number",
                    "patching_rect": [
                        1030.0,
                        156.0,
                        70.0,
                        22.0
                    ],
                    "valueof": 23,
                    "minimum": 0,
                    "presentation": 1,
                    "presentation_rect": [
                        1030.0,
                        156.0,
                        70.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "seed_pack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1110.0,
                        156.0,
                        175.0,
                        22.0
                    ],
                    "text": "o.pack /qmw/recursive/seed",
                    "presentation": 1,
                    "presentation_rect": [
                        1110.0,
                        156.0,
                        175.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "depth_label",
                    "maxclass": "comment",
                    "patching_rect": [
                        910.0,
                        189.0,
                        110.0,
                        20.0
                    ],
                    "text": "max depth 1\u2013256",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        189.0,
                        110.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "depth",
                    "maxclass": "number",
                    "patching_rect": [
                        1030.0,
                        188.0,
                        70.0,
                        22.0
                    ],
                    "valueof": 32,
                    "minimum": 1,
                    "maximum": 256,
                    "presentation": 1,
                    "presentation_rect": [
                        1030.0,
                        188.0,
                        70.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "depth_pack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1110.0,
                        188.0,
                        190.0,
                        22.0
                    ],
                    "text": "o.pack /qmw/recursive/max_depth",
                    "presentation": 1,
                    "presentation_rect": [
                        1110.0,
                        188.0,
                        190.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "interval_label",
                    "maxclass": "comment",
                    "patching_rect": [
                        910.0,
                        221.0,
                        110.0,
                        20.0
                    ],
                    "text": "interval ms",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        221.0,
                        110.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "interval",
                    "maxclass": "number",
                    "patching_rect": [
                        1030.0,
                        220.0,
                        70.0,
                        22.0
                    ],
                    "valueof": 240,
                    "minimum": 30,
                    "presentation": 1,
                    "presentation_rect": [
                        1030.0,
                        220.0,
                        70.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "interval_pack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1110.0,
                        220.0,
                        195.0,
                        22.0
                    ],
                    "text": "o.pack /qmw/recursive/interval_ms",
                    "presentation": 1,
                    "presentation_rect": [
                        1110.0,
                        220.0,
                        195.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "control_udp",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1320.0,
                        172.0,
                        150.0,
                        22.0
                    ],
                    "text": "udpsend 127.0.0.1 7403",
                    "presentation": 1,
                    "presentation_rect": [
                        1320.0,
                        172.0,
                        150.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "receive_label",
                    "maxclass": "comment",
                    "patching_rect": [
                        910.0,
                        268.0,
                        470.0,
                        20.0
                    ],
                    "text": "HEXANY STATE \u00b7 six vertices of the 2)4 1-3-5-7 CPS",
                    "fontsize": 14.0,
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        268.0,
                        470.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "receive",
                    "maxclass": "newobj",
                    "patching_rect": [
                        910.0,
                        298.0,
                        105.0,
                        22.0
                    ],
                    "text": "udpreceive 7410",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        298.0,
                        105.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "route_qmw",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1030.0,
                        298.0,
                        115.0,
                        22.0
                    ],
                    "text": "OSC-route /qmw",
                    "presentation": 1,
                    "presentation_rect": [
                        1030.0,
                        298.0,
                        115.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "route_domain",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1160.0,
                        298.0,
                        175.0,
                        22.0
                    ],
                    "text": "OSC-route /recursive /circuit",
                    "presentation": 1,
                    "presentation_rect": [
                        1160.0,
                        298.0,
                        175.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "route_recursive",
                    "maxclass": "newobj",
                    "patching_rect": [
                        910.0,
                        332.0,
                        440.0,
                        22.0
                    ],
                    "text": "OSC-route /wilson_note /status /error /running /seed_accepted",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        332.0,
                        440.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "note_unpack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        910.0,
                        372.0,
                        510.0,
                        22.0
                    ],
                    "text": "unpack i i i i i i f f f i i i i i",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        372.0,
                        510.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "status",
                    "maxclass": "message",
                    "patching_rect": [
                        910.0,
                        410.0,
                        510.0,
                        22.0
                    ],
                    "text": "generation \u00b7 shell probability \u00b7 entropy \u00b7 temperature \u00b7 depth \u00b7 seed \u00b7 revision \u00b7 gates",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        410.0,
                        510.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "error",
                    "maxclass": "message",
                    "patching_rect": [
                        910.0,
                        442.0,
                        510.0,
                        22.0
                    ],
                    "text": "no recursive errors",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        442.0,
                        510.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "running",
                    "maxclass": "toggle",
                    "patching_rect": [
                        1360.0,
                        332.0,
                        24.0,
                        24.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        1360.0,
                        332.0,
                        24.0,
                        24.0
                    ]
                }
            },
            {
                "box": {
                    "id": "running_label",
                    "maxclass": "comment",
                    "patching_rect": [
                        1390.0,
                        334.0,
                        70.0,
                        20.0
                    ],
                    "text": "running",
                    "presentation": 1,
                    "presentation_rect": [
                        1390.0,
                        334.0,
                        70.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "midi_label",
                    "maxclass": "comment",
                    "patching_rect": [
                        910.0,
                        490.0,
                        490.0,
                        20.0
                    ],
                    "text": "MPE OUTPUT \u00b7 channels 2\u20137; phase is timbral CC74",
                    "fontsize": 14.0,
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        490.0,
                        490.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "makenote",
                    "maxclass": "newobj",
                    "patching_rect": [
                        910.0,
                        530.0,
                        150.0,
                        22.0
                    ],
                    "text": "makenote 64 120 2",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        530.0,
                        150.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "noteout",
                    "maxclass": "newobj",
                    "patching_rect": [
                        910.0,
                        570.0,
                        80.0,
                        22.0
                    ],
                    "text": "noteout 1",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        570.0,
                        80.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "xbendout",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1080.0,
                        530.0,
                        75.0,
                        22.0
                    ],
                    "text": "xbendout",
                    "presentation": 1,
                    "presentation_rect": [
                        1080.0,
                        530.0,
                        75.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "midiout",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1080.0,
                        570.0,
                        80.0,
                        22.0
                    ],
                    "text": "midiout",
                    "presentation": 1,
                    "presentation_rect": [
                        1080.0,
                        570.0,
                        80.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "ctlout",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1190.0,
                        530.0,
                        85.0,
                        22.0
                    ],
                    "text": "ctlout 74",
                    "presentation": 1,
                    "presentation_rect": [
                        1190.0,
                        530.0,
                        85.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "midi_note",
                    "maxclass": "comment",
                    "patching_rect": [
                        910.0,
                        615.0,
                        510.0,
                        56.0
                    ],
                    "text": "Pitch = exact Wilson product ratio via MIDI note + 14-bit bend.\nVelocity = \u221a(conditional probability). CC74 = relative quantum phase.\nThe exchange recursion preserves the weight-two Hexany shell.",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        615.0,
                        510.0,
                        56.0
                    ]
                }
            },
            {
                "box": {
                    "id": "print",
                    "maxclass": "newobj",
                    "patching_rect": [
                        910.0,
                        700.0,
                        165.0,
                        22.0
                    ],
                    "text": "print QMW_RECURSIVE_WILSON",
                    "presentation": 1,
                    "presentation_rect": [
                        910.0,
                        700.0,
                        165.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "default_temp",
                    "maxclass": "newobj",
                    "patching_rect": [
                        20.0,
                        790.0,
                        95.0,
                        22.0
                    ],
                    "text": "loadmess 0.65",
                    "hidden": 1,
                    "presentation": 1,
                    "presentation_rect": [
                        20.0,
                        790.0,
                        95.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "default_seed",
                    "maxclass": "newobj",
                    "patching_rect": [
                        125.0,
                        790.0,
                        90.0,
                        22.0
                    ],
                    "text": "loadmess 23",
                    "hidden": 1,
                    "presentation": 1,
                    "presentation_rect": [
                        125.0,
                        790.0,
                        90.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "default_depth",
                    "maxclass": "newobj",
                    "patching_rect": [
                        225.0,
                        790.0,
                        90.0,
                        22.0
                    ],
                    "text": "loadmess 32",
                    "hidden": 1,
                    "presentation": 1,
                    "presentation_rect": [
                        225.0,
                        790.0,
                        90.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "default_interval",
                    "maxclass": "newobj",
                    "patching_rect": [
                        325.0,
                        790.0,
                        100.0,
                        22.0
                    ],
                    "text": "loadmess 240",
                    "hidden": 1,
                    "presentation": 1,
                    "presentation_rect": [
                        325.0,
                        790.0,
                        100.0,
                        22.0
                    ]
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "source": [
                        "temp",
                        0
                    ],
                    "destination": [
                        "temp_pack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "temp_pack",
                        0
                    ],
                    "destination": [
                        "control_udp",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "seed",
                        0
                    ],
                    "destination": [
                        "seed_pack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "seed_pack",
                        0
                    ],
                    "destination": [
                        "control_udp",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "depth",
                        0
                    ],
                    "destination": [
                        "depth_pack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "depth_pack",
                        0
                    ],
                    "destination": [
                        "control_udp",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "interval",
                        0
                    ],
                    "destination": [
                        "interval_pack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "interval_pack",
                        0
                    ],
                    "destination": [
                        "control_udp",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "default_temp",
                        0
                    ],
                    "destination": [
                        "temp",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "default_seed",
                        0
                    ],
                    "destination": [
                        "seed",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "default_depth",
                        0
                    ],
                    "destination": [
                        "depth",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "default_interval",
                        0
                    ],
                    "destination": [
                        "interval",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "receive",
                        0
                    ],
                    "destination": [
                        "route_qmw",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "route_qmw",
                        0
                    ],
                    "destination": [
                        "route_domain",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "route_domain",
                        0
                    ],
                    "destination": [
                        "route_recursive",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "route_recursive",
                        0
                    ],
                    "destination": [
                        "note_unpack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "route_recursive",
                        1
                    ],
                    "destination": [
                        "status",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "route_recursive",
                        2
                    ],
                    "destination": [
                        "error",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "route_recursive",
                        3
                    ],
                    "destination": [
                        "running",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "route_recursive",
                        0
                    ],
                    "destination": [
                        "print",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "route_recursive",
                        1
                    ],
                    "destination": [
                        "print",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "note_unpack",
                        3
                    ],
                    "destination": [
                        "makenote",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "note_unpack",
                        4
                    ],
                    "destination": [
                        "makenote",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "note_unpack",
                        5
                    ],
                    "destination": [
                        "makenote",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "note_unpack",
                        13
                    ],
                    "destination": [
                        "makenote",
                        3
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "makenote",
                        0
                    ],
                    "destination": [
                        "noteout",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "makenote",
                        1
                    ],
                    "destination": [
                        "noteout",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "note_unpack",
                        13
                    ],
                    "destination": [
                        "noteout",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "note_unpack",
                        11
                    ],
                    "destination": [
                        "xbendout",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "note_unpack",
                        13
                    ],
                    "destination": [
                        "xbendout",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "xbendout",
                        0
                    ],
                    "destination": [
                        "midiout",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "note_unpack",
                        12
                    ],
                    "destination": [
                        "ctlout",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "note_unpack",
                        13
                    ],
                    "destination": [
                        "ctlout",
                        2
                    ]
                }
            }
        ],
        "dependency_cache": [
            {
                "name": "QMW_QAC_Circuit_Programmer_Recursive_v3_3.maxpat",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "JSON",
                "implicit": 1
            },
            {
                "name": "OSC-route.mxo",
                "type": "iLaX"
            },
            {
                "name": "o.pack.mxo",
                "type": "iLaX"
            }
        ],
        "autosave": 0
    }
}
