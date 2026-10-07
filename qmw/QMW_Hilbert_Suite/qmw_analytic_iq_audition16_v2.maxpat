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
      1280,
      680
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            18,
            850,
            30
          ],
          "text": "QMW Norm-Preserving Analytic I/Q Audition 16 v2",
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
            1120,
            40
          ],
          "text": "Both quadrature rails survive rotation. Real audio appears only at the explicit final projection; full pre/post IQ rails remain available.",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": [],
          "linecount": 2
        }
      },
      {
        "box": {
          "id": "pre-i",
          "maxclass": "inlet",
          "patching_rect": [
            35,
            115,
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
            180,
            115,
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
            325,
            115,
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
          "id": "post-q",
          "maxclass": "inlet",
          "patching_rect": [
            470,
            115,
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
            615,
            115,
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
            760,
            115,
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
          "id": "smooth",
          "maxclass": "newobj",
          "patching_rect": [
            615,
            180,
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
            220,
            270,
            565,
            22
          ],
          "text": "mc.gen~ @gen qmw_analytic_iq_rotator16_v2 @chans 16",
          "numinlets": 5,
          "numoutlets": 7,
          "outlettype": [
            "multichannelsignal",
            "multichannelsignal",
            "multichannelsignal",
            "multichannelsignal",
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
            830,
            180,
            410,
            22
          ],
          "text": "route phasedepth phasespread phasebias ssbhz projectionangle deltagain",
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
          "id": "pd",
          "maxclass": "newobj",
          "patching_rect": [
            830,
            220,
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
            830,
            250,
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
            830,
            280,
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
            830,
            310,
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
          "id": "pa",
          "maxclass": "newobj",
          "patching_rect": [
            830,
            340,
            155,
            22
          ],
          "text": "prepend projection_angle",
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
            830,
            370,
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
            830,
            410,
            205,
            22
          ],
          "text": "print qmw.iq.v2.unknown",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pre-proj",
          "maxclass": "outlet",
          "patching_rect": [
            120,
            530,
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
          "id": "post-proj",
          "maxclass": "outlet",
          "patching_rect": [
            260,
            530,
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
          "id": "delta",
          "maxclass": "outlet",
          "patching_rect": [
            400,
            530,
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
          "id": "pre-i-out",
          "maxclass": "outlet",
          "patching_rect": [
            560,
            530,
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
          "id": "pre-q-out",
          "maxclass": "outlet",
          "patching_rect": [
            700,
            530,
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
          "id": "post-i-out",
          "maxclass": "outlet",
          "patching_rect": [
            840,
            530,
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
          "id": "post-q-out",
          "maxclass": "outlet",
          "patching_rect": [
            980,
            530,
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
          "id": "labels",
          "maxclass": "comment",
          "patching_rect": [
            75,
            575,
            1030,
            40
          ],
          "text": "PRE projection     POST projection      delta             PRE-I              PRE-Q              POST-I             POST-Q",
          "numinlets": 1,
          "numoutlets": 0,
          "outlettype": [],
          "linecount": 2
        }
      },
      {
        "box": {
          "id": "load",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            270,
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
            305,
            170,
            22
          ],
          "text": "phasedepth 1., phasespread 0., ssbhz 0., projectionangle 0., deltagain 2.",
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
            "post-i",
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
            "post-q",
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
            "pd",
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
            "ps",
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
            "pb",
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
            "ssb",
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
            "pa",
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
            "pa",
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
            4
          ],
          "destination": [
            "pre-proj",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gen",
            5
          ],
          "destination": [
            "post-proj",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gen",
            6
          ],
          "destination": [
            "delta",
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
            "pre-i-out",
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
            "pre-q-out",
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
            "post-i-out",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gen",
            3
          ],
          "destination": [
            "post-q-out",
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
