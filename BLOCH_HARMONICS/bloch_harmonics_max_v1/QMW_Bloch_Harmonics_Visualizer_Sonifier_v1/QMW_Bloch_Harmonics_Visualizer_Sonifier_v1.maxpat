{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 8,
      "minor": 6,
      "revision": 5,
      "architecture": "x64",
      "modernui": 1
    },
    "rect": [
      50,
      50,
      1450,
      1120
    ],
    "bglocked": 0,
    "openinpresentation": 1,
    "default_fontsize": 12,
    "default_fontface": 0,
    "default_fontname": "Arial",
    "gridonopen": 1,
    "gridsize": [
      15,
      15
    ],
    "toolbarvisible": 1,
    "boxanimatetime": 200,
    "imprint": 0,
    "enablehscroll": 1,
    "enablevscroll": 1,
    "devicewidth": 0,
    "boxes": [
      {
        "box": {
          "id": "obj-1",
          "maxclass": "comment",
          "patching_rect": [
            20,
            15,
            690,
            28
          ],
          "fontsize": 18,
          "presentation": 1,
          "presentation_rect": [
            20,
            15,
            720,
            28
          ],
          "text": "BLOCH SPHERE → SPHERICAL HARMONICS SONIFIER"
        }
      },
      {
        "box": {
          "id": "obj-2",
          "maxclass": "comment",
          "patching_rect": [
            20,
            43,
            730,
            38
          ],
          "linecount": 2,
          "presentation": 1,
          "presentation_rect": [
            20,
            43,
            730,
            38
          ],
          "text": "Move θ and φ in the embedded visualization. The 15 visible Yℓm bars directly control 15 tuned oscillator amplitudes; negative bars invert phase."
        }
      },
      {
        "box": {
          "id": "obj-3",
          "maxclass": "jweb",
          "patching_rect": [
            20,
            90,
            740,
            720
          ],
          "rendermode": 0,
          "presentation": 1,
          "presentation_rect": [
            20,
            90,
            740,
            720
          ]
        }
      },
      {
        "box": {
          "id": "obj-4",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            720,
            60,
            22
          ],
          "text": "loadbang"
        }
      },
      {
        "box": {
          "id": "obj-5",
          "maxclass": "message",
          "patching_rect": [
            800,
            750,
            225,
            22
          ],
          "text": "readfile bloch-harmonics-max-direct.html"
        }
      },
      {
        "box": {
          "id": "obj-6",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            90,
            120,
            22
          ],
          "text": "route maxmessage"
        }
      },
      {
        "box": {
          "id": "obj-7",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            120,
            80,
            22
          ],
          "text": "route state"
        }
      },
      {
        "box": {
          "id": "obj-8",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            150,
            570,
            22
          ],
          "text": "unpack f f f f f f f f f f f f f f f f f f f f"
        }
      },
      {
        "box": {
          "id": "obj-9",
          "maxclass": "comment",
          "patching_rect": [
            790,
            205,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            110,
            110,
            20
          ],
          "text": "θ (degrees)"
        }
      },
      {
        "box": {
          "id": "obj-10",
          "maxclass": "flonum",
          "patching_rect": [
            900,
            200,
            95,
            24
          ],
          "format": 6,
          "presentation": 1,
          "presentation_rect": [
            900,
            105,
            95,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-11",
          "maxclass": "comment",
          "patching_rect": [
            790,
            259,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            164,
            110,
            20
          ],
          "text": "φ (degrees)"
        }
      },
      {
        "box": {
          "id": "obj-12",
          "maxclass": "flonum",
          "patching_rect": [
            900,
            254,
            95,
            24
          ],
          "format": 6,
          "presentation": 1,
          "presentation_rect": [
            900,
            159,
            95,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-13",
          "maxclass": "comment",
          "patching_rect": [
            790,
            313,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            218,
            110,
            20
          ],
          "text": "Bloch X"
        }
      },
      {
        "box": {
          "id": "obj-14",
          "maxclass": "flonum",
          "patching_rect": [
            900,
            308,
            95,
            24
          ],
          "format": 6,
          "presentation": 1,
          "presentation_rect": [
            900,
            213,
            95,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-15",
          "maxclass": "comment",
          "patching_rect": [
            790,
            367,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            272,
            110,
            20
          ],
          "text": "Bloch Y"
        }
      },
      {
        "box": {
          "id": "obj-16",
          "maxclass": "flonum",
          "patching_rect": [
            900,
            362,
            95,
            24
          ],
          "format": 6,
          "presentation": 1,
          "presentation_rect": [
            900,
            267,
            95,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-17",
          "maxclass": "comment",
          "patching_rect": [
            790,
            421,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            326,
            110,
            20
          ],
          "text": "Bloch Z"
        }
      },
      {
        "box": {
          "id": "obj-18",
          "maxclass": "flonum",
          "patching_rect": [
            900,
            416,
            95,
            24
          ],
          "format": 6,
          "presentation": 1,
          "presentation_rect": [
            900,
            321,
            95,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-19",
          "maxclass": "comment",
          "patching_rect": [
            790,
            175,
            260,
            20
          ],
          "fontsize": 14,
          "presentation": 1,
          "presentation_rect": [
            790,
            80,
            280,
            20
          ],
          "text": "Live state from the animation"
        }
      },
      {
        "box": {
          "id": "obj-20",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            470,
            90,
            22
          ],
          "text": "cycle~ 110"
        }
      },
      {
        "box": {
          "id": "obj-21",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            498,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-22",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            525,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-23",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            552,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-24",
          "maxclass": "newobj",
          "patching_rect": [
            886,
            552,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-25",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            470,
            90,
            22
          ],
          "text": "cycle~ 138.59"
        }
      },
      {
        "box": {
          "id": "obj-26",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            498,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-27",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            525,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-28",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            552,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-29",
          "maxclass": "newobj",
          "patching_rect": [
            1021,
            552,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-30",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            470,
            90,
            22
          ],
          "text": "cycle~ 164.81"
        }
      },
      {
        "box": {
          "id": "obj-31",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            498,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-32",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            525,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-33",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            552,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-34",
          "maxclass": "newobj",
          "patching_rect": [
            1156,
            552,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-35",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            470,
            90,
            22
          ],
          "text": "cycle~ 220"
        }
      },
      {
        "box": {
          "id": "obj-36",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            498,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-37",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            525,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-38",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            552,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-39",
          "maxclass": "newobj",
          "patching_rect": [
            1291,
            552,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-40",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            470,
            90,
            22
          ],
          "text": "cycle~ 246.94"
        }
      },
      {
        "box": {
          "id": "obj-41",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            498,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-42",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            525,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-43",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            552,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-44",
          "maxclass": "newobj",
          "patching_rect": [
            1426,
            552,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-45",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            585,
            90,
            22
          ],
          "text": "cycle~ 277.18"
        }
      },
      {
        "box": {
          "id": "obj-46",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            613,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-47",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            640,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-48",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            667,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-49",
          "maxclass": "newobj",
          "patching_rect": [
            886,
            667,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-50",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            585,
            90,
            22
          ],
          "text": "cycle~ 311.13"
        }
      },
      {
        "box": {
          "id": "obj-51",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            613,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-52",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            640,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-53",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            667,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-54",
          "maxclass": "newobj",
          "patching_rect": [
            1021,
            667,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-55",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            585,
            90,
            22
          ],
          "text": "cycle~ 349.23"
        }
      },
      {
        "box": {
          "id": "obj-56",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            613,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-57",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            640,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-58",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            667,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-59",
          "maxclass": "newobj",
          "patching_rect": [
            1156,
            667,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-60",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            585,
            90,
            22
          ],
          "text": "cycle~ 440"
        }
      },
      {
        "box": {
          "id": "obj-61",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            613,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-62",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            640,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-63",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            667,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-64",
          "maxclass": "newobj",
          "patching_rect": [
            1291,
            667,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-65",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            585,
            90,
            22
          ],
          "text": "cycle~ 493.88"
        }
      },
      {
        "box": {
          "id": "obj-66",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            613,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-67",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            640,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-68",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            667,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-69",
          "maxclass": "newobj",
          "patching_rect": [
            1426,
            667,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-70",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            700,
            90,
            22
          ],
          "text": "cycle~ 554.37"
        }
      },
      {
        "box": {
          "id": "obj-71",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            728,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-72",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            755,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-73",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            782,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-74",
          "maxclass": "newobj",
          "patching_rect": [
            886,
            782,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-75",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            700,
            90,
            22
          ],
          "text": "cycle~ 622.25"
        }
      },
      {
        "box": {
          "id": "obj-76",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            728,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-77",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            755,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-78",
          "maxclass": "newobj",
          "patching_rect": [
            935,
            782,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-79",
          "maxclass": "newobj",
          "patching_rect": [
            1021,
            782,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-80",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            700,
            90,
            22
          ],
          "text": "cycle~ 698.46"
        }
      },
      {
        "box": {
          "id": "obj-81",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            728,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-82",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            755,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-83",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            782,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-84",
          "maxclass": "newobj",
          "patching_rect": [
            1156,
            782,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-85",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            700,
            90,
            22
          ],
          "text": "cycle~ 783.99"
        }
      },
      {
        "box": {
          "id": "obj-86",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            728,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-87",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            755,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-88",
          "maxclass": "newobj",
          "patching_rect": [
            1205,
            782,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-89",
          "maxclass": "newobj",
          "patching_rect": [
            1291,
            782,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-90",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            700,
            90,
            22
          ],
          "text": "cycle~ 880"
        }
      },
      {
        "box": {
          "id": "obj-91",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            728,
            58,
            22
          ],
          "text": "* 0.12"
        }
      },
      {
        "box": {
          "id": "obj-92",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            755,
            78,
            22
          ],
          "text": "pack 0. 40"
        }
      },
      {
        "box": {
          "id": "obj-93",
          "maxclass": "newobj",
          "patching_rect": [
            1340,
            782,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-94",
          "maxclass": "newobj",
          "patching_rect": [
            1426,
            782,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-95",
          "maxclass": "newobj",
          "patching_rect": [
            1105,
            840,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-96",
          "maxclass": "newobj",
          "patching_rect": [
            1160,
            840,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-97",
          "maxclass": "newobj",
          "patching_rect": [
            1050,
            868,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-98",
          "maxclass": "newobj",
          "patching_rect": [
            1105,
            868,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-99",
          "maxclass": "newobj",
          "patching_rect": [
            1160,
            868,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-100",
          "maxclass": "newobj",
          "patching_rect": [
            1050,
            896,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-101",
          "maxclass": "newobj",
          "patching_rect": [
            1105,
            896,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-102",
          "maxclass": "newobj",
          "patching_rect": [
            1160,
            896,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-103",
          "maxclass": "newobj",
          "patching_rect": [
            1050,
            924,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-104",
          "maxclass": "newobj",
          "patching_rect": [
            1105,
            924,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-105",
          "maxclass": "newobj",
          "patching_rect": [
            1160,
            924,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-106",
          "maxclass": "newobj",
          "patching_rect": [
            1050,
            952,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-107",
          "maxclass": "newobj",
          "patching_rect": [
            1105,
            952,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-108",
          "maxclass": "newobj",
          "patching_rect": [
            1160,
            952,
            40,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-109",
          "maxclass": "newobj",
          "patching_rect": [
            1210,
            1000,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-110",
          "maxclass": "newobj",
          "patching_rect": [
            1120,
            930,
            48,
            22
          ],
          "text": "dbtoa"
        }
      },
      {
        "box": {
          "id": "obj-111",
          "maxclass": "newobj",
          "patching_rect": [
            1120,
            960,
            78,
            22
          ],
          "text": "pack 0. 60"
        }
      },
      {
        "box": {
          "id": "obj-112",
          "maxclass": "newobj",
          "patching_rect": [
            1120,
            990,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-113",
          "maxclass": "newobj",
          "patching_rect": [
            1210,
            1030,
            95,
            22
          ],
          "text": "clip~ -0.9 0.9"
        }
      },
      {
        "box": {
          "id": "obj-114",
          "maxclass": "comment",
          "patching_rect": [
            790,
            485,
            125,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            405,
            125,
            20
          ],
          "text": "Master level (dB)"
        }
      },
      {
        "box": {
          "id": "obj-115",
          "maxclass": "flonum",
          "patching_rect": [
            920,
            480,
            70,
            24
          ],
          "minimum": -60,
          "maximum": 0,
          "presentation": 1,
          "presentation_rect": [
            920,
            400,
            70,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-116",
          "maxclass": "newobj",
          "patching_rect": [
            1000,
            480,
            85,
            22
          ],
          "text": "loadmess -18."
        }
      },
      {
        "box": {
          "id": "obj-117",
          "maxclass": "meter~",
          "patching_rect": [
            790,
            530,
            200,
            16
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            450,
            200,
            16
          ]
        }
      },
      {
        "box": {
          "id": "obj-118",
          "maxclass": "comment",
          "patching_rect": [
            790,
            575,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            500,
            100,
            20
          ],
          "text": "Audio on/off"
        }
      },
      {
        "box": {
          "id": "obj-119",
          "maxclass": "ezdac~",
          "patching_rect": [
            900,
            565,
            48,
            48
          ],
          "local": 1,
          "presentation": 1,
          "presentation_rect": [
            900,
            490,
            48,
            48
          ]
        }
      },
      {
        "box": {
          "id": "obj-120",
          "maxclass": "comment",
          "patching_rect": [
            790,
            640,
            220,
            22
          ],
          "fontsize": 14,
          "presentation": 1,
          "presentation_rect": [
            790,
            570,
            240,
            22
          ],
          "text": "Sonification mapping"
        }
      },
      {
        "box": {
          "id": "obj-121",
          "maxclass": "comment",
          "patching_rect": [
            790,
            670,
            580,
            45
          ],
          "linecount": 2,
          "presentation": 1,
          "presentation_rect": [
            790,
            600,
            580,
            45
          ],
          "text": "Degree 1: low triad  •  Degree 2: middle pentad  •  Degree 3: upper septad\\nBar magnitude → loudness; bar sign → oscillator phase. 40 ms smoothing prevents zipper noise."
        }
      },
      {
        "box": {
          "id": "obj-122",
          "maxclass": "comment",
          "patching_rect": [
            790,
            730,
            500,
            22
          ],
          "textcolor": [
            0.45,
            0.45,
            0.45,
            1
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            665,
            520,
            22
          ],
          "text": "Runtime asset: bloch-harmonics-max.html must remain beside this patch."
        }
      },
      {
        "box": {
          "id": "obj-123",
          "maxclass": "newobj",
          "patching_rect": [
            940,
            90,
            75,
            22
          ],
          "text": "route state"
        }
      },
      {
        "box": {
          "id": "obj-124",
          "maxclass": "button",
          "patching_rect": [
            1030,
            90,
            24,
            24
          ],
          "presentation": 1,
          "presentation_rect": [
            1030,
            80,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-125",
          "maxclass": "comment",
          "patching_rect": [
            1060,
            92,
            160,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            1060,
            82,
            180,
            20
          ],
          "text": "harmonic bridge activity"
        }
      },
      {
        "box": {
          "id": "obj-126",
          "maxclass": "newobj",
          "patching_rect": [
            800,
            440,
            92,
            22
          ],
          "text": "loadmess 0.35"
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "obj-4",
            0
          ],
          "destination": [
            "obj-5",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-5",
            0
          ],
          "destination": [
            "obj-3",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-3",
            0
          ],
          "destination": [
            "obj-6",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-3",
            0
          ],
          "destination": [
            "obj-123",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-123",
            0
          ],
          "destination": [
            "obj-8",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-123",
            0
          ],
          "destination": [
            "obj-124",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-6",
            0
          ],
          "destination": [
            "obj-7",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-7",
            0
          ],
          "destination": [
            "obj-8",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-7",
            0
          ],
          "destination": [
            "obj-124",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-126",
            0
          ],
          "destination": [
            "obj-21",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            0
          ],
          "destination": [
            "obj-10",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            1
          ],
          "destination": [
            "obj-12",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            2
          ],
          "destination": [
            "obj-14",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            3
          ],
          "destination": [
            "obj-16",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            4
          ],
          "destination": [
            "obj-18",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            5
          ],
          "destination": [
            "obj-21",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-21",
            0
          ],
          "destination": [
            "obj-22",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-22",
            0
          ],
          "destination": [
            "obj-23",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-20",
            0
          ],
          "destination": [
            "obj-24",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-23",
            0
          ],
          "destination": [
            "obj-24",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            6
          ],
          "destination": [
            "obj-26",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-26",
            0
          ],
          "destination": [
            "obj-27",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-27",
            0
          ],
          "destination": [
            "obj-28",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-25",
            0
          ],
          "destination": [
            "obj-29",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-28",
            0
          ],
          "destination": [
            "obj-29",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            7
          ],
          "destination": [
            "obj-31",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-31",
            0
          ],
          "destination": [
            "obj-32",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-32",
            0
          ],
          "destination": [
            "obj-33",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-30",
            0
          ],
          "destination": [
            "obj-34",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-33",
            0
          ],
          "destination": [
            "obj-34",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            8
          ],
          "destination": [
            "obj-36",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-36",
            0
          ],
          "destination": [
            "obj-37",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-37",
            0
          ],
          "destination": [
            "obj-38",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-35",
            0
          ],
          "destination": [
            "obj-39",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-38",
            0
          ],
          "destination": [
            "obj-39",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            9
          ],
          "destination": [
            "obj-41",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-41",
            0
          ],
          "destination": [
            "obj-42",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-42",
            0
          ],
          "destination": [
            "obj-43",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-40",
            0
          ],
          "destination": [
            "obj-44",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-43",
            0
          ],
          "destination": [
            "obj-44",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            10
          ],
          "destination": [
            "obj-46",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-46",
            0
          ],
          "destination": [
            "obj-47",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-47",
            0
          ],
          "destination": [
            "obj-48",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-45",
            0
          ],
          "destination": [
            "obj-49",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-48",
            0
          ],
          "destination": [
            "obj-49",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            11
          ],
          "destination": [
            "obj-51",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-51",
            0
          ],
          "destination": [
            "obj-52",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-52",
            0
          ],
          "destination": [
            "obj-53",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-50",
            0
          ],
          "destination": [
            "obj-54",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-53",
            0
          ],
          "destination": [
            "obj-54",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            12
          ],
          "destination": [
            "obj-56",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-56",
            0
          ],
          "destination": [
            "obj-57",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-57",
            0
          ],
          "destination": [
            "obj-58",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-55",
            0
          ],
          "destination": [
            "obj-59",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-58",
            0
          ],
          "destination": [
            "obj-59",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            13
          ],
          "destination": [
            "obj-61",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-61",
            0
          ],
          "destination": [
            "obj-62",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-62",
            0
          ],
          "destination": [
            "obj-63",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-60",
            0
          ],
          "destination": [
            "obj-64",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-63",
            0
          ],
          "destination": [
            "obj-64",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            14
          ],
          "destination": [
            "obj-66",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-66",
            0
          ],
          "destination": [
            "obj-67",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-67",
            0
          ],
          "destination": [
            "obj-68",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-65",
            0
          ],
          "destination": [
            "obj-69",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-68",
            0
          ],
          "destination": [
            "obj-69",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            15
          ],
          "destination": [
            "obj-71",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-71",
            0
          ],
          "destination": [
            "obj-72",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-72",
            0
          ],
          "destination": [
            "obj-73",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-70",
            0
          ],
          "destination": [
            "obj-74",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-73",
            0
          ],
          "destination": [
            "obj-74",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            16
          ],
          "destination": [
            "obj-76",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-76",
            0
          ],
          "destination": [
            "obj-77",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-77",
            0
          ],
          "destination": [
            "obj-78",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-75",
            0
          ],
          "destination": [
            "obj-79",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-78",
            0
          ],
          "destination": [
            "obj-79",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            17
          ],
          "destination": [
            "obj-81",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-81",
            0
          ],
          "destination": [
            "obj-82",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-82",
            0
          ],
          "destination": [
            "obj-83",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-80",
            0
          ],
          "destination": [
            "obj-84",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-83",
            0
          ],
          "destination": [
            "obj-84",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            18
          ],
          "destination": [
            "obj-86",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-86",
            0
          ],
          "destination": [
            "obj-87",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-87",
            0
          ],
          "destination": [
            "obj-88",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-85",
            0
          ],
          "destination": [
            "obj-89",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-88",
            0
          ],
          "destination": [
            "obj-89",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-8",
            19
          ],
          "destination": [
            "obj-91",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-91",
            0
          ],
          "destination": [
            "obj-92",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-92",
            0
          ],
          "destination": [
            "obj-93",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-90",
            0
          ],
          "destination": [
            "obj-94",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-93",
            0
          ],
          "destination": [
            "obj-94",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-24",
            0
          ],
          "destination": [
            "obj-95",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-29",
            0
          ],
          "destination": [
            "obj-95",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-95",
            0
          ],
          "destination": [
            "obj-96",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-34",
            0
          ],
          "destination": [
            "obj-96",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-96",
            0
          ],
          "destination": [
            "obj-97",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-39",
            0
          ],
          "destination": [
            "obj-97",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-97",
            0
          ],
          "destination": [
            "obj-98",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-44",
            0
          ],
          "destination": [
            "obj-98",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-98",
            0
          ],
          "destination": [
            "obj-99",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-49",
            0
          ],
          "destination": [
            "obj-99",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-99",
            0
          ],
          "destination": [
            "obj-100",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-54",
            0
          ],
          "destination": [
            "obj-100",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-100",
            0
          ],
          "destination": [
            "obj-101",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-59",
            0
          ],
          "destination": [
            "obj-101",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-101",
            0
          ],
          "destination": [
            "obj-102",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-64",
            0
          ],
          "destination": [
            "obj-102",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-102",
            0
          ],
          "destination": [
            "obj-103",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-69",
            0
          ],
          "destination": [
            "obj-103",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-103",
            0
          ],
          "destination": [
            "obj-104",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-74",
            0
          ],
          "destination": [
            "obj-104",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-104",
            0
          ],
          "destination": [
            "obj-105",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-79",
            0
          ],
          "destination": [
            "obj-105",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-105",
            0
          ],
          "destination": [
            "obj-106",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-84",
            0
          ],
          "destination": [
            "obj-106",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-106",
            0
          ],
          "destination": [
            "obj-107",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-89",
            0
          ],
          "destination": [
            "obj-107",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-107",
            0
          ],
          "destination": [
            "obj-108",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-94",
            0
          ],
          "destination": [
            "obj-108",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-110",
            0
          ],
          "destination": [
            "obj-111",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-111",
            0
          ],
          "destination": [
            "obj-112",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-108",
            0
          ],
          "destination": [
            "obj-109",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-112",
            0
          ],
          "destination": [
            "obj-109",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-109",
            0
          ],
          "destination": [
            "obj-113",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-116",
            0
          ],
          "destination": [
            "obj-115",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-115",
            0
          ],
          "destination": [
            "obj-110",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-113",
            0
          ],
          "destination": [
            "obj-117",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-113",
            0
          ],
          "destination": [
            "obj-119",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-113",
            0
          ],
          "destination": [
            "obj-119",
            1
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "bloch-harmonics-max-direct.html",
        "type": "TEXT",
        "implicit": 1
      }
    ],
    "autosave": 0
  }
}
