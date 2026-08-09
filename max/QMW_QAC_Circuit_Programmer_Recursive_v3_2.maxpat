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
            80.0,
            80.0,
            900.0,
            680.0
        ],
        "openinpresentation": 1,
        "gridsize": [
            15.0,
            15.0
        ],
        "boxes": [
            {
                "box": {
                    "fontsize": 18.0,
                    "id": "title",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        25.0,
                        18.0,
                        700.0,
                        27.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        25.0,
                        18.0,
                        700.0,
                        27.0
                    ],
                    "text": "QMW CIRCUIT PROGRAMMER \u00b7 RECURSIVE WILSON v3.2",
                    "textcolor": [
                        0.9,
                        0.93,
                        0.97,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "filename": "qmw_qac_circuit_programmer_recursive_v3_2.js",
                    "id": "ui",
                    "jsarguments": [
                        "qmw_qac_circuit_programmer_recursive_v3_2.js"
                    ],
                    "maxclass": "jsui",
                    "numinlets": 1,
                    "numoutlets": 7,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        25.0,
                        55.0,
                        780.0,
                        425.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        25.0,
                        55.0,
                        780.0,
                        425.0
                    ]
                }
            },
            {
                "box": {
                    "id": "status_label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        25.0,
                        500.0,
                        70.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        25.0,
                        500.0,
                        70.0,
                        20.0
                    ],
                    "text": "STATUS",
                    "textcolor": [
                        0.51,
                        0.81,
                        1.0,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "status",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        95.0,
                        497.0,
                        520.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        95.0,
                        497.0,
                        520.0,
                        22.0
                    ],
                    "text": "\"sent 9 gates \u2192 QASM bridge\""
                }
            },
            {
                "box": {
                    "id": "qac",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        25.0,
                        532.0,
                        235.0,
                        22.0
                    ],
                    "text": "och.microqiskit qc 4 4 sim 1024 1"
                }
            },
            {
                "box": {
                    "id": "tee",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "patching_rect": [
                        280.0,
                        532.0,
                        40.0,
                        22.0
                    ],
                    "text": "t l l"
                }
            },
            {
                "box": {
                    "id": "sender",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        340.0,
                        532.0,
                        235.0,
                        22.0
                    ],
                    "text": "qac_quantumsonification_sender_recursive_v3"
                }
            },
            {
                "box": {
                    "id": "qac_print",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        590.0,
                        532.0,
                        95.0,
                        22.0
                    ],
                    "text": "print QAC_OUT"
                }
            },
            {
                "box": {
                    "id": "tx_print",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        700.0,
                        532.0,
                        136.0,
                        22.0
                    ],
                    "text": "print QAC_BRIDGE_TX"
                }
            },
            {
                "box": {
                    "id": "gate_pack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        570.0,
                        158.0,
                        22.0
                    ],
                    "text": "o.pack /qmw/qac/gate",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        "FullPacket"
                    ]
                }
            },
            {
                "box": {
                    "id": "gate_udp",
                    "maxclass": "newobj",
                    "patching_rect": [
                        200.0,
                        570.0,
                        157.0,
                        22.0
                    ],
                    "text": "udpsend 127.0.0.1 7403",
                    "numinlets": 1,
                    "numoutlets": 0
                }
            },
            {
                "box": {
                    "id": "gate_print",
                    "maxclass": "newobj",
                    "patching_rect": [
                        375.0,
                        570.0,
                        156.0,
                        22.0
                    ],
                    "text": "print QAC_LIVE_GATE_TX",
                    "numinlets": 1,
                    "numoutlets": 0
                }
            },
            {
                "box": {
                    "id": "next_pack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        25.0,
                        610.0,
                        160.0,
                        22.0
                    ],
                    "text": "o.pack /qmw/recursive/next",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "FullPacket"
                    ]
                }
            },
            {
                "box": {
                    "id": "start_pack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        205.0,
                        610.0,
                        160.0,
                        22.0
                    ],
                    "text": "o.pack /qmw/recursive/start",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "FullPacket"
                    ]
                }
            },
            {
                "box": {
                    "id": "stop_pack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        385.0,
                        610.0,
                        160.0,
                        22.0
                    ],
                    "text": "o.pack /qmw/recursive/stop",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "FullPacket"
                    ]
                }
            },
            {
                "box": {
                    "id": "reset_pack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        565.0,
                        610.0,
                        160.0,
                        22.0
                    ],
                    "text": "o.pack /qmw/recursive/reset",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "FullPacket"
                    ]
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "destination": [
                        "tee",
                        0
                    ],
                    "source": [
                        "qac",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "tx_print",
                        0
                    ],
                    "source": [
                        "sender",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "qac_print",
                        0
                    ],
                    "source": [
                        "tee",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "sender",
                        0
                    ],
                    "source": [
                        "tee",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "qac",
                        0
                    ],
                    "source": [
                        "ui",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "status",
                        0
                    ],
                    "source": [
                        "ui",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "ui",
                        2
                    ],
                    "destination": [
                        "gate_pack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "gate_pack",
                        0
                    ],
                    "destination": [
                        "gate_udp",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "ui",
                        2
                    ],
                    "destination": [
                        "gate_print",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "ui",
                        3
                    ],
                    "destination": [
                        "next_pack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "next_pack",
                        0
                    ],
                    "destination": [
                        "gate_udp",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "ui",
                        4
                    ],
                    "destination": [
                        "start_pack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "start_pack",
                        0
                    ],
                    "destination": [
                        "gate_udp",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "ui",
                        5
                    ],
                    "destination": [
                        "stop_pack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "stop_pack",
                        0
                    ],
                    "destination": [
                        "gate_udp",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "ui",
                        6
                    ],
                    "destination": [
                        "reset_pack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "reset_pack",
                        0
                    ],
                    "destination": [
                        "gate_udp",
                        0
                    ]
                }
            }
        ],
        "originid": "pat-37",
        "dependency_cache": [
            {
                "name": "o.pack.mxo",
                "type": "iLaX"
            },
            {
                "name": "och.microqiskit.mxo",
                "type": "iLaX"
            },
            {
                "name": "qac_qasm_sender_v1.js",
                "bootpath": "~/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1
            },
            {
                "name": "qmw_qac_circuit_programmer_v1.js",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1
            },
            {
                "name": "qmw_qac_circuit_programmer_recursive_v3_2.js",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1
            },
            {
                "name": "qmw_qac_circuit_programmer_v2.js",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1
            },
            {
                "name": "qac_quantumsonification_sender_recursive_v3.maxpat",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "JSON",
                "implicit": 1
            }
        ],
        "autosave": 0
    }
}
