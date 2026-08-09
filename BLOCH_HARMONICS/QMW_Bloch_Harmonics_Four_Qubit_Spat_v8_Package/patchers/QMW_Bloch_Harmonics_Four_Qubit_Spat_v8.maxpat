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
			85,
			100,
			1323,
			816
		],
		"openinpresentation": 1,
		"gridsize": [
			15,
			15
		],
		"boxes": [
			{
				"box": {
					"fontsize": 18,
					"id": "obj-1",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						20,
						15,
						753,
						27
					],
					"presentation": 1,
					"presentation_rect": [
						20,
						15,
						753,
						27
					],
					"text": "FOUR-QUBIT RESONATORS + GLOBAL DENSITY FIELD + SPAT5 THIRD-ORDER HOA v8"
				}
			},
			{
				"box": {
					"id": "obj-2",
					"linecount": 2,
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						20,
						43,
						732,
						33
					],
					"presentation": 1,
					"presentation_linecount": 2,
					"presentation_rect": [
						20,
						43,
						730,
						33
					],
					"text": "Density-engine OSC drives the Bloch direction; Yℓm excites the canonical GenExpr resonator; a portable dual-geometry convolution stage morphs between Tanglecube and Heart impulse responses."
				}
			},
			{
				"box": {
					"disablefind": 0,
					"id": "obj-3",
					"maxclass": "jweb",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						20,
						90,
						740,
						720
					],
					"presentation": 1,
					"presentation_rect": [
						20,
						90,
						740,
						720
					],
					"rendermode": 0,
					"url": "file://bloch-harmonics-four-qubit-max.html"
				}
			},
			{
				"box": {
					"id": "obj-4",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					],
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
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						800,
						750,
						247,
						22
					],
					"text": "readfile bloch-harmonics-four-qubit-max.html"
				}
			},
			{
				"box": {
					"id": "obj-6",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
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
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
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
					"numinlets": 1,
					"numoutlets": 20,
					"outlettype": [
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float",
						"float"
					],
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
					"numinlets": 1,
					"numoutlets": 0,
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
					"format": 6,
					"id": "obj-10",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						900,
						200,
						95,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						900,
						105,
						95,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-11",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
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
					"format": 6,
					"id": "obj-12",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						900,
						254,
						95,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						900,
						159,
						95,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-13",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
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
					"format": 6,
					"id": "obj-14",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						900,
						308,
						95,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						900,
						213,
						95,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-15",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
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
					"format": 6,
					"id": "obj-16",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						900,
						362,
						95,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						900,
						267,
						95,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-17",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
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
					"format": 6,
					"id": "obj-18",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						900,
						416,
						95,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						900,
						321,
						95,
						22
					]
				}
			},
			{
				"box": {
					"fontsize": 14,
					"id": "obj-19",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						175,
						260,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						80,
						280,
						22
					],
					"text": "Live q0 state from the OSC viewer"
				}
			},
			{
				"box": {
					"fontsize": 14,
					"id": "obj-120",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						640,
						220,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						625,
						240,
						22
					],
					"text": "GenExpr mapping"
				}
			},
			{
				"box": {
					"id": "obj-121",
					"linecount": 4,
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						670,
						307,
						60
					],
					"presentation": 1,
					"presentation_linecount": 5,
					"presentation_rect": [
						790,
						655,
						192,
						74
					],
					"text": "|Yℓm| → resonator magnitude  •  sign(Yℓm) → 0/π phase  •  degree sets decay speed\\nThe first 15 resonant lanes follow the visible bars; lane 16 remains reserved."
				}
			},
			{
				"box": {
					"id": "obj-122",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						730,
						500,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						775,
						520,
						20
					],
					"text": "Runtime assets and both stereo IR files must remain beside this patch.",
					"textcolor": [
						0.45,
						0.45,
						0.45,
						1
					]
				}
			},
			{
				"box": {
					"id": "obj-123",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
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
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					],
					"parameter_enable": 0,
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
					"numinlets": 1,
					"numoutlets": 0,
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
					"id": "obj-200",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"signal",
						"signal",
						"signal"
					],
					"patching_rect": [
						674,
						862,
						210,
						22
					],
					"text": "gen~ qmw_density_field_resonator"
				}
			},
			{
				"box": {
					"id": "obj-201",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						385,
						110,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						350,
						110,
						20
					],
					"text": "Qubit pitch (Hz)"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-202",
					"maxclass": "flonum",
					"maximum": 1000,
					"minimum": 20,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						905,
						384,
						85,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						905,
						370,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-203",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1005,
						289,
						85,
						22
					],
					"text": "loadmess 55."
				}
			},
			{
				"box": {
					"id": "obj-204",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1095,
						380,
						38,
						22
					],
					"text": "sig~"
				}
			},
			{
				"box": {
					"id": "obj-842",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1150,
						380,
						150,
						22
					],
					"text": "s qmw.q0.basefreq"
				}
			},
			{
				"box": {
					"id": "obj-843",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						905,
						350,
						35,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						905,
						350,
						35,
						20
					],
					"text": "q0"
				}
			},
			{
				"box": {
					"id": "obj-844",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1000,
						350,
						35,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1000,
						350,
						35,
						20
					],
					"text": "q1"
				}
			},
			{
				"box": {
					"id": "obj-845",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1095,
						350,
						35,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1095,
						350,
						35,
						20
					],
					"text": "q2"
				}
			},
			{
				"box": {
					"id": "obj-846",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1190,
						350,
						35,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1190,
						350,
						35,
						20
					],
					"text": "q3"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-847",
					"maxclass": "flonum",
					"maximum": 1000,
					"minimum": 20,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1000,
						384,
						85,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1000,
						370,
						85,
						22
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-848",
					"maxclass": "flonum",
					"maximum": 1000,
					"minimum": 20,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1095,
						384,
						85,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1095,
						370,
						85,
						22
					]
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-849",
					"maxclass": "flonum",
					"maximum": 1000,
					"minimum": 20,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1190,
						384,
						85,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1190,
						370,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-850",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1000,
						320,
						105,
						22
					],
					"text": "loadmess 61.735"
				}
			},
			{
				"box": {
					"id": "obj-851",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1110,
						320,
						105,
						22
					],
					"text": "loadmess 73.416"
				}
			},
			{
				"box": {
					"id": "obj-852",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1220,
						320,
						105,
						22
					],
					"text": "loadmess 82.407"
				}
			},
			{
				"box": {
					"id": "obj-853",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1000,
						415,
						145,
						22
					],
					"text": "s qmw.q1.basefreq"
				}
			},
			{
				"box": {
					"id": "obj-854",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1150,
						415,
						145,
						22
					],
					"text": "s qmw.q2.basefreq"
				}
			},
			{
				"box": {
					"id": "obj-855",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1300,
						415,
						145,
						22
					],
					"text": "s qmw.q3.basefreq"
				}
			},
			{
				"box": {
					"id": "obj-205",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						420,
						110,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						410,
						110,
						20
					],
					"text": "Spectral tilt trim"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-206",
					"maxclass": "flonum",
					"maximum": 0.5,
					"minimum": -0.5,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						905,
						415,
						85,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						905,
						405,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-207",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1000,
						415,
						140,
						22
					],
					"text": "prepend brightness"
				}
			},
			{
				"box": {
					"id": "obj-208",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1150,
						415,
						95,
						22
					],
					"text": "loadmess 0."
				}
			},
			{
				"box": {
					"id": "obj-209",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						455,
						110,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						445,
						110,
						20
					],
					"text": "Purity"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-210",
					"ignoreclick": 1,
					"maxclass": "flonum",
					"maximum": 1,
					"minimum": 0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						905,
						450,
						85,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						905,
						440,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-211",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1000,
						450,
						140,
						22
					],
					"text": "prepend purity"
				}
			},
			{
				"box": {
					"id": "obj-212",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1150,
						450,
						95,
						22
					],
					"text": "loadmess 1"
				}
			},
			{
				"box": {
					"id": "obj-213",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						490,
						110,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						480,
						110,
						20
					],
					"text": "Entropy"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-214",
					"ignoreclick": 1,
					"maxclass": "flonum",
					"maximum": 1,
					"minimum": 0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						905,
						485,
						85,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						905,
						475,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-215",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1000,
						485,
						140,
						22
					],
					"text": "prepend entropy"
				}
			},
			{
				"box": {
					"id": "obj-216",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1150,
						485,
						95,
						22
					],
					"text": "loadmess 0.12"
				}
			},
			{
				"box": {
					"id": "obj-217",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						525,
						110,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						515,
						110,
						20
					],
					"text": "Coherence"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-218",
					"ignoreclick": 1,
					"maxclass": "flonum",
					"maximum": 1,
					"minimum": 0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						905,
						520,
						85,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						905,
						510,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-219",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1000,
						520,
						140,
						22
					],
					"text": "prepend coherence"
				}
			},
			{
				"box": {
					"id": "obj-220",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1150,
						520,
						95,
						22
					],
					"text": "loadmess 0.7"
				}
			},
			{
				"box": {
					"id": "obj-221",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						560,
						110,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						550,
						110,
						20
					],
					"text": "Slow decay (ms)"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-222",
					"maxclass": "flonum",
					"maximum": 5000,
					"minimum": 100,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						905,
						555,
						85,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						905,
						545,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-223",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1000,
						555,
						141,
						22
					],
					"text": "prepend slow_decay_ms"
				}
			},
			{
				"box": {
					"id": "obj-224",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1150,
						555,
						95,
						22
					],
					"text": "loadmess 1200"
				}
			},
			{
				"box": {
					"id": "obj-225",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						595,
						110,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						585,
						110,
						20
					],
					"text": "Fast decay (ms)"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-226",
					"maxclass": "flonum",
					"maximum": 1000,
					"minimum": 10,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						905,
						590,
						85,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						905,
						580,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-227",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1000,
						590,
						140,
						22
					],
					"text": "prepend fast_decay_ms"
				}
			},
			{
				"box": {
					"id": "obj-228",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1150,
						590,
						95,
						22
					],
					"text": "loadmess 90"
				}
			},
			{
				"box": {
					"id": "obj-229",
					"linecount": 2,
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						800,
						800,
						393,
						35
					],
					"text": "s0 0.18, s1 0.18, s2 0.18, s3 0.42, s4 0.42, s5 0.42, s6 0.42, s7 0.42, s8 0.72, s9 0.72, s10 0.72, s11 0.72, s12 0.72, s13 0.72, s14 0.72, s15 0.9"
				}
			},
			{
				"box": {
					"id": "obj-230",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						800,
						670,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-231",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						800,
						697,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-232",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						800,
						724,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-233",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						800,
						751,
						82,
						22
					],
					"text": "prepend m0"
				}
			},
			{
				"box": {
					"id": "obj-234",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						886,
						670,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-235",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						886,
						697,
						90,
						22
					],
					"text": "prepend ph0"
				}
			},
			{
				"box": {
					"id": "obj-236",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						950,
						670,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-237",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						950,
						697,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-238",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						950,
						724,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-239",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						950,
						751,
						82,
						22
					],
					"text": "prepend m1"
				}
			},
			{
				"box": {
					"id": "obj-240",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1036,
						670,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-241",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1036,
						697,
						90,
						22
					],
					"text": "prepend ph1"
				}
			},
			{
				"box": {
					"id": "obj-242",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1100,
						670,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-243",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1100,
						697,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-244",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1100,
						724,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-245",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1100,
						751,
						82,
						22
					],
					"text": "prepend m2"
				}
			},
			{
				"box": {
					"id": "obj-246",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1186,
						670,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-247",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1186,
						697,
						90,
						22
					],
					"text": "prepend ph2"
				}
			},
			{
				"box": {
					"id": "obj-248",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1250,
						670,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-249",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1250,
						697,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-250",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1250,
						724,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-251",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1250,
						751,
						82,
						22
					],
					"text": "prepend m3"
				}
			},
			{
				"box": {
					"id": "obj-252",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1336,
						670,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-253",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1336,
						697,
						90,
						22
					],
					"text": "prepend ph3"
				}
			},
			{
				"box": {
					"id": "obj-254",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1400,
						670,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-255",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1400,
						697,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-256",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1400,
						724,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-257",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1400,
						751,
						82,
						22
					],
					"text": "prepend m4"
				}
			},
			{
				"box": {
					"id": "obj-258",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1486,
						670,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-259",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1486,
						697,
						90,
						22
					],
					"text": "prepend ph4"
				}
			},
			{
				"box": {
					"id": "obj-260",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						800,
						800,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-261",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						800,
						827,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-262",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						800,
						854,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-263",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						800,
						881,
						82,
						22
					],
					"text": "prepend m5"
				}
			},
			{
				"box": {
					"id": "obj-264",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						886,
						800,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-265",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						886,
						827,
						90,
						22
					],
					"text": "prepend ph5"
				}
			},
			{
				"box": {
					"id": "obj-266",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						950,
						800,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-267",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						950,
						827,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-268",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						950,
						854,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-269",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						950,
						881,
						82,
						22
					],
					"text": "prepend m6"
				}
			},
			{
				"box": {
					"id": "obj-270",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1036,
						800,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-271",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1036,
						827,
						90,
						22
					],
					"text": "prepend ph6"
				}
			},
			{
				"box": {
					"id": "obj-272",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1100,
						800,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-273",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1100,
						827,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-274",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1100,
						854,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-275",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1100,
						881,
						82,
						22
					],
					"text": "prepend m7"
				}
			},
			{
				"box": {
					"id": "obj-276",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1186,
						800,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-277",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1186,
						827,
						90,
						22
					],
					"text": "prepend ph7"
				}
			},
			{
				"box": {
					"id": "obj-278",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1250,
						800,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-279",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1250,
						827,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-280",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1250,
						854,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-281",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1250,
						881,
						82,
						22
					],
					"text": "prepend m8"
				}
			},
			{
				"box": {
					"id": "obj-282",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1336,
						800,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-283",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1336,
						827,
						90,
						22
					],
					"text": "prepend ph8"
				}
			},
			{
				"box": {
					"id": "obj-284",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1400,
						800,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-285",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1400,
						827,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-286",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1400,
						854,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-287",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1400,
						881,
						82,
						22
					],
					"text": "prepend m9"
				}
			},
			{
				"box": {
					"id": "obj-288",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1486,
						800,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-289",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1486,
						827,
						90,
						22
					],
					"text": "prepend ph9"
				}
			},
			{
				"box": {
					"id": "obj-290",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						800,
						930,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-291",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						800,
						957,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-292",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						800,
						984,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-293",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						800,
						1011,
						82,
						22
					],
					"text": "prepend m10"
				}
			},
			{
				"box": {
					"id": "obj-294",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						886,
						930,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-295",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						886,
						957,
						90,
						22
					],
					"text": "prepend ph10"
				}
			},
			{
				"box": {
					"id": "obj-296",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						950,
						930,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-297",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						950,
						957,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-298",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						950,
						984,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-299",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						950,
						1011,
						82,
						22
					],
					"text": "prepend m11"
				}
			},
			{
				"box": {
					"id": "obj-300",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1036,
						930,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-301",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1036,
						957,
						90,
						22
					],
					"text": "prepend ph11"
				}
			},
			{
				"box": {
					"id": "obj-302",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1100,
						930,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-303",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1100,
						957,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-304",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1100,
						984,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-305",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1100,
						1011,
						82,
						22
					],
					"text": "prepend m12"
				}
			},
			{
				"box": {
					"id": "obj-306",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1186,
						930,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-307",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1186,
						957,
						90,
						22
					],
					"text": "prepend ph12"
				}
			},
			{
				"box": {
					"id": "obj-308",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1250,
						930,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-309",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1250,
						957,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-310",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1250,
						984,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-311",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1250,
						1011,
						82,
						22
					],
					"text": "prepend m13"
				}
			},
			{
				"box": {
					"id": "obj-312",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1336,
						930,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-313",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1336,
						957,
						90,
						22
					],
					"text": "prepend ph13"
				}
			},
			{
				"box": {
					"id": "obj-314",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1400,
						930,
						48,
						22
					],
					"text": "abs 0."
				}
			},
			{
				"box": {
					"id": "obj-315",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1400,
						957,
						48,
						22
					],
					"text": "* 1.6"
				}
			},
			{
				"box": {
					"id": "obj-316",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1400,
						984,
						72,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-317",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1400,
						1011,
						82,
						22
					],
					"text": "prepend m14"
				}
			},
			{
				"box": {
					"id": "obj-318",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1486,
						930,
						155,
						22
					],
					"text": "expr ($f1 < 0.) * 3.141593"
				}
			},
			{
				"box": {
					"id": "obj-319",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1486,
						957,
						90,
						22
					],
					"text": "prepend ph14"
				}
			},
			{
				"box": {
					"id": "obj-320",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						800,
						1065,
						135,
						22
					],
					"text": "m15 0, ph15 0"
				}
			},
			{
				"box": {
					"id": "obj-321",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1030,
						385,
						120,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						375,
						120,
						20
					],
					"text": "Master level (dB)"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-322",
					"maxclass": "flonum",
					"maximum": 0,
					"minimum": -60,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1150,
						380,
						75,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1150,
						370,
						75,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-323",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1235,
						380,
						90,
						22
					],
					"text": "loadmess -10."
				}
			},
			{
				"box": {
					"id": "obj-324",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1150,
						410,
						48,
						22
					],
					"text": "dbtoa"
				}
			},
			{
				"box": {
					"id": "obj-325",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1205,
						410,
						78,
						22
					],
					"text": "pack 0. 60"
				}
			},
			{
				"box": {
					"id": "obj-326",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"bang"
					],
					"patching_rect": [
						1290,
						410,
						48,
						22
					],
					"text": "line~"
				}
			},
			{
				"box": {
					"id": "obj-327",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1210,
						900,
						40,
						22
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "obj-328",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1260,
						900,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-329",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1030,
						455,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1023,
						231,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-330",
					"maxclass": "newobj",
					"numinlets": 16,
					"numoutlets": 0,
					"patching_rect": [
						1210,
						1700,
						330,
						22
					],
					"text": "dac~ 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16"
				}
			},
			{
				"box": {
					"id": "obj-400",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						20,
						850,
						115,
						22
					],
					"text": "udpreceive 7400"
				}
			},
			{
				"box": {
					"id": "obj-401",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						145,
						850,
						105,
						22
					],
					"text": "OSC-route /qmw"
				}
			},
			{
				"box": {
					"id": "obj-402",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						260,
						850,
						110,
						22
					],
					"text": "OSC-route /bloch"
				}
			},
			{
				"box": {
					"id": "obj-403",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": [
						"",
						"",
						"",
						""
					],
					"patching_rect": [
						380,
						850,
						245,
						22
					],
					"text": "OSC-route /vector_x /vector_y /vector_z"
				}
			},
			{
				"box": {
					"id": "obj-404",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						635,
						850,
						70,
						22
					],
					"text": "pak f f f"
				}
			},
			{
				"box": {
					"id": "obj-405",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						715,
						835,
						434,
						22
					],
					"text": "expr acos(max(-1.\\, min(1.\\, $f3 / max(sqrt($f1*$f1+$f2*$f2+$f3*$f3)\\, 0.000001))))"
				}
			},
			{
				"box": {
					"id": "obj-406",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						715,
						865,
						128,
						22
					],
					"text": "expr atan2($f2\\, $f1)"
				}
			},
			{
				"box": {
					"id": "obj-407",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1155,
						835,
						92,
						22
					],
					"text": "* 57.29578"
				}
			},
			{
				"box": {
					"id": "obj-408",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1155,
						865,
						92,
						22
					],
					"text": "* 57.29578"
				}
			},
			{
				"box": {
					"id": "obj-409",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1257,
						850,
						58,
						22
					],
					"text": "pak f f"
				}
			},
			{
				"box": {
					"id": "obj-410",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1325,
						850,
						48,
						22
					],
					"text": "gate 1"
				}
			},
			{
				"box": {
					"id": "obj-411",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1383,
						850,
						118,
						22
					],
					"text": "prepend setAngles"
				}
			},
			{
				"box": {
					"id": "obj-412",
					"maxclass": "toggle",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"int"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1030,
						500,
						24,
						24
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						475,
						24,
						24
					]
				}
			},
			{
				"box": {
					"id": "obj-413",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1060,
						502,
						130,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1060,
						477,
						130,
						20
					],
					"text": "OSC angle drive"
				}
			},
			{
				"box": {
					"id": "obj-414",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1195,
						500,
						82,
						22
					],
					"text": "loadmess 1"
				}
			},
			{
				"box": {
					"id": "obj-415",
					"maxclass": "button",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1030,
						535,
						24,
						24
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						510,
						24,
						24
					]
				}
			},
			{
				"box": {
					"id": "obj-416",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1060,
						537,
						210,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1060,
						512,
						230,
						20
					],
					"text": "density OSC activity · UDP 7400"
				}
			},
			{
				"box": {
					"id": "obj-417",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1030,
						572,
						90,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						547,
						90,
						20
					],
					"text": "OSC θ (°)"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-418",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1120,
						567,
						90,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1120,
						542,
						90,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-419",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1030,
						607,
						90,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						582,
						90,
						20
					],
					"text": "OSC φ (°)"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-420",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1120,
						602,
						90,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1120,
						577,
						90,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-421",
					"linecount": 2,
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1030,
						642,
						330,
						33
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						617,
						427,
						20
					],
					"text": "Source: /qmw/bloch/vector_x, vector_y, vector_z\\nθ = acos(z/r),  φ = atan2(y,x)"
				}
			},
			{
				"box": {
					"id": "obj-500",
					"maxclass": "newobj",
					"numinlets": 5,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"signal"
					],
					"patching_rect": [
						850,
						1120,
						210,
						22
					],
					"text": "qmw_bloch_convolution_ir~"
				}
			},
			{
				"box": {
					"fontsize": 14,
					"id": "obj-501",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1030,
						690,
						260,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						665,
						280,
						22
					],
					"text": "Dual-geometry convolution IR"
				}
			},
			{
				"box": {
					"id": "obj-502",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1030,
						725,
						110,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						700,
						110,
						20
					],
					"text": "Convolution mix"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-503",
					"maxclass": "flonum",
					"maximum": 1,
					"minimum": 0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1150,
						720,
						80,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1150,
						695,
						80,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-504",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1240,
						720,
						95,
						22
					],
					"text": "loadmess 0.35"
				}
			},
			{
				"box": {
					"id": "obj-505",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"float"
					],
					"patching_rect": [
						1150,
						755,
						42,
						22
					],
					"text": "t f f"
				}
			},
			{
				"box": {
					"id": "obj-506",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1200,
						755,
						92,
						22
					],
					"text": "expr sqrt($f1)"
				}
			},
			{
				"box": {
					"id": "obj-507",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1090,
						755,
						148,
						22
					],
					"text": "expr sqrt(max(0.\\, 1. - $f1))"
				}
			},
			{
				"box": {
					"id": "obj-508",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1020,
						785,
						92,
						22
					],
					"text": "expr sqrt($f1)"
				}
			},
			{
				"box": {
					"id": "obj-509",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1120,
						785,
						35,
						22
					],
					"text": "sig~"
				}
			},
			{
				"box": {
					"id": "obj-510",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1165,
						1120,
						35,
						22
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "obj-511",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1070,
						1155,
						35,
						22
					],
					"text": "+~"
				}
			},
			{
				"box": {
					"id": "obj-512",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1160,
						1155,
						35,
						22
					],
					"text": "+~"
				}
			},
			{
				"box": {
					"id": "obj-513",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1000,
						1120,
						67,
						22
					],
					"text": "dcblocker~"
				}
			},
			{
				"box": {
					"id": "obj-514",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1070,
						1120,
						67,
						22
					],
					"text": "dcblocker~"
				}
			},
			{
				"box": {
					"id": "obj-515",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1070,
						1190,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-516",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1175,
						1190,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-517",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1030,
						760,
						110,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						735,
						110,
						20
					],
					"text": "IR geometry"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-518",
					"maxclass": "flonum",
					"maximum": 1,
					"minimum": 0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1150,
						755,
						80,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1150,
						730,
						80,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-519",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1240,
						755,
						82,
						22
					],
					"text": "loadmess 0."
				}
			},
			{
				"box": {
					"id": "obj-520",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1030,
						790,
						300,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						765,
						300,
						20
					],
					"text": "0 = Tanglecube  ·  1 = Heart"
				}
			},
			{
				"box": {
					"id": "obj-521",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1360,
						720,
						36,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1240,
						700,
						36,
						20
					],
					"text": "IR A"
				}
			},
			{
				"box": {
					"id": "obj-522",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1400,
						720,
						62,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1278,
						698,
						62,
						22
					],
					"text": "replace"
				}
			},
			{
				"box": {
					"id": "obj-523",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1360,
						755,
						36,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1240,
						735,
						36,
						20
					],
					"text": "IR B"
				}
			},
			{
				"box": {
					"id": "obj-524",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1400,
						755,
						62,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1278,
						733,
						62,
						22
					],
					"text": "replace"
				}
			},
			{
				"box": {
					"id": "obj-530",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						20,
						1080,
						125,
						22
					],
					"text": "OSC-route /density"
				}
			},
			{
				"box": {
					"id": "obj-531",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 4,
					"outlettype": [
						"",
						"",
						"",
						""
					],
					"patching_rect": [
						155,
						1080,
						350,
						22
					],
					"text": "OSC-route /coherence_l1 /von_neumann_entropy /purity"
				}
			},
			{
				"box": {
					"id": "obj-532",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						155,
						1110,
						45,
						22
					],
					"text": "/ 15."
				}
			},
			{
				"box": {
					"id": "obj-533",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						210,
						1110,
						68,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-534",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						288,
						1110,
						78,
						22
					],
					"text": "pack 0. 180"
				}
			},
			{
				"box": {
					"id": "obj-535",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"patching_rect": [
						376,
						1110,
						48,
						22
					],
					"text": "line 0."
				}
			},
			{
				"box": {
					"id": "obj-536",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"float",
						"float"
					],
					"patching_rect": [
						434,
						1110,
						42,
						22
					],
					"text": "t f f"
				}
			},
			{
				"box": {
					"id": "obj-537",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						486,
						1110,
						125,
						22
					],
					"text": "prepend coherence"
				}
			},
			{
				"box": {
					"id": "obj-538",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						155,
						1140,
						92,
						22
					],
					"text": "/ 2.772589"
				}
			},
			{
				"box": {
					"id": "obj-539",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						257,
						1140,
						68,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-540",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						335,
						1140,
						78,
						22
					],
					"text": "pack 0. 180"
				}
			},
			{
				"box": {
					"id": "obj-541",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"patching_rect": [
						423,
						1140,
						48,
						22
					],
					"text": "line 0."
				}
			},
			{
				"box": {
					"id": "obj-542",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						481,
						1140,
						110,
						22
					],
					"text": "prepend entropy"
				}
			},
			{
				"box": {
					"id": "obj-543",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						515,
						1080,
						68,
						22
					],
					"text": "clip 0. 1."
				}
			},
			{
				"box": {
					"id": "obj-544",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						593,
						1080,
						78,
						22
					],
					"text": "pack 0. 180"
				}
			},
			{
				"box": {
					"id": "obj-545",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"patching_rect": [
						681,
						1080,
						48,
						22
					],
					"text": "line 0."
				}
			},
			{
				"box": {
					"id": "obj-546",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						434,
						1170,
						60,
						22
					],
					"text": "pak f f"
				}
			},
			{
				"box": {
					"id": "obj-547",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						504,
						1170,
						270,
						22
					],
					"text": "expr max(0.05\\,min(1.\\,0.9-0.75*$f1+$f2))"
				}
			},
			{
				"box": {
					"id": "obj-548",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1000,
						415,
						230,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1000,
						400,
						230,
						20
					],
					"text": "OSC coherence + entropy; manual offset"
				}
			},
			{
				"box": {
					"id": "obj-700",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 5,
					"outlettype": [
						"",
						"",
						"",
						"",
						""
					],
					"patching_rect": [
						20,
						1220,
						430,
						22
					],
					"text": "OSC-route /qubit/0/bloch /qubit/1/bloch /qubit/2/bloch /qubit/3/bloch"
				}
			},
			{
				"box": {
					"id": "obj-701",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 5,
					"outlettype": [
						"",
						"",
						"",
						"",
						""
					],
					"patching_rect": [
						150,
						1220,
						175,
						22
					],
					"text": "OSC-route /0 /1 /2 /3"
				}
			},
			{
				"box": {
					"id": "obj-702",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						335,
						1190,
						110,
						22
					],
					"text": "OSC-route /bloch"
				}
			},
			{
				"box": {
					"id": "obj-703",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						335,
						1220,
						110,
						22
					],
					"text": "OSC-route /bloch"
				}
			},
			{
				"box": {
					"id": "obj-704",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						335,
						1250,
						110,
						22
					],
					"text": "OSC-route /bloch"
				}
			},
			{
				"box": {
					"id": "obj-705",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						335,
						1280,
						110,
						22
					],
					"text": "OSC-route /bloch"
				}
			},
			{
				"box": {
					"id": "obj-706",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						455,
						1190,
						105,
						22
					],
					"text": "s qmw.q0.bloch"
				}
			},
			{
				"box": {
					"id": "obj-707",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						455,
						1220,
						105,
						22
					],
					"text": "s qmw.q1.bloch"
				}
			},
			{
				"box": {
					"id": "obj-708",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						455,
						1250,
						105,
						22
					],
					"text": "s qmw.q2.bloch"
				}
			},
			{
				"box": {
					"id": "obj-709",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						455,
						1280,
						105,
						22
					],
					"text": "s qmw.q3.bloch"
				}
			},
			{
				"box": {
					"id": "obj-800",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						580,
						1220,
						115,
						22
					],
					"text": "prepend setQubit0"
				}
			},
			{
				"box": {
					"id": "obj-801",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						700,
						1220,
						115,
						22
					],
					"text": "prepend setQubit1"
				}
			},
			{
				"box": {
					"id": "obj-802",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						820,
						1220,
						115,
						22
					],
					"text": "prepend setQubit2"
				}
			},
			{
				"box": {
					"id": "obj-803",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						940,
						1220,
						115,
						22
					],
					"text": "prepend setQubit3"
				}
			},
			{
				"box": {
					"id": "obj-710",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						580,
						1190,
						135,
						22
					],
					"text": "s qmw.global.purity"
				}
			},
			{
				"box": {
					"id": "obj-711",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						580,
						1220,
						140,
						22
					],
					"text": "s qmw.global.entropy"
				}
			},
			{
				"box": {
					"id": "obj-712",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						580,
						1250,
						155,
						22
					],
					"text": "s qmw.global.coherence"
				}
			},
			{
				"box": {
					"id": "obj-713",
					"maxclass": "newobj",
					"numinlets": 0,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						780,
						1190,
						255,
						22
					],
					"text": "qmw_qubit_genexpr_voice~ qmw.q0.bloch 55. qmw.q0.basefreq"
				}
			},
			{
				"box": {
					"id": "obj-714",
					"maxclass": "newobj",
					"numinlets": 0,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						780,
						1220,
						275,
						22
					],
					"text": "qmw_qubit_genexpr_voice~ qmw.q1.bloch 61.735 qmw.q1.basefreq"
				}
			},
			{
				"box": {
					"id": "obj-715",
					"maxclass": "newobj",
					"numinlets": 0,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						780,
						1250,
						275,
						22
					],
					"text": "qmw_qubit_genexpr_voice~ qmw.q2.bloch 73.416 qmw.q2.basefreq"
				}
			},
			{
				"box": {
					"id": "obj-716",
					"maxclass": "newobj",
					"numinlets": 0,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						780,
						1280,
						275,
						22
					],
					"text": "qmw_qubit_genexpr_voice~ qmw.q3.bloch 82.407 qmw.q3.basefreq"
				}
			},
			{
				"box": {
					"id": "obj-717",
					"maxclass": "newobj",
					"numinlets": 12,
					"numoutlets": 16,
					"outlettype": [
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal"
					],
					"patching_rect": [
						1170,
						1240,
						250,
						22
					],
					"text": "qmw_four_qubit_spat5_hoa3~"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-718",
					"maxclass": "flonum",
					"maximum": 0.5,
					"minimum": 0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						900,
						1360,
						80,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						900,
						840,
						80,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-719",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						990,
						1360,
						90,
						22
					],
					"text": "loadmess 0.12"
				}
			},
			{
				"box": {
					"id": "obj-720",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						900,
						1395,
						155,
						22
					],
					"text": "s qmw.local.voice.level"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-721",
					"maxclass": "flonum",
					"maximum": 1,
					"minimum": 0,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1150,
						1360,
						80,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1150,
						840,
						80,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-722",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1240,
						1360,
						90,
						22
					],
					"text": "loadmess 0.2"
				}
			},
			{
				"box": {
					"id": "obj-723",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1150,
						1395,
						35,
						22
					],
					"text": "sig~"
				}
			},
			{
				"box": {
					"id": "obj-724",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1060,
						1430,
						35,
						22
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "obj-725",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1130,
						1430,
						35,
						22
					],
					"text": "*~"
				}
			},
			{
				"box": {
					"id": "obj-726",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1220,
						1430,
						35,
						22
					],
					"text": "+~"
				}
			},
			{
				"box": {
					"id": "obj-727",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1290,
						1430,
						35,
						22
					],
					"text": "+~"
				}
			},
			{
				"box": {
					"id": "obj-728",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1220,
						1470,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-729",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1325,
						1470,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-730",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1383.5,
						1085,
						105,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1250,
						840,
						105,
						22
					],
					"text": "/window/open"
				}
			},
			{
				"box": {
					"id": "obj-731",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						1325,
						280,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						805,
						280,
						20
					],
					"text": "FOUR INDEPENDENT QUBIT VOICES"
				}
			},
			{
				"box": {
					"id": "obj-732",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						1365,
						105,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						790,
						845,
						105,
						20
					],
					"text": "Voice amplitude"
				}
			},
			{
				"box": {
					"id": "obj-733",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1030,
						1365,
						115,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						845,
						115,
						20
					],
					"text": "Global field level"
				}
			},
			{
				"box": {
					"id": "obj-734",
					"linecount": 2,
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						790,
						1410,
						564,
						33
					],
					"presentation": 1,
					"presentation_linecount": 2,
					"presentation_rect": [
						790,
						880,
						563,
						33
					],
					"text": "q0–q3 drive four separate resonator sources; global convolution L/R form sources 5–6.\nSpat5 encodes all six sources to third-order 3D HOA: DAC 1–16 carry ACN 0–15 in SN3D normalization."
				}
			},
			{
				"box": {
					"id": "obj-735",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1200,
						1325,
						84,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1200,
						805,
						84,
						20
					],
					"text": "Spat rate (Hz)"
				}
			},
			{
				"box": {
					"format": 6,
					"id": "obj-736",
					"maxclass": "flonum",
					"maximum": 60,
					"minimum": 5,
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1290,
						1208,
						65,
						22
					],
					"presentation": 1,
					"presentation_rect": [
						1290,
						800,
						65,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-737",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1290,
						1290,
						145,
						22
					],
					"text": "expr 1000./max(1.\\,$f1)"
				}
			},
			{
				"box": {
					"id": "obj-738",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1200,
						1290,
						80,
						22
					],
					"text": "loadmess 50."
				}
			},
			{
				"box": {
					"id": "obj-804",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						740,
						1080,
						55,
						22
					],
					"text": "set $1"
				}
			},
			{
				"box": {
					"id": "obj-805",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						740,
						1110,
						55,
						22
					],
					"text": "set $1"
				}
			},
			{
				"box": {
					"id": "obj-806",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						740,
						1140,
						55,
						22
					],
					"text": "set $1"
				}
			},
			{
				"box": {
					"id": "obj-807",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						805,
						1080,
						155,
						22
					],
					"text": "OSC-route /populations"
				}
			},
			{
				"box": {
					"id": "obj-808",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						970,
						1080,
						145,
						22
					],
					"text": "prepend setPopulations"
				}
			},
			{
				"box": {
					"id": "obj-809",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						990,
						1470,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-810",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1090,
						1470,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-811",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1190,
						1470,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-812",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1290,
						1470,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-813",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1390,
						1470,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-814",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1490,
						1470,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-815",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1057,
						455,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1050,
						231,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-816",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1084,
						455,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1077,
						231,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-817",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1111,
						455,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1104,
						231,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-818",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1138,
						455,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1131,
						231,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-819",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1165,
						455,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1158,
						231,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-820",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1192,
						455,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1185,
						231,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-821",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1219,
						455,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1212,
						231,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-826",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						790,
						1530,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-827",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						890,
						1530,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-828",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						990,
						1530,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-829",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1090,
						1530,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-830",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1190,
						1530,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-831",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1290,
						1530,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-832",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1390,
						1530,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-833",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						1490,
						1530,
						95,
						22
					],
					"text": "clip~ -0.9 0.9"
				}
			},
			{
				"box": {
					"id": "obj-834",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1030,
						520,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1023,
						296,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-835",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1057,
						520,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1050,
						296,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-836",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1084,
						520,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1077,
						296,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-837",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1111,
						520,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1104,
						296,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-838",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1138,
						520,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1131,
						296,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-839",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1165,
						520,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1158,
						296,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-840",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1192,
						520,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1185,
						296,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-841",
					"maxclass": "meter~",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						1219,
						520,
						22,
						58
					],
					"presentation": 1,
					"presentation_rect": [
						1212,
						296,
						22,
						58
					]
				}
			},
			{
				"box": {
					"id": "obj-822",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1030,
						505,
						215,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1030,
						457,
						215,
						20
					],
					"text": "HOA3 · DAC 1–16 · ACN 0–15 · SN3D"
				}
			},
			{
				"box": {
					"id": "obj-823",
					"maxclass": "toggle",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"int"
					],
					"parameter_enable": 0,
					"patching_rect": [
						1260,
						455,
						24,
						24
					],
					"presentation": 1,
					"presentation_rect": [
						1260,
						420,
						24,
						24
					]
				}
			},
			{
				"box": {
					"id": "obj-824",
					"maxclass": "newobj",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"",
						"int"
					],
					"patching_rect": [
						1260,
						490,
						95,
						22
					],
					"text": "adstatus switch"
				}
			},
			{
				"box": {
					"id": "obj-825",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1290,
						457,
						128,
						20
					],
					"presentation": 1,
					"presentation_rect": [
						1290,
						422,
						128,
						20
					],
					"text": "DSP · 16 HOA outputs"
				}
			},
			{
				"box": {
					"id": "obj-900",
					"maxclass": "bpatcher",
					"name": "qmw_four_qubit_state_monitor.maxpat",
					"numinlets": 0,
					"numoutlets": 0,
					"patching_rect": [
						1570,
						80,
						345,
						255
					],
					"presentation": 1,
					"presentation_rect": [
						1260,
						160,
						345,
						255
					],
					"border": 1,
					"viewvisibility": 1
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"destination": [
						"obj-124",
						0
					],
					"order": 0,
					"source": [
						"obj-123",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-8",
						0
					],
					"order": 1,
					"source": [
						"obj-123",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-327",
						0
					],
					"hidden": 1,
					"source": [
						"obj-200",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-204",
						0
					],
					"order": 1,
					"source": [
						"obj-202",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-842",
						0
					],
					"order": 0,
					"source": [
						"obj-202",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-202",
						0
					],
					"source": [
						"obj-203",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-847",
						0
					],
					"source": [
						"obj-850",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-853",
						0
					],
					"source": [
						"obj-847",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-848",
						0
					],
					"source": [
						"obj-851",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-854",
						0
					],
					"source": [
						"obj-848",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-849",
						0
					],
					"source": [
						"obj-852",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-855",
						0
					],
					"source": [
						"obj-849",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-204",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-546",
						1
					],
					"source": [
						"obj-206",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-207",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-206",
						0
					],
					"source": [
						"obj-208",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-211",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-215",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-219",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-223",
						0
					],
					"source": [
						"obj-222",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-223",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-222",
						0
					],
					"source": [
						"obj-224",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-227",
						0
					],
					"source": [
						"obj-226",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-227",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-226",
						0
					],
					"source": [
						"obj-228",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-229",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-231",
						0
					],
					"source": [
						"obj-230",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-232",
						0
					],
					"source": [
						"obj-231",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-233",
						0
					],
					"source": [
						"obj-232",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-233",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-235",
						0
					],
					"source": [
						"obj-234",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-235",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-237",
						0
					],
					"source": [
						"obj-236",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-238",
						0
					],
					"source": [
						"obj-237",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-239",
						0
					],
					"source": [
						"obj-238",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-239",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-241",
						0
					],
					"source": [
						"obj-240",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-241",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-243",
						0
					],
					"source": [
						"obj-242",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-244",
						0
					],
					"source": [
						"obj-243",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-245",
						0
					],
					"source": [
						"obj-244",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-245",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-247",
						0
					],
					"source": [
						"obj-246",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-247",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-249",
						0
					],
					"source": [
						"obj-248",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-250",
						0
					],
					"source": [
						"obj-249",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-251",
						0
					],
					"source": [
						"obj-250",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-251",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-253",
						0
					],
					"source": [
						"obj-252",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-253",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-255",
						0
					],
					"source": [
						"obj-254",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-256",
						0
					],
					"source": [
						"obj-255",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-257",
						0
					],
					"source": [
						"obj-256",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-257",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-259",
						0
					],
					"source": [
						"obj-258",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-259",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-261",
						0
					],
					"source": [
						"obj-260",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-262",
						0
					],
					"source": [
						"obj-261",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-263",
						0
					],
					"source": [
						"obj-262",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-263",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-265",
						0
					],
					"source": [
						"obj-264",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-265",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-267",
						0
					],
					"source": [
						"obj-266",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-268",
						0
					],
					"source": [
						"obj-267",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-269",
						0
					],
					"source": [
						"obj-268",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-269",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-271",
						0
					],
					"source": [
						"obj-270",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-271",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-273",
						0
					],
					"source": [
						"obj-272",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-274",
						0
					],
					"source": [
						"obj-273",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-275",
						0
					],
					"source": [
						"obj-274",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-275",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-277",
						0
					],
					"source": [
						"obj-276",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-277",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-279",
						0
					],
					"source": [
						"obj-278",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-280",
						0
					],
					"source": [
						"obj-279",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-281",
						0
					],
					"source": [
						"obj-280",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-281",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-283",
						0
					],
					"source": [
						"obj-282",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-283",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-285",
						0
					],
					"source": [
						"obj-284",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-286",
						0
					],
					"source": [
						"obj-285",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-287",
						0
					],
					"source": [
						"obj-286",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-287",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-289",
						0
					],
					"source": [
						"obj-288",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-289",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-291",
						0
					],
					"source": [
						"obj-290",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-292",
						0
					],
					"source": [
						"obj-291",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-293",
						0
					],
					"source": [
						"obj-292",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-293",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-295",
						0
					],
					"source": [
						"obj-294",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-295",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-297",
						0
					],
					"source": [
						"obj-296",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-298",
						0
					],
					"source": [
						"obj-297",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-299",
						0
					],
					"source": [
						"obj-298",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-299",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-123",
						0
					],
					"order": 0,
					"source": [
						"obj-3",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-6",
						0
					],
					"order": 1,
					"source": [
						"obj-3",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-301",
						0
					],
					"source": [
						"obj-300",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-301",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-303",
						0
					],
					"source": [
						"obj-302",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-304",
						0
					],
					"source": [
						"obj-303",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-305",
						0
					],
					"source": [
						"obj-304",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-305",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-307",
						0
					],
					"source": [
						"obj-306",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-307",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-309",
						0
					],
					"source": [
						"obj-308",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-310",
						0
					],
					"source": [
						"obj-309",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-311",
						0
					],
					"source": [
						"obj-310",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-311",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-313",
						0
					],
					"source": [
						"obj-312",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-313",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-315",
						0
					],
					"source": [
						"obj-314",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-316",
						0
					],
					"source": [
						"obj-315",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-317",
						0
					],
					"source": [
						"obj-316",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-317",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-319",
						0
					],
					"source": [
						"obj-318",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-319",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-320",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-324",
						0
					],
					"source": [
						"obj-322",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-322",
						0
					],
					"source": [
						"obj-323",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-325",
						0
					],
					"source": [
						"obj-324",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-326",
						0
					],
					"source": [
						"obj-325",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-327",
						1
					],
					"source": [
						"obj-326",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-328",
						0
					],
					"source": [
						"obj-327",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-500",
						0
					],
					"order": 1,
					"source": [
						"obj-328",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-510",
						0
					],
					"order": 0,
					"source": [
						"obj-328",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-229",
						0
					],
					"order": 1,
					"source": [
						"obj-4",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-320",
						0
					],
					"order": 0,
					"source": [
						"obj-4",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-5",
						0
					],
					"order": 2,
					"source": [
						"obj-4",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-401",
						0
					],
					"source": [
						"obj-400",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-402",
						0
					],
					"order": 0,
					"source": [
						"obj-401",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-530",
						0
					],
					"order": 2,
					"source": [
						"obj-401",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-700",
						0
					],
					"order": 1,
					"source": [
						"obj-401",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-403",
						0
					],
					"source": [
						"obj-402",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-404",
						2
					],
					"order": 1,
					"source": [
						"obj-403",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-404",
						1
					],
					"order": 1,
					"source": [
						"obj-403",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-404",
						0
					],
					"order": 1,
					"source": [
						"obj-403",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-415",
						0
					],
					"order": 0,
					"source": [
						"obj-403",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-415",
						0
					],
					"order": 0,
					"source": [
						"obj-403",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-415",
						0
					],
					"order": 0,
					"source": [
						"obj-403",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-405",
						0
					],
					"order": 1,
					"source": [
						"obj-404",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-406",
						0
					],
					"order": 0,
					"source": [
						"obj-404",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-407",
						0
					],
					"source": [
						"obj-405",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-408",
						0
					],
					"source": [
						"obj-406",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-409",
						0
					],
					"order": 0,
					"source": [
						"obj-407",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-418",
						0
					],
					"order": 1,
					"source": [
						"obj-407",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-409",
						1
					],
					"order": 0,
					"source": [
						"obj-408",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-420",
						0
					],
					"order": 1,
					"source": [
						"obj-408",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-410",
						1
					],
					"source": [
						"obj-409",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-411",
						0
					],
					"source": [
						"obj-410",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-410",
						0
					],
					"source": [
						"obj-412",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-412",
						0
					],
					"source": [
						"obj-414",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-3",
						0
					],
					"source": [
						"obj-5",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-513",
						0
					],
					"source": [
						"obj-500",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-514",
						0
					],
					"source": [
						"obj-500",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-505",
						0
					],
					"source": [
						"obj-503",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-503",
						0
					],
					"source": [
						"obj-504",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-506",
						0
					],
					"source": [
						"obj-505",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-507",
						0
					],
					"source": [
						"obj-505",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-500",
						2
					],
					"source": [
						"obj-506",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-509",
						0
					],
					"source": [
						"obj-507",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-510",
						1
					],
					"source": [
						"obj-509",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-511",
						0
					],
					"order": 1,
					"source": [
						"obj-510",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-512",
						0
					],
					"order": 0,
					"source": [
						"obj-510",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-515",
						0
					],
					"source": [
						"obj-511",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-516",
						0
					],
					"source": [
						"obj-512",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-511",
						1
					],
					"source": [
						"obj-513",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-512",
						1
					],
					"source": [
						"obj-514",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-724",
						0
					],
					"source": [
						"obj-515",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-725",
						0
					],
					"source": [
						"obj-516",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-500",
						1
					],
					"source": [
						"obj-518",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-518",
						0
					],
					"source": [
						"obj-519",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-500",
						3
					],
					"source": [
						"obj-522",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-500",
						4
					],
					"source": [
						"obj-524",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-531",
						0
					],
					"order": 1,
					"source": [
						"obj-530",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-807",
						0
					],
					"order": 0,
					"source": [
						"obj-530",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-532",
						0
					],
					"source": [
						"obj-531",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-538",
						0
					],
					"source": [
						"obj-531",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-543",
						0
					],
					"source": [
						"obj-531",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-533",
						0
					],
					"source": [
						"obj-532",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-534",
						0
					],
					"source": [
						"obj-533",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-535",
						0
					],
					"source": [
						"obj-534",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-536",
						0
					],
					"order": 2,
					"source": [
						"obj-535",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-712",
						0
					],
					"order": 1,
					"source": [
						"obj-535",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-806",
						0
					],
					"order": 0,
					"source": [
						"obj-535",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-537",
						0
					],
					"source": [
						"obj-536",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-546",
						0
					],
					"source": [
						"obj-536",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-537",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-539",
						0
					],
					"source": [
						"obj-538",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-540",
						0
					],
					"source": [
						"obj-539",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-541",
						0
					],
					"source": [
						"obj-540",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-542",
						0
					],
					"order": 2,
					"source": [
						"obj-541",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-711",
						0
					],
					"order": 1,
					"source": [
						"obj-541",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-805",
						0
					],
					"order": 0,
					"source": [
						"obj-541",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-200",
						0
					],
					"hidden": 1,
					"source": [
						"obj-542",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-544",
						0
					],
					"source": [
						"obj-543",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-545",
						0
					],
					"source": [
						"obj-544",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-211",
						0
					],
					"order": 0,
					"source": [
						"obj-545",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-710",
						0
					],
					"order": 2,
					"source": [
						"obj-545",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-804",
						0
					],
					"order": 1,
					"source": [
						"obj-545",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-547",
						0
					],
					"source": [
						"obj-546",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-207",
						0
					],
					"source": [
						"obj-547",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-7",
						0
					],
					"source": [
						"obj-6",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-124",
						0
					],
					"order": 0,
					"source": [
						"obj-7",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-8",
						0
					],
					"order": 1,
					"source": [
						"obj-7",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-706",
						0
					],
					"order": 2,
					"source": [
						"obj-700",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-707",
						0
					],
					"order": 2,
					"source": [
						"obj-700",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-708",
						0
					],
					"order": 2,
					"source": [
						"obj-700",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-709",
						0
					],
					"order": 2,
					"source": [
						"obj-700",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						9
					],
					"order": 0,
					"source": [
						"obj-700",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						8
					],
					"order": 0,
					"source": [
						"obj-700",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						7
					],
					"order": 0,
					"source": [
						"obj-700",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						6
					],
					"order": 0,
					"source": [
						"obj-700",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-800",
						0
					],
					"order": 1,
					"source": [
						"obj-700",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-801",
						0
					],
					"order": 1,
					"source": [
						"obj-700",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-802",
						0
					],
					"order": 1,
					"source": [
						"obj-700",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-803",
						0
					],
					"order": 1,
					"source": [
						"obj-700",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						0
					],
					"source": [
						"obj-713",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						1
					],
					"source": [
						"obj-714",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						2
					],
					"source": [
						"obj-715",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						3
					],
					"source": [
						"obj-716",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-728",
						0
					],
					"source": [
						"obj-717",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-729",
						0
					],
					"source": [
						"obj-717",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-809",
						0
					],
					"source": [
						"obj-717",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-810",
						0
					],
					"source": [
						"obj-717",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-811",
						0
					],
					"source": [
						"obj-717",
						4
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-812",
						0
					],
					"source": [
						"obj-717",
						5
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-813",
						0
					],
					"source": [
						"obj-717",
						6
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-814",
						0
					],
					"source": [
						"obj-717",
						7
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-826",
						0
					],
					"source": [
						"obj-717",
						8
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-827",
						0
					],
					"source": [
						"obj-717",
						9
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-828",
						0
					],
					"source": [
						"obj-717",
						10
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-829",
						0
					],
					"source": [
						"obj-717",
						11
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-830",
						0
					],
					"source": [
						"obj-717",
						12
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-831",
						0
					],
					"source": [
						"obj-717",
						13
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-832",
						0
					],
					"source": [
						"obj-717",
						14
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-833",
						0
					],
					"source": [
						"obj-717",
						15
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-720",
						0
					],
					"source": [
						"obj-718",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-718",
						0
					],
					"source": [
						"obj-719",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-723",
						0
					],
					"source": [
						"obj-721",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-721",
						0
					],
					"source": [
						"obj-722",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-724",
						1
					],
					"order": 1,
					"source": [
						"obj-723",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-725",
						1
					],
					"order": 0,
					"source": [
						"obj-723",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						4
					],
					"source": [
						"obj-724",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						5
					],
					"source": [
						"obj-725",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-329",
						0
					],
					"order": 1,
					"source": [
						"obj-728",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						0
					],
					"order": 0,
					"source": [
						"obj-728",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						1
					],
					"order": 0,
					"source": [
						"obj-729",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-815",
						0
					],
					"order": 1,
					"source": [
						"obj-729",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						11
					],
					"source": [
						"obj-730",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-737",
						0
					],
					"source": [
						"obj-736",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-717",
						10
					],
					"source": [
						"obj-737",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-736",
						0
					],
					"source": [
						"obj-738",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-10",
						0
					],
					"source": [
						"obj-8",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-12",
						0
					],
					"source": [
						"obj-8",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-14",
						0
					],
					"source": [
						"obj-8",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-16",
						0
					],
					"source": [
						"obj-8",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-18",
						0
					],
					"source": [
						"obj-8",
						4
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-230",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						5
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-234",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						5
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-236",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						6
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-240",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						6
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-242",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						7
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-246",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						7
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-248",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						8
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-252",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						8
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-254",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						9
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-258",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						9
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-260",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						10
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-264",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						10
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-266",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						11
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-270",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						11
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-272",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						12
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-276",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						12
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-278",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						13
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-282",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						13
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-284",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						14
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-288",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						14
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-290",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						15
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-294",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						15
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-296",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						16
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-300",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						16
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-302",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						17
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-306",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						17
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-308",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						18
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-312",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						18
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-314",
						0
					],
					"order": 1,
					"source": [
						"obj-8",
						19
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-318",
						0
					],
					"order": 0,
					"source": [
						"obj-8",
						19
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-3",
						0
					],
					"source": [
						"obj-800",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-3",
						0
					],
					"source": [
						"obj-801",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-3",
						0
					],
					"source": [
						"obj-802",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-3",
						0
					],
					"source": [
						"obj-803",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-210",
						0
					],
					"source": [
						"obj-804",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-214",
						0
					],
					"source": [
						"obj-805",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-218",
						0
					],
					"source": [
						"obj-806",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-808",
						0
					],
					"source": [
						"obj-807",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-3",
						0
					],
					"source": [
						"obj-808",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						2
					],
					"order": 0,
					"source": [
						"obj-809",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-816",
						0
					],
					"order": 1,
					"source": [
						"obj-809",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						3
					],
					"order": 0,
					"source": [
						"obj-810",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-817",
						0
					],
					"order": 1,
					"source": [
						"obj-810",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						4
					],
					"order": 0,
					"source": [
						"obj-811",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-818",
						0
					],
					"order": 1,
					"source": [
						"obj-811",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						5
					],
					"order": 0,
					"source": [
						"obj-812",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-819",
						0
					],
					"order": 1,
					"source": [
						"obj-812",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						6
					],
					"order": 0,
					"source": [
						"obj-813",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-820",
						0
					],
					"order": 1,
					"source": [
						"obj-813",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						7
					],
					"order": 0,
					"source": [
						"obj-814",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-821",
						0
					],
					"order": 1,
					"source": [
						"obj-814",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-824",
						0
					],
					"source": [
						"obj-823",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						8
					],
					"order": 0,
					"source": [
						"obj-826",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-834",
						0
					],
					"order": 1,
					"source": [
						"obj-826",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						9
					],
					"order": 0,
					"source": [
						"obj-827",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-835",
						0
					],
					"order": 1,
					"source": [
						"obj-827",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						10
					],
					"order": 0,
					"source": [
						"obj-828",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-836",
						0
					],
					"order": 1,
					"source": [
						"obj-828",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						11
					],
					"order": 0,
					"source": [
						"obj-829",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-837",
						0
					],
					"order": 1,
					"source": [
						"obj-829",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						12
					],
					"order": 0,
					"source": [
						"obj-830",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-838",
						0
					],
					"order": 1,
					"source": [
						"obj-830",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						13
					],
					"order": 0,
					"source": [
						"obj-831",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-839",
						0
					],
					"order": 1,
					"source": [
						"obj-831",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						14
					],
					"order": 0,
					"source": [
						"obj-832",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-840",
						0
					],
					"order": 1,
					"source": [
						"obj-832",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-330",
						15
					],
					"order": 0,
					"source": [
						"obj-833",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-841",
						0
					],
					"order": 1,
					"source": [
						"obj-833",
						0
					]
				}
			}
		],
		"originid": "pat-4",
		"dependency_cache": [
			{
				"name": "OSC-route.mxo",
				"type": "iLaX"
			},
			{
				"name": "dcblocker~.mxo",
				"type": "iLaX"
			},
			{
				"name": "multiconvolve~.mxo",
				"type": "iLaX"
			},
			{
				"name": "qmw_bloch_convolution_ir~.maxpat",
				"bootpath": "~/QuantumSonification/BLOCH_HARMONICS/bloch_harmonics_four_qubit_spat_v8",
				"patcherrelativepath": ".",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "qmw_density_field_resonator.gendsp",
				"bootpath": "~/QuantumSonification/BLOCH_HARMONICS/bloch_harmonics_four_qubit_spat_v8",
				"patcherrelativepath": ".",
				"type": "gDSP",
				"implicit": 1
			},
			{
				"name": "qmw_four_qubit_spat5_hoa3~.maxpat",
				"bootpath": "~/QuantumSonification/BLOCH_HARMONICS/bloch_harmonics_four_qubit_spat_v8",
				"patcherrelativepath": ".",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "qmw_qubit_genexpr_voice~.maxpat",
				"bootpath": "~/QuantumSonification/BLOCH_HARMONICS/bloch_harmonics_four_qubit_spat_v8",
				"patcherrelativepath": ".",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "qmw_qubit_resonator.gendsp",
				"bootpath": "~/QuantumSonification/BLOCH_HARMONICS/bloch_harmonics_four_qubit_spat_v8",
				"patcherrelativepath": ".",
				"type": "gDSP",
				"implicit": 1
			},
			{
				"name": "qmw_qubit_spat_control.maxpat",
				"bootpath": "~/QuantumSonification/BLOCH_HARMONICS/bloch_harmonics_four_qubit_spat_v8",
				"patcherrelativepath": ".",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "spat5.oper.mxo",
				"type": "iLaX"
			},
			{
				"name": "spat5.spat~.mxo",
				"type": "iLaX"
			},
			{
				"name": "qmw_four_qubit_state_monitor.maxpat",
				"type": "JSON",
				"implicit": 1
			}
		],
		"autosave": 0
	}
}
