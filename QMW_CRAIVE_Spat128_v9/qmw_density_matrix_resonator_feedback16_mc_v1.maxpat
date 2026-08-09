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
		"rect" : [ 35.0, 35.0, 1540.0, 990.0 ],
		"bglocked" : 0,
		"openinpresentation" : 0,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"description" : "Sixteen-channel complex density-matrix coupling inside causal resonator feedback branches.",
		"digest" : "Feeds a phase projection of rho times the analytic resonator state back through explicit MC delays.",
		"tags" : "MC hilbert density matrix resonator feedback complex coupling quantum",
		"boxes" : [
			{
				"box" : {
					"id" : "obj-1",
					"maxclass" : "comment",
					"fontsize" : 22.0,
					"fontface" : 1,
					"text" : "QMW Density-Matrix Resonator Feedback — 16 MC v1",
					"patching_rect" : [ 30.0, 18.0, 640.0, 31.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-2",
					"maxclass" : "comment",
					"fontsize" : 13.0,
					"text" : "s=x+g Delay{Re[e^(i theta) rho Hilbert{s}]}; full cross-basis complex coupling with explicit causal memory",
					"patching_rect" : [ 31.0, 52.0, 900.0, 21.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-3",
					"maxclass" : "inlet",
					"index" : 1,
					"comment" : "raw 16-channel MC resonator bank output",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 55.0, 120.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-4",
					"maxclass" : "inlet",
					"index" : 2,
					"comment" : "Re(rho), 256 row-major values",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 260.0, 120.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-5",
					"maxclass" : "inlet",
					"index" : 3,
					"comment" : "Im(rho), 256 row-major values",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 405.0, 120.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-6",
					"maxclass" : "inlet",
					"index" : 4,
					"comment" : "sixteen quantum projection phases in radians",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 580.0, 120.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-7",
					"maxclass" : "inlet",
					"index" : 5,
					"comment" : "sixteen feedback gains",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 730.0, 120.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-8",
					"maxclass" : "inlet",
					"index" : 6,
					"comment" : "sixteen feedback delays in milliseconds",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 875.0, 120.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-9",
					"maxclass" : "inlet",
					"index" : 7,
					"comment" : "feedback-network controls",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1050.0, 120.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-10",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "raw resonator MC",
					"patching_rect" : [ 30.0, 94.0, 125.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-11",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "Re(rho)",
					"patching_rect" : [ 245.0, 94.0, 70.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-12",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "Im(rho)",
					"patching_rect" : [ 390.0, 94.0, 70.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-13",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "theta[16]",
					"patching_rect" : [ 560.0, 94.0, 80.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-14",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "gain[16]",
					"patching_rect" : [ 710.0, 94.0, 75.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-15",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "delay ms[16]",
					"patching_rect" : [ 850.0, 94.0, 105.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-16",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "control",
					"patching_rect" : [ 1037.0, 94.0, 65.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-17",
					"maxclass" : "newobj",
					"text" : "mc.+~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 80.0, 285.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-18",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "coupled state s = raw + delayed return",
					"patching_rect" : [ 35.0, 315.0, 245.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-19",
					"maxclass" : "newobj",
					"text" : "qmw_density_matrix_hilbert_operator16_mc_v1",
					"numinlets" : 4,
					"numoutlets" : 4,
					"outlettype" : [ "multichannelsignal", "multichannelsignal", "multichannelsignal", "" ],
					"patching_rect" : [ 245.0, 285.0, 315.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-20",
					"maxclass" : "newobj",
					"text" : "js qmw_feedback_branch_controls16_v1.js",
					"numinlets" : 3,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 650.0, 205.0, 255.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-21",
					"maxclass" : "comment",
					"text" : "No autonomous motion: data -> phase vectors / bounded gains / explicit delays",
					"patching_rect" : [ 650.0, 235.0, 430.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-22",
					"maxclass" : "newobj",
					"text" : "mc.list~ 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. @chans 16",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 590.0, 285.0, 430.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-23",
					"maxclass" : "newobj",
					"text" : "mc.rampsmooth~ 2400 2400",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 650.0, 315.0, 165.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-24",
					"maxclass" : "newobj",
					"text" : "mc.cosx~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 710.0, 350.0, 72.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-25",
					"maxclass" : "newobj",
					"text" : "mc.sinx~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 930.0, 350.0, 72.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-26",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "theta radians -> one smoothed MC phase signal",
					"patching_rect" : [ 590.0, 260.0, 285.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-27",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "mc.cosx~ / mc.sinx~ preserve a unit-length rotation during ramps",
					"patching_rect" : [ 885.0, 325.0, 390.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-28",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 590.0, 385.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-29",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 1035.0, 385.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-30",
					"maxclass" : "newobj",
					"text" : "mc.-~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 810.0, 440.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-31",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "Re{exp(i theta) y} = cos(theta)y_re - sin(theta)y_im",
					"patching_rect" : [ 660.0, 470.0, 370.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-32",
					"maxclass" : "newobj",
					"text" : "mc.list~ 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. @chans 16",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 530.0, 525.0, 430.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-33",
					"maxclass" : "newobj",
					"text" : "mc.rampsmooth~ 2400 2400",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 665.0, 555.0, 165.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-34",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "bounded branch gains",
					"patching_rect" : [ 530.0, 500.0, 150.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-35",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 1015.0, 715.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-36",
					"maxclass" : "newobj",
					"text" : "mc.tapin~ 2000.",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "tap" ],
					"patching_rect" : [ 810.0, 655.0, 105.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-37",
					"maxclass" : "newobj",
					"text" : "mc.list~ 10. 10. 10. 10. 10. 10. 10. 10. 10. 10. 10. 10. 10. 10. 10. 10. @chans 16",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 995.0, 525.0, 475.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-38",
					"maxclass" : "newobj",
					"text" : "mc.rampsmooth~ 4800 4800",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 1130.0, 555.0, 165.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-39",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "explicit per-branch delay (ms)",
					"patching_rect" : [ 995.0, 500.0, 205.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-40",
					"maxclass" : "newobj",
					"text" : "mc.tapout~ 10.",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 1015.0, 655.0, 95.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-41",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "causal return",
					"patching_rect" : [ 1015.0, 685.0, 100.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-42",
					"maxclass" : "number",
					"minimum" : 1,
					"maximum" : 2,
					"patching_rect" : [ 55.0, 430.0, 50.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-43",
					"maxclass" : "comment",
					"text" : "mode: 1 exact RAW / 2 coupled state",
					"patching_rect" : [ 113.0, 432.0, 220.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-44",
					"maxclass" : "newobj",
					"text" : "clip 1 2",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 55.0, 460.0, 58.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-45",
					"maxclass" : "newobj",
					"text" : "mc.selector~ 2",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 95.0, 520.0, 92.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-46",
					"maxclass" : "outlet",
					"index" : 1,
					"comment" : "selected 16-channel output; mode 1 exact raw, mode 2 coupled",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 125.0, 575.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-47",
					"maxclass" : "outlet",
					"index" : 2,
					"comment" : "internal coupled state s",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 245.0, 370.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-48",
					"maxclass" : "outlet",
					"index" : 3,
					"comment" : "bounded delayed feedback return",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1080.0, 710.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-49",
					"maxclass" : "outlet",
					"index" : 4,
					"comment" : "density operator y_re",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 470.0, 385.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-50",
					"maxclass" : "outlet",
					"index" : 5,
					"comment" : "density operator y_im",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 520.0, 385.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-51",
					"maxclass" : "newobj",
					"text" : "route mode clear panic safe identity matrixclear commit autocommit threshold matrixramp status",
					"numinlets" : 1,
					"numoutlets" : 12,
					"outlettype" : [ "", "", "", "", "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 1000.0, 165.0, 515.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-52",
					"maxclass" : "newobj",
					"text" : "t b b",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "bang", "bang" ],
					"patching_rect" : [ 980.0, 760.0, 42.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-53",
					"maxclass" : "message",
					"text" : "hilbertclear",
					"patching_rect" : [ 935.0, 795.0, 75.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-54",
					"maxclass" : "message",
					"text" : "clear",
					"patching_rect" : [ 1020.0, 795.0, 42.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-55",
					"maxclass" : "message",
					"text" : "safe",
					"patching_rect" : [ 1072.0, 795.0, 38.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-56",
					"maxclass" : "message",
					"text" : "identity",
					"patching_rect" : [ 1120.0, 795.0, 55.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-57",
					"maxclass" : "message",
					"text" : "clear",
					"patching_rect" : [ 1185.0, 795.0, 42.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-58",
					"maxclass" : "message",
					"text" : "commit",
					"patching_rect" : [ 1237.0, 795.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-59",
					"maxclass" : "newobj",
					"text" : "prepend autocommit",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1299.0, 795.0, 125.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-60",
					"maxclass" : "newobj",
					"text" : "prepend threshold",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 935.0, 835.0, 110.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-61",
					"maxclass" : "newobj",
					"text" : "prepend ramp",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1055.0, 835.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-62",
					"maxclass" : "message",
					"text" : "status",
					"patching_rect" : [ 1155.0, 835.0, 47.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-63",
					"maxclass" : "message",
					"text" : "status",
					"patching_rect" : [ 245.0, 850.0, 930.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-64",
					"maxclass" : "newobj",
					"text" : "print qmw.feedback16.status",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 245.0, 885.0, 170.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-65",
					"maxclass" : "outlet",
					"index" : 6,
					"comment" : "combined feedback and density diagnostics",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 430.0, 885.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-66",
					"maxclass" : "newobj",
					"text" : "loadbang",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 55.0, 760.0, 60.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-67",
					"maxclass" : "newobj",
					"text" : "t b b b b",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "bang", "bang", "bang", "bang" ],
					"patching_rect" : [ 55.0, 790.0, 70.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-68",
					"maxclass" : "message",
					"text" : "initialize",
					"patching_rect" : [ 55.0, 825.0, 60.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-69",
					"maxclass" : "message",
					"text" : "identity",
					"patching_rect" : [ 225.0, 825.0, 55.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-70",
					"maxclass" : "message",
					"text" : "1",
					"patching_rect" : [ 290.0, 825.0, 30.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-71",
					"maxclass" : "comment",
					"text" : "boot: gains zero / 10 ms delays / theta zero / identity rho / autocommit 0 / exact RAW output",
					"patching_rect" : [ 55.0, 860.0, 520.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-72",
					"maxclass" : "newobj",
					"text" : "t i i",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "int", "int" ],
					"patching_rect" : [ 55.0, 490.0, 42.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-73",
					"maxclass" : "newobj",
					"text" : "== 2",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 200.0, 490.0, 42.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-74",
					"maxclass" : "newobj",
					"text" : "pack 0. 10.",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 200.0, 520.0, 82.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-75",
					"maxclass" : "newobj",
					"text" : "line~",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 200.0, 550.0, 45.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-76",
					"maxclass" : "newobj",
					"text" : "mc.*~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 1015.0, 750.0, 52.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-77",
					"maxclass" : "newobj",
					"text" : "t b b b b",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "bang", "bang", "bang", "bang" ],
					"patching_rect" : [ 1220.0, 750.0, 70.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-78",
					"maxclass" : "message",
					"text" : "0 0",
					"patching_rect" : [ 1300.0, 750.0, 35.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-79",
					"maxclass" : "message",
					"text" : "autocommit 0",
					"patching_rect" : [ 125.0, 825.0, 90.0, 22.0 ]
				}
			}
		],
		"lines" : [
			{ "patchline" : { "source" : [ "obj-3", 0 ], "destination" : [ "obj-17", 0 ] } },
			{ "patchline" : { "source" : [ "obj-76", 0 ], "destination" : [ "obj-17", 1 ] } },
			{ "patchline" : { "source" : [ "obj-17", 0 ], "destination" : [ "obj-19", 0 ] } },
			{ "patchline" : { "source" : [ "obj-4", 0 ], "destination" : [ "obj-19", 1 ] } },
			{ "patchline" : { "source" : [ "obj-5", 0 ], "destination" : [ "obj-19", 2 ] } },
			{ "patchline" : { "source" : [ "obj-6", 0 ], "destination" : [ "obj-20", 0 ] } },
			{ "patchline" : { "source" : [ "obj-7", 0 ], "destination" : [ "obj-20", 1 ] } },
			{ "patchline" : { "source" : [ "obj-8", 0 ], "destination" : [ "obj-20", 2 ] } },
			{ "patchline" : { "source" : [ "obj-20", 0 ], "destination" : [ "obj-22", 0 ] } },
			{ "patchline" : { "source" : [ "obj-22", 0 ], "destination" : [ "obj-23", 0 ] } },
			{ "patchline" : { "source" : [ "obj-23", 0 ], "destination" : [ "obj-24", 0 ] } },
			{ "patchline" : { "source" : [ "obj-23", 0 ], "destination" : [ "obj-25", 0 ] } },
			{ "patchline" : { "source" : [ "obj-19", 0 ], "destination" : [ "obj-28", 0 ] } },
			{ "patchline" : { "source" : [ "obj-24", 0 ], "destination" : [ "obj-28", 1 ] } },
			{ "patchline" : { "source" : [ "obj-19", 1 ], "destination" : [ "obj-29", 0 ] } },
			{ "patchline" : { "source" : [ "obj-25", 0 ], "destination" : [ "obj-29", 1 ] } },
			{ "patchline" : { "source" : [ "obj-28", 0 ], "destination" : [ "obj-30", 0 ] } },
			{ "patchline" : { "source" : [ "obj-29", 0 ], "destination" : [ "obj-30", 1 ] } },
			{ "patchline" : { "source" : [ "obj-20", 1 ], "destination" : [ "obj-32", 0 ] } },
			{ "patchline" : { "source" : [ "obj-32", 0 ], "destination" : [ "obj-33", 0 ] } },
			{ "patchline" : { "source" : [ "obj-30", 0 ], "destination" : [ "obj-36", 0 ] } },
			{ "patchline" : { "source" : [ "obj-33", 0 ], "destination" : [ "obj-35", 1 ] } },
			{ "patchline" : { "source" : [ "obj-76", 0 ], "destination" : [ "obj-48", 0 ] } },
			{ "patchline" : { "source" : [ "obj-20", 2 ], "destination" : [ "obj-37", 0 ] } },
			{ "patchline" : { "source" : [ "obj-37", 0 ], "destination" : [ "obj-38", 0 ] } },
			{ "patchline" : { "source" : [ "obj-36", 0 ], "destination" : [ "obj-40", 0 ] } },
			{ "patchline" : { "source" : [ "obj-38", 0 ], "destination" : [ "obj-40", 0 ] } },
			{ "patchline" : { "source" : [ "obj-40", 0 ], "destination" : [ "obj-35", 0 ] } },
			{ "patchline" : { "source" : [ "obj-35", 0 ], "destination" : [ "obj-76", 0 ] } },
			{ "patchline" : { "source" : [ "obj-75", 0 ], "destination" : [ "obj-76", 1 ] } },
			{ "patchline" : { "source" : [ "obj-42", 0 ], "destination" : [ "obj-44", 0 ] } },
			{ "patchline" : { "source" : [ "obj-44", 0 ], "destination" : [ "obj-72", 0 ] } },
			{ "patchline" : { "source" : [ "obj-72", 0 ], "destination" : [ "obj-45", 0 ] } },
			{ "patchline" : { "source" : [ "obj-72", 1 ], "destination" : [ "obj-73", 0 ] } },
			{ "patchline" : { "source" : [ "obj-73", 0 ], "destination" : [ "obj-74", 0 ] } },
			{ "patchline" : { "source" : [ "obj-74", 0 ], "destination" : [ "obj-75", 0 ] } },
			{ "patchline" : { "source" : [ "obj-3", 0 ], "destination" : [ "obj-45", 1 ] } },
			{ "patchline" : { "source" : [ "obj-17", 0 ], "destination" : [ "obj-45", 2 ] } },
			{ "patchline" : { "source" : [ "obj-45", 0 ], "destination" : [ "obj-46", 0 ] } },
			{ "patchline" : { "source" : [ "obj-17", 0 ], "destination" : [ "obj-47", 0 ] } },
			{ "patchline" : { "source" : [ "obj-19", 0 ], "destination" : [ "obj-49", 0 ] } },
			{ "patchline" : { "source" : [ "obj-19", 1 ], "destination" : [ "obj-50", 0 ] } },
			{ "patchline" : { "source" : [ "obj-9", 0 ], "destination" : [ "obj-51", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 0 ], "destination" : [ "obj-42", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 1 ], "destination" : [ "obj-52", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 2 ], "destination" : [ "obj-77", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 3 ], "destination" : [ "obj-55", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 4 ], "destination" : [ "obj-56", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 5 ], "destination" : [ "obj-57", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 6 ], "destination" : [ "obj-58", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 7 ], "destination" : [ "obj-59", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 8 ], "destination" : [ "obj-60", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 9 ], "destination" : [ "obj-61", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 10 ], "destination" : [ "obj-62", 0 ] } },
			{ "patchline" : { "source" : [ "obj-51", 11 ], "destination" : [ "obj-20", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 0 ], "destination" : [ "obj-53", 0 ] } },
			{ "patchline" : { "source" : [ "obj-52", 1 ], "destination" : [ "obj-54", 0 ] } },
			{ "patchline" : { "source" : [ "obj-53", 0 ], "destination" : [ "obj-19", 3 ] } },
			{ "patchline" : { "source" : [ "obj-54", 0 ], "destination" : [ "obj-36", 0 ] } },
			{ "patchline" : { "source" : [ "obj-55", 0 ], "destination" : [ "obj-20", 0 ] } },
			{ "patchline" : { "source" : [ "obj-56", 0 ], "destination" : [ "obj-19", 3 ] } },
			{ "patchline" : { "source" : [ "obj-57", 0 ], "destination" : [ "obj-19", 3 ] } },
			{ "patchline" : { "source" : [ "obj-58", 0 ], "destination" : [ "obj-19", 3 ] } },
			{ "patchline" : { "source" : [ "obj-59", 0 ], "destination" : [ "obj-19", 3 ] } },
			{ "patchline" : { "source" : [ "obj-60", 0 ], "destination" : [ "obj-19", 3 ] } },
			{ "patchline" : { "source" : [ "obj-61", 0 ], "destination" : [ "obj-19", 3 ] } },
			{ "patchline" : { "source" : [ "obj-62", 0 ], "destination" : [ "obj-19", 3 ] } },
			{ "patchline" : { "source" : [ "obj-62", 0 ], "destination" : [ "obj-20", 0 ] } },
			{ "patchline" : { "source" : [ "obj-77", 0 ], "destination" : [ "obj-55", 0 ] } },
			{ "patchline" : { "source" : [ "obj-77", 1 ], "destination" : [ "obj-53", 0 ] } },
			{ "patchline" : { "source" : [ "obj-77", 2 ], "destination" : [ "obj-54", 0 ] } },
			{ "patchline" : { "source" : [ "obj-77", 3 ], "destination" : [ "obj-78", 0 ] } },
			{ "patchline" : { "source" : [ "obj-78", 0 ], "destination" : [ "obj-75", 0 ] } },
			{ "patchline" : { "source" : [ "obj-19", 3 ], "destination" : [ "obj-63", 0 ] } },
			{ "patchline" : { "source" : [ "obj-20", 3 ], "destination" : [ "obj-63", 0 ] } },
			{ "patchline" : { "source" : [ "obj-19", 3 ], "destination" : [ "obj-64", 0 ] } },
			{ "patchline" : { "source" : [ "obj-20", 3 ], "destination" : [ "obj-64", 0 ] } },
			{ "patchline" : { "source" : [ "obj-19", 3 ], "destination" : [ "obj-65", 0 ] } },
			{ "patchline" : { "source" : [ "obj-20", 3 ], "destination" : [ "obj-65", 0 ] } },
			{ "patchline" : { "source" : [ "obj-66", 0 ], "destination" : [ "obj-67", 0 ] } },
			{ "patchline" : { "source" : [ "obj-67", 0 ], "destination" : [ "obj-68", 0 ] } },
			{ "patchline" : { "source" : [ "obj-67", 1 ], "destination" : [ "obj-79", 0 ] } },
			{ "patchline" : { "source" : [ "obj-67", 2 ], "destination" : [ "obj-69", 0 ] } },
			{ "patchline" : { "source" : [ "obj-67", 3 ], "destination" : [ "obj-70", 0 ] } },
			{ "patchline" : { "source" : [ "obj-68", 0 ], "destination" : [ "obj-20", 0 ] } },
			{ "patchline" : { "source" : [ "obj-69", 0 ], "destination" : [ "obj-19", 3 ] } },
			{ "patchline" : { "source" : [ "obj-79", 0 ], "destination" : [ "obj-19", 3 ] } },
			{ "patchline" : { "source" : [ "obj-70", 0 ], "destination" : [ "obj-42", 0 ] } }
		],
		"dependency_cache" : [
			{
				"name" : "qmw_density_matrix_hilbert_operator16_mc_v1.maxpat",
				"type" : "JSON",
				"implicit" : 1
			},
			{
				"name" : "qmw_feedback_branch_controls16_v1.js",
				"type" : "TEXT",
				"implicit" : 1
			},
			{
				"name" : "qmw_density_matrix16_to_mcs_matrix_v1.js",
				"type" : "TEXT",
				"implicit" : 1
			}
		],
		"autosave" : 0
	}
}
