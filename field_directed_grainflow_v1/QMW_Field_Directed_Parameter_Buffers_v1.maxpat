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
      65.0,
      35.0,
      1100.0,
      930.0
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
            20.0,
            14.0,
            1100.0,
            28.0
          ],
          "text": "QMW FIELD-DIRECTED GRAINFLOW \u2014 8-VOICE PARAMETER FIELDS v1",
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            20.0,
            45.0,
            1100.0,
            38.0
          ],
          "text": "Each grain voice reads a stable slot from named rate, traversal-delay, and window-offset buffers. Amplitude is an eight-channel signal field. Mode 1 preserves assignments; mode 2 samples the same fields statistically."
        }
      },
      {
        "box": {
          "id": "source",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            95.0,
            390.0,
            22.0
          ],
          "text": "buffer~ qmw_fdg_source CP_Bubbling_Pasta_Sauce.wav",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "float",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "rates_buf",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            128.0,
            285.0,
            22.0
          ],
          "text": "buffer~ qmw_fdg_rates @samps 9",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "float",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "delays_buf",
          "maxclass": "newobj",
          "patching_rect": [
            320.0,
            128.0,
            285.0,
            22.0
          ],
          "text": "buffer~ qmw_fdg_delays @samps 9",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "float",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "windows_buf",
          "maxclass": "newobj",
          "patching_rect": [
            620.0,
            128.0,
            295.0,
            22.0
          ],
          "text": "buffer~ qmw_fdg_windows @samps 9",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "float",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "clock_label",
          "maxclass": "comment",
          "patching_rect": [
            20.0,
            178.0,
            85.0,
            20.0
          ],
          "text": "grain clock"
        }
      },
      {
        "box": {
          "id": "clock",
          "maxclass": "flonum",
          "patching_rect": [
            108.0,
            175.0,
            72.0,
            22.0
          ],
          "minimum": 0.1,
          "maximum": 100.0,
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
          "id": "clock_sig",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            175.0,
            82.0,
            22.0
          ],
          "text": "phasor~ 8.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "scan_label",
          "maxclass": "comment",
          "patching_rect": [
            300.0,
            178.0,
            78.0,
            20.0
          ],
          "text": "source scan"
        }
      },
      {
        "box": {
          "id": "scan",
          "maxclass": "flonum",
          "patching_rect": [
            380.0,
            175.0,
            72.0,
            22.0
          ],
          "minimum": -4.0,
          "maximum": 4.0,
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
          "id": "scan_sig",
          "maxclass": "newobj",
          "patching_rect": [
            462.0,
            175.0,
            82.0,
            22.0
          ],
          "text": "phasor~ 0.12",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "enable",
          "maxclass": "toggle",
          "patching_rect": [
            570.0,
            174.0,
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
          "id": "enable_label",
          "maxclass": "comment",
          "patching_rect": [
            602.0,
            178.0,
            72.0,
            20.0
          ],
          "text": "granulator"
        }
      },
      {
        "box": {
          "id": "mode_label",
          "maxclass": "comment",
          "patching_rect": [
            700.0,
            178.0,
            45.0,
            20.0
          ],
          "text": "mode"
        }
      },
      {
        "box": {
          "id": "mode",
          "maxclass": "umenu",
          "patching_rect": [
            748.0,
            175.0,
            215.0,
            22.0
          ],
          "items": [
            "0 scalar",
            ",",
            "1 deterministic field",
            ",",
            "2 random field lookup"
          ],
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "int",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "mode_pre",
          "maxclass": "newobj",
          "patching_rect": [
            975.0,
            175.0,
            92.0,
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
          "id": "grain",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            225.0,
            320.0,
            22.0
          ],
          "text": "grainflow~ qmw_fdg_source 8 grainflow.Hanning.aif",
          "numinlets": 4,
          "numoutlets": 9,
          "outlettype": [
            "multichannelsignal",
            "list",
            "multichannelsignal",
            "multichannelsignal",
            "multichannelsignal",
            "multichannelsignal",
            "multichannelsignal",
            "multichannelsignal",
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "scalar_rate",
          "maxclass": "newobj",
          "patching_rect": [
            635.0,
            225.0,
            62.0,
            22.0
          ],
          "text": "sig~ 1.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "amp_mc",
          "maxclass": "newobj",
          "patching_rect": [
            365.0,
            225.0,
            128.0,
            22.0
          ],
          "text": "mc.sig~ 0. @chans 8",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "amp_smooth",
          "maxclass": "newobj",
          "patching_rect": [
            505.0,
            225.0,
            115.0,
            22.0
          ],
          "text": "mc.slide~ 80 80",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "pan",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            265.0,
            190.0,
            22.0
          ],
          "text": "grainflow.util.stereoPan~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "unpack",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            305.0,
            92.0,
            22.0
          ],
          "text": "mc.unpack~ 2",
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
          "id": "gain_l",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            345.0,
            55.0,
            22.0
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
          "id": "gain_r",
          "maxclass": "newobj",
          "patching_rect": [
            125.0,
            345.0,
            55.0,
            22.0
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
          "id": "meter_l",
          "maxclass": "meter~",
          "patching_rect": [
            205.0,
            325.0,
            18.0,
            55.0
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
            232.0,
            325.0,
            18.0,
            55.0
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
            275.0,
            325.0,
            52.0,
            52.0
          ],
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "metadata",
          "maxclass": "message",
          "patching_rect": [
            365.0,
            265.0,
            610.0,
            22.0
          ],
          "text": "grain metadata",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "field_title",
          "maxclass": "comment",
          "patching_rect": [
            20.0,
            410.0,
            920.0,
            22.0
          ],
          "text": "QUANTUM FIELD INPUT \u2014 local controls and /qmw/density_field OSC drive the same writer",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "mag_label",
          "maxclass": "comment",
          "patching_rect": [
            20.0,
            447.0,
            72.0,
            20.0
          ],
          "text": "magnitude"
        }
      },
      {
        "box": {
          "id": "mag",
          "maxclass": "flonum",
          "patching_rect": [
            95.0,
            444.0,
            72.0,
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
          "id": "mag_pre",
          "maxclass": "newobj",
          "patching_rect": [
            175.0,
            444.0,
            112.0,
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
          "id": "phase_label",
          "maxclass": "comment",
          "patching_rect": [
            310.0,
            447.0,
            48.0,
            20.0
          ],
          "text": "phase"
        }
      },
      {
        "box": {
          "id": "phase",
          "maxclass": "flonum",
          "patching_rect": [
            360.0,
            444.0,
            72.0,
            22.0
          ],
          "minimum": -6.2832,
          "maximum": 6.2832,
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
          "id": "phase_pre",
          "maxclass": "newobj",
          "patching_rect": [
            440.0,
            444.0,
            92.0,
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
          "id": "purity_label",
          "maxclass": "comment",
          "patching_rect": [
            555.0,
            447.0,
            48.0,
            20.0
          ],
          "text": "purity"
        }
      },
      {
        "box": {
          "id": "purity",
          "maxclass": "flonum",
          "patching_rect": [
            605.0,
            444.0,
            72.0,
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
          "id": "purity_pre",
          "maxclass": "newobj",
          "patching_rect": [
            685.0,
            444.0,
            92.0,
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
          "id": "entropy_label",
          "maxclass": "comment",
          "patching_rect": [
            800.0,
            447.0,
            55.0,
            20.0
          ],
          "text": "entropy"
        }
      },
      {
        "box": {
          "id": "entropy",
          "maxclass": "flonum",
          "patching_rect": [
            858.0,
            444.0,
            72.0,
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
          "id": "entropy_pre",
          "maxclass": "newobj",
          "patching_rect": [
            938.0,
            444.0,
            102.0,
            22.0
          ],
          "text": "prepend entropy",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "coherence_label",
          "maxclass": "comment",
          "patching_rect": [
            20.0,
            482.0,
            72.0,
            20.0
          ],
          "text": "coherence"
        }
      },
      {
        "box": {
          "id": "coherence",
          "maxclass": "flonum",
          "patching_rect": [
            95.0,
            479.0,
            72.0,
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
          "id": "coherence_pre",
          "maxclass": "newobj",
          "patching_rect": [
            175.0,
            479.0,
            112.0,
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
          "id": "duration_label",
          "maxclass": "comment",
          "patching_rect": [
            310.0,
            482.0,
            120.0,
            20.0
          ],
          "text": "source duration ms"
        }
      },
      {
        "box": {
          "id": "duration",
          "maxclass": "flonum",
          "patching_rect": [
            430.0,
            479.0,
            90.0,
            22.0
          ],
          "minimum": 10.0,
          "maximum": 600000.0,
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
          "id": "duration_pre",
          "maxclass": "newobj",
          "patching_rect": [
            530.0,
            479.0,
            110.0,
            22.0
          ],
          "text": "prepend duration",
          "numinlets": 1,
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
            665.0,
            479.0,
            42.0,
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
          "id": "writer",
          "maxclass": "newobj",
          "patching_rect": [
            730.0,
            479.0,
            270.0,
            22.0
          ],
          "text": "js qmw_fdg_parameter_field_v1.js",
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
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            20.0,
            520.0,
            1020.0,
            42.0
          ],
          "text": "waiting for parameter field...",
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
            20.0,
            580.0,
            250.0,
            20.0
          ],
          "text": "RATE FIELD \u2014 signed gap \u2192 playback ratio"
        }
      },
      {
        "box": {
          "id": "rate_view",
          "maxclass": "multislider",
          "patching_rect": [
            20.0,
            603.0,
            500.0,
            48.0
          ],
          "size": 8,
          "setminmax": [
            -4.0,
            4.0
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
          "id": "delay_label",
          "maxclass": "comment",
          "patching_rect": [
            550.0,
            580.0,
            350.0,
            20.0
          ],
          "text": "DELAY FIELD \u2014 phase \u2192 temporal offset (ms)"
        }
      },
      {
        "box": {
          "id": "delay_view",
          "maxclass": "multislider",
          "patching_rect": [
            550.0,
            603.0,
            500.0,
            48.0
          ],
          "size": 8,
          "setminmax": [
            -60000.0,
            0.0
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
          "id": "window_label",
          "maxclass": "comment",
          "patching_rect": [
            20.0,
            670.0,
            360.0,
            20.0
          ],
          "text": "WINDOW-OFFSET FIELD \u2014 relational voice position"
        }
      },
      {
        "box": {
          "id": "window_view",
          "maxclass": "multislider",
          "patching_rect": [
            20.0,
            693.0,
            500.0,
            48.0
          ],
          "size": 8,
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
          "id": "amp_label",
          "maxclass": "comment",
          "patching_rect": [
            550.0,
            670.0,
            300.0,
            20.0
          ],
          "text": "AMPLITUDE FIELD \u2014 normalized quantum weight"
        }
      },
      {
        "box": {
          "id": "amp_view",
          "maxclass": "multislider",
          "patching_rect": [
            550.0,
            693.0,
            500.0,
            48.0
          ],
          "size": 8,
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
          "id": "osc",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            775.0,
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
            160.0,
            775.0,
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
          "id": "route_density",
          "maxclass": "newobj",
          "patching_rect": [
            280.0,
            775.0,
            145.0,
            22.0
          ],
          "text": "OSC-route /density_field",
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
          "id": "route_fields",
          "maxclass": "newobj",
          "patching_rect": [
            440.0,
            775.0,
            510.0,
            22.0
          ],
          "text": "OSC-route /magnitude /phase /purity /entropy /coherence",
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
          "id": "osc_note",
          "maxclass": "comment",
          "patching_rect": [
            20.0,
            810.0,
            1030.0,
            36.0
          ],
          "text": "Mode 1 reads table slot i for grain voice i. Mode 2 randomly samples the table while entropy sets rate, delay, and offset random depth. Observable envelope families belong in a later env2D atlas; Grainflow's windowBuffer is specifically the window-offset table."
        }
      },
      {
        "box": {
          "id": "init_clock",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            865.0,
            85.0,
            22.0
          ],
          "text": "loadmess 8.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_scan",
          "maxclass": "newobj",
          "patching_rect": [
            115.0,
            865.0,
            95.0,
            22.0
          ],
          "text": "loadmess 0.12",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_enable",
          "maxclass": "newobj",
          "patching_rect": [
            220.0,
            865.0,
            85.0,
            22.0
          ],
          "text": "loadmess 1",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_mode",
          "maxclass": "newobj",
          "patching_rect": [
            315.0,
            865.0,
            85.0,
            22.0
          ],
          "text": "loadmess 1",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_mag",
          "maxclass": "newobj",
          "patching_rect": [
            410.0,
            865.0,
            95.0,
            22.0
          ],
          "text": "loadmess 0.55",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_phase",
          "maxclass": "newobj",
          "patching_rect": [
            515.0,
            865.0,
            85.0,
            22.0
          ],
          "text": "loadmess 0.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_purity",
          "maxclass": "newobj",
          "patching_rect": [
            610.0,
            865.0,
            95.0,
            22.0
          ],
          "text": "loadmess 0.8",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_entropy",
          "maxclass": "newobj",
          "patching_rect": [
            715.0,
            865.0,
            95.0,
            22.0
          ],
          "text": "loadmess 0.2",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_coherence",
          "maxclass": "newobj",
          "patching_rect": [
            820.0,
            865.0,
            95.0,
            22.0
          ],
          "text": "loadmess 0.8",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_duration",
          "maxclass": "newobj",
          "patching_rect": [
            925.0,
            865.0,
            115.0,
            22.0
          ],
          "text": "loadmess 5587.528",
          "numinlets": 1,
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
            "clock",
            0
          ],
          "destination": [
            "clock_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "scan",
            0
          ],
          "destination": [
            "scan_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clock_sig",
            0
          ],
          "destination": [
            "grain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "scan_sig",
            0
          ],
          "destination": [
            "grain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "scalar_rate",
            0
          ],
          "destination": [
            "grain",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp_mc",
            0
          ],
          "destination": [
            "amp_smooth",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp_smooth",
            0
          ],
          "destination": [
            "grain",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "enable",
            0
          ],
          "destination": [
            "grain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "grain",
            0
          ],
          "destination": [
            "pan",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "grain",
            2
          ],
          "destination": [
            "pan",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "grain",
            1
          ],
          "destination": [
            "metadata",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan",
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
            "gain_l",
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
            "mode",
            0
          ],
          "destination": [
            "mode_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mode_pre",
            0
          ],
          "destination": [
            "writer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mag",
            0
          ],
          "destination": [
            "mag_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mag_pre",
            0
          ],
          "destination": [
            "writer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase",
            0
          ],
          "destination": [
            "phase_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_pre",
            0
          ],
          "destination": [
            "writer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "purity",
            0
          ],
          "destination": [
            "purity_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "purity_pre",
            0
          ],
          "destination": [
            "writer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "entropy",
            0
          ],
          "destination": [
            "entropy_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "entropy_pre",
            0
          ],
          "destination": [
            "writer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "coherence",
            0
          ],
          "destination": [
            "coherence_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "coherence_pre",
            0
          ],
          "destination": [
            "writer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "duration",
            0
          ],
          "destination": [
            "duration_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "duration_pre",
            0
          ],
          "destination": [
            "writer",
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
            "writer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "writer",
            0
          ],
          "destination": [
            "rate_view",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "writer",
            1
          ],
          "destination": [
            "delay_view",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "writer",
            2
          ],
          "destination": [
            "window_view",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "writer",
            3
          ],
          "destination": [
            "amp_view",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "writer",
            4
          ],
          "destination": [
            "amp_mc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "writer",
            5
          ],
          "destination": [
            "grain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "writer",
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
            "osc",
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
            "route_density",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_density",
            0
          ],
          "destination": [
            "route_fields",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_fields",
            0
          ],
          "destination": [
            "mag_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_fields",
            1
          ],
          "destination": [
            "phase_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_fields",
            2
          ],
          "destination": [
            "purity_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_fields",
            3
          ],
          "destination": [
            "entropy_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_fields",
            4
          ],
          "destination": [
            "coherence_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_clock",
            0
          ],
          "destination": [
            "clock",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_scan",
            0
          ],
          "destination": [
            "scan",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_enable",
            0
          ],
          "destination": [
            "enable",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_mode",
            0
          ],
          "destination": [
            "mode",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_mag",
            0
          ],
          "destination": [
            "mag",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_phase",
            0
          ],
          "destination": [
            "phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_purity",
            0
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
            "init_entropy",
            0
          ],
          "destination": [
            "entropy",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_coherence",
            0
          ],
          "destination": [
            "coherence",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_duration",
            0
          ],
          "destination": [
            "duration",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "CP_Bubbling_Pasta_Sauce.wav",
        "type": "WAVE"
      },
      {
        "name": "grainflow~.mxo",
        "type": "iLaX"
      },
      {
        "name": "grainflow.util.stereoPan~.maxpat",
        "type": "JSON"
      },
      {
        "name": "grainflow.Hanning.aif",
        "type": "AIFF"
      },
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
      },
      {
        "name": "qmw_fdg_parameter_field_v1.js",
        "type": "TEXT"
      }
    ],
    "autosave": 0
  }
}
