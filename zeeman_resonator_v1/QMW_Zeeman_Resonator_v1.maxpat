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
		"rect" : [ 38.0, 117.0, 1060.0, 760.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 18.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 18.0, 720.0, 27.0 ],
					"text" : "QMW ZEEMAN RESONATOR — THE TRIPLET BREAKS"
				}

			}
, 			{
				"box" : 				{
					"id" : "subtitle",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 48.0, 971.0, 20.0 ],
					"text" : "A quadrature ring-modulator bank. Lower sidebands move left; upper sidebands move right. The optical scale is perceptually magnified while Landé-factor relationships remain intact."
				}

			}
, 			{
				"box" : 				{
					"id" : "preset_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 102.0, 100.0, 20.0 ],
					"text" : "transition"
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
					"patching_rect" : [ 130.0, 100.0, 190.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "preset_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 335.0, 100.0, 105.0, 22.0 ],
					"text" : "prepend preset"
				}

			}
, 			{
				"box" : 				{
					"id" : "field_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 143.0, 100.0, 20.0 ],
					"text" : "field B (tesla)"
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
					"patching_rect" : [ 130.0, 140.0, 90.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "field_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 235.0, 140.0, 90.0, 22.0 ],
					"text" : "prepend field"
				}

			}
, 			{
				"box" : 				{
					"id" : "sweep_open",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 572.0, 83.0, 112.0, 22.0 ],
					"text" : "0., 5. 12000"
				}

			}
, 			{
				"box" : 				{
					"id" : "sweep_close",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 450.0, 88.0, 112.0, 22.0 ],
					"text" : "5., 0. 12000"
				}

			}
, 			{
				"box" : 				{
					"id" : "sweep_line",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"patching_rect" : [ 585.0, 140.0, 41.0, 22.0 ],
					"text" : "line 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "spread_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 183.0, 100.0, 20.0 ],
					"text" : "audible Hz/T"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "spread",
					"maxclass" : "flonum",
					"maximum" : 1000.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 130.0, 180.0, 90.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "spread_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 235.0, 180.0, 98.0, 22.0 ],
					"text" : "prepend spread"
				}

			}
, 			{
				"box" : 				{
					"id" : "carrier_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 223.0, 100.0, 20.0 ],
					"text" : "carrier Hz"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "carrier",
					"maxclass" : "flonum",
					"maximum" : 12000.0,
					"minimum" : 20.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 130.0, 220.0, 90.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "carrier_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 235.0, 220.0, 102.0, 22.0 ],
					"text" : "prepend carrier"
				}

			}
, 			{
				"box" : 				{
					"id" : "bank_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 263.0, 100.0, 20.0 ],
					"text" : "ring-bank level"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "bank",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 130.0, 260.0, 90.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "bank_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 235.0, 260.0, 96.0, 22.0 ],
					"text" : "prepend bank"
				}

			}
, 			{
				"box" : 				{
					"id" : "dry_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 303.0, 100.0, 20.0 ],
					"text" : "pi carrier level"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "dry",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 130.0, 300.0, 90.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "dry_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 235.0, 300.0, 90.0, 22.0 ],
					"text" : "prepend dry"
				}

			}
, 			{
				"box" : 				{
					"id" : "master_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 343.0, 100.0, 20.0 ],
					"text" : "master level"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "master",
					"maxclass" : "flonum",
					"maximum" : 0.5,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 130.0, 340.0, 90.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "master_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 235.0, 340.0, 75.0, 22.0 ],
					"text" : "pack f 30"
				}

			}
, 			{
				"box" : 				{
					"id" : "master_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 320.0, 340.0, 42.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "controller",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 5,
					"outlettype" : [ "", "", "", "", "" ],
					"patching_rect" : [ 30.0, 395.0, 248.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_zeeman_controller_v1.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_zeeman_controller_v1.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 300.0, 395.0, 720.0, 22.0 ],
					"text" : "set \"ANOMALOUS D2 SEXTET | B=0.000 T | audible scale=10.80 Hz/T | 3 ring voices\""
				}

			}
, 			{
				"box" : 				{
					"id" : "shift_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 438.0, 110.0, 20.0 ],
					"text" : "sideband shifts"
				}

			}
, 			{
				"box" : 				{
					"id" : "shifts",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 145.0, 435.0, 875.0, 44.0 ],
					"setminmax" : [ 0.0, 400.0 ],
					"size" : 8
				}

			}
, 			{
				"box" : 				{
					"id" : "gain_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 492.0, 110.0, 20.0 ],
					"text" : "voice amplitudes"
				}

			}
, 			{
				"box" : 				{
					"id" : "gains",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 145.0, 489.0, 875.0, 44.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"size" : 8
				}

			}
, 			{
				"box" : 				{
					"id" : "poly",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 30.0, 560.0, 305.0, 22.0 ],
					"text" : "poly~ qmw_zeeman_ring_voice_v1 8 @parallel 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "dry_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 365.0, 560.0, 75.0, 22.0 ],
					"text" : "pack f 30"
				}

			}
, 			{
				"box" : 				{
					"id" : "dry_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 450.0, 560.0, 42.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "dry_freq_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 510.0, 560.0, 75.0, 22.0 ],
					"text" : "pack f 30"
				}

			}
, 			{
				"box" : 				{
					"id" : "dry_freq_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 595.0, 560.0, 42.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "dry_cycle",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 655.0, 560.0, 65.0, 22.0 ],
					"text" : "cycle~"
				}

			}
, 			{
				"box" : 				{
					"id" : "dry_gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 735.0, 560.0, 36.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "sum_l",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 145.0, 610.0, 36.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "sum_r",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 255.0, 610.0, 36.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "master_l",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 145.0, 650.0, 36.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "master_r",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 255.0, 650.0, 36.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "clip_l",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 145.0, 685.0, 91.0, 22.0 ],
					"text" : "clip~ -0.95 0.95"
				}

			}
, 			{
				"box" : 				{
					"id" : "clip_r",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 255.0, 685.0, 91.0, 22.0 ],
					"text" : "clip~ -0.95 0.95"
				}

			}
, 			{
				"box" : 				{
					"id" : "meter_l",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 365.0, 620.0, 18.0, 88.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "meter_r",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 395.0, 620.0, 18.0, 88.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "dac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 445.0, 640.0, 52.0, 52.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "spatial_note",
					"linecount" : 4,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 525.0, 622.0, 280.0, 60.0 ],
					"text" : "STEREO FIELD\nLEFT  = sigma- / negative-frequency displacement\nRIGHT = sigma+ / positive-frequency displacement\nThe central pi line is equal in both channels."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_preset",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 700.0, 100.0, 104.0, 22.0 ],
					"text" : "loadmess normal"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_field",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 815.0, 100.0, 88.0, 22.0 ],
					"text" : "loadmess 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_spread",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 915.0, 100.0, 96.0, 22.0 ],
					"text" : "loadmess 40."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_carrier",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 700.0, 140.0, 104.0, 22.0 ],
					"text" : "loadmess 220."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_bank",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 815.0, 140.0, 96.0, 22.0 ],
					"text" : "loadmess 0.42"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_dry",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 915.0, 140.0, 96.0, 22.0 ],
					"text" : "loadmess 0.28"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_master",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 700.0, 180.0, 96.0, 22.0 ],
					"text" : "loadmess 0.18"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "bank_prepend", 0 ],
					"source" : [ "bank", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "bank_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "carrier_prepend", 0 ],
					"order" : 1,
					"source" : [ "carrier", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dry_freq_pack", 0 ],
					"order" : 0,
					"source" : [ "carrier", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "carrier_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"order" : 0,
					"source" : [ "clip_l", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "meter_l", 0 ],
					"order" : 1,
					"source" : [ "clip_l", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 1 ],
					"order" : 0,
					"source" : [ "clip_r", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "meter_r", 0 ],
					"order" : 1,
					"source" : [ "clip_r", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dry_pack", 0 ],
					"source" : [ "controller", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gains", 0 ],
					"source" : [ "controller", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "poly", 0 ],
					"source" : [ "controller", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "shifts", 0 ],
					"source" : [ "controller", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 1 ],
					"source" : [ "controller", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dry_prepend", 0 ],
					"source" : [ "dry", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dry_gain", 0 ],
					"source" : [ "dry_cycle", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dry_cycle", 0 ],
					"source" : [ "dry_freq_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dry_freq_line", 0 ],
					"source" : [ "dry_freq_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_l", 1 ],
					"order" : 1,
					"source" : [ "dry_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_r", 1 ],
					"order" : 0,
					"source" : [ "dry_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dry_gain", 1 ],
					"source" : [ "dry_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dry_line", 0 ],
					"source" : [ "dry_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "dry_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "field_prepend", 0 ],
					"source" : [ "field", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "field_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "bank", 0 ],
					"source" : [ "init_bank", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "carrier", 0 ],
					"source" : [ "init_carrier", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dry", 0 ],
					"source" : [ "init_dry", 0 ]
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
					"destination" : [ "master", 0 ],
					"source" : [ "init_master", 0 ]
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
					"destination" : [ "spread", 0 ],
					"source" : [ "init_spread", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master_pack", 0 ],
					"source" : [ "master", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "clip_l", 0 ],
					"source" : [ "master_l", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master_l", 1 ],
					"order" : 1,
					"source" : [ "master_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master_r", 1 ],
					"order" : 0,
					"source" : [ "master_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master_line", 0 ],
					"source" : [ "master_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "clip_r", 0 ],
					"source" : [ "master_r", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_l", 0 ],
					"source" : [ "poly", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_r", 0 ],
					"source" : [ "poly", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "preset_prepend", 0 ],
					"source" : [ "preset", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "preset_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spread_prepend", 0 ],
					"source" : [ "spread", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "spread_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master_l", 0 ],
					"source" : [ "sum_l", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master_r", 0 ],
					"source" : [ "sum_r", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sweep_line", 0 ],
					"source" : [ "sweep_close", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "field", 0 ],
					"source" : [ "sweep_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sweep_line", 0 ],
					"source" : [ "sweep_open", 0 ]
				}

			}
 ],
		"originid" : "pat-26",
		"dependency_cache" : [ 			{
				"name" : "qmw_zeeman_controller_v1.js",
				"bootpath" : "~/QuantumSonification/zeeman_resonator_v1",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_zeeman_ring_voice_v1.maxpat",
				"bootpath" : "~/QuantumSonification/zeeman_resonator_v1",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
