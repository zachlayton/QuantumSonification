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
		"rect" : [ 592.0, 100.0, 1444.0, 816.0 ],
		"openinpresentation" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 20.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 15.0, 1200.0, 29.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 15.0, 1200.0, 29.0 ],
					"text" : "QMW · COMPLETE 16-STATE WILSON CPS FLOW INSTRUMENT v5"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 12.0,
					"id" : "instructions",
					"linecount" : 2,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 48.0, 1380.0, 33.0 ],
					"presentation" : 1,
					"presentation_linecount" : 2,
					"presentation_rect" : [ 20.0, 48.0, 1380.0, 33.0 ],
					"text" : "Run examples/qmw_complete_cps_flow_v5.py · EMPTY/CLEAR is silent · BELL, GHZ, and WEAVE now commit and audition immediately · ranks 0)4…4)4 occupy successive registers · temperature explores Pascal grades 1–4–6–4–1 · circuit topology derives the Wilson master set and MOS address · LOOP sequences programmed columns; RECURSE explores probabilistically · XY moves within grades and H crosses grades"
				}

			}
, 			{
				"box" : 				{
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"enablehscroll" : 0,
					"enablevscroll" : 0,
					"id" : "programmer",
					"lockeddragscroll" : 0,
					"lockedsize" : 0,
					"maxclass" : "bpatcher",
					"name" : "QMW_QAC_Circuit_Programmer_Recursive_v3_3.maxpat",
					"numinlets" : 0,
					"numoutlets" : 0,
					"offset" : [ 0.0, 0.0 ],
					"patching_rect" : [ 20.0, 95.0, 865.0, 675.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 24.0, 95.0, 861.0, 550.0 ],
					"viewvisibility" : 1
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "controls_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 910.0, 95.0, 420.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 95.0, 420.0, 22.0 ],
					"text" : "RECURSION FIELD"
				}

			}
, 			{
				"box" : 				{
					"id" : "temp_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 910.0, 125.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 125.0, 110.0, 20.0 ],
					"text" : "temperature 0–2"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "temp",
					"maxclass" : "flonum",
					"maximum" : 2.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1030.0, 124.0, 70.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1030.0, 124.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "temp_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 1110.0, 124.0, 205.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1110.0, 124.0, 205.0, 22.0 ],
					"text" : "o.pack /qmw/recursive/temperature"
				}

			}
, 			{
				"box" : 				{
					"id" : "seed_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 910.0, 157.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 157.0, 110.0, 20.0 ],
					"text" : "random seed"
				}

			}
, 			{
				"box" : 				{
					"id" : "seed",
					"maxclass" : "number",
					"minimum" : 0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1030.0, 156.0, 70.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1030.0, 156.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "seed_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 1110.0, 156.0, 175.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1110.0, 156.0, 175.0, 22.0 ],
					"text" : "o.pack /qmw/recursive/seed"
				}

			}
, 			{
				"box" : 				{
					"id" : "depth_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 910.0, 189.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 189.0, 110.0, 20.0 ],
					"text" : "max depth 1–256"
				}

			}
, 			{
				"box" : 				{
					"id" : "depth",
					"maxclass" : "number",
					"maximum" : 256,
					"minimum" : 1,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1030.0, 188.0, 70.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1030.0, 188.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "depth_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 1110.0, 188.0, 191.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1110.0, 188.0, 191.0, 22.0 ],
					"text" : "o.pack /qmw/recursive/max_depth"
				}

			}
, 			{
				"box" : 				{
					"id" : "interval_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 910.0, 221.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 221.0, 110.0, 20.0 ],
					"text" : "interval ms"
				}

			}
, 			{
				"box" : 				{
					"id" : "interval",
					"maxclass" : "number",
					"minimum" : 30,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1030.0, 220.0, 70.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1030.0, 220.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "interval_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 1110.0, 220.0, 195.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1110.0, 220.0, 195.0, 22.0 ],
					"text" : "o.pack /qmw/recursive/interval_ms"
				}

			}
, 			{
				"box" : 				{
					"id" : "control_udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1320.0, 172.0, 150.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1320.0, 172.0, 150.0, 22.0 ],
					"text" : "udpsend 127.0.0.1 7403"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "receive_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 910.0, 268.0, 470.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 268.0, 470.0, 22.0 ],
					"text" : "COMPLETE CPS FLOW · 1–4–6–4–1 · all 16 basis states"
				}

			}
, 			{
				"box" : 				{
					"id" : "receive",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 910.0, 298.0, 105.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 298.0, 105.0, 22.0 ],
					"text" : "udpreceive 7410"
				}

			}
, 			{
				"box" : 				{
					"id" : "route_qmw",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 1030.0, 298.0, 115.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1030.0, 298.0, 115.0, 22.0 ],
					"text" : "OSC-route /qmw"
				}

			}
, 			{
				"box" : 				{
					"id" : "route_domain",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 1160.0, 298.0, 175.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1160.0, 298.0, 175.0, 22.0 ],
					"text" : "OSC-route /recursive /circuit"
				}

			}
, 			{
				"box" : 				{
					"id" : "route_recursive",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 7,
					"outlettype" : [ "", "", "", "", "", "", "" ],
					"patching_rect" : [ 910.0, 332.0, 560.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 332.0, 560.0, 22.0 ],
					"text" : "OSC-route /cps_flow_note /modulation /status /error /running /seed_accepted"
				}

			}
, 			{
				"box" : 				{
					"id" : "note_unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 14,
					"outlettype" : [ "int", "int", "int", "int", "int", "int", "float", "float", "float", "float", "int", "int", "int", "int" ],
					"patching_rect" : [ 910.0, 372.0, 510.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 372.0, 510.0, 22.0 ],
					"text" : "unpack i i i i i i f f f f i i i i"
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 910.0, 410.0, 510.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 410.0, 510.0, 22.0 ],
					"text" : "generation · shell probability · entropy · temperature · depth · seed · revision · gates"
				}

			}
, 			{
				"box" : 				{
					"id" : "error",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 910.0, 442.0, 510.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 442.0, 510.0, 22.0 ],
					"text" : "no recursive errors"
				}

			}
, 			{
				"box" : 				{
					"id" : "running",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1360.0, 332.0, 24.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1360.0, 332.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "running_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1390.0, 334.0, 70.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1390.0, 334.0, 70.0, 20.0 ],
					"text" : "running"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "midi_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 910.0, 490.0, 536.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 490.0, 536.0, 22.0 ],
					"text" : "MPE CPS OUTPUT · dynamic channels 2–16 · Ch. 1 master · from Max 1 → Ableton"
				}

			}
, 			{
				"box" : 				{
					"id" : "makenote",
					"maxclass" : "newobj",
					"numinlets" : 4,
					"numoutlets" : 3,
					"outlettype" : [ "float", "float", "float" ],
					"patching_rect" : [ 910.0, 530.0, 150.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 530.0, 150.0, 22.0 ],
					"text" : "makenote 64 120 2"
				}

			}
, 			{
				"box" : 				{
					"id" : "noteout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 910.0, 570.0, 80.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 910.0, 570.0, 80.0, 22.0 ],
					"text" : "noteout 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "xbendout",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 1080.0, 530.0, 75.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1080.0, 530.0, 75.0, 22.0 ],
					"text" : "xbendout"
				}

			}
, 			{
				"box" : 				{
					"id" : "midiout",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1080.0, 570.0, 80.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1080.0, 570.0, 80.0, 22.0 ],
					"text" : "midiout"
				}

			}
, 			{
				"box" : 				{
					"id" : "ctlout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 1190.0, 530.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1190.0, 530.0, 85.0, 22.0 ],
					"text" : "ctlout 74"
				}

			}
, 			{
				"box" : 				{
					"id" : "midi_note",
					"linecount" : 4,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 910.0, 615.0, 507.0, 60.0 ],
					"presentation" : 1,
					"presentation_linecount" : 4,
					"presentation_rect" : [ 910.0, 615.0, 507.0, 60.0 ],
					"text" : "0000 is the low identity pole; 1111 is the high total-product pole.\nCircuit commit gives a short population fingerprint; it never creates a background drone.\nTemperature 0 follows occupied vertices; 2 approaches Pascal-weighted exploration.\nCircuit tuning ON: paired/global/woven interaction geometry retunes the same basis identities."
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "default_temp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 20.0, 790.0, 95.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 790.0, 95.0, 22.0 ],
					"text" : "loadmess 0.65"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "default_seed",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 125.0, 790.0, 90.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 125.0, 790.0, 90.0, 22.0 ],
					"text" : "loadmess 23"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "default_depth",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 225.0, 790.0, 90.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 225.0, 790.0, 90.0, 22.0 ],
					"text" : "loadmess 32"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "default_interval",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 325.0, 790.0, 100.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 325.0, 790.0, 100.0, 22.0 ],
					"text" : "loadmess 240"
				}

			}
, 			{
				"box" : 				{
					"id" : "midi_port_load",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 1300.0, 530.0, 60.0, 22.0 ],
					"text" : "loadbang"
				}

			}
, 			{
				"box" : 				{
					"id" : "midi_port_message",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1290.0, 570.0, 125.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1290.0, 570.0, 125.0, 22.0 ],
					"text" : "port \"from Max 1\""
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "mod_bank_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 830.0, 1180.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 830.0, 1180.0, 22.0 ],
					"text" : "ABLETON GLOBAL MODULATION · OSC → smoothed MIDI CC · channel 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 9,
					"outlettype" : [ "int", "float", "float", "float", "float", "float", "float", "float", "float" ],
					"patching_rect" : [ 20.0, 858.0, 520.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 858.0, 520.0, 22.0 ],
					"text" : "unpack i f f f f f f f f"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entropy_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 892.0, 180.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 892.0, 180.0, 20.0 ],
					"text" : "entropy · CC20"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entropy_slide",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 20.0, 917.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 917.0, 65.0, 22.0 ],
					"text" : "slide 2 4"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entropy_scale",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 92.0, 917.0, 125.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 92.0, 917.0, 125.0, 22.0 ],
					"text" : "scale 0. 1. 0 127"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entropy_int",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 224.0, 917.0, 24.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 224.0, 917.0, 24.0, 22.0 ],
					"text" : "i"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entropy_change",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "int", "int" ],
					"patching_rect" : [ 255.0, 917.0, 54.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 255.0, 917.0, 54.0, 22.0 ],
					"text" : "change"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entropy_ctlout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 316.0, 917.0, 64.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 316.0, 917.0, 64.0, 22.0 ],
					"text" : "ctlout 20 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_coherence_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 380.0, 892.0, 180.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 380.0, 892.0, 180.0, 20.0 ],
					"text" : "coherence · CC21"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_coherence_slide",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 380.0, 917.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 380.0, 917.0, 65.0, 22.0 ],
					"text" : "slide 2 4"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_coherence_scale",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 452.0, 917.0, 125.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 452.0, 917.0, 125.0, 22.0 ],
					"text" : "scale 0. 1. 0 127"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_coherence_int",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 584.0, 917.0, 24.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 584.0, 917.0, 24.0, 22.0 ],
					"text" : "i"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_coherence_change",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "int", "int" ],
					"patching_rect" : [ 615.0, 917.0, 54.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 615.0, 917.0, 54.0, 22.0 ],
					"text" : "change"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_coherence_ctlout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 676.0, 917.0, 64.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 676.0, 917.0, 64.0, 22.0 ],
					"text" : "ctlout 21 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entanglement_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 740.0, 892.0, 180.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 740.0, 892.0, 180.0, 20.0 ],
					"text" : "entanglement · CC22"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entanglement_slide",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 740.0, 917.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 740.0, 917.0, 65.0, 22.0 ],
					"text" : "slide 2 4"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entanglement_scale",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 812.0, 917.0, 125.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 812.0, 917.0, 125.0, 22.0 ],
					"text" : "scale 0. 1. 0 127"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entanglement_int",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 944.0, 917.0, 24.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 944.0, 917.0, 24.0, 22.0 ],
					"text" : "i"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entanglement_change",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "int", "int" ],
					"patching_rect" : [ 975.0, 917.0, 54.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 975.0, 917.0, 54.0, 22.0 ],
					"text" : "change"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_entanglement_ctlout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 1036.0, 917.0, 64.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1036.0, 917.0, 64.0, 22.0 ],
					"text" : "ctlout 22 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_participation_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1100.0, 892.0, 180.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1100.0, 892.0, 180.0, 20.0 ],
					"text" : "participation · CC23"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_participation_slide",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1100.0, 917.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1100.0, 917.0, 65.0, 22.0 ],
					"text" : "slide 2 4"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_participation_scale",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1172.0, 917.0, 125.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1172.0, 917.0, 125.0, 22.0 ],
					"text" : "scale 0. 1. 0 127"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_participation_int",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 1304.0, 917.0, 24.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1304.0, 917.0, 24.0, 22.0 ],
					"text" : "i"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_participation_change",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "int", "int" ],
					"patching_rect" : [ 1335.0, 917.0, 54.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1335.0, 917.0, 54.0, 22.0 ],
					"text" : "change"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_participation_ctlout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 1396.0, 917.0, 64.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1396.0, 917.0, 64.0, 22.0 ],
					"text" : "ctlout 23 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_phase_order_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 970.0, 180.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 970.0, 180.0, 20.0 ],
					"text" : "phase order · CC24"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_phase_order_slide",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 20.0, 995.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 995.0, 65.0, 22.0 ],
					"text" : "slide 2 4"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_phase_order_scale",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 92.0, 995.0, 125.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 92.0, 995.0, 125.0, 22.0 ],
					"text" : "scale 0. 1. 0 127"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_phase_order_int",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 224.0, 995.0, 24.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 224.0, 995.0, 24.0, 22.0 ],
					"text" : "i"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_phase_order_change",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "int", "int" ],
					"patching_rect" : [ 255.0, 995.0, 54.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 255.0, 995.0, 54.0, 22.0 ],
					"text" : "change"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_phase_order_ctlout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 316.0, 995.0, 64.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 316.0, 995.0, 64.0, 22.0 ],
					"text" : "ctlout 24 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_grade_centroid_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 380.0, 970.0, 180.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 380.0, 970.0, 180.0, 20.0 ],
					"text" : "grade centroid · CC25"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_grade_centroid_slide",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 380.0, 995.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 380.0, 995.0, 65.0, 22.0 ],
					"text" : "slide 2 4"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_grade_centroid_scale",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 452.0, 995.0, 125.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 452.0, 995.0, 125.0, 22.0 ],
					"text" : "scale 0. 1. 0 127"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_grade_centroid_int",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 584.0, 995.0, 24.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 584.0, 995.0, 24.0, 22.0 ],
					"text" : "i"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_grade_centroid_change",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "int", "int" ],
					"patching_rect" : [ 615.0, 995.0, 54.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 615.0, 995.0, 54.0, 22.0 ],
					"text" : "change"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_grade_centroid_ctlout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 676.0, 995.0, 64.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 676.0, 995.0, 64.0, 22.0 ],
					"text" : "ctlout 25 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_hexany_mass_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 740.0, 970.0, 180.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 740.0, 970.0, 180.0, 20.0 ],
					"text" : "hexany mass · CC26"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_hexany_mass_slide",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 740.0, 995.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 740.0, 995.0, 65.0, 22.0 ],
					"text" : "slide 2 4"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_hexany_mass_scale",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 812.0, 995.0, 125.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 812.0, 995.0, 125.0, 22.0 ],
					"text" : "scale 0. 1. 0 127"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_hexany_mass_int",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 944.0, 995.0, 24.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 944.0, 995.0, 24.0, 22.0 ],
					"text" : "i"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_hexany_mass_change",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "int", "int" ],
					"patching_rect" : [ 975.0, 995.0, 54.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 975.0, 995.0, 54.0, 22.0 ],
					"text" : "change"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_hexany_mass_ctlout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 1036.0, 995.0, 64.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1036.0, 995.0, 64.0, 22.0 ],
					"text" : "ctlout 26 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_flow_strength_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1100.0, 970.0, 180.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1100.0, 970.0, 180.0, 20.0 ],
					"text" : "flow strength · CC27"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_flow_strength_slide",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1100.0, 995.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1100.0, 995.0, 65.0, 22.0 ],
					"text" : "slide 2 4"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_flow_strength_scale",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1172.0, 995.0, 125.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1172.0, 995.0, 125.0, 22.0 ],
					"text" : "scale 0. 1. 0 127"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_flow_strength_int",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"patching_rect" : [ 1304.0, 995.0, 24.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1304.0, 995.0, 24.0, 22.0 ],
					"text" : "i"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_flow_strength_change",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "int", "int" ],
					"patching_rect" : [ 1335.0, 995.0, 54.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1335.0, 995.0, 54.0, 22.0 ],
					"text" : "change"
				}

			}
, 			{
				"box" : 				{
					"id" : "mod_flow_strength_ctlout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 1396.0, 995.0, 64.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1396.0, 995.0, 64.0, 22.0 ],
					"text" : "ctlout 27 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "navigation_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 684.0, 760.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 684.0, 760.0, 20.0 ],
					"text" : "PHASE 4 NAVIGATION · Pascal grade as instrument · MOS Scale-Tree morph"
				}

			}
, 			{
				"box" : 				{
					"id" : "grade_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 714.0, 115.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 714.0, 115.0, 20.0 ],
					"text" : "grade -1/all, 0–4"
				}

			}
, 			{
				"box" : 				{
					"id" : "grade",
					"maxclass" : "number",
					"maximum" : 4,
					"minimum" : -1,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 140.0, 712.0, 55.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 140.0, 712.0, 55.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "grade_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 205.0, 712.0, 235.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 205.0, 712.0, 235.0, 22.0 ],
					"text" : "o.pack /qmw/wilson/navigation/grade"
				}

			}
, 			{
				"box" : 				{
					"id" : "mos_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 746.0, 115.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 746.0, 115.0, 20.0 ],
					"text" : "MOS target L/s"
				}

			}
, 			{
				"box" : 				{
					"id" : "mos_numerator",
					"maxclass" : "number",
					"minimum" : 1,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 140.0, 744.0, 45.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 140.0, 744.0, 45.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "mos_denominator",
					"maxclass" : "number",
					"minimum" : 2,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 190.0, 744.0, 45.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 190.0, 744.0, 45.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "mos_pair",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 245.0, 744.0, 55.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 245.0, 744.0, 55.0, 22.0 ],
					"text" : "pak 3 7"
				}

			}
, 			{
				"box" : 				{
					"id" : "mos_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 310.0, 744.0, 270.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 310.0, 744.0, 270.0, 22.0 ],
					"text" : "o.pack /qmw/wilson/navigation/mos_target"
				}

			}
, 			{
				"box" : 				{
					"id" : "morph_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 778.0, 167.0, 20.0 ],
					"presentation" : 1,
					"presentation_linecount" : 2,
					"presentation_rect" : [ 20.0, 778.0, 99.0, 33.0 ],
					"text" : "MOS pitch + voice morph 0–1"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "morph",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 140.0, 776.0, 70.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 140.0, 776.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "morph_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 220.0, 776.0, 270.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 220.0, 776.0, 270.0, 22.0 ],
					"text" : "o.pack /qmw/wilson/navigation/mos_progress"
				}

			}
, 			{
				"box" : 				{
					"id" : "default_grade",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 500.0, 712.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 500.0, 712.0, 85.0, 22.0 ],
					"text" : "loadmess -1"
				}

			}
, 			{
				"box" : 				{
					"id" : "default_mos_num",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 590.0, 712.0, 80.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 590.0, 712.0, 80.0, 22.0 ],
					"text" : "loadmess 2"
				}

			}
, 			{
				"box" : 				{
					"id" : "default_mos_den",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 675.0, 712.0, 80.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 675.0, 712.0, 80.0, 22.0 ],
					"text" : "loadmess 5"
				}

			}
, 			{
				"box" : 				{
					"id" : "default_morph",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 760.0, 712.0, 90.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 760.0, 712.0, 90.0, 22.0 ],
					"text" : "loadmess 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "tuning_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 500.0, 778.0, 155.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 500.0, 778.0, 155.0, 20.0 ],
					"text" : "circuit-derived tuning"
				}

			}
, 			{
				"box" : 				{
					"id" : "tuning_enabled",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 660.0, 776.0, 24.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 660.0, 776.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "tuning_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 694.0, 776.0, 230.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 694.0, 776.0, 230.0, 22.0 ],
					"text" : "o.pack /qmw/wilson/tuning/enabled"
				}

			}
, 			{
				"box" : 				{
					"id" : "default_tuning",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 860.0, 712.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 860.0, 712.0, 85.0, 22.0 ],
					"text" : "loadmess 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "tuning_mode_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 950.0, 746.0, 90.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 950.0, 746.0, 90.0, 20.0 ],
					"text" : "tuning space"
				}

			}
, 			{
				"box" : 				{
					"id" : "tuning_mode",
					"items" : [ "cps", ",", "diamond", ",", "mos", ",", "scala", ",", "equal" ],
					"maxclass" : "umenu",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "int", "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1040.0, 744.0, 120.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1040.0, 744.0, 120.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "tuning_mode_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 1170.0, 744.0, 255.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1170.0, 744.0, 255.0, 22.0 ],
					"text" : "o.pack /qmw/wilson/tuning/mode"
				}

			}
, 			{
				"box" : 				{
					"id" : "default_tuning_mode",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 950.0, 712.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 950.0, 712.0, 85.0, 22.0 ],
					"text" : "loadmess 0"
				}

			}
, 			{
				"box" : 				{
					"id" : "scala_load_button",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 950.0, 778.0, 22.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 950.0, 778.0, 22.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "scala_load_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 976.0, 779.0, 68.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 976.0, 779.0, 68.0, 20.0 ],
					"text" : "load .scl"
				}

			}
, 			{
				"box" : 				{
					"id" : "scala_save_button",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1050.0, 778.0, 22.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1050.0, 778.0, 22.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "scala_save_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1076.0, 779.0, 68.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1076.0, 779.0, 68.0, 20.0 ],
					"text" : "save .scl"
				}

			}
, 			{
				"box" : 				{
					"id" : "scala_open_dialog",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"patching_rect" : [ 950.0, 820.0, 70.0, 22.0 ],
					"text" : "opendialog"
				}

			}
, 			{
				"box" : 				{
					"id" : "scala_save_dialog",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "bang" ],
					"patching_rect" : [ 1050.0, 820.0, 70.0, 22.0 ],
					"text" : "savedialog"
				}

			}
, 			{
				"box" : 				{
					"id" : "scala_load_trigger",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"patching_rect" : [ 950.0, 854.0, 42.0, 22.0 ],
					"text" : "t s b"
				}

			}
, 			{
				"box" : 				{
					"id" : "scala_mode_set",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1000.0, 854.0, 38.0, 22.0 ],
					"text" : "set 3"
				}

			}
, 			{
				"box" : 				{
					"id" : "scala_load_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 950.0, 888.0, 250.0, 22.0 ],
					"text" : "o.pack /qmw/wilson/tuning/scala/load"
				}

			}
, 			{
				"box" : 				{
					"id" : "scala_save_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 1210.0, 888.0, 250.0, 22.0 ],
					"text" : "o.pack /qmw/wilson/tuning/scala/save"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "depth", 0 ],
					"source" : [ "default_depth", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "grade", 0 ],
					"source" : [ "default_grade", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "interval", 0 ],
					"source" : [ "default_interval", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "morph", 0 ],
					"source" : [ "default_morph", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mos_denominator", 0 ],
					"source" : [ "default_mos_den", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mos_numerator", 0 ],
					"source" : [ "default_mos_num", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "seed", 0 ],
					"source" : [ "default_seed", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "temp", 0 ],
					"source" : [ "default_temp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tuning_enabled", 0 ],
					"source" : [ "default_tuning", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tuning_mode", 0 ],
					"source" : [ "default_tuning_mode", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "depth_pack", 0 ],
					"source" : [ "depth", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "depth_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "grade_pack", 0 ],
					"source" : [ "grade", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "grade_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "interval_pack", 0 ],
					"source" : [ "interval", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "interval_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "noteout", 2 ],
					"source" : [ "makenote", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "noteout", 1 ],
					"source" : [ "makenote", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "noteout", 0 ],
					"source" : [ "makenote", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "midi_port_message", 0 ],
					"source" : [ "midi_port_load", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ctlout", 0 ],
					"order" : 2,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "midiout", 0 ],
					"order" : 3,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_coherence_ctlout", 0 ],
					"order" : 8,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entanglement_ctlout", 0 ],
					"order" : 5,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entropy_ctlout", 0 ],
					"order" : 10,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_flow_strength_ctlout", 0 ],
					"order" : 0,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_grade_centroid_ctlout", 0 ],
					"order" : 7,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_hexany_mass_ctlout", 0 ],
					"order" : 4,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_participation_ctlout", 0 ],
					"order" : 1,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_phase_order_ctlout", 0 ],
					"order" : 9,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "noteout", 0 ],
					"order" : 6,
					"source" : [ "midi_port_message", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_coherence_ctlout", 0 ],
					"source" : [ "mod_coherence_change", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_coherence_change", 0 ],
					"source" : [ "mod_coherence_int", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_coherence_int", 0 ],
					"source" : [ "mod_coherence_scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_coherence_scale", 0 ],
					"source" : [ "mod_coherence_slide", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entanglement_ctlout", 0 ],
					"source" : [ "mod_entanglement_change", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entanglement_change", 0 ],
					"source" : [ "mod_entanglement_int", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entanglement_int", 0 ],
					"source" : [ "mod_entanglement_scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entanglement_scale", 0 ],
					"source" : [ "mod_entanglement_slide", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entropy_ctlout", 0 ],
					"source" : [ "mod_entropy_change", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entropy_change", 0 ],
					"source" : [ "mod_entropy_int", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entropy_int", 0 ],
					"source" : [ "mod_entropy_scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entropy_scale", 0 ],
					"source" : [ "mod_entropy_slide", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_flow_strength_ctlout", 0 ],
					"source" : [ "mod_flow_strength_change", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_flow_strength_change", 0 ],
					"source" : [ "mod_flow_strength_int", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_flow_strength_int", 0 ],
					"source" : [ "mod_flow_strength_scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_flow_strength_scale", 0 ],
					"source" : [ "mod_flow_strength_slide", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_grade_centroid_ctlout", 0 ],
					"source" : [ "mod_grade_centroid_change", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_grade_centroid_change", 0 ],
					"source" : [ "mod_grade_centroid_int", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_grade_centroid_int", 0 ],
					"source" : [ "mod_grade_centroid_scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_grade_centroid_scale", 0 ],
					"source" : [ "mod_grade_centroid_slide", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_hexany_mass_ctlout", 0 ],
					"source" : [ "mod_hexany_mass_change", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_hexany_mass_change", 0 ],
					"source" : [ "mod_hexany_mass_int", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_hexany_mass_int", 0 ],
					"source" : [ "mod_hexany_mass_scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_hexany_mass_scale", 0 ],
					"source" : [ "mod_hexany_mass_slide", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_participation_ctlout", 0 ],
					"source" : [ "mod_participation_change", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_participation_change", 0 ],
					"source" : [ "mod_participation_int", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_participation_int", 0 ],
					"source" : [ "mod_participation_scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_participation_scale", 0 ],
					"source" : [ "mod_participation_slide", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_phase_order_ctlout", 0 ],
					"source" : [ "mod_phase_order_change", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_phase_order_change", 0 ],
					"source" : [ "mod_phase_order_int", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_phase_order_int", 0 ],
					"source" : [ "mod_phase_order_scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_phase_order_scale", 0 ],
					"source" : [ "mod_phase_order_slide", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_coherence_slide", 0 ],
					"source" : [ "mod_unpack", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entanglement_slide", 0 ],
					"source" : [ "mod_unpack", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_entropy_slide", 0 ],
					"source" : [ "mod_unpack", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_flow_strength_slide", 0 ],
					"source" : [ "mod_unpack", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_grade_centroid_slide", 0 ],
					"source" : [ "mod_unpack", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_hexany_mass_slide", 0 ],
					"source" : [ "mod_unpack", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_participation_slide", 0 ],
					"source" : [ "mod_unpack", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_phase_order_slide", 0 ],
					"source" : [ "mod_unpack", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "morph_pack", 0 ],
					"source" : [ "morph", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "morph_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mos_pair", 1 ],
					"source" : [ "mos_denominator", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mos_pair", 0 ],
					"source" : [ "mos_numerator", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "mos_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mos_pack", 0 ],
					"source" : [ "mos_pair", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ctlout", 2 ],
					"order" : 0,
					"source" : [ "note_unpack", 12 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ctlout", 0 ],
					"source" : [ "note_unpack", 11 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "makenote", 3 ],
					"order" : 2,
					"source" : [ "note_unpack", 12 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "makenote", 2 ],
					"source" : [ "note_unpack", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "makenote", 1 ],
					"source" : [ "note_unpack", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "makenote", 0 ],
					"source" : [ "note_unpack", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "xbendout", 1 ],
					"order" : 1,
					"source" : [ "note_unpack", 12 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "xbendout", 0 ],
					"source" : [ "note_unpack", 10 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "route_qmw", 0 ],
					"source" : [ "receive", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "route_recursive", 0 ],
					"source" : [ "route_domain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "route_domain", 0 ],
					"source" : [ "route_qmw", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "error", 0 ],
					"source" : [ "route_recursive", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mod_unpack", 0 ],
					"source" : [ "route_recursive", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "note_unpack", 0 ],
					"source" : [ "route_recursive", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "running", 0 ],
					"source" : [ "route_recursive", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 0 ],
					"source" : [ "route_recursive", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scala_open_dialog", 0 ],
					"source" : [ "scala_load_button", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "scala_load_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scala_load_pack", 0 ],
					"source" : [ "scala_load_trigger", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scala_mode_set", 0 ],
					"source" : [ "scala_load_trigger", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tuning_mode", 0 ],
					"source" : [ "scala_mode_set", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scala_load_trigger", 0 ],
					"source" : [ "scala_open_dialog", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scala_save_dialog", 0 ],
					"source" : [ "scala_save_button", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scala_save_pack", 0 ],
					"source" : [ "scala_save_dialog", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "scala_save_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "seed_pack", 0 ],
					"source" : [ "seed", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "seed_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "temp_pack", 0 ],
					"source" : [ "temp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "temp_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tuning_pack", 0 ],
					"source" : [ "tuning_enabled", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tuning_mode_pack", 0 ],
					"source" : [ "tuning_mode", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "tuning_mode_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "control_udp", 0 ],
					"source" : [ "tuning_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "midiout", 0 ],
					"source" : [ "xbendout", 0 ]
				}

			}
 ],
		"originid" : "pat-55",
		"dependency_cache" : [ 			{
				"name" : "OSC-route.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "QMW_QAC_Circuit_Programmer_Recursive_v3_3.maxpat",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
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
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qac_quantumsonification_sender_recursive_v3.maxpat",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_qac_circuit_programmer_recursive_v3_3.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
