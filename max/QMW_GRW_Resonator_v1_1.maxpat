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
      60,
      50,
      1160,
      850
    ],
    "gridsize": [
      15,
      15
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            15,
            820,
            25
          ],
          "text": "QMW GRW Resonator v1 \u2014 four committed-state branches",
          "fontsize": 16
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            25,
            44,
            1080,
            36
          ],
          "text": "trace distance \u2192 amplitude | coherence loss \u2192 bandwidth/grains | qubit \u2192 branch | Pauli delta \u2192 orientation | rho+ \u2192 persistent condition"
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            92,
            115,
            22
          ],
          "text": "udpreceive 7400",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "route_root",
          "maxclass": "newobj",
          "patching_rect": [
            155,
            92,
            245,
            22
          ],
          "text": "OSC-route /qmw/grw/sonification",
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
          "id": "route",
          "maxclass": "newobj",
          "patching_rect": [
            415,
            92,
            535,
            22
          ],
          "text": "OSC-route /event /post/branch_levels /post/population /post/rho_magnitude /pauli",
          "numinlets": 1,
          "numoutlets": 6,
          "outlettype": [
            "",
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
          "id": "pre_event",
          "maxclass": "newobj",
          "patching_rect": [
            415,
            128,
            95,
            22
          ],
          "text": "prepend event",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_levels",
          "maxclass": "newobj",
          "patching_rect": [
            520,
            128,
            145,
            22
          ],
          "text": "prepend branch_levels",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_pop",
          "maxclass": "newobj",
          "patching_rect": [
            675,
            128,
            120,
            22
          ],
          "text": "prepend population",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_rho",
          "maxclass": "newobj",
          "patching_rect": [
            805,
            128,
            145,
            22
          ],
          "text": "prepend rho_magnitude",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_pauli",
          "maxclass": "newobj",
          "patching_rect": [
            960,
            128,
            95,
            22
          ],
          "text": "prepend pauli",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "js",
          "maxclass": "newobj",
          "patching_rect": [
            415,
            168,
            220,
            22
          ],
          "text": "js qmw_grw_sonification_v1.js",
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
          ]
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            650,
            168,
            445,
            22
          ],
          "text": "waiting for a committed GRW event...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pop_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            660,
            160,
            20
          ],
          "text": "rho+ populations"
        }
      },
      {
        "box": {
          "id": "population",
          "maxclass": "multislider",
          "patching_rect": [
            180,
            650,
            650,
            58
          ],
          "size": 16,
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
          "id": "levels_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            727,
            160,
            20
          ],
          "text": "rho+ branch levels"
        }
      },
      {
        "box": {
          "id": "levels",
          "maxclass": "multislider",
          "patching_rect": [
            180,
            718,
            650,
            58
          ],
          "size": 4,
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
          "id": "gain",
          "maxclass": "gain~",
          "patching_rect": [
            930,
            620,
            45,
            130
          ],
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "newobj",
          "patching_rect": [
            920,
            780,
            65,
            22
          ],
          "text": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "v0_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            220,
            245,
            20
          ],
          "text": "branch 0  |  base 55 Hz"
        }
      },
      {
        "box": {
          "id": "v0_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            248,
            165,
            22
          ],
          "text": "unpack f f f i f f",
          "numinlets": 1,
          "numoutlets": 6,
          "outlettype": [
            "float",
            "float",
            "float",
            "int",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v0_amp_delta",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            282,
            72,
            22
          ],
          "text": "pak f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v0_amp_expr",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            314,
            145,
            22
          ],
          "text": "expr $f1*(1.+abs($f2))",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v0_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            346,
            45,
            22
          ],
          "text": "t b f",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v0_click",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            382,
            45,
            22
          ],
          "text": "click~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v0_amp_sig",
          "maxclass": "newobj",
          "patching_rect": [
            83,
            382,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v0_hit_mul",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            420,
            35,
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
          "id": "v0_axis_sign",
          "maxclass": "newobj",
          "patching_rect": [
            175,
            282,
            72,
            22
          ],
          "text": "pak i f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v0_freq",
          "maxclass": "newobj",
          "patching_rect": [
            175,
            314,
            245,
            22
          ],
          "text": "expr 55 * (0.5 + 0.5 * $i1) * (1. + 0.025 * $f2)",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v0_bw_grain",
          "maxclass": "newobj",
          "patching_rect": [
            175,
            346,
            72,
            22
          ],
          "text": "pak f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v0_q",
          "maxclass": "newobj",
          "patching_rect": [
            175,
            378,
            185,
            22
          ],
          "text": "expr 5.+((1.-$f1)*195.)+($f2*20.)",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v0_reson",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            458,
            155,
            22
          ],
          "text": "reson~ 55 1. 120.",
          "numinlets": 4,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v0_post_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            492,
            90,
            22
          ],
          "text": "unpack f f f f",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "float",
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v0_post_scale",
          "maxclass": "newobj",
          "patching_rect": [
            123,
            492,
            48,
            22
          ],
          "text": "* 0.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v0_post_sig",
          "maxclass": "newobj",
          "patching_rect": [
            179,
            492,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v0_cycle",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            526,
            78,
            22
          ],
          "text": "cycle~ 55",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v0_post_mul",
          "maxclass": "newobj",
          "patching_rect": [
            113,
            526,
            35,
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
          "id": "v0_sum",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            562,
            35,
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
          "id": "v1_label",
          "maxclass": "comment",
          "patching_rect": [
            300,
            220,
            245,
            20
          ],
          "text": "branch 1  |  base 82.5 Hz"
        }
      },
      {
        "box": {
          "id": "v1_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            248,
            165,
            22
          ],
          "text": "unpack f f f i f f",
          "numinlets": 1,
          "numoutlets": 6,
          "outlettype": [
            "float",
            "float",
            "float",
            "int",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v1_amp_delta",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            282,
            72,
            22
          ],
          "text": "pak f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v1_amp_expr",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            314,
            145,
            22
          ],
          "text": "expr $f1*(1.+abs($f2))",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v1_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            346,
            45,
            22
          ],
          "text": "t b f",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v1_click",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            382,
            45,
            22
          ],
          "text": "click~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v1_amp_sig",
          "maxclass": "newobj",
          "patching_rect": [
            358,
            382,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v1_hit_mul",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            420,
            35,
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
          "id": "v1_axis_sign",
          "maxclass": "newobj",
          "patching_rect": [
            450,
            282,
            72,
            22
          ],
          "text": "pak i f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v1_freq",
          "maxclass": "newobj",
          "patching_rect": [
            450,
            314,
            245,
            22
          ],
          "text": "expr 82.5 * (0.5 + 0.5 * $i1) * (1. + 0.025 * $f2)",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v1_bw_grain",
          "maxclass": "newobj",
          "patching_rect": [
            450,
            346,
            72,
            22
          ],
          "text": "pak f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v1_q",
          "maxclass": "newobj",
          "patching_rect": [
            450,
            378,
            185,
            22
          ],
          "text": "expr 5.+((1.-$f1)*195.)+($f2*20.)",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v1_reson",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            458,
            155,
            22
          ],
          "text": "reson~ 82.5 1. 120.",
          "numinlets": 4,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v1_post_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            492,
            90,
            22
          ],
          "text": "unpack f f f f",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "float",
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v1_post_scale",
          "maxclass": "newobj",
          "patching_rect": [
            398,
            492,
            48,
            22
          ],
          "text": "* 0.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v1_post_sig",
          "maxclass": "newobj",
          "patching_rect": [
            454,
            492,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v1_cycle",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            526,
            78,
            22
          ],
          "text": "cycle~ 82.5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v1_post_mul",
          "maxclass": "newobj",
          "patching_rect": [
            388,
            526,
            35,
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
          "id": "v1_sum",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            562,
            35,
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
          "id": "v2_label",
          "maxclass": "comment",
          "patching_rect": [
            575,
            220,
            245,
            20
          ],
          "text": "branch 2  |  base 110 Hz"
        }
      },
      {
        "box": {
          "id": "v2_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            248,
            165,
            22
          ],
          "text": "unpack f f f i f f",
          "numinlets": 1,
          "numoutlets": 6,
          "outlettype": [
            "float",
            "float",
            "float",
            "int",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v2_amp_delta",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            282,
            72,
            22
          ],
          "text": "pak f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v2_amp_expr",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            314,
            145,
            22
          ],
          "text": "expr $f1*(1.+abs($f2))",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v2_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            346,
            45,
            22
          ],
          "text": "t b f",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v2_click",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            382,
            45,
            22
          ],
          "text": "click~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v2_amp_sig",
          "maxclass": "newobj",
          "patching_rect": [
            633,
            382,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v2_hit_mul",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            420,
            35,
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
          "id": "v2_axis_sign",
          "maxclass": "newobj",
          "patching_rect": [
            725,
            282,
            72,
            22
          ],
          "text": "pak i f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v2_freq",
          "maxclass": "newobj",
          "patching_rect": [
            725,
            314,
            245,
            22
          ],
          "text": "expr 110 * (0.5 + 0.5 * $i1) * (1. + 0.025 * $f2)",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v2_bw_grain",
          "maxclass": "newobj",
          "patching_rect": [
            725,
            346,
            72,
            22
          ],
          "text": "pak f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v2_q",
          "maxclass": "newobj",
          "patching_rect": [
            725,
            378,
            185,
            22
          ],
          "text": "expr 5.+((1.-$f1)*195.)+($f2*20.)",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v2_reson",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            458,
            155,
            22
          ],
          "text": "reson~ 110 1. 120.",
          "numinlets": 4,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v2_post_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            492,
            90,
            22
          ],
          "text": "unpack f f f f",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "float",
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v2_post_scale",
          "maxclass": "newobj",
          "patching_rect": [
            673,
            492,
            48,
            22
          ],
          "text": "* 0.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v2_post_sig",
          "maxclass": "newobj",
          "patching_rect": [
            729,
            492,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v2_cycle",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            526,
            78,
            22
          ],
          "text": "cycle~ 110",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v2_post_mul",
          "maxclass": "newobj",
          "patching_rect": [
            663,
            526,
            35,
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
          "id": "v2_sum",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            562,
            35,
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
          "id": "v3_label",
          "maxclass": "comment",
          "patching_rect": [
            850,
            220,
            245,
            20
          ],
          "text": "branch 3  |  base 165 Hz"
        }
      },
      {
        "box": {
          "id": "v3_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            248,
            165,
            22
          ],
          "text": "unpack f f f i f f",
          "numinlets": 1,
          "numoutlets": 6,
          "outlettype": [
            "float",
            "float",
            "float",
            "int",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v3_amp_delta",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            282,
            72,
            22
          ],
          "text": "pak f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v3_amp_expr",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            314,
            145,
            22
          ],
          "text": "expr $f1*(1.+abs($f2))",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v3_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            346,
            45,
            22
          ],
          "text": "t b f",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v3_click",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            382,
            45,
            22
          ],
          "text": "click~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v3_amp_sig",
          "maxclass": "newobj",
          "patching_rect": [
            908,
            382,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v3_hit_mul",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            420,
            35,
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
          "id": "v3_axis_sign",
          "maxclass": "newobj",
          "patching_rect": [
            1000,
            282,
            72,
            22
          ],
          "text": "pak i f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v3_freq",
          "maxclass": "newobj",
          "patching_rect": [
            1000,
            314,
            245,
            22
          ],
          "text": "expr 165 * (0.5 + 0.5 * $i1) * (1. + 0.025 * $f2)",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v3_bw_grain",
          "maxclass": "newobj",
          "patching_rect": [
            1000,
            346,
            72,
            22
          ],
          "text": "pak f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "v3_q",
          "maxclass": "newobj",
          "patching_rect": [
            1000,
            378,
            185,
            22
          ],
          "text": "expr 5.+((1.-$f1)*195.)+($f2*20.)",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v3_reson",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            458,
            155,
            22
          ],
          "text": "reson~ 165 1. 120.",
          "numinlets": 4,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v3_post_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            492,
            90,
            22
          ],
          "text": "unpack f f f f",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "float",
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v3_post_scale",
          "maxclass": "newobj",
          "patching_rect": [
            948,
            492,
            48,
            22
          ],
          "text": "* 0.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "v3_post_sig",
          "maxclass": "newobj",
          "patching_rect": [
            1004,
            492,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v3_cycle",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            526,
            78,
            22
          ],
          "text": "cycle~ 165",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "v3_post_mul",
          "maxclass": "newobj",
          "patching_rect": [
            938,
            526,
            35,
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
          "id": "v3_sum",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            562,
            35,
            22
          ],
          "text": "+~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "udp",
            0
          ],
          "destination": [
            "route_root",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_root",
            0
          ],
          "destination": [
            "route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            0
          ],
          "destination": [
            "pre_event",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            1
          ],
          "destination": [
            "pre_levels",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            2
          ],
          "destination": [
            "pre_pop",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            3
          ],
          "destination": [
            "pre_rho",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            4
          ],
          "destination": [
            "pre_pauli",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_event",
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
            "pre_levels",
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
            "pre_pop",
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
            "pre_rho",
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
            "pre_pauli",
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
            4
          ],
          "destination": [
            "levels",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            5
          ],
          "destination": [
            "population",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            7
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
      },
      {
        "patchline": {
          "source": [
            "js",
            0
          ],
          "destination": [
            "v0_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_unpack",
            5
          ],
          "destination": [
            "v0_amp_delta",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_unpack",
            0
          ],
          "destination": [
            "v0_amp_delta",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_amp_delta",
            0
          ],
          "destination": [
            "v0_amp_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_amp_expr",
            0
          ],
          "destination": [
            "v0_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_trigger",
            0
          ],
          "destination": [
            "v0_click",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_trigger",
            1
          ],
          "destination": [
            "v0_amp_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_click",
            0
          ],
          "destination": [
            "v0_hit_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_amp_sig",
            0
          ],
          "destination": [
            "v0_hit_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_unpack",
            3
          ],
          "destination": [
            "v0_axis_sign",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_unpack",
            4
          ],
          "destination": [
            "v0_axis_sign",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_axis_sign",
            0
          ],
          "destination": [
            "v0_freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_freq",
            0
          ],
          "destination": [
            "v0_reson",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_unpack",
            1
          ],
          "destination": [
            "v0_bw_grain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_unpack",
            2
          ],
          "destination": [
            "v0_bw_grain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_bw_grain",
            0
          ],
          "destination": [
            "v0_q",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_q",
            0
          ],
          "destination": [
            "v0_reson",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_hit_mul",
            0
          ],
          "destination": [
            "v0_reson",
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
            "v0_post_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_post_unpack",
            0
          ],
          "destination": [
            "v0_post_scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_post_scale",
            0
          ],
          "destination": [
            "v0_post_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_cycle",
            0
          ],
          "destination": [
            "v0_post_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_post_sig",
            0
          ],
          "destination": [
            "v0_post_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_reson",
            0
          ],
          "destination": [
            "v0_sum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_post_mul",
            0
          ],
          "destination": [
            "v0_sum",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v0_sum",
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
            "js",
            1
          ],
          "destination": [
            "v1_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_unpack",
            5
          ],
          "destination": [
            "v1_amp_delta",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_unpack",
            0
          ],
          "destination": [
            "v1_amp_delta",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_amp_delta",
            0
          ],
          "destination": [
            "v1_amp_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_amp_expr",
            0
          ],
          "destination": [
            "v1_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_trigger",
            0
          ],
          "destination": [
            "v1_click",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_trigger",
            1
          ],
          "destination": [
            "v1_amp_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_click",
            0
          ],
          "destination": [
            "v1_hit_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_amp_sig",
            0
          ],
          "destination": [
            "v1_hit_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_unpack",
            3
          ],
          "destination": [
            "v1_axis_sign",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_unpack",
            4
          ],
          "destination": [
            "v1_axis_sign",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_axis_sign",
            0
          ],
          "destination": [
            "v1_freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_freq",
            0
          ],
          "destination": [
            "v1_reson",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_unpack",
            1
          ],
          "destination": [
            "v1_bw_grain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_unpack",
            2
          ],
          "destination": [
            "v1_bw_grain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_bw_grain",
            0
          ],
          "destination": [
            "v1_q",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_q",
            0
          ],
          "destination": [
            "v1_reson",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_hit_mul",
            0
          ],
          "destination": [
            "v1_reson",
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
            "v1_post_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_post_unpack",
            1
          ],
          "destination": [
            "v1_post_scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_post_scale",
            0
          ],
          "destination": [
            "v1_post_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_cycle",
            0
          ],
          "destination": [
            "v1_post_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_post_sig",
            0
          ],
          "destination": [
            "v1_post_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_reson",
            0
          ],
          "destination": [
            "v1_sum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_post_mul",
            0
          ],
          "destination": [
            "v1_sum",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v1_sum",
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
            "js",
            2
          ],
          "destination": [
            "v2_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_unpack",
            5
          ],
          "destination": [
            "v2_amp_delta",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_unpack",
            0
          ],
          "destination": [
            "v2_amp_delta",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_amp_delta",
            0
          ],
          "destination": [
            "v2_amp_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_amp_expr",
            0
          ],
          "destination": [
            "v2_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_trigger",
            0
          ],
          "destination": [
            "v2_click",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_trigger",
            1
          ],
          "destination": [
            "v2_amp_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_click",
            0
          ],
          "destination": [
            "v2_hit_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_amp_sig",
            0
          ],
          "destination": [
            "v2_hit_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_unpack",
            3
          ],
          "destination": [
            "v2_axis_sign",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_unpack",
            4
          ],
          "destination": [
            "v2_axis_sign",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_axis_sign",
            0
          ],
          "destination": [
            "v2_freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_freq",
            0
          ],
          "destination": [
            "v2_reson",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_unpack",
            1
          ],
          "destination": [
            "v2_bw_grain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_unpack",
            2
          ],
          "destination": [
            "v2_bw_grain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_bw_grain",
            0
          ],
          "destination": [
            "v2_q",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_q",
            0
          ],
          "destination": [
            "v2_reson",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_hit_mul",
            0
          ],
          "destination": [
            "v2_reson",
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
            "v2_post_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_post_unpack",
            2
          ],
          "destination": [
            "v2_post_scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_post_scale",
            0
          ],
          "destination": [
            "v2_post_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_cycle",
            0
          ],
          "destination": [
            "v2_post_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_post_sig",
            0
          ],
          "destination": [
            "v2_post_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_reson",
            0
          ],
          "destination": [
            "v2_sum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_post_mul",
            0
          ],
          "destination": [
            "v2_sum",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v2_sum",
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
            "js",
            3
          ],
          "destination": [
            "v3_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_unpack",
            5
          ],
          "destination": [
            "v3_amp_delta",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_unpack",
            0
          ],
          "destination": [
            "v3_amp_delta",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_amp_delta",
            0
          ],
          "destination": [
            "v3_amp_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_amp_expr",
            0
          ],
          "destination": [
            "v3_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_trigger",
            0
          ],
          "destination": [
            "v3_click",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_trigger",
            1
          ],
          "destination": [
            "v3_amp_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_click",
            0
          ],
          "destination": [
            "v3_hit_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_amp_sig",
            0
          ],
          "destination": [
            "v3_hit_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_unpack",
            3
          ],
          "destination": [
            "v3_axis_sign",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_unpack",
            4
          ],
          "destination": [
            "v3_axis_sign",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_axis_sign",
            0
          ],
          "destination": [
            "v3_freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_freq",
            0
          ],
          "destination": [
            "v3_reson",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_unpack",
            1
          ],
          "destination": [
            "v3_bw_grain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_unpack",
            2
          ],
          "destination": [
            "v3_bw_grain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_bw_grain",
            0
          ],
          "destination": [
            "v3_q",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_q",
            0
          ],
          "destination": [
            "v3_reson",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_hit_mul",
            0
          ],
          "destination": [
            "v3_reson",
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
            "v3_post_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_post_unpack",
            3
          ],
          "destination": [
            "v3_post_scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_post_scale",
            0
          ],
          "destination": [
            "v3_post_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_cycle",
            0
          ],
          "destination": [
            "v3_post_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_post_sig",
            0
          ],
          "destination": [
            "v3_post_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_reson",
            0
          ],
          "destination": [
            "v3_sum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_post_mul",
            0
          ],
          "destination": [
            "v3_sum",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "v3_sum",
            0
          ],
          "destination": [
            "gain",
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
        "name": "qmw_grw_sonification_v1.js",
        "type": "TEXT"
      }
    ],
    "autosave": 0
  }
}
