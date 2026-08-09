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
      780.0,
      590.0
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
            25.0,
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
            25.0,
            330.0,
            22.0
          ],
          "text": "route carrier shift side raw index gain pan",
          "numinlets": 1,
          "numoutlets": 8,
          "outlettype": [
            "",
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
          "id": "carrier_pack",
          "maxclass": "newobj",
          "patching_rect": [
            35.0,
            68.0,
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
            35.0,
            98.0,
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
            125.0,
            68.0,
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
            125.0,
            98.0,
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
          "id": "side_l_expr",
          "maxclass": "newobj",
          "patching_rect": [
            215.0,
            68.0,
            125.0,
            22.0
          ],
          "text": "expr (1.-$f1)*0.5",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "side_u_expr",
          "maxclass": "newobj",
          "patching_rect": [
            350.0,
            68.0,
            125.0,
            22.0
          ],
          "text": "expr (1.+$f1)*0.5",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "side_l_pack",
          "maxclass": "newobj",
          "patching_rect": [
            235.0,
            98.0,
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
          "id": "side_u_pack",
          "maxclass": "newobj",
          "patching_rect": [
            370.0,
            98.0,
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
          "id": "side_l_line",
          "maxclass": "newobj",
          "patching_rect": [
            235.0,
            128.0,
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
          "id": "side_u_line",
          "maxclass": "newobj",
          "patching_rect": [
            370.0,
            128.0,
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
            35.0,
            160.0,
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
            150.0,
            160.0,
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
          "id": "mod_cos",
          "maxclass": "newobj",
          "patching_rect": [
            35.0,
            197.0,
            98.0,
            22.0
          ],
          "text": "cycle~ 30. 0.",
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
            150.0,
            197.0,
            105.0,
            22.0
          ],
          "text": "cycle~ 30. 0.25",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "index_cycles",
          "maxclass": "newobj",
          "patching_rect": [
            500.0,
            310.0,
            132.0,
            22.0
          ],
          "text": "expr $f1/6.28318530718",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "index_pack",
          "maxclass": "newobj",
          "patching_rect": [
            500.0,
            340.0,
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
          "id": "index_line",
          "maxclass": "newobj",
          "patching_rect": [
            500.0,
            370.0,
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
          "id": "phase_mod",
          "maxclass": "newobj",
          "patching_rect": [
            285.0,
            197.0,
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
          "id": "phase_quadrature",
          "maxclass": "newobj",
          "patching_rect": [
            335.0,
            197.0,
            72.0,
            22.0
          ],
          "text": "+~ 0.25",
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
            70.0,
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
          "id": "ring_sin",
          "maxclass": "newobj",
          "patching_rect": [
            175.0,
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
          "id": "lower",
          "maxclass": "newobj",
          "patching_rect": [
            75.0,
            273.0,
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
            180.0,
            273.0,
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
          "id": "lower_select",
          "maxclass": "newobj",
          "patching_rect": [
            75.0,
            310.0,
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
          "id": "upper_select",
          "maxclass": "newobj",
          "patching_rect": [
            180.0,
            310.0,
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
          "id": "selected",
          "maxclass": "newobj",
          "patching_rect": [
            130.0,
            347.0,
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
          "id": "raw_ssb_expr",
          "maxclass": "newobj",
          "patching_rect": [
            485.0,
            205.0,
            92.0,
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
          "id": "raw_ssb_pack",
          "maxclass": "newobj",
          "patching_rect": [
            485.0,
            235.0,
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
          "id": "raw_ssb_line",
          "maxclass": "newobj",
          "patching_rect": [
            485.0,
            265.0,
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
          "id": "raw_pack",
          "maxclass": "newobj",
          "patching_rect": [
            590.0,
            235.0,
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
          "id": "raw_line",
          "maxclass": "newobj",
          "patching_rect": [
            590.0,
            265.0,
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
          "id": "raw_scaled",
          "maxclass": "newobj",
          "patching_rect": [
            270.0,
            310.0,
            92.0,
            22.0
          ],
          "text": "*~ 1.41421356",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "ssb_mix",
          "maxclass": "newobj",
          "patching_rect": [
            105.0,
            382.0,
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
          "id": "raw_mix",
          "maxclass": "newobj",
          "patching_rect": [
            210.0,
            382.0,
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
          "id": "topology_mix",
          "maxclass": "newobj",
          "patching_rect": [
            155.0,
            417.0,
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
          "id": "gain_pack",
          "maxclass": "newobj",
          "patching_rect": [
            500.0,
            68.0,
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
            500.0,
            98.0,
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
            155.0,
            452.0,
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
          "id": "pan_l_expr",
          "maxclass": "newobj",
          "patching_rect": [
            590.0,
            68.0,
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
          "id": "pan_r_expr",
          "maxclass": "newobj",
          "patching_rect": [
            590.0,
            98.0,
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
          "id": "pan_l_pack",
          "maxclass": "newobj",
          "patching_rect": [
            590.0,
            128.0,
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
          "id": "pan_r_pack",
          "maxclass": "newobj",
          "patching_rect": [
            670.0,
            128.0,
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
          "id": "pan_l_line",
          "maxclass": "newobj",
          "patching_rect": [
            590.0,
            158.0,
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
          "id": "pan_r_line",
          "maxclass": "newobj",
          "patching_rect": [
            670.0,
            158.0,
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
          "id": "left",
          "maxclass": "newobj",
          "patching_rect": [
            115.0,
            490.0,
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
            205.0,
            490.0,
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
            115.0,
            528.0,
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
            205.0,
            528.0,
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
            "route",
            4
          ],
          "destination": [
            "index_cycles",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "index_cycles",
            0
          ],
          "destination": [
            "index_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "index_pack",
            0
          ],
          "destination": [
            "index_line",
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
            "phase_mod",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "index_line",
            0
          ],
          "destination": [
            "phase_mod",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_mod",
            0
          ],
          "destination": [
            "carrier_cos",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_mod",
            0
          ],
          "destination": [
            "phase_quadrature",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_quadrature",
            0
          ],
          "destination": [
            "carrier_sin",
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
            "side_l_expr",
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
            "side_u_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "side_l_expr",
            0
          ],
          "destination": [
            "side_l_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "side_u_expr",
            0
          ],
          "destination": [
            "side_u_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "side_l_pack",
            0
          ],
          "destination": [
            "side_l_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "side_u_pack",
            0
          ],
          "destination": [
            "side_u_line",
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
            "lower_select",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "side_l_line",
            0
          ],
          "destination": [
            "lower_select",
            1
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
            "upper_select",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "side_u_line",
            0
          ],
          "destination": [
            "upper_select",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "lower_select",
            0
          ],
          "destination": [
            "selected",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "upper_select",
            0
          ],
          "destination": [
            "selected",
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
            "raw_ssb_expr",
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
            "raw_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "raw_ssb_expr",
            0
          ],
          "destination": [
            "raw_ssb_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "raw_ssb_pack",
            0
          ],
          "destination": [
            "raw_ssb_line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "raw_pack",
            0
          ],
          "destination": [
            "raw_line",
            0
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
            "raw_scaled",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "selected",
            0
          ],
          "destination": [
            "ssb_mix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "raw_ssb_line",
            0
          ],
          "destination": [
            "ssb_mix",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "raw_scaled",
            0
          ],
          "destination": [
            "raw_mix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "raw_line",
            0
          ],
          "destination": [
            "raw_mix",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ssb_mix",
            0
          ],
          "destination": [
            "topology_mix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "raw_mix",
            0
          ],
          "destination": [
            "topology_mix",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            5
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
            "topology_mix",
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
            6
          ],
          "destination": [
            "pan_l_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            6
          ],
          "destination": [
            "pan_r_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pan_l_expr",
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
            "pan_r_expr",
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
            "gain",
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
            "gain",
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
