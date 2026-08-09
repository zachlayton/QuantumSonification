{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 9,
      "minor": 0,
      "revision": 8,
      "architecture": "x64",
      "modernui": 1
    },
    "classnamespace": "box",
    "rect": [
      100,
      100,
      560,
      620
    ],
    "openinpresentation": 1,
    "default_fontsize": 12,
    "default_fontface": 0,
    "default_fontname": "Arial",
    "gridonopen": 1,
    "gridsize": [
      15,
      15
    ],
    "boxes": [
      {
        "box": {
          "id": "monitor-1",
          "maxclass": "comment",
          "patching_rect": [
            10,
            8,
            310,
            22
          ],
          "text": "LIVE FOUR-QUBIT BLOCH STATE",
          "fontsize": 14,
          "fontface": 1,
          "presentation": 1,
          "presentation_rect": [
            10,
            8,
            310,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-2",
          "maxclass": "comment",
          "patching_rect": [
            10,
            34,
            42,
            20
          ],
          "text": "qubit",
          "presentation": 1,
          "presentation_rect": [
            10,
            34,
            42,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-3",
          "maxclass": "comment",
          "patching_rect": [
            56,
            34,
            58,
            20
          ],
          "text": "θ°",
          "presentation": 1,
          "presentation_rect": [
            56,
            34,
            58,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-4",
          "maxclass": "comment",
          "patching_rect": [
            112,
            34,
            58,
            20
          ],
          "text": "φ°",
          "presentation": 1,
          "presentation_rect": [
            112,
            34,
            58,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-5",
          "maxclass": "comment",
          "patching_rect": [
            168,
            34,
            58,
            20
          ],
          "text": "x",
          "presentation": 1,
          "presentation_rect": [
            168,
            34,
            58,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-6",
          "maxclass": "comment",
          "patching_rect": [
            224,
            34,
            58,
            20
          ],
          "text": "y",
          "presentation": 1,
          "presentation_rect": [
            224,
            34,
            58,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-7",
          "maxclass": "comment",
          "patching_rect": [
            280,
            34,
            58,
            20
          ],
          "text": "z",
          "presentation": 1,
          "presentation_rect": [
            280,
            34,
            58,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-8",
          "maxclass": "comment",
          "patching_rect": [
            10,
            60,
            38,
            20
          ],
          "text": "q0",
          "presentation": 1,
          "presentation_rect": [
            10,
            60,
            38,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-9",
          "maxclass": "flonum",
          "patching_rect": [
            56,
            58,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            56,
            58,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-10",
          "maxclass": "flonum",
          "patching_rect": [
            112,
            58,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            112,
            58,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-11",
          "maxclass": "flonum",
          "patching_rect": [
            168,
            58,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            168,
            58,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-12",
          "maxclass": "flonum",
          "patching_rect": [
            224,
            58,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            224,
            58,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-13",
          "maxclass": "flonum",
          "patching_rect": [
            280,
            58,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            280,
            58,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-14",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            230,
            110,
            22
          ],
          "text": "r qmw.q0.bloch",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-15",
          "maxclass": "newobj",
          "patching_rect": [
            130,
            230,
            58,
            22
          ],
          "text": "t l l l",
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
          "id": "monitor-16",
          "maxclass": "newobj",
          "patching_rect": [
            198,
            230,
            88,
            22
          ],
          "text": "unpack f f f",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "monitor-17",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            262,
            430,
            22
          ],
          "text": "expr acos(max(-1.\\,min(1.\\,$f3/max(sqrt($f1*$f1+$f2*$f2+$f3*$f3)\\,0.000001))))*57.29578",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-18",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            288,
            190,
            22
          ],
          "text": "expr atan2($f2\\,$f1)*57.29578",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-19",
          "maxclass": "comment",
          "patching_rect": [
            10,
            94,
            38,
            20
          ],
          "text": "q1",
          "presentation": 1,
          "presentation_rect": [
            10,
            94,
            38,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-20",
          "maxclass": "flonum",
          "patching_rect": [
            56,
            92,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            56,
            92,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-21",
          "maxclass": "flonum",
          "patching_rect": [
            112,
            92,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            112,
            92,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-22",
          "maxclass": "flonum",
          "patching_rect": [
            168,
            92,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            168,
            92,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-23",
          "maxclass": "flonum",
          "patching_rect": [
            224,
            92,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            224,
            92,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-24",
          "maxclass": "flonum",
          "patching_rect": [
            280,
            92,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            280,
            92,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-25",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            320,
            110,
            22
          ],
          "text": "r qmw.q1.bloch",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-26",
          "maxclass": "newobj",
          "patching_rect": [
            130,
            320,
            58,
            22
          ],
          "text": "t l l l",
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
          "id": "monitor-27",
          "maxclass": "newobj",
          "patching_rect": [
            198,
            320,
            88,
            22
          ],
          "text": "unpack f f f",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "monitor-28",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            352,
            430,
            22
          ],
          "text": "expr acos(max(-1.\\,min(1.\\,$f3/max(sqrt($f1*$f1+$f2*$f2+$f3*$f3)\\,0.000001))))*57.29578",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-29",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            378,
            190,
            22
          ],
          "text": "expr atan2($f2\\,$f1)*57.29578",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-30",
          "maxclass": "comment",
          "patching_rect": [
            10,
            128,
            38,
            20
          ],
          "text": "q2",
          "presentation": 1,
          "presentation_rect": [
            10,
            128,
            38,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-31",
          "maxclass": "flonum",
          "patching_rect": [
            56,
            126,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            56,
            126,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-32",
          "maxclass": "flonum",
          "patching_rect": [
            112,
            126,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            112,
            126,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-33",
          "maxclass": "flonum",
          "patching_rect": [
            168,
            126,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            168,
            126,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-34",
          "maxclass": "flonum",
          "patching_rect": [
            224,
            126,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            224,
            126,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-35",
          "maxclass": "flonum",
          "patching_rect": [
            280,
            126,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            280,
            126,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-36",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            410,
            110,
            22
          ],
          "text": "r qmw.q2.bloch",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-37",
          "maxclass": "newobj",
          "patching_rect": [
            130,
            410,
            58,
            22
          ],
          "text": "t l l l",
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
          "id": "monitor-38",
          "maxclass": "newobj",
          "patching_rect": [
            198,
            410,
            88,
            22
          ],
          "text": "unpack f f f",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "monitor-39",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            442,
            430,
            22
          ],
          "text": "expr acos(max(-1.\\,min(1.\\,$f3/max(sqrt($f1*$f1+$f2*$f2+$f3*$f3)\\,0.000001))))*57.29578",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-40",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            468,
            190,
            22
          ],
          "text": "expr atan2($f2\\,$f1)*57.29578",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-41",
          "maxclass": "comment",
          "patching_rect": [
            10,
            162,
            38,
            20
          ],
          "text": "q3",
          "presentation": 1,
          "presentation_rect": [
            10,
            162,
            38,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-42",
          "maxclass": "flonum",
          "patching_rect": [
            56,
            160,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            56,
            160,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-43",
          "maxclass": "flonum",
          "patching_rect": [
            112,
            160,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            112,
            160,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-44",
          "maxclass": "flonum",
          "patching_rect": [
            168,
            160,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            168,
            160,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-45",
          "maxclass": "flonum",
          "patching_rect": [
            224,
            160,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            224,
            160,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-46",
          "maxclass": "flonum",
          "patching_rect": [
            280,
            160,
            52,
            22
          ],
          "format": 6,
          "parameter_enable": 0,
          "presentation": 1,
          "presentation_rect": [
            280,
            160,
            52,
            22
          ]
        }
      },
      {
        "box": {
          "id": "monitor-47",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            500,
            110,
            22
          ],
          "text": "r qmw.q3.bloch",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-48",
          "maxclass": "newobj",
          "patching_rect": [
            130,
            500,
            58,
            22
          ],
          "text": "t l l l",
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
          "id": "monitor-49",
          "maxclass": "newobj",
          "patching_rect": [
            198,
            500,
            88,
            22
          ],
          "text": "unpack f f f",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "monitor-50",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            532,
            430,
            22
          ],
          "text": "expr acos(max(-1.\\,min(1.\\,$f3/max(sqrt($f1*$f1+$f2*$f2+$f3*$f3)\\,0.000001))))*57.29578",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-51",
          "maxclass": "newobj",
          "patching_rect": [
            10,
            558,
            190,
            22
          ],
          "text": "expr atan2($f2\\,$f1)*57.29578",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "monitor-52",
          "maxclass": "comment",
          "patching_rect": [
            10,
            198,
            310,
            20
          ],
          "text": "θ = acos(z/r)   ·   φ = atan2(y,x)",
          "presentation": 1,
          "presentation_rect": [
            10,
            198,
            310,
            20
          ]
        }
      },
      {
        "box": {
          "id": "monitor-udp-pack",
          "maxclass": "newobj",
          "numinlets": 20,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            300,
            560,
            255,
            22
          ],
          "text": "pak 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0."
        }
      },
      {
        "box": {
          "id": "monitor-udp-speedlim",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            300,
            590,
            75,
            22
          ],
          "text": "speedlim 10"
        }
      },
      {
        "box": {
          "id": "monitor-udp-send",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            385,
            590,
            205,
            22
          ],
          "text": "udpsend 129.161.12.215 9000"
        }
      },
      {
        "box": {
          "id": "monitor-udp-label",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            10,
            220,
            325,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            10,
            220,
            325,
            20
          ],
          "text": "UDP → 129.161.12.215:9000 · q0–q3 · θ φ x y z"
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "monitor-14",
            0
          ],
          "destination": [
            "monitor-15",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-15",
            0
          ],
          "destination": [
            "monitor-16",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-15",
            1
          ],
          "destination": [
            "monitor-17",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-15",
            2
          ],
          "destination": [
            "monitor-18",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-17",
            0
          ],
          "destination": [
            "monitor-9",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-18",
            0
          ],
          "destination": [
            "monitor-10",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-16",
            0
          ],
          "destination": [
            "monitor-11",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-16",
            1
          ],
          "destination": [
            "monitor-12",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-16",
            2
          ],
          "destination": [
            "monitor-13",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-25",
            0
          ],
          "destination": [
            "monitor-26",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-26",
            0
          ],
          "destination": [
            "monitor-27",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-26",
            1
          ],
          "destination": [
            "monitor-28",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-26",
            2
          ],
          "destination": [
            "monitor-29",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-28",
            0
          ],
          "destination": [
            "monitor-20",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-29",
            0
          ],
          "destination": [
            "monitor-21",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-27",
            0
          ],
          "destination": [
            "monitor-22",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-27",
            1
          ],
          "destination": [
            "monitor-23",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-27",
            2
          ],
          "destination": [
            "monitor-24",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-36",
            0
          ],
          "destination": [
            "monitor-37",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-37",
            0
          ],
          "destination": [
            "monitor-38",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-37",
            1
          ],
          "destination": [
            "monitor-39",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-37",
            2
          ],
          "destination": [
            "monitor-40",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-39",
            0
          ],
          "destination": [
            "monitor-31",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-40",
            0
          ],
          "destination": [
            "monitor-32",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-38",
            0
          ],
          "destination": [
            "monitor-33",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-38",
            1
          ],
          "destination": [
            "monitor-34",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-38",
            2
          ],
          "destination": [
            "monitor-35",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-47",
            0
          ],
          "destination": [
            "monitor-48",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-48",
            0
          ],
          "destination": [
            "monitor-49",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-48",
            1
          ],
          "destination": [
            "monitor-50",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-48",
            2
          ],
          "destination": [
            "monitor-51",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-50",
            0
          ],
          "destination": [
            "monitor-42",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-51",
            0
          ],
          "destination": [
            "monitor-43",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-49",
            0
          ],
          "destination": [
            "monitor-44",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-49",
            1
          ],
          "destination": [
            "monitor-45",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-49",
            2
          ],
          "destination": [
            "monitor-46",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-9",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-10",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-11",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-12",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-13",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-20",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            5
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-21",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-22",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            7
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-23",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            8
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-24",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            9
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-31",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            10
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-32",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            11
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-33",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            12
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-34",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            13
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-35",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            14
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-42",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            15
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-43",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            16
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-44",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            17
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-45",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            18
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-46",
            0
          ],
          "destination": [
            "monitor-udp-pack",
            19
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-udp-pack",
            0
          ],
          "destination": [
            "monitor-udp-speedlim",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "monitor-udp-speedlim",
            0
          ],
          "destination": [
            "monitor-udp-send",
            0
          ]
        }
      }
    ]
  }
}
