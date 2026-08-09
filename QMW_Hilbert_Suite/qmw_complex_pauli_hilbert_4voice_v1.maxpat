{
	"patcher" : {
		"fileversion" : 1,
		"appversion" : {
			"major" : 9,
			"minor" : 0,
			"revision" : 0,
			"architecture" : "x64",
			"modernui" : 1
		},
		"classnamespace" : "box",
		"rect" : [ 50.0, 50.0, 1430.0, 930.0 ],
		"bglocked" : 0,
		"openinpresentation" : 0,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"description" : "Four-voice MC Hilbert processor for the QMW Complex Pauli Synth.",
		"digest" : "Applies four quantum complex coefficients to four analytic audio voices.",
		"tags" : "MC hilbert Pauli complex synthesis density matrix",
		"boxes" : [
			{
				"box" : {
					"id" : "obj-1",
					"maxclass" : "comment",
					"fontsize" : 21.0,
					"fontface" : 1,
					"text" : "QMW Complex Pauli Hilbert — 4 Voice v1",
					"patching_rect" : [ 30.0, 20.0, 470.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-2",
					"maxclass" : "comment",
					"fontsize" : 13.0,
					"text" : "Four Gen~ voices -> mc.hilbert~ -> (I+iQ)(a+ib) -> complex MC field",
					"patching_rect" : [ 31.0, 53.0, 570.0, 21.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-3",
					"maxclass" : "inlet",
					"index" : 1,
					"comment" : "q0 audio signal",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 45.0, 115.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-4",
					"maxclass" : "inlet",
					"index" : 2,
					"comment" : "q1 audio signal",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 115.0, 115.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-5",
					"maxclass" : "inlet",
					"index" : 3,
					"comment" : "q2 audio signal",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 185.0, 115.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-6",
					"maxclass" : "inlet",
					"index" : 4,
					"comment" : "q3 audio signal",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 255.0, 115.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-7",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "q0          q1          q2          q3",
					"patching_rect" : [ 43.0, 90.0, 260.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-8",
					"maxclass" : "inlet",
					"index" : 5,
					"comment" : "complex real coefficient list a0 a1 a2 a3",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 500.0, 115.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-9",
					"maxclass" : "inlet",
					"index" : 6,
					"comment" : "complex imaginary coefficient list b0 b1 b2 b3",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 665.0, 115.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-10",
					"maxclass" : "comment",
					"text" : "a list: real / Pauli x",
					"patching_rect" : [ 465.0, 90.0, 135.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-11",
					"maxclass" : "comment",
					"text" : "b list: imag / Pauli y",
					"patching_rect" : [ 630.0, 90.0, 145.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-12",
					"maxclass" : "newobj",
					"text" : "mc.pack~ 4",
					"numinlets" : 4,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 125.0, 185.0, 82.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-13",
					"maxclass" : "newobj",
					"text" : "mc.meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 30.0, 225.0, 78.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-14",
					"maxclass" : "newobj",
					"text" : "mc.hilbert~",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "multichannelsignal", "multichannelsignal" ],
					"patching_rect" : [ 125.0, 250.0, 82.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-15",
					"maxclass" : "message",
					"text" : "clear",
					"patching_rect" : [ 220.0, 250.0, 40.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-16",
					"maxclass" : "newobj",
					"text" : "mc.list~ 1. 1. 1. 1. @chans 4",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 450.0, 185.0, 190.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-17",
					"maxclass" : "newobj",
					"text" : "mc.rampsmooth~ 960 960",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 465.0, 225.0, 155.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-18",
					"maxclass" : "newobj",
					"text" : "mc.list~ 0. 0. 0. 0. @chans 4",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 650.0, 185.0, 190.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-19",
					"maxclass" : "newobj",
					"text" : "mc.rampsmooth~ 960 960",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 665.0, 225.0, 155.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-20",
					"maxclass" : "comment",
					"text" : "960 samples of smoothing prevents list-rate coefficient clicks without inventing motion.",
					"patching_rect" : [ 465.0, 255.0, 470.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-21",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 390.0, 330.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-22",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 480.0, 330.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-23",
					"maxclass" : "newobj",
					"text" : "mc.-~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 435.0, 385.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-24",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 585.0, 330.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-25",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 675.0, 330.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-26",
					"maxclass" : "newobj",
					"text" : "mc.+~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 630.0, 385.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-27",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "real = Ia - Qb",
					"patching_rect" : [ 415.0, 415.0, 115.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-28",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "imag = Ib + Qa",
					"patching_rect" : [ 610.0, 415.0, 120.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-29",
					"maxclass" : "flonum",
					"format" : 6,
					"minimum" : 0.0,
					"maximum" : 1.0,
					"patching_rect" : [ 930.0, 255.0, 70.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-30",
					"maxclass" : "comment",
					"text" : "Hilbert wet",
					"patching_rect" : [ 1007.0, 257.0, 80.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-31",
					"maxclass" : "newobj",
					"text" : "pack 0. 50",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 930.0, 290.0, 75.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-32",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 930.0, 325.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-33",
					"maxclass" : "newobj",
					"text" : "!- 1.",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1025.0, 290.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-34",
					"maxclass" : "newobj",
					"text" : "pack 0. 50",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1025.0, 325.0, 75.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-35",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 1025.0, 360.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-36",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 890.0, 410.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-37",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 1020.0, 410.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-38",
					"maxclass" : "newobj",
					"text" : "mc.+~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 955.0, 455.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-39",
					"maxclass" : "comment",
					"text" : "audition output: dry synth <-> transformed real field",
					"patching_rect" : [ 870.0, 485.0, 300.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-40",
					"maxclass" : "outlet",
					"index" : 1,
					"comment" : "four-channel complex real MC output",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 435.0, 500.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-41",
					"maxclass" : "outlet",
					"index" : 2,
					"comment" : "four-channel complex imaginary MC output",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 630.0, 500.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-42",
					"maxclass" : "outlet",
					"index" : 3,
					"comment" : "four-channel dry-wet audition MC output",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 965.0, 525.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-43",
					"maxclass" : "newobj",
					"text" : "loadbang",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 1210.0, 110.0, 60.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-44",
					"maxclass" : "message",
					"text" : "1. 1. 1. 1.",
					"patching_rect" : [ 1120.0, 150.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-45",
					"maxclass" : "message",
					"text" : "0. 0. 0. 0.",
					"patching_rect" : [ 1220.0, 150.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-46",
					"maxclass" : "message",
					"text" : "1.",
					"patching_rect" : [ 1320.0, 150.0, 32.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-47",
					"maxclass" : "number",
					"minimum" : 1,
					"maximum" : 4,
					"patching_rect" : [ 1115.0, 595.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-48",
					"maxclass" : "comment",
					"text" : "scope voice q0=1 ... q3=4",
					"patching_rect" : [ 1172.0, 597.0, 170.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-49",
					"maxclass" : "newobj",
					"text" : "mc.unpack~ 4",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "signal", "signal", "signal", "signal" ],
					"patching_rect" : [ 60.0, 590.0, 100.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-50",
					"maxclass" : "newobj",
					"text" : "mc.unpack~ 4",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "signal", "signal", "signal", "signal" ],
					"patching_rect" : [ 195.0, 590.0, 100.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-51",
					"maxclass" : "newobj",
					"text" : "mc.unpack~ 4",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "signal", "signal", "signal", "signal" ],
					"patching_rect" : [ 510.0, 590.0, 100.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-52",
					"maxclass" : "newobj",
					"text" : "mc.unpack~ 4",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "signal", "signal", "signal", "signal" ],
					"patching_rect" : [ 645.0, 590.0, 100.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-53",
					"maxclass" : "newobj",
					"text" : "selector~ 4",
					"numinlets" : 5,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 85.0, 635.0, 95.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-54",
					"maxclass" : "newobj",
					"text" : "selector~ 4",
					"numinlets" : 5,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 220.0, 635.0, 95.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-55",
					"maxclass" : "newobj",
					"text" : "selector~ 4",
					"numinlets" : 5,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 535.0, 635.0, 95.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-56",
					"maxclass" : "newobj",
					"text" : "selector~ 4",
					"numinlets" : 5,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 670.0, 635.0, 95.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-57",
					"maxclass" : "scope~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"bufsize" : 1024,
					"calccount" : 2,
					"drawstyle" : 1,
					"range" : [ -1.0, 1.0 ],
					"bgcolor" : [ 0.025, 0.035, 0.05, 1.0 ],
					"fgcolor" : [ 0.2, 0.95, 0.8, 1.0 ],
					"gridcolor" : [ 0.18, 0.22, 0.28, 1.0 ],
					"patching_rect" : [ 70.0, 700.0, 300.0, 180.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-58",
					"maxclass" : "scope~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"bufsize" : 1024,
					"calccount" : 2,
					"drawstyle" : 1,
					"range" : [ -1.0, 1.0 ],
					"bgcolor" : [ 0.025, 0.035, 0.05, 1.0 ],
					"fgcolor" : [ 0.95, 0.55, 0.25, 1.0 ],
					"gridcolor" : [ 0.18, 0.22, 0.28, 1.0 ],
					"patching_rect" : [ 480.0, 700.0, 300.0, 180.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-59",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "HILBERT I / Q",
					"patching_rect" : [ 70.0, 675.0, 125.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-60",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "AFTER PAULI COMPLEX MULTIPLICATION",
					"patching_rect" : [ 480.0, 675.0, 280.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-61",
					"maxclass" : "comment",
					"text" : "Identity lists 1+0i are the neutral baseline. Feeding the same x/y that already shaped the source is a recursive c²-like mode.",
					"patching_rect" : [ 860.0, 705.0, 525.0, 35.0 ],
					"linecount" : 2
				}
			},
			{
				"box" : {
					"id" : "obj-62",
					"maxclass" : "comment",
					"text" : "For relational coupling, feed a distinct four-element density-matrix off-diagonal real/imag stream into inlets 5 and 6.",
					"patching_rect" : [ 860.0, 750.0, 525.0, 35.0 ],
					"linecount" : 2
				}
			},
			{
				"box" : {
					"id" : "obj-63",
					"maxclass" : "message",
					"text" : "0.",
					"patching_rect" : [ 1275.0, 190.0, 32.0, 22.0 ]
				}
			}
		],
		"lines" : [
			{ "patchline" : { "source" : [ "obj-3", 0 ], "destination" : [ "obj-12", 0 ] } },
			{ "patchline" : { "source" : [ "obj-4", 0 ], "destination" : [ "obj-12", 1 ] } },
			{ "patchline" : { "source" : [ "obj-5", 0 ], "destination" : [ "obj-12", 2 ] } },
			{ "patchline" : { "source" : [ "obj-6", 0 ], "destination" : [ "obj-12", 3 ] } },
			{ "patchline" : { "source" : [ "obj-8", 0 ], "destination" : [ "obj-16", 0 ] } },
			{ "patchline" : { "source" : [ "obj-9", 0 ], "destination" : [ "obj-18", 0 ] } },
			{ "patchline" : { "source" : [ "obj-12", 0 ], "destination" : [ "obj-13", 0 ] } },
			{ "patchline" : { "source" : [ "obj-12", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-15", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-16", 0 ], "destination" : [ "obj-17", 0 ] } },
			{ "patchline" : { "source" : [ "obj-18", 0 ], "destination" : [ "obj-19", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 0 ], "destination" : [ "obj-21", 0 ] } },
			{ "patchline" : { "source" : [ "obj-17", 0 ], "destination" : [ "obj-21", 1 ] } },
			{ "patchline" : { "source" : [ "obj-14", 1 ], "destination" : [ "obj-22", 0 ] } },
			{ "patchline" : { "source" : [ "obj-19", 0 ], "destination" : [ "obj-22", 1 ] } },
			{ "patchline" : { "source" : [ "obj-21", 0 ], "destination" : [ "obj-23", 0 ] } },
			{ "patchline" : { "source" : [ "obj-22", 0 ], "destination" : [ "obj-23", 1 ] } },
			{ "patchline" : { "source" : [ "obj-14", 0 ], "destination" : [ "obj-24", 0 ] } },
			{ "patchline" : { "source" : [ "obj-19", 0 ], "destination" : [ "obj-24", 1 ] } },
			{ "patchline" : { "source" : [ "obj-14", 1 ], "destination" : [ "obj-25", 0 ] } },
			{ "patchline" : { "source" : [ "obj-17", 0 ], "destination" : [ "obj-25", 1 ] } },
			{ "patchline" : { "source" : [ "obj-24", 0 ], "destination" : [ "obj-26", 0 ] } },
			{ "patchline" : { "source" : [ "obj-25", 0 ], "destination" : [ "obj-26", 1 ] } },
			{ "patchline" : { "source" : [ "obj-29", 0 ], "destination" : [ "obj-31", 0 ] } },
			{ "patchline" : { "source" : [ "obj-29", 0 ], "destination" : [ "obj-33", 0 ] } },
			{ "patchline" : { "source" : [ "obj-31", 0 ], "destination" : [ "obj-32", 0 ] } },
			{ "patchline" : { "source" : [ "obj-33", 0 ], "destination" : [ "obj-34", 0 ] } },
			{ "patchline" : { "source" : [ "obj-34", 0 ], "destination" : [ "obj-35", 0 ] } },
			{ "patchline" : { "source" : [ "obj-23", 0 ], "destination" : [ "obj-36", 0 ] } },
			{ "patchline" : { "source" : [ "obj-32", 0 ], "destination" : [ "obj-36", 1 ] } },
			{ "patchline" : { "source" : [ "obj-12", 0 ], "destination" : [ "obj-37", 0 ] } },
			{ "patchline" : { "source" : [ "obj-35", 0 ], "destination" : [ "obj-37", 1 ] } },
			{ "patchline" : { "source" : [ "obj-36", 0 ], "destination" : [ "obj-38", 0 ] } },
			{ "patchline" : { "source" : [ "obj-37", 0 ], "destination" : [ "obj-38", 1 ] } },
			{ "patchline" : { "source" : [ "obj-23", 0 ], "destination" : [ "obj-40", 0 ] } },
			{ "patchline" : { "source" : [ "obj-26", 0 ], "destination" : [ "obj-41", 0 ] } },
			{ "patchline" : { "source" : [ "obj-38", 0 ], "destination" : [ "obj-42", 0 ] } },
			{ "patchline" : { "source" : [ "obj-43", 0 ], "destination" : [ "obj-44", 0 ] } },
			{ "patchline" : { "source" : [ "obj-43", 0 ], "destination" : [ "obj-45", 0 ] } },
			{ "patchline" : { "source" : [ "obj-43", 0 ], "destination" : [ "obj-46", 0 ] } },
			{ "patchline" : { "source" : [ "obj-43", 0 ], "destination" : [ "obj-63", 0 ] } },
			{ "patchline" : { "source" : [ "obj-44", 0 ], "destination" : [ "obj-16", 0 ] } },
			{ "patchline" : { "source" : [ "obj-45", 0 ], "destination" : [ "obj-18", 0 ] } },
			{ "patchline" : { "source" : [ "obj-46", 0 ], "destination" : [ "obj-47", 0 ] } },
			{ "patchline" : { "source" : [ "obj-63", 0 ], "destination" : [ "obj-29", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 0 ], "destination" : [ "obj-49", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 1 ], "destination" : [ "obj-50", 0 ] } },
			{ "patchline" : { "source" : [ "obj-23", 0 ], "destination" : [ "obj-51", 0 ] } },
			{ "patchline" : { "source" : [ "obj-26", 0 ], "destination" : [ "obj-52", 0 ] } },
			{ "patchline" : { "source" : [ "obj-47", 0 ], "destination" : [ "obj-53", 0 ] } },
			{ "patchline" : { "source" : [ "obj-47", 0 ], "destination" : [ "obj-54", 0 ] } },
			{ "patchline" : { "source" : [ "obj-47", 0 ], "destination" : [ "obj-55", 0 ] } },
			{ "patchline" : { "source" : [ "obj-47", 0 ], "destination" : [ "obj-56", 0 ] } },
			{ "patchline" : { "source" : [ "obj-49", 0 ], "destination" : [ "obj-53", 1 ] } },
			{ "patchline" : { "source" : [ "obj-49", 1 ], "destination" : [ "obj-53", 2 ] } },
			{ "patchline" : { "source" : [ "obj-49", 2 ], "destination" : [ "obj-53", 3 ] } },
			{ "patchline" : { "source" : [ "obj-49", 3 ], "destination" : [ "obj-53", 4 ] } },
			{ "patchline" : { "source" : [ "obj-50", 0 ], "destination" : [ "obj-54", 1 ] } },
			{ "patchline" : { "source" : [ "obj-50", 1 ], "destination" : [ "obj-54", 2 ] } },
			{ "patchline" : { "source" : [ "obj-50", 2 ], "destination" : [ "obj-54", 3 ] } },
			{ "patchline" : { "source" : [ "obj-50", 3 ], "destination" : [ "obj-54", 4 ] } },
			{ "patchline" : { "source" : [ "obj-51", 0 ], "destination" : [ "obj-55", 1 ] } },
			{ "patchline" : { "source" : [ "obj-51", 1 ], "destination" : [ "obj-55", 2 ] } },
			{ "patchline" : { "source" : [ "obj-51", 2 ], "destination" : [ "obj-55", 3 ] } },
			{ "patchline" : { "source" : [ "obj-51", 3 ], "destination" : [ "obj-55", 4 ] } },
			{ "patchline" : { "source" : [ "obj-52", 0 ], "destination" : [ "obj-56", 1 ] } },
			{ "patchline" : { "source" : [ "obj-52", 1 ], "destination" : [ "obj-56", 2 ] } },
			{ "patchline" : { "source" : [ "obj-52", 2 ], "destination" : [ "obj-56", 3 ] } },
			{ "patchline" : { "source" : [ "obj-52", 3 ], "destination" : [ "obj-56", 4 ] } },
			{ "patchline" : { "source" : [ "obj-53", 0 ], "destination" : [ "obj-57", 0 ] } },
			{ "patchline" : { "source" : [ "obj-54", 0 ], "destination" : [ "obj-57", 1 ] } },
			{ "patchline" : { "source" : [ "obj-55", 0 ], "destination" : [ "obj-58", 0 ] } },
			{ "patchline" : { "source" : [ "obj-56", 0 ], "destination" : [ "obj-58", 1 ] } }
		],
		"dependency_cache" : [ ],
		"autosave" : 0
	}
}
