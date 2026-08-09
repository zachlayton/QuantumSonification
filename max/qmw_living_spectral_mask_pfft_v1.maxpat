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
      760,
      400
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            20,
            15,
            700,
            24
          ],
          "text": "QMW living spectral magnitude processor - audio STFT phase remains local",
          "fontsize": 15.0
        }
      },
      {
        "box": {
          "id": "fftin",
          "maxclass": "newobj",
          "patching_rect": [
            35,
            75,
            70,
            22
          ],
          "text": "fftin~ 1",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "signal",
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "cartopol",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            75,
            80,
            22
          ],
          "text": "cartopol~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "mask",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            145,
            205,
            22
          ],
          "text": "index~ qmw_living_spectral_mask",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "smooth",
          "maxclass": "newobj",
          "patching_rect": [
            380,
            145,
            135,
            22
          ],
          "text": "rampsmooth~ 128 128",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "multiply",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            215,
            45,
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
          "id": "poltocar",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            275,
            80,
            22
          ],
          "text": "poltocar~",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "fftout",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            335,
            75,
            22
          ],
          "text": "fftout~ 1",
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "phase_note",
          "maxclass": "comment",
          "patching_rect": [
            275,
            270,
            440,
            44
          ],
          "text": "Original cartopol~ phase goes straight to poltocar~. Use framedelta~/frameaccum~ only for an audio phase-vocoder extension; never inject eigenfield phase deltas here."
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "fftin",
            0
          ],
          "destination": [
            "cartopol",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fftin",
            1
          ],
          "destination": [
            "cartopol",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fftin",
            2
          ],
          "destination": [
            "mask",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mask",
            0
          ],
          "destination": [
            "smooth",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "cartopol",
            0
          ],
          "destination": [
            "multiply",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "smooth",
            0
          ],
          "destination": [
            "multiply",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "multiply",
            0
          ],
          "destination": [
            "poltocar",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "cartopol",
            1
          ],
          "destination": [
            "poltocar",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "poltocar",
            0
          ],
          "destination": [
            "fftout",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "poltocar",
            1
          ],
          "destination": [
            "fftout",
            1
          ]
        }
      }
    ],
    "dependency_cache": []
  }
}
