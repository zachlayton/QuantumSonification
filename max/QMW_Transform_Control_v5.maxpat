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
      1560.0,
      360.0
    ],
    "openinpresentation": 1,
    "default_fontname": "Arial",
    "boxes": [
      {
        "box": {
          "id": "panel",
          "maxclass": "panel",
          "patching_rect": [
            0.0,
            0.0,
            1540.0,
            180.0
          ],
          "presentation": 1,
          "presentation_rect": [
            0.0,
            0.0,
            1540.0,
            180.0
          ],
          "bgcolor": [
            0.08,
            0.09,
            0.12,
            1.0
          ],
          "border": 1,
          "background": 1,
          "ignoreclick": 1
        }
      },
      {
        "box": {
          "id": "heading",
          "maxclass": "comment",
          "patching_rect": [
            16.0,
            8.0,
            420.0,
            24.0
          ],
          "text": "REPRESENTATION TRANSFORM",
          "presentation": 1,
          "presentation_rect": [
            16.0,
            8.0,
            420.0,
            24.0
          ],
          "fontsize": 15.0,
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
          "id": "j_label",
          "maxclass": "comment",
          "patching_rect": [
            16.0,
            42.0,
            42.0,
            20.0
          ],
          "text": "J",
          "presentation": 1,
          "presentation_rect": [
            16.0,
            42.0,
            42.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "j",
          "maxclass": "flonum",
          "patching_rect": [
            60.0,
            38.0,
            78.0,
            25.0
          ],
          "presentation": 1,
          "presentation_rect": [
            60.0,
            38.0,
            78.0,
            25.0
          ],
          "minimum": -4.0,
          "maximum": 4.0,
          "varname": "hamiltonian_j",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "ht_label",
          "maxclass": "comment",
          "patching_rect": [
            146.0,
            42.0,
            42.0,
            20.0
          ],
          "text": "h\u22a5",
          "presentation": 1,
          "presentation_rect": [
            146.0,
            42.0,
            42.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "ht",
          "maxclass": "flonum",
          "patching_rect": [
            190.0,
            38.0,
            78.0,
            25.0
          ],
          "presentation": 1,
          "presentation_rect": [
            190.0,
            38.0,
            78.0,
            25.0
          ],
          "minimum": -4.0,
          "maximum": 4.0,
          "varname": "hamiltonian_ht",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "hl_label",
          "maxclass": "comment",
          "patching_rect": [
            276.0,
            42.0,
            42.0,
            20.0
          ],
          "text": "h\u2225",
          "presentation": 1,
          "presentation_rect": [
            276.0,
            42.0,
            42.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "hl",
          "maxclass": "flonum",
          "patching_rect": [
            320.0,
            38.0,
            78.0,
            25.0
          ],
          "presentation": 1,
          "presentation_rect": [
            320.0,
            38.0,
            78.0,
            25.0
          ],
          "minimum": -4.0,
          "maximum": 4.0,
          "varname": "hamiltonian_hl",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "time_label",
          "maxclass": "comment",
          "patching_rect": [
            406.0,
            42.0,
            42.0,
            20.0
          ],
          "text": "time",
          "presentation": 1,
          "presentation_rect": [
            406.0,
            42.0,
            42.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "time",
          "maxclass": "flonum",
          "patching_rect": [
            450.0,
            38.0,
            78.0,
            25.0
          ],
          "presentation": 1,
          "presentation_rect": [
            450.0,
            38.0,
            78.0,
            25.0
          ],
          "minimum": -100.0,
          "maximum": 100.0,
          "varname": "hamiltonian_time",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "transform_label",
          "maxclass": "comment",
          "patching_rect": [
            552.0,
            42.0,
            68.0,
            20.0
          ],
          "text": "transform",
          "presentation": 1,
          "presentation_rect": [
            552.0,
            42.0,
            68.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "transform",
          "maxclass": "umenu",
          "patching_rect": [
            622.0,
            38.0,
            220.0,
            24.0
          ],
          "presentation": 1,
          "presentation_rect": [
            622.0,
            38.0,
            220.0,
            24.0
          ],
          "items": [
            "identity",
            ",",
            "hadamard",
            ",",
            "qft",
            ",",
            "inverse_qft",
            ",",
            "hamiltonian",
            ",",
            "graph_laplacian",
            ",",
            "floquet",
            ",",
            "grover_amplified",
            ",",
            "epistrophe"
          ],
          "varname": "representation_transform",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "boundary_label",
          "maxclass": "comment",
          "patching_rect": [
            858.0,
            42.0,
            72.0,
            20.0
          ],
          "text": "boundary",
          "presentation": 1,
          "presentation_rect": [
            858.0,
            42.0,
            72.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "boundary",
          "maxclass": "umenu",
          "patching_rect": [
            932.0,
            38.0,
            114.0,
            24.0
          ],
          "presentation": 1,
          "presentation_rect": [
            932.0,
            38.0,
            114.0,
            24.0
          ],
          "items": [
            "open",
            ",",
            "periodic"
          ],
          "varname": "hamiltonian_boundary",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "preset_label",
          "maxclass": "comment",
          "patching_rect": [
            16.0,
            88.0,
            48.0,
            20.0
          ],
          "text": "state",
          "presentation": 1,
          "presentation_rect": [
            16.0,
            88.0,
            48.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "preset",
          "maxclass": "umenu",
          "patching_rect": [
            66.0,
            84.0,
            154.0,
            24.0
          ],
          "presentation": 1,
          "presentation_rect": [
            66.0,
            84.0,
            154.0,
            24.0
          ],
          "items": [
            "ghz",
            ",",
            "bell",
            ",",
            "weave"
          ],
          "varname": "hamiltonian_preset",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "shots_label",
          "maxclass": "comment",
          "patching_rect": [
            238.0,
            88.0,
            46.0,
            20.0
          ],
          "text": "shots",
          "presentation": 1,
          "presentation_rect": [
            238.0,
            88.0,
            46.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "shots",
          "maxclass": "number",
          "patching_rect": [
            286.0,
            84.0,
            66.0,
            25.0
          ],
          "presentation": 1,
          "presentation_rect": [
            286.0,
            84.0,
            66.0,
            25.0
          ],
          "minimum": 1,
          "varname": "hamiltonian_shots",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "sampling_label",
          "maxclass": "comment",
          "patching_rect": [
            370.0,
            88.0,
            68.0,
            20.0
          ],
          "text": "sampling",
          "presentation": 1,
          "presentation_rect": [
            370.0,
            88.0,
            68.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "sampling",
          "maxclass": "umenu",
          "patching_rect": [
            440.0,
            84.0,
            198.0,
            24.0
          ],
          "presentation": 1,
          "presentation_rect": [
            440.0,
            84.0,
            198.0,
            24.0
          ],
          "items": [
            "fixed",
            ",",
            "resample",
            ",",
            "sequence"
          ],
          "varname": "hamiltonian_sampling",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "seed_label",
          "maxclass": "comment",
          "patching_rect": [
            656.0,
            88.0,
            38.0,
            20.0
          ],
          "text": "seed",
          "presentation": 1,
          "presentation_rect": [
            656.0,
            88.0,
            38.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "seed",
          "maxclass": "number",
          "patching_rect": [
            696.0,
            84.0,
            82.0,
            25.0
          ],
          "presentation": 1,
          "presentation_rect": [
            696.0,
            84.0,
            82.0,
            25.0
          ],
          "minimum": 0,
          "varname": "hamiltonian_seed",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "commit",
          "maxclass": "textbutton",
          "patching_rect": [
            800.0,
            78.0,
            168.0,
            36.0
          ],
          "text": "COMMIT TOMOGRAPHY",
          "presentation": 1,
          "presentation_rect": [
            800.0,
            78.0,
            168.0,
            36.0
          ],
          "texton": "COMMIT TOMOGRAPHY",
          "bgcolor": [
            0.96,
            0.56,
            0.18,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "reset",
          "maxclass": "message",
          "patching_rect": [
            982.0,
            84.0,
            102.0,
            24.0
          ],
          "text": "reset tracking",
          "presentation": 1,
          "presentation_rect": [
            982.0,
            84.0,
            102.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "store1",
          "maxclass": "message",
          "patching_rect": [
            1120.0,
            38.0,
            58.0,
            24.0
          ],
          "text": "store 1",
          "presentation": 1,
          "presentation_rect": [
            1120.0,
            38.0,
            58.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "recall1",
          "maxclass": "message",
          "patching_rect": [
            1184.0,
            38.0,
            34.0,
            24.0
          ],
          "text": "1",
          "presentation": 1,
          "presentation_rect": [
            1184.0,
            38.0,
            34.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "write",
          "maxclass": "message",
          "patching_rect": [
            1224.0,
            38.0,
            48.0,
            24.0
          ],
          "text": "write",
          "presentation": 1,
          "presentation_rect": [
            1224.0,
            38.0,
            48.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "read",
          "maxclass": "message",
          "patching_rect": [
            1278.0,
            38.0,
            44.0,
            24.0
          ],
          "text": "read",
          "presentation": 1,
          "presentation_rect": [
            1278.0,
            38.0,
            44.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "preset_note",
          "maxclass": "comment",
          "patching_rect": [
            1120.0,
            68.0,
            240.0,
            42.0
          ],
          "text": "preset 1 \u00b7 store / recall / write / read",
          "presentation": 1,
          "presentation_rect": [
            1120.0,
            68.0,
            240.0,
            42.0
          ],
          "textcolor": [
            0.7,
            0.72,
            0.78,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "preview_note",
          "maxclass": "comment",
          "patching_rect": [
            650.0,
            132.0,
            700.0,
            24.0
          ],
          "text": "J / fields / time: Hamiltonian + Floquet \u00b7 graph / marked / steps: operator-specific",
          "presentation": 1,
          "presentation_rect": [
            650.0,
            132.0,
            700.0,
            24.0
          ],
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
          "id": "graph_label",
          "maxclass": "comment",
          "patching_rect": [
            16.0,
            136.0,
            42.0,
            20.0
          ],
          "text": "graph",
          "presentation": 1,
          "presentation_rect": [
            16.0,
            136.0,
            42.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "graph",
          "maxclass": "umenu",
          "patching_rect": [
            60.0,
            132.0,
            110.0,
            24.0
          ],
          "presentation": 1,
          "presentation_rect": [
            60.0,
            132.0,
            110.0,
            24.0
          ],
          "items": [
            "cycle",
            ",",
            "path",
            ",",
            "complete"
          ],
          "varname": "representation_graph",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "normalized_label",
          "maxclass": "comment",
          "patching_rect": [
            180.0,
            136.0,
            76.0,
            20.0
          ],
          "text": "normalized",
          "presentation": 1,
          "presentation_rect": [
            180.0,
            136.0,
            76.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "normalized",
          "maxclass": "toggle",
          "patching_rect": [
            258.0,
            132.0,
            24.0,
            24.0
          ],
          "presentation": 1,
          "presentation_rect": [
            258.0,
            132.0,
            24.0,
            24.0
          ],
          "varname": "representation_normalized_graph",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "marked_label",
          "maxclass": "comment",
          "patching_rect": [
            300.0,
            136.0,
            52.0,
            20.0
          ],
          "text": "marked",
          "presentation": 1,
          "presentation_rect": [
            300.0,
            136.0,
            52.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "marked",
          "maxclass": "number",
          "patching_rect": [
            354.0,
            132.0,
            54.0,
            24.0
          ],
          "presentation": 1,
          "presentation_rect": [
            354.0,
            132.0,
            54.0,
            24.0
          ],
          "minimum": 0,
          "maximum": 15,
          "varname": "representation_marked_state",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "steps_label",
          "maxclass": "comment",
          "patching_rect": [
            426.0,
            136.0,
            40.0,
            20.0
          ],
          "text": "steps",
          "presentation": 1,
          "presentation_rect": [
            426.0,
            136.0,
            40.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "steps",
          "maxclass": "number",
          "patching_rect": [
            468.0,
            132.0,
            54.0,
            24.0
          ],
          "presentation": 1,
          "presentation_rect": [
            468.0,
            132.0,
            54.0,
            24.0
          ],
          "minimum": 0,
          "varname": "representation_steps",
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "pak",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            220.0,
            680.0,
            24.0
          ],
          "text": "pak i s f f f f s s i s i s i i i"
        }
      },
      {
        "box": {
          "id": "speedlim",
          "maxclass": "newobj",
          "patching_rect": [
            500.0,
            220.0,
            90.0,
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
            610.0,
            220.0,
            240.0,
            24.0
          ],
          "text": "o.pack /qmw/v5/transform/preview"
        }
      },
      {
        "box": {
          "id": "commit_store",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            255.0,
            58.0,
            24.0
          ],
          "text": "zl reg"
        }
      },
      {
        "box": {
          "id": "commit_pack",
          "maxclass": "newobj",
          "patching_rect": [
            100.0,
            255.0,
            240.0,
            24.0
          ],
          "text": "o.pack /qmw/v5/transform/commit"
        }
      },
      {
        "box": {
          "id": "reset_pack",
          "maxclass": "newobj",
          "patching_rect": [
            360.0,
            255.0,
            230.0,
            24.0
          ],
          "text": "o.pack /qmw/v5/transform/reset_tracking"
        }
      },
      {
        "box": {
          "id": "send",
          "maxclass": "newobj",
          "patching_rect": [
            890.0,
            220.0,
            170.0,
            24.0
          ],
          "text": "udpsend 127.0.0.1 7445"
        }
      },
      {
        "box": {
          "id": "autopattr",
          "maxclass": "newobj",
          "patching_rect": [
            650.0,
            255.0,
            70.0,
            24.0
          ],
          "text": "autopattr"
        }
      },
      {
        "box": {
          "id": "presets",
          "maxclass": "newobj",
          "patching_rect": [
            740.0,
            255.0,
            300.0,
            24.0
          ],
          "text": "pattrstorage qmw_v5_transform_presets @autorestore 0"
        }
      },
      {
        "box": {
          "id": "load_j",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0.7"
        }
      },
      {
        "box": {
          "id": "load_ht",
          "maxclass": "newobj",
          "patching_rect": [
            114.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0.45"
        }
      },
      {
        "box": {
          "id": "load_hl",
          "maxclass": "newobj",
          "patching_rect": [
            208.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0.13"
        }
      },
      {
        "box": {
          "id": "load_time",
          "maxclass": "newobj",
          "patching_rect": [
            302.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 1."
        }
      },
      {
        "box": {
          "id": "load_transform",
          "maxclass": "newobj",
          "patching_rect": [
            396.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 4"
        }
      },
      {
        "box": {
          "id": "load_boundary",
          "maxclass": "newobj",
          "patching_rect": [
            490.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0"
        }
      },
      {
        "box": {
          "id": "load_preset",
          "maxclass": "newobj",
          "patching_rect": [
            584.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0"
        }
      },
      {
        "box": {
          "id": "load_shots",
          "maxclass": "newobj",
          "patching_rect": [
            678.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 256"
        }
      },
      {
        "box": {
          "id": "load_sampling",
          "maxclass": "newobj",
          "patching_rect": [
            772.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0"
        }
      },
      {
        "box": {
          "id": "load_seed",
          "maxclass": "newobj",
          "patching_rect": [
            866.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 23"
        }
      },
      {
        "box": {
          "id": "load_graph",
          "maxclass": "newobj",
          "patching_rect": [
            960.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0"
        }
      },
      {
        "box": {
          "id": "load_normalized",
          "maxclass": "newobj",
          "patching_rect": [
            1054.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0"
        }
      },
      {
        "box": {
          "id": "load_marked",
          "maxclass": "newobj",
          "patching_rect": [
            1148.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 0"
        }
      },
      {
        "box": {
          "id": "load_steps",
          "maxclass": "newobj",
          "patching_rect": [
            1242.0,
            300.0,
            88.0,
            22.0
          ],
          "text": "loadmess 1"
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "transform",
            1
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
            "j",
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
            "ht",
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
            "hl",
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
            "time",
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
            "boundary",
            1
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
            "preset",
            1
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
            "sampling",
            1
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
            "graph",
            1
          ],
          "destination": [
            "pak",
            11
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "normalized",
            0
          ],
          "destination": [
            "pak",
            12
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "marked",
            0
          ],
          "destination": [
            "pak",
            13
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "steps",
            0
          ],
          "destination": [
            "pak",
            14
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
            "store1",
            0
          ],
          "destination": [
            "presets",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "recall1",
            0
          ],
          "destination": [
            "presets",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "write",
            0
          ],
          "destination": [
            "presets",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "read",
            0
          ],
          "destination": [
            "presets",
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
            "load_transform",
            0
          ],
          "destination": [
            "transform",
            0
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
            "boundary",
            0
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
            "preset",
            0
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
            "sampling",
            0
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
      },
      {
        "patchline": {
          "source": [
            "load_graph",
            0
          ],
          "destination": [
            "graph",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_normalized",
            0
          ],
          "destination": [
            "normalized",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_marked",
            0
          ],
          "destination": [
            "marked",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load_steps",
            0
          ],
          "destination": [
            "steps",
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
