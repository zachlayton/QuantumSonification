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
		"rect" : [ 40.0, 40.0, 1510.0, 980.0 ],
		"bglocked" : 0,
		"openinpresentation" : 0,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"description" : "Complex 16-channel density-matrix operator for analytic MC audio.",
		"digest" : "Computes y=(Re(rho)+i Im(rho))(I+iQ) across sixteen basis channels.",
		"tags" : "MC hilbert analytic signal density matrix quantum complex operator",
		"boxes" : [
			{
				"box" : {
					"id" : "obj-1",
					"maxclass" : "comment",
					"fontsize" : 22.0,
					"fontface" : 1,
					"text" : "QMW Density-Matrix Hilbert Operator — 16 MC v1",
					"patching_rect" : [ 30.0, 18.0, 600.0, 31.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-2",
					"maxclass" : "comment",
					"fontsize" : 13.0,
					"text" : "z=I+iQ, rho=R+iM:   y_re=R I-M Q,   y_im=R Q+M I;   y[i]=sum_j rho[i,j] z[j]",
					"patching_rect" : [ 31.0, 52.0, 820.0, 21.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-3",
					"maxclass" : "inlet",
					"index" : 1,
					"comment" : "16-channel MC source from direct basis-state synth",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 50.0, 115.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-4",
					"maxclass" : "inlet",
					"index" : 2,
					"comment" : "Re(rho), 256 floats, row-major",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 385.0, 115.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-5",
					"maxclass" : "inlet",
					"index" : 3,
					"comment" : "Im(rho), 256 floats, row-major",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 570.0, 115.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-6",
					"maxclass" : "inlet",
					"index" : 4,
					"comment" : "control: wet, mode, ramp, identity, clear, commit, autocommit, threshold, status, hilbertclear",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 790.0, 115.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-7",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "16ch MC audio",
					"patching_rect" : [ 30.0, 90.0, 105.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-8",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "Re(rho): 256 row-major",
					"patching_rect" : [ 330.0, 90.0, 155.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-9",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "Im(rho): 256 row-major",
					"patching_rect" : [ 515.0, 90.0, 155.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-10",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "operator control",
					"patching_rect" : [ 750.0, 90.0, 115.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-11",
					"maxclass" : "newobj",
					"text" : "mc.hilbert~",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "multichannelsignal", "multichannelsignal" ],
					"patching_rect" : [ 50.0, 205.0, 84.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-12",
					"maxclass" : "message",
					"text" : "clear",
					"patching_rect" : [ 150.0, 205.0, 42.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-13",
					"maxclass" : "comment",
					"text" : "reset Hilbert filter history",
					"patching_rect" : [ 198.0, 207.0, 155.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-14",
					"maxclass" : "newobj",
					"text" : "js qmw_density_matrix16_to_mcs_matrix_v1.js",
					"numinlets" : 2,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 385.0, 205.0, 285.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-15",
					"maxclass" : "comment",
					"text" : "row-major rho[i,j] -> mcs.matrix~ list: input j, output i, gain",
					"patching_rect" : [ 385.0, 235.0, 430.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-16",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "R I",
					"patching_rect" : [ 50.0, 292.0, 40.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-17",
					"maxclass" : "newobj",
					"text" : "mcs.matrix~ 16 16 0. @ramp 25.",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "multichannelsignal", "" ],
					"patching_rect" : [ 50.0, 318.0, 205.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-18",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "M Q",
					"patching_rect" : [ 285.0, 292.0, 45.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-19",
					"maxclass" : "newobj",
					"text" : "mcs.matrix~ 16 16 0. @ramp 25.",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "multichannelsignal", "" ],
					"patching_rect" : [ 285.0, 318.0, 205.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-20",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "R Q",
					"patching_rect" : [ 520.0, 292.0, 45.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-21",
					"maxclass" : "newobj",
					"text" : "mcs.matrix~ 16 16 0. @ramp 25.",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "multichannelsignal", "" ],
					"patching_rect" : [ 520.0, 318.0, 205.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-22",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "M I",
					"patching_rect" : [ 755.0, 292.0, 40.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-23",
					"maxclass" : "newobj",
					"text" : "mcs.matrix~ 16 16 0. @ramp 25.",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "multichannelsignal", "" ],
					"patching_rect" : [ 755.0, 318.0, 205.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-24",
					"maxclass" : "newobj",
					"text" : "mc.-~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 170.0, 400.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-25",
					"maxclass" : "newobj",
					"text" : "mc.+~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 635.0, 400.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-26",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "y_re = R I - M Q",
					"patching_rect" : [ 120.0, 430.0, 150.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-27",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "y_im = R Q + M I",
					"patching_rect" : [ 585.0, 430.0, 150.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-28",
					"maxclass" : "outlet",
					"index" : 1,
					"comment" : "16-channel real output y_re",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 170.0, 485.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-29",
					"maxclass" : "outlet",
					"index" : 2,
					"comment" : "16-channel imaginary output y_im",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 635.0, 485.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-30",
					"maxclass" : "comment",
					"fontsize" : 15.0,
					"fontface" : 1,
					"text" : "Audition / RAW baseline",
					"patching_rect" : [ 1010.0, 185.0, 210.0, 24.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-31",
					"maxclass" : "flonum",
					"format" : 6,
					"minimum" : 0.0,
					"maximum" : 1.0,
					"patching_rect" : [ 1010.0, 240.0, 70.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-32",
					"maxclass" : "comment",
					"text" : "wet (mode 2 only)",
					"patching_rect" : [ 1088.0, 242.0, 120.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-33",
					"maxclass" : "newobj",
					"text" : "clip 0. 1.",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1010.0, 272.0, 68.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-34",
					"maxclass" : "newobj",
					"text" : "t f f",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "float" ],
					"patching_rect" : [ 1010.0, 302.0, 42.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-35",
					"maxclass" : "newobj",
					"text" : "pack 0. 20.",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1010.0, 337.0, 82.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-36",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 1010.0, 367.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-37",
					"maxclass" : "newobj",
					"text" : "!- 1.",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1110.0, 302.0, 48.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-38",
					"maxclass" : "newobj",
					"text" : "pack 1. 20.",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1110.0, 337.0, 82.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-39",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 1110.0, 367.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-40",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 970.0, 430.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-41",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 1090.0, 430.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-42",
					"maxclass" : "newobj",
					"text" : "mc.+~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 1030.0, 475.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-43",
					"maxclass" : "number",
					"minimum" : 1,
					"maximum" : 2,
					"patching_rect" : [ 1215.0, 420.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-44",
					"maxclass" : "comment",
					"text" : "mode: 1 RAW / 2 blend",
					"patching_rect" : [ 1273.0, 422.0, 145.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-45",
					"maxclass" : "newobj",
					"text" : "clip 1 2",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 1215.0, 452.0, 58.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-46",
					"maxclass" : "newobj",
					"text" : "mc.selector~ 2",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 1100.0, 520.0, 92.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-47",
					"maxclass" : "outlet",
					"index" : 3,
					"comment" : "16-channel audition output; mode 1 is exact RAW path",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1130.0, 570.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-48",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "audition out: 16ch MC",
					"patching_rect" : [ 1065.0, 608.0, 165.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-49",
					"maxclass" : "flonum",
					"format" : 6,
					"minimum" : 0.0,
					"patching_rect" : [ 1010.0, 680.0, 70.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-50",
					"maxclass" : "comment",
					"text" : "matrix ramp ms",
					"patching_rect" : [ 1088.0, 682.0, 105.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-51",
					"maxclass" : "message",
					"text" : "ramp $1",
					"patching_rect" : [ 1010.0, 712.0, 62.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-52",
					"maxclass" : "newobj",
					"text" : "route wet mode ramp identity clear commit autocommit threshold status hilbertclear",
					"numinlets" : 1,
					"numoutlets" : 11,
					"outlettype" : [ "", "", "", "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 650.0, 165.0, 545.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-53",
					"maxclass" : "message",
					"text" : "identity",
					"patching_rect" : [ 390.0, 680.0, 55.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-54",
					"maxclass" : "message",
					"text" : "clear",
					"patching_rect" : [ 455.0, 680.0, 42.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-55",
					"maxclass" : "message",
					"text" : "commit",
					"patching_rect" : [ 507.0, 680.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-56",
					"maxclass" : "newobj",
					"text" : "prepend autocommit",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 570.0, 680.0, 125.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-57",
					"maxclass" : "newobj",
					"text" : "prepend threshold",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 705.0, 680.0, 110.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-58",
					"maxclass" : "message",
					"text" : "status",
					"patching_rect" : [ 825.0, 680.0, 47.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-59",
					"maxclass" : "newobj",
					"text" : "print qmw.rho16.unknown_control",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1185.0, 165.0, 205.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-60",
					"maxclass" : "message",
					"text" : "status",
					"patching_rect" : [ 385.0, 765.0, 700.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-61",
					"maxclass" : "newobj",
					"text" : "print qmw.rho16.status",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 385.0, 800.0, 145.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-62",
					"maxclass" : "outlet",
					"index" : 4,
					"comment" : "matrix validation and status messages",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1350.0, 800.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-63",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "Matrix diagnostics (display / Max Console / outlet 4)",
					"patching_rect" : [ 385.0, 740.0, 330.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-64",
					"maxclass" : "newobj",
					"text" : "loadbang",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 50.0, 680.0, 60.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-65",
					"maxclass" : "newobj",
					"text" : "t b b b b",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "bang", "bang", "bang", "bang" ],
					"patching_rect" : [ 50.0, 710.0, 70.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-66",
					"maxclass" : "message",
					"text" : "identity",
					"patching_rect" : [ 50.0, 750.0, 55.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-67",
					"maxclass" : "message",
					"text" : "25.",
					"patching_rect" : [ 115.0, 750.0, 35.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-68",
					"maxclass" : "message",
					"text" : "0.",
					"patching_rect" : [ 160.0, 750.0, 31.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-69",
					"maxclass" : "message",
					"text" : "1",
					"patching_rect" : [ 201.0, 750.0, 30.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-70",
					"maxclass" : "comment",
					"text" : "init: identity operator / 25 ms matrix ramp / wet 0 / exact RAW audition",
					"patching_rect" : [ 50.0, 785.0, 330.0, 20.0 ]
				}
			}
		],
		"lines" : [
			{ "patchline" : { "source" : [ "obj-3", 0 ], "destination" : [ "obj-11", 0 ] } },
			{ "patchline" : { "source" : [ "obj-12", 0 ], "destination" : [ "obj-11", 0 ] } },
			{ "patchline" : { "source" : [ "obj-4", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-5", 0 ], "destination" : [ "obj-14", 1 ] } },
			{ "patchline" : { "source" : [ "obj-11", 0 ], "destination" : [ "obj-17", 0 ] } },
			{ "patchline" : { "source" : [ "obj-11", 0 ], "destination" : [ "obj-23", 0 ] } },
			{ "patchline" : { "source" : [ "obj-11", 1 ], "destination" : [ "obj-19", 0 ] } },
			{ "patchline" : { "source" : [ "obj-11", 1 ], "destination" : [ "obj-21", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 0 ], "destination" : [ "obj-17", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 0 ], "destination" : [ "obj-21", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 1 ], "destination" : [ "obj-19", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 1 ], "destination" : [ "obj-23", 0 ] } },
			{ "patchline" : { "source" : [ "obj-17", 0 ], "destination" : [ "obj-24", 0 ] } },
			{ "patchline" : { "source" : [ "obj-19", 0 ], "destination" : [ "obj-24", 1 ] } },
			{ "patchline" : { "source" : [ "obj-21", 0 ], "destination" : [ "obj-25", 0 ] } },
			{ "patchline" : { "source" : [ "obj-23", 0 ], "destination" : [ "obj-25", 1 ] } },
			{ "patchline" : { "source" : [ "obj-24", 0 ], "destination" : [ "obj-28", 0 ] } },
			{ "patchline" : { "source" : [ "obj-25", 0 ], "destination" : [ "obj-29", 0 ] } },
			{ "patchline" : { "source" : [ "obj-31", 0 ], "destination" : [ "obj-33", 0 ] } },
			{ "patchline" : { "source" : [ "obj-33", 0 ], "destination" : [ "obj-34", 0 ] } },
			{ "patchline" : { "source" : [ "obj-34", 0 ], "destination" : [ "obj-35", 0 ] } },
			{ "patchline" : { "source" : [ "obj-34", 1 ], "destination" : [ "obj-37", 0 ] } },
			{ "patchline" : { "source" : [ "obj-35", 0 ], "destination" : [ "obj-36", 0 ] } },
			{ "patchline" : { "source" : [ "obj-37", 0 ], "destination" : [ "obj-38", 0 ] } },
			{ "patchline" : { "source" : [ "obj-38", 0 ], "destination" : [ "obj-39", 0 ] } },
			{ "patchline" : { "source" : [ "obj-24", 0 ], "destination" : [ "obj-40", 0 ] } },
			{ "patchline" : { "source" : [ "obj-36", 0 ], "destination" : [ "obj-40", 1 ] } },
			{ "patchline" : { "source" : [ "obj-3", 0 ], "destination" : [ "obj-41", 0 ] } },
			{ "patchline" : { "source" : [ "obj-39", 0 ], "destination" : [ "obj-41", 1 ] } },
			{ "patchline" : { "source" : [ "obj-40", 0 ], "destination" : [ "obj-42", 0 ] } },
			{ "patchline" : { "source" : [ "obj-41", 0 ], "destination" : [ "obj-42", 1 ] } },
			{ "patchline" : { "source" : [ "obj-43", 0 ], "destination" : [ "obj-45", 0 ] } },
			{ "patchline" : { "source" : [ "obj-45", 0 ], "destination" : [ "obj-46", 0 ] } },
			{ "patchline" : { "source" : [ "obj-3", 0 ], "destination" : [ "obj-46", 1 ] } },
			{ "patchline" : { "source" : [ "obj-42", 0 ], "destination" : [ "obj-46", 2 ] } },
			{ "patchline" : { "source" : [ "obj-46", 0 ], "destination" : [ "obj-47", 0 ] } },
			{ "patchline" : { "source" : [ "obj-49", 0 ], "destination" : [ "obj-51", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 0 ], "destination" : [ "obj-17", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 0 ], "destination" : [ "obj-19", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 0 ], "destination" : [ "obj-21", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 0 ], "destination" : [ "obj-23", 0 ] } },
			{ "patchline" : { "source" : [ "obj-6", 0 ], "destination" : [ "obj-52", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 0 ], "destination" : [ "obj-31", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 1 ], "destination" : [ "obj-43", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 2 ], "destination" : [ "obj-49", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 3 ], "destination" : [ "obj-53", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 4 ], "destination" : [ "obj-54", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 5 ], "destination" : [ "obj-55", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 6 ], "destination" : [ "obj-56", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 7 ], "destination" : [ "obj-57", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 8 ], "destination" : [ "obj-58", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 9 ], "destination" : [ "obj-12", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 10 ], "destination" : [ "obj-59", 0 ] } },
			{ "patchline" : { "source" : [ "obj-53", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-54", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-55", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-56", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-57", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-58", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 2 ], "destination" : [ "obj-60", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 2 ], "destination" : [ "obj-61", 0 ] } },
			{ "patchline" : { "source" : [ "obj-14", 2 ], "destination" : [ "obj-62", 0 ] } },
			{ "patchline" : { "source" : [ "obj-64", 0 ], "destination" : [ "obj-65", 0 ] } },
			{ "patchline" : { "source" : [ "obj-65", 0 ], "destination" : [ "obj-66", 0 ] } },
			{ "patchline" : { "source" : [ "obj-65", 1 ], "destination" : [ "obj-67", 0 ] } },
			{ "patchline" : { "source" : [ "obj-65", 2 ], "destination" : [ "obj-68", 0 ] } },
			{ "patchline" : { "source" : [ "obj-65", 3 ], "destination" : [ "obj-69", 0 ] } },
			{ "patchline" : { "source" : [ "obj-66", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-67", 0 ], "destination" : [ "obj-49", 0 ] } },
			{ "patchline" : { "source" : [ "obj-68", 0 ], "destination" : [ "obj-31", 0 ] } },
			{ "patchline" : { "source" : [ "obj-69", 0 ], "destination" : [ "obj-43", 0 ] } }
		],
		"dependency_cache" : [
			{
				"name" : "qmw_density_matrix16_to_mcs_matrix_v1.js",
				"type" : "TEXT",
				"implicit" : 1
			}
		],
		"autosave" : 0
	}
}
