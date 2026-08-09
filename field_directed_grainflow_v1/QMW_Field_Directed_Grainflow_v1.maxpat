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
      55.0,
      35.0,
      1180.0,
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
            16.0,
            850.0,
            28.0
          ],
          "text": "QMW FIELD-DIRECTED GRAINFLOW v1 \u2014 ZEEMAN ENERGY SHELL",
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            47.0,
            1110.0,
            38.0
          ],
          "text": "Zeeman line geometry selects six energy modes; quantum statistics assigns occupations; GrainFlow renders occupied modes as events."
        }
      },
      {
        "box": {
          "id": "source_title",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            96.0,
            420.0,
            22.0
          ],
          "text": "DOUBLE-BUFFERED QUANTUM WAVETABLE ATLAS",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "source",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            130.0,
            280.0,
            22.0
          ],
          "text": "buffer~ qmw_wavetable @samps 256 @channels 1",
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
          "id": "atlas_a",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            163.0,
            330.0,
            22.0
          ],
          "text": "buffer~ qmw_pauli_atlas_A @samps 98304 @channels 1",
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
          "id": "atlas_b",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            196.0,
            330.0,
            22.0
          ],
          "text": "buffer~ qmw_pauli_atlas_B @samps 98304 @channels 1",
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
          "id": "atlas_js",
          "maxclass": "newobj",
          "patching_rect": [
            385.0,
            130.0,
            245.0,
            22.0
          ],
          "text": "js qmw_field_directed_atlas_v1.js",
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
          "id": "capture",
          "maxclass": "message",
          "patching_rect": [
            385.0,
            165.0,
            88.0,
            22.0
          ],
          "text": "render",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "seed",
          "maxclass": "message",
          "patching_rect": [
            483.0,
            165.0,
            118.0,
            22.0
          ],
          "text": "seed, render",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "capture_note",
          "maxclass": "comment",
          "patching_rect": [
            620.0,
            163.0,
            515.0,
            34.0
          ],
          "text": "CAPTURE reads the shared qmw_wavetable. SEED+CAPTURE supplies a local test source. Atlas A/B never change while their Grainflow engine is foregrounded."
        }
      },
      {
        "box": {
          "id": "atlas_status",
          "maxclass": "message",
          "patching_rect": [
            385.0,
            202.0,
            750.0,
            22.0
          ],
          "text": "waiting for atlas commit...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "xfade_b_pack",
          "maxclass": "newobj",
          "patching_rect": [
            650.0,
            130.0,
            82.0,
            22.0
          ],
          "text": "pack f 120",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "xfade_b",
          "maxclass": "newobj",
          "patching_rect": [
            742.0,
            130.0,
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
          "id": "xfade_a_expr",
          "maxclass": "newobj",
          "patching_rect": [
            805.0,
            130.0,
            82.0,
            22.0
          ],
          "text": "expr 1.-$f1",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "xfade_a_pack",
          "maxclass": "newobj",
          "patching_rect": [
            897.0,
            130.0,
            82.0,
            22.0
          ],
          "text": "pack f 120",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "xfade_a",
          "maxclass": "newobj",
          "patching_rect": [
            989.0,
            130.0,
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
          "id": "stats_title",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            245.0,
            420.0,
            22.0
          ],
          "text": "CANONICAL OCCUPATION SCHEDULER",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "stats_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            280.0,
            92.0,
            20.0
          ],
          "text": "statistics"
        }
      },
      {
        "box": {
          "id": "stats",
          "maxclass": "umenu",
          "patching_rect": [
            115.0,
            277.0,
            130.0,
            22.0
          ],
          "items": [
            "fermion",
            ",",
            "boson",
            ",",
            "classical"
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
          "id": "stats_pre",
          "maxclass": "newobj",
          "patching_rect": [
            255.0,
            277.0,
            112.0,
            22.0
          ],
          "text": "prepend statistics",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "particles_label",
          "maxclass": "comment",
          "patching_rect": [
            390.0,
            280.0,
            80.0,
            20.0
          ],
          "text": "particles N"
        }
      },
      {
        "box": {
          "id": "particles",
          "maxclass": "number",
          "patching_rect": [
            475.0,
            277.0,
            65.0,
            22.0
          ],
          "minimum": 0,
          "maximum": 12,
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
          "id": "particles_pre",
          "maxclass": "newobj",
          "patching_rect": [
            550.0,
            277.0,
            108.0,
            22.0
          ],
          "text": "prepend particles",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "run",
          "maxclass": "toggle",
          "patching_rect": [
            680.0,
            276.0,
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
          "id": "run_label",
          "maxclass": "comment",
          "patching_rect": [
            710.0,
            280.0,
            108.0,
            20.0
          ],
          "text": "sample ensemble"
        }
      },
      {
        "box": {
          "id": "metro",
          "maxclass": "newobj",
          "patching_rect": [
            825.0,
            277.0,
            72.0,
            22.0
          ],
          "text": "metro 400",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "scheduler",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            320.0,
            270.0,
            22.0
          ],
          "text": "js qmw_field_directed_scheduler_v1.js",
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
          "id": "occupancy",
          "maxclass": "multislider",
          "patching_rect": [
            315.0,
            315.0,
            335.0,
            42.0
          ],
          "size": 6,
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
          "id": "stat_status",
          "maxclass": "message",
          "patching_rect": [
            670.0,
            320.0,
            465.0,
            22.0
          ],
          "text": "initializing statistical shell...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "field_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            378.0,
            78.0,
            20.0
          ],
          "text": "field B"
        }
      },
      {
        "box": {
          "id": "field",
          "maxclass": "flonum",
          "patching_rect": [
            98.0,
            375.0,
            70.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 20.0,
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
          "id": "field_pre",
          "maxclass": "newobj",
          "patching_rect": [
            178.0,
            375.0,
            90.0,
            22.0
          ],
          "text": "prepend field",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "center_label",
          "maxclass": "comment",
          "patching_rect": [
            290.0,
            378.0,
            92.0,
            20.0
          ],
          "text": "shell center"
        }
      },
      {
        "box": {
          "id": "center",
          "maxclass": "flonum",
          "patching_rect": [
            382.0,
            375.0,
            70.0,
            22.0
          ],
          "minimum": -20.0,
          "maximum": 20.0,
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
          "id": "center_pre",
          "maxclass": "newobj",
          "patching_rect": [
            462.0,
            375.0,
            95.0,
            22.0
          ],
          "text": "prepend center",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "width_label",
          "maxclass": "comment",
          "patching_rect": [
            580.0,
            378.0,
            82.0,
            20.0
          ],
          "text": "shell width"
        }
      },
      {
        "box": {
          "id": "width",
          "maxclass": "flonum",
          "patching_rect": [
            665.0,
            375.0,
            70.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 40.0,
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
          "id": "width_pre",
          "maxclass": "newobj",
          "patching_rect": [
            745.0,
            375.0,
            92.0,
            22.0
          ],
          "text": "prepend width",
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
            855.0,
            378.0,
            82.0,
            20.0
          ],
          "text": "exploration"
        }
      },
      {
        "box": {
          "id": "entropy",
          "maxclass": "flonum",
          "patching_rect": [
            938.0,
            375.0,
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
          "id": "entropy_pre",
          "maxclass": "newobj",
          "patching_rect": [
            1018.0,
            375.0,
            98.0,
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
            25.0,
            418.0,
            82.0,
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
            98.0,
            415.0,
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
          "id": "coherence_pre",
          "maxclass": "newobj",
          "patching_rect": [
            178.0,
            415.0,
            108.0,
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
          "id": "density_label",
          "maxclass": "comment",
          "patching_rect": [
            310.0,
            418.0,
            76.0,
            20.0
          ],
          "text": "event density"
        }
      },
      {
        "box": {
          "id": "density",
          "maxclass": "flonum",
          "patching_rect": [
            392.0,
            415.0,
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
          "id": "density_pre",
          "maxclass": "newobj",
          "patching_rect": [
            472.0,
            415.0,
            100.0,
            22.0
          ],
          "text": "prepend density",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "deviation_label",
          "maxclass": "comment",
          "patching_rect": [
            595.0,
            418.0,
            108.0,
            20.0
          ],
          "text": "energy deviation"
        }
      },
      {
        "box": {
          "id": "deviation",
          "maxclass": "flonum",
          "patching_rect": [
            705.0,
            415.0,
            70.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 24.0,
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
          "id": "deviation_pre",
          "maxclass": "newobj",
          "patching_rect": [
            785.0,
            415.0,
            110.0,
            22.0
          ],
          "text": "prepend deviation",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "grain_title",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            465.0,
            500.0,
            22.0
          ],
          "text": "GRAINFLOW MULTICHANNEL RENDERER \u2014 6 streams x 4 grains",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "clock_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            500.0,
            90.0,
            20.0
          ],
          "text": "grain clock Hz"
        }
      },
      {
        "box": {
          "id": "clock",
          "maxclass": "flonum",
          "patching_rect": [
            120.0,
            497.0,
            72.0,
            22.0
          ],
          "minimum": 0.05,
          "maximum": 200.0,
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
          "id": "clock_mc",
          "maxclass": "newobj",
          "patching_rect": [
            205.0,
            497.0,
            168.0,
            22.0
          ],
          "text": "mc.phasor~ 10. @chans 6",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "trav_label",
          "maxclass": "comment",
          "patching_rect": [
            395.0,
            500.0,
            100.0,
            20.0
          ],
          "text": "atlas scan Hz"
        }
      },
      {
        "box": {
          "id": "trav",
          "maxclass": "flonum",
          "patching_rect": [
            495.0,
            497.0,
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
          "id": "trav_mc",
          "maxclass": "newobj",
          "patching_rect": [
            580.0,
            497.0,
            170.0,
            22.0
          ],
          "text": "mc.phasor~ 0.18 @chans 6",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "fm_index_label",
          "maxclass": "comment",
          "patching_rect": [
            770.0,
            480.0,
            70.0,
            20.0
          ],
          "text": "FM index"
        }
      },
      {
        "box": {
          "id": "fm_index",
          "maxclass": "flonum",
          "patching_rect": [
            840.0,
            497.0,
            70.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 2.0,
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
          "id": "fm_index_pack",
          "maxclass": "newobj",
          "patching_rect": [
            920.0,
            497.0,
            78.0,
            22.0
          ],
          "text": "pack f 30",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "fm_index_line",
          "maxclass": "newobj",
          "patching_rect": [
            1008.0,
            497.0,
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
          "id": "fm_cycle",
          "maxclass": "newobj",
          "patching_rect": [
            770.0,
            535.0,
            285.0,
            22.0
          ],
          "text": "mc.cycle~ @chans 6 @values 0.19 0.23 0.29 0.31 0.37 0.43",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "fm_mult",
          "maxclass": "newobj",
          "patching_rect": [
            1065.0,
            535.0,
            58.0,
            22.0
          ],
          "text": "mc.*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "am_mc",
          "maxclass": "newobj",
          "patching_rect": [
            1010.0,
            565.0,
            128.0,
            22.0
          ],
          "text": "mc.sig~ 1. @chans 6",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "env_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            598.0,
            75.0,
            20.0
          ],
          "text": "envelope"
        }
      },
      {
        "box": {
          "id": "env_menu",
          "maxclass": "umenu",
          "patching_rect": [
            105.0,
            595.0,
            185.0,
            22.0
          ],
          "items": [
            "qmw_env_hanning",
            ",",
            "qmw_env_blackman",
            ",",
            "qmw_env_pluck"
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
          "id": "env_pre",
          "maxclass": "newobj",
          "patching_rect": [
            300.0,
            595.0,
            88.0,
            22.0
          ],
          "text": "prepend env",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "env_hanning",
          "maxclass": "newobj",
          "patching_rect": [
            410.0,
            595.0,
            250.0,
            22.0
          ],
          "text": "buffer~ qmw_env_hanning grainflow.Hanning.aif",
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
          "id": "env_blackman",
          "maxclass": "newobj",
          "patching_rect": [
            675.0,
            595.0,
            255.0,
            22.0
          ],
          "text": "buffer~ qmw_env_blackman grainflow.Blackman.aif",
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
          "id": "env_pluck",
          "maxclass": "newobj",
          "patching_rect": [
            945.0,
            595.0,
            190.0,
            22.0
          ],
          "text": "buffer~ qmw_env_pluck grainflow.Pluck.aif",
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
          "id": "grain_a",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            635.0,
            320.0,
            22.0
          ],
          "text": "grainflow.streams~ 6 4 qmw_pauli_atlas_A",
          "numinlets": 4,
          "numoutlets": 2,
          "outlettype": [
            "multichannelsignal",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "grain_b",
          "maxclass": "newobj",
          "patching_rect": [
            365.0,
            635.0,
            320.0,
            22.0
          ],
          "text": "grainflow.streams~ 6 4 qmw_pauli_atlas_B",
          "numinlets": 4,
          "numoutlets": 2,
          "outlettype": [
            "multichannelsignal",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "gain_a",
          "maxclass": "newobj",
          "patching_rect": [
            125.0,
            675.0,
            58.0,
            22.0
          ],
          "text": "mc.*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "gain_b",
          "maxclass": "newobj",
          "patching_rect": [
            465.0,
            675.0,
            58.0,
            22.0
          ],
          "text": "mc.*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "mc_sum",
          "maxclass": "newobj",
          "patching_rect": [
            290.0,
            710.0,
            58.0,
            22.0
          ],
          "text": "mc.+~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "mixdown",
          "maxclass": "newobj",
          "patching_rect": [
            275.0,
            745.0,
            180.0,
            22.0
          ],
          "text": "mc.mixdown~ 2 @autogain 1",
          "numinlets": 1,
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
            305.0,
            780.0,
            90.0,
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
          "id": "master_label",
          "maxclass": "comment",
          "patching_rect": [
            485.0,
            750.0,
            70.0,
            20.0
          ],
          "text": "master"
        }
      },
      {
        "box": {
          "id": "master",
          "maxclass": "flonum",
          "patching_rect": [
            550.0,
            747.0,
            70.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 0.5,
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
          "id": "master_pack",
          "maxclass": "newobj",
          "patching_rect": [
            630.0,
            747.0,
            75.0,
            22.0
          ],
          "text": "pack f 30",
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
            715.0,
            747.0,
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
          "id": "master_l",
          "maxclass": "newobj",
          "patching_rect": [
            280.0,
            815.0,
            36.0,
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
          "id": "master_r",
          "maxclass": "newobj",
          "patching_rect": [
            380.0,
            815.0,
            36.0,
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
          "id": "clip_l",
          "maxclass": "newobj",
          "patching_rect": [
            280.0,
            850.0,
            82.0,
            22.0
          ],
          "text": "clip~ -0.95 0.95",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "clip_r",
          "maxclass": "newobj",
          "patching_rect": [
            380.0,
            850.0,
            82.0,
            22.0
          ],
          "text": "clip~ -0.95 0.95",
          "numinlets": 3,
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
            495.0,
            805.0,
            18.0,
            70.0
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
            525.0,
            805.0,
            18.0,
            70.0
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
            575.0,
            815.0,
            52.0,
            52.0
          ],
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "grain_info_a",
          "maxclass": "message",
          "patching_rect": [
            710.0,
            635.0,
            205.0,
            22.0
          ],
          "text": "A grain metadata",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "grain_info_b",
          "maxclass": "message",
          "patching_rect": [
            930.0,
            635.0,
            205.0,
            22.0
          ],
          "text": "B grain metadata",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            895.0,
            105.0,
            22.0
          ],
          "text": "loadmess initialize",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_render",
          "maxclass": "newobj",
          "patching_rect": [
            140.0,
            895.0,
            105.0,
            22.0
          ],
          "text": "loadmess bang",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_render_delay",
          "maxclass": "newobj",
          "patching_rect": [
            140.0,
            957.0,
            70.0,
            22.0
          ],
          "text": "delay 150",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "init_render_message",
          "maxclass": "message",
          "patching_rect": [
            220.0,
            957.0,
            82.0,
            22.0
          ],
          "text": "seed, render",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_stats",
          "maxclass": "newobj",
          "patching_rect": [
            255.0,
            895.0,
            120.0,
            22.0
          ],
          "text": "loadmess 0",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_particles",
          "maxclass": "newobj",
          "patching_rect": [
            385.0,
            895.0,
            88.0,
            22.0
          ],
          "text": "loadmess 2",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_field",
          "maxclass": "newobj",
          "patching_rect": [
            483.0,
            895.0,
            88.0,
            22.0
          ],
          "text": "loadmess 1.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_center",
          "maxclass": "newobj",
          "patching_rect": [
            581.0,
            895.0,
            88.0,
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
          "id": "init_width",
          "maxclass": "newobj",
          "patching_rect": [
            679.0,
            895.0,
            88.0,
            22.0
          ],
          "text": "loadmess 4.",
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
            777.0,
            895.0,
            96.0,
            22.0
          ],
          "text": "loadmess 0.35",
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
            883.0,
            895.0,
            96.0,
            22.0
          ],
          "text": "loadmess 0.75",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_density",
          "maxclass": "newobj",
          "patching_rect": [
            989.0,
            895.0,
            96.0,
            22.0
          ],
          "text": "loadmess 0.88",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_deviation",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            927.0,
            88.0,
            22.0
          ],
          "text": "loadmess 1.5",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_clock",
          "maxclass": "newobj",
          "patching_rect": [
            123.0,
            927.0,
            88.0,
            22.0
          ],
          "text": "loadmess 10.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_trav",
          "maxclass": "newobj",
          "patching_rect": [
            221.0,
            927.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0.18",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_env",
          "maxclass": "newobj",
          "patching_rect": [
            319.0,
            927.0,
            128.0,
            22.0
          ],
          "text": "loadmess 0",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_master",
          "maxclass": "newobj",
          "patching_rect": [
            457.0,
            927.0,
            96.0,
            22.0
          ],
          "text": "loadmess 0.16",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_run",
          "maxclass": "newobj",
          "patching_rect": [
            563.0,
            927.0,
            88.0,
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
          "id": "init_run_delay",
          "maxclass": "newobj",
          "patching_rect": [
            563.0,
            957.0,
            70.0,
            22.0
          ],
          "text": "delay 250",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "init_run_value",
          "maxclass": "message",
          "patching_rect": [
            643.0,
            957.0,
            32.0,
            22.0
          ],
          "text": "1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_fm_index",
          "maxclass": "newobj",
          "patching_rect": [
            661.0,
            927.0,
            96.0,
            22.0
          ],
          "text": "loadmess 0.08",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "fdg_normal",
          "maxclass": "message",
          "text": "preset normal",
          "patching_rect": [
            620.0,
            205.0,
            100.0,
            22.0
          ],
          "presentation": 1,
          "presentation_rect": [
            620.0,
            205.0,
            100.0,
            22.0
          ],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "fdg_d1",
          "maxclass": "message",
          "text": "preset sodium_d1",
          "patching_rect": [
            730.0,
            205.0,
            125.0,
            22.0
          ],
          "presentation": 1,
          "presentation_rect": [
            730.0,
            205.0,
            125.0,
            22.0
          ],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "fdg_d2",
          "maxclass": "message",
          "text": "preset sodium_d2",
          "patching_rect": [
            865.0,
            205.0,
            125.0,
            22.0
          ],
          "presentation": 1,
          "presentation_rect": [
            865.0,
            205.0,
            125.0,
            22.0
          ],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "fdg_label",
          "maxclass": "comment",
          "text": "ZEEMAN MODE GEOMETRY",
          "patching_rect": [
            620.0,
            180.0,
            370.0,
            20.0
          ],
          "presentation": 1,
          "presentation_rect": [
            620.0,
            180.0,
            370.0,
            20.0
          ]
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "capture",
            0
          ],
          "destination": [
            "atlas_js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "seed",
            0
          ],
          "destination": [
            "atlas_js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "atlas_js",
            0
          ],
          "destination": [
            "xfade_b_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "xfade_b_pack",
            0
          ],
          "destination": [
            "xfade_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "atlas_js",
            0
          ],
          "destination": [
            "xfade_a_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "xfade_a_expr",
            0
          ],
          "destination": [
            "xfade_a_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "xfade_a_pack",
            0
          ],
          "destination": [
            "xfade_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "atlas_js",
            1
          ],
          "destination": [
            "atlas_status",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "stats",
            1
          ],
          "destination": [
            "stats_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "stats_pre",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "particles",
            0
          ],
          "destination": [
            "particles_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "particles_pre",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "run",
            0
          ],
          "destination": [
            "metro",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "metro",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "scheduler",
            3
          ],
          "destination": [
            "metro",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "scheduler",
            0
          ],
          "destination": [
            "grain_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "scheduler",
            0
          ],
          "destination": [
            "grain_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "scheduler",
            1
          ],
          "destination": [
            "occupancy",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "scheduler",
            2
          ],
          "destination": [
            "stat_status",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field",
            0
          ],
          "destination": [
            "field_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_pre",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "center",
            0
          ],
          "destination": [
            "center_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "center_pre",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "width",
            0
          ],
          "destination": [
            "width_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "width_pre",
            0
          ],
          "destination": [
            "scheduler",
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
            "scheduler",
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
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "density",
            0
          ],
          "destination": [
            "density_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "density_pre",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "deviation",
            0
          ],
          "destination": [
            "deviation_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "deviation_pre",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clock",
            0
          ],
          "destination": [
            "clock_mc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "trav",
            0
          ],
          "destination": [
            "trav_mc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clock_mc",
            0
          ],
          "destination": [
            "grain_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clock_mc",
            0
          ],
          "destination": [
            "grain_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "trav_mc",
            0
          ],
          "destination": [
            "grain_a",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "trav_mc",
            0
          ],
          "destination": [
            "grain_b",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fm_index",
            0
          ],
          "destination": [
            "fm_index_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fm_index_pack",
            0
          ],
          "destination": [
            "fm_index_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fm_cycle",
            0
          ],
          "destination": [
            "fm_mult",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fm_index_line",
            0
          ],
          "destination": [
            "fm_mult",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fm_mult",
            0
          ],
          "destination": [
            "grain_a",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fm_mult",
            0
          ],
          "destination": [
            "grain_b",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "am_mc",
            0
          ],
          "destination": [
            "grain_a",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "am_mc",
            0
          ],
          "destination": [
            "grain_b",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env_menu",
            1
          ],
          "destination": [
            "env_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env_pre",
            0
          ],
          "destination": [
            "grain_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env_pre",
            0
          ],
          "destination": [
            "grain_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "grain_a",
            0
          ],
          "destination": [
            "gain_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "xfade_a",
            0
          ],
          "destination": [
            "gain_a",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "grain_b",
            0
          ],
          "destination": [
            "gain_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "xfade_b",
            0
          ],
          "destination": [
            "gain_b",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "grain_a",
            1
          ],
          "destination": [
            "grain_info_a",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "grain_b",
            1
          ],
          "destination": [
            "grain_info_b",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gain_a",
            0
          ],
          "destination": [
            "mc_sum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gain_b",
            0
          ],
          "destination": [
            "mc_sum",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mc_sum",
            0
          ],
          "destination": [
            "mixdown",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mixdown",
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
            "master",
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
            "unpack",
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
            "master_line",
            0
          ],
          "destination": [
            "master_l",
            1
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
            "master_r",
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
            "master_r",
            1
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
            "clip_l",
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
            "init",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_render",
            0
          ],
          "destination": [
            "init_render_delay",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_render_delay",
            0
          ],
          "destination": [
            "init_render_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_render_message",
            0
          ],
          "destination": [
            "atlas_js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_stats",
            0
          ],
          "destination": [
            "stats",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_particles",
            0
          ],
          "destination": [
            "particles",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_field",
            0
          ],
          "destination": [
            "field",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_center",
            0
          ],
          "destination": [
            "center",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_width",
            0
          ],
          "destination": [
            "width",
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
            "init_density",
            0
          ],
          "destination": [
            "density",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_deviation",
            0
          ],
          "destination": [
            "deviation",
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
            "init_trav",
            0
          ],
          "destination": [
            "trav",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_env",
            0
          ],
          "destination": [
            "env_menu",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_master",
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
            "init_run",
            0
          ],
          "destination": [
            "init_run_delay",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_run_delay",
            0
          ],
          "destination": [
            "init_run_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_run_value",
            0
          ],
          "destination": [
            "run",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_fm_index",
            0
          ],
          "destination": [
            "fm_index",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fdg_normal",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fdg_d1",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fdg_d2",
            0
          ],
          "destination": [
            "scheduler",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "qmw_field_directed_atlas_v1.js",
        "type": "TEXT",
        "bootpath": "~/QuantumSonification/field_directed_grainflow_v1"
      },
      {
        "name": "qmw_field_directed_scheduler_v1.js",
        "type": "TEXT",
        "bootpath": "~/QuantumSonification/field_directed_grainflow_v1"
      },
      {
        "name": "grainflow.streams~.maxpat",
        "type": "JSON"
      },
      {
        "name": "grainflow~.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
