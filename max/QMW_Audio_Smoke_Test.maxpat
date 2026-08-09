{
  "patcher": {
    "fileversion": 1,
    "appversion": { "major": 9, "minor": 0, "revision": 0, "architecture": "x64", "modernui": 1 },
    "classnamespace": "box",
    "rect": [ 100.0, 100.0, 440.0, 240.0 ],
    "boxes": [
      { "box": { "id": "title", "maxclass": "comment", "text": "QMW AUDIO SMOKE TEST — click ezdac~; expect a quiet 220 Hz tone", "patching_rect": [ 25.0, 20.0, 380.0, 20.0 ] } },
      { "box": { "id": "osc", "maxclass": "newobj", "text": "cycle~ 220.", "patching_rect": [ 25.0, 70.0, 78.0, 22.0 ], "numinlets": 2, "numoutlets": 1, "outlettype": [ "signal" ] } },
      { "box": { "id": "gain", "maxclass": "newobj", "text": "*~ 0.03", "patching_rect": [ 25.0, 110.0, 62.0, 22.0 ], "numinlets": 2, "numoutlets": 1, "outlettype": [ "signal" ] } },
      { "box": { "id": "meter", "maxclass": "meter~", "patching_rect": [ 125.0, 105.0, 18.0, 80.0 ], "numinlets": 1, "numoutlets": 1, "outlettype": [ "float" ] } },
      { "box": { "id": "dac", "maxclass": "ezdac~", "patching_rect": [ 25.0, 160.0, 45.0, 45.0 ], "numinlets": 2, "numoutlets": 0 } }
    ],
    "lines": [
      { "patchline": { "source": [ "osc", 0 ], "destination": [ "gain", 0 ] } },
      { "patchline": { "source": [ "gain", 0 ], "destination": [ "meter", 0 ] } },
      { "patchline": { "source": [ "gain", 0 ], "destination": [ "dac", 0 ] } },
      { "patchline": { "source": [ "gain", 0 ], "destination": [ "dac", 1 ] } }
    ]
  }
}
