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
      980.0,
      620.0
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
          "text": "Independent reduced-qubit GenExpr harmonic resonator (#1 bus)",
          "patching_rect": [
            30.0,
            20.0,
            420.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "r_bloch",
          "maxclass": "newobj",
          "text": "r #1",
          "patching_rect": [
            30.0,
            65.0,
            120.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "unpack",
          "maxclass": "newobj",
          "text": "unpack f f f",
          "patching_rect": [
            30.0,
            100.0,
            85.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "px",
          "maxclass": "newobj",
          "text": "prepend x",
          "patching_rect": [
            30.0,
            135.0,
            72.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "py",
          "maxclass": "newobj",
          "text": "prepend y",
          "patching_rect": [
            115.0,
            135.0,
            72.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "pz",
          "maxclass": "newobj",
          "text": "prepend z",
          "patching_rect": [
            200.0,
            135.0,
            72.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "r_purity",
          "maxclass": "newobj",
          "text": "r qmw.global.purity",
          "patching_rect": [
            320.0,
            65.0,
            135.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "r_entropy",
          "maxclass": "newobj",
          "text": "r qmw.global.entropy",
          "patching_rect": [
            470.0,
            65.0,
            140.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "r_coherence",
          "maxclass": "newobj",
          "text": "r qmw.global.coherence",
          "patching_rect": [
            625.0,
            65.0,
            155.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "r_level",
          "maxclass": "newobj",
          "text": "r qmw.local.voice.level",
          "patching_rect": [
            795.0,
            65.0,
            155.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "ppurity",
          "maxclass": "newobj",
          "text": "prepend purity",
          "patching_rect": [
            320.0,
            100.0,
            100.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "pentropy",
          "maxclass": "newobj",
          "text": "prepend entropy",
          "patching_rect": [
            470.0,
            100.0,
            105.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "pcoherence",
          "maxclass": "newobj",
          "text": "prepend coherence",
          "patching_rect": [
            625.0,
            100.0,
            125.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "pamp",
          "maxclass": "newobj",
          "text": "prepend amp",
          "patching_rect": [
            795.0,
            100.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "base",
          "maxclass": "newobj",
          "text": "loadmess #2",
          "patching_rect": [
            320.0,
            135.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "pbase",
          "maxclass": "newobj",
          "text": "prepend basefreq",
          "patching_rect": [
            420.0,
            135.0,
            115.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "r_basefreq",
          "maxclass": "newobj",
          "text": "r #3",
          "patching_rect": [
            550.0,
            135.0,
            140.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "gen",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            30.0,
            205.0,
            220.0,
            22.0
          ],
          "text": "gen~ qmw_qubit_resonator"
        }
      },
      {
        "box": {
          "id": "out",
          "maxclass": "outlet",
          "index": 1,
          "comment": "qubit resonator signal",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            520.0,
            30.0,
            30.0
          ]
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "r_bloch",
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
            "px",
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
            "py",
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
            "pz",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "px",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "py",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pz",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "r_purity",
            0
          ],
          "destination": [
            "ppurity",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "r_entropy",
            0
          ],
          "destination": [
            "pentropy",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "r_coherence",
            0
          ],
          "destination": [
            "pcoherence",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "r_level",
            0
          ],
          "destination": [
            "pamp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ppurity",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pentropy",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pcoherence",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pamp",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "base",
            0
          ],
          "destination": [
            "pbase",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "r_basefreq",
            0
          ],
          "destination": [
            "pbase",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pbase",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gen",
            0
          ],
          "destination": [
            "out",
            0
          ]
        }
      }
    ],
    "autosave": 0
  }
}
