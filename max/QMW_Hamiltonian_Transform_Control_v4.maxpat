{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 9,
      "minor": 0,
      "revision": 8,
      "architecture": "x64",
      "modernui": 1
    },
    "classnamespace": "box",
    "rect": [
      40.0,
      50.0,
      1000.0,
      580.0
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            18.0,
            930.0,
            32.0
          ],
          "text": "QMW \u00b7 HAMILTONIAN TRANSFORM CONTROL v4",
          "fontsize": 20.0,
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
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            52.0,
            930.0,
            22.0
          ],
          "text": "Preview rebuilds the exact representation \u00b7 Commit runs paired 81-setting Full Pauli tomography"
        }
      },
      {
        "box": {
          "id": "launch",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            78.0,
            930.0,
            22.0
          ],
          "text": "Start: python workshop_lightweight/qmw_representation_hamiltonian_v4.py",
          "textcolor": [
            0.68,
            0.7,
            0.75,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "j_label",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            122.0,
            180.0,
            20.0
          ],
          "text": "COUPLING  J"
        }
      },
      {
        "box": {
          "id": "j",
          "maxclass": "flonum",
          "patching_rect": [
            220.0,
            118.0,
            92.0,
            26.0
          ],
          "minimum": -4.0,
          "maximum": 4.0
        }
      },
      {
        "box": {
          "id": "ht_label",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            162.0,
            180.0,
            20.0
          ],
          "text": "TRANSVERSE FIELD  h\u22a5"
        }
      },
      {
        "box": {
          "id": "ht",
          "maxclass": "flonum",
          "patching_rect": [
            220.0,
            158.0,
            92.0,
            26.0
          ],
          "minimum": -4.0,
          "maximum": 4.0
        }
      },
      {
        "box": {
          "id": "hl_label",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            202.0,
            180.0,
            20.0
          ],
          "text": "LONGITUDINAL FIELD  h\u2225"
        }
      },
      {
        "box": {
          "id": "hl",
          "maxclass": "flonum",
          "patching_rect": [
            220.0,
            198.0,
            92.0,
            26.0
          ],
          "minimum": -4.0,
          "maximum": 4.0
        }
      },
      {
        "box": {
          "id": "time_label",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            242.0,
            180.0,
            20.0
          ],
          "text": "EVOLUTION TIME  t"
        }
      },
      {
        "box": {
          "id": "time",
          "maxclass": "flonum",
          "patching_rect": [
            220.0,
            238.0,
            92.0,
            26.0
          ],
          "minimum": -100.0,
          "maximum": 100.0
        }
      },
      {
        "box": {
          "id": "mode_label",
          "maxclass": "comment",
          "patching_rect": [
            370.0,
            122.0,
            130.0,
            20.0
          ],
          "text": "MODE"
        }
      },
      {
        "box": {
          "id": "mode_eigen",
          "maxclass": "message",
          "patching_rect": [
            510.0,
            118.0,
            102.0,
            24.0
          ],
          "text": "eigenbasis"
        }
      },
      {
        "box": {
          "id": "mode_evolution",
          "maxclass": "message",
          "patching_rect": [
            620.0,
            118.0,
            92.0,
            24.0
          ],
          "text": "evolution"
        }
      },
      {
        "box": {
          "id": "boundary_label",
          "maxclass": "comment",
          "patching_rect": [
            370.0,
            162.0,
            130.0,
            20.0
          ],
          "text": "BOUNDARY"
        }
      },
      {
        "box": {
          "id": "boundary_open",
          "maxclass": "message",
          "patching_rect": [
            510.0,
            158.0,
            62.0,
            24.0
          ],
          "text": "open"
        }
      },
      {
        "box": {
          "id": "boundary_periodic",
          "maxclass": "message",
          "patching_rect": [
            580.0,
            158.0,
            82.0,
            24.0
          ],
          "text": "periodic"
        }
      },
      {
        "box": {
          "id": "preset_label",
          "maxclass": "comment",
          "patching_rect": [
            370.0,
            202.0,
            130.0,
            20.0
          ],
          "text": "STATE"
        }
      },
      {
        "box": {
          "id": "preset_ghz",
          "maxclass": "message",
          "patching_rect": [
            510.0,
            198.0,
            48.0,
            24.0
          ],
          "text": "ghz"
        }
      },
      {
        "box": {
          "id": "preset_bell",
          "maxclass": "message",
          "patching_rect": [
            566.0,
            198.0,
            48.0,
            24.0
          ],
          "text": "bell"
        }
      },
      {
        "box": {
          "id": "preset_weave",
          "maxclass": "message",
          "patching_rect": [
            622.0,
            198.0,
            58.0,
            24.0
          ],
          "text": "weave"
        }
      },
      {
        "box": {
          "id": "shots_label",
          "maxclass": "comment",
          "patching_rect": [
            370.0,
            242.0,
            130.0,
            20.0
          ],
          "text": "SHOTS / SETTING"
        }
      },
      {
        "box": {
          "id": "shots",
          "maxclass": "number",
          "patching_rect": [
            510.0,
            238.0,
            78.0,
            26.0
          ],
          "minimum": 1
        }
      },
      {
        "box": {
          "id": "sampling_label",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            298.0,
            180.0,
            20.0
          ],
          "text": "SAMPLING"
        }
      },
      {
        "box": {
          "id": "sampling_fixed",
          "maxclass": "message",
          "patching_rect": [
            220.0,
            294.0,
            58.0,
            24.0
          ],
          "text": "fixed"
        }
      },
      {
        "box": {
          "id": "sampling_resample",
          "maxclass": "message",
          "patching_rect": [
            286.0,
            294.0,
            74.0,
            24.0
          ],
          "text": "resample"
        }
      },
      {
        "box": {
          "id": "sampling_sequence",
          "maxclass": "message",
          "patching_rect": [
            368.0,
            294.0,
            74.0,
            24.0
          ],
          "text": "sequence"
        }
      },
      {
        "box": {
          "id": "seed_label",
          "maxclass": "comment",
          "patching_rect": [
            480.0,
            298.0,
            48.0,
            20.0
          ],
          "text": "SEED"
        }
      },
      {
        "box": {
          "id": "seed",
          "maxclass": "number",
          "patching_rect": [
            536.0,
            294.0,
            96.0,
            26.0
          ],
          "minimum": 0
        }
      },
      {
        "box": {
          "id": "pak",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            350.0,
            470.0,
            24.0
          ],
          "text": "pak i f f f f s s s i s i"
        }
      },
      {
        "box": {
          "id": "speedlim",
          "maxclass": "newobj",
          "patching_rect": [
            520.0,
            350.0,
            92.0,
            24.0
          ],
          "text": "speedlim 150"
        }
      },
      {
        "box": {
          "id": "preview_pack",
          "maxclass": "newobj",
          "patching_rect": [
            628.0,
            350.0,
            260.0,
            24.0
          ],
          "text": "o.pack /qmw/v4/hamiltonian/preview"
        }
      },
      {
        "box": {
          "id": "commit_store",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            390.0,
            58.0,
            24.0
          ],
          "text": "zl reg"
        }
      },
      {
        "box": {
          "id": "commit",
          "maxclass": "textbutton",
          "patching_rect": [
            106.0,
            386.0,
            180.0,
            34.0
          ],
          "text": "COMMIT TOMOGRAPHY",
          "texton": "COMMIT TOMOGRAPHY",
          "bgcolor": [
            0.95,
            0.55,
            0.18,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "commit_pack",
          "maxclass": "newobj",
          "patching_rect": [
            304.0,
            390.0,
            260.0,
            24.0
          ],
          "text": "o.pack /qmw/v4/hamiltonian/commit"
        }
      },
      {
        "box": {
          "id": "reset",
          "maxclass": "message",
          "patching_rect": [
            590.0,
            390.0,
            108.0,
            24.0
          ],
          "text": "reset tracking"
        }
      },
      {
        "box": {
          "id": "reset_pack",
          "maxclass": "newobj",
          "patching_rect": [
            714.0,
            390.0,
            230.0,
            24.0
          ],
          "text": "o.pack /qmw/v4/hamiltonian/reset_tracking"
        }
      },
      {
        "box": {
          "id": "send",
          "maxclass": "newobj",
          "patching_rect": [
            628.0,
            438.0,
            170.0,
            24.0
          ],
          "text": "udpsend 127.0.0.1 7445"
        }
      },
      {
        "box": {
          "id": "notice",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            446.0,
            560.0,
            42.0
          ],
          "text": "Parameter changes are throttled to exact previews. Only COMMIT launches stochastic tomography.",
          "textcolor": [
            0.95,
            0.55,
            0.18,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "load_j",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            510.0,
            80.0,
            22.0
          ],
          "text": "loadmess 0.7",
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "load_ht",
          "maxclass": "newobj",
          "patching_rect": [
            116.0,
            510.0,
            80.0,
            22.0
          ],
          "text": "loadmess 0.45",
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "load_hl",
          "maxclass": "newobj",
          "patching_rect": [
            202.0,
            510.0,
            80.0,
            22.0
          ],
          "text": "loadmess 0.13",
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "load_time",
          "maxclass": "newobj",
          "patching_rect": [
            288.0,
            510.0,
            80.0,
            22.0
          ],
          "text": "loadmess 1.",
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "load_mode",
          "maxclass": "newobj",
          "patching_rect": [
            374.0,
            510.0,
            80.0,
            22.0
          ],
          "text": "loadmess eigenbasis",
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "load_boundary",
          "maxclass": "newobj",
          "patching_rect": [
            460.0,
            510.0,
            80.0,
            22.0
          ],
          "text": "loadmess open",
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "load_preset",
          "maxclass": "newobj",
          "patching_rect": [
            546.0,
            510.0,
            80.0,
            22.0
          ],
          "text": "loadmess ghz",
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "load_shots",
          "maxclass": "newobj",
          "patching_rect": [
            632.0,
            510.0,
            80.0,
            22.0
          ],
          "text": "loadmess 256",
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "load_sampling",
          "maxclass": "newobj",
          "patching_rect": [
            718.0,
            510.0,
            80.0,
            22.0
          ],
          "text": "loadmess fixed",
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "load_seed",
          "maxclass": "newobj",
          "patching_rect": [
            804.0,
            510.0,
            80.0,
            22.0
          ],
          "text": "loadmess 23",
          "hidden": 1
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "j",
            0
          ],
          "destination": [
            "pak",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ht",
            0
          ],
          "destination": [
            "pak",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "hl",
            0
          ],
          "destination": [
            "pak",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "time",
            0
          ],
          "destination": [
            "pak",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mode_eigen",
            0
          ],
          "destination": [
            "pak",
            5
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mode_evolution",
            0
          ],
          "destination": [
            "pak",
            5
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "boundary_open",
            0
          ],
          "destination": [
            "pak",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "boundary_periodic",
            0
          ],
          "destination": [
            "pak",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "preset_ghz",
            0
          ],
          "destination": [
            "pak",
            7
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "preset_bell",
            0
          ],
          "destination": [
            "pak",
            7
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "preset_weave",
            0
          ],
          "destination": [
            "pak",
            7
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "shots",
            0
          ],
          "destination": [
            "pak",
            8
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sampling_fixed",
            0
          ],
          "destination": [
            "pak",
            9
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sampling_resample",
            0
          ],
          "destination": [
            "pak",
            9
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sampling_sequence",
            0
          ],
          "destination": [
            "pak",
            9
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
            "pak",
            10
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pak",
            0
          ],
          "destination": [
            "speedlim",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pak",
            0
          ],
          "destination": [
            "commit_store",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "speedlim",
            0
          ],
          "destination": [
            "preview_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "preview_pack",
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
            "commit",
            0
          ],
          "destination": [
            "commit_store",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "commit_store",
            0
          ],
          "destination": [
            "commit_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "commit_pack",
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
            "reset",
            0
          ],
          "destination": [
            "reset_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "reset_pack",
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
            "load_j",
            0
          ],
          "destination": [
            "j",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_ht",
            0
          ],
          "destination": [
            "ht",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_hl",
            0
          ],
          "destination": [
            "hl",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_time",
            0
          ],
          "destination": [
            "time",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_mode",
            0
          ],
          "destination": [
            "pak",
            5
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_boundary",
            0
          ],
          "destination": [
            "pak",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_preset",
            0
          ],
          "destination": [
            "pak",
            7
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_shots",
            0
          ],
          "destination": [
            "shots",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_sampling",
            0
          ],
          "destination": [
            "pak",
            9
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_seed",
            0
          ],
          "destination": [
            "seed",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "o.pack.mxo",
        "type": "iLaX",
        "implicit": 1
      }
    ],
    "autosave": 0
  }
}
