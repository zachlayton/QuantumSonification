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
      70,
      50,
      1280,
      900
    ],
    "gridsize": [
      15,
      15
    ],
    "boxes": [
      {
        "box": {
          "id": "obj-1",
          "maxclass": "comment",
          "patching_rect": [
            24,
            18,
            1020,
            28
          ],
          "text": "QMW QUANTUM CHLADNI SYNTH v1 \u2014 Jitter matrix instrument",
          "fontsize": 18,
          "fontface": 1
        }
      },
      {
        "box": {
          "id": "obj-2",
          "maxclass": "comment",
          "patching_rect": [
            24,
            48,
            1080,
            36
          ],
          "text": "Laplace\u2013Beltrami eigenbasis \u00d7 complex quantum amplitudes in jit.la.mult; jit.bfg deforms the sampled surface field; jit.spill exposes modal planes only at list/audio boundaries.",
          "linecount": 2
        }
      },
      {
        "box": {
          "id": "obj-3",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            105,
            145,
            22
          ],
          "text": "udpreceive 7470 cnmat"
        }
      },
      {
        "box": {
          "id": "obj-4",
          "maxclass": "newobj",
          "patching_rect": [
            185,
            105,
            130,
            22
          ],
          "text": "OpenSoundControl"
        }
      },
      {
        "box": {
          "id": "obj-5",
          "maxclass": "newobj",
          "patching_rect": [
            330,
            105,
            135,
            22
          ],
          "text": "OSC-route /qchladni"
        }
      },
      {
        "box": {
          "id": "obj-6",
          "maxclass": "newobj",
          "patching_rect": [
            480,
            105,
            405,
            22
          ],
          "text": "OSC-route /begin /mode /end /strike /status /geometry"
        }
      },
      {
        "box": {
          "id": "obj-7",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            105,
            220,
            22
          ],
          "text": "OSC-route /begin /vertex /end"
        }
      },
      {
        "box": {
          "id": "obj-8",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            145,
            104,
            22
          ],
          "text": "prepend begin"
        }
      },
      {
        "box": {
          "id": "obj-9",
          "maxclass": "newobj",
          "patching_rect": [
            140,
            145,
            104,
            22
          ],
          "text": "prepend mode"
        }
      },
      {
        "box": {
          "id": "obj-10",
          "maxclass": "newobj",
          "patching_rect": [
            256,
            145,
            104,
            22
          ],
          "text": "prepend end"
        }
      },
      {
        "box": {
          "id": "obj-11",
          "maxclass": "newobj",
          "patching_rect": [
            372,
            145,
            104,
            22
          ],
          "text": "prepend strike"
        }
      },
      {
        "box": {
          "id": "obj-12",
          "maxclass": "newobj",
          "patching_rect": [
            488,
            145,
            104,
            22
          ],
          "text": "prepend status"
        }
      },
      {
        "box": {
          "id": "obj-13",
          "maxclass": "newobj",
          "patching_rect": [
            620,
            145,
            143,
            22
          ],
          "text": "prepend geometry_begin"
        }
      },
      {
        "box": {
          "id": "obj-14",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            145,
            143,
            22
          ],
          "text": "prepend geometry_vertex"
        }
      },
      {
        "box": {
          "id": "obj-15",
          "maxclass": "newobj",
          "patching_rect": [
            930,
            145,
            143,
            22
          ],
          "text": "prepend geometry_end"
        }
      },
      {
        "box": {
          "id": "obj-16",
          "maxclass": "newobj",
          "patching_rect": [
            425,
            190,
            270,
            22
          ],
          "text": "js qmw_quantum_chladni_router_v1.js",
          "numinlets": 4,
          "numoutlets": 9
        }
      },
      {
        "box": {
          "id": "obj-17",
          "maxclass": "flonum",
          "patching_rect": [
            24,
            215,
            70,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0
        }
      },
      {
        "box": {
          "id": "obj-18",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            185,
            70,
            22
          ],
          "text": "loadmess 1."
        }
      },
      {
        "box": {
          "id": "obj-19",
          "maxclass": "flonum",
          "patching_rect": [
            118,
            215,
            70,
            22
          ],
          "minimum": 0.1,
          "maximum": 8.0
        }
      },
      {
        "box": {
          "id": "obj-20",
          "maxclass": "newobj",
          "patching_rect": [
            118,
            185,
            70,
            22
          ],
          "text": "loadmess 1."
        }
      },
      {
        "box": {
          "id": "obj-21",
          "maxclass": "flonum",
          "patching_rect": [
            212,
            215,
            70,
            22
          ],
          "minimum": 0.125,
          "maximum": 8.0
        }
      },
      {
        "box": {
          "id": "obj-22",
          "maxclass": "newobj",
          "patching_rect": [
            212,
            185,
            70,
            22
          ],
          "text": "loadmess 1."
        }
      },
      {
        "box": {
          "id": "obj-23",
          "maxclass": "comment",
          "patching_rect": [
            24,
            242,
            78,
            20
          ],
          "text": "QUANTUM"
        }
      },
      {
        "box": {
          "id": "obj-24",
          "maxclass": "comment",
          "patching_rect": [
            118,
            242,
            72,
            20
          ],
          "text": "DECAY"
        }
      },
      {
        "box": {
          "id": "obj-25",
          "maxclass": "comment",
          "patching_rect": [
            212,
            242,
            92,
            20
          ],
          "text": "FREQ SCALE"
        }
      },
      {
        "box": {
          "id": "obj-26",
          "maxclass": "button",
          "patching_rect": [
            325,
            220,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-27",
          "maxclass": "message",
          "patching_rect": [
            358,
            221,
            42,
            22
          ],
          "text": "demo"
        }
      },
      {
        "box": {
          "id": "obj-28",
          "maxclass": "newobj",
          "patching_rect": [
            325,
            185,
            92,
            22
          ],
          "text": "loadmess demo"
        }
      },
      {
        "box": {
          "id": "obj-29",
          "maxclass": "comment",
          "patching_rect": [
            325,
            247,
            105,
            20
          ],
          "text": "LOCAL DEMO"
        }
      },
      {
        "box": {
          "id": "obj-30",
          "maxclass": "message",
          "patching_rect": [
            425,
            220,
            510,
            22
          ],
          "text": "waiting for Python/Jitter matrices\u2026"
        }
      },
      {
        "box": {
          "id": "obj-31",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            300,
            250,
            22
          ],
          "text": "jit.matrix qchladni_modes 6 float32 24 1"
        }
      },
      {
        "box": {
          "id": "obj-32",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            335,
            108,
            22
          ],
          "text": "jit.unpack 6"
        }
      },
      {
        "box": {
          "id": "obj-33",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            335,
            190,
            22
          ],
          "text": "jit.spill @plane 0 @listlength 24"
        }
      },
      {
        "box": {
          "id": "obj-34",
          "maxclass": "multislider",
          "patching_rect": [
            24,
            370,
            310,
            110
          ],
          "size": 24,
          "setminmax": [
            0.0,
            1.0
          ],
          "slidercolor": [
            0.2,
            0.75,
            1.0,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-35",
          "maxclass": "comment",
          "patching_rect": [
            24,
            488,
            320,
            20
          ],
          "text": "JITTER MODAL PROBABILITY PLANE \u2192 jit.spill"
        }
      },
      {
        "box": {
          "id": "obj-36",
          "maxclass": "newobj",
          "patching_rect": [
            380,
            300,
            275,
            22
          ],
          "text": "jit.matrix qchladni_amplitudes 2 float32 1 24"
        }
      },
      {
        "box": {
          "id": "obj-37",
          "maxclass": "newobj",
          "patching_rect": [
            680,
            300,
            305,
            22
          ],
          "text": "jit.matrix qchladni_eigenvectors 2 float32 24 768"
        }
      },
      {
        "box": {
          "id": "obj-38",
          "maxclass": "newobj",
          "patching_rect": [
            560,
            345,
            120,
            22
          ],
          "text": "jit.la.mult"
        }
      },
      {
        "box": {
          "id": "obj-39",
          "maxclass": "newobj",
          "patching_rect": [
            560,
            380,
            72,
            22
          ],
          "text": "jit.unpack 2"
        }
      },
      {
        "box": {
          "id": "obj-40",
          "maxclass": "newobj",
          "patching_rect": [
            710,
            430,
            290,
            22
          ],
          "text": "jit.matrix qchladni_coordinates 3 float32 1 768"
        }
      },
      {
        "box": {
          "id": "obj-41",
          "maxclass": "newobj",
          "patching_rect": [
            370,
            430,
            275,
            22
          ],
          "text": "jit.bfg 1 float32 @basis noise.gradient"
        }
      },
      {
        "box": {
          "id": "obj-42",
          "maxclass": "newobj",
          "patching_rect": [
            370,
            465,
            125,
            22
          ],
          "text": "jit.op @op * @val 0.08"
        }
      },
      {
        "box": {
          "id": "obj-43",
          "maxclass": "newobj",
          "patching_rect": [
            520,
            465,
            78,
            22
          ],
          "text": "jit.op @op +"
        }
      },
      {
        "box": {
          "id": "obj-44",
          "maxclass": "newobj",
          "patching_rect": [
            620,
            510,
            505,
            22
          ],
          "text": "jit.expr @expr \"in[0].p[0]\" \"in[0].p[1]\" \"in[0].p[2]+in[1].p[0]*0.22\""
        }
      },
      {
        "box": {
          "id": "obj-45",
          "maxclass": "toggle",
          "patching_rect": [
            1020,
            300,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-46",
          "maxclass": "newobj",
          "patching_rect": [
            1020,
            335,
            220,
            22
          ],
          "text": "jit.world qchladni @size 700 560 @erase_color 0.015 0.02 0.035 1"
        }
      },
      {
        "box": {
          "id": "obj-47",
          "maxclass": "newobj",
          "patching_rect": [
            820,
            555,
            400,
            22
          ],
          "text": "jit.gl.mesh qchladni @draw_mode points @point_size 3 @color 0.15 0.72 1. 1."
        }
      },
      {
        "box": {
          "id": "obj-48",
          "maxclass": "newobj",
          "patching_rect": [
            820,
            590,
            230,
            22
          ],
          "text": "jit.gl.handle qchladni @auto_rotate 1"
        }
      },
      {
        "box": {
          "id": "obj-49",
          "maxclass": "comment",
          "patching_rect": [
            710,
            620,
            500,
            36
          ],
          "text": "Actual eigenfield displacement = V \u00d7 a. jit.bfg adds a shallow procedural deformation evaluated at the same surface coordinates.",
          "linecount": 2
        }
      },
      {
        "box": {
          "id": "obj-50",
          "maxclass": "newobj",
          "patching_rect": [
            185,
            610,
            390,
            22
          ],
          "text": "resonators~ smooth 110. 0.45 3.5 164.81 0.32 3.1 220. 0.25 2.8 277.18 0.20 2.5 329.63 0.16 2.2 440. 0.13 1.9 554.37 0.10 1.6 659.25 0.08 1.4"
        }
      },
      {
        "box": {
          "id": "obj-51",
          "maxclass": "newobj",
          "patching_rect": [
            595,
            610,
            390,
            22
          ],
          "text": "resonators~ smooth 110. 0.45 3.5 164.81 0.32 3.1 220. 0.25 2.8 277.18 0.20 2.5 329.63 0.16 2.2 440. 0.13 1.9 554.37 0.10 1.6 659.25 0.08 1.4"
        }
      },
      {
        "box": {
          "id": "obj-52",
          "maxclass": "live.gain~",
          "patching_rect": [
            330,
            655,
            110,
            120
          ],
          "parameter_enable": 1
        }
      },
      {
        "box": {
          "id": "obj-53",
          "maxclass": "newobj",
          "patching_rect": [
            346,
            795,
            78,
            22
          ],
          "text": "ezdac~"
        }
      },
      {
        "box": {
          "id": "obj-54",
          "maxclass": "button",
          "patching_rect": [
            24,
            610,
            28,
            28
          ]
        }
      },
      {
        "box": {
          "id": "obj-55",
          "maxclass": "newobj",
          "patching_rect": [
            65,
            580,
            45,
            22
          ],
          "text": "t b 1"
        }
      },
      {
        "box": {
          "id": "obj-56",
          "maxclass": "message",
          "patching_rect": [
            65,
            613,
            38,
            22
          ],
          "text": "0.72"
        }
      },
      {
        "box": {
          "id": "obj-57",
          "maxclass": "comment",
          "patching_rect": [
            24,
            646,
            125,
            20
          ],
          "text": "STRIKE"
        }
      },
      {
        "box": {
          "id": "obj-58",
          "maxclass": "toggle",
          "patching_rect": [
            24,
            725,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-59",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            690,
            70,
            22
          ],
          "text": "loadmess 1"
        }
      },
      {
        "box": {
          "id": "obj-60",
          "maxclass": "newobj",
          "patching_rect": [
            60,
            725,
            210,
            22
          ],
          "text": "o.pack /qchladni/control/run"
        }
      },
      {
        "box": {
          "id": "obj-61",
          "maxclass": "button",
          "patching_rect": [
            24,
            765,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-62",
          "maxclass": "newobj",
          "patching_rect": [
            60,
            765,
            242,
            22
          ],
          "text": "o.pack /qchladni/control/measure"
        }
      },
      {
        "box": {
          "id": "obj-63",
          "maxclass": "newobj",
          "patching_rect": [
            165,
            810,
            145,
            22
          ],
          "text": "udpsend 127.0.0.1 7471"
        }
      },
      {
        "box": {
          "id": "obj-64",
          "maxclass": "newobj",
          "patching_rect": [
            320,
            765,
            62,
            22
          ],
          "text": "loadbang"
        }
      },
      {
        "box": {
          "id": "obj-65",
          "maxclass": "newobj",
          "patching_rect": [
            395,
            765,
            245,
            22
          ],
          "text": "o.pack /qchladni/control/geometry"
        }
      },
      {
        "box": {
          "id": "obj-66",
          "maxclass": "comment",
          "patching_rect": [
            315,
            835,
            720,
            20
          ],
          "text": "Start Python: python -m quantum_chladni_synth_v1.quantum_chladni_controller_v1"
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "obj-6",
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
            "obj-6",
            1
          ],
          "destination": [
            "obj-9",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-6",
            2
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
            "obj-6",
            3
          ],
          "destination": [
            "obj-11",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-6",
            4
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
            "obj-7",
            0
          ],
          "destination": [
            "obj-13",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-7",
            1
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
            "obj-7",
            2
          ],
          "destination": [
            "obj-15",
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
            "obj-16",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-9",
            0
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
            "obj-10",
            0
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
            "obj-11",
            0
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
            "obj-12",
            0
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
            "obj-13",
            0
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
            "obj-14",
            0
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
            "obj-15",
            0
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
            "obj-3",
            0
          ],
          "destination": [
            "obj-4",
            0
          ]
        }
      },
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
            "obj-6",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-6",
            5
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
            "obj-18",
            0
          ],
          "destination": [
            "obj-17",
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
            "obj-19",
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
            "obj-21",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-17",
            0
          ],
          "destination": [
            "obj-16",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            0
          ],
          "destination": [
            "obj-16",
            2
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
            "obj-16",
            3
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
            "obj-16",
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
            "obj-16",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-16",
            8
          ],
          "destination": [
            "obj-30",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-16",
            3
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
            3
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
            "obj-33",
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
            "obj-16",
            4
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
            "obj-38",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-16",
            6
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
            "obj-38",
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
            "obj-16",
            5
          ],
          "destination": [
            "obj-40",
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
            "obj-41",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-16",
            7
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
            1
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
            "obj-43",
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
            "obj-45",
            0
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
            "obj-44",
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
            "obj-48",
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
            "obj-16",
            0
          ],
          "destination": [
            "obj-50",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-16",
            1
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
            "obj-16",
            2
          ],
          "destination": [
            "obj-50",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-16",
            2
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
            "obj-54",
            0
          ],
          "destination": [
            "obj-55",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-55",
            1
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
            "obj-55",
            0
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
            "obj-50",
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
            "obj-51",
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
            "obj-52",
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
            1
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
            "obj-52",
            1
          ],
          "destination": [
            "obj-53",
            1
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
            "obj-58",
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
            "obj-60",
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
            "obj-63",
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
            "obj-64",
            0
          ],
          "destination": [
            "obj-65",
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
            "obj-63",
            0
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "qmw_quantum_chladni_router_v1.js",
        "type": "TEXT"
      },
      {
        "name": "OpenSoundControl.mxo",
        "type": "iLaX"
      },
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
      },
      {
        "name": "o.pack.mxo",
        "type": "iLaX"
      },
      {
        "name": "jit.bfg.mxo",
        "type": "iLaX"
      },
      {
        "name": "jit.spill.mxo",
        "type": "iLaX"
      },
      {
        "name": "jit.la.mult.mxo",
        "type": "iLaX"
      },
      {
        "name": "resonators~.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
