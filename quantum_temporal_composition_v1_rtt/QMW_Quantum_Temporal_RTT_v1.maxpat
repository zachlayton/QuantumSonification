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
      60,
      1080,
      960
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
            940,
            28
          ],
          "text": "QMW QUANTUM TEMPORAL COMPOSITION \u00b7 RTT RELATIONAL REALIZER v1",
          "fontsize": 17.0
        }
      },
      {
        "box": {
          "id": "concept",
          "maxclass": "comment",
          "patching_rect": [
            25,
            48,
            1040,
            42
          ],
          "text": "OSC observations reconstruct independent signal-rate phases. RTT transforms each local phase; no bar/beat transport is present. rtt.clock~ is a confidence-controlled fallback only."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            105,
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
            105,
            850,
            22
          ],
          "text": "OSC-route /qmw/temporal/v1/clock /qmw/temporal/v1/conditional/purity /qmw/temporal/v1/process/resonance /qmw/temporal/v1/process/memory /qmw/temporal/v1/process/spatial /qmw/temporal/v1/event /qmw/temporal/v1/branch /qmw/temporal/v1/snapshot/begin /qmw/temporal/v1/snapshot/end",
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
          "id": "global_loadbang",
          "maxclass": "newobj",
          "patching_rect": [
            940,
            205,
            65,
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
          "id": "clock_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            145,
            105,
            22
          ],
          "text": "unpack f f f",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "clock_phase_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            174,
            88,
            20
          ],
          "text": "clock phase"
        }
      },
      {
        "box": {
          "id": "clock_phase",
          "maxclass": "flonum",
          "patching_rect": [
            115,
            172,
            76,
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
          "id": "confidence_label",
          "maxclass": "comment",
          "patching_rect": [
            215,
            174,
            105,
            20
          ],
          "text": "clock confidence"
        }
      },
      {
        "box": {
          "id": "confidence",
          "maxclass": "flonum",
          "patching_rect": [
            325,
            172,
            76,
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
          "id": "prob_label",
          "maxclass": "comment",
          "patching_rect": [
            425,
            174,
            126,
            20
          ],
          "text": "conditional probability"
        }
      },
      {
        "box": {
          "id": "clock_probability",
          "maxclass": "flonum",
          "patching_rect": [
            555,
            172,
            76,
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
          "id": "purity_label",
          "maxclass": "comment",
          "patching_rect": [
            655,
            174,
            105,
            20
          ],
          "text": "conditional purity"
        }
      },
      {
        "box": {
          "id": "purity",
          "maxclass": "flonum",
          "patching_rect": [
            765,
            172,
            76,
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
          "id": "clock_note",
          "maxclass": "comment",
          "patching_rect": [
            325,
            205,
            570,
            20
          ],
          "text": "Clock confidence is diagnostic; each subsystem below owns an independent relational rtt.clock~."
        }
      },
      {
        "box": {
          "id": "event_send",
          "maxclass": "newobj",
          "patching_rect": [
            855,
            145,
            155,
            22
          ],
          "text": "s qmw.temporal.event",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "branch_send",
          "maxclass": "newobj",
          "patching_rect": [
            855,
            172,
            160,
            22
          ],
          "text": "s qmw.temporal.branch",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "dsp_toggle",
          "maxclass": "toggle",
          "patching_rect": [
            25,
            905,
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
            907,
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
          "id": "dsp_note",
          "maxclass": "comment",
          "patching_rect": [
            125,
            908,
            330,
            20
          ],
          "text": "Turn DSP on: RTT objects and phase reconstruction are signal-rate."
        }
      },
      {
        "box": {
          "id": "audio_receive",
          "maxclass": "newobj",
          "patching_rect": [
            480,
            905,
            190,
            22
          ],
          "text": "receive~ qmw.temporal.audio",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "audio_gain",
          "maxclass": "newobj",
          "patching_rect": [
            685,
            905,
            62,
            22
          ],
          "text": "*~ 0.7",
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
            920,
            905,
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
          "id": "resonance_panel",
          "maxclass": "panel",
          "patching_rect": [
            20,
            260,
            1020,
            188
          ],
          "bgcolor": [
            0.12,
            0.2,
            0.27,
            0.72
          ],
          "border": 1,
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "resonance_title",
          "maxclass": "comment",
          "patching_rect": [
            30,
            270,
            150,
            22
          ],
          "text": "RESONANCE LOCAL TIME",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "resonance_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            30,
            300,
            145,
            22
          ],
          "text": "unpack f f f f f",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
            "float",
            "float",
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_unwrap",
          "maxclass": "newobj",
          "patching_rect": [
            190,
            300,
            235,
            22
          ],
          "text": "js qmw_relational_phase_unwrap_v1.js resonance",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_phase_value",
          "maxclass": "flonum",
          "patching_rect": [
            440,
            300,
            72,
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
          "id": "resonance_bpm_value",
          "maxclass": "flonum",
          "patching_rect": [
            525,
            300,
            72,
            22
          ],
          "minimum": 8.0,
          "maximum": 480.0,
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
          "id": "resonance_bpm_message",
          "maxclass": "newobj",
          "patching_rect": [
            610,
            300,
            82,
            22
          ],
          "text": "prepend bpm",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "resonance_clock",
          "maxclass": "newobj",
          "patching_rect": [
            705,
            300,
            70,
            22
          ],
          "text": "rtt.clock~",
          "numinlets": 4,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_loop",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            300,
            68,
            22
          ],
          "text": "rtt.loop~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_binary",
          "maxclass": "newobj",
          "patching_rect": [
            855,
            300,
            78,
            22
          ],
          "text": "rtt.binary~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_rprob",
          "maxclass": "newobj",
          "patching_rect": [
            945,
            300,
            78,
            22
          ],
          "text": "rtt.rprob~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_corr_label",
          "maxclass": "comment",
          "patching_rect": [
            30,
            337,
            70,
            20
          ],
          "text": "correlation"
        }
      },
      {
        "box": {
          "id": "resonance_corr",
          "maxclass": "flonum",
          "patching_rect": [
            102,
            335,
            62,
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
          "id": "resonance_sal_label",
          "maxclass": "comment",
          "patching_rect": [
            180,
            337,
            55,
            20
          ],
          "text": "salience"
        }
      },
      {
        "box": {
          "id": "resonance_sal",
          "maxclass": "flonum",
          "patching_rect": [
            240,
            335,
            62,
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
          "id": "resonance_sal_map",
          "maxclass": "newobj",
          "patching_rect": [
            315,
            335,
            210,
            22
          ],
          "text": "expr min(0.98, 0.25 + 0.75*$f1)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_sal_message",
          "maxclass": "newobj",
          "patching_rect": [
            315,
            360,
            190,
            22
          ],
          "text": "prepend message probabilities",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "resonance_drive_label",
          "maxclass": "comment",
          "patching_rect": [
            375,
            337,
            88,
            20
          ],
          "text": "quantum drive"
        }
      },
      {
        "box": {
          "id": "resonance_drive",
          "maxclass": "flonum",
          "patching_rect": [
            465,
            335,
            62,
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
          "id": "resonance_scope",
          "maxclass": "live.scope~",
          "patching_rect": [
            545,
            335,
            225,
            42
          ],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_sequence",
          "maxclass": "newobj",
          "patching_rect": [
            785,
            340,
            90,
            22
          ],
          "text": "rtt.sequence~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_makenote",
          "maxclass": "newobj",
          "patching_rect": [
            890,
            340,
            132,
            22
          ],
          "text": "rtt.makenote~ @duration 320 @velocity 100",
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
          "id": "resonance_send",
          "maxclass": "newobj",
          "patching_rect": [
            785,
            375,
            190,
            22
          ],
          "text": "s~ qmw.temporal.resonance.trigger",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "resonance_edge",
          "maxclass": "newobj",
          "patching_rect": [
            980,
            375,
            45,
            22
          ],
          "text": "edge~",
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
          "id": "resonance_indicator",
          "maxclass": "button",
          "patching_rect": [
            1030,
            374,
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
          "id": "resonance_midiparse",
          "maxclass": "newobj",
          "patching_rect": [
            650,
            412,
            112,
            22
          ],
          "text": "midiparse @hires 1",
          "numinlets": 1,
          "numoutlets": 8,
          "outlettype": [
            "",
            "",
            "",
            "int",
            "int",
            "",
            "int",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "resonance_note_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            412,
            68,
            22
          ],
          "text": "unpack i i",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "int",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_mtof",
          "maxclass": "newobj",
          "patching_rect": [
            855,
            412,
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
          "id": "resonance_osc",
          "maxclass": "newobj",
          "patching_rect": [
            905,
            412,
            48,
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
          "id": "resonance_vel_norm",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            438,
            38,
            22
          ],
          "text": "/ 127.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_env_pack",
          "maxclass": "newobj",
          "patching_rect": [
            823,
            438,
            68,
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
          "id": "resonance_env",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            438,
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
          "id": "resonance_vca",
          "maxclass": "newobj",
          "patching_rect": [
            952,
            412,
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
          "id": "resonance_level",
          "maxclass": "newobj",
          "patching_rect": [
            995,
            412,
            48,
            22
          ],
          "text": "*~ 0.12",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "resonance_audio_send",
          "maxclass": "newobj",
          "patching_rect": [
            995,
            438,
            190,
            22
          ],
          "text": "send~ qmw.temporal.audio",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "resonance_loop_init",
          "maxclass": "message",
          "patching_rect": [
            30,
            382,
            170,
            22
          ],
          "text": "subdiv 16, steps 9",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "resonance_binary_init",
          "maxclass": "message",
          "patching_rect": [
            210,
            382,
            150,
            22
          ],
          "text": "steps 9, seed 179",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "resonance_rprob_init",
          "maxclass": "message",
          "patching_rect": [
            370,
            382,
            270,
            22
          ],
          "text": "output input, message probabilities 0.75",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "resonance_clock_init",
          "maxclass": "message",
          "patching_rect": [
            30,
            412,
            245,
            22
          ],
          "text": "transportstate 1, barlength 1, bpm 60",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "resonance_notes",
          "maxclass": "message",
          "patching_rect": [
            555,
            388,
            210,
            22
          ],
          "text": "0 2 7 5 9 12 7 14, low 36, high 60, offset 36, stepsize 1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "resonance_notes_load",
          "maxclass": "newobj",
          "patching_rect": [
            555,
            415,
            70,
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
          "id": "memory_panel",
          "maxclass": "panel",
          "patching_rect": [
            20,
            460,
            1020,
            188
          ],
          "bgcolor": [
            0.24,
            0.16,
            0.28,
            0.72
          ],
          "border": 1,
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "memory_title",
          "maxclass": "comment",
          "patching_rect": [
            30,
            470,
            150,
            22
          ],
          "text": "MEMORY LOCAL TIME",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "memory_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            30,
            500,
            145,
            22
          ],
          "text": "unpack f f f f f",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
            "float",
            "float",
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "memory_unwrap",
          "maxclass": "newobj",
          "patching_rect": [
            190,
            500,
            235,
            22
          ],
          "text": "js qmw_relational_phase_unwrap_v1.js memory",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "memory_phase_value",
          "maxclass": "flonum",
          "patching_rect": [
            440,
            500,
            72,
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
          "id": "memory_bpm_value",
          "maxclass": "flonum",
          "patching_rect": [
            525,
            500,
            72,
            22
          ],
          "minimum": 8.0,
          "maximum": 480.0,
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
          "id": "memory_bpm_message",
          "maxclass": "newobj",
          "patching_rect": [
            610,
            500,
            82,
            22
          ],
          "text": "prepend bpm",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "memory_clock",
          "maxclass": "newobj",
          "patching_rect": [
            705,
            500,
            70,
            22
          ],
          "text": "rtt.clock~",
          "numinlets": 4,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "memory_loop",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            500,
            68,
            22
          ],
          "text": "rtt.loop~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "memory_binary",
          "maxclass": "newobj",
          "patching_rect": [
            855,
            500,
            78,
            22
          ],
          "text": "rtt.binary~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "memory_rprob",
          "maxclass": "newobj",
          "patching_rect": [
            945,
            500,
            78,
            22
          ],
          "text": "rtt.rprob~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "memory_corr_label",
          "maxclass": "comment",
          "patching_rect": [
            30,
            537,
            70,
            20
          ],
          "text": "correlation"
        }
      },
      {
        "box": {
          "id": "memory_corr",
          "maxclass": "flonum",
          "patching_rect": [
            102,
            535,
            62,
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
          "id": "memory_sal_label",
          "maxclass": "comment",
          "patching_rect": [
            180,
            537,
            55,
            20
          ],
          "text": "salience"
        }
      },
      {
        "box": {
          "id": "memory_sal",
          "maxclass": "flonum",
          "patching_rect": [
            240,
            535,
            62,
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
          "id": "memory_sal_map",
          "maxclass": "newobj",
          "patching_rect": [
            315,
            535,
            210,
            22
          ],
          "text": "expr min(0.98, 0.25 + 0.75*$f1)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "memory_sal_message",
          "maxclass": "newobj",
          "patching_rect": [
            315,
            560,
            190,
            22
          ],
          "text": "prepend message probabilities",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "memory_drive_label",
          "maxclass": "comment",
          "patching_rect": [
            375,
            537,
            88,
            20
          ],
          "text": "quantum drive"
        }
      },
      {
        "box": {
          "id": "memory_drive",
          "maxclass": "flonum",
          "patching_rect": [
            465,
            535,
            62,
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
          "id": "memory_scope",
          "maxclass": "live.scope~",
          "patching_rect": [
            545,
            535,
            225,
            42
          ],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "memory_sequence",
          "maxclass": "newobj",
          "patching_rect": [
            785,
            540,
            90,
            22
          ],
          "text": "rtt.sequence~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "memory_makenote",
          "maxclass": "newobj",
          "patching_rect": [
            890,
            540,
            132,
            22
          ],
          "text": "rtt.makenote~ @duration 320 @velocity 100",
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
          "id": "memory_send",
          "maxclass": "newobj",
          "patching_rect": [
            785,
            575,
            190,
            22
          ],
          "text": "s~ qmw.temporal.memory.trigger",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "memory_edge",
          "maxclass": "newobj",
          "patching_rect": [
            980,
            575,
            45,
            22
          ],
          "text": "edge~",
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
          "id": "memory_indicator",
          "maxclass": "button",
          "patching_rect": [
            1030,
            574,
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
          "id": "memory_midiparse",
          "maxclass": "newobj",
          "patching_rect": [
            650,
            612,
            112,
            22
          ],
          "text": "midiparse @hires 1",
          "numinlets": 1,
          "numoutlets": 8,
          "outlettype": [
            "",
            "",
            "",
            "int",
            "int",
            "",
            "int",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "memory_note_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            612,
            68,
            22
          ],
          "text": "unpack i i",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "int",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "memory_mtof",
          "maxclass": "newobj",
          "patching_rect": [
            855,
            612,
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
          "id": "memory_osc",
          "maxclass": "newobj",
          "patching_rect": [
            905,
            612,
            48,
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
          "id": "memory_vel_norm",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            638,
            38,
            22
          ],
          "text": "/ 127.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "memory_env_pack",
          "maxclass": "newobj",
          "patching_rect": [
            823,
            638,
            68,
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
          "id": "memory_env",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            638,
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
          "id": "memory_vca",
          "maxclass": "newobj",
          "patching_rect": [
            952,
            612,
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
          "id": "memory_level",
          "maxclass": "newobj",
          "patching_rect": [
            995,
            612,
            48,
            22
          ],
          "text": "*~ 0.12",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "memory_audio_send",
          "maxclass": "newobj",
          "patching_rect": [
            995,
            638,
            190,
            22
          ],
          "text": "send~ qmw.temporal.audio",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "memory_loop_init",
          "maxclass": "message",
          "patching_rect": [
            30,
            582,
            170,
            22
          ],
          "text": "subdiv 16, steps 9",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "memory_binary_init",
          "maxclass": "message",
          "patching_rect": [
            210,
            582,
            150,
            22
          ],
          "text": "steps 9, seed 271",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "memory_rprob_init",
          "maxclass": "message",
          "patching_rect": [
            370,
            582,
            270,
            22
          ],
          "text": "output input, message probabilities 0.75",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "memory_clock_init",
          "maxclass": "message",
          "patching_rect": [
            30,
            612,
            245,
            22
          ],
          "text": "transportstate 1, barlength 1, bpm 60",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "memory_notes",
          "maxclass": "message",
          "patching_rect": [
            555,
            588,
            210,
            22
          ],
          "text": "0 3 7 10 5 12 8 15, low 48, high 72, offset 48, stepsize 1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "memory_notes_load",
          "maxclass": "newobj",
          "patching_rect": [
            555,
            615,
            70,
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
          "id": "spatial_panel",
          "maxclass": "panel",
          "patching_rect": [
            20,
            660,
            1020,
            188
          ],
          "bgcolor": [
            0.14,
            0.27,
            0.22,
            0.72
          ],
          "border": 1,
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "spatial_title",
          "maxclass": "comment",
          "patching_rect": [
            30,
            670,
            150,
            22
          ],
          "text": "SPATIAL LOCAL TIME",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "spatial_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            30,
            700,
            145,
            22
          ],
          "text": "unpack f f f f f",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
            "float",
            "float",
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_unwrap",
          "maxclass": "newobj",
          "patching_rect": [
            190,
            700,
            235,
            22
          ],
          "text": "js qmw_relational_phase_unwrap_v1.js spatial",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_phase_value",
          "maxclass": "flonum",
          "patching_rect": [
            440,
            700,
            72,
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
          "id": "spatial_bpm_value",
          "maxclass": "flonum",
          "patching_rect": [
            525,
            700,
            72,
            22
          ],
          "minimum": 8.0,
          "maximum": 480.0,
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
          "id": "spatial_bpm_message",
          "maxclass": "newobj",
          "patching_rect": [
            610,
            700,
            82,
            22
          ],
          "text": "prepend bpm",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spatial_clock",
          "maxclass": "newobj",
          "patching_rect": [
            705,
            700,
            70,
            22
          ],
          "text": "rtt.clock~",
          "numinlets": 4,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_loop",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            700,
            68,
            22
          ],
          "text": "rtt.loop~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_binary",
          "maxclass": "newobj",
          "patching_rect": [
            855,
            700,
            78,
            22
          ],
          "text": "rtt.binary~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_rprob",
          "maxclass": "newobj",
          "patching_rect": [
            945,
            700,
            78,
            22
          ],
          "text": "rtt.rprob~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_corr_label",
          "maxclass": "comment",
          "patching_rect": [
            30,
            737,
            70,
            20
          ],
          "text": "correlation"
        }
      },
      {
        "box": {
          "id": "spatial_corr",
          "maxclass": "flonum",
          "patching_rect": [
            102,
            735,
            62,
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
          "id": "spatial_sal_label",
          "maxclass": "comment",
          "patching_rect": [
            180,
            737,
            55,
            20
          ],
          "text": "salience"
        }
      },
      {
        "box": {
          "id": "spatial_sal",
          "maxclass": "flonum",
          "patching_rect": [
            240,
            735,
            62,
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
          "id": "spatial_sal_map",
          "maxclass": "newobj",
          "patching_rect": [
            315,
            735,
            210,
            22
          ],
          "text": "expr min(0.98, 0.25 + 0.75*$f1)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_sal_message",
          "maxclass": "newobj",
          "patching_rect": [
            315,
            760,
            190,
            22
          ],
          "text": "prepend message probabilities",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spatial_drive_label",
          "maxclass": "comment",
          "patching_rect": [
            375,
            737,
            88,
            20
          ],
          "text": "quantum drive"
        }
      },
      {
        "box": {
          "id": "spatial_drive",
          "maxclass": "flonum",
          "patching_rect": [
            465,
            735,
            62,
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
          "id": "spatial_scope",
          "maxclass": "live.scope~",
          "patching_rect": [
            545,
            735,
            225,
            42
          ],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_sequence",
          "maxclass": "newobj",
          "patching_rect": [
            785,
            740,
            90,
            22
          ],
          "text": "rtt.sequence~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_makenote",
          "maxclass": "newobj",
          "patching_rect": [
            890,
            740,
            132,
            22
          ],
          "text": "rtt.makenote~ @duration 320 @velocity 100",
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
          "id": "spatial_send",
          "maxclass": "newobj",
          "patching_rect": [
            785,
            775,
            190,
            22
          ],
          "text": "s~ qmw.temporal.spatial.trigger",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "spatial_edge",
          "maxclass": "newobj",
          "patching_rect": [
            980,
            775,
            45,
            22
          ],
          "text": "edge~",
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
          "id": "spatial_indicator",
          "maxclass": "button",
          "patching_rect": [
            1030,
            774,
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
          "id": "spatial_midiparse",
          "maxclass": "newobj",
          "patching_rect": [
            650,
            812,
            112,
            22
          ],
          "text": "midiparse @hires 1",
          "numinlets": 1,
          "numoutlets": 8,
          "outlettype": [
            "",
            "",
            "",
            "int",
            "int",
            "",
            "int",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spatial_note_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            812,
            68,
            22
          ],
          "text": "unpack i i",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "int",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_mtof",
          "maxclass": "newobj",
          "patching_rect": [
            855,
            812,
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
          "id": "spatial_osc",
          "maxclass": "newobj",
          "patching_rect": [
            905,
            812,
            48,
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
          "id": "spatial_vel_norm",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            838,
            38,
            22
          ],
          "text": "/ 127.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_env_pack",
          "maxclass": "newobj",
          "patching_rect": [
            823,
            838,
            68,
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
          "id": "spatial_env",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            838,
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
          "id": "spatial_vca",
          "maxclass": "newobj",
          "patching_rect": [
            952,
            812,
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
          "id": "spatial_level",
          "maxclass": "newobj",
          "patching_rect": [
            995,
            812,
            48,
            22
          ],
          "text": "*~ 0.12",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "spatial_audio_send",
          "maxclass": "newobj",
          "patching_rect": [
            995,
            838,
            190,
            22
          ],
          "text": "send~ qmw.temporal.audio",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "spatial_loop_init",
          "maxclass": "message",
          "patching_rect": [
            30,
            782,
            170,
            22
          ],
          "text": "subdiv 16, steps 9",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spatial_binary_init",
          "maxclass": "message",
          "patching_rect": [
            210,
            782,
            150,
            22
          ],
          "text": "steps 9, seed 431",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spatial_rprob_init",
          "maxclass": "message",
          "patching_rect": [
            370,
            782,
            270,
            22
          ],
          "text": "output input, message probabilities 0.75",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spatial_clock_init",
          "maxclass": "message",
          "patching_rect": [
            30,
            812,
            245,
            22
          ],
          "text": "transportstate 1, barlength 1, bpm 60",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spatial_notes",
          "maxclass": "message",
          "patching_rect": [
            555,
            788,
            210,
            22
          ],
          "text": "0 5 9 14 7 12 16 19, low 60, high 84, offset 60, stepsize 1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spatial_notes_load",
          "maxclass": "newobj",
          "patching_rect": [
            555,
            815,
            70,
            22
          ],
          "text": "loadbang",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
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
            "clock_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clock_unpack",
            0
          ],
          "destination": [
            "clock_phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clock_unpack",
            1
          ],
          "destination": [
            "confidence",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clock_unpack",
            2
          ],
          "destination": [
            "clock_probability",
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
            "purity",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            5
          ],
          "destination": [
            "event_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            6
          ],
          "destination": [
            "branch_send",
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
            "audio_receive",
            0
          ],
          "destination": [
            "audio_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "audio_gain",
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
            "audio_gain",
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
            "route",
            2
          ],
          "destination": [
            "resonance_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_unpack",
            0
          ],
          "destination": [
            "resonance_unwrap",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_unpack",
            2
          ],
          "destination": [
            "resonance_corr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_unpack",
            3
          ],
          "destination": [
            "resonance_sal",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_unpack",
            3
          ],
          "destination": [
            "resonance_sal_map",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_sal_map",
            0
          ],
          "destination": [
            "resonance_sal_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_unpack",
            4
          ],
          "destination": [
            "resonance_drive",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_unwrap",
            0
          ],
          "destination": [
            "resonance_phase_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_unwrap",
            1
          ],
          "destination": [
            "resonance_bpm_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_unwrap",
            1
          ],
          "destination": [
            "resonance_bpm_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_bpm_message",
            0
          ],
          "destination": [
            "resonance_clock",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_clock_init",
            0
          ],
          "destination": [
            "resonance_clock",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_clock",
            0
          ],
          "destination": [
            "resonance_loop",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_clock",
            0
          ],
          "destination": [
            "resonance_scope",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_loop",
            1
          ],
          "destination": [
            "resonance_binary",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_binary",
            1
          ],
          "destination": [
            "resonance_rprob",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_sal_message",
            0
          ],
          "destination": [
            "resonance_rprob",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_rprob",
            0
          ],
          "destination": [
            "resonance_sequence",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_rprob",
            0
          ],
          "destination": [
            "resonance_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_rprob",
            0
          ],
          "destination": [
            "resonance_edge",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_edge",
            0
          ],
          "destination": [
            "resonance_indicator",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_sequence",
            0
          ],
          "destination": [
            "resonance_makenote",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_rprob",
            0
          ],
          "destination": [
            "resonance_makenote",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_makenote",
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
            "resonance_makenote",
            2
          ],
          "destination": [
            "resonance_midiparse",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_midiparse",
            0
          ],
          "destination": [
            "resonance_note_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_note_unpack",
            0
          ],
          "destination": [
            "resonance_mtof",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_mtof",
            0
          ],
          "destination": [
            "resonance_osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_note_unpack",
            1
          ],
          "destination": [
            "resonance_vel_norm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_vel_norm",
            0
          ],
          "destination": [
            "resonance_env_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_env_pack",
            0
          ],
          "destination": [
            "resonance_env",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_osc",
            0
          ],
          "destination": [
            "resonance_vca",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_env",
            0
          ],
          "destination": [
            "resonance_vca",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_vca",
            0
          ],
          "destination": [
            "resonance_level",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_level",
            0
          ],
          "destination": [
            "resonance_audio_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "resonance_clock_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "resonance_loop_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "resonance_binary_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "resonance_rprob_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_loop_init",
            0
          ],
          "destination": [
            "resonance_loop",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_binary_init",
            0
          ],
          "destination": [
            "resonance_binary",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_rprob_init",
            0
          ],
          "destination": [
            "resonance_rprob",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_notes_load",
            0
          ],
          "destination": [
            "resonance_notes",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "resonance_notes",
            0
          ],
          "destination": [
            "resonance_sequence",
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
            "memory_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_unpack",
            0
          ],
          "destination": [
            "memory_unwrap",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_unpack",
            2
          ],
          "destination": [
            "memory_corr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_unpack",
            3
          ],
          "destination": [
            "memory_sal",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_unpack",
            3
          ],
          "destination": [
            "memory_sal_map",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_sal_map",
            0
          ],
          "destination": [
            "memory_sal_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_unpack",
            4
          ],
          "destination": [
            "memory_drive",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_unwrap",
            0
          ],
          "destination": [
            "memory_phase_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_unwrap",
            1
          ],
          "destination": [
            "memory_bpm_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_unwrap",
            1
          ],
          "destination": [
            "memory_bpm_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_bpm_message",
            0
          ],
          "destination": [
            "memory_clock",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_clock_init",
            0
          ],
          "destination": [
            "memory_clock",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_clock",
            0
          ],
          "destination": [
            "memory_loop",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_clock",
            0
          ],
          "destination": [
            "memory_scope",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_loop",
            1
          ],
          "destination": [
            "memory_binary",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_binary",
            1
          ],
          "destination": [
            "memory_rprob",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_sal_message",
            0
          ],
          "destination": [
            "memory_rprob",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_rprob",
            0
          ],
          "destination": [
            "memory_sequence",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_rprob",
            0
          ],
          "destination": [
            "memory_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_rprob",
            0
          ],
          "destination": [
            "memory_edge",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_edge",
            0
          ],
          "destination": [
            "memory_indicator",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_sequence",
            0
          ],
          "destination": [
            "memory_makenote",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_rprob",
            0
          ],
          "destination": [
            "memory_makenote",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_makenote",
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
            "memory_makenote",
            2
          ],
          "destination": [
            "memory_midiparse",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_midiparse",
            0
          ],
          "destination": [
            "memory_note_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_note_unpack",
            0
          ],
          "destination": [
            "memory_mtof",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_mtof",
            0
          ],
          "destination": [
            "memory_osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_note_unpack",
            1
          ],
          "destination": [
            "memory_vel_norm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_vel_norm",
            0
          ],
          "destination": [
            "memory_env_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_env_pack",
            0
          ],
          "destination": [
            "memory_env",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_osc",
            0
          ],
          "destination": [
            "memory_vca",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_env",
            0
          ],
          "destination": [
            "memory_vca",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_vca",
            0
          ],
          "destination": [
            "memory_level",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_level",
            0
          ],
          "destination": [
            "memory_audio_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "memory_clock_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "memory_loop_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "memory_binary_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "memory_rprob_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_loop_init",
            0
          ],
          "destination": [
            "memory_loop",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_binary_init",
            0
          ],
          "destination": [
            "memory_binary",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_rprob_init",
            0
          ],
          "destination": [
            "memory_rprob",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_notes_load",
            0
          ],
          "destination": [
            "memory_notes",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_notes",
            0
          ],
          "destination": [
            "memory_sequence",
            1
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
            "spatial_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_unpack",
            0
          ],
          "destination": [
            "spatial_unwrap",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_unpack",
            2
          ],
          "destination": [
            "spatial_corr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_unpack",
            3
          ],
          "destination": [
            "spatial_sal",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_unpack",
            3
          ],
          "destination": [
            "spatial_sal_map",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_sal_map",
            0
          ],
          "destination": [
            "spatial_sal_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_unpack",
            4
          ],
          "destination": [
            "spatial_drive",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_unwrap",
            0
          ],
          "destination": [
            "spatial_phase_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_unwrap",
            1
          ],
          "destination": [
            "spatial_bpm_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_unwrap",
            1
          ],
          "destination": [
            "spatial_bpm_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_bpm_message",
            0
          ],
          "destination": [
            "spatial_clock",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_clock_init",
            0
          ],
          "destination": [
            "spatial_clock",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_clock",
            0
          ],
          "destination": [
            "spatial_loop",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_clock",
            0
          ],
          "destination": [
            "spatial_scope",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_loop",
            1
          ],
          "destination": [
            "spatial_binary",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_binary",
            1
          ],
          "destination": [
            "spatial_rprob",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_sal_message",
            0
          ],
          "destination": [
            "spatial_rprob",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_rprob",
            0
          ],
          "destination": [
            "spatial_sequence",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_rprob",
            0
          ],
          "destination": [
            "spatial_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_rprob",
            0
          ],
          "destination": [
            "spatial_edge",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_edge",
            0
          ],
          "destination": [
            "spatial_indicator",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_sequence",
            0
          ],
          "destination": [
            "spatial_makenote",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_rprob",
            0
          ],
          "destination": [
            "spatial_makenote",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_makenote",
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
            "spatial_makenote",
            2
          ],
          "destination": [
            "spatial_midiparse",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_midiparse",
            0
          ],
          "destination": [
            "spatial_note_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_note_unpack",
            0
          ],
          "destination": [
            "spatial_mtof",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_mtof",
            0
          ],
          "destination": [
            "spatial_osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_note_unpack",
            1
          ],
          "destination": [
            "spatial_vel_norm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_vel_norm",
            0
          ],
          "destination": [
            "spatial_env_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_env_pack",
            0
          ],
          "destination": [
            "spatial_env",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_osc",
            0
          ],
          "destination": [
            "spatial_vca",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_env",
            0
          ],
          "destination": [
            "spatial_vca",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_vca",
            0
          ],
          "destination": [
            "spatial_level",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_level",
            0
          ],
          "destination": [
            "spatial_audio_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "spatial_clock_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "spatial_loop_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "spatial_binary_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "global_loadbang",
            0
          ],
          "destination": [
            "spatial_rprob_init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_loop_init",
            0
          ],
          "destination": [
            "spatial_loop",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_binary_init",
            0
          ],
          "destination": [
            "spatial_binary",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_rprob_init",
            0
          ],
          "destination": [
            "spatial_rprob",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_notes_load",
            0
          ],
          "destination": [
            "spatial_notes",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatial_notes",
            0
          ],
          "destination": [
            "spatial_sequence",
            1
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
        "name": "qmw_relational_phase_unwrap_v1.js",
        "type": "TEXT"
      },
      {
        "name": "rtt.clock~.mxo",
        "type": "iLaX"
      },
      {
        "name": "rtt.loop~.mxo",
        "type": "iLaX"
      },
      {
        "name": "rtt.binary~.mxo",
        "type": "iLaX"
      },
      {
        "name": "rtt.rprob~.mxo",
        "type": "iLaX"
      },
      {
        "name": "rtt.sequence~.mxo",
        "type": "iLaX"
      },
      {
        "name": "rtt.makenote~.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
