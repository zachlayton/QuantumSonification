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
		"rect" : [ 200.0, 100.0, 1001.0, 810.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-4",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 653.0, 526.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-2",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 575.0, 541.0, 34.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 17.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 18.0, 850.0, 25.0 ],
					"text" : "QMW Density Matrix → CNMAT Resonant Body v1"
				}

			}
, 			{
				"box" : 				{
					"id" : "subtitle",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 48.0, 930.0, 20.0 ],
					"text" : "The canonical engine tunes 256 CNMAT resonances on UDP 7400. QTM v1 density-clock pulses on the same QMW bus excite the stored body independently."
				}

			}
, 			{
				"box" : 				{
					"id" : "engine_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 100.0, 250.0, 20.0 ],
					"text" : "MODEL — canonical QMW engine"
				}

			}
, 			{
				"box" : 				{
					"id" : "engine_udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 25.0, 126.0, 112.0, 22.0 ],
					"text" : "udpreceive 7400"
				}

			}
, 			{
				"box" : 				{
					"id" : "engine_qmw",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 150.0, 126.0, 104.0, 22.0 ],
					"text" : "OSC-route /qmw"
				}

			}
, 			{
				"box" : 				{
					"id" : "engine_cnmat",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 267.0, 126.0, 118.0, 22.0 ],
					"text" : "OSC-route /cnmat"
				}

			}
, 			{
				"box" : 				{
					"id" : "engine_density",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 398.0, 126.0, 190.0, 22.0 ],
					"text" : "OSC-route /density_resonator"
				}

			}
, 			{
				"box" : 				{
					"id" : "engine_route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 5,
					"outlettype" : [ "", "", "", "", "" ],
					"patching_rect" : [ 601.0, 126.0, 216.0, 22.0 ],
					"text" : "OSC-route /begin /row /end /trigger"
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_begin",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 560.0, 166.0, 92.0, 22.0 ],
					"text" : "prepend begin"
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_row",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 662.0, 166.0, 82.0, 22.0 ],
					"text" : "prepend row"
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_end",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 754.0, 166.0, 82.0, 22.0 ],
					"text" : "prepend end"
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_trigger",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 846.0, 166.0, 100.0, 22.0 ],
					"text" : "prepend trigger"
				}

			}
, 			{
				"box" : 				{
					"id" : "qtm_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 214.0, 300.0, 20.0 ],
					"text" : "TRIGGER — QTM v1 intrinsic density clock"
				}

			}
, 			{
				"box" : 				{
					"id" : "qtm_mechanics",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 267.0, 240.0, 188.0, 22.0 ],
					"text" : "OSC-route /temporal-mechanics"
				}

			}
, 			{
				"box" : 				{
					"id" : "qtm_v1",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 468.0, 240.0, 92.0, 22.0 ],
					"text" : "OSC-route /v1"
				}

			}
, 			{
				"box" : 				{
					"id" : "qtm_clock",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 573.0, 240.0, 146.0, 22.0 ],
					"text" : "OSC-route /density-clock"
				}

			}
, 			{
				"box" : 				{
					"id" : "qtm_pulse",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 732.0, 240.0, 102.0, 22.0 ],
					"text" : "OSC-route /pulse"
				}

			}
, 			{
				"box" : 				{
					"id" : "qtm_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 241.0, 220.0, 20.0 ],
					"text" : "arrives on the engine's UDP 7400 bus"
				}

			}
, 			{
				"box" : 				{
					"id" : "js",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 350.0, 320.0, 260.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_cnmat_density_resonator_v1.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_cnmat_density_resonator_v1.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 350.0, 356.0, 460.0, 22.0 ],
					"text" : "set \"model 5071 committed: 256 resonances\""
				}

			}
, 			{
				"box" : 				{
					"id" : "test_button",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 25.0, 319.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "test_message",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 60.0, 320.0, 34.0, 22.0 ],
					"text" : "test"
				}

			}
, 			{
				"box" : 				{
					"id" : "test_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 105.0, 321.0, 185.0, 20.0 ],
					"text" : "local model + impulse test"
				}

			}
, 			{
				"box" : 				{
					"id" : "manual_button",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 25.0, 375.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "manual_amp",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 60.0, 376.0, 38.0, 22.0 ],
					"text" : "0.7"
				}

			}
, 			{
				"box" : 				{
					"id" : "manual_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 108.0, 377.0, 182.0, 20.0 ],
					"text" : "independent manual impulse"
				}

			}
, 			{
				"box" : 				{
					"id" : "click",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 475.0, 416.0, 42.0, 22.0 ],
					"text" : "click~"
				}

			}
, 			{
				"box" : 				{
					"id" : "resonators",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "list" ],
					"patching_rect" : [ 384.0, 462.0, 115.0, 22.0 ],
					"text" : "resonators~ smooth"
				}

			}
, 			{
				"box" : 				{
					"id" : "clear",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 565.0, 430.0, 40.0, 22.0 ],
					"text" : "clear"
				}

			}
, 			{
				"box" : 				{
					"id" : "squelch",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 615.0, 430.0, 54.0, 22.0 ],
					"text" : "squelch"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain",
					"lastchannelcount" : 0,
					"maxclass" : "live.gain~",
					"numinlets" : 2,
					"numoutlets" : 5,
					"outlettype" : [ "signal", "signal", "", "float", "list" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 243.0, 548.0, 96.0, 125.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_longname" : "live.gain~",
							"parameter_mmax" : 6.0,
							"parameter_mmin" : -70.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "live.gain~",
							"parameter_type" : 0,
							"parameter_unitstyle" : 4
						}

					}
,
					"varname" : "live.gain~"
				}

			}
, 			{
				"box" : 				{
					"id" : "dac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 418.0, 674.0, 45.0, 45.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "architecture",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 735.0, 1050.0, 20.0 ],
					"text" : "Tuning does not excite the bank. A complete begin/row/end frame replaces the model atomically; engine events, QTM resonance relations, and the manual button are independent impulse sources."
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "resonators", 0 ],
					"source" : [ "clear", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "resonators", 0 ],
					"source" : [ "click", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "engine_density", 0 ],
					"source" : [ "engine_cnmat", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "engine_route", 0 ],
					"source" : [ "engine_density", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "engine_cnmat", 0 ],
					"order" : 1,
					"source" : [ "engine_qmw", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qtm_mechanics", 0 ],
					"order" : 0,
					"source" : [ "engine_qmw", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_begin", 0 ],
					"source" : [ "engine_route", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_end", 0 ],
					"source" : [ "engine_route", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_row", 0 ],
					"source" : [ "engine_route", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_trigger", 0 ],
					"source" : [ "engine_route", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "engine_qmw", 0 ],
					"source" : [ "engine_udp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 1 ],
					"source" : [ "gain", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"source" : [ "gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "click", 0 ],
					"source" : [ "js", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "resonators", 0 ],
					"source" : [ "js", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 1 ],
					"source" : [ "js", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "click", 0 ],
					"source" : [ "manual_amp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "manual_amp", 0 ],
					"source" : [ "manual_button", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain", 1 ],
					"order" : 0,
					"source" : [ "obj-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain", 0 ],
					"order" : 1,
					"source" : [ "obj-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 1 ],
					"source" : [ "obj-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "js", 0 ],
					"source" : [ "prepend_begin", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "js", 0 ],
					"source" : [ "prepend_end", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "js", 0 ],
					"source" : [ "prepend_row", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "js", 0 ],
					"source" : [ "prepend_trigger", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qtm_pulse", 0 ],
					"source" : [ "qtm_clock", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qtm_v1", 0 ],
					"source" : [ "qtm_mechanics", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "js", 1 ],
					"source" : [ "qtm_pulse", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qtm_clock", 0 ],
					"source" : [ "qtm_v1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"source" : [ "resonators", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "resonators", 0 ],
					"source" : [ "squelch", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "test_message", 0 ],
					"source" : [ "test_button", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "js", 0 ],
					"source" : [ "test_message", 0 ]
				}

			}
 ],
		"originid" : "pat-32",
		"parameters" : 		{
			"gain" : [ "live.gain~", "live.gain~", 0 ],
			"parameterbanks" : 			{
				"0" : 				{
					"index" : 0,
					"name" : "",
					"parameters" : [ "-", "-", "-", "-", "-", "-", "-", "-" ]
				}

			}
,
			"inherited_shortname" : 1
		}
,
		"dependency_cache" : [ 			{
				"name" : "OSC-route.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "qmw_cnmat_density_resonator_v1.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "resonators~.mxo",
				"type" : "iLaX"
			}
 ],
		"autosave" : 0
	}

}
