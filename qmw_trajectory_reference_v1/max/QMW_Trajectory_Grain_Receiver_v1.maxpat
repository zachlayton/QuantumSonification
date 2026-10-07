{
  "patcher": {
    "fileversion": 1,
    "appversion": { "major": 9, "minor": 0, "revision": 0, "architecture": "x64" },
    "classnamespace": "box",
    "rect": [ 80.0, 80.0, 1180.0, 410.0 ],
    "boxes": [
      { "box": { "id": "title", "maxclass": "comment", "text": "QMW trajectory-grain observer — UDP 17905 — read-only control monitor", "patching_rect": [ 30.0, 20.0, 620.0, 22.0 ] } },
      { "box": { "id": "receive", "maxclass": "newobj", "text": "udpreceive 17905", "patching_rect": [ 30.0, 65.0, 120.0, 22.0 ] } },
      { "box": { "id": "parse", "maxclass": "newobj", "text": "oscparse", "patching_rect": [ 30.0, 105.0, 70.0, 22.0 ] } },
      { "box": { "id": "route", "maxclass": "newobj", "text": "route /qmw/trajectory_grain/v1/grain", "patching_rect": [ 30.0, 145.0, 245.0, 22.0 ] } },
      { "box": { "id": "unpack", "maxclass": "newobj", "text": "unpack i i f f f f f f f", "patching_rect": [ 30.0, 185.0, 230.0, 22.0 ] } },
      { "box": { "id": "revisionLabel", "maxclass": "comment", "text": "revision", "patching_rect": [ 30.0, 230.0, 75.0, 20.0 ] } },
      { "box": { "id": "indexLabel", "maxclass": "comment", "text": "index", "patching_rect": [ 150.0, 230.0, 75.0, 20.0 ] } },
      { "box": { "id": "timeLabel", "maxclass": "comment", "text": "simulation time", "patching_rect": [ 270.0, 230.0, 100.0, 20.0 ] } },
      { "box": { "id": "positionLabel", "maxclass": "comment", "text": "buffer position", "patching_rect": [ 390.0, 230.0, 105.0, 20.0 ] } },
      { "box": { "id": "durationLabel", "maxclass": "comment", "text": "duration ms", "patching_rect": [ 510.0, 230.0, 95.0, 20.0 ] } },
      { "box": { "id": "rateLabel", "maxclass": "comment", "text": "rate", "patching_rect": [ 630.0, 230.0, 75.0, 20.0 ] } },
      { "box": { "id": "amplitudeLabel", "maxclass": "comment", "text": "amplitude", "patching_rect": [ 750.0, 230.0, 80.0, 20.0 ] } },
      { "box": { "id": "panLabel", "maxclass": "comment", "text": "pan", "patching_rect": [ 870.0, 230.0, 70.0, 20.0 ] } },
      { "box": { "id": "densityLabel", "maxclass": "comment", "text": "density Hz", "patching_rect": [ 990.0, 230.0, 80.0, 20.0 ] } },
      { "box": { "id": "revision", "maxclass": "number", "patching_rect": [ 30.0, 260.0, 90.0, 22.0 ] } },
      { "box": { "id": "index", "maxclass": "number", "patching_rect": [ 150.0, 260.0, 90.0, 22.0 ] } },
      { "box": { "id": "time", "maxclass": "flonum", "patching_rect": [ 270.0, 260.0, 90.0, 22.0 ] } },
      { "box": { "id": "position", "maxclass": "flonum", "patching_rect": [ 390.0, 260.0, 90.0, 22.0 ] } },
      { "box": { "id": "duration", "maxclass": "flonum", "patching_rect": [ 510.0, 260.0, 90.0, 22.0 ] } },
      { "box": { "id": "rate", "maxclass": "flonum", "patching_rect": [ 630.0, 260.0, 90.0, 22.0 ] } },
      { "box": { "id": "amplitude", "maxclass": "flonum", "patching_rect": [ 750.0, 260.0, 90.0, 22.0 ] } },
      { "box": { "id": "pan", "maxclass": "flonum", "patching_rect": [ 870.0, 260.0, 90.0, 22.0 ] } },
      { "box": { "id": "density", "maxclass": "flonum", "patching_rect": [ 990.0, 260.0, 90.0, 22.0 ] } },
      { "box": { "id": "boundary", "maxclass": "comment", "text": "These are musical control values from an explicit projection. They are not quantum state variables and do not feed back to QMW physics.", "patching_rect": [ 30.0, 330.0, 980.0, 22.0 ] } }
    ],
    "lines": [
      { "patchline": { "source": [ "receive", 0 ], "destination": [ "parse", 0 ] } },
      { "patchline": { "source": [ "parse", 0 ], "destination": [ "route", 0 ] } },
      { "patchline": { "source": [ "route", 0 ], "destination": [ "unpack", 0 ] } },
      { "patchline": { "source": [ "unpack", 0 ], "destination": [ "revision", 0 ] } },
      { "patchline": { "source": [ "unpack", 1 ], "destination": [ "index", 0 ] } },
      { "patchline": { "source": [ "unpack", 2 ], "destination": [ "time", 0 ] } },
      { "patchline": { "source": [ "unpack", 3 ], "destination": [ "position", 0 ] } },
      { "patchline": { "source": [ "unpack", 4 ], "destination": [ "duration", 0 ] } },
      { "patchline": { "source": [ "unpack", 5 ], "destination": [ "rate", 0 ] } },
      { "patchline": { "source": [ "unpack", 6 ], "destination": [ "amplitude", 0 ] } },
      { "patchline": { "source": [ "unpack", 7 ], "destination": [ "pan", 0 ] } },
      { "patchline": { "source": [ "unpack", 8 ], "destination": [ "density", 0 ] } }
    ]
  }
}
