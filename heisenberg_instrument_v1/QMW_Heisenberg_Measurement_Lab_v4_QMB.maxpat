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
      40.0,
      30.0,
      1660.0,
      910.0
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            14.0,
            1100.0,
            28.0
          ],
          "text": "QMW HEISENBERG MEASUREMENT LAB v4 \u2014 LEGACY AUDIO + QUANTUM MATRIX BUS",
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "thesis",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            45.0,
            1110.0,
            42.0
          ],
          "text": "One question only: how does an intermediate measurement alter the later state? Preparation, later evolution, observable A=(X+Z)/\u221a2, frequencies, gain, panning, and CNMAT renderer remain identical in all three cases."
        }
      },
      {
        "box": {
          "id": "pipeline",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            92.0,
            1100.0,
            25.0
          ],
          "text": "|0\u3009  \u2192  Ry(\u03c0/2)  \u2192  [NO MEASUREMENT / UNREAD Z / RECORDED Z]  \u2192  Ry(\u2212\u03c0/2)  \u2192  same observable A",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "coherent_text",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            128.0,
            350.0,
            52.0
          ],
          "text": "COHERENT\nNo intermediate observation. The two alternatives remain available to interfere."
        }
      },
      {
        "box": {
          "id": "unread_text",
          "maxclass": "comment",
          "patching_rect": [
            395.0,
            128.0,
            350.0,
            52.0
          ],
          "text": "UNREAD\nA Z observation occurs, but its result is discarded. Coherence is lost; no single result remains."
        }
      },
      {
        "box": {
          "id": "recorded_text",
          "maxclass": "comment",
          "patching_rect": [
            765.0,
            128.0,
            350.0,
            52.0
          ],
          "text": "RECORDED\nOne Z result is retained. The later state is pure but conditioned on that particular result."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            195.0,
            126.0,
            22.0
          ],
          "text": "udpreceive 7420",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "route_qmw",
          "maxclass": "newobj",
          "patching_rect": [
            165.0,
            195.0,
            104.0,
            22.0
          ],
          "text": "OSC-route /qmw",
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
          "id": "route_h",
          "maxclass": "newobj",
          "patching_rect": [
            285.0,
            195.0,
            185.0,
            22.0
          ],
          "text": "OSC-route /heisenberg_clear",
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
          "id": "route_active",
          "maxclass": "newobj",
          "patching_rect": [
            485.0,
            195.0,
            125.0,
            22.0
          ],
          "text": "OSC-route /active",
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
          "id": "route_meta",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            235.0,
            865.0,
            22.0
          ],
          "text": "OSC-route /mode /outcome /final_probabilities /bloch /purity /coherence /disturbance /expectation /matrix",
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
          "id": "route_matrix",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            275.0,
            720.0,
            22.0
          ],
          "text": "OSC-route /begin /end /real /imag /magnitude /phase /frequency_hz /pan",
          "numinlets": 1,
          "numoutlets": 9,
          "outlettype": [
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
          "id": "pre_mode",
          "maxclass": "newobj",
          "patching_rect": [
            910.0,
            235.0,
            105.0,
            22.0
          ],
          "text": "prepend mode",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_outcome",
          "maxclass": "newobj",
          "patching_rect": [
            1025.0,
            235.0,
            120.0,
            22.0
          ],
          "text": "prepend outcome",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_probs",
          "maxclass": "newobj",
          "patching_rect": [
            760.0,
            275.0,
            175.0,
            22.0
          ],
          "text": "prepend final_probabilities",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_purity",
          "maxclass": "newobj",
          "patching_rect": [
            950.0,
            275.0,
            105.0,
            22.0
          ],
          "text": "prepend purity",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_coherence",
          "maxclass": "newobj",
          "patching_rect": [
            1065.0,
            275.0,
            135.0,
            22.0
          ],
          "text": "prepend coherence",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_expect",
          "maxclass": "newobj",
          "patching_rect": [
            950.0,
            310.0,
            130.0,
            22.0
          ],
          "text": "prepend expectation",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_begin",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            312.0,
            105.0,
            22.0
          ],
          "text": "prepend begin",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_end",
          "maxclass": "newobj",
          "patching_rect": [
            140.0,
            312.0,
            95.0,
            22.0
          ],
          "text": "prepend end",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_real",
          "maxclass": "newobj",
          "patching_rect": [
            245.0,
            312.0,
            95.0,
            22.0
          ],
          "text": "prepend real",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_mag",
          "maxclass": "newobj",
          "patching_rect": [
            350.0,
            312.0,
            125.0,
            22.0
          ],
          "text": "prepend magnitude",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_freq",
          "maxclass": "newobj",
          "patching_rect": [
            485.0,
            312.0,
            145.0,
            22.0
          ],
          "text": "prepend frequency_hz",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_pan",
          "maxclass": "newobj",
          "patching_rect": [
            640.0,
            312.0,
            95.0,
            22.0
          ],
          "text": "prepend pan",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "renderer",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            360.0,
            290.0,
            22.0
          ],
          "text": "js qmw_heisenberg_clear_renderer_v3.js",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "sin_l",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            405.0,
            105.0,
            22.0
          ],
          "text": "sinusoids~ bwe",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "sin_r",
          "maxclass": "newobj",
          "patching_rect": [
            150.0,
            405.0,
            105.0,
            22.0
          ],
          "text": "sinusoids~ bwe",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "gain_l",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            445.0,
            52.0,
            22.0
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
          "id": "gain_r",
          "maxclass": "newobj",
          "patching_rect": [
            150.0,
            445.0,
            52.0,
            22.0
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
          "id": "meter_l",
          "maxclass": "meter~",
          "patching_rect": [
            225.0,
            425.0,
            18.0,
            60.0
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
            252.0,
            425.0,
            18.0,
            60.0
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
            290.0,
            425.0,
            52.0,
            52.0
          ],
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "matrix_label",
          "maxclass": "comment",
          "patching_rect": [
            395.0,
            355.0,
            340.0,
            20.0
          ],
          "text": "C[m,n] = \u03c1[m,n] A[n,m] \u2014 real contribution"
        }
      },
      {
        "box": {
          "id": "matrix",
          "maxclass": "jit.cellblock",
          "patching_rect": [
            395.0,
            380.0,
            350.0,
            220.0
          ],
          "cols": 2,
          "rows": 2,
          "colhead": 1,
          "rowhead": 1,
          "numinlets": 2,
          "numoutlets": 4,
          "outlettype": [
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "cell_legend",
          "maxclass": "comment",
          "patching_rect": [
            765.0,
            365.0,
            385.0,
            86.0
          ],
          "text": "CELL MEANING\n(0,0) population of |0\u3009 \u2014 110 Hz\n(0,1) and (1,0) coherence \u2014 440 Hz, opposite sides\n(1,1) population of |1\u3009 \u2014 165 Hz"
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            765.0,
            465.0,
            385.0,
            68.0
          ],
          "text": "waiting for one-qubit state...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "bloch_label",
          "maxclass": "comment",
          "patching_rect": [
            765.0,
            550.0,
            165.0,
            20.0
          ],
          "text": "final Bloch vector x / y / z"
        }
      },
      {
        "box": {
          "id": "bloch",
          "maxclass": "multislider",
          "patching_rect": [
            765.0,
            575.0,
            385.0,
            42.0
          ],
          "size": 3,
          "setminmax": [
            -1.0,
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
          "id": "prob_label",
          "maxclass": "comment",
          "patching_rect": [
            765.0,
            630.0,
            220.0,
            20.0
          ],
          "text": "final probabilities P(0), P(1)"
        }
      },
      {
        "box": {
          "id": "prob_view",
          "maxclass": "multislider",
          "patching_rect": [
            765.0,
            655.0,
            385.0,
            42.0
          ],
          "size": 2,
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
          "id": "controls",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            625.0,
            680.0,
            22.0
          ],
          "text": "CHANGE ONLY THE INTERMEDIATE MEASUREMENT PROTOCOL",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "coherent",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            660.0,
            245.0,
            22.0
          ],
          "text": "/qmw/heisenberg_clear/mode coherent",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "unread",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            695.0,
            235.0,
            22.0
          ],
          "text": "/qmw/heisenberg_clear/mode unread",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "recorded",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            730.0,
            250.0,
            22.0
          ],
          "text": "/qmw/heisenberg_clear/mode recorded",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "record",
          "maxclass": "message",
          "patching_rect": [
            295.0,
            730.0,
            215.0,
            22.0
          ],
          "text": "/qmw/heisenberg_clear/record 1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "send",
          "maxclass": "newobj",
          "patching_rect": [
            530.0,
            730.0,
            160.0,
            22.0
          ],
          "text": "udpsend 127.0.0.1 7421",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "compare_toggle",
          "maxclass": "toggle",
          "patching_rect": [
            25.0,
            780.0,
            24.0,
            24.0
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
          "id": "compare_label",
          "maxclass": "comment",
          "patching_rect": [
            58.0,
            783.0,
            170.0,
            20.0
          ],
          "text": "slow comparison (6 sec)"
        }
      },
      {
        "box": {
          "id": "compare_metro",
          "maxclass": "newobj",
          "patching_rect": [
            240.0,
            780.0,
            82.0,
            22.0
          ],
          "text": "metro 6000",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "compare_counter",
          "maxclass": "newobj",
          "patching_rect": [
            335.0,
            780.0,
            82.0,
            22.0
          ],
          "text": "counter 0 2",
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
          "id": "compare_sel",
          "maxclass": "newobj",
          "patching_rect": [
            430.0,
            780.0,
            62.0,
            22.0
          ],
          "text": "sel 0 1 2",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "bang",
            "bang",
            "bang",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "rule",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            830.0,
            1125.0,
            38.0
          ],
          "text": "AUDITION RULE: do not interpret timbral presets\u2014there are none. The two CNMAT banks receive the same four cell frequencies and the same mapping in every case. What changes is only the density matrix produced by the measurement protocol."
        }
      },
      {
        "box": {
          "id": "pre_imag",
          "maxclass": "newobj",
          "patching_rect": [
            1180.0,
            245.0,
            95.0,
            22.0
          ],
          "text": "prepend imag",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_phase",
          "maxclass": "newobj",
          "patching_rect": [
            1285.0,
            245.0,
            105.0,
            22.0
          ],
          "text": "prepend phase",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "qmb_panel",
          "maxclass": "panel",
          "patching_rect": [
            1170.0,
            14.0,
            465.0,
            850.0
          ],
          "bgcolor": [
            0.08,
            0.11,
            0.14,
            1.0
          ],
          "border": 2,
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "qmb_title",
          "maxclass": "comment",
          "patching_rect": [
            1190.0,
            28.0,
            420.0,
            28.0
          ],
          "text": "QUANTUM MATRIX BUS \u2014 LIVE COMPATIBILITY PATH",
          "fontsize": 15.0,
          "textcolor": [
            0.45,
            0.86,
            1.0,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "qmb_note",
          "maxclass": "comment",
          "patching_rect": [
            1190.0,
            62.0,
            410.0,
            60.0
          ],
          "text": "The legacy renderer remains audible. QMB receives the same transactional frame, validates every field, fills an inactive Jitter bank, then commits the complete revision.",
          "textcolor": [
            0.88,
            0.92,
            0.95,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "qmb_selftest",
          "maxclass": "message",
          "patching_rect": [
            1190.0,
            130.0,
            72.0,
            22.0
          ],
          "text": "selftest",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "qmb_selftest_note",
          "maxclass": "comment",
          "patching_rect": [
            1275.0,
            132.0,
            325.0,
            20.0
          ],
          "text": "local 2\u00d72 test; Python engine not required",
          "textcolor": [
            0.75,
            0.8,
            0.84,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "qmb_adapter",
          "maxclass": "newobj",
          "patching_rect": [
            1190.0,
            175.0,
            270.0,
            22.0
          ],
          "text": "js qmb_heisenberg_adapter_v1.js",
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
          "id": "qmb_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            1190.0,
            225.0,
            78.0,
            22.0
          ],
          "text": "jit.unpack 2",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "jit_matrix",
            "jit_matrix"
          ]
        }
      },
      {
        "box": {
          "id": "qmb_real_label",
          "maxclass": "comment",
          "patching_rect": [
            1190.0,
            262.0,
            180.0,
            20.0
          ],
          "text": "QMB contribution \u2014 REAL",
          "textcolor": [
            0.45,
            0.86,
            1.0,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "qmb_real",
          "maxclass": "jit.cellblock",
          "patching_rect": [
            1190.0,
            285.0,
            195.0,
            150.0
          ],
          "cols": 2,
          "rows": 2,
          "colhead": 1,
          "rowhead": 1,
          "numinlets": 2,
          "numoutlets": 4,
          "outlettype": [
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "qmb_imag_label",
          "maxclass": "comment",
          "patching_rect": [
            1410.0,
            262.0,
            190.0,
            20.0
          ],
          "text": "QMB contribution \u2014 IMAG",
          "textcolor": [
            0.45,
            0.86,
            1.0,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "qmb_imag",
          "maxclass": "jit.cellblock",
          "patching_rect": [
            1410.0,
            285.0,
            195.0,
            150.0
          ],
          "cols": 2,
          "rows": 2,
          "colhead": 1,
          "rowhead": 1,
          "numinlets": 2,
          "numoutlets": 4,
          "outlettype": [
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "qmb_mag_label",
          "maxclass": "comment",
          "patching_rect": [
            1190.0,
            455.0,
            180.0,
            20.0
          ],
          "text": "QMB magnitude matrix",
          "textcolor": [
            0.45,
            0.86,
            1.0,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "qmb_mag",
          "maxclass": "jit.cellblock",
          "patching_rect": [
            1190.0,
            478.0,
            195.0,
            150.0
          ],
          "cols": 2,
          "rows": 2,
          "colhead": 1,
          "rowhead": 1,
          "numinlets": 2,
          "numoutlets": 4,
          "outlettype": [
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "qmb_commit_label",
          "maxclass": "comment",
          "patching_rect": [
            1410.0,
            455.0,
            180.0,
            20.0
          ],
          "text": "ATOMIC COMMIT",
          "textcolor": [
            0.45,
            0.86,
            1.0,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "qmb_commit",
          "maxclass": "message",
          "patching_rect": [
            1410.0,
            478.0,
            195.0,
            55.0
          ],
          "text": "waiting for QMB frame...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "qmb_diag",
          "maxclass": "newobj",
          "patching_rect": [
            1410.0,
            550.0,
            185.0,
            22.0
          ],
          "text": "print QMB_HEISENBERG",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "qmb_rule",
          "maxclass": "comment",
          "patching_rect": [
            1190.0,
            655.0,
            410.0,
            90.0
          ],
          "text": "COMMIT RULE\nMatrix outlets announce candidate references. The commit outlet fires last. Downstream QMB consumers must react to commit, so a partial or rejected frame can never become active.",
          "textcolor": [
            0.88,
            0.92,
            0.95,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "qmb_legacy_note",
          "maxclass": "comment",
          "patching_rect": [
            1190.0,
            770.0,
            410.0,
            55.0
          ],
          "text": "Comparison: the original real-contribution cellblock remains at center-left. It and the QMB REAL table should agree for every committed frame.",
          "textcolor": [
            0.75,
            0.8,
            0.84,
            1.0
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
            "route_h",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_h",
            0
          ],
          "destination": [
            "route_active",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_active",
            0
          ],
          "destination": [
            "route_meta",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            8
          ],
          "destination": [
            "route_matrix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            0
          ],
          "destination": [
            "pre_mode",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            1
          ],
          "destination": [
            "pre_outcome",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            2
          ],
          "destination": [
            "pre_probs",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            2
          ],
          "destination": [
            "prob_view",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            3
          ],
          "destination": [
            "bloch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            4
          ],
          "destination": [
            "pre_purity",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            5
          ],
          "destination": [
            "pre_coherence",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            7
          ],
          "destination": [
            "pre_expect",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            0
          ],
          "destination": [
            "pre_begin",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            1
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
            "route_matrix",
            2
          ],
          "destination": [
            "pre_real",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            4
          ],
          "destination": [
            "pre_mag",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            6
          ],
          "destination": [
            "pre_freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            7
          ],
          "destination": [
            "pre_pan",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_mode",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_outcome",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_probs",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_purity",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_coherence",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_expect",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_begin",
            0
          ],
          "destination": [
            "renderer",
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
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_real",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_mag",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_freq",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_pan",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "renderer",
            0
          ],
          "destination": [
            "sin_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "renderer",
            1
          ],
          "destination": [
            "sin_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "renderer",
            2
          ],
          "destination": [
            "matrix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "renderer",
            3
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
            "sin_l",
            0
          ],
          "destination": [
            "gain_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sin_r",
            0
          ],
          "destination": [
            "gain_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gain_l",
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
            "gain_r",
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
            "gain_l",
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
            "gain_r",
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
            "coherent",
            0
          ],
          "destination": [
            "send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unread",
            0
          ],
          "destination": [
            "send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "recorded",
            0
          ],
          "destination": [
            "send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "record",
            0
          ],
          "destination": [
            "send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "compare_toggle",
            0
          ],
          "destination": [
            "compare_metro",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "compare_metro",
            0
          ],
          "destination": [
            "compare_counter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "compare_counter",
            0
          ],
          "destination": [
            "compare_sel",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "compare_sel",
            0
          ],
          "destination": [
            "coherent",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "compare_sel",
            1
          ],
          "destination": [
            "unread",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "compare_sel",
            2
          ],
          "destination": [
            "recorded",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            3
          ],
          "destination": [
            "pre_imag",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            5
          ],
          "destination": [
            "pre_phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_begin",
            0
          ],
          "destination": [
            "qmb_adapter",
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
            "qmb_adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_real",
            0
          ],
          "destination": [
            "qmb_adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_imag",
            0
          ],
          "destination": [
            "qmb_adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_mag",
            0
          ],
          "destination": [
            "qmb_adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_phase",
            0
          ],
          "destination": [
            "qmb_adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_freq",
            0
          ],
          "destination": [
            "qmb_adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_pan",
            0
          ],
          "destination": [
            "qmb_adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "qmb_selftest",
            0
          ],
          "destination": [
            "qmb_adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "qmb_adapter",
            0
          ],
          "destination": [
            "qmb_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "qmb_unpack",
            0
          ],
          "destination": [
            "qmb_real",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "qmb_unpack",
            1
          ],
          "destination": [
            "qmb_imag",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "qmb_adapter",
            1
          ],
          "destination": [
            "qmb_mag",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "qmb_adapter",
            5
          ],
          "destination": [
            "qmb_commit",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "qmb_adapter",
            6
          ],
          "destination": [
            "qmb_diag",
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
        "name": "sinusoids~.mxo",
        "type": "iLaX"
      },
      {
        "name": "qmw_heisenberg_clear_renderer_v3.js",
        "type": "TEXT"
      },
      {
        "name": "qmb_heisenberg_adapter_v1.js",
        "type": "TEXT"
      }
    ],
    "autosave": 0
  }
}
