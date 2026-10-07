{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 9,
      "minor": 0,
      "revision": 0,
      "architecture": "x64"
    },
    "rect": [
      80.0,
      80.0,
      1050.0,
      600.0
    ],
    "boxes": [
      {
        "box": {
          "id": "obj-1",
          "maxclass": "comment",
          "text": "QMW QuantumFrame OSC Receiver \u2014 /qmw/grain",
          "patching_rect": [
            30.0,
            20.0,
            400.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-2",
          "maxclass": "newobj",
          "text": "udpreceive 7405",
          "patching_rect": [
            30.0,
            60.0,
            120.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-3",
          "maxclass": "newobj",
          "text": "oscparse",
          "patching_rect": [
            30.0,
            100.0,
            80.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-4",
          "maxclass": "newobj",
          "text": "route /qmw/grain",
          "patching_rect": [
            30.0,
            140.0,
            140.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-5",
          "maxclass": "newobj",
          "text": "unpack i f f f f f f f",
          "patching_rect": [
            30.0,
            185.0,
            190.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "num-0",
          "maxclass": "number",
          "patching_rect": [
            30.0,
            260.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "num-1",
          "maxclass": "flonum",
          "patching_rect": [
            150.0,
            260.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "num-2",
          "maxclass": "flonum",
          "patching_rect": [
            270.0,
            260.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "num-3",
          "maxclass": "flonum",
          "patching_rect": [
            390.0,
            260.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "num-4",
          "maxclass": "flonum",
          "patching_rect": [
            510.0,
            260.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "num-5",
          "maxclass": "flonum",
          "patching_rect": [
            630.0,
            260.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "num-6",
          "maxclass": "flonum",
          "patching_rect": [
            750.0,
            260.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "num-7",
          "maxclass": "flonum",
          "patching_rect": [
            870.0,
            260.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "lab-0",
          "maxclass": "comment",
          "text": "index",
          "patching_rect": [
            30.0,
            235.0,
            105.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "lab-1",
          "maxclass": "comment",
          "text": "sim time",
          "patching_rect": [
            150.0,
            235.0,
            105.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "lab-2",
          "maxclass": "comment",
          "text": "position",
          "patching_rect": [
            270.0,
            235.0,
            105.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "lab-3",
          "maxclass": "comment",
          "text": "duration ms",
          "patching_rect": [
            390.0,
            235.0,
            105.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "lab-4",
          "maxclass": "comment",
          "text": "rate",
          "patching_rect": [
            510.0,
            235.0,
            105.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "lab-5",
          "maxclass": "comment",
          "text": "amplitude",
          "patching_rect": [
            630.0,
            235.0,
            105.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "lab-6",
          "maxclass": "comment",
          "text": "pan",
          "patching_rect": [
            750.0,
            235.0,
            105.0,
            20.0
          ]
        }
      },
      {
        "box": {
          "id": "lab-7",
          "maxclass": "comment",
          "text": "density Hz",
          "patching_rect": [
            870.0,
            235.0,
            105.0,
            20.0
          ]
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "obj-2",
            0
          ],
          "destination": [
            "obj-3",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-3",
            0
          ],
          "destination": [
            "obj-4",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-4",
            0
          ],
          "destination": [
            "obj-5",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-5",
            0
          ],
          "destination": [
            "num-0",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-5",
            1
          ],
          "destination": [
            "num-1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-5",
            2
          ],
          "destination": [
            "num-2",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-5",
            3
          ],
          "destination": [
            "num-3",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-5",
            4
          ],
          "destination": [
            "num-4",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-5",
            5
          ],
          "destination": [
            "num-5",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-5",
            6
          ],
          "destination": [
            "num-6",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-5",
            7
          ],
          "destination": [
            "num-7",
            0
          ]
        }
      }
    ]
  }
}