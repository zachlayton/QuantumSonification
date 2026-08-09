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
      1280.0,
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
            25.0,
            15.0,
            1080.0,
            28.0
          ],
          "text": "QMW PAULI MuBu CORPUS INSTRUMENT v1 \u2014 THE ENERGY SHELL AS MEMORY",
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            45.0,
            1180.0,
            35.0
          ],
          "text": "Quantum wavetable atlas + exact Pauli occupations + per-event MuBu grains + persistent mode/state/grain tracks. MuBu 1.10.7; six MC mode outputs."
        }
      },
      {
        "box": {
          "id": "source_title",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            90.0,
            450.0,
            22.0
          ],
          "text": "DOUBLE-BUFFERED QUANTUM SOURCE",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "source",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            120.0,
            285.0,
            22.0
          ],
          "text": "buffer~ qmw_wavetable @samps 256",
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
            150.0,
            345.0,
            22.0
          ],
          "text": "buffer~ qmw_pauli_mubu_atlas_A @samps 98304",
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
            180.0,
            345.0,
            22.0
          ],
          "text": "buffer~ qmw_pauli_mubu_atlas_B @samps 98304",
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
          "id": "atlas_mubu_a",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            210.0,
            235.0,
            22.0
          ],
          "text": "mubu qmw_pauli_mubu_atlas_A",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "atlas_mubu_b",
          "maxclass": "newobj",
          "patching_rect": [
            270.0,
            210.0,
            235.0,
            22.0
          ],
          "text": "mubu qmw_pauli_mubu_atlas_B",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "atlas_js",
          "maxclass": "newobj",
          "patching_rect": [
            395.0,
            120.0,
            238.0,
            22.0
          ],
          "text": "js qmw_mubu_wavetable_atlas_v1.js",
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
            395.0,
            152.0,
            65.0,
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
            470.0,
            152.0,
            112.0,
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
          "id": "atlas_status",
          "maxclass": "message",
          "patching_rect": [
            395.0,
            184.0,
            335.0,
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
            395.0,
            216.0,
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
            487.0,
            216.0,
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
            545.0,
            216.0,
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
            637.0,
            216.0,
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
            729.0,
            216.0,
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
          "id": "corpus_title",
          "maxclass": "comment",
          "patching_rect": [
            790.0,
            90.0,
            410.0,
            22.0
          ],
          "text": "MuBu CORPUS: MODES / STATES / GRAINS",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "mode_track",
          "maxclass": "newobj",
          "patching_rect": [
            790.0,
            305.0,
            420.0,
            22.0
          ],
          "text": "mubu.track qmw_pauli_mubu_corpus 1 modes @matrixcols 5 @matrixcolnames ml two_ms g position mode @extradata label @info gui \"interface multiwave, bounds -2 6, autobounds 0\" @predef yes",
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
          "id": "state_track",
          "maxclass": "newobj",
          "patching_rect": [
            790.0,
            335.0,
            420.0,
            22.0
          ],
          "text": "mubu.track qmw_pauli_mubu_corpus 2 states @matrixcols 11 @matrixcolnames N M Omega entropy B occ1 occ2 occ3 occ4 occ5 occ6 @timetagged yes @extradata label @maxsize 4096 @ring 1 @info gui \"interface multibpf, bounds 0 12, autobounds 0, paramcols occ1 occ2 occ3 occ4 occ5 occ6\" @predef yes",
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
          "id": "grain_track",
          "maxclass": "newobj",
          "patching_rect": [
            790.0,
            365.0,
            420.0,
            22.0
          ],
          "text": "mubu.track qmw_pauli_mubu_corpus 3 grains @matrixcols 5 @matrixcolnames mode position_ms resampling_cents duration_ms level_db @timetagged yes @extradata label @maxsize 16384 @ring 1 @info gui \"interface bpf, bounds 0 6, autobounds 0, paramcols mode\" @predef yes",
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
          "id": "corpus",
          "maxclass": "imubu",
          "patching_rect": [
            790.0,
            120.0,
            420.0,
            175.0
          ],
          "name": "qmw_pauli_mubu_corpus",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "embed": 0,
          "autobounds": 0,
          "autoupdate": 500.0,
          "autorefreshrate": 1,
          "maintrack": 2,
          "tabs_visible": 1,
          "toolbar_visible": 2,
          "bufferchooser_visible": 0,
          "domain_bounds": [
            0.0,
            30000.0
          ],
          "domainruler_visible": 1,
          "domainscrollbar_visible": 1,
          "tool": "cursor"
        }
      },
      {
        "box": {
          "id": "mode_seed",
          "maxclass": "message",
          "patching_rect": [
            790.0,
            395.0,
            420.0,
            22.0
          ],
          "text": "clear, append -1 -1 -2 0.083333 1 mode_1, append -1 1 0 0.25 2 mode_2, append 0 -1 -1 0.416667 3 mode_3, append 0 1 1 0.583333 4 mode_4, append 1 -1 0 0.75 5 mode_5, append 1 1 2 0.916667 6 mode_6",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "corpus_note",
          "maxclass": "comment",
          "patching_rect": [
            790.0,
            423.0,
            420.0,
            32.0
          ],
          "text": "The state and grain tracks are bounded ring memories. Double-click a mubu.track or use imubu tabs to inspect the corpus while playing."
        }
      },
      {
        "box": {
          "id": "state_append_route",
          "maxclass": "newobj",
          "patching_rect": [
            790.0,
            460.0,
            88.0,
            22.0
          ],
          "text": "route append",
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
          "id": "state_time",
          "maxclass": "newobj",
          "patching_rect": [
            888.0,
            460.0,
            65.0,
            22.0
          ],
          "text": "unpack f",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "view_speedlim",
          "maxclass": "newobj",
          "patching_rect": [
            963.0,
            460.0,
            100.0,
            22.0
          ],
          "text": "speedlim 1000",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "view_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            1073.0,
            460.0,
            50.0,
            22.0
          ],
          "text": "t f f",
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
          "id": "view_start",
          "maxclass": "newobj",
          "patching_rect": [
            790.0,
            495.0,
            165.0,
            22.0
          ],
          "text": "expr max(0.,$f1-30000.)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "view_end",
          "maxclass": "newobj",
          "patching_rect": [
            965.0,
            495.0,
            165.0,
            22.0
          ],
          "text": "expr max(30000.,$f1)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "view_pack",
          "maxclass": "newobj",
          "patching_rect": [
            1140.0,
            495.0,
            80.0,
            22.0
          ],
          "text": "pack f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "view_freeze_label",
          "maxclass": "comment",
          "patching_rect": [
            790.0,
            533.0,
            82.0,
            20.0
          ],
          "text": "freeze view"
        }
      },
      {
        "box": {
          "id": "view_freeze",
          "maxclass": "toggle",
          "patching_rect": [
            875.0,
            530.0,
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
          "id": "view_freeze_pre",
          "maxclass": "newobj",
          "patching_rect": [
            910.0,
            530.0,
            105.0,
            22.0
          ],
          "text": "prepend freeze",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "view_domain",
          "maxclass": "newobj",
          "patching_rect": [
            1035.0,
            530.0,
            185.0,
            22.0
          ],
          "text": "prepend domain bounds",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "stats_title",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            270.0,
            500.0,
            22.0
          ],
          "text": "EXACT OCCUPATION \u2192 ASYNCHRONOUS GRAIN EVENTS",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "stats_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            304.0,
            82.0,
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
            110.0,
            301.0,
            120.0,
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
            240.0,
            301.0,
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
            370.0,
            304.0,
            76.0,
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
            450.0,
            301.0,
            60.0,
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
            520.0,
            301.0,
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
            650.0,
            300.0,
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
            680.0,
            304.0,
            90.0,
            20.0
          ],
          "text": "emit grains"
        }
      },
      {
        "box": {
          "id": "metro",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            335.0,
            72.0,
            22.0
          ],
          "text": "metro 55",
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
            110.0,
            335.0,
            245.0,
            22.0
          ],
          "text": "js qmw_pauli_mubu_scheduler_v1.js",
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
          "id": "occupancy",
          "maxclass": "multislider",
          "patching_rect": [
            370.0,
            332.0,
            250.0,
            38.0
          ],
          "size": 6,
          "setminmax": [
            0.0,
            12.0
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
            25.0,
            375.0,
            730.0,
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
            414.0,
            56.0,
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
            82.0,
            411.0,
            62.0,
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
            150.0,
            411.0,
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
            250.0,
            414.0,
            80.0,
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
            330.0,
            411.0,
            62.0,
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
            400.0,
            411.0,
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
            505.0,
            414.0,
            72.0,
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
            580.0,
            411.0,
            62.0,
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
            650.0,
            411.0,
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
          "id": "explore_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            450.0,
            76.0,
            20.0
          ],
          "text": "exploration"
        }
      },
      {
        "box": {
          "id": "explore",
          "maxclass": "flonum",
          "patching_rect": [
            102.0,
            447.0,
            62.0,
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
          "id": "explore_pre",
          "maxclass": "newobj",
          "patching_rect": [
            170.0,
            447.0,
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
            278.0,
            450.0,
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
            350.0,
            447.0,
            62.0,
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
            420.0,
            447.0,
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
            538.0,
            450.0,
            54.0,
            20.0
          ],
          "text": "density"
        }
      },
      {
        "box": {
          "id": "density",
          "maxclass": "flonum",
          "patching_rect": [
            595.0,
            447.0,
            62.0,
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
            665.0,
            447.0,
            95.0,
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
          "id": "period_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            486.0,
            78.0,
            20.0
          ],
          "text": "event ms"
        }
      },
      {
        "box": {
          "id": "period",
          "maxclass": "flonum",
          "patching_rect": [
            102.0,
            483.0,
            62.0,
            22.0
          ],
          "minimum": 5.0,
          "maximum": 2000.0,
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
          "id": "period_pre",
          "maxclass": "newobj",
          "patching_rect": [
            170.0,
            483.0,
            115.0,
            22.0
          ],
          "text": "prepend grainperiod",
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
            295.0,
            486.0,
            74.0,
            20.0
          ],
          "text": "duration ms"
        }
      },
      {
        "box": {
          "id": "duration",
          "maxclass": "flonum",
          "patching_rect": [
            370.0,
            483.0,
            62.0,
            22.0
          ],
          "minimum": 2.0,
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
          "id": "duration_pre",
          "maxclass": "newobj",
          "patching_rect": [
            440.0,
            483.0,
            102.0,
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
          "id": "positionvar_label",
          "maxclass": "comment",
          "patching_rect": [
            552.0,
            486.0,
            82.0,
            20.0
          ],
          "text": "position var"
        }
      },
      {
        "box": {
          "id": "positionvar",
          "maxclass": "flonum",
          "patching_rect": [
            635.0,
            483.0,
            62.0,
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
          "id": "positionvar_pre",
          "maxclass": "newobj",
          "patching_rect": [
            705.0,
            483.0,
            118.0,
            22.0
          ],
          "text": "prepend positionvar",
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
            25.0,
            522.0,
            92.0,
            20.0
          ],
          "text": "deviation st"
        }
      },
      {
        "box": {
          "id": "deviation",
          "maxclass": "flonum",
          "patching_rect": [
            118.0,
            519.0,
            62.0,
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
            188.0,
            519.0,
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
          "id": "fm_label",
          "maxclass": "comment",
          "patching_rect": [
            310.0,
            522.0,
            100.0,
            20.0
          ],
          "text": "grain FM cents"
        }
      },
      {
        "box": {
          "id": "fm",
          "maxclass": "flonum",
          "patching_rect": [
            410.0,
            519.0,
            62.0,
            22.0
          ],
          "minimum": 0.0,
          "maximum": 2400.0,
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
          "id": "fm_pre",
          "maxclass": "newobj",
          "patching_rect": [
            480.0,
            519.0,
            100.0,
            22.0
          ],
          "text": "prepend fmindex",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "sr",
          "maxclass": "newobj",
          "patching_rect": [
            600.0,
            519.0,
            72.0,
            22.0
          ],
          "text": "adstatus sr",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "sr_pre",
          "maxclass": "newobj",
          "patching_rect": [
            680.0,
            519.0,
            125.0,
            22.0
          ],
          "text": "prepend samplerate",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "mubu_title",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            565.0,
            500.0,
            22.0
          ],
          "text": "MuBu PER-GRAIN PARAMETERS",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "window_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            600.0,
            58.0,
            20.0
          ],
          "text": "window"
        }
      },
      {
        "box": {
          "id": "window",
          "maxclass": "umenu",
          "patching_rect": [
            85.0,
            597.0,
            110.0,
            22.0
          ],
          "items": [
            "cosine",
            ",",
            "trapezoid",
            ",",
            "sine"
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
          "id": "window_pre",
          "maxclass": "newobj",
          "patching_rect": [
            205.0,
            597.0,
            100.0,
            22.0
          ],
          "text": "prepend window",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "filtermode_label",
          "maxclass": "comment",
          "patching_rect": [
            320.0,
            600.0,
            72.0,
            20.0
          ],
          "text": "filter mode"
        }
      },
      {
        "box": {
          "id": "filtermode",
          "maxclass": "number",
          "patching_rect": [
            395.0,
            597.0,
            52.0,
            22.0
          ],
          "minimum": 0,
          "maximum": 4,
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
          "id": "filtermode_pre",
          "maxclass": "newobj",
          "patching_rect": [
            455.0,
            597.0,
            115.0,
            22.0
          ],
          "text": "prepend filtermode",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "filterfreq_label",
          "maxclass": "comment",
          "patching_rect": [
            585.0,
            600.0,
            66.0,
            20.0
          ],
          "text": "filter Hz"
        }
      },
      {
        "box": {
          "id": "filterfreq",
          "maxclass": "flonum",
          "patching_rect": [
            650.0,
            597.0,
            70.0,
            22.0
          ],
          "minimum": 20.0,
          "maximum": 20000.0,
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
          "id": "filterfreq_pre",
          "maxclass": "newobj",
          "patching_rect": [
            730.0,
            597.0,
            110.0,
            22.0
          ],
          "text": "prepend filterfreq",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "filterq_label",
          "maxclass": "comment",
          "patching_rect": [
            855.0,
            600.0,
            52.0,
            20.0
          ],
          "text": "Q"
        }
      },
      {
        "box": {
          "id": "filterq",
          "maxclass": "flonum",
          "patching_rect": [
            900.0,
            597.0,
            62.0,
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
          "id": "filterq_pre",
          "maxclass": "newobj",
          "patching_rect": [
            970.0,
            597.0,
            95.0,
            22.0
          ],
          "text": "prepend filterq",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "reset",
          "maxclass": "message",
          "patching_rect": [
            1080.0,
            597.0,
            125.0,
            22.0
          ],
          "text": "resetoutputs 100",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "mubu_a",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            645.0,
            565.0,
            22.0
          ],
          "text": "mc.mubu.granular~ 6 qmw_pauli_mubu_atlas_A @play 0 @cyclic 1 @microtiming 1 @centered 1 @outputposition 1 @maxresampling 4800",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "multichannelsignal",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "mubu_b",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            680.0,
            565.0,
            22.0
          ],
          "text": "mc.mubu.granular~ 6 qmw_pauli_mubu_atlas_B @play 0 @cyclic 1 @microtiming 1 @centered 1 @outputposition 1 @maxresampling 4800",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "multichannelsignal",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "metadata_a",
          "maxclass": "message",
          "patching_rect": [
            610.0,
            645.0,
            285.0,
            22.0
          ],
          "text": "A actual grain position / duration",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "metadata_b",
          "maxclass": "message",
          "patching_rect": [
            610.0,
            680.0,
            285.0,
            22.0
          ],
          "text": "B actual grain position / duration",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "gain_a",
          "maxclass": "newobj",
          "patching_rect": [
            920.0,
            645.0,
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
            920.0,
            680.0,
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
          "id": "sum",
          "maxclass": "newobj",
          "patching_rect": [
            1010.0,
            663.0,
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
            1090.0,
            663.0,
            145.0,
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
            1115.0,
            705.0,
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
            790.0,
            745.0,
            55.0,
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
            845.0,
            742.0,
            65.0,
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
            920.0,
            742.0,
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
            1005.0,
            742.0,
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
            1080.0,
            742.0,
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
            1170.0,
            742.0,
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
            1080.0,
            777.0,
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
            1170.0,
            777.0,
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
            1010.0,
            775.0,
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
            1040.0,
            775.0,
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
            1110.0,
            820.0,
            52.0,
            52.0
          ],
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "init",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            745.0,
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
          "maxclass": "message",
          "patching_rect": [
            140.0,
            745.0,
            65.0,
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
          "id": "loadbang",
          "maxclass": "newobj",
          "patching_rect": [
            255.0,
            745.0,
            62.0,
            22.0
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
          "id": "atlas_start",
          "maxclass": "newobj",
          "patching_rect": [
            327.0,
            745.0,
            42.0,
            22.0
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
          "id": "atlas_attach_delay",
          "maxclass": "newobj",
          "patching_rect": [
            379.0,
            745.0,
            72.0,
            22.0
          ],
          "text": "delay 100",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "init_atlas_a",
          "maxclass": "message",
          "patching_rect": [
            461.0,
            745.0,
            220.0,
            22.0
          ],
          "text": "mubuname qmw_pauli_mubu_atlas_A",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_atlas_b",
          "maxclass": "message",
          "patching_rect": [
            691.0,
            745.0,
            220.0,
            22.0
          ],
          "text": "mubuname qmw_pauli_mubu_atlas_B",
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
            25.0,
            780.0,
            110.0,
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
            145.0,
            780.0,
            82.0,
            22.0
          ],
          "text": "loadmess 4",
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
            237.0,
            780.0,
            82.0,
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
            329.0,
            780.0,
            82.0,
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
            421.0,
            780.0,
            82.0,
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
          "id": "init_explore",
          "maxclass": "newobj",
          "patching_rect": [
            513.0,
            780.0,
            90.0,
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
            613.0,
            780.0,
            90.0,
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
            713.0,
            780.0,
            90.0,
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
          "id": "init_period",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            815.0,
            82.0,
            22.0
          ],
          "text": "loadmess 55.",
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
            117.0,
            815.0,
            90.0,
            22.0
          ],
          "text": "loadmess 140.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_positionvar",
          "maxclass": "newobj",
          "patching_rect": [
            217.0,
            815.0,
            90.0,
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
          "id": "init_deviation",
          "maxclass": "newobj",
          "patching_rect": [
            317.0,
            815.0,
            82.0,
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
          "id": "init_fm",
          "maxclass": "newobj",
          "patching_rect": [
            409.0,
            815.0,
            82.0,
            22.0
          ],
          "text": "loadmess 35.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_window",
          "maxclass": "newobj",
          "patching_rect": [
            501.0,
            815.0,
            105.0,
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
          "id": "init_filtermode",
          "maxclass": "newobj",
          "patching_rect": [
            616.0,
            815.0,
            82.0,
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
          "id": "init_filterfreq",
          "maxclass": "newobj",
          "patching_rect": [
            708.0,
            815.0,
            98.0,
            22.0
          ],
          "text": "loadmess 5000.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "init_filterq",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            850.0,
            82.0,
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
          "id": "init_master",
          "maxclass": "newobj",
          "patching_rect": [
            117.0,
            850.0,
            90.0,
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
            217.0,
            850.0,
            82.0,
            22.0
          ],
          "text": "loadmess 1",
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
            "loadbang",
            0
          ],
          "destination": [
            "mode_seed",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mode_seed",
            0
          ],
          "destination": [
            "mode_track",
            0
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
            "mubu_a",
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
            "mubu_b",
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
            "scheduler",
            4
          ],
          "destination": [
            "state_track",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "scheduler",
            5
          ],
          "destination": [
            "grain_track",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "scheduler",
            4
          ],
          "destination": [
            "state_append_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "state_append_route",
            0
          ],
          "destination": [
            "state_time",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "state_time",
            0
          ],
          "destination": [
            "view_speedlim",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "view_speedlim",
            0
          ],
          "destination": [
            "view_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "view_trigger",
            1
          ],
          "destination": [
            "view_end",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "view_end",
            0
          ],
          "destination": [
            "view_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "view_trigger",
            0
          ],
          "destination": [
            "view_start",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "view_start",
            0
          ],
          "destination": [
            "view_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "view_pack",
            0
          ],
          "destination": [
            "view_domain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "view_domain",
            0
          ],
          "destination": [
            "corpus",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "view_freeze",
            0
          ],
          "destination": [
            "view_freeze_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "view_freeze_pre",
            0
          ],
          "destination": [
            "corpus",
            0
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
            "explore",
            0
          ],
          "destination": [
            "explore_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "explore_pre",
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
            "period",
            0
          ],
          "destination": [
            "period_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "period_pre",
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
            "scheduler",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "positionvar",
            0
          ],
          "destination": [
            "positionvar_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "positionvar_pre",
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
            "fm",
            0
          ],
          "destination": [
            "fm_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fm_pre",
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
            "loadbang",
            0
          ],
          "destination": [
            "sr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sr",
            0
          ],
          "destination": [
            "sr_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sr_pre",
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
            "window",
            1
          ],
          "destination": [
            "window_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "window_pre",
            0
          ],
          "destination": [
            "mubu_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "window_pre",
            0
          ],
          "destination": [
            "mubu_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "filtermode",
            0
          ],
          "destination": [
            "filtermode_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "filtermode_pre",
            0
          ],
          "destination": [
            "mubu_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "filtermode_pre",
            0
          ],
          "destination": [
            "mubu_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "filterfreq",
            0
          ],
          "destination": [
            "filterfreq_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "filterfreq_pre",
            0
          ],
          "destination": [
            "mubu_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "filterfreq_pre",
            0
          ],
          "destination": [
            "mubu_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "filterq",
            0
          ],
          "destination": [
            "filterq_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "filterq_pre",
            0
          ],
          "destination": [
            "mubu_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "filterq_pre",
            0
          ],
          "destination": [
            "mubu_b",
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
            "mubu_a",
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
            "mubu_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mubu_a",
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
            "mubu_b",
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
            "mubu_a",
            1
          ],
          "destination": [
            "metadata_a",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mubu_b",
            1
          ],
          "destination": [
            "metadata_b",
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
            "sum",
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
            "loadbang",
            0
          ],
          "destination": [
            "atlas_start",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "atlas_start",
            1
          ],
          "destination": [
            "init_render",
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
            "atlas_js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "atlas_start",
            0
          ],
          "destination": [
            "atlas_attach_delay",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "atlas_attach_delay",
            0
          ],
          "destination": [
            "init_atlas_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "atlas_attach_delay",
            0
          ],
          "destination": [
            "init_atlas_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_atlas_a",
            0
          ],
          "destination": [
            "mubu_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_atlas_b",
            0
          ],
          "destination": [
            "mubu_b",
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
            "init_explore",
            0
          ],
          "destination": [
            "explore",
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
            "init_period",
            0
          ],
          "destination": [
            "period",
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
      },
      {
        "patchline": {
          "source": [
            "init_positionvar",
            0
          ],
          "destination": [
            "positionvar",
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
            "init_fm",
            0
          ],
          "destination": [
            "fm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_window",
            0
          ],
          "destination": [
            "window",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_filtermode",
            0
          ],
          "destination": [
            "filtermode",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_filterfreq",
            0
          ],
          "destination": [
            "filterfreq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_filterq",
            0
          ],
          "destination": [
            "filterq",
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
            "run",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "qmw_pauli_mubu_scheduler_v1.js",
        "type": "TEXT"
      },
      {
        "name": "qmw_mubu_wavetable_atlas_v1.js",
        "type": "TEXT"
      },
      {
        "name": "mc.mubu.granular~.mxo",
        "type": "iLaX"
      },
      {
        "name": "mubu.mxo",
        "type": "iLaX"
      },
      {
        "name": "mubu.track.mxo",
        "type": "iLaX"
      },
      {
        "name": "imubu.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
