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
      1120,
      380
    ],
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
          "id": "in",
          "maxclass": "inlet",
          "patching_rect": [
            30,
            35,
            30,
            30
          ]
        }
      },
      {
        "box": {
          "id": "trigger",
          "maxclass": "newobj",
          "text": "t b b",
          "patching_rect": [
            30,
            85,
            48,
            22
          ],
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "config",
          "maxclass": "message",
          "text": "/speakers/number 30, /norm SN3D, /method energy-preserving, /powercompensation 1",
          "patching_rect": [
            90,
            125,
            535,
            22
          ],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "geometry",
          "maxclass": "message",
          "text": "/speakers/xyz -0.1396 -6.0143 0 -2.3603 -6.0143 0 -5.0782 -4.5695 0 -5.0782 -2.1371 0 -5.0782 0.1493 0 -5.0782 1.8642 0 -5.0013 4.7833 0 -2.3715 6.0229 0 -0.1576 6.0229 0 2.6097 6.0229 0 4.8474 5.1167 0 5.0526 2.1425 0 5.0526 -0.1428 0 5.0526 -1.8568 0 4.8645 -5.0141 0 1.526 -6.0143 0 5.5 0 -1 3.889087 3.889087 -1 0 5.5 -1 -3.889087 3.889087 -1 -5.5 0 -1 -3.889087 -3.889087 -1 0 -5.5 -1 3.889087 -3.889087 -1 5.5 0 1 2.75 4.76314 1 -2.75 4.76314 1 -5.5 0 1 -2.75 -4.76314 1 2.75 -4.76314 1",
          "patching_rect": [
            90,
            175,
            970,
            70
          ],
          "linecount": 4,
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "out",
          "maxclass": "outlet",
          "patching_rect": [
            30,
            315,
            30,
            30
          ],
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "text": "CRAIVE experimental three-ring HOA layout: exact supplied center 16 + provisional lower 8 + provisional upper 6",
          "patching_rect": [
            90,
            35,
            900,
            22
          ]
        }
      },
      {
        "box": {
          "id": "mapping",
          "maxclass": "comment",
          "text": "Decoder order → hardware: 4 8 12 16 20 23 28 33 37 42 46 51 55 58 63 1 129 130 131 132 133 134 135 136 137 138 139 140 141 142",
          "patching_rect": [
            90,
            255,
            970,
            22
          ]
        }
      },
      {
        "box": {
          "id": "warning",
          "maxclass": "comment",
          "text": "IMPORTANT: outputs 129–142 and their elevations are provisional assumptions. Verify physical routing with CRAIVE staff and test one channel at a time at very low level.",
          "patching_rect": [
            90,
            280,
            970,
            36
          ],
          "linecount": 2
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
            "trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "trigger",
            1
          ],
          "destination": [
            "config",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "trigger",
            0
          ],
          "destination": [
            "geometry",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "config",
            0
          ],
          "destination": [
            "out",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "geometry",
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
