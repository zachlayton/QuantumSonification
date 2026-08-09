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
		"rect" : [ 73.0, 100.0, 1209.0, 766.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 20.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 28.0, 16.0, 1200.0, 29.0 ],
					"text" : "QMW · PAULI BASIS LABORATORY v3 · REPRESENTATION COMPARATOR",
					"textcolor" : [ 0.12, 0.82, 0.92, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 12.0,
					"id" : "subtitle",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 48.0, 1540.0, 20.0 ],
					"text" : "One canonical density matrix · two simultaneous 81-setting tomographies · unchanged 255-Pauli synthesis contract"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 10.0,
					"id" : "launch",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 76.0, 1540.0, 18.0 ],
					"text" : "Start: /Users/zlayton/miniconda3/envs/music/bin/python workshop_lightweight/qmw_pauli_basis_laboratory_v3.py --save-dir qmw_pauli_basis_laboratory_v3/runs",
					"textcolor" : [ 0.68, 0.7, 0.75, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "ghz_qft",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 30.0, 106.0, 138.0, 22.0 ],
					"text" : "ghz qft 256 23"
				}

			}
, 			{
				"box" : 				{
					"id" : "ghz_hadamard",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 178.0, 106.0, 172.0, 22.0 ],
					"text" : "ghz hadamard 256 23"
				}

			}
, 			{
				"box" : 				{
					"id" : "ghz_hamiltonian",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 360.0, 106.0, 190.0, 22.0 ],
					"text" : "ghz hamiltonian 256 23"
				}

			}
, 			{
				"box" : 				{
					"id" : "weave_qft",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 560.0, 106.0, 148.0, 22.0 ],
					"text" : "weave qft 256 23"
				}

			}
, 			{
				"box" : 				{
					"id" : "identity",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 718.0, 106.0, 168.0, 22.0 ],
					"text" : "ghz identity 256 23"
				}

			}
, 			{
				"box" : 				{
					"id" : "opack_run",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 906.0, 106.0, 184.0, 22.0 ],
					"text" : "o.pack /qmw/basis/run"
				}

			}
, 			{
				"box" : 				{
					"id" : "udpsend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1106.0, 106.0, 164.0, 22.0 ],
					"text" : "udpsend 127.0.0.1 7435"
				}

			}
, 			{
				"box" : 				{
					"id" : "ping",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1290.0, 106.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "opack_ping",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 1328.0, 106.0, 190.0, 22.0 ],
					"text" : "o.pack /qmw/basis/ping"
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 30.0, 140.0, 1540.0, 22.0 ],
					"text" : "Start the v3 Python service, then choose a basis comparison."
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 13.0,
					"id" : "computational_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 180.0, 760.0, 21.0 ],
					"text" : "COMPUTATIONAL REPRESENTATION · Identity(ρ)",
					"textcolor" : [ 0.12, 0.82, 0.92, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 13.0,
					"id" : "experimental_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 830.0, 180.0, 760.0, 21.0 ],
					"text" : "EXPERIMENTAL REPRESENTATION · UρU†",
					"textcolor" : [ 0.78, 0.32, 0.88, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "computational_heatmap",
					"maxclass" : "jit.pwindow",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "jit_matrix", "" ],
					"patching_rect" : [ 30.0, 204.0, 760.0, 250.0 ],
					"sync" : 1
				}

			}
, 			{
				"box" : 				{
					"id" : "experimental_heatmap",
					"maxclass" : "jit.pwindow",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "jit_matrix", "" ],
					"patching_rect" : [ 830.0, 204.0, 760.0, 250.0 ],
					"sync" : 1
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "select_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 468.0, 230.0, 19.0 ],
					"text" : "SYNCHRONIZED SETTING / Y (0–80)",
					"textcolor" : [ 0.9, 0.72, 0.22, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "select",
					"maxclass" : "flonum",
					"maximum" : 80.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 270.0, 466.0, 76.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_select",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 358.0, 466.0, 100.0, 22.0 ],
					"text" : "prepend select"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "mix_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 500.0, 468.0, 360.0, 19.0 ],
					"text" : "COMPUTATIONAL  ← AUDIO CROSSFADE →  EXPERIMENTAL",
					"textcolor" : [ 0.12, 0.82, 0.92, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "mix",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 875.0, 466.0, 82.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "difference_mode",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 990.0, 466.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "difference_mode_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1024.0, 468.0, 360.0, 19.0 ],
					"text" : "DIFFERENCE ONLY · experimental − computational",
					"textcolor" : [ 0.96, 0.56, 0.18, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 10.0,
					"id" : "computational_hist_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 506.0, 760.0, 18.0 ],
					"text" : "Selected row · 16 computational-basis probabilities"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 10.0,
					"id" : "experimental_hist_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 830.0, 506.0, 760.0, 18.0 ],
					"text" : "Selected row · 16 experimental-basis probabilities"
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
					"id" : "computational_histogram",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 30.0, 528.0, 760.0, 90.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"setstyle" : 1,
					"size" : 16,
					"slidercolor" : [ 0.12, 0.82, 0.92, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
					"id" : "experimental_histogram",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 830.0, 528.0, 760.0, 90.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"setstyle" : 1,
					"size" : 16,
					"slidercolor" : [ 0.78, 0.32, 0.88, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 10.0,
					"id" : "computational_pauli_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 634.0, 760.0, 18.0 ],
					"text" : "COMPUTATIONAL · 255 non-identity Pauli coefficients",
					"textcolor" : [ 0.9, 0.72, 0.22, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 10.0,
					"id" : "experimental_pauli_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 830.0, 634.0, 760.0, 18.0 ],
					"text" : "EXPERIMENTAL · 255 non-identity Pauli coefficients",
					"textcolor" : [ 0.9, 0.72, 0.22, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
					"id" : "computational_paulis",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 30.0, 656.0, 760.0, 116.0 ],
					"setstyle" : 1,
					"size" : 255,
					"slidercolor" : [ 0.12, 0.82, 0.92, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
					"id" : "experimental_paulis",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 830.0, 656.0, 760.0, 116.0 ],
					"setstyle" : 1,
					"size" : 255,
					"slidercolor" : [ 0.78, 0.32, 0.88, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 10.0,
					"id" : "difference_pauli_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 788.0, 1200.0, 18.0 ],
					"text" : "REPRESENTATION RESIDUE · 255 Pauli deltas (experimental − computational, range −2…+2)",
					"textcolor" : [ 0.96, 0.56, 0.18, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
					"id" : "difference_paulis",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 30.0, 810.0, 1560.0, 86.0 ],
					"setminmax" : [ -2.0, 2.0 ],
					"setstyle" : 1,
					"size" : 255,
					"slidercolor" : [ 0.96, 0.56, 0.18, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 10.0,
					"id" : "computational_shell_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 910.0, 500.0, 18.0 ],
					"text" : "COMPUTATIONAL correlation shells · weights 0–4"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 10.0,
					"id" : "experimental_shell_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 830.0, 910.0, 500.0, 18.0 ],
					"text" : "EXPERIMENTAL correlation shells · weights 0–4"
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
					"id" : "computational_shells",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 30.0, 932.0, 500.0, 62.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"setstyle" : 1,
					"size" : 5,
					"slidercolor" : [ 0.12, 0.82, 0.92, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
					"id" : "experimental_shells",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 830.0, 932.0, 500.0, 62.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"setstyle" : 1,
					"size" : 5,
					"slidercolor" : [ 0.78, 0.32, 0.88, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "buffer_computational",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 30.0, 1014.0, 330.0, 22.0 ],
					"text" : "buffer~ qmw_basis_computational_v3_2d @samps 20736"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "buffer_experimental",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 30.0, 1044.0, 330.0, 22.0 ],
					"text" : "buffer~ qmw_basis_experimental_v3_2d @samps 20736"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "frequency",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1362.0, 932.0, 76.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "phasor",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 480.0, 1028.0, 78.0, 22.0 ],
					"text" : "phasor~ 110."
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "select_norm",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 570.0, 1028.0, 154.0, 22.0 ],
					"text" : "expr ($f1 + 0.5) / 81."
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "select_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 738.0, 1028.0, 86.0, 22.0 ],
					"text" : "pack 0. 80"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "select_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 838.0, 1028.0, 48.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "wave_computational",
					"maxclass" : "newobj",
					"numinlets" : 4,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 910.0, 1010.0, 300.0, 22.0 ],
					"text" : "2d.wave~ qmw_basis_computational_v3_2d 0. 0. 1 81"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "wave_experimental",
					"maxclass" : "newobj",
					"numinlets" : 4,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 910.0, 1050.0, 300.0, 22.0 ],
					"text" : "2d.wave~ qmw_basis_experimental_v3_2d 0. 0. 1 81"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "mix_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 390.0, 1080.0, 86.0, 22.0 ],
					"text" : "pack 0. 80"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "mix_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 490.0, 1080.0, 48.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "comp_phase",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 550.0, 1070.0, 58.0, 22.0 ],
					"text" : "*~ 0.25"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "comp_gain",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 620.0, 1070.0, 48.0, 22.0 ],
					"text" : "cos~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "exp_invert",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 550.0, 1110.0, 58.0, 22.0 ],
					"text" : "!-~ 1."
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "exp_phase",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 620.0, 1110.0, 58.0, 22.0 ],
					"text" : "*~ 0.25"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "exp_gain",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 680.0, 1110.0, 48.0, 22.0 ],
					"text" : "cos~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "comp_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1230.0, 1010.0, 46.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "exp_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1230.0, 1050.0, 46.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "normal_sum",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1290.0, 1030.0, 46.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "difference_sub",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1230.0, 1090.0, 46.0, 22.0 ],
					"text" : "-~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "mode_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 760.0, 1090.0, 86.0, 22.0 ],
					"text" : "pack 0. 60"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "mode_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 860.0, 1090.0, 48.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "mode_invert",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 920.0, 1090.0, 58.0, 22.0 ],
					"text" : "!-~ 1."
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "normal_mode_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1290.0, 1070.0, 46.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "difference_mode_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1290.0, 1110.0, 46.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "mode_sum",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1350.0, 1090.0, 46.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1410.0, 1090.0, 58.0, 22.0 ],
					"text" : "*~ 0.12"
				}

			}
, 			{
				"box" : 				{
					"id" : "dac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 1358.0, 966.0, 52.0, 36.0 ]
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "load_frequency",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 30.0, 1090.0, 88.0, 22.0 ],
					"text" : "loadmess 110."
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "load_select",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 130.0, 1090.0, 78.0, 22.0 ],
					"text" : "loadmess 0."
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "load_mix",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 220.0, 1090.0, 80.0, 22.0 ],
					"text" : "loadmess 0.5"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "load_difference",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 310.0, 1090.0, 70.0, 22.0 ],
					"text" : "loadmess 0"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "receiver",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 10,
					"outlettype" : [ "", "", "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 30.0, 1160.0, 300.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_pauli_basis_laboratory_receiver_v3.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_pauli_basis_laboratory_receiver_v3.js"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "udpreceive",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 350.0, 1160.0, 140.0, 22.0 ],
					"text" : "udpreceive 7436"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 9,
					"outlettype" : [ "", "", "", "", "", "", "", "", "FullPacket" ],
					"patching_rect" : [ 510.0, 1160.0, 1093.0, 22.0 ],
					"text" : "o.route /qmw/tomography/begin /qmw/tomography/setting /qmw/tomography/pauli /qmw/tomography/shell /qmw/tomography/metrics /qmw/tomography/end /qmw/tomography/status /qmw/tomography/error"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "prepend_begin",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 510.0, 1190.0, 100.0, 22.0 ],
					"text" : "prepend begin"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "prepend_setting",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 620.0, 1190.0, 100.0, 22.0 ],
					"text" : "prepend setting"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "prepend_pauli",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 730.0, 1190.0, 100.0, 22.0 ],
					"text" : "prepend pauli"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "prepend_shell",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 840.0, 1190.0, 100.0, 22.0 ],
					"text" : "prepend shell"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "prepend_metrics",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 950.0, 1190.0, 100.0, 22.0 ],
					"text" : "prepend metrics"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "prepend_end",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1060.0, 1190.0, 100.0, 22.0 ],
					"text" : "prepend end"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "prepend_status",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1170.0, 1190.0, 100.0, 22.0 ],
					"text" : "prepend status"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "prepend_error",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1280.0, 1190.0, 100.0, 22.0 ],
					"text" : "prepend error"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "comp_mul", 1 ],
					"hidden" : 1,
					"source" : [ "comp_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "normal_sum", 0 ],
					"hidden" : 1,
					"source" : [ "comp_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "comp_gain", 0 ],
					"hidden" : 1,
					"source" : [ "comp_phase", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_pack", 0 ],
					"hidden" : 1,
					"source" : [ "difference_mode", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_sum", 1 ],
					"hidden" : 1,
					"source" : [ "difference_mode_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "difference_mode_mul", 0 ],
					"hidden" : 1,
					"source" : [ "difference_sub", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "exp_mul", 1 ],
					"hidden" : 1,
					"source" : [ "exp_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "exp_phase", 0 ],
					"hidden" : 1,
					"source" : [ "exp_invert", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "normal_sum", 1 ],
					"hidden" : 1,
					"source" : [ "exp_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "exp_gain", 0 ],
					"hidden" : 1,
					"source" : [ "exp_phase", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "phasor", 0 ],
					"hidden" : 1,
					"source" : [ "frequency", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 1 ],
					"hidden" : 1,
					"order" : 0,
					"source" : [ "gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"hidden" : 1,
					"order" : 1,
					"source" : [ "gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_run", 0 ],
					"source" : [ "ghz_hadamard", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_run", 0 ],
					"source" : [ "ghz_hamiltonian", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_run", 0 ],
					"source" : [ "ghz_qft", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_run", 0 ],
					"source" : [ "identity", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "difference_mode", 0 ],
					"hidden" : 1,
					"source" : [ "load_difference", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "frequency", 0 ],
					"hidden" : 1,
					"source" : [ "load_frequency", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mix", 0 ],
					"hidden" : 1,
					"source" : [ "load_mix", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "select", 0 ],
					"hidden" : 1,
					"source" : [ "load_select", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mix_pack", 0 ],
					"hidden" : 1,
					"source" : [ "mix", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "comp_phase", 0 ],
					"hidden" : 1,
					"order" : 1,
					"source" : [ "mix_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "exp_invert", 0 ],
					"hidden" : 1,
					"order" : 0,
					"source" : [ "mix_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mix_line", 0 ],
					"hidden" : 1,
					"source" : [ "mix_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "normal_mode_mul", 1 ],
					"hidden" : 1,
					"source" : [ "mode_invert", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "difference_mode_mul", 1 ],
					"hidden" : 1,
					"order" : 0,
					"source" : [ "mode_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_invert", 0 ],
					"hidden" : 1,
					"order" : 1,
					"source" : [ "mode_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_line", 0 ],
					"hidden" : 1,
					"source" : [ "mode_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain", 0 ],
					"hidden" : 1,
					"source" : [ "mode_sum", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mode_sum", 0 ],
					"hidden" : 1,
					"source" : [ "normal_mode_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "normal_mode_mul", 0 ],
					"hidden" : 1,
					"source" : [ "normal_sum", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "udpsend", 0 ],
					"source" : [ "opack_ping", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "udpsend", 0 ],
					"source" : [ "opack_run", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_computational", 0 ],
					"hidden" : 1,
					"order" : 1,
					"source" : [ "phasor", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_experimental", 0 ],
					"hidden" : 1,
					"order" : 0,
					"source" : [ "phasor", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_ping", 0 ],
					"source" : [ "ping", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "prepend_begin", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "prepend_end", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "prepend_error", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "prepend_metrics", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "prepend_pauli", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "prepend_select", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "prepend_setting", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "prepend_shell", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "prepend_status", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "computational_heatmap", 0 ],
					"hidden" : 1,
					"source" : [ "receiver", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "computational_histogram", 0 ],
					"hidden" : 1,
					"source" : [ "receiver", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "computational_paulis", 0 ],
					"hidden" : 1,
					"source" : [ "receiver", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "computational_shells", 0 ],
					"hidden" : 1,
					"source" : [ "receiver", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "difference_paulis", 0 ],
					"hidden" : 1,
					"source" : [ "receiver", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "experimental_heatmap", 0 ],
					"hidden" : 1,
					"source" : [ "receiver", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "experimental_histogram", 0 ],
					"hidden" : 1,
					"source" : [ "receiver", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "experimental_paulis", 0 ],
					"hidden" : 1,
					"source" : [ "receiver", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "experimental_shells", 0 ],
					"hidden" : 1,
					"source" : [ "receiver", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 0 ],
					"hidden" : 1,
					"source" : [ "receiver", 9 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_begin", 0 ],
					"hidden" : 1,
					"source" : [ "route", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_end", 0 ],
					"hidden" : 1,
					"source" : [ "route", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_error", 0 ],
					"hidden" : 1,
					"source" : [ "route", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_metrics", 0 ],
					"hidden" : 1,
					"source" : [ "route", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_pauli", 0 ],
					"hidden" : 1,
					"source" : [ "route", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_setting", 0 ],
					"hidden" : 1,
					"source" : [ "route", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_shell", 0 ],
					"hidden" : 1,
					"source" : [ "route", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_status", 0 ],
					"hidden" : 1,
					"source" : [ "route", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_select", 0 ],
					"order" : 1,
					"source" : [ "select", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "select_norm", 0 ],
					"hidden" : 1,
					"order" : 0,
					"source" : [ "select", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_computational", 1 ],
					"hidden" : 1,
					"order" : 1,
					"source" : [ "select_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "wave_experimental", 1 ],
					"hidden" : 1,
					"order" : 0,
					"source" : [ "select_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "select_pack", 0 ],
					"hidden" : 1,
					"source" : [ "select_norm", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "select_line", 0 ],
					"hidden" : 1,
					"source" : [ "select_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "route", 0 ],
					"hidden" : 1,
					"source" : [ "udpreceive", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "comp_mul", 0 ],
					"hidden" : 1,
					"order" : 1,
					"source" : [ "wave_computational", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "difference_sub", 1 ],
					"hidden" : 1,
					"order" : 0,
					"source" : [ "wave_computational", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "difference_sub", 0 ],
					"hidden" : 1,
					"order" : 0,
					"source" : [ "wave_experimental", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "exp_mul", 0 ],
					"hidden" : 1,
					"order" : 1,
					"source" : [ "wave_experimental", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_run", 0 ],
					"source" : [ "weave_qft", 0 ]
				}

			}
 ],
		"originid" : "pat-8",
		"dependency_cache" : [ 			{
				"name" : "o.pack.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "o.route.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "qmw_pauli_basis_laboratory_receiver_v3.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
