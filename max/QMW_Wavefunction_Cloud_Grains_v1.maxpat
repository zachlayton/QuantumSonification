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
      80,
      70,
      960,
      500
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            15,
            850,
            25
          ],
          "text": "QMW 3D Wavefunction Cloud Grains v1 \u2014 no sustained chord",
          "fontsize": 16
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            25,
            44,
            900,
            35
          ],
          "text": "Every probability sample becomes a self-contained grain: default 0.25 ms attack + 5 ms decay."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            92,
            115,
            22
          ],
          "text": "udpreceive 7480",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "root",
          "maxclass": "newobj",
          "patching_rect": [
            155,
            92,
            240,
            22
          ],
          "text": "OSC-route /qmw/wavefunction/cloud",
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
          "id": "route",
          "maxclass": "newobj",
          "patching_rect": [
            410,
            92,
            180,
            22
          ],
          "text": "OSC-route /grain /frame /end",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "dispatch",
          "maxclass": "newobj",
          "patching_rect": [
            410,
            132,
            250,
            22
          ],
          "text": "js qmw_wavefunction_cloud_dispatch_v1.js",
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
          "id": "poly",
          "maxclass": "newobj",
          "patching_rect": [
            410,
            182,
            380,
            22
          ],
          "text": "poly~ qmw_wavefunction_cloud_grain_voice_v1.maxpat 64 @steal 1",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "signal",
            "signal",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "gain",
          "maxclass": "live.gain~",
          "patching_rect": [
            810,
            170,
            96,
            140
          ],
          "numinlets": 2,
          "numoutlets": 5,
          "outlettype": [
            "signal",
            "signal",
            "",
            "float",
            "list"
          ],
          "parameter_enable": 1,
          "saved_attribute_attributes": {
            "valueof": {
              "parameter_initial": [
                -12.0
              ],
              "parameter_initial_enable": 1,
              "parameter_longname": "Wavefunction cloud output",
              "parameter_mmax": 6.0,
              "parameter_mmin": -70.0,
              "parameter_modmode": 0,
              "parameter_shortname": "cloud output",
              "parameter_type": 0,
              "parameter_unitstyle": 4
            }
          },
          "varname": "wavefunction_cloud_output"
        }
      },
      {
        "box": {
          "id": "pre_meter_l",
          "maxclass": "newobj",
          "patching_rect": [
            700,
            220,
            70,
            22
          ],
          "text": "meter~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "pre_meter_r",
          "maxclass": "newobj",
          "patching_rect": [
            700,
            250,
            70,
            22
          ],
          "text": "meter~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            335,
            65,
            22
          ],
          "text": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "dsp_on",
          "maxclass": "newobj",
          "patching_rect": [
            885,
            335,
            75,
            22
          ],
          "text": "loadmess 1",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "test_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            182,
            175,
            22
          ],
          "text": "Click to test poly~ locally:"
        }
      },
      {
        "box": {
          "id": "test_grain",
          "maxclass": "message",
          "patching_rect": [
            25,
            207,
            360,
            22
          ],
          "text": "target 1, grain -0.2 0. 0. 0.8 0. 0. 0. 0. 0.4 80.",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "meter_note",
          "maxclass": "comment",
          "patching_rect": [
            665,
            280,
            135,
            35
          ],
          "text": "poly~ signal meters\n(before output gain)"
        }
      },
      {
        "box": {
          "id": "direct_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            252,
            250,
            22
          ],
          "text": "DIRECT AUDIO TEST (bypasses poly~):"
        }
      },
      {
        "box": {
          "id": "direct_toggle",
          "maxclass": "toggle",
          "patching_rect": [
            278,
            252,
            24,
            24
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "direct_cycle",
          "maxclass": "newobj",
          "patching_rect": [
            310,
            252,
            70,
            22
          ],
          "text": "cycle~ 220",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "direct_amp",
          "maxclass": "newobj",
          "patching_rect": [
            390,
            252,
            52,
            22
          ],
          "text": "*~ 0.08",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "direct_note",
          "maxclass": "comment",
          "patching_rect": [
            25,
            280,
            430,
            35
          ],
          "text": "Toggle on: a steady 220 Hz tone proves DSP, output gain, and audio device."
        }
      },
      {
        "box": {
          "id": "unmute",
          "maxclass": "newobj",
          "patching_rect": [
            410,
            215,
            100,
            22
          ],
          "text": "loadmess mute 0 0",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "voice_ack",
          "maxclass": "message",
          "patching_rect": [
            520,
            215,
            270,
            22
          ],
          "text": "waiting for poly~ voice acknowledgement...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "ack_note",
          "maxclass": "comment",
          "patching_rect": [
            520,
            240,
            275,
            22
          ],
          "text": "Changes to 'received ...' when a voice loads and routes a grain."
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            25,
            132,
            350,
            22
          ],
          "text": "waiting for 5 ms cloud grains...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "note",
          "maxclass": "comment",
          "patching_rect": [
            25,
            390,
            900,
            50
          ],
          "text": "Start: python examples/wavefunction_cloud_osc_v1.py --source schrodinger_packet_3d --grid 32 --fps 30 --grains 16 --decay-ms 5"
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
            "root",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "root",
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
            "dispatch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dispatch",
            0
          ],
          "destination": [
            "poly",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dispatch",
            1
          ],
          "destination": [
            "status",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "poly",
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
            "poly",
            1
          ],
          "destination": [
            "gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "poly",
            0
          ],
          "destination": [
            "pre_meter_l",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "poly",
            1
          ],
          "destination": [
            "pre_meter_r",
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
            1
          ],
          "destination": [
            "dac",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dsp_on",
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
            "test_grain",
            0
          ],
          "destination": [
            "poly",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "direct_cycle",
            0
          ],
          "destination": [
            "direct_amp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "direct_toggle",
            0
          ],
          "destination": [
            "direct_amp",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "direct_amp",
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
            "direct_amp",
            0
          ],
          "destination": [
            "gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unmute",
            0
          ],
          "destination": [
            "poly",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "poly",
            2
          ],
          "destination": [
            "voice_ack",
            1
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
      },
      {
        "name": "qmw_wavefunction_cloud_dispatch_v1.js",
        "type": "TEXT"
      },
      {
        "name": "qmw_wavefunction_cloud_grain_voice_v1.maxpat",
        "type": "JSON"
      }
    ],
    "autosave": 0
  }
}
