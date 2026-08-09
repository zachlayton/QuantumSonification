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
      100.0,
      100.0,
      500.0,
      330.0
    ],
    "gridsize": [
      15.0,
      15.0
    ],
    "boxes": [
      {
        "box": {
          "id": "in",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            20.0,
            34.0,
            22.0
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
            70.0,
            20.0,
            185.0,
            22.0
          ],
          "text": "route freq gain pan event",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
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
          "id": "freq_pack",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            65.0,
            72.0,
            22.0
          ],
          "text": "pack f 35",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "freq_line",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            95.0,
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
          "id": "osc",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            130.0,
            70.0,
            22.0
          ],
          "text": "cycle~ 110.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "gain_pack",
          "maxclass": "newobj",
          "patching_rect": [
            120.0,
            65.0,
            72.0,
            22.0
          ],
          "text": "pack f 35",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "gain_line",
          "maxclass": "newobj",
          "patching_rect": [
            120.0,
            95.0,
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
          "id": "gain",
          "maxclass": "newobj",
          "patching_rect": [
            70.0,
            165.0,
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
          "id": "event_message",
          "maxclass": "message",
          "patching_rect": [
            385.0,
            65.0,
            88.0,
            22.0
          ],
          "text": "$1, 0. $2",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "event_line",
          "maxclass": "newobj",
          "patching_rect": [
            385.0,
            95.0,
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
          "id": "event_gain",
          "maxclass": "newobj",
          "patching_rect": [
            70.0,
            195.0,
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
          "id": "pan_l",
          "maxclass": "newobj",
          "patching_rect": [
            215.0,
            65.0,
            150.0,
            22.0
          ],
          "text": "expr sqrt((1.-$f1)*0.5)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pan_r",
          "maxclass": "newobj",
          "patching_rect": [
            215.0,
            95.0,
            150.0,
            22.0
          ],
          "text": "expr sqrt((1.+$f1)*0.5)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pan_l_sig",
          "maxclass": "newobj",
          "patching_rect": [
            215.0,
            130.0,
            45.0,
            22.0
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "pan_r_sig",
          "maxclass": "newobj",
          "patching_rect": [
            285.0,
            130.0,
            45.0,
            22.0
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "left",
          "maxclass": "newobj",
          "patching_rect": [
            45.0,
            235.0,
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
          "id": "right",
          "maxclass": "newobj",
          "patching_rect": [
            115.0,
            235.0,
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
          "id": "out_l",
          "maxclass": "newobj",
          "patching_rect": [
            45.0,
            270.0,
            48.0,
            22.0
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
            115.0,
            270.0,
            48.0,
            22.0
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
            "route",
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
            "gain",
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
            "gain",
            1
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
            "event_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "event_message",
            0
          ],
          "destination": [
            "event_line",
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
            "event_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "event_line",
            0
          ],
          "destination": [
            "event_gain",
            1
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
            "pan_l",
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
            "pan_l_sig",
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
            "pan_r_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "event_gain",
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
            "pan_l_sig",
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
            "event_gain",
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
            "pan_r_sig",
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
