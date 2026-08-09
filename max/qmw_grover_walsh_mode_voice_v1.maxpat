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
      100,
      100,
      510,
      300
    ],
    "boxes": [
      {
        "box": {
          "id": "in",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            20,
            42,
            22
          ],
          "text": "in 1",
          "numinlets": 0,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "route",
          "maxclass": "newobj",
          "patching_rect": [
            75,
            20,
            72,
            22
          ],
          "text": "route mode",
          "numinlets": 1,
          "numoutlets": 2
        }
      },
      {
        "box": {
          "id": "unpack",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            60,
            185,
            22
          ],
          "text": "unpack f f f f",
          "numinlets": 1,
          "numoutlets": 4
        }
      },
      {
        "box": {
          "id": "freq_pack",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            98,
            68,
            22
          ],
          "text": "pack f f",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "freq_line",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            132,
            48,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "osc",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            166,
            58,
            22
          ],
          "text": "cycle~",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "gain_pack",
          "maxclass": "newobj",
          "patching_rect": [
            100,
            98,
            68,
            22
          ],
          "text": "pack f f",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "gain_line",
          "maxclass": "newobj",
          "patching_rect": [
            100,
            132,
            48,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "amp",
          "maxclass": "newobj",
          "patching_rect": [
            90,
            166,
            38,
            22
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "pan_l",
          "maxclass": "newobj",
          "patching_rect": [
            180,
            98,
            145,
            22
          ],
          "text": "expr sqrt((1.-$f1)*0.5)",
          "numinlets": 1,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "pan_r",
          "maxclass": "newobj",
          "patching_rect": [
            335,
            98,
            145,
            22
          ],
          "text": "expr sqrt((1.+$f1)*0.5)",
          "numinlets": 1,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "pan_l_pack",
          "maxclass": "newobj",
          "patching_rect": [
            180,
            132,
            68,
            22
          ],
          "text": "pack f f",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "pan_r_pack",
          "maxclass": "newobj",
          "patching_rect": [
            335,
            132,
            68,
            22
          ],
          "text": "pack f f",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "pan_l_line",
          "maxclass": "newobj",
          "patching_rect": [
            180,
            166,
            48,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "pan_r_line",
          "maxclass": "newobj",
          "patching_rect": [
            335,
            166,
            48,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "left",
          "maxclass": "newobj",
          "patching_rect": [
            90,
            205,
            38,
            22
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "right",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            205,
            38,
            22
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "out_l",
          "maxclass": "newobj",
          "patching_rect": [
            90,
            245,
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
            150,
            245,
            52,
            22
          ],
          "text": "out~ 2",
          "numinlets": 1,
          "numoutlets": 0
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
            3
          ],
          "destination": [
            "freq_pack",
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
            "gain_pack",
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
            "pan_l_pack",
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
            "pan_r_pack",
            1
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
            "freq_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq_pack",
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
            "osc",
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
            "gain_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gain_pack",
            0
          ],
          "destination": [
            "gain_line",
            0
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
            "amp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gain_line",
            0
          ],
          "destination": [
            "amp",
            1
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
            "pan_l",
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
            "pan_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan_l",
            0
          ],
          "destination": [
            "pan_l_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan_r",
            0
          ],
          "destination": [
            "pan_r_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan_l_pack",
            0
          ],
          "destination": [
            "pan_l_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan_r_pack",
            0
          ],
          "destination": [
            "pan_r_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp",
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
            "pan_l_line",
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
            "amp",
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
            "pan_r_line",
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
    "autosave": 0
  }
}
