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
		"rect" : [ 131.0, 136.0, 920.0, 480.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 743.0, 287.0, 32.0, 22.0 ],
					"text" : "print"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-4",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 689.0, 287.0, 32.0, 22.0 ],
					"text" : "print"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-3",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 700.0, 257.0, 125.0, 22.0 ],
					"text" : "OSC-route /qac /state"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-2",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 704.0, 220.0, 98.0, 22.0 ],
					"text" : "OSC-route /qmw"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-1",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 626.0, 189.0, 97.0, 22.0 ],
					"text" : "udpreceive 7410"
				}

			}
, 			{
				"box" : 				{
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 35.0, 25.0, 520.0, 20.0 ],
					"text" : "QAC 1.0.4 → QuantumSonification: four-qubit Bell smoke test"
				}

			}
, 			{
				"box" : 				{
					"id" : "note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 35.0, 52.0, 760.0, 20.0 ],
					"text" : "Requires The QAC Toolkit in Documents/Max 9/Packages and the Python bridge listening on UDP 7401."
				}

			}
, 			{
				"box" : 				{
					"id" : "bell",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 35.0, 105.0, 465.0, 22.0 ],
					"text" : "QuantumCircuit qc 4 4, qc h 0, qc cx 0 1, Simulator sim qc 1024"
				}

			}
, 			{
				"box" : 				{
					"id" : "bell-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 510.0, 106.0, 210.0, 20.0 ],
					"text" : "1. reset/create Bell circuit"
				}

			}
, 			{
				"box" : 				{
					"id" : "get",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 35.0, 145.0, 100.0, 22.0 ],
					"text" : "sim get_qasm"
				}

			}
, 			{
				"box" : 				{
					"id" : "get-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 145.0, 146.0, 280.0, 20.0 ],
					"text" : "2. export QASM through the QAC outlet"
				}

			}
, 			{
				"box" : 				{
					"id" : "state",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 35.0, 185.0, 135.0, 22.0 ],
					"text" : "sim get_statevector"
				}

			}
, 			{
				"box" : 				{
					"id" : "state-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 180.0, 186.0, 255.0, 20.0 ],
					"text" : "optional: compare QAC's local preview"
				}

			}
, 			{
				"box" : 				{
					"id" : "qac",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 35.0, 240.0, 235.0, 22.0 ],
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
					"patching_rect" : [ 35.0, 285.0, 40.0, 22.0 ],
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
					"patching_rect" : [ 35.0, 330.0, 235.0, 22.0 ],
					"text" : "qac_quantumsonification_sender_v1"
				}

			}
, 			{
				"box" : 				{
					"id" : "qac-print",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 110.0, 285.0, 95.0, 22.0 ],
					"text" : "print QAC_OUT"
				}

			}
, 			{
				"box" : 				{
					"id" : "status-print",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 35.0, 375.0, 136.0, 22.0 ],
					"text" : "print QAC_BRIDGE_TX"
				}

			}
, 			{
				"box" : 				{
					"id" : "monitor",
					"maxclass" : "newobj",
					"numinlets" : 0,
					"numoutlets" : 0,
					"patching_rect" : [ 360.0, 330.0, 235.0, 22.0 ],
					"text" : "qac_quantumsonification_monitor_v1"
				}

			}
, 			{
				"box" : 				{
					"id" : "monitor-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 610.0, 331.0, 290.0, 20.0 ],
					"text" : "Python results are printed by this monitor abstraction"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "qac", 0 ],
					"source" : [ "bell", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qac", 0 ],
					"source" : [ "get", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"source" : [ "obj-1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-3", 0 ],
					"source" : [ "obj-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-4", 0 ],
					"source" : [ "obj-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-5", 0 ],
					"source" : [ "obj-3", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tee", 0 ],
					"source" : [ "qac", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status-print", 0 ],
					"source" : [ "sender", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qac", 0 ],
					"source" : [ "state", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sender", 0 ],
					"source" : [ "tee", 0 ]
				}

			}
 ],
		"originid" : "pat-1085",
		"dependency_cache" : [ 			{
				"name" : "OSC-route.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "o.pack.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "och.microqiskit.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "qac_qasm_sender_v1.js",
				"bootpath" : "~/QuantumSonification/qac_quantumsonification_bridge_v1/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qac_quantumsonification_monitor_v1.maxpat",
				"bootpath" : "~/QuantumSonification/qac_quantumsonification_bridge_v1/max",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
			}
, 			{
				"name" : "qac_quantumsonification_sender_v1.maxpat",
				"bootpath" : "~/QuantumSonification/qac_quantumsonification_bridge_v1/max",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
