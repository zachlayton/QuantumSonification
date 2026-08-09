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
      40.0,
      1040.0,
      815.0
    ],
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
            28.0,
            18.0,
            780.0,
            28.0
          ],
          "text": "QMW PAULI STATE INSTRUMENT v1 \u2014 THE COMPLETE ADDRESS",
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            28.0,
            49.0,
            1010.0,
            38.0
          ],
          "text": "Six 2p states are individually addressed by (n,l,m_l,m_s). Every line is produced by quadrature carrier x state-modulator multiplication, with one selected sideband per occupied address."
        }
      },
      {
        "box": {
          "id": "ledger_title",
          "maxclass": "comment",
          "patching_rect": [
            28.0,
            100.0,
            360.0,
            22.0
          ],
          "text": "FERMIONIC STATE LEDGER \u2014 click an address to toggle it",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "state0",
          "maxclass": "message",
          "patching_rect": [
            28.0,
            135.0,
            150.0,
            22.0
          ],
          "text": "toggle 0",
          "annotation": "(2,1,-1,down)",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "label0",
          "maxclass": "comment",
          "patching_rect": [
            28.0,
            159.0,
            150.0,
            20.0
          ],
          "text": "(2,1,-1,down)"
        }
      },
      {
        "box": {
          "id": "state1",
          "maxclass": "message",
          "patching_rect": [
            188.0,
            135.0,
            150.0,
            22.0
          ],
          "text": "toggle 1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "label1",
          "maxclass": "comment",
          "patching_rect": [
            188.0,
            159.0,
            150.0,
            20.0
          ],
          "text": "(2,1,-1,up)"
        }
      },
      {
        "box": {
          "id": "state2",
          "maxclass": "message",
          "patching_rect": [
            348.0,
            135.0,
            150.0,
            22.0
          ],
          "text": "toggle 2",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "label2",
          "maxclass": "comment",
          "patching_rect": [
            348.0,
            159.0,
            150.0,
            20.0
          ],
          "text": "(2,1,0,down)"
        }
      },
      {
        "box": {
          "id": "state3",
          "maxclass": "message",
          "patching_rect": [
            508.0,
            135.0,
            150.0,
            22.0
          ],
          "text": "toggle 3",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "label3",
          "maxclass": "comment",
          "patching_rect": [
            508.0,
            159.0,
            150.0,
            20.0
          ],
          "text": "(2,1,0,up)"
        }
      },
      {
        "box": {
          "id": "state4",
          "maxclass": "message",
          "patching_rect": [
            668.0,
            135.0,
            150.0,
            22.0
          ],
          "text": "toggle 4",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "label4",
          "maxclass": "comment",
          "patching_rect": [
            668.0,
            159.0,
            150.0,
            20.0
          ],
          "text": "(2,1,1,down)"
        }
      },
      {
        "box": {
          "id": "state5",
          "maxclass": "message",
          "patching_rect": [
            828.0,
            135.0,
            150.0,
            22.0
          ],
          "text": "toggle 5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "label5",
          "maxclass": "comment",
          "patching_rect": [
            828.0,
            159.0,
            150.0,
            20.0
          ],
          "text": "(2,1,1,up)"
        }
      },
      {
        "box": {
          "id": "fill",
          "maxclass": "message",
          "patching_rect": [
            28.0,
            195.0,
            78.0,
            22.0
          ],
          "text": "fill",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "clear",
          "maxclass": "message",
          "patching_rect": [
            116.0,
            195.0,
            78.0,
            22.0
          ],
          "text": "clear",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "exclude",
          "maxclass": "message",
          "patching_rect": [
            204.0,
            195.0,
            105.0,
            22.0
          ],
          "text": "occupy 0",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "exclude_note",
          "maxclass": "comment",
          "patching_rect": [
            320.0,
            196.0,
            350.0,
            20.0
          ],
          "text": "attempt duplicate occupation after filling the shell"
        }
      },
      {
        "box": {
          "id": "occupancy",
          "maxclass": "multislider",
          "patching_rect": [
            680.0,
            192.0,
            298.0,
            36.0
          ],
          "size": 6,
          "setminmax": [
            0.0,
            1.0
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
          "id": "field_label",
          "maxclass": "comment",
          "patching_rect": [
            28.0,
            253.0,
            120.0,
            20.0
          ],
          "text": "magnetic field B"
        }
      },
      {
        "box": {
          "id": "field",
          "maxclass": "flonum",
          "patching_rect": [
            150.0,
            250.0,
            80.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 20.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "field_pre",
          "maxclass": "newobj",
          "patching_rect": [
            240.0,
            250.0,
            90.0,
            22.0
          ],
          "text": "prepend field",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "base_label",
          "maxclass": "comment",
          "patching_rect": [
            350.0,
            253.0,
            90.0,
            20.0
          ],
          "text": "base Hz"
        }
      },
      {
        "box": {
          "id": "base",
          "maxclass": "flonum",
          "patching_rect": [
            430.0,
            250.0,
            80.0,
            22.0
          ],
          "minimum": 30.0,
          "maximum": 8000.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "base_pre",
          "maxclass": "newobj",
          "patching_rect": [
            520.0,
            250.0,
            88.0,
            22.0
          ],
          "text": "prepend base",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "orb_label",
          "maxclass": "comment",
          "patching_rect": [
            628.0,
            253.0,
            96.0,
            20.0
          ],
          "text": "orbital Hz"
        }
      },
      {
        "box": {
          "id": "orb",
          "maxclass": "flonum",
          "patching_rect": [
            718.0,
            250.0,
            72.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 1000.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "orb_pre",
          "maxclass": "newobj",
          "patching_rect": [
            800.0,
            250.0,
            98.0,
            22.0
          ],
          "text": "prepend orbital",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "zee_label",
          "maxclass": "comment",
          "patching_rect": [
            28.0,
            291.0,
            120.0,
            20.0
          ],
          "text": "audible Zeeman Hz/T"
        }
      },
      {
        "box": {
          "id": "zee",
          "maxclass": "flonum",
          "patching_rect": [
            150.0,
            288.0,
            80.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 1000.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "zee_pre",
          "maxclass": "newobj",
          "patching_rect": [
            240.0,
            288.0,
            102.0,
            22.0
          ],
          "text": "prepend zeeman",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "raw_label",
          "maxclass": "comment",
          "patching_rect": [
            370.0,
            291.0,
            115.0,
            20.0
          ],
          "text": "raw RM blend"
        }
      },
      {
        "box": {
          "id": "raw",
          "maxclass": "flonum",
          "patching_rect": [
            480.0,
            288.0,
            80.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 1.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "raw_pre",
          "maxclass": "newobj",
          "patching_rect": [
            570.0,
            288.0,
            88.0,
            22.0
          ],
          "text": "prepend raw",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "index_label",
          "maxclass": "comment",
          "patching_rect": [
            675.0,
            291.0,
            80.0,
            20.0
          ],
          "text": "FM index"
        }
      },
      {
        "box": {
          "id": "index",
          "maxclass": "flonum",
          "patching_rect": [
            750.0,
            288.0,
            70.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 12.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "index_pre",
          "maxclass": "newobj",
          "patching_rect": [
            830.0,
            288.0,
            98.0,
            22.0
          ],
          "text": "prepend index",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spin_title",
          "maxclass": "comment",
          "patching_rect": [
            28.0,
            338.0,
            500.0,
            22.0
          ],
          "text": "SPINOR INTERFERENCE \u2014 2pi changes sign; 4pi returns",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "rotate_label",
          "maxclass": "comment",
          "patching_rect": [
            28.0,
            376.0,
            110.0,
            20.0
          ],
          "text": "rotation degrees"
        }
      },
      {
        "box": {
          "id": "rotate",
          "maxclass": "flonum",
          "patching_rect": [
            140.0,
            373.0,
            90.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 720.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "rotate_pre",
          "maxclass": "newobj",
          "patching_rect": [
            240.0,
            373.0,
            98.0,
            22.0
          ],
          "text": "prepend rotate",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "rotate_sweep",
          "maxclass": "message",
          "patching_rect": [
            350.0,
            373.0,
            138.0,
            22.0
          ],
          "text": "0., 720. 16000",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "rotate_line",
          "maxclass": "newobj",
          "patching_rect": [
            500.0,
            373.0,
            38.0,
            22.0
          ],
          "text": "line",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spin_note",
          "maxclass": "comment",
          "patching_rect": [
            560.0,
            367.0,
            418.0,
            36.0
          ],
          "text": "110 Hz reference-interference tone: full at 0 deg, silent at 360 deg, restored at 720 deg."
        }
      },
      {
        "box": {
          "id": "anti_title",
          "maxclass": "comment",
          "patching_rect": [
            28.0,
            425.0,
            500.0,
            22.0
          ],
          "text": "ANTISYMMETRIC TWO-FERMION NORM",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "overlap_label",
          "maxclass": "comment",
          "patching_rect": [
            28.0,
            463.0,
            110.0,
            20.0
          ],
          "text": "state overlap"
        }
      },
      {
        "box": {
          "id": "overlap",
          "maxclass": "flonum",
          "patching_rect": [
            140.0,
            460.0,
            90.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 1.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "overlap_pre",
          "maxclass": "newobj",
          "patching_rect": [
            240.0,
            460.0,
            105.0,
            22.0
          ],
          "text": "prepend overlap",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "overlap_sweep",
          "maxclass": "message",
          "patching_rect": [
            360.0,
            460.0,
            125.0,
            22.0
          ],
          "text": "0., 1. 10000",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "overlap_line",
          "maxclass": "newobj",
          "patching_rect": [
            500.0,
            460.0,
            38.0,
            22.0
          ],
          "text": "line",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "anti_note",
          "maxclass": "comment",
          "patching_rect": [
            560.0,
            454.0,
            418.0,
            36.0
          ],
          "text": "330 Hz Slater-wedge tone: amplitude sqrt(1-|overlap|^2); identical one-particle states force silence."
        }
      },
      {
        "box": {
          "id": "controller",
          "maxclass": "newobj",
          "patching_rect": [
            28.0,
            520.0,
            258.0,
            22.0
          ],
          "text": "js qmw_pauli_state_controller_v1.js",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
            "",
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            305.0,
            520.0,
            673.0,
            22.0
          ],
          "text": "initializing complete-state ledger...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "poly",
          "maxclass": "newobj",
          "patching_rect": [
            28.0,
            575.0,
            285.0,
            22.0
          ],
          "text": "poly~ qmw_pauli_state_voice_v1 6 @parallel 1",
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
          "id": "spin_amp_pack",
          "maxclass": "newobj",
          "patching_rect": [
            335.0,
            575.0,
            75.0,
            22.0
          ],
          "text": "pack f 30",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spin_amp_line",
          "maxclass": "newobj",
          "patching_rect": [
            420.0,
            575.0,
            42.0,
            22.0
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "spin_osc",
          "maxclass": "newobj",
          "patching_rect": [
            475.0,
            575.0,
            72.0,
            22.0
          ],
          "text": "cycle~ 110.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "spin_gain",
          "maxclass": "newobj",
          "patching_rect": [
            560.0,
            575.0,
            36.0,
            22.0
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "anti_amp_pack",
          "maxclass": "newobj",
          "patching_rect": [
            620.0,
            575.0,
            75.0,
            22.0
          ],
          "text": "pack f 30",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "anti_amp_line",
          "maxclass": "newobj",
          "patching_rect": [
            705.0,
            575.0,
            42.0,
            22.0
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "anti_osc",
          "maxclass": "newobj",
          "patching_rect": [
            760.0,
            575.0,
            72.0,
            22.0
          ],
          "text": "cycle~ 330.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "anti_gain",
          "maxclass": "newobj",
          "patching_rect": [
            845.0,
            575.0,
            36.0,
            22.0
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "sum_l1",
          "maxclass": "newobj",
          "patching_rect": [
            130.0,
            625.0,
            36.0,
            22.0
          ],
          "text": "+~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "sum_l2",
          "maxclass": "newobj",
          "patching_rect": [
            180.0,
            625.0,
            36.0,
            22.0
          ],
          "text": "+~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "sum_r1",
          "maxclass": "newobj",
          "patching_rect": [
            255.0,
            625.0,
            36.0,
            22.0
          ],
          "text": "+~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "sum_r2",
          "maxclass": "newobj",
          "patching_rect": [
            305.0,
            625.0,
            36.0,
            22.0
          ],
          "text": "+~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "master_label",
          "maxclass": "comment",
          "patching_rect": [
            380.0,
            628.0,
            90.0,
            20.0
          ],
          "text": "master"
        }
      },
      {
        "box": {
          "id": "master",
          "maxclass": "flonum",
          "patching_rect": [
            445.0,
            625.0,
            72.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 0.5,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "master_pack",
          "maxclass": "newobj",
          "patching_rect": [
            530.0,
            625.0,
            75.0,
            22.0
          ],
          "text": "pack f 30",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "master_line",
          "maxclass": "newobj",
          "patching_rect": [
            615.0,
            625.0,
            42.0,
            22.0
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "master_l",
          "maxclass": "newobj",
          "patching_rect": [
            180.0,
            670.0,
            36.0,
            22.0
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "master_r",
          "maxclass": "newobj",
          "patching_rect": [
            305.0,
            670.0,
            36.0,
            22.0
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "clip_l",
          "maxclass": "newobj",
          "patching_rect": [
            180.0,
            707.0,
            82.0,
            22.0
          ],
          "text": "clip~ -0.95 0.95",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "clip_r",
          "maxclass": "newobj",
          "patching_rect": [
            305.0,
            707.0,
            82.0,
            22.0
          ],
          "text": "clip~ -0.95 0.95",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "meter_l",
          "maxclass": "meter~",
          "patching_rect": [
            420.0,
            675.0,
            18.0,
            70.0
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "meter_r",
          "maxclass": "meter~",
          "patching_rect": [
            450.0,
            675.0,
            18.0,
            70.0
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "ezdac~",
          "patching_rect": [
            500.0,
            685.0,
            52.0,
            52.0
          ],
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "footer",
          "maxclass": "comment",
          "patching_rect": [
            590.0,
            680.0,
            388.0,
            60.0
          ],
          "text": "Each shell voice is a true quadrature SSB ring modulator. The factor m_l + 2m_s controls its signed displacement from the carrier."
        }
      },
      {
        "box": {
          "id": "init_fill",
          "maxclass": "newobj",
          "patching_rect": [
            28.0,
            755.0,
            82.0,
            22.0
          ],
          "text": "loadmess fill",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_field",
          "maxclass": "newobj",
          "patching_rect": [
            120.0,
            755.0,
            88.0,
            22.0
          ],
          "text": "loadmess 1.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_base",
          "maxclass": "newobj",
          "patching_rect": [
            218.0,
            755.0,
            98.0,
            22.0
          ],
          "text": "loadmess 220.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_orb",
          "maxclass": "newobj",
          "patching_rect": [
            326.0,
            755.0,
            92.0,
            22.0
          ],
          "text": "loadmess 24.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_zee",
          "maxclass": "newobj",
          "patching_rect": [
            428.0,
            755.0,
            92.0,
            22.0
          ],
          "text": "loadmess 30.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_raw",
          "maxclass": "newobj",
          "patching_rect": [
            530.0,
            755.0,
            88.0,
            22.0
          ],
          "text": "loadmess 1.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_index",
          "maxclass": "newobj",
          "patching_rect": [
            628.0,
            755.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_rotate",
          "maxclass": "newobj",
          "patching_rect": [
            726.0,
            755.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_overlap",
          "maxclass": "newobj",
          "patching_rect": [
            824.0,
            755.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_master",
          "maxclass": "newobj",
          "patching_rect": [
            922.0,
            755.0,
            96.0,
            22.0
          ],
          "text": "loadmess 0.16",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "state0",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "state1",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "state2",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "state3",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "state4",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "state5",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fill",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clear",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "exclude",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field",
            0
          ],
          "destination": [
            "field_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_pre",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "base",
            0
          ],
          "destination": [
            "base_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "base_pre",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "orb",
            0
          ],
          "destination": [
            "orb_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "orb_pre",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "zee",
            0
          ],
          "destination": [
            "zee_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "zee_pre",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "raw",
            0
          ],
          "destination": [
            "raw_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "raw_pre",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "index",
            0
          ],
          "destination": [
            "index_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "index_pre",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rotate",
            0
          ],
          "destination": [
            "rotate_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rotate_pre",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rotate_sweep",
            0
          ],
          "destination": [
            "rotate_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rotate_line",
            0
          ],
          "destination": [
            "rotate",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "overlap",
            0
          ],
          "destination": [
            "overlap_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "overlap_pre",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "overlap_sweep",
            0
          ],
          "destination": [
            "overlap_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "overlap_line",
            0
          ],
          "destination": [
            "overlap",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "controller",
            0
          ],
          "destination": [
            "poly",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "controller",
            1
          ],
          "destination": [
            "occupancy",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "controller",
            2
          ],
          "destination": [
            "spin_amp_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_amp_pack",
            0
          ],
          "destination": [
            "spin_amp_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_osc",
            0
          ],
          "destination": [
            "spin_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_amp_line",
            0
          ],
          "destination": [
            "spin_gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "controller",
            3
          ],
          "destination": [
            "anti_amp_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "anti_amp_pack",
            0
          ],
          "destination": [
            "anti_amp_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "anti_osc",
            0
          ],
          "destination": [
            "anti_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "anti_amp_line",
            0
          ],
          "destination": [
            "anti_gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "controller",
            4
          ],
          "destination": [
            "status",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "poly",
            0
          ],
          "destination": [
            "sum_l1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_gain",
            0
          ],
          "destination": [
            "sum_l1",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sum_l1",
            0
          ],
          "destination": [
            "sum_l2",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "anti_gain",
            0
          ],
          "destination": [
            "sum_l2",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "poly",
            1
          ],
          "destination": [
            "sum_r1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_gain",
            0
          ],
          "destination": [
            "sum_r1",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sum_r1",
            0
          ],
          "destination": [
            "sum_r2",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "anti_gain",
            0
          ],
          "destination": [
            "sum_r2",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "master",
            0
          ],
          "destination": [
            "master_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "master_pack",
            0
          ],
          "destination": [
            "master_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sum_l2",
            0
          ],
          "destination": [
            "master_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "master_line",
            0
          ],
          "destination": [
            "master_l",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sum_r2",
            0
          ],
          "destination": [
            "master_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "master_line",
            0
          ],
          "destination": [
            "master_r",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "master_l",
            0
          ],
          "destination": [
            "clip_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "master_r",
            0
          ],
          "destination": [
            "clip_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clip_l",
            0
          ],
          "destination": [
            "meter_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clip_r",
            0
          ],
          "destination": [
            "meter_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clip_l",
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
            "clip_r",
            0
          ],
          "destination": [
            "dac",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_fill",
            0
          ],
          "destination": [
            "controller",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_field",
            0
          ],
          "destination": [
            "field",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_base",
            0
          ],
          "destination": [
            "base",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_orb",
            0
          ],
          "destination": [
            "orb",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_zee",
            0
          ],
          "destination": [
            "zee",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_raw",
            0
          ],
          "destination": [
            "raw",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_index",
            0
          ],
          "destination": [
            "index",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_rotate",
            0
          ],
          "destination": [
            "rotate",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_overlap",
            0
          ],
          "destination": [
            "overlap",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_master",
            0
          ],
          "destination": [
            "master",
            0
          ]
        }
      }
    ],
    "autosave": 0,
    "dependency_cache": [
      {
        "name": "qmw_pauli_state_controller_v1.js",
        "type": "TEXT"
      },
      {
        "name": "qmw_pauli_state_voice_v1.maxpat",
        "type": "JSON"
      }
    ]
  }
}
