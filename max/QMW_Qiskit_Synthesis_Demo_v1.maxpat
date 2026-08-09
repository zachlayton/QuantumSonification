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
		"rect" : [ 214.0, 116.0, 1061.0, 660.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 22.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 22.0, 620.0, 31.0 ],
					"text" : "QMW · QISKIT SYNTHESIS LISTENING LAB v1"
				}

			}
, 			{
				"box" : 				{
					"id" : "subtitle",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 31.0, 55.0, 560.0, 20.0 ],
					"text" : "Four-qubit synthesis → canonical 256-value density architecture"
				}

			}
, 			{
				"box" : 				{
					"id" : "instructions",
					"linecount" : 3,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 90.0, 410.0, 47.0 ],
					"text" : "1. Start examples/qmw_synthesis_max_demo_v1.py\n2. Select a MIDI output in Options > MIDI Setup\n3. Click a synthesis family"
				}

			}
, 			{
				"box" : 				{
					"id" : "qft",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 30.0, 170.0, 90.0, 22.0 ],
					"text" : "qft"
				}

			}
, 			{
				"box" : 				{
					"id" : "evolution",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 135.0, 170.0, 100.0, 22.0 ],
					"text" : "evolution"
				}

			}
, 			{
				"box" : 				{
					"id" : "clifford",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 250.0, 170.0, 100.0, 22.0 ],
					"text" : "clifford"
				}

			}
, 			{
				"box" : 				{
					"id" : "permutation",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 365.0, 170.0, 110.0, 22.0 ],
					"text" : "permutation"
				}

			}
, 			{
				"box" : 				{
					"id" : "osc_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 30.0, 220.0, 205.0, 22.0 ],
					"text" : "o.pack /qmw/synthesis/demo"
				}

			}
, 			{
				"box" : 				{
					"id" : "send",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 260.0, 180.0, 22.0 ],
					"text" : "udpsend 127.0.0.1 7403"
				}

			}
, 			{
				"box" : 				{
					"id" : "receive_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 530.0, 95.0, 260.0, 20.0 ],
					"text" : "SYNTHESIS STATUS FROM PYTHON"
				}

			}
, 			{
				"box" : 				{
					"id" : "receive",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 530.0, 125.0, 125.0, 22.0 ],
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
					"patching_rect" : [ 530.0, 175.0, 110.0, 22.0 ],
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
					"patching_rect" : [ 530.0, 220.0, 180.0, 22.0 ],
					"text" : "OSC-route /circuit /synthesis"
				}

			}
, 			{
				"box" : 				{
					"id" : "route_circuit",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 500.0, 270.0, 220.0, 22.0 ],
					"text" : "OSC-route /load /op_count /qasm3"
				}

			}
, 			{
				"box" : 				{
					"id" : "route_load",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 445.0, 320.0, 180.0, 22.0 ],
					"text" : "OSC-route /accepted /error"
				}

			}
, 			{
				"box" : 				{
					"id" : "accepted_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 405.0, 382.0, 275.0, 20.0 ],
					"text" : "accepted revision · kind · operations · qubits"
				}

			}
, 			{
				"box" : 				{
					"id" : "accepted",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 405.0, 410.0, 360.0, 22.0 ],
					"text" : "1784572514 evolution 42 4"
				}

			}
, 			{
				"box" : 				{
					"id" : "error",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 405.0, 450.0, 360.0, 22.0 ],
					"text" : "no errors"
				}

			}
, 			{
				"box" : 				{
					"id" : "route_synthesis",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 720.0, 270.0, 105.0, 22.0 ],
					"text" : "OSC-route /demo"
				}

			}
, 			{
				"box" : 				{
					"id" : "route_demo",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 6,
					"outlettype" : [ "", "", "", "", "", "" ],
					"patching_rect" : [ 650.0, 320.0, 334.0, 22.0 ],
					"text" : "OSC-route /summary /error /gate /performance /tonnetz_note"
				}

			}
, 			{
				"box" : 				{
					"id" : "summary",
					"linecount" : 7,
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 720.0, 382.0, 225.0, 102.0 ],
					"text" : "1784572514 evolution \"{\\\"depth\\\": 22, \\\"kind\\\": \\\"evolution\\\", \\\"method\\\": \\\"suzuki_trotter\\\", \\\"operations\\\": {\\\"cx\\\": 16, \\\"u\\\": 26}, \\\"order\\\": 2, \\\"qubits\\\": 4, \\\"reps\\\": 2, \\\"seed\\\": null, \\\"size\\\": 42, \\\"terms\\\": [[\\\"XXII\\\", 0.7], [\\\"IIZZ\\\", 0.35], [\\\"ZIII\\\", 0.2]], \\\"time\\\": 1.5}\""
				}

			}
, 			{
				"box" : 				{
					"id" : "gate_unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 13,
					"outlettype" : [ "int", "int", "", "", "int", "int", "int", "float", "int", "float", "float", "float", "float" ],
					"patching_rect" : [ 442.5, 474.0, 285.0, 22.0 ],
					"text" : "unpack i i s s i i i f i f f f f"
				}

			}
, 			{
				"box" : 				{
					"id" : "gate_label",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 430.0, 535.0, 165.0, 22.0 ],
					"text" : "u3"
				}

			}
, 			{
				"box" : 				{
					"id" : "state_unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 11,
					"outlettype" : [ "int", "int", "int", "int", "int", "int", "int", "float", "float", "int", "int" ],
					"patching_rect" : [ 385.0, 559.0, 255.0, 22.0 ],
					"text" : "unpack i i i i i i i f f i i"
				}

			}
, 			{
				"box" : 				{
					"id" : "midi_pitch_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 630.0, 510.0, 55.0, 20.0 ],
					"text" : "pitch"
				}

			}
, 			{
				"box" : 				{
					"id" : "midi_pitch",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 630.0, 535.0, 55.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "midi_velocity_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 705.0, 510.0, 65.0, 20.0 ],
					"text" : "velocity"
				}

			}
, 			{
				"box" : 				{
					"id" : "midi_velocity",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 705.0, 535.0, 55.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "midi_duration_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 780.0, 510.0, 90.0, 20.0 ],
					"text" : "duration ms"
				}

			}
, 			{
				"box" : 				{
					"id" : "midi_duration",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 780.0, 535.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "makenote",
					"maxclass" : "newobj",
					"numinlets" : 4,
					"numoutlets" : 3,
					"outlettype" : [ "float", "float", "float" ],
					"patching_rect" : [ 630.0, 615.0, 130.0, 22.0 ],
					"text" : "makenote 64 120 2"
				}

			}
, 			{
				"box" : 				{
					"id" : "noteout",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 630.0, 655.0, 82.0, 22.0 ],
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
					"patching_rect" : [ 800.0, 615.0, 75.0, 22.0 ],
					"text" : "xbendout"
				}

			}
, 			{
				"box" : 				{
					"id" : "midiout",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 800.0, 655.0, 65.0, 22.0 ],
					"text" : "midiout"
				}

			}
, 			{
				"box" : 				{
					"id" : "midi_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 655.0, 410.0, 20.0 ],
					"text" : "Tonnetz vertices → MPE channels 2–16; phase → 14-bit bend"
				}

			}
, 			{
				"box" : 				{
					"id" : "print",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 620.0, 195.0, 150.0, 22.0 ],
					"text" : "print QMW_SYNTHESIS"
				}

			}
, 			{
				"box" : 				{
					"id" : "op_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 330.0, 130.0, 20.0 ],
					"text" : "operation count"
				}

			}
, 			{
				"box" : 				{
					"id" : "op_count",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 30.0, 360.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "audio_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 400.0, 340.0, 20.0 ],
					"text" : "MIDI now follows the simulated quantum-state trajectory"
				}

			}
, 			{
				"box" : 				{
					"id" : "basis_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 435.0, 95.0, 20.0 ],
					"text" : "expected basis"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "basis_value",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 30.0, 458.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "dominant_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 120.0, 435.0, 70.0, 20.0 ],
					"text" : "dominant"
				}

			}
, 			{
				"box" : 				{
					"id" : "dominant_value",
					"maxclass" : "number",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 120.0, 458.0, 55.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "coherence_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 190.0, 435.0, 75.0, 20.0 ],
					"text" : "coherence"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "coherence_value",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 190.0, 458.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "entropy_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 270.0, 435.0, 90.0, 20.0 ],
					"text" : "population H"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "entropy_value",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 270.0, 458.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "entanglement_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 350.0, 435.0, 90.0, 20.0 ],
					"text" : "entanglement"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "entanglement_value",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 350.0, 458.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "phase_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 430.0, 435.0, 90.0, 20.0 ],
					"text" : "relative phase"
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
					"patching_rect" : [ 430.0, 458.0, 70.0, 22.0 ]
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "osc_pack", 0 ],
					"source" : [ "clifford", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "osc_pack", 0 ],
					"source" : [ "evolution", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "basis_value", 0 ],
					"source" : [ "gate_unpack", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "coherence_value", 0 ],
					"source" : [ "gate_unpack", 9 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dominant_value", 0 ],
					"source" : [ "gate_unpack", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "entanglement_value", 0 ],
					"source" : [ "gate_unpack", 11 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "entropy_value", 0 ],
					"source" : [ "gate_unpack", 10 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gate_label", 1 ],
					"source" : [ "gate_unpack", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "phase_value", 0 ],
					"source" : [ "gate_unpack", 12 ]
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
					"destination" : [ "makenote", 2 ],
					"source" : [ "midi_duration", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "makenote", 0 ],
					"source" : [ "midi_pitch", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "makenote", 1 ],
					"source" : [ "midi_velocity", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "send", 0 ],
					"source" : [ "osc_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "osc_pack", 0 ],
					"source" : [ "permutation", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "osc_pack", 0 ],
					"source" : [ "qft", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "print", 0 ],
					"order" : 0,
					"source" : [ "receive", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "route_qmw", 0 ],
					"order" : 1,
					"source" : [ "receive", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "op_count", 0 ],
					"source" : [ "route_circuit", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "route_load", 0 ],
					"source" : [ "route_circuit", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "error", 1 ],
					"source" : [ "route_demo", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gate_unpack", 0 ],
					"source" : [ "route_demo", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "state_unpack", 0 ],
					"source" : [ "route_demo", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "summary", 1 ],
					"source" : [ "route_demo", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "route_circuit", 0 ],
					"source" : [ "route_domain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "route_synthesis", 0 ],
					"source" : [ "route_domain", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "accepted", 1 ],
					"source" : [ "route_load", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "error", 1 ],
					"source" : [ "route_load", 1 ]
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
					"destination" : [ "route_demo", 0 ],
					"source" : [ "route_synthesis", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "makenote", 3 ],
					"order" : 1,
					"source" : [ "state_unpack", 10 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "midi_duration", 0 ],
					"source" : [ "state_unpack", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "midi_pitch", 0 ],
					"source" : [ "state_unpack", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "midi_velocity", 0 ],
					"source" : [ "state_unpack", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "xbendout", 1 ],
					"order" : 0,
					"source" : [ "state_unpack", 10 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "xbendout", 0 ],
					"source" : [ "state_unpack", 9 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "midiout", 0 ],
					"source" : [ "xbendout", 0 ]
				}

			}
 ],
		"originid" : "pat-278",
		"dependency_cache" : [ 			{
				"name" : "OSC-route.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "o.pack.mxo",
				"type" : "iLaX"
			}
 ],
		"autosave" : 0
	}

}
