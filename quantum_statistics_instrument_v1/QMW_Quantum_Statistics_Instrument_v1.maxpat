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
		"rect" : [ 199.0, 114.0, 1250.0, 816.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-20",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1359.0, 644.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-19",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1082.0, 631.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-14",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1265.5, 336.0, 64.0, 22.0 ],
					"text" : "model $1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-15",
					"maxclass" : "number",
					"maximum" : 5,
					"minimum" : 0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1265.5, 304.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-16",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1341.5, 336.0, 88.0, 22.0 ],
					"text" : "polyphony $1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-17",
					"maxclass" : "number",
					"maximum" : 4,
					"minimum" : 1,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1341.5, 304.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-76",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1136.0, 401.0, 64.0, 22.0 ],
					"text" : "model $1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-77",
					"maxclass" : "number",
					"maximum" : 5,
					"minimum" : 0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1136.0, 369.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-75",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1212.0, 401.0, 88.0, 22.0 ],
					"text" : "polyphony $1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-73",
					"maxclass" : "number",
					"maximum" : 4,
					"minimum" : 1,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1212.0, 369.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-2",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 1449.0, 520.0, 44.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.204724 ],
							"parameter_initial_enable" : 1,
							"parameter_longname" : "live.dial[1]",
							"parameter_mmax" : 1.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "POS",
							"parameter_type" : 0,
							"parameter_unitstyle" : 1
						}

					}
,
					"varname" : "live.dial[1]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-3",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 1399.0, 520.0, 44.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.76378 ],
							"parameter_initial_enable" : 1,
							"parameter_longname" : "live.dial[2]",
							"parameter_mmax" : 1.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "DAMP",
							"parameter_type" : 0,
							"parameter_unitstyle" : 1
						}

					}
,
					"varname" : "live.dial[2]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-4",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 1349.0, 520.0, 44.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.653543 ],
							"parameter_initial_enable" : 1,
							"parameter_longname" : "live.dial[3]",
							"parameter_mmax" : 1.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "BRIGHT",
							"parameter_type" : 0,
							"parameter_unitstyle" : 1
						}

					}
,
					"varname" : "live.dial[3]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 1298.0, 520.0, 44.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.25 ],
							"parameter_initial_enable" : 1,
							"parameter_longname" : "live.dial[4]",
							"parameter_mmax" : 1.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "STRUCT",
							"parameter_type" : 0,
							"parameter_unitstyle" : 1
						}

					}
,
					"varname" : "live.dial[4]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-6",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 1247.0, 520.0, 44.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.409449 ],
							"parameter_initial_enable" : 1,
							"parameter_longname" : "live.dial[5]",
							"parameter_mmax" : 1.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "FREQ",
							"parameter_type" : 0,
							"parameter_unitstyle" : 1
						}

					}
,
					"varname" : "live.dial[5]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-7",
					"maxclass" : "newobj",
					"numinlets" : 8,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 1223.0, 656.0, 92.5, 22.0 ],
					"text" : "vb.mi.rngs~"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-8",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 950.0, 586.0, 559.0, 20.0 ],
					"text" : "The central subharmonic is the macroscopic zero-momentum mode; it is silent below the critical density."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-48",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 1149.0, 509.0, 44.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.204724 ],
							"parameter_initial_enable" : 1,
							"parameter_longname" : "live.dial[14]",
							"parameter_mmax" : 1.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "POS",
							"parameter_type" : 0,
							"parameter_unitstyle" : 1
						}

					}
,
					"varname" : "live.dial[14]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-45",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 1099.0, 509.0, 44.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.76378 ],
							"parameter_initial_enable" : 1,
							"parameter_longname" : "live.dial[13]",
							"parameter_mmax" : 1.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "DAMP",
							"parameter_type" : 0,
							"parameter_unitstyle" : 1
						}

					}
,
					"varname" : "live.dial[13]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-42",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 1049.0, 509.0, 44.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.653543 ],
							"parameter_initial_enable" : 1,
							"parameter_longname" : "live.dial[9]",
							"parameter_mmax" : 1.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "BRIGHT",
							"parameter_type" : 0,
							"parameter_unitstyle" : 1
						}

					}
,
					"varname" : "live.dial[9]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-34",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 998.0, 509.0, 44.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.25 ],
							"parameter_initial_enable" : 1,
							"parameter_longname" : "live.dial[8]",
							"parameter_mmax" : 1.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "STRUCT",
							"parameter_type" : 0,
							"parameter_unitstyle" : 1
						}

					}
,
					"varname" : "live.dial[8]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-28",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 947.0, 509.0, 44.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.409449 ],
							"parameter_initial_enable" : 1,
							"parameter_longname" : "live.dial[7]",
							"parameter_mmax" : 1.0,
							"parameter_modmode" : 0,
							"parameter_shortname" : "FREQ",
							"parameter_type" : 0,
							"parameter_unitstyle" : 1
						}

					}
,
					"varname" : "live.dial[7]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-1",
					"maxclass" : "newobj",
					"numinlets" : 8,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 923.0, 645.0, 92.5, 22.0 ],
					"text" : "vb.mi.rngs~"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 18.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 18.0, 1050.0, 27.0 ],
					"text" : "QMW QUANTUM STATISTICS INSTRUMENT v1 — PAULI'S IDEAL GAS"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 12.0,
					"id" : "subtitle",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 50.0, 1100.0, 20.0 ],
					"text" : "One control D = n lambda_T^3. Listen to 20 ms detector windows: Fermi modes emit only singleton pips; Bose modes admit geometrically distributed multiparticle bursts and condensation."
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "control_title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 102.0, 500.0, 22.0 ],
					"text" : "PHASE-SPACE DENSITY / WAVEFUNCTION OVERLAP"
				}

			}
, 			{
				"box" : 				{
					"id" : "log_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 140.0, 150.0, 20.0 ],
					"text" : "log10(n lambda_T^3)"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "log_density",
					"maxclass" : "flonum",
					"maximum" : 2.0,
					"minimum" : -3.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 180.0, 137.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "log_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 275.0, 137.0, 125.0, 22.0 ],
					"text" : "prepend logdensity"
				}

			}
, 			{
				"box" : 				{
					"id" : "sweep",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 415.0, 137.0, 145.0, 22.0 ],
					"text" : "-1., 2. 30000"
				}

			}
, 			{
				"box" : 				{
					"id" : "sweep_line",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"patching_rect" : [ 570.0, 137.0, 38.0, 22.0 ],
					"text" : "line"
				}

			}
, 			{
				"box" : 				{
					"annotation" : "audible D=1 comparison",
					"id" : "audition",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 620.0, 137.0, 42.0, 22.0 ],
					"text" : "0."
				}

			}
, 			{
				"box" : 				{
					"annotation" : "log10(zeta(3/2))",
					"id" : "critical",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 640.0, 97.0, 82.0, 22.0 ],
					"text" : "0.417036"
				}

			}
, 			{
				"box" : 				{
					"id" : "critical_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 762.0, 140.0, 308.0, 20.0 ],
					"text" : "D=1 audition | Bose condensation threshold"
				}

			}
, 			{
				"box" : 				{
					"id" : "base_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 180.0, 75.0, 20.0 ],
					"text" : "base Hz"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "base",
					"maxclass" : "flonum",
					"maximum" : 1000.0,
					"minimum" : 30.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 95.0, 177.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "base_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 180.0, 177.0, 90.0, 22.0 ],
					"text" : "prepend base"
				}

			}
, 			{
				"box" : 				{
					"id" : "spacing_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 300.0, 180.0, 85.0, 20.0 ],
					"text" : "spacing Hz"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "spacing",
					"maxclass" : "flonum",
					"maximum" : 200.0,
					"minimum" : 1.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 385.0, 177.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "spacing_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 470.0, 177.0, 105.0, 22.0 ],
					"text" : "prepend spacing"
				}

			}
, 			{
				"box" : 				{
					"id" : "event_toggle",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 610.0, 177.0, 22.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "event_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 640.0, 180.0, 115.0, 20.0 ],
					"text" : "statistics events"
				}

			}
, 			{
				"box" : 				{
					"id" : "event_metro",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 760.0, 177.0, 65.0, 22.0 ],
					"text" : "metro 20"
				}

			}
, 			{
				"box" : 				{
					"id" : "tick_message",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 835.0, 177.0, 38.0, 22.0 ],
					"text" : "tick"
				}

			}
, 			{
				"box" : 				{
					"id" : "detect_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 885.0, 180.0, 70.0, 20.0 ],
					"text" : "detector"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "detection",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 950.0, 177.0, 60.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "detection_pre",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1015.0, 177.0, 112.0, 22.0 ],
					"text" : "prepend detection"
				}

			}
, 			{
				"box" : 				{
					"id" : "controller",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 7,
					"outlettype" : [ "", "", "", "", "", "", "" ],
					"patching_rect" : [ 25.0, 225.0, 285.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_quantum_statistics_controller_v1.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_quantum_statistics_controller_v1.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 325.0, 225.0, 745.0, 22.0 ],
					"text" : "set \"BOSE CONDENSED | D=n*lambda^3=3.0928 | Fermi P/nkT=1.5181 (blocking/stiffening) | Bose P/nkT=0.4345 | condensate=15.4%\""
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "fermi_title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 275.0, 500.0, 22.0 ],
					"text" : "FERMI–DIRAC — ANTISYMMETRIC / BLOCKING"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "bose_title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 570.0, 275.0, 500.0, 22.0 ],
					"text" : "BOSE–EINSTEIN — SYMMETRIC / BUNCHING"
				}

			}
, 			{
				"box" : 				{
					"id" : "fermi_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 305.0, 662.0, 20.0 ],
					"text" : "Bernoulli occupation n={0,1}: at most one short detection per mode/window. Degeneracy pressure expands carrier spacing."
				}

			}
, 			{
				"box" : 				{
					"id" : "bose_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 570.0, 305.0, 632.0, 20.0 ],
					"text" : "Geometric occupation n={0,1,2,...}: same-mode multiparticle bursts. Above zeta(3/2), the coherent condensate grows."
				}

			}
, 			{
				"box" : 				{
					"id" : "fermi_slider",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 45.0, 350.0, 500.0, 115.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"size" : 10
				}

			}
, 			{
				"box" : 				{
					"id" : "bose_slider",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 570.0, 350.0, 500.0, 115.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"size" : 10
				}

			}
, 			{
				"box" : 				{
					"id" : "fermi_poly",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 25.0, 490.0, 325.0, 22.0 ],
					"text" : "poly~ qmw_quantum_statistics_voice_v1 10 @parallel 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "bose_poly",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 570.0, 490.0, 325.0, 22.0 ],
					"text" : "poly~ qmw_quantum_statistics_voice_v1 10 @parallel 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "metrics_unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 5,
					"outlettype" : [ "float", "float", "float", "float", "float" ],
					"patching_rect" : [ 350.0, 535.0, 225.0, 22.0 ],
					"text" : "unpack f f f f f"
				}

			}
, 			{
				"box" : 				{
					"id" : "d_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 540.0, 55.0, 20.0 ],
					"text" : "D"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "d_value",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 65.0, 537.0, 90.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "fp_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 25.0, 575.0, 95.0, 20.0 ],
					"text" : "Fermi P/nkT"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "fp_value",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 125.0, 572.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "bp_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 230.0, 575.0, 90.0, 20.0 ],
					"text" : "Bose P/nkT"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "bp_value",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 325.0, 572.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "cond_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 430.0, 575.0, 115.0, 20.0 ],
					"text" : "condensate fraction"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "cond_value",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 550.0, 572.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "cond_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 660.0, 537.0, 72.0, 22.0 ],
					"text" : "pack f 40"
				}

			}
, 			{
				"box" : 				{
					"id" : "cond_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 740.0, 537.0, 42.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "cond_osc",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 805.0, 537.0, 70.0, 22.0 ],
					"text" : "cycle~ 55."
				}

			}
, 			{
				"box" : 				{
					"id" : "cond_gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 890.0, 537.0, 36.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "cond_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 650.0, 575.0, 559.0, 20.0 ],
					"text" : "The central subharmonic is the macroscopic zero-momentum mode; it is silent below the critical density."
				}

			}
, 			{
				"box" : 				{
					"id" : "sum_l1",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 80.0, 635.0, 36.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "sum_l2",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 130.0, 635.0, 36.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "sum_r1",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 250.0, 635.0, 36.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "sum_r2",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 300.0, 635.0, 36.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "master_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 390.0, 640.0, 65.0, 20.0 ],
					"text" : "master"
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
					"patching_rect" : [ 455.0, 637.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "master_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 540.0, 637.0, 72.0, 22.0 ],
					"text" : "pack f 40"
				}

			}
, 			{
				"box" : 				{
					"id" : "master_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 620.0, 637.0, 42.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "master_l",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 130.0, 680.0, 36.0, 22.0 ],
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
					"patching_rect" : [ 300.0, 680.0, 36.0, 22.0 ],
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
					"patching_rect" : [ 130.0, 715.0, 91.0, 22.0 ],
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
					"patching_rect" : [ 300.0, 715.0, 91.0, 22.0 ],
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
					"patching_rect" : [ 420.0, 685.0, 18.0, 60.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "meter_r",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 450.0, 685.0, 18.0, 60.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "dac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 508.0, 709.0, 52.0, 52.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "footer",
					"linecount" : 2,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 600.0, 680.0, 500.0, 33.0 ],
					"text" : "Event multiplicities sample the exact Bernoulli (Fermi) and geometric (Bose) one-mode laws. Carrier spacing retains the equation-of-state mapping through the exact P/(nkT)."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_log",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 25.0, 770.0, 100.0, 22.0 ],
					"text" : "loadmess 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_base",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 135.0, 770.0, 105.0, 22.0 ],
					"text" : "loadmess 110."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_spacing",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 250.0, 770.0, 98.0, 22.0 ],
					"text" : "loadmess 38."
				}

			}
, 			{
				"box" : 				{
					"id" : "init_master",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 358.0, 770.0, 98.0, 22.0 ],
					"text" : "loadmess 0.18"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_events",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 466.0, 770.0, 88.0, 22.0 ],
					"text" : "loadmess 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "init_detection",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 564.0, 770.0, 98.0, 22.0 ],
					"text" : "loadmess 0.3"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "log_density", 0 ],
					"source" : [ "audition", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "base_pre", 0 ],
					"source" : [ "base", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "base_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_l1", 1 ],
					"source" : [ "bose_poly", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_r1", 1 ],
					"source" : [ "bose_poly", 1 ]
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
					"destination" : [ "obj-1", 0 ],
					"order" : 0,
					"source" : [ "clip_l", 0 ]
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
					"destination" : [ "obj-7", 0 ],
					"order" : 0,
					"source" : [ "clip_r", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_l2", 1 ],
					"order" : 1,
					"source" : [ "cond_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_r2", 1 ],
					"order" : 0,
					"source" : [ "cond_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "cond_gain", 1 ],
					"source" : [ "cond_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "cond_gain", 0 ],
					"source" : [ "cond_osc", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "cond_line", 0 ],
					"source" : [ "cond_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "bose_poly", 0 ],
					"source" : [ "controller", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "bose_slider", 0 ],
					"source" : [ "controller", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "cond_pack", 0 ],
					"source" : [ "controller", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "fermi_poly", 0 ],
					"source" : [ "controller", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "fermi_slider", 0 ],
					"source" : [ "controller", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "metrics_unpack", 0 ],
					"source" : [ "controller", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 1 ],
					"source" : [ "controller", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "log_density", 0 ],
					"source" : [ "critical", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "detection_pre", 0 ],
					"source" : [ "detection", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "detection_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "tick_message", 0 ],
					"source" : [ "event_metro", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "event_metro", 0 ],
					"source" : [ "event_toggle", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_l1", 0 ],
					"source" : [ "fermi_poly", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_r1", 0 ],
					"source" : [ "fermi_poly", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "base", 0 ],
					"source" : [ "init_base", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "detection", 0 ],
					"source" : [ "init_detection", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "event_toggle", 0 ],
					"source" : [ "init_events", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "log_density", 0 ],
					"source" : [ "init_log", 0 ]
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
					"destination" : [ "spacing", 0 ],
					"source" : [ "init_spacing", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "log_pre", 0 ],
					"source" : [ "log_density", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "log_pre", 0 ]
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
					"destination" : [ "bp_value", 0 ],
					"source" : [ "metrics_unpack", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "cond_osc", 0 ],
					"source" : [ "metrics_unpack", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "cond_value", 0 ],
					"source" : [ "metrics_unpack", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "d_value", 0 ],
					"source" : [ "metrics_unpack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "fp_value", 0 ],
					"source" : [ "metrics_unpack", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 1 ],
					"order" : 0,
					"source" : [ "obj-1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"order" : 1,
					"source" : [ "obj-1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 0 ],
					"source" : [ "obj-14", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-14", 0 ],
					"source" : [ "obj-15", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 0 ],
					"source" : [ "obj-16", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-16", 0 ],
					"source" : [ "obj-17", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 7 ],
					"source" : [ "obj-19", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 5 ],
					"source" : [ "obj-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 7 ],
					"source" : [ "obj-20", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 1 ],
					"source" : [ "obj-28", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 4 ],
					"source" : [ "obj-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 2 ],
					"source" : [ "obj-34", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 3 ],
					"source" : [ "obj-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 3 ],
					"source" : [ "obj-42", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 4 ],
					"source" : [ "obj-45", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 5 ],
					"source" : [ "obj-48", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 2 ],
					"source" : [ "obj-5", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 1 ],
					"source" : [ "obj-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 1 ],
					"order" : 0,
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"order" : 1,
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-75", 0 ],
					"source" : [ "obj-73", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 0 ],
					"source" : [ "obj-75", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 0 ],
					"source" : [ "obj-76", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-76", 0 ],
					"source" : [ "obj-77", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spacing_pre", 0 ],
					"source" : [ "spacing", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "spacing_pre", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_l2", 0 ],
					"source" : [ "sum_l1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master_l", 0 ],
					"source" : [ "sum_l2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum_r2", 0 ],
					"source" : [ "sum_r1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master_r", 0 ],
					"source" : [ "sum_r2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sweep_line", 0 ],
					"source" : [ "sweep", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "log_density", 0 ],
					"source" : [ "sweep_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controller", 0 ],
					"source" : [ "tick_message", 0 ]
				}

			}
 ],
		"originid" : "pat-303",
		"parameters" : 		{
			"obj-2" : [ "live.dial[1]", "POS", 0 ],
			"obj-28" : [ "live.dial[7]", "FREQ", 0 ],
			"obj-3" : [ "live.dial[2]", "DAMP", 0 ],
			"obj-34" : [ "live.dial[8]", "STRUCT", 0 ],
			"obj-4" : [ "live.dial[3]", "BRIGHT", 0 ],
			"obj-42" : [ "live.dial[9]", "BRIGHT", 0 ],
			"obj-45" : [ "live.dial[13]", "DAMP", 0 ],
			"obj-48" : [ "live.dial[14]", "POS", 0 ],
			"obj-5" : [ "live.dial[4]", "STRUCT", 0 ],
			"obj-6" : [ "live.dial[5]", "FREQ", 0 ],
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
				"name" : "qmw_quantum_statistics_controller_v1.js",
				"bootpath" : "~/QuantumSonification/quantum_statistics_instrument_v1",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_quantum_statistics_voice_v1.maxpat",
				"bootpath" : "~/QuantumSonification/quantum_statistics_instrument_v1",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
			}
, 			{
				"name" : "vb.mi.rngs~.mxo",
				"type" : "iLaX"
			}
 ],
		"autosave" : 0
	}

}
