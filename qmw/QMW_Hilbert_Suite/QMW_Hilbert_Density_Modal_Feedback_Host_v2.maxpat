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
      45.0,
      45.0,
      1590.0,
      1010.0
    ],
    "bglocked": 0,
    "openinpresentation": 0,
    "default_fontsize": 12.0,
    "default_fontface": 0,
    "default_fontname": "Arial",
    "gridonopen": 1,
    "gridsize": [
      15.0,
      15.0
    ],
    "gridsnaponopen": 1,
    "objectsnaponopen": 1,
    "description": "Excitation-driven modal host with visible complex Hilbert feedback architecture.",
    "digest": "Quantum-field motion excites sixteen damped resonances before analytic density-matrix feedback.",
    "tags": "QMW conductor MC resonator hilbert density matrix feedback host",
    "boxes": [
      {
        "box": {
          "id": "obj-1",
          "maxclass": "comment",
          "fontsize": 24.0,
          "fontface": 1,
          "text": "QMW Hilbert Density Modal Feedback Host v2",
          "patching_rect": [
            30.0,
            18.0,
            560.0,
            34.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-2",
          "maxclass": "comment",
          "fontsize": 13.0,
          "text": "Open this patch—not the inner abstraction. It receives the conductor on UDP 7400 and owns every safety-critical connection.",
          "patching_rect": [
            31.0,
            55.0,
            920.0,
            21.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-3",
          "maxclass": "comment",
          "fontsize": 16.0,
          "fontface": 1,
          "text": "1  CONDUCTOR INPUT",
          "patching_rect": [
            30.0,
            100.0,
            190.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-4",
          "maxclass": "newobj",
          "text": "udpreceive 7400",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "FullPacket",
            ""
          ],
          "patching_rect": [
            40.0,
            140.0,
            112.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-5",
          "maxclass": "newobj",
          "text": "OSC-route /qmw",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "FullPacket",
            "FullPacket"
          ],
          "patching_rect": [
            40.0,
            175.0,
            110.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-6",
          "maxclass": "newobj",
          "text": "OSC-route /density_field /state /qac",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "FullPacket",
            "FullPacket",
            "FullPacket",
            "FullPacket"
          ],
          "patching_rect": [
            40.0,
            210.0,
            240.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-7",
          "maxclass": "newobj",
          "text": "OSC-route /magnitude /phase /speed /harmonics /purity /entropy /coherence",
          "numinlets": 1,
          "numoutlets": 8,
          "outlettype": [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
          ],
          "patching_rect": [
            40.0,
            250.0,
            485.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-8",
          "maxclass": "button",
          "patching_rect": [
            165.0,
            140.0,
            24.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-9",
          "maxclass": "comment",
          "text": "flashes when density frames arrive",
          "patching_rect": [
            197.0,
            143.0,
            205.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-10",
          "maxclass": "comment",
          "text": "Do not open another patch that also binds UDP port 7400.",
          "patching_rect": [
            40.0,
            282.0,
            350.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-11",
          "maxclass": "newobj",
          "text": "js qmw_density_field_to_mc_resonator16_v1.js",
          "numinlets": 7,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            40.0,
            330.0,
            292.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-12",
          "maxclass": "newobj",
          "text": "print qmw.host.density",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            350.0,
            330.0,
            150.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-13",
          "maxclass": "comment",
          "fontsize": 16.0,
          "fontface": 1,
          "text": "2  SIXTEEN EXCITED MODAL RESONATORS",
          "patching_rect": [
            40.0,
            390.0,
            265.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-14",
          "maxclass": "flonum",
          "minimum": 20.0,
          "maximum": 1000.0,
          "patching_rect": [
            40.0,
            430.0,
            70.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-15",
          "maxclass": "comment",
          "text": "fundamental Hz",
          "patching_rect": [
            118.0,
            432.0,
            105.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-16",
          "maxclass": "newobj",
          "text": "sig~ 55.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            40.0,
            470.0,
            55.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-17",
          "maxclass": "newobj",
          "text": "mc.gen~ @gen qmw_density_field_modal_resonator16_mc_v2 @chans 16",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ],
          "patching_rect": [
            40.0,
            515.0,
            420.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-18",
          "maxclass": "comment",
          "text": "No free-running oscillators: field motion excites one damped noise-driven mode per basis state.",
          "patching_rect": [
            40.0,
            545.0,
            390.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-19",
          "maxclass": "comment",
          "fontsize": 16.0,
          "fontface": 1,
          "text": "3  FULL DENSITY MATRIX (OPTIONAL)",
          "patching_rect": [
            570.0,
            100.0,
            310.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-20",
          "maxclass": "comment",
          "text": "Identity is retained unless a genuine 256-cell rho stream arrives.",
          "patching_rect": [
            570.0,
            128.0,
            390.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-21",
          "maxclass": "newobj",
          "text": "OSC-route /rho",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "FullPacket",
            "FullPacket"
          ],
          "patching_rect": [
            570.0,
            175.0,
            105.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-22",
          "maxclass": "newobj",
          "text": "OSC-route /real /imag",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ],
          "patching_rect": [
            570.0,
            210.0,
            145.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-23",
          "maxclass": "newobj",
          "text": "zl.slice 1",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            570.0,
            250.0,
            68.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-24",
          "maxclass": "newobj",
          "text": "zl.slice 1",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            660.0,
            250.0,
            68.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-25",
          "maxclass": "newobj",
          "text": "t b l",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "list"
          ],
          "patching_rect": [
            660.0,
            285.0,
            42.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-26",
          "maxclass": "message",
          "text": "commit",
          "patching_rect": [
            620.0,
            320.0,
            52.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-27",
          "maxclass": "newobj",
          "text": "OSC-route /rho",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "FullPacket",
            "FullPacket"
          ],
          "patching_rect": [
            780.0,
            175.0,
            105.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-28",
          "maxclass": "newobj",
          "text": "OSC-route /real /imag",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ],
          "patching_rect": [
            780.0,
            210.0,
            145.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-29",
          "maxclass": "newobj",
          "text": "t b l",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "list"
          ],
          "patching_rect": [
            870.0,
            250.0,
            42.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-30",
          "maxclass": "message",
          "text": "commit",
          "patching_rect": [
            830.0,
            285.0,
            52.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-31",
          "maxclass": "button",
          "patching_rect": [
            745.0,
            320.0,
            24.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-32",
          "maxclass": "comment",
          "text": "flashes on full rho update",
          "patching_rect": [
            777.0,
            322.0,
            160.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-33",
          "maxclass": "comment",
          "text": "/state/rho includes a revision atom, removed here; /qac/rho does not.",
          "patching_rect": [
            570.0,
            355.0,
            450.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-34",
          "maxclass": "comment",
          "fontsize": 16.0,
          "fontface": 1,
          "text": "4  COMPLEX HILBERT FEEDBACK ENGINE",
          "patching_rect": [
            570.0,
            410.0,
            270.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-35",
          "maxclass": "newobj",
          "text": "qmw_density_matrix_resonator_feedback16_mc_v1",
          "numinlets": 7,
          "numoutlets": 4,
          "outlettype": [
            "multichannelsignal",
            "multichannelsignal",
            "multichannelsignal",
            ""
          ],
          "patching_rect": [
            570.0,
            515.0,
            335.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-36",
          "maxclass": "newobj",
          "text": "print qmw.host.feedback",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            920.0,
            515.0,
            160.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-37",
          "maxclass": "comment",
          "text": "modal field -> mc.hilbert~ -> rho -> phase projection -> causal delay -> bounded feedback",
          "patching_rect": [
            570.0,
            545.0,
            600.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-38",
          "maxclass": "button",
          "patching_rect": [
            570.0,
            610.0,
            38.0,
            38.0
          ],
          "bgcolor": [
            0.2,
            0.65,
            0.3,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-39",
          "maxclass": "comment",
          "fontface": 1,
          "text": "RAW SAFE",
          "patching_rect": [
            615.0,
            619.0,
            80.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-40",
          "maxclass": "message",
          "text": "safe",
          "patching_rect": [
            570.0,
            665.0,
            38.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-41",
          "maxclass": "button",
          "patching_rect": [
            720.0,
            610.0,
            38.0,
            38.0
          ],
          "bgcolor": [
            0.25,
            0.55,
            0.85,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-42",
          "maxclass": "comment",
          "fontface": 1,
          "text": "LOW FEEDBACK",
          "patching_rect": [
            765.0,
            619.0,
            110.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-43",
          "maxclass": "newobj",
          "text": "t b b b",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "bang",
            "bang",
            "bang"
          ],
          "patching_rect": [
            720.0,
            665.0,
            58.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-44",
          "maxclass": "message",
          "text": "0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03",
          "patching_rect": [
            720.0,
            705.0,
            525.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-45",
          "maxclass": "message",
          "text": "tune 55 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16",
          "patching_rect": [
            790.0,
            665.0,
            325.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-46",
          "maxclass": "message",
          "text": "mode 2",
          "patching_rect": [
            1125.0,
            665.0,
            52.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-47",
          "maxclass": "button",
          "patching_rect": [
            930.0,
            610.0,
            38.0,
            38.0
          ],
          "bgcolor": [
            0.9,
            0.15,
            0.12,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-48",
          "maxclass": "comment",
          "fontface": 1,
          "text": "PANIC + MUTE",
          "patching_rect": [
            975.0,
            619.0,
            115.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-49",
          "maxclass": "newobj",
          "text": "t b b",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "bang"
          ],
          "patching_rect": [
            930.0,
            665.0,
            42.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-50",
          "maxclass": "message",
          "text": "panic",
          "patching_rect": [
            930.0,
            705.0,
            42.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-51",
          "maxclass": "message",
          "text": "0",
          "patching_rect": [
            985.0,
            705.0,
            30.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-52",
          "maxclass": "button",
          "patching_rect": [
            1120.0,
            610.0,
            30.0,
            30.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-53",
          "maxclass": "comment",
          "text": "LOCAL TEST (basis 0)",
          "patching_rect": [
            1158.0,
            615.0,
            150.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-54",
          "maxclass": "message",
          "text": "test",
          "patching_rect": [
            1120.0,
            705.0,
            35.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-55",
          "maxclass": "comment",
          "fontsize": 16.0,
          "fontface": 1,
          "text": "5  SAFE STEREO MONITOR",
          "patching_rect": [
            40.0,
            610.0,
            230.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-56",
          "maxclass": "newobj",
          "text": "mc.mixdown~ 2 @autogain 0",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ],
          "patching_rect": [
            40.0,
            665.0,
            175.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-57",
          "maxclass": "newobj",
          "text": "mc.*~ 4.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ],
          "patching_rect": [
            40.0,
            705.0,
            72.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-58",
          "maxclass": "newobj",
          "text": "mc.clip~ -0.95 0.95",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ],
          "patching_rect": [
            40.0,
            745.0,
            130.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-59",
          "maxclass": "newobj",
          "text": "mc.unpack~ 2",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ],
          "patching_rect": [
            40.0,
            785.0,
            85.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-60",
          "maxclass": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0,
          "patching_rect": [
            40.0,
            835.0,
            52.0,
            52.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-61",
          "maxclass": "comment",
          "text": "Click only after the conductor indicator flashes. Sparse states receive 4x monitor gain, then safe clipping.",
          "patching_rect": [
            105.0,
            850.0,
            570.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-62",
          "maxclass": "comment",
          "text": "The monitor clip/trim is outside the recursive loop and cannot alter its quantum coupling.",
          "patching_rect": [
            40.0,
            900.0,
            520.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-63",
          "maxclass": "newobj",
          "text": "loadbang",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "patching_rect": [
            1300.0,
            100.0,
            60.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-64",
          "maxclass": "newobj",
          "text": "t b b b",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "bang",
            "bang",
            "bang"
          ],
          "patching_rect": [
            1300.0,
            140.0,
            58.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-65",
          "maxclass": "message",
          "text": "safe",
          "patching_rect": [
            1300.0,
            180.0,
            38.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-66",
          "maxclass": "message",
          "text": "autocommit 0",
          "patching_rect": [
            1350.0,
            180.0,
            92.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-67",
          "maxclass": "message",
          "text": "55.",
          "patching_rect": [
            1450.0,
            180.0,
            38.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-68",
          "maxclass": "comment",
          "text": "Boot is silent, RAW, identity rho, zero feedback. DSP never starts automatically.",
          "patching_rect": [
            1230.0,
            220.0,
            350.0,
            34.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-69",
          "maxclass": "comment",
          "fontface": 1,
          "fontsize": 13.0,
          "text": "VISIBLE COMPLEX PATH: the mc.hilbert~ pair lives inside the density operator; it is not bypassed.",
          "patching_rect": [
            570.0,
            445.0,
            650.0,
            21.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-70",
          "maxclass": "comment",
          "text": "To inspect it: double-click the feedback abstraction below, then double-click qmw_density_matrix_hilbert_operator16_mc_v1.",
          "patching_rect": [
            570.0,
            475.0,
            760.0,
            20.0
          ]
        }
      }
    ],
    "lines": [
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
            "obj-7",
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
            "obj-7",
            1
          ],
          "destination": [
            "obj-11",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-7",
            2
          ],
          "destination": [
            "obj-11",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-7",
            3
          ],
          "destination": [
            "obj-11",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-7",
            4
          ],
          "destination": [
            "obj-11",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-7",
            5
          ],
          "destination": [
            "obj-11",
            5
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-7",
            6
          ],
          "destination": [
            "obj-11",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-11",
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
            "obj-11",
            1
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
            "obj-14",
            0
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
            "obj-35",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-7",
            1
          ],
          "destination": [
            "obj-35",
            3
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
            "obj-23",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-22",
            1
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
            "obj-23",
            1
          ],
          "destination": [
            "obj-35",
            1
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
            "obj-25",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-25",
            1
          ],
          "destination": [
            "obj-35",
            2
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
            "obj-35",
            6
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
            "obj-31",
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
            "obj-28",
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
            "obj-35",
            1
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
            "obj-29",
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
            2
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
            "obj-30",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-30",
            0
          ],
          "destination": [
            "obj-35",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-30",
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
            "obj-35",
            3
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
            "obj-38",
            0
          ],
          "destination": [
            "obj-40",
            0
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
            "obj-35",
            6
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
            "obj-43",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-43",
            2
          ],
          "destination": [
            "obj-44",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-43",
            1
          ],
          "destination": [
            "obj-45",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-43",
            0
          ],
          "destination": [
            "obj-46",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-44",
            0
          ],
          "destination": [
            "obj-35",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-45",
            0
          ],
          "destination": [
            "obj-35",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-46",
            0
          ],
          "destination": [
            "obj-35",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-47",
            0
          ],
          "destination": [
            "obj-49",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-49",
            1
          ],
          "destination": [
            "obj-50",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-49",
            0
          ],
          "destination": [
            "obj-51",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-50",
            0
          ],
          "destination": [
            "obj-35",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-51",
            0
          ],
          "destination": [
            "obj-60",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-52",
            0
          ],
          "destination": [
            "obj-54",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-54",
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
            "obj-35",
            0
          ],
          "destination": [
            "obj-56",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-56",
            0
          ],
          "destination": [
            "obj-57",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-57",
            0
          ],
          "destination": [
            "obj-58",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-58",
            0
          ],
          "destination": [
            "obj-59",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-59",
            0
          ],
          "destination": [
            "obj-60",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-59",
            1
          ],
          "destination": [
            "obj-60",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-63",
            0
          ],
          "destination": [
            "obj-64",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-64",
            2
          ],
          "destination": [
            "obj-65",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-64",
            1
          ],
          "destination": [
            "obj-66",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-64",
            0
          ],
          "destination": [
            "obj-67",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-65",
            0
          ],
          "destination": [
            "obj-35",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-66",
            0
          ],
          "destination": [
            "obj-35",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-67",
            0
          ],
          "destination": [
            "obj-14",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "qmw_density_field_modal_resonator16_mc_v2.gendsp",
        "type": "JSON",
        "implicit": 1
      },
      {
        "name": "qmw_density_field_to_mc_resonator16_v1.js",
        "type": "TEXT",
        "implicit": 1
      },
      {
        "name": "qmw_density_matrix_resonator_feedback16_mc_v1.maxpat",
        "type": "JSON",
        "implicit": 1
      },
      {
        "name": "qmw_feedback_branch_controls16_v1.js",
        "type": "TEXT",
        "implicit": 1
      },
      {
        "name": "qmw_density_matrix_hilbert_operator16_mc_v1.maxpat",
        "type": "JSON",
        "implicit": 1
      },
      {
        "name": "qmw_density_matrix16_to_mcs_matrix_v1.js",
        "type": "TEXT",
        "implicit": 1
      }
    ]
  }
}
