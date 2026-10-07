{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 9,
      "minor": 0,
      "revision": 7,
      "architecture": "x64",
      "modernui": 1
    },
    "classnamespace": "box",
    "rect": [
      0,
      0,
      1160,
      620
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            18,
            760,
            30
          ],
          "text": "QMW Direct Analytic Audition 16 v1",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": [],
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "desc",
          "maxclass": "comment",
          "patching_rect": [
            25,
            50,
            990,
            20
          ],
          "text": "Aligned pre/post complex rails share one phase rotator: conductor phase + per-harmonic spread + continuous SSB motion.",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "pre-i",
          "maxclass": "inlet",
          "patching_rect": [
            35,
            105,
            30,
            30
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre-q",
          "maxclass": "inlet",
          "patching_rect": [
            175,
            105,
            30,
            30
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "post-r",
          "maxclass": "inlet",
          "patching_rect": [
            315,
            105,
            30,
            30
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "post-i",
          "maxclass": "inlet",
          "patching_rect": [
            455,
            105,
            30,
            30
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "phase",
          "maxclass": "inlet",
          "patching_rect": [
            595,
            105,
            30,
            30
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "control",
          "maxclass": "inlet",
          "patching_rect": [
            790,
            105,
            30,
            30
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "labels",
          "maxclass": "comment",
          "patching_rect": [
            25,
            80,
            760,
            20
          ],
          "text": "pre I             pre Q             rho real           rho imag           phase[16]                       control",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "smooth",
          "maxclass": "newobj",
          "patching_rect": [
            570,
            170,
            160,
            22
          ],
          "text": "mc.rampsmooth~ 2400 2400",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "gen",
          "maxclass": "newobj",
          "patching_rect": [
            245,
            245,
            535,
            22
          ],
          "text": "mc.gen~ @gen qmw_analytic_phase_projector16_v1 @chans 16",
          "numinlets": 5,
          "numoutlets": 3,
          "outlettype": [
            "multichannelsignal",
            "multichannelsignal",
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "route",
          "maxclass": "newobj",
          "patching_rect": [
            790,
            170,
            345,
            22
          ],
          "text": "route hilbertdepth phasedepth phasespread phasebias ssbhz deltagain",
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
          "id": "h",
          "maxclass": "newobj",
          "patching_rect": [
            790,
            215,
            135,
            22
          ],
          "text": "prepend hilbert_depth",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pd",
          "maxclass": "newobj",
          "patching_rect": [
            790,
            250,
            125,
            22
          ],
          "text": "prepend phase_depth",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "ps",
          "maxclass": "newobj",
          "patching_rect": [
            790,
            285,
            132,
            22
          ],
          "text": "prepend phase_spread",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pb",
          "maxclass": "newobj",
          "patching_rect": [
            790,
            320,
            120,
            22
          ],
          "text": "prepend phase_bias",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "ssb",
          "maxclass": "newobj",
          "patching_rect": [
            790,
            355,
            105,
            22
          ],
          "text": "prepend ssb_hz",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "dg",
          "maxclass": "newobj",
          "patching_rect": [
            790,
            390,
            115,
            22
          ],
          "text": "prepend delta_gain",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "unknown",
          "maxclass": "newobj",
          "patching_rect": [
            920,
            430,
            185,
            22
          ],
          "text": "print qmw.analytic.unknown",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre-out",
          "maxclass": "outlet",
          "patching_rect": [
            280,
            455,
            30,
            30
          ],
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "post-out",
          "maxclass": "outlet",
          "patching_rect": [
            450,
            455,
            30,
            30
          ],
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "delta-out",
          "maxclass": "outlet",
          "patching_rect": [
            620,
            455,
            30,
            30
          ],
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "out-label",
          "maxclass": "comment",
          "patching_rect": [
            240,
            500,
            500,
            20
          ],
          "text": "analytic pre-rho                 full matrix wet                 matrix-only delta",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": []
        }
      },
      {
        "box": {
          "id": "load",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            250,
            60,
            22
          ],
          "text": "loadbang",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "defaults",
          "maxclass": "message",
          "patching_rect": [
            25,
            285,
            190,
            22
          ],
          "text": "hilbertdepth 1., phasedepth 1., phasespread 0., ssbhz 0., deltagain 2.",
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
            "pre-i",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pre-q",
            0
          ],
          "destination": [
            "gen",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "post-r",
            0
          ],
          "destination": [
            "gen",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "post-i",
            0
          ],
          "destination": [
            "gen",
            3
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
            "smooth",
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
            "gen",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "control",
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
            "h",
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
            "pd",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            2
          ],
          "destination": [
            "ps",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            3
          ],
          "destination": [
            "pb",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            4
          ],
          "destination": [
            "ssb",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            5
          ],
          "destination": [
            "dg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            6
          ],
          "destination": [
            "unknown",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pd",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ps",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pb",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ssb",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dg",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gen",
            0
          ],
          "destination": [
            "pre-out",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gen",
            1
          ],
          "destination": [
            "post-out",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gen",
            2
          ],
          "destination": [
            "delta-out",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "defaults",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "defaults",
            0
          ],
          "destination": [
            "route",
            0
          ]
        }
      }
    ]
  }
}
