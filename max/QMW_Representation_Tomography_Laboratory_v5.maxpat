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
		"rect" : [ 55.0, 105.0, 1444.0, 816.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"autofit" : 1,
					"forceaspect" : 1,
					"id" : "obj-3",
					"maxclass" : "fpic",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "jit_matrix" ],
					"patching_rect" : [ 1154.0, 177.0, 289.0, 57.10361445783132 ],
					"pic" : "/var/folders/sb/rmflyp5n0llgt6lhsysqww6r0000gp/T/TemporaryItems/NSIRD_screencaptureui_HfnROU/Screenshot 2026-07-25 at 8.50.31 PM.png"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 13.0,
					"id" : "computational_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 310.0, 760.0, 21.0 ],
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
					"patching_rect" : [ 830.0, 310.0, 760.0, 21.0 ],
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
					"patching_rect" : [ 30.0, 334.0, 760.0, 250.0 ],
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
					"patching_rect" : [ 830.0, 334.0, 760.0, 250.0 ],
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
					"patching_rect" : [ 30.0, 598.0, 230.0, 19.0 ],
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
					"patching_rect" : [ 270.0, 596.0, 76.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_select",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 358.0, 596.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 500.0, 598.0, 360.0, 19.0 ],
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
					"patching_rect" : [ 875.0, 596.0, 82.0, 22.0 ]
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
					"patching_rect" : [ 990.0, 596.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "difference_mode_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1024.0, 598.0, 360.0, 19.0 ],
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
					"patching_rect" : [ 30.0, 636.0, 760.0, 18.0 ],
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
					"patching_rect" : [ 830.0, 636.0, 760.0, 18.0 ],
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
					"patching_rect" : [ 30.0, 658.0, 760.0, 90.0 ],
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
					"patching_rect" : [ 830.0, 658.0, 760.0, 90.0 ],
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
					"patching_rect" : [ 30.0, 764.0, 760.0, 18.0 ],
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
					"patching_rect" : [ 830.0, 764.0, 760.0, 18.0 ],
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
					"patching_rect" : [ 30.0, 786.0, 760.0, 116.0 ],
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
					"patching_rect" : [ 830.0, 786.0, 760.0, 116.0 ],
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
					"patching_rect" : [ 30.0, 918.0, 1200.0, 18.0 ],
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
					"patching_rect" : [ 30.0, 940.0, 1560.0, 86.0 ],
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
					"patching_rect" : [ 30.0, 1040.0, 500.0, 18.0 ],
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
					"patching_rect" : [ 830.0, 1040.0, 500.0, 18.0 ],
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
					"patching_rect" : [ 30.0, 1062.0, 500.0, 62.0 ],
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
					"patching_rect" : [ 830.0, 1062.0, 500.0, 62.0 ],
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
					"patching_rect" : [ 30.0, 1144.0, 330.0, 22.0 ],
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
					"patching_rect" : [ 30.0, 1174.0, 330.0, 22.0 ],
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
					"patching_rect" : [ 714.0, 1095.0, 76.0, 22.0 ]
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
					"patching_rect" : [ 480.0, 1158.0, 78.0, 22.0 ],
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
					"patching_rect" : [ 570.0, 1158.0, 154.0, 22.0 ],
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
					"patching_rect" : [ 738.0, 1158.0, 86.0, 22.0 ],
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
					"patching_rect" : [ 838.0, 1158.0, 48.0, 22.0 ],
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
					"patching_rect" : [ 910.0, 1140.0, 300.0, 22.0 ],
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
					"patching_rect" : [ 910.0, 1180.0, 300.0, 22.0 ],
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
					"patching_rect" : [ 390.0, 1210.0, 86.0, 22.0 ],
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
					"patching_rect" : [ 490.0, 1210.0, 48.0, 22.0 ],
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
					"patching_rect" : [ 550.0, 1200.0, 58.0, 22.0 ],
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
					"patching_rect" : [ 620.0, 1200.0, 48.0, 22.0 ],
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
					"patching_rect" : [ 550.0, 1240.0, 58.0, 22.0 ],
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
					"patching_rect" : [ 620.0, 1240.0, 58.0, 22.0 ],
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
					"patching_rect" : [ 680.0, 1240.0, 48.0, 22.0 ],
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
					"patching_rect" : [ 1230.0, 1140.0, 46.0, 22.0 ],
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
					"patching_rect" : [ 1230.0, 1180.0, 46.0, 22.0 ],
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
					"patching_rect" : [ 1290.0, 1160.0, 46.0, 22.0 ],
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
					"patching_rect" : [ 1230.0, 1220.0, 46.0, 22.0 ],
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
					"patching_rect" : [ 760.0, 1220.0, 86.0, 22.0 ],
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
					"patching_rect" : [ 860.0, 1220.0, 48.0, 22.0 ],
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
					"patching_rect" : [ 920.0, 1220.0, 58.0, 22.0 ],
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
					"patching_rect" : [ 1290.0, 1200.0, 46.0, 22.0 ],
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
					"patching_rect" : [ 1290.0, 1240.0, 46.0, 22.0 ],
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
					"patching_rect" : [ 1350.0, 1220.0, 46.0, 22.0 ],
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
					"patching_rect" : [ 1410.0, 1220.0, 58.0, 22.0 ],
					"text" : "*~ 0.12"
				}

			}
, 			{
				"box" : 				{
					"id" : "dac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 717.0, 1054.0, 52.0, 36.0 ]
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
					"patching_rect" : [ 30.0, 1220.0, 88.0, 22.0 ],
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
					"patching_rect" : [ 130.0, 1220.0, 78.0, 22.0 ],
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
					"patching_rect" : [ 220.0, 1220.0, 80.0, 22.0 ],
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
					"patching_rect" : [ 310.0, 1220.0, 70.0, 22.0 ],
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
					"patching_rect" : [ 30.0, 1290.0, 300.0, 22.0 ],
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
					"patching_rect" : [ 350.0, 1290.0, 140.0, 22.0 ],
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
					"patching_rect" : [ 510.0, 1290.0, 1093.0, 22.0 ],
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
					"patching_rect" : [ 510.0, 1320.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 620.0, 1320.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 730.0, 1320.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 840.0, 1320.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 950.0, 1320.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 1060.0, 1320.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 1170.0, 1320.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 1280.0, 1320.0, 100.0, 22.0 ],
					"text" : "prepend error"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 20.0,
					"id" : "v5_title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 28.0, 14.0, 1100.0, 29.0 ],
					"text" : "QMW · REPRESENTATION LABORATORY v5 · LIVE TRANSFORM INSTRUMENT",
					"textcolor" : [ 0.12, 0.82, 0.92, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "v5_launch",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 48.0, 1500.0, 20.0 ],
					"text" : "Run only: python workshop_lightweight/qmw_representation_laboratory_v5.py",
					"textcolor" : [ 0.68, 0.7, 0.75, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"bgmode" : 0,
					"border" : 1,
					"clickthrough" : 0,
					"embed" : 1,
					"enablehscroll" : 0,
					"enablevscroll" : 0,
					"id" : "transform_controls",
					"lockeddragscroll" : 0,
					"lockedsize" : 0,
					"maxclass" : "bpatcher",
					"name" : "QMW_Transform_Control_v5.maxpat",
					"numinlets" : 0,
					"numoutlets" : 0,
					"offset" : [ 0.0, 0.0 ],
					"patcher" : 					{
						"fileversion" : 1,
						"appversion" : 						{
							"major" : 9,
							"minor" : 0,
							"revision" : 5,
							"architecture" : "x64",
							"modernui" : 1
						}
,
						"classnamespace" : "box",
						"rect" : [ 40.0, 50.0, 1560.0, 360.0 ],
						"openinpresentation" : 1,
						"gridsize" : [ 15.0, 15.0 ],
						"boxes" : [ 							{
								"box" : 								{
									"background" : 1,
									"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
									"border" : 1,
									"id" : "panel",
									"maxclass" : "panel",
									"mode" : 0,
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 0.0, 0.0, 1540.0, 180.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 0.0, 0.0, 1540.0, 180.0 ]
								}

							}
, 							{
								"box" : 								{
									"fontsize" : 15.0,
									"id" : "heading",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 16.0, 8.0, 420.0, 23.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 16.0, 8.0, 420.0, 23.0 ],
									"text" : "REPRESENTATION TRANSFORM",
									"textcolor" : [ 0.12, 0.82, 0.92, 1.0 ]
								}

							}
, 							{
								"box" : 								{
									"id" : "j_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 16.0, 42.0, 42.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 16.0, 42.0, 42.0, 20.0 ],
									"text" : "J"
								}

							}
, 							{
								"box" : 								{
									"format" : 6,
									"id" : "j",
									"maxclass" : "flonum",
									"maximum" : 4.0,
									"minimum" : -4.0,
									"numinlets" : 1,
									"numoutlets" : 2,
									"outlettype" : [ "", "bang" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 60.0, 38.0, 78.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 60.0, 38.0, 78.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_longname" : "hamiltonian_j",
											"parameter_mmax" : 4.0,
											"parameter_mmin" : -4.0,
											"parameter_modmode" : 0,
											"parameter_shortname" : "hamiltonian_j",
											"parameter_type" : 0
										}

									}
,
									"varname" : "hamiltonian_j"
								}

							}
, 							{
								"box" : 								{
									"id" : "ht_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 146.0, 42.0, 42.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 146.0, 42.0, 42.0, 20.0 ],
									"text" : "h⊥"
								}

							}
, 							{
								"box" : 								{
									"format" : 6,
									"id" : "ht",
									"maxclass" : "flonum",
									"maximum" : 4.0,
									"minimum" : -4.0,
									"numinlets" : 1,
									"numoutlets" : 2,
									"outlettype" : [ "", "bang" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 190.0, 38.0, 78.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 190.0, 38.0, 78.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_longname" : "hamiltonian_ht",
											"parameter_mmax" : 4.0,
											"parameter_mmin" : -4.0,
											"parameter_modmode" : 0,
											"parameter_shortname" : "hamiltonian_ht",
											"parameter_type" : 0
										}

									}
,
									"varname" : "hamiltonian_ht"
								}

							}
, 							{
								"box" : 								{
									"id" : "hl_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 276.0, 42.0, 42.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 276.0, 42.0, 42.0, 20.0 ],
									"text" : "h∥"
								}

							}
, 							{
								"box" : 								{
									"format" : 6,
									"id" : "hl",
									"maxclass" : "flonum",
									"maximum" : 4.0,
									"minimum" : -4.0,
									"numinlets" : 1,
									"numoutlets" : 2,
									"outlettype" : [ "", "bang" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 320.0, 38.0, 78.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 320.0, 38.0, 78.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_longname" : "hamiltonian_hl",
											"parameter_mmax" : 4.0,
											"parameter_mmin" : -4.0,
											"parameter_modmode" : 0,
											"parameter_shortname" : "hamiltonian_hl",
											"parameter_type" : 0
										}

									}
,
									"varname" : "hamiltonian_hl"
								}

							}
, 							{
								"box" : 								{
									"id" : "time_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 406.0, 42.0, 42.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 406.0, 42.0, 42.0, 20.0 ],
									"text" : "time"
								}

							}
, 							{
								"box" : 								{
									"format" : 6,
									"id" : "time",
									"maxclass" : "flonum",
									"maximum" : 100.0,
									"minimum" : -100.0,
									"numinlets" : 1,
									"numoutlets" : 2,
									"outlettype" : [ "", "bang" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 450.0, 38.0, 78.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 450.0, 38.0, 78.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_longname" : "hamiltonian_time",
											"parameter_mmax" : 100.0,
											"parameter_mmin" : -100.0,
											"parameter_modmode" : 0,
											"parameter_shortname" : "hamiltonian_time",
											"parameter_type" : 0
										}

									}
,
									"varname" : "hamiltonian_time"
								}

							}
, 							{
								"box" : 								{
									"id" : "transform_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 552.0, 42.0, 68.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 552.0, 42.0, 68.0, 20.0 ],
									"text" : "transform"
								}

							}
, 							{
								"box" : 								{
									"id" : "transform",
									"items" : [ "identity", ",", "hadamard", ",", "qft", ",", "inverse_qft", ",", "hamiltonian", ",", "graph_laplacian", ",", "floquet", ",", "grover_amplified", ",", "epistrophe" ],
									"maxclass" : "umenu",
									"numinlets" : 1,
									"numoutlets" : 3,
									"outlettype" : [ "int", "", "" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 622.0, 38.0, 220.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 622.0, 38.0, 220.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_enum" : [ "identity", "hadamard", "qft", "inverse_qft", "hamiltonian", "graph_laplacian", "floquet", "grover_amplified", "epistrophe" ],
											"parameter_longname" : "representation_transform",
											"parameter_mmax" : 8,
											"parameter_modmode" : 0,
											"parameter_shortname" : "representation_transform",
											"parameter_type" : 2
										}

									}
,
									"varname" : "representation_transform"
								}

							}
, 							{
								"box" : 								{
									"id" : "boundary_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 858.0, 42.0, 72.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 858.0, 42.0, 72.0, 20.0 ],
									"text" : "boundary"
								}

							}
, 							{
								"box" : 								{
									"id" : "boundary",
									"items" : [ "open", ",", "periodic" ],
									"maxclass" : "umenu",
									"numinlets" : 1,
									"numoutlets" : 3,
									"outlettype" : [ "int", "", "" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 932.0, 38.0, 114.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 932.0, 38.0, 114.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_enum" : [ "open", "periodic" ],
											"parameter_longname" : "hamiltonian_boundary",
											"parameter_mmax" : 1,
											"parameter_modmode" : 0,
											"parameter_shortname" : "hamiltonian_boundary",
											"parameter_type" : 2
										}

									}
,
									"varname" : "hamiltonian_boundary"
								}

							}
, 							{
								"box" : 								{
									"id" : "preset_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 16.0, 88.0, 48.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 16.0, 88.0, 48.0, 20.0 ],
									"text" : "state"
								}

							}
, 							{
								"box" : 								{
									"id" : "preset",
									"items" : [ "ghz", ",", "bell", ",", "weave" ],
									"maxclass" : "umenu",
									"numinlets" : 1,
									"numoutlets" : 3,
									"outlettype" : [ "int", "", "" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 66.0, 84.0, 154.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 66.0, 84.0, 154.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_enum" : [ "ghz", "bell", "weave" ],
											"parameter_longname" : "hamiltonian_preset",
											"parameter_mmax" : 2,
											"parameter_modmode" : 0,
											"parameter_shortname" : "hamiltonian_preset",
											"parameter_type" : 2
										}

									}
,
									"varname" : "hamiltonian_preset"
								}

							}
, 							{
								"box" : 								{
									"id" : "shots_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 238.0, 88.0, 46.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 238.0, 88.0, 46.0, 20.0 ],
									"text" : "shots"
								}

							}
, 							{
								"box" : 								{
									"id" : "shots",
									"maxclass" : "number",
									"minimum" : 1,
									"numinlets" : 1,
									"numoutlets" : 2,
									"outlettype" : [ "", "bang" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 286.0, 84.0, 66.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 286.0, 84.0, 66.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_invisible" : 1,
											"parameter_longname" : "hamiltonian_shots",
											"parameter_modmode" : 0,
											"parameter_shortname" : "hamiltonian_shots",
											"parameter_type" : 3
										}

									}
,
									"varname" : "hamiltonian_shots"
								}

							}
, 							{
								"box" : 								{
									"id" : "sampling_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 370.0, 88.0, 68.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 370.0, 88.0, 68.0, 20.0 ],
									"text" : "sampling"
								}

							}
, 							{
								"box" : 								{
									"id" : "sampling",
									"items" : [ "fixed", ",", "resample", ",", "sequence" ],
									"maxclass" : "umenu",
									"numinlets" : 1,
									"numoutlets" : 3,
									"outlettype" : [ "int", "", "" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 440.0, 84.0, 198.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 440.0, 84.0, 198.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_enum" : [ "fixed", "resample", "sequence" ],
											"parameter_longname" : "hamiltonian_sampling",
											"parameter_mmax" : 2,
											"parameter_modmode" : 0,
											"parameter_shortname" : "hamiltonian_sampling",
											"parameter_type" : 2
										}

									}
,
									"varname" : "hamiltonian_sampling"
								}

							}
, 							{
								"box" : 								{
									"id" : "seed_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 656.0, 88.0, 38.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 656.0, 88.0, 38.0, 20.0 ],
									"text" : "seed"
								}

							}
, 							{
								"box" : 								{
									"id" : "seed",
									"maxclass" : "number",
									"minimum" : 0,
									"numinlets" : 1,
									"numoutlets" : 2,
									"outlettype" : [ "", "bang" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 696.0, 84.0, 82.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 696.0, 84.0, 82.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_invisible" : 1,
											"parameter_longname" : "hamiltonian_seed",
											"parameter_modmode" : 0,
											"parameter_shortname" : "hamiltonian_seed",
											"parameter_type" : 3
										}

									}
,
									"varname" : "hamiltonian_seed"
								}

							}
, 							{
								"box" : 								{
									"bgcolor" : [ 0.96, 0.56, 0.18, 1.0 ],
									"id" : "commit",
									"maxclass" : "textbutton",
									"numinlets" : 1,
									"numoutlets" : 3,
									"outlettype" : [ "", "", "int" ],
									"parameter_enable" : 0,
									"patching_rect" : [ 800.0, 78.0, 168.0, 36.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 800.0, 78.0, 168.0, 36.0 ],
									"text" : "COMMIT TOMOGRAPHY",
									"texton" : "COMMIT TOMOGRAPHY"
								}

							}
, 							{
								"box" : 								{
									"id" : "reset",
									"maxclass" : "message",
									"numinlets" : 2,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 982.0, 84.0, 102.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 982.0, 84.0, 102.0, 22.0 ],
									"text" : "reset tracking"
								}

							}
, 							{
								"box" : 								{
									"id" : "store1",
									"maxclass" : "message",
									"numinlets" : 2,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 1120.0, 38.0, 58.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 1120.0, 38.0, 58.0, 22.0 ],
									"text" : "store 1"
								}

							}
, 							{
								"box" : 								{
									"id" : "recall1",
									"maxclass" : "message",
									"numinlets" : 2,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 1184.0, 38.0, 34.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 1184.0, 38.0, 34.0, 22.0 ],
									"text" : "1"
								}

							}
, 							{
								"box" : 								{
									"id" : "write",
									"maxclass" : "message",
									"numinlets" : 2,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 1224.0, 38.0, 48.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 1224.0, 38.0, 48.0, 22.0 ],
									"text" : "write"
								}

							}
, 							{
								"box" : 								{
									"id" : "read",
									"maxclass" : "message",
									"numinlets" : 2,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 1278.0, 38.0, 44.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 1278.0, 38.0, 44.0, 22.0 ],
									"text" : "read"
								}

							}
, 							{
								"box" : 								{
									"id" : "preset_note",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 1120.0, 68.0, 240.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 1120.0, 68.0, 240.0, 20.0 ],
									"text" : "preset 1 · store / recall / write / read",
									"textcolor" : [ 0.7, 0.72, 0.78, 1.0 ]
								}

							}
, 							{
								"box" : 								{
									"id" : "preview_note",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 650.0, 132.0, 700.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 650.0, 132.0, 700.0, 20.0 ],
									"text" : "J / fields / time: Hamiltonian + Floquet · graph / marked / steps: operator-specific",
									"textcolor" : [ 0.96, 0.56, 0.18, 1.0 ]
								}

							}
, 							{
								"box" : 								{
									"id" : "graph_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 16.0, 136.0, 42.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 16.0, 136.0, 42.0, 20.0 ],
									"text" : "graph"
								}

							}
, 							{
								"box" : 								{
									"id" : "graph",
									"items" : [ "cycle", ",", "path", ",", "complete" ],
									"maxclass" : "umenu",
									"numinlets" : 1,
									"numoutlets" : 3,
									"outlettype" : [ "int", "", "" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 60.0, 132.0, 110.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 60.0, 132.0, 110.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_enum" : [ "cycle", "path", "complete" ],
											"parameter_longname" : "representation_graph",
											"parameter_mmax" : 2,
											"parameter_modmode" : 0,
											"parameter_shortname" : "representation_graph",
											"parameter_type" : 2
										}

									}
,
									"varname" : "representation_graph"
								}

							}
, 							{
								"box" : 								{
									"id" : "normalized_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 180.0, 136.0, 76.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 180.0, 136.0, 76.0, 20.0 ],
									"text" : "normalized"
								}

							}
, 							{
								"box" : 								{
									"id" : "normalized",
									"maxclass" : "toggle",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "int" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 258.0, 132.0, 24.0, 24.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 258.0, 132.0, 24.0, 24.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_enum" : [ "off", "on" ],
											"parameter_longname" : "representation_normalized_graph",
											"parameter_mmax" : 1,
											"parameter_modmode" : 0,
											"parameter_shortname" : "representation_normalized_graph",
											"parameter_type" : 2
										}

									}
,
									"varname" : "representation_normalized_graph"
								}

							}
, 							{
								"box" : 								{
									"id" : "marked_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 300.0, 136.0, 52.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 300.0, 136.0, 52.0, 20.0 ],
									"text" : "marked"
								}

							}
, 							{
								"box" : 								{
									"id" : "marked",
									"maxclass" : "number",
									"maximum" : 15,
									"minimum" : 0,
									"numinlets" : 1,
									"numoutlets" : 2,
									"outlettype" : [ "", "bang" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 354.0, 132.0, 54.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 354.0, 132.0, 54.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_longname" : "representation_marked_state",
											"parameter_mmax" : 15.0,
											"parameter_modmode" : 0,
											"parameter_shortname" : "representation_marked_state",
											"parameter_type" : 0
										}

									}
,
									"varname" : "representation_marked_state"
								}

							}
, 							{
								"box" : 								{
									"id" : "steps_label",
									"maxclass" : "comment",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 426.0, 136.0, 40.0, 20.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 426.0, 136.0, 40.0, 20.0 ],
									"text" : "steps"
								}

							}
, 							{
								"box" : 								{
									"id" : "steps",
									"maxclass" : "number",
									"minimum" : 0,
									"numinlets" : 1,
									"numoutlets" : 2,
									"outlettype" : [ "", "bang" ],
									"parameter_enable" : 1,
									"patching_rect" : [ 468.0, 132.0, 54.0, 22.0 ],
									"presentation" : 1,
									"presentation_rect" : [ 468.0, 132.0, 54.0, 22.0 ],
									"saved_attribute_attributes" : 									{
										"valueof" : 										{
											"parameter_invisible" : 1,
											"parameter_longname" : "representation_steps",
											"parameter_modmode" : 0,
											"parameter_shortname" : "representation_steps",
											"parameter_type" : 3
										}

									}
,
									"varname" : "representation_steps"
								}

							}
, 							{
								"box" : 								{
									"id" : "pak",
									"maxclass" : "newobj",
									"numinlets" : 15,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 20.0, 220.0, 680.0, 22.0 ],
									"text" : "pak i s f f f f s s i s i s i i i"
								}

							}
, 							{
								"box" : 								{
									"id" : "speedlim",
									"maxclass" : "newobj",
									"numinlets" : 2,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 500.0, 220.0, 90.0, 22.0 ],
									"text" : "speedlim 150"
								}

							}
, 							{
								"box" : 								{
									"id" : "preview_pack",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "FullPacket" ],
									"patching_rect" : [ 610.0, 220.0, 240.0, 22.0 ],
									"text" : "o.pack /qmw/v5/transform/preview"
								}

							}
, 							{
								"box" : 								{
									"id" : "commit_store",
									"maxclass" : "newobj",
									"numinlets" : 2,
									"numoutlets" : 2,
									"outlettype" : [ "", "" ],
									"patching_rect" : [ 20.0, 255.0, 58.0, 22.0 ],
									"text" : "zl reg"
								}

							}
, 							{
								"box" : 								{
									"id" : "commit_pack",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "FullPacket" ],
									"patching_rect" : [ 100.0, 255.0, 240.0, 22.0 ],
									"text" : "o.pack /qmw/v5/transform/commit"
								}

							}
, 							{
								"box" : 								{
									"id" : "reset_pack",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "FullPacket" ],
									"patching_rect" : [ 360.0, 255.0, 230.0, 22.0 ],
									"text" : "o.pack /qmw/v5/transform/reset_tracking"
								}

							}
, 							{
								"box" : 								{
									"id" : "send",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 0,
									"patching_rect" : [ 890.0, 220.0, 170.0, 22.0 ],
									"text" : "udpsend 127.0.0.1 7445"
								}

							}
, 							{
								"box" : 								{
									"id" : "autopattr",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 4,
									"outlettype" : [ "", "", "", "" ],
									"patching_rect" : [ 650.0, 255.0, 70.0, 22.0 ],
									"restore" : 									{
										"hamiltonian_boundary" : [ 1 ],
										"hamiltonian_hl" : [ 0.52 ],
										"hamiltonian_ht" : [ 0.45 ],
										"hamiltonian_j" : [ 0.327 ],
										"hamiltonian_preset" : [ 2 ],
										"hamiltonian_sampling" : [ 2 ],
										"hamiltonian_seed" : [ 47 ],
										"hamiltonian_shots" : [ 512 ],
										"hamiltonian_time" : [ 85.0 ],
										"representation_graph" : [ 1 ],
										"representation_marked_state" : [ 0 ],
										"representation_normalized_graph" : [ 1 ],
										"representation_steps" : [ 256 ],
										"representation_transform" : [ 1 ]
									}
,
									"text" : "autopattr",
									"varname" : "u542002905"
								}

							}
, 							{
								"box" : 								{
									"id" : "presets",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 740.0, 255.0, 310.0, 22.0 ],
									"saved_object_attributes" : 									{
										"client_rect" : [ 100, 100, 500, 600 ],
										"parameter_enable" : 0,
										"parameter_mappable" : 0,
										"storage_rect" : [ 200, 200, 800, 500 ]
									}
,
									"text" : "pattrstorage qmw_v5_transform_presets @autorestore 0",
									"varname" : "qmw_v5_transform_presets"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_j",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 20.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 0.7"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_ht",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 114.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 0.45"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_hl",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 208.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 0.13"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_time",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 302.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 1."
								}

							}
, 							{
								"box" : 								{
									"id" : "load_transform",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 396.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 4"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_boundary",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 490.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 0"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_preset",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 584.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 0"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_shots",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 678.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 256"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_sampling",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 772.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 0"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_seed",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 866.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 23"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_graph",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 960.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 0"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_normalized",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 1054.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 0"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_marked",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 1148.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 0"
								}

							}
, 							{
								"box" : 								{
									"id" : "load_steps",
									"maxclass" : "newobj",
									"numinlets" : 1,
									"numoutlets" : 1,
									"outlettype" : [ "" ],
									"patching_rect" : [ 1242.0, 300.0, 88.0, 22.0 ],
									"text" : "loadmess 1"
								}

							}
 ],
						"lines" : [ 							{
								"patchline" : 								{
									"destination" : [ "pak", 6 ],
									"source" : [ "boundary", 1 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "commit_store", 0 ],
									"source" : [ "commit", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "send", 0 ],
									"source" : [ "commit_pack", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "commit_pack", 0 ],
									"source" : [ "commit_store", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 11 ],
									"source" : [ "graph", 1 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 4 ],
									"source" : [ "hl", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 3 ],
									"source" : [ "ht", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 2 ],
									"source" : [ "j", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "boundary", 0 ],
									"source" : [ "load_boundary", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "graph", 0 ],
									"source" : [ "load_graph", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "hl", 0 ],
									"source" : [ "load_hl", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "ht", 0 ],
									"source" : [ "load_ht", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "j", 0 ],
									"source" : [ "load_j", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "marked", 0 ],
									"source" : [ "load_marked", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "normalized", 0 ],
									"source" : [ "load_normalized", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "preset", 0 ],
									"source" : [ "load_preset", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "sampling", 0 ],
									"source" : [ "load_sampling", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "seed", 0 ],
									"source" : [ "load_seed", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "shots", 0 ],
									"source" : [ "load_shots", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "steps", 0 ],
									"source" : [ "load_steps", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "time", 0 ],
									"source" : [ "load_time", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "transform", 0 ],
									"source" : [ "load_transform", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 13 ],
									"source" : [ "marked", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 12 ],
									"source" : [ "normalized", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "commit_store", 1 ],
									"order" : 1,
									"source" : [ "pak", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "speedlim", 0 ],
									"order" : 0,
									"source" : [ "pak", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 7 ],
									"source" : [ "preset", 1 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "send", 0 ],
									"source" : [ "preview_pack", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "presets", 0 ],
									"source" : [ "read", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "presets", 0 ],
									"source" : [ "recall1", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "reset_pack", 0 ],
									"source" : [ "reset", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "send", 0 ],
									"source" : [ "reset_pack", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 9 ],
									"source" : [ "sampling", 1 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 10 ],
									"source" : [ "seed", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 8 ],
									"source" : [ "shots", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "preview_pack", 0 ],
									"source" : [ "speedlim", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 14 ],
									"source" : [ "steps", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "presets", 0 ],
									"source" : [ "store1", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 5 ],
									"source" : [ "time", 0 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "pak", 1 ],
									"source" : [ "transform", 1 ]
								}

							}
, 							{
								"patchline" : 								{
									"destination" : [ "presets", 0 ],
									"source" : [ "write", 0 ]
								}

							}
 ],
						"originid" : "pat-35"
					}
,
					"patching_rect" : [ 30.0, 78.0, 1560.0, 180.0 ],
					"varname" : "QMW_Transform_Control_v5",
					"viewvisibility" : 1
				}

			}
, 			{
				"box" : 				{
					"id" : "v5_status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 30.0, 272.0, 432.0, 22.0 ],
					"text" : "\"commit_complete 25611385 hadamard 54 51222770 51222771\""
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "v4_status_route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "FullPacket" ],
					"patching_rect" : [ 1080.0, 1320.0, 500.0, 22.0 ],
					"text" : "o.route /qmw/v5/transform/status /qmw/v5/transform/error"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "v4_prepend_status",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1080.0, 1350.0, 110.0, 22.0 ],
					"text" : "prepend status"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "v4_prepend_error",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1200.0, 1350.0, 110.0, 22.0 ],
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
					"destination" : [ "v5_status", 0 ],
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
					"order" : 1,
					"source" : [ "udpreceive", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v4_status_route", 0 ],
					"hidden" : 1,
					"order" : 0,
					"source" : [ "udpreceive", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "v4_prepend_error", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "receiver", 0 ],
					"hidden" : 1,
					"source" : [ "v4_prepend_status", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v4_prepend_error", 0 ],
					"hidden" : 1,
					"source" : [ "v4_status_route", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v4_prepend_status", 0 ],
					"hidden" : 1,
					"source" : [ "v4_status_route", 0 ]
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
 ],
		"originid" : "pat-27",
		"parameters" : 		{
			"transform_controls::boundary" : [ "hamiltonian_boundary", "hamiltonian_boundary", 0 ],
			"transform_controls::graph" : [ "representation_graph", "representation_graph", 0 ],
			"transform_controls::hl" : [ "hamiltonian_hl", "hamiltonian_hl", 0 ],
			"transform_controls::ht" : [ "hamiltonian_ht", "hamiltonian_ht", 0 ],
			"transform_controls::j" : [ "hamiltonian_j", "hamiltonian_j", 0 ],
			"transform_controls::marked" : [ "representation_marked_state", "representation_marked_state", 0 ],
			"transform_controls::normalized" : [ "representation_normalized_graph", "representation_normalized_graph", 0 ],
			"transform_controls::preset" : [ "hamiltonian_preset", "hamiltonian_preset", 0 ],
			"transform_controls::sampling" : [ "hamiltonian_sampling", "hamiltonian_sampling", 0 ],
			"transform_controls::seed" : [ "hamiltonian_seed", "hamiltonian_seed", 0 ],
			"transform_controls::shots" : [ "hamiltonian_shots", "hamiltonian_shots", 0 ],
			"transform_controls::steps" : [ "representation_steps", "representation_steps", 0 ],
			"transform_controls::time" : [ "hamiltonian_time", "hamiltonian_time", 0 ],
			"transform_controls::transform" : [ "representation_transform", "representation_transform", 0 ],
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
				"name" : "Screenshot 2026-07-25 at 8.50.31 PM.png",
				"bootpath" : "/private/var/folders/sb/rmflyp5n0llgt6lhsysqww6r0000gp/T/TemporaryItems/NSIRD_screencaptureui_HfnROU",
				"patcherrelativepath" : "../../../../private/var/folders/sb/rmflyp5n0llgt6lhsysqww6r0000gp/T/TemporaryItems/NSIRD_screencaptureui_HfnROU",
				"type" : "PNG",
				"implicit" : 1
			}
, 			{
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
