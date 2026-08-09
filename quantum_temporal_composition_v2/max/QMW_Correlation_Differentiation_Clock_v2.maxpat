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
      60,
      1040,
      840
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
            960,
            28
          ],
          "text": "QMW CORRELATION / DIFFERENTIATION CLOCK v2",
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "principle",
          "maxclass": "comment",
          "patching_rect": [
            25,
            48,
            1000,
            40
          ],
          "text": "No metro \u00b7 no phasor \u00b7 no rtt.clock~. Max receives ticks only when accumulated relational change crosses a quantum."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            100,
            145,
            22
          ],
          "text": "udpreceive 7442",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "FullPacket"
          ]
        }
      },
      {
        "box": {
          "id": "route",
          "maxclass": "newobj",
          "patching_rect": [
            185,
            100,
            820,
            22
          ],
          "text": "OSC-route /qmw/temporal/v2/tick /qmw/temporal/v2/relation /qmw/temporal/v2/condition /qmw/temporal/v2/snapshot/end /qmw/temporal/v2/config",
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
          "id": "router",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            142,
            235,
            22
          ],
          "text": "js qmw_correlation_tick_router_v2.js",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "tick_monitor",
          "maxclass": "message",
          "patching_rect": [
            280,
            142,
            720,
            22
          ],
          "text": "waiting for a relational tick...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "relation_monitor",
          "maxclass": "message",
          "patching_rect": [
            280,
            174,
            720,
            22
          ],
          "text": "waiting for relation samples...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "condition_monitor",
          "maxclass": "message",
          "patching_rect": [
            280,
            206,
            400,
            22
          ],
          "text": "waiting for conditional state...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "config_monitor",
          "maxclass": "message",
          "patching_rect": [
            700,
            235,
            300,
            22
          ],
          "text": "change quantum not yet acknowledged",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "snapshot_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            700,
            206,
            90,
            22
          ],
          "text": "unpack i i i",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "int",
            "int",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "time_label",
          "maxclass": "comment",
          "patching_rect": [
            805,
            208,
            105,
            20
          ],
          "text": "RELATIONAL TIME"
        }
      },
      {
        "box": {
          "id": "time_number",
          "maxclass": "number",
          "patching_rect": [
            915,
            205,
            75,
            24
          ],
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
          "id": "dsp_toggle",
          "maxclass": "toggle",
          "patching_rect": [
            25,
            715,
            26,
            26
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
          "id": "dsp",
          "maxclass": "newobj",
          "patching_rect": [
            60,
            717,
            52,
            22
          ],
          "text": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "audio_level",
          "maxclass": "newobj",
          "patching_rect": [
            635,
            715,
            62,
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
          "id": "midiout",
          "maxclass": "newobj",
          "patching_rect": [
            915,
            715,
            60,
            22
          ],
          "text": "midiout",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "quantum_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            760,
            150,
            22
          ],
          "text": "CHANGE QUANTUM",
          "fontsize": 13.0
        }
      },
      {
        "box": {
          "id": "quantum_number",
          "maxclass": "flonum",
          "patching_rect": [
            175,
            758,
            90,
            24
          ],
          "minimum": 1e-06,
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
          "id": "quantum_default",
          "maxclass": "newobj",
          "patching_rect": [
            275,
            758,
            92,
            22
          ],
          "text": "loadmess 0.005",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "quantum_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            375,
            758,
            420,
            22
          ],
          "text": "prepend /qmw/temporal/v2/control/change-quantum",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "quantum_packet_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            805,
            758,
            42,
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
          "id": "quantum_osc",
          "maxclass": "newobj",
          "patching_rect": [
            858,
            758,
            120,
            22
          ],
          "text": "OpenSoundControl",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            "OSCTimeTag"
          ]
        }
      },
      {
        "box": {
          "id": "quantum_udp",
          "maxclass": "newobj",
          "patching_rect": [
            858,
            790,
            142,
            22
          ],
          "text": "udpsend 127.0.0.1 7444",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "correlate_panel",
          "maxclass": "panel",
          "patching_rect": [
            20,
            260,
            980,
            205
          ],
          "bgcolor": [
            0.1,
            0.28,
            0.24,
            0.75
          ],
          "border": 1,
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "correlate_title",
          "maxclass": "comment",
          "patching_rect": [
            35,
            270,
            260,
            24
          ],
          "text": "CORRELATE TICKS",
          "fontsize": 16.0
        }
      },
      {
        "box": {
          "id": "correlate_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            304,
            42,
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
          "id": "correlate_flash",
          "maxclass": "button",
          "patching_rect": [
            88,
            303,
            28,
            28
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
          "id": "correlate_counter",
          "maxclass": "newobj",
          "patching_rect": [
            128,
            306,
            55,
            22
          ],
          "text": "counter",
          "numinlets": 5,
          "numoutlets": 4,
          "outlettype": [
            "int",
            "",
            "",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "correlate_count",
          "maxclass": "number",
          "patching_rect": [
            195,
            304,
            72,
            24
          ],
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
          "id": "correlate_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            342,
            330,
            22
          ],
          "text": "unpack s s s i i f f f i i f",
          "numinlets": 1,
          "numoutlets": 11,
          "outlettype": [
            "",
            "",
            "",
            "int",
            "int",
            "float",
            "float",
            "float",
            "int",
            "int",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "correlate_edge",
          "maxclass": "message",
          "patching_rect": [
            380,
            342,
            205,
            22
          ],
          "text": "edge",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "correlate_corr",
          "maxclass": "flonum",
          "patching_rect": [
            600,
            342,
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
          "id": "correlate_diff",
          "maxclass": "flonum",
          "patching_rect": [
            685,
            342,
            82,
            22
          ],
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
          "id": "correlate_strength",
          "maxclass": "flonum",
          "patching_rect": [
            780,
            342,
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
          "id": "correlate_note_sig",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            380,
            42,
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
          "id": "correlate_click",
          "maxclass": "newobj",
          "patching_rect": [
            88,
            380,
            42,
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
          "id": "correlate_vel_sig",
          "maxclass": "newobj",
          "patching_rect": [
            142,
            380,
            42,
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
          "id": "correlate_dur_sig",
          "maxclass": "newobj",
          "patching_rect": [
            195,
            380,
            42,
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
          "id": "correlate_vel_clip",
          "maxclass": "newobj",
          "patching_rect": [
            142,
            413,
            72,
            22
          ],
          "text": "clip 0 127",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "correlate_makenote",
          "maxclass": "newobj",
          "patching_rect": [
            255,
            380,
            105,
            22
          ],
          "text": "rtt.makenote~ @noteoff 1",
          "numinlets": 5,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "correlate_mtof",
          "maxclass": "newobj",
          "patching_rect": [
            375,
            380,
            38,
            22
          ],
          "text": "mtof",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "correlate_osc",
          "maxclass": "newobj",
          "patching_rect": [
            425,
            380,
            52,
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
          "id": "correlate_env_message",
          "maxclass": "message",
          "patching_rect": [
            545,
            380,
            148,
            22
          ],
          "text": "0.82 5, 0. 360 5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "correlate_env",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            380,
            42,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "correlate_vca",
          "maxclass": "newobj",
          "patching_rect": [
            905,
            380,
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
          "id": "correlate_manual",
          "maxclass": "button",
          "patching_rect": [
            875,
            303,
            28,
            28
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
          "id": "correlate_manual_label",
          "maxclass": "comment",
          "patching_rect": [
            910,
            307,
            65,
            20
          ],
          "text": "test tick"
        }
      },
      {
        "box": {
          "id": "correlate_note_default",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            438,
            72,
            22
          ],
          "text": "loadmess 60",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "correlate_vel_default",
          "maxclass": "newobj",
          "patching_rect": [
            118,
            438,
            78,
            22
          ],
          "text": "loadmess 100",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "correlate_dur_default",
          "maxclass": "newobj",
          "patching_rect": [
            208,
            438,
            78,
            22
          ],
          "text": "loadmess 320",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_panel",
          "maxclass": "panel",
          "patching_rect": [
            20,
            490,
            980,
            205
          ],
          "bgcolor": [
            0.3,
            0.13,
            0.2,
            0.75
          ],
          "border": 1,
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "differentiate_title",
          "maxclass": "comment",
          "patching_rect": [
            35,
            500,
            260,
            24
          ],
          "text": "DIFFERENTIATE TICKS",
          "fontsize": 16.0
        }
      },
      {
        "box": {
          "id": "differentiate_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            534,
            42,
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
          "id": "differentiate_flash",
          "maxclass": "button",
          "patching_rect": [
            88,
            533,
            28,
            28
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
          "id": "differentiate_counter",
          "maxclass": "newobj",
          "patching_rect": [
            128,
            536,
            55,
            22
          ],
          "text": "counter",
          "numinlets": 5,
          "numoutlets": 4,
          "outlettype": [
            "int",
            "",
            "",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_count",
          "maxclass": "number",
          "patching_rect": [
            195,
            534,
            72,
            24
          ],
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
          "id": "differentiate_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            572,
            330,
            22
          ],
          "text": "unpack s s s i i f f f i i f",
          "numinlets": 1,
          "numoutlets": 11,
          "outlettype": [
            "",
            "",
            "",
            "int",
            "int",
            "float",
            "float",
            "float",
            "int",
            "int",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_edge",
          "maxclass": "message",
          "patching_rect": [
            380,
            572,
            205,
            22
          ],
          "text": "edge",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_corr",
          "maxclass": "flonum",
          "patching_rect": [
            600,
            572,
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
          "id": "differentiate_diff",
          "maxclass": "flonum",
          "patching_rect": [
            685,
            572,
            82,
            22
          ],
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
          "id": "differentiate_strength",
          "maxclass": "flonum",
          "patching_rect": [
            780,
            572,
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
          "id": "differentiate_note_sig",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            610,
            42,
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
          "id": "differentiate_click",
          "maxclass": "newobj",
          "patching_rect": [
            88,
            610,
            42,
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
          "id": "differentiate_vel_sig",
          "maxclass": "newobj",
          "patching_rect": [
            142,
            610,
            42,
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
          "id": "differentiate_dur_sig",
          "maxclass": "newobj",
          "patching_rect": [
            195,
            610,
            42,
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
          "id": "differentiate_vel_clip",
          "maxclass": "newobj",
          "patching_rect": [
            142,
            643,
            72,
            22
          ],
          "text": "clip 0 127",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_makenote",
          "maxclass": "newobj",
          "patching_rect": [
            255,
            610,
            105,
            22
          ],
          "text": "rtt.makenote~ @noteoff 1",
          "numinlets": 5,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_mtof",
          "maxclass": "newobj",
          "patching_rect": [
            375,
            610,
            38,
            22
          ],
          "text": "mtof",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_osc",
          "maxclass": "newobj",
          "patching_rect": [
            425,
            610,
            52,
            22
          ],
          "text": "tri~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_env_message",
          "maxclass": "message",
          "patching_rect": [
            545,
            610,
            148,
            22
          ],
          "text": "0.68 3, 0. 150 3",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_env",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            610,
            42,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_vca",
          "maxclass": "newobj",
          "patching_rect": [
            905,
            610,
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
          "id": "differentiate_manual",
          "maxclass": "button",
          "patching_rect": [
            875,
            533,
            28,
            28
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
          "id": "differentiate_manual_label",
          "maxclass": "comment",
          "patching_rect": [
            910,
            537,
            65,
            20
          ],
          "text": "test tick"
        }
      },
      {
        "box": {
          "id": "differentiate_note_default",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            668,
            72,
            22
          ],
          "text": "loadmess 66",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_vel_default",
          "maxclass": "newobj",
          "patching_rect": [
            118,
            668,
            78,
            22
          ],
          "text": "loadmess 100",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "differentiate_dur_default",
          "maxclass": "newobj",
          "patching_rect": [
            208,
            668,
            78,
            22
          ],
          "text": "loadmess 320",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
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
            "router",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "router",
            2
          ],
          "destination": [
            "tick_monitor",
            1
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
            "relation_monitor",
            1
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
            "condition_monitor",
            1
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
            "snapshot_unpack",
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
            "config_monitor",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "snapshot_unpack",
            1
          ],
          "destination": [
            "time_number",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dsp_toggle",
            0
          ],
          "destination": [
            "dsp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "audio_level",
            0
          ],
          "destination": [
            "dsp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "audio_level",
            0
          ],
          "destination": [
            "dsp",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "quantum_default",
            0
          ],
          "destination": [
            "quantum_number",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "quantum_number",
            0
          ],
          "destination": [
            "quantum_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "quantum_prepend",
            0
          ],
          "destination": [
            "quantum_packet_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "quantum_packet_trigger",
            1
          ],
          "destination": [
            "quantum_osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "quantum_packet_trigger",
            0
          ],
          "destination": [
            "quantum_osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "quantum_osc",
            0
          ],
          "destination": [
            "quantum_udp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "router",
            0
          ],
          "destination": [
            "correlate_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_trigger",
            1
          ],
          "destination": [
            "correlate_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_trigger",
            0
          ],
          "destination": [
            "correlate_flash",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_trigger",
            0
          ],
          "destination": [
            "correlate_counter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_trigger",
            0
          ],
          "destination": [
            "correlate_click",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_trigger",
            0
          ],
          "destination": [
            "correlate_env_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_manual",
            0
          ],
          "destination": [
            "correlate_click",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_manual",
            0
          ],
          "destination": [
            "correlate_env_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_counter",
            0
          ],
          "destination": [
            "correlate_count",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_unpack",
            1
          ],
          "destination": [
            "correlate_edge",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_unpack",
            5
          ],
          "destination": [
            "correlate_corr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_unpack",
            6
          ],
          "destination": [
            "correlate_diff",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_unpack",
            7
          ],
          "destination": [
            "correlate_strength",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_unpack",
            8
          ],
          "destination": [
            "correlate_note_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_unpack",
            8
          ],
          "destination": [
            "correlate_mtof",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_unpack",
            9
          ],
          "destination": [
            "correlate_vel_clip",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_unpack",
            10
          ],
          "destination": [
            "correlate_dur_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_note_sig",
            0
          ],
          "destination": [
            "correlate_makenote",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_vel_clip",
            0
          ],
          "destination": [
            "correlate_vel_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_vel_sig",
            0
          ],
          "destination": [
            "correlate_makenote",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_dur_sig",
            0
          ],
          "destination": [
            "correlate_makenote",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_click",
            0
          ],
          "destination": [
            "correlate_makenote",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_makenote",
            2
          ],
          "destination": [
            "midiout",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_mtof",
            0
          ],
          "destination": [
            "correlate_osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_env_message",
            0
          ],
          "destination": [
            "correlate_env",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_osc",
            0
          ],
          "destination": [
            "correlate_vca",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_env",
            0
          ],
          "destination": [
            "correlate_vca",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_vca",
            0
          ],
          "destination": [
            "audio_level",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_note_default",
            0
          ],
          "destination": [
            "correlate_note_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_note_default",
            0
          ],
          "destination": [
            "correlate_mtof",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_vel_default",
            0
          ],
          "destination": [
            "correlate_vel_clip",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "correlate_dur_default",
            0
          ],
          "destination": [
            "correlate_dur_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "router",
            1
          ],
          "destination": [
            "differentiate_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_trigger",
            1
          ],
          "destination": [
            "differentiate_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_trigger",
            0
          ],
          "destination": [
            "differentiate_flash",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_trigger",
            0
          ],
          "destination": [
            "differentiate_counter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_trigger",
            0
          ],
          "destination": [
            "differentiate_click",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_trigger",
            0
          ],
          "destination": [
            "differentiate_env_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_manual",
            0
          ],
          "destination": [
            "differentiate_click",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_manual",
            0
          ],
          "destination": [
            "differentiate_env_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_counter",
            0
          ],
          "destination": [
            "differentiate_count",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_unpack",
            1
          ],
          "destination": [
            "differentiate_edge",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_unpack",
            5
          ],
          "destination": [
            "differentiate_corr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_unpack",
            6
          ],
          "destination": [
            "differentiate_diff",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_unpack",
            7
          ],
          "destination": [
            "differentiate_strength",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_unpack",
            8
          ],
          "destination": [
            "differentiate_note_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_unpack",
            8
          ],
          "destination": [
            "differentiate_mtof",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_unpack",
            9
          ],
          "destination": [
            "differentiate_vel_clip",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_unpack",
            10
          ],
          "destination": [
            "differentiate_dur_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_note_sig",
            0
          ],
          "destination": [
            "differentiate_makenote",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_vel_clip",
            0
          ],
          "destination": [
            "differentiate_vel_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_vel_sig",
            0
          ],
          "destination": [
            "differentiate_makenote",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_dur_sig",
            0
          ],
          "destination": [
            "differentiate_makenote",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_click",
            0
          ],
          "destination": [
            "differentiate_makenote",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_makenote",
            2
          ],
          "destination": [
            "midiout",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_mtof",
            0
          ],
          "destination": [
            "differentiate_osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_env_message",
            0
          ],
          "destination": [
            "differentiate_env",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_osc",
            0
          ],
          "destination": [
            "differentiate_vca",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_env",
            0
          ],
          "destination": [
            "differentiate_vca",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_vca",
            0
          ],
          "destination": [
            "audio_level",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_note_default",
            0
          ],
          "destination": [
            "differentiate_note_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_note_default",
            0
          ],
          "destination": [
            "differentiate_mtof",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_vel_default",
            0
          ],
          "destination": [
            "differentiate_vel_clip",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "differentiate_dur_default",
            0
          ],
          "destination": [
            "differentiate_dur_sig",
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
        "name": "OpenSoundControl.mxo",
        "type": "iLaX"
      },
      {
        "name": "qmw_correlation_tick_router_v2.js",
        "type": "TEXT"
      },
      {
        "name": "rtt.makenote~.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
