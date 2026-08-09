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
		"rect" : [ 79.0, 104.0, 821.0, 459.0 ],
		"openinpresentation" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 18.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 18.0, 700.0, 27.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 25.0, 18.0, 700.0, 27.0 ],
					"text" : "QMW QAC/QASM CIRCUIT PROGRAMMER v1",
					"textcolor" : [ 0.9, 0.93, 0.97, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"filename" : "qmw_qac_circuit_programmer_v1.js",
					"id" : "ui",
					"jsarguments" : [ "qmw_qac_circuit_programmer_v1.js" ],
					"maxclass" : "jsui",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 25.0, 55.0, 780.0, 390.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 25.0, 55.0, 780.0, 390.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "status_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 458.0, 70.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 25.0, 458.0, 70.0, 20.0 ],
					"text" : "STATUS",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 95.0, 455.0, 520.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 95.0, 455.0, 520.0, 22.0 ],
					"text" : "\"sent 9 gates → QASM bridge\""
				}

			}
, 			{
				"box" : 				{
					"id" : "qac",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 25.0, 490.0, 235.0, 22.0 ],
					"text" : "och.microqiskit qc 4 4 sim 1024 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "tee",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 280.0, 490.0, 40.0, 22.0 ],
					"text" : "t l l"
				}

			}
, 			{
				"box" : 				{
					"id" : "sender",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 340.0, 490.0, 235.0, 22.0 ],
					"text" : "qac_quantumsonification_sender_v1"
				}

			}
, 			{
				"box" : 				{
					"id" : "qac_print",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 590.0, 490.0, 95.0, 22.0 ],
					"text" : "print QAC_OUT"
				}

			}
, 			{
				"box" : 				{
					"id" : "tx_print",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 700.0, 490.0, 136.0, 22.0 ],
					"text" : "print QAC_BRIDGE_TX"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "tee", 0 ],
					"source" : [ "qac", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tx_print", 0 ],
					"source" : [ "sender", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qac_print", 0 ],
					"source" : [ "tee", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sender", 0 ],
					"source" : [ "tee", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qac", 0 ],
					"source" : [ "ui", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 0 ],
					"source" : [ "ui", 1 ]
				}

			}
 ],
		"originid" : "pat-37",
		"dependency_cache" : [ 			{
				"name" : "o.pack.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "och.microqiskit.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "qac_qasm_sender_v1.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qac_quantumsonification_sender_v1.maxpat",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_qac_circuit_programmer_v1.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
