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
      1220
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
          "text": "QMW QPE \u00d7 QUANTUM CHLADNI SYNTH v1.5",
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
          "text": "Finite-register phase estimation of Laplace\u2013Beltrami eigenvalues conditions the eigenmode superposition. The same posterior drives resonator gains and jit.la.mult spatial shape.",
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
            130,
            22
          ],
          "text": "udpreceive 7400"
        }
      },
      {
        "box": {
          "id": "obj-4",
          "maxclass": "newobj",
          "patching_rect": [
            185,
            105,
            105,
            22
          ],
          "text": "OSC-route /qmw"
        }
      },
      {
        "box": {
          "id": "obj-5",
          "maxclass": "newobj",
          "patching_rect": [
            305,
            105,
            125,
            22
          ],
          "text": "OSC-route /chladni"
        }
      },
      {
        "box": {
          "id": "obj-6",
          "maxclass": "newobj",
          "patching_rect": [
            305,
            75,
            300,
            22
          ],
          "text": "OSC-route /temporal-mechanics/v1/density-clock"
        }
      },
      {
        "box": {
          "id": "obj-7",
          "maxclass": "newobj",
          "patching_rect": [
            620,
            75,
            150,
            22
          ],
          "text": "OSC-route /state /pulse"
        }
      },
      {
        "box": {
          "id": "obj-8",
          "maxclass": "newobj",
          "patching_rect": [
            450,
            105,
            520,
            22
          ],
          "text": "OSC-route /begin /mode /end /strike /status /populations /geometry"
        }
      },
      {
        "box": {
          "id": "obj-9",
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
          "id": "obj-10",
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
          "id": "obj-11",
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
          "id": "obj-12",
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
          "id": "obj-13",
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
          "id": "obj-14",
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
          "id": "obj-15",
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
          "id": "obj-16",
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
          "id": "obj-17",
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
          "id": "obj-18",
          "maxclass": "newobj",
          "patching_rect": [
            510,
            170,
            130,
            22
          ],
          "text": "prepend populations"
        }
      },
      {
        "box": {
          "id": "obj-19",
          "maxclass": "newobj",
          "patching_rect": [
            425,
            190,
            270,
            22
          ],
          "text": "js qmw_quantum_chladni_router_v1.js",
          "numinlets": 5,
          "numoutlets": 25
        }
      },
      {
        "box": {
          "id": "obj-20",
          "maxclass": "newobj",
          "patching_rect": [
            785,
            65,
            145,
            22
          ],
          "text": "prepend temporal_state"
        }
      },
      {
        "box": {
          "id": "obj-21",
          "maxclass": "newobj",
          "patching_rect": [
            785,
            90,
            145,
            22
          ],
          "text": "prepend temporal_pulse"
        }
      },
      {
        "box": {
          "id": "obj-22",
          "maxclass": "number",
          "patching_rect": [
            965,
            185,
            72,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-23",
          "maxclass": "number",
          "patching_rect": [
            1050,
            185,
            72,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-24",
          "maxclass": "comment",
          "patching_rect": [
            955,
            212,
            90,
            20
          ],
          "text": "OSC REV"
        }
      },
      {
        "box": {
          "id": "obj-25",
          "maxclass": "comment",
          "patching_rect": [
            1045,
            212,
            115,
            20
          ],
          "text": "GEOMETRY N"
        }
      },
      {
        "box": {
          "id": "obj-26",
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
          "id": "obj-27",
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
          "id": "obj-28",
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
          "id": "obj-29",
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
          "id": "obj-30",
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
          "id": "obj-31",
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
          "id": "obj-32",
          "maxclass": "flonum",
          "patching_rect": [
            306,
            280,
            70,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0
        }
      },
      {
        "box": {
          "id": "obj-33",
          "maxclass": "newobj",
          "patching_rect": [
            306,
            255,
            92,
            22
          ],
          "text": "loadmess 0.01"
        }
      },
      {
        "box": {
          "id": "obj-34",
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
          "id": "obj-35",
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
          "id": "obj-36",
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
          "id": "obj-37",
          "maxclass": "comment",
          "patching_rect": [
            306,
            305,
            112,
            20
          ],
          "text": "POPULATION GATE"
        }
      },
      {
        "box": {
          "id": "obj-38",
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
          "id": "obj-39",
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
          "id": "obj-40",
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
          "id": "obj-41",
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
          "id": "obj-42",
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
          "id": "obj-43",
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
          "id": "obj-44",
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
          "id": "obj-45",
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
          "id": "obj-46",
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
          "id": "obj-47",
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
          "id": "obj-48",
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
          "id": "obj-49",
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
          "id": "obj-50",
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
          "id": "obj-51",
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
          "id": "obj-52",
          "maxclass": "newobj",
          "patching_rect": [
            545,
            410,
            90,
            22
          ],
          "text": "jit.normalize"
        }
      },
      {
        "box": {
          "id": "obj-53",
          "maxclass": "newobj",
          "patching_rect": [
            535,
            440,
            110,
            22
          ],
          "text": "jit.op @op * @val 2."
        }
      },
      {
        "box": {
          "id": "obj-54",
          "maxclass": "newobj",
          "patching_rect": [
            535,
            470,
            110,
            22
          ],
          "text": "jit.op @op - @val 1."
        }
      },
      {
        "box": {
          "id": "obj-55",
          "maxclass": "newobj",
          "patching_rect": [
            410,
            500,
            100,
            22
          ],
          "text": "scale 0. 1. 0.04 0.55"
        }
      },
      {
        "box": {
          "id": "obj-56",
          "maxclass": "newobj",
          "patching_rect": [
            410,
            530,
            78,
            22
          ],
          "text": "prepend val"
        }
      },
      {
        "box": {
          "id": "obj-57",
          "maxclass": "newobj",
          "patching_rect": [
            525,
            500,
            130,
            22
          ],
          "text": "jit.op @op * @val 0.55"
        }
      },
      {
        "box": {
          "id": "obj-58",
          "maxclass": "newobj",
          "patching_rect": [
            525,
            535,
            190,
            22
          ],
          "text": "jit.slide @slide_up 5 @slide_down 5"
        }
      },
      {
        "box": {
          "id": "obj-59",
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
          "id": "obj-60",
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
          "id": "obj-61",
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
          "id": "obj-62",
          "maxclass": "newobj",
          "patching_rect": [
            620,
            510,
            505,
            22
          ],
          "text": "jit.expr @expr \"in[0].p[0]\" \"in[0].p[1]\" \"in[0].p[2]+in[1].p[0]\""
        }
      },
      {
        "box": {
          "id": "obj-63",
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
          "id": "obj-64",
          "maxclass": "newobj",
          "patching_rect": [
            1055,
            300,
            78,
            22
          ],
          "text": "loadmess 1"
        }
      },
      {
        "box": {
          "id": "obj-65",
          "maxclass": "newobj",
          "patching_rect": [
            1020,
            335,
            250,
            22
          ],
          "text": "jit.world qchladni @enable 1 @size 700 560 @erase_color 0.015 0.02 0.035 1"
        }
      },
      {
        "box": {
          "id": "obj-66",
          "maxclass": "newobj",
          "patching_rect": [
            710,
            475,
            430,
            22
          ],
          "text": "jit.gl.mesh qchladni @draw_mode points @point_size 2 @color 0.35 0.35 0.42 1."
        }
      },
      {
        "box": {
          "id": "obj-67",
          "maxclass": "newobj",
          "patching_rect": [
            820,
            555,
            430,
            22
          ],
          "text": "jit.gl.mesh qchladni @draw_mode points @point_size 5 @color 0.15 0.72 1. 1."
        }
      },
      {
        "box": {
          "id": "obj-68",
          "maxclass": "newobj",
          "patching_rect": [
            1020,
            370,
            260,
            22
          ],
          "text": "jit.gl.gridshape qchladni @shape sphere @scale 0.035 @color 1. 0.35 0.1 1."
        }
      },
      {
        "box": {
          "id": "obj-69",
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
          "id": "obj-70",
          "maxclass": "comment",
          "patching_rect": [
            710,
            620,
            540,
            36
          ],
          "text": "Gray = received coordinates (transport diagnostic). Blue = actual eigenfield displacement V \u00d7 a. Orange origin marker proves the GL context is rendering.",
          "linecount": 2
        }
      },
      {
        "box": {
          "id": "obj-71",
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
          "id": "obj-72",
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
          "id": "obj-73",
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
          "id": "obj-74",
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
          "id": "obj-75",
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
          "id": "obj-76",
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
          "id": "obj-77",
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
          "id": "obj-78",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            535,
            52,
            22
          ],
          "text": "change"
        }
      },
      {
        "box": {
          "id": "obj-79",
          "maxclass": "newobj",
          "patching_rect": [
            82,
            535,
            88,
            22
          ],
          "text": "speedlim 140"
        }
      },
      {
        "box": {
          "id": "obj-80",
          "maxclass": "message",
          "patching_rect": [
            176,
            535,
            38,
            22
          ],
          "text": "0.28"
        }
      },
      {
        "box": {
          "id": "obj-81",
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
          "id": "obj-82",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            875,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-83",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            902,
            64,
            22
          ],
          "text": "*~ 0.4200"
        }
      },
      {
        "box": {
          "id": "obj-84",
          "maxclass": "newobj",
          "patching_rect": [
            94,
            902,
            64,
            22
          ],
          "text": "*~ 0.0000"
        }
      },
      {
        "box": {
          "id": "obj-85",
          "maxclass": "comment",
          "patching_rect": [
            166,
            902,
            140,
            20
          ],
          "text": "|0000> BANK 1"
        }
      },
      {
        "box": {
          "id": "obj-86",
          "maxclass": "newobj",
          "patching_rect": [
            329,
            875,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-87",
          "maxclass": "newobj",
          "patching_rect": [
            329,
            902,
            64,
            22
          ],
          "text": "*~ 0.4058"
        }
      },
      {
        "box": {
          "id": "obj-88",
          "maxclass": "newobj",
          "patching_rect": [
            399,
            902,
            64,
            22
          ],
          "text": "*~ 0.1084"
        }
      },
      {
        "box": {
          "id": "obj-89",
          "maxclass": "comment",
          "patching_rect": [
            471,
            902,
            140,
            20
          ],
          "text": "|0001> BANK 2"
        }
      },
      {
        "box": {
          "id": "obj-90",
          "maxclass": "newobj",
          "patching_rect": [
            634,
            875,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-91",
          "maxclass": "newobj",
          "patching_rect": [
            634,
            902,
            64,
            22
          ],
          "text": "*~ 0.3910"
        }
      },
      {
        "box": {
          "id": "obj-92",
          "maxclass": "newobj",
          "patching_rect": [
            704,
            902,
            64,
            22
          ],
          "text": "*~ 0.1534"
        }
      },
      {
        "box": {
          "id": "obj-93",
          "maxclass": "comment",
          "patching_rect": [
            776,
            902,
            140,
            20
          ],
          "text": "|0010> BANK 3"
        }
      },
      {
        "box": {
          "id": "obj-94",
          "maxclass": "newobj",
          "patching_rect": [
            939,
            875,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-95",
          "maxclass": "newobj",
          "patching_rect": [
            939,
            902,
            64,
            22
          ],
          "text": "*~ 0.3757"
        }
      },
      {
        "box": {
          "id": "obj-96",
          "maxclass": "newobj",
          "patching_rect": [
            1009,
            902,
            64,
            22
          ],
          "text": "*~ 0.1878"
        }
      },
      {
        "box": {
          "id": "obj-97",
          "maxclass": "comment",
          "patching_rect": [
            1081,
            902,
            140,
            20
          ],
          "text": "|0011> BANK 4"
        }
      },
      {
        "box": {
          "id": "obj-98",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            945,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-99",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            972,
            64,
            22
          ],
          "text": "*~ 0.3597"
        }
      },
      {
        "box": {
          "id": "obj-100",
          "maxclass": "newobj",
          "patching_rect": [
            94,
            972,
            64,
            22
          ],
          "text": "*~ 0.2169"
        }
      },
      {
        "box": {
          "id": "obj-101",
          "maxclass": "comment",
          "patching_rect": [
            166,
            972,
            140,
            20
          ],
          "text": "|0100> BANK 5"
        }
      },
      {
        "box": {
          "id": "obj-102",
          "maxclass": "newobj",
          "patching_rect": [
            329,
            945,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-103",
          "maxclass": "newobj",
          "patching_rect": [
            329,
            972,
            64,
            22
          ],
          "text": "*~ 0.3429"
        }
      },
      {
        "box": {
          "id": "obj-104",
          "maxclass": "newobj",
          "patching_rect": [
            399,
            972,
            64,
            22
          ],
          "text": "*~ 0.2425"
        }
      },
      {
        "box": {
          "id": "obj-105",
          "maxclass": "comment",
          "patching_rect": [
            471,
            972,
            140,
            20
          ],
          "text": "|0101> BANK 6"
        }
      },
      {
        "box": {
          "id": "obj-106",
          "maxclass": "newobj",
          "patching_rect": [
            634,
            945,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-107",
          "maxclass": "newobj",
          "patching_rect": [
            634,
            972,
            64,
            22
          ],
          "text": "*~ 0.3253"
        }
      },
      {
        "box": {
          "id": "obj-108",
          "maxclass": "newobj",
          "patching_rect": [
            704,
            972,
            64,
            22
          ],
          "text": "*~ 0.2656"
        }
      },
      {
        "box": {
          "id": "obj-109",
          "maxclass": "comment",
          "patching_rect": [
            776,
            972,
            140,
            20
          ],
          "text": "|0110> BANK 7"
        }
      },
      {
        "box": {
          "id": "obj-110",
          "maxclass": "newobj",
          "patching_rect": [
            939,
            945,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-111",
          "maxclass": "newobj",
          "patching_rect": [
            939,
            972,
            64,
            22
          ],
          "text": "*~ 0.3067"
        }
      },
      {
        "box": {
          "id": "obj-112",
          "maxclass": "newobj",
          "patching_rect": [
            1009,
            972,
            64,
            22
          ],
          "text": "*~ 0.2869"
        }
      },
      {
        "box": {
          "id": "obj-113",
          "maxclass": "comment",
          "patching_rect": [
            1081,
            972,
            140,
            20
          ],
          "text": "|0111> BANK 8"
        }
      },
      {
        "box": {
          "id": "obj-114",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            1015,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-115",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            1042,
            64,
            22
          ],
          "text": "*~ 0.2869"
        }
      },
      {
        "box": {
          "id": "obj-116",
          "maxclass": "newobj",
          "patching_rect": [
            94,
            1042,
            64,
            22
          ],
          "text": "*~ 0.3067"
        }
      },
      {
        "box": {
          "id": "obj-117",
          "maxclass": "comment",
          "patching_rect": [
            166,
            1042,
            140,
            20
          ],
          "text": "|1000> BANK 9"
        }
      },
      {
        "box": {
          "id": "obj-118",
          "maxclass": "newobj",
          "patching_rect": [
            329,
            1015,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-119",
          "maxclass": "newobj",
          "patching_rect": [
            329,
            1042,
            64,
            22
          ],
          "text": "*~ 0.2656"
        }
      },
      {
        "box": {
          "id": "obj-120",
          "maxclass": "newobj",
          "patching_rect": [
            399,
            1042,
            64,
            22
          ],
          "text": "*~ 0.3253"
        }
      },
      {
        "box": {
          "id": "obj-121",
          "maxclass": "comment",
          "patching_rect": [
            471,
            1042,
            140,
            20
          ],
          "text": "|1001> BANK 10"
        }
      },
      {
        "box": {
          "id": "obj-122",
          "maxclass": "newobj",
          "patching_rect": [
            634,
            1015,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-123",
          "maxclass": "newobj",
          "patching_rect": [
            634,
            1042,
            64,
            22
          ],
          "text": "*~ 0.2425"
        }
      },
      {
        "box": {
          "id": "obj-124",
          "maxclass": "newobj",
          "patching_rect": [
            704,
            1042,
            64,
            22
          ],
          "text": "*~ 0.3429"
        }
      },
      {
        "box": {
          "id": "obj-125",
          "maxclass": "comment",
          "patching_rect": [
            776,
            1042,
            140,
            20
          ],
          "text": "|1010> BANK 11"
        }
      },
      {
        "box": {
          "id": "obj-126",
          "maxclass": "newobj",
          "patching_rect": [
            939,
            1015,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-127",
          "maxclass": "newobj",
          "patching_rect": [
            939,
            1042,
            64,
            22
          ],
          "text": "*~ 0.2169"
        }
      },
      {
        "box": {
          "id": "obj-128",
          "maxclass": "newobj",
          "patching_rect": [
            1009,
            1042,
            64,
            22
          ],
          "text": "*~ 0.3597"
        }
      },
      {
        "box": {
          "id": "obj-129",
          "maxclass": "comment",
          "patching_rect": [
            1081,
            1042,
            140,
            20
          ],
          "text": "|1011> BANK 12"
        }
      },
      {
        "box": {
          "id": "obj-130",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            1085,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-131",
          "maxclass": "newobj",
          "patching_rect": [
            24,
            1112,
            64,
            22
          ],
          "text": "*~ 0.1878"
        }
      },
      {
        "box": {
          "id": "obj-132",
          "maxclass": "newobj",
          "patching_rect": [
            94,
            1112,
            64,
            22
          ],
          "text": "*~ 0.3757"
        }
      },
      {
        "box": {
          "id": "obj-133",
          "maxclass": "comment",
          "patching_rect": [
            166,
            1112,
            140,
            20
          ],
          "text": "|1100> BANK 13"
        }
      },
      {
        "box": {
          "id": "obj-134",
          "maxclass": "newobj",
          "patching_rect": [
            329,
            1085,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-135",
          "maxclass": "newobj",
          "patching_rect": [
            329,
            1112,
            64,
            22
          ],
          "text": "*~ 0.1534"
        }
      },
      {
        "box": {
          "id": "obj-136",
          "maxclass": "newobj",
          "patching_rect": [
            399,
            1112,
            64,
            22
          ],
          "text": "*~ 0.3910"
        }
      },
      {
        "box": {
          "id": "obj-137",
          "maxclass": "comment",
          "patching_rect": [
            471,
            1112,
            140,
            20
          ],
          "text": "|1101> BANK 14"
        }
      },
      {
        "box": {
          "id": "obj-138",
          "maxclass": "newobj",
          "patching_rect": [
            634,
            1085,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-139",
          "maxclass": "newobj",
          "patching_rect": [
            634,
            1112,
            64,
            22
          ],
          "text": "*~ 0.1084"
        }
      },
      {
        "box": {
          "id": "obj-140",
          "maxclass": "newobj",
          "patching_rect": [
            704,
            1112,
            64,
            22
          ],
          "text": "*~ 0.4058"
        }
      },
      {
        "box": {
          "id": "obj-141",
          "maxclass": "comment",
          "patching_rect": [
            776,
            1112,
            140,
            20
          ],
          "text": "|1110> BANK 15"
        }
      },
      {
        "box": {
          "id": "obj-142",
          "maxclass": "newobj",
          "patching_rect": [
            939,
            1085,
            290,
            22
          ],
          "text": "resonators~ smooth 110. 0.2 2.4 164.81 0.16 2.1 220. 0.13 1.9 277.18 0.1 1.7 329.63 0.08 1.5 440. 0.06 1.3"
        }
      },
      {
        "box": {
          "id": "obj-143",
          "maxclass": "newobj",
          "patching_rect": [
            939,
            1112,
            64,
            22
          ],
          "text": "*~ 0.0000"
        }
      },
      {
        "box": {
          "id": "obj-144",
          "maxclass": "newobj",
          "patching_rect": [
            1009,
            1112,
            64,
            22
          ],
          "text": "*~ 0.4200"
        }
      },
      {
        "box": {
          "id": "obj-145",
          "maxclass": "comment",
          "patching_rect": [
            1081,
            1112,
            140,
            20
          ],
          "text": "|1111> BANK 16"
        }
      },
      {
        "box": {
          "id": "obj-146",
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
          "id": "obj-147",
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
          "id": "obj-148",
          "maxclass": "newobj",
          "patching_rect": [
            60,
            725,
            235,
            22
          ],
          "text": "o.pack /qmw/chladni/control/run"
        }
      },
      {
        "box": {
          "id": "obj-149",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            725,
            290,
            22
          ],
          "text": "o.pack /qmw/chladni/control/entanglement"
        }
      },
      {
        "box": {
          "id": "obj-150",
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
          "id": "obj-151",
          "maxclass": "newobj",
          "patching_rect": [
            60,
            765,
            270,
            22
          ],
          "text": "o.pack /qmw/chladni/control/measure"
        }
      },
      {
        "box": {
          "id": "obj-152",
          "maxclass": "number",
          "patching_rect": [
            430,
            795,
            55,
            22
          ],
          "minimum": 2,
          "maximum": 10
        }
      },
      {
        "box": {
          "id": "obj-153",
          "maxclass": "newobj",
          "patching_rect": [
            430,
            765,
            78,
            22
          ],
          "text": "loadmess 5"
        }
      },
      {
        "box": {
          "id": "obj-154",
          "maxclass": "newobj",
          "patching_rect": [
            495,
            795,
            270,
            22
          ],
          "text": "o.pack /qmw/chladni/control/qpe-bits"
        }
      },
      {
        "box": {
          "id": "obj-155",
          "maxclass": "comment",
          "patching_rect": [
            430,
            820,
            150,
            20
          ],
          "text": "QPE REGISTER QUBITS"
        }
      },
      {
        "box": {
          "id": "obj-156",
          "maxclass": "newobj",
          "patching_rect": [
            165,
            810,
            145,
            22
          ],
          "text": "udpsend 127.0.0.1 7473"
        }
      },
      {
        "box": {
          "id": "obj-157",
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
          "id": "obj-158",
          "maxclass": "message",
          "patching_rect": [
            385,
            765,
            30,
            22
          ],
          "text": "1"
        }
      },
      {
        "box": {
          "id": "obj-159",
          "maxclass": "newobj",
          "patching_rect": [
            395,
            765,
            270,
            22
          ],
          "text": "o.pack /qmw/chladni/control/geometry"
        }
      },
      {
        "box": {
          "id": "obj-160",
          "maxclass": "button",
          "patching_rect": [
            660,
            765,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-161",
          "maxclass": "message",
          "patching_rect": [
            695,
            765,
            64,
            22
          ],
          "text": "loopback"
        }
      },
      {
        "box": {
          "id": "obj-162",
          "maxclass": "newobj",
          "patching_rect": [
            770,
            765,
            210,
            22
          ],
          "text": "o.pack /qmw/chladni/status"
        }
      },
      {
        "box": {
          "id": "obj-163",
          "maxclass": "newobj",
          "patching_rect": [
            995,
            765,
            145,
            22
          ],
          "text": "udpsend 127.0.0.1 7400"
        }
      },
      {
        "box": {
          "id": "obj-164",
          "maxclass": "flonum",
          "patching_rect": [
            680,
            700,
            70,
            22
          ],
          "minimum": 0.001,
          "maximum": 1.0
        }
      },
      {
        "box": {
          "id": "obj-165",
          "maxclass": "newobj",
          "patching_rect": [
            680,
            675,
            92,
            22
          ],
          "text": "loadmess 0.08"
        }
      },
      {
        "box": {
          "id": "obj-166",
          "maxclass": "newobj",
          "patching_rect": [
            755,
            700,
            330,
            22
          ],
          "text": "o.pack /qmw/temporal-mechanics/v1/control/distance"
        }
      },
      {
        "box": {
          "id": "obj-167",
          "maxclass": "flonum",
          "patching_rect": [
            680,
            735,
            70,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0
        }
      },
      {
        "box": {
          "id": "obj-168",
          "maxclass": "newobj",
          "patching_rect": [
            680,
            760,
            92,
            22
          ],
          "text": "loadmess 0.35"
        }
      },
      {
        "box": {
          "id": "obj-169",
          "maxclass": "newobj",
          "patching_rect": [
            755,
            735,
            380,
            22
          ],
          "text": "o.pack /qmw/temporal-mechanics/v1/control/coherence-depth"
        }
      },
      {
        "box": {
          "id": "obj-170",
          "maxclass": "newobj",
          "patching_rect": [
            1090,
            700,
            145,
            22
          ],
          "text": "udpsend 127.0.0.1 7444"
        }
      },
      {
        "box": {
          "id": "obj-171",
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
            "obj-11",
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
            "obj-12",
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
            "obj-13",
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
            "obj-14",
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
            "obj-15",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-9",
            1
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
            2
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
            "obj-8",
            5
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
            "obj-10",
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
            "obj-11",
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
            "obj-12",
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
            "obj-13",
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
            "obj-14",
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
            "obj-15",
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
            "obj-16",
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
            "obj-17",
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
            "obj-18",
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
            "obj-7",
            0
          ],
          "destination": [
            "obj-20",
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
            "obj-21",
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
            "obj-21",
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
            "obj-4",
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
            "obj-5",
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
            "obj-8",
            6
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
            "obj-8",
            2
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
            "obj-9",
            2
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
            "obj-27",
            0
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
            "obj-29",
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
            "obj-31",
            0
          ],
          "destination": [
            "obj-30",
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
            "obj-19",
            1
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
            "obj-19",
            2
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
            "obj-19",
            3
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
            "obj-19",
            4
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
            "obj-39",
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
            "obj-40",
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
            "obj-19",
            8
          ],
          "destination": [
            "obj-42",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            3
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
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-44",
            3
          ],
          "destination": [
            "obj-45",
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
            "obj-19",
            4
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
            "obj-48",
            0
          ],
          "destination": [
            "obj-50",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            6
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
            "obj-49",
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
            "obj-50",
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
            "obj-53",
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
            "obj-54",
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
            "obj-26",
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
            "obj-57",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            5
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
            "obj-59",
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
            "obj-19",
            7
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
            "obj-61",
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
            "obj-62",
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
            "obj-62",
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
            "obj-65",
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
            "obj-63",
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
            "obj-66",
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
            "obj-67",
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
            "obj-67",
            0
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
            "obj-71",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            1
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
            "obj-19",
            2
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
            "obj-19",
            2
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
            "obj-75",
            0
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
            1
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
            "obj-71",
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
            "obj-72",
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
            "obj-78",
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
            "obj-80",
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
            "obj-71",
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
            "obj-72",
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
            "obj-73",
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
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            9
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
            "obj-82",
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
            "obj-73",
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
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            10
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
            "obj-86",
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
            "obj-87",
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
            "obj-88",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            11
          ],
          "destination": [
            "obj-90",
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
            "obj-91",
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
            "obj-92",
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
            "obj-73",
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
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            12
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
            "obj-94",
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
            "obj-94",
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
            "obj-95",
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
            "obj-96",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            13
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
            "obj-98",
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
            "obj-99",
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
            "obj-100",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            14
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
            "obj-102",
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
            "obj-103",
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
            "obj-104",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            15
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
            "obj-106",
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
            "obj-107",
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
            "obj-108",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            16
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
            "obj-110",
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
            "obj-111",
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
            "obj-112",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            17
          ],
          "destination": [
            "obj-114",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-114",
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
            "obj-114",
            0
          ],
          "destination": [
            "obj-116",
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
            "obj-73",
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
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            18
          ],
          "destination": [
            "obj-118",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-118",
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
            "obj-118",
            0
          ],
          "destination": [
            "obj-120",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-119",
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
            "obj-120",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            19
          ],
          "destination": [
            "obj-122",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-122",
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
            "obj-122",
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
            "obj-123",
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
            "obj-124",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            20
          ],
          "destination": [
            "obj-126",
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
            "obj-127",
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
            "obj-128",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-127",
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
            "obj-128",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            21
          ],
          "destination": [
            "obj-130",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-130",
            0
          ],
          "destination": [
            "obj-131",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-130",
            0
          ],
          "destination": [
            "obj-132",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-131",
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
            "obj-132",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            22
          ],
          "destination": [
            "obj-134",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-134",
            0
          ],
          "destination": [
            "obj-135",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-134",
            0
          ],
          "destination": [
            "obj-136",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-135",
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
            "obj-136",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            23
          ],
          "destination": [
            "obj-138",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-138",
            0
          ],
          "destination": [
            "obj-139",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-138",
            0
          ],
          "destination": [
            "obj-140",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-139",
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
            "obj-140",
            0
          ],
          "destination": [
            "obj-73",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-19",
            24
          ],
          "destination": [
            "obj-142",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-142",
            0
          ],
          "destination": [
            "obj-143",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-142",
            0
          ],
          "destination": [
            "obj-144",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-143",
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
            "obj-144",
            0
          ],
          "destination": [
            "obj-73",
            1
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
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-73",
            1
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
            "obj-147",
            0
          ],
          "destination": [
            "obj-146",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-146",
            0
          ],
          "destination": [
            "obj-148",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-148",
            0
          ],
          "destination": [
            "obj-156",
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
            "obj-149",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-149",
            0
          ],
          "destination": [
            "obj-156",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-150",
            0
          ],
          "destination": [
            "obj-151",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-151",
            0
          ],
          "destination": [
            "obj-156",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-153",
            0
          ],
          "destination": [
            "obj-152",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-152",
            0
          ],
          "destination": [
            "obj-154",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-154",
            0
          ],
          "destination": [
            "obj-156",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-157",
            0
          ],
          "destination": [
            "obj-158",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-158",
            0
          ],
          "destination": [
            "obj-159",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-159",
            0
          ],
          "destination": [
            "obj-156",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-160",
            0
          ],
          "destination": [
            "obj-161",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-161",
            0
          ],
          "destination": [
            "obj-162",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-162",
            0
          ],
          "destination": [
            "obj-163",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-165",
            0
          ],
          "destination": [
            "obj-164",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-164",
            0
          ],
          "destination": [
            "obj-166",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-166",
            0
          ],
          "destination": [
            "obj-170",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-168",
            0
          ],
          "destination": [
            "obj-167",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-167",
            0
          ],
          "destination": [
            "obj-169",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-169",
            0
          ],
          "destination": [
            "obj-170",
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
