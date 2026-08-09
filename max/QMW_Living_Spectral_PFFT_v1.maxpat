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
      0,
      0,
      1180,
      720
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            20,
            15,
            1080,
            30
          ],
          "text": "QMW LIVING SPECTRAL PFFT v1 - stochastic eigenfield-history masking",
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "source",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            75,
            150,
            22
          ],
          "text": "playlist~ @loop 1",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
            "signal",
            "signal",
            "signal",
            "",
            "dictionary"
          ]
        }
      },
      {
        "box": {
          "id": "pfft",
          "maxclass": "newobj",
          "patching_rect": [
            220,
            75,
            315,
            22
          ],
          "text": "pfft~ qmw_living_spectral_mask_pfft_v1 4096 4",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "gain",
          "maxclass": "newobj",
          "patching_rect": [
            585,
            75,
            75,
            22
          ],
          "text": "*~ 0.2",
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
            720,
            70,
            52,
            52
          ],
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "buffer",
          "maxclass": "newobj",
          "patching_rect": [
            220,
            125,
            305,
            22
          ],
          "text": "buffer~ qmw_living_spectral_mask @samps 2048",
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
          "id": "waveform",
          "maxclass": "waveform~",
          "patching_rect": [
            550,
            125,
            560,
            80
          ],
          "buffername": "qmw_living_spectral_mask",
          "numinlets": 5,
          "numoutlets": 6,
          "outlettype": [
            "float",
            "float",
            "float",
            "float",
            "list",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "testmask",
          "maxclass": "message",
          "patching_rect": [
            20,
            140,
            80,
            22
          ],
          "text": "test_mask",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "passthrough",
          "maxclass": "message",
          "patching_rect": [
            110,
            140,
            90,
            22
          ],
          "text": "passthrough",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            235,
            165,
            22
          ],
          "text": "udpreceive 7460 cnmat",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "osc",
          "maxclass": "newobj",
          "patching_rect": [
            215,
            235,
            130,
            22
          ],
          "text": "OpenSoundControl",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            "OSCTimeTag"
          ]
        }
      },
      {
        "box": {
          "id": "living",
          "maxclass": "newobj",
          "patching_rect": [
            375,
            235,
            120,
            22
          ],
          "text": "OSC-route /living",
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
          "id": "rootroute",
          "maxclass": "newobj",
          "patching_rect": [
            525,
            235,
            225,
            22
          ],
          "text": "OSC-route /spectral /publication",
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
          "id": "spectralroute",
          "maxclass": "newobj",
          "patching_rect": [
            525,
            285,
            200,
            22
          ],
          "text": "OSC-route /history /playback",
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
          "id": "historyroute",
          "maxclass": "newobj",
          "patching_rect": [
            380,
            335,
            430,
            22
          ],
          "text": "OSC-route /shape /magnitudes /frequencies_hz /transients",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
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
          "id": "playbackroute",
          "maxclass": "newobj",
          "patching_rect": [
            830,
            285,
            300,
            22
          ],
          "text": "OSC-route /blur_width /transition /freeze",
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
          "id": "publicationroute",
          "maxclass": "newobj",
          "patching_rect": [
            815,
            235,
            110,
            22
          ],
          "text": "OSC-route /end",
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
          "id": "shape",
          "maxclass": "newobj",
          "patching_rect": [
            380,
            385,
            125,
            22
          ],
          "text": "prepend shape",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "magnitudes",
          "maxclass": "newobj",
          "patching_rect": [
            510,
            385,
            125,
            22
          ],
          "text": "prepend magnitudes",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "frequencies",
          "maxclass": "newobj",
          "patching_rect": [
            665,
            385,
            125,
            22
          ],
          "text": "prepend frequencies_hz",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "transients",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            385,
            125,
            22
          ],
          "text": "prepend transients",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "blur",
          "maxclass": "newobj",
          "patching_rect": [
            805,
            335,
            125,
            22
          ],
          "text": "prepend blur_width",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "transition",
          "maxclass": "newobj",
          "patching_rect": [
            950,
            335,
            125,
            22
          ],
          "text": "prepend transition",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "freeze",
          "maxclass": "newobj",
          "patching_rect": [
            1080,
            335,
            125,
            22
          ],
          "text": "prepend freeze",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "commit",
          "maxclass": "newobj",
          "patching_rect": [
            805,
            335,
            125,
            22
          ],
          "text": "prepend commit",
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
            530,
            465,
            240,
            22
          ],
          "text": "js qmw_living_spectral_mask_v1.js",
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
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            530,
            515,
            395,
            22
          ],
          "text": "",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "transient",
          "maxclass": "flonum",
          "patching_rect": [
            950,
            465,
            75,
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
          "id": "note",
          "maxclass": "comment",
          "patching_rect": [
            20,
            610,
            1090,
            60
          ],
          "text": "pfft~ uses a 4096-sample FFT and overlap 4 (hop 1024; latency 3072 samples). fftin~ supplies real, imaginary, and bin-index signals. The eigenfield history becomes a magnitude mask; the audio STFT phase is preserved inside the pfft~ patch.",
          "fontsize": 13.0
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "source",
            0
          ],
          "destination": [
            "pfft",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pfft",
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
      },
      {
        "patchline": {
          "source": [
            "udp",
            0
          ],
          "destination": [
            "osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "osc",
            0
          ],
          "destination": [
            "living",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "living",
            0
          ],
          "destination": [
            "rootroute",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rootroute",
            0
          ],
          "destination": [
            "spectralroute",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rootroute",
            1
          ],
          "destination": [
            "publicationroute",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spectralroute",
            0
          ],
          "destination": [
            "historyroute",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spectralroute",
            1
          ],
          "destination": [
            "playbackroute",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "historyroute",
            0
          ],
          "destination": [
            "shape",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "historyroute",
            1
          ],
          "destination": [
            "magnitudes",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "historyroute",
            2
          ],
          "destination": [
            "frequencies",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "historyroute",
            3
          ],
          "destination": [
            "transients",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "playbackroute",
            0
          ],
          "destination": [
            "blur",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "playbackroute",
            1
          ],
          "destination": [
            "transition",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "playbackroute",
            2
          ],
          "destination": [
            "freeze",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "publicationroute",
            0
          ],
          "destination": [
            "commit",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "shape",
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
            "magnitudes",
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
            "frequencies",
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
            "transients",
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
            "blur",
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
            "transition",
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
            "freeze",
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
            "commit",
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
            "status",
            1
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
            "transient",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "testmask",
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
            "passthrough",
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
        "name": "qmw_living_spectral_mask_pfft_v1.maxpat",
        "type": "JSON"
      },
      {
        "name": "qmw_living_spectral_mask_v1.js",
        "type": "TEXT"
      },
      {
        "name": "OpenSoundControl.mxo",
        "type": "iLaX"
      },
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
      }
    ]
  }
}
