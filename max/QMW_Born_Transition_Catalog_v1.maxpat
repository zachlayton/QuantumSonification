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
      120,
      80,
      1000,
      850
    ],
    "gridsize": [
      15,
      15
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            15,
            650,
            24
          ],
          "text": "QMW Born Transition Catalog \u2014 persistent comparison view",
          "fontsize": 16
        }
      },
      {
        "box": {
          "id": "help",
          "maxclass": "comment",
          "patching_rect": [
            25,
            43,
            760,
            34
          ],
          "text": "Connect the outlet after OSC-route /born to this inlet. Table values are exact; aligned sliders show normalized log-frequency, probability, and duration."
        }
      },
      {
        "box": {
          "id": "in",
          "maxclass": "inlet",
          "patching_rect": [
            25,
            88,
            30,
            30
          ],
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
            92,
            255,
            22
          ],
          "text": "OSC-route /catalog /active_index /transition",
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
          "id": "catalog_route",
          "maxclass": "newobj",
          "patching_rect": [
            75,
            126,
            190,
            22
          ],
          "text": "OSC-route /begin /row /end",
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
          "id": "begin",
          "maxclass": "newobj",
          "patching_rect": [
            75,
            160,
            84,
            22
          ],
          "text": "prepend begin",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "row",
          "maxclass": "newobj",
          "patching_rect": [
            170,
            160,
            76,
            22
          ],
          "text": "prepend row",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "end",
          "maxclass": "newobj",
          "patching_rect": [
            257,
            160,
            78,
            22
          ],
          "text": "prepend end",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "active",
          "maxclass": "newobj",
          "patching_rect": [
            345,
            126,
            90,
            22
          ],
          "text": "prepend active",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "js",
          "maxclass": "newobj",
          "patching_rect": [
            75,
            198,
            235,
            22
          ],
          "text": "js qmw_born_transition_catalog_v1.js",
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
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            325,
            198,
            460,
            22
          ],
          "text": "waiting for catalog...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "table",
          "maxclass": "jit.cellblock",
          "patching_rect": [
            25,
            240,
            930,
            330
          ],
          "cols": 9,
          "rows": 15,
          "colhead": 0,
          "rowhead": 0,
          "numinlets": 2,
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
          "id": "freq_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            588,
            145,
            20
          ],
          "text": "log audio frequency"
        }
      },
      {
        "box": {
          "id": "freq",
          "maxclass": "multislider",
          "patching_rect": [
            175,
            584,
            780,
            42
          ],
          "size": 14,
          "setminmax": [
            0.0,
            1.0
          ],
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
          "id": "prob_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            640,
            145,
            20
          ],
          "text": "relative probability"
        }
      },
      {
        "box": {
          "id": "prob",
          "maxclass": "multislider",
          "patching_rect": [
            175,
            636,
            780,
            42
          ],
          "size": 14,
          "setminmax": [
            0.0,
            1.0
          ],
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
          "id": "dur_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            692,
            145,
            20
          ],
          "text": "relative duration"
        }
      },
      {
        "box": {
          "id": "dur",
          "maxclass": "multislider",
          "patching_rect": [
            175,
            688,
            780,
            42
          ],
          "size": 14,
          "setminmax": [
            0.0,
            1.0
          ],
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
          "id": "menu_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            757,
            115,
            20
          ],
          "text": "isotope preset"
        }
      },
      {
        "box": {
          "id": "menu",
          "maxclass": "umenu",
          "patching_rect": [
            140,
            754,
            170,
            22
          ],
          "items": [
            "H-1",
            ",",
            "H-2",
            ",",
            "H-3",
            ",",
            "He-3+",
            ",",
            "He-4+",
            ",",
            "Li-6++",
            ",",
            "Li-7++"
          ],
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "int",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_species",
          "maxclass": "newobj",
          "patching_rect": [
            330,
            754,
            240,
            22
          ],
          "text": "prepend /qmw/excitation/born/species",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "send",
          "maxclass": "newobj",
          "patching_rect": [
            590,
            754,
            155,
            22
          ],
          "text": "udpsend 127.0.0.1 7402",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "isotope_note",
          "maxclass": "comment",
          "patching_rect": [
            25,
            790,
            900,
            34
          ],
          "text": "H-3 is radioactive, but this engine models electronic E1 transitions only\u2014not beta decay. Higher-Z ions are the presets with substantially faster electronic dynamics."
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
            "catalog_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "catalog_route",
            0
          ],
          "destination": [
            "begin",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "catalog_route",
            1
          ],
          "destination": [
            "row",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "catalog_route",
            2
          ],
          "destination": [
            "end",
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
            "active",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "begin",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "row",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "end",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "active",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            0
          ],
          "destination": [
            "table",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            1
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
            "js",
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
            "js",
            3
          ],
          "destination": [
            "dur",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            4
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
            "menu",
            1
          ],
          "destination": [
            "prepend_species",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_species",
            0
          ],
          "destination": [
            "send",
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
        "name": "qmw_born_transition_catalog_v1.js",
        "type": "TEXT"
      }
    ],
    "autosave": 0
  }
}
