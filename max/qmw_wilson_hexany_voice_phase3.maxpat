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
      80,
      80,
      780,
      470
    ],
    "boxes": [
      {
        "box": {
          "id": "in",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            20,
            40,
            22
          ],
          "text": "in 1",
          "numinlets": 0,
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
            75,
            20,
            112,
            22
          ],
          "text": "route accent mute",
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
          "id": "unpack",
          "maxclass": "newobj",
          "patching_rect": [
            210,
            20,
            205,
            22
          ],
          "text": "unpack f f f f f",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
            "float",
            "float",
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "freq_msg",
          "maxclass": "message",
          "patching_rect": [
            25,
            75,
            62,
            22
          ],
          "text": "$1 35"
        }
      },
      {
        "box": {
          "id": "freq_line",
          "maxclass": "newobj",
          "patching_rect": [
            95,
            75,
            45,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "fund",
          "maxclass": "newobj",
          "patching_rect": [
            150,
            75,
            50,
            22
          ],
          "text": "cycle~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "double",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            110,
            42,
            22
          ],
          "text": "* 2."
        }
      },
      {
        "box": {
          "id": "double_msg",
          "maxclass": "message",
          "patching_rect": [
            75,
            110,
            62,
            22
          ],
          "text": "$1 35"
        }
      },
      {
        "box": {
          "id": "double_line",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            110,
            45,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "partial",
          "maxclass": "newobj",
          "patching_rect": [
            200,
            110,
            50,
            22
          ],
          "text": "cycle~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "phase_norm",
          "maxclass": "newobj",
          "patching_rect": [
            270,
            110,
            210,
            22
          ],
          "text": "expr (($f1 / 6.2831853) + 1.) % 1."
        }
      },
      {
        "box": {
          "id": "phase_msg",
          "maxclass": "message",
          "patching_rect": [
            490,
            110,
            62,
            22
          ],
          "text": "$1 60"
        }
      },
      {
        "box": {
          "id": "phase_line",
          "maxclass": "newobj",
          "patching_rect": [
            560,
            110,
            45,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "coh_amp",
          "maxclass": "newobj",
          "patching_rect": [
            270,
            145,
            150,
            22
          ],
          "text": "expr 0.06 + 0.24*$f1"
        }
      },
      {
        "box": {
          "id": "coh_msg",
          "maxclass": "message",
          "patching_rect": [
            430,
            145,
            70,
            22
          ],
          "text": "$1 100"
        }
      },
      {
        "box": {
          "id": "coh_line",
          "maxclass": "newobj",
          "patching_rect": [
            510,
            145,
            45,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "partial_amp",
          "maxclass": "newobj",
          "patching_rect": [
            200,
            180,
            36,
            22
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
          "id": "mix",
          "maxclass": "newobj",
          "patching_rect": [
            150,
            215,
            36,
            22
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
          "id": "activation_clip",
          "maxclass": "newobj",
          "patching_rect": [
            270,
            215,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "activation_sqrt",
          "maxclass": "newobj",
          "patching_rect": [
            350,
            215,
            78,
            22
          ],
          "text": "expr sqrt($f1)"
        }
      },
      {
        "box": {
          "id": "activation_msg",
          "maxclass": "message",
          "patching_rect": [
            438,
            215,
            70,
            22
          ],
          "text": "$1 80"
        }
      },
      {
        "box": {
          "id": "activation_line",
          "maxclass": "newobj",
          "patching_rect": [
            518,
            215,
            45,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "accent_msg",
          "maxclass": "message",
          "patching_rect": [
            25,
            250,
            105,
            22
          ],
          "text": "$1 3, 0 450 3"
        }
      },
      {
        "box": {
          "id": "accent_line",
          "maxclass": "newobj",
          "patching_rect": [
            140,
            250,
            45,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "env_add",
          "maxclass": "newobj",
          "patching_rect": [
            200,
            250,
            36,
            22
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
          "id": "env_clip",
          "maxclass": "newobj",
          "patching_rect": [
            245,
            250,
            72,
            22
          ],
          "text": "clip~ 0. 1."
        }
      },
      {
        "box": {
          "id": "voiced",
          "maxclass": "newobj",
          "patching_rect": [
            150,
            285,
            36,
            22
          ],
          "text": "*~ 0.12",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "pan_msg",
          "maxclass": "message",
          "patching_rect": [
            340,
            285,
            72,
            22
          ],
          "text": "$1 120"
        }
      },
      {
        "box": {
          "id": "pan_line",
          "maxclass": "newobj",
          "patching_rect": [
            422,
            285,
            45,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "left_gain",
          "maxclass": "newobj",
          "patching_rect": [
            340,
            320,
            190,
            22
          ],
          "text": "expr~ sqrt((1.-$v1)*0.5)"
        }
      },
      {
        "box": {
          "id": "right_gain",
          "maxclass": "newobj",
          "patching_rect": [
            540,
            320,
            190,
            22
          ],
          "text": "expr~ sqrt((1.+$v1)*0.5)"
        }
      },
      {
        "box": {
          "id": "left",
          "maxclass": "newobj",
          "patching_rect": [
            150,
            355,
            36,
            22
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
          "id": "right",
          "maxclass": "newobj",
          "patching_rect": [
            210,
            355,
            36,
            22
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
          "id": "out_l",
          "maxclass": "newobj",
          "patching_rect": [
            150,
            400,
            52,
            22
          ],
          "text": "out~ 1",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "out_r",
          "maxclass": "newobj",
          "patching_rect": [
            210,
            400,
            52,
            22
          ],
          "text": "out~ 2",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "thispoly",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            400,
            62,
            22
          ],
          "text": "thispoly~",
          "numinlets": 2,
          "numoutlets": 3,
          "outlettype": [
            "int",
            "int",
            "int"
          ]
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
            2
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
            "route",
            0
          ],
          "destination": [
            "accent_msg",
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
            "thispoly",
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
            "freq_msg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq_msg",
            0
          ],
          "destination": [
            "freq_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq_line",
            0
          ],
          "destination": [
            "fund",
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
            "double",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "double",
            0
          ],
          "destination": [
            "double_msg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "double_msg",
            0
          ],
          "destination": [
            "double_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "double_line",
            0
          ],
          "destination": [
            "partial",
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
            "phase_norm",
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
            "phase_msg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_msg",
            0
          ],
          "destination": [
            "phase_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_line",
            0
          ],
          "destination": [
            "partial",
            1
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
            "coh_amp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "coh_amp",
            0
          ],
          "destination": [
            "coh_msg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "coh_msg",
            0
          ],
          "destination": [
            "coh_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "partial",
            0
          ],
          "destination": [
            "partial_amp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "coh_line",
            0
          ],
          "destination": [
            "partial_amp",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fund",
            0
          ],
          "destination": [
            "mix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "partial_amp",
            0
          ],
          "destination": [
            "mix",
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
            "activation_clip",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "activation_clip",
            0
          ],
          "destination": [
            "activation_sqrt",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "activation_sqrt",
            0
          ],
          "destination": [
            "activation_msg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "activation_msg",
            0
          ],
          "destination": [
            "activation_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "accent_msg",
            0
          ],
          "destination": [
            "accent_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "activation_line",
            0
          ],
          "destination": [
            "env_add",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "accent_line",
            0
          ],
          "destination": [
            "env_add",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env_add",
            0
          ],
          "destination": [
            "env_clip",
            0
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
            "voiced",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env_clip",
            0
          ],
          "destination": [
            "voiced",
            1
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
            "pan_msg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan_msg",
            0
          ],
          "destination": [
            "pan_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan_line",
            0
          ],
          "destination": [
            "left_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan_line",
            0
          ],
          "destination": [
            "right_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "voiced",
            0
          ],
          "destination": [
            "left",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "left_gain",
            0
          ],
          "destination": [
            "left",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "voiced",
            0
          ],
          "destination": [
            "right",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "right_gain",
            0
          ],
          "destination": [
            "right",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "left",
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
            "right",
            0
          ],
          "destination": [
            "out_r",
            0
          ]
        }
      }
    ],
    "dependency_cache": [],
    "autosave": 0
  }
}
