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
		"rect" : [ 56.0, 102.0, 1378.0, 730.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "ctl-label",
					"maxclass" : "comment",
					"patching_rect" : [ 760.0, 20.0, 410.0, 20.0 ],
					"text" : "TIMBRE                              SPATIAL REVERB"
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-blend-label",
					"maxclass" : "comment",
					"patching_rect" : [ 760.0, 55.0, 150.0, 20.0 ],
					"text" : "spectral  ←→  spatial"
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-blend",
					"maxclass" : "flonum",
					"minimum" : 0.0,
					"maximum" : 1.0,
					"patching_rect" : [ 760.0, 78.0, 62.0, 22.0 ]
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-blend-msg",
					"maxclass" : "newobj",
					"patching_rect" : [ 830.0, 78.0, 145.0, 22.0 ],
					"text" : "prepend spectral_spatial"
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-detail-label",
					"maxclass" : "comment",
					"patching_rect" : [ 760.0, 110.0, 75.0, 20.0 ],
					"text" : "detail"
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-detail",
					"maxclass" : "flonum",
					"minimum" : 0.0,
					"maximum" : 1.0,
					"patching_rect" : [ 760.0, 132.0, 62.0, 22.0 ]
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-detail-msg",
					"maxclass" : "newobj",
					"patching_rect" : [ 830.0, 132.0, 88.0, 22.0 ],
					"text" : "prepend detail"
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-revmix-label",
					"maxclass" : "comment",
					"patching_rect" : [ 1030.0, 55.0, 100.0, 20.0 ],
					"text" : "spatial mix"
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-revmix",
					"maxclass" : "flonum",
					"minimum" : 0.0,
					"maximum" : 1.0,
					"patching_rect" : [ 1030.0, 78.0, 62.0, 22.0 ]
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-decay-label",
					"maxclass" : "comment",
					"patching_rect" : [ 1120.0, 55.0, 70.0, 20.0 ],
					"text" : "decay"
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-decay",
					"maxclass" : "flonum",
					"minimum" : 0.0,
					"maximum" : 1.0,
					"patching_rect" : [ 1120.0, 78.0, 62.0, 22.0 ]
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-load-blend",
					"maxclass" : "newobj",
					"patching_rect" : [ 760.0, 165.0, 88.0, 22.0 ],
					"text" : "loadmess 0.22"
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-load-detail",
					"maxclass" : "newobj",
					"patching_rect" : [ 855.0, 165.0, 88.0, 22.0 ],
					"text" : "loadmess 0.15"
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-load-revmix",
					"maxclass" : "newobj",
					"patching_rect" : [ 1030.0, 120.0, 88.0, 22.0 ],
					"text" : "loadmess 0.24"
				}
			}
, 			{
				"box" : 				{
					"id" : "ctl-load-decay",
					"maxclass" : "newobj",
					"patching_rect" : [ 1120.0, 120.0, 88.0, 22.0 ],
					"text" : "loadmess 0.58"
				}
			}
, 			{
				"box" : 				{
					"id" : "spatial-reverb",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 350.0, 445.0, 205.0, 22.0 ],
					"text" : "QMW_Hybrid_Spatial_Reverb"
				}
			}
, 			{
				"box" : 				{
					"id" : "convolution-label",
					"maxclass" : "comment",
					"linecount" : 2,
					"patching_rect" : [ 760.0, 215.0, 405.0, 38.0 ],
					"text" : "LIVING CONVOLUTION ENGINE\nDouble-click the module to open IR slots, morphing, and activation status."
				}
			}
, 			{
				"box" : 				{
					"id" : "convolution-engine",
					"maxclass" : "newobj",
					"numinlets" : 0,
					"numoutlets" : 0,
					"patching_rect" : [ 760.0, 265.0, 225.0, 22.0 ],
					"text" : "QMW_Operator_Ecology_Lab_v1"
				}
			}
, 			{
				"box" : 				{
					"id" : "convolution-send-l",
					"maxclass" : "newobj",
					"patching_rect" : [ 760.0, 315.0, 145.0, 22.0 ],
					"text" : "send~ qmw_spectral_L"
				}
			}
, 			{
				"box" : 				{
					"id" : "convolution-send-r",
					"maxclass" : "newobj",
					"patching_rect" : [ 920.0, 315.0, 145.0, 22.0 ],
					"text" : "send~ qmw_spectral_R"
				}
			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-15",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 379.0, 174.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-13",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 337.0, 211.0, 81.0, 22.0 ],
					"text" : "smoothing $1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-6",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 475.0, 237.0, 97.0, 22.0 ],
					"text" : "prepend weights"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-5",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 599.0, 155.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-4",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 542.0, 155.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-3",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 486.0, 155.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-1",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 477.0, 195.0, 68.0, 22.0 ],
					"text" : "pak 0. 0. 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 35.0, 20.0, 430.0, 20.0 ],
					"text" : "QMW Hybrid Wavetable 256 — OSC audition patch (port 7400)"
				}

			}
, 			{
				"box" : 				{
					"id" : "udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 35.0, 115.0, 102.0, 22.0 ],
					"text" : "udpreceive 7400"
				}

			}
, 			{
				"box" : 				{
					"id" : "qmw",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 35.0, 166.0, 100.0, 22.0 ],
					"text" : "OSC-route /qmw"
				}

			}
, 			{
				"box" : 				{
					"id" : "density",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 35.0, 195.0, 145.0, 22.0 ],
					"text" : "OSC-route /density_field"
				}

			}
, 			{
				"box" : 				{
					"id" : "fields",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 10,
					"outlettype" : [ "", "", "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 35.0, 243.0, 410.0, 22.0 ],
					"text" : "OSC-route /x /y /vx /vy /speed /real /imag /magnitude /phase"
				}

			}
, 			{
				"box" : 				{
					"id" : "hybrid",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 2,
					"outlettype" : [ "", "signal" ],
					"patching_rect" : [ 350.0, 330.0, 225.0, 22.0 ],
					"text" : "QMW_Hybrid_Wavetable256"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "freq",
					"maxclass" : "flonum",
					"maximum" : 2000.0,
					"minimum" : 10.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 655.0, 235.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "load",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 655.0, 195.0, 82.0, 22.0 ],
					"text" : "loadmess 55."
				}

			}
, 			{
				"box" : 				{
					"id" : "gain",
					"maxclass" : "gain~",
					"multichannelvariant" : 0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 350.0, 395.0, 120.0, 28.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "dac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 350.0, 470.0, 45.0, 45.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 73.0, 374.0, 260.0, 22.0 ],
					"text" : "rendered qmw_hybrid_table_B 256 0.016561"
				}

			}
, 			{
				"box" : 				{
					"id" : "tip",
					"linecount" : 3,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 35.0, 530.0, 610.0, 47.0 ],
					"text" : "Start with low gain. Adjust the frequency, then audition renderer messages by sending\nweights 0.8 0.15 0.05 (spectral) or weights 0.25 0.65 0.10 (contour)\nto inlet 1 of the abstraction."
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "fields", 0 ],
					"source" : [ "density", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "hybrid", 3 ],
					"source" : [ "fields", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "hybrid", 2 ],
					"source" : [ "fields", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "hybrid", 1 ],
					"source" : [ "fields", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "hybrid", 0 ],
					"source" : [ "fields", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "hybrid", 4 ],
					"source" : [ "fields", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "hybrid", 5 ],
					"source" : [ "freq", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spatial-reverb", 0 ],
					"order" : 0,
					"source" : [ "gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain", 0 ],
					"source" : [ "hybrid", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "convolution-send-l", 0 ],
					"source" : [ "gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "convolution-send-r", 0 ],
					"source" : [ "gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 1 ],
					"source" : [ "hybrid", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "freq", 0 ],
					"source" : [ "load", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-6", 0 ],
					"source" : [ "obj-1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "hybrid", 0 ],
					"source" : [ "obj-13", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-15", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 0 ],
					"source" : [ "obj-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 1 ],
					"source" : [ "obj-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 2 ],
					"source" : [ "obj-5", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "hybrid", 0 ],
					"source" : [ "obj-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ctl-blend-msg", 0 ],
					"source" : [ "ctl-blend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "hybrid", 0 ],
					"source" : [ "ctl-blend-msg", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ctl-detail-msg", 0 ],
					"source" : [ "ctl-detail", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "hybrid", 0 ],
					"source" : [ "ctl-detail-msg", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ctl-blend", 0 ],
					"source" : [ "ctl-load-blend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ctl-detail", 0 ],
					"source" : [ "ctl-load-detail", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ctl-revmix", 0 ],
					"source" : [ "ctl-load-revmix", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ctl-decay", 0 ],
					"source" : [ "ctl-load-decay", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spatial-reverb", 1 ],
					"source" : [ "ctl-revmix", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spatial-reverb", 2 ],
					"source" : [ "ctl-decay", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"source" : [ "spatial-reverb", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 1 ],
					"source" : [ "spatial-reverb", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "density", 0 ],
					"source" : [ "qmw", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qmw", 0 ],
					"source" : [ "udp", 0 ]
				}

			}
 ],
		"originid" : "pat-6",
		"parameters" : 		{
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
				"name" : "QMW_Operator_Ecology_Lab_v1.maxpat",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : "..",
				"type" : "JSON",
				"implicit" : 1
			}
, 			{
				"name" : "OSC-route.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "QMW_Hybrid_Wavetable256.maxpat",
				"bootpath" : "~/QuantumSonification/max/patches",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_hybrid_wavetable_renderer.js",
				"bootpath" : "~/QuantumSonification/max/patches",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
