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
		"rect" : [ 134.0, 172.0, 570.0, 530.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"comment" : "",
					"id" : "in-re",
					"index" : 1,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 30.0, 30.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "",
					"id" : "in-im",
					"index" : 2,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 250.0, 30.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "",
					"id" : "in-ch",
					"index" : 3,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 470.0, 30.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "un-re",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 16,
					"outlettype" : [ "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal" ],
					"patching_rect" : [ 30.0, 100.0, 95.0, 22.0 ],
					"text" : "mc.unpack~ 16"
				}

			}
, 			{
				"box" : 				{
					"id" : "un-im",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 16,
					"outlettype" : [ "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal", "signal" ],
					"patching_rect" : [ 250.0, 100.0, 95.0, 22.0 ],
					"text" : "mc.unpack~ 16"
				}

			}
, 			{
				"box" : 				{
					"id" : "sel-re",
					"maxclass" : "newobj",
					"numinlets" : 17,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 30.0, 180.0, 85.0, 22.0 ],
					"text" : "selector~ 16"
				}

			}
, 			{
				"box" : 				{
					"id" : "sel-im",
					"maxclass" : "newobj",
					"numinlets" : 17,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 250.0, 180.0, 85.0, 22.0 ],
					"text" : "selector~ 16"
				}

			}
, 			{
				"box" : 				{
					"id" : "clip",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 470.0, 100.0, 65.0, 22.0 ],
					"text" : "clip 1 16"
				}

			}
, 			{
				"box" : 				{
					"bufsize" : 256,
					"calccount" : 4,
					"id" : "scope",
					"maxclass" : "scope~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 120.0, 250.0, 300.0, 240.0 ],
					"range" : [ -0.1, 0.1 ]
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "comment",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 120.0, 220.0, 330.0, 20.0 ],
					"text" : "Selected-channel I/Q trajectory (pre/post rho output)"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 0 ],
					"order" : 0,
					"source" : [ "clip", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 0 ],
					"order" : 1,
					"source" : [ "clip", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "clip", 0 ],
					"source" : [ "in-ch", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "un-im", 0 ],
					"source" : [ "in-im", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "un-re", 0 ],
					"source" : [ "in-re", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scope", 1 ],
					"source" : [ "sel-im", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scope", 0 ],
					"source" : [ "sel-re", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 16 ],
					"source" : [ "un-im", 15 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 15 ],
					"source" : [ "un-im", 14 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 14 ],
					"source" : [ "un-im", 13 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 13 ],
					"source" : [ "un-im", 12 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 12 ],
					"source" : [ "un-im", 11 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 11 ],
					"source" : [ "un-im", 10 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 10 ],
					"source" : [ "un-im", 9 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 9 ],
					"source" : [ "un-im", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 8 ],
					"source" : [ "un-im", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 7 ],
					"source" : [ "un-im", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 6 ],
					"source" : [ "un-im", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 5 ],
					"source" : [ "un-im", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 4 ],
					"source" : [ "un-im", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 3 ],
					"source" : [ "un-im", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 2 ],
					"source" : [ "un-im", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-im", 1 ],
					"source" : [ "un-im", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 16 ],
					"source" : [ "un-re", 15 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 15 ],
					"source" : [ "un-re", 14 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 14 ],
					"source" : [ "un-re", 13 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 13 ],
					"source" : [ "un-re", 12 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 12 ],
					"source" : [ "un-re", 11 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 11 ],
					"source" : [ "un-re", 10 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 10 ],
					"source" : [ "un-re", 9 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 9 ],
					"source" : [ "un-re", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 8 ],
					"source" : [ "un-re", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 7 ],
					"source" : [ "un-re", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 6 ],
					"source" : [ "un-re", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 5 ],
					"source" : [ "un-re", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 4 ],
					"source" : [ "un-re", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 3 ],
					"source" : [ "un-re", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 2 ],
					"source" : [ "un-re", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sel-re", 1 ],
					"source" : [ "un-re", 0 ]
				}

			}
 ],
		"originid" : "pat-438"
	}

}
