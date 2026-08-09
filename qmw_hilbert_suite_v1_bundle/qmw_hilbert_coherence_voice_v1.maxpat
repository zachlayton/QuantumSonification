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
		"rect" : [ 58.0, 40.0, 1370.0, 1080.0 ],
		"bglocked" : 0,
		"openinpresentation" : 0,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"statusbarvisible" : 2,
		"toolbarvisible" : 1,
		"lefttoolbarpinned" : 0,
		"toptoolbarpinned" : 0,
		"righttoolbarpinned" : 0,
		"bottomtoolbarpinned" : 0,
		"toolbars_unpinned_last_save" : 0,
		"tallnewobj" : 0,
		"boxanimatetime" : 200,
		"enablehscroll" : 1,
		"enablevscroll" : 1,
		"devicewidth" : 0.0,
		"description" : "Hilbert analytic-signal test voice for complex quantum coherence and SSB translation.",
		"digest" : "Real audio becomes I+iQ, then multiplies a+ib.",
		"tags" : "hilbert analytic signal quantum coherence pauli density matrix",
		"boxes" : [
			{
				"box" : {
					"id" : "obj-1",
					"maxclass" : "comment",
					"fontsize" : 22.0,
					"fontface" : 1,
					"text" : "QMW Hilbert Coherence Voice v1",
					"patching_rect" : [ 30.0, 20.0, 420.0, 31.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-2",
					"maxclass" : "comment",
					"fontsize" : 13.0,
					"text" : "x(t) -> hilbert~ -> I+iQ;  (I+iQ)(a+ib) = (Ia-Qb) + i(Ib+Qa)",
					"patching_rect" : [ 31.0, 53.0, 650.0, 21.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-3",
					"maxclass" : "inlet",
					"index" : 1,
					"comment" : "external audio signal",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 35.0, 135.0, 30.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-4",
					"maxclass" : "comment",
					"text" : "external audio inlet",
					"patching_rect" : [ 28.0, 110.0, 130.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-5",
					"maxclass" : "newobj",
					"text" : "cycle~ 110.",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 185.0, 160.0, 77.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-6",
					"maxclass" : "flonum",
					"format" : 6,
					"minimum" : 0.01,
					"patching_rect" : [ 185.0, 130.0, 72.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-7",
					"maxclass" : "comment",
					"text" : "test frequency Hz",
					"patching_rect" : [ 265.0, 132.0, 115.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-8",
					"maxclass" : "number",
					"minimum" : 1,
					"maximum" : 3,
					"patching_rect" : [ 35.0, 205.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-9",
					"maxclass" : "comment",
					"text" : "source: 1 sine / 2 harmonic geometry / 3 inlet",
					"patching_rect" : [ 92.0, 207.0, 155.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-10",
					"maxclass" : "newobj",
					"text" : "selector~ 3",
					"numinlets" : 4,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 115.0, 245.0, 80.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-11",
					"maxclass" : "flonum",
					"format" : 6,
					"minimum" : 0.0,
					"maximum" : 1.0,
					"patching_rect" : [ 220.0, 245.0, 65.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-12",
					"maxclass" : "comment",
					"text" : "source gain",
					"patching_rect" : [ 292.0, 247.0, 90.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-13",
					"maxclass" : "newobj",
					"text" : "pack 0. 20",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 220.0, 275.0, 75.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-14",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 220.0, 305.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-15",
					"maxclass" : "newobj",
					"text" : "*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 115.0, 305.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-16",
					"maxclass" : "newobj",
					"text" : "hilbert~",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 115.0, 360.0, 63.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-17",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "ANALYTIC AUDIO",
					"patching_rect" : [ 30.0, 335.0, 125.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-18",
					"maxclass" : "number~",
					"mode" : 2,
					"patching_rect" : [ 30.0, 415.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-19",
					"maxclass" : "number~",
					"mode" : 2,
					"patching_rect" : [ 135.0, 415.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-20",
					"maxclass" : "newobj",
					"text" : "cartopol~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 115.0, 460.0, 70.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-21",
					"maxclass" : "number~",
					"mode" : 2,
					"patching_rect" : [ 30.0, 500.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-22",
					"maxclass" : "number~",
					"mode" : 2,
					"patching_rect" : [ 135.0, 500.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-23",
					"maxclass" : "comment",
					"text" : "I (real)               Q (imag)                  magnitude          phase radians",
					"patching_rect" : [ 30.0, 390.0, 360.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-24",
					"maxclass" : "flonum",
					"format" : 6,
					"patching_rect" : [ 465.0, 150.0, 80.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-25",
					"maxclass" : "flonum",
					"format" : 6,
					"patching_rect" : [ 570.0, 150.0, 80.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-26",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "QUANTUM COHERENCE  c = a + ib",
					"patching_rect" : [ 435.0, 105.0, 255.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-27",
					"maxclass" : "newobj",
					"text" : "pack 0. 25",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 465.0, 185.0, 75.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-28",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 465.0, 220.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-29",
					"maxclass" : "newobj",
					"text" : "pack 0. 25",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 570.0, 185.0, 75.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-30",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 570.0, 220.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-31",
					"maxclass" : "newobj",
					"text" : "*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 430.0, 340.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-32",
					"maxclass" : "newobj",
					"text" : "*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 505.0, 340.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-33",
					"maxclass" : "newobj",
					"text" : "-~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 465.0, 390.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-34",
					"maxclass" : "newobj",
					"text" : "*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 575.0, 340.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-35",
					"maxclass" : "newobj",
					"text" : "*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 650.0, 340.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-36",
					"maxclass" : "newobj",
					"text" : "+~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 615.0, 390.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-37",
					"maxclass" : "newobj",
					"text" : "cartopol~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 520.0, 260.0, 70.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-38",
					"maxclass" : "number~",
					"mode" : 2,
					"patching_rect" : [ 445.0, 295.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-39",
					"maxclass" : "number~",
					"mode" : 2,
					"patching_rect" : [ 555.0, 295.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-40",
					"maxclass" : "comment",
					"text" : "|c|                         arg(c) radians",
					"patching_rect" : [ 447.0, 275.0, 245.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-41",
					"maxclass" : "message",
					"text" : "1. 0.",
					"patching_rect" : [ 700.0, 145.0, 48.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-42",
					"maxclass" : "message",
					"text" : "0. 1.",
					"patching_rect" : [ 755.0, 145.0, 48.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-43",
					"maxclass" : "message",
					"text" : "0. -1.",
					"patching_rect" : [ 810.0, 145.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-44",
					"maxclass" : "message",
					"text" : "0.7071 0.7071",
					"patching_rect" : [ 870.0, 145.0, 100.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-45",
					"maxclass" : "message",
					"text" : "0.5 0.",
					"patching_rect" : [ 980.0, 145.0, 53.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-46",
					"maxclass" : "newobj",
					"text" : "unpack 0. 0.",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "float" ],
					"patching_rect" : [ 700.0, 185.0, 83.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-47",
					"maxclass" : "comment",
					"text" : "presets: identity / +90deg / -90deg / +45deg / attenuate",
					"patching_rect" : [ 700.0, 118.0, 365.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-48",
					"maxclass" : "flonum",
					"format" : 6,
					"patching_rect" : [ 820.0, 285.0, 80.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-49",
					"maxclass" : "newobj",
					"text" : "pack 0. 50",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 820.0, 320.0, 75.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-50",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 820.0, 355.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-51",
					"maxclass" : "newobj",
					"text" : "phasor~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 820.0, 390.0, 55.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-52",
					"maxclass" : "newobj",
					"text" : "cos~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 790.0, 435.0, 42.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-53",
					"maxclass" : "newobj",
					"text" : "-~ 0.25",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 875.0, 435.0, 58.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-54",
					"maxclass" : "newobj",
					"text" : "cos~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 883.0, 470.0, 42.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-55",
					"maxclass" : "newobj",
					"text" : "*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 760.0, 520.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-56",
					"maxclass" : "newobj",
					"text" : "*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 865.0, 520.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-57",
					"maxclass" : "newobj",
					"text" : "-~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 790.0, 565.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-58",
					"maxclass" : "newobj",
					"text" : "+~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 865.0, 565.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-59",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "SSB AUDITION: complex carrier at shift Hz",
					"patching_rect" : [ 785.0, 250.0, 295.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-60",
					"maxclass" : "number",
					"minimum" : 1,
					"maximum" : 4,
					"patching_rect" : [ 1045.0, 395.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-61",
					"maxclass" : "comment",
					"text" : "output: 1 coherence real / 2 coherence imag / 3 +SSB / 4 -SSB",
					"patching_rect" : [ 1045.0, 370.0, 325.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-62",
					"maxclass" : "newobj",
					"text" : "selector~ 4",
					"numinlets" : 5,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1045.0, 450.0, 95.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-63",
					"maxclass" : "flonum",
					"format" : 6,
					"minimum" : 0.0,
					"maximum" : 1.0,
					"patching_rect" : [ 1190.0, 450.0, 70.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-64",
					"maxclass" : "comment",
					"text" : "master",
					"patching_rect" : [ 1265.0, 452.0, 55.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-65",
					"maxclass" : "newobj",
					"text" : "pack 0. 50",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1190.0, 485.0, 75.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-66",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 1190.0, 520.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-67",
					"maxclass" : "newobj",
					"text" : "*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1090.0, 520.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-68",
					"maxclass" : "newobj",
					"text" : "clip~ -0.95 0.95",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1060.0, 565.0, 110.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-69",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1190.0, 565.0, 80.0, 13.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-70",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 1085.0, 620.0, 45.0, 45.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-71",
					"maxclass" : "outlet",
					"index" : 1,
					"comment" : "complex product real output",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 465.0, 520.0, 30.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-72",
					"maxclass" : "outlet",
					"index" : 2,
					"comment" : "complex product imaginary output",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 615.0, 520.0, 30.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-73",
					"maxclass" : "outlet",
					"index" : 3,
					"comment" : "selected audition signal before master gain",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1035.0, 620.0, 30.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-74",
					"maxclass" : "comment",
					"text" : "outlets: coherence real                 coherence imag                                      selected (pre-master)",
					"patching_rect" : [ 430.0, 548.0, 655.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-75",
					"maxclass" : "newobj",
					"text" : "loadbang",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 35.0, 990.0, 60.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-76",
					"maxclass" : "message",
					"text" : "110.",
					"patching_rect" : [ 110.0, 990.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-77",
					"maxclass" : "message",
					"text" : "1",
					"patching_rect" : [ 165.0, 990.0, 30.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-78",
					"maxclass" : "message",
					"text" : "0.5",
					"patching_rect" : [ 205.0, 990.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-79",
					"maxclass" : "message",
					"text" : "1. 0.",
					"patching_rect" : [ 253.0, 990.0, 48.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-80",
					"maxclass" : "message",
					"text" : "0.",
					"patching_rect" : [ 311.0, 990.0, 32.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-81",
					"maxclass" : "message",
					"text" : "1",
					"patching_rect" : [ 353.0, 990.0, 30.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-82",
					"maxclass" : "message",
					"text" : "0.3",
					"patching_rect" : [ 393.0, 990.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-83",
					"maxclass" : "comment",
					"text" : "A constant unit-magnitude c rotates phase; changing c(t) or the SSB carrier produces audible spectral motion.",
					"patching_rect" : [ 435.0, 585.0, 660.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-84",
					"maxclass" : "comment",
					"text" : "Replace a and b with smoothed Bloch x/y, alpha*beta, or density-matrix off-diagonal real/imag values.",
					"patching_rect" : [ 435.0, 610.0, 650.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-85",
					"maxclass" : "message",
					"text" : "clear",
					"patching_rect" : [ 195.0, 360.0, 40.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-86",
					"maxclass" : "comment",
					"text" : "clear filter memory",
					"patching_rect" : [ 240.0, 362.0, 125.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-87",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "HARMONIC GEOMETRY SOURCE",
					"patching_rect" : [ 30.0, 585.0, 230.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-88",
					"maxclass" : "number",
					"minimum" : 2,
					"maximum" : 32,
					"patching_rect" : [ 30.0, 625.0, 55.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-89",
					"maxclass" : "comment",
					"text" : "harmonic n",
					"patching_rect" : [ 92.0, 627.0, 82.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-90",
					"maxclass" : "newobj",
					"text" : "t b i",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "bang", "int" ],
					"patching_rect" : [ 30.0, 660.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-91",
					"maxclass" : "newobj",
					"text" : "* 4.",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 110.0, 690.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-92",
					"maxclass" : "newobj",
					"text" : "cycle~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 110.0, 725.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-93",
					"maxclass" : "flonum",
					"format" : 6,
					"minimum" : 0.0,
					"maximum" : 1.0,
					"patching_rect" : [ 30.0, 725.0, 65.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-94",
					"maxclass" : "comment",
					"text" : "amplitude A",
					"patching_rect" : [ 30.0, 750.0, 85.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-95",
					"maxclass" : "newobj",
					"text" : "pack 0. 25",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 30.0, 775.0, 75.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-96",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 30.0, 810.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-97",
					"maxclass" : "newobj",
					"text" : "*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 110.0, 775.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-98",
					"maxclass" : "newobj",
					"text" : "+~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 180.0, 775.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-99",
					"maxclass" : "message",
					"text" : "4 0.25",
					"patching_rect" : [ 30.0, 865.0, 55.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-100",
					"maxclass" : "message",
					"text" : "6 0.1667",
					"patching_rect" : [ 92.0, 865.0, 70.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-101",
					"maxclass" : "message",
					"text" : "6 0.35",
					"patching_rect" : [ 170.0, 865.0, 55.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-102",
					"maxclass" : "message",
					"text" : "8 0.25",
					"patching_rect" : [ 233.0, 865.0, 55.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-103",
					"maxclass" : "newobj",
					"text" : "unpack 0 0.",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "int", "float" ],
					"patching_rect" : [ 30.0, 900.0, 75.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-104",
					"maxclass" : "comment",
					"text" : "n=4,A=1/4 gives 3 cusps; n=6,A=1/6 gives 5 cusps; larger A opens loops/stellar rosettes.",
					"patching_rect" : [ 30.0, 925.0, 550.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-105",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "I / Q HILBERT TRAJECTORY",
					"patching_rect" : [ 430.0, 650.0, 210.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-106",
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
					"patching_rect" : [ 430.0, 675.0, 290.0, 220.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-107",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "AFTER COMPLEX COHERENCE",
					"patching_rect" : [ 760.0, 650.0, 225.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-108",
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
					"patching_rect" : [ 760.0, 675.0, 290.0, 220.0 ]
				}
			}
		],
		"lines" : [
			{ "patchline" : { "source" : [ "obj-6", 0 ], "destination" : [ "obj-5", 0 ] } },
			{ "patchline" : { "source" : [ "obj-8", 0 ], "destination" : [ "obj-10", 0 ] } },
			{ "patchline" : { "source" : [ "obj-5", 0 ], "destination" : [ "obj-10", 1 ] } },
			{ "patchline" : { "source" : [ "obj-3", 0 ], "destination" : [ "obj-10", 3 ] } },
			{ "patchline" : { "source" : [ "obj-10", 0 ], "destination" : [ "obj-15", 0 ] } },
			{ "patchline" : { "source" : [ "obj-11", 0 ], "destination" : [ "obj-13", 0 ] } },
			{ "patchline" : { "source" : [ "obj-13", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 0 ], "destination" : [ "obj-15", 1 ] } },
			{ "patchline" : { "source" : [ "obj-15", 0 ], "destination" : [ "obj-16", 0 ] } },
			{ "patchline" : { "source" : [ "obj-85", 0 ], "destination" : [ "obj-16", 0 ] } },
			{ "patchline" : { "source" : [ "obj-16", 0 ], "destination" : [ "obj-18", 0 ] } },
			{ "patchline" : { "source" : [ "obj-16", 1 ], "destination" : [ "obj-19", 0 ] } },
			{ "patchline" : { "source" : [ "obj-16", 0 ], "destination" : [ "obj-20", 0 ] } },
			{ "patchline" : { "source" : [ "obj-16", 1 ], "destination" : [ "obj-20", 1 ] } },
			{ "patchline" : { "source" : [ "obj-20", 0 ], "destination" : [ "obj-21", 0 ] } },
			{ "patchline" : { "source" : [ "obj-20", 1 ], "destination" : [ "obj-22", 0 ] } },
			{ "patchline" : { "source" : [ "obj-24", 0 ], "destination" : [ "obj-27", 0 ] } },
			{ "patchline" : { "source" : [ "obj-27", 0 ], "destination" : [ "obj-28", 0 ] } },
			{ "patchline" : { "source" : [ "obj-25", 0 ], "destination" : [ "obj-29", 0 ] } },
			{ "patchline" : { "source" : [ "obj-29", 0 ], "destination" : [ "obj-30", 0 ] } },
			{ "patchline" : { "source" : [ "obj-28", 0 ], "destination" : [ "obj-31", 1 ] } },
			{ "patchline" : { "source" : [ "obj-30", 0 ], "destination" : [ "obj-32", 1 ] } },
			{ "patchline" : { "source" : [ "obj-16", 0 ], "destination" : [ "obj-31", 0 ] } },
			{ "patchline" : { "source" : [ "obj-16", 1 ], "destination" : [ "obj-32", 0 ] } },
			{ "patchline" : { "source" : [ "obj-31", 0 ], "destination" : [ "obj-33", 0 ] } },
			{ "patchline" : { "source" : [ "obj-32", 0 ], "destination" : [ "obj-33", 1 ] } },
			{ "patchline" : { "source" : [ "obj-30", 0 ], "destination" : [ "obj-34", 1 ] } },
			{ "patchline" : { "source" : [ "obj-28", 0 ], "destination" : [ "obj-35", 1 ] } },
			{ "patchline" : { "source" : [ "obj-16", 0 ], "destination" : [ "obj-34", 0 ] } },
			{ "patchline" : { "source" : [ "obj-16", 1 ], "destination" : [ "obj-35", 0 ] } },
			{ "patchline" : { "source" : [ "obj-34", 0 ], "destination" : [ "obj-36", 0 ] } },
			{ "patchline" : { "source" : [ "obj-35", 0 ], "destination" : [ "obj-36", 1 ] } },
			{ "patchline" : { "source" : [ "obj-28", 0 ], "destination" : [ "obj-37", 0 ] } },
			{ "patchline" : { "source" : [ "obj-30", 0 ], "destination" : [ "obj-37", 1 ] } },
			{ "patchline" : { "source" : [ "obj-37", 0 ], "destination" : [ "obj-38", 0 ] } },
			{ "patchline" : { "source" : [ "obj-37", 1 ], "destination" : [ "obj-39", 0 ] } },
			{ "patchline" : { "source" : [ "obj-41", 0 ], "destination" : [ "obj-46", 0 ] } },
			{ "patchline" : { "source" : [ "obj-42", 0 ], "destination" : [ "obj-46", 0 ] } },
			{ "patchline" : { "source" : [ "obj-43", 0 ], "destination" : [ "obj-46", 0 ] } },
			{ "patchline" : { "source" : [ "obj-44", 0 ], "destination" : [ "obj-46", 0 ] } },
			{ "patchline" : { "source" : [ "obj-45", 0 ], "destination" : [ "obj-46", 0 ] } },
			{ "patchline" : { "source" : [ "obj-46", 0 ], "destination" : [ "obj-24", 0 ] } },
			{ "patchline" : { "source" : [ "obj-46", 1 ], "destination" : [ "obj-25", 0 ] } },
			{ "patchline" : { "source" : [ "obj-48", 0 ], "destination" : [ "obj-49", 0 ] } },
			{ "patchline" : { "source" : [ "obj-49", 0 ], "destination" : [ "obj-50", 0 ] } },
			{ "patchline" : { "source" : [ "obj-50", 0 ], "destination" : [ "obj-51", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 0 ], "destination" : [ "obj-52", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 0 ], "destination" : [ "obj-53", 0 ] } },
			{ "patchline" : { "source" : [ "obj-53", 0 ], "destination" : [ "obj-54", 0 ] } },
			{ "patchline" : { "source" : [ "obj-16", 0 ], "destination" : [ "obj-55", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 0 ], "destination" : [ "obj-55", 1 ] } },
			{ "patchline" : { "source" : [ "obj-16", 1 ], "destination" : [ "obj-56", 0 ] } },
			{ "patchline" : { "source" : [ "obj-54", 0 ], "destination" : [ "obj-56", 1 ] } },
			{ "patchline" : { "source" : [ "obj-55", 0 ], "destination" : [ "obj-57", 0 ] } },
			{ "patchline" : { "source" : [ "obj-56", 0 ], "destination" : [ "obj-57", 1 ] } },
			{ "patchline" : { "source" : [ "obj-55", 0 ], "destination" : [ "obj-58", 0 ] } },
			{ "patchline" : { "source" : [ "obj-56", 0 ], "destination" : [ "obj-58", 1 ] } },
			{ "patchline" : { "source" : [ "obj-60", 0 ], "destination" : [ "obj-62", 0 ] } },
			{ "patchline" : { "source" : [ "obj-33", 0 ], "destination" : [ "obj-62", 1 ] } },
			{ "patchline" : { "source" : [ "obj-36", 0 ], "destination" : [ "obj-62", 2 ] } },
			{ "patchline" : { "source" : [ "obj-57", 0 ], "destination" : [ "obj-62", 3 ] } },
			{ "patchline" : { "source" : [ "obj-58", 0 ], "destination" : [ "obj-62", 4 ] } },
			{ "patchline" : { "source" : [ "obj-63", 0 ], "destination" : [ "obj-65", 0 ] } },
			{ "patchline" : { "source" : [ "obj-65", 0 ], "destination" : [ "obj-66", 0 ] } },
			{ "patchline" : { "source" : [ "obj-62", 0 ], "destination" : [ "obj-67", 0 ] } },
			{ "patchline" : { "source" : [ "obj-66", 0 ], "destination" : [ "obj-67", 1 ] } },
			{ "patchline" : { "source" : [ "obj-67", 0 ], "destination" : [ "obj-68", 0 ] } },
			{ "patchline" : { "source" : [ "obj-68", 0 ], "destination" : [ "obj-69", 0 ] } },
			{ "patchline" : { "source" : [ "obj-68", 0 ], "destination" : [ "obj-70", 0 ] } },
			{ "patchline" : { "source" : [ "obj-68", 0 ], "destination" : [ "obj-70", 1 ] } },
			{ "patchline" : { "source" : [ "obj-33", 0 ], "destination" : [ "obj-71", 0 ] } },
			{ "patchline" : { "source" : [ "obj-36", 0 ], "destination" : [ "obj-72", 0 ] } },
			{ "patchline" : { "source" : [ "obj-62", 0 ], "destination" : [ "obj-73", 0 ] } },
			{ "patchline" : { "source" : [ "obj-75", 0 ], "destination" : [ "obj-76", 0 ] } },
			{ "patchline" : { "source" : [ "obj-75", 0 ], "destination" : [ "obj-77", 0 ] } },
			{ "patchline" : { "source" : [ "obj-75", 0 ], "destination" : [ "obj-78", 0 ] } },
			{ "patchline" : { "source" : [ "obj-75", 0 ], "destination" : [ "obj-79", 0 ] } },
			{ "patchline" : { "source" : [ "obj-75", 0 ], "destination" : [ "obj-80", 0 ] } },
			{ "patchline" : { "source" : [ "obj-75", 0 ], "destination" : [ "obj-81", 0 ] } },
			{ "patchline" : { "source" : [ "obj-75", 0 ], "destination" : [ "obj-82", 0 ] } },
			{ "patchline" : { "source" : [ "obj-76", 0 ], "destination" : [ "obj-6", 0 ] } },
			{ "patchline" : { "source" : [ "obj-77", 0 ], "destination" : [ "obj-8", 0 ] } },
			{ "patchline" : { "source" : [ "obj-78", 0 ], "destination" : [ "obj-11", 0 ] } },
			{ "patchline" : { "source" : [ "obj-79", 0 ], "destination" : [ "obj-46", 0 ] } },
			{ "patchline" : { "source" : [ "obj-80", 0 ], "destination" : [ "obj-48", 0 ] } },
			{ "patchline" : { "source" : [ "obj-81", 0 ], "destination" : [ "obj-60", 0 ] } },
			{ "patchline" : { "source" : [ "obj-82", 0 ], "destination" : [ "obj-63", 0 ] } },
			{ "patchline" : { "source" : [ "obj-88", 0 ], "destination" : [ "obj-90", 0 ] } },
			{ "patchline" : { "source" : [ "obj-90", 1 ], "destination" : [ "obj-91", 1 ] } },
			{ "patchline" : { "source" : [ "obj-90", 0 ], "destination" : [ "obj-6", 0 ] } },
			{ "patchline" : { "source" : [ "obj-6", 0 ], "destination" : [ "obj-91", 0 ] } },
			{ "patchline" : { "source" : [ "obj-91", 0 ], "destination" : [ "obj-92", 0 ] } },
			{ "patchline" : { "source" : [ "obj-93", 0 ], "destination" : [ "obj-95", 0 ] } },
			{ "patchline" : { "source" : [ "obj-95", 0 ], "destination" : [ "obj-96", 0 ] } },
			{ "patchline" : { "source" : [ "obj-92", 0 ], "destination" : [ "obj-97", 0 ] } },
			{ "patchline" : { "source" : [ "obj-96", 0 ], "destination" : [ "obj-97", 1 ] } },
			{ "patchline" : { "source" : [ "obj-5", 0 ], "destination" : [ "obj-98", 0 ] } },
			{ "patchline" : { "source" : [ "obj-97", 0 ], "destination" : [ "obj-98", 1 ] } },
			{ "patchline" : { "source" : [ "obj-98", 0 ], "destination" : [ "obj-10", 2 ] } },
			{ "patchline" : { "source" : [ "obj-99", 0 ], "destination" : [ "obj-103", 0 ] } },
			{ "patchline" : { "source" : [ "obj-100", 0 ], "destination" : [ "obj-103", 0 ] } },
			{ "patchline" : { "source" : [ "obj-101", 0 ], "destination" : [ "obj-103", 0 ] } },
			{ "patchline" : { "source" : [ "obj-102", 0 ], "destination" : [ "obj-103", 0 ] } },
			{ "patchline" : { "source" : [ "obj-103", 0 ], "destination" : [ "obj-88", 0 ] } },
			{ "patchline" : { "source" : [ "obj-103", 1 ], "destination" : [ "obj-93", 0 ] } },
			{ "patchline" : { "source" : [ "obj-75", 0 ], "destination" : [ "obj-99", 0 ] } },
			{ "patchline" : { "source" : [ "obj-16", 0 ], "destination" : [ "obj-106", 0 ] } },
			{ "patchline" : { "source" : [ "obj-16", 1 ], "destination" : [ "obj-106", 1 ] } },
			{ "patchline" : { "source" : [ "obj-33", 0 ], "destination" : [ "obj-108", 0 ] } },
			{ "patchline" : { "source" : [ "obj-36", 0 ], "destination" : [ "obj-108", 1 ] } }
		],
		"dependency_cache" : [ ],
		"autosave" : 0
	}
}
