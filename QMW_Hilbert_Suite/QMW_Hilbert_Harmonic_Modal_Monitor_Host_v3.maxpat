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
      41.0,
      108.0,
      1429.0,
      801.0
    ],
    "gridsize": [
      15.0,
      15.0
    ],
    "description": "Harmonic-reference modal host with interpretable quantum excitation and visible complex Hilbert feedback.",
    "digest": "Sixteen locked harmonic modes make quantum behavior audible relative to a stable fundamental.",
    "tags": "QMW conductor MC resonator hilbert density matrix feedback host",
    "boxes": [
      {
        "box": {
          "id": "obj-95",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            720.0,
            800.0,
            432.0,
            22.0
          ],
          "text": "125. 125. 125. 125. 250. 125. 125. 125. 250. 125. 125. 125. 125. 125. 125. 125."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 24.0,
          "id": "obj-1",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            18.0,
            560.0,
            33.0
          ],
          "text": "QMW Hilbert Harmonic-Modal Monitor Host v3"
        }
      },
      {
        "box": {
          "fontsize": 13.0,
          "id": "obj-2",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            31.0,
            55.0,
            920.0,
            21.0
          ],
          "text": "Open this patch—not the inner abstraction. It receives the conductor on UDP 7400 and owns every safety-critical connection."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16.0,
          "id": "obj-3",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            100.0,
            190.0,
            24.0
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
            40.0,
            140.0,
            112.0,
            22.0
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
            40.0,
            175.0,
            110.0,
            22.0
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
            40.0,
            210.0,
            240.0,
            22.0
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
            40.0,
            250.0,
            485.0,
            22.0
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
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            197.0,
            143.0,
            205.0,
            20.0
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
            40.0,
            282.0,
            350.0,
            20.0
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
            40.0,
            330.0,
            292.0,
            22.0
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
            350.0,
            330.0,
            150.0,
            22.0
          ],
          "text": "print qmw.host.density"
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16.0,
          "id": "obj-13",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            40.0,
            390.0,
            340.0,
            24.0
          ],
          "text": "2  SIXTEEN HARMONIC MODAL MONITORS"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-14",
          "maxclass": "flonum",
          "maximum": 1000.0,
          "minimum": 20.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
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
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            118.0,
            432.0,
            105.0,
            20.0
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
            40.0,
            470.0,
            55.0,
            22.0
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
            40.0,
            515.0,
            465.0,
            22.0
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
            40.0,
            545.0,
            535.0,
            20.0
          ],
          "text": "Exact harmonics dominate; quantum gaps deform them only by the explicit Harmonic Lock amount."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16.0,
          "id": "obj-19",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            570.0,
            100.0,
            310.0,
            24.0
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
            570.0,
            128.0,
            390.0,
            20.0
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
            570.0,
            175.0,
            105.0,
            22.0
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
            570.0,
            210.0,
            145.0,
            22.0
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
            570.0,
            250.0,
            68.0,
            22.0
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
            660.0,
            250.0,
            68.0,
            22.0
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
            660.0,
            285.0,
            42.0,
            22.0
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
            620.0,
            320.0,
            52.0,
            22.0
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
            780.0,
            175.0,
            105.0,
            22.0
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
            780.0,
            210.0,
            145.0,
            22.0
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
            870.0,
            250.0,
            42.0,
            22.0
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
            830.0,
            285.0,
            52.0,
            22.0
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
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            777.0,
            322.0,
            160.0,
            20.0
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
            570.0,
            355.0,
            450.0,
            20.0
          ],
          "text": "/state/rho includes a revision atom, removed here; /qac/rho does not."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16.0,
          "id": "obj-34",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            570.0,
            410.0,
            338.0,
            24.0
          ],
          "text": "4  COMPLEX HILBERT FEEDBACK ENGINE"
        }
      },
      {
        "box": {
          "id": "obj-35",
          "maxclass": "newobj",
          "numinlets": 7,
          "numoutlets": 4,
          "outlettype": [
            "multichannelsignal",
            "multichannelsignal",
            "",
            ""
          ],
          "patching_rect": [
            660.0,
            381.0,
            335.0,
            22.0
          ],
          "text": "qmw_density_matrix_resonator_feedback16_mc_v1"
        }
      },
      {
        "box": {
          "id": "obj-36",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            920.0,
            515.0,
            160.0,
            22.0
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
            570.0,
            545.0,
            600.0,
            20.0
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
            1.0
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
            570.0,
            610.0,
            38.0,
            38.0
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
            615.0,
            619.0,
            80.0,
            20.0
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
            570.0,
            665.0,
            38.0,
            22.0
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
            1.0
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
            720.0,
            610.0,
            38.0,
            38.0
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
            765.0,
            619.0,
            110.0,
            20.0
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
            720.0,
            665.0,
            58.0,
            22.0
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
            720.0,
            705.0,
            38.0,
            22.0
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
            790.0,
            665.0,
            38.0,
            22.0
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
            1125.0,
            665.0,
            52.0,
            22.0
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
            1.0
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
            930.0,
            610.0,
            38.0,
            38.0
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
            975.0,
            619.0,
            115.0,
            20.0
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
            930.0,
            665.0,
            42.0,
            22.0
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
            930.0,
            705.0,
            42.0,
            22.0
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
            985.0,
            705.0,
            30.0,
            22.0
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
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1158.0,
            615.0,
            150.0,
            20.0
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
            1120.0,
            705.0,
            35.0,
            22.0
          ],
          "text": "test"
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16.0,
          "id": "obj-55",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            40.0,
            610.0,
            230.0,
            24.0
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
            40.0,
            665.0,
            175.0,
            22.0
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
            40.0,
            705.0,
            72.0,
            22.0
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
            40.0,
            745.0,
            130.0,
            22.0
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
            40.0,
            785.0,
            85.0,
            22.0
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
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            105.0,
            850.0,
            570.0,
            20.0
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
            40.0,
            900.0,
            520.0,
            20.0
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
            1300.0,
            100.0,
            60.0,
            22.0
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
            1300.0,
            140.0,
            58.0,
            22.0
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
            1300.0,
            180.0,
            38.0,
            22.0
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
            1350.0,
            180.0,
            92.0,
            22.0
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
            1450.0,
            180.0,
            38.0,
            22.0
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
            1230.0,
            220.0,
            430.0,
            20.0
          ],
          "text": "Boot is silent, RAW, identity rho, zero feedback. DSP never starts automatically."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 13.0,
          "id": "obj-69",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            570.0,
            445.0,
            662.0,
            21.0
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
            530.0,
            476.0,
            647.0,
            33.0
          ],
          "text": "To inspect it: double-click the feedback abstraction below, then double-click qmw_density_matrix_hilbert_operator16_mc_v1."
        }
      },
      {
        "box": {
          "fontface": 1,
          "fontsize": 16.0,
          "id": "obj-71",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1220.0,
            285.0,
            278.0,
            24.0
          ],
          "text": "MUSICAL REFERENCE CONTROLS"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-72",
          "maxclass": "flonum",
          "maximum": 1.0,
          "minimum": 0.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1220.0,
            325.0,
            70.0,
            22.0
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
            1220.0,
            355.0,
            145.0,
            22.0
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
            1300.0,
            327.0,
            310.0,
            20.0
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
          "minimum": 0.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1220.0,
            400.0,
            70.0,
            22.0
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
            1220.0,
            430.0,
            125.0,
            22.0
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
            1300.0,
            402.0,
            309.0,
            20.0
          ],
          "text": "Motion Drive: sustained breath from density-field velocity"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-78",
          "maxclass": "flonum",
          "maximum": 5000.0,
          "minimum": 25.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1220.0,
            475.0,
            78.0,
            22.0
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
            1220.0,
            505.0,
            145.0,
            22.0
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
            1308.0,
            477.0,
            319.0,
            20.0
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
          "minimum": 0.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1220.0,
            550.0,
            78.0,
            22.0
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
            1220.0,
            580.0,
            145.0,
            22.0
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
            1308.0,
            552.0,
            307.0,
            20.0
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
            1390.0,
            355.0,
            38.0,
            22.0
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
            1390.0,
            430.0,
            45.0,
            22.0
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
            1390.0,
            505.0,
            29.5,
            22.0
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
            1390.0,
            580.0,
            55.0,
            22.0
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
            1110.0,
            630.0,
            470.0,
            33.0
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
          "minimum": 0.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1260.0,
            700.0,
            70.0,
            22.0
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
            1260.0,
            730.0,
            145.0,
            22.0
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
            1340.0,
            702.0,
            250.0,
            20.0
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
            1420.0,
            730.0,
            38.0,
            22.0
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
            259.0,
            406.0,
            220.0,
            22.0
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
            230.0,
            460.0,
            390.0,
            20.0
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
            460.0,
            430.0,
            145.0,
            22.0
          ],
          "text": "print qmw.host.delays"
        }
      },
      {
        "box": {
          "id": "obj-96",
          "maxclass": "newobj",
          "text": "js qmw_coherence_feedback_gain16_v1.js",
          "numinlets": 3,
          "numoutlets": 3,
          "outlettype": [
            "",
            "float",
            ""
          ],
          "patching_rect": [
            1090.0,
            790.0,
            240.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-97",
          "maxclass": "flonum",
          "minimum": 0.0,
          "maximum": 1.0,
          "patching_rect": [
            1090.0,
            835.0,
            70.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-98",
          "maxclass": "comment",
          "fontface": 1,
          "text": "Feedback Depth (0 = fixed 0.03 baseline)",
          "patching_rect": [
            1170.0,
            837.0,
            260.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-99",
          "maxclass": "flonum",
          "patching_rect": [
            1090.0,
            875.0,
            70.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-100",
          "maxclass": "comment",
          "text": "effective bounded gain",
          "patching_rect": [
            1170.0,
            877.0,
            150.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-101",
          "maxclass": "newobj",
          "text": "print qmw.host.feedback_gain",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1340.0,
            790.0,
            185.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-102",
          "maxclass": "message",
          "text": "0.5",
          "patching_rect": [
            1450.0,
            835.0,
            35.0,
            22.0
          ],
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "obj-103",
          "maxclass": "comment",
          "text": "gain = 0.03 + Depth * 0.09 * coherence * (1 - 0.6 entropy), capped at 0.15",
          "patching_rect": [
            1090.0,
            915.0,
            465.0,
            20.0
          ]
        }
      }
    ],
    "lines": [
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
            "obj-35",
            1
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
            "obj-35",
            2
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
            "obj-35",
            1
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
            "obj-35",
            2
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
            "obj-6",
            0
          ],
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
            "obj-64",
            0
          ],
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
            "obj-84",
            0
          ],
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
            "obj-85",
            0
          ],
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
            "obj-86",
            0
          ],
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
            "obj-87",
            0
          ],
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
            "obj-92",
            0
          ],
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
          "source": [
            "obj-67",
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
            "obj-99",
            0
          ],
          "source": [
            "obj-93",
            1
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
            "obj-96",
            0
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
            "obj-96",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-97",
            0
          ],
          "destination": [
            "obj-96",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-96",
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
            "obj-96",
            1
          ],
          "destination": [
            "obj-99",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-96",
            2
          ],
          "destination": [
            "obj-101",
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
            "obj-96",
            0
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
            "obj-102",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-102",
            0
          ],
          "destination": [
            "obj-97",
            0
          ]
        }
      }
    ],
    "originid": "pat-195",
    "dependency_cache": [
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
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
        "name": "qmw_density_matrix_hilbert_operator16_mc_v1.maxpat",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "JSON",
        "implicit": 1
      },
      {
        "name": "qmw_density_matrix_resonator_feedback16_mc_v1.maxpat",
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
        "name": "qmw_coherence_feedback_gain16_v1.js",
        "type": "TEXT",
        "implicit": 1
      }
    ],
    "autosave": 0
  }
}
