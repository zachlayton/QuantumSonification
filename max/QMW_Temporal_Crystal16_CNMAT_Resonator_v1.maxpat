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
		"rect" : [ 134.0, 100.0, 1200.0, 816.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 17.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 18.0, 1040.0, 25.0 ],
					"text" : "QMW Temporal Crystal 16 → CNMAT Resonant Body v1"
				}

			}
, 			{
				"box" : 				{
					"id" : "subtitle",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 48.0, 1120.0, 20.0 ],
					"text" : "The canonical 16×16 density matrix retunes 256 CNMAT resonances. Each /qmw/time/chronos/tick excites the stored body independently."
				}

			}
, 			{
				"box" : 				{
					"id" : "port_warning",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 18.0, 400.0, 20.0 ],
					"text" : "Close every other Max patch that binds UDP 7400.",
					"textcolor" : [ 0.8, 0.18, 0.12, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "engine_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 100.0, 300.0, 20.0 ],
					"text" : "MODEL — canonical QMW density engine"
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
					"fontface" : 1,
					"id" : "mode_control_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 830.0, 100.0, 340.0, 20.0 ],
					"text" : "LIVE TEMPORAL MODE → Python control port 7402"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_observer",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 830.0, 126.0, 68.0, 22.0 ],
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
					"patching_rect" : [ 908.0, 126.0, 58.0, 22.0 ],
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
					"patching_rect" : [ 976.0, 126.0, 36.0, 22.0 ],
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
					"patching_rect" : [ 1022.0, 126.0, 94.0, 22.0 ],
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
					"patching_rect" : [ 830.0, 166.0, 208.0, 22.0 ],
					"text" : "o.pack /qmw/time/control/mode"
				}

			}
, 			{
				"box" : 				{
					"id" : "control_udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1050.0, 166.0, 145.0, 22.0 ],
					"text" : "udpsend 127.0.0.1 7402"
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
					"fontface" : 1,
					"id" : "time_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 215.0, 560.0, 20.0 ],
					"text" : "TEMPORAL CRYSTAL 16 — logical clock, protocol, and diagnostics"
				}

			}
, 			{
				"box" : 				{
					"id" : "time_root",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 25.0, 242.0, 108.0, 22.0 ],
					"text" : "OSC-route /time"
				}

			}
, 			{
				"box" : 				{
					"id" : "time_route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 11,
					"outlettype" : [ "", "", "", "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 145.0, 242.0, 855.0, 22.0 ],
					"text" : "OSC-route /enabled /mode /rate_hz /revision /protocol /chronos /lfsr /spqt /kairos /aion"
				}

			}
, 			{
				"box" : 				{
					"id" : "enabled_value",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 25.0, 285.0, 55.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "enabled_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 310.0, 70.0, 20.0 ],
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
					"patching_rect" : [ 95.0, 285.0, 72.0, 22.0 ],
					"text" : "prepend set"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_value",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 178.0, 285.0, 112.0, 22.0 ],
					"text" : "observer"
				}

			}
, 			{
				"box" : 				{
					"id" : "mode_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 178.0, 310.0, 90.0, 20.0 ],
					"text" : "MODE"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "rate_value",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 305.0, 285.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "rate_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 305.0, 310.0, 90.0, 20.0 ],
					"text" : "RATE Hz"
				}

			}
, 			{
				"box" : 				{
					"id" : "revision_value",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 390.0, 285.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "revision_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 390.0, 310.0, 90.0, 20.0 ],
					"text" : "REVISION"
				}

			}
, 			{
				"box" : 				{
					"id" : "protocol_set",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 475.0, 285.0, 72.0, 22.0 ],
					"text" : "prepend set"
				}

			}
, 			{
				"box" : 				{
					"id" : "protocol_value",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 558.0, 285.0, 330.0, 22.0 ],
					"text" : "observer_no_state_mutation"
				}

			}
, 			{
				"box" : 				{
					"id" : "protocol_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 558.0, 310.0, 90.0, 20.0 ],
					"text" : "PROTOCOL"
				}

			}
, 			{
				"box" : 				{
					"id" : "chronos_route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 25.0, 345.0, 202.0, 22.0 ],
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
					"patching_rect" : [ 242.0, 345.0, 43.0, 22.0 ],
					"text" : "t i b"
				}

			}
, 			{
				"box" : 				{
					"id" : "tick_value",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 300.0, 345.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "tick_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 300.0, 370.0, 60.0, 20.0 ],
					"text" : "TICK"
				}

			}
, 			{
				"box" : 				{
					"id" : "index_value",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 380.0, 345.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "index_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 380.0, 370.0, 60.0, 20.0 ],
					"text" : "INDEX"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "phase_value",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 460.0, 345.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "phase_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 460.0, 370.0, 110.0, 20.0 ],
					"text" : "PHASE rad"
				}

			}
, 			{
				"box" : 				{
					"id" : "tick_trigger",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 575.0, 345.0, 82.0, 22.0 ],
					"text" : "trigger 0.45"
				}

			}
, 			{
				"box" : 				{
					"id" : "tick_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 670.0, 347.0, 300.0, 20.0 ],
					"text" : "bounded Chronos impulse → existing trigger path"
				}

			}
, 			{
				"box" : 				{
					"id" : "lfsr_route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 25.0, 405.0, 196.0, 22.0 ],
					"text" : "OSC-route /state /bits /phase"
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
					"patching_rect" : [ 235.0, 405.0, 60.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "lfsr_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 235.0, 430.0, 90.0, 20.0 ],
					"text" : "LFSR STATE"
				}

			}
, 			{
				"box" : 				{
					"id" : "spqt_route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 330.0, 405.0, 288.0, 22.0 ],
					"text" : "OSC-route /macrocycle_position /macrocycle_length"
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
					"patching_rect" : [ 615.0, 405.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "spqt_position_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 615.0, 430.0, 90.0, 20.0 ],
					"text" : "SPQT POS"
				}

			}
, 			{
				"box" : 				{
					"id" : "spqt_length",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 700.0, 405.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "spqt_length_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 700.0, 430.0, 100.0, 20.0 ],
					"text" : "SPQT LENGTH"
				}

			}
, 			{
				"box" : 				{
					"id" : "kairos_route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 25.0, 462.0, 142.0, 22.0 ],
					"text" : "OSC-route /count /event"
				}

			}
, 			{
				"box" : 				{
					"id" : "kairos_count",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 180.0, 462.0, 60.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "kairos_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 180.0, 487.0, 90.0, 20.0 ],
					"text" : "KAIROS N"
				}

			}
, 			{
				"box" : 				{
					"id" : "kairos_set",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 255.0, 462.0, 72.0, 22.0 ],
					"text" : "prepend set"
				}

			}
, 			{
				"box" : 				{
					"id" : "kairos_event",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 340.0, 462.0, 380.0, 22.0 ],
					"text" : "no Kairos event"
				}

			}
, 			{
				"box" : 				{
					"id" : "aion_route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 790.0, 405.0, 377.0, 22.0 ],
					"text" : "OSC-route /target_frequency /target_amplitude /peak_to_background"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "aion_frequency",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 790.0, 442.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "aion_amplitude",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 880.0, 442.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "aion_peak",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 970.0, 442.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "aion_labels",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 467.0, 330.0, 20.0 ],
					"text" : "AION target Hz     amplitude        peak/background"
				}

			}
, 			{
				"box" : 				{
					"id" : "qtm_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 520.0, 420.0, 20.0 ],
					"text" : "LEGACY OPTIONAL TRIGGER — QTM v1 density clock"
				}

			}
, 			{
				"box" : 				{
					"id" : "qtm_mechanics",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 360.0, 520.0, 188.0, 22.0 ],
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
					"patching_rect" : [ 560.0, 520.0, 92.0, 22.0 ],
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
					"patching_rect" : [ 665.0, 520.0, 146.0, 22.0 ],
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
					"patching_rect" : [ 824.0, 520.0, 102.0, 22.0 ],
					"text" : "OSC-route /pulse"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "gain_vector_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 563.0, 1120.0, 20.0 ],
					"text" : "CLICK-LATCHED RESONANCE GAINS — 256 ordered relations, row-major: slider index = 16m + n"
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.1, 0.14, 1.0 ],
					"id" : "gain_multislider",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 25.0, 588.0, 1120.0, 125.0 ],
					"setminmax" : [ 0.0, 0.419999986886978 ],
					"size" : 256,
					"slidercolor" : [ 0.34, 0.78, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "js",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 5,
					"outlettype" : [ "", "", "", "", "" ],
					"patching_rect" : [ 390.0, 760.0, 330.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_temporal_crystal16_cnmat_resonator_v1.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_temporal_crystal16_cnmat_resonator_v1.js"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "frequency_multiplier_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 745.0, 735.0, 370.0, 20.0 ],
					"text" : "GLOBAL RESONANCE FREQUENCY × — applied on next click"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "frequency_multiplier",
					"maxclass" : "flonum",
					"maximum" : 8.0,
					"minimum" : 0.03125,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 745.0, 760.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "frequency_quarter",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 830.0, 760.0, 42.0, 22.0 ],
					"text" : "0.25"
				}

			}
, 			{
				"box" : 				{
					"id" : "frequency_half",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 882.0, 760.0, 34.0, 22.0 ],
					"text" : "0.5"
				}

			}
, 			{
				"box" : 				{
					"id" : "frequency_unity",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 926.0, 760.0, 30.0, 22.0 ],
					"text" : "1."
				}

			}
, 			{
				"box" : 				{
					"id" : "frequency_load",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 970.0, 760.0, 84.0, 22.0 ],
					"text" : "loadmess 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 390.0, 796.0, 530.0, 22.0 ],
					"text" : "set \"model 29561 staged: waiting for next click\""
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
					"patching_rect" : [ 25.0, 759.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "test_message",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 60.0, 760.0, 34.0, 22.0 ],
					"text" : "test"
				}

			}
, 			{
				"box" : 				{
					"id" : "test_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 105.0, 761.0, 185.0, 20.0 ],
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
					"patching_rect" : [ 25.0, 815.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "manual_amp",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 60.0, 816.0, 76.0, 22.0 ],
					"text" : "trigger 0.7"
				}

			}
, 			{
				"box" : 				{
					"id" : "manual_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 108.0, 817.0, 182.0, 20.0 ],
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
					"patching_rect" : [ 515.0, 856.0, 42.0, 22.0 ],
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
					"patching_rect" : [ 424.0, 902.0, 156.0, 22.0 ],
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
					"patching_rect" : [ 605.0, 870.0, 40.0, 22.0 ],
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
					"patching_rect" : [ 655.0, 870.0, 54.0, 22.0 ],
					"text" : "squelch"
				}

			}
, 			{
				"box" : 				{
					"id" : "sinusoids",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 25.0, 902.0, 112.0, 22.0 ],
					"text" : "sinusoids~ bwe"
				}

			}
, 			{
				"box" : 				{
					"id" : "sine_gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 155.0, 902.0, 40.0, 22.0 ],
					"text" : "*~ 0.1"
				}

			}
, 			{
				"box" : 				{
					"id" : "sine_level_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 940.0, 112.0, 20.0 ],
					"text" : "SINE BLEND"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "sine_level",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 155.0, 938.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "sine_level_load",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 240.0, 938.0, 98.0, 22.0 ],
					"text" : "loadmess 0.25"
				}

			}
, 			{
				"box" : 				{
					"id" : "makeup",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 605.0, 902.0, 66.0, 22.0 ],
					"text" : "*~ 500."
				}

			}
, 			{
				"box" : 				{
					"id" : "spectral_mix",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 690.0, 902.0, 36.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "safety_clip",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 745.0, 902.0, 104.0, 22.0 ],
					"text" : "clip~ -0.98 0.98"
				}

			}
, 			{
				"box" : 				{
					"id" : "makeup_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 605.0, 940.0, 78.0, 20.0 ],
					"text" : "MAKEUP ×"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "makeup_value",
					"maxclass" : "flonum",
					"maximum" : 1000.0,
					"minimum" : 1.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 690.0, 938.0, 76.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "makeup_load",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 785.0, 938.0, 98.0, 22.0 ],
					"text" : "loadmess 500."
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
					"patching_rect" : [ 449.0, 990.0, 96.0, 125.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_longname" : "live.gain~",
							"parameter_mmax" : 6.0,
							"parameter_mmin" : -70.0,
							"parameter_modmode" : 3,
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
					"patching_rect" : [ 458.0, 1140.0, 45.0, 45.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "architecture",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 1194.0, 1376.0, 20.0 ],
					"text" : "Complete model updates are staged silently. Chronos ticks, canonical resonance events, optional legacy QTM pulses, and the manual button commit the newest model immediately before click~. Adjustable makeup is bounded by clip~ before the output fader."
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "aion_amplitude", 0 ],
					"source" : [ "aion_route", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "aion_frequency", 0 ],
					"source" : [ "aion_route", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "aion_peak", 0 ],
					"source" : [ "aion_route", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "index_value", 0 ],
					"source" : [ "chronos_route", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "phase_value", 0 ],
					"source" : [ "chronos_route", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tick_dispatch", 0 ],
					"source" : [ "chronos_route", 0 ]
				}

			}
, 			{
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
					"destination" : [ "time_root", 0 ],
					"order" : 2,
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
					"destination" : [ "frequency_multiplier", 0 ],
					"source" : [ "frequency_half", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "frequency_multiplier", 0 ],
					"source" : [ "frequency_load", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "js", 2 ],
					"source" : [ "frequency_multiplier", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "frequency_multiplier", 0 ],
					"source" : [ "frequency_quarter", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "frequency_multiplier", 0 ],
					"source" : [ "frequency_unity", 0 ]
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
					"destination" : [ "gain_multislider", 0 ],
					"source" : [ "js", 3 ]
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
					"destination" : [ "sinusoids", 0 ],
					"source" : [ "js", 4 ]
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
					"destination" : [ "kairos_count", 0 ],
					"source" : [ "kairos_route", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "kairos_set", 0 ],
					"source" : [ "kairos_route", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "kairos_event", 0 ],
					"source" : [ "kairos_set", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "lfsr_state", 0 ],
					"source" : [ "lfsr_route", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spectral_mix", 0 ],
					"source" : [ "makeup", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "makeup_value", 0 ],
					"source" : [ "makeup_load", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "makeup", 1 ],
					"source" : [ "makeup_value", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "js", 0 ],
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
					"destination" : [ "mode_value", 0 ],
					"source" : [ "mode_set", 0 ]
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
					"destination" : [ "protocol_value", 0 ],
					"source" : [ "protocol_set", 0 ]
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
					"destination" : [ "makeup", 0 ],
					"source" : [ "resonators", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain", 1 ],
					"order" : 0,
					"source" : [ "safety_clip", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain", 0 ],
					"order" : 1,
					"source" : [ "safety_clip", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spectral_mix", 1 ],
					"source" : [ "sine_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sine_gain", 1 ],
					"source" : [ "sine_level", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sine_level", 0 ],
					"source" : [ "sine_level_load", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sine_gain", 0 ],
					"source" : [ "sinusoids", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "safety_clip", 0 ],
					"source" : [ "spectral_mix", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spqt_length", 0 ],
					"source" : [ "spqt_route", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spqt_position", 0 ],
					"source" : [ "spqt_route", 0 ]
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
, 			{
				"patchline" : 				{
					"destination" : [ "tick_trigger", 0 ],
					"source" : [ "tick_dispatch", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tick_value", 0 ],
					"source" : [ "tick_dispatch", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "js", 0 ],
					"source" : [ "tick_trigger", 0 ]
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
					"destination" : [ "aion_route", 0 ],
					"source" : [ "time_route", 9 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "chronos_route", 0 ],
					"source" : [ "time_route", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "enabled_value", 0 ],
					"source" : [ "time_route", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "kairos_route", 0 ],
					"source" : [ "time_route", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "lfsr_route", 0 ],
					"source" : [ "time_route", 6 ]
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
					"source" : [ "time_route", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rate_value", 0 ],
					"source" : [ "time_route", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "revision_value", 0 ],
					"source" : [ "time_route", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spqt_route", 0 ],
					"source" : [ "time_route", 7 ]
				}

			}
 ],
		"originid" : "pat-76",
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
				"name" : "o.pack.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "qmw_temporal_crystal16_cnmat_resonator_v1.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "resonators~.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "sinusoids~.mxo",
				"type" : "iLaX"
			}
 ],
		"autosave" : 0
	}

}
