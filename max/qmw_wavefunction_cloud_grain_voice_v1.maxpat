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
      90,
      90,
      720,
      380
    ],
    "boxes": [
      {
        "box": {
          "id": "in",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            25,
            42,
            22
          ],
          "text": "in 1",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "route",
          "maxclass": "newobj",
          "patching_rect": [
            70,
            29,
            72,
            22
          ],
          "text": "route grain",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "grain_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            155,
            29,
            52,
            22
          ],
          "text": "t l l",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "list",
            "list"
          ]
        }
      },
      {
        "box": {
          "id": "ack",
          "maxclass": "newobj",
          "patching_rect": [
            220,
            29,
            105,
            22
          ],
          "text": "prepend received",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "out_ack",
          "maxclass": "newobj",
          "patching_rect": [
            335,
            29,
            42,
            22
          ],
          "text": "out 1",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "unpack",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            70,
            245,
            22
          ],
          "text": "unpack f f f f f f f f f f",
          "numinlets": 1,
          "numoutlets": 10,
          "outlettype": [
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "energy_freq",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            112,
            145,
            22
          ],
          "text": "expr 70.*pow(102.857,$f1)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "cycle",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            150,
            55,
            22
          ],
          "text": "cycle~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "phase",
          "maxclass": "newobj",
          "patching_rect": [
            185,
            112,
            105,
            22
          ],
          "text": "expr ($f1+1.)*0.5",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "amp_sig",
          "maxclass": "newobj",
          "patching_rect": [
            95,
            150,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "tonal_amp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            188,
            35,
            22
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "decay_store",
          "maxclass": "newobj",
          "patching_rect": [
            310,
            112,
            40,
            22
          ],
          "text": "f 5.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "x_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            365,
            112,
            45,
            22
          ],
          "text": "t b f",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "env_message",
          "maxclass": "message",
          "patching_rect": [
            310,
            150,
            100,
            22
          ],
          "text": "1., 0. $1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "env",
          "maxclass": "newobj",
          "patching_rect": [
            310,
            188,
            45,
            22
          ],
          "text": "line~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "enveloped",
          "maxclass": "newobj",
          "patching_rect": [
            80,
            226,
            35,
            22
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "left_gain",
          "maxclass": "newobj",
          "patching_rect": [
            365,
            150,
            150,
            22
          ],
          "text": "expr sqrt((1.-$f1)*0.5)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "right_gain",
          "maxclass": "newobj",
          "patching_rect": [
            525,
            150,
            150,
            22
          ],
          "text": "expr sqrt((1.+$f1)*0.5)",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "left_sig",
          "maxclass": "newobj",
          "patching_rect": [
            365,
            188,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "right_sig",
          "maxclass": "newobj",
          "patching_rect": [
            525,
            188,
            45,
            22
          ],
          "text": "sig~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "left",
          "maxclass": "newobj",
          "patching_rect": [
            80,
            264,
            35,
            22
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "right",
          "maxclass": "newobj",
          "patching_rect": [
            150,
            264,
            35,
            22
          ],
          "text": "*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "out_left",
          "maxclass": "newobj",
          "patching_rect": [
            80,
            308,
            52,
            22
          ],
          "text": "out~ 1",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "out_right",
          "maxclass": "newobj",
          "patching_rect": [
            150,
            308,
            52,
            22
          ],
          "text": "out~ 2",
          "numinlets": 1,
          "numoutlets": 0
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
            "grain_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "grain_trigger",
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
            "grain_trigger",
            1
          ],
          "destination": [
            "ack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ack",
            0
          ],
          "destination": [
            "out_ack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            8
          ],
          "destination": [
            "energy_freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "energy_freq",
            0
          ],
          "destination": [
            "cycle",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            4
          ],
          "destination": [
            "phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phase",
            0
          ],
          "destination": [
            "cycle",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            3
          ],
          "destination": [
            "amp_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "cycle",
            0
          ],
          "destination": [
            "tonal_amp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp_sig",
            0
          ],
          "destination": [
            "tonal_amp",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            9
          ],
          "destination": [
            "decay_store",
            1
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
            "x_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "x_trigger",
            0
          ],
          "destination": [
            "decay_store",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "decay_store",
            0
          ],
          "destination": [
            "env_message",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env_message",
            0
          ],
          "destination": [
            "env",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "tonal_amp",
            0
          ],
          "destination": [
            "enveloped",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env",
            0
          ],
          "destination": [
            "enveloped",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "x_trigger",
            1
          ],
          "destination": [
            "left_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "x_trigger",
            1
          ],
          "destination": [
            "right_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "left_gain",
            0
          ],
          "destination": [
            "left_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "right_gain",
            0
          ],
          "destination": [
            "right_sig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "enveloped",
            0
          ],
          "destination": [
            "left",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "left_sig",
            0
          ],
          "destination": [
            "left",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "enveloped",
            0
          ],
          "destination": [
            "right",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "right_sig",
            0
          ],
          "destination": [
            "right",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "left",
            0
          ],
          "destination": [
            "out_left",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "right",
            0
          ],
          "destination": [
            "out_right",
            0
          ]
        }
      }
    ],
    "autosave": 0
  }
}
