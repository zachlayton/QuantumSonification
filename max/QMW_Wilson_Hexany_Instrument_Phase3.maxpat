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
      70,
      70,
      1200,
      780
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            18,
            1130,
            30
          ],
          "text": "QMW \u00b7 WILSON HEXANY INSTRUMENT \u00b7 PHASE 3",
          "fontsize": 21,
          "presentation": 1,
          "presentation_rect": [
            25,
            18,
            1130,
            30
          ]
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            25,
            50,
            1150,
            38
          ],
          "text": "Six exact 2)4 \u00b7 1\u20133\u20135\u20137 voices. Probability drives energy, relative phase drives spectral color and space, Johnson-flow creates accents; complement exchanges particle and hole.",
          "presentation": 1,
          "presentation_rect": [
            25,
            50,
            1150,
            38
          ]
        }
      },
      {
        "box": {
          "id": "rx_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            105,
            360,
            20
          ],
          "text": "AUTHORITATIVE CPS STATE \u00b7 UDP 7420",
          "fontsize": 14,
          "presentation": 1,
          "presentation_rect": [
            25,
            105,
            360,
            20
          ]
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            135,
            110,
            22
          ],
          "text": "udpreceive 7420",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "presentation": 1,
          "presentation_rect": [
            25,
            135,
            110,
            22
          ]
        }
      },
      {
        "box": {
          "id": "route_qmw",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            135,
            110,
            22
          ],
          "text": "OSC-route /qmw",
          "presentation": 1,
          "presentation_rect": [
            145,
            135,
            110,
            22
          ]
        }
      },
      {
        "box": {
          "id": "route_wilson",
          "maxclass": "newobj",
          "patching_rect": [
            265,
            135,
            125,
            22
          ],
          "text": "OSC-route /wilson",
          "presentation": 1,
          "presentation_rect": [
            265,
            135,
            125,
            22
          ]
        }
      },
      {
        "box": {
          "id": "route_cps",
          "maxclass": "newobj",
          "patching_rect": [
            400,
            135,
            105,
            22
          ],
          "text": "OSC-route /cps",
          "presentation": 1,
          "presentation_rect": [
            400,
            135,
            105,
            22
          ]
        }
      },
      {
        "box": {
          "id": "route_messages",
          "maxclass": "newobj",
          "patching_rect": [
            515,
            135,
            630,
            22
          ],
          "text": "OSC-route /definition /edge /frame /vertex /end /measurement /flow /status",
          "presentation": 1,
          "presentation_rect": [
            515,
            135,
            630,
            22
          ]
        }
      },
      {
        "box": {
          "id": "pre_definition",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            180,
            120,
            22
          ],
          "text": "prepend definition",
          "presentation": 1,
          "presentation_rect": [
            25,
            180,
            120,
            22
          ]
        }
      },
      {
        "box": {
          "id": "pre_edge",
          "maxclass": "newobj",
          "patching_rect": [
            155,
            180,
            90,
            22
          ],
          "text": "prepend edge",
          "presentation": 1,
          "presentation_rect": [
            155,
            180,
            90,
            22
          ]
        }
      },
      {
        "box": {
          "id": "pre_frame",
          "maxclass": "newobj",
          "patching_rect": [
            255,
            180,
            95,
            22
          ],
          "text": "prepend frame",
          "presentation": 1,
          "presentation_rect": [
            255,
            180,
            95,
            22
          ]
        }
      },
      {
        "box": {
          "id": "pre_vertex",
          "maxclass": "newobj",
          "patching_rect": [
            360,
            180,
            100,
            22
          ],
          "text": "prepend vertex",
          "presentation": 1,
          "presentation_rect": [
            360,
            180,
            100,
            22
          ]
        }
      },
      {
        "box": {
          "id": "pre_end",
          "maxclass": "newobj",
          "patching_rect": [
            470,
            180,
            85,
            22
          ],
          "text": "prepend end",
          "presentation": 1,
          "presentation_rect": [
            470,
            180,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "pre_measurement",
          "maxclass": "newobj",
          "patching_rect": [
            565,
            180,
            135,
            22
          ],
          "text": "prepend measurement",
          "presentation": 1,
          "presentation_rect": [
            565,
            180,
            135,
            22
          ]
        }
      },
      {
        "box": {
          "id": "pre_flow",
          "maxclass": "newobj",
          "patching_rect": [
            710,
            180,
            85,
            22
          ],
          "text": "prepend flow",
          "presentation": 1,
          "presentation_rect": [
            710,
            180,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "pre_status",
          "maxclass": "newobj",
          "patching_rect": [
            805,
            180,
            95,
            22
          ],
          "text": "prepend status",
          "presentation": 1,
          "presentation_rect": [
            805,
            180,
            95,
            22
          ]
        }
      },
      {
        "box": {
          "id": "dispatch",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            225,
            250,
            22
          ],
          "text": "js qmw_wilson_hexany_phase3.js",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "list",
            ""
          ],
          "presentation": 1,
          "presentation_rect": [
            25,
            225,
            250,
            22
          ]
        }
      },
      {
        "box": {
          "id": "poly",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            270,
            390,
            22
          ],
          "text": "poly~ qmw_wilson_hexany_voice_phase3.maxpat 6 @steal 0",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ],
          "presentation": 1,
          "presentation_rect": [
            25,
            270,
            390,
            22
          ]
        }
      },
      {
        "box": {
          "id": "activation_label",
          "maxclass": "comment",
          "patching_rect": [
            445,
            224,
            450,
            20
          ],
          "text": "AUDITORY ACTIVATION \u00b7 attack + post-release persistence",
          "presentation": 1,
          "presentation_rect": [
            445,
            224,
            450,
            20
          ]
        }
      },
      {
        "box": {
          "id": "activation",
          "maxclass": "multislider",
          "patching_rect": [
            445,
            252,
            450,
            85
          ],
          "size": 6,
          "setminmax": [
            0.0,
            1.0
          ],
          "orientation": 0,
          "slidercolor": [
            0.32,
            0.75,
            1.0,
            1.0
          ],
          "presentation": 1,
          "presentation_rect": [
            445,
            252,
            450,
            85
          ]
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            445,
            350,
            700,
            22
          ],
          "text": "waiting for CPS frame \u2026",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "presentation": 1,
          "presentation_rect": [
            445,
            350,
            700,
            22
          ]
        }
      },
      {
        "box": {
          "id": "gain",
          "maxclass": "live.gain~",
          "patching_rect": [
            25,
            320,
            105,
            150
          ],
          "numinlets": 2,
          "numoutlets": 5,
          "outlettype": [
            "signal",
            "signal",
            "",
            "float",
            "list"
          ],
          "parameter_enable": 1,
          "saved_attribute_attributes": {
            "valueof": {
              "parameter_initial": [
                -12.0
              ],
              "parameter_initial_enable": 1,
              "parameter_longname": "Wilson Hexany output",
              "parameter_mmax": 6.0,
              "parameter_mmin": -70.0,
              "parameter_shortname": "Hexany output",
              "parameter_type": 0,
              "parameter_unitstyle": 4
            }
          },
          "presentation": 1,
          "presentation_rect": [
            25,
            320,
            105,
            150
          ]
        }
      },
      {
        "box": {
          "id": "clip_l",
          "maxclass": "newobj",
          "patching_rect": [
            155,
            350,
            85,
            22
          ],
          "text": "clip~ -0.95 0.95",
          "presentation": 1,
          "presentation_rect": [
            155,
            350,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "clip_r",
          "maxclass": "newobj",
          "patching_rect": [
            155,
            390,
            85,
            22
          ],
          "text": "clip~ -0.95 0.95",
          "presentation": 1,
          "presentation_rect": [
            155,
            390,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "meter_l",
          "maxclass": "newobj",
          "patching_rect": [
            255,
            350,
            65,
            22
          ],
          "text": "meter~",
          "presentation": 1,
          "presentation_rect": [
            255,
            350,
            65,
            22
          ]
        }
      },
      {
        "box": {
          "id": "meter_r",
          "maxclass": "newobj",
          "patching_rect": [
            255,
            390,
            65,
            22
          ],
          "text": "meter~",
          "presentation": 1,
          "presentation_rect": [
            255,
            390,
            65,
            22
          ]
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "newobj",
          "patching_rect": [
            335,
            370,
            65,
            22
          ],
          "text": "ezdac~",
          "presentation": 1,
          "presentation_rect": [
            335,
            370,
            65,
            22
          ]
        }
      },
      {
        "box": {
          "id": "dsp_on",
          "maxclass": "newobj",
          "patching_rect": [
            335,
            410,
            72,
            22
          ],
          "text": "loadmess 1",
          "hidden": 1,
          "presentation": 1,
          "presentation_rect": [
            335,
            410,
            72,
            22
          ]
        }
      },
      {
        "box": {
          "id": "controls_label",
          "maxclass": "comment",
          "patching_rect": [
            445,
            405,
            540,
            22
          ],
          "text": "COMPOSITIONAL NAVIGATION",
          "fontsize": 14,
          "presentation": 1,
          "presentation_rect": [
            445,
            405,
            540,
            22
          ]
        }
      },
      {
        "box": {
          "id": "start",
          "maxclass": "message",
          "patching_rect": [
            445,
            440,
            55,
            22
          ],
          "text": "start",
          "presentation": 1,
          "presentation_rect": [
            445,
            440,
            55,
            22
          ]
        }
      },
      {
        "box": {
          "id": "start_pack",
          "maxclass": "newobj",
          "patching_rect": [
            445,
            470,
            175,
            22
          ],
          "text": "o.pack /qmw/recursive/start",
          "presentation": 1,
          "presentation_rect": [
            445,
            470,
            175,
            22
          ]
        }
      },
      {
        "box": {
          "id": "stop",
          "maxclass": "message",
          "patching_rect": [
            510,
            440,
            50,
            22
          ],
          "text": "stop",
          "presentation": 1,
          "presentation_rect": [
            510,
            440,
            50,
            22
          ]
        }
      },
      {
        "box": {
          "id": "stop_pack",
          "maxclass": "newobj",
          "patching_rect": [
            630,
            470,
            170,
            22
          ],
          "text": "o.pack /qmw/recursive/stop",
          "presentation": 1,
          "presentation_rect": [
            630,
            470,
            170,
            22
          ]
        }
      },
      {
        "box": {
          "id": "next",
          "maxclass": "message",
          "patching_rect": [
            570,
            440,
            50,
            22
          ],
          "text": "next",
          "presentation": 1,
          "presentation_rect": [
            570,
            440,
            50,
            22
          ]
        }
      },
      {
        "box": {
          "id": "next_pack",
          "maxclass": "newobj",
          "patching_rect": [
            810,
            470,
            170,
            22
          ],
          "text": "o.pack /qmw/recursive/next",
          "presentation": 1,
          "presentation_rect": [
            810,
            470,
            170,
            22
          ]
        }
      },
      {
        "box": {
          "id": "reset",
          "maxclass": "message",
          "patching_rect": [
            630,
            440,
            50,
            22
          ],
          "text": "reset",
          "presentation": 1,
          "presentation_rect": [
            630,
            440,
            50,
            22
          ]
        }
      },
      {
        "box": {
          "id": "reset_pack",
          "maxclass": "newobj",
          "patching_rect": [
            990,
            470,
            175,
            22
          ],
          "text": "o.pack /qmw/recursive/reset",
          "presentation": 1,
          "presentation_rect": [
            990,
            470,
            175,
            22
          ]
        }
      },
      {
        "box": {
          "id": "complement",
          "maxclass": "message",
          "patching_rect": [
            690,
            440,
            95,
            22
          ],
          "text": "complement",
          "presentation": 1,
          "presentation_rect": [
            690,
            440,
            95,
            22
          ]
        }
      },
      {
        "box": {
          "id": "complement_pack",
          "maxclass": "newobj",
          "patching_rect": [
            445,
            510,
            230,
            22
          ],
          "text": "o.pack /qmw/wilson/cps/complement",
          "presentation": 1,
          "presentation_rect": [
            445,
            510,
            230,
            22
          ]
        }
      },
      {
        "box": {
          "id": "control_udp",
          "maxclass": "newobj",
          "patching_rect": [
            995,
            550,
            165,
            22
          ],
          "text": "udpsend 127.0.0.1 7433",
          "presentation": 1,
          "presentation_rect": [
            995,
            550,
            165,
            22
          ]
        }
      },
      {
        "box": {
          "id": "temp_label",
          "maxclass": "comment",
          "patching_rect": [
            445,
            555,
            82,
            20
          ],
          "text": "temperature",
          "presentation": 1,
          "presentation_rect": [
            445,
            555,
            82,
            20
          ]
        }
      },
      {
        "box": {
          "id": "temperature",
          "maxclass": "flonum",
          "patching_rect": [
            535,
            553,
            65,
            22
          ],
          "minimum": 0.0,
          "maximum": 2.0,
          "presentation": 1,
          "presentation_rect": [
            535,
            553,
            65,
            22
          ]
        }
      },
      {
        "box": {
          "id": "temp_pack",
          "maxclass": "newobj",
          "patching_rect": [
            610,
            553,
            205,
            22
          ],
          "text": "o.pack /qmw/recursive/temperature",
          "presentation": 1,
          "presentation_rect": [
            610,
            553,
            205,
            22
          ]
        }
      },
      {
        "box": {
          "id": "interval_label",
          "maxclass": "comment",
          "patching_rect": [
            445,
            590,
            75,
            20
          ],
          "text": "interval ms",
          "presentation": 1,
          "presentation_rect": [
            445,
            590,
            75,
            20
          ]
        }
      },
      {
        "box": {
          "id": "interval",
          "maxclass": "number",
          "patching_rect": [
            535,
            588,
            65,
            22
          ],
          "minimum": 30,
          "maximum": 5000,
          "presentation": 1,
          "presentation_rect": [
            535,
            588,
            65,
            22
          ]
        }
      },
      {
        "box": {
          "id": "interval_pack",
          "maxclass": "newobj",
          "patching_rect": [
            610,
            588,
            205,
            22
          ],
          "text": "o.pack /qmw/recursive/interval_ms",
          "presentation": 1,
          "presentation_rect": [
            610,
            588,
            205,
            22
          ]
        }
      },
      {
        "box": {
          "id": "transpose_label",
          "maxclass": "comment",
          "patching_rect": [
            445,
            625,
            125,
            20
          ],
          "text": "temporary anchor \u00b148 st",
          "presentation": 1,
          "presentation_rect": [
            445,
            625,
            125,
            20
          ]
        }
      },
      {
        "box": {
          "id": "transpose",
          "maxclass": "flonum",
          "patching_rect": [
            575,
            623,
            65,
            22
          ],
          "minimum": -48.0,
          "maximum": 48.0,
          "presentation": 1,
          "presentation_rect": [
            575,
            623,
            65,
            22
          ]
        }
      },
      {
        "box": {
          "id": "pre_transpose",
          "maxclass": "newobj",
          "patching_rect": [
            650,
            623,
            120,
            22
          ],
          "text": "prepend transpose",
          "presentation": 1,
          "presentation_rect": [
            650,
            623,
            120,
            22
          ]
        }
      },
      {
        "box": {
          "id": "test",
          "maxclass": "message",
          "patching_rect": [
            800,
            623,
            80,
            22
          ],
          "text": "local test",
          "presentation": 1,
          "presentation_rect": [
            800,
            623,
            80,
            22
          ]
        }
      },
      {
        "box": {
          "id": "test_msg",
          "maxclass": "message",
          "patching_rect": [
            890,
            623,
            45,
            22
          ],
          "text": "test",
          "presentation": 1,
          "presentation_rect": [
            890,
            623,
            45,
            22
          ]
        }
      },
      {
        "box": {
          "id": "load_temp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            650,
            90,
            22
          ],
          "text": "loadmess 0.65",
          "hidden": 1,
          "presentation": 1,
          "presentation_rect": [
            25,
            650,
            90,
            22
          ]
        }
      },
      {
        "box": {
          "id": "load_interval",
          "maxclass": "newobj",
          "patching_rect": [
            125,
            650,
            95,
            22
          ],
          "text": "loadmess 240",
          "hidden": 1,
          "presentation": 1,
          "presentation_rect": [
            125,
            650,
            95,
            22
          ]
        }
      },
      {
        "box": {
          "id": "load_transpose",
          "maxclass": "newobj",
          "patching_rect": [
            230,
            650,
            80,
            22
          ],
          "text": "loadmess 0",
          "hidden": 1,
          "presentation": 1,
          "presentation_rect": [
            230,
            650,
            80,
            22
          ]
        }
      },
      {
        "box": {
          "id": "note",
          "maxclass": "comment",
          "patching_rect": [
            25,
            690,
            1130,
            48
          ],
          "text": "Start examples/qmw_wilson_hexany_phase3.py. The same revisioned CPS packets drive this sound field and the Processing Hexany geometry on UDP 7411. The temporary anchor transposes without changing Wilson interval identity.",
          "presentation": 1,
          "presentation_rect": [
            25,
            690,
            1130,
            48
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
            "route_qmw",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_qmw",
            0
          ],
          "destination": [
            "route_wilson",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_wilson",
            0
          ],
          "destination": [
            "route_cps",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_cps",
            0
          ],
          "destination": [
            "route_messages",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_messages",
            0
          ],
          "destination": [
            "pre_definition",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_definition",
            0
          ],
          "destination": [
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_messages",
            1
          ],
          "destination": [
            "pre_edge",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_edge",
            0
          ],
          "destination": [
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_messages",
            2
          ],
          "destination": [
            "pre_frame",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_frame",
            0
          ],
          "destination": [
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_messages",
            3
          ],
          "destination": [
            "pre_vertex",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_vertex",
            0
          ],
          "destination": [
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_messages",
            4
          ],
          "destination": [
            "pre_end",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_end",
            0
          ],
          "destination": [
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_messages",
            5
          ],
          "destination": [
            "pre_measurement",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_measurement",
            0
          ],
          "destination": [
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_messages",
            6
          ],
          "destination": [
            "pre_flow",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_flow",
            0
          ],
          "destination": [
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_messages",
            7
          ],
          "destination": [
            "pre_status",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_status",
            0
          ],
          "destination": [
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dispatch",
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
            "dispatch",
            1
          ],
          "destination": [
            "activation",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dispatch",
            2
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
            "gain",
            0
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
            "clip_l",
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
            "dsp_on",
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
            "start",
            0
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
            "stop",
            0
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
            "next",
            0
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
            "reset",
            0
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
            "complement",
            0
          ],
          "destination": [
            "complement_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "temperature",
            0
          ],
          "destination": [
            "temp_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "interval",
            0
          ],
          "destination": [
            "interval_pack",
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
            "control_udp",
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
            "control_udp",
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
            "control_udp",
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
            "control_udp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "complement_pack",
            0
          ],
          "destination": [
            "control_udp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "temp_pack",
            0
          ],
          "destination": [
            "control_udp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "interval_pack",
            0
          ],
          "destination": [
            "control_udp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "transpose",
            0
          ],
          "destination": [
            "pre_transpose",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_transpose",
            0
          ],
          "destination": [
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "test",
            0
          ],
          "destination": [
            "test_msg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "test_msg",
            0
          ],
          "destination": [
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_temp",
            0
          ],
          "destination": [
            "temperature",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_interval",
            0
          ],
          "destination": [
            "interval",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_transpose",
            0
          ],
          "destination": [
            "transpose",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "qmw_wilson_hexany_phase3.js",
        "bootpath": "/Users/zlayton/QuantumSonification/max",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      },
      {
        "name": "qmw_wilson_hexany_voice_phase3.maxpat",
        "bootpath": "/Users/zlayton/QuantumSonification/max",
        "patcherrelativepath": ".",
        "type": "JSON",
        "implicit": 1
      },
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
      },
      {
        "name": "o.pack.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0,
    "openinpresentation": 1
  }
}
