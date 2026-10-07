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
    "rect": [100.0, 100.0, 600.0, 420.0],
    "gridsize": [15.0, 15.0],
    "boxes": [
      {
        "box": {
          "id": "in-control",
          "maxclass": "newobj",
          "text": "in 1",
          "patching_rect": [45.0, 40.0, 35.0, 22.0],
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [""]
        }
      },
      {
        "box": {
          "id": "route-control",
          "maxclass": "newobj",
          "text": "route amp frequency",
          "patching_rect": [45.0, 82.0, 130.0, 22.0],
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": ["", "", ""]
        }
      },
      {
        "box": {
          "id": "amp-pack",
          "maxclass": "newobj",
          "text": "pack 0. 35",
          "patching_rect": [45.0, 130.0, 76.0, 22.0],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [""]
        }
      },
      {
        "box": {
          "id": "amp-line",
          "maxclass": "newobj",
          "text": "line~",
          "patching_rect": [45.0, 174.0, 40.0, 22.0],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": ["signal"]
        }
      },
      {
        "box": {
          "id": "oscillator",
          "maxclass": "newobj",
          "text": "cycle~",
          "patching_rect": [214.0, 174.0, 48.0, 22.0],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": ["signal"]
        }
      },
      {
        "box": {
          "id": "voice-amplitude",
          "maxclass": "newobj",
          "text": "*~",
          "patching_rect": [214.0, 222.0, 38.0, 22.0],
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": ["signal"]
        }
      },
      {
        "box": {
          "id": "out-audio",
          "maxclass": "newobj",
          "text": "out~ 1",
          "patching_rect": [214.0, 272.0, 45.0, 22.0],
          "numinlets": 1,
          "numoutlets": 0
        }
      }
    ],
    "lines": [
      {"patchline": {"source": ["in-control", 0], "destination": ["route-control", 0]}},
      {"patchline": {"source": ["route-control", 0], "destination": ["amp-pack", 0]}},
      {"patchline": {"source": ["route-control", 1], "destination": ["oscillator", 0]}},
      {"patchline": {"source": ["amp-pack", 0], "destination": ["amp-line", 0]}},
      {"patchline": {"source": ["oscillator", 0], "destination": ["voice-amplitude", 0]}},
      {"patchline": {"source": ["amp-line", 0], "destination": ["voice-amplitude", 1]}},
      {"patchline": {"source": ["voice-amplitude", 0], "destination": ["out-audio", 0]}}
    ]
  }
}
