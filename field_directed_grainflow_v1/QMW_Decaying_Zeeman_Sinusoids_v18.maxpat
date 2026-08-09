{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 9,
      "minor": 0,
      "revision": 5,
      "architecture": "x64"
    },
    "rect": [
      0,
      0,
      900,
      360
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            20,
            15,
            850,
            28
          ],
          "text": "QMW DECAYING ZEEMAN SINUSOIDS v18 \u2014 MINIMAL CNMAT TEST",
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "note",
          "maxclass": "comment",
          "patching_rect": [
            20,
            48,
            850,
            38
          ],
          "text": "OSC updates the spectral model; RING resets virtual time to zero. No GrainFlow, resonators~, or convolution is present."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            100,
            120,
            22
          ],
          "text": "udpreceive 7400",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "FullPacket"
          ]
        }
      },
      {
        "box": {
          "id": "route",
          "maxclass": "newobj",
          "patching_rect": [
            155,
            100,
            500,
            22
          ],
          "text": "o.route /qmw/conductor/eigenfield/grid/4 /qmw/conductor/zeeman",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "list",
            "list",
            "FullPacket"
          ]
        }
      },
      {
        "box": {
          "id": "js",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            140,
            245,
            22
          ],
          "text": "js qmw_decaying_zeeman_model_v18.js",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "list",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            280,
            140,
            490,
            22
          ],
          "text": "waiting for conductor model",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "decay",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            230,
            170,
            22
          ],
          "text": "decaying-sinusoids~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "ring",
          "maxclass": "button",
          "patching_rect": [
            20,
            180,
            24,
            24
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "ring_label",
          "maxclass": "comment",
          "patching_rect": [
            52,
            181,
            70,
            20
          ],
          "text": "RING"
        }
      },
      {
        "box": {
          "id": "goto",
          "maxclass": "message",
          "patching_rect": [
            125,
            180,
            52,
            22
          ],
          "text": "goto 0.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "test",
          "maxclass": "message",
          "patching_rect": [
            205,
            180,
            390,
            22
          ],
          "text": "220. 0.22 2.5 330. 0.16 3.2 440. 0.1 4.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "test_label",
          "maxclass": "comment",
          "patching_rect": [
            605,
            181,
            180,
            20
          ],
          "text": "manual three-mode model"
        }
      },
      {
        "box": {
          "id": "gain",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            270,
            62,
            22
          ],
          "text": "*~ 0.3",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "ezdac~",
          "patching_rect": [
            110,
            255,
            55,
            55
          ],
          "numinlets": 2,
          "numoutlets": 0
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "udp",
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
            "js",
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
            "js",
            1
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
            "decay",
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
            "status",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ring",
            0
          ],
          "destination": [
            "goto",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "goto",
            0
          ],
          "destination": [
            "decay",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "test",
            0
          ],
          "destination": [
            "decay",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "decay",
            0
          ],
          "destination": [
            "gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gain",
            0
          ],
          "destination": [
            "dac",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gain",
            0
          ],
          "destination": [
            "dac",
            1
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "qmw_decaying_zeeman_model_v18.js",
        "bootpath": "~/QuantumSonification/field_directed_grainflow_v1",
        "type": "TEXT"
      },
      {
        "name": "decaying-sinusoids~.mxo",
        "type": "iLaX"
      },
      {
        "name": "o.route.mxo",
        "type": "iLaX"
      }
    ]
  }
}
