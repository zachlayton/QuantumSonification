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
      80,
      60,
      1080,
      830
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
            28,
            18,
            900,
            30
          ],
          "text": "QMW QPE SYNTHESIZER v1 \u2014 LISTEN TO PHASE COLLAPSE",
          "fontsize": 18
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            28,
            50,
            1010,
            38
          ],
          "text": "A trial-state superposition enters finite-register Quantum Phase Estimation. Each clock pulse measures one phase bin and voices the collapsed eigenstate."
        }
      },
      {
        "box": {
          "id": "run_label",
          "maxclass": "comment",
          "patching_rect": [
            28,
            105,
            80,
            20
          ],
          "text": "RUN SHOTS"
        }
      },
      {
        "box": {
          "id": "run",
          "maxclass": "toggle",
          "patching_rect": [
            110,
            102,
            24,
            24
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
          "id": "metro",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            103,
            78,
            22
          ],
          "text": "metro 240",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "manual",
          "maxclass": "button",
          "patching_rect": [
            235,
            102,
            24,
            24
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "manual_label",
          "maxclass": "comment",
          "patching_rect": [
            266,
            105,
            88,
            20
          ],
          "text": "single shot"
        }
      },
      {
        "box": {
          "id": "tempo_label",
          "maxclass": "comment",
          "patching_rect": [
            370,
            105,
            85,
            20
          ],
          "text": "interval ms"
        }
      },
      {
        "box": {
          "id": "tempo",
          "maxclass": "number",
          "patching_rect": [
            455,
            102,
            70,
            22
          ],
          "minimum": 40,
          "maximum": 2000,
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
          "id": "bits_label",
          "maxclass": "comment",
          "patching_rect": [
            560,
            105,
            115,
            20
          ],
          "text": "estimation qubits"
        }
      },
      {
        "box": {
          "id": "bits",
          "maxclass": "number",
          "patching_rect": [
            680,
            102,
            60,
            22
          ],
          "minimum": 2,
          "maximum": 10,
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
          "id": "bits_pre",
          "maxclass": "newobj",
          "patching_rect": [
            750,
            102,
            112,
            22
          ],
          "text": "prepend precision",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "phase_title",
          "maxclass": "comment",
          "patching_rect": [
            28,
            157,
            460,
            24
          ],
          "text": "UNITARY EIGENPHASES  \u03c6j",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "phases",
          "maxclass": "multislider",
          "patching_rect": [
            28,
            187,
            480,
            105
          ],
          "size": 4,
          "setminmax": [
            0.0,
            1.0
          ],
          "setstyle": 1,
          "spacing": 8,
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
          "id": "phases_pre",
          "maxclass": "newobj",
          "patching_rect": [
            28,
            300,
            112,
            22
          ],
          "text": "prepend setphases",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "weight_title",
          "maxclass": "comment",
          "patching_rect": [
            540,
            157,
            460,
            24
          ],
          "text": "TRIAL-STATE BORN WEIGHTS  |cj|\u00b2",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "weights",
          "maxclass": "multislider",
          "patching_rect": [
            540,
            187,
            480,
            105
          ],
          "size": 4,
          "setminmax": [
            0.0,
            1.0
          ],
          "setstyle": 1,
          "spacing": 8,
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
          "id": "weights_pre",
          "maxclass": "newobj",
          "patching_rect": [
            540,
            300,
            120,
            22
          ],
          "text": "prepend setweights",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "mapping",
          "maxclass": "comment",
          "patching_rect": [
            28,
            352,
            210,
            24
          ],
          "text": "PHASE \u2192 PITCH MAPPING",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "root_label",
          "maxclass": "comment",
          "patching_rect": [
            28,
            390,
            75,
            20
          ],
          "text": "root Hz"
        }
      },
      {
        "box": {
          "id": "root",
          "maxclass": "flonum",
          "patching_rect": [
            105,
            387,
            75,
            22
          ],
          "minimum": 20.0,
          "maximum": 440.0,
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
          "id": "root_pre",
          "maxclass": "newobj",
          "patching_rect": [
            190,
            387,
            88,
            22
          ],
          "text": "prepend root",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "span_label",
          "maxclass": "comment",
          "patching_rect": [
            305,
            390,
            95,
            20
          ],
          "text": "span octaves"
        }
      },
      {
        "box": {
          "id": "span",
          "maxclass": "flonum",
          "patching_rect": [
            405,
            387,
            70,
            22
          ],
          "minimum": 0.5,
          "maximum": 7.0,
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
          "id": "span_pre",
          "maxclass": "newobj",
          "patching_rect": [
            485,
            387,
            88,
            22
          ],
          "text": "prepend span",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "dist_title",
          "maxclass": "comment",
          "patching_rect": [
            610,
            352,
            410,
            24
          ],
          "text": "CONDITIONAL PHASE-REGISTER DISTRIBUTION",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "distribution",
          "maxclass": "multislider",
          "patching_rect": [
            610,
            382,
            410,
            85
          ],
          "size": 1024,
          "setminmax": [
            0.0,
            1.0
          ],
          "setstyle": 1,
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
          "id": "js",
          "maxclass": "newobj",
          "patching_rect": [
            28,
            448,
            150,
            22
          ],
          "text": "js qpe_controller.js",
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
          "id": "freq_smooth",
          "maxclass": "newobj",
          "patching_rect": [
            28,
            490,
            82,
            22
          ],
          "text": "pack f 12",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "freq_line",
          "maxclass": "newobj",
          "patching_rect": [
            28,
            520,
            42,
            22
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
          "id": "osc1",
          "maxclass": "newobj",
          "patching_rect": [
            28,
            558,
            88,
            22
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
          "id": "ratio",
          "maxclass": "newobj",
          "patching_rect": [
            135,
            490,
            54,
            22
          ],
          "text": "* 2.01",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "ratio_smooth",
          "maxclass": "newobj",
          "patching_rect": [
            135,
            520,
            82,
            22
          ],
          "text": "pack f 12",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "ratio_line",
          "maxclass": "newobj",
          "patching_rect": [
            135,
            550,
            42,
            22
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
          "id": "osc2",
          "maxclass": "newobj",
          "patching_rect": [
            135,
            580,
            88,
            22
          ],
          "text": "cycle~ 220.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "osc2_gain",
          "maxclass": "newobj",
          "patching_rect": [
            135,
            615,
            42,
            22
          ],
          "text": "*~ 0.28",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "mix",
          "maxclass": "newobj",
          "patching_rect": [
            65,
            650,
            38,
            22
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
          "id": "env_message",
          "maxclass": "message",
          "patching_rect": [
            260,
            490,
            150,
            22
          ],
          "text": "$1 7, 0. 360 7",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "env",
          "maxclass": "newobj",
          "patching_rect": [
            260,
            520,
            42,
            22
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
          "id": "amp",
          "maxclass": "newobj",
          "patching_rect": [
            65,
            686,
            38,
            22
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
          "id": "pan_l",
          "maxclass": "newobj",
          "patching_rect": [
            335,
            600,
            160,
            22
          ],
          "text": "expr sqrt((1.-$f1)*0.5)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pan_r",
          "maxclass": "newobj",
          "patching_rect": [
            505,
            600,
            160,
            22
          ],
          "text": "expr sqrt((1.+$f1)*0.5)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "left",
          "maxclass": "newobj",
          "patching_rect": [
            260,
            686,
            38,
            22
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
          "id": "right",
          "maxclass": "newobj",
          "patching_rect": [
            370,
            686,
            38,
            22
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
          "id": "gain",
          "maxclass": "live.gain~",
          "patching_rect": [
            480,
            650,
            130,
            72
          ],
          "numinlets": 2,
          "numoutlets": 5,
          "outlettype": [
            "signal",
            "signal",
            "",
            "float",
            "list"
          ]
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "newobj",
          "patching_rect": [
            650,
            686,
            72,
            22
          ],
          "text": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "comment",
          "patching_rect": [
            28,
            752,
            992,
            38
          ],
          "text": "READY",
          "fontsize": 12
        }
      },
      {
        "box": {
          "id": "load",
          "maxclass": "newobj",
          "patching_rect": [
            880,
            102,
            60,
            22
          ],
          "text": "loadbang",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "defaults",
          "maxclass": "message",
          "patching_rect": [
            880,
            130,
            165,
            22
          ],
          "text": "240 5 55. 4.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "unpack",
          "maxclass": "newobj",
          "patching_rect": [
            880,
            158,
            150,
            22
          ],
          "text": "unpack i i f f",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "int",
            "int",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "phase_default",
          "maxclass": "message",
          "patching_rect": [
            880,
            188,
            158,
            22
          ],
          "text": "0.125 0.301 0.547 0.823",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "weight_default",
          "maxclass": "message",
          "patching_rect": [
            880,
            218,
            158,
            22
          ],
          "text": "0.42 0.27 0.20 0.11",
          "numinlets": 2,
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
            "run",
            0
          ],
          "destination": [
            "metro",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "tempo",
            0
          ],
          "destination": [
            "metro",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "metro",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "manual",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "bits",
            0
          ],
          "destination": [
            "bits_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "bits_pre",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phases",
            0
          ],
          "destination": [
            "phases_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phases_pre",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "weights",
            0
          ],
          "destination": [
            "weights_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "weights_pre",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "root",
            0
          ],
          "destination": [
            "root_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "root_pre",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "span",
            0
          ],
          "destination": [
            "span_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "span_pre",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            0
          ],
          "destination": [
            "freq_smooth",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq_smooth",
            0
          ],
          "destination": [
            "freq_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq_line",
            0
          ],
          "destination": [
            "osc1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            0
          ],
          "destination": [
            "ratio",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ratio",
            0
          ],
          "destination": [
            "ratio_smooth",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ratio_smooth",
            0
          ],
          "destination": [
            "ratio_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ratio_line",
            0
          ],
          "destination": [
            "osc2",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "osc2",
            0
          ],
          "destination": [
            "osc2_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "osc1",
            0
          ],
          "destination": [
            "mix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "osc2_gain",
            0
          ],
          "destination": [
            "mix",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            1
          ],
          "destination": [
            "env_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env_message",
            0
          ],
          "destination": [
            "env",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mix",
            0
          ],
          "destination": [
            "amp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env",
            0
          ],
          "destination": [
            "amp",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            2
          ],
          "destination": [
            "distribution",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            3
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
            "js",
            4
          ],
          "destination": [
            "pan_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            4
          ],
          "destination": [
            "pan_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp",
            0
          ],
          "destination": [
            "left",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan_l",
            0
          ],
          "destination": [
            "left",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp",
            0
          ],
          "destination": [
            "right",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan_r",
            0
          ],
          "destination": [
            "right",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "left",
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
            "right",
            0
          ],
          "destination": [
            "gain",
            1
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
            1
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
            "load",
            0
          ],
          "destination": [
            "defaults",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "defaults",
            0
          ],
          "destination": [
            "unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            0
          ],
          "destination": [
            "tempo",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            1
          ],
          "destination": [
            "bits",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            2
          ],
          "destination": [
            "root",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            3
          ],
          "destination": [
            "span",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "phase_default",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_default",
            0
          ],
          "destination": [
            "phases",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "weight_default",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "weight_default",
            0
          ],
          "destination": [
            "weights",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "qpe_controller.js",
        "type": "TEXT",
        "implicit": 1
      }
    ],
    "autosave": 0
  }
}
