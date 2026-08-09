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
      25.0,
      25.0,
      620.0,
      520.0
    ],
    "boxes": [
      {
        "box": {
          "id": "in",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            30.0,
            35.0,
            22.0
          ],
          "text": "in 1",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "route",
          "maxclass": "newobj",
          "patching_rect": [
            30.0,
            65.0,
            85.0,
            22.0
          ],
          "text": "route params",
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
          "id": "unpack",
          "maxclass": "newobj",
          "patching_rect": [
            95.0,
            100.0,
            145.0,
            22.0
          ],
          "text": "unpack f f f f f f i",
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
          "id": "mtof",
          "maxclass": "newobj",
          "patching_rect": [
            95.0,
            140.0,
            38.0,
            22.0
          ],
          "text": "mtof",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "rate",
          "maxclass": "newobj",
          "patching_rect": [
            95.0,
            175.0,
            45.0,
            22.0
          ],
          "text": "* 0.5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "phasor",
          "maxclass": "newobj",
          "patching_rect": [
            95.0,
            210.0,
            72.0,
            22.0
          ],
          "text": "phasor~ 55",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "wave_recv",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            175.0,
            185.0,
            22.0
          ],
          "text": "r qmb.heisenberg.rings.wave",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "peek",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            210.0,
            390.0,
            22.0
          ],
          "text": "jit.peek~ qmb_heisenberg_rings_wave_a 1 0 @interp 1 @normalize 1",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "amp_target",
          "maxclass": "newobj",
          "patching_rect": [
            330.0,
            65.0,
            78.0,
            22.0
          ],
          "text": "pack f 180.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "amp_sig",
          "maxclass": "newobj",
          "patching_rect": [
            330.0,
            100.0,
            62.0,
            22.0
          ],
          "text": "line~ 0.1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "exc_amp",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            250.0,
            35.0,
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
          "id": "note_msg",
          "maxclass": "newobj",
          "patching_rect": [
            95.0,
            320.0,
            82.0,
            22.0
          ],
          "text": "prepend note",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "model_msg",
          "maxclass": "newobj",
          "patching_rect": [
            400.0,
            100.0,
            90.0,
            22.0
          ],
          "text": "prepend model",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "polyphony",
          "maxclass": "message",
          "patching_rect": [
            500.0,
            100.0,
            78.0,
            22.0
          ],
          "text": "polyphony 1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "load",
          "maxclass": "newobj",
          "patching_rect": [
            500.0,
            65.0,
            60.0,
            22.0
          ],
          "text": "loadbang",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "struct_target",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            285.0,
            78.0,
            22.0
          ],
          "text": "pack f 180.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "bright_target",
          "maxclass": "newobj",
          "patching_rect": [
            275.0,
            285.0,
            78.0,
            22.0
          ],
          "text": "pack f 180.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "damp_target",
          "maxclass": "newobj",
          "patching_rect": [
            360.0,
            285.0,
            78.0,
            22.0
          ],
          "text": "pack f 180.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pos_target",
          "maxclass": "newobj",
          "patching_rect": [
            445.0,
            285.0,
            78.0,
            22.0
          ],
          "text": "pack f 180.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "struct",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            320.0,
            62.0,
            22.0
          ],
          "text": "line~ 0.4",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "bright",
          "maxclass": "newobj",
          "patching_rect": [
            255.0,
            320.0,
            62.0,
            22.0
          ],
          "text": "line~ 0.5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "damp",
          "maxclass": "newobj",
          "patching_rect": [
            320.0,
            320.0,
            62.0,
            22.0
          ],
          "text": "line~ 0.7",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "pos",
          "maxclass": "newobj",
          "patching_rect": [
            385.0,
            320.0,
            62.0,
            22.0
          ],
          "text": "line~ 0.5",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "rings",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            370.0,
            360.0,
            24.0
          ],
          "text": "vb.mi.rngs~",
          "numinlets": 8,
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
            190.0,
            420.0,
            58.0,
            22.0
          ],
          "text": "*~ 0.32",
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
            320.0,
            420.0,
            58.0,
            22.0
          ],
          "text": "*~ 0.32",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "out_l",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            460.0,
            48.0,
            22.0
          ],
          "text": "out~ 1",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "out_r",
          "maxclass": "newobj",
          "patching_rect": [
            320.0,
            460.0,
            48.0,
            22.0
          ],
          "text": "out~ 2",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "in",
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
            "mtof",
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
            "note_msg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mtof",
            0
          ],
          "destination": [
            "rate",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rate",
            0
          ],
          "destination": [
            "phasor",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "wave_recv",
            0
          ],
          "destination": [
            "peek",
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
            "peek",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "peek",
            0
          ],
          "destination": [
            "exc_amp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            5
          ],
          "destination": [
            "amp_target",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp_target",
            0
          ],
          "destination": [
            "amp_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp_sig",
            0
          ],
          "destination": [
            "exc_amp",
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
            "struct_target",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "struct_target",
            0
          ],
          "destination": [
            "struct",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            2
          ],
          "destination": [
            "bright_target",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "bright_target",
            0
          ],
          "destination": [
            "bright",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            3
          ],
          "destination": [
            "damp_target",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "damp_target",
            0
          ],
          "destination": [
            "damp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            4
          ],
          "destination": [
            "pos_target",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pos_target",
            0
          ],
          "destination": [
            "pos",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            6
          ],
          "destination": [
            "model_msg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "polyphony",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "exc_amp",
            0
          ],
          "destination": [
            "rings",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "note_msg",
            0
          ],
          "destination": [
            "rings",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "model_msg",
            0
          ],
          "destination": [
            "rings",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "polyphony",
            0
          ],
          "destination": [
            "rings",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "struct",
            0
          ],
          "destination": [
            "rings",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "bright",
            0
          ],
          "destination": [
            "rings",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "damp",
            0
          ],
          "destination": [
            "rings",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pos",
            0
          ],
          "destination": [
            "rings",
            5
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rings",
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
            "rings",
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
            "out_l",
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
            "out_r",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "vb.mi.rngs~.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
