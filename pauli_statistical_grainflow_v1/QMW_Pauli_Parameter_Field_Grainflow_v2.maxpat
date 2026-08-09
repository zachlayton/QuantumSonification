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
		"rect" : [ 134.0, 100.0, 1110.0, 816.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-2",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 498.0, 76.0, 33.0, 22.0 ],
					"text" : "read"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 18.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 14.0, 1160.0, 27.0 ],
					"text" : "QMW PAULI PARAMETER-FIELD GRAINFLOW v2 — 6 STREAMS × 4 GRAINS"
				}

			}
, 			{
				"box" : 				{
					"id" : "subtitle",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 45.0, 1150.0, 20.0 ],
					"text" : "Twenty-four stable slots preserve stream and grain identity. Statistics determines occupation; the energy shell determines rate; coherence and entropy determine temporal order versus randomized lookup."
				}

			}
, 			{
				"box" : 				{
					"id" : "source",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 20.0, 95.0, 390.0, 22.0 ],
					"text" : "buffer~ qmw_pauli_source CP_Bubbling_Pasta_Sauce.wav"
				}

			}
, 			{
				"box" : 				{
					"id" : "rates_buf",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 20.0, 128.0, 290.0, 22.0 ],
					"text" : "buffer~ qmw_pauli_rates @samps 25"
				}

			}
, 			{
				"box" : 				{
					"id" : "delays_buf",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 325.0, 128.0, 290.0, 22.0 ],
					"text" : "buffer~ qmw_pauli_delays @samps 25"
				}

			}
, 			{
				"box" : 				{
					"id" : "windows_buf",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 630.0, 128.0, 300.0, 22.0 ],
					"text" : "buffer~ qmw_pauli_windows @samps 25"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "clock",
					"maxclass" : "flonum",
					"maximum" : 100.0,
					"minimum" : 0.1,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 20.0, 180.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "clock_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 100.0, 183.0, 72.0, 20.0 ],
					"text" : "clock Hz"
				}

			}
, 			{
				"box" : 				{
					"id" : "clock_sig",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 180.0, 180.0, 88.0, 22.0 ],
					"text" : "phasor~ 7."
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "scan",
					"maxclass" : "flonum",
					"maximum" : 4.0,
					"minimum" : -4.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 290.0, 180.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "scan_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 370.0, 183.0, 65.0, 20.0 ],
					"text" : "scan Hz"
				}

			}
, 			{
				"box" : 				{
					"id" : "scan_sig",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 445.0, 180.0, 88.0, 22.0 ],
					"text" : "phasor~ 0.1"
				}

			}
, 			{
				"box" : 				{
					"id" : "scalar_rate",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 550.0, 180.0, 62.0, 22.0 ],
					"text" : "sig~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "enable",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 635.0, 179.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "enable_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 667.0, 183.0, 62.0, 20.0 ],
					"text" : "enable"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode",
					"items" : [ "0 scalar", ",", "1 deterministic slots", ",", "2 random lookup" ],
					"maxclass" : "umenu",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "int", "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 750.0, 180.0, 205.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 970.0, 180.0, 92.0, 22.0 ],
					"text" : "prepend mode"
				}

			}
, 			{
				"box" : 				{
					"id" : "grain",
					"maxclass" : "newobj",
					"numinlets" : 4,
					"numoutlets" : 9,
					"outlettype" : [ "multichannelsignal", "list", "multichannelsignal", "multichannelsignal", "multichannelsignal", "multichannelsignal", "multichannelsignal", "multichannelsignal", "multichannelsignal" ],
					"patching_rect" : [ 20.0, 225.0, 330.0, 22.0 ],
					"text" : "grainflow~ qmw_pauli_source 24 grainflow.Hanning.aif"
				}

			}
, 			{
				"box" : 				{
					"id" : "amp_mc",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 370.0, 225.0, 135.0, 22.0 ],
					"text" : "mc.sig~ 0. @chans 24"
				}

			}
, 			{
				"box" : 				{
					"id" : "amp_smooth",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 520.0, 225.0, 115.0, 22.0 ],
					"text" : "mc.slide~ 80 80"
				}

			}
, 			{
				"box" : 				{
					"id" : "pan",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "multichannelsignal", "list" ],
					"patching_rect" : [ 20.0, 265.0, 190.0, 22.0 ],
					"text" : "grainflow.util.stereoPan~"
				}

			}
, 			{
				"box" : 				{
					"id" : "unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 20.0, 305.0, 92.0, 22.0 ],
					"text" : "mc.unpack~ 2"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain_l",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 20.0, 342.0, 55.0, 22.0 ],
					"text" : "*~ 0.24"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain_r",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 125.0, 342.0, 55.0, 22.0 ],
					"text" : "*~ 0.24"
				}

			}
, 			{
				"box" : 				{
					"id" : "dac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 220.0, 325.0, 52.0, 52.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "metadata",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 370.0, 265.0, 650.0, 22.0 ],
					"text" : "grainInfo dictionary u150003490"
				}

			}
, 			{
				"box" : 				{
					"id" : "writer",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 8,
					"outlettype" : [ "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 20.0, 405.0, 275.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_pauli_parameter_field_v2.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_pauli_parameter_field_v2.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 315.0, 405.0, 755.0, 22.0 ],
					"text" : "set \"PAULI 24-SLOT FIELD\" SODIUM_D2 BOSON N=2 occupation=2/0/0/0/0/0 mode=0"
				}

			}
, 			{
				"box" : 				{
					"id" : "preset",
					"items" : [ "normal", ",", "sodium_d1", ",", "sodium_d2" ],
					"maxclass" : "umenu",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "int", "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 20.0, 465.0, 135.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "preset_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 165.0, 465.0, 102.0, 22.0 ],
					"text" : "prepend preset"
				}

			}
, 			{
				"box" : 				{
					"id" : "stats",
					"items" : [ "fermion", ",", "boson", ",", "classical" ],
					"maxclass" : "umenu",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "int", "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 285.0, 465.0, 120.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "stats_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 415.0, 465.0, 115.0, 22.0 ],
					"text" : "prepend statistics"
				}

			}
, 			{
				"box" : 				{
					"id" : "particles",
					"maxclass" : "number",
					"maximum" : 16,
					"minimum" : 0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 550.0, 465.0, 55.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "particles_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 615.0, 465.0, 110.0, 22.0 ],
					"text" : "prepend particles"
				}

			}
, 			{
				"box" : 				{
					"id" : "resample",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 745.0, 464.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "resample_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 777.0, 468.0, 155.0, 20.0 ],
					"text" : "sample occupation"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "field",
					"maxclass" : "flonum",
					"maximum" : 20.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 20.0, 505.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "field_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 95.0, 505.0, 88.0, 22.0 ],
					"text" : "prepend field"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "center",
					"maxclass" : "flonum",
					"maximum" : 20.0,
					"minimum" : -20.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 200.0, 505.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "center_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 275.0, 505.0, 95.0, 22.0 ],
					"text" : "prepend center"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "width",
					"maxclass" : "flonum",
					"maximum" : 40.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 390.0, 505.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "width_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 465.0, 505.0, 92.0, 22.0 ],
					"text" : "prepend width"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "entropy",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 580.0, 505.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "entropy_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 655.0, 505.0, 102.0, 22.0 ],
					"text" : "prepend entropy"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "coherence",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 780.0, 505.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "coherence_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 855.0, 505.0, 112.0, 22.0 ],
					"text" : "prepend coherence"
				}

			}
, 			{
				"box" : 				{
					"id" : "occupation",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 20.0, 555.0, 1050.0, 42.0 ],
					"setminmax" : [ 0.0, 8.0 ],
					"size" : 6
				}

			}
, 			{
				"box" : 				{
					"id" : "rate_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 620.0, 346.0, 20.0 ],
					"text" : "24 RATE SLOTS — stream energy plus within-stream deviation"
				}

			}
, 			{
				"box" : 				{
					"id" : "rate_view",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 20.0, 642.0, 500.0, 48.0 ],
					"setminmax" : [ 0.125, 8.0 ],
					"size" : 24
				}

			}
, 			{
				"box" : 				{
					"id" : "delay_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 550.0, 620.0, 300.0, 20.0 ],
					"text" : "24 DELAY SLOTS — shell phase positions"
				}

			}
, 			{
				"box" : 				{
					"id" : "delay_view",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 550.0, 642.0, 500.0, 48.0 ],
					"setminmax" : [ -5588.0, 0.0 ],
					"size" : 24
				}

			}
, 			{
				"box" : 				{
					"id" : "window_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 710.0, 300.0, 20.0 ],
					"text" : "24 WINDOW-OFFSET SLOTS"
				}

			}
, 			{
				"box" : 				{
					"id" : "window_view",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 20.0, 732.0, 500.0, 48.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"size" : 24
				}

			}
, 			{
				"box" : 				{
					"id" : "amp_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 550.0, 710.0, 330.0, 20.0 ],
					"text" : "24 AMPLITUDE SLOTS — occupation weights"
				}

			}
, 			{
				"box" : 				{
					"id" : "amp_view",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 550.0, 732.0, 500.0, 48.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"size" : 24
				}

			}
, 			{
				"box" : 				{
					"id" : "init_clock",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 20.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 7."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_scan",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 106.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 0.1"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_enable",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 192.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_mode",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 278.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_preset",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 364.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 0"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_stats",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 450.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 0"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_particles",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 536.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 2"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_field",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 622.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_center",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 708.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_width",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 794.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 4."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_entropy",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 880.0, 820.0, 87.0, 22.0 ],
					"text" : "loadmess 0.25"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_coherence",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 966.0, 820.0, 80.0, 22.0 ],
					"text" : "loadmess 0.8"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "amp_smooth", 0 ],
					"source" : [ "amp_mc", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "grain", 3 ],
					"source" : [ "amp_smooth", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "center_pre", 0 ],
					"source" : [ "center", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "writer", 0 ],
					"source" : [ "center_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "clock_sig", 0 ],
					"source" : [ "clock", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "grain", 0 ],
					"source" : [ "clock_sig", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "coherence_pre", 0 ],
					"source" : [ "coherence", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "writer", 0 ],
					"source" : [ "coherence_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "grain", 0 ],
					"source" : [ "enable", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "entropy_pre", 0 ],
					"source" : [ "entropy", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "writer", 0 ],
					"source" : [ "entropy_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "field_pre", 0 ],
					"source" : [ "field", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "writer", 0 ],
					"source" : [ "field_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"source" : [ "gain_l", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 1 ],
					"source" : [ "gain_r", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "metadata", 1 ],
					"source" : [ "grain", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "pan", 1 ],
					"source" : [ "grain", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "pan", 0 ],
					"source" : [ "grain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "center", 0 ],
					"source" : [ "init_center", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "clock", 0 ],
					"source" : [ "init_clock", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "coherence", 0 ],
					"source" : [ "init_coherence", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "enable", 0 ],
					"source" : [ "init_enable", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "entropy", 0 ],
					"source" : [ "init_entropy", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "field", 0 ],
					"source" : [ "init_field", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode", 0 ],
					"source" : [ "init_mode", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "particles", 0 ],
					"source" : [ "init_particles", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "preset", 0 ],
					"source" : [ "init_preset", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scan", 0 ],
					"source" : [ "init_scan", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "stats", 0 ],
					"source" : [ "init_stats", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "width", 0 ],
					"source" : [ "init_width", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_pre", 0 ],
					"source" : [ "mode", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "writer", 0 ],
					"source" : [ "mode_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "source", 0 ],
					"source" : [ "obj-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "unpack", 0 ],
					"source" : [ "pan", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "particles_pre", 0 ],
					"source" : [ "particles", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "writer", 0 ],
					"source" : [ "particles_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "preset_pre", 0 ],
					"source" : [ "preset", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "writer", 0 ],
					"source" : [ "preset_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "writer", 0 ],
					"source" : [ "resample", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "grain", 2 ],
					"source" : [ "scalar_rate", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scan_sig", 0 ],
					"source" : [ "scan", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "grain", 1 ],
					"source" : [ "scan_sig", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "stats_pre", 0 ],
					"source" : [ "stats", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "writer", 0 ],
					"source" : [ "stats_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain_l", 0 ],
					"source" : [ "unpack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain_r", 0 ],
					"source" : [ "unpack", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "width_pre", 0 ],
					"source" : [ "width", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "writer", 0 ],
					"source" : [ "width_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "amp_mc", 0 ],
					"source" : [ "writer", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "amp_view", 0 ],
					"source" : [ "writer", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "delay_view", 0 ],
					"source" : [ "writer", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "grain", 0 ],
					"source" : [ "writer", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "occupation", 0 ],
					"source" : [ "writer", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rate_view", 0 ],
					"source" : [ "writer", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 1 ],
					"source" : [ "writer", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "window_view", 0 ],
					"source" : [ "writer", 2 ]
				}

			}
 ],
		"originid" : "pat-78",
		"dependency_cache" : [ 			{
				"name" : "grainflow.util.stereopan~.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "grainflow~.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "qmw_pauli_parameter_field_v2.js",
				"bootpath" : "~/QuantumSonification/pauli_statistical_grainflow_v1",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
