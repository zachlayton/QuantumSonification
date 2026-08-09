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
      45,
      45,
      1340,
      840
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            15,
            920,
            26
          ],
          "text": "QMW GROVER STATEVECTOR \u2014 LITERAL REALTIME SONIFICATION",
          "fontsize": 17,
          "fontface": 1
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            25,
            43,
            1100,
            40
          ],
          "text": "65,536 complex amplitudes evolve exactly. Max hears measured oracle and diffusion frames; no closed-form trajectory drives the sound."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            95,
            118,
            22
          ],
          "text": "udpreceive 7493",
          "numinlets": 0,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "root",
          "maxclass": "newobj",
          "patching_rect": [
            155,
            95,
            245,
            22
          ],
          "text": "OSC-route /qmw/grover/statevector",
          "numinlets": 1,
          "numoutlets": 2
        }
      },
      {
        "box": {
          "id": "route",
          "maxclass": "newobj",
          "patching_rect": [
            415,
            95,
            290,
            22
          ],
          "text": "OSC-route /frame /modes /found /state",
          "numinlets": 1,
          "numoutlets": 5
        }
      },
      {
        "box": {
          "id": "pre_frame",
          "maxclass": "newobj",
          "patching_rect": [
            415,
            132,
            92,
            22
          ],
          "text": "prepend frame"
        }
      },
      {
        "box": {
          "id": "pre_modes",
          "maxclass": "newobj",
          "patching_rect": [
            515,
            132,
            92,
            22
          ],
          "text": "prepend modes"
        }
      },
      {
        "box": {
          "id": "pre_found",
          "maxclass": "newobj",
          "patching_rect": [
            615,
            132,
            92,
            22
          ],
          "text": "prepend found"
        }
      },
      {
        "box": {
          "id": "pre_state",
          "maxclass": "newobj",
          "patching_rect": [
            715,
            132,
            92,
            22
          ],
          "text": "prepend state"
        }
      },
      {
        "box": {
          "id": "dispatch",
          "maxclass": "newobj",
          "patching_rect": [
            415,
            170,
            255,
            22
          ],
          "text": "js qmw_grover_statevector_dispatch_v1.js",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
            "",
            "",
            "float",
            "",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            25,
            132,
            375,
            22
          ],
          "text": "waiting for exact statevector stream...",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "prob_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            175,
            155,
            20
          ],
          "text": "MARKED PROBABILITY"
        }
      },
      {
        "box": {
          "id": "prob",
          "maxclass": "flonum",
          "patching_rect": [
            180,
            175,
            130,
            22
          ],
          "format": 6,
          "numinlets": 1,
          "numoutlets": 2
        }
      },
      {
        "box": {
          "id": "meter",
          "maxclass": "newobj",
          "patching_rect": [
            320,
            175,
            80,
            22
          ],
          "text": "scale 0. 1. 0 127",
          "numinlets": 6,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "prob_slider",
          "maxclass": "slider",
          "patching_rect": [
            25,
            205,
            375,
            20
          ],
          "size": 128,
          "min": 0.0,
          "mult": 1.0,
          "numinlets": 1,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "poly",
          "maxclass": "newobj",
          "patching_rect": [
            415,
            215,
            385,
            22
          ],
          "text": "poly~ qmw_grover_walsh_mode_voice_v1.maxpat 64 @steal 0",
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
          "id": "send_l",
          "maxclass": "newobj",
          "patching_rect": [
            415,
            255,
            145,
            22
          ],
          "text": "send~ qmw_spectral_L"
        }
      },
      {
        "box": {
          "id": "send_r",
          "maxclass": "newobj",
          "patching_rect": [
            570,
            255,
            145,
            22
          ],
          "text": "send~ qmw_spectral_R"
        }
      },
      {
        "box": {
          "id": "surface",
          "maxclass": "bpatcher",
          "patching_rect": [
            25,
            265,
            760,
            490
          ],
          "name": "QMW_Realtime_Surface_Reverb_Grover_v1.maxpat",
          "numinlets": 0,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "surface_ctl",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            215,
            142,
            22
          ],
          "text": "s qmw.surface.control",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "wet_l",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            265,
            145,
            22
          ],
          "text": "receive~ qmw_surface_L"
        }
      },
      {
        "box": {
          "id": "wet_r",
          "maxclass": "newobj",
          "patching_rect": [
            970,
            265,
            145,
            22
          ],
          "text": "receive~ qmw_surface_R"
        }
      },
      {
        "box": {
          "id": "ringmod",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            305,
            265,
            22
          ],
          "text": "abl.dsp.ringmod~ @frequency 7. @mix 0.8",
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
          "id": "tides",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            345,
            250,
            22
          ],
          "text": "abl.dsp.tides~ @rate 0.18 @tides 0.7 @mix 0.7",
          "numinlets": 5,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "modal_l",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            385,
            235,
            22
          ],
          "text": "abl.dsp.modalresonator~ 84 0.7 @decay 0.75 @damping 0.28",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "modal_r",
          "maxclass": "newobj",
          "patching_rect": [
            1060,
            385,
            235,
            22
          ],
          "text": "abl.dsp.modalresonator~ 91 0.7 @decay 0.75 @damping 0.28",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "prism",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            425,
            280,
            22
          ],
          "text": "abl.dsp.prism~ @decay 0.86 @size 0.72 @mix 1.",
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
          "id": "event_sel",
          "maxclass": "newobj",
          "patching_rect": [
            1120,
            215,
            62,
            22
          ],
          "text": "sel 1 0",
          "numinlets": 1,
          "numoutlets": 3
        }
      },
      {
        "box": {
          "id": "found_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            1120,
            250,
            70,
            22
          ],
          "text": "t b b b",
          "numinlets": 1,
          "numoutlets": 3
        }
      },
      {
        "box": {
          "id": "freeze",
          "maxclass": "message",
          "patching_rect": [
            1200,
            250,
            62,
            22
          ],
          "text": "freeze 1"
        }
      },
      {
        "box": {
          "id": "unfreeze",
          "maxclass": "message",
          "patching_rect": [
            1200,
            280,
            62,
            22
          ],
          "text": "freeze 0"
        }
      },
      {
        "box": {
          "id": "moving_down",
          "maxclass": "message",
          "patching_rect": [
            1120,
            315,
            70,
            22
          ],
          "text": "0. 700"
        }
      },
      {
        "box": {
          "id": "held_up",
          "maxclass": "message",
          "patching_rect": [
            1200,
            315,
            70,
            22
          ],
          "text": "1. 700"
        }
      },
      {
        "box": {
          "id": "moving_up",
          "maxclass": "message",
          "patching_rect": [
            1120,
            345,
            70,
            22
          ],
          "text": "1. 80"
        }
      },
      {
        "box": {
          "id": "held_down",
          "maxclass": "message",
          "patching_rect": [
            1200,
            345,
            70,
            22
          ],
          "text": "0. 80"
        }
      },
      {
        "box": {
          "id": "moving_gain",
          "maxclass": "newobj",
          "patching_rect": [
            1120,
            385,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "held_gain",
          "maxclass": "newobj",
          "patching_rect": [
            1200,
            385,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "move_l",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            465,
            38,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "move_r",
          "maxclass": "newobj",
          "patching_rect": [
            860,
            465,
            38,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "hold_l",
          "maxclass": "newobj",
          "patching_rect": [
            925,
            465,
            38,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "hold_r",
          "maxclass": "newobj",
          "patching_rect": [
            970,
            465,
            38,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "sum_l",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            505,
            38,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "sum_r",
          "maxclass": "newobj",
          "patching_rect": [
            870,
            505,
            38,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "wet_scale_l",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            540,
            55,
            22
          ],
          "text": "*~ 0.7"
        }
      },
      {
        "box": {
          "id": "wet_scale_r",
          "maxclass": "newobj",
          "patching_rect": [
            880,
            540,
            55,
            22
          ],
          "text": "*~ 0.7"
        }
      },
      {
        "box": {
          "id": "dry_l",
          "maxclass": "newobj",
          "patching_rect": [
            950,
            540,
            55,
            22
          ],
          "text": "*~ 0.3"
        }
      },
      {
        "box": {
          "id": "dry_r",
          "maxclass": "newobj",
          "patching_rect": [
            1015,
            540,
            55,
            22
          ],
          "text": "*~ 0.3"
        }
      },
      {
        "box": {
          "id": "final_l",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            575,
            38,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "final_r",
          "maxclass": "newobj",
          "patching_rect": [
            870,
            575,
            38,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "gain",
          "maxclass": "live.gain~",
          "patching_rect": [
            950,
            575,
            95,
            125
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
                -9.0
              ],
              "parameter_initial_enable": 1,
              "parameter_longname": "Grover statevector output",
              "parameter_mmax": 6.0,
              "parameter_mmin": -70.0,
              "parameter_modmode": 0,
              "parameter_shortname": "Grover output",
              "parameter_type": 0,
              "parameter_unitstyle": 4
            }
          },
          "varname": "grover_statevector_output"
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "newobj",
          "patching_rect": [
            965,
            720,
            68,
            22
          ],
          "text": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "init",
          "maxclass": "newobj",
          "patching_rect": [
            1080,
            575,
            190,
            22
          ],
          "text": "loadmess 0.7 0.7 0.8",
          "numinlets": 0,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "init_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            1080,
            610,
            95,
            22
          ],
          "text": "unpack f f f"
        }
      },
      {
        "box": {
          "id": "init_wet",
          "maxclass": "message",
          "patching_rect": [
            1080,
            645,
            88,
            22
          ],
          "text": "dry_wet $1"
        }
      },
      {
        "box": {
          "id": "init_deform",
          "maxclass": "message",
          "patching_rect": [
            1175,
            645,
            72,
            22
          ],
          "text": "deform $1"
        }
      },
      {
        "box": {
          "id": "init_ring",
          "maxclass": "message",
          "patching_rect": [
            1255,
            645,
            52,
            22
          ],
          "text": "mix $1"
        }
      },
      {
        "box": {
          "id": "command",
          "maxclass": "comment",
          "patching_rect": [
            815,
            760,
            495,
            42
          ],
          "text": "Run: python feedback/grover_statevector_osc_v1.py\nDefault target 57893 = |1110001000100101>, exact 16-qubit evolution. Add --backend mlx for Metal."
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
            "root",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "root",
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
            "pre_frame",
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
            "pre_modes",
            0
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
            "pre_found",
            0
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
            "pre_state",
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
            "pre_modes",
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
            "pre_found",
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
            "pre_state",
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
            "status",
            1
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
            "prob",
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
            "meter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "meter",
            0
          ],
          "destination": [
            "prob_slider",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dispatch",
            3
          ],
          "destination": [
            "surface_ctl",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dispatch",
            4
          ],
          "destination": [
            "event_sel",
            0
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
            "send_l",
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
            "send_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wet_l",
            0
          ],
          "destination": [
            "ringmod",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wet_r",
            0
          ],
          "destination": [
            "ringmod",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ringmod",
            0
          ],
          "destination": [
            "tides",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ringmod",
            1
          ],
          "destination": [
            "tides",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "tides",
            0
          ],
          "destination": [
            "modal_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "tides",
            1
          ],
          "destination": [
            "modal_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modal_l",
            0
          ],
          "destination": [
            "prism",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modal_r",
            0
          ],
          "destination": [
            "prism",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "event_sel",
            0
          ],
          "destination": [
            "found_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "event_sel",
            1
          ],
          "destination": [
            "unfreeze",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "found_trigger",
            0
          ],
          "destination": [
            "freeze",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "found_trigger",
            1
          ],
          "destination": [
            "moving_down",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "found_trigger",
            2
          ],
          "destination": [
            "held_up",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freeze",
            0
          ],
          "destination": [
            "prism",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unfreeze",
            0
          ],
          "destination": [
            "prism",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "event_sel",
            1
          ],
          "destination": [
            "moving_up",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "event_sel",
            1
          ],
          "destination": [
            "held_down",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "moving_down",
            0
          ],
          "destination": [
            "moving_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "moving_up",
            0
          ],
          "destination": [
            "moving_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "held_up",
            0
          ],
          "destination": [
            "held_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "held_down",
            0
          ],
          "destination": [
            "held_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modal_l",
            0
          ],
          "destination": [
            "move_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modal_r",
            0
          ],
          "destination": [
            "move_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "moving_gain",
            0
          ],
          "destination": [
            "move_l",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "moving_gain",
            0
          ],
          "destination": [
            "move_r",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prism",
            0
          ],
          "destination": [
            "hold_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prism",
            1
          ],
          "destination": [
            "hold_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "held_gain",
            0
          ],
          "destination": [
            "hold_l",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "held_gain",
            0
          ],
          "destination": [
            "hold_r",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "move_l",
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
            "hold_l",
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
            "move_r",
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
            "hold_r",
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
            "wet_scale_l",
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
            "wet_scale_r",
            0
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
            "dry_l",
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
            "dry_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wet_scale_l",
            0
          ],
          "destination": [
            "final_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dry_l",
            0
          ],
          "destination": [
            "final_l",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wet_scale_r",
            0
          ],
          "destination": [
            "final_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dry_r",
            0
          ],
          "destination": [
            "final_r",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "final_l",
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
            "final_r",
            0
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
            "dac",
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
            "init_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_unpack",
            0
          ],
          "destination": [
            "init_wet",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_unpack",
            1
          ],
          "destination": [
            "init_deform",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_unpack",
            2
          ],
          "destination": [
            "init_ring",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_wet",
            0
          ],
          "destination": [
            "surface_ctl",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_deform",
            0
          ],
          "destination": [
            "surface_ctl",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init_ring",
            0
          ],
          "destination": [
            "ringmod",
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
        "name": "qmw_grover_statevector_dispatch_v1.js",
        "type": "TEXT"
      },
      {
        "name": "qmw_grover_walsh_mode_voice_v1.maxpat",
        "type": "JSON"
      },
      {
        "name": "QMW_Realtime_Surface_Reverb_Grover_v1.maxpat",
        "type": "JSON"
      },
      {
        "name": "abl.dsp.ringmod~.mxo",
        "type": "iLaX"
      },
      {
        "name": "abl.dsp.tides~.mxo",
        "type": "iLaX"
      },
      {
        "name": "abl.dsp.prism~.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
