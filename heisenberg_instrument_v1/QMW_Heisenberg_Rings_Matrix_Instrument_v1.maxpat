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
      45.0,
      40.0,
      1210.0,
      1380.0
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            20.0,
            1100.0,
            32.0
          ],
          "text": "QMW HEISENBERG \u2014 16-BODY COMPLEX MATRIX RINGS INSTRUMENT v1",
          "fontsize": 20.0,
          "fontface": 1
        }
      },
      {
        "box": {
          "id": "concept",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            58.0,
            1130.0,
            42.0
          ],
          "text": "Each matrix row is one vb.mi.rngs~ body. Its sixteen complex relationships determine pitch, structure, brightness, damping, position, excitation, and wavetable phase."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            120.0,
            120.0,
            22.0
          ],
          "text": "udpreceive 7400",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "retry_udp",
          "maxclass": "message",
          "patching_rect": [
            930.0,
            120.0,
            78.0,
            22.0
          ],
          "text": "port 7400",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "retry_udp_label",
          "maxclass": "comment",
          "patching_rect": [
            1015.0,
            121.0,
            145.0,
            34.0
          ],
          "text": "RETRY UDP 7400 after conflict"
        }
      },
      {
        "box": {
          "id": "route_qmw",
          "maxclass": "newobj",
          "patching_rect": [
            165.0,
            120.0,
            105.0,
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
            120.0,
            145.0,
            22.0
          ],
          "text": "OSC-route /heisenberg",
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
            445.0,
            120.0,
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
            585.0,
            120.0,
            330.0,
            22.0
          ],
          "text": "OSC-route /matrix /mode /outcome /disturbance",
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
          "id": "route_matrix",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            165.0,
            650.0,
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
          "id": "pre_begin",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            205.0,
            95.0,
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
            130.0,
            205.0,
            85.0,
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
            220.0,
            205.0,
            90.0,
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
          "id": "pre_imag",
          "maxclass": "newobj",
          "patching_rect": [
            315.0,
            205.0,
            90.0,
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
          "id": "pre_mag",
          "maxclass": "newobj",
          "patching_rect": [
            410.0,
            205.0,
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
          "id": "pre_phase",
          "maxclass": "newobj",
          "patching_rect": [
            540.0,
            205.0,
            100.0,
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
          "id": "pre_freq",
          "maxclass": "newobj",
          "patching_rect": [
            645.0,
            205.0,
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
            795.0,
            205.0,
            90.0,
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
          "id": "adapter",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            255.0,
            245.0,
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
          "id": "tag_c",
          "maxclass": "newobj",
          "patching_rect": [
            300.0,
            250.0,
            135.0,
            22.0
          ],
          "text": "prepend contributions",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "tag_m",
          "maxclass": "newobj",
          "patching_rect": [
            445.0,
            250.0,
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
          "id": "tag_p",
          "maxclass": "newobj",
          "patching_rect": [
            580.0,
            250.0,
            100.0,
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
          "id": "tag_f",
          "maxclass": "newobj",
          "patching_rect": [
            690.0,
            250.0,
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
          "id": "tag_pan",
          "maxclass": "newobj",
          "patching_rect": [
            845.0,
            250.0,
            90.0,
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
          "id": "controller",
          "maxclass": "newobj",
          "patching_rect": [
            300.0,
            300.0,
            285.0,
            22.0
          ],
          "text": "js qmb_heisenberg_rings_controller_v1.js",
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
          "id": "wave_route",
          "maxclass": "newobj",
          "patching_rect": [
            300.0,
            345.0,
            100.0,
            22.0
          ],
          "text": "route jit_matrix",
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
          "id": "wave_name",
          "maxclass": "newobj",
          "patching_rect": [
            300.0,
            380.0,
            130.0,
            22.0
          ],
          "text": "prepend matrix_name",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "wave_send",
          "maxclass": "newobj",
          "patching_rect": [
            300.0,
            415.0,
            185.0,
            22.0
          ],
          "text": "s qmb.heisenberg.rings.wave",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "poly_router",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            345.0,
            270.0,
            22.0
          ],
          "text": "js qmb_heisenberg_rings_poly_router_v1.js",
          "numinlets": 1,
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
            610.0,
            390.0,
            260.0,
            22.0
          ],
          "text": "poly~ qmb_heisenberg_rings_voice_v1 16",
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
          "id": "master_l",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            445.0,
            58.0,
            22.0
          ],
          "text": "*~ 0.85",
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
            745.0,
            445.0,
            58.0,
            22.0
          ],
          "text": "*~ 0.85",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "lim_l",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            480.0,
            105.0,
            22.0
          ],
          "text": "clip~ -0.95 0.95",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "lim_r",
          "maxclass": "newobj",
          "patching_rect": [
            745.0,
            480.0,
            105.0,
            22.0
          ],
          "text": "clip~ -0.95 0.95",
          "numinlets": 1,
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
            825.0,
            435.0,
            18.0,
            65.0
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
            850.0,
            435.0,
            18.0,
            65.0
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
            900.0,
            440.0,
            50.0,
            50.0
          ],
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "sum",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            530.0,
            35.0,
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
          "id": "memory_gain",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            565.0,
            55.0,
            22.0
          ],
          "text": "*~ 0.5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "mem_matrix",
          "maxclass": "newobj",
          "patching_rect": [
            700.0,
            565.0,
            330.0,
            22.0
          ],
          "text": "jit.matrix qmb_heisenberg_rings_memory 1 float32 256 64",
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
          "id": "x_phase",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            610.0,
            112.0,
            22.0
          ],
          "text": "phasor~ 172.265625",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "x_scale",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            645.0,
            58.0,
            22.0
          ],
          "text": "*~ 255.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "y_phase",
          "maxclass": "newobj",
          "patching_rect": [
            750.0,
            610.0,
            85.0,
            22.0
          ],
          "text": "phasor~ 0.05",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "y_scale",
          "maxclass": "newobj",
          "patching_rect": [
            750.0,
            645.0,
            52.0,
            22.0
          ],
          "text": "*~ 63.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "poke",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            690.0,
            280.0,
            22.0
          ],
          "text": "jit.poke~ qmb_heisenberg_rings_memory 2 0",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "memory_note",
          "maxclass": "comment",
          "patching_rect": [
            610.0,
            725.0,
            420.0,
            42.0
          ],
          "text": "jit.poke~ writes the resulting acoustic output into a separate 256\u00d764 performance memory. The canonical quantum matrices are never overwritten."
        }
      },
      {
        "box": {
          "id": "diag_adapter",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            305.0,
            175.0,
            22.0
          ],
          "text": "print QMB_RINGS_ADAPTER",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "adapter_status",
          "maxclass": "message",
          "patching_rect": [
            30.0,
            340.0,
            245.0,
            48.0
          ],
          "text": "adapter: waiting for /matrix/begin...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "diag_music",
          "maxclass": "newobj",
          "patching_rect": [
            300.0,
            455.0,
            165.0,
            22.0
          ],
          "text": "print QMB_RINGS_MUSIC",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            300.0,
            490.0,
            280.0,
            48.0
          ],
          "text": "waiting for musical matrix commit...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "controls_label",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            585.0,
            430.0,
            22.0
          ],
          "text": "HEISENBERG CONTROLS \u2014 publisher listens on UDP 7412",
          "fontface": 1
        }
      },
      {
        "box": {
          "id": "coherent",
          "maxclass": "message",
          "patching_rect": [
            30.0,
            620.0,
            250.0,
            22.0
          ],
          "text": "/qmw/heisenberg/mode coherent",
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
            30.0,
            655.0,
            240.0,
            22.0
          ],
          "text": "/qmw/heisenberg/mode unread",
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
            30.0,
            690.0,
            255.0,
            22.0
          ],
          "text": "/qmw/heisenberg/mode recorded",
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
            300.0,
            690.0,
            215.0,
            22.0
          ],
          "text": "/qmw/heisenberg/record 1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "xz",
          "maxclass": "message",
          "patching_rect": [
            300.0,
            620.0,
            250.0,
            22.0
          ],
          "text": "/qmw/heisenberg/observable XZ0",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "y0",
          "maxclass": "message",
          "patching_rect": [
            300.0,
            655.0,
            245.0,
            22.0
          ],
          "text": "/qmw/heisenberg/observable Y0",
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
            30.0,
            740.0,
            165.0,
            22.0
          ],
          "text": "udpsend 127.0.0.1 7412",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "phase_label",
          "maxclass": "comment",
          "patching_rect": [
            610.0,
            790.0,
            500.0,
            22.0
          ],
          "text": "LIVE PHASE OBSERVABLE \u2014 normalized 0\u20261 maps to 0\u20262\u03c0 radians",
          "fontface": 1
        }
      },
      {
        "box": {
          "id": "phase_norm",
          "maxclass": "flonum",
          "patching_rect": [
            610.0,
            825.0,
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
          "id": "phase_clip",
          "maxclass": "newobj",
          "patching_rect": [
            710.0,
            825.0,
            70.0,
            22.0
          ],
          "text": "clip 0. 1.",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "phase_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            790.0,
            825.0,
            255.0,
            22.0
          ],
          "text": "prepend /qmw/bridge/observable/phase",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "phase_send",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            860.0,
            165.0,
            22.0
          ],
          "text": "udpsend 127.0.0.1 7421",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "phase_0",
          "maxclass": "message",
          "patching_rect": [
            790.0,
            860.0,
            38.0,
            22.0
          ],
          "text": "0.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "phase_y",
          "maxclass": "message",
          "patching_rect": [
            835.0,
            860.0,
            42.0,
            22.0
          ],
          "text": "0.25",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "phase_pi",
          "maxclass": "message",
          "patching_rect": [
            884.0,
            860.0,
            38.0,
            22.0
          ],
          "text": "0.5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "phase_minus_y",
          "maxclass": "message",
          "patching_rect": [
            929.0,
            860.0,
            42.0,
            22.0
          ],
          "text": "0.75",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "phase_tau",
          "maxclass": "message",
          "patching_rect": [
            978.0,
            860.0,
            32.0,
            22.0
          ],
          "text": "1.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "four_observable",
          "maxclass": "message",
          "patching_rect": [
            1020.0,
            860.0,
            180.0,
            22.0
          ],
          "text": "/qmw/bridge/observable FOUR",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "rate_label",
          "maxclass": "comment",
          "patching_rect": [
            610.0,
            895.0,
            175.0,
            22.0
          ],
          "text": "MUSICAL COMMIT RATE (Hz)"
        }
      },
      {
        "box": {
          "id": "rate_hz",
          "maxclass": "flonum",
          "patching_rect": [
            790.0,
            895.0,
            70.0,
            22.0
          ],
          "minimum": 0.25,
          "maximum": 30.0,
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
          "id": "rate_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            870.0,
            895.0,
            220.0,
            22.0
          ],
          "text": "prepend /qmw/bridge/output_hz",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "smooth_label",
          "maxclass": "comment",
          "patching_rect": [
            610.0,
            930.0,
            175.0,
            22.0
          ],
          "text": "COMPLEX SMOOTHING (ms)"
        }
      },
      {
        "box": {
          "id": "smooth_ms",
          "maxclass": "flonum",
          "patching_rect": [
            790.0,
            930.0,
            70.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 5000.0,
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
          "id": "smooth_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            870.0,
            930.0,
            235.0,
            22.0
          ],
          "text": "prepend /qmw/bridge/smoothing_ms",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "qubit_phase_label",
          "maxclass": "comment",
          "patching_rect": [
            610.0,
            965.0,
            500.0,
            22.0
          ],
          "text": "QUBIT PHASE OFFSETS \u2014 normalized turns (defaults: 0, .25, .5, .75)"
        }
      },
      {
        "box": {
          "id": "q0_phase",
          "maxclass": "flonum",
          "patching_rect": [
            610.0,
            1000.0,
            58.0,
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
          "id": "q1_phase",
          "maxclass": "flonum",
          "patching_rect": [
            735.0,
            1000.0,
            58.0,
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
          "id": "q2_phase",
          "maxclass": "flonum",
          "patching_rect": [
            860.0,
            1000.0,
            58.0,
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
          "id": "q3_phase",
          "maxclass": "flonum",
          "patching_rect": [
            985.0,
            1000.0,
            58.0,
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
          "id": "q0_label",
          "maxclass": "comment",
          "patching_rect": [
            675.0,
            1001.0,
            24.0,
            22.0
          ],
          "text": "q0"
        }
      },
      {
        "box": {
          "id": "q1_label",
          "maxclass": "comment",
          "patching_rect": [
            800.0,
            1001.0,
            24.0,
            22.0
          ],
          "text": "q1"
        }
      },
      {
        "box": {
          "id": "q2_label",
          "maxclass": "comment",
          "patching_rect": [
            925.0,
            1001.0,
            24.0,
            22.0
          ],
          "text": "q2"
        }
      },
      {
        "box": {
          "id": "q3_label",
          "maxclass": "comment",
          "patching_rect": [
            1050.0,
            1001.0,
            24.0,
            22.0
          ],
          "text": "q3"
        }
      },
      {
        "box": {
          "id": "q0_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            1035.0,
            280.0,
            22.0
          ],
          "text": "prepend /qmw/bridge/observable/phase/q0",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "q1_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            1065.0,
            280.0,
            22.0
          ],
          "text": "prepend /qmw/bridge/observable/phase/q1",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "q2_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            900.0,
            1035.0,
            280.0,
            22.0
          ],
          "text": "prepend /qmw/bridge/observable/phase/q2",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "q3_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            900.0,
            1065.0,
            280.0,
            22.0
          ],
          "text": "prepend /qmw/bridge/observable/phase/q3",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "morph_label",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            1100.0,
            360.0,
            22.0
          ],
          "text": "VOICE MAPPING CROSSFADE \u2014 relational 0 \u2190\u2192 component 1",
          "fontface": 1
        }
      },
      {
        "box": {
          "id": "mapping_morph",
          "maxclass": "flonum",
          "patching_rect": [
            400.0,
            1100.0,
            70.0,
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
          "id": "morph_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            480.0,
            1100.0,
            155.0,
            22.0
          ],
          "text": "prepend mapping_morph",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "morph_rel",
          "maxclass": "message",
          "patching_rect": [
            650.0,
            1100.0,
            32.0,
            22.0
          ],
          "text": "0.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "morph_mid",
          "maxclass": "message",
          "patching_rect": [
            690.0,
            1100.0,
            38.0,
            22.0
          ],
          "text": "0.5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "morph_comp",
          "maxclass": "message",
          "patching_rect": [
            736.0,
            1100.0,
            32.0,
            22.0
          ],
          "text": "1.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "voice_map_label",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            1140.0,
            760.0,
            22.0
          ],
          "text": "PER-VOICE MAP \u2014 voice_map <1\u202616 | 0=all> <destination> <source> <amount -1\u20261>",
          "fontface": 1
        }
      },
      {
        "box": {
          "id": "map_example_1",
          "maxclass": "message",
          "patching_rect": [
            30.0,
            1175.0,
            235.0,
            22.0
          ],
          "text": "voice_map 1 brightness real 1.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "map_example_2",
          "maxclass": "message",
          "patching_rect": [
            275.0,
            1175.0,
            275.0,
            22.0
          ],
          "text": "voice_map 1 damping magnitude -0.5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "map_example_3",
          "maxclass": "message",
          "patching_rect": [
            560.0,
            1175.0,
            255.0,
            22.0
          ],
          "text": "voice_map 7 structure phase 0.4",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "map_example_all",
          "maxclass": "message",
          "patching_rect": [
            825.0,
            1175.0,
            260.0,
            22.0
          ],
          "text": "voice_map 0 position imag 0.6",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "map_clear",
          "maxclass": "message",
          "patching_rect": [
            30.0,
            1210.0,
            135.0,
            22.0
          ],
          "text": "voice_map_clear 0",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "map_sources",
          "maxclass": "comment",
          "patching_rect": [
            180.0,
            1210.0,
            900.0,
            22.0
          ],
          "text": "sources: magnitude real imag phase frequency pan     destinations: structure brightness damping position"
        }
      },
      {
        "box": {
          "id": "cell_map_label",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            1250.0,
            850.0,
            22.0
          ],
          "text": "RAW REALTIME CELL MAP \u2014 cell_map <voice> <destination> <list> <column 1\u202616> <amount>",
          "fontface": 1
        }
      },
      {
        "box": {
          "id": "cell_example_1",
          "maxclass": "message",
          "patching_rect": [
            30.0,
            1285.0,
            270.0,
            22.0
          ],
          "text": "cell_map 1 brightness real 4 1.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "cell_example_2",
          "maxclass": "message",
          "patching_rect": [
            310.0,
            1285.0,
            300.0,
            22.0
          ],
          "text": "cell_map 2 damping magnitude 9 0.7",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "cell_example_3",
          "maxclass": "message",
          "patching_rect": [
            620.0,
            1285.0,
            280.0,
            22.0
          ],
          "text": "cell_map 7 structure imag 12 -0.5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "cell_example_all",
          "maxclass": "message",
          "patching_rect": [
            910.0,
            1285.0,
            270.0,
            22.0
          ],
          "text": "cell_map 0 position phase 8 0.4",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "cell_clear",
          "maxclass": "message",
          "patching_rect": [
            30.0,
            1320.0,
            130.0,
            22.0
          ],
          "text": "cell_map_clear 0",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "run_note",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            790.0,
            540.0,
            70.0
          ],
          "text": "Static proof: run heisenberg_lab_v1. Live motion: run quantumsonification_conductor.py on 7421 plus qmb_conductor_density_bridge_v1. Max continues to receive committed matrices on 7400."
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "retry_udp",
            0
          ],
          "destination": [
            "udp",
            0
          ]
        }
      },
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
            0
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
            "pre_begin",
            0
          ],
          "destination": [
            "adapter",
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
            "adapter",
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
            "adapter",
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
            "adapter",
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
            "adapter",
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
            "adapter",
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
            "adapter",
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
            "adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            0
          ],
          "destination": [
            "tag_c",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            1
          ],
          "destination": [
            "tag_m",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            2
          ],
          "destination": [
            "tag_p",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            3
          ],
          "destination": [
            "tag_f",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            4
          ],
          "destination": [
            "tag_pan",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            5
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
            "adapter",
            6
          ],
          "destination": [
            "diag_adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            6
          ],
          "destination": [
            "adapter_status",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "tag_c",
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
            "tag_m",
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
            "tag_p",
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
            "tag_f",
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
            "tag_pan",
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
            "controller",
            0
          ],
          "destination": [
            "wave_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wave_route",
            0
          ],
          "destination": [
            "wave_name",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wave_name",
            0
          ],
          "destination": [
            "wave_send",
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
            "poly_router",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "poly_router",
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
            2
          ],
          "destination": [
            "diag_music",
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
            "master_l",
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
            "master_r",
            0
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
            "lim_l",
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
            "lim_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "lim_l",
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
            "lim_r",
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
            "lim_l",
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
            "lim_r",
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
            "lim_l",
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
            "lim_r",
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
            "sum",
            0
          ],
          "destination": [
            "memory_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "memory_gain",
            0
          ],
          "destination": [
            "poke",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "x_phase",
            0
          ],
          "destination": [
            "x_scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "x_scale",
            0
          ],
          "destination": [
            "poke",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "y_phase",
            0
          ],
          "destination": [
            "y_scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "y_scale",
            0
          ],
          "destination": [
            "poke",
            2
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
            "xz",
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
            "y0",
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
            "xz",
            0
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "y0",
            0
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "four_observable",
            0
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_norm",
            0
          ],
          "destination": [
            "phase_clip",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_clip",
            0
          ],
          "destination": [
            "phase_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_prepend",
            0
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_0",
            0
          ],
          "destination": [
            "phase_norm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_y",
            0
          ],
          "destination": [
            "phase_norm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_pi",
            0
          ],
          "destination": [
            "phase_norm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_minus_y",
            0
          ],
          "destination": [
            "phase_norm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_tau",
            0
          ],
          "destination": [
            "phase_norm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rate_hz",
            0
          ],
          "destination": [
            "rate_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rate_prepend",
            0
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "smooth_ms",
            0
          ],
          "destination": [
            "smooth_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "smooth_prepend",
            0
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "q0_phase",
            0
          ],
          "destination": [
            "q0_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "q0_prepend",
            0
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "q1_phase",
            0
          ],
          "destination": [
            "q1_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "q1_prepend",
            0
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "q2_phase",
            0
          ],
          "destination": [
            "q2_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "q2_prepend",
            0
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "q3_phase",
            0
          ],
          "destination": [
            "q3_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "q3_prepend",
            0
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mapping_morph",
            0
          ],
          "destination": [
            "morph_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "morph_prepend",
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
            "morph_rel",
            0
          ],
          "destination": [
            "mapping_morph",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "morph_mid",
            0
          ],
          "destination": [
            "mapping_morph",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "morph_comp",
            0
          ],
          "destination": [
            "mapping_morph",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "map_example_1",
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
            "map_example_2",
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
            "map_example_3",
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
            "map_example_all",
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
            "map_clear",
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
            "cell_example_1",
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
            "cell_example_2",
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
            "cell_example_3",
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
            "cell_example_all",
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
            "cell_clear",
            0
          ],
          "destination": [
            "controller",
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
        "name": "qmb_heisenberg_adapter_v1.js",
        "type": "TEXT"
      },
      {
        "name": "qmb_heisenberg_rings_controller_v1.js",
        "type": "TEXT"
      },
      {
        "name": "qmb_heisenberg_rings_poly_router_v1.js",
        "type": "TEXT"
      },
      {
        "name": "qmb_heisenberg_rings_voice_v1.maxpat",
        "type": "JSON"
      }
    ],
    "autosave": 0
  }
}
