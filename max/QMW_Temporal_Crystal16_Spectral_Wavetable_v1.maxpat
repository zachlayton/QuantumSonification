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
		"rect" : [ 1091.0, 100.0, 1200.0, 816.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 17.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 18.0, 1030.0, 25.0 ],
					"text" : "QMW Temporal Crystal 16 → Spectral Wavetable v1"
				}

			}
, 			{
				"box" : 				{
					"id" : "subtitle",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 49.0, 1120.0, 20.0 ],
					"text" : "QAC/QFT-style 16-harmonic rendering of canonical rho. Tables stage silently and crossfade only on temporal clicks."
				}

			}
, 			{
				"box" : 				{
					"id" : "port_warning",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 800.0, 18.0, 390.0, 20.0 ],
					"text" : "Close every other Max patch that binds UDP 7400.",
					"textcolor" : [ 0.8, 0.18, 0.12, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 25.0, 106.0, 112.0, 22.0 ],
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
					"patching_rect" : [ 150.0, 106.0, 104.0, 22.0 ],
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
					"patching_rect" : [ 267.0, 106.0, 118.0, 22.0 ],
					"text" : "OSC-route /density"
				}

			}
, 			{
				"box" : 				{
					"id" : "wavetable",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 398.0, 106.0, 132.0, 22.0 ],
					"text" : "OSC-route /wavetable"
				}

			}
, 			{
				"box" : 				{
					"id" : "wavetable_route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 5,
					"outlettype" : [ "", "", "", "", "" ],
					"patching_rect" : [ 543.0, 106.0, 258.0, 22.0 ],
					"text" : "OSC-route /begin /chunk /harmonics /end"
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_begin",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 410.0, 145.0, 92.0, 22.0 ],
					"text" : "prepend begin"
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_chunk",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 512.0, 145.0, 98.0, 22.0 ],
					"text" : "prepend chunk"
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_harmonics",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 620.0, 145.0, 122.0, 22.0 ],
					"text" : "prepend harmonics"
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_end",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 752.0, 145.0, 82.0, 22.0 ],
					"text" : "prepend end"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "mode_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 835.0, 100.0, 340.0, 20.0 ],
					"text" : "LIVE TEMPORAL MODE → Python 7402"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_observer",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 835.0, 126.0, 68.0, 22.0 ],
					"text" : "observer"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_floquet",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 913.0, 126.0, 58.0, 22.0 ],
					"text" : "floquet"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_lfsr",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 981.0, 126.0, 36.0, 22.0 ],
					"text" : "lfsr"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_pythagorean",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1027.0, 126.0, 94.0, 22.0 ],
					"text" : "pythagorean"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 835.0, 166.0, 208.0, 22.0 ],
					"text" : "o.pack /qmw/time/control/mode"
				}

			}
, 			{
				"box" : 				{
					"id" : "control_udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1053.0, 166.0, 142.0, 22.0 ],
					"text" : "udpsend 127.0.0.1 7402"
				}

			}
, 			{
				"box" : 				{
					"id" : "receiver",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 390.0, 205.0, 330.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_temporal_crystal16_spectral_wavetable_v1.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_temporal_crystal16_spectral_wavetable_v1.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 390.0, 238.0, 600.0, 22.0 ],
					"text" : "set \"wavetable 0 committed to qmw_tc_wave_B\""
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
					"patching_rect" : [ 25.0, 204.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "test_message",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 60.0, 205.0, 34.0, 22.0 ],
					"text" : "test"
				}

			}
, 			{
				"box" : 				{
					"id" : "test_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 105.0, 207.0, 235.0, 20.0 ],
					"text" : "local 16-harmonic table + commit"
				}

			}
, 			{
				"box" : 				{
					"id" : "commit_button",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 25.0, 240.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "commit_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 60.0, 242.0, 260.0, 20.0 ],
					"text" : "manual commit of newest staged table"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "waveform_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 285.0, 1120.0, 20.0 ],
					"text" : "CLICK-LATCHED 256-SAMPLE WAVETABLE"
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.1, 0.14, 1.0 ],
					"id" : "waveform",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 25.0, 310.0, 1120.0, 165.0 ],
					"size" : 256,
					"slidercolor" : [ 0.34, 0.78, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "harmonic_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 492.0, 1120.0, 20.0 ],
					"text" : "ENERGY-BASIS HARMONIC AMPLITUDES — sqrt(population), H1…H16"
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.1, 0.14, 1.0 ],
					"id" : "harmonics",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 25.0, 517.0, 1120.0, 90.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"size" : 16,
					"slidercolor" : [ 0.95, 0.58, 0.24, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "time_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 630.0, 500.0, 20.0 ],
					"text" : "TEMPORAL STATE AND CLICK COMMIT"
				}

			}
, 			{
				"box" : 				{
					"id" : "time_root",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 25.0, 657.0, 108.0, 22.0 ],
					"text" : "OSC-route /time"
				}

			}
, 			{
				"box" : 				{
					"id" : "time_route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 8,
					"outlettype" : [ "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 145.0, 657.0, 585.0, 22.0 ],
					"text" : "OSC-route /enabled /mode /rate_hz /protocol /chronos /lfsr /spqt"
				}

			}
, 			{
				"box" : 				{
					"id" : "enabled",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 25.0, 700.0, 55.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "enabled_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 725.0, 70.0, 20.0 ],
					"text" : "ENABLED"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_set",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 95.0, 700.0, 72.0, 22.0 ],
					"text" : "prepend set"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 178.0, 700.0, 110.0, 22.0 ],
					"text" : "floquet"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_value_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 178.0, 725.0, 70.0, 20.0 ],
					"text" : "MODE"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "rate",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 305.0, 700.0, 68.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "rate_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 305.0, 725.0, 75.0, 20.0 ],
					"text" : "RATE Hz"
				}

			}
, 			{
				"box" : 				{
					"id" : "protocol_set",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 390.0, 700.0, 72.0, 22.0 ],
					"text" : "prepend set"
				}

			}
, 			{
				"box" : 				{
					"id" : "protocol",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 475.0, 700.0, 350.0, 22.0 ],
					"text" : "floquet_repeated_single_period_map"
				}

			}
, 			{
				"box" : 				{
					"id" : "chronos",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 25.0, 760.0, 202.0, 22.0 ],
					"text" : "OSC-route /tick /index /phase"
				}

			}
, 			{
				"box" : 				{
					"id" : "tick_dispatch",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "int", "bang" ],
					"patching_rect" : [ 240.0, 760.0, 43.0, 22.0 ],
					"text" : "t i b"
				}

			}
, 			{
				"box" : 				{
					"id" : "tick",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 295.0, 760.0, 62.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "tick_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 295.0, 785.0, 55.0, 20.0 ],
					"text" : "TICK"
				}

			}
, 			{
				"box" : 				{
					"id" : "lfsr",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 385.0, 760.0, 116.0, 22.0 ],
					"text" : "OSC-route /state"
				}

			}
, 			{
				"box" : 				{
					"id" : "lfsr_state",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 515.0, 760.0, 62.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "lfsr_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 515.0, 785.0, 85.0, 20.0 ],
					"text" : "LFSR"
				}

			}
, 			{
				"box" : 				{
					"id" : "spqt",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 615.0, 760.0, 214.0, 22.0 ],
					"text" : "OSC-route /macrocycle_position"
				}

			}
, 			{
				"box" : 				{
					"id" : "spqt_position",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 845.0, 760.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "spqt_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 845.0, 785.0, 90.0, 20.0 ],
					"text" : "SPQT POS"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "audio_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 825.0, 430.0, 20.0 ],
					"text" : "QFT-STYLE DOUBLE-BUFFERED WAVETABLE VOICE"
				}

			}
, 			{
				"box" : 				{
					"id" : "buffer_a",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 25.0, 850.0, 288.0, 22.0 ],
					"text" : "buffer~ qmw_tc_wave_A @samps 256 @channels 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "buffer_b",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 295.0, 850.0, 288.0, 22.0 ],
					"text" : "buffer~ qmw_tc_wave_B @samps 256 @channels 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "fundamental_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 890.0, 125.0, 20.0 ],
					"text" : "FUNDAMENTAL Hz"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "fundamental",
					"maxclass" : "flonum",
					"maximum" : 1000.0,
					"minimum" : 10.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 150.0, 887.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "fundamental_low",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 238.0, 887.0, 42.0, 22.0 ],
					"text" : "27.5"
				}

			}
, 			{
				"box" : 				{
					"id" : "fundamental_mid",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 290.0, 887.0, 30.0, 22.0 ],
					"text" : "55."
				}

			}
, 			{
				"box" : 				{
					"id" : "fundamental_high",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 330.0, 887.0, 38.0, 22.0 ],
					"text" : "110."
				}

			}
, 			{
				"box" : 				{
					"id" : "fundamental_load",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 380.0, 887.0, 92.0, 22.0 ],
					"text" : "loadmess 55."
				}

			}
, 			{
				"box" : 				{
					"id" : "frequency_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 150.0, 920.0, 80.0, 22.0 ],
					"text" : "pack f 80"
				}

			}
, 			{
				"box" : 				{
					"id" : "frequency_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 242.0, 920.0, 42.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "phasor",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 295.0, 920.0, 52.0, 22.0 ],
					"text" : "phasor~"
				}

			}
, 			{
				"box" : 				{
					"id" : "wave_a",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 365.0, 920.0, 146.0, 22.0 ],
					"text" : "wave~ qmw_tc_wave_A"
				}

			}
, 			{
				"box" : 				{
					"id" : "wave_b",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 525.0, 920.0, 146.0, 22.0 ],
					"text" : "wave~ qmw_tc_wave_B"
				}

			}
, 			{
				"box" : 				{
					"id" : "xfade_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 700.0, 850.0, 80.0, 22.0 ],
					"text" : "pack f 50"
				}

			}
, 			{
				"box" : 				{
					"id" : "xfade_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 790.0, 850.0, 42.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "xfade_inverse",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 845.0, 850.0, 55.0, 22.0 ],
					"text" : "!-~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "wave_a_gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 420.0, 960.0, 36.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "wave_b_gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 570.0, 960.0, 36.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "wave_sum",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 500.0, 998.0, 36.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "dcblock",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 500.0, 1033.0, 67.0, 22.0 ],
					"text" : "dcblocker~"
				}

			}
, 			{
				"box" : 				{
					"id" : "safety",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 500.0, 1068.0, 104.0, 22.0 ],
					"text" : "clip~ -0.98 0.98"
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
					"patching_rect" : [ 484.0, 1105.0, 96.0, 125.0 ],
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
					"patching_rect" : [ 493.0, 1240.0, 45.0, 45.0 ]
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "tick_dispatch", 0 ],
					"source" : [ "chronos", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 1 ],
					"source" : [ "commit_button", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "safety", 0 ],
					"source" : [ "dcblock", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wavetable", 0 ],
					"source" : [ "density", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "phasor", 0 ],
					"source" : [ "frequency_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "frequency_line", 0 ],
					"source" : [ "frequency_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "frequency_pack", 0 ],
					"source" : [ "fundamental", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "fundamental", 0 ],
					"source" : [ "fundamental_high", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "fundamental", 0 ],
					"source" : [ "fundamental_load", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "fundamental", 0 ],
					"source" : [ "fundamental_low", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "fundamental", 0 ],
					"source" : [ "fundamental_mid", 0 ]
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
					"destination" : [ "lfsr_state", 0 ],
					"source" : [ "lfsr", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_pack", 0 ],
					"source" : [ "mode_floquet", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_pack", 0 ],
					"source" : [ "mode_lfsr", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_pack", 0 ],
					"source" : [ "mode_observer", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "mode_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_pack", 0 ],
					"source" : [ "mode_pythagorean", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode", 0 ],
					"source" : [ "mode_set", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_a", 0 ],
					"order" : 1,
					"source" : [ "phasor", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_b", 0 ],
					"order" : 0,
					"source" : [ "phasor", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"source" : [ "prepend_begin", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"source" : [ "prepend_chunk", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"source" : [ "prepend_end", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"source" : [ "prepend_harmonics", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "protocol", 0 ],
					"source" : [ "protocol_set", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "density", 0 ],
					"order" : 0,
					"source" : [ "qmw", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "time_root", 0 ],
					"order" : 1,
					"source" : [ "qmw", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "harmonics", 0 ],
					"source" : [ "receiver", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 1 ],
					"source" : [ "receiver", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "waveform", 0 ],
					"source" : [ "receiver", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "xfade_pack", 0 ],
					"source" : [ "receiver", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain", 1 ],
					"order" : 0,
					"source" : [ "safety", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain", 0 ],
					"order" : 1,
					"source" : [ "safety", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spqt_position", 0 ],
					"source" : [ "spqt", 0 ]
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
					"destination" : [ "receiver", 0 ],
					"source" : [ "test_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 1 ],
					"source" : [ "tick_dispatch", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tick", 0 ],
					"source" : [ "tick_dispatch", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "time_route", 0 ],
					"source" : [ "time_root", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "chronos", 0 ],
					"source" : [ "time_route", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "enabled", 0 ],
					"source" : [ "time_route", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "lfsr", 0 ],
					"source" : [ "time_route", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_set", 0 ],
					"source" : [ "time_route", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "protocol_set", 0 ],
					"source" : [ "time_route", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rate", 0 ],
					"source" : [ "time_route", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spqt", 0 ],
					"source" : [ "time_route", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qmw", 0 ],
					"source" : [ "udp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_a_gain", 0 ],
					"source" : [ "wave_a", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_sum", 0 ],
					"source" : [ "wave_a_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_b_gain", 0 ],
					"source" : [ "wave_b", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_sum", 1 ],
					"source" : [ "wave_b_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dcblock", 0 ],
					"source" : [ "wave_sum", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wavetable_route", 0 ],
					"source" : [ "wavetable", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_begin", 0 ],
					"source" : [ "wavetable_route", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_chunk", 0 ],
					"source" : [ "wavetable_route", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_end", 0 ],
					"source" : [ "wavetable_route", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_harmonics", 0 ],
					"source" : [ "wavetable_route", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_a_gain", 1 ],
					"source" : [ "xfade_inverse", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_b_gain", 1 ],
					"order" : 1,
					"source" : [ "xfade_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "xfade_inverse", 0 ],
					"order" : 0,
					"source" : [ "xfade_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "xfade_line", 0 ],
					"source" : [ "xfade_pack", 0 ]
				}

			}
 ],
		"originid" : "pat-981",
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
				"name" : "dcblocker~.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "o.pack.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "qmw_temporal_crystal16_spectral_wavetable_v1.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
