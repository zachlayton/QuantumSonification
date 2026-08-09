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
      35,
      1100,
      915
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
            16,
            930,
            25
          ],
          "text": "QMW ZX Processing Companion \u2014 exact OSC receiver + audible voice",
          "fontsize": 16
        }
      },
      {
        "box": {
          "id": "help",
          "maxclass": "comment",
          "patching_rect": [
            25,
            47,
            1020,
            38
          ],
          "text": "Processing sends normalized performance controls and diagram edits to UDP 7496. Click the speaker at the bottom after values appear."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            105,
            118,
            22
          ],
          "text": "udpreceive 7496",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "routes",
          "maxclass": "newobj",
          "patching_rect": [
            165,
            105,
            865,
            22
          ],
          "text": "OSC-route /qmw/zx/fader /qmw/zx/node/position /qmw/zx/node/phase /qmw/zx/node/add /qmw/zx/node/delete /qmw/zx/edge/add /qmw/zx/rewrite/fuse /qmw/zx/graph/scalar /qmw/zx/rewrite/apply",
          "numinlets": 1,
          "numoutlets": 10,
          "outlettype": [
            "",
            "",
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
          "id": "fader_route",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            150,
            150,
            22
          ],
          "text": "route 1 2 3 4 5 6",
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
          ]
        }
      },
      {
        "box": {
          "id": "label_1",
          "maxclass": "comment",
          "patching_rect": [
            25,
            195,
            130,
            20
          ],
          "text": "1  phase"
        }
      },
      {
        "box": {
          "id": "value_1",
          "maxclass": "flonum",
          "patching_rect": [
            157,
            193,
            72,
            22
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
          "id": "label_2",
          "maxclass": "comment",
          "patching_rect": [
            245,
            195,
            130,
            20
          ],
          "text": "2  Z expectation"
        }
      },
      {
        "box": {
          "id": "value_2",
          "maxclass": "flonum",
          "patching_rect": [
            377,
            193,
            72,
            22
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
          "id": "label_3",
          "maxclass": "comment",
          "patching_rect": [
            465,
            195,
            130,
            20
          ],
          "text": "3  entropy"
        }
      },
      {
        "box": {
          "id": "value_3",
          "maxclass": "flonum",
          "patching_rect": [
            597,
            193,
            72,
            22
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
          "id": "label_4",
          "maxclass": "comment",
          "patching_rect": [
            25,
            265,
            130,
            20
          ],
          "text": "4  coherence"
        }
      },
      {
        "box": {
          "id": "value_4",
          "maxclass": "flonum",
          "patching_rect": [
            157,
            263,
            72,
            22
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
          "id": "label_5",
          "maxclass": "comment",
          "patching_rect": [
            245,
            265,
            130,
            20
          ],
          "text": "5  gradient"
        }
      },
      {
        "box": {
          "id": "value_5",
          "maxclass": "flonum",
          "patching_rect": [
            377,
            263,
            72,
            22
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
          "id": "label_6",
          "maxclass": "comment",
          "patching_rect": [
            465,
            265,
            130,
            20
          ],
          "text": "6  probability"
        }
      },
      {
        "box": {
          "id": "value_6",
          "maxclass": "flonum",
          "patching_rect": [
            597,
            263,
            72,
            22
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
          "id": "position_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            357,
            245,
            20
          ],
          "text": "/node/position  id x y"
        }
      },
      {
        "box": {
          "id": "position",
          "maxclass": "message",
          "patching_rect": [
            280,
            355,
            600,
            22
          ],
          "text": "waiting...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "position_print",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            355,
            155,
            22
          ],
          "text": "print ZX_POSITION",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "phase_event_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            391,
            245,
            20
          ],
          "text": "/node/phase  id kind radians"
        }
      },
      {
        "box": {
          "id": "phase_event",
          "maxclass": "message",
          "patching_rect": [
            280,
            389,
            600,
            22
          ],
          "text": "waiting...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "phase_event_print",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            389,
            155,
            22
          ],
          "text": "print ZX_PHASE_EVENT",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "add_event_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            425,
            245,
            20
          ],
          "text": "/node/add  id kind x y phase"
        }
      },
      {
        "box": {
          "id": "add_event",
          "maxclass": "message",
          "patching_rect": [
            280,
            423,
            600,
            22
          ],
          "text": "waiting...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "add_event_print",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            423,
            155,
            22
          ],
          "text": "print ZX_ADD_EVENT",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "delete_event_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            459,
            245,
            20
          ],
          "text": "/node/delete  id"
        }
      },
      {
        "box": {
          "id": "delete_event",
          "maxclass": "message",
          "patching_rect": [
            280,
            457,
            600,
            22
          ],
          "text": "waiting...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "delete_event_print",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            457,
            155,
            22
          ],
          "text": "print ZX_DELETE_EVENT",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "edge_event_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            493,
            245,
            20
          ],
          "text": "/edge/add  source target plain"
        }
      },
      {
        "box": {
          "id": "edge_event",
          "maxclass": "message",
          "patching_rect": [
            280,
            491,
            600,
            22
          ],
          "text": "waiting...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "edge_event_print",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            491,
            155,
            22
          ],
          "text": "print ZX_EDGE_EVENT",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "fusion_event_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            527,
            245,
            20
          ],
          "text": "/rewrite/fuse  keep removed kind phase"
        }
      },
      {
        "box": {
          "id": "fusion_event",
          "maxclass": "message",
          "patching_rect": [
            280,
            525,
            600,
            22
          ],
          "text": "waiting...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "fusion_event_print",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            525,
            155,
            22
          ],
          "text": "print ZX_FUSION_EVENT",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "scalar_event_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            561,
            245,
            20
          ],
          "text": "/graph/scalar  real imag"
        }
      },
      {
        "box": {
          "id": "scalar_event",
          "maxclass": "message",
          "patching_rect": [
            280,
            559,
            600,
            22
          ],
          "text": "waiting...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "scalar_event_print",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            559,
            155,
            22
          ],
          "text": "print ZX_SCALAR_EVENT",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "rule_event_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            595,
            245,
            20
          ],
          "text": "/rewrite/apply  rule error scalar-real scalar-imag"
        }
      },
      {
        "box": {
          "id": "rule_event",
          "maxclass": "message",
          "patching_rect": [
            280,
            593,
            600,
            22
          ],
          "text": "waiting...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "rule_event_print",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            593,
            155,
            22
          ],
          "text": "print ZX_RULE_EVENT",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "audio_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            625,
            680,
            20
          ],
          "text": "Audible monitor: phase \u2192 carrier pitch \u00b7 expectation \u2192 upper partial \u00b7 coherence \u2192 partial level \u00b7 probability \u2192 gain"
        }
      },
      {
        "box": {
          "id": "base_expr",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            655,
            185,
            22
          ],
          "text": "expr 110.*pow(2.,$f1*2.)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "base_pack",
          "maxclass": "newobj",
          "patching_rect": [
            225,
            655,
            70,
            22
          ],
          "text": "pack f 40",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "base_line",
          "maxclass": "newobj",
          "patching_rect": [
            310,
            655,
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
          "id": "carrier",
          "maxclass": "newobj",
          "patching_rect": [
            370,
            655,
            55,
            22
          ],
          "text": "cycle~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "carrier_gain",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            655,
            48,
            22
          ],
          "text": "*~ 0.65",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "upper_expr",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            692,
            175,
            22
          ],
          "text": "expr 165.+($f1*330.)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "upper_pack",
          "maxclass": "newobj",
          "patching_rect": [
            215,
            692,
            70,
            22
          ],
          "text": "pack f 40",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "upper_line",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            692,
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
          "id": "upper",
          "maxclass": "newobj",
          "patching_rect": [
            360,
            692,
            55,
            22
          ],
          "text": "cycle~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "coherence_scale",
          "maxclass": "newobj",
          "patching_rect": [
            505,
            692,
            52,
            22
          ],
          "text": "* 0.14",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "coherence_pack",
          "maxclass": "newobj",
          "patching_rect": [
            570,
            692,
            70,
            22
          ],
          "text": "pack f 60",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "coherence_line",
          "maxclass": "newobj",
          "patching_rect": [
            655,
            692,
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
          "id": "upper_gain",
          "maxclass": "newobj",
          "patching_rect": [
            430,
            692,
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
          "id": "sum",
          "maxclass": "newobj",
          "patching_rect": [
            520,
            655,
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
          "id": "master_scale",
          "maxclass": "newobj",
          "patching_rect": [
            720,
            692,
            130,
            22
          ],
          "text": "expr 0.015+($f1*0.09)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "master_pack",
          "maxclass": "newobj",
          "patching_rect": [
            865,
            692,
            70,
            22
          ],
          "text": "pack f 80",
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
            950,
            692,
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
          "id": "master",
          "maxclass": "newobj",
          "patching_rect": [
            590,
            655,
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
          "id": "fusion_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            742,
            48,
            22
          ],
          "text": "t b l",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "fusion_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            90,
            742,
            105,
            22
          ],
          "text": "unpack i i s f",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "int",
            "int",
            "",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "rewrite_freq",
          "maxclass": "newobj",
          "patching_rect": [
            210,
            742,
            235,
            22
          ],
          "text": "expr 220.*pow(2.,$f1/6.283185*2.)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "rewrite_pack",
          "maxclass": "newobj",
          "patching_rect": [
            460,
            742,
            70,
            22
          ],
          "text": "pack f 20",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "rewrite_line",
          "maxclass": "newobj",
          "patching_rect": [
            545,
            742,
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
          "id": "rewrite_osc",
          "maxclass": "newobj",
          "patching_rect": [
            605,
            742,
            55,
            22
          ],
          "text": "cycle~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "rewrite_envelope_message",
          "maxclass": "message",
          "patching_rect": [
            90,
            780,
            105,
            22
          ],
          "text": "0.2, 0. 700",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "rewrite_envelope",
          "maxclass": "newobj",
          "patching_rect": [
            210,
            780,
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
          "id": "rewrite_gain",
          "maxclass": "newobj",
          "patching_rect": [
            675,
            742,
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
          "id": "post_rewrite_sum",
          "maxclass": "newobj",
          "patching_rect": [
            735,
            655,
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
          "id": "rewrite_label",
          "maxclass": "comment",
          "patching_rect": [
            270,
            780,
            560,
            22
          ],
          "text": "Every verified fusion or named rule produces a confirmation chime."
        }
      },
      {
        "box": {
          "id": "named_rewrite_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            835,
            742,
            42,
            22
          ],
          "text": "t b b",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "named_rewrite_freq",
          "maxclass": "message",
          "patching_rect": [
            835,
            780,
            42,
            22
          ],
          "text": "440.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "audio_prompt",
          "maxclass": "comment",
          "patching_rect": [
            655,
            842,
            225,
            22
          ],
          "text": "Click speaker to start/stop Max audio \u2192"
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "newobj",
          "patching_rect": [
            895,
            833,
            65,
            32
          ],
          "text": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0
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
            "routes",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            0
          ],
          "destination": [
            "fader_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fader_route",
            0
          ],
          "destination": [
            "value_1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fader_route",
            1
          ],
          "destination": [
            "value_2",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fader_route",
            2
          ],
          "destination": [
            "value_3",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fader_route",
            3
          ],
          "destination": [
            "value_4",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fader_route",
            4
          ],
          "destination": [
            "value_5",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fader_route",
            5
          ],
          "destination": [
            "value_6",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            1
          ],
          "destination": [
            "position",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            1
          ],
          "destination": [
            "position_print",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            2
          ],
          "destination": [
            "phase_event",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            2
          ],
          "destination": [
            "phase_event_print",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            3
          ],
          "destination": [
            "add_event",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            3
          ],
          "destination": [
            "add_event_print",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            4
          ],
          "destination": [
            "delete_event",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            4
          ],
          "destination": [
            "delete_event_print",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            5
          ],
          "destination": [
            "edge_event",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            5
          ],
          "destination": [
            "edge_event_print",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            6
          ],
          "destination": [
            "fusion_event",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            6
          ],
          "destination": [
            "fusion_event_print",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            7
          ],
          "destination": [
            "scalar_event",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            7
          ],
          "destination": [
            "scalar_event_print",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            8
          ],
          "destination": [
            "rule_event",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            8
          ],
          "destination": [
            "rule_event_print",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_1",
            0
          ],
          "destination": [
            "base_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "base_expr",
            0
          ],
          "destination": [
            "base_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "base_pack",
            0
          ],
          "destination": [
            "base_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "base_line",
            0
          ],
          "destination": [
            "carrier",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "carrier",
            0
          ],
          "destination": [
            "carrier_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_2",
            0
          ],
          "destination": [
            "upper_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "upper_expr",
            0
          ],
          "destination": [
            "upper_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "upper_pack",
            0
          ],
          "destination": [
            "upper_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "upper_line",
            0
          ],
          "destination": [
            "upper",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_4",
            0
          ],
          "destination": [
            "coherence_scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "coherence_scale",
            0
          ],
          "destination": [
            "coherence_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "coherence_pack",
            0
          ],
          "destination": [
            "coherence_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "upper",
            0
          ],
          "destination": [
            "upper_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "coherence_line",
            0
          ],
          "destination": [
            "upper_gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "carrier_gain",
            0
          ],
          "destination": [
            "sum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "upper_gain",
            0
          ],
          "destination": [
            "sum",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_6",
            0
          ],
          "destination": [
            "master_scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "master_scale",
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
            "routes",
            6
          ],
          "destination": [
            "fusion_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            8
          ],
          "destination": [
            "named_rewrite_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fusion_trigger",
            1
          ],
          "destination": [
            "fusion_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fusion_unpack",
            3
          ],
          "destination": [
            "rewrite_freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rewrite_freq",
            0
          ],
          "destination": [
            "rewrite_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rewrite_pack",
            0
          ],
          "destination": [
            "rewrite_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rewrite_line",
            0
          ],
          "destination": [
            "rewrite_osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fusion_trigger",
            0
          ],
          "destination": [
            "rewrite_envelope_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "named_rewrite_trigger",
            1
          ],
          "destination": [
            "named_rewrite_freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "named_rewrite_freq",
            0
          ],
          "destination": [
            "rewrite_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "named_rewrite_trigger",
            0
          ],
          "destination": [
            "rewrite_envelope_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rewrite_envelope_message",
            0
          ],
          "destination": [
            "rewrite_envelope",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rewrite_osc",
            0
          ],
          "destination": [
            "rewrite_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rewrite_envelope",
            0
          ],
          "destination": [
            "rewrite_gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sum",
            0
          ],
          "destination": [
            "post_rewrite_sum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rewrite_gain",
            0
          ],
          "destination": [
            "post_rewrite_sum",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "post_rewrite_sum",
            0
          ],
          "destination": [
            "master",
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
            "master",
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
            "dac",
            0
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
            "dac",
            1
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
