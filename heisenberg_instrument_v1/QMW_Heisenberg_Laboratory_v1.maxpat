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
      80.0,
      55.0,
      1130.0,
      920.0
    ],
    "gridsize": [
      15.0,
      15.0
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            16.0,
            900.0,
            28.0
          ],
          "text": "QMW HEISENBERG LAB v1 \u2014 THREE EXPERIMENTS / 16 \u00d7 16 TRANSITION RESONATOR",
          "fontsize": 17.0
        }
      },
      {
        "box": {
          "id": "description",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            48.0,
            1050.0,
            40.0
          ],
          "text": "Each resonant cell is one ordered energy-basis relation (m,n): rho[m,n] A[n,m]. COHERENT preserves alternatives; UNREAD performs and discards an intermediate measurement; RECORDED conditions the future on one outcome."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            102.0,
            126.0,
            22.0
          ],
          "text": "udpreceive 7400",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "route_qmw",
          "maxclass": "newobj",
          "patching_rect": [
            170.0,
            102.0,
            104.0,
            22.0
          ],
          "text": "OSC-route /qmw",
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
          "id": "route_h",
          "maxclass": "newobj",
          "patching_rect": [
            292.0,
            102.0,
            145.0,
            22.0
          ],
          "text": "OSC-route /heisenberg",
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
          "id": "route_active",
          "maxclass": "newobj",
          "patching_rect": [
            455.0,
            102.0,
            125.0,
            22.0
          ],
          "text": "OSC-route /active",
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
          "id": "route_meta",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            144.0,
            650.0,
            22.0
          ],
          "text": "OSC-route /mode /outcome /disturbance /coherence_before /coherence_after /matrix",
          "numinlets": 1,
          "numoutlets": 7,
          "outlettype": [
            "",
            "",
            "",
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "route_matrix",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            184.0,
            810.0,
            22.0
          ],
          "text": "OSC-route /begin /end /magnitude_normalized /frequency_hz /phase /pan /real /imag",
          "numinlets": 1,
          "numoutlets": 9,
          "outlettype": [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_begin",
          "maxclass": "newobj",
          "patching_rect": [
            850.0,
            184.0,
            105.0,
            22.0
          ],
          "text": "prepend begin",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_end",
          "maxclass": "newobj",
          "patching_rect": [
            970.0,
            184.0,
            95.0,
            22.0
          ],
          "text": "prepend end",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_mag",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            222.0,
            185.0,
            22.0
          ],
          "text": "prepend magnitude_normalized",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_freq",
          "maxclass": "newobj",
          "patching_rect": [
            225.0,
            222.0,
            150.0,
            22.0
          ],
          "text": "prepend frequency_hz",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_phase",
          "maxclass": "newobj",
          "patching_rect": [
            390.0,
            222.0,
            110.0,
            22.0
          ],
          "text": "prepend phase",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_pan",
          "maxclass": "newobj",
          "patching_rect": [
            515.0,
            222.0,
            100.0,
            22.0
          ],
          "text": "prepend pan",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_mode",
          "maxclass": "newobj",
          "patching_rect": [
            700.0,
            144.0,
            105.0,
            22.0
          ],
          "text": "prepend mode",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_outcome",
          "maxclass": "newobj",
          "patching_rect": [
            815.0,
            144.0,
            125.0,
            22.0
          ],
          "text": "prepend outcome",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre_disturbance",
          "maxclass": "newobj",
          "patching_rect": [
            950.0,
            144.0,
            145.0,
            22.0
          ],
          "text": "prepend disturbance",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "js",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            270.0,
            285.0,
            22.0
          ],
          "text": "js qmw_heisenberg_matrix_resonator_v1.js",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
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
            25.0,
            315.0,
            340.0,
            22.0
          ],
          "text": "poly~ qmw_heisenberg_cell_voice_v1 256 @parallel 1",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "gain_l",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            360.0,
            42.0,
            22.0
          ],
          "text": "*~ 0.7",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "gain_r",
          "maxclass": "newobj",
          "patching_rect": [
            90.0,
            360.0,
            42.0,
            22.0
          ],
          "text": "*~ 0.7",
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
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            405.0,
            52.0,
            32.0
          ],
          "text": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "matrix",
          "maxclass": "jit.cellblock",
          "patching_rect": [
            410.0,
            270.0,
            685.0,
            430.0
          ],
          "cols": 16,
          "rows": 16,
          "colhead": 0,
          "rowhead": 0,
          "numinlets": 2,
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
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            470.0,
            350.0,
            42.0
          ],
          "text": "waiting for Heisenberg field...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "mode_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            540.0,
            280.0,
            20.0
          ],
          "text": "Intermediate observation protocol"
        }
      },
      {
        "box": {
          "id": "coherent",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            570.0,
            230.0,
            22.0
          ],
          "text": "/qmw/heisenberg/mode coherent",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "unread",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            602.0,
            220.0,
            22.0
          ],
          "text": "/qmw/heisenberg/mode unread",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "recorded",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            634.0,
            235.0,
            22.0
          ],
          "text": "/qmw/heisenberg/mode recorded",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "record",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            676.0,
            195.0,
            22.0
          ],
          "text": "/qmw/heisenberg/record 1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "send",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            718.0,
            155.0,
            22.0
          ],
          "text": "udpsend 127.0.0.1 7412",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "obs_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            760.0,
            280.0,
            20.0
          ],
          "text": "Observable addressed by the matrix"
        }
      },
      {
        "box": {
          "id": "obs_x",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            790.0,
            205.0,
            22.0
          ],
          "text": "/qmw/heisenberg/observable X0",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "obs_y",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            822.0,
            205.0,
            22.0
          ],
          "text": "/qmw/heisenberg/observable Y0",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "obs_z",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            854.0,
            205.0,
            22.0
          ],
          "text": "/qmw/heisenberg/observable Z0",
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
            270.0,
            676.0,
            42.0,
            22.0
          ],
          "text": "test",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
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
            "route_qmw",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_qmw",
            0
          ],
          "destination": [
            "route_h",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_h",
            0
          ],
          "destination": [
            "route_active",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_active",
            0
          ],
          "destination": [
            "route_meta",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            0
          ],
          "destination": [
            "pre_mode",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            1
          ],
          "destination": [
            "pre_outcome",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            2
          ],
          "destination": [
            "pre_disturbance",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_meta",
            5
          ],
          "destination": [
            "route_matrix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            0
          ],
          "destination": [
            "pre_begin",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            1
          ],
          "destination": [
            "pre_end",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            2
          ],
          "destination": [
            "pre_mag",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            3
          ],
          "destination": [
            "pre_freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            4
          ],
          "destination": [
            "pre_phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route_matrix",
            5
          ],
          "destination": [
            "pre_pan",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre_begin",
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
            "pre_end",
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
            "pre_mag",
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
            "pre_freq",
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
            "pre_phase",
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
            "pre_pan",
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
            "pre_mode",
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
            "pre_outcome",
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
            "pre_disturbance",
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
            "js",
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
            "js",
            1
          ],
          "destination": [
            "matrix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            2
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
            "gain_l",
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
            "gain_r",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gain_l",
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
            "gain_r",
            0
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
            "coherent",
            0
          ],
          "destination": [
            "send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unread",
            0
          ],
          "destination": [
            "send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "recorded",
            0
          ],
          "destination": [
            "send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "record",
            0
          ],
          "destination": [
            "send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obs_x",
            0
          ],
          "destination": [
            "send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obs_y",
            0
          ],
          "destination": [
            "send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obs_z",
            0
          ],
          "destination": [
            "send",
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
            "js",
            0
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
        "name": "qmw_heisenberg_matrix_resonator_v1.js",
        "type": "TEXT"
      },
      {
        "name": "qmw_heisenberg_cell_voice_v1.maxpat",
        "type": "JSON"
      }
    ],
    "autosave": 0
  }
}
