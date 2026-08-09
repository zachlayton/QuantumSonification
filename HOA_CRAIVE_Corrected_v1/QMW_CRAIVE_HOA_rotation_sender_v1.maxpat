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
            100,
            100,
            860,
            470
        ],
        "openinpresentation": 0,
        "default_fontsize": 12,
        "default_fontface": 0,
        "default_fontname": "Arial",
        "gridonopen": 1,
        "gridsize": [
            15,
            15
        ],
        "boxes": [
            {
                "box": {
                    "id": "title",
                    "maxclass": "comment",
                    "text": "QMW → CRAIVE HOA ROTATION SENDER",
                    "patching_rect": [
                        25,
                        20,
                        550,
                        28
                    ],
                    "fontsize": 18,
                    "linecount": 1
                }
            },
            {
                "box": {
                    "id": "subtitle",
                    "maxclass": "comment",
                    "text": "Runs on your computer. Sends only low-rate orientation control; all audio stays on the 16-channel analog snake.",
                    "patching_rect": [
                        25,
                        55,
                        760,
                        38
                    ],
                    "fontsize": 12,
                    "linecount": 2
                }
            },
            {
                "box": {
                    "id": "yaw-label",
                    "maxclass": "comment",
                    "text": "yaw (degrees)",
                    "patching_rect": [
                        25,
                        120,
                        110,
                        20
                    ],
                    "fontsize": 11,
                    "linecount": 1
                }
            },
            {
                "box": {
                    "id": "pitch-label",
                    "maxclass": "comment",
                    "text": "pitch (degrees)",
                    "patching_rect": [
                        175,
                        120,
                        110,
                        20
                    ],
                    "fontsize": 11,
                    "linecount": 1
                }
            },
            {
                "box": {
                    "id": "roll-label",
                    "maxclass": "comment",
                    "text": "roll (degrees)",
                    "patching_rect": [
                        325,
                        120,
                        110,
                        20
                    ],
                    "fontsize": 11,
                    "linecount": 1
                }
            },
            {
                "box": {
                    "id": "yaw",
                    "maxclass": "flonum",
                    "patching_rect": [
                        25,
                        145,
                        100,
                        22
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "minimum": -180,
                    "maximum": 180,
                    "format": 6,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "pitch",
                    "maxclass": "flonum",
                    "patching_rect": [
                        175,
                        145,
                        100,
                        22
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "minimum": -90,
                    "maximum": 90,
                    "format": 6,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "roll",
                    "maxclass": "flonum",
                    "patching_rect": [
                        325,
                        145,
                        100,
                        22
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "minimum": -180,
                    "maximum": 180,
                    "format": 6,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "pak",
                    "maxclass": "newobj",
                    "text": "pak 0. 0. 0.",
                    "patching_rect": [
                        25,
                        195,
                        240,
                        22
                    ],
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        "list"
                    ]
                }
            },
            {
                "box": {
                    "id": "speedlim",
                    "maxclass": "newobj",
                    "text": "speedlim 33",
                    "patching_rect": [
                        25,
                        235,
                        90,
                        22
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "osc-message",
                    "maxclass": "message",
                    "text": "/qmw/craive/hoa/ypr $1 $2 $3",
                    "patching_rect": [
                        25,
                        275,
                        240,
                        22
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "udp-send",
                    "maxclass": "newobj",
                    "text": "spat5.osc.udpsend @ip 127.0.0.1 @port 7475",
                    "patching_rect": [
                        25,
                        325,
                        320,
                        22
                    ],
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
                    "id": "refresh-toggle",
                    "maxclass": "toggle",
                    "patching_rect": [
                        475,
                        145,
                        26,
                        26
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "int"
                    ]
                }
            },
            {
                "box": {
                    "id": "refresh-metro",
                    "maxclass": "newobj",
                    "text": "qmetro 100",
                    "patching_rect": [
                        475,
                        195,
                        78,
                        22
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "refresh-init",
                    "maxclass": "newobj",
                    "text": "loadmess 1",
                    "patching_rect": [
                        475,
                        105,
                        78,
                        22
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "center",
                    "maxclass": "message",
                    "text": "0. 0. 0.",
                    "patching_rect": [
                        325,
                        195,
                        90,
                        22
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "center-unpack",
                    "maxclass": "newobj",
                    "text": "unpack 0. 0. 0.",
                    "patching_rect": [
                        325,
                        235,
                        125,
                        22
                    ],
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "float",
                        "float",
                        "float"
                    ]
                }
            },
            {
                "box": {
                    "id": "center-label",
                    "maxclass": "comment",
                    "text": "center field",
                    "patching_rect": [
                        325,
                        220,
                        90,
                        20
                    ],
                    "fontsize": 11,
                    "linecount": 1
                }
            },
            {
                "box": {
                    "id": "ip-warning",
                    "maxclass": "comment",
                    "text": "IMPORTANT: replace 127.0.0.1 in the spat5.osc.udpsend object with the CRAIVE computer’s shared-network IPv4 address.",
                    "patching_rect": [
                        380,
                        300,
                        395,
                        50
                    ],
                    "fontsize": 12,
                    "linecount": 2
                }
            },
            {
                "box": {
                    "id": "refresh-note",
                    "maxclass": "comment",
                    "text": "The 10 Hz refresh is intentional: a dropped UDP packet is automatically corrected by the next packet, and current orientation is restored after a brief network interruption.",
                    "patching_rect": [
                        580,
                        120,
                        250,
                        90
                    ],
                    "fontsize": 11,
                    "linecount": 2
                }
            },
            {
                "box": {
                    "id": "protocol-note",
                    "maxclass": "comment",
                    "text": "Protocol: UDP 7475 · /qmw/craive/hoa/ypr <yaw> <pitch> <roll>. Traffic is only a few small packets per second.",
                    "patching_rect": [
                        25,
                        385,
                        720,
                        40
                    ],
                    "fontsize": 11,
                    "linecount": 2
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "source": [
                        "yaw",
                        0
                    ],
                    "destination": [
                        "pak",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "pitch",
                        0
                    ],
                    "destination": [
                        "pak",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "roll",
                        0
                    ],
                    "destination": [
                        "pak",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "pak",
                        0
                    ],
                    "destination": [
                        "speedlim",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "speedlim",
                        0
                    ],
                    "destination": [
                        "osc-message",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "osc-message",
                        0
                    ],
                    "destination": [
                        "udp-send",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "refresh-init",
                        0
                    ],
                    "destination": [
                        "refresh-toggle",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "refresh-toggle",
                        0
                    ],
                    "destination": [
                        "refresh-metro",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "refresh-metro",
                        0
                    ],
                    "destination": [
                        "pak",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "center",
                        0
                    ],
                    "destination": [
                        "center-unpack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "center-unpack",
                        0
                    ],
                    "destination": [
                        "yaw",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "center-unpack",
                        1
                    ],
                    "destination": [
                        "pitch",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "center-unpack",
                        2
                    ],
                    "destination": [
                        "roll",
                        0
                    ]
                }
            }
        ],
        "dependency_cache": [
            {
                "name": "spat5.osc.udpsend.mxo",
                "type": "iLaX",
                "implicit": 1
            }
        ]
    }
}
