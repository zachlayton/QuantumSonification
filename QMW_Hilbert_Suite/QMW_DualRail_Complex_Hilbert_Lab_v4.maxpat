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
      34,
      100,
      1444,
      816
    ],
    "gridsize": [
      15,
      15
    ],
    "description": "V4 dual-rail complex feedback laboratory around the stable harmonic-modal monitor.",
    "digest": "Exposes analytic rotation, coherence pairs, full density coupling, and persistent complex memory.",
    "tags": "QMW conductor MC resonator hilbert density matrix feedback host",
    "boxes": [
      {
        "box": {
          "fontface": 1,
          "fontsize": 24,
          "id": "obj-1",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30,
            18,
            560,
            33
          ],
          "text": "QMW Dual-Rail Complex Hilbert Laboratory v4"
        }
      },
      {
        "box": {
          "fontsize": 13,
          "id": "obj-2",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            31,
            55,
            920,
            21
          ],
          "text": "Open this patch—not the inner abstraction. It receives the conductor on UDP 7400 and owns every safety-critical connection."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16,
          "id": "obj-3",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30,
            100,
            190,
            24
          ],
          "text": "1  CONDUCTOR INPUT"
        }
      },
      {
        "box": {
          "id": "obj-4",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            40,
            140,
            112,
            22
          ],
          "text": "udpreceive 7400"
        }
      },
      {
        "box": {
          "id": "obj-5",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            40,
            175,
            110,
            22
          ],
          "text": "OSC-route /qmw"
        }
      },
      {
        "box": {
          "id": "obj-6",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "",
            "",
            "",
            ""
          ],
          "patching_rect": [
            40,
            210,
            240,
            22
          ],
          "text": "OSC-route /density_field /state /qac"
        }
      },
      {
        "box": {
          "id": "obj-7",
          "maxclass": "newobj",
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
            40,
            250,
            485,
            22
          ],
          "text": "OSC-route /magnitude /phase /speed /harmonics /purity /entropy /coherence"
        }
      },
      {
        "box": {
          "id": "obj-8",
          "maxclass": "button",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            165,
            140,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-9",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            197,
            143,
            205,
            20
          ],
          "text": "flashes when density frames arrive"
        }
      },
      {
        "box": {
          "id": "obj-10",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            40,
            282,
            350,
            20
          ],
          "text": "Do not open another patch that also binds UDP port 7400."
        }
      },
      {
        "box": {
          "id": "obj-11",
          "maxclass": "newobj",
          "numinlets": 7,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            40,
            330,
            292,
            22
          ],
          "saved_object_attributes": {
            "filename": "qmw_density_field_to_mc_resonator16_v1.js",
            "parameter_enable": 0
          },
          "text": "js qmw_density_field_to_mc_resonator16_v1.js"
        }
      },
      {
        "box": {
          "id": "obj-12",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            350,
            330,
            150,
            22
          ],
          "text": "print qmw.host.density"
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16,
          "id": "obj-13",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            40,
            390,
            340,
            24
          ],
          "text": "2  SIXTEEN HARMONIC MODAL MONITORS"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-14",
          "maxclass": "flonum",
          "maximum": 1000,
          "minimum": 20,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            40,
            430,
            70,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-15",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            118,
            432,
            105,
            20
          ],
          "text": "fundamental Hz"
        }
      },
      {
        "box": {
          "id": "obj-16",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            40,
            470,
            55,
            22
          ],
          "text": "sig~ 55."
        }
      },
      {
        "box": {
          "id": "obj-17",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ],
          "patching_rect": [
            40,
            515,
            465,
            22
          ],
          "text": "mc.gen~ @gen qmw_density_field_harmonic_modal_resonator16_mc_v3 @chans 16"
        }
      },
      {
        "box": {
          "id": "obj-18",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            40,
            545,
            535,
            20
          ],
          "text": "Exact harmonics dominate; quantum gaps deform them only by the explicit Harmonic Lock amount."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16,
          "id": "obj-19",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            570,
            100,
            310,
            24
          ],
          "text": "3  FULL DENSITY MATRIX (OPTIONAL)"
        }
      },
      {
        "box": {
          "id": "obj-20",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            570,
            128,
            390,
            20
          ],
          "text": "Identity is retained unless a genuine 256-cell rho stream arrives."
        }
      },
      {
        "box": {
          "id": "obj-21",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            570,
            175,
            105,
            22
          ],
          "text": "OSC-route /rho"
        }
      },
      {
        "box": {
          "id": "obj-22",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ],
          "patching_rect": [
            570,
            210,
            145,
            22
          ],
          "text": "OSC-route /real /imag"
        }
      },
      {
        "box": {
          "id": "obj-23",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            570,
            250,
            68,
            22
          ],
          "text": "zl.slice 1"
        }
      },
      {
        "box": {
          "id": "obj-24",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            660,
            250,
            68,
            22
          ],
          "text": "zl.slice 1"
        }
      },
      {
        "box": {
          "id": "obj-25",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            ""
          ],
          "patching_rect": [
            660,
            285,
            42,
            22
          ],
          "text": "t b l"
        }
      },
      {
        "box": {
          "id": "obj-26",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            620,
            320,
            52,
            22
          ],
          "text": "commit"
        }
      },
      {
        "box": {
          "id": "obj-27",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            780,
            175,
            105,
            22
          ],
          "text": "OSC-route /rho"
        }
      },
      {
        "box": {
          "id": "obj-28",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ],
          "patching_rect": [
            780,
            210,
            145,
            22
          ],
          "text": "OSC-route /real /imag"
        }
      },
      {
        "box": {
          "id": "obj-29",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            ""
          ],
          "patching_rect": [
            870,
            250,
            42,
            22
          ],
          "text": "t b l"
        }
      },
      {
        "box": {
          "id": "obj-30",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            830,
            285,
            52,
            22
          ],
          "text": "commit"
        }
      },
      {
        "box": {
          "id": "obj-31",
          "maxclass": "button",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            745,
            320,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-32",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            777,
            322,
            160,
            20
          ],
          "text": "flashes on full rho update"
        }
      },
      {
        "box": {
          "id": "obj-33",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            570,
            355,
            450,
            20
          ],
          "text": "/state/rho includes a revision atom, removed here; /qac/rho does not."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16,
          "id": "obj-34",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            570,
            410,
            338,
            24
          ],
          "text": "4  COMPLEX HILBERT FEEDBACK ENGINE"
        }
      },
      {
        "box": {
          "id": "obj-35",
          "maxclass": "newobj",
          "numinlets": 7,
          "numoutlets": 6,
          "outlettype": [
            "multichannelsignal",
            "multichannelsignal",
            "",
            "",
            "multichannelsignal",
            "multichannelsignal"
          ],
          "patching_rect": [
            660,
            381,
            335,
            22
          ],
          "text": "qmw_density_matrix_dualrail_feedback16_mc_v2"
        }
      },
      {
        "box": {
          "id": "obj-36",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            920,
            515,
            160,
            22
          ],
          "text": "print qmw.host.feedback"
        }
      },
      {
        "box": {
          "id": "obj-37",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            570,
            545,
            600,
            20
          ],
          "text": "stable harmonic modal field -> mc.hilbert~ -> rho -> phase projection -> causal bounded feedback"
        }
      },
      {
        "box": {
          "bgcolor": [
            0.2,
            0.65,
            0.3,
            1
          ],
          "id": "obj-38",
          "maxclass": "button",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            570,
            610,
            38,
            38
          ]
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "obj-39",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            615,
            619,
            80,
            20
          ],
          "text": "RAW SAFE"
        }
      },
      {
        "box": {
          "id": "obj-40",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            570,
            665,
            38,
            22
          ],
          "text": "safe"
        }
      },
      {
        "box": {
          "bgcolor": [
            0.25,
            0.55,
            0.85,
            1
          ],
          "id": "obj-41",
          "maxclass": "button",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            720,
            610,
            38,
            38
          ]
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "obj-42",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            765,
            619,
            110,
            20
          ],
          "text": "LOW FEEDBACK"
        }
      },
      {
        "box": {
          "id": "obj-43",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "bang",
            "bang",
            "bang"
          ],
          "patching_rect": [
            720,
            665,
            58,
            22
          ],
          "text": "t b b b"
        }
      },
      {
        "box": {
          "id": "obj-44",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            720,
            705,
            38,
            22
          ],
          "text": "bang"
        }
      },
      {
        "box": {
          "id": "obj-45",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            790,
            665,
            38,
            22
          ],
          "text": "bang"
        }
      },
      {
        "box": {
          "id": "obj-46",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1125,
            665,
            52,
            22
          ],
          "text": "mode 2"
        }
      },
      {
        "box": {
          "bgcolor": [
            0.9,
            0.15,
            0.12,
            1
          ],
          "id": "obj-47",
          "maxclass": "button",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            930,
            610,
            38,
            38
          ]
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "obj-48",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            975,
            619,
            115,
            20
          ],
          "text": "PANIC + MUTE"
        }
      },
      {
        "box": {
          "id": "obj-49",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "bang"
          ],
          "patching_rect": [
            930,
            665,
            42,
            22
          ],
          "text": "t b b"
        }
      },
      {
        "box": {
          "id": "obj-50",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            930,
            705,
            42,
            22
          ],
          "text": "panic"
        }
      },
      {
        "box": {
          "id": "obj-51",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            985,
            705,
            30,
            22
          ],
          "text": "0"
        }
      },
      {
        "box": {
          "id": "obj-52",
          "maxclass": "button",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1120,
            610,
            30,
            30
          ]
        }
      },
      {
        "box": {
          "id": "obj-53",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1158,
            615,
            150,
            20
          ],
          "text": "LOCAL TEST (basis 0)"
        }
      },
      {
        "box": {
          "id": "obj-54",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1120,
            705,
            35,
            22
          ],
          "text": "test"
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16,
          "id": "obj-55",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            40,
            610,
            230,
            24
          ],
          "text": "5  SAFE STEREO MONITOR"
        }
      },
      {
        "box": {
          "id": "obj-56",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ],
          "patching_rect": [
            40,
            665,
            175,
            22
          ],
          "text": "mc.mixdown~ 2 @autogain 0"
        }
      },
      {
        "box": {
          "id": "obj-57",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ],
          "patching_rect": [
            40,
            705,
            72,
            22
          ],
          "text": "mc.*~ 4."
        }
      },
      {
        "box": {
          "id": "obj-58",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ],
          "patching_rect": [
            40,
            745,
            130,
            22
          ],
          "text": "mc.clip~ -0.95 0.95"
        }
      },
      {
        "box": {
          "id": "obj-59",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ],
          "patching_rect": [
            40,
            785,
            85,
            22
          ],
          "text": "mc.unpack~ 2"
        }
      },
      {
        "box": {
          "id": "obj-60",
          "maxclass": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0,
          "patching_rect": [
            40,
            835,
            52,
            52
          ]
        }
      },
      {
        "box": {
          "id": "obj-61",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            105,
            850,
            570,
            20
          ],
          "text": "Click only after the conductor indicator flashes. Sparse states receive 4x monitor gain, then safe clipping."
        }
      },
      {
        "box": {
          "id": "obj-62",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            40,
            900,
            520,
            20
          ],
          "text": "The monitor clip/trim is outside the recursive loop and cannot alter its quantum coupling."
        }
      },
      {
        "box": {
          "id": "obj-63",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "patching_rect": [
            1300,
            100,
            60,
            22
          ],
          "text": "loadbang"
        }
      },
      {
        "box": {
          "id": "obj-64",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "bang",
            "bang",
            "bang"
          ],
          "patching_rect": [
            1300,
            140,
            58,
            22
          ],
          "text": "t b b b"
        }
      },
      {
        "box": {
          "id": "obj-65",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1294,
            187,
            38,
            22
          ],
          "text": "safe"
        }
      },
      {
        "box": {
          "id": "obj-66",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1344,
            187,
            92,
            22
          ],
          "text": "autocommit 0"
        }
      },
      {
        "box": {
          "id": "obj-67",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1444,
            187,
            38,
            22
          ],
          "text": "55."
        }
      },
      {
        "box": {
          "id": "obj-68",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1230,
            220,
            430,
            20
          ],
          "text": "Boot is silent, RAW, identity rho, zero feedback. DSP never starts automatically."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 13,
          "id": "obj-69",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            570,
            445,
            662,
            21
          ],
          "text": "VISIBLE COMPLEX PATH: mc.hilbert~ follows the stable harmonic-modal field inside the density operator."
        }
      },
      {
        "box": {
          "id": "obj-70",
          "linecount": 2,
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            530,
            476,
            647,
            33
          ],
          "text": "To inspect it: double-click the feedback abstraction below, then double-click qmw_density_matrix_hilbert_operator16_mc_v1."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16,
          "id": "obj-71",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1220,
            285,
            278,
            24
          ],
          "text": "MUSICAL REFERENCE CONTROLS"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-72",
          "maxclass": "flonum",
          "maximum": 1,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1220,
            325,
            70,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-73",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1220,
            355,
            145,
            22
          ],
          "text": "prepend harmonic_lock"
        }
      },
      {
        "box": {
          "id": "obj-74",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1029,
            303,
            310,
            20
          ],
          "text": "Harmonic Lock: 1 = exact 1..16; 0 = conductor gap ratios"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-75",
          "maxclass": "flonum",
          "maximum": 0.5,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1220,
            410,
            70,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-76",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1220,
            430,
            125,
            22
          ],
          "text": "prepend speed_drive"
        }
      },
      {
        "box": {
          "id": "obj-77",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1300,
            402,
            309,
            20
          ],
          "text": "Motion Drive: sustained breath from density-field velocity"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-78",
          "maxclass": "flonum",
          "maximum": 5000,
          "minimum": 25,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1220,
            475,
            78,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-79",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1220,
            505,
            145,
            22
          ],
          "text": "prepend ring_decay_ms"
        }
      },
      {
        "box": {
          "id": "obj-80",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1308,
            477,
            319,
            20
          ],
          "text": "Ring Decay ms: temporal memory of each harmonic mode"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-81",
          "maxclass": "flonum",
          "maximum": 0.01,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1220,
            550,
            78,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-82",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1220,
            580,
            145,
            22
          ],
          "text": "prepend excitation_floor"
        }
      },
      {
        "box": {
          "id": "obj-83",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1308,
            552,
            307,
            20
          ],
          "text": "Noise Floor: static-state audibility; default is nearly silent"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-84",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1390,
            355,
            38,
            22
          ],
          "text": "1."
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-85",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1390,
            430,
            45,
            22
          ],
          "text": "0.1"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-86",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1390,
            505,
            29.5,
            22
          ],
          "text": "25."
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-87",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1390,
            580,
            55,
            22
          ],
          "text": "0.0002"
        }
      },
      {
        "box": {
          "id": "obj-88",
          "linecount": 2,
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1110,
            630,
            470,
            33
          ],
          "text": "Interpretation: stable tone = harmonic reference; population = participation; change = strike; motion = articulation; entropy/coherence = damping; phase = Hilbert rotation."
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-89",
          "maxclass": "flonum",
          "maximum": 0.5,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1260,
            700,
            70,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-90",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1260,
            730,
            145,
            22
          ],
          "text": "prepend reference_tone"
        }
      },
      {
        "box": {
          "id": "obj-91",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1340,
            702,
            250,
            20
          ],
          "text": "Reference Tone: stable harmonic carrier level"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-92",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1420,
            730,
            38,
            22
          ],
          "text": "0.2"
        }
      },
      {
        "box": {
          "id": "obj-93",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            259,
            406,
            220,
            22
          ],
          "saved_object_attributes": {
            "filename": "qmw_harmonic_delay_list16_v1.js",
            "parameter_enable": 0
          },
          "text": "js qmw_harmonic_delay_list16_v1.js"
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "obj-98",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            230,
            460,
            390,
            20
          ],
          "text": "ENGINE ratio list[16] + fundamental + Lock -> delay inlet 6"
        }
      },
      {
        "box": {
          "id": "obj-99",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            460,
            430,
            145,
            22
          ],
          "text": "print qmw.host.delays"
        }
      },
      {
        "box": {
          "id": "obj-96",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ],
          "patching_rect": [
            1090,
            790,
            240,
            22
          ],
          "saved_object_attributes": {
            "filename": "qmw_coherence_feedback_gain16_v1.js",
            "parameter_enable": 0
          },
          "text": "js qmw_coherence_feedback_gain16_v1.js"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-97",
          "maxclass": "flonum",
          "maximum": 1,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1090,
            835,
            70,
            22
          ]
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "obj-94",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1170,
            837,
            260,
            20
          ],
          "text": "Feedback Depth (0 = fixed 0.03 baseline)"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-100",
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            985,
            876,
            70,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-101",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1170,
            877,
            150,
            20
          ],
          "text": "effective bounded gain"
        }
      },
      {
        "box": {
          "id": "obj-102",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1340,
            790,
            185,
            22
          ],
          "text": "print qmw.host.feedback_gain"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-103",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1450,
            835,
            35,
            22
          ],
          "text": "0.5"
        }
      },
      {
        "box": {
          "id": "obj-104",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1090,
            915,
            465,
            20
          ],
          "text": "gain = 0.03 + Depth * 0.09 * coherence * (1 - 0.6 entropy), capped at 0.15"
        }
      },
      {
        "box": {
          "id": "obj-105",
          "maxclass": "newobj",
          "numinlets": 4,
          "numoutlets": 4,
          "outlettype": [
            "",
            "",
            "",
            ""
          ],
          "patching_rect": [
            959,
            203,
            245,
            22
          ],
          "saved_object_attributes": {
            "filename": "qmw_complex_matrix_presets16_v1.js",
            "parameter_enable": 0
          },
          "text": "js qmw_complex_matrix_presets16_v1.js"
        }
      },
      {
        "box": {
          "id": "obj-106",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ],
          "patching_rect": [
            1370,
            100,
            245,
            22
          ],
          "saved_object_attributes": {
            "filename": "qmw_v4_complex_mode_controller.js",
            "parameter_enable": 0
          },
          "text": "js qmw_v4_complex_mode_controller.js"
        }
      },
      {
        "box": {
          "id": "obj-107",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1370,
            145,
            48,
            22
          ],
          "text": "mode1"
        }
      },
      {
        "box": {
          "id": "obj-108",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1425,
            145,
            48,
            22
          ],
          "text": "mode2"
        }
      },
      {
        "box": {
          "id": "obj-109",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1480,
            145,
            48,
            22
          ],
          "text": "mode3"
        }
      },
      {
        "box": {
          "id": "obj-110",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1535,
            145,
            48,
            22
          ],
          "text": "mode4"
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "obj-111",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1324,
            55.5,
            390,
            20
          ],
          "text": "1 Rotation   2 Pairs   3 Full rho   4 Complex Memory"
        }
      },
      {
        "box": {
          "id": "obj-112",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1370,
            235,
            53,
            22
          ],
          "text": "identity"
        }
      },
      {
        "box": {
          "id": "obj-113",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1430,
            235,
            58,
            22
          ],
          "text": "diagonal"
        }
      },
      {
        "box": {
          "id": "obj-114",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1495,
            235,
            125,
            22
          ],
          "text": "fundamental_octave"
        }
      },
      {
        "box": {
          "id": "obj-115",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1370,
            270,
            115,
            22
          ],
          "text": "fundamental_fifth"
        }
      },
      {
        "box": {
          "id": "obj-116",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1495,
            270,
            92,
            22
          ],
          "text": "third_seventh"
        }
      },
      {
        "box": {
          "id": "obj-117",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1595,
            270,
            35,
            22
          ],
          "text": "ring"
        }
      },
      {
        "box": {
          "id": "obj-118",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1640,
            270,
            55,
            22
          ],
          "text": "external"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-119",
          "maxclass": "flonum",
          "maximum": 1,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1370,
            325,
            65,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-120",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1370,
            355,
            115,
            22
          ],
          "text": "prepend imagdepth"
        }
      },
      {
        "box": {
          "id": "obj-121",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1445,
            327,
            130,
            20
          ],
          "text": "Imaginary Coupling"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-122",
          "maxclass": "flonum",
          "maximum": 1,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1370,
            410,
            65,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-123",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1370,
            440,
            125,
            22
          ],
          "text": "prepend hilbertdepth"
        }
      },
      {
        "box": {
          "id": "obj-124",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1445,
            412,
            100,
            20
          ],
          "text": "Hilbert Depth"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-125",
          "maxclass": "flonum",
          "maximum": 1,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1370,
            495,
            65,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-126",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1370,
            525,
            120,
            22
          ],
          "text": "prepend phasedepth"
        }
      },
      {
        "box": {
          "id": "obj-127",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1445,
            497,
            100,
            20
          ],
          "text": "Phase Depth"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-128",
          "maxclass": "flonum",
          "maximum": 1,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1370,
            580,
            65,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-129",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1370,
            610,
            145,
            22
          ],
          "text": "prepend complexmemory"
        }
      },
      {
        "box": {
          "id": "obj-130",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1445,
            582,
            110,
            20
          ],
          "text": "Complex Memory"
        }
      },
      {
        "box": {
          "id": "obj-131",
          "maxclass": "number",
          "maximum": 15,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1590,
            325,
            50,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-132",
          "maxclass": "number",
          "maximum": 15,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1650,
            325,
            50,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-133",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1590,
            355,
            105,
            22
          ],
          "text": "pak cellpair 0 1"
        }
      },
      {
        "box": {
          "id": "obj-134",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1575,
            385,
            195,
            20
          ],
          "text": "custom coherence pair (0-based)"
        }
      },
      {
        "box": {
          "id": "obj-135",
          "maxclass": "number",
          "maximum": 16,
          "minimum": 1,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1370,
            680,
            50,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-136",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 0,
          "patching_rect": [
            1370,
            720,
            195,
            22
          ],
          "text": "qmw_iq_scope_selector16_v1"
        }
      },
      {
        "box": {
          "id": "obj-137",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1430,
            682,
            330,
            20
          ],
          "text": "I/Q scope channel (1..16); double-click scope abstraction"
        }
      },
      {
        "box": {
          "id": "obj-138",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1020,
            415,
            140,
            22
          ],
          "text": "print qmw.v4.matrix"
        }
      },
      {
        "box": {
          "id": "obj-139",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1630,
            100,
            130,
            22
          ],
          "text": "print qmw.v4.mode"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-140",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1720,
            325,
            30,
            22
          ],
          "text": "1."
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-141",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1720,
            410,
            30,
            22
          ],
          "text": "1."
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-142",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1720,
            495,
            30,
            22
          ],
          "text": "1."
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-143",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1720,
            580,
            30,
            22
          ],
          "text": "0."
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "obj-144",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1720,
            680,
            30,
            22
          ],
          "text": "1"
        }
      },
      {
        "box": {
          "id": "obj-145",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            610,
            325,
            120,
            22
          ],
          "text": "OSC-route /density"
        }
      },
      {
        "box": {
          "id": "obj-146",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            610,
            355,
            145,
            22
          ],
          "text": "OSC-route /populations"
        }
      },
      {
        "box": {
          "id": "obj-147",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 0,
          "patching_rect": [
            1580,
            720,
            195,
            22
          ],
          "text": "qmw_iq_scope_selector16_v1"
        }
      },
      {
        "box": {
          "id": "obj-148",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1370,
            747,
            80,
            20
          ],
          "text": "POST rho"
        }
      },
      {
        "box": {
          "id": "obj-149",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1580,
            747,
            80,
            20
          ],
          "text": "PRE rho"
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "destination": [
            "obj-97",
            0
          ],
          "source": [
            "obj-103",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-138",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-105",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "hidden": 1,
          "source": [
            "obj-105",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            2
          ],
          "hidden": 1,
          "source": [
            "obj-105",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            1
          ],
          "source": [
            "obj-105",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            3
          ],
          "hidden": 1,
          "source": [
            "obj-106",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-139",
            0
          ],
          "source": [
            "obj-106",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "hidden": 1,
          "source": [
            "obj-106",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-106",
            0
          ],
          "source": [
            "obj-107",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-106",
            0
          ],
          "source": [
            "obj-108",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-106",
            0
          ],
          "source": [
            "obj-109",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-12",
            0
          ],
          "source": [
            "obj-11",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-17",
            0
          ],
          "source": [
            "obj-11",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-106",
            0
          ],
          "source": [
            "obj-110",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            3
          ],
          "hidden": 1,
          "source": [
            "obj-112",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            3
          ],
          "hidden": 1,
          "source": [
            "obj-113",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            3
          ],
          "hidden": 1,
          "source": [
            "obj-114",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            3
          ],
          "hidden": 1,
          "source": [
            "obj-115",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            3
          ],
          "hidden": 1,
          "source": [
            "obj-116",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            3
          ],
          "hidden": 1,
          "source": [
            "obj-117",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            3
          ],
          "hidden": 1,
          "source": [
            "obj-118",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-120",
            0
          ],
          "source": [
            "obj-119",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            3
          ],
          "hidden": 1,
          "source": [
            "obj-120",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-123",
            0
          ],
          "source": [
            "obj-122",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "source": [
            "obj-123",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-126",
            0
          ],
          "source": [
            "obj-125",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "hidden": 1,
          "source": [
            "obj-126",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-129",
            0
          ],
          "source": [
            "obj-128",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "hidden": 1,
          "source": [
            "obj-129",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-133",
            1
          ],
          "source": [
            "obj-131",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-133",
            2
          ],
          "source": [
            "obj-132",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            3
          ],
          "hidden": 1,
          "source": [
            "obj-133",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-136",
            2
          ],
          "order": 1,
          "source": [
            "obj-135",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-147",
            2
          ],
          "order": 0,
          "source": [
            "obj-135",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-16",
            0
          ],
          "order": 1,
          "source": [
            "obj-14",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-93",
            0
          ],
          "order": 0,
          "source": [
            "obj-14",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-119",
            0
          ],
          "source": [
            "obj-140",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-122",
            0
          ],
          "source": [
            "obj-141",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-125",
            0
          ],
          "source": [
            "obj-142",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-128",
            0
          ],
          "source": [
            "obj-143",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-135",
            0
          ],
          "source": [
            "obj-144",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-146",
            0
          ],
          "source": [
            "obj-145",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            2
          ],
          "source": [
            "obj-146",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-17",
            0
          ],
          "source": [
            "obj-16",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            0
          ],
          "source": [
            "obj-17",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-22",
            0
          ],
          "source": [
            "obj-21",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-23",
            0
          ],
          "source": [
            "obj-22",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-24",
            0
          ],
          "source": [
            "obj-22",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            0
          ],
          "source": [
            "obj-23",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-25",
            0
          ],
          "source": [
            "obj-24",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            1
          ],
          "source": [
            "obj-25",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-26",
            0
          ],
          "source": [
            "obj-25",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-31",
            0
          ],
          "order": 1,
          "source": [
            "obj-26",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "order": 0,
          "source": [
            "obj-26",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-28",
            0
          ],
          "source": [
            "obj-27",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            0
          ],
          "source": [
            "obj-28",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-29",
            0
          ],
          "source": [
            "obj-28",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            1
          ],
          "source": [
            "obj-29",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-30",
            0
          ],
          "source": [
            "obj-29",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-31",
            0
          ],
          "order": 1,
          "source": [
            "obj-30",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "order": 0,
          "source": [
            "obj-30",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-136",
            1
          ],
          "source": [
            "obj-35",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-136",
            0
          ],
          "source": [
            "obj-35",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-147",
            1
          ],
          "hidden": 1,
          "source": [
            "obj-35",
            5
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-147",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-35",
            4
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-36",
            0
          ],
          "source": [
            "obj-35",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-56",
            0
          ],
          "source": [
            "obj-35",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-40",
            0
          ],
          "source": [
            "obj-38",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-5",
            0
          ],
          "source": [
            "obj-4",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "source": [
            "obj-40",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-43",
            0
          ],
          "source": [
            "obj-41",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-44",
            0
          ],
          "source": [
            "obj-43",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-45",
            0
          ],
          "source": [
            "obj-43",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-46",
            0
          ],
          "source": [
            "obj-43",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-96",
            0
          ],
          "source": [
            "obj-44",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-93",
            0
          ],
          "source": [
            "obj-45",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "source": [
            "obj-46",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-49",
            0
          ],
          "source": [
            "obj-47",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-50",
            0
          ],
          "source": [
            "obj-49",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-51",
            0
          ],
          "source": [
            "obj-49",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-145",
            0
          ],
          "order": 0,
          "source": [
            "obj-5",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-6",
            0
          ],
          "order": 1,
          "source": [
            "obj-5",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "source": [
            "obj-50",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-60",
            0
          ],
          "source": [
            "obj-51",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-54",
            0
          ],
          "source": [
            "obj-52",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-11",
            0
          ],
          "source": [
            "obj-54",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-57",
            0
          ],
          "source": [
            "obj-56",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-58",
            0
          ],
          "source": [
            "obj-57",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-59",
            0
          ],
          "source": [
            "obj-58",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-60",
            1
          ],
          "source": [
            "obj-59",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-60",
            0
          ],
          "source": [
            "obj-59",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-21",
            0
          ],
          "source": [
            "obj-6",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-27",
            0
          ],
          "source": [
            "obj-6",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-7",
            0
          ],
          "source": [
            "obj-6",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-103",
            0
          ],
          "hidden": 1,
          "order": 5,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-140",
            0
          ],
          "hidden": 1,
          "order": 4,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-141",
            0
          ],
          "hidden": 1,
          "order": 3,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-142",
            0
          ],
          "hidden": 1,
          "order": 2,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-143",
            0
          ],
          "hidden": 1,
          "order": 1,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-144",
            0
          ],
          "hidden": 1,
          "order": 0,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-64",
            0
          ],
          "hidden": 1,
          "order": 11,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-84",
            0
          ],
          "hidden": 1,
          "order": 10,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-85",
            0
          ],
          "hidden": 1,
          "order": 9,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-86",
            0
          ],
          "hidden": 1,
          "order": 8,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-87",
            0
          ],
          "hidden": 1,
          "order": 7,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-92",
            0
          ],
          "hidden": 1,
          "order": 6,
          "source": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-65",
            0
          ],
          "source": [
            "obj-64",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-66",
            0
          ],
          "source": [
            "obj-64",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-67",
            0
          ],
          "source": [
            "obj-64",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "hidden": 1,
          "source": [
            "obj-65",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            6
          ],
          "hidden": 1,
          "source": [
            "obj-66",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-14",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-67",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-105",
            2
          ],
          "order": 0,
          "source": [
            "obj-7",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-11",
            6
          ],
          "order": 1,
          "source": [
            "obj-7",
            6
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-11",
            5
          ],
          "order": 1,
          "source": [
            "obj-7",
            5
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-11",
            4
          ],
          "source": [
            "obj-7",
            4
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-11",
            3
          ],
          "order": 1,
          "source": [
            "obj-7",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-11",
            2
          ],
          "source": [
            "obj-7",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-11",
            1
          ],
          "order": 1,
          "source": [
            "obj-7",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-11",
            0
          ],
          "order": 2,
          "source": [
            "obj-7",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            3
          ],
          "order": 0,
          "source": [
            "obj-7",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-8",
            0
          ],
          "order": 1,
          "source": [
            "obj-7",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-93",
            1
          ],
          "order": 0,
          "source": [
            "obj-7",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-96",
            0
          ],
          "order": 0,
          "source": [
            "obj-7",
            6
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-96",
            1
          ],
          "order": 0,
          "source": [
            "obj-7",
            5
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-73",
            0
          ],
          "order": 0,
          "source": [
            "obj-72",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-93",
            2
          ],
          "order": 1,
          "source": [
            "obj-72",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-17",
            0
          ],
          "source": [
            "obj-73",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-76",
            0
          ],
          "source": [
            "obj-75",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-17",
            0
          ],
          "source": [
            "obj-76",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-79",
            0
          ],
          "source": [
            "obj-78",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-17",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-79",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-82",
            0
          ],
          "source": [
            "obj-81",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-17",
            0
          ],
          "source": [
            "obj-82",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-72",
            0
          ],
          "source": [
            "obj-84",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-75",
            0
          ],
          "source": [
            "obj-85",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-78",
            0
          ],
          "source": [
            "obj-86",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-81",
            0
          ],
          "source": [
            "obj-87",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-90",
            0
          ],
          "source": [
            "obj-89",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-17",
            0
          ],
          "source": [
            "obj-90",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-89",
            0
          ],
          "source": [
            "obj-92",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            5
          ],
          "source": [
            "obj-93",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-100",
            0
          ],
          "source": [
            "obj-96",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-102",
            0
          ],
          "source": [
            "obj-96",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-35",
            4
          ],
          "source": [
            "obj-96",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-96",
            2
          ],
          "source": [
            "obj-97",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-93",
            1
          ],
          "destination": [
            "obj-99",
            0
          ]
        }
      }
    ],
    "originid": "pat-428",
    "dependency_cache": [
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
      },
      {
        "name": "qmw_coherence_feedback_gain16_v1.js",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      },
      {
        "name": "qmw_complex_matrix_presets16_v1.js",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      },
      {
        "name": "qmw_density_field_harmonic_modal_resonator16_mc_v3.gendsp",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "gDSP",
        "implicit": 1
      },
      {
        "name": "qmw_density_field_to_mc_resonator16_v1.js",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      },
      {
        "name": "qmw_density_matrix16_to_mcs_matrix_v1.js",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      },
      {
        "name": "qmw_density_matrix_dualrail_feedback16_mc_v2.maxpat",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "JSON",
        "implicit": 1
      },
      {
        "name": "qmw_density_matrix_hilbert_operator16_mc_v1.maxpat",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "JSON",
        "implicit": 1
      },
      {
        "name": "qmw_feedback_branch_controls16_v1.js",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      },
      {
        "name": "qmw_harmonic_delay_list16_v1.js",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      },
      {
        "name": "qmw_iq_scope_selector16_v1.maxpat",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "JSON",
        "implicit": 1
      },
      {
        "name": "qmw_v4_complex_mode_controller.js",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      }
    ],
    "autosave": 0
  }
}
