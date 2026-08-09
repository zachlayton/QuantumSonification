{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 9,
			"minor" : 0,
			"revision" : 5,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ 120.0, 120.0, 1040.0, 620.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"comment" : "qubit 0 audio",
					"id" : "in1",
					"index" : 1,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 40.0, 40.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "qubit 1 audio",
					"id" : "in2",
					"index" : 2,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 110.0, 40.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "qubit 2 audio",
					"id" : "in3",
					"index" : 3,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 180.0, 40.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "qubit 3 audio",
					"id" : "in4",
					"index" : 4,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 250.0, 40.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "qubit 0 Bloch XYZ",
					"id" : "ctrl1",
					"index" : 5,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 330.0, 40.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "qubit 1 Bloch XYZ",
					"id" : "ctrl2",
					"index" : 6,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 390.0, 40.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "qubit 2 Bloch XYZ",
					"id" : "ctrl3",
					"index" : 7,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 450.0, 40.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "qubit 3 Bloch XYZ",
					"id" : "ctrl4",
					"index" : 8,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 510.0, 40.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "open Spat5 window",
					"id" : "open_in",
					"index" : 10,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 900.0, 40.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "Spat update interval (ms)",
					"id" : "rate_in",
					"index" : 9,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 570.0, 40.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 330.0, 20.0, 470.0, 20.0 ],
					"text" : "Four independent reduced-qubit sources → Spat5 binaural renderer"
				}

			}
, 			{
				"box" : 				{
					"id" : "c1",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 330.0, 80.0, 430.0, 22.0 ],
					"text" : "qmw_qubit_spat_control /source/1/aed /source/1/aperture /source/1/yaw"
				}

			}
, 			{
				"box" : 				{
					"id" : "c2",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 330.0, 115.0, 430.0, 22.0 ],
					"text" : "qmw_qubit_spat_control /source/2/aed /source/2/aperture /source/2/yaw"
				}

			}
, 			{
				"box" : 				{
					"id" : "c3",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 330.0, 150.0, 430.0, 22.0 ],
					"text" : "qmw_qubit_spat_control /source/3/aed /source/3/aperture /source/3/yaw"
				}

			}
, 			{
				"box" : 				{
					"id" : "c4",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 330.0, 185.0, 430.0, 22.0 ],
					"text" : "qmw_qubit_spat_control /source/4/aed /source/4/aperture /source/4/yaw"
				}

			}
, 			{
				"box" : 				{
					"id" : "oper",
					"linecount" : 2,
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 330.0, 240.0, 680.0, 35.0 ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0
					}
,
					"text" : "spat5.oper @initwith \"/source/number 4, /source/1/label q0, /source/2/label q1, /source/3/label q2, /source/4/label q3, /source/*/aperture/visible 1, /source/*/constraint/circular 0\""
				}

			}
, 			{
				"box" : 				{
					"id" : "renderer",
					"maxclass" : "newobj",
					"numinlets" : 4,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "" ],
					"patching_rect" : [ 330.0, 320.0, 610.0, 22.0 ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0
					}
,
					"text" : "spat5.spat~ @inputs 4 @internals 8 @outputs 2 @rooms 1 @initwith \"/panning/type binaural\""
				}

			}
, 			{
				"box" : 				{
					"id" : "loadbang",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 760.0, 80.0, 60.0, 22.0 ],
					"text" : "loadbang"
				}

			}
, 			{
				"box" : 				{
					"id" : "delay",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 830.0, 80.0, 70.0, 22.0 ],
					"text" : "delay 750"
				}

			}
, 			{
				"box" : 				{
					"id" : "open",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 879.0, 141.0, 95.0, 22.0 ],
					"text" : "/window/open"
				}

			}
, 			{
				"box" : 				{
					"comment" : "binaural left",
					"id" : "out_l",
					"index" : 1,
					"maxclass" : "outlet",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 420.0, 410.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "binaural right",
					"id" : "out_r",
					"index" : 2,
					"maxclass" : "outlet",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 500.0, 410.0, 30.0, 30.0 ]
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "oper", 0 ],
					"source" : [ "c1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "oper", 0 ],
					"source" : [ "c2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "oper", 0 ],
					"source" : [ "c3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "oper", 0 ],
					"source" : [ "c4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "c1", 0 ],
					"source" : [ "ctrl1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "c2", 0 ],
					"source" : [ "ctrl2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "c3", 0 ],
					"source" : [ "ctrl3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "c4", 0 ],
					"source" : [ "ctrl4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "open", 0 ],
					"source" : [ "delay", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "renderer", 0 ],
					"source" : [ "in1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "renderer", 1 ],
					"source" : [ "in2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "renderer", 2 ],
					"source" : [ "in3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "renderer", 3 ],
					"source" : [ "in4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "delay", 0 ],
					"source" : [ "loadbang", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "oper", 0 ],
					"source" : [ "open", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "open", 0 ],
					"source" : [ "open_in", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "renderer", 0 ],
					"source" : [ "oper", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "c1", 1 ],
					"order" : 3,
					"source" : [ "rate_in", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "c2", 1 ],
					"order" : 2,
					"source" : [ "rate_in", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "c3", 1 ],
					"order" : 1,
					"source" : [ "rate_in", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "c4", 1 ],
					"order" : 0,
					"source" : [ "rate_in", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "out_l", 0 ],
					"source" : [ "renderer", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "out_r", 0 ],
					"source" : [ "renderer", 1 ]
				}

			}
 ],
		"originid" : "pat-179"
	}

}
