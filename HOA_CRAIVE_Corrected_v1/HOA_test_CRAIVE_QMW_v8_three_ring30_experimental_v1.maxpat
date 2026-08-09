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
		"classnamespace": "box",
		"rect": [
			155,
			79,
			1404,
			1040
		],
		"bglocked": 0,
		"openinpresentation": 0,
		"default_fontsize": 12,
		"default_fontface": 0,
		"default_fontname": "Arial",
		"gridonopen": 1,
		"gridsize": [
			15,
			15
		],
		"gridsnaponopen": 1,
		"objectsnaponopen": 1,
		"statusbarvisible": 2,
		"toolbarvisible": 1,
		"lefttoolbarpinned": 0,
		"toptoolbarpinned": 0,
		"righttoolbarpinned": 0,
		"bottomtoolbarpinned": 0,
		"toolbars_unpinned_last_save": 0,
		"tallnewobj": 0,
		"boxanimatetime": 200,
		"enablehscroll": 1,
		"enablevscroll": 1,
		"devicewidth": 0,
		"description": "",
		"digest": "",
		"tags": "",
		"style": "",
		"subpatcher_template": "",
		"assistshowspatchername": 0,
		"boxes": [
			{
				"box": {
					"id": "obj-11",
					"maxclass": "newobj",
					"numinlets": 16,
					"numoutlets": 1,
					"outlettype": [
						"multichannelsignal"
					],
					"patching_rect": [
						18,
						660,
						228,
						22
					],
					"text": "mc.pack~ 16"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-1673",
					"linecount": 2,
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						23,
						930,
						700,
						36
					],
					"text": "mc.dac~ 4 8 12 16 20 23 28 33 37 42 46 51 55 58 63 1 129 130 131 132 133 134 135 136 137 138 139 140 141 142"
				}
			},
			{
				"box": {
					"id": "obj-2",
					"maxclass": "newobj",
					"numinlets": 1,
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
						13.444443,
						160,
						302,
						22
					],
					"text": "adc~ 17 18 19 20 21 22 23 24 33 34 35 36 37 38 39 40"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-48",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						397.444458,
						261.5,
						29,
						21
					],
					"text": "thru"
				}
			},
			{
				"box": {
					"id": "obj-31",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						490,
						169,
						95,
						22
					],
					"text": "loadmess SN3D"
				}
			},
			{
				"box": {
					"bgmode": 0,
					"border": 0,
					"clickthrough": 0,
					"enablehscroll": 0,
					"enablevscroll": 0,
					"id": "obj-37",
					"lockeddragscroll": 0,
					"lockedsize": 0,
					"maxclass": "bpatcher",
					"name": "spat5.known.hoanorm.maxpat",
					"numinlets": 1,
					"numoutlets": 1,
					"offset": [
						0,
						0
					],
					"outlettype": [
						""
					],
					"patching_rect": [
						490,
						199,
						50,
						17
					],
					"varname": "live.menu[1]",
					"viewvisibility": 1
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-43",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						490,
						219,
						54,
						21
					],
					"text": "/norm $1"
				}
			},
			{
				"box": {
					"id": "obj-29",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						1100.444458,
						338,
						127,
						22
					],
					"text": "spat5.osc.route /hoa/1"
				}
			},
			{
				"box": {
					"id": "obj-27",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					],
					"patching_rect": [
						1100.444458,
						231,
						58,
						22
					],
					"text": "loadbang"
				}
			},
			{
				"box": {
					"id": "obj-17",
					"maxclass": "live.button",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"parameter_enable": 1,
					"patching_rect": [
						1100.444458,
						257.5,
						15,
						15
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_enum": [
								"off",
								"on"
							],
							"parameter_longname": "live.button[16]",
							"parameter_mmax": 1,
							"parameter_modmode": 0,
							"parameter_shortname": "live.button",
							"parameter_type": 2
						}
					},
					"varname": "live.button"
				}
			},
			{
				"box": {
					"id": "obj-5",
					"linecount": 3,
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"",
						"",
						""
					],
					"patching_rect": [
						1099.944458,
						279,
						131,
						49
					],
					"saved_object_attributes": {
						"parameter_enable": 0
					},
					"text": "spat5.viewer @initwith \"/hoa/number 1, /display/zoom 40\"",
					"varname": "spat5.viewer[1]"
				}
			},
			{
				"box": {
					"focusbordercolor": [
						0.313725,
						0.313725,
						0.313725,
						0
					],
					"id": "obj-32",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						549.444458,
						296,
						44,
						48
					],
					"saved_attribute_attributes": {
						"focusbordercolor": {
							"expression": ""
						},
						"valueof": {
							"parameter_longname": "live.dial[10]",
							"parameter_mmax": 360,
							"parameter_mmin": -360,
							"parameter_modmode": 0,
							"parameter_shortname": "roll",
							"parameter_type": 0,
							"parameter_unitstyle": 1
						}
					},
					"varname": "live.dial[8]"
				}
			},
			{
				"box": {
					"focusbordercolor": [
						0.313725,
						0.313725,
						0.313725,
						0
					],
					"id": "obj-33",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						492.444458,
						296,
						44,
						48
					],
					"saved_attribute_attributes": {
						"focusbordercolor": {
							"expression": ""
						},
						"valueof": {
							"parameter_longname": "live.dial[12]",
							"parameter_mmax": 360,
							"parameter_mmin": -360,
							"parameter_modmode": 0,
							"parameter_shortname": "pitch",
							"parameter_type": 0,
							"parameter_unitstyle": 1
						}
					},
					"varname": "live.dial[9]"
				}
			},
			{
				"box": {
					"focusbordercolor": [
						0.313725,
						0.313725,
						0.313725,
						0
					],
					"id": "obj-36",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						435.444458,
						296,
						44,
						48
					],
					"saved_attribute_attributes": {
						"focusbordercolor": {
							"expression": ""
						},
						"valueof": {
							"parameter_longname": "live.dial[15]",
							"parameter_mmax": 360,
							"parameter_mmin": -360,
							"parameter_modmode": 0,
							"parameter_shortname": "yaw",
							"parameter_type": 0,
							"parameter_unitstyle": 1
						}
					},
					"varname": "live.dial[10]"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-38",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						600,
						231,
						133,
						21
					],
					"text": "pak 0. 0. 0."
				}
			},
			{
				"box": {
					"focusbordercolor": [
						0.313725,
						0.313725,
						0.313725,
						0
					],
					"id": "obj-40",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						714,
						180,
						44,
						48
					],
					"saved_attribute_attributes": {
						"focusbordercolor": {
							"expression": ""
						},
						"valueof": {
							"parameter_longname": "live.dial[7]",
							"parameter_mmax": 360,
							"parameter_mmin": -360,
							"parameter_modmode": 0,
							"parameter_shortname": "roll",
							"parameter_type": 0,
							"parameter_unitstyle": 1
						}
					},
					"varname": "live.dial[2]"
				}
			},
			{
				"box": {
					"focusbordercolor": [
						0.313725,
						0.313725,
						0.313725,
						0
					],
					"id": "obj-41",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						657,
						180,
						44,
						48
					],
					"saved_attribute_attributes": {
						"focusbordercolor": {
							"expression": ""
						},
						"valueof": {
							"parameter_longname": "live.dial[8]",
							"parameter_mmax": 360,
							"parameter_mmin": -360,
							"parameter_modmode": 0,
							"parameter_shortname": "pitch",
							"parameter_type": 0,
							"parameter_unitstyle": 1
						}
					},
					"varname": "live.dial[3]"
				}
			},
			{
				"box": {
					"focusbordercolor": [
						0.313725,
						0.313725,
						0.313725,
						0
					],
					"id": "obj-42",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						600,
						180,
						44,
						48
					],
					"saved_attribute_attributes": {
						"focusbordercolor": {
							"expression": ""
						},
						"valueof": {
							"parameter_longname": "live.dial[16]",
							"parameter_mmax": 360,
							"parameter_mmin": -360,
							"parameter_modmode": 0,
							"parameter_shortname": "yaw",
							"parameter_type": 0,
							"parameter_unitstyle": 1
						}
					},
					"varname": "live.dial[7]"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-90",
					"maxclass": "newobj",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						778.444458,
						151,
						133,
						21
					],
					"text": "pak 0. 0. 0."
				}
			},
			{
				"box": {
					"focusbordercolor": [
						0.313725,
						0.313725,
						0.313725,
						0
					],
					"id": "obj-97",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						892.444458,
						100,
						44,
						48
					],
					"saved_attribute_attributes": {
						"focusbordercolor": {
							"expression": ""
						},
						"valueof": {
							"parameter_longname": "live.dial[6]",
							"parameter_mmax": 360,
							"parameter_mmin": -360,
							"parameter_modmode": 0,
							"parameter_shortname": "roll",
							"parameter_type": 0,
							"parameter_unitstyle": 1
						}
					},
					"varname": "live.dial[6]"
				}
			},
			{
				"box": {
					"focusbordercolor": [
						0.313725,
						0.313725,
						0.313725,
						0
					],
					"id": "obj-99",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						835.444458,
						100,
						44,
						48
					],
					"saved_attribute_attributes": {
						"focusbordercolor": {
							"expression": ""
						},
						"valueof": {
							"parameter_longname": "live.dial[5]",
							"parameter_mmax": 360,
							"parameter_mmin": -360,
							"parameter_modmode": 0,
							"parameter_shortname": "pitch",
							"parameter_type": 0,
							"parameter_unitstyle": 1
						}
					},
					"varname": "live.dial[5]"
				}
			},
			{
				"box": {
					"focusbordercolor": [
						0.313725,
						0.313725,
						0.313725,
						0
					],
					"id": "obj-100",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						778.444458,
						100,
						44,
						48
					],
					"saved_attribute_attributes": {
						"focusbordercolor": {
							"expression": ""
						},
						"valueof": {
							"parameter_longname": "live.dial[4]",
							"parameter_mmax": 360,
							"parameter_mmin": -360,
							"parameter_modmode": 0,
							"parameter_shortname": "yaw",
							"parameter_type": 0,
							"parameter_unitstyle": 1
						}
					},
					"varname": "live.dial[4]"
				}
			},
			{
				"box": {
					"focusbordercolor": [
						0,
						0.019608,
						0.078431,
						0
					],
					"id": "obj-34",
					"maxclass": "live.dial",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						640,
						296,
						44,
						48
					],
					"saved_attribute_attributes": {
						"focusbordercolor": {
							"expression": ""
						},
						"valueof": {
							"parameter_initial": [
								30
							],
							"parameter_initial_enable": 1,
							"parameter_longname": "live.dial[14]",
							"parameter_mmax": 500,
							"parameter_modmode": 0,
							"parameter_shortname": " ",
							"parameter_type": 0,
							"parameter_unitstyle": 2
						}
					},
					"varname": "live.dial[1]"
				}
			},
			{
				"box": {
					"fontsize": 11,
					"id": "obj-35",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						640,
						346.5,
						78,
						21
					],
					"text": "/ramp/time $1"
				}
			},
			{
				"box": {
					"channels": 16,
					"id": "obj-22",
					"lastchannelcount": 0,
					"maxclass": "live.gain~",
					"numinlets": 16,
					"numoutlets": 19,
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
						"signal",
						"",
						"float",
						"list"
					],
					"parameter_enable": 1,
					"patching_rect": [
						13.444443,
						296.5,
						293,
						90
					],
					"relative": 1,
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_initial": [
								0
							],
							"parameter_longname": "live.gain~[2]",
							"parameter_mmax": 6,
							"parameter_mmin": -70,
							"parameter_modmode": 0,
							"parameter_shortname": "HOA stream",
							"parameter_type": 0,
							"parameter_unitstyle": 4
						}
					},
					"varname": "live.gain~[1]"
				}
			},
			{
				"box": {
					"bgmode": 0,
					"border": 0,
					"clickthrough": 0,
					"enablehscroll": 0,
					"enablevscroll": 0,
					"id": "obj-10",
					"lockeddragscroll": 0,
					"lockedsize": 0,
					"maxclass": "bpatcher",
					"name": "spat5.dsp.control.maxpat",
					"numinlets": 1,
					"numoutlets": 1,
					"offset": [
						0,
						0
					],
					"outlettype": [
						""
					],
					"patching_rect": [
						412.444458,
						90,
						110,
						57
					],
					"viewvisibility": 1
				}
			},
			{
				"box": {
					"bgcolor": [
						1,
						1,
						1,
						0
					],
					"bgmode": 0,
					"border": 0,
					"clickthrough": 0,
					"enablehscroll": 0,
					"enablevscroll": 0,
					"id": "obj-20",
					"lockeddragscroll": 0,
					"lockedsize": 0,
					"maxclass": "bpatcher",
					"name": "spat5.copyright.maxpat",
					"numinlets": 0,
					"numoutlets": 0,
					"offset": [
						0,
						0
					],
					"patching_rect": [
						1007.9444579999999,
						10,
						239,
						70
					],
					"viewvisibility": 1
				}
			},
			{
				"box": {
					"channels": 16,
					"id": "obj-28",
					"lastchannelcount": 0,
					"maxclass": "live.gain~",
					"numinlets": 16,
					"numoutlets": 19,
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
						"signal",
						"",
						"float",
						"list"
					],
					"parameter_enable": 1,
					"patching_rect": [
						34.17777777777778,
						496,
						197,
						90
					],
					"relative": 1,
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_initial": [
								0
							],
							"parameter_longname": "live.gain~[1]",
							"parameter_mmax": 6,
							"parameter_mmin": -70,
							"parameter_modmode": 0,
							"parameter_shortname": "HOA stream",
							"parameter_type": 0,
							"parameter_unitstyle": 4
						}
					},
					"varname": "live.gain~"
				}
			},
			{
				"box": {
					"bubble": 1,
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-26",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						312,
						475,
						216,
						23
					],
					"text": "double-click to open the status window"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-6",
					"maxclass": "newobj",
					"numinlets": 0,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						397.444458,
						59.5,
						125,
						21
					],
					"text": "spat5.dsp.management"
				}
			},
			{
				"box": {
					"bubble": 1,
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-67",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						312,
						450,
						160,
						23
					],
					"text": "rotation in the HOA domain"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-21",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						397.444458,
						346.5,
						29,
						21
					],
					"text": "thru"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-19",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						397.444458,
						156.5,
						29,
						21
					],
					"text": "thru"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-7",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						778.444458,
						346.5,
						78,
						21
					],
					"text": "prepend /quat"
				}
			},
			{
				"box": {
					"bubble": 1,
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-54",
					"linecount": 4,
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1140.444458,
						107.5,
						112,
						60
					],
					"text": "In Spat, roll/pitch/yaw follows the Euler zyx convention"
				}
			},
			{
				"box": {
					"bubble": 1,
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-55",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						893.444458,
						203.5,
						205,
						23
					],
					"text": "Converts Euler angles to quarternion"
				}
			},
			{
				"box": {
					"id": "obj-56",
					"maxclass": "live.menu",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"",
						"",
						"float"
					],
					"parameter_enable": 1,
					"patching_rect": [
						1038.444458,
						118.5,
						100,
						15
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_enum": [
								"xyx",
								"yxy",
								"yzy",
								"zxz",
								"zyz",
								"xyz",
								"xzy",
								"yxz",
								"yzx",
								"zxy",
								"zyx"
							],
							"parameter_initial": [
								10
							],
							"parameter_initial_enable": 1,
							"parameter_longname": "live.menu[3]",
							"parameter_mmax": 10,
							"parameter_modmode": 0,
							"parameter_shortname": "live.menu[3]",
							"parameter_type": 2
						}
					},
					"varname": "live.menu"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-57",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1038.444458,
						148.5,
						56,
						21
					],
					"text": "/mode $1"
				}
			},
			{
				"box": {
					"bubble": 1,
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-58",
					"linecount": 3,
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						935.444458,
						100,
						93,
						47
					],
					"text": "Euler angles, expressed in degrees"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-68",
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
						778.444458,
						239.5,
						247,
						21
					],
					"text": "unjoin 4"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-70",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					],
					"patching_rect": [
						778.444458,
						204.5,
						111,
						21
					],
					"text": "spat5.quat.fromeuler"
				}
			},
			{
				"box": {
					"bubble": 1,
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-39",
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						1001.444458,
						273.5,
						79,
						23
					],
					"text": "quaternion"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"format": 6,
					"id": "obj-44",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						949.444458,
						274.5,
						50,
						21
					]
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"format": 6,
					"id": "obj-45",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						892.444458,
						274.5,
						50,
						21
					]
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"format": 6,
					"id": "obj-46",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						835.444458,
						274.5,
						50,
						21
					]
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"format": 6,
					"id": "obj-47",
					"maxclass": "flonum",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"bang"
					],
					"parameter_enable": 0,
					"patching_rect": [
						778.444458,
						274.5,
						50,
						21
					]
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-50",
					"maxclass": "newobj",
					"numinlets": 4,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						778.444458,
						309.5,
						190,
						21
					],
					"text": "pak 0. 0. 0. 0."
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-75",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						600,
						261.5,
						75,
						21
					],
					"text": "/ypr $1 $2 $3"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-18",
					"maxclass": "newobj",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						435.444458,
						389.5,
						29,
						21
					],
					"text": "thru"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-1",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						549.444458,
						346.5,
						44,
						21
					],
					"text": "/roll $1"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-3",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						492.444458,
						346.5,
						52,
						21
					],
					"text": "/pitch $1"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-16",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						435.444458,
						346.5,
						48,
						21
					],
					"text": "/yaw $1"
				}
			},
			{
				"box": {
					"bgmode": 0,
					"border": 0,
					"clickthrough": 0,
					"enablehscroll": 0,
					"enablevscroll": 0,
					"id": "obj-9",
					"lockeddragscroll": 0,
					"lockedsize": 0,
					"maxclass": "bpatcher",
					"name": "spat5.monitor.maxpat",
					"numinlets": 1,
					"numoutlets": 0,
					"offset": [
						0,
						0
					],
					"patching_rect": [
						810,
						458.75,
						380,
						133.5
					],
					"viewvisibility": 1
				}
			},
			{
				"box": {
					"bubble": 1,
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-8",
					"linecount": 3,
					"maxclass": "comment",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [
						504,
						402,
						149,
						47
					],
					"text": "NB : HOA components  use the \"ACN\" sorting convention"
				}
			},
			{
				"box": {
					"fontname": "Arial",
					"fontsize": 11,
					"id": "obj-15",
					"maxclass": "newobj",
					"numinlets": 16,
					"numoutlets": 17,
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
						"signal",
						""
					],
					"patching_rect": [
						13.444443,
						441.5,
						225,
						21
					],
					"saved_object_attributes": {
						"parameter_enable": 0
					},
					"text": "spat5.hoa.rotate~ @order 3 @dimension 3D"
				}
			},
			{
				"box": {
					"id": "obj-qmw-input-comment",
					"maxclass": "comment",
					"text": "Analog snake input from QMW Bloch Harmonics v8: QMW DAC 1–8 → ADC 17–24; QMW DAC 9–16 → ADC 33–40. These are HOA3 ACN 0–15 / SN3D components, so they bypass the encoder.",
					"patching_rect": [
						13,
						190,
						720,
						36
					],
					"linecount": 2
				}
			},
			{
				"box": {
					"id": "obj-qmw-decoder",
					"maxclass": "newobj",
					"text": "spat5.hoa.decoder~ @order 3 @dimension 3D @outputs 30 @mc 1 @initwith \"/norm SN3D, /method energy-preserving, /powercompensation 1\"",
					"patching_rect": [
						18,
						710,
						650,
						22
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"multichannelsignal",
						""
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-safety",
					"maxclass": "newobj",
					"text": "mc.*~ 0.1",
					"patching_rect": [
						18,
						770,
						82,
						22
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"multichannelsignal"
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-layout",
					"maxclass": "newobj",
					"text": "qmw_craive_three_ring30_experimental_layout_v1",
					"patching_rect": [
						700,
						710,
						305,
						22
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
					"id": "obj-qmw-loadbang",
					"maxclass": "newobj",
					"text": "loadbang",
					"patching_rect": [
						700,
						655,
						60,
						22
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-reload",
					"maxclass": "button",
					"patching_rect": [
						780,
						655,
						24,
						24
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-reload-comment",
					"maxclass": "comment",
					"text": "reload CRAIVE decoder geometry",
					"patching_rect": [
						815,
						656,
						190,
						22
					],
					"linecount": 1
				}
			},
			{
				"box": {
					"id": "obj-qmw-decoder-comment",
					"maxclass": "comment",
					"text": "Third-order ACN/SN3D HOA → experimental CRAIVE three-ring 30-speaker array",
					"patching_rect": [
						18,
						685,
						570,
						22
					],
					"linecount": 1
				}
			},
			{
				"box": {
					"id": "obj-qmw-safety-comment",
					"maxclass": "comment",
					"text": "−20 dB safety trim for first room test; change 0.1 toward 1.0 only after routing is verified",
					"patching_rect": [
						115,
						770,
						560,
						22
					],
					"linecount": 2
				}
			},
			{
				"box": {
					"id": "obj-qmw-output-comment",
					"maxclass": "comment",
					"text": "EXPERIMENTAL routing. Decoder 1–30 → hardware 4 8 12 16 20 23 28 33 37 42 46 51 55 58 63 1 129 130 131 132 133 134 135 136 137 138 139 140 141 142. Verify outputs 129–142 physically before room playback.",
					"patching_rect": [
						23,
						885,
						900,
						36
					],
					"linecount": 2
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-receive",
					"maxclass": "newobj",
					"text": "spat5.osc.udpreceive @port 7475",
					"patching_rect": [
						960,
						620,
						230,
						22
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-route",
					"maxclass": "newobj",
					"text": "spat5.osc.route /qmw/craive/hoa",
					"patching_rect": [
						960,
						660,
						220,
						22
					],
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						""
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-trigger",
					"maxclass": "newobj",
					"text": "t l b b",
					"patching_rect": [
						960,
						700,
						65,
						22
					],
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"list",
						"bang",
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-fresh",
					"maxclass": "message",
					"text": "1",
					"patching_rect": [
						1100,
						700,
						30,
						22
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-rearm",
					"maxclass": "message",
					"text": "stop, bang",
					"patching_rect": [
						1040,
						740,
						70,
						22
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-delay",
					"maxclass": "newobj",
					"text": "delay 1000",
					"patching_rect": [
						1040,
						780,
						75,
						22
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"bang"
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-stale",
					"maxclass": "message",
					"text": "0",
					"patching_rect": [
						1040,
						820,
						30,
						22
					],
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-status",
					"maxclass": "toggle",
					"patching_rect": [
						1150,
						780,
						28,
						28
					],
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"int"
					]
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-ramp-init",
					"maxclass": "newobj",
					"text": "loadmess /ramp/time 50",
					"patching_rect": [
						960,
						860,
						145,
						22
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
					"id": "obj-qmw-osc-title",
					"maxclass": "comment",
					"text": "REMOTE HOA ROTATION · UDP 7475",
					"patching_rect": [
						960,
						585,
						300,
						24
					],
					"fontsize": 13,
					"linecount": 1
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-path",
					"maxclass": "comment",
					"text": "Accepts /qmw/craive/hoa/ypr yaw pitch roll, plus /yaw, /pitch, /roll or /quat. Green means a valid packet arrived within the last second.",
					"patching_rect": [
						1195,
						650,
						195,
						78
					],
					"fontsize": 11,
					"linecount": 2
				}
			},
			{
				"box": {
					"id": "obj-qmw-osc-failsafe",
					"maxclass": "comment",
					"text": "If OSC becomes stale, audio continues and rotation holds its last value. The original local rotation controls remain available as a fallback.",
					"patching_rect": [
						1195,
						780,
						195,
						72
					],
					"fontsize": 11,
					"linecount": 2
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"destination": [
						"obj-18",
						0
					],
					"midpoints": [
						558.944458,
						376,
						444.944458,
						376
					],
					"source": [
						"obj-1",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-19",
						0
					],
					"source": [
						"obj-10",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-90",
						0
					],
					"source": [
						"obj-100",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						15
					],
					"source": [
						"obj-15",
						15
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						14
					],
					"source": [
						"obj-15",
						14
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						13
					],
					"source": [
						"obj-15",
						13
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						12
					],
					"source": [
						"obj-15",
						12
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						11
					],
					"source": [
						"obj-15",
						11
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						10
					],
					"source": [
						"obj-15",
						10
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						9
					],
					"source": [
						"obj-15",
						9
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						8
					],
					"source": [
						"obj-15",
						8
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						7
					],
					"source": [
						"obj-15",
						7
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						6
					],
					"source": [
						"obj-15",
						6
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						5
					],
					"source": [
						"obj-15",
						5
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						4
					],
					"source": [
						"obj-15",
						4
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						3
					],
					"source": [
						"obj-15",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						2
					],
					"source": [
						"obj-15",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						1
					],
					"source": [
						"obj-15",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-28",
						0
					],
					"source": [
						"obj-15",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-18",
						0
					],
					"midpoints": [
						444.944458,
						378,
						444.944458,
						378
					],
					"source": [
						"obj-16",
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
					"source": [
						"obj-17",
						0
					]
				}
			},
			{
				"patchline": {
					"color": [
						0.000110864639282,
						0.001760244369507,
						0.998218417167664,
						1
					],
					"destination": [
						"obj-15",
						0
					],
					"midpoints": [
						444.944458,
						423,
						22.944443,
						423
					],
					"source": [
						"obj-18",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-48",
						0
					],
					"source": [
						"obj-19",
						0
					]
				}
			},
			{
				"patchline": {
					"color": [
						0.000110864639282,
						0.001760244369507,
						0.998218417167664,
						1
					],
					"destination": [
						"obj-18",
						0
					],
					"source": [
						"obj-21",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						15
					],
					"source": [
						"obj-22",
						15
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						14
					],
					"source": [
						"obj-22",
						14
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						13
					],
					"source": [
						"obj-22",
						13
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						12
					],
					"source": [
						"obj-22",
						12
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						11
					],
					"source": [
						"obj-22",
						11
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						10
					],
					"source": [
						"obj-22",
						10
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						9
					],
					"source": [
						"obj-22",
						9
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						8
					],
					"source": [
						"obj-22",
						8
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						7
					],
					"source": [
						"obj-22",
						7
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						6
					],
					"source": [
						"obj-22",
						6
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						5
					],
					"source": [
						"obj-22",
						5
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						4
					],
					"source": [
						"obj-22",
						4
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						3
					],
					"source": [
						"obj-22",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						2
					],
					"source": [
						"obj-22",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						1
					],
					"source": [
						"obj-22",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-15",
						0
					],
					"source": [
						"obj-22",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-17",
						0
					],
					"source": [
						"obj-27",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						15
					],
					"source": [
						"obj-28",
						15
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						14
					],
					"source": [
						"obj-28",
						14
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						13
					],
					"source": [
						"obj-28",
						13
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						12
					],
					"source": [
						"obj-28",
						12
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						11
					],
					"source": [
						"obj-28",
						11
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						10
					],
					"source": [
						"obj-28",
						10
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						9
					],
					"source": [
						"obj-28",
						9
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						8
					],
					"source": [
						"obj-28",
						8
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						7
					],
					"source": [
						"obj-28",
						7
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						6
					],
					"source": [
						"obj-28",
						6
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						5
					],
					"source": [
						"obj-28",
						5
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						4
					],
					"source": [
						"obj-28",
						4
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						3
					],
					"source": [
						"obj-28",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						2
					],
					"source": [
						"obj-28",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						1
					],
					"source": [
						"obj-28",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-11",
						0
					],
					"source": [
						"obj-28",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-18",
						0
					],
					"midpoints": [
						1109.944458,
						378,
						444.944458,
						378
					],
					"source": [
						"obj-29",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-18",
						0
					],
					"midpoints": [
						501.944458,
						376,
						444.944458,
						376
					],
					"source": [
						"obj-3",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-37",
						0
					],
					"source": [
						"obj-31",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-1",
						0
					],
					"source": [
						"obj-32",
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
						"obj-33",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-35",
						0
					],
					"source": [
						"obj-34",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-18",
						0
					],
					"midpoints": [
						649.5,
						378,
						444.944458,
						378
					],
					"source": [
						"obj-35",
						0
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
						"obj-36",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-43",
						0
					],
					"source": [
						"obj-37",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-75",
						0
					],
					"source": [
						"obj-38",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-38",
						2
					],
					"source": [
						"obj-40",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-38",
						1
					],
					"source": [
						"obj-41",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-38",
						0
					],
					"source": [
						"obj-42",
						0
					]
				}
			},
			{
				"patchline": {
					"color": [
						0.000110864639282,
						0.001760244369507,
						0.998218417167664,
						1
					],
					"destination": [
						"obj-48",
						0
					],
					"midpoints": [
						499.5,
						250.25,
						406.944458,
						250.25
					],
					"order": 0,
					"source": [
						"obj-43",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-50",
						3
					],
					"source": [
						"obj-44",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-50",
						2
					],
					"source": [
						"obj-45",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-50",
						1
					],
					"source": [
						"obj-46",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-50",
						0
					],
					"source": [
						"obj-47",
						0
					]
				}
			},
			{
				"patchline": {
					"color": [
						0.000110864639282,
						0.001760244369507,
						0.998218417167664,
						1
					],
					"destination": [
						"obj-21",
						0
					],
					"source": [
						"obj-48",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-29",
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
						"obj-7",
						0
					],
					"source": [
						"obj-50",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-57",
						0
					],
					"source": [
						"obj-56",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-70",
						0
					],
					"midpoints": [
						1047.944458,
						191.5,
						787.944458,
						191.5
					],
					"source": [
						"obj-57",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-19",
						0
					],
					"midpoints": [
						406.944458,
						147.5,
						406.944458,
						147.5
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
						"obj-44",
						0
					],
					"source": [
						"obj-68",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-45",
						0
					],
					"source": [
						"obj-68",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-46",
						0
					],
					"source": [
						"obj-68",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-47",
						0
					],
					"source": [
						"obj-68",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-18",
						0
					],
					"midpoints": [
						787.944458,
						377,
						444.944458,
						377
					],
					"source": [
						"obj-7",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-68",
						0
					],
					"source": [
						"obj-70",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-18",
						0
					],
					"midpoints": [
						609.5,
						376,
						444.944458,
						376
					],
					"source": [
						"obj-75",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-70",
						0
					],
					"source": [
						"obj-90",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-90",
						2
					],
					"source": [
						"obj-97",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-90",
						1
					],
					"source": [
						"obj-99",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
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
						"obj-2",
						1
					],
					"destination": [
						"obj-22",
						1
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						2
					],
					"destination": [
						"obj-22",
						2
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						3
					],
					"destination": [
						"obj-22",
						3
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						4
					],
					"destination": [
						"obj-22",
						4
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						5
					],
					"destination": [
						"obj-22",
						5
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						6
					],
					"destination": [
						"obj-22",
						6
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						7
					],
					"destination": [
						"obj-22",
						7
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						8
					],
					"destination": [
						"obj-22",
						8
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						9
					],
					"destination": [
						"obj-22",
						9
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						10
					],
					"destination": [
						"obj-22",
						10
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						11
					],
					"destination": [
						"obj-22",
						11
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						12
					],
					"destination": [
						"obj-22",
						12
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						13
					],
					"destination": [
						"obj-22",
						13
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						14
					],
					"destination": [
						"obj-22",
						14
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-2",
						15
					],
					"destination": [
						"obj-22",
						15
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
						"obj-qmw-decoder",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-decoder",
						0
					],
					"destination": [
						"obj-qmw-safety",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-safety",
						0
					],
					"destination": [
						"obj-1673",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-loadbang",
						0
					],
					"destination": [
						"obj-qmw-layout",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-reload",
						0
					],
					"destination": [
						"obj-qmw-layout",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-layout",
						0
					],
					"destination": [
						"obj-qmw-decoder",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-osc-receive",
						0
					],
					"destination": [
						"obj-qmw-osc-route",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-osc-route",
						0
					],
					"destination": [
						"obj-qmw-osc-trigger",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-osc-trigger",
						0
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
						"obj-qmw-osc-trigger",
						1
					],
					"destination": [
						"obj-qmw-osc-rearm",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-osc-trigger",
						2
					],
					"destination": [
						"obj-qmw-osc-fresh",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-osc-fresh",
						0
					],
					"destination": [
						"obj-qmw-osc-status",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-osc-rearm",
						0
					],
					"destination": [
						"obj-qmw-osc-delay",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-osc-delay",
						0
					],
					"destination": [
						"obj-qmw-osc-stale",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-osc-stale",
						0
					],
					"destination": [
						"obj-qmw-osc-status",
						0
					]
				}
			},
			{
				"patchline": {
					"source": [
						"obj-qmw-osc-ramp-init",
						0
					],
					"destination": [
						"obj-18",
						0
					]
				}
			}
		],
		"parameters": {
			"obj-100": [
				"live.dial[4]",
				"yaw",
				0
			],
			"obj-10::obj-58": [
				"live.text[9]",
				"live.text[9]",
				0
			],
			"obj-10::obj-62": [
				"live.text[11]",
				"live.text[9]",
				0
			],
			"obj-10::obj-6::obj-3": [
				"live.text[8]",
				"live.text",
				0
			],
			"obj-10::obj-6::obj-6": [
				"live.text[7]",
				"live.text",
				0
			],
			"obj-17": [
				"live.button[16]",
				"live.button",
				0
			],
			"obj-22": [
				"live.gain~[2]",
				"HOA stream",
				0
			],
			"obj-28": [
				"live.gain~[1]",
				"HOA stream",
				0
			],
			"obj-32": [
				"live.dial[10]",
				"roll",
				0
			],
			"obj-33": [
				"live.dial[12]",
				"pitch",
				0
			],
			"obj-34": [
				"live.dial[14]",
				" ",
				0
			],
			"obj-36": [
				"live.dial[15]",
				"yaw",
				0
			],
			"obj-37::obj-10": [
				"live.menu[1]",
				"live.menu[1]",
				0
			],
			"obj-40": [
				"live.dial[7]",
				"roll",
				0
			],
			"obj-41": [
				"live.dial[8]",
				"pitch",
				0
			],
			"obj-42": [
				"live.dial[16]",
				"yaw",
				0
			],
			"obj-56": [
				"live.menu[3]",
				"live.menu[3]",
				0
			],
			"obj-6::obj-14": [
				"live.toggle[5]",
				"live.toggle[2]",
				0
			],
			"obj-6::obj-25": [
				"live.toggle[9]",
				"live.toggle",
				0
			],
			"obj-6::obj-31": [
				"live.dial[9]",
				"automute",
				0
			],
			"obj-6::obj-34": [
				"live.toggle[3]",
				"live.toggle[2]",
				0
			],
			"obj-6::obj-37": [
				"live.toggle[10]",
				"live.toggle[2]",
				0
			],
			"obj-6::obj-40::obj-8": [
				"live.toggle[6]",
				"live.toggle[6]",
				0
			],
			"obj-6::obj-42": [
				"live.dial[1]",
				"ramp",
				0
			],
			"obj-6::obj-50": [
				"live.dial[2]",
				"ramp",
				0
			],
			"obj-6::obj-52": [
				"live.tab[1]",
				"live.tab[1]",
				0
			],
			"obj-6::obj-55": [
				"live.toggle[4]",
				"live.toggle[2]",
				0
			],
			"obj-6::obj-58": [
				"live.toggle[7]",
				"live.toggle[2]",
				0
			],
			"obj-6::obj-66": [
				"live.dial[11]",
				"dry/wet",
				0
			],
			"obj-6::obj-70": [
				"live.toggle[8]",
				"live.toggle[8]",
				0
			],
			"obj-6::obj-7::obj-58": [
				"live.text[10]",
				"live.text[9]",
				0
			],
			"obj-6::obj-7::obj-62": [
				"live.text[12]",
				"live.text[9]",
				0
			],
			"obj-6::obj-7::obj-6::obj-3": [
				"live.text",
				"live.text",
				0
			],
			"obj-6::obj-7::obj-6::obj-6": [
				"live.text[6]",
				"live.text",
				0
			],
			"obj-97": [
				"live.dial[6]",
				"roll",
				0
			],
			"obj-99": [
				"live.dial[5]",
				"pitch",
				0
			],
			"obj-9::obj-11": [
				"live.text[4]",
				"live.text",
				0
			],
			"obj-9::obj-110": [
				"live.text[5]",
				"live.text",
				0
			],
			"obj-9::obj-16": [
				"live.text[1]",
				"live.text",
				0
			],
			"obj-9::obj-55": [
				"live.text[3]",
				"live.text",
				0
			],
			"obj-9::obj-606": [
				"live.text[2]",
				"live.text",
				0
			],
			"obj-9::obj-607": [
				"live.button[2]",
				"live.button",
				0
			],
			"parameterbanks": {
				"0": {
					"index": 0,
					"name": "",
					"parameters": [
						"-",
						"-",
						"-",
						"-",
						"-",
						"-",
						"-",
						"-"
					]
				}
			},
			"parameter_overrides": {
				"obj-10::obj-58": {
					"parameter_longname": "live.text[9]"
				},
				"obj-10::obj-62": {
					"parameter_longname": "live.text[11]"
				},
				"obj-10::obj-6::obj-3": {
					"parameter_longname": "live.text[8]"
				},
				"obj-10::obj-6::obj-6": {
					"parameter_longname": "live.text[7]"
				},
				"obj-6::obj-25": {
					"parameter_longname": "live.toggle[9]"
				},
				"obj-6::obj-37": {
					"parameter_longname": "live.toggle[10]"
				},
				"obj-6::obj-7::obj-6::obj-6": {
					"parameter_longname": "live.text[6]"
				},
				"obj-9::obj-607": {
					"parameter_longname": "live.button[2]"
				}
			},
			"inherited_shortname": 1
		},
		"dependency_cache": [
			{
				"name": "ircam-cnrs-spat-alpha.png",
				"bootpath": "~/Documents/Max 8/Packages/spat5/media/images",
				"patcherrelativepath": "../Documents/Max 8/Packages/spat5/media/images",
				"type": "PNG",
				"implicit": 1
			},
			{
				"name": "spat5.copyright.maxpat",
				"bootpath": "~/Documents/Max 8/Packages/spat5/patchers",
				"patcherrelativepath": "../Documents/Max 8/Packages/spat5/patchers",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "spat5.cpu.mxo",
				"type": "iLaX"
			},
			{
				"name": "spat5.dsp.control.maxpat",
				"bootpath": "~/Documents/Max 8/Packages/spat5/patchers",
				"patcherrelativepath": "../Documents/Max 8/Packages/spat5/patchers",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "spat5.dsp.management.maxpat",
				"bootpath": "~/Documents/Max 8/Packages/spat5/patchers",
				"patcherrelativepath": "../Documents/Max 8/Packages/spat5/patchers",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "spat5.dsp.mute.bypass.maxpat",
				"bootpath": "~/Documents/Max 8/Packages/spat5/patchers",
				"patcherrelativepath": "../Documents/Max 8/Packages/spat5/patchers",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "spat5.hoa.encoder~.mxo",
				"type": "iLaX"
			},
			{
				"name": "spat5.hoa.rotate~.mxo",
				"type": "iLaX"
			},
			{
				"name": "spat5.hostinfos.mxo",
				"type": "iLaX"
			},
			{
				"name": "spat5.known.hoanorm.maxpat",
				"bootpath": "~/Documents/Max 8/Packages/spat5/patchers",
				"patcherrelativepath": "../Documents/Max 8/Packages/spat5/patchers",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "spat5.monitor.maxpat",
				"bootpath": "~/Documents/Max 8/Packages/spat5/patchers",
				"patcherrelativepath": "../Documents/Max 8/Packages/spat5/patchers",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "spat5.osc.route.mxo",
				"type": "iLaX"
			},
			{
				"name": "spat5.quat.fromeuler.mxo",
				"type": "iLaX"
			},
			{
				"name": "spat5.viewer.mxo",
				"type": "iLaX"
			},
			{
				"name": "thru.maxpat",
				"bootpath": "C74:/patchers/m4l/Pluggo for Live resources/patches",
				"type": "JSON",
				"implicit": 1
			},
			{
				"name": "spat5.osc.udpreceive.mxo",
				"type": "iLaX",
				"implicit": 1
			},
			{
				"name": "qmw_craive_three_ring30_experimental_layout_v1.maxpat",
				"type": "JSON",
				"implicit": 1
			}
		],
		"autosave": 0
	}
}
