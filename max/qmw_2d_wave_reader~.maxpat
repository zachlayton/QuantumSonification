{
  "patcher": {
    "fileversion": 1,
    "appversion": { "major": 9, "minor": 0, "revision": 0, "architecture": "x64", "modernui": 1 },
    "classnamespace": "box",
    "rect": [ 0.0, 0.0, 430.0, 230.0 ],
    "boxes": [
      { "box": { "id": "x", "maxclass": "newobj", "text": "inlet~", "patching_rect": [ 25.0, 25.0, 42.0, 22.0 ], "numinlets": 1, "numoutlets": 2, "outlettype": [ "signal", "bang" ] } },
      { "box": { "id": "y", "maxclass": "newobj", "text": "inlet~", "patching_rect": [ 145.0, 25.0, 42.0, 22.0 ], "numinlets": 1, "numoutlets": 2, "outlettype": [ "signal", "bang" ] } },
      { "box": { "id": "xclip", "maxclass": "newobj", "text": "clip~ 0. 1.", "patching_rect": [ 25.0, 70.0, 75.0, 22.0 ], "numinlets": 3, "numoutlets": 1, "outlettype": [ "signal" ] } },
      { "box": { "id": "yclip", "maxclass": "newobj", "text": "clip~ 0. 1.", "patching_rect": [ 145.0, 70.0, 75.0, 22.0 ], "numinlets": 3, "numoutlets": 1, "outlettype": [ "signal" ] } },
      { "box": { "id": "xscale", "maxclass": "newobj", "text": "*~ 0.25", "patching_rect": [ 25.0, 110.0, 62.0, 22.0 ], "numinlets": 2, "numoutlets": 1, "outlettype": [ "signal" ] } },
      { "box": { "id": "yscale", "maxclass": "newobj", "text": "*~ 0.75", "patching_rect": [ 145.0, 110.0, 62.0, 22.0 ], "numinlets": 2, "numoutlets": 1, "outlettype": [ "signal" ] } },
      { "box": { "id": "sum", "maxclass": "newobj", "text": "+~", "patching_rect": [ 90.0, 145.0, 42.0, 22.0 ], "numinlets": 2, "numoutlets": 1, "outlettype": [ "signal" ] } },
      { "box": { "id": "lookup", "maxclass": "newobj", "text": "wave~ #1", "patching_rect": [ 90.0, 180.0, 72.0, 22.0 ], "numinlets": 3, "numoutlets": 1, "outlettype": [ "signal" ] } },
      { "box": { "id": "out", "maxclass": "newobj", "text": "outlet~", "patching_rect": [ 210.0, 180.0, 48.0, 22.0 ], "numinlets": 1, "numoutlets": 0 } }
    ],
    "lines": [
      { "patchline": { "source": [ "x", 0 ], "destination": [ "xclip", 0 ] } },
      { "patchline": { "source": [ "y", 0 ], "destination": [ "yclip", 0 ] } },
      { "patchline": { "source": [ "xclip", 0 ], "destination": [ "xscale", 0 ] } },
      { "patchline": { "source": [ "yclip", 0 ], "destination": [ "yscale", 0 ] } },
      { "patchline": { "source": [ "xscale", 0 ], "destination": [ "sum", 0 ] } },
      { "patchline": { "source": [ "yscale", 0 ], "destination": [ "sum", 1 ] } },
      { "patchline": { "source": [ "sum", 0 ], "destination": [ "lookup", 0 ] } },
      { "patchline": { "source": [ "lookup", 0 ], "destination": [ "out", 0 ] } }
    ]
  }
}
