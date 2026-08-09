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
		"rect" : [ 134.0, 172.0, 820.0, 440.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"comment" : "QASM from och.microqiskit get_qasm",
					"id" : "in-qasm",
					"index" : 1,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 48.0, 47.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "comment-in",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 91.0, 52.0, 300.0, 20.0 ],
					"text" : "Connect the QASM outlet from och.microqiskit here"
				}

			}
, 			{
				"box" : 				{
					"id" : "js",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 48.0, 112.0, 167.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qac_qasm_sender_v1.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qac_qasm_sender_v1.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "osc-begin",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 48.0, 182.0, 138.0, 22.0 ],
					"text" : "o.pack /qmw/qac/begin"
				}

			}
, 			{
				"box" : 				{
					"id" : "osc-chunk",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 224.0, 182.0, 141.0, 22.0 ],
					"text" : "o.pack /qmw/qac/chunk"
				}

			}
, 			{
				"box" : 				{
					"id" : "osc-end",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 403.0, 182.0, 129.0, 22.0 ],
					"text" : "o.pack /qmw/qac/end"
				}

			}
, 			{
				"box" : 				{
					"id" : "udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 224.0, 252.0, 157.0, 22.0 ],
					"text" : "udpsend 127.0.0.1 7401"
				}

			}
, 			{
				"box" : 				{
					"comment" : "sender status",
					"id" : "status",
					"index" : 1,
					"maxclass" : "outlet",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 590.0, 250.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "comment-port",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 224.0, 290.0, 220.0, 20.0 ],
					"text" : "QAC circuit score → Python bridge"
				}

			}
, 			{
				"box" : 				{
					"id" : "comment-status",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 628.0, 255.0, 60.0, 20.0 ],
					"text" : "status"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "js", 0 ],
					"source" : [ "in-qasm", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "osc-begin", 0 ],
					"source" : [ "js", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "osc-chunk", 0 ],
					"source" : [ "js", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "osc-end", 0 ],
					"source" : [ "js", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 0 ],
					"source" : [ "js", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "udp", 0 ],
					"source" : [ "osc-begin", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "udp", 0 ],
					"source" : [ "osc-chunk", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "udp", 0 ],
					"source" : [ "osc-end", 0 ]
				}

			}
 ],
		"originid" : "pat-1087"
	}

}
