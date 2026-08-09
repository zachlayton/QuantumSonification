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
      120,
      80,
      840,
      730
    ],
    "gridsize": [
      15,
      15
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            18,
            720,
            25
          ],
          "text": "QMW ZX / PennyLane Monitor \u2014 the Max side of the shared patch",
          "fontsize": 16
        }
      },
      {
        "box": {
          "id": "help",
          "maxclass": "comment",
          "patching_rect": [
            25,
            50,
            790,
            38
          ],
          "text": "Receives the same six normalized controls sent to VCV Rack. Python/PennyLane remains the semantic authority; Max is the visible patching and modulation laboratory."
        }
      },
      {
        "box": {
          "id": "udp_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            105,
            160,
            20
          ],
          "text": "OSC input (UDP 7496)"
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            130,
            118,
            22
          ],
          "text": "udpreceive 7496",
          "numinlets": 0,
          "numoutlets": 1
        }
      },
      {
        "box": {
          "id": "route_fader",
          "maxclass": "newobj",
          "patching_rect": [
            165,
            130,
            210,
            22
          ],
          "text": "OSC-route /qmw/zx/fader",
          "numinlets": 1,
          "numoutlets": 2
        }
      },
      {
        "box": {
          "id": "route_ids",
          "maxclass": "newobj",
          "patching_rect": [
            395,
            130,
            150,
            22
          ],
          "text": "route 1 2 3 4 5 6",
          "numinlets": 1,
          "numoutlets": 7
        }
      },
      {
        "box": {
          "id": "signal_note",
          "maxclass": "comment",
          "patching_rect": [
            25,
            176,
            780,
            34
          ],
          "text": "Each number is a control-rate projection of the current quantum state. Patch these outlets into scale, line~, mc.* or your own sonification modules."
        }
      },
      {
        "box": {
          "id": "label_1",
          "maxclass": "comment",
          "patching_rect": [
            25,
            233,
            230,
            20
          ],
          "text": "1  ZX phase (turns)"
        }
      },
      {
        "box": {
          "id": "value_1",
          "maxclass": "flonum",
          "patching_rect": [
            265,
            230,
            100,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "slider_1",
          "maxclass": "slider",
          "patching_rect": [
            385,
            230,
            300,
            22
          ],
          "floatoutput": 1,
          "min": 0.0,
          "size": 1.0,
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "send_1",
          "maxclass": "newobj",
          "patching_rect": [
            705,
            230,
            88,
            22
          ],
          "text": "s qmw.zx.1",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "label_2",
          "maxclass": "comment",
          "patching_rect": [
            25,
            301,
            230,
            20
          ],
          "text": "2  <Z0> mapped to 0..1"
        }
      },
      {
        "box": {
          "id": "value_2",
          "maxclass": "flonum",
          "patching_rect": [
            265,
            298,
            100,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "slider_2",
          "maxclass": "slider",
          "patching_rect": [
            385,
            298,
            300,
            22
          ],
          "floatoutput": 1,
          "min": 0.0,
          "size": 1.0,
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "send_2",
          "maxclass": "newobj",
          "patching_rect": [
            705,
            298,
            88,
            22
          ],
          "text": "s qmw.zx.2",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "label_3",
          "maxclass": "comment",
          "patching_rect": [
            25,
            369,
            230,
            20
          ],
          "text": "3  population entropy"
        }
      },
      {
        "box": {
          "id": "value_3",
          "maxclass": "flonum",
          "patching_rect": [
            265,
            366,
            100,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "slider_3",
          "maxclass": "slider",
          "patching_rect": [
            385,
            366,
            300,
            22
          ],
          "floatoutput": 1,
          "min": 0.0,
          "size": 1.0,
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "send_3",
          "maxclass": "newobj",
          "patching_rect": [
            705,
            366,
            88,
            22
          ],
          "text": "s qmw.zx.3",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "label_4",
          "maxclass": "comment",
          "patching_rect": [
            25,
            437,
            230,
            20
          ],
          "text": "4  l1 coherence"
        }
      },
      {
        "box": {
          "id": "value_4",
          "maxclass": "flonum",
          "patching_rect": [
            265,
            434,
            100,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "slider_4",
          "maxclass": "slider",
          "patching_rect": [
            385,
            434,
            300,
            22
          ],
          "floatoutput": 1,
          "min": 0.0,
          "size": 1.0,
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "send_4",
          "maxclass": "newobj",
          "patching_rect": [
            705,
            434,
            88,
            22
          ],
          "text": "s qmw.zx.4",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "label_5",
          "maxclass": "comment",
          "patching_rect": [
            25,
            505,
            230,
            20
          ],
          "text": "5  parameter gradient"
        }
      },
      {
        "box": {
          "id": "value_5",
          "maxclass": "flonum",
          "patching_rect": [
            265,
            502,
            100,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "slider_5",
          "maxclass": "slider",
          "patching_rect": [
            385,
            502,
            300,
            22
          ],
          "floatoutput": 1,
          "min": 0.0,
          "size": 1.0,
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "send_5",
          "maxclass": "newobj",
          "patching_rect": [
            705,
            502,
            88,
            22
          ],
          "text": "s qmw.zx.5",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "label_6",
          "maxclass": "comment",
          "patching_rect": [
            25,
            573,
            230,
            20
          ],
          "text": "6  dominant probability"
        }
      },
      {
        "box": {
          "id": "value_6",
          "maxclass": "flonum",
          "patching_rect": [
            265,
            570,
            100,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "slider_6",
          "maxclass": "slider",
          "patching_rect": [
            385,
            570,
            300,
            22
          ],
          "floatoutput": 1,
          "min": 0.0,
          "size": 1.0,
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "send_6",
          "maxclass": "newobj",
          "patching_rect": [
            705,
            570,
            88,
            22
          ],
          "text": "s qmw.zx.6",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "footer",
          "maxclass": "comment",
          "patching_rect": [
            25,
            655,
            780,
            42
          ],
          "text": "Named sends: qmw.zx.1 \u2026 qmw.zx.6. The next faithful module layer will carry each logical ZX wire as four real channels [Re|0>, Im|0>, Re|1>, Im|1>]."
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
            "route_fader",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_fader",
            0
          ],
          "destination": [
            "route_ids",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_ids",
            0
          ],
          "destination": [
            "value_1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_1",
            0
          ],
          "destination": [
            "slider_1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_1",
            0
          ],
          "destination": [
            "send_1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_ids",
            1
          ],
          "destination": [
            "value_2",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_2",
            0
          ],
          "destination": [
            "slider_2",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_2",
            0
          ],
          "destination": [
            "send_2",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_ids",
            2
          ],
          "destination": [
            "value_3",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_3",
            0
          ],
          "destination": [
            "slider_3",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_3",
            0
          ],
          "destination": [
            "send_3",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_ids",
            3
          ],
          "destination": [
            "value_4",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_4",
            0
          ],
          "destination": [
            "slider_4",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_4",
            0
          ],
          "destination": [
            "send_4",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_ids",
            4
          ],
          "destination": [
            "value_5",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_5",
            0
          ],
          "destination": [
            "slider_5",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_5",
            0
          ],
          "destination": [
            "send_5",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_ids",
            5
          ],
          "destination": [
            "value_6",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_6",
            0
          ],
          "destination": [
            "slider_6",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "value_6",
            0
          ],
          "destination": [
            "send_6",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
