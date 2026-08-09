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
		"rect" : [ 90.0, 100.0, 1080.0, 520.0 ],
		"bglocked" : 0,
		"openinpresentation" : 0,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"description" : "Route four Complex Pauli Synth x/y pairs into real and imaginary lists for the Hilbert processor.",
		"digest" : "FullPacket OSC to four-channel Pauli complex coefficient lists.",
		"tags" : "OSC Pauli complex hilbert router",
		"boxes" : [
			{
				"box" : {
					"id" : "obj-1",
					"maxclass" : "comment",
					"fontsize" : 20.0,
					"fontface" : 1,
					"text" : "QMW Complex Pauli Hilbert Router v1",
					"patching_rect" : [ 30.0, 20.0, 430.0, 29.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-2",
					"maxclass" : "comment",
					"text" : "Branch the existing udpreceive 7403 FullPacket into this inlet. Do not create a second udpreceive on the same port.",
					"patching_rect" : [ 31.0, 55.0, 710.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-3",
					"maxclass" : "inlet",
					"index" : 1,
					"comment" : "OSC FullPacket from the existing receiver",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 35.0, 110.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-4",
					"maxclass" : "newobj",
					"text" : "OSC-route /qmw/pauli/q/0/x /qmw/pauli/q/0/y /qmw/pauli/q/1/x /qmw/pauli/q/1/y /qmw/pauli/q/2/x /qmw/pauli/q/2/y /qmw/pauli/q/3/x /qmw/pauli/q/3/y",
					"numinlets" : 1,
					"numoutlets" : 9,
					"outlettype" : [ "", "", "", "", "", "", "", "", "FullPacket" ],
					"patching_rect" : [ 35.0, 170.0, 985.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-5",
					"maxclass" : "newobj",
					"text" : "pak 1. 1. 1. 1.",
					"numinlets" : 4,
					"numoutlets" : 1,
					"outlettype" : [ "list" ],
					"patching_rect" : [ 175.0, 260.0, 110.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-6",
					"maxclass" : "newobj",
					"text" : "pak 0. 0. 0. 0.",
					"numinlets" : 4,
					"numoutlets" : 1,
					"outlettype" : [ "list" ],
					"patching_rect" : [ 510.0, 260.0, 110.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-7",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "a = [x0 x1 x2 x3]",
					"patching_rect" : [ 175.0, 230.0, 170.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-8",
					"maxclass" : "comment",
					"fontface" : 1,
					"text" : "b = [y0 y1 y2 y3]",
					"patching_rect" : [ 510.0, 230.0, 170.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-9",
					"maxclass" : "message",
					"text" : "1. 1. 1. 1.",
					"patching_rect" : [ 175.0, 305.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-10",
					"maxclass" : "message",
					"text" : "0. 0. 0. 0.",
					"patching_rect" : [ 510.0, 305.0, 90.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-11",
					"maxclass" : "comment",
					"text" : "live real list",
					"patching_rect" : [ 275.0, 307.0, 85.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-12",
					"maxclass" : "comment",
					"text" : "live imaginary list",
					"patching_rect" : [ 610.0, 307.0, 115.0, 20.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-13",
					"maxclass" : "outlet",
					"index" : 1,
					"comment" : "Pauli x list: a0 a1 a2 a3",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 210.0, 390.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-14",
					"maxclass" : "outlet",
					"index" : 2,
					"comment" : "Pauli y list: b0 b1 b2 b3",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 545.0, 390.0, 30.0, 30.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-15",
					"maxclass" : "newobj",
					"text" : "loadbang",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 785.0, 260.0, 60.0, 22.0 ]
				}
			},
			{
				"box" : {
					"id" : "obj-16",
					"maxclass" : "comment",
					"text" : "Initial identity is emitted until live OSC values arrive.",
					"patching_rect" : [ 785.0, 290.0, 300.0, 20.0 ]
				}
			}
		],
		"lines" : [
			{ "patchline" : { "source" : [ "obj-3", 0 ], "destination" : [ "obj-4", 0 ] } },
			{ "patchline" : { "source" : [ "obj-4", 0 ], "destination" : [ "obj-5", 0 ] } },
			{ "patchline" : { "source" : [ "obj-4", 1 ], "destination" : [ "obj-6", 0 ] } },
			{ "patchline" : { "source" : [ "obj-4", 2 ], "destination" : [ "obj-5", 1 ] } },
			{ "patchline" : { "source" : [ "obj-4", 3 ], "destination" : [ "obj-6", 1 ] } },
			{ "patchline" : { "source" : [ "obj-4", 4 ], "destination" : [ "obj-5", 2 ] } },
			{ "patchline" : { "source" : [ "obj-4", 5 ], "destination" : [ "obj-6", 2 ] } },
			{ "patchline" : { "source" : [ "obj-4", 6 ], "destination" : [ "obj-5", 3 ] } },
			{ "patchline" : { "source" : [ "obj-4", 7 ], "destination" : [ "obj-6", 3 ] } },
			{ "patchline" : { "source" : [ "obj-5", 0 ], "destination" : [ "obj-9", 1 ] } },
			{ "patchline" : { "source" : [ "obj-6", 0 ], "destination" : [ "obj-10", 1 ] } },
			{ "patchline" : { "source" : [ "obj-5", 0 ], "destination" : [ "obj-13", 0 ] } },
			{ "patchline" : { "source" : [ "obj-6", 0 ], "destination" : [ "obj-14", 0 ] } },
			{ "patchline" : { "source" : [ "obj-15", 0 ], "destination" : [ "obj-5", 0 ] } },
			{ "patchline" : { "source" : [ "obj-15", 0 ], "destination" : [ "obj-6", 0 ] } }
		],
		"dependency_cache" : [ ],
		"autosave" : 0
	}
}
