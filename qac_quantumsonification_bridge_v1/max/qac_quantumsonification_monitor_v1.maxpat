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
		"rect" : [ 353.0, 398.0, 740.0, 390.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 55.0, 54.0, 97.0, 22.0 ],
					"text" : "udpreceive 7410"
				}

			}
, 			{
				"box" : 				{
					"id" : "parse",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 55.0, 103.0, 98.0, 22.0 ],
					"text" : "OSC-route /qmw"
				}

			}
, 			{
				"box" : 				{
					"id" : "qmw",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 55.0, 201.0, 125.0, 22.0 ],
					"text" : "OSC-route /qac /state"
				}

			}
, 			{
				"box" : 				{
					"id" : "print",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 55.0, 299.0, 118.0, 22.0 ],
					"text" : "print QAC_BRIDGE"
				}

			}
, 			{
				"box" : 				{
					"id" : "state-print",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 200.0, 250.0, 110.0, 22.0 ],
					"text" : "print QAC_STATE"
				}

			}
, 			{
				"box" : 				{
					"id" : "comment",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 194.0, 299.0, 460.0, 20.0 ],
					"text" : "Monitor: QAC analysis and /qmw/state committed/error appear in the Max Console"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "qmw", 0 ],
					"source" : [ "parse", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "print", 0 ],
					"source" : [ "qmw", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "state-print", 0 ],
					"source" : [ "qmw", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "parse", 0 ],
					"source" : [ "udp", 0 ]
				}

			}
 ],
		"originid" : "pat-1089"
	}

}
