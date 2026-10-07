{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 9,
      "minor": 0,
      "revision": 7,
      "architecture": "x64",
      "modernui": 1
    },
    "classnamespace": "box",
    "rect": [
      0,
      0,
      980,
      670
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            18,
            660,
            30
          ],
          "text": "QMW Poly Harmonic Voice 16 v2 \u2014 bounded quantum tuning",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": [],
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "note-in",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            80,
            35,
            22
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
          "id": "note-label",
          "maxclass": "comment",
          "patching_rect": [
            80,
            81,
            190,
            20
          ],
          "text": "midinote pitch velocity",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "unpack",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            120,
            75,
            22
          ],
          "text": "unpack 0 0",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "int",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "mtof",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            165,
            38,
            22
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
          "id": "freq-pack",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            200,
            80,
            22
          ],
          "text": "pack 0. 12.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "freq-line",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            235,
            42,
            22
          ],
          "text": "line~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "vel-scale",
          "maxclass": "newobj",
          "patching_rect": [
            150,
            165,
            48,
            22
          ],
          "text": "/ 127.",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "attack-in",
          "maxclass": "newobj",
          "patching_rect": [
            330,
            80,
            35,
            22
          ],
          "text": "in 2",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "decay-in",
          "maxclass": "newobj",
          "patching_rect": [
            390,
            80,
            35,
            22
          ],
          "text": "in 3",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "sustain-in",
          "maxclass": "newobj",
          "patching_rect": [
            450,
            80,
            35,
            22
          ],
          "text": "in 4",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "release-in",
          "maxclass": "newobj",
          "patching_rect": [
            510,
            80,
            35,
            22
          ],
          "text": "in 5",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "adsr",
          "maxclass": "newobj",
          "patching_rect": [
            150,
            235,
            158,
            22
          ],
          "text": "adsr~ 18. 140. 0.72 850.",
          "numinlets": 5,
          "numoutlets": 4,
          "outlettype": [
            "signal",
            "signal",
            "signal",
            "list"
          ]
        }
      },
      {
        "box": {
          "id": "field-r",
          "maxclass": "newobj",
          "patching_rect": [
            375,
            165,
            120,
            22
          ],
          "text": "r qmw.v6.field",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "gen",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            320,
            468,
            22
          ],
          "text": "mc.gen~ @gen qmw_density_field_harmonic_modal_resonator16_mc_v4 @chans 16",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "env-mul",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            380,
            56,
            22
          ],
          "text": "mc.*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "norm",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            425,
            75,
            22
          ],
          "text": "mc.*~ 0.32",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "out",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            480,
            145,
            22
          ],
          "text": "mc.out~ 1 @chans 16",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "thispoly",
          "maxclass": "newobj",
          "patching_rect": [
            330,
            235,
            135,
            22
          ],
          "text": "thispoly~ @automute 1",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "int",
            "int",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "note-comment",
          "maxclass": "comment",
          "patching_rect": [
            35,
            535,
            720,
            40
          ],
          "text": "mcs.poly~ sums matching harmonic lanes across voices. The shared conductor field shapes timbre; MIDI pitch and ADSR remain independent per note.",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": [],
          "linecount": 2
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "note-in",
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
            "mtof",
            0
          ],
          "destination": [
            "freq-pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq-pack",
            0
          ],
          "destination": [
            "freq-line",
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
            "vel-scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "vel-scale",
            0
          ],
          "destination": [
            "adsr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "attack-in",
            0
          ],
          "destination": [
            "adsr",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "decay-in",
            0
          ],
          "destination": [
            "adsr",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "sustain-in",
            0
          ],
          "destination": [
            "adsr",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "release-in",
            0
          ],
          "destination": [
            "adsr",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq-line",
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
            "field-r",
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
            "env-mul",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adsr",
            0
          ],
          "destination": [
            "env-mul",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adsr",
            0
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
            "env-mul",
            0
          ],
          "destination": [
            "norm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "norm",
            0
          ],
          "destination": [
            "out",
            0
          ]
        }
      }
    ]
  }
}
