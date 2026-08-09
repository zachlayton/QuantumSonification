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
      510.0,
      450.0
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
            12.0,
            460.0,
            20.0
          ],
          "text": "QUADRATURE RING VOICE: L=carrier-shift, R=carrier+shift"
        }
      },
      {
        "box": {
          "id": "in",
          "maxclass": "newobj",
          "patching_rect": [
            20.0,
            48.0,
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
            75.0,
            48.0,
            175.0,
            22.0
          ],
          "text": "route carrier shift gain",
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
          "id": "carrier_pack",
          "maxclass": "newobj",
          "patching_rect": [
            75.0,
            84.0,
            72.0,
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
          "id": "carrier_line",
          "maxclass": "newobj",
          "patching_rect": [
            75.0,
            116.0,
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
          "id": "shift_pack",
          "maxclass": "newobj",
          "patching_rect": [
            175.0,
            84.0,
            72.0,
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
          "id": "shift_line",
          "maxclass": "newobj",
          "patching_rect": [
            175.0,
            116.0,
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
          "id": "gain_pack",
          "maxclass": "newobj",
          "patching_rect": [
            275.0,
            84.0,
            72.0,
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
          "id": "gain_line",
          "maxclass": "newobj",
          "patching_rect": [
            275.0,
            116.0,
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
          "id": "carrier_cos",
          "maxclass": "newobj",
          "patching_rect": [
            45.0,
            168.0,
            105.0,
            22.0
          ],
          "text": "cycle~ 220. 0.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "carrier_sin",
          "maxclass": "newobj",
          "patching_rect": [
            165.0,
            168.0,
            112.0,
            22.0
          ],
          "text": "cycle~ 220. 0.25",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "mod_cos",
          "maxclass": "newobj",
          "patching_rect": [
            45.0,
            208.0,
            98.0,
            22.0
          ],
          "text": "cycle~ 40. 0.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "mod_sin",
          "maxclass": "newobj",
          "patching_rect": [
            165.0,
            208.0,
            105.0,
            22.0
          ],
          "text": "cycle~ 40. 0.25",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "ring_cos",
          "maxclass": "newobj",
          "patching_rect": [
            60.0,
            252.0,
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
          "id": "ring_sin",
          "maxclass": "newobj",
          "patching_rect": [
            180.0,
            252.0,
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
          "id": "lower",
          "maxclass": "newobj",
          "patching_rect": [
            80.0,
            296.0,
            36.0,
            22.0
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
          "id": "upper",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            296.0,
            36.0,
            22.0
          ],
          "text": "-~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "lower_gain",
          "maxclass": "newobj",
          "patching_rect": [
            80.0,
            340.0,
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
          "id": "upper_gain",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            340.0,
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
            80.0,
            388.0,
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
            190.0,
            388.0,
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
            "carrier_pack",
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
            "shift_pack",
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
            "gain_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "carrier_pack",
            0
          ],
          "destination": [
            "carrier_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "shift_pack",
            0
          ],
          "destination": [
            "shift_line",
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
            "carrier_line",
            0
          ],
          "destination": [
            "carrier_cos",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "carrier_line",
            0
          ],
          "destination": [
            "carrier_sin",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "shift_line",
            0
          ],
          "destination": [
            "mod_cos",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "shift_line",
            0
          ],
          "destination": [
            "mod_sin",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "carrier_cos",
            0
          ],
          "destination": [
            "ring_cos",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mod_cos",
            0
          ],
          "destination": [
            "ring_cos",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "carrier_sin",
            0
          ],
          "destination": [
            "ring_sin",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mod_sin",
            0
          ],
          "destination": [
            "ring_sin",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ring_cos",
            0
          ],
          "destination": [
            "lower",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ring_sin",
            0
          ],
          "destination": [
            "lower",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ring_cos",
            0
          ],
          "destination": [
            "upper",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ring_sin",
            0
          ],
          "destination": [
            "upper",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "lower",
            0
          ],
          "destination": [
            "lower_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "upper",
            0
          ],
          "destination": [
            "upper_gain",
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
            "lower_gain",
            1
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
            "upper_gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "lower_gain",
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
            "upper_gain",
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
