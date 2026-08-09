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
      35.0,
      1200.0,
      990.0
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
            25.0,
            14.0,
            1130.0,
            28.0
          ],
          "text": "QMW HEISENBERG LAB v2 \u2014 CNMAT SPECTRAL / 16 \u00d7 16 TRANSITION FIELD",
          "fontsize": 17.0
        }
      },
      {
        "box": {
          "id": "description",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            45.0,
            1140.0,
            42.0
          ],
          "text": "The same 256 ordered relations become bandwidth-enhanced partials, a shared-input resonator bank, and simultaneous 1TRC / 1RES SDIF frames. Measurement changes the excitation process, not merely the tuning."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            100.0,
            126.0,
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
          "id": "route_qmw",
          "maxclass": "newobj",
          "patching_rect": [
            170.0,
            100.0,
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
            292.0,
            100.0,
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
            455.0,
            100.0,
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
            140.0,
            650.0,
            22.0
          ],
          "text": "OSC-route /mode /outcome /disturbance /coherence_before /coherence_after /matrix",
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
          "id": "route_matrix",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            180.0,
            810.0,
            22.0
          ],
          "text": "OSC-route /begin /end /magnitude_normalized /frequency_hz /phase /pan /real /imag",
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
            850.0,
            180.0,
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
            970.0,
            180.0,
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
          "id": "pre_mag",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            218.0,
            185.0,
            22.0
          ],
          "text": "prepend magnitude_normalized",
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
            225.0,
            218.0,
            150.0,
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
          "id": "pre_phase",
          "maxclass": "newobj",
          "patching_rect": [
            390.0,
            218.0,
            110.0,
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
          "id": "pre_pan",
          "maxclass": "newobj",
          "patching_rect": [
            515.0,
            218.0,
            100.0,
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
          "id": "pre_mode",
          "maxclass": "newobj",
          "patching_rect": [
            700.0,
            140.0,
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
            815.0,
            140.0,
            125.0,
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
          "id": "pre_disturbance",
          "maxclass": "newobj",
          "patching_rect": [
            950.0,
            140.0,
            145.0,
            22.0
          ],
          "text": "prepend disturbance",
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
            25.0,
            265.0,
            305.0,
            22.0
          ],
          "text": "js qmw_heisenberg_cnmat_spectral_v2.js",
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
          "id": "sin_l",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            310.0,
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
            145.0,
            310.0,
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
          "id": "res_l",
          "maxclass": "newobj",
          "patching_rect": [
            270.0,
            310.0,
            125.0,
            22.0
          ],
          "text": "resonators~ smooth",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "res_r",
          "maxclass": "newobj",
          "patching_rect": [
            410.0,
            310.0,
            125.0,
            22.0
          ],
          "text": "resonators~ smooth",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "noise",
          "maxclass": "newobj",
          "patching_rect": [
            555.0,
            310.0,
            52.0,
            22.0
          ],
          "text": "noise~",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "noise_mul",
          "maxclass": "newobj",
          "patching_rect": [
            555.0,
            350.0,
            42.0,
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
          "id": "control_route",
          "maxclass": "newobj",
          "patching_rect": [
            640.0,
            310.0,
            285.0,
            22.0
          ],
          "text": "route impulse noise_gain sin_gain res_gain",
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
          "id": "noise_pack",
          "maxclass": "newobj",
          "patching_rect": [
            700.0,
            350.0,
            92.0,
            22.0
          ],
          "text": "pack 0. 80.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "noise_line",
          "maxclass": "newobj",
          "patching_rect": [
            700.0,
            382.0,
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
          "id": "sin_pack",
          "maxclass": "newobj",
          "patching_rect": [
            805.0,
            350.0,
            92.0,
            22.0
          ],
          "text": "pack 0. 80.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "sin_line",
          "maxclass": "newobj",
          "patching_rect": [
            805.0,
            382.0,
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
          "id": "res_pack",
          "maxclass": "newobj",
          "patching_rect": [
            910.0,
            350.0,
            92.0,
            22.0
          ],
          "text": "pack 0. 80.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "res_line",
          "maxclass": "newobj",
          "patching_rect": [
            910.0,
            382.0,
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
          "id": "sin_l_gain",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            400.0,
            42.0,
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
          "id": "sin_r_gain",
          "maxclass": "newobj",
          "patching_rect": [
            145.0,
            400.0,
            42.0,
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
          "id": "res_l_gain",
          "maxclass": "newobj",
          "patching_rect": [
            270.0,
            400.0,
            42.0,
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
          "id": "res_r_gain",
          "maxclass": "newobj",
          "patching_rect": [
            410.0,
            400.0,
            42.0,
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
          "id": "sum_l",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            445.0,
            42.0,
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
          "id": "sum_r",
          "maxclass": "newobj",
          "patching_rect": [
            145.0,
            445.0,
            42.0,
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
          "id": "master_l",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            485.0,
            52.0,
            22.0
          ],
          "text": "*~ 0.55",
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
            145.0,
            485.0,
            52.0,
            22.0
          ],
          "text": "*~ 0.55",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            525.0,
            52.0,
            32.0
          ],
          "text": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "matrix",
          "maxclass": "jit.cellblock",
          "patching_rect": [
            610.0,
            430.0,
            555.0,
            350.0
          ],
          "cols": 16,
          "rows": 16,
          "colhead": 0,
          "rowhead": 0,
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
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            580.0,
            550.0,
            42.0
          ],
          "text": "waiting for CNMAT Heisenberg field...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "sdif_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            638.0,
            550.0,
            20.0
          ],
          "text": "LIVE SDIF MEMORY \u2014 every active matrix is written as both sinusoidal tracks and resonances"
        }
      },
      {
        "box": {
          "id": "trc_buffer",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            668.0,
            205.0,
            22.0
          ],
          "text": "SDIF-buffer qmw_heisenberg_trc",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "trc_poke",
          "maxclass": "newobj",
          "patching_rect": [
            245.0,
            668.0,
            215.0,
            22.0
          ],
          "text": "SDIF-listpoke qmw_heisenberg_trc",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "res_buffer",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            703.0,
            205.0,
            22.0
          ],
          "text": "SDIF-buffer qmw_heisenberg_res",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "res_poke",
          "maxclass": "newobj",
          "patching_rect": [
            245.0,
            703.0,
            215.0,
            22.0
          ],
          "text": "SDIF-listpoke qmw_heisenberg_res",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "write_trc",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            738.0,
            250.0,
            22.0
          ],
          "text": "write QMW_Heisenberg_1TRC.sdif",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "write_res",
          "maxclass": "message",
          "patching_rect": [
            290.0,
            738.0,
            250.0,
            22.0
          ],
          "text": "write QMW_Heisenberg_1RES.sdif",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
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
            790.0,
            1140.0,
            20.0
          ],
          "text": "ONE CONTROLLED COMPARISON \u2014 keep XZ0 fixed and change only the status of the intermediate measurement"
        }
      },
      {
        "box": {
          "id": "coherent",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            820.0,
            225.0,
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
            260.0,
            820.0,
            215.0,
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
            485.0,
            820.0,
            230.0,
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
            725.0,
            820.0,
            195.0,
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
          "id": "test",
          "maxclass": "message",
          "patching_rect": [
            940.0,
            820.0,
            72.0,
            22.0
          ],
          "text": "test",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "resume",
          "maxclass": "message",
          "patching_rect": [
            1022.0,
            820.0,
            72.0,
            22.0
          ],
          "text": "resume",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "obs_xz",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            855.0,
            220.0,
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
          "id": "obs_x",
          "maxclass": "message",
          "patching_rect": [
            260.0,
            855.0,
            210.0,
            22.0
          ],
          "text": "/qmw/heisenberg/observable X0",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "obs_y",
          "maxclass": "message",
          "patching_rect": [
            485.0,
            855.0,
            210.0,
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
          "id": "obs_z",
          "maxclass": "message",
          "patching_rect": [
            710.0,
            855.0,
            210.0,
            22.0
          ],
          "text": "/qmw/heisenberg/observable Z0",
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
            940.0,
            855.0,
            160.0,
            22.0
          ],
          "text": "udpsend 127.0.0.1 7412",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "compare_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            890.0,
            1140.0,
            20.0
          ],
          "text": "AUTO COMPARE (4 seconds each): COHERENT = alternatives retained  \u2192  UNREAD = coherence lost, no fact retained  \u2192  RECORDED = one outcome conditions the future"
        }
      },
      {
        "box": {
          "id": "compare_toggle",
          "maxclass": "toggle",
          "patching_rect": [
            25.0,
            918.0,
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
          "id": "compare_toggle_label",
          "maxclass": "comment",
          "patching_rect": [
            55.0,
            920.0,
            118.0,
            20.0
          ],
          "text": "run comparison"
        }
      },
      {
        "box": {
          "id": "compare_metro",
          "maxclass": "newobj",
          "patching_rect": [
            180.0,
            918.0,
            78.0,
            22.0
          ],
          "text": "metro 4000",
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
            270.0,
            918.0,
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
          "id": "compare_select",
          "maxclass": "newobj",
          "patching_rect": [
            365.0,
            918.0,
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
          "id": "listen",
          "maxclass": "comment",
          "patching_rect": [
            455.0,
            910.0,
            700.0,
            38.0
          ],
          "text": "Listen for continuity \u2192 diffuse/noisy resonance \u2192 outcome-triggered strike. The point is the changed measurement context, not three arbitrary presets."
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
            "pre_disturbance",
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
            "pre_mag",
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
            "pre_freq",
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
            "pre_phase",
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
            "js",
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
            "js",
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
            "js",
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
            "js",
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
            "js",
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
            "js",
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
            "js",
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
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_disturbance",
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
            "sin_l",
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
            "sin_r",
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
            "res_l",
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
            "res_r",
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
            "control_route",
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
            "matrix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            6
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
            "js",
            7
          ],
          "destination": [
            "trc_poke",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            8
          ],
          "destination": [
            "res_poke",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "noise",
            0
          ],
          "destination": [
            "noise_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "noise_line",
            0
          ],
          "destination": [
            "noise_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "noise_mul",
            0
          ],
          "destination": [
            "res_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "noise_mul",
            0
          ],
          "destination": [
            "res_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "control_route",
            0
          ],
          "destination": [
            "res_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "control_route",
            0
          ],
          "destination": [
            "res_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "control_route",
            1
          ],
          "destination": [
            "noise_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "noise_pack",
            0
          ],
          "destination": [
            "noise_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "control_route",
            2
          ],
          "destination": [
            "sin_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sin_pack",
            0
          ],
          "destination": [
            "sin_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "control_route",
            3
          ],
          "destination": [
            "res_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "res_pack",
            0
          ],
          "destination": [
            "res_line",
            0
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
            "sin_l_gain",
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
            "sin_r_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sin_line",
            0
          ],
          "destination": [
            "sin_l_gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sin_line",
            0
          ],
          "destination": [
            "sin_r_gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "res_l",
            0
          ],
          "destination": [
            "res_l_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "res_r",
            0
          ],
          "destination": [
            "res_r_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "res_line",
            0
          ],
          "destination": [
            "res_l_gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "res_line",
            0
          ],
          "destination": [
            "res_r_gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sin_l_gain",
            0
          ],
          "destination": [
            "sum_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "res_l_gain",
            0
          ],
          "destination": [
            "sum_l",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sin_r_gain",
            0
          ],
          "destination": [
            "sum_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "res_r_gain",
            0
          ],
          "destination": [
            "sum_r",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sum_l",
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
            "sum_r",
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
            "master_l",
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
            "master_r",
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
            "write_trc",
            0
          ],
          "destination": [
            "trc_buffer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "write_res",
            0
          ],
          "destination": [
            "res_buffer",
            0
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
            "obs_xz",
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
            "obs_x",
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
            "obs_y",
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
            "obs_z",
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
            "test",
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
            "resume",
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
            "compare_select",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "compare_select",
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
            "compare_select",
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
            "compare_select",
            2
          ],
          "destination": [
            "recorded",
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
        "name": "qmw_heisenberg_cnmat_spectral_v2.js",
        "type": "TEXT"
      },
      {
        "name": "sinusoids~.mxo",
        "type": "iLaX"
      },
      {
        "name": "resonators~.mxo",
        "type": "iLaX"
      },
      {
        "name": "SDIF-buffer.mxo",
        "type": "iLaX"
      },
      {
        "name": "SDIF-listpoke.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
