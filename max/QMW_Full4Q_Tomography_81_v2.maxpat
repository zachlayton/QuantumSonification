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
      50.0,
      1440.0,
      1140.0
    ],
    "gridsize": [
      15.0,
      15.0
    ],
    "boxes": [
      {
        "box": {
          "fontsize": 20.0,
          "id": "title",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            28.0,
            18.0,
            920.0,
            29.0
          ],
          "text": "QMW \u00b7 FULL FOUR-QUBIT TOMOGRAPHY \u00b7 2D WAVETABLE INSTRUMENT v2",
          "textcolor": [
            0.12,
            0.82,
            0.92,
            1.0
          ]
        }
      },
      {
        "box": {
          "fontsize": 13.0,
          "id": "subtitle",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            54.0,
            1180.0,
            21.0
          ],
          "text": "Two 81 \u00d7 256 wavetable surfaces preserve LOCAL and IBM independently. X is oscillator phase; signal-rate Y scans the complete tomography score; Difference Only reveals the IBM \u2212 LOCAL spectral residue."
        }
      },
      {
        "box": {
          "fontsize": 11.0,
          "id": "launch",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            94.0,
            1280.0,
            19.0
          ],
          "text": "Start Python from workshop_lightweight:  /Users/zlayton/miniconda3/envs/music/bin/python qmw_full4q_tomography_osc_v1.py --save-dir /Users/zlayton/QuantumSonification/full4q_tomography_v1/runs",
          "textcolor": [
            0.7,
            0.72,
            0.76,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "ghz",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            30.0,
            132.0,
            130.0,
            22.0
          ],
          "text": "ghz none 256 23"
        }
      },
      {
        "box": {
          "id": "ghzqft",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            170.0,
            132.0,
            130.0,
            22.0
          ],
          "text": "ghz qft 256 23"
        }
      },
      {
        "box": {
          "id": "bell",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            310.0,
            132.0,
            130.0,
            22.0
          ],
          "text": "bell none 256 23"
        }
      },
      {
        "box": {
          "id": "weave",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            450.0,
            132.0,
            140.0,
            22.0
          ],
          "text": "weave none 256 23"
        }
      },
      {
        "box": {
          "fontsize": 11.0,
          "id": "runlabel",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            160.0,
            550.0,
            19.0
          ],
          "text": "Edit any message as preset  transform  shots  seed, then click it."
        }
      },
      {
        "box": {
          "id": "opack_run",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "FullPacket"
          ],
          "patching_rect": [
            612.0,
            132.0,
            194.0,
            22.0
          ],
          "text": "o.pack /qmw/tomography/run"
        }
      },
      {
        "box": {
          "id": "udpsend",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            822.0,
            132.0,
            160.0,
            22.0
          ],
          "text": "udpsend 127.0.0.1 7425"
        }
      },
      {
        "box": {
          "id": "pingbutton",
          "maxclass": "button",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1000.0,
            132.0,
            24.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "opack_ping",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "FullPacket"
          ],
          "patching_rect": [
            1034.0,
            132.0,
            196.0,
            22.0
          ],
          "text": "o.pack /qmw/tomography/ping"
        }
      },
      {
        "box": {
          "fontsize": 10.0,
          "id": "pinglabel",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            995.0,
            158.0,
            240.0,
            18.0
          ],
          "text": "ping Python service"
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            30.0,
            188.0,
            1200.0,
            23.0
          ],
          "text": "\"LOCAL\u2713  IBM\u2713  mix 0.500  setting 40.500/80  YYYY \u2192 YYYZ  row morph 0.500\""
        }
      },
      {
        "box": {
          "fontsize": 12.0,
          "id": "heatlabel",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            226.0,
            560.0,
            20.0
          ],
          "text": "THE 81-SETTING SCORE \u00b7 each row is one XXXX\u2026ZZZZ setting; 16 basis bins across",
          "textcolor": [
            0.9,
            0.72,
            0.22,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "heatmap",
          "maxclass": "jit.pwindow",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "jit_matrix",
            ""
          ],
          "patching_rect": [
            30.0,
            254.0,
            560.0,
            390.0
          ],
          "sync": 1
        }
      },
      {
        "box": {
          "fontsize": 12.0,
          "id": "selectlabel",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            625.0,
            226.0,
            185.0,
            20.0
          ],
          "text": "SETTING / Y POSITION (0\u201380)",
          "textcolor": [
            0.9,
            0.72,
            0.22,
            1.0
          ]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "select",
          "maxclass": "flonum",
          "maximum": 80.0,
          "minimum": 0.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            625.0,
            254.0,
            72.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "prepend_select",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            712.0,
            254.0,
            96.0,
            22.0
          ],
          "text": "prepend select"
        }
      },
      {
        "box": {
          "fontsize": 12.0,
          "id": "mixlabel",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            820.0,
            226.0,
            420.0,
            20.0
          ],
          "text": "LOCAL  \u2190  COMPLETE-DATA CROSSFADE  \u2192  IBM",
          "textcolor": [
            0.12,
            0.82,
            0.92,
            1.0
          ]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "mix",
          "maxclass": "flonum",
          "maximum": 1.0,
          "minimum": 0.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            820.0,
            254.0,
            92.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "prepend_xfade",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            926.0,
            254.0,
            106.0,
            22.0
          ],
          "text": "prepend xfade"
        }
      },
      {
        "box": {
          "fontsize": 11.0,
          "id": "mixhelp",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1044.0,
            254.0,
            285.0,
            19.0
          ],
          "text": "0.000 = local     1.000 = IBM"
        }
      },
      {
        "box": {
          "fontsize": 11.0,
          "id": "histlabel",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            625.0,
            292.0,
            500.0,
            19.0
          ],
          "text": "Interpolated setting: 16 measured basis-state probabilities"
        }
      },
      {
        "box": {
          "bgcolor": [
            0.08,
            0.09,
            0.12,
            1.0
          ],
          "id": "histogram",
          "maxclass": "multislider",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "parameter_enable": 0,
          "patching_rect": [
            625.0,
            318.0,
            755.0,
            140.0
          ],
          "setminmax": [
            0.0,
            1.0
          ],
          "setstyle": 1,
          "size": 16,
          "slidercolor": [
            0.12,
            0.82,
            0.92,
            1.0
          ]
        }
      },
      {
        "box": {
          "fontsize": 11.0,
          "id": "paulilabel",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            625.0,
            476.0,
            740.0,
            19.0
          ],
          "text": "THE 255 NON-IDENTITY PAULI COEFFICIENTS \u00b7 IIXY\u2026ZZZZ",
          "textcolor": [
            0.9,
            0.72,
            0.22,
            1.0
          ]
        }
      },
      {
        "box": {
          "bgcolor": [
            0.08,
            0.09,
            0.12,
            1.0
          ],
          "id": "paulis",
          "maxclass": "multislider",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "parameter_enable": 0,
          "patching_rect": [
            625.0,
            502.0,
            755.0,
            142.0
          ],
          "setstyle": 1,
          "size": 255,
          "slidercolor": [
            0.78,
            0.32,
            0.88,
            1.0
          ]
        }
      },
      {
        "box": {
          "fontsize": 11.0,
          "id": "shelllabel",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            625.0,
            662.0,
            680.0,
            19.0
          ],
          "text": "CORRELATION-WEIGHT SHELLS \u00b7 weights 0\u20134 contain 1, 12, 54, 108, 81 terms",
          "textcolor": [
            0.9,
            0.72,
            0.22,
            1.0
          ]
        }
      },
      {
        "box": {
          "bgcolor": [
            0.08,
            0.09,
            0.12,
            1.0
          ],
          "id": "shells",
          "maxclass": "multislider",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "parameter_enable": 0,
          "patching_rect": [
            625.0,
            688.0,
            500.0,
            96.0
          ],
          "setminmax": [
            0.0,
            1.0
          ],
          "setstyle": 1,
          "size": 5,
          "slidercolor": [
            0.96,
            0.56,
            0.18,
            1.0
          ]
        }
      },
      {
        "box": {
          "fontsize": 11.0,
          "id": "audiolabel",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            664.0,
            520.0,
            19.0
          ],
          "text": "SONIFY THE 2D SCORE \u00b7 81 settings become rows; data can drive Y continuously at signal rate",
          "textcolor": [
            0.9,
            0.72,
            0.22,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "buffer",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "float",
            "bang"
          ],
          "patching_rect": [
            30.0,
            694.0,
            290.0,
            24.0
          ],
          "text": "buffer~ qmw_full4q_local_2d @samps 20736"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "frequency",
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            30.0,
            768.0,
            76.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "phasor",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            122.0,
            768.0,
            72.0,
            24.0
          ],
          "text": "phasor~ 110."
        }
      },
      {
        "box": {
          "id": "wave",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            330.0,
            744.0,
            285.0,
            24.0
          ],
          "text": "2d.wave~ qmw_full4q_local_2d 0. 0. 1 81"
        }
      },
      {
        "box": {
          "id": "gain",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            1060.0,
            938.0,
            58.0,
            24.0
          ],
          "text": "*~ 0.12"
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0,
          "patching_rect": [
            1136.0,
            930.0,
            52.0,
            36.0
          ]
        }
      },
      {
        "box": {
          "fontsize": 11.0,
          "id": "warning",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            1000.0,
            600.0,
            22.0
          ],
          "text": "SOURCE MEMORY \u00b7 reload the latest saved datasets without rerunning either source."
        }
      },
      {
        "box": {
          "id": "replay_local",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            30.0,
            1028.0,
            118.0,
            24.0
          ],
          "text": "local"
        }
      },
      {
        "box": {
          "id": "replay_ibm",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            160.0,
            1028.0,
            118.0,
            24.0
          ],
          "text": "ibm"
        }
      },
      {
        "box": {
          "id": "opack_replay",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "FullPacket"
          ],
          "patching_rect": [
            290.0,
            1028.0,
            220.0,
            24.0
          ],
          "text": "o.pack /qmw/tomography/replay"
        }
      },
      {
        "box": {
          "fontsize": 11.0,
          "id": "replay_help",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            520.0,
            1028.0,
            390.0,
            24.0
          ],
          "text": "LOAD LAST LOCAL / LOAD LAST IBM"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "load_frequency",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            30.0,
            1066.0,
            86.0,
            24.0
          ],
          "text": "loadmess 110."
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "load_select",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            130.0,
            1066.0,
            78.0,
            24.0
          ],
          "text": "loadmess 0."
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "load_mix",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            220.0,
            1066.0,
            78.0,
            24.0
          ],
          "text": "loadmess 0."
        }
      },
      {
        "box": {
          "id": "receiver",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 6,
          "outlettype": [
            "",
            "",
            "",
            "",
            "",
            ""
          ],
          "patching_rect": [
            1160.0,
            688.0,
            214.0,
            24.0
          ],
          "saved_object_attributes": {
            "filename": "qmw_full4q_tomography_receiver_v1.js",
            "parameter_enable": 0
          },
          "text": "js qmw_full4q_tomography_receiver_v2.js"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "udpreceive",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            30.0,
            900.0,
            140.0,
            22.0
          ],
          "text": "udpreceive 7426"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "route",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 12,
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
            "",
            "",
            "FullPacket"
          ],
          "patching_rect": [
            184.0,
            900.0,
            1358.0,
            22.0
          ],
          "text": "o.route /qmw/tomography/begin /qmw/tomography/setting /qmw/tomography/pauli /qmw/tomography/shell /qmw/tomography/metrics /qmw/tomography/end /qmw/tomography/status /qmw/tomography/error /qmw/tomography/xfade /qmw/tomography/select /qmw/tomography/difference /qmw/zx/pauli/live"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "prepend_begin",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            184.0,
            938.0,
            100.0,
            22.0
          ],
          "text": "prepend begin"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "prepend_setting",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            294.0,
            938.0,
            100.0,
            22.0
          ],
          "text": "prepend setting"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "prepend_pauli",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            404.0,
            938.0,
            100.0,
            22.0
          ],
          "text": "prepend pauli"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "prepend_shell",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            514.0,
            938.0,
            100.0,
            22.0
          ],
          "text": "prepend shell"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "prepend_metrics",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            624.0,
            938.0,
            100.0,
            22.0
          ],
          "text": "prepend metrics"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "prepend_end",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            734.0,
            938.0,
            100.0,
            22.0
          ],
          "text": "prepend end"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "prepend_status",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            844.0,
            938.0,
            100.0,
            22.0
          ],
          "text": "prepend status"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "prepend_error",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            954.0,
            938.0,
            100.0,
            22.0
          ],
          "text": "prepend error"
        }
      },
      {
        "box": {
          "id": "buffer_ibm",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            724.0,
            290.0,
            24.0
          ],
          "text": "buffer~ qmw_full4q_ibm_2d @samps 20736"
        }
      },
      {
        "box": {
          "id": "wave_ibm",
          "maxclass": "newobj",
          "patching_rect": [
            330.0,
            794.0,
            285.0,
            24.0
          ],
          "text": "2d.wave~ qmw_full4q_ibm_2d 0. 0. 1 81"
        }
      },
      {
        "box": {
          "id": "ylabel",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            808.0,
            305.0,
            20.0
          ],
          "text": "Y row center = (setting position + 0.5) / 81",
          "fontsize": 10.0,
          "textcolor": [
            0.7,
            0.72,
            0.76,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "select_norm",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            834.0,
            154.0,
            24.0
          ],
          "text": "expr ($f1 + 0.5) / 81."
        }
      },
      {
        "box": {
          "id": "select_pack",
          "maxclass": "newobj",
          "patching_rect": [
            198.0,
            834.0,
            86.0,
            24.0
          ],
          "text": "pack 0. 80"
        }
      },
      {
        "box": {
          "id": "select_line",
          "maxclass": "newobj",
          "patching_rect": [
            298.0,
            834.0,
            48.0,
            24.0
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "mix_pack",
          "maxclass": "newobj",
          "patching_rect": [
            630.0,
            804.0,
            86.0,
            24.0
          ],
          "text": "pack 0. 80"
        }
      },
      {
        "box": {
          "id": "mix_line",
          "maxclass": "newobj",
          "patching_rect": [
            730.0,
            804.0,
            48.0,
            24.0
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "local_gain",
          "maxclass": "newobj",
          "patching_rect": [
            860.0,
            790.0,
            48.0,
            24.0
          ],
          "text": "cos~"
        }
      },
      {
        "box": {
          "id": "ibm_gain",
          "maxclass": "newobj",
          "patching_rect": [
            930.0,
            850.0,
            48.0,
            24.0
          ],
          "text": "cos~"
        }
      },
      {
        "box": {
          "id": "local_phase",
          "maxclass": "newobj",
          "patching_rect": [
            790.0,
            790.0,
            58.0,
            24.0
          ],
          "text": "*~ 0.25"
        }
      },
      {
        "box": {
          "id": "ibm_invert",
          "maxclass": "newobj",
          "patching_rect": [
            790.0,
            850.0,
            58.0,
            24.0
          ],
          "text": "!-~ 1."
        }
      },
      {
        "box": {
          "id": "ibm_phase",
          "maxclass": "newobj",
          "patching_rect": [
            860.0,
            850.0,
            58.0,
            24.0
          ],
          "text": "*~ 0.25"
        }
      },
      {
        "box": {
          "id": "local_mul",
          "maxclass": "newobj",
          "patching_rect": [
            920.0,
            790.0,
            46.0,
            24.0
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "ibm_mul",
          "maxclass": "newobj",
          "patching_rect": [
            990.0,
            850.0,
            46.0,
            24.0
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "audio_sum",
          "maxclass": "newobj",
          "patching_rect": [
            1046.0,
            826.0,
            46.0,
            24.0
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "source_audio_label",
          "maxclass": "comment",
          "patching_rect": [
            630.0,
            876.0,
            470.0,
            22.0
          ],
          "text": "Equal-power audio crossfade; LOCAL and IBM remain separate 2D surfaces",
          "fontsize": 10.0,
          "textcolor": [
            0.12,
            0.82,
            0.92,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "difference_mode",
          "maxclass": "toggle",
          "patching_rect": [
            630.0,
            908.0,
            24.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "difference_label",
          "maxclass": "comment",
          "patching_rect": [
            664.0,
            908.0,
            430.0,
            24.0
          ],
          "text": "DIFFERENCE ONLY \u00b7 IBM \u2212 LOCAL (identical wavetable data cancels to silence)",
          "fontsize": 11.0,
          "textcolor": [
            0.96,
            0.56,
            0.18,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "difference_sub",
          "maxclass": "newobj",
          "patching_rect": [
            1046.0,
            866.0,
            46.0,
            24.0
          ],
          "text": "-~"
        }
      },
      {
        "box": {
          "id": "mode_pack",
          "maxclass": "newobj",
          "patching_rect": [
            630.0,
            942.0,
            86.0,
            24.0
          ],
          "text": "pack 0. 60"
        }
      },
      {
        "box": {
          "id": "mode_line",
          "maxclass": "newobj",
          "patching_rect": [
            730.0,
            942.0,
            48.0,
            24.0
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "mode_invert",
          "maxclass": "newobj",
          "patching_rect": [
            790.0,
            922.0,
            58.0,
            24.0
          ],
          "text": "!-~ 1."
        }
      },
      {
        "box": {
          "id": "normal_mode_mul",
          "maxclass": "newobj",
          "patching_rect": [
            860.0,
            922.0,
            46.0,
            24.0
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "difference_mode_mul",
          "maxclass": "newobj",
          "patching_rect": [
            860.0,
            962.0,
            46.0,
            24.0
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "mode_sum",
          "maxclass": "newobj",
          "patching_rect": [
            926.0,
            942.0,
            46.0,
            24.0
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "load_difference",
          "maxclass": "newobj",
          "patching_rect": [
            310.0,
            1066.0,
            78.0,
            24.0
          ],
          "text": "loadmess 0"
        }
      },
      {
        "box": {
          "id": "pauli_select_label",
          "maxclass": "comment",
          "patching_rect": [
            1120.0,
            1000.0,
            270.0,
            20.0
          ],
          "text": "PAULI TERM 0\u2013254 \u2192 ZX gadget highlight",
          "fontsize": 10.0
        }
      },
      {
        "box": {
          "id": "pauli_select",
          "maxclass": "number",
          "patching_rect": [
            1120.0,
            1024.0,
            72.0,
            24.0
          ],
          "minimum": 0,
          "maximum": 254,
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
          "id": "pauli_select_command",
          "maxclass": "newobj",
          "patching_rect": [
            1205.0,
            1024.0,
            132.0,
            24.0
          ],
          "text": "prepend select_pauli"
        }
      },
      {
        "box": {
          "id": "pauli_selected_label",
          "maxclass": "message",
          "patching_rect": [
            1120.0,
            1056.0,
            108.0,
            24.0
          ],
          "text": "\u2014",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pauli_select_osc",
          "maxclass": "newobj",
          "patching_rect": [
            1240.0,
            1056.0,
            205.0,
            24.0
          ],
          "text": "prepend /qmw/zx/pauli/select"
        }
      },
      {
        "box": {
          "id": "pauli_select_udp",
          "maxclass": "newobj",
          "patching_rect": [
            1240.0,
            1088.0,
            195.0,
            24.0
          ],
          "text": "udpsend 127.0.0.1 7497"
        }
      },
      {
        "box": {
          "id": "pauli_live_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            1010.0,
            1088.0,
            120.0,
            24.0
          ],
          "text": "prepend live_pauli",
          "hidden": 1
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "destination": [
            "opack_run",
            0
          ],
          "source": [
            "bell",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "phasor",
            0
          ],
          "hidden": 1,
          "order": 0,
          "source": [
            "frequency",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "warning",
            0
          ],
          "hidden": 1,
          "order": 1,
          "source": [
            "frequency",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "opack_run",
            0
          ],
          "source": [
            "ghz",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "opack_run",
            0
          ],
          "source": [
            "ghzqft",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "frequency",
            0
          ],
          "hidden": 1,
          "source": [
            "load_frequency",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "mix",
            0
          ],
          "hidden": 1,
          "source": [
            "load_mix",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "select",
            0
          ],
          "hidden": 1,
          "source": [
            "load_select",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend_xfade",
            0
          ],
          "source": [
            "mix",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "udpsend",
            0
          ],
          "source": [
            "opack_ping",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "udpsend",
            0
          ],
          "hidden": 1,
          "source": [
            "opack_replay",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "udpsend",
            0
          ],
          "source": [
            "opack_run",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "opack_ping",
            0
          ],
          "source": [
            "pingbutton",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "receiver",
            0
          ],
          "hidden": 1,
          "source": [
            "prepend_begin",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "receiver",
            0
          ],
          "hidden": 1,
          "source": [
            "prepend_end",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "receiver",
            0
          ],
          "hidden": 1,
          "source": [
            "prepend_error",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "receiver",
            0
          ],
          "hidden": 1,
          "source": [
            "prepend_metrics",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "receiver",
            0
          ],
          "hidden": 1,
          "source": [
            "prepend_pauli",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "receiver",
            0
          ],
          "source": [
            "prepend_select",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "receiver",
            0
          ],
          "hidden": 1,
          "source": [
            "prepend_setting",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "receiver",
            0
          ],
          "hidden": 1,
          "source": [
            "prepend_shell",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "receiver",
            0
          ],
          "hidden": 1,
          "source": [
            "prepend_status",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "receiver",
            0
          ],
          "source": [
            "prepend_xfade",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "heatmap",
            0
          ],
          "source": [
            "receiver",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "histogram",
            0
          ],
          "source": [
            "receiver",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "paulis",
            0
          ],
          "source": [
            "receiver",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "shells",
            0
          ],
          "source": [
            "receiver",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "status",
            0
          ],
          "source": [
            "receiver",
            4
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "opack_replay",
            0
          ],
          "source": [
            "replay_ibm",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "opack_replay",
            0
          ],
          "source": [
            "replay_local",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "mix",
            0
          ],
          "hidden": 1,
          "source": [
            "route",
            8
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend_begin",
            0
          ],
          "hidden": 1,
          "source": [
            "route",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend_end",
            0
          ],
          "hidden": 1,
          "source": [
            "route",
            5
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend_error",
            0
          ],
          "hidden": 1,
          "source": [
            "route",
            7
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend_metrics",
            0
          ],
          "hidden": 1,
          "source": [
            "route",
            4
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend_pauli",
            0
          ],
          "hidden": 1,
          "source": [
            "route",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend_setting",
            0
          ],
          "hidden": 1,
          "source": [
            "route",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend_shell",
            0
          ],
          "hidden": 1,
          "source": [
            "route",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend_status",
            0
          ],
          "hidden": 1,
          "source": [
            "route",
            6
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "select",
            0
          ],
          "hidden": 1,
          "source": [
            "route",
            9
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend_select",
            0
          ],
          "source": [
            "select",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "route",
            0
          ],
          "hidden": 1,
          "source": [
            "udpreceive",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "opack_run",
            0
          ],
          "source": [
            "weave",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phasor",
            0
          ],
          "destination": [
            "wave",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phasor",
            0
          ],
          "destination": [
            "wave_ibm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "select",
            0
          ],
          "destination": [
            "select_norm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "select_norm",
            0
          ],
          "destination": [
            "select_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "select_pack",
            0
          ],
          "destination": [
            "select_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "select_line",
            0
          ],
          "destination": [
            "wave",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "select_line",
            0
          ],
          "destination": [
            "wave_ibm",
            1
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
            "mix_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mix_pack",
            0
          ],
          "destination": [
            "mix_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mix_line",
            0
          ],
          "destination": [
            "local_phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "local_phase",
            0
          ],
          "destination": [
            "local_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mix_line",
            0
          ],
          "destination": [
            "ibm_invert",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ibm_invert",
            0
          ],
          "destination": [
            "ibm_phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ibm_phase",
            0
          ],
          "destination": [
            "ibm_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wave",
            0
          ],
          "destination": [
            "local_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "local_gain",
            0
          ],
          "destination": [
            "local_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wave_ibm",
            0
          ],
          "destination": [
            "ibm_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ibm_gain",
            0
          ],
          "destination": [
            "ibm_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "local_mul",
            0
          ],
          "destination": [
            "audio_sum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ibm_mul",
            0
          ],
          "destination": [
            "audio_sum",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wave_ibm",
            0
          ],
          "destination": [
            "difference_sub",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wave",
            0
          ],
          "destination": [
            "difference_sub",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "difference_mode",
            0
          ],
          "destination": [
            "mode_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mode_pack",
            0
          ],
          "destination": [
            "mode_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mode_line",
            0
          ],
          "destination": [
            "mode_invert",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "audio_sum",
            0
          ],
          "destination": [
            "normal_mode_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mode_invert",
            0
          ],
          "destination": [
            "normal_mode_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "difference_sub",
            0
          ],
          "destination": [
            "difference_mode_mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mode_line",
            0
          ],
          "destination": [
            "difference_mode_mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "normal_mode_mul",
            0
          ],
          "destination": [
            "mode_sum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "difference_mode_mul",
            0
          ],
          "destination": [
            "mode_sum",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mode_sum",
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
            "load_difference",
            0
          ],
          "destination": [
            "difference_mode",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            10
          ],
          "destination": [
            "difference_mode",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pauli_select",
            0
          ],
          "destination": [
            "pauli_select_command",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pauli_select_command",
            0
          ],
          "destination": [
            "receiver",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "receiver",
            5
          ],
          "destination": [
            "pauli_selected_label",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "receiver",
            5
          ],
          "destination": [
            "pauli_select_osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pauli_select_osc",
            0
          ],
          "destination": [
            "pauli_select_udp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            11
          ],
          "destination": [
            "pauli_live_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pauli_live_prepend",
            0
          ],
          "destination": [
            "receiver",
            0
          ]
        }
      }
    ],
    "originid": "pat-1009",
    "dependency_cache": [
      {
        "name": "o.pack.mxo",
        "type": "iLaX"
      },
      {
        "name": "o.route.mxo",
        "type": "iLaX"
      },
      {
        "name": "qmw_full4q_tomography_receiver_v2.js",
        "bootpath": "~/QuantumSonification/max",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      }
    ],
    "autosave": 0
  }
}
