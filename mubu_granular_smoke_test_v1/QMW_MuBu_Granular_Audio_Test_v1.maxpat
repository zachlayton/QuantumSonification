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
      60.0,
      60.0,
      840.0,
      650.0
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
            15.0,
            720.0,
            28.0
          ],
          "text": "QMW MuBu GRANULAR AUDIO SMOKE TEST v1",
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "purpose",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            48.0,
            760.0,
            38.0
          ],
          "text": "Known-good Max file \u2192 same-named buffer~/MuBu container \u2192 mubu.granular~ \u2192 stereo output. No atlas, scheduler, MC, or corpus."
        }
      },
      {
        "box": {
          "id": "reload",
          "maxclass": "message",
          "patching_rect": [
            25.0,
            105.0,
            145.0,
            22.0
          ],
          "text": "replace cherokee.aif",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "autoload",
          "maxclass": "newobj",
          "patching_rect": [
            180.0,
            105.0,
            180.0,
            22.0
          ],
          "text": "loadmess replace cherokee.aif",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "source",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            140.0,
            235.0,
            22.0
          ],
          "text": "buffer~ qmw_mubu_audio_test",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "float",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "length_label",
          "maxclass": "comment",
          "patching_rect": [
            275.0,
            142.0,
            90.0,
            20.0
          ],
          "text": "length (ms)"
        }
      },
      {
        "box": {
          "id": "length",
          "maxclass": "flonum",
          "patching_rect": [
            365.0,
            140.0,
            80.0,
            22.0
          ],
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
          "id": "ready",
          "maxclass": "newobj",
          "patching_rect": [
            460.0,
            140.0,
            42.0,
            22.0
          ],
          "text": "t b b",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "bang",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            515.0,
            140.0,
            285.0,
            22.0
          ],
          "text": "waiting for cherokee.aif...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "status_set",
          "maxclass": "message",
          "patching_rect": [
            515.0,
            105.0,
            285.0,
            22.0
          ],
          "text": "set AUDIO LOADED \u2014 MuBu should now play",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "source_container",
          "maxclass": "imubu",
          "patching_rect": [
            25.0,
            180.0,
            775.0,
            150.0
          ],
          "name": "qmw_mubu_audio_test",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "embed": 0,
          "autobounds": 0,
          "autoupdate": 250.0,
          "autorefreshrate": 1,
          "toolbar_visible": 2,
          "tabs_visible": 1,
          "bufferchooser_visible": 0,
          "domain_bounds": [
            0.0,
            3000.0
          ],
          "domainruler_visible": 1,
          "domainscrollbar_visible": 1,
          "tool": "cursor"
        }
      },
      {
        "box": {
          "id": "engine_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            350.0,
            440.0,
            22.0
          ],
          "text": "ONE MuBu ENGINE \u2014 stereo, stock file, explicit level 100",
          "fontsize": 14.0
        }
      },
      {
        "box": {
          "id": "engine",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            382.0,
            755.0,
            28.0
          ],
          "text": "mubu.granular~ 2 qmw_mubu_audio_test @play 0 @period 180 @position 900 @positionvar 80 @duration 300 @level 100 @duplicatechannels 1 @outputposition 1",
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
          "id": "ready_delay",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            425.0,
            65.0,
            22.0
          ],
          "text": "delay 50",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "config",
          "maxclass": "message",
          "patching_rect": [
            100.0,
            425.0,
            680.0,
            35.0
          ],
          "text": "position 900, positionvar 80, duration 300, durationvar 60, resampling 0, resamplingvar 120, level 100, levelvar 0, window cosine, duplicatechannels 1, play 1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "manual_label",
          "maxclass": "comment",
          "patching_rect": [
            25.0,
            480.0,
            112.0,
            20.0
          ],
          "text": "manual grain"
        }
      },
      {
        "box": {
          "id": "manual",
          "maxclass": "button",
          "patching_rect": [
            140.0,
            477.0,
            26.0,
            26.0
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
          "id": "play_label",
          "maxclass": "comment",
          "patching_rect": [
            195.0,
            480.0,
            75.0,
            20.0
          ],
          "text": "auto play"
        }
      },
      {
        "box": {
          "id": "play",
          "maxclass": "toggle",
          "patching_rect": [
            270.0,
            477.0,
            26.0,
            26.0
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
          "id": "play_pre",
          "maxclass": "newobj",
          "patching_rect": [
            306.0,
            479.0,
            82.0,
            22.0
          ],
          "text": "prepend play",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "metadata",
          "maxclass": "message",
          "patching_rect": [
            415.0,
            479.0,
            365.0,
            22.0
          ],
          "text": "grain position / duration metadata",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "gain_l",
          "maxclass": "newobj",
          "patching_rect": [
            145.0,
            535.0,
            58.0,
            22.0
          ],
          "text": "*~ 0.18",
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
            285.0,
            535.0,
            58.0,
            22.0
          ],
          "text": "*~ 0.18",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "meter_l",
          "maxclass": "meter~",
          "patching_rect": [
            215.0,
            525.0,
            18.0,
            65.0
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "meter_r",
          "maxclass": "meter~",
          "patching_rect": [
            355.0,
            525.0,
            18.0,
            65.0
          ],
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
          "maxclass": "ezdac~",
          "patching_rect": [
            430.0,
            525.0,
            55.0,
            55.0
          ],
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "instruction",
          "maxclass": "comment",
          "patching_rect": [
            505.0,
            526.0,
            295.0,
            54.0
          ],
          "text": "CLICK THE SPEAKER TO ENABLE DSP.\nMeters should move continuously; press manual grain for an immediate trigger.",
          "fontsize": 13.0
        }
      },
      {
        "box": {
          "id": "init_play",
          "maxclass": "newobj",
          "patching_rect": [
            25.0,
            535.0,
            75.0,
            22.0
          ],
          "text": "loadmess 1",
          "numinlets": 1,
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
            "reload",
            0
          ],
          "destination": [
            "source",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "autoload",
            0
          ],
          "destination": [
            "source",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "source",
            0
          ],
          "destination": [
            "length",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "source",
            1
          ],
          "destination": [
            "ready",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ready",
            1
          ],
          "destination": [
            "status_set",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "status_set",
            0
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
            "ready",
            0
          ],
          "destination": [
            "ready_delay",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ready_delay",
            0
          ],
          "destination": [
            "config",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "config",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "manual",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "play",
            0
          ],
          "destination": [
            "play_pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "play_pre",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            2
          ],
          "destination": [
            "metadata",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
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
            "engine",
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
            "meter_l",
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
            "meter_r",
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
            "init_play",
            0
          ],
          "destination": [
            "play",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "mubu.granular~.mxo",
        "type": "iLaX"
      },
      {
        "name": "imubu.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
