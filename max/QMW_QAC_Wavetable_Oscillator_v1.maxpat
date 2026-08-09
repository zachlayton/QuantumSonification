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
            980.0,
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
                    "id": "panel",
                    "maxclass": "panel",
                    "patching_rect": [
                        10.0,
                        10.0,
                        940.0,
                        625.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        10.0,
                        940.0,
                        625.0
                    ],
                    "bgcolor": [
                        0.045,
                        0.06,
                        0.09,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "title",
                    "maxclass": "comment",
                    "patching_rect": [
                        28.0,
                        22.0,
                        850.0,
                        28.0
                    ],
                    "text": "QAC \u2192 LOCAL / IBM QUANTUM \u2192 256-POINT WAVETABLE",
                    "fontsize": 18.0,
                    "presentation": 1,
                    "presentation_rect": [
                        28.0,
                        22.0,
                        850.0,
                        28.0
                    ],
                    "textcolor": [
                        0.85,
                        0.93,
                        1.0,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "instructions",
                    "maxclass": "comment",
                    "patching_rect": [
                        28.0,
                        56.0,
                        880.0,
                        38.0
                    ],
                    "text": "Build a circuit in QAC, export QASM, then hear the local table immediately and the IBM-count table when the job completes.",
                    "presentation": 1,
                    "presentation_rect": [
                        28.0,
                        56.0,
                        880.0,
                        38.0
                    ],
                    "textcolor": [
                        0.65,
                        0.72,
                        0.82,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "qac",
                    "maxclass": "newobj",
                    "patching_rect": [
                        28.0,
                        110.0,
                        235.0,
                        22.0
                    ],
                    "text": "och.microqiskit qc 4 4 sim 256 1",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "presentation": 1,
                    "presentation_rect": [
                        28.0,
                        110.0,
                        235.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "bell",
                    "maxclass": "message",
                    "patching_rect": [
                        28.0,
                        146.0,
                        420.0,
                        22.0
                    ],
                    "text": "QuantumCircuit qc 4 4, qc h 0, qc cx 0 1, Simulator sim qc 256",
                    "presentation": 1,
                    "presentation_rect": [
                        28.0,
                        146.0,
                        420.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "getqasm",
                    "maxclass": "message",
                    "patching_rect": [
                        470.0,
                        146.0,
                        92.0,
                        22.0
                    ],
                    "text": "sim get_qasm",
                    "presentation": 1,
                    "presentation_rect": [
                        470.0,
                        146.0,
                        92.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "sender",
                    "maxclass": "newobj",
                    "patching_rect": [
                        285.0,
                        110.0,
                        180.0,
                        22.0
                    ],
                    "text": "qac_wavetable_sender_v1",
                    "numinlets": 1,
                    "numoutlets": 1
                }
            },
            {
                "box": {
                    "id": "sendstatus",
                    "maxclass": "message",
                    "patching_rect": [
                        485.0,
                        110.0,
                        360.0,
                        22.0
                    ],
                    "text": "sender ready",
                    "presentation": 1,
                    "presentation_rect": [
                        485.0,
                        110.0,
                        360.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "udp",
                    "maxclass": "newobj",
                    "patching_rect": [
                        28.0,
                        210.0,
                        132.0,
                        22.0
                    ],
                    "text": "udpreceive 7412",
                    "numinlets": 1,
                    "numoutlets": 2
                }
            },
            {
                "box": {
                    "id": "oroute",
                    "maxclass": "newobj",
                    "patching_rect": [
                        175.0,
                        210.0,
                        610.0,
                        22.0
                    ],
                    "text": "o.route /qmw/wavetable/points /qmw/wavetable/status /qmw/wavetable/error /qmw/wavetable/correlations",
                    "numinlets": 1,
                    "numoutlets": 5
                }
            },
            {
                "box": {
                    "id": "rawprint",
                    "maxclass": "newobj",
                    "patching_rect": [
                        625.0,
                        250.0,
                        135.0,
                        22.0
                    ],
                    "text": "print WTABLE_RAW"
                }
            },
            {
                "box": {
                    "id": "loader",
                    "maxclass": "newobj",
                    "patching_rect": [
                        28.0,
                        260.0,
                        195.0,
                        22.0
                    ],
                    "text": "js qmw_wavetable_receiver_v1.js",
                    "numinlets": 1,
                    "numoutlets": 3
                }
            },
            {
                "box": {
                    "id": "buffer",
                    "maxclass": "newobj",
                    "patching_rect": [
                        28.0,
                        305.0,
                        265.0,
                        22.0
                    ],
                    "text": "buffer~ qmw_wavetable @samps 256 @channels 1"
                }
            },
            {
                "box": {
                    "id": "display",
                    "maxclass": "multislider",
                    "patching_rect": [
                        28.0,
                        350.0,
                        880.0,
                        150.0
                    ],
                    "size": 256,
                    "setminmax": [
                        -1.0,
                        1.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        28.0,
                        350.0,
                        880.0,
                        150.0
                    ],
                    "bgcolor": [
                        0.08,
                        0.1,
                        0.14,
                        1.0
                    ],
                    "slidercolor": [
                        0.34,
                        0.78,
                        1.0,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "freq",
                    "maxclass": "flonum",
                    "patching_rect": [
                        28.0,
                        525.0,
                        75.0,
                        22.0
                    ],
                    "value": 110.0,
                    "presentation": 1,
                    "presentation_rect": [
                        28.0,
                        525.0,
                        75.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "freqlabel",
                    "maxclass": "comment",
                    "patching_rect": [
                        110.0,
                        525.0,
                        95.0,
                        20.0
                    ],
                    "text": "frequency Hz",
                    "presentation": 1,
                    "presentation_rect": [
                        110.0,
                        525.0,
                        95.0,
                        20.0
                    ],
                    "textcolor": [
                        0.7,
                        0.76,
                        0.84,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "phasor",
                    "maxclass": "newobj",
                    "patching_rect": [
                        28.0,
                        565.0,
                        62.0,
                        22.0
                    ],
                    "text": "sig~ 110."
                }
            },
            {
                "box": {
                    "id": "wave",
                    "maxclass": "gen.codebox~",
                    "patching_rect": [
                        110.0,
                        555.0,
                        390.0,
                        105.0
                    ],
                    "code": "Buffer table(\"qmw_wavetable\");\nHistory phase(0);\nfreq = max(in1, 0);\nphase = fract(phase + freq / samplerate);\nsample, idx = wave(table, phase, 0, 256, 0, channels=1);\nout1 = sample;\nout2 = phase;",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "signal",
                        "signal"
                    ]
                }
            },
            {
                "box": {
                    "id": "gain",
                    "maxclass": "newobj",
                    "patching_rect": [
                        520.0,
                        565.0,
                        52.0,
                        22.0
                    ],
                    "text": "*~ 0.12"
                }
            },
            {
                "box": {
                    "id": "dac",
                    "maxclass": "newobj",
                    "patching_rect": [
                        345.0,
                        560.0,
                        48.0,
                        32.0
                    ],
                    "text": "ezdac~",
                    "presentation": 1,
                    "presentation_rect": [
                        345.0,
                        555.0,
                        48.0,
                        32.0
                    ]
                }
            },
            {
                "box": {
                    "id": "statuslabel",
                    "maxclass": "comment",
                    "patching_rect": [
                        430.0,
                        525.0,
                        62.0,
                        20.0
                    ],
                    "text": "STATUS",
                    "presentation": 1,
                    "presentation_rect": [
                        430.0,
                        525.0,
                        62.0,
                        20.0
                    ],
                    "textcolor": [
                        0.34,
                        0.78,
                        1.0,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "status",
                    "maxclass": "message",
                    "patching_rect": [
                        500.0,
                        522.0,
                        408.0,
                        24.0
                    ],
                    "text": "waiting for wavetable",
                    "presentation": 1,
                    "presentation_rect": [
                        500.0,
                        522.0,
                        408.0,
                        24.0
                    ]
                }
            },
            {
                "box": {
                    "id": "print",
                    "maxclass": "newobj",
                    "patching_rect": [
                        780.0,
                        210.0,
                        150.0,
                        22.0
                    ],
                    "text": "print WTABLE_OTHER"
                }
            },
            {
                "box": {
                    "id": "corr_unpack",
                    "maxclass": "newobj",
                    "patching_rect": [
                        505.0,
                        250.0,
                        90.0,
                        22.0
                    ],
                    "text": "unpack i f f f"
                }
            },
            {
                "box": {
                    "id": "xx",
                    "maxclass": "flonum",
                    "patching_rect": [
                        610.0,
                        250.0,
                        65.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        610.0,
                        305.0,
                        65.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "yy",
                    "maxclass": "flonum",
                    "patching_rect": [
                        690.0,
                        250.0,
                        65.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        690.0,
                        305.0,
                        65.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "zz",
                    "maxclass": "flonum",
                    "patching_rect": [
                        770.0,
                        250.0,
                        65.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        770.0,
                        305.0,
                        65.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "corr_label",
                    "maxclass": "comment",
                    "patching_rect": [
                        610.0,
                        278.0,
                        230.0,
                        20.0
                    ],
                    "text": "XX                 YY                 ZZ",
                    "presentation": 1,
                    "presentation_rect": [
                        610.0,
                        332.0,
                        230.0,
                        20.0
                    ],
                    "textcolor": [
                        0.51,
                        0.81,
                        1.0,
                        1.0
                    ]
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "source": [
                        "bell",
                        0
                    ],
                    "destination": [
                        "qac",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "getqasm",
                        0
                    ],
                    "destination": [
                        "qac",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "qac",
                        0
                    ],
                    "destination": [
                        "sender",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "sender",
                        0
                    ],
                    "destination": [
                        "sendstatus",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "udp",
                        0
                    ],
                    "destination": [
                        "oroute",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "udp",
                        0
                    ],
                    "destination": [
                        "rawprint",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "oroute",
                        0
                    ],
                    "destination": [
                        "loader",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "oroute",
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
                        "oroute",
                        2
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
                        "oroute",
                        3
                    ],
                    "destination": [
                        "corr_unpack",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "oroute",
                        4
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
                        "corr_unpack",
                        1
                    ],
                    "destination": [
                        "xx",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "corr_unpack",
                        2
                    ],
                    "destination": [
                        "yy",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "corr_unpack",
                        3
                    ],
                    "destination": [
                        "zz",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "loader",
                        1
                    ],
                    "destination": [
                        "display",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "loader",
                        2
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
                        "freq",
                        0
                    ],
                    "destination": [
                        "phasor",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "phasor",
                        0
                    ],
                    "destination": [
                        "wave",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "wave",
                        0
                    ],
                    "destination": [
                        "gain",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "gain",
                        0
                    ],
                    "destination": [
                        "dac",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "gain",
                        0
                    ],
                    "destination": [
                        "dac",
                        1
                    ]
                }
            }
        ],
        "dependency_cache": [
            {
                "name": "qmw_wavetable_receiver_v1.js",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1
            },
            {
                "name": "qac_wavetable_sender_v1.maxpat",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "JSON",
                "implicit": 1
            },
            {
                "name": "qac_qasm_sender_v1.js",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1
            },
            {
                "name": "o.route.mxo",
                "type": "iLaX"
            }
        ]
    }
}
