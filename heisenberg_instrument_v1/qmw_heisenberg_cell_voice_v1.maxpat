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
      120.0,
      120.0,
      760.0,
      340.0
    ],
    "boxes": [
      {
        "box": {
          "id": "in",
          "maxclass": "newobj",
          "patching_rect": [
            28.0,
            27.0,
            42.0,
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
            78.0,
            27.0,
            292.0,
            22.0
          ],
          "text": "route frequency amplitude phase pan decay",
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
          "id": "freq",
          "maxclass": "flonum",
          "patching_rect": [
            78.0,
            72.0,
            72.0,
            22.0
          ],
          "valueof": 55.0
        }
      },
      {
        "box": {
          "id": "osc",
          "maxclass": "newobj",
          "patching_rect": [
            78.0,
            112.0,
            76.0,
            22.0
          ],
          "text": "cycle~ 55.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "amp_pack",
          "maxclass": "newobj",
          "patching_rect": [
            168.0,
            72.0,
            94.0,
            22.0
          ],
          "text": "pack 0. 80.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "amp_line",
          "maxclass": "newobj",
          "patching_rect": [
            168.0,
            112.0,
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
          "id": "phase_expr",
          "maxclass": "newobj",
          "patching_rect": [
            278.0,
            72.0,
            190.0,
            22.0
          ],
          "text": "expr ($f1 + 3.14159265) / 6.2831853",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "phase_sig",
          "maxclass": "newobj",
          "patching_rect": [
            278.0,
            112.0,
            42.0,
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
          "id": "multiply",
          "maxclass": "newobj",
          "patching_rect": [
            78.0,
            160.0,
            42.0,
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
            344.0,
            112.0,
            170.0,
            22.0
          ],
          "text": "expr sqrt((1.-$f1)*0.5)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "pan_r",
          "maxclass": "newobj",
          "patching_rect": [
            526.0,
            112.0,
            170.0,
            22.0
          ],
          "text": "expr sqrt((1.+$f1)*0.5)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "pan_l_pack",
          "maxclass": "newobj",
          "patching_rect": [
            344.0,
            151.0,
            90.0,
            22.0
          ],
          "text": "pack 0. 40.",
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
            526.0,
            151.0,
            90.0,
            22.0
          ],
          "text": "pack 0. 40.",
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
            344.0,
            189.0,
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
            526.0,
            189.0,
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
            116.0,
            230.0,
            42.0,
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
            190.0,
            230.0,
            42.0,
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
            116.0,
            280.0,
            52.0,
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
            280.0,
            52.0,
            22.0
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
            650.0,
            27.0,
            70.0,
            22.0
          ],
          "text": "thispoly~",
          "numinlets": 2,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
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
            0
          ],
          "destination": [
            "freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq",
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
            "amp_pack",
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
            "amp_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp_pack",
            0
          ],
          "destination": [
            "amp_line",
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
            "phase_expr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_expr",
            0
          ],
          "destination": [
            "phase_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase_sig",
            0
          ],
          "destination": [
            "osc",
            1
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
            "multiply",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp_line",
            0
          ],
          "destination": [
            "multiply",
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
            "pan_l",
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
            "multiply",
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
            "multiply",
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
